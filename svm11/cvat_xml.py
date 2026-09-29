"""Stable-order CVAT for images 1.1 reader."""
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from . import LabError


def xml_bytes(path):
    path = Path(path)
    if not path.is_file():
        raise LabError("Không thấy file %s" % path)
    if path.suffix.lower() == ".xml":
        return path.read_bytes()
    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                names = [name for name in archive.namelist() if Path(name).name == "annotations.xml"]
                if len(names) != 1:
                    raise LabError("ZIP phải có đúng một annotations.xml")
                return archive.read(names[0])
        except zipfile.BadZipFile as exc:
            raise LabError("ZIP CVAT không hợp lệ") from exc
    raise LabError("Export phải là .xml hoặc .zip")


def parse_bytes(data):
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise LabError("XML CVAT không hợp lệ: %s" % exc) from exc
    if root.tag != "annotations" or root.findtext("version") != "1.1":
        raise LabError("Cần CVAT for images 1.1")
    if root.find("track") is not None:
        raise LabError("Cần CVAT for images 1.1, không phải video")
    images = {}
    for image in root.findall("image"):
        name = Path(image.get("name", "")).name
        shapes = []
        box_index = 0
        for node in image:
            if node.tag not in ("box", "polygon"):
                continue
            attrs = {a.get("name", ""): a.text or "" for a in node.findall("attribute")}
            item = {"kind": node.tag, "label": node.get("label", ""), "attrs": attrs,
                    "source": node.get("source", ""), "group_id": node.get("group_id", ""),
                    "id": node.get("id", "")}
            if node.tag == "box":
                box_index += 1
                item["index"] = box_index
                item["box"] = tuple(float(node.get(key, "0")) for key in ("xtl", "ytl", "xbr", "ybr"))
            else:
                item["points"] = [tuple(float(v) for v in pair.split(","))
                                  for pair in node.get("points", "").split(";") if pair]
            shapes.append(item)
        images[name] = {"shapes": shapes, "size": (int(image.get("width", "0")),
                                                    int(image.get("height", "0")))}
    return {"images": images, "meta": root.findtext(".//meta//name") or ""}


def parse_file(path):
    return parse_bytes(xml_bytes(path))


def boxes(document, frame):
    return [s for s in document["images"].get(frame, {}).get("shapes", []) if s["kind"] == "box"]


def polygons(document, frame, label=None):
    return [s for s in document["images"].get(frame, {}).get("shapes", [])
            if s["kind"] == "polygon" and (label is None or s["label"] == label)]
