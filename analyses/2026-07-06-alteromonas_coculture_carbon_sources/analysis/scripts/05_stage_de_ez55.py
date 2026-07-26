#!/usr/bin/env python3
"""
Analysis milestone -- stage EZ55 presence-contrast DE (both pCO2 arms).

Experiments (significant_only -- only significant genes have rows):
  400: 10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_400_ez55_rnaseq
  800: 10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_800_ez55_rnaseq

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/05_stage_de_ez55.py
"""
import os
import pandas as pd
from multiomics_explorer import differential_expression_by_gene

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
ARMS = {
    "400": "10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_400_ez55_rnaseq",
    "800": "10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_800_ez55_rnaseq",
}


def main():
    for arm, exp in ARMS.items():
        res = differential_expression_by_gene(experiment_ids=[exp], organism="EZ55",
                                              verbose=True, limit=None)
        df = pd.DataFrame([{
            "locus_tag": r["locus_tag"], "gene_name": r.get("gene_name"),
            "product": r.get("product"), "gene_category": r.get("gene_category"),
            "log2fc": r["log2fc"], "padj": r.get("padj"),
            "expression_status": r.get("expression_status"), "timepoint": r.get("timepoint"),
        } for r in res["results"]])
        out = os.path.join(DATA, f"de_ez55_{arm}.csv")
        df.to_csv(out, index=False)
        n = len(df)
        up = int((df.expression_status == "significant_up").sum())
        down = int((df.expression_status == "significant_down").sum())
        frac_neg = float((df.log2fc < 0).mean())
        print(f"[{arm}] wrote {n} rows -> {out}")
        print(f"      up/down = {up}/{down}  | fraction negative log2fc = {frac_neg:.3f} "
              f"| table_scope={res['experiments'][0]['table_scope']}")


if __name__ == "__main__":
    main()
