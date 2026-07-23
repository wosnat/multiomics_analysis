"""
Module-scoring machinery for the carbon-source analysis (methods milestone).

Implements the score chain per (experiment x timepoint). Pure functions on plain
inputs so they are unit-testable on a tiny synthetic universe (see test_scoring.py).
This module builds and toy-tests the machinery ONLY -- it is NOT run on real DE
data here (that is a later milestone).

Resolved spec ambiguities (flagged for the main thread):
  - up-percentile = average_rank / N (1-based ranks; ties get the average rank).
    Range is (0, 1]; most-down = 1/N (not exactly 0), most-up = 1.0. Chosen to
    match the spec's explicit "= rank/N".
  - module `broad` flag = (module holds >1 system) -- i.e. a resolved-class label
    that merged several systems. A single-system resolved module is not broad.
  - permutation p estimator = (count + 1) / (n_perms + 1); floor = 1/(n_perms+1).
  - null draws k DISTINCT genes per system (sample without replacement) from the
    full universe (module's own genes included, standard).
  - reference-class btuB/heme carve-out is keyword-based on gene_summary.
"""
from __future__ import annotations

import random
import re
import statistics
from dataclasses import dataclass, field


# ---------- 1. rank -> up-percentile (average-rank ties) ----------
def up_percentiles(log2fc: dict[str, float]) -> dict[str, float]:
    """Rank genes by log2fc; up-percentile = average_rank / N (ties -> average)."""
    items = sorted(log2fc.items(), key=lambda kv: kv[1])
    n = len(items)
    out: dict[str, float] = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and items[j + 1][1] == items[i][1]:
            j += 1
        # 1-based ranks i+1 .. j+1 -> average rank
        avg_rank = sum(range(i + 1, j + 2)) / (j - i + 1)
        for k in range(i, j + 1):
            out[items[k][0]] = avg_rank / n
        i = j + 1
    return out


# ---------- 2. subunit -> system (median over present) ----------
def score_system(subunit_tags: list[str], pct_by_gene: dict[str, float]):
    """System percentile = median of present subunit percentiles. None if no
    subunit is present. present-count and total subunit_count travel with the call."""
    present = [pct_by_gene[t] for t in subunit_tags if t in pct_by_gene]
    if not present:
        return None
    return {
        "percentile": statistics.median(present),
        "n_present": len(present),
        "subunit_count": len(subunit_tags),
    }


# ---------- 3. system -> module (decision-12) ----------
@dataclass
class System:
    system_id: str
    substrate: str
    subunit_tags: list[str]


@dataclass
class Module:
    module_id: str
    substrate: str
    system_ids: list[str] = field(default_factory=list)
    broad: bool = False


def _is_unresolved(substrate) -> bool:
    return (substrate is None) or (str(substrate).strip().lower() in ("", "unresolved"))


def build_modules(systems: list[System]) -> list[Module]:
    """Group systems into modules. Resolved substrate labels sharing the same
    string merge into one module (broad if >1 system). Unresolved systems each
    become their OWN module -- never merged."""
    modules: dict[str, Module] = {}
    order: list[str] = []
    for s in systems:
        if _is_unresolved(s.substrate):
            mid = f"unresolved::{s.system_id}"
            modules[mid] = Module(mid, "unresolved", [s.system_id], broad=False)
            order.append(mid)
        else:
            mid = f"resolved::{s.substrate}"
            if mid not in modules:
                modules[mid] = Module(mid, s.substrate, [], broad=False)
                order.append(mid)
            modules[mid].system_ids.append(s.system_id)
    for m in modules.values():
        if m.substrate != "unresolved" and len(m.system_ids) > 1:
            m.broad = True
    return [modules[mid] for mid in order]


def module_effect(system_percentiles: list[float]) -> float:
    """Module effect = max system percentile (best uptake route)."""
    return max(system_percentiles)


# ---------- 4. matched-max permutation null ----------
def _draw_system_percentile(size: int, universe: list[float], rng: random.Random) -> float:
    genes = rng.sample(universe, size) if size <= len(universe) else \
        [rng.choice(universe) for _ in range(size)]
    return statistics.median(genes)


def matched_max_null(system_subunit_counts: list[int], universe_percentiles: list[float],
                     observed_max: float, n_perms: int = 10000, seed: int = 0) -> float:
    """Draw random system-sets matched on system count AND each system's subunit
    count; take each draw's max system-percentile -> null. p = P(null max >= observed).
    Estimator (count+1)/(n_perms+1) so p has a floor of 1/(n_perms+1)."""
    rng = random.Random(seed)
    universe = list(universe_percentiles)
    count = 0
    for _ in range(n_perms):
        draw_max = float("-inf")
        for k in system_subunit_counts:
            m = _draw_system_percentile(k, universe, rng)
            if m > draw_max:
                draw_max = m
        if draw_max >= observed_max:
            count += 1
    return (count + 1) / (n_perms + 1)


# ---------- 5. BH / FDR ----------
def bh_fdr(pvals: list[float]) -> list[float]:
    """Benjamini-Hochberg q-values with step-up monotonicity. Equal p-values
    (incl. ties at the permutation floor) receive equal q."""
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    q = [0.0] * n
    prev = 1.0
    for rank in range(n, 0, -1):
        i = order[rank - 1]
        val = pvals[i] * n / rank
        prev = min(prev, val)
        q[i] = prev
    return q


# ---------- 6. breakdown flag (ORA read-off; map selection deferred/STUB) ----------
def select_degradation_maps(substrate: str):
    """STUB -- degradation-map selection is deferred to a later milestone."""
    raise NotImplementedError("degradation-map selection is deferred (stub)")


def breakdown_flag(ora_result: dict, q_threshold: float = 0.10) -> str:
    """Read-off of a map's ORA result -> 'up' | 'not-up'. Corroboration-only,
    outside the FDR family. 'up' iff over-represented among up-genes (direction
    'up') at q < q_threshold."""
    q = ora_result.get("qvalue")
    direction = ora_result.get("direction")
    if q is not None and q < q_threshold and direction == "up":
        return "up"
    return "not-up"


# ---------- reference-class assignment (data-prep helper) ----------
SET_ASIDE_LOCI = {"ACZ81_18465", "EZ55_03813"}  # antimicrobial-peptide ABC (pass-4 set-aside)
_TONB = re.compile(r"tonb", re.I)
_B12_HEME = re.compile(r"\bb12\b|cobalamin|btub|\bheme\b|\bhaem\b", re.I)
_IRON = re.compile(r"iron|ferric|ferrous|siderophore|catecholate|hydroxamate|"
                   r"ferrichrome|enterobactin|\bfe\b|dicitrate", re.I)


def assign_reference_class(row: dict) -> str:
    """Assign a system's reference_class for the null comparison groups."""
    lt = row.get("locus_tag", "")
    cls = row.get("class_", "")
    summ = str(row.get("gene_summary") or "")
    oc = row.get("organic_c_vs_inorganic")
    imp = row.get("importer_vs_exporter")
    # in_candidate may arrive as a real bool (fixture) or the CSV string "True"/"False";
    # bool("False") is truthy, so parse the string form explicitly.
    inc = str(row.get("in_candidate")).strip().lower() == "true"

    if lt in SET_ASIDE_LOCI:
        return "set-aside"
    if cls == "secondary-carrier-unresolved":
        return "set-aside"
    if inc:
        return "candidate"
    if _TONB.search(summ):
        if _B12_HEME.search(summ):
            return "interaction-coupled"
        if _IRON.search(summ):
            return "control-TonB"
        return "ambiguous-TonB"
    if oc == "inorganic" and cls in ("transport-role", "carrier-family") and imp == "importer":
        return "control-ABC"
    return "other"
