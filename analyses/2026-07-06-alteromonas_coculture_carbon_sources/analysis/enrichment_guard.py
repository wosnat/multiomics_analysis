"""Analysis milestone, step 5: genome-wide enrichment guard + per-module breakdown
flags. Runs the KG's built-in `pathway_enrichment` (ORA) once on the primary
experiment at KEGG and EC (pathway-map / enzyme-subclass level), reads the
UP-direction over-represented pathways, and for each candidate module that has a
DEDICATED KEGG degradation map reads off an up/not-up breakdown flag from the same
run (falling back to the map's median up-percentile when it is too small for ORA).
Facts only.

Level choice: `ontology_landscape` on this experiment ranks KEGG level 2 (145
pathway-map terms) and EC level 2 (85 terms) as the pathway-level slices; the
KEGG degradation maps (e.g. ko00280) are level-2 terms, so both the guard and the
breakdown flag read at KEGG level 2.

Outputs (analysis/): enrichment_guard.csv
"""
import csv
import json
import os

import numpy as np
from multiomics_explorer import pathway_enrichment, genes_by_ontology

EXP = "10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq"
ORG = "Alteromonas macleodii HOT1A3"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")

# Candidate module substrate -> dedicated KEGG degradation map (id, name, match_type).
# match_type: exact | broader (class map for a specific substrate) | narrower.
MODULE_DEGRADATION_MAP = {
    "branched-chain amino acid": ("kegg.pathway:ko00280", "Valine, leucine and isoleucine degradation", "exact"),
    "benzoate": ("kegg.pathway:ko00362", "Benzoate degradation", "exact"),
    "aminobenzoyl-glutamate": ("kegg.pathway:ko00627", "Aminobenzoate degradation", "broader"),
    "3-phenylpropionic acid": ("kegg.pathway:ko01220", "Degradation of aromatic compounds", "broader"),
}


def up_percentile(de):
    import pandas as pd
    s = pd.Series(de, dtype=float)
    r = s.rank(method="average")
    return {k: float(v) for k, v in ((r - 1) / (len(s) - 1)).items()}


def run_enr(ontology, level):
    res = pathway_enrichment(organism=ORG, experiment_ids=[EXP], ontology=ontology,
                             level=level, direction="both", significant_only=True,
                             background="table_scope")
    env = res.to_envelope() if hasattr(res, "to_envelope") else res
    return env


def main():
    de = {k: float(v) for k, v in json.load(open(os.path.join(CACHE, "de_table.json"))).items()}
    pct = up_percentile(de)

    rows_out = []   # (row_type, ...)

    # ---- genome-wide guard: KEGG level 2 + EC level 2 ----
    kegg = run_enr("kegg", 2)
    ec = run_enr("ec", 2)
    guard_index = {}   # (ontology, term_id, direction) -> row
    for ont, env in [("kegg", kegg), ("ec", ec)]:
        for r in env.get("results", []):
            guard_index[(ont, r["term_id"], r["direction"])] = r
            rows_out.append({
                "row_type": "genome_wide_enrichment", "ontology": ont,
                "term_id": r["term_id"], "term_name": r["term_name"],
                "direction": r["direction"], "count_k": r["count"],
                "bg_count_M": r["bg_count"], "gene_ratio": r["gene_ratio"],
                "fold_enrichment": round(r["fold_enrichment"], 3),
                "p_value": _sci(r["pvalue"]), "p_adjust": _sci(r["p_adjust"]),
                "significant": r["p_adjust"] < 0.05,
            })
    n_kegg_up = sum(1 for k, v in guard_index.items()
                    if k[0] == "kegg" and k[2] == "up" and v["p_adjust"] < 0.05)
    n_ec_up = sum(1 for k, v in guard_index.items()
                  if k[0] == "ec" and k[2] == "up" and v["p_adjust"] < 0.05)

    # ---- per-module breakdown flags ----
    for substrate, (map_id, map_name, match_type) in MODULE_DEGRADATION_MAP.items():
        up_row = guard_index.get(("kegg", map_id, "up"))
        if up_row is not None:
            flag = "up (ORA-enriched)" if up_row["p_adjust"] < 0.05 else "tested, not enriched (up)"
            evidence = (f"KEGG up ORA: k={up_row['count']}/M={up_row['bg_count']}, "
                        f"fold={up_row['fold_enrichment']:.2f}, p_adj={up_row['p_adjust']:.2g}")
            median_pct = None
        else:
            # fallback: median up-percentile of the map's HOT1A3 genes
            g = genes_by_ontology(ontology="kegg", organism=ORG, term_ids=[map_id],
                                  min_gene_set_size=0, max_gene_set_size=None, limit=None)
            genes = sorted({r["locus_tag"] for r in g.get("results", [])})
            pcts = [pct[x] for x in genes if x in pct]
            median_pct = float(np.median(pcts)) if pcts else None
            if median_pct is None:
                flag = "not determinable (map has no scored genes)"
                evidence = f"{map_id} genes in DE: 0"
            else:
                flag = f"median up-pct={median_pct:.3f} (>0.5=up-leaning)" if median_pct > 0.5 \
                    else f"median up-pct={median_pct:.3f} (<=0.5=not up)"
                evidence = f"fallback: {len(pcts)} genes of {map_id} scored, median up-pct={median_pct:.3f}"
        rows_out.append({
            "row_type": "module_breakdown_flag", "ontology": "kegg",
            "term_id": map_id, "term_name": map_name, "direction": "up",
            "substrate_module": substrate, "match_type": match_type,
            "breakdown_flag": flag, "evidence": evidence,
            "median_up_pct": round(median_pct, 4) if median_pct is not None else None,
        })

    # ---- write ----
    cols = ["row_type", "ontology", "term_id", "term_name", "direction",
            "substrate_module", "match_type", "breakdown_flag", "evidence",
            "median_up_pct", "count_k", "bg_count_M", "gene_ratio",
            "fold_enrichment", "p_value", "p_adjust", "significant"]
    path = os.path.join(HERE, "enrichment_guard.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows_out:
            w.writerow(r)

    summary = {
        "kegg_terms_tested": kegg.get("total_matching"),
        "kegg_up_significant": n_kegg_up,
        "ec_up_significant": n_ec_up,
        "kegg_n_significant_all": kegg.get("n_significant"),
        "ec_n_significant_all": ec.get("n_significant"),
        "top_kegg_up": [(v["term_name"], round(v["fold_enrichment"], 2),
                         _sci(v["p_adjust"])) for k, v in
                        sorted(guard_index.items(), key=lambda kv: kv[1]["p_adjust"])
                        if k[0] == "kegg" and k[2] == "up" and v["p_adjust"] < 0.05][:12],
        "breakdown_flags": [(r["substrate_module"], r["breakdown_flag"])
                            for r in rows_out if r["row_type"] == "module_breakdown_flag"],
    }
    json.dump(summary, open(os.path.join(CACHE, "enrichment_summary.json"), "w"),
              indent=1, default=str)
    print("KEGG up-significant terms:", n_kegg_up, "| EC up-significant:", n_ec_up)
    print("top KEGG up:", summary["top_kegg_up"])
    print("breakdown flags:", summary["breakdown_flags"])
    print("wrote enrichment_guard.csv")


def _sci(x):
    return None if x is None else float(f"{x:.3e}")


if __name__ == "__main__":
    main()
