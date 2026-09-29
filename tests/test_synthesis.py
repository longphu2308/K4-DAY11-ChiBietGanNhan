import tempfile
import unittest
import json
from pathlib import Path

from svm11.synthesis import card, rework
from svm11.locking import lock_export
from svm11.findings import append_rows
from svm11 import LabError


class SynthesisTest(unittest.TestCase):
    def test_card_keeps_written_prose(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            folder = base / "submission"
            folder.mkdir()
            path = card(base)
            self.assertIn("TODO", path.read_text())
            path.write_text("Human analysis\n")
            card(base)
            self.assertEqual(path.read_text(), "Human analysis\n")

    def test_card_rerun_refreshes_tables_and_keeps_partial_analysis(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "submission").mkdir()
            path = card(base)
            path.write_text(path.read_text().replace("TODO", "E1 box lỏng ở rìa", 1))
            append_rows(base / "submission/findings.csv", [
                {"round": "r3_diag", "slice": "B1-edge", "frame": "f.jpg", "object_ref": "M1",
                 "cell": "M_only", "what": "SPURIOUS"}])
            text = card(base).read_text()
            self.assertIn("E1 box lỏng ở rìa", text)
            self.assertIn("SPURIOUS: 1", text)
            self.assertEqual(text.count("## Phân tích của bạn"), 1)

    def test_card_rerun_keeps_text_when_heading_removed(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "submission").mkdir()
            path = card(base)
            path.write_text(path.read_text().replace("## Phân tích của bạn", "## Ghi chú của em")
                            .replace("TODO", "E1 box lỏng ở rìa", 1))
            text = card(base).read_text()
            self.assertIn("E1 box lỏng ở rìa", text)
            self.assertEqual(text.count("## Phân tích của bạn"), 1)
            self.assertEqual(card(base).read_text().count("E1 box lỏng ở rìa"), 1)

    def test_card_counts_what_by_zone_and_block_from_correct_document(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,0,0,100\n")
            def document(x1, x2):
                return ('<annotations><version>1.1</version><image id="0" name="f.jpg" width="200" height="200">'
                        '<box label="Car" xtl="%d" ytl="0" xbr="%d" ybr="40"/>'
                        '</image></annotations>') % (x1, x2)
            for relative, text in (("assets/model-yolo26m.xml", document(65, 85)),
                                   ("submission/p1_calib/annotations.xml", document(0, 20)),
                                   ("submission/r1_craft/annotations.xml", document(65, 85))):
                path = base / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
            append_rows(base / "submission/findings.csv", [
                {"round": "r3_diag", "slice": "B1-edge", "frame": "f.jpg", "object_ref": "M1",
                 "cell": "M_only", "what": "SPURIOUS"},
                {"round": "calib", "slice": "C0", "frame": "f.jpg", "object_ref": "L1",
                 "cell": "L_only", "what": "ATTRIBUTE"}])
            text = card(base).read_text()
            self.assertIn("| edge | B1 | SPURIOUS | 1 |", text)
            self.assertIn("| center | C0 | ATTRIBUTE | 1 |", text)

    def test_rework_uses_geometry_and_stable_reference_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text(json.dumps({"slices": [{"slice": "B1-edge", "frames": ["f.jpg"]}]}))
            (base / "assets/labels.json").write_text('[{"name":"Car"}]')
            (base / "assets/frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,300,150,300\n")
            (base / "submission/00_setup").mkdir(parents=True)
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            def document(boxes):
                return ('<annotations><version>1.1</version><image id="0" name="f.jpg" width="600" height="300">'
                        + boxes + '</image></annotations>')
            before = base / "before.xml"; after = base / "after.xml"
            left_box = '<box label="Car" xtl="0" ytl="0" xbr="100" ybr="100"/>'
            unrelated = '<box label="Car" xtl="200" ytl="0" xbr="300" ybr="100"/>'
            before.write_text(document(left_box))
            after.write_text(document(unrelated + left_box))
            lock_export(base, "r1_craft", before)
            lock_export(base, "rework", after)
            ref = base / "data/_ref/B1-edge.xml"; ref.parent.mkdir(parents=True)
            ref.write_text(document('<box label="Car" xtl="400" ytl="0" xbr="500" ybr="100"/>'))
            append_rows(base / "submission/findings.csv", [
                {"round": "r3_diag", "slice": "B1-edge", "frame": "f.jpg", "object_ref": "R1+M1",
                 "cell": "RM_noL", "what": "MISSING", "action": "rework"},
                {"round": "r3_diag", "slice": "B1-edge", "frame": "f.jpg", "object_ref": "M1",
                 "cell": "M_only", "what": "SPURIOUS", "action": "rework"},
                {"round": "r1_craft", "slice": "B1-edge", "frame": "f.jpg", "object_ref": "L1",
                 "cell": "L_only", "what": "SPURIOUS", "action": "rework"}])
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B2-mid"}')
            text = rework(base).read_text()
            self.assertIn("R1+M1 MISSING: chưa sửa", text)
            self.assertIn("M1 SPURIOUS: không áp dụng", text)
            self.assertIn("L1 SPURIOUS: chưa sửa", text)
            lock2 = base / "submission/rework/lock2.txt"
            lock2.write_text(lock2.read_text().replace("slice: B1-edge", "slice: B2-mid"))
            with self.assertRaises(LabError):
                rework(base)
