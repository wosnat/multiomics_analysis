#!/usr/bin/env python3
"""
Methods milestone -- Task A + Task B.

Enumerate the transporter-gene "parts list" for BOTH Alteromonas strains as the
UNION of four annotation sources, and write a frozen CSV. Then compute compact QC
(Task B) including the aromatic/xenobiotic-importer subset.

The heavy result lives in DataFrames/CSV on disk -- only compact summaries print.

Sources (per strain):
  1. BRITE  -- transporters tree ko02000  (genes_by_ontology brite, tree=transporters)
  2. KEGG   -- KEGG KO whose KO *name* matches a transporter keyword regex
  3. TCDB   -- every TCDB-classified gene (TCDB *is* the transporter classification)
  4. ANNO   -- product / function_description keyword search (genes_by_function)

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/01_enumerate_transporters.py
"""
import os
import re
import pandas as pd

from multiomics_explorer import (
    genes_by_ontology,
    genes_by_function,
    gene_overview,
    gene_ontology_terms,
    GraphConnection,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(DATA, exist_ok=True)
OUT_TRANSPORTERS = os.path.join(DATA, "transporter_genes.csv")
OUT_AROMATIC = os.path.join(DATA, "qc_aromatic_importers.csv")

ORGANISMS = [
    "Alteromonas macleodii HOT1A3",
    "Alteromonas macleodii EZ55",
]

# ---- KEGG-KO-name transporter regex (matches the KO NAME string) ----
# Token-ish, case-insensitive. Captures transporter/permease/*porter*/channel/etc.
TRANSPORT_RE = re.compile(
    r"transport|permease|symport|antiport|uniport|porter\b|\bporter|"
    r"uptake|translocase|\bchannel|efflux|\bTonB|\bTRAP\b|"
    r"\bPTS\b|phosphotransferase system|"
    r"substrate-binding|solute-binding|ATP-binding cassette|\bABC\b|\bMFS\b|"
    r"facilitator",
    re.IGNORECASE,
)

# ---- Annotation-search Lucene query (product / function_description) ----
# NOTE (documented friction): genes_by_function returns 0 when search_text is
# combined with category=. So NO category is passed here (ontology-first / text
# search without category).
ANNO_QUERY = (
    "transporter OR importer OR exporter OR symporter OR antiporter OR uniporter "
    "OR permease OR transport OR symport OR antiport OR \"substrate-binding\" "
    "OR \"solute-binding\" OR TonB OR translocase OR channel OR efflux OR MFS "
    "OR \"ABC transporter\" OR \"ATP-binding cassette\" OR facilitator"
)

# ---- Aromatic / xenobiotic substrate keywords (Task B) ----
AROMATIC_RE = re.compile(
    r"benzoate|benzoic|benzene|naphthalene|xylene|toluene|aromatic|biphenyl|"
    r"phenol|catechol|salicylate|vanillate|vanillin|protocatechuate|gentisate|"
    r"phthalate|chlorobenzo|bromobenzo|halobenzo|dibenzo|styrene|cymene|"
    r"anthranilate|hydroxybenzo|muconate",
    re.IGNORECASE,
)


def _rows(result):
    return result.get("results", []) if isinstance(result, dict) else []


def _agg(series):
    """Join unique non-null strings with ' ; '."""
    vals = [str(v) for v in series if v is not None and str(v) != "nan" and str(v) != ""]
    seen, out = set(), []
    for v in vals:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return " ; ".join(out)


def enumerate_strain(org, conn):
    print(f"\n=== {org} ===")

    # --- Source 1: BRITE transporters tree (ko02000) ---
    brite = genes_by_ontology(
        ontology="brite", organism=org, tree="transporters", level=0,
        min_gene_set_size=1, max_gene_set_size=100000, limit=None, conn=conn,
    )
    brite_rows = _rows(brite)
    brite_set = {r["locus_tag"] for r in brite_rows}
    print(f"  BRITE ko02000 genes: {len(brite_set)} (total_matching={brite.get('total_matching')})")

    # --- Source 3: TCDB (all TCDB-classified genes are transporters) ---
    tcdb = genes_by_ontology(
        ontology="tcdb", organism=org, level=0,
        min_gene_set_size=1, max_gene_set_size=100000, limit=None, conn=conn,
    )
    tcdb_set = {r["locus_tag"] for r in _rows(tcdb)}
    print(f"  TCDB genes: {len(tcdb_set)} (total_matching={tcdb.get('total_matching')})")

    # --- Source 2: KEGG KO transporter terms (regex on KO name) ---
    # Full KEGG level-3 (orthology) pull -- doubles as KO annotation for all genes.
    kegg = genes_by_ontology(
        ontology="kegg", organism=org, level=3,
        min_gene_set_size=1, max_gene_set_size=100000, limit=None, conn=conn,
    )
    kegg_rows = _rows(kegg)
    kegg_df = pd.DataFrame(
        [{"locus_tag": r["locus_tag"],
          "kegg_ko_id": r["term_id"].replace("kegg.orthology:", ""),
          "kegg_ko_name": r["term_name"]} for r in kegg_rows]
    )
    kegg_set = {r["locus_tag"] for r in kegg_rows if TRANSPORT_RE.search(r["term_name"] or "")}
    print(f"  KEGG all-KO genes: {kegg_df['locus_tag'].nunique() if len(kegg_df) else 0}; "
          f"KEGG transporter-KO genes: {len(kegg_set)}")

    # --- Source 4: annotation keyword search ---
    anno = genes_by_function(search_text=ANNO_QUERY, organism=org, verbose=True, limit=None, conn=conn)
    anno_rows = _rows(anno)
    anno_set = {r["locus_tag"] for r in anno_rows}
    print(f"  Annotation-search genes: {len(anno_set)} (total_matching={anno.get('total_matching')})")

    union = brite_set | kegg_set | tcdb_set | anno_set
    print(f"  UNION genes: {len(union)}")

    union_list = sorted(union)

    # --- Annotation: gene_overview (product, gene_name, function_description) ---
    ov = gene_overview(locus_tags=union_list, verbose=True, limit=None, conn=conn)
    ov_map = {}
    for r in _rows(ov):
        ov_map[r["locus_tag"]] = {
            "gene_name": r.get("gene_name"),
            "product": r.get("product"),
            "function_description": r.get("function_description"),
            "gene_category": r.get("gene_category"),
        }

    # --- Annotation: TCDB leaf family (finest) ---
    tcdb_leaf = gene_ontology_terms(
        locus_tags=union_list, organism=org, ontology="tcdb", mode="leaf",
        limit=None, conn=conn,
    )
    tcdb_leaf_df = pd.DataFrame(
        [{"locus_tag": r["locus_tag"], "tcdb_family": r["term_name"]} for r in _rows(tcdb_leaf)]
    )
    tcdb_fam = (tcdb_leaf_df.groupby("locus_tag")["tcdb_family"].apply(_agg).to_dict()
                if len(tcdb_leaf_df) else {})

    # --- Annotation: BRITE transporters leaf (finest) ---
    brite_leaf = gene_ontology_terms(
        locus_tags=union_list, organism=org, ontology="brite", tree="transporters",
        mode="leaf", limit=None, conn=conn,
    )
    brite_leaf_df = pd.DataFrame(
        [{"locus_tag": r["locus_tag"], "brite_leaf": r["term_name"]} for r in _rows(brite_leaf)]
    )
    brite_leaf_map = (brite_leaf_df.groupby("locus_tag")["brite_leaf"].apply(_agg).to_dict()
                      if len(brite_leaf_df) else {})

    # --- KEGG KO per gene (aggregate multiple KOs) ---
    if len(kegg_df):
        kegg_g = kegg_df[kegg_df["locus_tag"].isin(union)].groupby("locus_tag")
        kegg_id_map = kegg_g["kegg_ko_id"].apply(_agg).to_dict()
        kegg_name_map = kegg_g["kegg_ko_name"].apply(_agg).to_dict()
    else:
        kegg_id_map, kegg_name_map = {}, {}

    # --- Assemble one row per gene ---
    out = []
    for lt in union_list:
        srcs = []
        if lt in brite_set:
            srcs.append("brite")
        if lt in kegg_set:
            srcs.append("kegg")
        if lt in tcdb_set:
            srcs.append("tcdb")
        if lt in anno_set:
            srcs.append("annotation")
        ovd = ov_map.get(lt, {})
        out.append({
            "organism_name": org,
            "locus_tag": lt,
            "gene_name": ovd.get("gene_name"),
            "product": ovd.get("product"),
            "function_description": ovd.get("function_description"),
            "kegg_ko_id": kegg_id_map.get(lt),
            "kegg_ko_name": kegg_name_map.get(lt),
            "tcdb_family": tcdb_fam.get(lt),
            "brite_leaf": brite_leaf_map.get(lt),
            "sources": "|".join(srcs),
            "gene_category": ovd.get("gene_category"),
        })
    df = pd.DataFrame(out)

    # source-membership booleans for QC
    df["in_brite"] = df["locus_tag"].isin(brite_set)
    df["in_kegg"] = df["locus_tag"].isin(kegg_set)
    df["in_tcdb"] = df["locus_tag"].isin(tcdb_set)
    df["in_annotation"] = df["locus_tag"].isin(anno_set)
    return df


def main():
    all_dfs = []
    first = True
    with GraphConnection() as conn:
        for org in ORGANISMS:
            df = enumerate_strain(org, conn)
            # incremental write: append after each strain so partial progress survives
            cols = ["organism_name", "locus_tag", "gene_name", "product",
                    "function_description", "kegg_ko_id", "kegg_ko_name",
                    "tcdb_family", "brite_leaf", "sources", "gene_category",
                    "in_brite", "in_kegg", "in_tcdb", "in_annotation"]
            df[cols].to_csv(OUT_TRANSPORTERS, mode="w" if first else "a",
                            header=first, index=False)
            first = False
            all_dfs.append(df)
            print(f"  wrote {len(df)} rows -> {OUT_TRANSPORTERS}")

    full = pd.concat(all_dfs, ignore_index=True)

    # ================= Task B: QC =================
    print("\n\n################  TASK B  QC  ################")
    aromatic_records = []
    for org in ORGANISMS:
        d = full[full["organism_name"] == org]
        print(f"\n--- {org} ---")
        print(f"  per-source counts:  BRITE={d['in_brite'].sum()}  "
              f"KEGG={d['in_kegg'].sum()}  TCDB={d['in_tcdb'].sum()}  "
              f"ANNO={d['in_annotation'].sum()}")
        print(f"  UNION total: {len(d)}")
        # pairwise unique contributions (genes ONLY from that source)
        only_b = d[d["in_brite"] & ~d["in_kegg"] & ~d["in_tcdb"] & ~d["in_annotation"]]
        only_k = d[~d["in_brite"] & d["in_kegg"] & ~d["in_tcdb"] & ~d["in_annotation"]]
        only_t = d[~d["in_brite"] & ~d["in_kegg"] & d["in_tcdb"] & ~d["in_annotation"]]
        only_a = d[~d["in_brite"] & ~d["in_kegg"] & ~d["in_tcdb"] & d["in_annotation"]]
        print(f"  UNIQUE (sole-source) contributions:  BRITE-only={len(only_b)}  "
              f"KEGG-only={len(only_k)}  TCDB-only={len(only_t)}  ANNO-only={len(only_a)}")
        # aromatic importers
        text = (d["product"].fillna("") + " || " + d["function_description"].fillna("")
                + " || " + d["kegg_ko_name"].fillna(""))
        arom_mask = text.apply(lambda s: bool(AROMATIC_RE.search(s)))
        arom = d[arom_mask]
        print(f"  AROMATIC/xenobiotic transporter genes: {len(arom)}")
        for _, r in arom.iterrows():
            print(f"      {r['locus_tag']}  |  {r['product']}  |  KO={r['kegg_ko_name']}")
            aromatic_records.append({
                "organism_name": org, "locus_tag": r["locus_tag"],
                "gene_name": r["gene_name"], "product": r["product"],
                "function_description": r["function_description"],
                "kegg_ko_id": r["kegg_ko_id"], "kegg_ko_name": r["kegg_ko_name"],
                "tcdb_family": r["tcdb_family"], "brite_leaf": r["brite_leaf"],
                "sources": r["sources"],
            })

    pd.DataFrame(aromatic_records).to_csv(OUT_AROMATIC, index=False)
    print(f"\n  wrote {len(aromatic_records)} aromatic rows -> {OUT_AROMATIC}")
    print("\nDONE.")


if __name__ == "__main__":
    main()
