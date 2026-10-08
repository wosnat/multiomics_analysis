"""Toy tests for methods/n_transport.py (phase 1: pure logic, no KG).

Runner: stdlib unittest (pytest is NOT installed in the venv; nothing new installed).
    .venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/methods/tests -v
The file is also pytest-compatible if pytest is added later.

Fixture rule: every fixture is CSV TEXT parsed with pandas.read_csv(io.StringIO(...)),
i.e. exactly what a `to_dataframe(...).to_csv(index=False)` file looks like when read back:
booleans as "True"/"False", missing values as empty fields (-> NaN), list columns joined
by " | " (to_dataframe's list join). Every expected value is hand-computed in a comment.
"""
import io
import math
import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import n_transport as nt  # noqa: E402


def csv(text, **kw):
    return pd.read_csv(io.StringIO(text.strip() + "\n"), **kw)


# --------------------------------------------------------------------------- helpers
class TestToBool(unittest.TestCase):
    def test_string_false_is_not_truthy(self):
        # Round-1 bug: bool("False") is True. Our parser must return False.
        self.assertIs(nt.to_bool("False"), False)
        self.assertIs(nt.to_bool("false"), False)
        self.assertIs(nt.to_bool("True"), True)

    def test_string_false_column_from_csv(self):
        # dtype=str forces the column to stay as the literal strings "False"/"True".
        df = csv("""
locus_tag,flag
g1,False
g2,True
g3,
""", dtype=str)
        self.assertEqual(df.loc[0, "flag"], "False")  # really a string
        self.assertEqual([nt.to_bool(v) for v in df["flag"]], [False, True, False])  # NaN -> False

    def test_native_and_nan(self):
        self.assertIs(nt.to_bool(True), True)
        self.assertIs(nt.to_bool(False), False)
        self.assertIs(nt.to_bool(float("nan")), False)
        self.assertIs(nt.to_bool(None), False)
        self.assertIs(nt.to_bool(""), False)

    def test_unknown_string_raises(self):
        with self.assertRaises(ValueError):
            nt.to_bool("maybe")


class TestParseList(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(nt.parse_list("pfam:PF00528 | pfam:PF19300"), ["pfam:PF00528", "pfam:PF19300"])
        self.assertEqual(nt.parse_list("['PF00528', 'PF19300']"), ["PF00528", "PF19300"])
        self.assertEqual(nt.parse_list(["a", "b"]), ["a", "b"])
        self.assertEqual(nt.parse_list(float("nan")), [])
        self.assertEqual(nt.parse_list(""), [])
        self.assertEqual(nt.parse_list("tcdb:3.A.1"), ["tcdb:3.A.1"])


class TestTcdbLevel(unittest.TestCase):
    def test_levels(self):
        # level = number of dotted fields - 1 (tcdb.md: 3 class(0), 3.A subclass(1), 3.A.1 family(2) ...)
        self.assertEqual(nt.tcdb_level("tcdb:3.A.1.16.1"), 4)
        self.assertEqual(nt.tcdb_level("tcdb:3.A.1.5"), 3)
        self.assertEqual(nt.tcdb_level("tcdb:3.A.1"), 2)
        self.assertEqual(nt.tcdb_level("1.A.11"), 2)

    def test_ancestor(self):
        self.assertEqual(nt.tcdb_ancestor("tcdb:3.A.1.16.1", 3), "tcdb:3.A.1.16")
        self.assertIsNone(nt.tcdb_ancestor("tcdb:3.A.1", 3))  # shallower than requested
        self.assertEqual(nt.tcdb_ancestor("tcdb:3.A.1.5", 3), "tcdb:3.A.1.5")


# --------------------------------------------------------------------------- pfam_role
class TestPfamRole(unittest.TestCase):
    def test_binding(self):
        # cynA-like: PF13379 + PF09084, both binding in the map
        self.assertEqual(nt.pfam_role(["PF13379", "PF09084"]), "substrate_binding")

    def test_permease_from_to_dataframe_string(self):
        # dppB-like, as to_dataframe joins term_ids: "pfam:PF00528 | pfam:PF19300"
        self.assertEqual(nt.pfam_role("pfam:PF00528 | pfam:PF19300"), "permease")

    def test_atpase_with_associated_domain(self):
        # ddpD-like: PF00005 ABC + PF08352 oligopeptide C-term (atpase-associated)
        self.assertEqual(nt.pfam_role(["PF00005", "PF08352"]), "atpase")

    def test_single_carrier(self):
        self.assertEqual(nt.pfam_role("pfam:PF00909"), "single_carrier")  # Amt

    def test_other_and_missing(self):
        self.assertEqual(nt.pfam_role(["PF00501"]), "other")  # AMP-binding, not in map
        self.assertEqual(nt.pfam_role(float("nan")), "other")

    def test_stringified_list(self):
        self.assertEqual(nt.pfam_role("['PF00528']"), "permease")

    def test_conflicting_roles_is_mixed(self):
        # binding + atpase domains on one gene -> 'mixed', never silently one of them
        self.assertEqual(nt.pfam_role(["PF13379", "PF00005"]), "mixed")


# --------------------------------------------------------------------------- coordinates
GENES_CSV = """
locus_tag,contig,start,end,strand
G4,c1,950,1200,+
G1,c1,100,400,+
G2,c1,420,700,+
G3,c1,690,900,-
G5,c1,1210,1500,+
G6,c1,3000,3300,+
H2,c2,260,500,-
H1,c2,50,200,-
"""
# Sorted by contig,start: c1: G1 G2 G3 G4 G5 G6 ; c2: H1 H2
# gap_to_next = next.start - this.end - 1 (bp strictly between; negative = overlap)
#   G1->G2: 420-400-1 = 19
#   G2->G3: 690-700-1 = -11 (11 bp overlap)
#   G3->G4: 950-900-1 = 49
#   G4->G5: 1210-1200-1 = 9
#   G5->G6: 3000-1500-1 = 1499
#   G6: last on c1 -> NaN
#   H1->H2: 260-200-1 = 59 ; H2 last -> NaN
# Cross-check with the real KG: cynA end 354660, cynB start 354691 -> 354691-354660-1 = 30,
# which equals gene_neighbors(PMM0371).bp_gap for PMM0370 (raw_samples).


class TestAdjacentGaps(unittest.TestCase):
    def setUp(self):
        self.g = nt.adjacent_gaps(csv(GENES_CSV))

    def test_sorted(self):
        self.assertEqual(self.g["locus_tag"].tolist(), ["G1", "G2", "G3", "G4", "G5", "G6", "H1", "H2"])

    def test_gap_values(self):
        gaps = dict(zip(self.g["locus_tag"], self.g["gap_to_next"]))
        self.assertEqual(gaps["G1"], 19)
        self.assertEqual(gaps["G2"], -11)
        self.assertEqual(gaps["G3"], 49)
        self.assertEqual(gaps["G4"], 9)
        self.assertEqual(gaps["G5"], 1499)
        self.assertTrue(math.isnan(gaps["G6"]))  # contig end, no wrap to H1
        self.assertEqual(gaps["H1"], 59)
        self.assertTrue(math.isnan(gaps["H2"]))

    def test_next_locus(self):
        nxt = dict(zip(self.g["locus_tag"], self.g["next_locus_tag"]))
        self.assertEqual(nxt["G2"], "G3")
        self.assertTrue(pd.isna(nxt["G6"]))

    def test_real_cyn_coordinates(self):
        df = csv("""
locus_tag,contig,start,end,strand
PMM0370,NC_005072.1,352975,354660,+
PMM0371,NC_005072.1,354691,355473,+
PMM0372,NC_005072.1,355490,356344,+
PMM0373,NC_005072.1,356377,356820,+
""")
        g = nt.adjacent_gaps(df)
        # 354691-354660-1=30 ; 355490-355473-1=16 ; 356377-356344-1=32
        self.assertEqual(g["gap_to_next"].tolist()[:3], [30, 16, 32])


class TestRuns(unittest.TestCase):
    def _runs(self, **kw):
        r = nt.runs(csv(GENES_CSV), **kw)
        return r.set_index("locus_tag")

    def test_opposite_strand_gene_inside_run(self):
        # max_gap 100: block c1 = G1..G5 (all gaps <=100; G5->G6 1499 breaks), block c2 = H1,H2.
        # Strand segments in block1: [G1,G2 +] [G3 -] [G4,G5 +]; G3 is a 1-gene opposite segment
        # bracketed by + segments -> + run = {G1,G2,G4,G5}; G3 flagged, own run of size 1.
        r = self._runs(max_gap_bp=100, same_strand=True)
        self.assertEqual(len({r.loc[x, "run_id"] for x in ["G1", "G2", "G4", "G5"]}), 1)
        self.assertEqual(r.loc["G1", "run_size"], 4)
        self.assertNotEqual(r.loc["G3", "run_id"], r.loc["G1", "run_id"])
        self.assertEqual(r.loc["G3", "run_size"], 1)
        self.assertIs(bool(r.loc["G3", "opposite_strand_in_run"]), True)
        self.assertEqual(r.loc["G3", "inside_run_id"], r.loc["G1", "run_id"])
        for x in ["G1", "G2", "G4", "G5", "G6", "H1", "H2"]:
            self.assertIs(bool(r.loc[x, "opposite_strand_in_run"]), False)
        self.assertEqual(r.loc["G6", "run_size"], 1)
        self.assertEqual(r.loc["H1", "run_id"], r.loc["H2", "run_id"])

    def test_unbracketed_opposite_gene_not_flagged(self):
        # max_gap 30: G3->G4 49 > 30 breaks; block [G1,G2,G3] has no + segment after G3 -> G3 not
        # flagged; runs {G1,G2}, {G3}, {G4,G5}, {G6}, {H1}, {H2} (59 > 30).
        r = self._runs(max_gap_bp=30, same_strand=True)
        self.assertIs(bool(r.loc["G3", "opposite_strand_in_run"]), False)
        self.assertEqual(r.loc["G1", "run_id"], r.loc["G2", "run_id"])
        self.assertNotEqual(r.loc["G2", "run_id"], r.loc["G4", "run_id"])
        self.assertNotEqual(r.loc["H1", "run_id"], r.loc["H2", "run_id"])
        self.assertEqual(r["run_id"].nunique(), 6)

    def test_strand_agnostic(self):
        # same_strand=False, max_gap 100: runs = block = {G1..G5}, {G6}, {H1,H2}; no flags.
        r = self._runs(max_gap_bp=100, same_strand=False)
        self.assertEqual(r.loc["G3", "run_id"], r.loc["G1", "run_id"])
        self.assertEqual(r.loc["G1", "run_size"], 5)
        self.assertEqual(r["run_id"].nunique(), 3)
        self.assertFalse(r["opposite_strand_in_run"].astype(bool).any())

    def test_two_gene_interloper_exceeds_limit(self):
        df = csv("""
locus_tag,contig,start,end,strand
A1,c,100,200,+
A2,c,210,300,-
A3,c,310,400,-
A4,c,410,500,+
""")
        # gaps 9,9,9; segments [A1 +][A2,A3 -][A4 +]; interloper length 2 > max_interlopers=1
        # -> no merge: runs {A1},{A2,A3},{A4}; nothing flagged.
        r = nt.runs(df, max_gap_bp=100, same_strand=True).set_index("locus_tag")
        self.assertNotEqual(r.loc["A1", "run_id"], r.loc["A4", "run_id"])
        self.assertFalse(r["opposite_strand_in_run"].astype(bool).any())
        # with max_interlopers=2 -> {A1,A4} merged, A2 and A3 flagged
        r2 = nt.runs(df, max_gap_bp=100, same_strand=True, max_interlopers=2).set_index("locus_tag")
        self.assertEqual(r2.loc["A1", "run_id"], r2.loc["A4", "run_id"])
        self.assertTrue(bool(r2.loc["A2", "opposite_strand_in_run"]))
        self.assertTrue(bool(r2.loc["A3", "opposite_strand_in_run"]))


# --------------------------------------------------------------------------- group_systems
TRANSPORTERS_CSV = """
locus_tag,run_id,role,tcdb_ids
cA,run_cA,substrate_binding,tcdb:3.A.1.16.1 | tcdb:3.A.1.16.2 | tcdb:3.A.1.17.3
cB,run_cA,permease,tcdb:3.A.1.16.1 | tcdb:3.A.1.16.2
cD,run_cA,atpase,tcdb:3.A.1.16.1
sY,run_cA,permease,tcdb:3.A.1
dA,run_dA,substrate_binding,tcdb:3.A.1.5.1
dB,run_dA,permease,tcdb:3.A.1.5.1
dC,run_dC,permease,tcdb:3.A.1.5.2
dD,run_dD,atpase,tcdb:3.A.1.5.3
oA,run_oA,substrate_binding,tcdb:3.A.1.5.4
oB,run_oA,permease,tcdb:3.A.1.5.4
oD,run_oA,atpase,tcdb:3.A.1.5.4
pS,run_pS,substrate_binding,tcdb:3.A.1.7.1
pC,run_pC,permease,tcdb:3.A.1.7.1
pA,run_pC,permease,tcdb:3.A.1.7.1
pB,run_pC,atpase,tcdb:3.A.1.7.1
amt,run_amt,single_carrier,tcdb:1.A.11.1.1
"""
# Within-run (level-3 ancestor shared, default within_run_min_level=3):
#   run_cA: cA,cB,cD share tcdb:3.A.1.16 -> S{cA,cB,cD} (roles b,p,a = complete)
#           sY attached only at tcdb:3.A.1 (level 2) -> no level-3 ancestor -> alone
#   run_dA: S{dA,dB} (b,p, incomplete) ; dC alone (p) ; dD alone (a)
#   run_oA: S{oA,oB,oD} complete ; pS alone (b) ; run_pC: S{pC,pA,pB} (p,a) ; amt alone
# Cross-locus (cross_locus=True, level 3, both incomplete, role sets differ):
#   {dA,dB},{dC},{dD} share tcdb:3.A.1.5, all incomplete -> merged {dA,dB,dC,dD}
#   {oA,oB,oD} shares 3.A.1.5 but is complete -> NOT merged
#   {pS} + {pC,pA,pB} share 3.A.1.7 -> merged
#   sY never (no level-3 ancestor)
# => cross_locus=True : 6 systems ; cross_locus=False : 9 systems


def partition(df):
    return sorted(sorted(g["locus_tag"]) for _, g in df.groupby("system_id"))


class TestGroupSystems(unittest.TestCase):
    def setUp(self):
        self.t = csv(TRANSPORTERS_CSV)

    def test_cross_locus_on(self):
        s = nt.group_systems(self.t, cross_locus=True)
        self.assertEqual(partition(s), sorted([
            ["cA", "cB", "cD"], ["sY"], ["dA", "dB", "dC", "dD"], ["oA", "oB", "oD"],
            ["pA", "pB", "pC", "pS"], ["amt"],
        ]))
        flag = dict(zip(s["locus_tag"], s["cross_locus_merged"]))
        self.assertTrue(flag["dC"] and flag["dA"] and flag["pS"])
        self.assertFalse(flag["cA"] or flag["oA"] or flag["sY"] or flag["amt"])
        nruns = dict(zip(s["locus_tag"], s["n_runs"]))
        self.assertEqual(nruns["dA"], 3)  # run_dA, run_dC, run_dD
        self.assertEqual(nruns["pS"], 2)

    def test_cross_locus_off(self):
        s = nt.group_systems(self.t, cross_locus=False)
        self.assertEqual(len(partition(s)), 9)
        self.assertIn(["dA", "dB"], partition(s))
        self.assertIn(["dC"], partition(s))
        self.assertFalse(s["cross_locus_merged"].astype(bool).any())

    def test_superfamily_only_gene_stays_alone(self):
        # sY (permease, tcdb:3.A.1 only) sits in run_cA, but the cyn system already has a permease
        # -> role sets not disjoint -> no role-join either. Alone under every switch combination.
        for on in (True, False):
            for byrole in (True, False):
                s = nt.group_systems(self.t, cross_locus=on, join_within_run_by_role=byrole)
                self.assertIn(["sY"], partition(s))

    def test_join_within_run_by_role(self):
        t = csv("""
locus_tag,run_id,role,tcdb_ids
a1,run_a1,substrate_binding,tcdb:3.A.1.7.1
a2,run_a1,permease,tcdb:3.A.1.7.1
a3,run_a1,atpase,tcdb:3.A.1
x1,run_x1,atpase,tcdb:3.A.1
q1,run_a1,other,tcdb:3.A.1
""")
        # Rule A: a1,a2 share tcdb:3.A.1.7 -> {a1,a2} roles {b,p}. a3 (atpase) only shares
        # tcdb:3.A.1 (level 2). Role-join ON: {a} disjoint from {b,p}, same run, shared level-2
        # ancestor tcdb:3.A.1 -> {a1,a2,a3}, joined_by "role|tcdb_level3".
        # x1 is in a different run -> never role-joined. q1 role "other" -> not a transporter role
        # -> never role-joined.
        on = nt.group_systems(t, cross_locus=False, join_within_run_by_role=True)
        self.assertEqual(partition(on), [["a1", "a2", "a3"], ["q1"], ["x1"]])
        self.assertEqual(on.set_index("locus_tag").loc["a3", "joined_by"], "role|tcdb_level3")
        off = nt.group_systems(t, cross_locus=False, join_within_run_by_role=False)
        self.assertEqual(partition(off), [["a1", "a2"], ["a3"], ["q1"], ["x1"]])
        self.assertEqual(off.set_index("locus_tag").loc["a1", "joined_by"], "tcdb_level3")

    def test_identical_role_sets_do_not_merge(self):
        t = csv("""
locus_tag,run_id,role,tcdb_ids
b1,run_b1,substrate_binding,tcdb:3.A.1.5.1
b2,run_b2,substrate_binding,tcdb:3.A.1.5.1
""")
        # both {b}: union adds nothing to either -> not complementary -> 2 systems
        self.assertEqual(partition(nt.group_systems(t, cross_locus=True)), [["b1"], ["b2"]])

    def test_member_runs_listed(self):
        s = nt.group_systems(self.t, cross_locus=True).set_index("locus_tag")
        # dpp-like system spans run_dA, run_dC, run_dD -> sorted, "|"-joined
        self.assertEqual(s.loc["dC", "member_runs"], "run_dA|run_dC|run_dD")
        self.assertEqual(s.loc["cA", "member_runs"], "run_cA")

    def test_joined_by_column(self):
        s = nt.group_systems(self.t, cross_locus=True).set_index("locus_tag")
        # cyn joined only by a shared level-3 ancestor; dpp by level-3 within run_dA + cross-locus;
        # amt alone -> ""
        self.assertEqual(s.loc["cA", "joined_by"], "tcdb_level3")
        self.assertEqual(s.loc["dA", "joined_by"], "cross_locus|tcdb_level3")
        self.assertEqual(s.loc["amt", "joined_by"], "")

    def test_input_order_independent(self):
        s1 = partition(nt.group_systems(self.t, cross_locus=True))
        s2 = partition(nt.group_systems(self.t.iloc[::-1].reset_index(drop=True), cross_locus=True))
        self.assertEqual(s1, s2)


# --------------------------------------------------------------------------- neighbours
NEIGH_CSV = """
locus_tag,pfam_ids,brite_transporter,tcdb_ids,is_linked_enzyme
n1,pfam:PF00005,False,,False
n2,pfam:PF02560 | pfam:PF21291,False,,True
n3,,False,,False
n4,pfam:PF01842,True,,False
n5,pfam:PF00528,False,tcdb:3.A.1.16.1,False
"""
# n1: atpase Pfam, no TCDB          -> missing_subunit (recruited_by pfam)
# n2: cyanase domains, enzyme flag  -> linked_enzyme
# n3: nothing                       -> context
# n4: no role Pfam, BRITE transporter KO, no TCDB -> missing_subunit (recruited_by ko)
# n5: has a TCDB call itself        -> tcdb_transporter (belongs in the transporter set, not here)


class TestClassifyNeighbour(unittest.TestCase):
    def test_classes(self):
        df = csv(NEIGH_CSV)
        got = {r.locus_tag: nt.classify_neighbour(r) for r in df.itertuples()}
        self.assertEqual(got, {"n1": "missing_subunit", "n2": "linked_enzyme", "n3": "context",
                               "n4": "missing_subunit", "n5": "tcdb_transporter"})

    def test_recruited_by(self):
        df = csv(NEIGH_CSV)
        got = {r.locus_tag: nt.recruited_by(r) for r in df.itertuples()}
        self.assertEqual(got["n1"], "pfam")
        self.assertEqual(got["n4"], "ko")
        self.assertIsNone(got["n3"])

    def test_string_false_flags_are_false(self):
        # all-string read: "False" must not count as a BRITE hit / enzyme flag
        df = csv(NEIGH_CSV, dtype=str)
        row = df.set_index("locus_tag").loc["n3"]
        self.assertEqual(row["brite_transporter"], "False")
        self.assertEqual(nt.classify_neighbour(row), "context")


# --------------------------------------------------------------------------- can_use
METAB_CSV = """
locus_tag,evidence_source,metabolite_id
cS,metabolism,kegg.compound:C01417
cS,metabolism,kegg.compound:C00014
gA,metabolism,kegg.compound:C00014
uC,metabolism,kegg.compound:C00086
cA,transport,chebi:14654
"""
# cyanate C01417: only cS, which is in the cyn system neighbourhood -> co-located
# ammonia C00014 for amt (neighbourhood {amt}): cS,gA elsewhere      -> elsewhere in genome
# nitrate chebi:14654: only a TRANSPORT row (ignored)                 -> no
# urea C00086 for cyn neighbourhood: uC elsewhere                     -> elsewhere in genome


class TestCanUse(unittest.TestCase):
    def setUp(self):
        self.m = csv(METAB_CSV)
        self.cyn = {"cA", "cB", "cD", "cS"}

    def test_colocated(self):
        self.assertEqual(nt.can_use("kegg.compound:C01417", self.m, self.cyn), "co-located")

    def test_elsewhere(self):
        self.assertEqual(nt.can_use("kegg.compound:C00014", self.m, {"amt"}), "elsewhere in genome")
        self.assertEqual(nt.can_use("kegg.compound:C00086", self.m, self.cyn), "elsewhere in genome")

    def test_no_transport_rows_ignored(self):
        self.assertEqual(nt.can_use("chebi:14654", self.m, self.cyn), "no")

    def test_loci_as_to_dataframe_string(self):
        self.assertEqual(nt.can_use("kegg.compound:C01417", self.m, "cA | cB | cD | cS"), "co-located")


# --------------------------------------------------------------------------- likely_transporter
LT_CSV = """
locus_tag,pfam_ids,brite_transporter,tcdb_ids
f1,pfam:PF00501 | pfam:PF13193,False,tcdb:4.C.1.1
s1,pfam:PF02687 | pfam:PF12704,False,tcdb:3.A.1
a1,pfam:PF00909,False,tcdb:1.A.11.1.1
t1,pfam:PF00889,False,tcdb:9.A.1
k1,,True,
k2,,True,tcdb:3.A.1.5.1
z1,,False,
"""
# f1 fadD-like: no role Pfam, no BRITE, TCDB class 4 (not counted) -> False
# s1 superfamily-only ABC permease-like: Pfams not in map, TCDB class 3 -> True (basis tcdb)
# a1 amt: single_carrier Pfam + class 1 -> True
# t1: class 9 (incompletely characterized) only -> False
# k1: BRITE transporter KO only -> True
# z1: nothing -> False


class TestLikelyTransporter(unittest.TestCase):
    # 3-valued: strong (role Pfam or BRITE KO) / tcdb_only (only TCDB class 1-3) / none
    def test_rule(self):
        df = csv(LT_CSV)
        got = {r.locus_tag: nt.likely_transporter(r) for r in df.itertuples()}
        # f1 class 4 only -> none ; s1 class 3, no role Pfam/KO -> tcdb_only ; a1 role Pfam -> strong
        # t1 class 9 only -> none ; k1 BRITE -> strong ; z1 -> none
        # v1.4: k1 BRITE KO alone -> none (the KO basis only upgrades a TCDB-listed gene); k2 KO + TCDB -> strong
        self.assertEqual(got, {"f1": "none", "s1": "tcdb_only", "a1": "strong", "t1": "none",
                               "k1": "none", "k2": "strong", "z1": "none"})

    def test_basis(self):
        df = csv(LT_CSV).set_index("locus_tag")
        self.assertEqual(nt.likely_transporter_basis(df.loc["a1"]), "pfam|tcdb")
        self.assertEqual(nt.likely_transporter_basis(df.loc["s1"]), "tcdb")
        self.assertEqual(nt.likely_transporter_basis(df.loc["k1"]), "ko")
        self.assertEqual(nt.likely_transporter_basis(df.loc["f1"]), "")

    def test_string_false_brite(self):
        df = csv(LT_CSV, dtype=str).set_index("locus_tag")
        self.assertEqual(nt.likely_transporter(df.loc["z1"]), "none")
        self.assertEqual(nt.likely_transporter(df.loc["k2"]), "strong")   # v1.4: KO needs TCDB
        self.assertEqual(nt.likely_transporter(df.loc["k1"]), "none")

    def test_custom_role_map(self):
        # with a data-built map that gives PF02687 a permease role, s1 becomes strong
        df = csv(LT_CSV).set_index("locus_tag")
        self.assertEqual(nt.likely_transporter(df.loc["s1"], role_map={"PF02687": "permease"}), "strong")


FADD_TCDB_CSV = """
locus_tag,term_id,evidence_score,source_agreement
f2,tcdb:2.A.1.1.1,0.0,single_source
f2,tcdb:4.C.1.1,0.6,both_sources
"""
# fadD-like gene with a class-2 hit (score 0, single source) and a class-4 hit (0.6, both):
#   class 1-3 attachments = {tcdb:2.A.1.1.1} -> max score 0.0, source_agreement "single_source"
#   (the class-4 0.6 / both_sources row must NOT leak in)
#   tcdb_ids "tcdb:2.A.1.1.1 | tcdb:4.C.1.1", no role Pfam, BRITE False -> "tcdb_only"


class TestTcdbTransporterEvidence(unittest.TestCase):
    def test_fadd_like(self):
        rows = csv(FADD_TCDB_CSV)
        ev = nt.tcdb_transporter_evidence(rows)
        self.assertEqual(ev["tcdb_c123_max_score"], 0.0)
        self.assertEqual(ev["tcdb_c123_source_agreement"], "single_source")
        row = {"pfam_ids": "pfam:PF00501", "brite_transporter": "False",
               "tcdb_ids": " | ".join(rows["term_id"])}
        self.assertEqual(nt.likely_transporter(row), "tcdb_only")

    def test_no_class123(self):
        rows = csv(FADD_TCDB_CSV).iloc[[1]]
        ev = nt.tcdb_transporter_evidence(rows)
        self.assertIsNone(ev["tcdb_c123_max_score"])
        self.assertEqual(ev["tcdb_c123_source_agreement"], "")


# --------------------------------------------------------------------------- evidence_profile
EP_CSV = """
system_id,locus_tag,role,term_id,evidence,evidence_score,source_agreement,pfam_support,attachment_depth
cyn,cA,substrate_binding,tcdb:3.A.1.16.1,family_inferred,0.6,both_sources,uncorroborated,most_specific
cyn,cA,substrate_binding,tcdb:3.A.1.17.3,family_inferred,0.4,single_source,uncorroborated,most_specific
cyn,cB,permease,tcdb:3.A.1.16.1,family_inferred,0.8,both_sources,corroborated,most_specific
cyn,cD,atpase,tcdb:3.A.1.16.1,family_inferred,0.8,both_sources,corroborated,most_specific
cyn,mX,atpase,,,,,,
amt,a1,single_carrier,tcdb:1.A.11.1.1,homology,0.8,both_sources,corroborated,most_specific
sup,s1,permease,tcdb:3.A.1,family_inferred,0.2,single_source,uncorroborated,most_specific
"""
# cyn: genes cA,cB,cD,mX = 4 ; with TCDB = 3 (mX recruited, no TCDB row)
#      depth max = 4 ; per-gene deepest = cA 4, cB 4, cD 4 -> min 4
#      evidence {family_inferred}; homology genes 0 ; family_inferred genes 3
#      max score 0.8 ; source_agreement {both_sources, single_source}
#      pfam_support {corroborated, uncorroborated}; genes with any corroborated row = cB,cD = 2
#      roles {atpase, permease, substrate_binding} -> role_complete True
# amt: 1 gene, depth 4, homology 1, score 0.8, single_carrier -> role_complete True
# sup: depth 2, score 0.2, role permease only -> role_complete False


class TestEvidenceProfile(unittest.TestCase):
    def setUp(self):
        self.df = csv(EP_CSV)

    def prof(self, sid):
        return nt.evidence_profile(self.df[self.df["system_id"] == sid])

    def test_abc_system(self):
        p = self.prof("cyn")
        self.assertEqual(p["n_genes"], 4)
        self.assertEqual(p["n_genes_with_tcdb"], 3)
        self.assertEqual(p["tcdb_depth_max"], 4)
        self.assertEqual(p["tcdb_depth_min_gene"], 4)
        self.assertEqual(p["evidence"], "family_inferred")
        self.assertEqual(p["n_homology_genes"], 0)
        self.assertEqual(p["n_family_inferred_genes"], 3)
        self.assertAlmostEqual(p["max_tcdb_evidence_score"], 0.8)
        self.assertEqual(p["source_agreement"], "both_sources|single_source")
        self.assertEqual(p["pfam_support"], "corroborated|uncorroborated")
        self.assertEqual(p["n_pfam_corroborated_genes"], 2)
        self.assertEqual(p["roles"], "atpase|permease|substrate_binding")
        self.assertTrue(p["has_binding"] and p["has_permease"] and p["has_atpase"])
        self.assertIs(p["role_complete"], True)

    def test_single_carrier(self):
        p = self.prof("amt")
        self.assertEqual(p["n_homology_genes"], 1)
        self.assertEqual(p["evidence"], "homology")
        self.assertIs(p["role_complete"], True)

    def test_superfamily_only(self):
        p = self.prof("sup")
        self.assertEqual(p["tcdb_depth_max"], 2)
        self.assertAlmostEqual(p["max_tcdb_evidence_score"], 0.2)
        self.assertIs(p["role_complete"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)


# --------------------------------------------------------------------------- data-built Pfam role map (pilot step 2)
NAMES_CSV = """
pfam_id,pfam_name
pfam:PF00528,Binding-protein-dependent transport system inner membrane component
pfam:PF02190,ATP-dependent protease La (LON) substrate-binding domain
pfam:PF00916,Sulfate permease family
pfam:PF12849,PBP superfamily domain
pfam:PF02687,FtsX-like permease C-terminal
pfam:PF12704,MacB-like periplasmic core domain
pfam:PF00005,ABC transporter
pfam:PF12399,Branched-chain amino acid ATP-binding cassette transporter
pfam:PF00909,Ammonium Transporter Family
pfam:PF00361,"NADH:quinone oxidoreductase/Mrp antiporter, TM"
pfam:PF12974,"ABC transporter, phosphonate, periplasmic substrate-binding protein"
pfam:PF00664,ABC transporter transmembrane region
pfam:PF08352,"Oligopeptide/dipeptide transporter, C-terminal region"
pfam:PF00004,ATPase family associated with various cellular activities (AAA)
pfam:PF13792,PF13792
"""
# Ordered rule (first match wins): seed -> enzyme_guard -> substrate_binding -> single_carrier
#   -> permease -> atpase -> other
#  PF00528: "Binding-protein-dependent" must NOT hit binding; "inner membrane component" -> permease
#  PF02190: "protease" -> enzyme_guard -> other (despite "substrate-binding")
#  PF00916: "Sulfate permease family" -> single_carrier (named SulP family, before permease)
#  PF12849: "PBP superfamily" -> substrate_binding
#  PF02687: FtsX -> permease ; PF12704: "MacB-like periplasmic core" -> permease
#  PF00005: "ABC transporter" -> atpase ; PF12399: "ATP-binding cassette" -> atpase
#  PF00909: "Ammonium Transporter" -> single_carrier
#  PF00361: "oxidoreductase" -> enzyme_guard -> other (despite "antiporter")
#  PF12974: "substrate-binding" -> substrate_binding (binding precedes atpase's "ABC transporter, ")
#  PF00664: "transmembrane region" -> permease
#  PF08352: name rule -> other ; seed says atpase -> final atpase, seed_conflict True
#  PF00004: AAA -> other ; PF13792 (name = accession) -> other


class TestPfamNameRole(unittest.TestCase):
    def setUp(self):
        self.n = csv(NAMES_CSV).set_index("pfam_id")["pfam_name"]

    def role(self, pid):
        return nt.pfam_name_role(self.n[pid])

    def test_name_rules(self):
        exp = {"pfam:PF00528": ("permease", "permease"),
               "pfam:PF02190": ("other", "enzyme_guard"),
               "pfam:PF00916": ("single_carrier", "single_carrier"),
               "pfam:PF12849": ("substrate_binding", "substrate_binding"),
               "pfam:PF02687": ("permease", "permease"),
               "pfam:PF12704": ("permease", "permease"),
               "pfam:PF00005": ("atpase", "atpase"),
               "pfam:PF12399": ("atpase", "atpase"),
               "pfam:PF00909": ("single_carrier", "single_carrier"),
               "pfam:PF00361": ("other", "enzyme_guard"),
               "pfam:PF12974": ("substrate_binding", "substrate_binding"),
               "pfam:PF00664": ("permease", "permease"),
               "pfam:PF08352": ("other", "no_match"),
               "pfam:PF00004": ("other", "no_match"),
               "pfam:PF13792": ("other", "no_match")}
        got = {p: self.role(p)[:2] for p in exp}
        self.assertEqual(got, exp)

    def test_rule_reports_matched_pattern(self):
        role, rule, pattern = self.role("pfam:PF02190")
        self.assertIn("protease", pattern.lower())

    def test_build_map_seed_override_and_conflict(self):
        df = csv(NAMES_CSV)
        m = nt.build_pfam_role_map(df).set_index("pfam_id")
        # seed PF08352 atpase overrides name-rule other -> conflict recorded
        self.assertEqual(m.loc["pfam:PF08352", "role"], "atpase")
        self.assertEqual(m.loc["pfam:PF08352", "rule_matched"], "seed")
        self.assertEqual(m.loc["pfam:PF08352", "name_rule_role"], "other")
        self.assertIs(bool(m.loc["pfam:PF08352", "seed_conflict"]), True)
        # seed PF00528 permease agrees with name rule -> no conflict, still rule 'seed'
        self.assertEqual(m.loc["pfam:PF00528", "rule_matched"], "seed")
        self.assertIs(bool(m.loc["pfam:PF00528", "seed_conflict"]), False)
        # non-seed: rule from name
        self.assertEqual(m.loc["pfam:PF12849", "rule_matched"], "substrate_binding")
        self.assertIs(bool(m.loc["pfam:PF12849", "seed_conflict"]), False)

    def test_map_dict_feeds_pfam_role(self):
        m = nt.build_pfam_role_map(csv(NAMES_CSV))
        rm = nt.role_map_dict(m)  # accession (no prefix) -> role
        self.assertEqual(rm["PF12849"], "substrate_binding")
        # salY-like gene PF02687 + PF12704 -> both permease -> permease
        self.assertEqual(nt.pfam_role("pfam:PF02687 | pfam:PF12704", rm), "permease")
        # fused exporter PF00664 + PF00005 -> mixed
        self.assertEqual(nt.pfam_role("pfam:PF00664 | pfam:PF00005", rm), "mixed")
        # PF02190 mapped "other" -> no role
        self.assertEqual(nt.pfam_role("pfam:PF02190", rm), "other")


class TestGroupSystemsEdges(unittest.TestCase):
    def test_edges_list_cross_locus_merges_with_shared_ancestor(self):
        t = csv(TRANSPORTERS_CSV)
        s, e = nt.group_systems(t, cross_locus=True, return_edges=True)
        cl = e[e["label"] == "cross_locus"]
        # Hand count (TRANSPORTERS_CSV, see comment above that fixture):
        #   after rule A the dpp pieces are {dA,dB} root dA, {dC}, {dD}; pst pieces {pS}, {pA,pB,pC} root pA.
        #   Pairs visited in sorted root order: (dA,dC) share 3.A.1.5 -> merge; (dA,dD) -> merge;
        #   (dC,dD) both still separate entries in the pre-computed list -> merge (same final root);
        #   (pA,pS) share 3.A.1.7 -> merge.  => 4 cross_locus edges
        self.assertEqual(len(cl), 4)
        self.assertEqual(set(cl["shared"]), {"tcdb:3.A.1.5", "tcdb:3.A.1.7"})
        self.assertEqual(set(cl.columns) >= {"a", "b", "label", "shared", "system_id"}, True)
        # every edge maps to the final system of its genes
        sid = dict(zip(s["locus_tag"], s["system_id"]))
        for r in e.itertuples():
            self.assertEqual(sid[r.a], r.system_id)
            self.assertEqual(sid[r.b], r.system_id)

    def test_default_returns_frame_only(self):
        out = nt.group_systems(csv(TRANSPORTERS_CSV))
        self.assertIsInstance(out, pd.DataFrame)


class TestCrossLocusChainGuards(unittest.TestCase):
    def test_sodx_chain_is_not_built(self):
        t = csv("""
locus_tag,run_id,role,tcdb_ids
m1,run_m1,mixed,tcdb:3.A.1.106.1
m2,run_m2,mixed,tcdb:3.A.1.106.5
o1,run_o1,other,tcdb:3.A.1.106.13 | tcdb:3.A.1.21.1
""")
        # All three share tcdb:3.A.1.106 at level 3, each in its own run.
        # Old rule: m1-o1 and m2-o1 qualify ({mixed} vs {other}, both incomplete) -> one chain of 3.
        # New rule: (1) a piece whose roles are all 'other' never joins cross-locus;
        #           (2) 'mixed' counts as role-complete -> never seeks a partner.
        # Expected: three separate systems, no cross-locus edges.
        s, e = nt.group_systems(t, cross_locus=True, return_edges=True)
        self.assertEqual(partition(s), [["m1"], ["m2"], ["o1"]])
        self.assertEqual(int((e["label"] == "cross_locus").sum()), 0)

    def test_ecf_chain_through_other_is_not_built(self):
        t = csv("""
locus_tag,run_id,role,tcdb_ids
a1,run_a1,atpase,tcdb:3.A.1.25.1
q1,run_q1,other,tcdb:3.A.1.25.1
a2,run_a2,atpase,tcdb:3.A.1.25.2
""")
        # q1 is all-'other' -> excluded from cross-locus; a1 vs a2 have identical role sets {atpase}
        # -> not complementary. Expected: three systems.
        self.assertEqual(partition(nt.group_systems(t, cross_locus=True)), [["a1"], ["a2"], ["q1"]])

    def test_mixed_is_role_complete(self):
        self.assertIs(nt._role_complete({"mixed"}), True)
        self.assertIs(nt._role_complete({"other"}), False)
        p = nt.evidence_profile(csv("""
locus_tag,role,term_id,evidence,evidence_score,source_agreement,pfam_support
x1,mixed,tcdb:3.A.1.106.1,family_inferred,0.6,both_sources,corroborated
"""))
        self.assertIs(p["role_complete"], True)


# --------------------------------------------------------------------------- pilot step 4: neighbours
GENOME_RUNS_CSV = """
locus_tag,contig,start,end,strand,run_id,opposite_strand_in_run,inside_run_id
g1,c,100,200,+,run_g1,False,
g2,c,300,400,+,run_g1,False,
g3,c,420,500,-,run_g3,True,run_g1
g4,c,510,600,+,run_g1,False,
g5,c,610,700,+,run_g1,False,
g6,c,1000,1100,-,run_g6,False,
g7,c,1110,1200,-,run_g6,False,
g8,c,5000,5100,+,run_g8,False,
g9,c,5110,5200,+,run_g8,False,
g10,c,6000,6100,+,run_g10,False,
"""
MEMBERS_CSV = """
locus_tag,system_id
g4,S1
g5,S1
g9,S2
"""
# window 2, genome order index g1=0 ... g10=9.
# S1 (g4 idx3, g5 idx4): candidates g2,g3 (from g4), g6,g7 (from g5); members excluded.
#   g2: nearest g4, rank -2, gap 510-400-1=109, same_strand T, in_system_run T (run_g1), interloper F
#   g3: nearest g4, rank -1, gap 510-500-1=9,   same_strand F, in_system_run F, interloper T (inside run_g1)
#   g6: nearest g5, rank +1, gap 1000-700-1=299, same_strand F, in_run F, interloper F
#   g7: nearest g5, rank +2, gap 1110-700-1=409, same_strand F
# S2 (g9 idx8): g7 rank -2 gap 5110-1200-1=3909 same F; g8 rank -1 gap 5110-5100-1=9 same T in_run T;
#   g10 rank +1 gap 6000-5200-1=799 same T in_run F (run_g10).  Total 7 rows.


class TestNeighbourCandidates(unittest.TestCase):
    def setUp(self):
        self.n = nt.neighbour_candidates(csv(GENOME_RUNS_CSV), csv(MEMBERS_CSV), window=2) \
            .set_index(["system_id", "candidate"])

    def test_rows(self):
        self.assertEqual(len(self.n), 7)
        self.assertEqual(sorted(self.n.loc["S1"].index), ["g2", "g3", "g6", "g7"])
        self.assertEqual(sorted(self.n.loc["S2"].index), ["g10", "g7", "g8"])

    def test_values(self):
        r = self.n.loc[("S1", "g3")]
        self.assertEqual((r.nearest_member, r.rank_offset, r.gap_to_nearest_member), ("g4", -1, 9))
        self.assertIs(nt.to_bool(r.same_strand), False)
        self.assertIs(nt.to_bool(r.in_system_run), False)
        self.assertIs(nt.to_bool(r.opposite_strand_interloper), True)
        r = self.n.loc[("S1", "g2")]
        self.assertEqual((r.rank_offset, r.gap_to_nearest_member), (-2, 109))
        self.assertIs(nt.to_bool(r.in_system_run), True)
        r = self.n.loc[("S1", "g7")]
        self.assertEqual((r.nearest_member, r.rank_offset, r.gap_to_nearest_member), ("g5", 2, 409))
        r = self.n.loc[("S2", "g7")]
        self.assertEqual((r.rank_offset, r.gap_to_nearest_member), (-2, 3909))
        r = self.n.loc[("S2", "g10")]
        self.assertEqual((r.rank_offset, r.gap_to_nearest_member), (1, 799))
        self.assertIs(nt.to_bool(r.same_strand), True)
        self.assertIs(nt.to_bool(r.in_system_run), False)

    def test_no_coordinate_candidates_by_tag_number(self):
        m = csv("""
locus_tag,system_id
PMM0004,S1
PMM0005,S1
""")
        # PMM0007 is 2 tag numbers from PMM0005 (<= window 2) -> candidate; PMM0020 is not.
        nc = nt.no_coordinate_candidates(m, ["PMM0007", "PMM0020"], window=2)
        self.assertEqual(nc["candidate"].tolist(), ["PMM0007"])
        self.assertEqual(nc["nearest_member"].tolist(), ["PMM0005"])
        self.assertEqual(nc["tag_distance"].tolist(), [2])


class TestClassifyNeighbourStep4(unittest.TestCase):
    def test_classes(self):
        df = csv("""
locus_tag,pfam_ids,brite_transporter,tcdb_ids,is_linked_enzyme,is_enzyme_candidate,has_coordinates
a,,False,,False,True,False
b,pfam:PF00005,False,tcdb:3.A.1.1.1,False,True,True
c,pfam:PF00005,False,,False,True,True
d,,False,,False,True,True
e,,False,,False,False,True
f,,False,,True,True,True
""")
        # a no coords (wins over everything); b TCDB; c role Pfam no TCDB -> missing_subunit;
        # d EC/reactions -> enzyme_candidate; e -> context; f linked enzyme flag (step 5) -> linked_enzyme
        got = {r.locus_tag: nt.classify_neighbour(r) for r in df.itertuples()}
        self.assertEqual(got, {"a": "no_coordinates", "b": "tcdb_transporter", "c": "missing_subunit",
                               "d": "enzyme_candidate", "e": "context", "f": "linked_enzyme"})

    def test_string_false_enzyme_flag(self):
        df = csv("""
locus_tag,pfam_ids,brite_transporter,tcdb_ids,is_enzyme_candidate,has_coordinates
e,,False,,False,True
""", dtype=str)
        self.assertEqual(nt.classify_neighbour(df.iloc[0]), "context")


class TestStep4Fixes(unittest.TestCase):
    def test_other_system_before_tcdb(self):
        df = csv("""
locus_tag,pfam_ids,brite_transporter,tcdb_ids,is_enzyme_candidate,has_coordinates,member_of_system
t,pfam:PF00005,False,tcdb:3.A.1.1.1,False,True,sys_X
u,pfam:PF00005,False,tcdb:3.A.1.1.1,False,True,
n,,False,,True,False,sys_Y
""")
        # t: member of another system -> other_system (checked before tcdb_transporter)
        # u: TCDB call but in no system -> tcdb_transporter ; n: no coordinates still wins first
        got = {r.locus_tag: nt.classify_neighbour(r) for r in df.itertuples()}
        self.assertEqual(got, {"t": "other_system", "u": "tcdb_transporter", "n": "no_coordinates"})

    def test_unseen_domain_gets_no_role(self):
        # step-2 map knows PF00005 only; LysR substrate-binding PF03466 unseen -> no role -> not recruited
        rm = {"PF00005": "atpase"}
        self.assertEqual(nt.pfam_role("pfam:PF03466", rm), "other")
        row = {"pfam_ids": "pfam:PF03466", "brite_transporter": "False", "tcdb_ids": "",
               "is_enzyme_candidate": "False", "has_coordinates": "True"}
        self.assertEqual(nt.classify_neighbour(row, rm), "context")


XREF_CSV = """
metabolite_id,name,chebi_id,mnxm_id
kegg.compound:C00244,Nitrate,25545,MNXM732399
chebi:14654,nitrate,14654,MNXM732398
kegg.compound:C01102,O-Phospho-L-homoserine,12693,MNXM1334
kegg.compound:C05702,O-Phosphorylhomoserine,12693,MNXM1334
kegg.compound:C00014,Ammonia,13405,MNXM729302
"""
# ids first: C01102 + C05702 share chebi 12693 -> group, basis "id".
# names: C00244 "Nitrate" and chebi:14654 "nitrate" share name_norm "nitrate" -> group, basis "name_soft".
# Ammonia alone -> basis "".


class TestEquivGroups(unittest.TestCase):
    def test_groups(self):
        x = nt.equiv_groups(csv(XREF_CSV, dtype={"chebi_id": str})).set_index("metabolite_id")
        self.assertEqual(x.loc["kegg.compound:C00244", "equiv_group"], x.loc["chebi:14654", "equiv_group"])
        self.assertEqual(x.loc["chebi:14654", "link_basis"], "name_soft")
        self.assertEqual(x.loc["kegg.compound:C01102", "equiv_group"], x.loc["kegg.compound:C05702", "equiv_group"])
        self.assertEqual(x.loc["kegg.compound:C05702", "link_basis"], "id")
        self.assertEqual(x.loc["kegg.compound:C00014", "link_basis"], "none")
        self.assertNotEqual(x.loc["kegg.compound:C00014", "equiv_group"], x.loc["chebi:14654", "equiv_group"])

    def test_chebi_float_string_normalised(self):
        df = csv(XREF_CSV)  # chebi parsed as int/float here
        x = nt.equiv_groups(df).set_index("metabolite_id")
        self.assertEqual(x.loc["kegg.compound:C05702", "link_basis"], "id")


# --------------------------------------------------------------------------- pilot step 5: can_use on equiv groups
GENOME_METAB_CSV = """
locus_tag,metabolite_id
cS,kegg.compound:C01417
cS,kegg.compound:C00014
gA,kegg.compound:C00014
nR,kegg.compound:C00244
"""
XREF5_CSV = """
metabolite_id,equiv_group,link_basis
kegg.compound:C01417,kegg.compound:C01417,
kegg.compound:C00014,kegg.compound:C00014,
kegg.compound:C00244,chebi:14654,name_soft
chebi:14654,chebi:14654,name_soft
kegg.compound:C00088,kegg.compound:C00088,
"""
# genome metabolism genes by group: C01417 {cS}; C00014 {cS,gA}; chebi:14654 group {nR} (via C00244)
#  cyanate, window {cS,x}, run {cS}  -> window co-located [cS], run co-located [cS], basis exact
#  ammonia, window {cS}, run {}      -> window co-located [cS]; run elsewhere in genome [cS,gA]
#  nitrate chebi:14654 (transport node), window {} run {} -> elsewhere [nR], basis name_soft
#  nitrite C00088 -> no


class TestCanUseEquiv(unittest.TestCase):
    def setUp(self):
        self.g = nt.genes_by_group(csv(GENOME_METAB_CSV), csv(XREF5_CSV))
        self.x = csv(XREF5_CSV).set_index("metabolite_id")

    def test_genes_by_group(self):
        self.assertEqual(self.g["chebi:14654"], {"nR": {"kegg.compound:C00244"}})
        self.assertEqual(set(self.g["kegg.compound:C00014"]), {"cS", "gA"})

    def test_cyanate(self):
        r = nt.can_use_equiv("kegg.compound:C01417", self.x, self.g, window_loci={"cS", "x"}, run_loci={"cS"})
        self.assertEqual((r["can_use_window"], r["can_use_run"]), ("co-located", "co-located"))
        self.assertEqual(r["linked_enzyme_loci_window"], "cS")
        self.assertEqual(r["match_basis"], "exact")

    def test_ammonia_window_vs_run(self):
        r = nt.can_use_equiv("kegg.compound:C00014", self.x, self.g, window_loci={"cS"}, run_loci=set())
        self.assertEqual((r["can_use_window"], r["can_use_run"]), ("co-located", "elsewhere in genome"))
        self.assertEqual(r["linked_enzyme_loci_run"], "")
        self.assertEqual(r["genome_enzyme_loci"], "cS|gA")

    def test_nitrate_via_name_soft(self):
        r = nt.can_use_equiv("chebi:14654", self.x, self.g, window_loci=set(), run_loci=set())
        self.assertEqual(r["can_use_window"], "elsewhere in genome")
        self.assertEqual(r["match_basis"], "name_soft")

    def test_nitrite_no(self):
        r = nt.can_use_equiv("kegg.compound:C00088", self.x, self.g, window_loci={"cS"}, run_loci={"cS"})
        self.assertEqual((r["can_use_window"], r["can_use_run"], r["match_basis"]), ("no", "no", "none"))

    def test_unknown_substrate_falls_back_to_own_id(self):
        r = nt.can_use_equiv("kegg.compound:C99999", self.x, self.g, window_loci=set(), run_loci=set())
        self.assertEqual(r["can_use_window"], "no")


# --------------------------------------------------------------------------- pilot step 6: currency + ms variant
class TestCurrency(unittest.TestCase):
    def test_constant_contents(self):
        ids = set(nt.CURRENCY_METABOLITES)
        # docs minimal-8 (11 KEGG ids: H2O, CO2, ATP, ADP, AMP, Pi, PPi, NAD+, NADH, NADP+, NADPH)
        for k in ["C00001", "C00011", "C00002", "C00008", "C00020", "C00009", "C00013",
                  "C00003", "C00004", "C00005", "C00006"]:
            self.assertIn("kegg.compound:" + k, ids)
        # coordinator extension: H+, CoA, FAD, GTP, GDP
        for k in ["C00080", "C00010", "C00016", "C00044", "C00035"]:
            self.assertIn("kegg.compound:" + k, ids)
        self.assertEqual(len(ids), 16)
        self.assertNotIn("kegg.compound:C00025", ids)  # glutamate is NOT currency (borderline, excluded)

    def test_currency_groups_via_xref(self):
        x = csv("""
metabolite_id,equiv_group
kegg.compound:C00002,kegg.compound:C00002
chebi:15422,kegg.compound:C00002
kegg.compound:C01417,kegg.compound:C01417
""")
        g = nt.currency_groups(x)
        # ATP's group (incl. its chebi twin) is currency; cyanate is not; ids absent from xref
        # (e.g. H2O, not N-containing) stay as their own group
        self.assertIn("kegg.compound:C00002", g)
        self.assertNotIn("kegg.compound:C01417", g)
        self.assertIn("kegg.compound:C00001", g)


MS_CSV = """
system_id,metabolite_id,substrate_depth,transport_substrate_resolution,is_lumping,is_currency,can_use_window,can_use_run,linked_enzyme_loci_window,linked_enzyme_loci_run
S,urea,most_specific,resolved,False,False,co-located,elsewhere in genome,e1,
S,atp,most_specific,resolved,False,True,co-located,co-located,e2,e2
S,cys,inherited,resolved,False,False,co-located,elsewhere in genome,e3,
S,val,most_specific,family_inferred,True,False,co-located,co-located,e4,e4
S,udpg,most_specific,resolved,True,False,co-located,co-located,e5,e5
"""
# Eligible = most_specific AND resolution == resolved AND not lumping AND not currency (API review C2).
# urea: eligible -> copies calls, loci e1. atp: currency -> n/a. cys: inherited -> n/a.
# val: family_inferred gene (superfamily-only) -> n/a (the PMM1682 / speE 2.A.1 case).
# udpg: resolved gene but the row's family is lumping (e.g. uvrA at 3.A.1) -> n/a (PMM1711 case).


class TestMsVariant(unittest.TestCase):
    def test_ms_columns(self):
        t = nt.add_ms_variant(csv(MS_CSV)).set_index("metabolite_id")
        self.assertEqual((t.loc["urea", "can_use_window_ms"], t.loc["urea", "can_use_run_ms"]),
                         ("co-located", "elsewhere in genome"))
        self.assertEqual(t.loc["urea", "linked_enzyme_loci_window_ms"], "e1")
        for m in ("atp", "cys", "val", "udpg"):
            self.assertEqual((t.loc[m, "can_use_window_ms"], t.loc[m, "can_use_run_ms"]),
                             ("not_eligible", "not_eligible"))
            self.assertEqual(t.loc[m, "linked_enzyme_loci_window_ms"], "")

    def test_string_false_currency(self):
        t = nt.add_ms_variant(csv(MS_CSV, dtype=str)).set_index("metabolite_id")
        self.assertEqual(t.loc["urea", "can_use_window_ms"], "co-located")
        self.assertEqual(t.loc["atp", "can_use_window_ms"], "not_eligible")


class TestLumpingAndNStatus(unittest.TestCase):
    def test_lumping_families(self):
        d = csv("""
term_id,level_kind,metabolite_count
tcdb:3.A.1,tc_family,554
tcdb:2.A.1,tc_family,476
tcdb:3.A.1.5,tc_subfamily,29
tcdb:1.A.11,tc_family,7
""")
        # threshold 100: tc_family with >= 100 substrates -> lumping (3.A.1, 2.A.1); subfamily never;
        # small family 1.A.11 not lumping.
        self.assertEqual(nt.lumping_families(d, threshold=100), {"tcdb:3.A.1", "tcdb:2.A.1"})

    def test_n_status(self):
        self.assertEqual(nt.n_status("C | H | N | O", "C2H5NO2"), "contains_N")
        self.assertEqual(nt.n_status("C | H | O", "C6H12O6"), "no_N")
        self.assertEqual(nt.n_status("Cl | Na", "ClNa"), "no_N")  # Na is not N
        self.assertEqual(nt.n_status(float("nan"), float("nan")), "no_formula")
        self.assertEqual(nt.n_status("", None), "no_formula")
        self.assertEqual(nt.n_status(["N", "O"], "NO3"), "contains_N")


class TestNoCoordinatePlaceability(unittest.TestCase):
    def test_status(self):
        m = csv("""
locus_tag,system_id
PMM0004,S1
PMM0900,S2
""")
        r = nt.no_coordinate_placeability(m, ["PMM0007", "PMM50003", "PMM_50048"], window=8)             .set_index("locus_tag")
        # PMM0007: prefix PMM shared, 3 from PMM0004 -> placed
        # PMM50003: prefix PMM shared, nearest member 49103 away -> prefix_shared_not_within_window
        # PMM_50048: prefix PMM_ shared with no member -> unplaceable
        self.assertEqual(r.loc["PMM0007", "placement_status"], "placed")
        self.assertEqual(r.loc["PMM50003", "placement_status"], "prefix_shared_not_within_window")
        self.assertEqual(r.loc["PMM_50048", "placement_status"], "unplaceable")
        self.assertIs(bool(r.loc["PMM50003", "shares_prefix_with_member"]), True)


class TestAttachRuns(unittest.TestCase):
    def test_universe_gene_without_coordinates_kept(self):
        runs = csv("""
locus_tag,run_id,opposite_strand_in_run,gap_to_next
g1,run_g1,False,10
g2,run_g1,False,
""").set_index("locus_tag")
        t = csv("""
locus_tag,role
g1,permease
g2,atpase
x9,single_carrier
""")
        # x9 has no coordinates (MIT9313 PMT_2355 / PMT_2631 case): never dropped; own pseudo-run;
        # has_coordinates False; opposite_strand_in_run False
        out = nt.attach_runs(t, runs).set_index("locus_tag")
        self.assertEqual(out.loc["g1", "run_id"], "run_g1")
        self.assertIs(bool(out.loc["g1", "has_coordinates"]), True)
        self.assertEqual(out.loc["x9", "run_id"], "nocoord_x9")
        self.assertIs(bool(out.loc["x9", "has_coordinates"]), False)
        self.assertIs(bool(out.loc["x9", "opposite_strand_in_run"]), False)
        self.assertEqual(len(out), 3)
        s = nt.group_systems(out.reset_index().assign(tcdb_ids=""), cross_locus=True)
        self.assertIn(["x9"], partition(s))


class TestLumpingCoverage(unittest.TestCase):
    TD = """
term_id,level_kind,metabolite_count
tcdb:3.A.1,tc_family,554
tcdb:3.A.1.5,tc_subfamily,29
tcdb:9.B.1,tc_family,
"""

    def test_required_family_missing_raises(self):
        with self.assertRaises(ValueError):
            nt.lumping_families(csv(self.TD), 100, required_ids=["tcdb:3.A.1", "tcdb:2.A.1"])

    def test_required_family_nan_count_raises(self):
        # a NaN metabolite_count must raise, never default to non-lumping
        with self.assertRaises(ValueError):
            nt.lumping_families(csv(self.TD), 100, required_ids=["tcdb:3.A.1", "tcdb:9.B.1"])

    def test_required_all_present_ok(self):
        self.assertEqual(nt.lumping_families(csv(self.TD), 100, required_ids=["tcdb:3.A.1", "tcdb:3.A.1.5"]),
                         {"tcdb:3.A.1"})


EXP_CSV = """
compound,can_use_window,can_use_run,can_use_window_ms,can_use_run_ms
nitrate,no,no,not_eligible,no
nitrate,no,no,no,no
nitrite,elsewhere in genome,elsewhere in genome,not_eligible,elsewhere in genome
nitrite,co-located,co-located,not_eligible,not_eligible
"""
# expected_usable False (nitrate): pass iff every considered (non not_eligible) value is "no".
# expected_usable True (nitrite): pass iff no considered value is "no".
# a definition with only not_eligible values -> pass None ("not evaluable"), counts still shown.


class TestExpectationCheck(unittest.TestCase):
    def test_not_usable_all_no_passes(self):
        t = csv(EXP_CSV)
        r = nt.expectation_check(t[t.compound == "nitrate"], expected_usable=False)
        self.assertIs(r["can_use_window"]["pass"], True)
        self.assertIs(r["can_use_window_ms"]["pass"], True)  # not_eligible ignored, the other row is "no"
        self.assertEqual(r["can_use_window_ms"]["observed"], {"not_eligible": 1, "no": 1})

    def test_usable_passes_and_na_only_not_evaluable(self):
        t = csv(EXP_CSV)
        r = nt.expectation_check(t[t.compound == "nitrite"], expected_usable=True)
        self.assertIs(r["can_use_window"]["pass"], True)
        self.assertIs(r["can_use_run_ms"]["pass"], True)
        self.assertIsNone(r["can_use_window_ms"]["pass"])  # only not_eligible

    def test_mismatch_fails(self):
        t = csv(EXP_CSV)
        r = nt.expectation_check(t[t.compound == "nitrate"], expected_usable=True)
        self.assertIs(r["can_use_window"]["pass"], False)


class TestNoNaCollidingCategories(unittest.TestCase):
    """Category values must survive a round trip through DEFAULT pd.read_csv (no keep_default_na):
    "n/a", "" etc. are in pandas' default NA set and would come back as NaN (critic finding)."""

    @staticmethod
    def roundtrip(df):
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        return pd.read_csv(buf)  # default NA handling, deliberately

    def test_strict_columns_roundtrip_no_nan(self):
        flagged = nt.add_ms_variant(csv(MS_CSV))
        back = self.roundtrip(flagged)
        for c in ("can_use_window_ms", "can_use_run_ms"):
            self.assertFalse(back[c].isna().any(), c)
            self.assertIn("not_eligible", set(back[c]))
        # urea eligible -> calls copied; atp/cys/val/udpg -> not_eligible: 4 of 5 rows
        self.assertEqual(int((back["can_use_window_ms"] == "not_eligible").sum()), 4)

    def test_match_basis_and_link_basis_roundtrip(self):
        x = nt.equiv_groups(csv(XREF_CSV, dtype={"chebi_id": str}))
        back = self.roundtrip(x)
        self.assertFalse(back["link_basis"].isna().any())
        self.assertEqual(back.set_index("metabolite_id").loc["kegg.compound:C00014", "link_basis"], "none")
        g = nt.genes_by_group(csv(GENOME_METAB_CSV), csv(XREF5_CSV))
        r = nt.can_use_equiv("kegg.compound:C00088", csv(XREF5_CSV).set_index("metabolite_id"), g, set(), set())
        self.assertEqual(self.roundtrip(pd.DataFrame([r]))["match_basis"].iloc[0], "none")

    def test_no_value_in_pandas_default_na_set(self):
        from pandas._libs.parsers import STR_NA_VALUES
        for v in ("not_eligible", "none", "no", "co-located", "elsewhere in genome"):
            self.assertNotIn(v, STR_NA_VALUES)


# --------------------------------------------------------------------------- decide-gate build (2026-10-08)
GENE_GROUPS = {"cS": {"cyanate", "ammonia"}, "gA": {"ammonia"}, "pn": {"ammonia"}, "tq": {"cyanate"},
               "m1": {"cyanate"}}
GENE_ROLES = {"cS": {"cyanorak.role:E.4"}, "gA": {"cyanorak.role:E.4", "cyanorak.role:A.3"},
              "pn": {"cyanorak.role:B.11"}, "tq": {"cyanorak.role:Q.1"}, "m1": {"cyanorak.role:E.4"}}
# system members {m1}; system roles = {E.4, Q.1}; carried groups {cyanate, ammonia}
#  function-linked (any distance): reaction on a carried group AND a shared NON-Q role; members excluded
#   cS: cyanate+ammonia, shares E.4 -> (ammonia, cS), (cyanate, cS)
#   gA: ammonia, shares E.4 -> (ammonia, gA)
#   pn: ammonia but only B.11 -> not linked (the pncC case)
#   tq: cyanate but shares only Q.1 (transport branch) -> not linked
#   m1: member -> excluded


class TestFunctionLinks(unittest.TestCase):
    def test_links(self):
        out = nt.function_links({"cyanorak.role:E.4", "cyanorak.role:Q.1"}, {"cyanate", "ammonia"},
                                GENE_GROUPS, GENE_ROLES, members={"m1"})
        got = sorted((r["equiv_group"], r["locus_tag"], r["shared_role_ids"]) for r in out)
        self.assertEqual(got, [("ammonia", "cS", "cyanorak.role:E.4"), ("ammonia", "gA", "cyanorak.role:E.4"),
                               ("cyanate", "cS", "cyanorak.role:E.4")])

    def test_q_only_system_links_nothing(self):
        self.assertEqual(nt.function_links({"cyanorak.role:Q.1"}, {"cyanate"}, GENE_GROUPS, GENE_ROLES, members=set()), [])


class TestNeighbourLinks(unittest.TestCase):
    def test_ubiquity_excludes(self):
        # window {cS, pn}; ammonia has 36 genes >= threshold 30 -> excluded; cyanate 1 gene -> kept
        out = nt.neighbour_links({"cyanate", "ammonia"}, {"cS", "pn"}, GENE_GROUPS,
                                 ubiquity={"ammonia": 36, "cyanate": 1}, threshold=30)
        self.assertEqual(sorted((r["equiv_group"], r["locus_tag"]) for r in out), [("cyanate", "cS")])

    def test_threshold_is_a_parameter(self):
        out = nt.neighbour_links({"ammonia"}, {"pn"}, GENE_GROUPS, ubiquity={"ammonia": 36}, threshold=40)
        self.assertEqual([(r["equiv_group"], r["locus_tag"]) for r in out], [("ammonia", "pn")])


class TestTransportClass(unittest.TestCase):
    def test_union_of_q_roles(self):
        roles = {"a": {"cyanorak.role:Q.1", "cyanorak.role:E.4"}, "b": {"cyanorak.role:Q.1"}, "c": {"cyanorak.role:Q.4"}}
        names = {"cyanorak.role:Q.1": "Transport > Amino acids, peptides and amines", "cyanorak.role:Q.4": "Cations"}
        ids, nm = nt.transport_class(roles, names)
        self.assertEqual(ids, "cyanorak.role:Q.1|cyanorak.role:Q.4")
        self.assertEqual(nm, "Transport > Amino acids, peptides and amines|Cations")
        self.assertEqual(nt.transport_class({"x": {"cyanorak.role:E.4"}}, names), ("none", "none"))


class TestSystemTier(unittest.TestCase):
    def t(self, **kw):
        base = dict(strong=False, tcdb_only=False, role_complete=False, member_resolutions=[], c123_max_score=None)
        base.update(kw)
        return nt.system_tier(**base)

    def test_rules(self):
        # amt1: strong, complete (single carrier), resolved, 0.8 -> High
        self.assertEqual(self.t(strong=True, role_complete=True, member_resolutions=["resolved"], c123_max_score=0.8)[0], "High")
        # salY: strong, incomplete, family_inferred only -> Low (superfamily-only)
        self.assertEqual(self.t(strong=True, member_resolutions=["family_inferred"], c123_max_score=0.8)[0], "Low")
        # fadD: tcdb_only, resolved, class 1-3 max score 0.0 -> Low (score-0-only)
        tier, why = self.t(tcdb_only=True, member_resolutions=["resolved"], c123_max_score=0.0)
        self.assertEqual(tier, "Low")
        self.assertIn("score-0", why)
        # v1.4: tcdb_only (no strong member) + resolved + score 0.6 -> Low catalogue-only;
        # strong incomplete resolved -> Medium
        tier, why = self.t(tcdb_only=True, member_resolutions=["resolved"], c123_max_score=0.6)
        self.assertEqual(tier, "Low")
        self.assertEqual(why, "catalogue-only (TCDB hit, no domain/KO/curated support)")
        self.assertEqual(self.t(strong=True, member_resolutions=["resolved"], c123_max_score=0.8)[0], "Medium")
        # mixed member resolutions count as resolved (flagged in the reason)
        tier, why = self.t(strong=True, role_complete=True, member_resolutions=["resolved", "family_inferred"],
                           c123_max_score=0.8)
        self.assertEqual(tier, "High")
        self.assertIn("mixed", why)
        # strong + complete but no TCDB at all -> Medium (not resolved)
        self.assertEqual(self.t(strong=True, role_complete=True, member_resolutions=[], c123_max_score=None)[0], "Medium")
        # no member is a likely transporter -> not_transporter
        self.assertEqual(self.t(member_resolutions=["resolved"], c123_max_score=None)[0], "not_transporter")


class TestCompoundClass(unittest.TestCase):
    def c(self, *names):
        return nt.compound_class(list(names))

    def test_inorganic_and_small(self):
        self.assertEqual(self.c("Ammonia")[:2], ("ammonium", "ammonium_exact"))
        self.assertEqual(self.c("methylamine")[0], "ammonium")
        self.assertIs(self.c("methylamine")[2], True)            # analogue flagged
        self.assertIs(self.c("Ammonia")[2], False)
        self.assertEqual(self.c("Urea")[:3], ("urea", "urea_exact", False))
        self.assertEqual(self.c("thiourea")[:3], ("urea", "urea_analogue", True))
        self.assertEqual(self.c("Cyanate")[0], "cyanate")
        self.assertEqual(self.c("Nitrite")[0], "nitrite")
        self.assertEqual(self.c("nitrate", "Nitrate")[0], "nitrate")

    def test_organic_classes(self):
        self.assertEqual(self.c("L-Glutamate")[0], "amino acids")
        self.assertEqual(self.c("Glycine betaine")[0], "osmolytes")      # osmolyte rule before amino acids
        self.assertEqual(self.c("dipeptide")[0], "peptides")
        self.assertEqual(self.c("Glutathione")[0], "peptides")
        self.assertEqual(self.c("Spermidine")[0], "polyamines")
        self.assertEqual(self.c("Thymidine")[0], "nucleobases/nucleosides")
        self.assertEqual(self.c("purine")[0], "nucleobases/nucleosides")
        self.assertEqual(self.c("S-Adenosyl-L-methionine")[0], "unclassified N")  # no substring matching
        self.assertEqual(self.c("Thiamin diphosphate")[:2], ("unclassified N", "no_rule"))

    def test_can_use_applicable(self):
        for k in ("amino acids", "peptides", "polyamines", "nucleobases/nucleosides", "osmolytes"):
            self.assertIs(nt.can_use_applicable(k), False)
        for k in ("ammonium", "urea", "cyanate", "nitrite", "nitrate", "unclassified N"):
            self.assertIs(nt.can_use_applicable(k), True)



# --------------------------------------------------------------------------- researcher decisions 2026-10-08 (A-D)
class TestCuratedTransportBasis(unittest.TestCase):
    # A: a Cyanorak Q.* role is a third basis for "strong"
    def test_cyanorak_q_makes_strong(self):
        row = {"pfam_ids": "pfam:PF01226", "brite_transporter": "False", "tcdb_ids": "tcdb:1.A.16",
               "cyanorak_roles": "cyanorak.role:Q.2 | cyanorak.role:D.1.3"}
        self.assertEqual(nt.likely_transporter_basis(row), "cyanorak|tcdb")
        self.assertEqual(nt.likely_transporter(row), "strong")

    def test_non_q_cyanorak_role_is_not_a_basis(self):
        row = {"pfam_ids": "", "brite_transporter": "False", "tcdb_ids": "tcdb:2.A.1",
               "cyanorak_roles": "cyanorak.role:E.4"}
        self.assertEqual(nt.likely_transporter(row), "tcdb_only")

    def test_absent_column_unchanged(self):
        self.assertEqual(nt.likely_transporter({"pfam_ids": "", "brite_transporter": "False", "tcdb_ids": "tcdb:2.A.1"}),
                         "tcdb_only")

    def test_curated_overrides_score0_low(self):
        # focA: strong via cyanorak Q.2, role-incomplete, resolved, class 1-3 max score 0 -> Medium (not Low)
        tier, why = nt.system_tier(strong=True, tcdb_only=False, role_complete=False,
                                   member_resolutions=["resolved"], c123_max_score=0.0, curated_q=True)
        self.assertEqual(tier, "Medium")
        # without the curated basis the score-0 rule still applies
        self.assertEqual(nt.system_tier(strong=False, tcdb_only=True, role_complete=False,
                                        member_resolutions=["resolved"], c123_max_score=0.0)[0], "Low")
        # v1.6 (researcher decision 2026-10-08): the curated basis DOES lift superfamily-only (see TestCuratedLiftsSuperfamily)
        self.assertEqual(nt.system_tier(strong=True, tcdb_only=False, role_complete=False,
                                        member_resolutions=["family_inferred"], c123_max_score=0.8,
                                        curated_q=True)[0], "Medium")


class TestUbiquitousAllowlist(unittest.TestCase):
    # B: for groups at/above the ubiquity threshold only allow-listed assimilation ECs link
    def test_allowlist(self):
        ecs = {"cS": {"ec:4.2.1.104"}, "gA": {"ec:6.3.1.2"}, "pn": set(), "tq": set(), "m1": set()}
        out = nt.function_links({"cyanorak.role:E.4", "cyanorak.role:Q.1"}, {"cyanate", "ammonia"}, GENE_GROUPS,
                                GENE_ROLES, members={"m1"}, ubiquity={"ammonia": 36, "cyanate": 1}, threshold=30,
                                gene_ecs=ecs)
        got = sorted((r["equiv_group"], r["locus_tag"], r["link_breadth"]) for r in out)
        # cS keeps cyanate (specific) but loses ammonia (EC 4.2.1.104 not allow-listed); gA keeps ammonia
        self.assertEqual(got, [("ammonia", "gA", "ubiquitous_allowlisted"), ("cyanate", "cS", "specific")])

    def test_allowlist_ecs_documented(self):
        self.assertEqual(set(nt.UBIQUITOUS_ALLOWLIST_EC), {"6.3.1.2", "1.4.7.1"})


class TestNoFormulaUnclassified(unittest.TestCase):
    # C: no-formula groups that no rule classifies are "unclassified (no formula)", never "other N"
    def test_no_formula(self):
        self.assertEqual(nt.compound_class(["a phospholipid derivative"], n_status=["no_formula"])[0],
                         "unclassified (no formula)")
        self.assertEqual(nt.compound_class(["Thiamin diphosphate"], n_status=["contains_N"])[0], "unclassified N")
        self.assertEqual(nt.compound_class(["dipeptide"], n_status=["no_formula"])[0], "peptides")


class TestNameRuleGaps(unittest.TestCase):
    # D layer 1 fixes
    def test_amino_acid_generic(self):
        for n in ("alpha-amino acid", "an alpha-amino acid", "polar amino acid", "Amino acid(NH3+)", "L-alpha-amino acid"):
            self.assertEqual(nt.compound_class([n])[0], "amino acids", n)

    def test_dipeptide_names(self):
        for n in ("Lys-Arg", "L-alanyl-L-alanine", "Gly-Pro-Ala", "N-formyl-peptide"):
            self.assertEqual(nt.compound_class([n])[0], "peptides", n)

    def test_amines(self):
        self.assertEqual(nt.compound_class(["Ethanolamine"])[0], "amines")
        self.assertEqual(nt.compound_class(["Tyramine"])[0], "amines")
        self.assertEqual(nt.compound_class(["Thiamine"])[0], "unclassified N")  # not an amine by suffix
        self.assertEqual(nt.compound_class(["Methylamine"])[0], "ammonium")     # analogue rule first
        self.assertEqual(nt.compound_class(["Ethylamine"])[0], "ammonium")
        self.assertIs(nt.can_use_applicable("amines"), False)


class TestPathwayLayer(unittest.TestCase):
    def test_pathway_class_rules(self):
        self.assertEqual(nt.pathway_class("kegg.pathway:ko00250", "Alanine, aspartate and glutamate metabolism")[0], "amino acids")
        self.assertEqual(nt.pathway_class("kegg.pathway:ko00230", "Purine metabolism")[0], "nucleobases/nucleosides")
        self.assertEqual(nt.pathway_class("kegg.pathway:ko00332", "Carbapenem biosynthesis")[0], "xenobiotic")
        self.assertEqual(nt.pathway_class("kegg.pathway:ko00730", "Thiamine metabolism")[0], "cofactors/vitamins")
        self.assertIsNone(nt.pathway_class("kegg.pathway:ko01100", "Metabolic pathways")[0])   # global map
        self.assertIsNone(nt.pathway_class("kegg.pathway:ko00010", "Glycolysis / Gluconeogenesis")[0])

    def test_vote_majority_tie_none(self):
        pmap = {"a1": "amino acids", "a2": "amino acids", "x": "xenobiotic", "n": None}
        self.assertEqual(nt.pathway_vote(["a1", "a2", "x", "n"], pmap)[0], "amino acids")      # 2 of 3 mapped
        cls, votes, tied = nt.pathway_vote(["a1", "x"], pmap)
        self.assertIsNone(cls)
        self.assertEqual(sorted(tied), ["amino acids", "xenobiotic"])
        self.assertEqual(nt.pathway_vote(["n"], pmap), (None, {}, []))


class TestFamilyContextLayer(unittest.TestCase):
    def test_family_context(self):
        self.assertEqual(nt.family_context_class("The Multidrug/Oligosaccharidyl-lipid/Polysaccharide (MOP) Flippase Superfamily", [])[0],
                         "xenobiotic (efflux family)")
        self.assertEqual(nt.family_context_class("The Iron Chelate Uptake Transporter (FeCT) Family", [])[0], "siderophore")
        self.assertEqual(nt.family_context_class("Some family", ["siderophore transport"])[0], "siderophore")
        self.assertIsNone(nt.family_context_class("The Peptide/Opine/Nickel Uptake Transporter (PepT) Family",
                                                  ["transporter activity"])[0])
        # GO links of lumping families are ignored (name only)
        self.assertIsNone(nt.family_context_class("The Major Facilitator Superfamily (MFS)", ["xenobiotic transport"],
                                                  use_go=False)[0])

    def test_group_family_class_needs_all_rows(self):
        self.assertEqual(nt.group_family_class(["siderophore", "siderophore"]), "siderophore")
        self.assertIsNone(nt.group_family_class(["siderophore", None]))
        self.assertIsNone(nt.group_family_class([]))


class TestNameOnlyClassWithContext(unittest.TestCase):
    # decision 2026-10-08 (v1.3): compound class = name rules only; pathways and carrying family are CONTEXT
    def test_name_assigns(self):
        r = nt.name_class_with_context(["contains_N"], ("amino acids", "amino_acid_name", False),
                                       ("xenobiotic", {"xenobiotic": 3}, []), "siderophore")
        self.assertEqual((r["compound_class"], r["class_source"]), ("amino acids", "name"))
        self.assertIn("xenobiotic:3", r["pathway_context"])
        self.assertEqual(r["family_context"], "siderophore")

    def test_pathway_and_family_never_assign(self):
        # thyroxine-like: pathway majority 'amino acids' but no name rule -> unclassified N
        r = nt.name_class_with_context(["contains_N"], (None, "no_rule", False),
                                       ("amino acids", {"amino acids": 1}, []), "xenobiotic (efflux family)")
        self.assertEqual((r["compound_class"], r["class_source"]), ("unclassified N", "none"))
        self.assertIn("amino acids:1", r["pathway_context"])
        self.assertEqual(r["family_context"], "xenobiotic (efflux family)")
        # a pathway tie is no longer broken by the transport class
        r = nt.name_class_with_context(["contains_N"], (None, "no_rule", False),
                                       (None, {"amino acids": 1, "cofactors/vitamins": 1}, ["amino acids", "cofactors/vitamins"]), None)
        self.assertEqual(r["compound_class"], "unclassified N")

    def test_no_formula_leftover_and_caveat(self):
        r = nt.name_class_with_context(["no_formula"], (None, "no_rule", False), (None, {}, []), None)
        self.assertEqual(r["compound_class"], "unclassified (no formula)")
        self.assertEqual(r["pathway_context"], "none")
        self.assertEqual(r["family_context"], "none")
        self.assertEqual(r["class_caveat"], "best effort: names only; KG has no chemical categories")
        self.assertFalse(hasattr(nt, "layered_class"))  # the layered assignment is gone


class TestCuratedBasisUpgradeOnly(unittest.TestCase):
    # decision 2026-10-08 (v1.3): a Cyanorak Q role only UPGRADES a catalogue-listed gene (tcdb_only -> strong)
    def test_q_without_tcdb_stays_none(self):
        row = {"pfam_ids": "pfam:PF00977", "brite_transporter": "False", "tcdb_ids": "",
               "cyanorak_roles": "cyanorak.role:A.4 | cyanorak.role:Q.1"}   # hisF-like
        self.assertEqual(nt.likely_transporter(row), "none")
        self.assertEqual(nt.likely_transporter_basis(row), "cyanorak")      # basis still recorded

    def test_q_with_non_transport_tcdb_class_stays_none(self):
        row = {"pfam_ids": "", "brite_transporter": "False", "tcdb_ids": "tcdb:9.A.1",
               "cyanorak_roles": "cyanorak.role:Q.9"}
        self.assertEqual(nt.likely_transporter(row), "none")

    def test_q_upgrades_tcdb_only(self):
        row = {"pfam_ids": "", "brite_transporter": "False", "tcdb_ids": "tcdb:1.A.16",
               "cyanorak_roles": "cyanorak.role:Q.2"}                       # focA-like
        self.assertEqual(nt.likely_transporter(row), "strong")



# --------------------------------------------------------------------------- v1.4 fix package (2026-10-08)
class TestCatalogueOnlyTier(unittest.TestCase):
    def test_tcdb_only_never_medium(self):
        for res in (["resolved"], ["resolved", "family_inferred"], []):
            tier, why = nt.system_tier(strong=False, tcdb_only=True, role_complete=True,
                                       member_resolutions=res, c123_max_score=0.9)
            self.assertEqual(tier, "Low", res)
            self.assertTrue(why.startswith("catalogue-only"), why)

    def test_strong_rules_unchanged(self):
        self.assertEqual(nt.system_tier(strong=True, tcdb_only=True, role_complete=False,
                                        member_resolutions=["resolved"], c123_max_score=0.8)[0], "Medium")
        self.assertEqual(nt.system_tier(strong=True, tcdb_only=False, role_complete=True,
                                        member_resolutions=["resolved"], c123_max_score=0.8)[0], "High")

    def test_earlier_low_reasons_keep_precedence(self):
        # superfamily-only and score-0-only are checked first (reasons unchanged for those systems)
        self.assertTrue(nt.system_tier(strong=False, tcdb_only=True, role_complete=False,
                                       member_resolutions=["resolved"], c123_max_score=0.0)[1].startswith("score-0"))
        self.assertTrue(nt.system_tier(strong=False, tcdb_only=True, role_complete=False,
                                       member_resolutions=["family_inferred"], c123_max_score=0.5)[1].startswith("superfamily"))

    def test_transporter_candidate(self):
        self.assertTrue(nt.is_transporter_candidate("High"))
        self.assertTrue(nt.is_transporter_candidate("Medium"))
        self.assertFalse(nt.is_transporter_candidate("Low"))
        self.assertFalse(nt.is_transporter_candidate("not_transporter"))


class TestKoBasisUpgradeOnly(unittest.TestCase):
    def test_gst_like_ko_only_is_none(self):
        row = {"pfam_ids": "pfam:PF00043 | pfam:PF13409", "brite_transporter": "True", "tcdb_ids": ""}
        self.assertEqual(nt.likely_transporter_basis(row), "ko")
        self.assertEqual(nt.likely_transporter(row), "none")

    def test_ko_with_non_transport_tcdb_class_is_none(self):
        row = {"pfam_ids": "", "brite_transporter": "True", "tcdb_ids": "tcdb:8.A.1"}
        self.assertEqual(nt.likely_transporter(row), "none")

    def test_ko_upgrades_tcdb_only(self):
        row = {"pfam_ids": "", "brite_transporter": "True", "tcdb_ids": "tcdb:2.A.1.1"}
        self.assertEqual(nt.likely_transporter(row), "strong")

    def test_role_pfam_alone_still_strong(self):
        row = {"pfam_ids": "pfam:PF00909", "brite_transporter": "False", "tcdb_ids": ""}
        self.assertEqual(nt.likely_transporter(row), "strong")


class TestKnownFalsePositive(unittest.TestCase):
    def test_ferritin_by_product(self):
        fp, why = nt.known_false_positive(["ferritin", "hypothetical protein"], ["ftn", None])
        self.assertTrue(fp)
        self.assertIn("ferritin", why)

    def test_not_bacterioferritin_or_other(self):
        self.assertFalse(nt.known_false_positive(["bacterioferritin comigratory protein"], ["bcp"])[0])
        self.assertFalse(nt.known_false_positive(["ammonium transporter"], ["amt1"])[0])
        self.assertEqual(nt.known_false_positive([], [])[1], "none")

    def test_case_insensitive(self):
        self.assertTrue(nt.known_false_positive(["Ferritin"], [None])[0])


FRAG_COORDS = """
locus_tag,gene_name,product,contig,start,end,strand
PMN2A_1298,nirA,ferredoxin--nitrite reductase,C1,1805411,1807072,+
PMN2A_RS10340,nirA,ferredoxin--nitrite reductase,C1,1807114,1807275,+
PMN2A_1299,focA,"nitrite transporter, FNT family",C1,1807338,1808228,+
X_RS00001,,hypothetical protein,C1,1808230,1808400,+
X_0002,,hypothetical protein,C1,1808450,1808600,+
X_RS00003,abc,ABC transporter,C1,1808650,1808700,-
X_0004,abc,ABC transporter,C1,1808720,1809000,+
X_RS00005,lys,lysine permease,C1,1809500,1809600,+
X_0006,lys,lysine permease,C1,1809750,1810000,+
X_RS00007,ovl,overlapping protein,C1,1810100,1810300,+
X_0008,ovl,Overlapping protein,C1,1810250,1810900,+
X_RS00009,ali,aliased gene,C1,1811000,1811100,+
X_0010,ali,aliased gene,C1,1811120,1811500,+
X_RS00011,ripp,CCRG-2 family RiPP,C1,1812000,1812150,+
X_RS00012,ripp,CCRG-2 family RiPP,C1,1812212,1812360,+
"""


class TestRefseqFragments(unittest.TestCase):
    def setUp(self):
        self.c = csv(FRAG_COORDS)
        self.aliases = {"X_RS00009": ["PMN2A_9999", "WP_1.1"], "PMN2A_RS10340": ["WP_225866306.1"]}
        self.f = nt.refseq_fragments(self.c, self.aliases).set_index("locus_tag")

    def test_nirA_fragment(self):
        self.assertEqual(self.f.loc["PMN2A_RS10340", "fragment_of"], "PMN2A_1298")
        self.assertEqual(self.f.loc["PMN2A_RS10340", "gap_bp"], 41)

    def test_overlap_counts(self):
        self.assertEqual(self.f.loc["X_RS00007", "fragment_of"], "X_0008")   # overlap, product case ignored
        self.assertLess(self.f.loc["X_RS00007", "gap_bp"], 0)

    def test_rejections(self):
        for lt in ("X_RS00001",   # generic product (hypothetical protein) guard
                   "X_RS00003",   # opposite strand
                   "X_RS00005",   # gap 149 > 100
                   "X_RS00009",   # has a PMx-style old locus-tag alias
                   "X_RS00011", "X_RS00012"):  # two RefSeq-only tandem copies: the parent must not be RefSeq-only
            self.assertNotIn(lt, self.f.index, lt)
        self.assertEqual(set(self.f.index), {"PMN2A_RS10340", "X_RS00007"})

    def test_refseq_only(self):
        self.assertTrue(nt.is_refseq_only("PMN2A_RS10340", ["WP_225866306.1"]))
        self.assertFalse(nt.is_refseq_only("PMN2A_RS10340", ["PMN2A_1300"]))
        self.assertFalse(nt.is_refseq_only("PMN2A_1298", []))
        self.assertTrue(nt.is_refseq_only("TX50_RS03815", None))

    def test_link_counts_exclude_fragments(self):
        df = pd.DataFrame({"system_id": ["s1", "s1", "s1", "s2"],
                           "locus_tag": ["PMN2A_1298", "PMN2A_RS10340", "PMN2A_1298", "PMN2A_RS10340"]})
        got = nt.link_counts(df, {"PMN2A_RS10340"})
        self.assertEqual(got, {"s1": 1, "s2": 0})


class TestNameRulesV14(unittest.TestCase):
    def cls(self, n):
        return nt.compound_class([n])[0]

    def test_osmolytes(self):
        for n in ("beta-Alaninebetaine", "Proline betaine", "O-Acetylcarnitine", "O-Butanoylcarnitine",
                  "O-acetyl-D-carnitine", "4-Trimethylammoniobutanoate", "(E)-4-(Trimethylammonio)but-2-enoate",
                  "5-Hydroxyectoine", "Hypotaurine", "Ectoine"):
            self.assertEqual(self.cls(n), "osmolytes", n)
        # detergent quaternary ammoniums are not "trimethylammonio" names
        self.assertEqual(self.cls("Cetyltrimethylammonium bromide"), "unclassified N")

    def test_amino_acids(self):
        for n in ("L-Cystine", "Hydroxyproline", "trans-4-Hydroxy-L-proline", "L-Selenomethionine", "selenocystine",
                  "S-Methyl-L-methionine", "Homoarginine", "L-DOPA", "branched-chain amino acid"):
            self.assertEqual(self.cls(n), "amino acids", n)
        self.assertEqual(self.cls("S-Methyl-L-cysteine"), "unclassified N")   # not in the approved list

    def test_peptides_polyamines_nucleo(self):
        for n in ("Bradykinin", "microcin", "microcin c", "Bacitracin"):
            self.assertEqual(self.cls(n), "peptides", n)
        self.assertEqual(self.cls("sym-Homospermidine"), "polyamines")
        self.assertEqual(self.cls("5-Fluorouridine"), "nucleobases/nucleosides")
        self.assertEqual(self.cls("a purine nucleobase"), "nucleobases/nucleosides")

    def test_amino_sugars(self):
        for n in ("N-acetylglucosamine", "N-Acetyl-beta-D-glucosamine", "glucosamine", "N-acetylgalactosamine",
                  "Chitobiose", "N-Acetyl-beta-neuraminate", "N-glycoloyl-beta-neuraminic acid", "Lacto-N-biose",
                  "N-acetyl-beta-D-glucosaminyl-(1->4)-N-acetyl-aldehydo-D-glucosamine"):
            self.assertEqual(self.cls(n), "amino sugars", n)
        # nucleotide sugars and the polymer are not amino-sugar substrates by these rules
        for n in ("UDP-N-acetyl-alpha-D-glucosamine", "CMP-N-acetylneuraminate", "Chitin"):
            self.assertEqual(self.cls(n), "unclassified N", n)
        self.assertIs(nt.can_use_applicable("amino sugars"), False)
        # allowed for no_formula groups
        self.assertEqual(nt.compound_class(["N-acetylglucosamine"], n_status=["no_formula"])[0], "amino sugars")

    def test_quaternary_ammoniums_not_ammonium_analogues(self):
        for n in ("Tetramethylammonium", "Tetraethylammonium"):
            self.assertEqual(self.cls(n), "unclassified N", n)
        self.assertEqual(self.cls("Triethylamine"), "amines")      # tertiary amine: amines, not an NH4+ analogue
        self.assertEqual(nt.compound_class(["Methylamine"])[:3], ("ammonium", "ammonium_analogue", True))
        self.assertEqual(nt.compound_class(["Ethylamine"])[:3], ("ammonium", "ammonium_analogue", True))


# --------------------------------------------------------------------------- v1.5 (2026-10-08): Rule A3 adjacent_abc
ADJ_CSV = """
locus_tag,run_id,role,tcdb_ids,likely_transporter,strand,next_locus_tag,gap_to_next
eA,run_e,atpase,tcdb:2.A.130 | tcdb:3.A.1,strong,+,eB,0
eB,run_e,permease,tcdb:3.A.1,strong,+,eC,-4
eC,run_e,permease,tcdb:3.A.1.141,strong,+,zz1,3
pc,run_d,other,tcdb:3.A.9,tcdb_only,+,dB,-1
dB,run_d,other,tcdb:3.A.1,strong,+,dC,-1
dC,run_d,permease,tcdb:3.A.1.114,strong,+,dA,14
dA,run_d,atpase,tcdb:3.A.1,strong,+,zz2,22
"""
# evr-like: eA (atpase) + eB (permease) join by role (A2); eC (second permease, 3 bp after eB) can only
#   join through A3 (roles overlap). dev-like: dC + dA join by role (A2); dB ('other', strong, shares
#   tcdb:3.A.1, immediately before dC) joins through A3; pc ('other', tcdb_only, 3.A.9) never joins.


class TestAdjacentAbcRule(unittest.TestCase):
    def g(self, text=ADJ_CSV, **kw):
        return nt.group_systems(csv(text), cross_locus=False, **kw)

    def test_second_permease_joins(self):
        s = self.g()
        self.assertIn(["eA", "eB", "eC"], partition(s))
        jb = dict(zip(s.locus_tag, s.joined_by))
        self.assertIn("adjacent_abc", jb["eC"].split("|"))
        self.assertIn("role", jb["eC"].split("|"))

    def test_strong_other_joins_but_tcdb_only_other_does_not(self):
        p = partition(self.g())
        self.assertIn(["dA", "dB", "dC"], p)
        self.assertIn(["pc"], p)

    def test_rule_off_without_adjacency_columns(self):
        t = csv(ADJ_CSV).drop(columns=["strand", "next_locus_tag", "gap_to_next"])
        p = partition(nt.group_systems(t, cross_locus=False))
        self.assertIn(["eA", "eB"], p)
        self.assertIn(["eC"], p)
        self.assertIn(["dB"], p)

    def test_switch_off(self):
        p = partition(self.g(join_adjacent_abc=False))
        self.assertIn(["eC"], p)
        self.assertIn(["dB"], p)

    def test_not_immediately_adjacent_or_far_or_other_strand(self):
        base = ADJ_CSV
        # an intervening gene (next of eB is a non-universe gene) -> no join
        p = partition(self.g(base.replace("eB,run_e,permease,tcdb:3.A.1,strong,+,eC,-4",
                                          "eB,run_e,permease,tcdb:3.A.1,strong,+,xx,-4")))
        self.assertIn(["eC"], p)
        # gap 250 > 200 -> no join
        p = partition(self.g(base.replace("+,eC,-4", "+,eC,250")))
        self.assertIn(["eC"], p)
        # opposite strand -> no join
        p = partition(self.g(base.replace("eC,run_e,permease,tcdb:3.A.1.141,strong,+", "eC,run_e,permease,tcdb:3.A.1.141,strong,-")))
        self.assertIn(["eC"], p)

    def test_other_needs_shared_level2_ancestor(self):
        p = partition(self.g(ADJ_CSV.replace("dB,run_d,other,tcdb:3.A.1,strong", "dB,run_d,other,tcdb:2.A.6,strong")))
        self.assertIn(["dB"], p)

    def test_two_complete_cassettes_do_not_merge(self):
        text = """
locus_tag,run_id,role,tcdb_ids,likely_transporter,strand,next_locus_tag,gap_to_next
s1,run_x,substrate_binding,tcdb:3.A.1.1,strong,+,p1,10
p1,run_x,permease,tcdb:3.A.1.1,strong,+,a1,10
a1,run_x,atpase,tcdb:3.A.1.1,strong,+,s2,10
s2,run_x,substrate_binding,tcdb:3.A.1.7,strong,+,p2,10
p2,run_x,permease,tcdb:3.A.1.7,strong,+,a2,10
a2,run_x,atpase,tcdb:3.A.1.7,strong,+,zz,10
"""
        p = partition(self.g(text))
        self.assertIn(["a1", "p1", "s1"], p)
        self.assertIn(["a2", "p2", "s2"], p)

    def test_non_abc_neighbour_never_joins(self):
        # glcH-like single carrier next to an ABC permease: neither side may be non-ABC
        text = """
locus_tag,run_id,role,tcdb_ids,likely_transporter,strand,next_locus_tag,gap_to_next
gH,run_g,single_carrier,tcdb:2.A.2,strong,+,yP,9
yP,run_g,permease,tcdb:3.A.1.27,strong,+,zz,4
"""
        self.assertEqual(partition(self.g(text)), [["gH"], ["yP"]])

    def test_attach_runs_carries_adjacency(self):
        runs = csv("""
locus_tag,run_id,opposite_strand_in_run,gap_to_next,next_locus_tag,strand
g1,run_g1,False,10,g2,+
g2,run_g1,False,,,+
""").set_index("locus_tag")
        out = nt.attach_runs(csv("locus_tag,role\ng1,permease\ng2,atpase\n"), runs).set_index("locus_tag")
        self.assertEqual(out.loc["g1", "next_locus_tag"], "g2")
        self.assertEqual(out.loc["g1", "strand"], "+")


class TestKnownFalsePositiveV15(unittest.TestCase):
    def test_gst_and_sodx(self):
        self.assertTrue(nt.known_false_positive(["glutathione S-transferase"])[0])
        self.assertTrue(nt.known_false_positive(["glutathione S-transferase, rho class"])[0])
        fp, why = nt.known_false_positive(["nickel-type superoxide dismutase maturation protease"])
        self.assertTrue(fp)
        self.assertIn("sodX", why)
        self.assertTrue(nt.known_false_positive(["ferritin"])[0])

    def test_not_flagged(self):
        for p in ("glutathione reductase", "lactoylglutathione lyase",
                  "membrane-associated proteins in eicosanoid and glutathione metabolism",
                  "glutathione-regulated potassium-efflux system protein"):
            self.assertFalse(nt.known_false_positive([p])[0], p)


class TestAdjacentAbcOrder(unittest.TestCase):
    def test_abc_pairs_before_other(self):
        # MIT9313 PMT1573 ('other', strong) - PMT1574 (permease) - PMT1575 (permease): the result must not
        # depend on pair order; ABC+ABC joins are made first, then the strong 'other' piece joins.
        text = """
locus_tag,run_id,role,tcdb_ids,likely_transporter,strand,next_locus_tag,gap_to_next
m3,run_m,other,tcdb:2.A.6 | tcdb:3.A.1,strong,+,m4,110
m4,run_m,permease,tcdb:3.A.1,strong,+,m5,10
m5,run_m,permease,tcdb:3.A.1,strong,+,zz,895
"""
        self.assertEqual(partition(nt.group_systems(csv(text), cross_locus=False)), [["m3", "m4", "m5"]])



# --------------------------------------------------------------------------- v1.6 (2026-10-08)
class TestCuratedLiftsSuperfamily(unittest.TestCase):
    def t(self, **kw):
        base = dict(strong=True, tcdb_only=False, role_complete=False, member_resolutions=["family_inferred"],
                    c123_max_score=0.8, curated_q=True)
        base.update(kw)
        return nt.system_tier(**base)

    def test_lift_to_medium_with_reason(self):
        tier, why = self.t()
        self.assertEqual(tier, "Medium")
        self.assertIn("superfamily-only overridden by curated Cyanorak transport role", why)

    def test_complete_but_unresolved_is_medium_not_high(self):
        self.assertEqual(self.t(role_complete=True)[0], "Medium")

    def test_without_curated_still_low(self):
        tier, why = self.t(curated_q=False)
        self.assertEqual(tier, "Low")
        self.assertTrue(why.startswith("superfamily-only"))

    def test_does_not_lift_catalogue_only(self):
        tier, why = self.t(strong=False, tcdb_only=True)
        self.assertEqual(tier, "Low")
        self.assertTrue(why.startswith("catalogue-only"), why)

    def test_score0_and_superfamily_both_overridden(self):
        tier, why = self.t(c123_max_score=0.0)
        self.assertEqual(tier, "Medium")
        self.assertIn("superfamily-only overridden", why)
        self.assertIn("score-0-only overridden", why)


class TestListingBasis(unittest.TestCase):
    KM = None

    def setUp(self):
        self.km = nt.CLASS_KEYWORDS

    def lb(self, cls, names, products, q=()):
        return nt.listing_basis(cls, names, products, q)

    def test_keyword_product_or_gene(self):
        self.assertEqual(self.lb("ammonium", ["amt1"], ["ammonium transporter"])[0], "dedicated")
        self.assertEqual(self.lb("urea", ["urtA"], ["urea ABC transporter, substrate binding protein"])[0], "dedicated")
        self.assertEqual(self.lb("peptides", ["dppA"], ["oligopeptide ABC transporter"])[0], "dedicated")
        self.assertEqual(self.lb("nitrite", ["focA"], ["nitrite transporter, FNT family"])[0], "dedicated")
        self.assertEqual(self.lb("osmolytes", ["proV"], ["ABC transporter ATP-binding protein"])[0], "dedicated")
        self.assertEqual(self.lb("amino acids", ["natB"], ["ABC transporter"])[0], "dedicated")

    def test_broad(self):
        self.assertEqual(self.lb("ammonium", ["ktrA"], ["Trk system potassium uptake protein"], ["Q.4"])[0], "broad listing")
        self.assertEqual(self.lb("ammonium", ["nhaS"], ["Na+/H+ antiporter"])[0], "broad listing")
        self.assertEqual(self.lb("amino acids", ["sul1"], ["sulfate permease"])[0], "broad listing")
        self.assertEqual(self.lb("urea", ["putP"], ["sodium/proline symporter"])[0], "broad listing")
        self.assertEqual(self.lb("urea", [None], ["sodium:solute symporter"])[0], "broad listing")

    def test_q_role_mapping(self):
        b, why = self.lb("peptides", ["xyz"], ["ABC transporter"], ["Q.1"])
        self.assertEqual(b, "dedicated")
        self.assertIn("Q.1", why)
        self.assertEqual(self.lb("polyamines", [None], ["ABC transporter"], ["cyanorak.role:Q.1"])[0], "dedicated")
        self.assertEqual(self.lb("nucleobases/nucleosides", [None], ["permease"], ["Q.5"])[0], "dedicated")
        self.assertEqual(self.lb("ammonium", [None], ["cation transporter"], ["Q.4"])[0], "broad listing")
        self.assertEqual(self.lb("osmolytes", [None], ["permease"], ["Q.1"])[0], "broad listing")

    def test_gene_keywords_anchor_on_gene_name(self):
        # 'amt' inside another gene name / product word must not count
        self.assertEqual(self.lb("ammonium", ["gamtX"], ["hypothetical"])[0], "broad listing")
        self.assertEqual(self.lb("amino acids", ["glnA"], ["glutamine synthetase"])[0], "dedicated")  # product word

    def test_keyword_table(self):
        df = nt.class_keyword_table()
        self.assertEqual(set(df.columns), {"compound_class", "product_regex", "product_exclude_regex", "gene_name_regex",
                                           "cyanorak_q_roles"})
        self.assertIn("ammonium", set(df.compound_class))
        q = dict(zip(df.compound_class, df.cyanorak_q_roles))
        self.assertEqual(q["ammonium"], "")
        self.assertEqual(q["peptides"], "Q.1")
        self.assertEqual(q["nucleobases/nucleosides"], "Q.5")

    def test_breadth(self):
        rows = pd.DataFrame({"system_id": ["s", "s", "s", "s", "s"],
                             "equiv_group": ["g1", "g1", "g2", "g3", "g4"],
                             "substrate_depth": ["most_specific"] * 4 + ["inherited"],
                             "is_lumping": [False, False, False, True, False],
                             "is_currency": [False, False, True, False, False],
                             "n_status": ["contains_N", "contains_N", "no_N", "no_N", "no_N"]})
        self.assertEqual(nt.substrate_breadth(rows), {"s": (1, 1)})



# --------------------------------------------------------------------------- v1.6.1 (delta-critic fixes, 2026-10-08)
class TestEffluxAnnotated(unittest.TestCase):
    def test_products(self):
        for prod in ("multidrug efflux transporter, MFS family", "ABC exporter ATP-binding subunit, DevA type",
                     "RND family multidrug efflux transporter, MMPL family", "MATE family efflux protein",
                     "drug resistance transporter", "ABC-type multidrug transport system, ATPase component",
                     "polysaccharide export protein"):
            self.assertTrue(nt.efflux_annotated([prod], [None]), prod)

    def test_gene_names(self):
        for g in ("devB", "evrC", "tolC", "acrA", "mdtA", "ccmA", "ycf38"):
            self.assertTrue(nt.efflux_annotated(["ABC-2 type transporter family protein"], [g]), g)

    def test_not_efflux(self):
        for prod in ("glutamate transporter", "ammonium transporter", "permease of the drug/metabolite transporter (DMT) superfamily",
                     "eamA-like transporter family protein", "ABC transporter, ATP-binding protein"):
            self.assertFalse(nt.efflux_annotated([prod], ["xyzA"]), prod)
        self.assertFalse(nt.efflux_annotated(["transporter"], ["devZ"]))   # not in the gene list


class TestDedicatedRuleV161(unittest.TestCase):
    def test_q_only_efflux_is_broad(self):
        b, why = nt.listing_basis("peptides", ["PMT0977"], ["ABC-type multidrug transport system"], ["Q.1"], efflux=True)
        self.assertEqual(b, "broad listing")
        self.assertEqual(why, "Q.1 only, efflux-annotated")
        # keyword hit wins even when efflux-annotated
        b, _ = nt.listing_basis("peptides", ["dppA"], ["oligopeptide ABC exporter"], ["Q.1"], efflux=True)
        self.assertEqual(b, "dedicated")
        # Q-only without efflux stays dedicated
        self.assertEqual(nt.listing_basis("peptides", ["x"], ["ABC transporter"], ["Q.1"], efflux=False)[0], "dedicated")

    def test_dedicated_basis(self):
        self.assertEqual(nt.dedicated_basis("gene name amt1; product 'ammonium transporter'"), "keyword")
        self.assertEqual(nt.dedicated_basis("product 'x'; Cyanorak Q.1"), "keyword")
        self.assertEqual(nt.dedicated_basis("Cyanorak Q.1"), "Q-role only")
        self.assertEqual(nt.dedicated_basis("none"), "none")
        self.assertEqual(nt.dedicated_basis("Q.1 only, efflux-annotated"), "none")

    def lb(self, cls, name, prod):
        return nt.listing_basis(cls, [name], [prod], [])[0]

    def test_tightened_keywords_do_not_match(self):
        self.assertEqual(self.lb("cyanate", None, "cyanophycin synthetase"), "broad listing")
        self.assertEqual(self.lb("cyanate", None, "cyanocobalamin ABC transporter"), "broad listing")
        self.assertEqual(self.lb("nitrate", None, "ABC-type nitrate/sulfonate/bicarbonate transport system"), "broad listing")
        self.assertEqual(self.lb("amino acids", None, "two-component sensor histidine kinase"), "broad listing")
        self.assertEqual(self.lb("osmolytes", None, "OsmC-like protein"), "broad listing")
        self.assertEqual(self.lb("amino acids", None, "glutamine amidotransferase class-I"), "broad listing")
        self.assertEqual(self.lb("amino acids", None, "glutamine--fructose-6-phosphate aminotransferase (isomerizing) amidotransferase"),
                         "broad listing")
        for g in ("gltX", "gltA", "gltB"):
            self.assertEqual(self.lb("amino acids", g, "enzyme"), "broad listing", g)

    def test_tightened_keywords_still_match(self):
        self.assertEqual(self.lb("cyanate", None, "cyanate ABC transporter, permease protein"), "dedicated")
        self.assertEqual(self.lb("nitrate", None, "nitrate transporter"), "dedicated")
        self.assertEqual(self.lb("amino acids", None, "histidine ABC transporter"), "dedicated")
        self.assertEqual(self.lb("osmolytes", None, "osmoprotectant ABC transporter"), "dedicated")
        self.assertEqual(self.lb("amino acids", None, "glutamine ABC transporter"), "dedicated")
        for g in ("gltS", "gltP", "gltI", "gltJ", "gltK", "gltL"):
            self.assertEqual(self.lb("amino acids", g, "transporter"), "dedicated", g)


class TestMapegFalsePositive(unittest.TestCase):
    def test_mapeg(self):
        fp, why = nt.known_false_positive(["membrane-associated, eicosanoid/glutathione metabolism (MAPEG) protein"])
        self.assertTrue(fp)
        self.assertIn("MAPEG", why)
        self.assertTrue(nt.known_false_positive(["MAPEG family protein"])[0])
