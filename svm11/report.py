"""Reference and frozen-model comparisons."""
from collections import Counter
from html import escape
from pathlib import Path

from . import LabError
from .common import circles, learner_section, round_dir, slices
from .cvat_xml import boxes, parse_file, polygons
from .findings import append_rows
from .locking import intact_lock
from .match import classify, iou, match_pairs
from .zones import ignored, in_scope, zone

ZONES = ("center", "mid", "edge")
CELLS = ("LRM", "LR_noM", "LM_noR", "L_only", "RM_noL", "R_only", "M_only")


def three_way_cell(left, right, model):
    return {(True, True, True): "LRM", (True, True, False): "LR_noM",
            (True, False, True): "LM_noR", (True, False, False): "L_only",
            (False, True, True): "RM_noL", (False, True, False): "R_only",
            (False, False, True): "M_only"}.get((left, right, model), "na")


def scoped(document, frame, ignore_polys=None, preserve_ignored=False):
    values = [dict(item) for item in boxes(document, frame) if in_scope(item["box"])]
    for index, item in enumerate(values, 1):
        item["index"] = index
    if ignore_polys and not preserve_ignored:
        values = [item for item in values if not ignored(item["box"], ignore_polys)]
    return values


def zone_counts(left, right, ignore_polys, circle, threshold=.5):
    active = [item for item in left if not ignored(item["box"], ignore_polys)]
    refs = right
    pairs = match_pairs(active, refs, threshold)
    used_l = {id(a) for a, _ in pairs}
    used_r = {id(b) for _, b in pairs}
    counts = {z: {"n_ref": 0, "matched": 0, "missing": 0, "spurious": 0} for z in ZONES}
    for item in refs:
        z = zone(item["box"], circle)
        counts[z]["n_ref"] += 1
        if id(item) not in used_r:
            counts[z]["missing"] += 1
    for item in active:
        if id(item) not in used_l:
            counts[zone(item["box"], circle)]["spurious"] += 1
    for _, item in pairs:
        counts[zone(item["box"], circle)]["matched"] += 1
    return counts


def _doc_paths(base, round_name):
    left_path, lock = intact_lock(base, round_name)
    slice_id = lock["slice"]
    ref_path = base / "data" / "_ref" / (slice_id + ".xml")
    if not ref_path.is_file():
        raise LabError("Chưa mở reference — chạy python3 lab11.py reference " + round_name)
    return slice_id, parse_file(left_path), parse_file(ref_path)


def _table(counts, keys):
    lines = ["| zone | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for bin_name in ZONES:
        lines.append("| %s | %s |" % (bin_name, " | ".join(str(counts[bin_name][key]) for key in keys)))
    return lines


def _overlay(frame, size, shapes, image_path, statuses=None):
    width, height = size
    lines = ['<h2>%s</h2>' % escape(frame),
             '<svg viewBox="0 0 %d %d" style="max-width:100%%;border:1px solid #aaa">' % (width, height),
             '<image href="%s" width="%d" height="%d"/>' % (escape(image_path, quote=True), width, height)]
    colors = {"L": "#00e5ff", "R": "#ffcc00", "M": "#fa5f85"}
    diagnostic = {"MATCHED": "#00a67a", "MISSING": "#ef4444", "SPURIOUS": "#f97316",
                  "WRONG_CLASS": "#8b5cf6", "BOX_GEOMETRY": "#0284c7", "DUPLICATE": "#db2777",
                  "IGNORE_SCOPE": "#64748b", "ATTRIBUTE": "#a16207"}
    for prefix, items in shapes.items():
        for item in items:
            x1, y1, x2, y2 = item["box"]
            status = statuses.get(id(item), "MATCHED") if statuses is not None else prefix
            color = diagnostic.get(status, colors[prefix])
            lines.append('<rect data-status="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="3"/>' %
                         (escape(status, quote=True), x1, y1, x2 - x1, y2 - y1, color))
            lines.append('<text x="%.1f" y="%.1f" fill="%s" font-size="20">%s%d %s</text>' %
                         (x1, max(20, y1), color, escape(prefix), item["index"], escape(item["label"])))
    lines.append("</svg>")
    return "\n".join(lines)


def _html(title, sections):
    return '<!doctype html><html lang="vi"><meta charset="utf-8"><title>%s</title><body>%s</body></html>\n' % (
        escape(title), "\n".join(sections))


def compare(base, round_name="r1_craft"):
    slice_id, left_doc, ref_doc = _doc_paths(base, round_name)
    frame_names = slices(base)[slice_id]
    circles_by_frame = circles(base)
    counts = {z: {key: 0 for key in ("n_ref", "matched", "missing", "spurious")} for z in ZONES}
    findings = []
    details = ["# So sánh L với R", "", "Chỉ số L/R là thứ tự box cao ≥ H=40 trong từng frame, theo thứ tự XML; bắt đầu từ 1.",
               "Box L trong ignore_region được báo IGNORE_SCOPE, không tính SPURIOUS.", ""]
    overlays = []
    for frame in frame_names:
        if frame not in circles_by_frame:
            raise LabError("Thiếu vòng kính trong frames.csv: " + frame)
        left = scoped(left_doc, frame, preserve_ignored=True)
        refs = scoped(ref_doc, frame)
        ignore_polys = [p["points"] for p in polygons(ref_doc, frame, "ignore_region")]
        active_refs = refs
        circle = circles_by_frame[frame]
        size = left_doc["images"].get(frame, ref_doc["images"].get(frame, {"size": (1920, 1080)}))["size"]
        for bin_name, result in zone_counts(left, active_refs, ignore_polys, circle).items():
            for key in result:
                counts[bin_name][key] += result[key]
        results = classify(left, active_refs, ignore_polys, circle, size)
        statuses = {}
        details.append("## " + frame)
        for item in results:
            if item["left"] is not None:
                statuses[id(item["left"])] = item["what"]
            if item["right"] is not None:
                statuses[id(item["right"])] = item["what"]
            details.append("- %s %s %s" % (item["object_ref"], item["zone"], item["what"]))
            findings.append({"round": round_name, "slice": slice_id, "frame": frame,
                             "object_ref": item["object_ref"], "cell": "na", "what": item["what"]})
        overlays.append(_overlay(frame, size, {"L": left, "R": active_refs},
                                 "../../assets/images/" + frame, statuses))
    details += ["", "## Theo zone"] + _table(counts, ("n_ref", "matched", "missing", "spurious"))
    folder = round_dir(base, round_name)
    (folder / "compare.md").write_text("\n".join(details) + "\n", encoding="utf-8")
    (folder / "compare.html").write_text(_html("Compare " + slice_id, overlays), encoding="utf-8")
    append_rows(base / "submission" / "findings.csv", findings)
    return counts


def group_three(left, refs, preds):
    """Assign each box to exactly one deterministic three-way group."""
    lr = match_pairs(left, refs)
    used_l = {id(a) for a, _ in lr}
    used_r = {id(b) for _, b in lr}
    groups = [(a, b, None) for a, b in lr]
    groups += [(a, None, None) for a in left if id(a) not in used_l]
    groups += [(None, b, None) for b in refs if id(b) not in used_r]
    candidates = []
    for group_index, (a, b, _) in enumerate(groups):
        for model_index, m in enumerate(preds):
            scores = [iou(item["box"], m["box"]) for item in (a, b)
                      if item is not None and item["label"] == m["label"]]
            if scores and max(scores) >= .5:
                candidates.append((-max(scores), group_index, model_index))
    assigned_groups, assigned_models = set(), set()
    for _, group_index, model_index in sorted(candidates):
        if group_index not in assigned_groups and model_index not in assigned_models:
            a, b, _ = groups[group_index]
            groups[group_index] = (a, b, preds[model_index])
            assigned_groups.add(group_index)
            assigned_models.add(model_index)
    groups += [(None, None, m) for index, m in enumerate(preds) if index not in assigned_models]
    return groups


def model(base):
    slice_id, left_doc, ref_doc = _doc_paths(base, "r1_craft")
    model_doc = parse_file(base / "assets" / "model-yolo26m.xml")
    frame_names = slices(base)[slice_id]
    circle_map = circles(base)
    counts = {z: Counter() for z in ZONES}
    left_counts = {z: Counter() for z in ZONES}
    left_issues = {z: Counter() for z in ZONES}
    rows, sections, overlays = [], ["# L / R / M", "", "L/R/M là thứ tự box in-scope theo XML của từng frame.", ""], []
    for frame in frame_names:
        if frame not in circle_map:
            raise LabError("Thiếu vòng kính trong frames.csv: " + frame)
        ignore_polys = [p["points"] for p in polygons(ref_doc, frame, "ignore_region")]
        left = [v for v in scoped(left_doc, frame) if not ignored(v["box"], ignore_polys)]
        refs = scoped(ref_doc, frame)
        preds = [v for v in scoped(model_doc, frame) if not ignored(v["box"], ignore_polys)]
        groups = group_three(left, refs, preds)
        size = left_doc["images"].get(frame, ref_doc["images"].get(frame))["size"]
        for bin_name, result in zone_counts(left, refs, ignore_polys, circle_map[frame]).items():
            left_counts[bin_name].update(result)
        for item in classify(scoped(left_doc, frame, preserve_ignored=True), refs, ignore_polys,
                             circle_map[frame], size):
            if item["what"] not in ("MATCHED", "IGNORE_SCOPE"):
                left_issues[item["zone"]][item["what"]] += 1
        sections.append("## " + frame)
        for a, b, c in groups:
            cell = three_way_cell(bool(a), bool(b), bool(c))
            label = "+".join("%s%d" % (prefix, item["index"]) for prefix, item in (("L", a), ("R", b), ("M", c)) if item)
            bin_name = zone((b or a or c)["box"], circle_map[frame])
            counts[bin_name][cell] += 1
            sections.append("- %s: %s (%s)" % (label, cell, bin_name))
            if cell != "LRM":
                what = "MISSING" if cell in ("LR_noM", "RM_noL", "R_only") else "SPURIOUS"
                rows.append({"round": "r3_diag", "slice": slice_id, "frame": frame,
                             "object_ref": label, "cell": cell, "what": what})
        overlays.append(_overlay(frame, size, {"L": left, "R": refs, "M": preds}, "../../assets/images/" + frame))
    sections += ["", "## Zone × cell"] + _table(counts, CELLS)
    folder = base / "submission" / "r3_diag"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "model_compare.md").write_text("\n".join(sections) + "\n", encoding="utf-8")
    (folder / "model_compare.html").write_text(_html("Model " + slice_id, overlays), encoding="utf-8")
    append_rows(base / "submission" / "findings.csv", rows)
    write_zone_table(folder / "zone_table.md", left_counts, counts, left_issues)
    return counts


ZONE_NOTES = ("## Nhận xét\n\n"
              "- Zone nào người (L) và model (M) gãy nhiều nhất, dẫn số ở bảng trên: TODO\n"
              "- Giả thuyết vì sao (méo fisheye, box lỏng, thiếu `ego_body`, ...) và giới hạn của slice ba frame: TODO\n")


def write_zone_table(path, left_counts, model_counts, left_issues):
    """Numbers come from the tool; the learner only writes the notes, which survive a rerun."""
    lines = ["# Zone table (slice của bạn)", "",
             "Lệnh `python3 lab11.py model` tự ghi bảng số (cùng cách đếm với `r1_craft/compare.md` và "
             "`model_compare.md`); chạy lại lệnh sẽ cập nhật bảng và giữ nguyên phần nhận xét. "
             "Bạn chỉ viết mục Nhận xét.", "",
             "| Zone | n_ref | L missing | L spurious | M missing (`LR_noM` + `R_only`) | "
             "M thừa (`LM_noR` + `M_only`) | Lỗi L chính (`what`) |",
             "|---|---:|---:|---:|---:|---:|---|"]
    for bin_name in ZONES:
        left, cells = left_counts[bin_name], model_counts[bin_name]
        top = left_issues[bin_name].most_common(1)
        lines.append("| %s | %d | %d | %d | %d | %d | %s |" % (
            bin_name, left["n_ref"], left["missing"], left["spurious"],
            cells["LR_noM"] + cells["R_only"], cells["LM_noR"] + cells["M_only"],
            "%s (%d)" % top[0] if top else "—"))
    previous = path.read_text(encoding="utf-8") if path.is_file() else ""
    notes = learner_section(previous, "## Nhận xét", ZONE_NOTES)
    path.write_text("\n".join(lines) + "\n\n" + notes, encoding="utf-8")


def iou_sweep(base, thresholds):
    slice_id, left_doc, ref_doc = _doc_paths(base, "r1_craft")
    model_doc = parse_file(base / "assets" / "model-yolo26m.xml")
    lines = ["# IoU sweep", "", "| threshold | side | zone | matched | missing | spurious |", "|---|---|---|---:|---:|---:|"]
    circle_map = circles(base)
    for threshold in thresholds:
        if not 0 < threshold <= 1:
            raise LabError("IoU phải trong (0,1]")
        for side, doc in (("L", left_doc), ("M", model_doc)):
            totals = {z: Counter() for z in ZONES}
            for frame in slices(base)[slice_id]:
                if frame not in circle_map:
                    raise LabError("Thiếu vòng kính trong frames.csv: " + frame)
                ignore_polys = [p["points"] for p in polygons(ref_doc, frame, "ignore_region")]
                result = zone_counts(scoped(doc, frame), scoped(ref_doc, frame), ignore_polys,
                                     circle_map[frame], threshold)
                for z in ZONES:
                    totals[z].update(result[z])
            for z in ZONES:
                lines.append("| %.2f | %s | %s | %d | %d | %d |" %
                             (threshold, side, z, totals[z]["matched"], totals[z]["missing"], totals[z]["spurious"]))
    path = base / "submission" / "r3_diag" / "iou_sweep.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return "\n".join(lines)
