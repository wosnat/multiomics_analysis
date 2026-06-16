"""Step 4 QC — cross-check the metric module against the step-3 controls.

Step 3 validated controls with gene_response_profile (a different tool). Here we run
the NEW aggregation path (differential_expression_by_gene -> aggregate_og_metrics)
on the same control genes (each treated as a singleton "OG") and confirm breadth and
max|log2FC| agree. Two independent code paths landing on the same numbers is the
check.

Scope note: this QC restricts to MED4 pooled experiments (the controls are MED4
genes); step-3's gene_response_profile was also MED4-scoped, so breadth should match
(any small diff is explainable by the pooled set excluding compartment contrasts).

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/4_methods/scripts/qc_controls_via_metric.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from multiomics_explorer import differential_expression_by_gene

STEP = Path(__file__).resolve().parents[1]
ROOT = STEP.parent
sys.path.insert(0, str(STEP))
from og_response_metric import aggregate_og_metrics  # noqa: E402

DATA = STEP / "data"
POOLED = pd.read_csv(ROOT / "3_analysis_framing" / "data" / "pooled_experiments.csv")
MED4_EXPS = POOLED.loc[POOLED["organism_name"] == "Prochlorococcus MED4",
                       "experiment_id"].tolist()
CONTROLS = {"PMM1385": "hli", "PMM0710": "pstS", "PMM1436": "groL1/groEL",
            "PMM0901": "htpG", "PMM1432": "dnaK1"}
EXPECT = pd.read_csv(ROOT / "3_analysis_framing" / "data" / "controls_validation.csv")


def main() -> None:
    frames = []
    for locus in CONTROLS:
        r = differential_expression_by_gene(organism="MED4", locus_tags=[locus],
                                            experiment_ids=MED4_EXPS,
                                            significant_only=False, limit=None)
        if r["results"]:
            f = pd.DataFrame(r["results"])
            f["og_id"] = locus  # singleton OG = the gene itself
            frames.append(f)
    de = pd.concat(frames, ignore_index=True)
    for c in ("rank_up", "rank_down"):
        if c not in de.columns:
            de[c] = None

    got = aggregate_og_metrics(de).rename(columns={"og_id": "locus_tag"})
    got["gene"] = got["locus_tag"].map(CONTROLS)
    cmp = got.merge(
        EXPECT[["locus_tag", "breadth_n_treatments", "max_abs_log2fc"]],
        on="locus_tag", how="left", suffixes=("_metric", "_step3"))

    cmp["breadth_match"] = cmp["breadth"] == cmp["breadth_n_treatments"]
    cmp["fc_match"] = (cmp["max_abs_log2fc_metric"].fillna(-1).round(2)
                       == cmp["max_abs_log2fc_step3"].fillna(-1).round(2))
    cols = ["gene", "locus_tag", "breadth", "breadth_n_treatments", "breadth_match",
            "max_abs_log2fc_metric", "max_abs_log2fc_step3", "fc_match",
            "best_rank", "direction"]
    print("[QC] new metric path vs step-3 gene_response_profile:\n")
    print(cmp[cols].to_string(index=False))
    print(f"\n[QC] breadth matches: {int(cmp['breadth_match'].sum())}/{len(cmp)}; "
          f"max|log2FC| matches: {int(cmp['fc_match'].sum())}/{len(cmp)}")
    cmp[cols].to_csv(DATA / "qc_controls_via_metric.csv", index=False)


if __name__ == "__main__":
    main()
