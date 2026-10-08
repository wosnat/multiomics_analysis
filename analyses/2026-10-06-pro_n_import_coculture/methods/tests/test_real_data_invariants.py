"""Real-data invariants for the v1.5.0 grouping fix (Rule A3 adjacent_abc). Reads methods/data only.

Compares the current pipeline output (data/<tag>/) with the v1.4.0 archive (data/v1.4.0_archive/<tag>/).
Skipped when the data directories are absent.
"""
import json
import unittest
from pathlib import Path

import pandas as pd

D = Path(__file__).resolve().parents[1] / "data"
A = D / "v1.6.0_archive"  # previous version (update on each version bump)
TAGS = ["med4", "mit9313", "natl2a"]
REF = "gap200_roleT_crossT"
# anchors of the N-relevant / reference systems (gene names; every gene with the name is checked)
ANCHORS = ["cynA", "cynB", "cynD", "urtA", "urtB", "urtC", "urtD", "urtE", "amt1", "pstS", "pstC", "pstA", "pstB",
           "dppA", "dppB", "dppC", "ddpD", "mntA", "mntB", "mntC", "phnC", "phnD", "phnE", "futA", "futB", "futC",
           "idiA"]
ABC = {"substrate_binding", "permease", "atpase"}
ADJ_JOINED_MED4 = {"PMM0976", "PMM0977", "PMM0978", "PMM0748", "PMM0749", "PMM0750"}  # systems changed by Rule A3
HAVE = all((D / t).is_dir() and (A / t).is_dir() for t in TAGS)


def membership(tag, base):
    g = pd.read_csv(base / tag / f"p3_{tag}_gene_systems_{REF}.csv")
    sy = pd.read_csv(base / tag / f"p11_{tag}_systems.csv").set_index("system_id")
    mem = g.groupby("system_id").locus_tag.agg(frozenset).to_dict()
    return g.set_index("locus_tag"), mem, sy


@unittest.skipUnless(HAVE, "pipeline data / v1.4.0 archive not present")
class TestRealDataV15(unittest.TestCase):
    def test_reference_systems_unchanged(self):
        bad = []
        for t in TAGS:
            gn, mn, sn = membership(t, D)
            go, mo, so = membership(t, A)
            for lt in gn.index[gn.gene_name.isin(ANCHORS)]:
                if lt not in go.index:
                    bad.append((t, lt, "not in v1.4.0"))
                    continue
                s_new, s_old = gn.loc[lt, "system_id"], go.loc[lt, "system_id"]
                if mn[s_new] != mo[s_old]:
                    bad.append((t, lt, "membership", sorted(mo[s_old]), sorted(mn[s_new])))
                if sn.loc[s_new, "tier"] != so.loc[s_old, "tier"]:
                    bad.append((t, lt, "tier", so.loc[s_old, "tier"], sn.loc[s_new, "tier"]))
        self.assertEqual(bad, [])

    def test_no_two_complete_cassettes_merged(self):
        bad = []
        for t in TAGS:
            gn, mn, _ = membership(t, D)
            go, mo, _ = membership(t, A)
            for sid, mem in mn.items():
                parts = {go.loc[lt, "system_id"] for lt in mem if lt in go.index}
                complete = [p for p in parts if ABC <= set(go.loc[list(mo[p]), "role"])]
                if len(parts) > 1 and len(complete) > 1:
                    bad.append((t, sid, sorted(complete)))
        self.assertEqual(bad, [])

    def test_nitrate_nitrite_expected_negative(self):
        for t in TAGS:
            e = pd.read_csv(D / t / f"p5_{t}_expectation_check.csv").set_index("compound")
            for c in ("nitrate", "nitrite"):
                self.assertTrue(bool(e.loc[c, "can_use_window_pass"]) and bool(e.loc[c, "can_use_run_pass"]), (t, c))

    def test_pilot_answer_key_comparisons_unchanged(self):
        for f in ("p1_med4_pilot_status.csv", "p2_pilot_roles.csv", "p4_med4_pilot_neighbours.csv",
                  "p5_med4_pilot_substrate_diff.csv", "p5_med4_pilot_rows_not_in_key.csv",
                  "p6_med4_pilot_gene_evidence_diff.csv", "p6_med4_pilot_system_profiles.csv", "p11_med4_pilot.csv"):
            new = pd.read_csv(D / "med4" / f)
            old = pd.read_csv(A / "med4" / f)
            if "other_system_id" in new.columns:
                # a neighbour's OTHER system id may be renamed only when that neighbour joined via adjacent_abc
                ch = new[new.other_system_id.fillna("").astype(str) != old.other_system_id.fillna("").astype(str)]
                self.assertTrue(set(ch.candidate) <= ADJ_JOINED_MED4, (f, sorted(set(ch.candidate))))
                new, old = new.drop(columns="other_system_id"), old.drop(columns="other_system_id")
            pd.testing.assert_frame_equal(new, old, check_dtype=False, obj=f)
        pil = json.loads((D / "med4" / "p11_med4_summary.json").read_text(encoding="utf-8"))["pilot"]
        tiers = {p["case"]: p["tier"] for p in pil}
        self.assertEqual(tiers, {"cyn": "High", "urt": "High", "dpp": "High", "amt1": "High", "pst": "High",
                                 "salY": "Low", "fadD": "Low"})


if __name__ == "__main__":
    unittest.main()
