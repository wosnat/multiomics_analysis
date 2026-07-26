#!/usr/bin/env python3
"""
Analysis milestone -- step 1: pull + stage the HOT1A3 day-11 presence contrast DE.

Experiment: 10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq
(all_detected_genes, DESeq2, single timepoint day 11). Stages every detected gene
to analysis/data/de_hot1a3_day11.csv and reports QC.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/01_stage_de.py
"""
import os
import pandas as pd
from multiomics_explorer import differential_expression_by_gene

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(DATA, exist_ok=True)
OUT = os.path.join(DATA, "de_hot1a3_day11.csv")
EXP = "10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq"


def main():
    res = differential_expression_by_gene(experiment_ids=[EXP], organism="HOT1A3",
                                          verbose=True, limit=None)
    rows = res["results"]
    df = pd.DataFrame([{
        "locus_tag": r["locus_tag"],
        "gene_name": r.get("gene_name"),
        "product": r.get("product"),
        "gene_category": r.get("gene_category"),
        "log2fc": r["log2fc"],
        "padj": r.get("padj"),
        "expression_status": r.get("expression_status"),
        "timepoint": r.get("timepoint"),
    } for r in rows])
    df.to_csv(OUT, index=False)

    n = len(df)
    up = int((df.expression_status == "significant_up").sum())
    down = int((df.expression_status == "significant_down").sum())
    frac_neg = float((df.log2fc < 0).mean())
    timepoints = sorted(df.timepoint.dropna().unique().tolist())
    null_l2fc = int(df.log2fc.isna().sum())

    print(f"wrote {n} rows -> {OUT}")
    print(f"  gene count: {n}  (expect ~3947)")
    print(f"  significant up / down: {up} / {down}  (proposal 111 / 163)")
    print(f"  fraction negative log2fc: {frac_neg:.3f}  (expect ~0.40-0.55; near-0 => sign lost)")
    print(f"  timepoints present: {timepoints}  (expect single 'day 11')")
    print(f"  null log2fc rows: {null_l2fc}  (expect 0 for all_detected_genes)")
    print(f"  is_time_course: {res['experiments'][0]['is_time_course']}")


if __name__ == "__main__":
    main()
