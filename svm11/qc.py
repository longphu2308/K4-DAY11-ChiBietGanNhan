"""Draft export staging, fill ratio, and automatic self-checks."""
from pathlib import Path

from . import LabError
from .common import chosen_slice, circles, read_json, round_dir, slices
from .cvat_xml import boxes, parse_bytes, parse_file, polygons, xml_bytes
from .locking import intact_lock, lock_paths
from .match import iou
from .zones import ignored, in_scope, truncated, zone

CHECKLIST = [
    "Phạm vi H=40 và vật cần vẽ", "lens_border và ego_body", "Class sáu nhãn",
    "Rider và Bike", "Geometry trên ảnh fisheye gốc", "truncated và occluded",
    "Vật thiếu hoặc box trùng", "ignore_region có reason", "Tên task raw_fisheye và export CVAT 1.1",
]

# The two selected ADASIND frames where no ego-vehicle body is visible.
NO_EGO_FRAMES = {"adasind_006840.jpg", "adasind_271039.jpg"}


def stage_draft(base, source):
    """Copy a CVAT draft export into the predictable path used by self-QC."""
    base = Path(base)
    data = xml_bytes(source)
    document = parse_bytes(data)
    expected = set(slices(base)[chosen_slice(base)])
    actual = set(document["images"])
    mode_path = base / "submission" / "00_setup" / "mode.json"
    mode = read_json(mode_path) if mode_path.is_file() else {}
    allowed = expected if "frame3" not in mode.get("degrade", []) else set(
        slices(base)[chosen_slice(base)][:2])
    if not actual or actual - expected or (actual != expected and actual != allowed):
        missing = ", ".join(sorted(expected - actual))
        raise LabError("Bản nháp thiếu/sai frame trong slice" + (": " + missing if missing else ""))
    path = base / "exports" / "r1-draft.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def polygon_area(points):
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]))) / 2


def polygon_bbox(points):
    return (min(p[0] for p in points), min(p[1] for p in points),
            max(p[0] for p in points), max(p[1] for p in points))


def fill_ratios(shapes):
    output = []
    for poly in shapes:
        if poly["kind"] != "polygon" or poly["label"] == "ignore_region" or not poly.get("points"):
            continue
        candidates = [b for b in shapes if b["kind"] == "box" and b["label"] == poly["label"]]
        group = poly.get("group_id")
        chosen = next((b for b in candidates if group not in (None, "", "0") and b.get("group_id") == group), None)
        if chosen is None:
            chosen = next((b for b in candidates if iou(b["box"], polygon_bbox(poly["points"])) >= .5), None)
        if chosen is not None:
            x1, y1, x2, y2 = chosen["box"]
            output.append((chosen, polygon_area(poly["points"]) / ((x2 - x1) * (y2 - y1) or 1)))
    return output


def draft_or_locked(base, round_name):
    _, lock_file = lock_paths(base, round_name)
    if lock_file.is_file():
        return intact_lock(base, round_name)[0]
    if round_name == "r1_craft":
        draft = base / "exports" / "r1-draft.xml"
        if draft.is_file():
            return draft
    stems = {"calib": ("c0", "calib"), "r1_craft": ("r1", "r1_craft"),
             "rework": ("r2", "rework")}[round_name]
    for stem in stems:
        for extension in (".zip", ".xml"):
            path = base / "exports" / (stem + extension)
            if path.is_file():
                return path
    folder = round_dir(base, round_name)
    return folder / ("annotations-v2.xml" if round_name == "rework" else "annotations.xml")


def fill(base, round_name="r1_craft"):
    folder = round_dir(base, round_name)
    doc = parse_file(draft_or_locked(base, round_name))
    lines = ["## Fill ratio (K12)"]
    values = []
    try:
        frame_circles = circles(base)
    except OSError:
        frame_circles = {}
    for frame, image in doc["images"].items():
        for item, ratio in fill_ratios(image["shapes"]):
            bin_name = zone(item["box"], frame_circles.get(frame, (0, 0, 1)))
            values.append((bin_name, ratio))
            lines.append("- %s box %s %s: %.3f" % (frame, item.get("index", "?"), bin_name, ratio))
    if not values:
        lines.append("chưa vẽ polygon K12 (degrade)")
    else:
        for bin_name in ("edge", "center"):
            subset = [v for z, v in values if z == bin_name]
            if subset:
                lines.append("mean %s: %.3f (n=%d)" % (bin_name, sum(subset) / len(subset), len(subset)))
    path = folder / "selfqc.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.is_file() else ""
    marker = "## Fill ratio (K12)"
    path.write_text((old.split(marker)[0].rstrip() + "\n\n" if old else "") + "\n".join(lines) + "\n", encoding="utf-8")
    return path


def selfqc(base, round_name="r1_craft"):
    folder = round_dir(base, round_name)
    doc = parse_file(draft_or_locked(base, round_name))
    circle_map = circles(base)
    lines = ["# Tự soát", ""]
    mode_path = base / "submission" / "00_setup" / "mode.json"
    if mode_path.is_file() and round_name == "r1_craft":
        expected_frames = slices(base)[chosen_slice(base)]
        mode = read_json(mode_path)
        required_frames = expected_frames[:2] if "frame3" in mode.get("degrade", []) else expected_frames
        for frame in required_frames:
            if frame not in doc["images"]:
                lines.append("- Thiếu frame trong export: " + frame)
    for frame, image in doc["images"].items():
        if frame not in circle_map:
            raise LabError("Thiếu vòng kính trong frames.csv: " + frame)
        all_boxes = boxes(doc, frame)
        ignore_shapes = polygons(doc, frame, "ignore_region")
        ignore_polys = [p["points"] for p in ignore_shapes]
        for item in all_boxes:
            ref = "%s L%d" % (frame, item["index"])
            if not in_scope(item["box"]):
                lines.append("- %s: chiều cao < H (xem lại phạm vi)" % ref)
            if ignored(item["box"], ignore_polys):
                lines.append("- %s: box trong ignore_region" % ref)
            expected = truncated(item["box"], circle_map[frame], image["size"])
            actual = item["attrs"].get("truncated", "false").lower() in ("true", "1")
            if expected != actual:
                lines.append("- %s: truncated khác dự kiến" % ref)
        for i, left in enumerate(all_boxes):
            for right in all_boxes[i + 1:]:
                if left["label"] == right["label"] and iou(left["box"], right["box"]) > .7:
                    lines.append("- %s: hai box cùng class IoU > 0.7" % frame)
        reasons = {p["attrs"].get("reason") for p in ignore_shapes}
        required_reasons = ("lens_border",) if frame in NO_EGO_FRAMES else ("ego_body", "lens_border")
        for reason in required_reasons:
            if reason not in reasons:
                lines.append("- %s: thiếu %s" % (frame, reason))
        if frame in NO_EGO_FRAMES and "ego_body" in reasons:
            lines.append("- %s: ego_body thừa (frame không thấy thân xe)" % frame)
        if None in reasons or "" in reasons:
            lines.append("- %s: ignore_region thiếu reason" % frame)
    if "raw_fisheye" not in doc["meta"]:
        lines.append("- Tên task thiếu raw_fisheye")
    path = folder / "selfqc.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.is_file() else ""
    ticked = {line[6:].strip() for line in old.splitlines() if line.lower().startswith("- [x] ")}
    lines += ["", "## Checklist thủ công"] + ["- [%s] %s" % ("x" if value in ticked else " ", value) for value in CHECKLIST]
    fill_section = "## Fill ratio (K12)" + old.split("## Fill ratio (K12)", 1)[1] if "## Fill ratio (K12)" in old else ""
    path.write_text("\n".join(lines) + "\n\n" + fill_section, encoding="utf-8")
    return path
