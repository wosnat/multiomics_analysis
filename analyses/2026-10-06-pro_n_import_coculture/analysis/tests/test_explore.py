"""Toy tests for analysis/explore.py (correlation, concordance quadrants, relative ranks, stereo-generic compound
equivalence). Run: .venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/analysis/tests
"""
import math
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import explore as ex  # noqa: E402


class TestSpearman(unittest.TestCase):
    def test_perfect_and_inverse(self):
        self.assertAlmostEqual(ex.spearman([1, 2, 3, 4], [10, 20, 30, 40])[0], 1.0)
        self.assertAlmostEqual(ex.spearman([1, 2, 3, 4], [4, 3, 2, 1])[0], -1.0)

    def test_nan_pairs_dropped_and_small_n(self):
        rho, n = ex.spearman([1, 2, float("nan"), 4], [1, 2, 3, 4])
        self.assertEqual(n, 3)
        self.assertAlmostEqual(rho, 1.0)
        rho, n = ex.spearman([1, 2], [2, 1])
        self.assertTrue(math.isnan(rho))
        self.assertEqual(n, 2)

    def test_ties(self):
        rho, _ = ex.spearman([1, 1, 2, 3], [1, 1, 2, 3])
        self.assertAlmostEqual(rho, 1.0)

    def test_constant_is_nan(self):
        self.assertTrue(math.isnan(ex.spearman([1, 1, 1, 1], [1, 2, 3, 4])[0]))


class TestQuadrants(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            "lfc_p": [2.0, 2.0, -1.0, -2.0, 0.5, 0.0],
            "lfc_r": [1.0, -1.0, 1.0, -1.0, -0.5, 1.0],
            "st_p": ["significant_up", "significant_up", "not_significant", "significant_down", "not_significant",
                     "not_significant"],
            "st_r": ["significant_up", "significant_down", "not_significant", "significant_down", "not_significant",
                     "not_significant"]})

    def test_sign_mode(self):
        q = ex.quadrants(self.df, mode="sign")
        self.assertEqual(q["n"], 6)
        self.assertEqual(q["up/up"], 1)
        self.assertEqual(q["up/down"], 2)        # rows 1 and 4 (0.5 / -0.5)
        self.assertEqual(q["down/up"], 1)
        self.assertEqual(q["down/down"], 1)
        self.assertEqual(q["zero"], 1)           # a zero log2FC is not placed in a quadrant
        self.assertAlmostEqual(q["share_up/down"], 2 / 6)

    def test_sig_mode(self):
        q = ex.quadrants(self.df, mode="sig")
        self.assertEqual(q["up/up"], 1)
        self.assertEqual(q["up/down"], 1)
        self.assertEqual(q["down/down"], 1)
        self.assertEqual(q["down/up"], 0)
        self.assertEqual(q["not both significant"], 3)

    def test_empty(self):
        q = ex.quadrants(self.df.iloc[0:0], mode="sign")
        self.assertEqual(q["n"], 0)
        self.assertTrue(math.isnan(q["share_up/up"]))


class TestRelativeRank(unittest.TestCase):
    def test_relative(self):
        self.assertAlmostEqual(ex.relative_rank(0.9, [0.5, 0.7, 0.6]), 0.3)
        self.assertAlmostEqual(ex.relative_rank(0.2, [0.5, float("nan"), 0.7]), -0.4)
        self.assertTrue(math.isnan(ex.relative_rank(float("nan"), [0.5])))
        self.assertTrue(math.isnan(ex.relative_rank(0.5, [])))


class TestStereoGeneric(unittest.TestCase):
    def test_key(self):
        self.assertEqual(ex.stereo_key("L-Cysteine"), ex.stereo_key("Cysteine"))
        self.assertEqual(ex.stereo_key("D-Alanine"), ex.stereo_key("alanine"))
        self.assertEqual(ex.stereo_key("DL-Methionine"), ex.stereo_key("Methionine"))
        self.assertNotEqual(ex.stereo_key("L-Cysteine"), ex.stereo_key("L-Cystine"))
        self.assertEqual(ex.stereo_key("Lacto-N-biose"), "lacto-n-biose")      # 'L' of a word is not a prefix

    def test_merge_groups(self):
        groups = pd.DataFrame({"equiv_group": ["kegg.compound:C00736", "kegg.compound:C00097", "g3", "g4"],
                               "name": ["Cysteine", "L-Cysteine", "Glycine", "L-Serine"],
                               "compound_class": ["amino acids", "amino acids", "amino acids", "amino acids"]})
        m = ex.stereo_equivalents(groups)
        self.assertEqual(m["kegg.compound:C00736"], {"kegg.compound:C00736", "kegg.compound:C00097"})
        self.assertEqual(m["kegg.compound:C00097"], {"kegg.compound:C00736", "kegg.compound:C00097"})
        self.assertEqual(m["g3"], {"g3"})

    def test_only_amino_acid_names_merge(self):
        groups = pd.DataFrame({"equiv_group": ["a", "b"], "name": ["Lactate", "L-Lactate"],
                               "compound_class": ["no_N", "no_N"]})
        m = ex.stereo_equivalents(groups)
        self.assertEqual(m["a"], {"a"})

    def test_explicit_id_pair(self):
        groups = pd.DataFrame({"equiv_group": ["kegg.compound:C00736"], "name": ["Cysteine"],
                               "compound_class": ["amino acids"]})
        m = ex.stereo_equivalents(groups, all_groups=pd.DataFrame(
            {"equiv_group": ["kegg.compound:C00097"], "name": ["L-Cysteine"], "compound_class": ["amino acids"]}))
        self.assertIn("kegg.compound:C00097", m["kegg.compound:C00736"])



class TestAlignedDifference(unittest.TestCase):
    def test_aligned_by_locus(self):
        a = pd.Series({"g1": 2.0, "g2": 1.0, "g3": 0.5})
        b = pd.Series({"g2": 0.5, "g1": 1.0, "g4": 3.0})
        d = ex.aligned_difference(a, b)
        self.assertEqual(sorted(d.index), ["g1", "g2"])          # only loci present in both
        self.assertAlmostEqual(d["g1"], 1.0)
        self.assertAlmostEqual(d["g2"], 0.5)

    def test_nan_dropped(self):
        d = ex.aligned_difference(pd.Series({"g1": float("nan"), "g2": 1.0}), pd.Series({"g1": 1.0, "g2": 1.0}))
        self.assertEqual(list(d.index), ["g2"])



class TestClassifyProfile(unittest.TestCase):
    H = [0, 3, 6, 12, 24, 48]

    def test_flat(self):
        self.assertEqual(ex.classify_profile(self.H, [0.1, 0.2, -0.3, 0.1, 0.0, 0.2])[0], "flat")

    def test_up_early_and_late(self):
        self.assertEqual(ex.classify_profile(self.H, [0, 0.6, 1.5, 2, 2, 1.8])[0], "up, early")
        self.assertEqual(ex.classify_profile(self.H, [0, 0, 0.1, 0.2, 0.9, 1.4])[0], "up, late")

    def test_transient(self):
        self.assertEqual(ex.classify_profile(self.H, [0, 1.0, 1.4, 0.3, 0.0, 0.1])[0], "up, transient")

    def test_down(self):
        self.assertEqual(ex.classify_profile(self.H, [0, -0.2, -0.8, -1.2, -1.5, -1.6])[0], "down, early")
        self.assertEqual(ex.classify_profile(self.H, [0, 0, 0, 0, -0.1, -1.0])[0], "down, late")

    def test_mixed(self):
        self.assertEqual(ex.classify_profile(self.H, [0, 1.0, 0.8, -0.2, -0.9, -1.0])[0], "mixed: up then down")

    def test_onset_reported(self):
        lab, onset, peak = ex.classify_profile(self.H, [0, 0.6, 1.5, 2, 2.5, 1.8])
        self.assertEqual(onset, 3)
        self.assertEqual(peak, 24)

    def test_nan_points_skipped(self):
        self.assertEqual(ex.classify_profile(self.H, [float("nan"), 0.6, 1.5, 2, 2, 1.8])[0], "up, early")


class TestGroupMedianBySlice(unittest.TestCase):
    def test_median_and_n(self):
        mem = pd.DataFrame({"cluster_id": ["c1", "c1", "c1", "c2"], "locus_tag": ["a", "b", "z", "c"]})
        vals = pd.Series({"a": 0.9, "b": 0.7, "c": 0.2})
        out = ex.group_median(mem, vals).set_index("cluster_id")
        self.assertAlmostEqual(out.loc["c1", "median"], 0.8)
        self.assertEqual(out.loc["c1", "n_detected"], 2)
        self.assertEqual(out.loc["c1", "n_members"], 3)
        self.assertEqual(out.loc["c2", "n_detected"], 1)



class TestCellStatus(unittest.TestCase):
    def test_states(self):
        U, D, N = "significant_up", "significant_down", "not_significant"
        self.assertEqual(ex.cell_status([U, N, N])[0], "up")
        self.assertEqual(ex.cell_status([D, N])[0], "down")
        self.assertEqual(ex.cell_status([U, D])[0], "mixed")
        self.assertEqual(ex.cell_status([N, N])[0], "ns")
        self.assertEqual(ex.cell_status([])[0], "not detected")
        self.assertEqual(ex.cell_status([], filtered=True)[0], "not listed")
        self.assertEqual(ex.cell_status([U, U, D, N]), ("mixed", 2, 1, 4))


class TestCocultureFlags(unittest.TestCase):
    def base(self, **kw):
        d = {"cc_d60_status": "up", "cc_d89_status": "up", "ax_d14_status": "ns", "ax_d31_status": "ns",
             "ax_d89_status": "ns", "ax_rna_d14_status": "ns",
             "ndep_statuses": ["ns", "ns", "down"], "ax_d14_pct": 0.5, "ndep_max_pct": 0.8}
        d.update(kw)
        return d

    def test_strict(self):
        self.assertTrue(ex.coculture_flags(self.base())[0])
        self.assertFalse(ex.coculture_flags(self.base(cc_d89_status="ns"))[0])
        self.assertFalse(ex.coculture_flags(self.base(ax_d14_status="up"))[0])
        self.assertFalse(ex.coculture_flags(self.base(ndep_statuses=["ns", "up"]))[0])
        self.assertTrue(ex.coculture_flags(self.base(ax_d14_status="not detected"))[0])

    def test_strict_all_axenic(self):
        self.assertFalse(ex.coculture_flags(self.base(ax_d31_status="up"))[0])
        self.assertFalse(ex.coculture_flags(self.base(ax_d89_status="up"))[0])
        self.assertFalse(ex.coculture_flags(self.base(ax_rna_d14_status="up"))[0])
        self.assertTrue(ex.coculture_flags(self.base(ax_d89_status="mixed"))[0])     # only "up" excludes
        self.assertTrue(ex.coculture_flags(self.base(ax_rna_d14_status="not detected"))[0])

    def test_new_keys_required(self):
        d = self.base()
        del d["ax_d31_status"]
        with self.assertRaises(KeyError):
            ex.coculture_flags(d)

    def test_loose(self):
        self.assertTrue(ex.coculture_flags(self.base(cc_d89_status="ns"))[1])
        self.assertFalse(ex.coculture_flags(self.base(cc_d60_status="ns", cc_d89_status="mixed"))[1])
        self.assertFalse(ex.coculture_flags(self.base(ax_d14_pct=0.8))[1])
        self.assertFalse(ex.coculture_flags(self.base(ndep_max_pct=0.95))[1])
        self.assertFalse(ex.coculture_flags(self.base(ax_d14_pct=float("nan")))[1])   # undetected: not evaluable

    def test_loose_axenic_death(self):
        self.assertFalse(ex.coculture_flags(self.base(ax_d31_status="up"))[1])
        self.assertFalse(ex.coculture_flags(self.base(ax_d89_status="up"))[1])
        self.assertTrue(ex.coculture_flags(self.base(ax_rna_d14_status="up"))[1])     # loose ignores axenic RNA


class TestUpLoci(unittest.TestCase):
    def test_lists_up_subunits_in_member_order(self):
        st = pd.Series({"A": "significant_up", "B": "not_significant", "C": "significant_up", "D": "significant_down"})
        self.assertEqual(ex.up_loci(st, ["C", "B", "A", "Z"]), ["C", "A"])
        self.assertEqual(ex.up_loci(st, ["B", "D"]), [])


class TestStimulonExcess(unittest.TestCase):
    pct = pd.Series({"a": 0.9, "b": 0.7, "c": float("nan"), "d": 0.2, "e": 0.6})

    def test_level_is_median_of_detected_members(self):
        self.assertAlmostEqual(ex.stimulon_level(self.pct, ["a", "b", "c", "zz"]), 0.8)
        self.assertTrue(math.isnan(ex.stimulon_level(self.pct, ["c", "zz"])))

    def test_system_excess_is_median_subunit_excess(self):
        self.assertAlmostEqual(ex.system_excess(self.pct, 0.5, ["a", "b", "d"]), 0.2)
        self.assertAlmostEqual(ex.system_excess(self.pct, 0.5, ["a", "c"]), 0.4)     # undetected subunit skipped
        self.assertTrue(math.isnan(ex.system_excess(self.pct, 0.5, ["c"])))
        self.assertTrue(math.isnan(ex.system_excess(self.pct, float("nan"), ["a"])))

    def test_mean_pair_requires_both(self):
        self.assertAlmostEqual(ex.mean_pair(0.2, 0.4), 0.3)
        self.assertTrue(math.isnan(ex.mean_pair(0.2, float("nan"))))


class TestEcClass(unittest.TestCase):
    def test_classes(self):
        self.assertEqual(ex.ec_class("ec:3.5.1.5"), "EC 3.5 C-N hydrolases (non-peptide)")
        self.assertEqual(ex.ec_class("ec:3.5.-.-"), "EC 3.5 C-N hydrolases (non-peptide)")
        self.assertEqual(ex.ec_class("ec:4.3.1.1"), "EC 4.3.1 ammonia-lyases")
        self.assertEqual(ex.ec_class("ec:3.4.21.92"), "EC 3.4 peptidases")
        self.assertEqual(ex.ec_class("EC:3.4.24.-"), "EC 3.4 peptidases")

    def test_outside(self):
        for x in ("ec:4.3.2.1", "ec:3.1.1.1", "ec:4.-.-.-", "ec:3.-.-.-", "ec:2.6.1.1", "", None):
            self.assertIsNone(ex.ec_class(x))


class TestCombineLabels(unittest.TestCase):
    def test_combine(self):
        self.assertEqual(ex.combine_labels(["up", "ns", "up"]), "up")
        self.assertEqual(ex.combine_labels(["up", "down"]), "mixed")
        self.assertEqual(ex.combine_labels(["ns", "not detected"]), "ns")
        self.assertEqual(ex.combine_labels(["not detected", "not detected"]), "not detected")
        self.assertEqual(ex.combine_labels(["not listed"]), "not listed")
        self.assertEqual(ex.combine_labels(["down", "ns"]), "down")


class TestCountUp(unittest.TestCase):
    def test_count(self):
        self.assertEqual(ex.count_up(["up", "ns", "not detected", "mixed", "down"]), (1, 4))
        self.assertEqual(ex.count_up(["not listed", "up"]), (1, 1))
        self.assertEqual(ex.count_up([]), (0, 0))


if __name__ == "__main__":
    unittest.main()
