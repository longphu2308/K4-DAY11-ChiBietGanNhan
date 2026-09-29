import json
import shlex
import tempfile
import unittest
from pathlib import Path

from svm11.common import LATE_TEMPLATES, ensure_late_templates
from svm11.workflow import mode, degrade, status, qa, cleanup
from svm11.common import code, digest
from svm11.cli import parser
from svm11 import LabError


class WorkflowTest(unittest.TestCase):
    def test_mode_and_degrade(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets" / "slices.json").write_text(json.dumps({"C0": {"frame": "c.jpg"},
                "slices": [{"slice": "B1-edge", "frames": ["a.jpg"]},
                           {"slice": "B2-mid", "frames": ["b.jpg"]},
                           {"slice": "B3-dense", "frames": ["d.jpg"]}]}))
            with self.assertRaisesRegex(LabError, "--self"):
                mode(base, "chi,an,binh")
            first = mode(base, "chi,an,binh", self_name="binh")
            path = base / "submission/00_setup/mode.json"
            path.write_text(json.dumps(dict(first, current_slice=first["slice"], support_prefill=True)))
            second = mode(base, "binh,chi,an", self_name="binh")
            self.assertEqual(second["current_slice"], first["slice"])
            self.assertTrue(second["support_prefill"])
            self.assertEqual(first["assignments"], second["assignments"])
            self.assertEqual(len(set(first["assignments"].values())), 3)
            self.assertEqual(second["slice"], second["assignments"]["binh"])
            self.assertEqual(second["self"], "binh")
            with self.assertRaisesRegex(LabError, "--self"):
                mode(base, "chi,an,binh", self_name="ngoai-nhom")
            degrade(base, "findings")
            with self.assertRaises(LabError):
                degrade(base, "zone_table")
            self.assertIn("findings", json.loads((base / "submission/00_setup/mode.json").read_text())["degrade"])
            self.assertIsInstance(status(base), str)

    def test_status_command_forms_parse(self):
        commands = (
            "doctor", "mode --members ten", "parking --file parking-export.zip", "cvat C0",
            "lock calib exports/c0.zip", "reference calib", "compare calib", "cvat B1-edge",
            "draft r1-draft.zip", "fill r1_craft", "selfqc r1_craft",
            "lock r1_craft exports/r1.zip",
            "qa --slice B1-edge --file annotations.xml --code XXXX-XXXX",
            "reference r1_craft", "compare r1_craft", "local-quality", "model",
            "iou-sweep --iou 0.3,0.5,0.7", "lock rework exports/r2.zip", "rework", "card", "check",
        )
        for command in commands:
            with self.subTest(command=command):
                parser().parse_args(shlex.split(command))

    def test_late_templates_appear_after_reference_and_never_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets/templates").mkdir(parents=True)
            for name in LATE_TEMPLATES:
                (base / "assets/templates" / name).write_text("TODO " + name)
            (base / "submission/r1_craft").mkdir(parents=True)
            self.assertEqual(ensure_late_templates(base), [])
            self.assertFalse((base / "submission/50_exit_ticket.md").exists())
            (base / "submission/r1_craft/reference.txt").write_text("lock_before_reveal: true\n")
            (base / "submission/20_guideline_patch.md").write_text("written by learner")
            created = ensure_late_templates(base)
            self.assertNotIn("20_guideline_patch.md", created)
            self.assertEqual((base / "submission/20_guideline_patch.md").read_text(), "written by learner")
            self.assertEqual((base / "submission/50_exit_ticket.md").read_text(), "TODO 50_exit_ticket.md")
            self.assertEqual(ensure_late_templates(base), [])

    def test_shipped_late_templates_exist(self):
        base = Path(__file__).resolve().parent.parent
        for name in LATE_TEMPLATES:
            self.assertTrue((base / "assets/templates" / name).is_file(), name)
            self.assertFalse((base / "submission" / name).exists(), name)

    def test_cleanup_requires_learner_root(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "data").mkdir()
            (base / "data/keep.txt").write_text("safe")
            with self.assertRaises(LabError):
                cleanup(base, yes=True)
            self.assertTrue((base / "data/keep.txt").is_file())

    def test_status_single_next_action_and_todo_progression(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            sub = base / "submission"
            self.assertEqual(status(base), "python3 lab11.py doctor")
            for relative in ("00_setup/doctor.txt", "00_setup/sensor_context.md"):
                path = sub / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("done")
            (sub / "00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            self.assertIn("python3 lab11.py parking --file", status(base))
            for relative in ("parking/annotations.xml", "parking/observations.md"):
                path = sub / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("done")
            self.assertEqual(status(base), "python3 lab11.py cvat C0")
            (sub / "00_setup/mode.json").write_text('{"slice":"B1-edge","current_slice":"C0"}')
            self.assertTrue(status(base).startswith("python3 lab11.py lock calib"))
            for relative in ("p1_calib/lock.txt", "p1_calib/reference.txt", "p1_calib/compare.md"):
                path = sub / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("done")
            self.assertEqual(status(base), "python3 lab11.py cvat B1-edge")
            (sub / "00_setup/mode.json").write_text('{"slice":"B1-edge","current_slice":"B1-edge"}')
            (sub / "r1_craft").mkdir()
            (sub / "r1_craft/selfqc.md").write_text("TODO")
            self.assertIn("python3 lab11.py draft", status(base))
            (base / "exports").mkdir()
            (base / "exports/r1-draft.xml").write_text("draft")
            self.assertEqual(status(base), "python3 lab11.py fill r1_craft")
            (sub / "r1_craft/selfqc.md").write_text("## Fill ratio (K12)\ndone")
            self.assertEqual(status(base), "python3 lab11.py selfqc r1_craft")
            checklist = "# Tự soát\n## Checklist thủ công\n" + "\n".join("- [x] item" for _ in range(9))
            (sub / "r1_craft/selfqc.md").write_text(checklist + "\n## Fill ratio (K12)\ndone")
            self.assertTrue(status(base).startswith("python3 lab11.py lock r1_craft"))

    def test_status_checks_final_deliverables(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp); sub = base / "submission"
            names = ("00_setup/doctor.txt", "00_setup/sensor_context.md", "p1_calib/lock.txt",
                     "p1_calib/reference.txt", "p1_calib/compare.md", "r1_craft/selfqc.md",
                     "r1_craft/lock.txt", "r2_qa/qa_review.md", "r1_craft/reference.txt",
                     "r1_craft/compare.md", "r3_diag/local_quality.md", "r3_diag/local_quality.json",
                     "r3_diag/local_quality_conflicts.csv", "r3_diag/local_quality_confusion.csv",
                     "r3_diag/model_compare.md",
                     "r3_diag/iou_sweep.md", "r3_diag/zone_table.md", "rework/lock2.txt",
                     "rework/delta.md", "findings.csv", "10_error_card.md", "20_guideline_patch.md",
                     "30_escalation_ticket.md", "40_decision_log.csv", "45_review_plan.md",
                     "45_sampling_plan.csv", "46_gold_set_plan.md", "50_exit_ticket.md",
                     "parking/annotations.xml", "parking/observations.md")
            for relative in names:
                path = sub / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("done")
            (sub / "00_setup/mode.json").write_text('{"slice":"B1-edge","current_slice":"B1-edge"}')
            (sub / "r1_craft/lock.txt").write_text("sha256: abc\n")
            (sub / "r3_diag/local_quality.json").write_text('{"locked_sha256":"abc"}')
            checklist = "# Tự soát\n## Checklist thủ công\n" + "\n".join("- [x] item" for _ in range(9))
            (sub / "r1_craft/selfqc.md").write_text(checklist + "\nFill ratio (K12)\ndone")
            (sub / "screenshots").mkdir(); (sub / "screenshots/a.png").write_bytes(b"x")
            (sub / "screenshots/b.png").write_bytes(b"x")
            (sub / "r3_diag/zone_table.md").unlink()
            self.assertEqual(status(base), "python3 lab11.py model")
            (sub / "r3_diag/zone_table.md").write_text("done")
            (sub / "10_error_card.md").write_text("# Error card\nTODO")
            self.assertEqual(status(base), "python3 lab11.py card")
            (sub / "10_error_card.md").write_text("# Error analysis card\nTODO")
            self.assertEqual(status(base), "Điền submission/10_error_card.md")
            (sub / "10_error_card.md").write_text("# Error card\nviết tay, không còn chỗ trống")
            (sub / "20_guideline_patch.md").write_text("TODO")
            self.assertEqual(status(base), "Điền submission/20_guideline_patch.md")
            (sub / "10_error_card.md").write_text("# Error analysis card\ndone")
            self.assertEqual(status(base), "Điền submission/20_guideline_patch.md")
            (sub / "20_guideline_patch.md").write_text("done")
            self.assertEqual(status(base), "python3 lab11.py check")
            (sub / "r3_diag/local_quality.md").unlink()
            self.assertEqual(status(base), "python3 lab11.py local-quality")
            (sub / "r3_diag/local_quality.md").write_text("complete\n")
            self.assertEqual(status(base), "python3 lab11.py check")

    def test_qa_keeps_reviewed_xml_for_zone_resolution(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text('{"slices":[{"slice":"B1-edge","frames":["f.jpg"]}]}')
            source = base / "review.xml"
            source.write_text('<annotations><version>1.1</version><image id="0" name="f.jpg" width="100" height="100">'
                              '<box label="Car" xtl="0" ytl="0" xbr="40" ybr="50"/></image></annotations>')
            qa(base, "B1-edge", source, code(digest(source.read_bytes())))
            self.assertEqual((base / "data/_qa/B1-edge.xml").read_bytes(), source.read_bytes())
