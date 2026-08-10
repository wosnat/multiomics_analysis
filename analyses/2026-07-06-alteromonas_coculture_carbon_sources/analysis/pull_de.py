"""Analysis milestone, step 1: pull the per-gene DE for the primary experiment
(HOT1A3 + MED4 coculture-vs-axenic, day 11) and cache it. all_detected_genes,
so tested-absent (`not_significant`) rows are kept -- they carry a real log2fc
and belong in the genome-wide ranking. Sign distribution is reported as a
data-integrity check (a genuine all-genes log2fc table is ~40-55% negative).

Run from repo root: uv run analyses/.../analysis/pull_de.py
"""
import json
import os
from collections import Counter
from multiomics_explorer import differential_expression_by_gene

EXP = "10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq"
ORG = "Alteromonas macleodii HOT1A3"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)


def main():
    r = differential_expression_by_gene(
        organism=ORG, experiment_ids=[EXP], limit=None, verbose=True)
    rows = r["results"]
    print("total_matching:", r["total_matching"], "returned:", len(rows))
    print("by_table_scope:", r.get("by_table_scope"))
    print("rows_by_status:", r.get("rows_by_status"))

    # one row per gene expected (single timepoint). Check for duplicates.
    per_gene = {}
    dup = 0
    for row in rows:
        lt = row["locus_tag"]
        if lt in per_gene:
            dup += 1
        per_gene.setdefault(lt, []).append(row)
    print("distinct genes:", len(per_gene), "duplicate rows:", dup)

    # de_table: locus_tag -> log2fc (single row each)
    de = {}
    meta = {}
    for lt, rws in per_gene.items():
        row = rws[0]
        de[lt] = row["log2fc"]
        meta[lt] = {"gene_name": row.get("gene_name"),
                    "product": row.get("product"),
                    "gene_category": row.get("gene_category"),
                    "log2fc": row["log2fc"], "padj": row.get("padj"),
                    "expression_status": row.get("expression_status")}

    # sign distribution over ALL genes (data-integrity check)
    n = len(de)
    neg = sum(1 for v in de.values() if v < 0)
    pos = sum(1 for v in de.values() if v > 0)
    zero = sum(1 for v in de.values() if v == 0)
    status = Counter(m["expression_status"] for m in meta.values())
    print(f"\nSIGN DISTRIBUTION (all {n} genes): "
          f"negative={neg} ({100*neg/n:.1f}%), positive={pos} ({100*pos/n:.1f}%), "
          f"zero={zero}")
    print("expression_status:", dict(status))

    json.dump(de, open(os.path.join(CACHE, "de_table.json"), "w"), indent=0)
    json.dump(meta, open(os.path.join(CACHE, "de_meta.json"), "w"), indent=1,
              default=str)
    json.dump({"experiment_id": EXP, "organism": ORG,
               "total_matching": r["total_matching"], "distinct_genes": n,
               "table_scope": r.get("by_table_scope"),
               "rows_by_status": r.get("rows_by_status"),
               "sign_negative": neg, "sign_positive": pos, "sign_zero": zero,
               "pct_negative": round(100*neg/n, 2),
               "duplicate_rows": dup},
              open(os.path.join(CACHE, "de_pull_log.json"), "w"), indent=1)
    print("\ncached de_table.json, de_meta.json, de_pull_log.json")


if __name__ == "__main__":
    main()
