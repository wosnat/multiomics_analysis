#!/usr/bin/env python3
"""
Methods milestone -- Task C.

Pull genomic neighborhoods + annotation for four HOT1A3 anchor transporters, to
provide raw material for system reconstruction. Small, per-gene, safe pulls.
Writes methods/data/anchor_neighbors.csv (one row per gene in-window), ordered by
contig+start, with a FIRST-PASS role read from KO name / product. No groupings
are decided here -- that is the main thread's job.

Anchors (HOT1A3):
  1. Fe(III) ABC system  ACZ81_00580 / 00585 / 00590   (K02010-12 iron(III) ABC)
  2. Branched-chain AA -- livK subunit ACZ81_03920 (K01999); the canonical liv
     permease/ATP KOs (K01997/98/95/96) have NO HOT1A3 gene -> cassette resolved
     by adjacency, reported factually.
  3. Glutamine (K10036 glnH) -- ABSENT in HOT1A3 (also K10037 glnP / K10038 glnQ
     absent). Nearest annotated system is the GENERIC polar-amino-acid ABC
     (K02030 ABC.PA.S, 7 substrate-binding paralogs). Representative anchor:
     ACZ81_02465. Reported as "glutamine KO absent; generic polar-AA ABC shown."
  4. Single-polypeptide TCDB 2.A carrier: benE ACZ81_03335 (TCDB 2.A.46.1,
     benzoate:H+ symporter). Single-gene because TCDB class 2.A =
     electrochemical-potential-driven secondary carriers (single polypeptide, no
     separate binding-protein/ATPase subunits), unlike ABC 3.A.1 multi-subunit.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/02_anchor_neighbors.py
"""
import os
import re
import pandas as pd

from multiomics_explorer import (
    gene_neighbors,
    gene_details,
    gene_overview,
    gene_ontology_terms,
    GraphConnection,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
os.makedirs(DATA, exist_ok=True)
OUT = os.path.join(DATA, "anchor_neighbors.csv")

ORG = "HOT1A3"

ANCHORS = {
    "Fe3_ABC_K02010-12": ["ACZ81_00580", "ACZ81_00585", "ACZ81_00590"],
    "branched_chain_AA_livK_K01999": ["ACZ81_03920"],
    "glutamine_K10036_ABSENT__polarAA_ABC_K02030_rep": ["ACZ81_02465"],
    "single_gene_2A_carrier_benE_2.A.46.1": ["ACZ81_03335"],
}


def _rows(r):
    return r.get("results", []) if isinstance(r, dict) else []


def first_pass_role(ko_name, product):
    s = f"{ko_name or ''} || {product or ''}".lower()
    if re.search(r"substrate-binding|solute-binding|periplasmic.*bind|binding.*periplasmic|extracellular solute", s):
        return "substrate-binding"
    if "permease" in s:
        return "permease"
    if re.search(r"atp-binding|atpase|atp binding", s):
        return "ATP-binding"
    if re.search(r"dehydrogenase|oxidase|reductase|hydrolase|synthase|synthetase|lyase|"
                 r"transferase|kinase|aldolase|decarboxylase|hydratase|isomerase|"
                 r"deaminase|degradation|catabolic|thiolase|carboxylase|mutase|esterase", s):
        return "catabolic"
    if re.search(r"transporter|symporter|antiporter|porter|channel|carrier|permease|"
                 r"tonb-dependent|mfs|abc transporter|translocase|efflux|uptake|facilitator", s):
        return "other"  # transporter component, role not resolved
    return "unclear"


def main():
    with GraphConnection() as conn:
        # collect all window locus tags per anchor
        gene_to_anchor = {}
        for aname, seeds in ANCHORS.items():
            nb = gene_neighbors(locus_tags=seeds, window=5, conn=conn)
            window = set(seeds)
            for r in _rows(nb):
                window.add(r["neighbor_locus_tag"])
            # also confirm anchors present
            for a in nb.get("anchors", []):
                window.add(a["locus_tag"])
            for lt in window:
                gene_to_anchor.setdefault(lt, set()).add(aname)
            print(f"{aname}: seeds={seeds} -> {len(window)} window genes")

        all_genes = sorted(gene_to_anchor)
        print(f"\nTotal unique window genes: {len(all_genes)}")

        # coordinates via gene_details
        det = gene_details(locus_tags=all_genes, limit=None, conn=conn)
        det_map = {r["locus_tag"]: r for r in _rows(det)}

        # product/function via gene_overview
        ov = gene_overview(locus_tags=all_genes, verbose=True, limit=None, conn=conn)
        ov_map = {r["locus_tag"]: r for r in _rows(ov)}

        # ontology leaf terms (kegg, tcdb, cog)
        ont = gene_ontology_terms(locus_tags=all_genes, organism=ORG, mode="leaf",
                                  limit=None, conn=conn)
        kegg_id, kegg_name, tcdb_fam, cog = {}, {}, {}, {}
        for r in _rows(ont):
            lt = r["locus_tag"]
            ot = r["ontology_type"]
            if ot == "kegg":
                kegg_id.setdefault(lt, []).append(r["term_id"].replace("kegg.orthology:", ""))
                kegg_name.setdefault(lt, []).append(r["term_name"])
            elif ot == "tcdb":
                tcdb_fam.setdefault(lt, []).append(r["term_name"])
            elif ot == "cog_category":
                cog.setdefault(lt, []).append(r["term_name"])

    def j(d, lt):
        return " ; ".join(dict.fromkeys(d.get(lt, []))) if d.get(lt) else None

    rows = []
    for lt in all_genes:
        d = det_map.get(lt, {})
        o = ov_map.get(lt, {})
        kn = j(kegg_name, lt)
        prod = o.get("product") or d.get("product")
        rows.append({
            "locus_tag": lt,
            "contig": d.get("contig"),
            "start": d.get("start"),
            "end": d.get("end"),
            "strand": d.get("strand"),
            "product": prod,
            "function_description": o.get("function_description") or d.get("function_description"),
            "kegg_ko_id": j(kegg_id, lt),
            "kegg_ko_name": kn,
            "tcdb_family": j(tcdb_fam, lt),
            "cog": j(cog, lt),
            "gene_category": o.get("gene_category") or d.get("gene_category"),
            "anchor": "|".join(sorted(gene_to_anchor[lt])),
            "role_first_pass": first_pass_role(kn, prod),
        })

    df = pd.DataFrame(rows).sort_values(["contig", "start"]).reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print(f"\nwrote {len(df)} rows -> {OUT}")

    # compact per-anchor echo
    for aname in ANCHORS:
        sub = df[df["anchor"].str.contains(re.escape(aname))].sort_values(["contig", "start"])
        print(f"\n=== {aname} ===")
        for _, r in sub.iterrows():
            print(f"  {r['locus_tag']} [{r['start']}-{r['end']} {r['strand']}] "
                  f"{r['role_first_pass']:16s} | {r['product']} | KO={r['kegg_ko_id']} "
                  f"| TCDB={r['tcdb_family']}")


if __name__ == "__main__":
    main()
