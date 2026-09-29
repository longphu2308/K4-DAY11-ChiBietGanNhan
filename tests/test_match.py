import unittest

from svm11.match import classify, match_pairs


def box(label, rect, index):
    return {"label": label, "box": rect, "index": index, "attrs": {}}


class MatchTest(unittest.TestCase):
    def test_greedy_and_diagnostic_classes(self):
        r = [box("Car", (0, 0, 100, 100), 1), box("Bus", (200, 0, 300, 100), 2)]
        l = [box("Car", (0, 0, 100, 100), 1), box("Car", (0, 0, 100, 100), 2),
             box("Car", (205, 0, 305, 100), 3)]
        self.assertEqual([(a["index"], b["index"]) for a, b in match_pairs(l, r)], [(1, 1)])
        results = classify(l, r, [], (0, 0, 1000))
        self.assertIn("DUPLICATE", [x["what"] for x in results])
        self.assertIn("WRONG_CLASS", [x["what"] for x in results])

    def test_geometry_and_ignored_report(self):
        r = [box("Car", (0, 0, 100, 100), 1)]
        l = [box("Car", (40, 0, 140, 100), 1), box("Bus", (200, 0, 300, 100), 2)]
        poly = [(190, 0), (310, 0), (310, 100), (190, 100)]
        values = classify(l, r, [poly], (0, 0, 1000))
        self.assertIn("BOX_GEOMETRY", [x["what"] for x in values])
        self.assertIn("IGNORE_SCOPE", [x["what"] for x in values])
        self.assertNotIn("SPURIOUS", [x["what"] for x in values])

    def test_reference_inside_ignore_remains_missing(self):
        ref = [box("Car", (0, 0, 100, 100), 1)]
        poly = [(0, 0), (100, 0), (100, 100), (0, 100)]
        self.assertEqual([item["what"] for item in classify([], ref, [poly], (0, 0, 1000))], ["MISSING"])

    def test_geometry_uses_best_same_class_candidate(self):
        left = [box("Bus", (0, 0, 100, 100), 1)]
        right = [box("Car", (38, 0, 138, 100), 1), box("Bus", (48, 0, 148, 100), 2)]
        self.assertEqual([item["what"] for item in classify(left, right, [], (0, 0, 1000)) if item["left"]],
                         ["BOX_GEOMETRY"])

    def test_free_reference_nearby_is_geometry_not_duplicate(self):
        left = [box("Car", (0, 0, 100, 100), 1), box("Car", (30, 0, 130, 100), 2)]
        right = [box("Car", (5, 0, 105, 100), 1), box("Car", (80, 0, 180, 100), 2)]
        results = [(item["what"], item["object_ref"]) for item in classify(left, right, [], (0, 0, 1000))]
        self.assertIn(("BOX_GEOMETRY", "L2+R2"), results)
        self.assertNotIn(("MISSING", "R2"), results)

    def test_wrong_class_precedes_duplicate_for_unmatched_reference(self):
        left = [box("Car", (10, 10, 110, 110), 1), box("Car", (10, 10, 110, 110), 2)]
        right = [box("Car", (10, 10, 110, 110), 1), box("Bus", (20, 10, 120, 110), 2)]
        results = classify(left, right, [], (0, 0, 1000))
        self.assertIn(("WRONG_CLASS", "L2+R2"),
                      [(item["what"], item["object_ref"]) for item in results])
        self.assertNotIn(("MISSING", "R2"),
                         [(item["what"], item["object_ref"]) for item in results])
