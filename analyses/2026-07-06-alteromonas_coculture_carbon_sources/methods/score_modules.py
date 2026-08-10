"""Module-scoring code for the Alteromonas carbon-source analysis.

Implements the proposal's Approach-step-2 + Statistics-decision scoring (with the
fourth-pass fixes). BUILD + TOY-TEST ONLY at the methods milestone — this module
is *ready* to accept a real per-gene DE table but is not run on the real HOT1A3
experiment here (that is the analysis milestone). No KG calls live in this module.

Scoring recipe (one (experiment x timepoint) at a time):
  1. Rank all detected genes by KG-provided log2fc -> up-percentile in [0,1]
     (0 = most down, 1 = most up). `scope` records genome-wide (all_detected_genes)
     vs within-significant-set (significant_only); the ranking universe is exactly
     the genes present in `de_table`.
  2. System percentile = MEDIAN of its subunit up-percentiles.
  3. Module effect = MAX system percentile (best uptake route).
  4. Significance = matched-max permutation null: draw many random system sets of
     the SAME size structure (same number of systems, each with the same subunit
     count) from the scored gene universe, take each draw's max system-percentile
     -> null -> p. A second p is computed against the inorganic-control set.
  5. BH/FDR across ALL modules within the unit (incl. 1-system modules) -> q.

The tested unit is the MODULE: one permutation p per module (from its max-system
up-percentile), NOT one p per system. Every module — including 1-system — gets a
proper q, and its system count travels with the call.
"""
from __future__ import annotations

import csv
import os
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# 1. up-percentile
# ----------------------------------------------------------------------------
def up_percentile(de_table: dict) -> dict:
    """Rank all detected genes by log2fc into an up-percentile in [0,1].

    0 = most down, 1 = most up. Ties get the average rank. Requires >= 2 genes.
    `de_table` maps locus_tag -> log2fc (the per-gene DE for one experiment x
    timepoint). Returns locus_tag -> up_percentile.
    """
    if len(de_table) < 2:
        raise ValueError("up_percentile needs >= 2 detected genes.")
    s = pd.Series(de_table, dtype=float)
    ranks = s.rank(method="average")          # 1..n, average ties
    pct = (ranks - 1.0) / (len(s) - 1.0)       # most-down -> 0, most-up -> 1
    return {k: float(v) for k, v in pct.items()}


# ----------------------------------------------------------------------------
# 2/3. system percentile (median) and module effect (max)
# ----------------------------------------------------------------------------
def system_percentile(locus_tags, pct_map) -> float | None:
    """Median of the subunit up-percentiles. Subunits absent from the scored
    universe (e.g. under significant_only scope) are dropped. Returns None if no
    subunit is present."""
    vals = [pct_map[t] for t in locus_tags if t in pct_map]
    if not vals:
        return None
    return float(np.median(vals))


def module_effect(systems, pct_map):
    """systems: list of subunit-locus-tag lists. Returns (effect, per_system)
    where effect = MAX present system-percentile and per_system is a list of
    dicts {locus_tags, n_genes_used, percentile}. effect is None if every system
    is undetected."""
    per_system = []
    present = []
    for sysgenes in systems:
        p = system_percentile(sysgenes, pct_map)
        n_used = sum(1 for t in sysgenes if t in pct_map)
        per_system.append({"locus_tags": list(sysgenes),
                           "n_genes_used": n_used, "percentile": p})
        if p is not None:
            present.append(p)
    effect = max(present) if present else None
    return effect, per_system


# ----------------------------------------------------------------------------
# 4. matched-max permutation null
# ----------------------------------------------------------------------------
def permutation_p(system_sizes, effect, universe_pcts, n_perm, rng):
    """Matched-max permutation p against the scored gene universe.

    `system_sizes` = list of subunit counts (one per system in the module) — the
    effect was the max over these systems, so the null matches BOTH the number of
    systems AND each system's subunit count. Each null draw builds one fake system
    per size by sampling that many genes (without replacement within the fake
    system) from `universe_pcts`, takes the median, then the max across the fake
    systems. p = (1 + #{null_max >= effect}) / (n_perm + 1)  (the permutation
    floor; min p ~ 1/(n_perm+1)).
    """
    universe = np.asarray(universe_pcts, dtype=float)
    n = len(universe)
    if effect is None or not system_sizes:
        return None
    null_max = np.empty(n_perm, dtype=float)
    for b in range(n_perm):
        best = -np.inf
        for k in system_sizes:
            idx = rng.choice(n, size=k, replace=(k > n))
            med = np.median(universe[idx])
            if med > best:
                best = med
        null_max[b] = best
    count = int(np.sum(null_max >= effect - 1e-12))
    return (1 + count) / (n_perm + 1)


def control_p(n_systems, effect, control_system_pcts, n_perm, rng):
    """Secondary p: draw `n_systems` control (inorganic-importer) system
    percentiles (with replacement), take the max -> null -> p. Reported, not part
    of the FDR family."""
    ctrl = np.asarray(control_system_pcts, dtype=float)
    if effect is None or n_systems <= 0 or len(ctrl) == 0:
        return None
    draws = rng.choice(ctrl, size=(n_perm, n_systems), replace=True)
    null_max = draws.max(axis=1)
    count = int(np.sum(null_max >= effect - 1e-12))
    return (1 + count) / (n_perm + 1)


# ----------------------------------------------------------------------------
# 5. Benjamini-Hochberg
# ----------------------------------------------------------------------------
def bh_qvalues(pvals):
    """Benjamini-Hochberg q-values. None entries pass through as None and are
    excluded from the family size m. Returns a list aligned to the input."""
    idx = [i for i, p in enumerate(pvals) if p is not None]
    m = len(idx)
    q = [None] * len(pvals)
    if m == 0:
        return q
    ps = sorted(idx, key=lambda i: pvals[i])            # positions sorted by p asc
    prev = 1.0
    for rank in range(m, 0, -1):                        # largest rank -> smallest
        i = ps[rank - 1]
        val = pvals[i] * m / rank
        prev = min(prev, val)
        q[i] = min(prev, 1.0)
    return q


# ----------------------------------------------------------------------------
# Module / control construction from the frozen transporter table
# ----------------------------------------------------------------------------
# Inorganic substrates that the proposal flags as interaction-coupled (exchanged
# in this system), NOT pure negatives — optionally excluded from the control set.
_INTERACTION_COUPLED = ("nitrate", "nitrite", "phosphate", "ammoni", "phosphonate")


def build_modules_from_csv(path, exclude_interaction_coupled_controls=False):
    """Build organic-carbon-importer MODULES and the inorganic-importer CONTROL
    set from `hot1a3_transporter_table.csv`.

    Modules: organic-C importer systems grouped by shared `substrate_call` (one
    substrate = one module). A system's members are its subunit locus_tags.
    Controls: inorganic-importer systems (each a subunit list).
    """
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    modules = {}
    controls = []
    for r in rows:
        if r["importer_or_exporter"] != "importer":
            continue
        tags = [t for t in r["locus_tags"].split(";") if t]
        if r["organic_or_inorganic"] == "organic":
            m = modules.setdefault(r["substrate_call"], {
                "substrate_call": r["substrate_call"],
                "resolution_level": r["resolution_level"],
                "confidence_flag": r["confidence_flag"],
                "systems": [], "system_ids": []})
            m["systems"].append(tags)
            m["system_ids"].append(r["system_id"])
        elif r["organic_or_inorganic"] == "inorganic":
            sub = (r["substrate_call"] or "").lower()
            if exclude_interaction_coupled_controls and any(
                    k in sub for k in _INTERACTION_COUPLED):
                continue
            controls.append({"system_id": r["system_id"], "locus_tags": tags})
    module_list = sorted(modules.values(), key=lambda m: m["substrate_call"])
    return module_list, controls


# ----------------------------------------------------------------------------
# Top-level: score every module for one (experiment x timepoint)
# ----------------------------------------------------------------------------
def score_modules(modules, controls, de_table, scope="genome_wide",
                  n_perm=10000, seed=0):
    """Score every module for one (experiment x timepoint).

    modules: list of {substrate_call, systems:[[locus_tags],...], ...}.
    controls: list of {locus_tags:[...]} inorganic-importer systems.
    de_table: locus_tag -> log2fc for this unit. scope in
    {'genome_wide','significant_only'} (documentary — the universe is the genes
    present in de_table). Returns a list of per-module result dicts (with q from
    BH across all modules), sorted by substrate_call.
    """
    if scope not in ("genome_wide", "significant_only"):
        raise ValueError("scope must be 'genome_wide' or 'significant_only'.")

    pct_map = up_percentile(de_table)
    universe_pcts = np.array(list(pct_map.values()), dtype=float)

    # control system percentiles (median of subunits), for the control null
    control_pcts = []
    for c in controls:
        p = system_percentile(c["locus_tags"], pct_map)
        if p is not None:
            control_pcts.append(p)

    mods = sorted(modules, key=lambda m: m["substrate_call"])
    results = []
    for i, m in enumerate(mods):
        effect, per_system = module_effect(m["systems"], pct_map)
        sizes = [ps["n_genes_used"] for ps in per_system if ps["percentile"] is not None]
        rng_perm = np.random.default_rng([seed, i])
        rng_ctrl = np.random.default_rng([seed, i, 1])
        p_perm = permutation_p(sizes, effect, universe_pcts, n_perm, rng_perm)
        p_ctrl = control_p(len(sizes), effect, control_pcts, n_perm, rng_ctrl)
        results.append({
            "substrate_call": m["substrate_call"],
            "resolution_level": m.get("resolution_level"),
            "confidence_flag": m.get("confidence_flag"),
            "n_systems": len(m["systems"]),
            "n_systems_detected": len(sizes),
            "module_effect": effect,
            "p_perm": p_perm,
            "p_vs_control": p_ctrl,
            "scope": scope,
            "per_system": per_system,
        })
    # BH across all modules (incl. 1-system) within this unit
    qs = bh_qvalues([r["p_perm"] for r in results])
    for r, q in zip(results, qs):
        r["q_perm"] = q
        r["called_up"] = (q is not None and q < 0.10)
    return results


def de_table_from_records(records, locus_key="locus_tag", log2fc_key="log2fc"):
    """Helper for real use: build a de_table dict from DE rows
    (e.g. differential_expression_by_gene results). KG-free."""
    out = {}
    for rec in records:
        lt = rec.get(locus_key)
        v = rec.get(log2fc_key)
        if lt is not None and v is not None:
            out[lt] = float(v)
    return out
