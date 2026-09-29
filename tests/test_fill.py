import unittest

from svm11.qc import fill_ratios, polygon_area


class FillTest(unittest.TestCase):
    def test_shoelace_and_group_pairing(self):
        self.assertEqual(polygon_area([(0, 0), (10, 0), (10, 10), (0, 10)]), 100)
        box = {"kind": "box", "label": "Car", "group_id": "7", "box": (0, 0, 10, 10)}
        poly = {"kind": "polygon", "label": "Car", "group_id": "7",
                "points": [(0, 0), (5, 0), (5, 10), (0, 10)]}
        result = fill_ratios([box, poly])
        self.assertEqual(result, [(box, .5)])

    def test_group_zero_uses_geometry(self):
        first = {"kind": "box", "label": "Car", "group_id": "0", "box": (0, 0, 10, 10)}
        second = {"kind": "box", "label": "Car", "group_id": "0", "box": (20, 0, 30, 10)}
        poly = {"kind": "polygon", "label": "Car", "group_id": "0",
                "points": [(20, 0), (30, 0), (30, 10), (20, 10)]}
        self.assertEqual(fill_ratios([first, second, poly]), [(second, 1.0)])
