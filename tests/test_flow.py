import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from svm11.locking import lock_export, reveal_reference
from svm11.report import compare, iou_sweep, model


XML = (Path(__file__).parent / "fixtures" / "tiny-cvat.xml").read_text(encoding="utf-8")


class FlowTest(unittest.TestCase):
    def test_lock_reveal_compare_model_sweep(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text(json.dumps({"slices": [{"slice": "B1-edge", "frames": ["f.jpg"]}]}))
            (base / "assets/labels.json").write_text('[{"name":"Car"},{"name":"ignore_region"}]')
            (base / "assets/frames.csv").write_text("frame,file,cx,cy,r\n0,f.jpg,100,100,100\n")
            (base / "assets/model-yolo26m.xml").write_text(XML)
            (base / "submission/00_setup").mkdir(parents=True)
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            (base / "refs").mkdir()
            with zipfile.ZipFile(base / "refs/slice-B1-edge.zip", "w") as archive:
                archive.writestr("opaque.xml", XML)
            export = base / "export.xml"; export.write_text(XML)
            lock_export(base, "r1_craft", export)
            reveal_reference(base, "r1_craft")
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B4-mid"}')
            self.assertEqual(compare(base, "r1_craft")["edge"]["n_ref"], 1)
            self.assertTrue((base / "submission/r1_craft/compare.html").is_file())
            export.write_text('<annotations><version>1.1</version><image id="0" name="f.jpg" width="200" height="200"/></annotations>')
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            lock_export(base, "r1_craft", export, relock=True)
            (base / "submission/00_setup/mode.json").write_text('{"slice":"B4-mid"}')
            ref = base / "data/_ref/B1-edge.xml"
            ref.write_text(XML.replace('</image>',
                '<polygon label="ignore_region" points="0,0;100,0;100,100;0,100"/></image>'))
            self.assertEqual(compare(base, "r1_craft")["edge"]["n_ref"], 1)
            markup = (base / "submission/r1_craft/compare.html").read_text()
            self.assertIn('data-status="MISSING"', markup)
            self.assertIn('stroke="#ef4444"', markup)
            self.assertEqual(model(base)["edge"]["R_only"], 1)
            table = base / "submission/r3_diag/zone_table.md"
            self.assertIn("| edge | 1 | 1 | 0 | 1 | 0 | MISSING (1) |", table.read_text())
            table.write_text(table.read_text().replace("TODO", "Edge gãy vì méo", 1))
            model(base)
            self.assertIn("Edge gãy vì méo", table.read_text())
            table.write_text(table.read_text().replace("## Nhận xét", "## Em nhận xét"))
            model(base)
            self.assertIn("Edge gãy vì méo", table.read_text())
            self.assertIn("## Bản cũ", table.read_text())
            self.assertIn("0.50", iou_sweep(base, [.3, .5, .7]))
