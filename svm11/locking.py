"""Export locks and controlled reference reveal."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import zipfile

from . import LabError
from .common import chosen_slice, code, digest, read_json, round_dir, slices
from .cvat_xml import boxes, parse_bytes, parse_file, xml_bytes
from .match import iou


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def lock_values(path):
    if not path.is_file():
        return {}
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "history:":
            break
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key] = value.strip()
    return result


def lock_paths(base, round_name):
    folder = round_dir(base, round_name)
    if round_name == "rework":
        return folder / "annotations-v2.xml", folder / "lock2.txt"
    return folder / "annotations.xml", folder / "lock.txt"


def intact_lock(base, round_name):
    target, lock_path = lock_paths(base, round_name)
    if not target.is_file() or not lock_path.is_file():
        raise LabError("Chưa khóa export — chạy python3 lab11.py lock <round> <file-export> trước khi mở reference")
    values = lock_values(lock_path)
    if digest(target.read_bytes()) != values.get("sha256"):
        raise LabError("File export đã thay đổi sau khi khóa; cần khóa lại")
    return target, values


def _prefill_counts(base, slice_id, document):
    mode_path = base / "submission" / "00_setup" / "mode.json"
    mode = read_json(mode_path) if mode_path.is_file() else {}
    suffix = "-support" if mode.get("support_prefill") and mode.get("support_slice") == slice_id else ""
    prefill = base / "assets" / "prefill" / (slice_id + suffix + ".xml")
    prior = parse_file(prefill) if prefill.is_file() else {"images": {}}
    kept = edited = new = 0
    for frame in document["images"]:
        source_boxes = boxes(prior, frame)
        all_boxes = boxes(document, frame)
        used_prefill = set()
        for item in all_boxes:
            if item["source"] == "file":
                kept += 1
                matches = sorted(((iou(item["box"], other["box"]), index)
                                  for index, other in enumerate(source_boxes) if index not in used_prefill),
                                 key=lambda pair: (-pair[0], pair[1]))
                if matches and matches[0][0] >= .5:
                    used_prefill.add(matches[0][1])
        manual = [item for item in all_boxes if item["source"] != "file"]
        candidates = sorted(((iou(item["box"], other["box"]), item_index, source_index)
                             for item_index, item in enumerate(manual)
                             for source_index, other in enumerate(source_boxes)
                             if source_index not in used_prefill),
                            key=lambda triple: (-triple[0], triple[1], triple[2]))
        used_manual = set()
        for value, item_index, source_index in candidates:
            if value < .5:
                break
            if item_index not in used_manual and source_index not in used_prefill:
                used_manual.add(item_index)
                used_prefill.add(source_index)
        edited += len(used_manual)
        new += len(manual) - len(used_manual)
    return kept, edited, new


def lock_export(base, round_name, source, relock=False):
    base, source = Path(base), Path(source)
    slice_id = chosen_slice(base, round_name)
    frame_list = slices(base).get(slice_id, [])
    frames = set(frame_list)
    if not frames:
        raise LabError("Slice không hợp lệ: " + slice_id)
    data = xml_bytes(source)
    document = parse_bytes(data)
    if not document["images"] or set(document["images"]) - frames:
        raise LabError("Export có ảnh ngoài slice hoặc không có ảnh")
    if round_name == "r1_craft":
        mode_path = base / "submission" / "00_setup" / "mode.json"
        mode = read_json(mode_path) if mode_path.is_file() else {}
        required = set(frame_list[:2] if "frame3" in mode.get("degrade", []) else frame_list)
        missing = required - set(document["images"])
        if missing:
            raise LabError("Export cuối thiếu frame bắt buộc: " + ", ".join(sorted(missing)))
    allowed = {item["name"] for item in read_json(base / "assets" / "labels.json")}
    labels = {s["label"] for image in document["images"].values() for s in image["shapes"]}
    if labels - allowed:
        raise LabError("Export có label ngoài labels.json: " + ", ".join(sorted(labels - allowed)))
    target, lock_path = lock_paths(base, round_name)
    old = lock_path.read_text(encoding="utf-8") if lock_path.is_file() else ""
    value = digest(data)
    if old and lock_values(lock_path).get("sha256") != value and not relock:
        raise LabError("Đã khóa file khác; dùng --relock nếu cần khóa lại")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    if old and lock_values(lock_path).get("sha256") == value:
        return code(value)
    kept, edited, new = _prefill_counts(base, slice_id, document)
    counts = Counter(s["kind"] for im in document["images"].values() for s in im["shapes"])
    lines = ["round: " + round_name, "slice: " + slice_id, "sha256: " + value,
             "code: " + code(value), "locked_at: " + now(),
             "shapes: " + ", ".join("%s=%d" % pair for pair in sorted(counts.items())),
             "prefill_kept: %d" % kept, "prefill_edited: %d" % edited, "new: %d" % new]
    if old:
        lines += ["history:"] + ["  " + line for line in old.splitlines()]
    lock_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return code(value)


def reveal_reference(base, round_name):
    base = Path(base)
    _, values = intact_lock(base, round_name)
    slice_id = values["slice"]
    zip_path = base / "refs" / ("slice-C0-calib.zip" if slice_id == "C0" else "slice-" + slice_id + ".zip")
    if not zip_path.is_file():
        raise LabError("Thiếu reference cho slice " + slice_id)
    try:
        with zipfile.ZipFile(zip_path) as archive:
            names = [n for n in archive.namelist() if n.endswith(".xml")]
            if len(names) != 1:
                raise LabError("Reference ZIP phải có một XML")
            data = archive.read(names[0])
    except zipfile.BadZipFile as exc:
        raise LabError("Reference ZIP hỏng") from exc
    parse_bytes(data)
    target = base / "data" / "_ref" / (slice_id + ".xml")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    path = round_dir(base, round_name) / "reference.txt"
    path.write_text("slice: %s\nlock_before_reveal: true\nopened_at: %s\n" % (slice_id, now()), encoding="utf-8")
    return target
