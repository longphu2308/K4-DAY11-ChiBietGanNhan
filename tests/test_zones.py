import unittest

from svm11.zones import zone, ignored, inside, in_scope


class ZonesTest(unittest.TestCase):
    def test_bins_and_height(self):
        circle = (0, 0, 100)
        self.assertEqual(zone((0, 0, 20, 40), circle), "center")
        self.assertEqual(zone((30, 0, 50, 40), circle), "mid")
        self.assertEqual(zone((65, 0, 85, 40), circle), "edge")
        self.assertFalse(in_scope((0, 0, 20, 39)))
        self.assertTrue(in_scope((0, 0, 20, 40)))

    def test_ignore_grid_threshold(self):
        box = (0, 0, 100, 100)
        sixty = [(0, 0), (60, 0), (60, 100), (0, 100)]
        forty = [(0, 0), (40, 0), (40, 100), (0, 100)]
        self.assertTrue(inside(20, 20, sixty))
        self.assertTrue(ignored(box, [sixty]))
        self.assertFalse(ignored(box, [forty]))
