"""Step 5 follow-on: profile the EZ55 secreted (exoproteome) proteins.

Two questions (researcher, step-5 decide):
  1. Gene-category distribution of the secreted proteins.
  2. Cross-route corroboration: which EZ55-secreted ortholog groups are ALSO found
     in the OTHER strains' vesicle cargo? (secreted is EZ55-only, so this is the
     strongest available cross-strain check.) Broken down by gene category to test
     the abundance-driven-contamination reading.

Inputs (frozen, this step): ../data/extruded_genes_all.csv, ../data/extruded_og_catalogue.csv
Plus one KG call for gene_category on the EZ55 secreted set.

Outputs (../data/):
  secreted_category_distribution.csv
  secreted_og_corroboration.csv
Figure (../figures/):
  secreted_profile.png  (category distribution + corroborated-vs-secreted-only by category)

Run: uv run python analyses/2026-06-17-alteromonas_extruded_proteome/5_analyze/scripts/02_secreted_profile.py
"""

from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from multiomics_explorer import genes_by_numeric_metric

DATA = Path(__file__).resolve().parents[1] / "data"
FIG = Path(__file__).resolve().parents[1] / "figures"


def main() -> None:
    genes_all = pd.read_csv(DATA / "extruded_genes_all.csv")
    cat = pd.read_csv(DATA / "extruded_og_catalogue.csv")

    # EZ55 secreted genes (with their OG) from the frozen step-5 table.
    sec = genes_all[genes_all["route"] == "secreted"].copy()
    print(f"[secreted] EZ55 secreted genes (detection >= 1): {len(sec)}")

    # Pull gene_category for the secreted set (one KG call).
    res = genes_by_numeric_metric(
        metric_types=["exoproteome_detection_replicates"],
        organism="EZ55", compartment="exoproteome", min_value=1.0, limit=None,
    )
    gcat = pd.DataFrame(
        [{"locus_tag": r["locus_tag"], "gene_category": r["gene_category"],
          "replicates": r["value"]} for r in res["results"]]
    )
    sec = sec.merge(gcat, on="locus_tag", how="left")

    # --- 1. category distribution ---
    dist = (sec["gene_category"].value_counts().rename_axis("gene_category")
            .reset_index(name="n_genes"))
    dist["pct"] = (100 * dist["n_genes"] / len(sec)).round(1)
    print("\n[category distribution] secreted proteins")
    print(dist.to_string(index=False))

    # --- 2. cross-route corroboration at OG level ---
    # An EZ55-secreted OG is corroborated if its catalogue 'routes' includes vesicle
    # (vesicle can only come from another strain — EZ55 has no vesicle data).
    route_map = dict(zip(cat["og_group_id"], cat["routes"]))
    strain_map = dict(zip(cat["og_group_id"], cat["strains"]))
    nstrain_map = dict(zip(cat["og_group_id"], cat["n_strains"]))
    sec["routes"] = sec["og_group_id"].map(route_map)
    sec["corroborated"] = sec["routes"].fillna("").str.contains("vesicle")
    sec["og_strains"] = sec["og_group_id"].map(strain_map)
    sec["og_n_strains"] = sec["og_group_id"].map(nstrain_map)

    # Collapse to OG level for the corroboration count (paralogs share an OG).
    og_level = (sec.dropna(subset=["og_group_id"])
                .groupby("og_group_id")
                .agg(gene_category=("gene_category", "first"),
                     corroborated=("corroborated", "first"),
                     og_n_strains=("og_n_strains", "first"),
                     og_strains=("og_strains", "first"),
                     locus_tags=("locus_tag", lambda s: ";".join(sorted(s))))
                .reset_index())
    n_og = len(og_level)
    n_corr = int(og_level["corroborated"].sum())
    print(f"\n[corroboration] distinct EZ55-secreted OGs: {n_og}")
    print(f"[corroboration] also in another strain's vesicle cargo: {n_corr} "
          f"({100*n_corr/n_og:.0f}%); secreted-only: {n_og - n_corr}")

    # corroboration rate by category
    by_cat = (og_level.groupby("gene_category")
              .agg(n_og=("og_group_id", "size"),
                   n_corroborated=("corroborated", "sum"))
              .reset_index().sort_values("n_og", ascending=False))
    by_cat["pct_corroborated"] = (100 * by_cat["n_corroborated"] / by_cat["n_og"]).round(0)
    print("\n[corroboration by category] (OG level)")
    print(by_cat.to_string(index=False))

    # --- figure ---
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    d = dist.sort_values("n_genes")
    ax[0].barh(d["gene_category"], d["n_genes"], color="#d8743b")
    ax[0].set_xlabel("secreted proteins (genes)")
    ax[0].set_title(f"EZ55 secreted: gene-category distribution (n={len(sec)})")
    b = by_cat.sort_values("n_og").set_index("gene_category")
    ax[1].barh(b.index, b["n_og"], color="#cccccc", label="secreted-only")
    ax[1].barh(b.index, b["n_corroborated"], color="#3b7dd8",
               label="also in vesicle (other strain)")
    ax[1].set_xlabel("EZ55-secreted ortholog groups")
    ax[1].set_title("Cross-route corroboration by category")
    ax[1].legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "secreted_profile.png", dpi=300)
    print("\n[written] figures/secreted_profile.png")

    dist.to_csv(DATA / "secreted_category_distribution.csv", index=False)
    og_level.sort_values(["corroborated", "og_n_strains"], ascending=False).to_csv(
        DATA / "secreted_og_corroboration.csv", index=False)
    print(f"[written] data/secreted_category_distribution.csv, data/secreted_og_corroboration.csv")


if __name__ == "__main__":
    main()
