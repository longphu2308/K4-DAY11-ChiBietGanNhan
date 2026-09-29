"""Learner workflow: assignment, CVAT task instructions, peer review, and status."""
import hashlib
from html import escape
import os
from pathlib import Path
import shutil
import webbrowser

from . import LabError
from .common import chosen_slice, code, digest, ensure_late_templates, read_json, slices, write_json
from .cvat_xml import parse_bytes, xml_bytes
from .locking import lock_values
from .report import _html, _overlay, scoped

DEGRADE_STEPS = {"stretch", "k12", "frame3", "findings", "rework"}


def mode(base, members, self_name=None):
    names = sorted({name.strip() for name in members.split(",") if name.strip()})
    if not 1 <= len(names) <= 3:
        raise LabError("MEMBERS cần 1–3 tên khác nhau")
    own_name = (self_name or "").strip()
    if len(names) > 1 and not own_name:
        raise LabError("Nhóm nhiều người cần --self <tên của bạn> trong --members")
    if not own_name:
        own_name = names[0]
    if own_name not in names:
        raise LabError("--self phải là một tên trong --members")
    choices = sorted(key for key in slices(base) if key != "C0")
    if len(choices) < len(names):
        raise LabError("Không đủ slice để chia thành viên")
    assignments = {}
    available = list(choices)
    for name in names:
        position = int(hashlib.sha256(name.encode()).hexdigest(), 16) % len(available)
        assignments[name] = available.pop(position)
    path = base / "submission" / "00_setup" / "mode.json"
    previous = read_json(path) if path.is_file() else {}
    value = dict(previous)  # keep current-slice and support-prefill state from the CVAT command
    value.update({"members": names, "assignments": assignments,
                  "self": own_name, "slice": assignments[own_name],
                  "degrade": previous.get("degrade", [])})
    write_json(path, value)
    if len(names) > 1:
        rotation = {names[i]: names[(i + 1) % len(names)] for i in range(len(names))}
        write_json(path.with_name("team.json"), {"qa_reviews": rotation})
    return value


def cvat(base, slice_id, support=False):
    all_slices = slices(base)
    if slice_id not in all_slices:
        raise LabError("Slice không hợp lệ: " + slice_id)
    mode_path = base / "submission" / "00_setup" / "mode.json"
    state = read_json(mode_path) if mode_path.is_file() else {}
    state["current_slice"] = slice_id
    state["support_prefill"] = bool(support)
    state["support_slice"] = slice_id if support else ""
    if slice_id != "C0":
        state["slice"] = slice_id
    prefill = base / "assets" / "prefill" / (slice_id + ("-support" if support else "") + ".xml")
    if not prefill.is_file():
        raise LabError("Thiếu prefill " + str(prefill))
    imported = []
    doc = parse_bytes(prefill.read_bytes())
    for frame, image in doc["images"].items():
        imported += ["%s:%s" % (frame, shape["id"] or shape["index"])
                     for shape in scoped(doc, frame) if shape["source"] == "file"]
    state["prefill_box_ids"] = imported
    write_json(mode_path, state)
    hints = read_json(base / "assets" / "k12.json") if (base / "assets" / "k12.json").is_file() else {}
    lines = ["Task: Day11 · ADASIND · %s · raw_fisheye" % slice_id,
             "Dán labels từ: %s" % (base / "assets" / "labels.json"),
             "Upload ảnh:"]
    lines += ["- %s" % (base / "assets" / "images" / frame) for frame in all_slices[slice_id]]
    lines += ["Upload annotations: %s (format CVAT 1.1)" % prefill,
              "Export: CVAT for images 1.1", "Box prefill: " + (", ".join(imported) or "không có")]
    for item in hints.get(slice_id, []):
        lines.append("K12: %s %s %s (%s)" % (item.get("frame"), item.get("label"), item.get("zone"), item.get("hint")))
    return "\n".join(lines)


def degrade(base, step):
    if step not in DEGRADE_STEPS:
        raise LabError("STEP không hợp lệ; chọn: " + ", ".join(sorted(DEGRADE_STEPS)))
    path = base / "submission" / "00_setup" / "mode.json"
    state = read_json(path) if path.is_file() else {}
    entries = state.setdefault("degrade", [])
    if step not in entries:
        entries.append(step)
    write_json(path, state)
    return "Đã ghi degrade: " + step


def qa(base, slice_id, source, verification_code):
    if slice_id not in slices(base):
        raise LabError("Slice QA không hợp lệ")
    data = xml_bytes(Path(source))
    actual = code(digest(data))
    if verification_code.upper() != actual:
        raise LabError("CODE không khớp file: cần %s" % actual)
    doc = parse_bytes(data)
    frames = slices(base)[slice_id]
    if set(doc["images"]) - set(frames):
        raise LabError("File QA có ảnh ngoài slice")
    retained = base / "data" / "_qa" / (slice_id + ".xml")
    retained.parent.mkdir(parents=True, exist_ok=True)
    retained.write_bytes(data)
    sections = []
    for frame in frames:
        size = doc["images"].get(frame, {"size": (1920, 1080)})["size"]
        sections.append(_overlay(frame, size, {"L": scoped(doc, frame)}, "../../assets/images/" + frame))
    folder = base / "submission" / "r2_qa"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "qa_overlay.html").write_text(_html("QA " + slice_id, sections), encoding="utf-8")
    review = folder / "qa_review.md"
    if not review.is_file():
        review.write_text("# QA review · %s\n\nMã khóa: %s\n\n| frame | object_ref | rule_id | nhận xét |\n|---|---|---|---|\n| TODO | TODO | TODO | TODO |\n\nGhi finding r2_qa: cell=L_only, rule_id có giá trị, why để trống.\n" %
                          (slice_id, actual), encoding="utf-8")
    return folder / "qa_overlay.html"


def status(base):
    sub = base / "submission"
    ensure_late_templates(base)
    def complete(relative):
        path = sub / relative
        return path.is_file() and path.stat().st_size > 0 and "TODO" not in path.read_text(encoding="utf-8", errors="replace")

    doctor_path = sub / "00_setup" / "doctor.txt"
    if not complete("00_setup/doctor.txt") or (doctor_path.is_file() and any(
            line.startswith("✗") for line in doctor_path.read_text(encoding="utf-8").splitlines())):
        return "python3 lab11.py doctor"
    if not complete("00_setup/mode.json"):
        return "python3 lab11.py mode --members ten"
    mode_state = read_json(sub / "00_setup" / "mode.json")
    own_slice = mode_state.get("slice") or mode_state.get("own_slice")
    if not complete("00_setup/sensor_context.md"):
        return "Điền submission/00_setup/sensor_context.md"
    if not complete("parking/annotations.xml"):
        return "Mở docs/11-parking-lines-vi.md → python3 lab11.py parking --file <file-export-zip>"
    if not complete("parking/observations.md"):
        return "Điền submission/parking/observations.md"
    if not complete("p1_calib/lock.txt"):
        if mode_state.get("current_slice") != "C0":
            return "python3 lab11.py cvat C0"
        return "python3 lab11.py lock calib exports/c0.zip"
    if not complete("p1_calib/reference.txt"):
        return "python3 lab11.py reference calib"
    if not complete("p1_calib/compare.md"):
        return "python3 lab11.py compare calib"
    if mode_state.get("current_slice") != own_slice or not own_slice:
        return "python3 lab11.py cvat %s" % (own_slice or "<slice>")
    if not (base / "exports" / "r1-draft.xml").is_file() and not complete("r1_craft/lock.txt"):
        return "Export bản nháp từ CVAT → python3 lab11.py draft <duong-dan-file-zip>"
    selfqc_path = sub / "r1_craft" / "selfqc.md"
    selfqc_text = selfqc_path.read_text(encoding="utf-8") if selfqc_path.is_file() else ""
    if "k12" not in mode_state.get("degrade", []) and "Fill ratio (K12)" not in selfqc_text:
        return "python3 lab11.py fill r1_craft"
    if "# Tự soát" not in selfqc_text or "## Checklist thủ công" not in selfqc_text:
        return "python3 lab11.py selfqc r1_craft"
    checklist = [line for line in selfqc_text.splitlines() if line.startswith("- [")]
    if len(checklist) < 9 or any(not line.lower().startswith("- [x]") for line in checklist):
        return "Hoàn thành checklist trong submission/r1_craft/selfqc.md"
    if not complete("r1_craft/lock.txt"):
        return "python3 lab11.py lock r1_craft exports/r1.zip"
    if not complete("r2_qa/qa_review.md"):
        if (sub / "r2_qa" / "qa_review.md").is_file():
            return "Điền submission/r2_qa/qa_review.md"
        return "python3 lab11.py qa --slice %s --file annotations.xml --code XXXX-XXXX" % own_slice
    if not complete("r1_craft/reference.txt"):
        return "python3 lab11.py reference r1_craft"
    if not complete("r1_craft/compare.md"):
        return "python3 lab11.py compare r1_craft"
    quality_files = ("r3_diag/local_quality.md", "r3_diag/local_quality.json",
                     "r3_diag/local_quality_conflicts.csv", "r3_diag/local_quality_confusion.csv")
    if not all(complete(name) for name in quality_files):
        return "python3 lab11.py local-quality"
    try:
        quality = read_json(sub / "r3_diag" / "local_quality.json")
    except LabError:
        return "python3 lab11.py local-quality"
    if quality.get("locked_sha256") != lock_values(sub / "r1_craft" / "lock.txt").get("sha256"):
        return "python3 lab11.py local-quality"
    if not complete("r3_diag/model_compare.md"):
        return "python3 lab11.py model"
    if not complete("r3_diag/iou_sweep.md"):
        return "python3 lab11.py iou-sweep --iou 0.3,0.5,0.7"
    if not (sub / "r3_diag" / "zone_table.md").is_file():
        return "python3 lab11.py model"
    for relative in ("findings.csv", "r3_diag/zone_table.md"):
        if not complete(relative):
            return "Điền submission/" + relative
    if not complete("rework/lock2.txt"):
        return "python3 lab11.py lock rework exports/r2.zip"
    if not complete("rework/delta.md"):
        return "python3 lab11.py rework"
    card_path = sub / "10_error_card.md"
    card_text = card_path.read_text(encoding="utf-8", errors="replace") if card_path.is_file() else ""
    # a hand-written card with no TODO is left alone by `card`, so only ask for it when `card` would act
    if "# Error analysis card" not in card_text and (not card_text.strip() or "TODO" in card_text):
        return "python3 lab11.py card"
    if not complete("10_error_card.md"):
        return "Điền submission/10_error_card.md"
    for relative in ("20_guideline_patch.md", "30_escalation_ticket.md", "40_decision_log.csv",
                     "45_review_plan.md", "45_sampling_plan.csv", "46_gold_set_plan.md",
                     "50_exit_ticket.md"):
        if not complete(relative):
            return "Điền submission/" + relative
    screenshots = [path for path in (sub / "screenshots").glob("*") if path.is_file() and not path.name.startswith(".")]
    if len(screenshots) < 2:
        return "Thêm hai ảnh vào submission/screenshots/"
    return "python3 lab11.py check"


def worked(base):
    path = base / "assets" / "worked" / "index.html"
    webbrowser.open(path.as_uri())
    return str(path)


def cleanup(base, yes=False):
    if not (base / "lab11.py").is_file() or not (base / "Makefile").is_file():
        raise LabError("Cleanup chỉ chạy trong thư mục learner của repo Day 11")
    targets = [base / name for name in ("data", "exports", "build")]
    if not yes:
        response = input("Xóa data/, exports/, build/ trong repo này? Gõ YES: ")
        if response != "YES":
            return "Đã hủy cleanup. Trong CVAT, xóa project bằng giao diện nếu cần."
    for path in targets:
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        elif path.exists():
            raise LabError("Mục cleanup không phải thư mục: " + str(path))
    return ("Đã xóa data/, exports/, build/ trong repo nếu có; lệnh này không hoàn tác. "
            "Trong CVAT, xóa project bằng giao diện nếu cần.")


def reset_task(base):
    return ("Tạo lại task trong giao diện CVAT: chọn project, đặt tên Day11 · ADASIND · <slice> · raw_fisheye, "
            "upload 3 ảnh trong assets/images, import prefill CVAT 1.1, rồi export lại CVAT for images 1.1. "
            "Lệnh này không xóa dữ liệu.")
