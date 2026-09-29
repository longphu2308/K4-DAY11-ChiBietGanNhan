"""Offline, descriptive rectangle quality metrics for a locked CVAT export."""
import csv
import json
from collections import Counter

from . import LabError
from .common import read_json, slices
from .cvat_xml import parse_file, polygons
from .locking import intact_lock
from .match import iou
from .report import scoped
from .zones import ignored

IOU_THRESHOLD = .5
METRICS = ("accuracy", "precision", "recall", "jaccard", "dice")


def _pairs(left, right):
    """Match geometry first, once per shape, with stable tie breaking."""
    candidates = sorted(((iou(a["box"], b["box"]), ai, bi)
                         for ai, a in enumerate(left) for bi, b in enumerate(right)),
                        key=lambda item: (-item[0], item[1], item[2]))
    used_left, used_right, pairs = set(), set(), []
    for overlap, ai, bi in candidates:
        if overlap < IOU_THRESHOLD:
            break
        if ai not in used_left and bi not in used_right:
            used_left.add(ai)
            used_right.add(bi)
            pairs.append((left[ai], right[bi], overlap))
    return pairs, used_left, used_right


def _scores(tp, fp, fn, outcomes):
    if not outcomes:
        return dict.fromkeys(METRICS)
    return {
        "accuracy": tp / outcomes,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "jaccard": tp / (tp + fp + fn),
        "dice": 2 * tp / (2 * tp + fp + fn),
    }


def _summary(events, label=None):
    selected = events if label is None else [event for event in events if
                                              event[0] == label or event[1] == label]
    tp = sum(actual == expected and actual is not None for actual, expected, _ in selected)
    fp = sum(actual == label and actual != expected for actual, expected, _ in selected) if label else \
        sum(actual is not None and actual != expected for actual, expected, _ in selected)
    fn = sum(expected == label and actual != expected for actual, expected, _ in selected) if label else \
        sum(expected is not None and actual != expected for actual, expected, _ in selected)
    scores = _scores(tp, fp, fn, len(selected) if label is None else len(events))
    if label is not None:
        # Per-label accuracy includes true negatives among spatial comparison outcomes.
        scores["accuracy"] = (tp + len(events) - len(selected)) / len(events) if events else None
    return {"tp": tp, "fp": fp, "fn": fn, "outcomes": len(selected), **scores}


def _format(value):
    return "N/A" if value is None else "%.3f" % value


def _attributes(attrs):
    defaults = {"occluded", "truncated", "edge_zone"}
    return {key: value.strip().lower() for key, value in attrs.items()
            if key not in defaults or value.strip().lower() not in {"", "false", "0"}}


def evaluate(left_doc, ref_doc, frames):
    """Compute metrics for rectangles only; polygons define ignored regions."""
    events, conflicts, overlaps = [], [], []
    by_frame = {}
    excluded = Counter()
    for frame in frames:
        if frame not in ref_doc["images"]:
            raise LabError("Teaching reference thiếu frame " + frame)
        ignore_regions = [shape["points"] for shape in polygons(ref_doc, frame, "ignore_region")]
        left_all = scoped(left_doc, frame)
        left = [shape for shape in left_all if not ignored(shape["box"], ignore_regions)]
        excluded[frame] = len(left_all) - len(left)
        right = scoped(ref_doc, frame)
        pairs, used_left, used_right = _pairs(left, right)
        frame_events = []

        def add(actual, expected, overlap, kind, left_id="", right_id=""):
            event = (actual, expected, overlap)
            events.append(event)
            frame_events.append(event)
            if kind:
                conflicts.append({"frame": frame, "type": kind, "left": left_id,
                                  "reference": right_id, "left_label": actual or "",
                                  "reference_label": expected or "", "iou": _format(overlap)})

        for actual, expected, overlap in pairs:
            same_label = actual["label"] == expected["label"]
            add(actual["label"], expected["label"], overlap,
                "mismatching_label" if not same_label else "",
                actual["index"], expected["index"])
            if same_label:
                overlaps.append(overlap)
                if _attributes(actual.get("attrs", {})) != _attributes(expected.get("attrs", {})):
                    conflicts.append({"frame": frame, "type": "mismatching_attributes",
                                      "left": actual["index"], "reference": expected["index"],
                                      "left_label": actual["label"], "reference_label": expected["label"],
                                      "iou": _format(overlap)})
        for index, actual in enumerate(left):
            if index not in used_left:
                add(actual["label"], None, None, "extra_annotation", actual["index"])
        for index, expected in enumerate(right):
            if index not in used_right:
                add(None, expected["label"], None, "missing_annotation", right_id=expected["index"])
        by_frame[frame] = _summary(frame_events)

    labels = sorted({name for actual, expected, _ in events for name in (actual, expected) if name})
    confusion = {expected: {actual: 0 for actual in labels + ["<missing>"]}
                 for expected in labels + ["<extra>"]}
    for actual, expected, _ in events:
        confusion[expected or "<extra>"][actual or "<missing>"] += 1
    by_label = {label: _summary(events, label) for label in labels}
    combined = _summary(events)
    aggregate = {}
    for metric in METRICS:
        values = [row[metric] for row in by_label.values() if row[metric] is not None]
        aggregate[metric] = {"micro": combined[metric],
                             "macro": sum(values) / len(values) if values else None,
                             "worst_label": min(values) if values else None}
    return {"frames": by_frame, "labels": by_label, "aggregate": aggregate,
            "counts": {key: combined[key] for key in ("tp", "fp", "fn", "outcomes")},
            "mean_iou_of_correct_matches": sum(overlaps) / len(overlaps) if overlaps else None,
            "excluded_in_ignore_region": dict(excluded), "conflicts": conflicts,
            "confusion": confusion}


def local_quality(base):
    locked_path, lock = intact_lock(base, "r1_craft")
    slice_id = lock["slice"]
    expected_frames = slices(base)[slice_id]
    left = parse_file(locked_path)
    reference_path = base / "data" / "_ref" / (slice_id + ".xml")
    if not reference_path.is_file():
        raise LabError("Chưa mở teaching reference — chạy python3 lab11.py reference r1_craft")
    reference = parse_file(reference_path)
    mode_path = base / "submission" / "00_setup" / "mode.json"
    mode = read_json(mode_path) if mode_path.is_file() else {}
    if "frame3" in mode.get("degrade", []):
        frames = [frame for frame in expected_frames if frame in left["images"]]
    else:
        frames = expected_frames
    if not frames:
        raise LabError("Không có frame nào để đối chiếu")
    result = evaluate(left, reference, frames)
    result.update({"slice": slice_id, "frames_evaluated": frames,
                   "frames_missing_from_export": [frame for frame in expected_frames
                                                  if frame not in left["images"]],
                   "locked_sha256": lock["sha256"], "iou_threshold": IOU_THRESHOLD})
    folder = base / "submission" / "r3_diag"
    folder.mkdir(parents=True, exist_ok=True)
    report = ["# Đối chiếu chất lượng cục bộ — rectangle", "",
              "Teaching reference, không phải gold set đã phê duyệt; không có điểm đạt tự động.",
              "Nguồn: export r1_craft đã khóa SHA256 `%s`; slice `%s`." % (lock["sha256"], slice_id),
              "Ghép hình học greedy một-một theo IoU ≥ %.2f, rồi so class; H ≥ 40 px." % IOU_THRESHOLD,
              "Box trái nằm chủ yếu trong ignore_region reference không tính. Polygon, polyline, track không được chấm.",
              "Đây là phép tính offline của lab, không phải báo cáo hay kết quả tương đương CVAT Premium.", "",
              "Frame được tính: %s. Frame thiếu trong export: %s." %
              (", ".join(frames), ", ".join(result["frames_missing_from_export"]) or "không"),
              "TP=%d; FP=%d; FN=%d; số lần đối chiếu=%d; mean IoU của TP=%s." %
              (result["counts"]["tp"], result["counts"]["fp"], result["counts"]["fn"],
               result["counts"]["outcomes"], _format(result["mean_iou_of_correct_matches"])), "",
              "| Chỉ số | Micro | Macro | Nhãn thấp nhất |", "|---|---:|---:|---:|"]
    for metric, scores in result["aggregate"].items():
        report.append("| %s | %s | %s | %s |" %
                      (metric, *(_format(scores[key]) for key in ("micro", "macro", "worst_label"))))
    report += ["", "| Nhãn | TP | FP | FN | Accuracy | Precision | Recall | Jaccard | Dice |",
               "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for label, row in result["labels"].items():
        report.append("| %s | %d | %d | %d | %s | %s | %s | %s | %s |" %
                      (label, row["tp"], row["fp"], row["fn"],
                       *(_format(row[key]) for key in METRICS)))
    report += ["", "| Frame | TP | FP | FN | Accuracy | Precision | Recall |",
               "|---|---:|---:|---:|---:|---:|---:|"]
    for frame, row in result["frames"].items():
        report.append("| %s | %d | %d | %d | %s | %s | %s |" %
                      (frame, row["tp"], row["fp"], row["fn"],
                       *(_format(row[key]) for key in ("accuracy", "precision", "recall"))))
    report += ["", "Confusion matrix: hàng = teaching reference; cột = export đã khóa.",
               "`<missing>` là thiếu box; `<extra>` là box thừa. Xem `local_quality_confusion.csv`.", ""]
    matrix_labels = list(result["labels"])
    report += ["| Reference \\ Export | " + " | ".join(matrix_labels + ["<missing>"]) + " |",
               "|---|" + "---:|" * (len(matrix_labels) + 1)]
    for expected in matrix_labels + ["<extra>"]:
        report.append("| %s | %s |" % (expected, " | ".join(str(result["confusion"][expected][actual])
                                                       for actual in matrix_labels + ["<missing>"])))
    report += ["", "Chi tiết xung đột trong `local_quality_conflicts.csv`; dữ liệu máy đọc trong `local_quality.json`.",
               "Mismatching label đóng góp một FP cho class vẽ và một FN cho class reference; attribute khác được báo riêng.",
               "Micro accuracy đếm mỗi cặp ghép sai class là một lần đối chiếu; Jaccard đếm cả FP và FN.",
               "Macro/worst bỏ nhãn không xuất hiện ở cả hai phía; chỉ số không có mẫu là N/A.", ""]
    (folder / "local_quality.md").write_text("\n".join(report), encoding="utf-8")
    (folder / "local_quality.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (folder / "local_quality_conflicts.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, ("frame", "type", "left", "reference", "left_label", "reference_label", "iou"))
        writer.writeheader()
        writer.writerows(result["conflicts"])
    with (folder / "local_quality_confusion.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["reference\\export", *matrix_labels, "<missing>"])
        for expected in matrix_labels + ["<extra>"]:
            writer.writerow([expected] + [result["confusion"][expected][actual]
                                          for actual in matrix_labels + ["<missing>"]])
    return folder / "local_quality.md"
