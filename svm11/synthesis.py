"""Rework delta and error-analysis card."""
from collections import Counter

from .common import circles, learner_section, slices
from .cvat_xml import parse_file, polygons
from .findings import read_rows
from .gates import _zone_for_row
from .locking import intact_lock
from .match import classify, iou, match_pairs
from .report import ZONES, scoped, zone_counts
from .zones import ignored


def rework(base):
    from . import LabError
    before_path, before_lock = intact_lock(base, "r1_craft")
    after_path, after_lock = intact_lock(base, "rework")
    slice_id = before_lock["slice"]
    if after_lock["slice"] != slice_id:
        raise LabError("Lock r1_craft và rework phải cùng slice")
    ref_path = base / "data" / "_ref" / (slice_id + ".xml")
    if not ref_path.is_file():
        raise LabError("Chưa mở reference")
    before, after, ref = parse_file(before_path), parse_file(after_path), parse_file(ref_path)
    circles_by_frame = circles(base)
    totals = {state: {z: Counter() for z in ZONES} for state in ("before", "after")}
    frame_state = {}
    for frame in slices(base)[slice_id]:
        polys = [p["points"] for p in polygons(ref, frame, "ignore_region")]
        refs = scoped(ref, frame)
        before_left = scoped(before, frame)
        after_left = scoped(after, frame)
        for state, doc in (("before", before), ("after", after)):
            left = scoped(doc, frame)
            result = zone_counts(left, refs, polys, circles_by_frame[frame])
            for bin_name in ZONES:
                totals[state][bin_name].update(result[bin_name])
        active_after = [item for item in after_left if not ignored(item["box"], polys)]
        size = after["images"].get(frame, ref["images"].get(frame))["size"]
        frame_state[frame] = (before_left, after_left, refs,
                              match_pairs(active_after, refs),
                              classify(after_left, refs, polys, circles_by_frame[frame], size))
    lines = ["# Rework delta", "", "| zone | matched before | matched after | missing before | missing after | spurious before | spurious after |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for z in ZONES:
        old, new = totals["before"][z], totals["after"][z]
        lines.append("| %s | %d | %d | %d | %d | %d | %d |" %
                     (z, old["matched"], new["matched"], old["missing"], new["missing"],
                      old["spurious"], new["spurious"]))
    lines += ["", "## Findings action=rework"]
    for row in read_rows(base / "submission" / "findings.csv"):
        if row.get("action") != "rework":
            continue
        frame, object_ref, what = row.get("frame", ""), row.get("object_ref", ""), row.get("what", "")
        state = "không áp dụng"
        if row.get("slice") == slice_id and frame in frame_state and row.get("cell") not in ("LR_noM", "M_only"):
            old_left, new_left, refs, pairs, issues = frame_state[frame]
            parts = {part[0]: int(part[1:]) for part in object_ref.split("+")
                     if len(part) > 1 and part[0] in "LRM" and part[1:].isdigit()}
            if "R" in parts:
                target = next((item for item in refs if item["index"] == parts["R"]), None)
                if target is not None:
                    matched = any(b is target for _, b in pairs)
                    same_issue = any(item["what"] == what and item["right"] is target for item in issues)
                    if what in ("MISSING", "WRONG_CLASS", "BOX_GEOMETRY"):
                        state = "đã sửa" if matched else "chưa sửa"
                    elif what in ("DUPLICATE", "ATTRIBUTE"):
                        state = "đã sửa" if matched and not same_issue else "chưa sửa"
                    else:
                        state = "không xác minh"
            elif "L" in parts:
                original = next((item for item in old_left if item["index"] == parts["L"]), None)
                if original is not None:
                    candidates = sorted(((iou(original["box"], item["box"]), item) for item in new_left),
                                        key=lambda pair: (-pair[0], pair[1]["index"]))
                    survivor = candidates[0][1] if candidates and candidates[0][0] >= .3 else None
                    if survivor is None:
                        state = "đã sửa"
                    else:
                        same_issue = any(item["what"] == what and item["left"] is survivor for item in issues)
                        state = "chưa sửa" if same_issue else "đã sửa"
        lines.append("- %s %s %s: %s" % (frame, object_ref, what, state))
    path = base / "submission" / "rework" / "delta.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


CARD_ANALYSIS = ("## Phân tích của bạn\n\n"
                 "Hai bảng trên do `python3 lab11.py card` tính từ `findings.csv`; chạy lại lệnh sẽ cập nhật bảng và "
                 "giữ nguyên mục này. Viết cho lỗi nổi bật nhất, dẫn frame/`object_ref`.\n\n"
                 "- Nguyên nhân khả dĩ (`why`) và vì sao bạn nghĩ vậy: TODO\n"
                 "- Cách sửa và ai nhận việc (`owner`): TODO\n"
                 "- Bằng chứng (ảnh trong `screenshots/`, dòng findings, rule): TODO\n")


def card(base):
    path = base / "submission" / "10_error_card.md"
    previous = path.read_text(encoding="utf-8") if path.is_file() else ""
    if previous and "TODO" not in previous:
        return path
    rows = read_rows(base / "submission" / "findings.csv")
    counts = Counter(row.get("what") for row in rows if row.get("what"))
    table = Counter()
    try:
        circle_map = circles(base)
    except OSError:
        circle_map = {}
    documents = {}
    for row in rows:
        block = row.get("slice", "").split("-", 1)[0]
        bin_name = _zone_for_row(base, row, circle_map, documents) or "unknown"
        table[(bin_name, block, row.get("what", ""))] += 1
    lines = ["# Error analysis card", "", "## Zone × block", "",
             "| zone | block | what | count |", "|---|---|---|---:|"]
    for bin_name, block, what in sorted(table):
        lines.append("| %s | %s | %s | %d |" % (bin_name, block, what, table[(bin_name, block, what)]))
    lines += ["", "## Top defects"]
    for what, count in counts.most_common(3):
        frame = next((row.get("frame", "") for row in rows if row.get("what") == what), "")
        lines.append("- %s: %d (ví dụ frame %s)" % (what, count, frame))
    analysis = learner_section(previous, "## Phân tích của bạn", CARD_ANALYSIS)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n\n" + analysis, encoding="utf-8")
    return path
