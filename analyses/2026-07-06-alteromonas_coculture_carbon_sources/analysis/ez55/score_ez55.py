"""EZ55 module scoring — Part 2 of the cross-strain step.

Scores the EZ55 organic-C importer modules on the two pCO2 presence contrasts
(coculture-vs-axenic at 400 and 800 ppm; both `significant_only`, edgeR). Reuses
the committed `methods/score_modules.py`. Because these tables are
`significant_only`, the up-percentile ranking and the permutation null live WITHIN
the significant set (`scope="significant_only"`) — a weaker, presence-weighted
signal, and most module systems have few/no genes detected. Artifacts only.

Outputs (analysis/ez55/):
  ez55_module_scores.csv   one row per (module x arm) + cross_arm_agreement
  ez55_validation.csv      motility / peptidase / ribosomal / glcB per arm
  ez55_run_manifest.md
"""
import csv
import json
import os
import sys
from collections import Counter

import numpy as np
from multiomics_explorer import differential_expression_by_gene

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
METHODS = os.path.abspath(os.path.join(HERE, "..", "..", "methods"))
sys.path.insert(0, METHODS)
import score_modules as sm

ORG = "Alteromonas macleodii EZ55"
TABLE = os.path.join(HERE, "ez55_transporter_table.csv")
GLCB = "EZ55_02804"       # malate synthase G (glycolate soft handle)
ARMS = {
    "400ppm": "10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_400_ez55_rnaseq",
    "800ppm": "10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_800_ez55_rnaseq",
}


def pull_arm(arm, exp):
    r = differential_expression_by_gene(organism=ORG, experiment_ids=[exp],
                                        limit=None, verbose=True)
    rows = r["results"]
    de, cat = {}, {}
    for row in rows:
        de[row["locus_tag"]] = row["log2fc"]
        cat[row["locus_tag"]] = row.get("gene_category")
    scope = list(r.get("by_table_scope", {}).keys())
    n = len(de)
    neg = sum(1 for v in de.values() if v < 0)
    pos = sum(1 for v in de.values() if v > 0)
    json.dump(de, open(os.path.join(CACHE, f"de_{arm}.json"), "w"))
    json.dump(cat, open(os.path.join(CACHE, f"cat_{arm}.json"), "w"))
    print(f"{arm}: n={n} scope={scope} neg={neg} ({100*neg/n:.1f}%) pos={pos} "
          f"status={r.get('rows_by_status')}")
    return de, cat, {"n_genes": n, "scope": scope, "negative": neg,
                     "positive": pos, "pct_negative": round(100*neg/n, 2),
                     "rows_by_status": r.get("rows_by_status")}


def main():
    modules, controls = sm.build_modules_from_csv(
        TABLE, exclude_interaction_coupled_controls=True)
    peptidase = set(json.load(open(os.path.join(CACHE, "ez55_peptidase_genes.json"))))
    print(f"EZ55 modules={len(modules)} controls={len(controls)}")

    de, cat, pull_log = {}, {}, {}
    scored, pcts = {}, {}
    for arm, exp in ARMS.items():
        de[arm], cat[arm], pull_log[arm] = pull_arm(arm, exp)
        res = sm.score_modules(modules, controls, de[arm],
                               scope="significant_only", n_perm=10000, seed=0)
        scored[arm] = {r["substrate_call"]: r for r in res}
        pcts[arm] = sm.up_percentile(de[arm])
        print(f"  scored {arm}: called_up={sum(1 for r in res if r['called_up'])}")

    subs = sorted({m["substrate_call"] for m in modules})
    nsys = {m["substrate_call"]: len(m["systems"]) for m in modules}

    # cross-arm agreement: called up (q<0.10) in BOTH arms
    agree = {s: (scored["400ppm"][s]["called_up"] and scored["800ppm"][s]["called_up"])
             for s in subs}

    # ---- module scores CSV (one row per module x arm) ----
    cols = ["substrate_call", "resolution_level", "confidence_flag", "arm",
            "n_systems", "n_systems_detected", "module_effect", "p_perm",
            "q_perm", "called_up", "p_vs_control", "cross_arm_agreement"]
    with open(os.path.join(HERE, "ez55_module_scores.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for s in subs:
            for arm in ARMS:
                r = scored[arm][s]
                w.writerow({
                    "substrate_call": s, "resolution_level": r["resolution_level"],
                    "confidence_flag": r["confidence_flag"], "arm": arm,
                    "n_systems": r["n_systems"],
                    "n_systems_detected": r["n_systems_detected"],
                    "module_effect": _r(r["module_effect"]),
                    "p_perm": _r(r["p_perm"]), "q_perm": _r(r["q_perm"]),
                    "called_up": r["called_up"], "p_vs_control": _r(r["p_vs_control"]),
                    "cross_arm_agreement": agree[s],
                })

    # ---- validation per arm ----
    with open(os.path.join(HERE, "ez55_validation.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arm", "set", "n_in_significant_set", "median_up_pct", "expected"])
        for arm in ARMS:
            pct = pcts[arm]
            mot = [pct[g] for g, c in cat[arm].items() if c == "Cell motility"]
            trn = [pct[g] for g, c in cat[arm].items() if c == "Translation"]
            pep = [pct[g] for g in peptidase if g in pct]
            for name, vals, exp in [("motility_Cell_motility", mot, "down"),
                                    ("peptidase_protease", pep, "up"),
                                    ("ribosomal_Translation", trn, "~neutral")]:
                med = float(np.median(vals)) if vals else None
                w.writerow([arm, name, len(vals), _r(med), exp])
            glcb = pct.get(GLCB)
            w.writerow([arm, f"glcB_{GLCB}", 1 if glcb is not None else 0, _r(glcb),
                        "up if glycolate (soft); absent from sig set => blank"])

    _manifest(modules, subs, nsys, scored, agree, pull_log, pcts, cat, peptidase)
    print("wrote ez55_module_scores.csv, ez55_validation.csv, ez55_run_manifest.md")


def _r(x):
    return round(x, 4) if isinstance(x, (int, float)) else x


def _manifest(modules, subs, nsys, scored, agree, pull_log, pcts, cat, peptidase):
    up = {arm: [s for s in subs if scored[arm][s]["called_up"]] for arm in ARMS}
    both = [s for s in subs if agree[s]]
    # detected-system sparsity (significant_only weakness)
    det = {arm: [scored[arm][s]["n_systems_detected"] for s in subs] for arm in ARMS}
    L = []
    L.append("# EZ55 module scoring — run manifest (facts only)\n")
    L.append("Two pCO2 presence contrasts (coculture-vs-axenic, MIT9312 partner), "
             "both `significant_only` / edgeR. Committed `score_modules.py` reused; "
             "`scope=\"significant_only\"` so ranking + null live within the "
             "significant set. The two arms are the **same lab/strain/cultures at "
             "two CO2 levels** → pCO2 agreement is an internal consistency check, "
             "NOT two independent supports.\n")
    L.append("## EZ55 transporter table (see ez55_build_manifest.md)\n")
    L.append(f"- {len(subs)} organic-C importer modules over "
             f"{sum(len(m['systems']) for m in modules)} systems; "
             f"clean inorganic control set (N/P excluded).\n")
    L.append("## Per-arm DE pulls\n")
    for arm in ARMS:
        p = pull_log[arm]
        L.append(f"- **{arm}**: {p['n_genes']} genes, scope={p['scope']}, "
                 f"sign {p['negative']} neg / {p['positive']} pos "
                 f"({p['pct_negative']}% neg), status={p['rows_by_status']}. "
                 f"(Both signs present → sign not lost; the 40–55%-negative "
                 f"all-genes check does not apply to a significant_only table.)")
    L.append("")
    L.append("## Modules called up (q<0.10)\n")
    for arm in ARMS:
        L.append(f"- **{arm}** ({len(up[arm])}): {up[arm]}")
    L.append(f"- **Called up in BOTH arms (pCO2-agreement, internal consistency — "
             f"one strain-partner support): {len(both)}** — {both}\n")
    L.append("## significant_only sparsity (weakness flag)\n")
    for arm in ARMS:
        d = det[arm]
        L.append(f"- **{arm}**: n_systems_detected per module — "
                 f"median {int(np.median(d))}, max {max(d)}, "
                 f"modules with 0 detected systems: {sum(1 for x in d if x == 0)} "
                 f"of {len(subs)}. Most modules have few/no systems with a gene in "
                 f"the significant set → thin, presence-weighted evidence.")
    L.append("")
    L.append("## Validation (median up-pct within the significant set)\n")
    for arm in ARMS:
        pct = pcts[arm]
        mot = [pct[g] for g, c in cat[arm].items() if c == "Cell motility"]
        trn = [pct[g] for g, c in cat[arm].items() if c == "Translation"]
        pep = [pct[g] for g in peptidase if g in pct]
        glcb = pct.get(GLCB)
        L.append(f"- **{arm}**: motility n={len(mot)} med="
                 f"{_r(float(np.median(mot))) if mot else None}; "
                 f"peptidase n={len(pep)} med={_r(float(np.median(pep))) if pep else None}; "
                 f"ribosomal n={len(trn)} med={_r(float(np.median(trn))) if trn else None}; "
                 f"glcB {GLCB}={'not in sig set' if glcb is None else _r(glcb)}")
    L.append("")
    L.append("## Anomalies / flags (facts)\n")
    L.append("- `significant_only` scope: ranking + permutation null are within the "
             "significant set (~419 / ~188 genes), not genome-wide — weaker, "
             "presence-weighted; n_systems_detected is low for most modules.")
    L.append("- The two arms are not independent supports (same cultures, two CO2 "
             "levels); reported as a pCO2 internal-consistency agreement count.")
    L.append("- `glcB` may be absent from a significant_only table (no row unless "
             "significant) — reported as 'not in sig set' where so.")
    with open(os.path.join(HERE, "ez55_run_manifest.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    main()
