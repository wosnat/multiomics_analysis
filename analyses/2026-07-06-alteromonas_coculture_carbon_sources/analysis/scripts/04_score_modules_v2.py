#!/usr/bin/env python3
"""
Analysis milestone -- refined scoring of the HOT1A3 day-11 contrast (v2).

Reads the COMMITTED ../methods/data/parts_list_v2.csv (methods parts list is NOT
edited) and applies documented ANALYSIS-LAYER refinements before scoring:

 R1. Drop TonB from scoring: control-TonB and ambiguous-TonB are removed from the
     scored sets. Scored control = control-ABC only. The iron-TonB system-level
     up-shift is recorded separately as a REPORTED OBSERVATION (not a control):
     "iron acquisition induced in coculture; iron/TonB is interaction-coupled."
 R2. Relabel ACZ81_18130 substrate 'unresolved' -> 'carbohydrate (MFS)'
     (gene_category Carbohydrate metabolism; product MFS transporter). Kept candidate.
 R3. Relabel ACZ81_06075 (SLC13) substrate 'SLC13 family' -> 'di-/tricarboxylate
     (citrate, CitMHS)'. KG evidence: Pfam CitMHS (PF03600 Citrate transporter) +
     eggNOG COG0471 (Di- and tricarboxylate transporters); no TCDB; the
     gene_category 'Inorganic ion transport' is a coarse COG-P bin, overridden ->
     organic acid (dicarboxylate), NOT sulfate. Kept candidate.
 R4. Module-grouping guard: decision-12 (distinct resolved substrates = distinct
     modules; unresolved/non-substrate labels each own module). Verified post-hoc.

Imports the committed scorer (../methods/scripts/scoring.py). Re-uses the staged
de_hot1a3_day11.csv. NO carbon-source conclusions.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/04_score_modules_v2.py
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

DE = os.path.join(DATA, "de_hot1a3_day11.csv")
OUT_CATALOG = os.path.join(DATA, "module_catalog_hot1a3_day11_v2.csv")
OUT_SYSTEMS = os.path.join(DATA, "system_scores_hot1a3_day11.csv")
OUT_CONTRAST = os.path.join(DATA, "qc_control_contrast.csv")

N_PERMS = 10000
SEED = 0
SCORED_CLASSES = ["candidate", "control-ABC"]        # R1: TonB dropped
PRIORITY = ["candidate", "control-ABC", "control-TonB", "interaction-coupled",
            "ambiguous-TonB", "set-aside", "other"]
# R2/R3 substrate relabels (analysis-layer, documented)
SUBSTRATE_OVERRIDE = {
    "ACZ81_18130": "carbohydrate (MFS)",
    "ACZ81_06075": "di-/tricarboxylate (citrate, CitMHS)",
}


def system_reference_class(ref_classes):
    for r in PRIORITY:
        if r in ref_classes:
            return r
    return "other"


def pick_substrate(members):
    def resolved(s):
        return s and str(s).strip().lower() not in ("", "unresolved", "nan")
    for m in members:  # R2/R3 override wins
        if m["locus_tag"] in SUBSTRATE_OVERRIDE:
            return SUBSTRATE_OVERRIDE[m["locus_tag"]], m["carrier_family"]
    conf = [m for m in members if m["substrate_confidence"] == "confident" and resolved(m["substrate_provisional"])]
    if conf:
        return conf[0]["substrate_provisional"], conf[0]["carrier_family"]
    inf = [m for m in members if resolved(m["substrate_provisional"])]
    if inf:
        return inf[0]["substrate_provisional"], inf[0]["carrier_family"]
    return "unresolved", members[0]["carrier_family"]


def main():
    de = pd.read_csv(DE)
    pct = up_percentiles(dict(zip(de.locus_tag, de.log2fc)))
    universe = list(pct.values())

    parts = pd.read_csv(PARTS)
    parts = parts[parts.organism_name.str.contains("HOT1A3")].copy()

    systems = {}
    for sid, grp in parts.groupby("system_id"):
        members = grp.to_dict("records")
        rc = system_reference_class(set(grp.reference_class))
        substrate, cfam = pick_substrate(members)
        tags = grp.locus_tag.tolist()
        scored = score_system(tags, pct)
        systems[sid] = dict(system_id=sid, reference_class=rc, substrate=substrate,
                            carrier_family=cfam, subunit_tags=tags, scored=scored)

    # --- R1 reported observation: iron-TonB (control-TonB) system-level up-shift ---
    tonb = [s["scored"]["percentile"] for s in systems.values()
            if s["reference_class"] == "control-TonB" and s["scored"] is not None]
    amb_tonb = [s["scored"]["percentile"] for s in systems.values()
                if s["reference_class"] == "ambiguous-TonB" and s["scored"] is not None]
    iron_tonb_median = float(pd.Series(tonb).median()) if tonb else None
    print(f"[R1] iron-TonB (control-TonB) systems={len(tonb)} median_pct={iron_tonb_median:.3f} "
          f"-> REPORTED (iron acquisition induced; interaction-coupled, NOT a control)")

    # --- build modules + score per scored reference_class ---
    catalog_rows, system_rows, cand_idx = [], [], []
    for rc in SCORED_CLASSES:
        rc_systems = [s for s in systems.values()
                      if s["reference_class"] == rc and s["scored"] is not None]
        mods = build_modules([System(s["system_id"], s["substrate"], s["subunit_tags"])
                              for s in rc_systems])
        sysmap = {s["system_id"]: s for s in rc_systems}
        for m in mods:
            msys = [sysmap[sid] for sid in m.system_ids]
            pcts = [s["scored"]["percentile"] for s in msys]
            kcs = [s["scored"]["n_present"] for s in msys]
            eff = module_effect(pcts)
            # effect-driving system -> module tier
            drive = msys[pcts.index(max(pcts))]
            tier = "single-gene" if drive["scored"]["subunit_count"] == 1 else "multi-subunit"
            p = matched_max_null(kcs, universe, observed_max=eff, n_perms=N_PERMS, seed=SEED)
            row = dict(reference_class=rc, module_id=f"{rc}::{m.module_id}",
                       substrate=m.substrate,
                       carrier_family=";".join(sorted({s["carrier_family"] for s in msys})),
                       broad=m.broad, tier=tier, n_systems=len(msys),
                       n_genes=sum(s["scored"]["subunit_count"] for s in msys),
                       module_percentile=eff, p=p, q="")
            if rc == "candidate":
                cand_idx.append(len(catalog_rows))
            catalog_rows.append(row)
            for s in msys:
                st = "single-gene" if s["scored"]["subunit_count"] == 1 else "multi-subunit"
                system_rows.append(dict(
                    system_id=s["system_id"], module_id=f"{rc}::{m.module_id}",
                    reference_class=rc, tier=st, substrate=s["substrate"],
                    carrier_family=s["carrier_family"],
                    n_present=s["scored"]["n_present"], subunit_count=s["scored"]["subunit_count"],
                    system_percentile=s["scored"]["percentile"]))

    # BH across candidate modules only
    cand_q = bh_fdr([catalog_rows[i]["p"] for i in cand_idx])
    for i, q in zip(cand_idx, cand_q):
        catalog_rows[i]["q"] = q

    cat = pd.DataFrame(catalog_rows)
    cand = cat[cat.reference_class == "candidate"].copy()
    cand = cand.sort_values(["tier", "q", "module_percentile"], ascending=[True, True, False])
    cand.to_csv(OUT_CATALOG, index=False)
    sysdf = pd.DataFrame(system_rows)
    sysdf.sort_values(["reference_class", "tier", "system_percentile"],
                      ascending=[True, True, False]).to_csv(OUT_SYSTEMS, index=False)
    print(f"wrote {len(cand)} candidate modules -> {OUT_CATALOG}")
    print(f"wrote {len(sysdf)} scored system rows -> {OUT_SYSTEMS}")

    # --- size-matched control contrast (system-level) ---
    contrast_rows = []
    for rc in ["candidate", "control-ABC"]:
        for tier in ["single-gene", "multi-subunit"]:
            sub = sysdf[(sysdf.reference_class == rc) & (sysdf.tier == tier)]
            contrast_rows.append(dict(reference_class=rc, tier=tier, n_systems=len(sub),
                                      median_percentile=float(sub.system_percentile.median()) if len(sub) else None,
                                      mean_percentile=float(sub.system_percentile.mean()) if len(sub) else None))
    contrast_rows.append(dict(reference_class="iron-TonB (REPORTED, not a control)", tier="all",
                              n_systems=len(tonb), median_percentile=iron_tonb_median,
                              mean_percentile=float(pd.Series(tonb).mean()) if tonb else None))
    contrast_rows.append(dict(reference_class="ambiguous-TonB (dropped from scoring)", tier="all",
                              n_systems=len(amb_tonb),
                              median_percentile=float(pd.Series(amb_tonb).median()) if amb_tonb else None,
                              mean_percentile=float(pd.Series(amb_tonb).mean()) if amb_tonb else None))
    pd.DataFrame(contrast_rows).to_csv(OUT_CONTRAST, index=False)
    print(f"wrote control contrast -> {OUT_CONTRAST}")

    # --- R4 module-grouping guard: report multi-system modules ---
    print("\n[R4] multi-system modules (must share a real resolved substrate):")
    multi = cat[cat.n_systems > 1]
    for r in multi.to_dict("records"):
        print(f"    {r['reference_class']} '{r['substrate']}' n_systems={r['n_systems']} tier={r['tier']}")
    if len(multi) == 0:
        print("    (none)")

    # --- compact console ---
    print("\n=== size-matched control contrast (system-level) ===")
    for r in contrast_rows:
        print(f"  {r['reference_class']:38s} {r['tier']:13s} n={r['n_systems']:>3} "
              f"median={r['median_percentile']}")
    n_pass = int((pd.to_numeric(cand.q, errors="coerce") < 0.10).sum())
    print(f"\ncandidate modules passing q<0.10: {n_pass} of {len(cand)}")
    print("\n=== top 12 candidate modules (within-tier by q) ===")
    for r in cand.head(12).to_dict("records"):
        print(f"  [{r['tier']:12s}] q={float(r['q']):.4f} pct={r['module_percentile']:.3f} "
              f"nsys={r['n_systems']} | {r['substrate']} | {r['carrier_family']}")


if __name__ == "__main__":
    main()
