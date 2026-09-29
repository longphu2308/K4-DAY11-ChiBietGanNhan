import tempfile
import unittest
import io
import contextlib
from pathlib import Path
from unittest.mock import patch

from svm11.quality import cvat_quality, Cvat


class QualityTest(unittest.TestCase):
    def test_failure_is_single_line_and_no_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch("svm11.quality.Cvat", side_effect=RuntimeError("offline secret")), \
                 patch.dict("os.environ", {"CVAT_TOKEN": "secret"}):
                message = cvat_quality(Path(temp), task_id=3)
            result = (Path(temp) / "submission/r3_diag/cvat_quality.md").read_text()
            self.assertEqual(result, "không chạy được: offline [ẩn]\n")
            self.assertIn("python3 lab11.py local-quality", message)

    def test_success_calls_ground_truth_settings_and_report(self):
        calls = self.run_success(project_id=5)
        self.assertIn(("GET", "/api/quality/settings?project_id=5", None), calls)

    def test_standalone_task_uses_its_own_settings(self):
        calls = self.run_success(project_id=None)
        self.assertIn(("GET", "/api/quality/settings?task_id=3", None), calls)

    def run_success(self, project_id):
        settings_path = "/api/quality/settings?" + ("project_id=%s" % project_id if project_id else "task_id=3")
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "submission/00_setup").mkdir(parents=True)
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            ref = base / "data/_ref/B1-edge.xml"
            ref.parent.mkdir(parents=True)
            ref.write_text('<annotations><version>1.1</version><image id="0" name="f.jpg" width="200" height="200">'
                           '<polygon label="ignore_region" points="0,0;100,0;100,100;0,100"/>'
                           '</image></annotations>')
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text('{"slices":[{"slice":"B1-edge","frames":["f.jpg"]}]}')
            calls = []

            class FakeCvat:
                def call(self, method, path, body=None, files=None, auth=True):
                    calls.append((method, path, body))
                    if path.startswith("/api/tasks/3"):
                        return {"id": 3, "name": "Day11 · ADASIND · B1-edge · raw_fisheye", "project_id": project_id}
                    if path == "/api/jobs/4/annotations":
                        # 26 is a polygon: its first two vertices lie mostly outside, its bounding box mostly inside
                        return {"shapes": [{"id": 25, "frame": 0, "points": [10, 10, 50, 50]},
                                           {"id": 26, "frame": 0, "points": [95, 5, 160, 95, 5, 95, 5, 5]}]}
                    if path == "/api/jobs" and method == "POST": return {"id": 7}
                    if path.startswith("/api/jobs/7/annotations?"): return {"rq_id": "import"}
                    if path == "/api/quality/reports" and method == "POST": return {"rq_id": "report"}
                    return {}

                def results(self, path):
                    calls.append(("GET", path, None))
                    if path == "/api/jobs?task_id=3": return []
                    if path == settings_path: return [{"id": 11}]
                    if path == "/api/quality/settings/requirements?settings_id=11":
                        return [{"id": 12, "name": "Base rectangle"}, {"id": 13, "name": "Base polygon"}]
                    if path.startswith("/api/quality/reports?"): return [{"id": 9, "summary": {"accuracy": .5}}]
                    if path == "/api/quality/conflicts?report_id=9":
                        return [{"type": "missing_annotation"},
                                {"type": "extra_annotation", "frame": 0,
                                 "annotation_ids": [{"job_id": 4, "obj_id": 25, "type": "shape"}]},
                                {"type": "extra_annotation", "frame": 0,
                                 "annotation_ids": [{"job_id": 4, "obj_id": 26, "type": "shape"}]}]
                    return []

                def wait(self, request_id): calls.append(("WAIT", request_id, None))

            with patch("svm11.quality.Cvat", FakeCvat):
                message = cvat_quality(base, task_id=3)
            text = (base / "submission/r3_diag/cvat_quality.md").read_text()
            self.assertIn("missing_annotation: 1", text)
            self.assertIn("extra trong ignore_region reference: 2", text)
            self.assertIn(("GET", "/api/jobs/4/annotations", None), calls)
            self.assertIn("quality report", message)
            self.assertIn(("POST", "/api/jobs", {"type": "ground_truth", "task_id": 3,
                                                    "frame_selection_method": "manual", "frames": [0, 1, 2]}), calls)
            self.assertIn(("PATCH", "/api/jobs/7", {"stage": "acceptance", "state": "completed"}), calls)
            self.assertIn(("PATCH", "/api/quality/settings/requirements/12",
                           {"enabled": True, "iou_threshold": .5}), calls)
            self.assertIn(("PATCH", "/api/quality/settings/requirements/13", {"enabled": False}), calls)
            self.assertIn(("POST", "/api/quality/reports", {"task_id": 3}), calls)
            order = [(method, path) for method, path, _ in calls]
            positions = [next(i for i, value in enumerate(order) if value[0] == method and value[1].startswith(path))
                         for method, path in (("POST", "/api/jobs"), ("POST", "/api/jobs/7/annotations"),
                                              ("WAIT", "import"), ("PATCH", "/api/jobs/7"),
                                              ("PATCH", "/api/quality/settings/requirements/12"),
                                              ("POST", "/api/quality/reports"), ("WAIT", "report"),
                                              ("GET", "/api/quality/reports?"),
                                              ("GET", "/api/quality/conflicts?"))]
            self.assertEqual(positions, sorted(positions))
            return calls

    def test_login_uses_prompted_password_without_output_or_disk(self):
        requests = []

        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b'{"key":"session-key"}'

        def urlopen(request, timeout):
            requests.append(request)
            return Response()

        out, err = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory() as temp, \
             patch("builtins.input", return_value="student"), \
             patch("svm11.quality.getpass.getpass", return_value="secret-pass"), \
             patch("svm11.quality.urllib.request.urlopen", side_effect=urlopen), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            api = Cvat(environ={"CVAT_URL": "http://localhost:8080"})
            self.assertEqual(list(Path(temp).iterdir()), [])
        self.assertEqual(api.auth, "Token session-key")
        self.assertIn(b"secret-pass", requests[0].data)
        self.assertNotIn("secret-pass", out.getvalue() + err.getvalue())

    def test_pagination_and_request_polling(self):
        api = Cvat(environ={"CVAT_TOKEN": "token"})
        with patch.object(api, "call", side_effect=[
            {"results": [{"id": 1}], "next": "/second"},
            {"results": [{"id": 2}], "next": None}]):
            self.assertEqual(api.results("/first"), [{"id": 1}, {"id": 2}])
        with patch.object(api, "call", side_effect=[{"status": "queued"},
                                                     {"status": "started"},
                                                     {"status": "finished"}]) as call, \
             patch("svm11.quality.time.sleep"):
            api.wait("rq id")
            self.assertEqual(call.call_count, 3)
            self.assertEqual(call.call_args.args[1], "/api/requests/rq%20id")
