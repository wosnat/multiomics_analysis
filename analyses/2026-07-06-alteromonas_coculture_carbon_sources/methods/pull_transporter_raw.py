"""Stage A+B: pull raw transporter enumeration + per-gene annotation for HOT1A3.

Enumerates candidate transporter genes by UNIONING four KG sources (proposal
Approach step 1): BRITE transporters tree ko02000, KEGG KO transporter
annotations, TCDB, and product/function search. Then pulls per-gene annotation
(gene_details coords/product/function, KEGG KO names, BRITE leaf, TCDB family)
for every candidate. All output is cached to JSON so the reconstruction /
resolution logic (build_transporter_table.py) can iterate without re-querying.

Every value here traces to a KG query (SKILL Rule 1). No substrate is guessed.
Run from repo root: uv run analyses/.../methods/pull_transporter_raw.py
"""
import json
import os
from multiomics_explorer import (
    genes_by_ontology, gene_details, gene_ontology_terms, genes_by_function,
)

ORG = "Alteromonas macleodii HOT1A3"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
os.makedirs(CACHE, exist_ok=True)

# Transporter-signal keywords for the product/function search source (source D)
# and for filtering KEGG-KO names to transporter KOs (source B).
FUNC_KEYWORDS = [
    "transporter", "permease", '"ABC transporter"', "symporter", "antiporter",
    "porin", '"TonB-dependent"', "channel", "efflux", "exporter",
    '"transport system"', "uptake", "importer",
]
# Keywords that mark a KEGG-KO *name* as a transporter (KO names are like
# "afuA, fbpA; iron(III) transport system substrate-binding protein").
KO_TRANSPORTER_KEYS = [
    "transport system", "transporter", "permease", "abc transport",
    "symporter", "antiporter", "porin", "tonb", "channel", "efflux",
    "mfs transport", "uptake", " importer", "translocase",
]
# Product keywords that keep a function-search hit as a transporter (drop
# enzymes like aminotransferase / dehydrogenase that merely mention a substrate).
PRODUCT_TRANSPORTER_KEYS = [
    "transporter", "permease", "transport system", "abc transport",
    "symporter", "antiporter", "porin", "tonb", "channel", "efflux pump",
    "translocase", "mfs ", "abc-type", "uptake", "importer", "exporter",
    "transport protein", "solute-binding", "substrate-binding",
]


def dump(name, obj):
    p = os.path.join(CACHE, name)
    with open(p, "w") as f:
        json.dump(obj, f, indent=1, default=str)
    print(f"  wrote {name} ({len(json.dumps(obj, default=str))} bytes)")


def is_transporter_name(text, keys):
    t = (text or "").lower()
    return any(k in t for k in keys)


def main():
    log = {}

    # ---- Source A: BRITE transporters tree ko02000 (level 0 = whole tree) ----
    print("Source A: BRITE transporters tree ko02000")
    a = genes_by_ontology(ontology="brite", organism=ORG, tree="transporters",
                          level=0, min_gene_set_size=0, max_gene_set_size=None,
                          verbose=True, limit=None)
    brite_genes = {}
    for r in a["results"]:
        brite_genes.setdefault(r["locus_tag"], []).append(
            {"term_id": r["term_id"], "term_name": r["term_name"],
             "level": r["level"]})
    log["brite_total_genes"] = a["total_genes"]
    print(f"  BRITE total_genes={a['total_genes']} rows={a['total_matching']}")
    dump("source_brite.json", {"total_genes": a["total_genes"],
                               "genes": sorted(brite_genes)})

    # ---- Source B: KEGG KO, filtered to transporter-signal KO names ----
    print("Source B: KEGG KO (level 3) filtered to transporter KO names")
    b = genes_by_ontology(ontology="kegg", organism=ORG, level=3,
                          min_gene_set_size=0, max_gene_set_size=None,
                          limit=None)
    kegg_transporter = {}
    for r in b["results"]:
        if is_transporter_name(r["term_name"], KO_TRANSPORTER_KEYS):
            kegg_transporter.setdefault(r["locus_tag"], []).append(
                {"term_id": r["term_id"], "term_name": r["term_name"]})
    log["kegg_all_genes"] = b["total_genes"]
    log["kegg_transporter_genes"] = len(kegg_transporter)
    print(f"  KEGG all genes={b['total_genes']}; transporter-KO genes={len(kegg_transporter)}")
    dump("source_kegg.json", {"transporter_genes": sorted(kegg_transporter)})

    # ---- Source C: TCDB (level 2 = family; every tcdb gene is a transporter) --
    print("Source C: TCDB")
    c = genes_by_ontology(ontology="tcdb", organism=ORG, level=2,
                          min_gene_set_size=0, max_gene_set_size=None,
                          limit=None)
    tcdb_genes = {}
    for r in c["results"]:
        tcdb_genes.setdefault(r["locus_tag"], []).append(
            {"term_id": r["term_id"], "term_name": r["term_name"],
             "level": r["level"]})
    log["tcdb_total_genes"] = c["total_genes"]
    print(f"  TCDB total_genes={c['total_genes']}")
    dump("source_tcdb.json", {"total_genes": c["total_genes"],
                              "genes": sorted(tcdb_genes)})

    # ---- Source D: product / function-description search ----
    print("Source D: product/function search")
    func_hits = {}
    per_kw = {}
    for kw in FUNC_KEYWORDS:
        d = genes_by_function(search_text=kw, organism=ORG, verbose=True,
                              limit=None)
        kept = 0
        for r in d["results"]:
            prod = r.get("product") or ""
            fdesc = r.get("function_description") or ""
            if (is_transporter_name(prod, PRODUCT_TRANSPORTER_KEYS)
                    or is_transporter_name(fdesc, PRODUCT_TRANSPORTER_KEYS)):
                func_hits[r["locus_tag"]] = {"product": prod,
                                             "gene_name": r.get("gene_name")}
                kept += 1
        per_kw[kw] = {"total_matching": d["total_matching"], "kept": kept}
    log["func_search_per_kw"] = per_kw
    log["func_transporter_genes"] = len(func_hits)
    print(f"  function-search transporter genes={len(func_hits)}")
    dump("source_func.json", {"genes": sorted(func_hits)})

    # ---- UNION ----
    union = set(brite_genes) | set(kegg_transporter) | set(tcdb_genes) | set(func_hits)
    per_gene_sources = {}
    for g in union:
        per_gene_sources[g] = {
            "brite": g in brite_genes,
            "kegg": g in kegg_transporter,
            "tcdb": g in tcdb_genes,
            "func": g in func_hits,
        }
    log["union_total"] = len(union)
    print(f"UNION candidate transporter genes = {len(union)}")
    dump("union_sources.json", per_gene_sources)

    # ---- Stage B: per-gene annotation for the union ----
    print("Stage B: gene_details for union")
    union_list = sorted(union)
    gd = gene_details(locus_tags=union_list, limit=None)
    details = {}
    for r in gd["results"]:
        details[r["locus_tag"]] = {
            k: r.get(k) for k in (
                "locus_tag", "gene_name", "product", "function_description",
                "gene_category", "contig", "start", "end", "strand",
                "tcdb_family_count", "cazy_family_count", "annotation_state",
                "annotation_quality", "subcellular_localization",
                "annotation_types", "gene_summary")
        }
    log["gene_details_returned"] = gd["returned"]
    log["gene_details_not_found"] = gd.get("not_found")
    dump("gene_details.json", details)

    # KEGG KO names per union gene (leaf), for substrate+role parsing
    print("Stage B: gene_ontology_terms KEGG for union")
    kt = gene_ontology_terms(locus_tags=union_list, organism=ORG,
                             ontology="kegg", mode="leaf", limit=None)
    ko_by_gene = {}
    for r in kt["results"]:
        ko_by_gene.setdefault(r["locus_tag"], []).append(
            {"term_id": r["term_id"], "term_name": r["term_name"]})
    dump("kegg_ko_by_gene.json", ko_by_gene)

    # BRITE transporters leaf term per gene (deepest level available)
    print("Stage B: gene_ontology_terms BRITE(transporters) for union")
    bt = gene_ontology_terms(locus_tags=union_list, organism=ORG,
                             ontology="brite", tree="transporters",
                             mode="leaf", limit=None)
    brite_leaf = {}
    for r in bt["results"]:
        brite_leaf.setdefault(r["locus_tag"], []).append(
            {"term_id": r["term_id"], "term_name": r["term_name"],
             "level": r.get("level")})
    dump("brite_leaf_by_gene.json", brite_leaf)

    # TCDB family (deepest) per gene
    print("Stage B: gene_ontology_terms TCDB for union")
    tt = gene_ontology_terms(locus_tags=union_list, organism=ORG,
                             ontology="tcdb", mode="leaf", limit=None)
    tcdb_by_gene = {}
    for r in tt["results"]:
        tcdb_by_gene.setdefault(r["locus_tag"], []).append(
            {"term_id": r["term_id"], "term_name": r["term_name"],
             "level": r.get("level")})
    dump("tcdb_by_gene.json", tcdb_by_gene)

    dump("pull_log.json", log)
    print("\nDONE. Cached raw pulls to", CACHE)


if __name__ == "__main__":
    main()
