"""Step 2 — enumerate the Prochlorococcus differential-expression universe.

Purpose:
  Freeze the set of Prochlorococcus DE experiments (the "conditions" we will
  pool over for broad-responsiveness) and the publications behind them, so the
  KG-entries selection is reproducible and reviewable.

Inputs:  KG via multiomics_explorer (Neo4j creds from repo-root .env).
Outputs:
  data/de_experiments.csv   — one row per DE experiment (the conditions universe)
  data/publications.csv     — one row per publication contributing experiments
  data/01_de_experiments.log (stdout tee) — funnel + breakdowns

Run:  uv run python 2_kg_selection/scripts/01_de_experiments.py
      (from the analysis dir: analyses/2026-06-16-conserved_hypothetical_de/)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from multiomics_explorer import list_experiments, to_dataframe

DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)


def main() -> None:
    res = list_experiments(organism="Prochlorococcus", limit=None, verbose=True)
    print(f"[funnel] total Prochlorococcus DE experiments matched: {res['total_matching']}")

    df = to_dataframe(res)  # one row per experiment (nested timepoints dropped)
    # Keep the columns that characterize a "condition" for pooling.
    keep = [
        "experiment_id", "organism_name", "treatment_type", "background_factors",
        "omics_type", "compartment", "table_scope", "table_scope_detail",
        "is_time_course", "coculture_partner", "gene_count", "distinct_gene_count",
        "genes_by_status_significant_up", "genes_by_status_significant_down",
        "growth_phases", "publication_doi", "publication_title",
        "experiment_name", "treatment", "control",
    ]
    keep = [c for c in keep if c in df.columns]
    exp = df[keep].drop_duplicates(subset=["experiment_id"]).reset_index(drop=True)
    exp.to_csv(DATA / "de_experiments.csv", index=False)
    print(f"[out] wrote {len(exp)} experiments -> data/de_experiments.csv")

    # Breakdowns (recon view) straight from the envelope rollups.
    def show(name: str, key: str, idkey: str) -> None:
        rows = res[key]
        print(f"\n[{name}]")
        for r in rows:
            print(f"  {r[idkey]:<28} {r['count']}")

    show("by strain", "by_organism", "organism_name")
    show("by treatment_type", "by_treatment_type", "treatment_type")
    show("by omics_type", "by_omics_type", "omics_type")
    show("by table_scope", "by_table_scope", "table_scope")

    # Publications behind these experiments (derived from per-experiment rows).
    pubs = (
        exp.dropna(subset=["publication_doi"])
        .groupby(["publication_doi", "publication_title"], dropna=False)
        .agg(n_experiments=("experiment_id", "nunique"),
             strains=("organism_name", lambda s: " | ".join(sorted(set(s)))),
             omics=("omics_type", lambda s: " | ".join(sorted(set(s)))))
        .reset_index()
        .sort_values("n_experiments", ascending=False)
    )
    pubs.to_csv(DATA / "publications.csv", index=False)
    print(f"\n[out] wrote {len(pubs)} publications -> data/publications.csv")

    # table_scope fairness note: experiments that kept all detected genes let us
    # tell "tested but flat" apart from "not reported"; significant_only cannot.
    fair = exp[exp["table_scope"] == "all_detected_genes"]
    print(f"\n[fairness] experiments with table_scope=all_detected_genes "
          f"(usable for tested-vs-flat denominator): {len(fair)} / {len(exp)}")


if __name__ == "__main__":
    main()
