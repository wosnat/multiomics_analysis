"""Step 5 follow-on: profile the vesicle (MV-cargo) proteins across the 6 strains.

Two questions (researcher, step-5 decide), parallel to the secreted profile:
  1. Gene-category distribution of vesicle cargo.
  2. Agreement between strains — DIRECT here (6 strains have MV data): at OG level,
     in how many strains does each vesicle OG appear (recurrence), what is the core
     shared cargo, and how similar are the strains pairwise (Jaccard on OG sets)?

Inputs (frozen, this step): ../data/extruded_genes_all.csv, ../data/extruded_og_catalogue.csv
Plus one KG call for gene_category on the vesicle set.

Outputs (../data/):
  vesicle_category_distribution.csv
  vesicle_og_strain_recurrence.csv
Figure (../figures/):
  vesicle_profile.png  (category distribution + OG strain-recurrence + pairwise Jaccard)

Run: uv run python analyses/2026-06-17-alteromonas_extruded_proteome/5_analyze/scripts/03_vesicle_profile.py
"""

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from multiomics_explorer import genes_by_numeric_metric

DATA = Path(__file__).resolve().parents[1] / "data"
FIG = Path(__file__).resolve().parents[1] / "figures"


def _short(s: str) -> str:
    return s.replace("Alteromonas macleodii ", "")


def main() -> None:
    genes_all = pd.read_csv(DATA / "extruded_genes_all.csv")
    cat = pd.read_csv(DATA / "extruded_og_catalogue.csv")
    prod_map = dict(zip(cat["og_group_id"], cat["og_product"]))

    ves = genes_all[genes_all["route"] == "vesicle"].copy()
    ves["strain_short"] = ves["strain"].map(_short)
    strains = sorted(ves["strain_short"].unique())
    print(f"[vesicle] MV-cargo gene rows: {len(ves)} across {len(strains)} strains: {strains}")

    # gene_category for the vesicle set (one KG call, all strains).
    res = genes_by_numeric_metric(
        metric_types=["prop_abund_mvs_percent"], compartment="vesicle", limit=None,
    )
    gcat = pd.DataFrame(
        [{"locus_tag": r["locus_tag"], "gene_category": r["gene_category"]}
         for r in res["results"]]
    )
    ves = ves.merge(gcat, on="locus_tag", how="left")

    # --- 1. category distribution (genes) ---
    dist = (ves["gene_category"].value_counts().rename_axis("gene_category")
            .reset_index(name="n_genes"))
    dist["pct"] = (100 * dist["n_genes"] / len(ves)).round(1)
    print("\n[category distribution] vesicle cargo (genes)")
    print(dist.to_string(index=False))

    # --- 2a. OG strain-recurrence (vesicle strains only) ---
    og = ves.dropna(subset=["og_group_id"]).copy()
    rec = (og.groupby("og_group_id")
           .agg(n_strains=("strain_short", "nunique"),
                strains=("strain_short", lambda s: ";".join(sorted(set(s)))),
                gene_category=("gene_category", "first"))
           .reset_index())
    rec["og_product"] = rec["og_group_id"].map(prod_map)
    n_og = len(rec)
    print(f"\n[agreement] distinct vesicle OGs: {n_og}")
    print("[agreement] OG strain-recurrence (how many of 6 strains share an OG):")
    print(rec["n_strains"].value_counts().sort_index().to_string())
    shared = rec[rec["n_strains"] >= 2]
    print(f"[agreement] shared by >=2 strains: {len(shared)} ({100*len(shared)/n_og:.0f}%); "
          f"strain-unique: {n_og - len(shared)}")

    core = rec[rec["n_strains"] >= 4].sort_values("n_strains", ascending=False)
    print(f"\n[core MV cargo] OGs in >=4 of 6 strains: {len(core)}")
    print(core[["og_group_id", "n_strains", "og_product", "gene_category"]].to_string(index=False))

    # --- 2b. pairwise Jaccard on OG sets ---
    og_sets = {s: set(og[og["strain_short"] == s]["og_group_id"]) for s in strains}
    J = np.eye(len(strains))
    for i, a in enumerate(strains):
        for j, b in enumerate(strains):
            if i < j:
                inter = len(og_sets[a] & og_sets[b])
                union = len(og_sets[a] | og_sets[b])
                J[i, j] = J[j, i] = inter / union if union else 0.0
    jac = pd.DataFrame(J, index=strains, columns=strains).round(3)
    print("\n[agreement] pairwise Jaccard on vesicle OG sets:")
    print(jac.to_string())
    offdiag = J[np.triu_indices(len(strains), k=1)]
    print(f"[agreement] mean pairwise Jaccard: {offdiag.mean():.3f} "
          f"(min {offdiag.min():.3f}, max {offdiag.max():.3f})")

    # --- figure ---
    fig, ax = plt.subplots(1, 3, figsize=(16, 5))
    d = dist.sort_values("n_genes")
    ax[0].barh(d["gene_category"], d["n_genes"], color="#3bd87d")
    ax[0].set_xlabel("vesicle cargo (genes)")
    ax[0].set_title(f"Vesicle: gene-category distribution (n={len(ves)})")

    rr = rec["n_strains"].value_counts().sort_index()
    ax[1].bar(rr.index.astype(str), rr.values, color="#3b7dd8")
    ax[1].set_xlabel("strains sharing the OG (of 6)")
    ax[1].set_ylabel("vesicle OGs")
    ax[1].set_title("MV-cargo OG strain-recurrence")

    im = ax[2].imshow(J, vmin=0, vmax=max(0.2, offdiag.max()), cmap="viridis")
    ax[2].set_xticks(range(len(strains))); ax[2].set_xticklabels(strains, rotation=45, ha="right")
    ax[2].set_yticks(range(len(strains))); ax[2].set_yticklabels(strains)
    ax[2].set_title("Pairwise Jaccard (vesicle OG sets)")
    for i in range(len(strains)):
        for j in range(len(strains)):
            ax[2].text(j, i, f"{J[i, j]:.2f}", ha="center", va="center",
                       color="white" if J[i, j] < 0.15 else "black", fontsize=7)
    fig.colorbar(im, ax=ax[2], fraction=0.046)
    fig.tight_layout()
    fig.savefig(FIG / "vesicle_profile.png", dpi=300)
    print("\n[written] figures/vesicle_profile.png")

    dist.to_csv(DATA / "vesicle_category_distribution.csv", index=False)
    rec.sort_values("n_strains", ascending=False).to_csv(
        DATA / "vesicle_og_strain_recurrence.csv", index=False)
    print("[written] data/vesicle_category_distribution.csv, data/vesicle_og_strain_recurrence.csv")


if __name__ == "__main__":
    main()
