import tempfile
import unittest
from pathlib import Path

from svm11 import LabError
from svm11.parking import save_export, validate_export


def export_xml(image="parking-lot-core.jpg", second_line=True):
    lines = '<polyline label="parking_line" points="1,1;2,2"/>'
    if second_line:
        lines += '<polyline label="parking_line" points="3,3;4,4"/>'
    return ('<annotations><version>1.1</version><image id="0" name="' + image + '" '
            'width="960" height="720">' + lines +
            '<polygon label="free_space" points="10,10;20,10;20,20"/>'
            '</image></annotations>').encode()


class ParkingExportTest(unittest.TestCase):
    def test_save_valid_export(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source = base / "download.xml"
            source.write_bytes(export_xml())
            target, counts = save_export(base, source)
            self.assertEqual(target, base / "submission/parking/annotations.xml")
            self.assertEqual(target.read_bytes(), source.read_bytes())
            self.assertEqual(counts, (2, 1))

    def test_rejects_road_image_or_incomplete_shapes(self):
        with self.assertRaises(LabError):
            validate_export(export_xml("street.jpg"))
        with self.assertRaises(LabError):
            validate_export(export_xml(second_line=False))


if __name__ == "__main__":
    unittest.main()
