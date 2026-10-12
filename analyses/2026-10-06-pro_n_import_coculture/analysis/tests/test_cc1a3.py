"""Toy tests for analysis/cc1a3.py (E15 external CC1A3 culture data helpers)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cc1a3 as cc  # noqa: E402


class TestParseSample(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(cc.parse_sample("P1A"), ("P", 1, "A"))
        self.assertEqual(cc.parse_sample("C4C"), ("C", 4, "C"))
        self.assertEqual(cc.parse_sample("A0B-d15-sybr"), ("A", 0, "B"))
        self.assertIsNone(cc.parse_sample("estimated"))
        self.assertIsNone(cc.parse_sample("blank"))

    def test_condition_names(self):
        self.assertEqual(cc.CONDITION["P"], "axenic MED4")
        self.assertEqual(cc.CONDITION["C"], "coculture")
        self.assertEqual(cc.CONDITION["A"], "HOT1A3 alone")


class TestNBiomass(unittest.TestCase):
    def test_quota(self):
        # 12.5 fg N / MED4 cell, 25 fg N / HOT1A3 cell; uM = cells/ml * fg/14 * 1e-9 * 1e3
        self.assertAlmostEqual(cc.n_biomass_uM(1e6, "MED4"), 0.892857142857, places=9)
        self.assertAlmostEqual(cc.n_biomass_uM(1e7, "HOT1A3"), 17.857142857, places=6)
        self.assertTrue(math.isnan(cc.n_biomass_uM(float("nan"), "MED4")))

    def test_unknown_organism(self):
        with self.assertRaises(KeyError):
            cc.n_biomass_uM(1e6, "SAR11")


class TestDON(unittest.TestCase):
    def test_by_difference_missing_biomass_is_zero(self):
        self.assertAlmostEqual(cc.don_by_difference(185.0, 15.0, 55.0, 20.0), 95.0)
        self.assertAlmostEqual(cc.don_by_difference(184.0, 1.0, float("nan"), 200.0), -17.0)

    def test_total0(self):
        self.assertAlmostEqual(cc.total_n0(147.0, 20.0, 17.0, float("nan")), 184.0)


class TestFirstMatch(unittest.TestCase):
    def test_vlookup_first(self):
        rows = [("A5A", 275.0), ("A5B", 244.8), ("A5B", 254.9), ("A5C", 238.8)]
        self.assertEqual(cc.first_match(rows, "A5B"), 244.8)
        self.assertIsNone(cc.first_match(rows, "Z9Z"))


class TestDayRounding(unittest.TestCase):
    def test_round(self):
        self.assertEqual(cc.day_rounded(10.658333), 11)
        self.assertEqual(cc.day_rounded(13.898611), 14)
        self.assertEqual(cc.day_rounded(59.660417), 60)
        self.assertEqual(cc.day_rounded(30.759722), 31)
        self.assertEqual(cc.day_rounded(17.602778), 18)

    def test_omics_day(self):
        self.assertTrue(cc.is_omics_day("P", 14))
        self.assertTrue(cc.is_omics_day("P", 31))
        self.assertTrue(cc.is_omics_day("P", 89))
        self.assertFalse(cc.is_omics_day("P", 11))
        self.assertTrue(cc.is_omics_day("C", 11))
        self.assertTrue(cc.is_omics_day("C", 60))
        self.assertFalse(cc.is_omics_day("A", 11))


if __name__ == "__main__":
    unittest.main()
