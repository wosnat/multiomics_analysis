"""Probe RefSeq-style MED4 locus tags (TX50_RS00005..TX50_RS10500, step 5) with gene_details to find
KG genes not reached by the coordinate sweep or the PMM-number probe. Output: raw/p4_med4_refseq_tag_probe.csv
Usage (repo root): .venv/Scripts/python.exe <this> --pilot-dir analyses/2026-10-06-pro_n_import_coculture/methods/data/pilot
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, gene_details, to_dataframe

ap = argparse.ArgumentParser(); ap.add_argument("--pilot-dir", required=True); a = ap.parse_args()
d = Path(a.pilot_dir)
tags = [f"TX50_RS{n:05d}" for n in range(5, 10505, 5)]
rows, offset, pages = [], 0, 0
with GraphConnection() as conn:
    while True:
        r = gene_details(locus_tags=tags, limit=200, offset=offset, conn=conn)
        pages += 1
        if pages == 1:
            total, nf = r["total_matching"], r.get("not_found") or []
        rows += r["results"]; offset += len(r["results"])
        if not r.get("truncated") or not r["results"]:
            break
assert len(rows) == total
df = to_dataframe({"results": rows}) if rows else pd.DataFrame()
gen = pd.read_csv(d / "raw" / "p3_med4_genome_coords.csv")
nocoord = pd.read_csv(d / "p3_med4_no_coordinate_genes.csv")
keep = [c for c in ["locus_tag", "organism_name", "gene_name", "product", "contig", "start", "end", "strand"] if c in df]
out = df[keep].copy() if len(df) else pd.DataFrame(columns=keep)
if len(out):
    out["in_genome_coord_table"] = out.locus_tag.isin(gen.locus_tag)
    out["in_no_coordinate_list"] = out.locus_tag.isin(nocoord.locus_tag)
    out["has_coordinates"] = out[["start", "end"]].notna().all(axis=1) if "start" in out else False
out.to_csv(d / "raw" / "p4_med4_refseq_tag_probe.csv", index=False)
print(json.dumps({"probed": len(tags), "found": int(len(out)), "not_found": len(nf), "pages": pages,
                  "organisms": out.organism_name.value_counts().to_dict() if len(out) else {},
                  "with_coords": int(out.has_coordinates.sum()) if len(out) else 0,
                  "in_genome_table": int(out.in_genome_coord_table.sum()) if len(out) else 0}, indent=1))
if len(out):
    print(out[~out.in_genome_coord_table].to_string())
