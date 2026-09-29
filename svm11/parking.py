"""Parking-lot micro-practice export validation; geometry is reviewed by a human."""
from pathlib import Path
from xml.etree import ElementTree as ET

from . import LabError
from .cvat_xml import parse_bytes, xml_bytes

CORE_IMAGE = "parking-lot-core.jpg"


def instructions(base):
    folder = Path(base) / "assets" / "parking"
    return "\n".join((
        "Bài vạch đỗ xe: xem docs/11-parking-lines-vi.md trước khi vẽ.",
        "Ảnh core: " + str(folder / CORE_IMAGE),
        "Ảnh đối chiếu: " + str(folder / "parking-lot-contrast.png"),
        "CVAT task: Day11 · parking_line · public-sample",
        "Dán nhãn từ: " + str(folder / "labels.json"),
        "Export CVAT for images 1.1 rồi chạy python3 lab11.py parking --file <file-zip>.",
    ))


def validate_export(data):
    document = parse_bytes(data)
    if set(document["images"]) != {CORE_IMAGE}:
        raise LabError("Bài parking cần đúng ảnh parking-lot-core.jpg")
    root = ET.fromstring(data)
    image = root.find("image")
    lines = [shape for shape in image.findall("polyline") if shape.get("label") == "parking_line"
             and len(shape.get("points", "").split(";")) >= 2]
    areas = [shape for shape in image.findall("polygon") if shape.get("label") == "free_space"
             and len(shape.get("points", "").split(";")) >= 3]
    if len(lines) < 2 or len(areas) < 1:
        raise LabError("Cần ≥2 polyline parking_line và ≥1 polygon free_space trên ảnh core")
    return len(lines), len(areas)


def save_export(base, source):
    data = xml_bytes(source)
    counts = validate_export(data)
    target = Path(base) / "submission" / "parking" / "annotations.xml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target, counts
