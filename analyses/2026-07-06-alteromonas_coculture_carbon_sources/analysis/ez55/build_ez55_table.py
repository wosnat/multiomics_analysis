"""EZ55 transporter table — Part 1 of the cross-strain step.

REUSES the committed HOT1A3 pipeline's logic and rules verbatim: it imports the
enumeration constants from `methods/pull_transporter_raw.py` and every
reconstruction / substrate-resolution / classification / non-importer-veto
function and lexicon from `methods/build_transporter_table.py`. Nothing about the
method is reinvented here — this driver only (a) points the committed pull at
*Alteromonas macleodii EZ55* and this folder's cache, (b) re-assembles the
per-gene record with the committed functions, (c) relabels system IDs EZ55_TS,
and (d) writes EZ55-named outputs + a facts manifest. `methods/` is untouched.

Run from repo root: uv run analyses/.../analysis/ez55/build_ez55_table.py
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
EZ55_CACHE = os.path.join(HERE, "cache")
METHODS = os.path.abspath(os.path.join(HERE, "..", "..", "methods"))
sys.path.insert(0, METHODS)

import pull_transporter_raw as pr          # committed enumeration + pull
import build_transporter_table as bt       # committed rules

ORG = "Alteromonas macleodii EZ55"
SYS_PREFIX = "EZ55_TS"


def build_records(gd, ko, brite, tcdb, srcs):
    """Per-gene record assembly — identical field-plumbing to
    build_transporter_table.main(), calling the committed rule functions
    (bt.parse_role, bt.ko_substrate_phrase, bt._resolve_gene)."""
    rec = {}
    for g in gd:
        d = gd[g]
        ko_terms = ko.get(g, [])
        ko_t = None
        for t in ko_terms:
            if any(k in t["term_name"].lower() for k in
                   ("transport", "permease", "porin", "channel", "symport", "antiport")):
                ko_t = t
                break
        if ko_t is None and ko_terms:
            ko_t = ko_terms[0]
        ko_name = ko_t["term_name"] if ko_t else None
        ko_id = ko_t["term_id"] if ko_t else None
        bl = brite.get(g, [])
        bl_best = max(bl, key=lambda x: x.get("level") or 0) if bl else None
        tl = tcdb.get(g, [])
        tl_best = max(tl, key=lambda x: x.get("level") or 0) if tl else None
        role = (bt.parse_role(ko_name) or bt.parse_role(d.get("product"))
                or bt.parse_role(d.get("function_description")))
        rec[g] = {
            "locus_tag": g, "gene_name": d.get("gene_name"),
            "product": d.get("product"),
            "function_description": d.get("function_description"),
            "gene_category": d.get("gene_category"), "contig": d.get("contig"),
            "start": d.get("start"), "end": d.get("end"), "strand": d.get("strand"),
            "ko_id": ko_id, "ko_name": ko_name,
            "brite_leaf": bl_best["term_name"] if bl_best else None,
            "brite_level": bl_best.get("level") if bl_best else None,
            "tcdb_id": tl_best["term_id"] if tl_best else None,
            "tcdb_name": tl_best["term_name"] if tl_best else None,
            "role": role,
            "sources": [k for k, v in srcs.get(g, {}).items() if v],
            "ko_substrate": bt.ko_substrate_phrase(ko_name),
        }
    for g, r in rec.items():
        r.update(bt._resolve_gene(r))
    return rec


def main():
    # ---- (a) run the committed pull against EZ55 into this folder's cache ----
    pr.ORG = ORG
    pr.CACHE = EZ55_CACHE
    os.makedirs(EZ55_CACHE, exist_ok=True)
    pr.main()

    # ---- (b) build records with the committed rules, reading EZ55 cache ----
    bt.CACHE = EZ55_CACHE       # bt.load() now reads EZ55 cache
    bt.HERE = HERE              # bt writers now target this folder
    gd = bt.load("gene_details.json")
    ko = bt.load("kegg_ko_by_gene.json")
    brite = bt.load("brite_leaf_by_gene.json")
    tcdb = bt.load("tcdb_by_gene.json")
    srcs = bt.load("union_sources.json")
    rec = build_records(gd, ko, brite, tcdb, srcs)

    # ---- (c) reconstruct systems (committed) + relabel HOT1A3_TS -> EZ55_TS ----
    systems = bt.reconstruct_systems(rec)
    systems = [(sid.replace("HOT1A3_TS", SYS_PREFIX), tags) for sid, tags in systems]
    sys_rows = [bt.resolve_system(sid, [rec[t] for t in tags]) for sid, tags in systems]

    # ---- (d) write EZ55-named outputs via the committed writers + rename ----
    bt.write_gene_csv(rec)      # writes hot1a3_transporter_gene_table.csv into HERE
    bt.write_system_csv(sys_rows)
    os.replace(os.path.join(HERE, "hot1a3_transporter_gene_table.csv"),
               os.path.join(HERE, "ez55_transporter_gene_table.csv"))
    os.replace(os.path.join(HERE, "hot1a3_transporter_table.csv"),
               os.path.join(HERE, "ez55_transporter_table.csv"))

    write_ez55_manifest(rec, sys_rows)
    print(f"EZ55: genes={len(rec)}  systems={len(sys_rows)}")


def write_ez55_manifest(rec, sys_rows):
    log = bt.load("pull_log.json")
    n_genes = len(rec)
    n_sys = len(sys_rows)
    lvl = Counter(r["resolution_level"] for r in sys_rows)
    imp = Counter(r["importer_or_exporter"] for r in sys_rows)
    org = Counter(r["organic_or_inorganic"] for r in sys_rows)
    oc = [r for r in sys_rows if r["importer_or_exporter"] == "importer"
          and r["organic_or_inorganic"] == "organic"]
    oc_lvl = Counter(r["resolution_level"] for r in oc)
    recl = [r for r in sys_rows if (r["source"] or "").startswith("reclassified:")]
    reason_ct = Counter((r["source"] or "").replace("reclassified: ", "").split(" (")[0]
                        for r in recl)
    ngenes_dist = Counter(r["n_genes"] for r in sys_rows)

    L = []
    L.append("# EZ55 transporter table — build manifest (facts only)\n")
    L.append("Built by `build_ez55_table.py`, which reuses the committed HOT1A3 "
             "pipeline verbatim (same enumeration union, 150 bp adjacency + KO-name "
             "role boundary rule, finest-confident substrate resolution, and "
             "non-importer veto) applied to **Alteromonas macleodii EZ55** "
             "(locus-tag prefix `EZ55_`). `methods/` code unchanged.\n")
    L.append("## Enumeration (union of four sources)\n")
    L.append(f"- BRITE transporters tree `ko02000`: {log['brite_total_genes']} genes")
    L.append(f"- KEGG-KO transporter-named: {log['kegg_transporter_genes']} genes "
             f"(of {log['kegg_all_genes']} KEGG-annotated)")
    L.append(f"- TCDB: {log['tcdb_total_genes']} genes")
    L.append(f"- product/function search (transporter-filtered): {log['func_transporter_genes']} genes")
    L.append(f"- **UNION candidate transporter genes: {log['union_total']}**\n")
    L.append("## Systems reconstructed\n")
    L.append(f"- Candidate transporter genes: **{n_genes}**")
    L.append(f"- Transport systems reconstructed: **{n_sys}** "
             f"(size dist n_genes:count = {dict(sorted(ngenes_dist.items()))})")
    L.append(f"- Adjacency gap ceiling: {bt.GAP_BP} bp (same contig, same strand)\n")
    L.append("## Resolution level distribution (per system)\n")
    for k in ["specific_compound", "narrow_class", "multi_substrate", "broad_class", "unresolved"]:
        L.append(f"- {k}: {lvl.get(k, 0)}")
    L.append("")
    L.append("## Classification\n")
    L.append(f"- importer: {imp.get('importer',0)}; exporter/efflux: {imp.get('exporter',0)}; "
             f"non_transporter (import veto): {imp.get('non_transporter',0)}")
    L.append(f"- organic: {org.get('organic',0)}; inorganic: {org.get('inorganic',0)}; "
             f"unknown: {org.get('unknown',0)}")
    L.append(f"- **organic-carbon importer systems: {len(oc)}** "
             f"(by resolution level: {dict(oc_lvl)})")
    L.append(f"- import veto reclassified {len(recl)} systems out of the importer set "
             f"(by reason: {dict(reason_ct)}).\n")
    with open(os.path.join(HERE, "ez55_build_manifest.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("wrote ez55_build_manifest.md; organic-C importers =", len(oc))


if __name__ == "__main__":
    main()
