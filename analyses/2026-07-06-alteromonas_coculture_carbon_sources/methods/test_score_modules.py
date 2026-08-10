"""Toy / hand-computed tests for score_modules.py (TDD, written first).

All expected values are computed BY HAND below and asserted against the code.
Deterministic pieces (up-percentile, system median, module max, BH) are checked
exactly; the seeded permutation p is checked against a hand-derived ANALYTIC
probability (within Monte-Carlo tolerance) plus a reproducibility assertion.

Run:  uv run analyses/.../methods/test_score_modules.py
(also works under pytest: functions are named test_*.)

------------------------------------------------------------------------------
TOY UNIVERSE (inline, not from the KG): 10 genes, log2fc = -5,-4,-3,-2,-1,1,2,3,4,5
Ranked ascending, up_percentile = (rank-1)/9:
  g1=-5 -> 0/9 = 0.000000     g6=+1 -> 5/9 = 0.555556
  g2=-4 -> 1/9 = 0.111111     g7=+2 -> 6/9 = 0.666667
  g3=-3 -> 2/9 = 0.222222     g8=+3 -> 7/9 = 0.777778
  g4=-2 -> 3/9 = 0.333333     g9=+4 -> 8/9 = 0.888889
  g5=-1 -> 4/9 = 0.444444     g10=+5 -> 9/9 = 1.000000

SYSTEMS & MODULES:
  module "glucose" (organic, 2 systems):
     A = {g9,g10} -> median(0.888889, 1.0)      = 0.944444
     B = {g8}     -> median(0.777778)           = 0.777778
     module effect = max(A,B)                    = 0.944444   (sizes [2,1])
  module "proline" (organic, 1-SYSTEM edge case):
     C = {g6,g7}  -> median(0.555556,0.666667)  = 0.611111
     module effect = 0.611111                    (sizes [2])
  inorganic CONTROL systems:
     E = {g1,g2}  -> median(0.0,0.111111)        = 0.055556
     F = {g3}     -> 0.222222
     G = {g4,g5}  -> median(0.333333,0.444444)   = 0.388889
------------------------------------------------------------------------------
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import score_modules as sm

# ---- toy inputs ----
DE = {"g1": -5, "g2": -4, "g3": -3, "g4": -2, "g5": -1,
      "g6": 1, "g7": 2, "g8": 3, "g9": 4, "g10": 5}
EXP_PCT = {"g1": 0/9, "g2": 1/9, "g3": 2/9, "g4": 3/9, "g5": 4/9,
           "g6": 5/9, "g7": 6/9, "g8": 7/9, "g9": 8/9, "g10": 9/9}
MODULES = [
    {"substrate_call": "glucose", "resolution_level": "specific_compound",
     "confidence_flag": "confident", "systems": [["g9", "g10"], ["g8"]]},
    {"substrate_call": "proline", "resolution_level": "specific_compound",
     "confidence_flag": "inferred", "systems": [["g6", "g7"]]},
]
CONTROLS = [{"locus_tags": ["g1", "g2"]}, {"locus_tags": ["g3"]},
            {"locus_tags": ["g4", "g5"]}]

APPROX = 1e-9
CHECKS = []   # (name, expected, actual, ok)


def _rec(name, expected, actual, ok):
    CHECKS.append((name, expected, actual, ok))
    assert ok, f"{name}: expected {expected}, got {actual}"


# ---------------------------------------------------------------- up-percentile
def test_up_percentile():
    pct = sm.up_percentile(DE)
    for g, exp in EXP_PCT.items():
        _rec(f"up_pct[{g}]", round(exp, 6), round(pct[g], 6),
             math.isclose(pct[g], exp, abs_tol=APPROX))


# ---------------------------------------------------------- system percentile
def test_system_percentile():
    pct = sm.up_percentile(DE)
    cases = {"A={g9,g10}": (["g9", "g10"], 0.944444),
             "B={g8}": (["g8"], 0.777778),
             "C={g6,g7}": (["g6", "g7"], 0.611111),
             "E={g1,g2}": (["g1", "g2"], 0.055556),
             "G={g4,g5}": (["g4", "g5"], 0.388889)}
    for name, (tags, exp) in cases.items():
        got = sm.system_percentile(tags, pct)
        _rec(f"sys_pct {name}", round(exp, 6), round(got, 6),
             math.isclose(got, exp, abs_tol=1e-6))


# ----------------------------------------------------------- module effect (max)
def test_module_effect():
    pct = sm.up_percentile(DE)
    eff_g, per_g = sm.module_effect(MODULES[0]["systems"], pct)
    _rec("glucose effect (max)", 0.944444, round(eff_g, 6),
         math.isclose(eff_g, 0.944444, abs_tol=1e-6))
    eff_p, _ = sm.module_effect(MODULES[1]["systems"], pct)
    _rec("proline effect (max, 1-system)", 0.611111, round(eff_p, 6),
         math.isclose(eff_p, 0.611111, abs_tol=1e-6))


# ------------------------------------------------------ system-absent (scope) edge
def test_missing_subunit_dropped():
    # significant_only style: g10 not in the scored set -> system A uses g9 only
    de_small = {k: v for k, v in DE.items() if k != "g10"}   # 9 genes
    pct = sm.up_percentile(de_small)                          # ranks over 9 genes
    got = sm.system_percentile(["g9", "g10"], pct)            # g10 dropped
    exp = pct["g9"]                                           # median of one value
    _rec("system w/ 1 missing subunit -> median of present", round(exp, 6),
         round(got, 6), math.isclose(got, exp, abs_tol=1e-9))


# ---------------------------------------------------------------- Benjamini-Hochberg
def test_bh_qvalues():
    # HAND: p=[0.02,0.30,0.80], m=3. raw q = p*m/rank: 0.06, 0.45, 0.80;
    # monotone (cummin from top): 0.06, 0.45, 0.80.
    q = sm.bh_qvalues([0.02, 0.30, 0.80])
    for name, exp, got in [("q[0.02]", 0.06, q[0]), ("q[0.30]", 0.45, q[1]),
                           ("q[0.80]", 0.80, q[2])]:
        _rec(f"BH {name}", exp, round(got, 6), math.isclose(got, exp, abs_tol=1e-9))
    # None passes through and is excluded from m
    q2 = sm.bh_qvalues([0.01, None, 0.04])   # m=2: 0.01*2/1=0.02 ; 0.04*2/2=0.04
    _rec("BH with None (m=2) q[0.01]", 0.02, round(q2[0], 6),
         math.isclose(q2[0], 0.02, abs_tol=1e-9) and q2[1] is None)


# ---------------------------------------------------- permutation null (analytic)
def test_permutation_p_extremes():
    pct = sm.up_percentile(DE)
    universe = np.array(list(pct.values()))
    # effect = 0.0 -> every null max >= 0 -> p == 1.0 EXACTLY
    p0 = sm.permutation_p([1], 0.0, universe, 5000, np.random.default_rng(1))
    _rec("perm p, effect=0.0 -> 1.0 exact", 1.0, p0, p0 == 1.0)
    # single-gene system, effect=1.0 -> only g10 (1/10) reaches it -> p ~ 0.10
    p1 = sm.permutation_p([1], 1.0, universe, 60000, np.random.default_rng(2))
    _rec("perm p, single {g10} effect=1.0 ~ 0.10 (analytic 1/10)",
         0.10, round(p1, 4), abs(p1 - 0.10) < 0.015)


def test_permutation_p_matched_size():
    pct = sm.up_percentile(DE)
    universe = np.array(list(pct.values()))
    # module "glucose": sizes [2,1], effect 0.944444.
    # size-1 fake hits effect iff gene=g10 (P=1/10); size-2 fake hits iff pair
    # mean>=0.944444 iff pair={g9,g10} (P=1/45). Independent draws:
    # p_analytic = 1 - (1-1/10)(1-1/45) = 0.12.
    pg = sm.permutation_p([2, 1], 0.944444, universe, 60000, np.random.default_rng(3))
    _rec("perm p, glucose sizes[2,1] eff0.9444 ~ 0.12 (analytic)",
         0.12, round(pg, 4), abs(pg - 0.12) < 0.015)
    # module "proline": sizes [2], effect 0.611111. one size-2 fake system;
    # P(mean of 2 sampled pcts >= 0.611111) = (#pairs with sum>=1.22222)/45 = 16/45.
    pp = sm.permutation_p([2], 0.611111, universe, 60000, np.random.default_rng(4))
    _rec("perm p, proline sizes[2] eff0.6111 ~ 0.3556 (analytic 16/45)",
         round(16/45, 4), round(pp, 4), abs(pp - 16/45) < 0.02)


def test_permutation_reproducible():
    pct = sm.up_percentile(DE)
    universe = np.array(list(pct.values()))
    a = sm.permutation_p([2, 1], 0.944444, universe, 20000, np.random.default_rng(7))
    b = sm.permutation_p([2, 1], 0.944444, universe, 20000, np.random.default_rng(7))
    _rec("perm p reproducible (same seed)", a, b, a == b)


# ---------------------------------------------------- full pipeline + 1-sys edge
def test_score_modules_pipeline():
    res = sm.score_modules(MODULES, CONTROLS, DE, scope="genome_wide",
                           n_perm=60000, seed=11)
    by = {r["substrate_call"]: r for r in res}
    # both modules scored; the 1-system module (proline) DOES get a p and a q
    _rec("pipeline: both modules present", 2, len(res), len(res) == 2)
    _rec("glucose effect", 0.944444, round(by["glucose"]["module_effect"], 6),
         math.isclose(by["glucose"]["module_effect"], 0.944444, abs_tol=1e-6))
    _rec("glucose n_systems", 2, by["glucose"]["n_systems"],
         by["glucose"]["n_systems"] == 2)
    _rec("proline (1-system) effect", 0.611111,
         round(by["proline"]["module_effect"], 6),
         math.isclose(by["proline"]["module_effect"], 0.611111, abs_tol=1e-6))
    _rec("proline (1-system) n_systems", 1, by["proline"]["n_systems"],
         by["proline"]["n_systems"] == 1)
    # 1-system module gets a proper q (fourth-pass fix: not excluded)
    _rec("proline 1-system HAS a q", True, by["proline"]["q_perm"] is not None,
         by["proline"]["q_perm"] is not None)
    _rec("glucose HAS a q", True, by["glucose"]["q_perm"] is not None,
         by["glucose"]["q_perm"] is not None)
    # per-system distribution reported
    ps = {tuple(d["locus_tags"]): d["percentile"] for d in by["glucose"]["per_system"]}
    _rec("glucose per-system A={g9,g10}=0.9444", 0.944444,
         round(ps[("g9", "g10")], 6), math.isclose(ps[("g9", "g10")], 0.944444, abs_tol=1e-6))
    _rec("glucose per-system B={g8}=0.7778", 0.777778,
         round(ps[("g8",)], 6), math.isclose(ps[("g8",)], 0.777778, abs_tol=1e-6))
    # permutation p within analytic tolerance (glucose ~0.12, proline ~0.3556)
    _rec("pipeline glucose p_perm ~0.12", 0.12, round(by["glucose"]["p_perm"], 4),
         abs(by["glucose"]["p_perm"] - 0.12) < 0.02)
    _rec("pipeline proline p_perm ~0.3556", round(16/45, 4),
         round(by["proline"]["p_perm"], 4), abs(by["proline"]["p_perm"] - 16/45) < 0.03)
    # control comparison present and small for the strong module
    _rec("glucose p_vs_control small (effect>all controls)", True,
         by["glucose"]["p_vs_control"] < 0.1, by["glucose"]["p_vs_control"] < 0.1)
    return res


ALL_TESTS = [test_up_percentile, test_system_percentile, test_module_effect,
             test_missing_subunit_dropped, test_bh_qvalues,
             test_permutation_p_extremes, test_permutation_p_matched_size,
             test_permutation_reproducible, test_score_modules_pipeline]


if __name__ == "__main__":
    failed = 0
    for t in ALL_TESTS:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print("\n--- hand-computed expected vs code output ---")
    print(f"{'check':52} {'expected':>12} {'actual':>12}  ok")
    for name, exp, act, ok in CHECKS:
        print(f"{name:52} {str(exp):>12} {str(act):>12}  {'Y' if ok else 'N'}")
    print(f"\n{len(ALL_TESTS)-failed}/{len(ALL_TESTS)} test functions passed.")
    sys.exit(1 if failed else 0)
