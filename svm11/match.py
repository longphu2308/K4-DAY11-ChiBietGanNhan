"""Greedy CVAT box matching and diagnostic reasons."""
from .zones import ignored, zone, truncated


def iou(a, b):
    overlap = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    return overlap / (area_a + area_b - overlap or 1)


def match_pairs(left, right, threshold=.5):
    candidates = sorted(((iou(a["box"], b["box"]), ai, bi) for ai, a in enumerate(left)
                         for bi, b in enumerate(right) if a["label"] == b["label"]),
                        key=lambda item: (-item[0], item[1], item[2]))
    used_a, used_b, pairs = set(), set(), []
    for value, ai, bi in candidates:
        if value < threshold:
            break
        if ai not in used_a and bi not in used_b:
            pairs.append((left[ai], right[bi]))
            used_a.add(ai)
            used_b.add(bi)
    return pairs


def classify(left, right, ignore_polys, circle, size=(1920, 1080)):
    ignored_left = [a for a in left if ignored(a["box"], ignore_polys)]
    active = [a for a in left if a not in ignored_left]
    pairs = match_pairs(active, right)
    used_l = {id(a) for a, _ in pairs}
    used_r = {id(b) for _, b in pairs}
    out = []

    def emit(what, a=None, b=None):
        ref = "+".join(("L%d" % a["index"] if a else "", "R%d" % b["index"] if b else "")).strip("+")
        item = {"what": what, "object_ref": ref, "zone": zone((b or a)["box"], circle),
                "left": a, "right": b}
        out.append(item)

    for a in ignored_left:
        emit("IGNORE_SCOPE", a)
    for a, b in pairs:
        value = a.get("attrs", {}).get("truncated", "false").lower() in ("true", "1")
        if value != truncated(a["box"], circle, size):
            emit("ATTRIBUTE", a, b)
    for a in active:
        if id(a) in used_l:
            continue
        candidates = sorted(((iou(a["box"], b["box"]), b) for b in right),
                            key=lambda item: (-item[0], item[1]["index"]))
        same_class = next(((value, b) for value, b in candidates if b["label"] == a["label"]), None)
        free_same = next(((value, b) for value, b in candidates
                          if b["label"] == a["label"] and id(b) not in used_r), None)
        wrong_class = next(((value, b) for value, b in candidates
                            if value >= .5 and b["label"] != a["label"] and id(b) not in used_r), None)
        if wrong_class:
            emit("WRONG_CLASS", a, wrong_class[1])
            used_r.add(id(wrong_class[1]))
        elif free_same and .3 <= free_same[0] < .5:
            emit("BOX_GEOMETRY", a, free_same[1])
            used_r.add(id(free_same[1]))
        elif same_class and same_class[0] >= .5:
            emit("DUPLICATE", a, same_class[1])
        else:
            emit("SPURIOUS", a)
    for b in right:
        if id(b) not in used_r:
            emit("MISSING", b=b)
    return out
