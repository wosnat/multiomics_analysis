#!/usr/bin/env python3
"""
Analysis milestone -- step 2: run the committed scorer on the HOT1A3 day-11 contrast.

Imports scoring.py from ../methods/scripts (does NOT reimplement). Loads the frozen
parts_list_v2.csv (systems, reference_class, substrate). Produces the module catalog,
per-system detail, and validation-set percentiles.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/02_score_modules.py
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
OUT_CATALOG = os.path.join(DATA, "module_catalog_hot1a3_day11.csv")
OUT_SYSTEMS = os.path.join(DATA, "system_scores_hot1a3_day11.csv")
OUT_VALID = os.path.join(DATA, "qc_validation.csv")

N_PERMS = 10000
SEED = 0
SCORED_CLASSES = ["candidate", "control-ABC", "control-TonB", "ambiguous-TonB"]
# priority for collapsing a multi-member system to one reference_class
PRIORITY = ["candidate", "control-ABC", "control-TonB", "interaction-coupled",
            "ambiguous-TonB", "set-aside", "other"]


def system_reference_class(ref_classes):
    for r in PRIORITY:
        if r in ref_classes:
            return r
    return "other"


def pick_substrate(members):
    """Best substrate for a system: confident+resolved > inferred+resolved > unresolved."""
    def resolved(s):
        return s and str(s).strip().lower() not in ("", "unresolved", "nan")
    conf = [m for m in members if m["substrate_confidence"] == "confident" and resolved(m["substrate_provisional"])]
    if conf:
        return conf[0]["substrate_provisional"], conf[0]["carrier_family"]
    inf = [m for m in members if resolved(m["substrate_provisional"])]
    if inf:
        return inf[0]["substrate_provisional"], inf[0]["carrier_family"]
    return "unresolved", members[0]["carrier_family"]


def main():
    de = pd.read_csv(DE)
    log2fc = dict(zip(de.locus_tag, de.log2fc))
    pct = up_percentiles(log2fc)
    universe = list(pct.values())
    print(f"up-percentiles over {len(pct)} detected genes")

    parts = pd.read_csv(PARTS)
    parts = parts[parts.organism_name.str.contains("HOT1A3")].copy()

    # ---- build systems ----
    systems = {}  # system_id -> dict
    for sid, grp in parts.groupby("system_id"):
        members = grp.to_dict("records")
        rc = system_reference_class(set(grp.reference_class))
        substrate, cfam = pick_substrate(members)
        tags = grp.locus_tag.tolist()
        scored = score_system(tags, pct)  # None if no subunit detected
        systems[sid] = dict(system_id=sid, reference_class=rc, substrate=substrate,
                            carrier_family=cfam, subunit_tags=tags, scored=scored)

    n_unscored = sum(1 for s in systems.values() if s["scored"] is None)
    print(f"{len(systems)} systems; {n_unscored} unscored (no subunit detected)")

    # ---- per reference_class group: build modules, score, null ----
    catalog_rows, system_rows = [], []
    cand_module_idx = []  # indices into catalog_rows that are candidates (for FDR)
    for rc in SCORED_CLASSES:
        rc_systems = [s for s in systems.values()
                      if s["reference_class"] == rc and s["scored"] is not None]
        mod_objs = build_modules([System(s["system_id"], s["substrate"], s["subunit_tags"])
                                  for s in rc_systems])
        sysmap = {s["system_id"]: s for s in rc_systems}
        for m in mod_objs:
            msys = [sysmap[sid] for sid in m.system_ids]
            sys_pcts = [s["scored"]["percentile"] for s in msys]
            k_counts = [s["scored"]["n_present"] for s in msys]
            eff = module_effect(sys_pcts)
            p = matched_max_null(k_counts, universe, observed_max=eff,
                                 n_perms=N_PERMS, seed=SEED)
            row = dict(reference_class=rc, module_id=f"{rc}::{m.module_id}",
                       substrate=m.substrate,
                       carrier_family=";".join(sorted({s["carrier_family"] for s in msys})),
                       broad=m.broad, n_systems=len(msys),
                       n_genes=sum(s["scored"]["subunit_count"] for s in msys),
                       module_percentile=eff, p=p, q="")
            if rc == "candidate":
                cand_module_idx.append(len(catalog_rows))
            catalog_rows.append(row)
            for s in msys:
                system_rows.append(dict(
                    system_id=s["system_id"], module_id=f"{rc}::{m.module_id}",
                    reference_class=rc, substrate=s["substrate"],
                    carrier_family=s["carrier_family"],
                    n_present=s["scored"]["n_present"],
                    subunit_count=s["scored"]["subunit_count"],
                    system_percentile=s["scored"]["percentile"]))

    # ---- BH/FDR across candidate modules only ----
    cand_p = [catalog_rows[i]["p"] for i in cand_module_idx]
    cand_q = bh_fdr(cand_p)
    for i, q in zip(cand_module_idx, cand_q):
        catalog_rows[i]["q"] = q

    cat = pd.DataFrame(catalog_rows)
    # sort: candidates by q then percentile; controls after
    cat["_qsort"] = cat["q"].apply(lambda x: x if x != "" else 9.0)
    cat = cat.sort_values(["_qsort", "module_percentile"], ascending=[True, False]).drop(columns="_qsort")
    cat.to_csv(OUT_CATALOG, index=False)
    pd.DataFrame(system_rows).sort_values(["reference_class", "module_id", "system_percentile"],
                                          ascending=[True, True, False]).to_csv(OUT_SYSTEMS, index=False)
    print(f"wrote {len(cat)} modules -> {OUT_CATALOG}")
    print(f"wrote {len(system_rows)} system rows -> {OUT_SYSTEMS}")

    # ---- validation sets ----
    val_rows = []
    de_pct = de.assign(pct=de.locus_tag.map(pct))
    mot = de_pct[de_pct.gene_category == "Cell motility"]
    val_rows.append(dict(set="motility/flagellar (Cell motility)", n=len(mot),
                         median_percentile=float(mot.pct.median()), expected="low (down)"))
    trans = de_pct[de_pct.gene_category == "Translation"]
    val_rows.append(dict(set="ribosomal/Translation", n=len(trans),
                         median_percentile=float(trans.pct.median()), expected="~0.5 neutral"))
    for lt, name in [("ACZ81_13685", "glcB glycolate"), ("ACZ81_05870", "hcaT aromatic/phenylpropionate")]:
        val_rows.append(dict(set=name, n=1,
                             median_percentile=(float(pct[lt]) if lt in pct else None),
                             expected="up if used (positive/soft)"))
    pd.DataFrame(val_rows).to_csv(OUT_VALID, index=False)
    print(f"wrote validation -> {OUT_VALID}")

    # ---- compact console summary ----
    print("\n=== control-class module-percentile medians ===")
    for rc in SCORED_CLASSES:
        sub = cat[cat.reference_class == rc]
        print(f"  {rc:16s}: n_modules={len(sub)}  median_module_pct={sub.module_percentile.median():.3f}")
    print("\n=== validation medians ===")
    for r in val_rows:
        print(f"  {r['set']}: n={r['n']} median_pct={r['median_percentile']}")
    print("\n=== top 15 candidate modules by q ===")
    cc = cat[cat.reference_class == "candidate"].head(15)
    for r in cc.to_dict("records"):
        print(f"  q={r['q']:.4f} pct={r['module_percentile']:.3f} nsys={r['n_systems']} "
              f"| {r['substrate']} | {r['carrier_family']}")


if __name__ == "__main__":
    main()
