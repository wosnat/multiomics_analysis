"""Step 5: build the combined Alteromonas extruded-OG catalogue across all 7 routes.

secreted: EZ55 (exoproteome_detection_replicates >= 1)
vesicle : MIT1002, BS11, ATCC27126, BGP6, AD45, HOT1A3 (MV-cargo membership)

Outputs (../data/):
  extruded_genes_all.csv   gene-level: locus_tag, strain, route, product, value, og_*
  extruded_og_catalogue.csv  one row per OG: routes, both_routes, n_strains, recurrence
Figure (../figures/):
  og_recurrence.png        recurrence distribution + both-routes count

Run: uv run python analyses/2026-06-17-alteromonas_extruded_proteome/5_analyze/scripts/01_build_catalogue.py
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "4_methods"))
from extruded_og import extract_route_genes, map_genes_to_og, build_og_catalogue  # noqa: E402

from multiomics_explorer import GraphConnection  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
FIG = Path(__file__).resolve().parents[1] / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

VESICLE_STRAINS = ["MIT1002", "BS11", "ATCC27126", "BGP6", "AD45", "HOT1A3"]
SECRETED_STRAINS = ["EZ55"]


def main() -> None:
    frames = []
    with GraphConnection() as conn:
        # --- secreted path (the step-4 watch-item) ---
        for strain in SECRETED_STRAINS:
            g = extract_route_genes(strain, "secreted", conn=conn)
            print(f"[secreted] {strain}: {len(g)} genes with detection >= 1 "
                  f"(of 234 tested-absent rows)")
            frames.append(g)
        # --- vesicle path ---
        for strain in VESICLE_STRAINS:
            g = extract_route_genes(strain, "vesicle", conn=conn)
            print(f"[vesicle]  {strain}: {len(g)} MV-cargo genes")
            frames.append(g)

        genes = pd.concat(frames, ignore_index=True)
        print(f"\n[combined] extruded gene rows: {len(genes)}")

        og = map_genes_to_og(genes["locus_tag"].tolist(), conn=conn)

    merged = genes.merge(og, on="locus_tag", how="left")
    n_no_og = merged["og_group_id"].isna().sum()
    print(f"[combined] mapped to eggnog OG: {len(merged) - n_no_og}; "
          f"strain-unique (no OG): {n_no_og}")

    cat = build_og_catalogue(merged)
    print(f"[combined] distinct extruded OGs: {len(cat)}")

    # --- recurrence / route structure ---
    both = cat[cat["both_routes"]]
    multi = cat[cat["n_strains"] >= 2]
    print(f"[structure] OGs extruded by BOTH routes: {len(both)}")
    print(f"[structure] OGs recurrent in >=2 strains: {len(multi)}")
    print(f"[structure] recurrence (n_strains) counts:")
    print(cat["n_strains"].value_counts().sort_index().to_string())

    # Positive control across strains: TonB OGs and their recurrence.
    tonb = cat[cat["og_product"].str.contains("TonB", case=False, na=False)]
    print(f"\n[positive control] TonB-dependent receptor OGs: {len(tonb)}")
    print(tonb[["og_group_id", "n_strains", "strains", "routes"]].to_string(index=False))

    print("\n[both-routes OGs]")
    if len(both):
        print(both[["og_group_id", "og_product", "n_strains", "strains"]].to_string(index=False))
    else:
        print("  none")

    # --- figure ---
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    rec = cat["n_strains"].value_counts().sort_index()
    ax[0].bar(rec.index.astype(str), rec.values, color="#3b7dd8")
    ax[0].set_xlabel("strains sharing the OG (recurrence)")
    ax[0].set_ylabel("number of extruded OGs")
    ax[0].set_title("Extruded-OG recurrence across strains")
    route_counts = cat["routes"].value_counts()
    ax[1].bar(route_counts.index, route_counts.values,
              color=["#d8743b", "#3bd87d", "#7d3bd8"][: len(route_counts)])
    ax[1].set_xlabel("route(s)")
    ax[1].set_ylabel("number of extruded OGs")
    ax[1].set_title("Extruded OGs by route")
    fig.tight_layout()
    fig.savefig(FIG / "og_recurrence.png", dpi=300)
    print(f"\n[written] figures/og_recurrence.png")

    merged.to_csv(DATA / "extruded_genes_all.csv", index=False)
    cat.to_csv(DATA / "extruded_og_catalogue.csv", index=False)
    print(f"[written] data/extruded_genes_all.csv ({len(merged)} genes), "
          f"data/extruded_og_catalogue.csv ({len(cat)} OGs)")


if __name__ == "__main__":
    main()
