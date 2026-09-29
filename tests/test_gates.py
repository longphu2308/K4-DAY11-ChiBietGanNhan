import csv
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from svm11.gates import check, doctor, _zone_for_row
from svm11.findings import HEADER
from svm11.common import digest


class GatesTest(unittest.TestCase):
    def test_doctor_requires_public_submission_repo(self):
        class CvatResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return b'{"version":"2.74.1"}'

        for visibility, expected in (("PUBLIC", "✓ Repo PUBLIC"),
                                     ("PRIVATE", "✗ Repo cần PUBLIC để chấm bài")):
            with self.subTest(visibility=visibility), tempfile.TemporaryDirectory() as temp:
                calls = [subprocess.CompletedProcess([], 0, "", ""),
                         subprocess.CompletedProcess([], 0, json.dumps({"visibility": visibility}), "")]
                with patch("svm11.gates.urllib.request.urlopen", return_value=CvatResponse()), \
                     patch("svm11.gates.shutil.which", return_value="/usr/bin/gh"), \
                     patch("svm11.gates.subprocess.run", side_effect=calls):
                    messages = doctor(Path(temp))
                self.assertIn(expected, messages)

    def test_bad_review_xml_does_not_crash_zone_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            path = base / "data/_qa/B1-edge.xml"
            path.parent.mkdir(parents=True)
            path.write_text("not xml")
            row = {"round": "r2_qa", "slice": "B1-edge", "frame": "f.jpg", "object_ref": "L1"}
            self.assertIsNone(_zone_for_row(base, row, {"f.jpg": (0, 0, 100)}, {}))
    def test_lr_no_model_does_not_satisfy_model_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            path = base / "submission/findings.csv"
            path.parent.mkdir(parents=True)
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, HEADER)
                writer.writeheader()
                for index in range(8):
                    writer.writerow({"round": "r1_craft", "slice": "B1-edge", "frame": "f.jpg",
                                     "object_ref": "L%d" % (index + 1), "cell": "LR_noM", "what": "MISSING"})
            self.assertTrue(any("≥8 dòng có M" in value for value in check(base)))
    def test_missing_and_filled_fixture(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            failures = check(base)
            self.assertTrue(any("findings" in value for value in failures))
            (base / "assets").mkdir()
            (base / "assets" / "slices.json").write_text(
                '{"slices":[{"slice":"B1-edge","frames":["f.jpg"]}]}')
            (base / "assets" / "frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,0,0,100\n")
            sub = base / "submission"
            (sub / "00_setup").mkdir(parents=True)
            (sub / "00_setup" / "mode.json").write_text('{"slice":"B1-edge"}')
            (sub / "findings.csv").write_text(",".join(HEADER) + "\n")
            failures = check(base)
            self.assertTrue(any("findings" in value for value in failures))
            self.assertTrue(any("decision" in value for value in failures))

    def test_filled_fixture_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            sub = base / "submission"
            (base / "assets").mkdir()
            (base / "assets" / "slices.json").write_text(
                '{"slices":[{"slice":"B1-edge","frames":["f.jpg"]}]}')
            (base / "assets" / "frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,0,0,100\n")
            (sub / "00_setup").mkdir(parents=True)
            (sub / "00_setup" / "mode.json").write_text('{"slice":"B1-edge"}')
            xml = ('<annotations><version>1.1</version><image id="0" name="f.jpg" width="200" height="200">'
                   '<box label="Car" xtl="0" ytl="0" xbr="5" ybr="20"/>'
                   '<box label="Car" xtl="-5" ytl="0" xbr="5" ybr="40"/>'
                   '<box label="Car" xtl="35" ytl="0" xbr="45" ybr="40"/>'
                   '<box label="Car" xtl="65" ytl="0" xbr="75" ybr="40"/>'
                   '</image></annotations>')
            for relative in ("p1_calib/annotations.xml", "r1_craft/annotations.xml", "rework/annotations-v2.xml"):
                path = sub / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(xml)
            ref = base / "data/_ref/B1-edge.xml"; ref.parent.mkdir(parents=True); ref.write_text(xml)
            (base / "assets/model-yolo26m.xml").write_text(xml)
            required = ["00_setup/doctor.txt", "00_setup/sensor_context.md",
                        "p1_calib/lock.txt", "p1_calib/reference.txt", "p1_calib/compare.md", "p1_calib/compare.html",
                        "r1_craft/lock.txt",
                        "r1_craft/selfqc.md", "r1_craft/reference.txt", "r1_craft/compare.md",
                        "r1_craft/compare.html", "r2_qa/qa_review.md", "r2_qa/qa_overlay.html",
                        "r3_diag/local_quality.md", "r3_diag/local_quality.json",
                        "r3_diag/local_quality_conflicts.csv", "r3_diag/local_quality_confusion.csv",
                        "r3_diag/model_compare.md", "r3_diag/model_compare.html",
                        "r3_diag/zone_table.md", "rework/lock2.txt", "rework/delta.md",
                        "10_error_card.md", "20_guideline_patch.md", "30_escalation_ticket.md",
                        "45_review_plan.md", "50_exit_ticket.md"]
            for relative in required:
                path = sub / relative; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("before 2 after 3\n" if relative.endswith("delta.md") else "complete\n")
            value = digest((sub / "r1_craft/annotations.xml").read_bytes())
            (sub / "r1_craft/lock.txt").write_text("sha256: %s\n" % value)
            (sub / "r3_diag/local_quality.json").write_text(json.dumps({"locked_sha256": value}))
            (sub / "40_decision_log.csv").write_text(
                "id,status,rationale\n1,done,a\n2,done,b\n3,done,c\n4,escalated,d\n")
            (sub / "parking/annotations.xml").parent.mkdir(parents=True)
            (sub / "parking/annotations.xml").write_text(
                '<annotations><version>1.1</version><image id="0" name="parking-lot-core.jpg" '
                'width="960" height="720">'
                '<polyline label="parking_line" points="1,1;2,2"/>'
                '<polyline label="parking_line" points="3,3;4,4"/>'
                '<polygon label="free_space" points="10,10;20,10;20,20"/>'
                '</image></annotations>')
            (sub / "parking/observations.md").write_text("Hai vạch chia ô; không vẽ mép lối xe chạy.\n")
            with (sub / "45_sampling_plan.csv").open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["camera_id", "slice_type", "frames", "risk", "rationale"])
                for camera in ("front", "rear", "left", "right"):
                    writer.writerow([camera, "normal", 25, "coverage", "baseline"])
                    writer.writerow([camera, "hard", 25, "ambiguity", "review"])
            (sub / "46_gold_set_plan.md").write_text("Mỗi camera có ca riêng và phân xử theo guideline.\n")
            (sub / "screenshots").mkdir()
            (sub / "screenshots/edge.png").write_bytes(b"image")
            (sub / "screenshots/ignore.png").write_bytes(b"image")
            rows = []
            for number in range(12):
                round_name = ("r1_craft", "r2_qa", "r3_diag", "calib")[number // 3]
                row = dict.fromkeys(HEADER, "")
                row.update(round=round_name, slice="B1-edge", frame="f.jpg",
                           object_ref="L%d" % (number % 3 + 1),
                           cell=("LRM", "LR_noM", "LM_noR", "RM_noL")[number // 3],
                           what="STRUCTURE")
                if round_name == "r2_qa": row["rule_id"] = "R1"
                if round_name == "r3_diag": row.update(why="E1_annotator_error", severity="P2",
                                                       owner="annotator", action="rework")
                rows.append(row)
            with (sub / "findings.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, HEADER); writer.writeheader(); writer.writerows(rows)
            self.assertEqual(check(base), [])
            (sub / "00_setup/mode.json").write_text('{"slice":"B1-edge","degrade":["findings"]}')
            with (sub / "findings.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, HEADER); writer.writeheader()
                writer.writerows(rows[index] for index in (0, 1, 3, 4, 6, 7, 8, 9))
            self.assertEqual(check(base), [])
            (sub / "00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            with (sub / "findings.csv").open("w", newline="") as stream:
                writer = csv.DictWriter(stream, HEADER); writer.writeheader(); writer.writerows(rows)
            (sub / "45_sampling_plan.csv").write_text("camera_id,slice_type,frames,risk,rationale\nfront,normal,200,x,x\n")
            self.assertTrue(any("45_sampling_plan.csv" in error for error in check(base)))
            with (sub / "45_sampling_plan.csv").open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["camera_id", "slice_type", "frames", "risk", "rationale"])
                for camera in ("front", "rear", "left", "right"):
                    writer.writerow([camera, "normal", 25, "coverage", "baseline"])
                    writer.writerow([camera, "hard", 25, "ambiguity", "review"])
            (sub / "r3_diag/local_quality.json").write_text('{"locked_sha256":"stale"}')
            self.assertTrue(any("local_quality cũ" in error for error in check(base)))
            (sub / "r3_diag/local_quality.json").write_text(json.dumps({"locked_sha256": value}))
            (sub / "r3_diag/local_quality_confusion.csv").unlink()
            self.assertIn("Thiếu file r3_diag/local_quality_confusion.csv", check(base))
            (sub / "r3_diag/local_quality_confusion.csv").write_text("reference\\export,Car\n")
            self.assertEqual(check(base), [])
            with (sub / "45_sampling_plan.csv").open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["camera_id", "slice_type", "frames", "risk", "rationale"])
                for camera in ("front", "rear", "left", "right"):
                    writer.writerow([" " + camera, "normal ", " 25 ", " coverage ", "baseline"])
                    writer.writerow([camera + " ", " hard", " 25", "ambiguity", " review "])
            self.assertEqual(check(base), [])
            (sub / "screenshots/ignore.png").rename(sub / "screenshots/.gitkeep")
            self.assertIn("screenshots cần ≥2 ảnh", check(base))
            (sub / "screenshots/.gitkeep").rename(sub / "screenshots/ignore.png")
            (sub / "40_decision_log.csv").write_text(
                "id,status,rationale\n1,done,a\n2,done,b\n3,done,c\n4,done,not escalated\n")
            self.assertTrue(any("decision log" in error for error in check(base)))
