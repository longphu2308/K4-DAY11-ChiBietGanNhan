import tempfile
import unittest
from pathlib import Path

from svm11 import LabError
from svm11.common import digest
from svm11.locking import lock_export
from svm11.qc import fill, selfqc, stage_draft


class DraftQCTest(unittest.TestCase):
    def test_stage_draft_makes_export_available_to_selfqc(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text('{"slices":[{"slice":"B1-center","frames":["adasind_006840.jpg"]}]}')
            (base / "assets/frames.csv").write_text("frame,file,cx,cy,r\n0,adasind_006840.jpg,50,50,100\n")
            (base / "submission/00_setup").mkdir(parents=True)
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B1-center"}')
            export = base / "download.xml"
            export.write_text('<annotations><version>1.1</version><meta><task><name>raw_fisheye</name></task></meta>'
                              '<image id="0" name="adasind_006840.jpg" width="100" height="100">'
                              '<polygon label="ignore_region" points="0,0;10,0;10,10">'
                              '<attribute name="reason">lens_border</attribute></polygon></image></annotations>')
            self.assertEqual(stage_draft(base, export), base / "exports/r1-draft.xml")
            report = selfqc(base).read_text()
            self.assertNotIn("thiếu ego_body", report)
            self.assertNotIn("ego_body thừa", report)

    def test_partial_draft_rejected_and_selfqc_flags_legacy_partial_export(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text(
                '{"slices":[{"slice":"B1-edge","frames":["a.jpg","b.jpg"]}]}')
            (base / "assets/frames.csv").write_text(
                "frame,file,cx,cy,r\n0,a.jpg,50,50,100\n1,b.jpg,50,50,100\n")
            (base / "submission/00_setup").mkdir(parents=True)
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            export = base / "partial.xml"
            export.write_text('<annotations><version>1.1</version>'
                              '<image id="0" name="a.jpg" width="100" height="100"/></annotations>')
            with self.assertRaisesRegex(LabError, "b.jpg"):
                stage_draft(base, export)
            (base / "assets/labels.json").write_text('[{"name":"Car"}]')
            with self.assertRaisesRegex(LabError, "b.jpg"):
                lock_export(base, "r1_craft", export)
            (base / "exports").mkdir()
            (base / "exports/r1.xml").write_bytes(export.read_bytes())
            self.assertIn("Thiếu frame trong export: b.jpg", selfqc(base).read_text())

    def test_locked_final_takes_precedence_over_staged_draft(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text(
                '{"slices":[{"slice":"B1-edge","frames":["f.jpg"]}]}')
            (base / "assets/frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,50,50,100\n")
            (base / "submission/00_setup").mkdir(parents=True)
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            draft = base / "draft.xml"
            draft.write_text('<annotations><version>1.1</version>'
                             '<image id="0" name="f.jpg" width="100" height="100"/></annotations>')
            stage_draft(base, draft)
            final = base / "submission/r1_craft/annotations.xml"
            final.parent.mkdir(parents=True)
            final.write_text('<annotations><version>1.1</version>'
                             '<image id="0" name="f.jpg" width="100" height="100">'
                             '<box label="Car" xtl="0" ytl="5" xbr="50" ybr="65" group_id="7"/>'
                             '<polygon label="Car" group_id="7" points="0,5;50,5;50,65;0,65"/>'
                             '</image></annotations>')
            (final.parent / "lock.txt").write_text("sha256: %s\n" % digest(final.read_bytes()))
            self.assertIn("mean", fill(base).read_text())
            self.assertIn("truncated khác dự kiến", selfqc(base).read_text())

    def test_selfqc_and_fill_before_lock_from_repo_export(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "exports").mkdir()
            (base / "assets").mkdir()
            (base / "assets/frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,50,50,100\n")
            (base / "exports/r1.xml").write_text('''<annotations><version>1.1</version>
            <meta><task><name>raw_fisheye</name></task></meta>
            <image id="0" name="f.jpg" width="100" height="100">
            <box label="Car" xtl="10" ytl="10" xbr="50" ybr="60" group_id="4"/>
            <polygon label="Car" group_id="4" points="10,10;50,10;50,60;10,60"/>
            </image></annotations>''')
            qc = selfqc(base, "r1_craft")
            self.assertTrue(qc.is_file())
            qc.write_text(qc.read_text().replace("- [ ] Class sáu nhãn", "- [x] Class sáu nhãn"))
            self.assertIn("- [x] Class sáu nhãn", selfqc(base, "r1_craft").read_text())
            filled = fill(base, "r1_craft")
            self.assertIn("Fill ratio (K12)", filled.read_text())


class SelfQCFrameTest(unittest.TestCase):
    def test_frame_missing_from_frames_csv_fails_even_without_boxes(self):
        from svm11 import LabError
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "exports").mkdir()
            (base / "assets").mkdir()
            (base / "assets/frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,50,50,100\n")
            (base / "exports/r1.xml").write_text('<annotations><version>1.1</version>'
                                                 '<image id="0" name="g.jpg" width="100" height="100"/></annotations>')
            with self.assertRaises(LabError):
                selfqc(base, "r1_craft")
