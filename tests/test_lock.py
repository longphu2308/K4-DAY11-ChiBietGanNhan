import json
import tempfile
import unittest
from pathlib import Path

from svm11 import LabError
from svm11.locking import lock_export, reveal_reference
from svm11.workflow import cvat


def xml(source="file", x=0):
    return ('''<annotations><version>1.1</version><image id="0" name="f.jpg" width="200" height="200">
    <box label="Car" source="%s" xtl="%s" ytl="0" xbr="100" ybr="100"/>
    </image></annotations>''' % (source, x)).encode()


class LockTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        (self.base / "assets").mkdir()
        (self.base / "assets" / "slices.json").write_text(json.dumps({"C0": {"frame": "f.jpg"}}))
        (self.base / "assets" / "labels.json").write_text(json.dumps([{"name": "Car"}]))
        (self.base / "submission" / "00_setup").mkdir(parents=True)
        (self.base / "submission" / "00_setup" / "mode.json").write_text('{"slice":"C0"}')
        (self.base / "assets" / "prefill").mkdir()
        (self.base / "assets" / "prefill" / "C0.xml").write_bytes(xml())
        self.source = self.base / "export.xml"
        self.source.write_bytes(xml())

    def tearDown(self):
        self.tmp.cleanup()

    def test_code_relock_and_integrity(self):
        code = lock_export(self.base, "calib", self.source)
        self.assertRegex(code, r"^[A-F0-9]{4}-[A-F0-9]{4}$")
        self.assertIn("prefill_kept: 1", (self.base / "submission/p1_calib/lock.txt").read_text())
        self.source.write_bytes(xml("manual", 10))
        with self.assertRaises(LabError):
            lock_export(self.base, "calib", self.source)
        lock_export(self.base, "calib", self.source, relock=True)
        self.assertIn("prefill_edited: 1", (self.base / "submission/p1_calib/lock.txt").read_text())
        expanded = xml("manual", 10).replace(b"</image>",
            b'<box label="Car" source="manual" xtl="120" ytl="0" xbr="180" ybr="100"/></image>')
        self.source.write_bytes(expanded)
        lock_export(self.base, "calib", self.source, relock=True)
        self.assertIn("new: 1", (self.base / "submission/p1_calib/lock.txt").read_text())
        (self.base / "submission/p1_calib/annotations.xml").write_bytes(xml())
        with self.assertRaises(LabError):
            reveal_reference(self.base, "calib")

    def test_support_prefill_class_change_and_one_to_one(self):
        (self.base / "assets/slices.json").write_text(json.dumps({"C0": {"frame": "f.jpg"},
            "slices": [{"slice": "B1-edge", "frames": ["f.jpg"]}]}))
        (self.base / "assets/labels.json").write_text(json.dumps([{"name": "Car"}, {"name": "Bus"}]))
        (self.base / "assets/prefill/B1-edge.xml").write_bytes(xml("file", 0))
        support = ('<annotations><version>1.1</version><image id="0" name="f.jpg" width="200" height="200">'
                   '<box label="Car" source="file" xtl="120" ytl="0" xbr="180" ybr="100"/>'
                   '</image></annotations>')
        (self.base / "assets/prefill/B1-edge-support.xml").write_text(support)
        cvat(self.base, "B1-edge", support=True)
        state = json.loads((self.base / "submission/00_setup/mode.json").read_text())
        self.assertTrue(state["support_prefill"])
        export = support.replace('label="Car" source="file"', 'label="Bus" source="manual"')
        export = export.replace('</image>', '<box label="Bus" source="manual" xtl="122" ytl="0" xbr="182" ybr="100"/></image>')
        self.source.write_text(export)
        lock_export(self.base, "r1_craft", self.source)
        values = (self.base / "submission/r1_craft/lock.txt").read_text()
        self.assertIn("prefill_edited: 1", values)
        self.assertIn("new: 1", values)
