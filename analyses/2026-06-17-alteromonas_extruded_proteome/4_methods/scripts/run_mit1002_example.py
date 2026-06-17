"""Step 4 driving example: validate extruded_og on MIT1002 vesicle cargo.

Funnel: MV-cargo genes -> mapped to OGs -> OG catalogue.
Positive-control check: TonB-dependent receptors must survive into the catalogue.

Run: uv run python analyses/2026-06-17-alteromonas_extruded_proteome/4_methods/scripts/run_mit1002_example.py
Output: ../data/mit1002_og.csv
"""

import sys
from pathlib import Path

# Import the methods module (parent dir of this script's parent).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from extruded_og import extract_route_genes, map_genes_to_og, build_og_catalogue  # noqa: E402

from multiomics_explorer import GraphConnection  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "mit1002_og.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)


def main() -> None:
    with GraphConnection() as conn:
        genes = extract_route_genes("MIT1002", "vesicle", conn=conn)
        print(f"[funnel] MV-cargo genes (prop_abund_mvs_percent present): {len(genes)}")

        og = map_genes_to_og(genes["locus_tag"].tolist(), conn=conn)
        merged = genes.merge(og, on="locus_tag", how="left")
        n_no_og = merged["og_group_id"].isna().sum()
        print(f"[funnel] genes mapped to an eggnog OG: {len(merged) - n_no_og}")
        print(f"[funnel] strain-unique (no OG): {n_no_og}")

        cat = build_og_catalogue(merged)
        print(f"[funnel] distinct extruded OGs: {len(cat)}")

    # Positive control: TonB-dependent receptors present?
    tonb = merged[merged["product"].str.contains("TonB", case=False, na=False)]
    print(f"\n[positive control] TonB-dependent receptor genes in MV cargo: {len(tonb)}")
    for _, r in tonb.iterrows():
        print(f"    {r['locus_tag']}  {r['product']}  -> OG {r['og_group_id']} ({r['og_level']})")

    print("\n[top OGs by abundance-bearing gene count]")
    print(cat.head(8).to_string(index=False))

    merged.to_csv(OUT.with_name("mit1002_genes_og.csv"), index=False)
    cat.to_csv(OUT, index=False)
    print(f"\n[written] {OUT.name} ({len(cat)} OGs), mit1002_genes_og.csv ({len(merged)} genes)")


if __name__ == "__main__":
    main()
