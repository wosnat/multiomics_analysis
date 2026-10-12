"""Toy tests for analysis/expr.py (rank percentiles and slice QC). Run from the repo root:
  .venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/analysis/tests
"""
import math
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import expr  # noqa: E402


def slice_df(vals, scope="all_detected_genes", exp="e1", tp="t1"):
    return pd.DataFrame({"experiment_id": exp, "timepoint": tp, "table_scope": scope,
                         "locus_tag": [f"g{i}" for i in range(len(vals))], "log2fc": vals})


class TestRankPercentile(unittest.TestCase):
    def test_simple(self):
        out = expr.add_rank_percentile(slice_df([3.0, 1.0, 2.0, -1.0])).set_index("locus_tag")
        # positions: g0=1, g2=2, g1=3, g3=4; n=4 -> 1 - (pos-1)/4
        self.assertEqual(out.loc["g0", "rank_percentile"], 1.0)
        self.assertEqual(out.loc["g2", "rank_percentile"], 0.75)
        self.assertEqual(out.loc["g1", "rank_percentile"], 0.5)
        self.assertEqual(out.loc["g3", "rank_percentile"], 0.25)
        self.assertTrue((out.n_detected_in_slice == 4).all())
        self.assertTrue(out.percentile_valid.all())

    def test_ties_use_mean_position(self):
        out = expr.add_rank_percentile(slice_df([2.0, 2.0, 1.0, 0.0])).set_index("locus_tag")
        # g0, g1 tie for positions 1 and 2 -> mean position 1.5 -> 1 - 0.5/4 = 0.875
        self.assertEqual(out.loc["g0", "rank_percentile"], 0.875)
        self.assertEqual(out.loc["g1", "rank_percentile"], 0.875)
        self.assertEqual(out.loc["g2", "rank_percentile"], 0.5)
        self.assertEqual(out.loc["g0", "rank_position"], 1.5)

    def test_n_equals_one(self):
        out = expr.add_rank_percentile(slice_df([-5.0]))
        self.assertEqual(out.rank_percentile.iloc[0], 1.0)
        self.assertEqual(out.n_detected_in_slice.iloc[0], 1)

    def test_slices_are_independent(self):
        df = pd.concat([slice_df([1.0, 2.0], tp="t1"), slice_df([5.0, 4.0, 3.0], tp="t2")], ignore_index=True)
        out = expr.add_rank_percentile(df)
        self.assertEqual(sorted(out[out.timepoint == "t1"].rank_percentile), [0.5, 1.0])
        self.assertEqual(out[out.timepoint == "t2"].n_detected_in_slice.iloc[0], 3)

    def test_missing_log2fc_not_ranked(self):
        out = expr.add_rank_percentile(slice_df([1.0, float("nan"), 0.5])).set_index("locus_tag")
        self.assertTrue(math.isnan(out.loc["g1", "rank_percentile"]))
        self.assertEqual(out.loc["g0", "n_detected_in_slice"], 2)
        self.assertEqual(out.loc["g2", "rank_percentile"], 0.5)

    def test_filtered_table_flagged(self):
        for scope in ("filtered_subset", "significant_any_timepoint", "significant_only", "top_n"):
            out = expr.add_rank_percentile(slice_df([1.0, 0.0], scope=scope))
            self.assertFalse(out.percentile_valid.any(), scope)
            self.assertEqual(out.percentile_note.iloc[0], "filtered table: positive evidence only")
            self.assertEqual(out.rank_percentile.max(), 1.0)          # still computed
        out = expr.add_rank_percentile(slice_df([1.0, 0.0]))
        self.assertEqual(out.percentile_note.iloc[0], "")


class TestSliceQC(unittest.TestCase):
    def test_qc_row(self):
        df = slice_df([1.0, -1.0, -2.0, 0.5, 0.2])
        df["padj"] = [0.01, 0.2, 0.04, 0.5, None]
        df["expression_status"] = ["significant_up", "not_significant", "significant_down", "not_significant",
                                   "not_significant"]
        q = expr.slice_qc(df, total_matching=5)
        self.assertEqual(q["rows"], 5)
        self.assertEqual(q["duplicate_rows"], 0)
        self.assertAlmostEqual(q["negative_share"], 0.4)
        self.assertTrue(q["negative_share_ok"])
        self.assertEqual(q["n_padj_lt_0.05"], 2)
        self.assertEqual(q["n_status_significant"], 2)
        self.assertEqual(q["n_sig_up"], 1)
        self.assertEqual(q["n_sig_down"], 1)
        # padj < 0.05 but stored not_significant (extra fold-change cutoff in the source): none here
        self.assertEqual(q["n_padj_lt_0.05_not_significant"], 0)
        self.assertEqual(q["min_abs_log2fc_significant"], 1.0)

    def test_padj_vs_status_gap(self):
        df = slice_df([0.59, 2.0, -1.5])
        df["padj"] = [0.0063, 0.001, 0.02]
        df["expression_status"] = ["not_significant", "significant_up", "significant_down"]
        q = expr.slice_qc(df, total_matching=3)
        self.assertEqual(q["n_padj_lt_0.05_not_significant"], 1)
        self.assertEqual(q["min_abs_log2fc_significant"], 1.5)
        self.assertEqual(q["max_abs_log2fc_padj_sig_but_not_significant"], 0.59)

    def test_negative_share_flag_only_for_all_detected(self):
        df = slice_df([1.0, 2.0, 3.0, -1.0])
        self.assertFalse(expr.slice_qc(df, total_matching=4)["negative_share_ok"])
        df2 = slice_df([1.0, 2.0, 3.0, -1.0], scope="filtered_subset")
        self.assertIsNone(expr.slice_qc(df2, total_matching=4)["negative_share_ok"])

    def test_duplicates(self):
        df = pd.concat([slice_df([1.0, 2.0]), slice_df([1.0])], ignore_index=True)
        self.assertEqual(expr.slice_qc(df, total_matching=3)["duplicate_rows"], 1)


class TestPooled(unittest.TestCase):
    def test_is_pooled(self):
        self.assertTrue(expr.is_pooled("days 60+89"))
        self.assertFalse(expr.is_pooled("day 60"))
        self.assertFalse(expr.is_pooled(None))


class TestProposalDay(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(expr.proposal_timepoint("day 14"), "d14")
        self.assertEqual(expr.proposal_timepoint("day 60"), "d60")
        self.assertEqual(expr.proposal_timepoint("days 60+89"), "d60+89 (combined; not used by the proposal)")
        self.assertEqual(expr.proposal_timepoint("12h"), "12 h")
        self.assertEqual(expr.proposal_timepoint("-12h"), "-12 h")
        self.assertEqual(expr.proposal_timepoint(None), "single contrast")



# --------------------------------------------------------------------------- stage 2 helpers
def de_rows(rows):
    """rows: (short, timepoint, locus, status, log2fc, percentile)"""
    return pd.DataFrame(rows, columns=["short_name", "timepoint", "locus_tag", "expression_status", "log2fc",
                                       "rank_percentile"])


class TestSystemStats(unittest.TestCase):
    def setUp(self):
        self.de = de_rows([
            ("p", "day 60", "a", "significant_up", 2.0, 0.95), ("p", "day 60", "b", "not_significant", 0.5, 0.80),
            ("p", "day 60", "c", "significant_down", -1.0, 0.10),
            ("p", "day 89", "a", "significant_up", 2.0, 0.97), ("p", "day 89", "b", "significant_up", 1.5, 0.93),
        ])

    def test_stats(self):
        s = expr.system_stats(self.de, "p", "day 60", ["a", "b", "c", "d"])
        self.assertEqual((s["n_members"], s["n_detected"], s["n_up"], s["n_down"]), (4, 3, 1, 1))
        self.assertAlmostEqual(s["median_percentile"], 0.80)
        self.assertAlmostEqual(s["median_log2fc"], 0.5)
        self.assertEqual(s["not_detected"], "d")
        s89 = expr.system_stats(self.de, "p", "day 89", ["a", "b", "c", "d"])
        self.assertEqual(s89["n_detected"], 2)
        empty = expr.system_stats(self.de, "p", "day 31", ["a"])
        self.assertEqual(empty["n_detected"], 0)
        self.assertTrue(math.isnan(empty["median_percentile"]))

    def test_up_variants(self):
        s = expr.system_stats(self.de, "p", "day 60", ["a", "b", "c"])
        self.assertTrue(expr.up_any(s))
        self.assertFalse(expr.up_any(s, require_no_down=True))
        self.assertFalse(expr.up_half(s))            # 1 of 3 detected
        s89 = expr.system_stats(self.de, "p", "day 89", ["a", "b", "c"])
        self.assertTrue(expr.up_half(s89))           # 2 of 2 detected
        none = expr.system_stats(self.de, "p", "day 31", ["a"])
        self.assertFalse(expr.up_half(none))
        self.assertFalse(expr.up_any(none))

    def test_criterion_b(self):
        self.assertTrue(expr.crit_b(0.95, 0.92, 0.80))
        self.assertFalse(expr.crit_b(0.95, 0.89, 0.50))      # below 0.90 at d89
        self.assertFalse(expr.crit_b(0.95, 0.92, 0.85))      # margin 0.07 < 0.10 at d89
        self.assertTrue(expr.crit_b(0.95, 0.95, 0.85))       # margin exactly 0.10
        self.assertFalse(expr.crit_b(float("nan"), 0.95, 0.5))
        self.assertFalse(expr.crit_b(0.95, 0.95, float("nan")))

    def test_criterion_a(self):
        s60 = expr.system_stats(self.de, "p", "day 60", ["a", "b"])
        s89 = expr.system_stats(self.de, "p", "day 89", ["a", "b"])
        self.assertTrue(expr.crit_a(s60, s89, 0.3, 0.1, "any"))
        self.assertFalse(expr.crit_a(s60, s89, 0.3, -0.1, "any"))     # RNA median must be > 0 at both
        self.assertTrue(expr.crit_a(s60, s89, 0.3, 0.1, "half"))      # 1 of 2 = half
        s60c = expr.system_stats(self.de, "p", "day 60", ["a", "b", "c"])
        self.assertFalse(expr.crit_a(s60c, s89, 0.3, 0.1, "any"))     # a down subunit at d60

    def test_c4_variants(self):
        grid = {"12h": {"a": "significant_up", "b": "not_significant", "c": "not_significant"},
                "24h": {"a": "not_significant", "b": "not_significant"}}
        self.assertTrue(expr.c4_any(grid))
        self.assertFalse(expr.c4_half(grid))
        grid2 = {"12h": {"a": "significant_up", "b": "significant_up", "c": "not_significant"}}
        self.assertTrue(expr.c4_half(grid2))
        self.assertFalse(expr.c4_any({"12h": {}}))


if __name__ == "__main__":
    unittest.main()
