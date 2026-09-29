"""Setup checks, findings triage, and formal submission gate."""
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

from . import LabError
from .common import LATE_TEMPLATES, circles, read_json, slices, write_json
from .findings import read_rows, validate_rows
from .locking import lock_values
from .report import scoped
from .zones import zone


def doctor(base):
    messages = []
    if sys.version_info < (3, 9):
        messages.append("✗ Cần Python 3.9 trở lên")
    else:
        messages.append("✓ Python %s.%s" % sys.version_info[:2])
    url = os.environ.get("CVAT_URL", "http://localhost:8080").rstrip("/")
    try:
        with urllib.request.urlopen(url + "/api/server/about", timeout=5) as response:
            about = json.loads(response.read())
        version = str(about.get("version", "không rõ"))
        messages.append("✓ CVAT %s" % version)
        if not version.startswith("2.74."):
            messages.append("! CVAT khác 2.74.x; kiểm tra API quality")
    except (urllib.error.URLError, ValueError) as exc:
        messages.append("✗ CVAT chưa kết nối được: %s" % exc)
    tracked = subprocess.run(["git", "ls-files", "--", "**/.env", ".env"], cwd=str(base),
                             capture_output=True, text=True, check=False)
    if any(path.split("/")[-1] == ".env" for path in tracked.stdout.splitlines()):
        messages.append("✗ Git đang track .env; bỏ file bí mật khỏi index")
    else:
        messages.append("✓ Git không track .env")
    if shutil.which("gh"):
        result = subprocess.run(["gh", "repo", "view", "--json", "visibility"], cwd=str(base),
                                capture_output=True, text=True, check=False)
        if result.returncode == 0:
            try:
                visibility = json.loads(result.stdout).get("visibility")
            except ValueError:
                visibility = None
            messages.append("✓ Repo PUBLIC" if visibility == "PUBLIC" else "✗ Repo cần PUBLIC để chấm bài")
        else:
            messages.append("✗ Không xác nhận được repo PUBLIC; kiểm tra remote và quyền gh")
    else:
        messages.append("! Chưa có gh; tự kiểm tra repo bài nộp là PUBLIC trên GitHub")
    path = base / "submission" / "00_setup" / "doctor.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(messages) + "\n", encoding="utf-8")
    return messages


def triage(base):
    return validate_rows(read_rows(base / "submission" / "findings.csv"))


MODEL_CELLS = {"LRM", "LM_noR", "RM_noL", "M_only"}


def _zone_for_row(base, row, frame_circles, xml_docs):
    from .cvat_xml import parse_file
    frame = row.get("frame", "")
    if frame not in frame_circles:
        return None
    slice_id = row.get("slice", "")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", slice_id):
        return None
    round_name = row.get("round", "")
    for part in row.get("object_ref", "").split("+"):
        if not part or part[0] not in "LRM":
            continue
        prefix = part[0]
        if prefix == "L":
            if round_name == "calib":
                path = base / "submission" / "p1_calib" / "annotations.xml"
            elif round_name == "rework":
                path = base / "submission" / "rework" / "annotations-v2.xml"
            elif round_name == "r2_qa":
                path = base / "data" / "_qa" / (slice_id + ".xml")
            else:
                path = base / "submission" / "r1_craft" / "annotations.xml"
        elif prefix == "R":
            path = base / "data" / "_ref" / (slice_id + ".xml")
        else:
            path = base / "assets" / "model-yolo26m.xml"
        if path not in xml_docs:
            try:
                xml_docs[path] = parse_file(path) if path.is_file() else None
            except (LabError, OSError, ValueError):
                xml_docs[path] = None
        doc = xml_docs[path]
        if doc is None:
            continue
        try:
            index = int(part[1:])
            matches = [s for s in scoped(doc, frame) if s["index"] == index]
            if matches:
                return zone(matches[0]["box"], frame_circles[frame])
        except (ValueError, KeyError):
            pass
    return None


def check(base):
    """Return human-readable failed gates; writes manifest even when incomplete."""
    from .cvat_xml import parse_file
    sub = base / "submission"
    failures = []
    mode_path = sub / "00_setup" / "mode.json"
    mode = read_json(mode_path) if mode_path.is_file() else {}
    rows = read_rows(sub / "findings.csv")
    row_errors = validate_rows(rows)
    failures += row_errors[:8]
    if len(row_errors) > 8:
        failures.append("… còn %d lỗi dòng findings nữa (sửa các dòng trên rồi chạy lại)" % (len(row_errors) - 8))
    reduced_findings = "findings" in mode.get("degrade", [])
    minimum = 8 if reduced_findings else 12
    if len(rows) < minimum:
        failures.append("findings cần ≥%d dòng (hiện %d)" % (minimum, len(rows)))
    cells = {r.get("cell") for r in rows} - {"na", ""}
    if len(cells) < 4:
        failures.append("findings cần ≥4 cell khác na")
    model_minimum = 5 if reduced_findings else 8
    if sum(r.get("cell") in MODEL_CELLS for r in rows) < model_minimum:
        failures.append("findings cần ≥%d dòng có M trong cell" % model_minimum)
    for round_name in ("r1_craft", "r2_qa", "r3_diag"):
        role_minimum = 2 if reduced_findings else 3
        if sum(r.get("round") == round_name for r in rows) < role_minimum:
            failures.append("findings cần ≥%d dòng vai %s" % (role_minimum, round_name))
    docs = {}
    try:
        frame_circles = circles(base)
    except OSError:
        frame_circles = {}
    zones = {_zone_for_row(base, r, frame_circles, docs) for r in rows}
    zones.discard(None)
    if len(zones) < 3:
        failures.append("findings cần ≥3 zone (hiện %d)" % len(zones))
    decision = sub / "40_decision_log.csv"
    try:
        with decision.open(encoding="utf-8-sig", newline="") as stream:
            decisions = list(csv.DictReader(stream))
    except OSError:
        decisions = []
    if len(decisions) < 4 or not any((row.get("status") or "").strip().lower() == "escalated"
                                     for row in decisions):
        failures.append("decision log cần ≥4 entry và ≥1 escalated")
    sampling = sub / "45_sampling_plan.csv"
    try:
        with sampling.open(encoding="utf-8-sig", newline="") as stream:
            allocations = list(csv.DictReader(stream))
        expected = {(camera, kind) for camera in ("front", "rear", "left", "right")
                    for kind in ("normal", "hard")}
        observed = {((row.get("camera_id") or "").strip(), (row.get("slice_type") or "").strip())
                    for row in allocations}
        total = sum(int((row.get("frames") or "").strip()) for row in allocations)
        if len(allocations) != 8 or observed != expected or total != 200 or any(
                int((row.get("frames") or "").strip()) <= 0 or not (row.get("risk") or "").strip() or
                not (row.get("rationale") or "").strip() for row in allocations):
            failures.append("45_sampling_plan.csv cần 4 camera × normal/hard, số dương, tổng 200 và lý do")
    except (OSError, ValueError, KeyError):
        failures.append("45_sampling_plan.csv chưa phải bảng phân bổ hợp lệ")
    required = [
        "00_setup/doctor.txt", "00_setup/mode.json", "00_setup/sensor_context.md",
        "parking/annotations.xml", "parking/observations.md",
        "p1_calib/annotations.xml", "p1_calib/lock.txt", "p1_calib/reference.txt",
        "p1_calib/compare.md", "p1_calib/compare.html",
        "r1_craft/annotations.xml", "r1_craft/lock.txt", "r1_craft/selfqc.md",
        "r1_craft/reference.txt", "r1_craft/compare.md", "r1_craft/compare.html",
        "r2_qa/qa_review.md", "r2_qa/qa_overlay.html",
        "r3_diag/local_quality.md", "r3_diag/local_quality.json", "r3_diag/local_quality_conflicts.csv",
        "r3_diag/local_quality_confusion.csv",
        "r3_diag/model_compare.md", "r3_diag/model_compare.html",
        "r3_diag/zone_table.md", "rework/annotations-v2.xml", "rework/lock2.txt",
        "rework/delta.md", "findings.csv", "10_error_card.md", "20_guideline_patch.md",
        "30_escalation_ticket.md", "40_decision_log.csv", "45_review_plan.md",
        "45_sampling_plan.csv", "46_gold_set_plan.md",
        "50_exit_ticket.md",
    ]
    manifest = []
    from .common import digest
    for relative in required:
        path = sub / relative
        if not path.is_file():
            if relative in LATE_TEMPLATES:
                failures.append("Thiếu file %s (mẫu tự tạo sau python3 lab11.py reference r1_craft)" % relative)
            elif relative == "r3_diag/zone_table.md":
                failures.append("Thiếu file %s (chạy python3 lab11.py model)" % relative)
            elif relative == "10_error_card.md":
                failures.append("Thiếu file %s (chạy python3 lab11.py card)" % relative)
            else:
                failures.append("Thiếu file " + relative)
            continue
        data = path.read_bytes()
        if not data.strip():
            failures.append("File rỗng " + relative)
        if b"TODO" in data:
            failures.append("Còn TODO trong " + relative)
        entry = {"file": relative, "lines": len(data.splitlines()), "sha256": digest(data)}
        if relative.endswith("lock.txt") or relative.endswith("lock2.txt"):
            entry["locked_at"] = lock_values(path).get("locked_at", "")
        if relative.endswith("reference.txt"):
            entry["lock_before_reveal"] = "lock_before_reveal: true" in data.decode("utf-8", "replace")
        manifest.append(entry)
    doctor_path = sub / "00_setup" / "doctor.txt"
    if doctor_path.is_file() and any(line.startswith("✗") for line in doctor_path.read_text(encoding="utf-8").splitlines()):
        failures.append("doctor còn lỗi; chạy python3 lab11.py doctor lại sau khi sửa môi trường")
    quality_path = sub / "r3_diag" / "local_quality.json"
    if quality_path.is_file():
        try:
            report = json.loads(quality_path.read_text(encoding="utf-8"))
            locked = lock_values(sub / "r1_craft" / "lock.txt")
            if report.get("locked_sha256") != locked.get("sha256"):
                failures.append("local_quality cũ so với bản export đã khóa; chạy python3 lab11.py local-quality lại")
        except (OSError, ValueError):
            failures.append("local_quality.json không hợp lệ; chạy python3 lab11.py local-quality lại")
    parking_path = sub / "parking" / "annotations.xml"
    if parking_path.is_file():
        from .parking import validate_export
        try:
            validate_export(parking_path.read_bytes())
        except (LabError, OSError, ValueError) as exc:
            failures.append("Parking export không hợp lệ: " + str(exc))
    craft_path = sub / "r1_craft" / "annotations.xml"
    if craft_path.is_file() and mode.get("slice") and (base / "assets" / "slices.json").is_file():
        try:
            frame_list = slices(base)[mode["slice"]]
            required = set(frame_list[:2] if "frame3" in mode.get("degrade", []) else frame_list)
            missing = required - set(parse_file(craft_path)["images"])
            if missing:
                failures.append("r1_craft thiếu frame bắt buộc: " + ", ".join(sorted(missing)))
        except (LabError, KeyError, ValueError) as exc:
            failures.append("Không kiểm được frame r1_craft: " + str(exc))
    delta = sub / "rework" / "delta.md"
    if delta.is_file() and len(re.findall(r"\d+", delta.read_text(encoding="utf-8"))) < 2:
        failures.append("delta.md cần số trước và sau")
    shots = list((sub / "screenshots").glob("*")) if (sub / "screenshots").is_dir() else []
    if len([p for p in shots if p.is_file() and not p.name.startswith(".")]) < 2:
        failures.append("screenshots cần ≥2 ảnh")
    write_json(sub / "manifest.json", {"files": manifest, "failed_gates": failures})
    return failures
