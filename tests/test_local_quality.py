import json
import tempfile
import unittest
from pathlib import Path

from svm11 import LabError
from svm11.common import digest
from svm11.cvat_xml import parse_bytes
from svm11.local_quality import evaluate, local_quality


def xml(boxes, ignored=False):
    region = '<polygon label="ignore_region" points="400,400;520,400;520,520;400,520"/>' if ignored else ""
    return ('<annotations><version>1.1</version><image id="0" name="f.jpg" width="600" height="600">'
            + region + boxes + '</image></annotations>').encode()


def box(label, x, y=0, attrs=""):
    return ('<box label="%s" xtl="%d" ytl="%d" xbr="%d" ybr="%d">%s</box>' %
            (label, x, y, x + 50, y + 50, attrs))


class LocalQualityTest(unittest.TestCase):
    def test_spatial_matching_metrics_and_ignore_region(self):
        left = parse_bytes(xml(box("Car", 0, attrs='<attribute name="truncated">true</attribute>')
                               + box("Pedestrian", 100) + box("Bus", 200) + box("Car", 420, 420)))
        reference = parse_bytes(xml(box("Car", 0, attrs='<attribute name="truncated">false</attribute>')
                                    + box("Bike", 100) + box("Rider", 300), ignored=True))
        result = evaluate(left, reference, ["f.jpg"])
        self.assertEqual(result["counts"], {"tp": 1, "fp": 2, "fn": 2, "outcomes": 4})
        self.assertAlmostEqual(result["aggregate"]["accuracy"]["micro"], .25)
        self.assertAlmostEqual(result["aggregate"]["jaccard"]["micro"], .2)
        self.assertAlmostEqual(result["aggregate"]["dice"]["micro"], 1 / 3)
        self.assertEqual(result["excluded_in_ignore_region"], {"f.jpg": 1})
        self.assertCountEqual([row["type"] for row in result["conflicts"]],
                              ["mismatching_label", "mismatching_attributes",
                               "extra_annotation", "missing_annotation"])
        self.assertEqual(result["labels"]["Car"]["tp"], 1)
        self.assertEqual(result["labels"]["Bike"]["fn"], 1)
        self.assertEqual(result["confusion"]["Bike"]["Pedestrian"], 1)
        self.assertEqual(result["confusion"]["Rider"]["<missing>"], 1)

    def test_empty_comparison_is_not_computed(self):
        result = evaluate(parse_bytes(xml("")), parse_bytes(xml("")), ["f.jpg"])
        self.assertIsNone(result["aggregate"]["precision"]["micro"])
        self.assertIsNone(result["mean_iou_of_correct_matches"])

    def test_omitted_default_attribute_equals_false(self):
        left = parse_bytes(xml(box("Car", 0, attrs='<attribute name="truncated">false</attribute>')))
        reference = parse_bytes(xml(box("Car", 0)))
        result = evaluate(left, reference, ["f.jpg"])
        self.assertEqual(result["conflicts"], [])

    def test_report_requires_intact_lock_and_revealed_reference(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            (base / "assets").mkdir()
            (base / "assets/slices.json").write_text('{"slices":[{"slice":"B1-edge","frames":["f.jpg"]}]}')
            sub = base / "submission"
            (sub / "00_setup").mkdir(parents=True)
            (sub / "00_setup/mode.json").write_text('{"slice":"B1-edge"}')
            source = sub / "r1_craft/annotations.xml"
            source.parent.mkdir()
            source.write_bytes(xml(box("Car", 0)))
            value = digest(source.read_bytes())
            (source.parent / "lock.txt").write_text("slice: B1-edge\nsha256: %s\n" % value)
            with self.assertRaises(LabError):
                local_quality(base)
            reference = base / "data/_ref/B1-edge.xml"
            reference.parent.mkdir(parents=True)
            reference.write_bytes(xml(box("Car", 0)))
            report = local_quality(base)
            self.assertIn("Teaching reference", report.read_text())
            data = json.loads((report.parent / "local_quality.json").read_text())
            self.assertEqual(data["locked_sha256"], value)
            self.assertEqual(data["counts"]["tp"], 1)
            self.assertTrue((report.parent / "local_quality_confusion.csv").is_file())
            source.write_bytes(xml(box("Car", 20)))
            with self.assertRaises(LabError):
                local_quality(base)
