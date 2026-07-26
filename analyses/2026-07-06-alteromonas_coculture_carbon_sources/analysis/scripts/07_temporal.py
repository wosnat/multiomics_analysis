#!/usr/bin/env python3
"""
Analysis milestone -- HOT1A3 temporal read (corroboration-only).

Difference-of-starvation-trajectories: each arm (coculture / axenic) vs its OWN
PRO99-lowN exponential baseline, scored per timepoint, then compared. Count-per-
trajectory of candidate modules "up" (q<0.10). NO carbon conclusions.

Experiments (all_detected_genes, fully rankable per timepoint):
  RNA  coculture: ..._nutrient_starvation_hot1a3_rnaseq_coculture     (d18/31/60/89,+60+89)
  RNA  axenic:    ..._nutrient_starvation_hot1a3_rnaseq_axenic        (d18/31,+60+89)
  Prot coculture: ..._nutrient_starvation_hot1a3_proteomics_coculture (d18/31/60/89,+60+89)
  Prot axenic:    ..._nutrient_starvation_hot1a3_proteomics_axenic    (d18[0 sig]/31)

Same refined candidate set as the presence runs (drop TonB; relabel 18130->carbohydrate
(MFS), 06075->di-/tricarboxylate). Imports committed scoring.py.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/07_temporal.py
"""
import os
import sys
import pandas as pd
from multiomics_explorer import differential_expression_by_gene

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
METHODS = os.path.normpath(os.path.join(HERE, "..", "..", "methods", "scripts"))
PARTS = os.path.normpath(os.path.join(HERE, "..", "..", "methods", "data", "parts_list_v2.csv"))
sys.path.insert(0, METHODS)
from scoring import up_percentiles, score_system, System, build_modules, module_effect, matched_max_null, bh_fdr  # noqa: E402

N_PERMS = 10000
SEED = 0
PRIORITY = ["candidate", "control-ABC", "control-TonB", "interaction-coupled",
            "ambiguous-TonB", "set-aside", "other"]
SUBSTRATE_OVERRIDE = {"ACZ81_18130": "carbohydrate (MFS)",
                      "ACZ81_06075": "di-/tricarboxylate (citrate, CitMHS)"}
BASE = "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_hot1a3"
EXPS = {
    ("rnaseq", "coculture"): f"{BASE}_rnaseq_coculture",
    ("rnaseq", "axenic"): f"{BASE}_rnaseq_axenic",
    ("proteomics", "coculture"): f"{BASE}_proteomics_coculture",
    ("proteomics", "axenic"): f"{BASE}_proteomics_axenic",
}


def system_reference_class(rcs):
    for r in PRIORITY:
        if r in rcs:
            return r
    return "other"


def pick_substrate(members):
    def resolved(s):
        return s and str(s).strip().lower() not in ("", "unresolved", "nan")
    for m in members:
        if m["locus_tag"] in SUBSTRATE_OVERRIDE:
            return SUBSTRATE_OVERRIDE[m["locus_tag"]], m["carrier_family"]
    conf = [m for m in members if m["substrate_confidence"] == "confident" and resolved(m["substrate_provisional"])]
    if conf:
        return conf[0]["substrate_provisional"], conf[0]["carrier_family"]
    inf = [m for m in members if resolved(m["substrate_provisional"])]
    if inf:
        return inf[0]["substrate_provisional"], inf[0]["carrier_family"]
    return "unresolved", members[0]["carrier_family"]


def build_candidate_modules():
    parts = pd.read_csv(PARTS)
    parts = parts[parts.organism_name.str.contains("HOT1A3")].copy()
    systems = {}
    for sid, grp in parts.groupby("system_id"):
        members = grp.to_dict("records")
        if system_reference_class(set(grp.reference_class)) != "candidate":
            continue
        substrate, cfam = pick_substrate(members)
        systems[sid] = dict(system_id=sid, substrate=substrate, carrier_family=cfam,
                            subunit_tags=grp.locus_tag.tolist())
    mods = build_modules([System(s["system_id"], s["substrate"], s["subunit_tags"])
                          for s in systems.values()])
    out = []
    for m in mods:
        msys = [systems[i] for i in m.system_ids]
        out.append(dict(module_id=m.module_id, substrate=m.substrate,
                        carrier_family=";".join(sorted({s["carrier_family"] for s in msys})),
                        systems=msys))
    return out


def score_modules_at(modules, pct):
    """Score all candidate modules at one (arm x timepoint); BH q across scored."""
    universe = list(pct.values())
    rows, ps = [], []
    for m in modules:
        scored = [(s, score_system(s["subunit_tags"], pct)) for s in m["systems"]]
        scored = [(s, sc) for s, sc in scored if sc is not None]
        if not scored:
            continue
        pcts = [sc["percentile"] for _, sc in scored]
        kcs = [sc["n_present"] for _, sc in scored]
        eff = max(pcts)
        drive = scored[pcts.index(eff)][1]
        tier = "single-gene" if drive["subunit_count"] == 1 else "multi-subunit"
        p = matched_max_null(kcs, universe, observed_max=eff, n_perms=N_PERMS, seed=SEED)
        rows.append(dict(module_id=m["module_id"], substrate=m["substrate"],
                         carrier_family=m["carrier_family"], tier=tier,
                         pct=eff, p=p, q=None))
        ps.append(p)
    qs = bh_fdr(ps) if ps else []
    for r, q in zip(rows, qs):
        r["q"] = q
        r["up_flag"] = q < 0.10
        r["soft_flag"] = r["pct"] >= 0.9
    return rows


def main():
    modules = build_candidate_modules()
    print(f"candidate modules (fixed set): {len(modules)}")

    score_rows = []
    arm_tp_up = {}   # (omics, arm, tp) -> set of module_id with up_flag
    for (omics, arm), exp in EXPS.items():
        de = differential_expression_by_gene(experiment_ids=[exp], organism="HOT1A3",
                                             verbose=True, limit=None)
        df = pd.DataFrame([{"locus_tag": r["locus_tag"], "log2fc": r["log2fc"],
                            "expression_status": r.get("expression_status"),
                            "timepoint": r.get("timepoint")} for r in de["results"]])
        df.to_csv(os.path.join(DATA, f"de_temporal_{omics}_{arm}.csv"), index=False)
        for tp in sorted(df.timepoint.dropna().unique()):
            sub = df[df.timepoint == tp]
            pct = up_percentiles(dict(zip(sub.locus_tag, sub.log2fc)))
            rows = score_modules_at(modules, pct)
            up = set()
            for r in rows:
                r.update(omics=omics, arm=arm, timepoint=tp)
                score_rows.append(r)
                if r["up_flag"]:
                    up.add(r["module_id"])
            arm_tp_up[(omics, arm, tp)] = up
            print(f"  {omics:10s} {arm:9s} {tp:12s}: {len(rows)} modules scored, {len(up)} up(q<0.10)")

    sdf = pd.DataFrame(score_rows)[["omics", "arm", "timepoint", "module_id", "substrate",
                                    "carrier_family", "tier", "pct", "q", "up_flag", "soft_flag"]]
    sdf.to_csv(os.path.join(DATA, "temporal_module_scores.csv"), index=False)

    # difference-of-trajectories on aligned timepoints (present in BOTH arms)
    counts = []
    sub_of = {m["module_id"]: m["substrate"] for m in modules}
    for omics in ["rnaseq", "proteomics"]:
        coc_tps = {tp for (o, a, tp) in arm_tp_up if o == omics and a == "coculture"}
        ax_tps = {tp for (o, a, tp) in arm_tp_up if o == omics and a == "axenic"}
        for tp in sorted(coc_tps & ax_tps):
            coc = arm_tp_up.get((omics, "coculture", tp), set())
            ax = arm_tp_up.get((omics, "axenic", tp), set())
            spec = coc - ax
            counts.append(dict(omics=omics, timepoint=tp, n_coculture_up=len(coc),
                               n_axenic_up=len(ax), n_coculture_specific=len(spec),
                               coculture_specific_substrates="; ".join(sorted(sub_of[m] for m in spec))))
    cdf = pd.DataFrame(counts)
    cdf.to_csv(os.path.join(DATA, "qc_temporal_counts.csv"), index=False)
    print("\nwrote temporal_module_scores.csv + qc_temporal_counts.csv")
    print("\n=== count-per-trajectory (aligned timepoints) ===")
    for r in counts:
        print(f"  {r['omics']:10s} {r['timepoint']:12s}: coc_up={r['n_coculture_up']} "
              f"ax_up={r['n_axenic_up']} coc_specific={r['n_coculture_specific']} "
              f"| {r['coculture_specific_substrates']}")


if __name__ == "__main__":
    main()
