"""Radial zones and reference ignore regions."""


def zone(box, circle):
    cx, cy, radius = circle
    x1, y1, x2, y2 = box
    rr = (((x1 + x2) / 2 - cx) ** 2 + ((y1 + y2) / 2 - cy) ** 2) ** .5 / radius
    return "center" if rr < .35 else "mid" if rr < .6 else "edge"


def in_scope(box, height=40):
    return box[3] - box[1] >= height


def inside(x, y, polygon):
    hit, j = False, len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def ignored(box, polygons, n=10):
    x1, y1, x2, y2 = box
    hits = sum(any(inside(x1 + (i + .5) * (x2 - x1) / n,
                          y1 + (j + .5) * (y2 - y1) / n, polygon)
                   for polygon in polygons) for i in range(n) for j in range(n))
    return hits >= n * n / 2


def truncated(box, circle, size):
    x1, y1, x2, y2 = box
    width, height = size
    if x1 <= 2 or y1 <= 2 or x2 >= width - 2 or y2 >= height - 2:
        return True
    cx, cy, radius = circle
    return any((x - cx) ** 2 + (y - cy) ** 2 > radius ** 2
               for x in (x1, x2) for y in (y1, y2))
