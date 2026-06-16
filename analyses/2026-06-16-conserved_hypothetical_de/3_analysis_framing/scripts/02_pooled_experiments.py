"""Step 3 — define the gene-DE stress-response experiment set to pool for breadth.

From the step-2 experiment universe (91), keep the experiments that yield
gene-level differential expression under a perturbation:
  - omics in {RNASEQ, MICROARRAY, PROTEOMICS, PAIRED_RNASEQ_PROTEOME}
    (drops METABOLOMICS = metabolite-anchored, and DNASEQ)
  - drop treatment_type 'compartment' (vesicle/exoproteome partitioning, not a
    stress response)

The distinct treatment_types in the kept set are the breadth axis: the maximum
number of conditions a family can respond to.

Input:   ../2_kg_selection/data/de_experiments.csv  (step 2)
Output:  data/pooled_experiments.csv  — kept experiments + treatment_type
         data/treatment_type_inventory.csv — per treatment_type: n experiments,
                                              table_scope mix
         data/02_pooled_experiments.log (stdout tee)

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/3_analysis_framing/scripts/02_pooled_experiments.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "2_kg_selection" / "data" / "de_experiments.csv"
DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)

GENE_DE_OMICS = {"RNASEQ", "MICROARRAY", "PROTEOMICS", "PAIRED_RNASEQ_PROTEOME"}
DROP_TREATMENTS = {"compartment"}


def explode_treatments(s: str) -> list[str]:
    """treatment_type may be a '|'-joined list (to_dataframe joins list cols)."""
    if pd.isna(s):
        return []
    return [t.strip() for t in str(s).split("|") if t.strip()]


def main() -> None:
    df = pd.read_csv(EXP)
    print(f"[in] {len(df)} Prochlorococcus DE experiments")

    kept = df[df["omics_type"].isin(GENE_DE_OMICS)].copy()
    print(f"[filter] gene-DE omics {sorted(GENE_DE_OMICS)}: {len(kept)}")

    # treatment_type may be a '|'-joined list; explode for the inventory.
    kept["treatments"] = kept["treatment_type"].apply(explode_treatments)
    # drop experiments whose ONLY treatment is a dropped one (e.g. compartment)
    kept["treatments_kept"] = kept["treatments"].apply(
        lambda ts: [t for t in ts if t not in DROP_TREATMENTS])
    kept = kept[kept["treatments_kept"].map(len) > 0].copy()
    print(f"[filter] after dropping {DROP_TREATMENTS}-only experiments: {len(kept)}")

    kept_out = kept[["experiment_id", "organism_name", "treatment_type",
                     "omics_type", "table_scope", "is_time_course",
                     "publication_doi"]].copy()
    kept_out.to_csv(DATA / "pooled_experiments.csv", index=False)
    print(f"[out] pooled_experiments.csv: {len(kept_out)} experiments")

    # treatment_type inventory (breadth axis)
    rows = []
    for t in sorted({t for ts in kept["treatments_kept"] for t in ts}):
        sub = kept[kept["treatments_kept"].apply(lambda ts: t in ts)]
        rows.append({
            "treatment_type": t,
            "n_experiments": len(sub),
            "n_all_detected": (sub["table_scope"] == "all_detected_genes").sum(),
            "strains": " | ".join(sorted(sub["organism_name"].str.replace(
                "Prochlorococcus ", "", regex=False).unique())),
        })
    inv = pd.DataFrame(rows).sort_values("n_experiments", ascending=False)
    inv.to_csv(DATA / "treatment_type_inventory.csv", index=False)

    print(f"\n[breadth axis] {len(inv)} distinct treatment types in the pooled set:")
    for _, r in inv.iterrows():
        print(f"  {r['treatment_type']:<14} exp={r['n_experiments']:>2} "
              f"(all_detected={r['n_all_detected']:>2})  strains: {r['strains']}")
    print(f"\n[max possible breadth] = {len(inv)} treatment types")


if __name__ == "__main__":
    main()
