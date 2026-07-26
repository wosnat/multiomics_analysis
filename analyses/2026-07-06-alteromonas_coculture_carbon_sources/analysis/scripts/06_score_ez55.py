#!/usr/bin/env python3
"""
Analysis milestone -- score the EZ55 presence contrasts (400 + 800 ppm pCO2).

significant_only scoring: the ranking universe per arm is that arm's significant
genes only (presence-weighted, as the proposal specifies). Same analysis-layer
refinements as HOT1A3:
  - Drop TonB (control-TonB + ambiguous-TonB) from scoring; control = control-ABC.
    Record EZ55 iron-TonB median as a reported finding (not a control).
  - Relabel EZ55_03747 'unresolved' -> 'carbohydrate (MFS)' (gene_category
    Carbohydrate metabolism; COG0738 Fucose permease). [KG-confirmed]
  - Relabel EZ55_01261 (SLC13) -> 'di-/tricarboxylate (citrate, CitMHS)'
    (Pfam CitMHS + eggNOG COG0471; inorganic gene_category is a coarse COG-P bin). [KG]
  - Module-grouping guard (decision-12).

Imports committed scoring.py. Reads committed parts_list_v2.csv (EZ55 rows).
Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/06_score_ez55.py
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
SCORED_CLASSES = ["candidate", "control-ABC"]
PRIORITY = ["candidate", "control-ABC", "control-TonB", "interaction-coupled",
            "ambiguous-TonB", "set-aside", "other"]
SUBSTRATE_OVERRIDE = {
    "EZ55_03747": "carbohydrate (MFS)",
    "EZ55_01261": "di-/tricarboxylate (citrate, CitMHS)",
}
VALID_GENES = {"glcB glycolate": "EZ55_02804", "benE aromatic": "EZ55_00725"}
ARMS = ["400", "800"]


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


def build_systems(parts, pct):
    systems = {}
    for sid, grp in parts.groupby("system_id"):
        members = grp.to_dict("records")
        rc = system_reference_class(set(grp.reference_class))
        substrate, cfam = pick_substrate(members)
        tags = grp.locus_tag.tolist()
        scored = score_system(tags, pct)  # median over PRESENT (significant-set) subunits
        systems[sid] = dict(system_id=sid, reference_class=rc, substrate=substrate,
                            carrier_family=cfam, subunit_tags=tags, scored=scored)
    return systems


def score_arm(arm, parts):
    de = pd.read_csv(os.path.join(DATA, f"de_ez55_{arm}.csv"))
    pct = up_percentiles(dict(zip(de.locus_tag, de.log2fc)))
    universe = list(pct.values())
    systems = build_systems(parts, pct)

    tonb = [s["scored"]["percentile"] for s in systems.values()
            if s["reference_class"] == "control-TonB" and s["scored"]]
    iron_med = float(pd.Series(tonb).median()) if tonb else None

    catalog, sysrows, cand_idx = [], [], []
    for rc in SCORED_CLASSES:
        rc_sys = [s for s in systems.values() if s["reference_class"] == rc and s["scored"]]
        mods = build_modules([System(s["system_id"], s["substrate"], s["subunit_tags"]) for s in rc_sys])
        smap = {s["system_id"]: s for s in rc_sys}
        for m in mods:
            msys = [smap[i] for i in m.system_ids]
            pcts = [s["scored"]["percentile"] for s in msys]
            kcs = [s["scored"]["n_present"] for s in msys]
            eff = module_effect(pcts)
            drive = msys[pcts.index(max(pcts))]
            tier = "single-gene" if drive["scored"]["subunit_count"] == 1 else "multi-subunit"
            p = matched_max_null(kcs, universe, observed_max=eff, n_perms=N_PERMS, seed=SEED)
            if rc == "candidate":
                cand_idx.append(len(catalog))
            catalog.append(dict(reference_class=rc, module_id=f"{rc}::{m.module_id}",
                                substrate=m.substrate,
                                carrier_family=";".join(sorted({s["carrier_family"] for s in msys})),
                                broad=m.broad, tier=tier, n_systems=len(msys),
                                n_genes=sum(s["scored"]["subunit_count"] for s in msys),
                                module_percentile=eff, p=p, q=""))
            for s in msys:
                st = "single-gene" if s["scored"]["subunit_count"] == 1 else "multi-subunit"
                sysrows.append(dict(arm=arm, system_id=s["system_id"], reference_class=rc,
                                    tier=st, substrate=s["substrate"],
                                    n_present=s["scored"]["n_present"],
                                    subunit_count=s["scored"]["subunit_count"],
                                    system_percentile=s["scored"]["percentile"]))
    cand_q = bh_fdr([catalog[i]["p"] for i in cand_idx])
    for i, q in zip(cand_idx, cand_q):
        catalog[i]["q"] = q

    cat = pd.DataFrame(catalog)
    cand = cat[cat.reference_class == "candidate"].sort_values(
        ["tier", "q", "module_percentile"], ascending=[True, True, False])
    cand.to_csv(os.path.join(DATA, f"module_catalog_ez55_{arm}.csv"), index=False)

    sysdf = pd.DataFrame(sysrows)
    # size-matched contrast rows
    contrast = []
    for rc in ["candidate", "control-ABC"]:
        for tier in ["single-gene", "multi-subunit"]:
            sub = sysdf[(sysdf.reference_class == rc) & (sysdf.tier == tier)]
            contrast.append(dict(arm=arm, reference_class=rc, tier=tier, n=len(sub),
                                 median_pct=float(sub.system_percentile.median()) if len(sub) else None,
                                 mean_pct=float(sub.system_percentile.mean()) if len(sub) else None))
    contrast.append(dict(arm=arm, reference_class="iron-TonB (REPORTED, not a control)",
                         tier="all", n=len(tonb), median_pct=iron_med,
                         mean_pct=float(pd.Series(tonb).mean()) if tonb else None))

    # validation
    de_pct = de.assign(pct=de.locus_tag.map(pct))
    val = []
    for label, cat_name in [("motility/flagellar (Cell motility)", "Cell motility"),
                            ("ribosomal/Translation", "Translation")]:
        s = de_pct[de_pct.gene_category == cat_name]
        val.append(dict(arm=arm, set=label, n=len(s),
                        median_percentile=float(s.pct.median()) if len(s) else None))
    for label, lt in VALID_GENES.items():
        present = lt in pct
        val.append(dict(arm=arm, set=label, n=(1 if present else 0),
                        median_percentile=(float(pct[lt]) if present else None)))
    return cand, contrast, val, iron_med, len(tonb)


def main():
    parts = pd.read_csv(PARTS)
    parts = parts[parts.organism_name.str.contains("EZ55")].copy()

    all_contrast, all_val = [], []
    arm_cand = {}
    for arm in ARMS:
        cand, contrast, val, iron_med, ntonb = score_arm(arm, parts)
        arm_cand[arm] = cand
        all_contrast += contrast
        all_val += val
        npass = int((pd.to_numeric(cand.q, errors="coerce") < 0.10).sum())
        print(f"\n### EZ55 {arm} ppm: {len(cand)} candidate modules, {npass} pass q<0.10; "
              f"iron-TonB median={iron_med:.3f} (n={ntonb}, REPORTED not control)")
        print("  top 10 candidate modules (within-tier by q):")
        for r in cand.head(10).to_dict("records"):
            print(f"    [{r['tier']:12s}] q={float(r['q']):.4f} pct={r['module_percentile']:.3f} "
                  f"nsys={r['n_systems']} | {r['substrate']} | {r['carrier_family']}")

    pd.DataFrame(all_contrast).to_csv(os.path.join(DATA, "qc_control_contrast_ez55.csv"), index=False)
    pd.DataFrame(all_val).to_csv(os.path.join(DATA, "qc_validation_ez55.csv"), index=False)
    print("\nwrote module_catalog_ez55_{400,800}.csv, qc_control_contrast_ez55.csv, qc_validation_ez55.csv")

    print("\n=== size-matched control contrast ===")
    for r in all_contrast:
        print(f"  {r['arm']} {r['reference_class']:38s} {r['tier']:13s} n={r['n']:>3} median={r['median_pct']}")
    print("\n=== validation medians ===")
    for r in all_val:
        print(f"  {r['arm']} {r['set']}: n={r['n']} median={r['median_percentile']}")

    # cross-strain reproducibility prep: which HOT1A3-type substrates score high in EZ55
    print("\n=== cross-strain prep: HOT1A3-type substrates in EZ55 candidate catalogs ===")
    keys = ["carbohydrate", "citrate", "dicarbox", "sugar", "fucose", "MFS", "benzoate", "aromatic"]
    for arm in ARMS:
        c = arm_cand[arm]
        hit = c[c.substrate.str.contains("|".join(keys), case=False) |
                c.carrier_family.str.contains("|".join(keys), case=False)]
        print(f"  [{arm}]")
        for r in hit.to_dict("records"):
            print(f"     q={float(r['q']):.3f} pct={r['module_percentile']:.3f} tier={r['tier']} "
                  f"| {r['substrate']} | {r['carrier_family']}")


if __name__ == "__main__":
    main()
