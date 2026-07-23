#!/usr/bin/env python3
"""
Methods follow-up -- Task 1.

Augment the anchor genes (data/anchor_neighbors.csv) with the rich, ~100%-populated
Gene fields (gene_summary, alternate_functional_descriptions) and a Pfam-based
component role. Writes data/anchor_neighbors_v2.csv (v1 untouched).

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/03_anchor_annotate_pfam.py
"""
import os
import pandas as pd
from multiomics_explorer import gene_details, GraphConnection
from pfam_roles import pfam_domains, role_from_pfam

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
V1 = os.path.join(DATA, "anchor_neighbors.csv")
V2 = os.path.join(DATA, "anchor_neighbors_v2.csv")


def main():
    v1 = pd.read_csv(V1)
    locus = v1["locus_tag"].tolist()

    with GraphConnection() as conn:
        det = gene_details(locus_tags=locus, limit=None, conn=conn)
    dmap = {r["locus_tag"]: r for r in det.get("results", [])}

    rows = []
    for lt in locus:
        d = dmap.get(lt, {})
        alt = d.get("alternate_functional_descriptions") or []
        pf = pfam_domains(alt)
        rows.append({
            "locus_tag": lt,
            "gene_summary": d.get("gene_summary"),
            "alternate_functional_descriptions": " || ".join(alt),
            "pfam_domains": " ; ".join(pf),
            "role_from_pfam": role_from_pfam(pf),
        })
    add = pd.DataFrame(rows)

    v2 = v1.merge(add, on="locus_tag", how="left")
    # column order: keep v1 cols, then the new rich ones
    new_cols = ["gene_summary", "alternate_functional_descriptions", "pfam_domains", "role_from_pfam"]
    v2 = v2[[c for c in v1.columns] + new_cols]
    v2.to_csv(V2, index=False)
    print(f"wrote {len(v2)} rows -> {V2}")

    # compact echo: role_first_pass vs role_from_pfam where they differ or resolve
    print("\n=== Pfam role resolution (where v1 was unclear/other, or role changed) ===")
    for _, r in v2.sort_values(["anchor", "start"]).iterrows():
        changed = (r["role_first_pass"] != r["role_from_pfam"])
        if changed or r["role_first_pass"] in ("unclear", "other"):
            print(f"  {r['locus_tag']:14s} {str(r['role_first_pass']):16s} -> "
                  f"{str(r['role_from_pfam']):22s} pfam=[{r['pfam_domains']}]")
    print("\n=== stays other/unclear even with Pfam ===")
    for _, r in v2.iterrows():
        if r["role_from_pfam"] in ("other/unclear",):
            print(f"  {r['locus_tag']:14s} pfam=[{r['pfam_domains']}] | {r['product']}")


if __name__ == "__main__":
    main()
