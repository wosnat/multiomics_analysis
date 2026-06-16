"""Step 4 — worked example of the response metric on driving OG cyanorak:CK_00000958.

Pipeline (the same shape step 5 will run over all 245 candidates, here for one OG):
  1. member loci of the OG (genes_by_homolog_group, Prochlorococcus-scoped)
  2. per-gene DE over the 74 pooled experiments, batched per strain
     (differential_expression_by_gene is single-organism), significant_only=False
     so tested-but-flat rows are kept where the table_scope provides them
  3. attach og_id, aggregate with og_response_metric.aggregate_og_metrics
  4. print the per-OG metric + the per-datapoint significant rows behind it

Output: data/worked_example_CK_00000958.csv          (per-datapoint DE rows)
        data/worked_example_CK_00000958_metric.csv    (the one aggregated row)
        data/01_worked_example.log (stdout tee)

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/4_methods/scripts/01_worked_example.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from multiomics_explorer import (genes_by_homolog_group,
                                 differential_expression_by_gene)

STEP = Path(__file__).resolve().parents[1]
ROOT = STEP.parent
sys.path.insert(0, str(STEP))
from og_response_metric import aggregate_og_metrics  # noqa: E402

DATA = STEP / "data"
DATA.mkdir(parents=True, exist_ok=True)

OG = "cyanorak:CK_00000958"
POOLED = pd.read_csv(ROOT / "3_analysis_framing" / "data" / "pooled_experiments.csv")
POOLED_IDS = POOLED["experiment_id"].tolist()
DE_COLS = ["locus_tag", "gene_name", "experiment_id", "treatment_type",
           "timepoint", "log2fc", "rank_up", "rank_down", "expression_status"]


def main() -> None:
    members = genes_by_homolog_group(group_ids=[OG], organisms=["Prochlorococcus"],
                                     limit=None)
    mdf = pd.DataFrame(members["results"])
    print(f"[members] {OG}: {len(mdf)} Prochlorococcus member genes across "
          f"{mdf['organism_name'].nunique()} strains")

    # Batch per strain (differential_expression_by_gene is single-organism, and
    # experiment_ids must belong to that organism).
    frames = []
    for org, sub in mdf.groupby("organism_name"):
        loci = sub["locus_tag"].tolist()
        org_exps = POOLED.loc[POOLED["organism_name"] == org, "experiment_id"].tolist()
        if not org_exps:
            continue  # strain has members but no pooled gene-DE experiments
        r = differential_expression_by_gene(organism=org, locus_tags=loci,
                                            experiment_ids=org_exps,
                                            significant_only=False, limit=None)
        if r["results"]:
            f = pd.DataFrame(r["results"])
            f["organism_name"] = org
            frames.append(f)
    if not frames:
        print("[warn] no DE rows for this OG in the pooled experiments")
        return
    de = pd.concat(frames, ignore_index=True)
    de["og_id"] = OG
    # ensure the rank columns exist (older rows may omit one direction)
    for c in ("rank_up", "rank_down"):
        if c not in de.columns:
            de[c] = None
    de.to_csv(DATA / "worked_example_CK_00000958.csv", index=False)
    print(f"[de] {len(de)} tested datapoints "
          f"({int(de['expression_status'].isin(['significant_up','significant_down']).sum())} significant)")

    metric = aggregate_og_metrics(de)
    metric.to_csv(DATA / "worked_example_CK_00000958_metric.csv", index=False)

    print("\n[metric] aggregated row for the driving OG:")
    m = metric.iloc[0].to_dict()
    for k, v in m.items():
        print(f"  {k:<26} {v}")

    print("\n[significant datapoints behind it]")
    sig = de[de["expression_status"].isin(["significant_up", "significant_down"])]
    show = sig[["organism_name"] + DE_COLS].copy()
    show["treatment_type"] = show["treatment_type"].apply(
        lambda t: t[0] if isinstance(t, list) and t else t)
    show["organism_name"] = show["organism_name"].str.replace(
        "Prochlorococcus ", "", regex=False)
    with pd.option_context("display.width", 180, "display.max_rows", None,
                           "display.max_columns", None):
        print(show.sort_values(["treatment_type", "log2fc"]).to_string(index=False))


if __name__ == "__main__":
    main()
