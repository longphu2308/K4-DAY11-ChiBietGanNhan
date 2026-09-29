"""Paths, configuration, and small file helpers."""
import csv
import hashlib
import json
import os
from pathlib import Path

from . import LabError

ROUNDS = {"calib": "p1_calib", "r1_craft": "r1_craft", "rework": "rework"}


def root(value=None):
    return Path(value or os.environ.get("LAB11_ROOT") or Path(__file__).resolve().parent.parent).resolve()


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LabError("Không đọc được %s: %s" % (path, exc)) from exc


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def slices(base):
    data = read_json(base / "assets" / "slices.json")
    result = {item["slice"]: item["frames"] for item in data.get("slices", [])}
    if "C0" in data:
        result["C0"] = [data["C0"]["frame"]]
    return result


def chosen_slice(base, round_name="r1_craft"):
    path = base / "submission" / "00_setup" / "mode.json"
    data = read_json(path)
    if round_name == "calib":
        return "C0"
    value = data.get("slice") or data.get("own_slice")
    if not value:
        raise LabError("Chưa chọn slice — chạy python3 lab11.py mode --members <ten> hoặc python3 lab11.py cvat <slice>")
    return value


def round_dir(base, round_name):
    if round_name not in ROUNDS:
        raise LabError("ROUND không hợp lệ: " + round_name)
    return base / "submission" / ROUNDS[round_name]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def code(digest_value):
    value = digest_value[:8].upper()
    return value[:4] + "-" + value[4:]


def circles(base):
    path = base / "assets" / "frames.csv"
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row["file"]: (float(row["cx"]), float(row["cy"]), float(row["r"]))
                for row in csv.DictReader(stream)}


def learner_section(previous, heading, template):
    """Return the learner-owned tail of a generated file so a rerun never drops prose.

    The tail starts at `heading`; if the learner removed that heading, the whole old text is kept
    below a fresh template instead of being overwritten.
    """
    if heading in previous:
        return previous[previous.index(heading):]
    if not previous.strip():
        return template
    return template + ("\n## Bản cũ\n\nLệnh không thấy tiêu đề `%s` nên giữ nguyên bản cũ dưới đây. "
                       "Chuyển phần bạn viết lên mục trên rồi xoá mục này.\n\n%s" % (heading.lstrip("# "), previous))


# Written only after the teaching reference of r1_craft is revealed, so the repo starts with P0–P3 files only.
LATE_TEMPLATES = ("20_guideline_patch.md", "30_escalation_ticket.md", "45_review_plan.md", "50_exit_ticket.md")


def ensure_late_templates(base):
    """Copy P4–P6 templates into submission/ once r1_craft reference is open; never overwrite."""
    sub = base / "submission"
    if not (sub / "r1_craft" / "reference.txt").is_file():
        return []
    created = []
    for name in LATE_TEMPLATES:
        source, target = base / "assets" / "templates" / name, sub / name
        if source.is_file() and not target.exists():
            target.write_bytes(source.read_bytes())
            created.append(name)
    return created
