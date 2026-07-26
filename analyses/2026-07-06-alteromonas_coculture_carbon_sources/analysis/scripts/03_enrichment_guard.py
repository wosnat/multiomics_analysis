#!/usr/bin/env python3
"""
Analysis milestone -- step 3: genome-wide enrichment guard (coarse).

ontology_landscape (run interactively) picked KEGG best_level=1, EC best_level=1
for this experiment. Runs pathway_enrichment (KEGG l1 + EC l1) on the full DE,
direction=both, table_scope background, and saves top over-represented terms.
This is the COARSE guard only -- per-module breakdown-map selection is deferred.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/03_enrichment_guard.py
"""
import os
import pandas as pd
from multiomics_explorer import pathway_enrichment

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
OUT = os.path.join(DATA, "qc_enrichment_guard.csv")
EXP = "10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq"


def main():
    frames = []
    for onto, lvl in [("kegg", 1), ("ec", 1)]:
        res = pathway_enrichment(organism="HOT1A3", experiment_ids=[EXP],
                                 ontology=onto, level=lvl, direction="both")
        df = res.results.copy()
        df["ontology"] = onto
        df["level"] = lvl
        frames.append(df)
    allr = pd.concat(frames, ignore_index=True)
    keep = ["ontology", "level", "cluster", "direction", "term_id", "term_name",
            "count", "bg_count", "gene_ratio", "fold_enrichment", "pvalue",
            "p_adjust", "signed_score"]
    keep = [c for c in keep if c in allr.columns]
    # keep informative rows: significant OR top by p_adjust per ontology
    out = allr[keep].sort_values(["ontology", "p_adjust"]).copy()
    out.to_csv(OUT, index=False)
    print(f"wrote {len(out)} rows -> {OUT}")
    print("\n=== padj < 0.10 terms (the guard) ===")
    sig = out[out.p_adjust < 0.10]
    for r in sig.to_dict("records"):
        print(f"  {r['ontology']} {r['direction']:4s} padj={r['p_adjust']:.4f} "
              f"fold={r['fold_enrichment']:.2f} {r['count']}/{r['bg_count']} | {r['term_name']}")


if __name__ == "__main__":
    main()
