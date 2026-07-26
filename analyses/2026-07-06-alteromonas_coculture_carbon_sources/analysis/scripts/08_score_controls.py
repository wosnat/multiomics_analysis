#!/usr/bin/env python3
"""
Analysis milestone -- score the CONTROL reference classes across every column of
the candidate heatmap, on the same scale (for a companion control heatmap).

Control classes (parts_list_v2.csv reference_class):
  control-ABC     inorganic ABC / secondary-carrier importers
  control-TonB    iron/siderophore TonB (interaction-coupled confound)
  ambiguous-TonB  bare TonB (control-for-the-control)

Same module-building + scoring as candidates (import committed scoring.py). Per
experiment x timepoint: up_percentiles over that column's gene universe -> system
median -> module max -> matched-max null (seed 0) -> BH q WITHIN that column's
control-module family (the 3 control classes pooled). NO carbon conclusions.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/08_score_controls.py
"""
import os
import sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
METHODS = os.path.normpath(os.path.join(HERE, "..", "..", "methods", "scripts"))
PARTS = os.path.normpath(os.path.join(HERE, "..", "..", "methods", "data", "parts_list_v2.csv"))
sys.path.insert(0, METHODS)
from scoring import up_percentiles, score_system, System, build_modules, module_effect, matched_max_null, bh_fdr  # noqa: E402

N_PERMS = 10000
SEED = 0
CONTROL_CLASSES = ["control-ABC", "control-TonB", "ambiguous-TonB"]
PRIORITY = ["candidate", "control-ABC", "control-TonB", "interaction-coupled",
            "ambiguous-TonB", "set-aside", "other"]
OUT = os.path.join(DATA, "control_module_scores.csv")

TP_SHORT = {"day 18": "d18", "day 31": "d31", "day 60": "d60", "day 89": "d89",
            "days 60+89": "d60+89", "day 11": "d11"}

# single-timepoint presence columns: (label, de_file, strain, omics, arm)
PRESENCE = [
    ("HOT1A3 d11", "de_hot1a3_day11.csv", "HOT1A3", "rnaseq", "coculture"),
    ("EZ55-400", "de_ez55_400.csv", "EZ55", "rnaseq", "coculture"),
    ("EZ55-800", "de_ez55_800.csv", "EZ55", "rnaseq", "coculture"),
]
# temporal multi-timepoint columns: (label_prefix, de_file, strain, omics, arm)
TEMPORAL = [
    ("co", "de_temporal_rnaseq_coculture.csv", "HOT1A3", "rnaseq", "coculture"),
    ("ax", "de_temporal_rnaseq_axenic.csv", "HOT1A3", "rnaseq", "axenic"),
    ("P co", "de_temporal_proteomics_coculture.csv", "HOT1A3", "proteomics", "coculture"),
    ("P ax", "de_temporal_proteomics_axenic.csv", "HOT1A3", "proteomics", "axenic"),
]


def system_reference_class(rcs):
    for r in PRIORITY:
        if r in rcs:
            return r
    return "other"


def pick_substrate(members):
    def resolved(s):
        return s and str(s).strip().lower() not in ("", "unresolved", "nan")
    conf = [m for m in members if m["substrate_confidence"] == "confident" and resolved(m["substrate_provisional"])]
    if conf:
        return conf[0]["substrate_provisional"], conf[0]["carrier_family"]
    inf = [m for m in members if resolved(m["substrate_provisional"])]
    if inf:
        return inf[0]["substrate_provisional"], inf[0]["carrier_family"]
    return "unresolved", members[0]["carrier_family"]


def build_control_modules(parts, strain):
    p = parts[parts.organism_name.str.contains(strain)]
    systems = {}
    for sid, grp in p.groupby("system_id"):
        rc = system_reference_class(set(grp.reference_class))
        if rc not in CONTROL_CLASSES:
            continue
        substrate, cfam = pick_substrate(grp.to_dict("records"))
        systems[sid] = dict(system_id=sid, reference_class=rc, substrate=substrate,
                            carrier_family=cfam, subunit_tags=grp.locus_tag.tolist())
    by_rc = {}
    for rc in CONTROL_CLASSES:
        rc_sys = [s for s in systems.values() if s["reference_class"] == rc]
        mods = build_modules([System(s["system_id"], s["substrate"], s["subunit_tags"]) for s in rc_sys])
        smap = {s["system_id"]: s for s in rc_sys}
        by_rc[rc] = [(m, [smap[i] for i in m.system_ids]) for m in mods]
    return by_rc


def score_column(by_rc, pct, label, omics, arm, timepoint):
    universe = list(pct.values())
    rows, ps = [], []
    for rc in CONTROL_CLASSES:
        for m, msys in by_rc[rc]:
            scored = [(s, score_system(s["subunit_tags"], pct)) for s in msys]
            scored = [(s, sc) for s, sc in scored if sc is not None]
            if not scored:
                continue
            pcts = [sc["percentile"] for _, sc in scored]
            kcs = [sc["n_present"] for _, sc in scored]
            eff = max(pcts)
            drive = scored[pcts.index(eff)][1]
            tier = "single-gene" if drive["subunit_count"] == 1 else "multi-subunit"
            p = matched_max_null(kcs, universe, observed_max=eff, n_perms=N_PERMS, seed=SEED)
            rows.append(dict(reference_class=rc, substrate=m.substrate,
                             carrier_family=";".join(sorted({s["carrier_family"] for s in msys})),
                             tier=tier, n_systems=len(scored), experiment_label=label,
                             omics=omics, arm=arm, timepoint=timepoint,
                             module_percentile=eff, q=None))
            ps.append(p)
    for r, q in zip(rows, bh_fdr(ps) if ps else []):
        r["q"] = q
    return rows


def main():
    parts = pd.read_csv(PARTS)
    ctrl = {s: build_control_modules(parts, s) for s in ["HOT1A3", "EZ55"]}
    for s in ["HOT1A3", "EZ55"]:
        print(f"{s} control modules: " + ", ".join(
            f"{rc}={len(ctrl[s][rc])}" for rc in CONTROL_CLASSES))

    all_rows = []
    for label, f, strain, omics, arm in PRESENCE:
        de = pd.read_csv(os.path.join(DATA, f))
        pct = up_percentiles(dict(zip(de.locus_tag, de.log2fc)))
        tp = "day 11" if "d11" in label else label
        all_rows += score_column(ctrl[strain], pct, label, omics, arm, tp)
    for prefix, f, strain, omics, arm in TEMPORAL:
        de = pd.read_csv(os.path.join(DATA, f))
        for tp in sorted(de.timepoint.dropna().unique()):
            sub = de[de.timepoint == tp]
            pct = up_percentiles(dict(zip(sub.locus_tag, sub.log2fc)))
            label = f"{prefix} {TP_SHORT.get(tp, tp)}"
            all_rows += score_column(ctrl[strain], pct, label, omics, arm, tp)

    df = pd.DataFrame(all_rows)[["reference_class", "substrate", "carrier_family", "tier",
                                "n_systems", "experiment_label", "omics", "arm", "timepoint",
                                "module_percentile", "q"]]
    df.to_csv(OUT, index=False)
    print(f"\nwrote {len(df)} rows across {df.experiment_label.nunique()} columns -> {OUT}")

    # --- factual medians (no interpretation) ---
    print("\n=== control-ABC median module_percentile per column ===")
    for lab in df.experiment_label.unique():
        sub = df[(df.experiment_label == lab) & (df.reference_class == "control-ABC")]
        if len(sub):
            print(f"  {lab:12s}: n={len(sub):>2} median_pct={sub.module_percentile.median():.3f}")
    print("\n=== all-control median by class @ HOT1A3 d11 and late-axenic (ax d60+89) ===")
    for lab in ["HOT1A3 d11", "ax d60+89"]:
        for rc in CONTROL_CLASSES:
            sub = df[(df.experiment_label == lab) & (df.reference_class == rc)]
            if len(sub):
                print(f"  {lab:12s} {rc:15s}: n={len(sub):>2} median_pct={sub.module_percentile.median():.3f} "
                      f"n_q<0.10={int((sub.q < 0.10).sum())}")


if __name__ == "__main__":
    main()
