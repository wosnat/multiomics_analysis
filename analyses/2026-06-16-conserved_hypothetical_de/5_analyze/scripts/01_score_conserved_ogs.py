"""Step 5 — score ALL conserved cyanorak families (the backdrop), tag category.

To judge whether our conserved HYPOTHETICAL families are unusually responsive, we
score the whole conserved set (>=9/17 strains) and compare. Our 245 hypotheticals are
flagged `is_hypothetical`; the other 1,465 characterized conserved families are the
comparison backdrop, coloured by gene_category in the figures.

Significant-response pass: we pull `significant_only=True` (breadth, prominence, and
direction all come from significant rows). The tested-denominator (% datapoints DE) is
NOT computed here — it needs a full table and is heavily table_scope-caveated; left to
a targeted pass if ever needed. n_tested_datapoints / pct_datapoints_de are nulled.

Pipeline:
  1. conserved set (>=9/17) from the step-2 landscape, tier + is_hypothetical
  2. member loci + gene_category (genes_by_homolog_group, one call)
  3. per-gene significant DE over pooled experiments, batched per strain
  4. aggregate (og_response_metric), join metadata + dominant gene_category

Output: data/conserved_og_scores.csv   — one row per conserved family (scored)
        data/de_long_significant.csv    — significant DE rows behind it (gitignored)
        data/01_score_conserved_ogs.log

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/5_analyze/scripts/01_score_conserved_ogs.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from multiomics_explorer import (genes_by_homolog_group,
                                 differential_expression_by_gene)

STEP = Path(__file__).resolve().parents[1]
ROOT = STEP.parent
sys.path.insert(0, str(ROOT / "4_methods"))
from og_response_metric import aggregate_og_metrics  # noqa: E402

DATA = STEP / "data"
DATA.mkdir(parents=True, exist_ok=True)

LANDSCAPE = pd.read_csv(ROOT / "2_kg_selection" / "data" / "og_conservation_landscape.csv")
POOLED = pd.read_csv(ROOT / "3_analysis_framing" / "data" / "pooled_experiments.csv")
CONSERVED_MIN, CORE_MIN, HYPO_FRAC = 9, 14, 0.80


def main() -> None:
    cons = LANDSCAPE[LANDSCAPE["proc_strains"] >= CONSERVED_MIN].copy()
    cons["tier"] = cons["proc_strains"].apply(lambda s: "core" if s >= CORE_MIN else "broad")
    cons["is_hypothetical"] = cons["frac_hypo"] >= HYPO_FRAC
    og_ids = cons["og_id"].tolist()
    print(f"[conserved set] {len(cons)} OGs (>= {CONSERVED_MIN}/17 strains); "
          f"{int(cons['is_hypothetical'].sum())} hypothetical, "
          f"{int((~cons['is_hypothetical']).sum())} characterized")

    # 1. members + gene_category (one call)
    mem = pd.DataFrame(
        genes_by_homolog_group(group_ids=og_ids, organisms=["Prochlorococcus"],
                               limit=None)["results"])
    locus2og = dict(zip(mem["locus_tag"], mem["group_id"]))
    # dominant gene_category per OG (characterized -> functional class; hypo -> Unknown)
    dom_cat = (mem.groupby("group_id")["gene_category"]
               .agg(lambda s: s.value_counts().idxmax())
               .rename_axis("og_id").reset_index(name="dominant_category"))
    print(f"[members] {len(mem)} member genes across {mem['organism_name'].nunique()} strains")

    # 2. significant DE per strain
    frames = []
    for org, sub in mem.groupby("organism_name"):
        org_exps = POOLED.loc[POOLED["organism_name"] == org, "experiment_id"].tolist()
        if not org_exps:
            continue
        r = differential_expression_by_gene(organism=org,
                                            locus_tags=sub["locus_tag"].tolist(),
                                            experiment_ids=org_exps,
                                            significant_only=True, limit=None)
        if r["results"]:
            frames.append(pd.DataFrame(r["results"]))
        print(f"  {org.replace('Prochlorococcus ',''):<34} sig_rows="
              f"{len(r['results']) if r['results'] else 0}")
    de = pd.concat(frames, ignore_index=True)
    de["og_id"] = de["locus_tag"].map(locus2og)
    for c in ("rank_up", "rank_down"):
        if c not in de.columns:
            de[c] = None
    de.to_csv(DATA / "de_long_significant.csv", index=False)
    print(f"[de] {len(de)} significant datapoints over {de['og_id'].nunique()} OGs")

    # 3. aggregate; null the tested-denominator fields (sig-only input)
    metric = aggregate_og_metrics(de)
    metric["n_tested_datapoints"] = pd.NA
    metric["pct_datapoints_de"] = pd.NA

    out = cons.merge(metric, on="og_id", how="left").merge(
        dom_cat, on="og_id", how="left")
    out["breadth"] = out["breadth"].fillna(0).astype(int)
    out["n_significant_datapoints"] = out["n_significant_datapoints"].fillna(0).astype(int)
    out["responded"] = out["n_significant_datapoints"] > 0
    out = out.sort_values(["is_hypothetical", "breadth", "n_significant_datapoints"],
                          ascending=False).reset_index(drop=True)
    out.to_csv(DATA / "conserved_og_scores.csv", index=False)

    # summary: hypothetical vs characterized breadth
    print(f"\n[coverage] {int(out['responded'].sum())}/{len(out)} conserved families "
          f"have >=1 significant response")
    g = out.groupby("is_hypothetical")["breadth"]
    print("\n[breadth: hypothetical vs characterized]")
    print(f"  {'group':<14}{'n':>5}{'mean':>7}{'median':>8}{'>=6 (broad)':>13}")
    for is_h, lbl in [(True, "hypothetical"), (False, "characterized")]:
        sub = out[out["is_hypothetical"] == is_h]["breadth"]
        print(f"  {lbl:<14}{len(sub):>5}{sub.mean():>7.2f}{sub.median():>8.0f}"
              f"{int((sub>=6).sum()):>13}")


if __name__ == "__main__":
    main()
