"""Optional CVAT Premium API report; local_quality is the core lab path."""
from collections import Counter
import getpass
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from . import LabError
from .common import chosen_slice, slices
from .cvat_xml import boxes, parse_file, polygons
from .zones import ignored


class Cvat:
    def __init__(self, environ=None):
        env = os.environ if environ is None else environ
        self.url = env.get("CVAT_URL", "http://localhost:8080").rstrip("/")
        self.auth = ""
        if env.get("CVAT_TOKEN"):
            self.auth = "Bearer " + env["CVAT_TOKEN"]
        else:
            user = env.get("CVAT_USER") or input("CVAT username: ")
            password = getpass.getpass("CVAT password: ")
            key = self.call("POST", "/api/auth/login", {"username": user, "password": password}, auth=False)["key"]
            self.auth = "Token " + key

    def call(self, method, path, body=None, files=None, auth=True):
        headers = {"Authorization": self.auth} if auth else {}
        if files is not None:
            boundary = uuid.uuid4().hex
            parts = []
            for field, value in (body or {}).items():
                parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' %
                              (boundary, field, value)).encode())
            for field, filename, data in files:
                parts += [('--%s\r\nContent-Disposition: form-data; name="%s"; filename="%s"\r\n'
                           'Content-Type: application/octet-stream\r\n\r\n' %
                           (boundary, field, filename)).encode() + data + b"\r\n"]
            parts.append(('--%s--\r\n' % boundary).encode())
            payload = b"".join(parts)
            headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
        elif body is not None:
            payload = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        else:
            payload = None
        request = urllib.request.Request(self.url + path if path.startswith("/") else path,
                                         data=payload, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            raise LabError("CVAT HTTP %d tại %s" % (exc.code, path)) from exc
        except urllib.error.URLError as exc:
            raise LabError("Không kết nối được CVAT") from exc
        return json.loads(raw) if raw else {}

    def results(self, path):
        rows = []
        while path:
            page = self.call("GET", path)
            if isinstance(page, list):
                rows += page
                break
            rows += page.get("results", [])
            path = page.get("next")
        return rows

    def wait(self, request_id):
        for _ in range(120):
            state = self.call("GET", "/api/requests/" + urllib.parse.quote(request_id, safe=""))
            if state.get("status") == "finished":
                return
            if state.get("status") == "failed":
                raise LabError("CVAT quality report thất bại")
            time.sleep(1)
        raise LabError("CVAT quality report quá thời gian chờ")


def _quality(base, task_id=None):
    api = Cvat()
    slice_id = chosen_slice(base)
    task_name = "Day11 · ADASIND · %s · raw_fisheye" % slice_id
    if task_id is None:
        tasks = api.results("/api/tasks?search=" + urllib.parse.quote(task_name))
        matches = [task for task in tasks if task.get("name") == task_name]
        if len(matches) != 1:
            raise LabError("Không tìm thấy đúng task %s" % task_name)
        task = matches[0]
    else:
        task = api.call("GET", "/api/tasks/%s" % task_id)
        if task.get("name") != task_name:
            raise LabError("Task ID không khớp tên slice")
    task_id = task["id"]
    jobs = api.results("/api/jobs?task_id=%s" % task_id)
    gt = next((job for job in jobs if job.get("type") == "ground_truth"), None)
    if gt is None:
        gt = api.call("POST", "/api/jobs", {"type": "ground_truth", "task_id": task_id,
                                             "frame_selection_method": "manual", "frames": [0, 1, 2]})
    ref_path = base / "data" / "_ref" / (slice_id + ".xml")
    if not ref_path.is_file():
        raise LabError("Chưa mở reference — chạy python3 lab11.py reference r1_craft")
    query = urllib.parse.urlencode({"format": "CVAT 1.1"})
    import_result = api.call("POST", "/api/jobs/%s/annotations?%s" % (gt["id"], query), {},
                             [("annotation_file", ref_path.name, ref_path.read_bytes())])
    if import_result.get("rq_id"):
        api.wait(import_result["rq_id"])
    api.call("PATCH", "/api/jobs/%s" % gt["id"], {"stage": "acceptance", "state": "completed"})
    project_id = task.get("project_id")
    # a task inside a project inherits the project settings; a standalone task (the guide's flow) has its own
    scope = "project_id=%s" % project_id if project_id else "task_id=%s" % task_id
    settings = api.results("/api/quality/settings?" + scope)
    if not settings:
        raise LabError("Không tìm thấy quality settings (%s)" % scope)
    requirements = api.results("/api/quality/settings/requirements?settings_id=%s" % settings[0]["id"])
    rectangle = next((r for r in requirements if r.get("name") == "Base rectangle"), None)
    if rectangle is None:
        raise LabError("Thiếu requirement Base rectangle")
    api.call("PATCH", "/api/quality/settings/requirements/%s" % rectangle["id"],
             {"enabled": True, "iou_threshold": .5})
    for item in requirements:
        if "polygon" in item.get("name", "").lower():
            api.call("PATCH", "/api/quality/settings/requirements/%s" % item["id"], {"enabled": False})
    result = api.call("POST", "/api/quality/reports", {"task_id": task_id})
    if result.get("rq_id"):
        api.wait(result["rq_id"])
    reports = api.results("/api/quality/reports?task_id=%s&target=task&sort=-id" % task_id)
    if not reports:
        raise LabError("Không tìm thấy quality report")
    report = reports[0]
    conflicts = api.results("/api/quality/conflicts?report_id=%s" % report["id"])
    counts = Counter(item.get("type", "unknown") for item in conflicts)
    document = parse_file(ref_path)
    ignore_by_frame = {frame: [p["points"] for p in polygons(document, frame, "ignore_region")]
                       for frame in document["images"]}
    extra_ignored = 0
    job_shapes = {}
    for conflict in conflicts:
        if conflict.get("type") not in ("extra", "extra_annotation"):
            continue
        frame = conflict.get("frame")
        if frame is None:
            frame = conflict.get("frame_name")
        if isinstance(frame, int):
            names = slices(base)[slice_id]
            frame = names[frame] if 0 <= frame < len(names) else None
        shape = conflict.get("annotation", {})
        if not shape:
            for annotation_id in conflict.get("annotation_ids", []):
                if annotation_id.get("type") != "shape":
                    continue
                job_id = annotation_id.get("job_id")
                if job_id not in job_shapes:
                    data = api.call("GET", "/api/jobs/%s/annotations" % job_id)
                    job_shapes[job_id] = {item.get("id"): item for item in data.get("shapes", [])}
                shape = job_shapes[job_id].get(annotation_id.get("obj_id"), {})
                if shape:
                    break
        if isinstance(shape, dict):
            if frame is None and isinstance(shape.get("frame"), int):
                names = slices(base)[slice_id]
                position = shape["frame"]
                frame = names[position] if 0 <= position < len(names) else None
            coords = shape.get("points") or shape.get("box")
            if isinstance(coords, list) and len(coords) >= 4:
                # CVAT sends flat x,y lists; a polygon has more than two points, so take its bounding box
                xs, ys = coords[0::2], coords[1::2]
                if ignored((min(xs), min(ys), max(xs), max(ys)), ignore_by_frame.get(frame, [])):
                    extra_ignored += 1
    lines = ["# CVAT quality report", "", "Task: %s" % task_name,
             "Report ID: %s" % report["id"], "", "## Summary",
             json.dumps(report.get("summary", {}), ensure_ascii=False, sort_keys=True), "", "## Conflicts by type"]
    lines += ["- %s: %s" % pair for pair in sorted(counts.items())]
    lines.append("- extra trong ignore_region reference: %d" % extra_ignored)
    return "\n".join(lines) + "\n"


def cvat_quality(base, task_id=None):
    path = base / "submission" / "r3_diag" / "cvat_quality.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        content = _quality(base, task_id)
        path.write_text(content, encoding="utf-8")
        return "Đã lưu CVAT quality report: %s" % path
    except Exception as exc:
        message = str(exc).replace("\n", " ").replace("\r", " ")
        for name in ("CVAT_TOKEN", "CVAT_PASSWORD"):
            secret = os.environ.get(name)
            if secret:
                message = message.replace(secret, "[ẩn]")
        path.write_text("không chạy được: %s\n" % message, encoding="utf-8")
        return "CVAT Quality Control không chạy được; dùng python3 lab11.py local-quality cho bài lõi"
