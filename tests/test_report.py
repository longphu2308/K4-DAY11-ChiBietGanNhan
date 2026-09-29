import unittest

from svm11.report import three_way_cell, zone_counts, group_three, _overlay


class ReportTest(unittest.TestCase):
    def test_three_way_cells(self):
        self.assertEqual(three_way_cell(True, True, True), "LRM")
        self.assertEqual(three_way_cell(True, False, True), "LM_noR")
        self.assertEqual(three_way_cell(False, True, True), "RM_noL")
        self.assertEqual(three_way_cell(False, False, True), "M_only")

    def test_zone_count_shape(self):
        self.assertEqual(zone_counts([], [], [], (0, 0, 100))["center"],
                         {"n_ref": 0, "matched": 0, "missing": 0, "spurious": 0})

    def test_reference_in_ignore_counts_as_reference(self):
        ref = {"label": "Car", "box": (0, 0, 100, 100), "index": 1}
        poly = [(0, 0), (100, 0), (100, 100), (0, 100)]
        self.assertEqual(zone_counts([], [ref], [poly], (0, 0, 1000))["center"]["n_ref"], 1)

    def test_three_way_group_uses_model_once(self):
        def item(index, x):
            return {"label": "Car", "box": (x, 0, x + 100, 100), "index": index}
        left, refs, model = [item(1, 0), item(2, 20)], [item(1, 0), item(2, 20)], [item(1, 10)]
        groups = group_three(left, refs, model)
        self.assertEqual(sum(group[2] is model[0] for group in groups), 1)
        self.assertEqual(len(groups), 2)

    def test_overlay_uses_diagnostic_colors_and_escapes_text(self):
        missing = {"label": "Car<&", "box": (0, 0, 50, 50), "index": 1}
        spurious = {"label": "Bus", "box": (60, 0, 100, 50), "index": 1}
        markup = _overlay("f<&.jpg", (200, 100), {"R": [missing], "L": [spurious]},
                          "../../assets/images/f<&.jpg",
                          {id(missing): "MISSING", id(spurious): "SPURIOUS"})
        self.assertIn('data-status="MISSING"', markup)
        self.assertIn('data-status="SPURIOUS"', markup)
        self.assertIn("Car&lt;&amp;", markup)
        self.assertNotIn("f<&.jpg", markup)
