"""
Hand-computed toy tests for the module-scoring machinery (scoring.py).

TDD: these are written FIRST and encode expected values computed BY HAND on a
tiny synthetic universe -- NO real DE data is touched anywhere in this file.

Toy universe (12 genes), log2fc chosen to include a TIE (g06==g07==0.5):
  g01=-3, g02=-2, g03=-1, g04=-0.5, g05=0, g06=0.5, g07=0.5,
  g08=1, g09=1.5, g10=2, g11=2.5, g12=3        (N=12)
Ascending ranks 1..12; g06,g07 tie at ranks 6,7 -> average rank 6.5.
up-percentile = average_rank / N:
  g01=1/12  g02=2/12  g03=3/12  g04=4/12  g05=5/12  g06=6.5/12 g07=6.5/12
  g08=8/12  g09=9/12  g10=10/12 g11=11/12 g12=12/12=1.0
"""
import pytest
from scoring import (
    up_percentiles, score_system, System, build_modules, module_effect,
    matched_max_null, bh_fdr, breakdown_flag, select_degradation_maps,
    assign_reference_class,
)

LOG2FC = {
    "g01": -3.0, "g02": -2.0, "g03": -1.0, "g04": -0.5, "g05": 0.0, "g06": 0.5,
    "g07": 0.5, "g08": 1.0, "g09": 1.5, "g10": 2.0, "g11": 2.5, "g12": 3.0,
}


@pytest.fixture
def pct():
    return up_percentiles(LOG2FC)


# ---------- 1. rank -> up-percentile (average-rank ties) ----------
def test_percentile_average_rank_tie(pct):
    assert pct["g06"] == pytest.approx(6.5 / 12)
    assert pct["g07"] == pytest.approx(6.5 / 12)
    assert pct["g06"] == pct["g07"]  # tie shares one percentile


def test_percentile_extremes(pct):
    assert pct["g12"] == pytest.approx(12 / 12)     # most up -> 1.0
    assert pct["g01"] == pytest.approx(1 / 12)      # most down -> 1/N
    assert pct["g10"] == pytest.approx(10 / 12)


# ---------- 2. subunit -> system (median) ----------
def test_single_gene_system(pct):
    s = score_system(["g10"], pct)
    assert s["percentile"] == pytest.approx(10 / 12)
    assert s["n_present"] == 1
    assert s["subunit_count"] == 1


def test_multi_subunit_system_median(pct):
    # medians of [8/12, 10/12, 12/12] -> 10/12
    s = score_system(["g08", "g10", "g12"], pct)
    assert s["percentile"] == pytest.approx(10 / 12)
    assert s["n_present"] == 3
    assert s["subunit_count"] == 3


def test_partial_coverage_median_over_present(pct):
    # 'gX' absent from universe -> median over [8/12, 10/12] = 9/12; count=2 of 3
    s = score_system(["g08", "g10", "gX"], pct)
    assert s["percentile"] == pytest.approx(9 / 12)
    assert s["n_present"] == 2
    assert s["subunit_count"] == 3


def test_system_needs_one_present_subunit(pct):
    assert score_system(["gX", "gY"], pct) is None


# ---------- 3. system -> module (decision-12) ----------
def test_module_build_decision12():
    systems = [
        System("S1", "polar amino acid", ["g10"]),
        System("S2", "polar amino acid", ["g09"]),
        System("S3", "maltose", ["g08"]),
        System("S4", "unresolved", ["g05"]),
        System("S5", "unresolved", ["g06"]),
    ]
    mods = build_modules(systems)
    by_sub = {m.substrate: m for m in mods}
    # resolved class merges into ONE broad module carrying both systems
    assert set(by_sub["polar amino acid"].system_ids) == {"S1", "S2"}
    assert by_sub["polar amino acid"].broad is True
    # a single-system specific module is not broad
    assert by_sub["maltose"].system_ids == ["S3"]
    assert by_sub["maltose"].broad is False
    # unresolved systems are EACH their own module -> never merged
    unresolved_mods = [m for m in mods if m.substrate == "unresolved"]
    assert len(unresolved_mods) == 2
    assert all(len(m.system_ids) == 1 for m in unresolved_mods)
    # total modules: 1 (polar AA) + 1 (maltose) + 2 (unresolved) = 4
    assert len(mods) == 4


def test_module_effect_max_over_systems(pct):
    # module with 2 systems: Sa=[g06,g07] median 6.5/12; Sb=[g09] 9/12 -> max 9/12
    sa = score_system(["g06", "g07"], pct)["percentile"]
    sb = score_system(["g09"], pct)["percentile"]
    assert module_effect([sa, sb]) == pytest.approx(9 / 12)


# ---------- 4. matched-max permutation null ----------
def test_null_single_gene_analytic(pct):
    # k=1 system, observed = 10/12. P(random gene pct >= 10/12) = 3/12 = 0.25
    universe = list(pct.values())
    p = matched_max_null([1], universe, observed_max=10 / 12, n_perms=20000, seed=0)
    assert p == pytest.approx(0.25, abs=0.02)


def test_null_single_gene_top_analytic(pct):
    # observed = 1.0 (g12). P(random gene >= 1.0) = 1/12 ~= 0.0833
    universe = list(pct.values())
    p = matched_max_null([1], universe, observed_max=1.0, n_perms=20000, seed=0)
    assert p == pytest.approx(1 / 12, abs=0.02)


def test_null_subunit_count_matters(pct):
    # A k=3 system's max achievable median is median of top-3 = 11/12 < 1.0,
    # so observed=1.0 is UNREACHABLE -> p hits the floor 1/(n+1).
    # A k=1 system CAN reach 1.0 (draw g12) -> p ~= 1/12, NOT the floor.
    universe = list(pct.values())
    n = 2000
    p_k3 = matched_max_null([3], universe, observed_max=1.0, n_perms=n, seed=0)
    p_k1 = matched_max_null([1], universe, observed_max=1.0, n_perms=n, seed=0)
    assert p_k3 == pytest.approx(1 / (n + 1))          # floor
    assert p_k1 > p_k3                                  # k=1 reaches it
    assert p_k1 == pytest.approx(1 / 12, abs=0.03)


def test_null_floor_when_unreachable(pct):
    # observed above every possible draw -> count 0 -> p = 1/(n_perms+1)
    universe = list(pct.values())
    p = matched_max_null([1], universe, observed_max=1.5, n_perms=1000, seed=0)
    assert p == pytest.approx(1 / 1001)


def test_null_two_system_module_smoke(pct):
    universe = list(pct.values())
    p = matched_max_null([1, 2], universe, observed_max=9 / 12, n_perms=5000, seed=0)
    assert 0.0 < p <= 1.0


# ---------- 5. BH / FDR ----------
def test_bh_fdr_hand_worked():
    # classic BH: p = [.001,.008,.039,.041,.9], N=5
    # raw p*N/i: .005, .020, .065, .05125, .9  -> monotone(right->left):
    # q = [.005, .020, .05125, .05125, .9]
    q = bh_fdr([0.001, 0.008, 0.039, 0.041, 0.9])
    assert q[0] == pytest.approx(0.005)
    assert q[1] == pytest.approx(0.020)
    assert q[2] == pytest.approx(0.05125)
    assert q[3] == pytest.approx(0.05125)
    assert q[4] == pytest.approx(0.9)
    called_up = [i for i, qq in enumerate(q) if qq < 0.10]
    assert called_up == [0, 1, 2, 3]


def test_bh_fdr_ties_at_floor():
    # three identical floor p-values -> equal q (= 0.0001)
    q = bh_fdr([0.0001, 0.0001, 0.0001])
    assert q[0] == pytest.approx(0.0001)
    assert q[1] == pytest.approx(0.0001)
    assert q[2] == pytest.approx(0.0001)


# ---------- 6. breakdown flag (ORA read-off; map selection stubbed) ----------
def test_breakdown_flag_up():
    assert breakdown_flag({"qvalue": 0.03, "direction": "up"}) == "up"


def test_breakdown_flag_not_up_high_q():
    assert breakdown_flag({"qvalue": 0.20, "direction": "up"}) == "not-up"


def test_breakdown_flag_not_up_wrong_direction():
    assert breakdown_flag({"qvalue": 0.01, "direction": "down"}) == "not-up"


def test_select_degradation_maps_is_stubbed():
    with pytest.raises(NotImplementedError):
        select_degradation_maps("glutamate")


# ---------- reference-class assignment ----------
@pytest.mark.parametrize("row,expected", [
    (dict(locus_tag="ACZ81_05460", class_="transport-role", in_candidate="True",
          organic_c_vs_inorganic="dual-C+N", importer_vs_exporter="importer",
          gene_summary="ABC transporter substrate-binding protein"), "candidate"),
    (dict(locus_tag="ACZ81_18465", class_="transport-role", in_candidate="True",
          organic_c_vs_inorganic="dual-C+N", importer_vs_exporter="importer",
          gene_summary="ABC-type antimicrobial peptide transporter"), "set-aside"),
    (dict(locus_tag="EZ55_03813", class_="transport-role", in_candidate="True",
          organic_c_vs_inorganic="dual-C+N", importer_vs_exporter="importer",
          gene_summary="ABC-type antimicrobial peptide transporter"), "set-aside"),
    (dict(locus_tag="ACZ81_00580", class_="transport-role", in_candidate="False",
          organic_c_vs_inorganic="inorganic", importer_vs_exporter="importer",
          gene_summary="iron(III) ABC transporter substrate-binding protein"), "control-ABC"),
    (dict(locus_tag="ACZ81_06575", class_="other", in_candidate="False",
          organic_c_vs_inorganic="inorganic", importer_vs_exporter="importer",
          gene_summary="TonB-dependent receptor catecholate siderophore iron complex"), "control-TonB"),
    (dict(locus_tag="ACZ81_btuB", class_="other", in_candidate="False",
          organic_c_vs_inorganic="inorganic", importer_vs_exporter="importer",
          gene_summary="TonB-dependent receptor btuB vitamin B12 cobalamin"), "interaction-coupled"),
    (dict(locus_tag="ACZ81_bareTonB", class_="other", in_candidate="False",
          organic_c_vs_inorganic="ambiguous", importer_vs_exporter="importer",
          gene_summary="TonB-dependent receptor"), "ambiguous-TonB"),
    (dict(locus_tag="ACZ81_uns", class_="secondary-carrier-unresolved", in_candidate="False",
          organic_c_vs_inorganic="ambiguous", importer_vs_exporter="importer",
          gene_summary="MFS transporter"), "set-aside"),
])
def test_reference_class_assignment(row, expected):
    assert assign_reference_class(row) == expected
