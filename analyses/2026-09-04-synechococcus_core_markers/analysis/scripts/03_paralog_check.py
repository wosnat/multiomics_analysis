"""Independent paralogy check on the marker genes.

The marker pipeline tests single-copy WITHIN the ortholog neighbourhood: a
strain must contribute exactly one gene across the union of every ortholog
group the marker belongs to. That catches any paralog sharing a group, but by
construction it cannot see a paralog placed in a DIFFERENT group, or one with
no group membership at all.

This script re-tests copy number with a signal independent of the ortholog
groups: Pfam domain content. For each marker gene it collects the gene's Pfam
entries, then counts how many genes in that SAME genome carry the same entry.
A count above 1 means the genome holds another gene with the same domain, i.e.
a domain-level paralog the neighbourhood test did not reject.

A domain match is weaker evidence than an ortholog group. Sharing a common
domain (a membrane-transport fold, a helix-turn-helix) does not make two genes
paralogs. So the output is a flag for review, not a verdict.

Inputs : data/markers.csv, data/markers_no_7002.csv
Outputs: data/paralog_check.csv    one row per (marker, strain)
         data/03_paralog_check.log
Usage  : uv run python analysis/scripts/03_paralog_check.py
"""

from __future__ import annotations

import csv
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

from multiomics_explorer import (
    GraphConnection,
    gene_ontology_terms,
    genes_by_ontology,
)

DATA = Path(__file__).resolve().parents[1] / "data"
log = logging.getLogger("paralog")

ORG_BY_COL = {
    "locus_CC9311": "Synechococcus CC9311",
    "locus_WH8109": "Synechococcus WH8109",
    "locus_WH8102": "Synechococcus WH8102",
    "locus_BL107": "Synechococcus sp. BL107",
    "locus_WH7803": "Synechococcus WH7803",
    "locus_PCC_7002": "Synechococcus PCC 7002",
}


def setup() -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(DATA / "03_paralog_check.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def load_markers() -> list[dict]:
    rows = []
    for fn, tag in (("markers.csv", "six_strain"), ("markers_no_7002.csv", "five_strain")):
        p = DATA / fn
        if not p.exists():
            continue
        for r in csv.DictReader(open(p)):
            r["_set"] = tag
            rows.append(r)
    return rows


def main() -> int:
    setup()
    markers = load_markers()
    log.info("marker rows loaded: %d", len(markers))

    # (locus_tag, organism) pairs to test.
    pairs: list[tuple[str, str, dict]] = []
    for mi, m in enumerate(markers):
        m["_id"] = f'{m["_set"]}:{mi}'
        for col, org in ORG_BY_COL.items():
            lt = m.get(col)
            if lt:
                pairs.append((lt, org, m))
    loci = sorted({lt for lt, _, _ in pairs})
    log.info("distinct marker genes to test: %d", len(loci))

    with GraphConnection() as conn:
        # 1. Pfam entries per marker gene.
        # gene_ontology_terms is single-organism, so batch per organism.
        loci_by_org: dict[str, list[str]] = defaultdict(list)
        for lt, org, _ in pairs:
            loci_by_org[org].append(lt)

        gene_pfam: dict[str, set[str]] = defaultdict(set)
        for org, org_loci in loci_by_org.items():
            org_loci = sorted(set(org_loci))
            for i in range(0, len(org_loci), 200):
                res = gene_ontology_terms(
                    locus_tags=org_loci[i : i + 200], ontology="pfam",
                    organism=org, limit=None, conn=conn,
                )
                for r in res["results"]:
                    gene_pfam[r["locus_tag"]].add(r["term_id"])
        n_with = sum(1 for lt in loci if gene_pfam.get(lt))
        log.info("marker genes carrying at least one Pfam entry: %d/%d", n_with, len(loci))

        all_terms = sorted({t for s in gene_pfam.values() for t in s})
        log.info("distinct Pfam entries involved: %d", len(all_terms))

        # 2. Per organism, how many genes carry each of those Pfam entries.
        # genes_by_ontology is single-organism, so one call per organism.
        per_org_counts: dict[str, Counter] = {}
        for org in sorted({o for _, o, _ in pairs}):
            c: Counter = Counter()
            for i in range(0, len(all_terms), 200):
                res = genes_by_ontology(
                    ontology="pfam",
                    term_ids=all_terms[i : i + 200],
                    organism=org,
                    limit=None,
                    conn=conn,
                )
                for r in res["results"]:
                    c[r["term_id"]] += 1
            per_org_counts[org] = c
            log.info("  %-28s pfam gene-rows: %d", org, sum(c.values()))

    # 3. Flag markers whose domains are shared with another gene in the genome.
    out = []
    flagged = 0
    no_pfam = 0
    for lt, org, m in pairs:
        terms = sorted(gene_pfam.get(lt, ()))
        if not terms:
            no_pfam += 1
            out.append({
                "marker_id": m["_id"],
                "marker_set": m["_set"],
                "gene": m.get("consensus_gene_name") or "",
                "product": m.get("consensus_product") or "",
                "organism": org,
                "locus_tag": lt,
                "pfam_entries": "",
                "max_genes_sharing_a_domain": "",
                "domain_paralog_flag": "no_pfam_annotation",
            })
            continue
        worst = max(per_org_counts[org].get(t, 0) for t in terms)
        flag = "clean" if worst <= 1 else "shares_domain"
        if flag == "shares_domain":
            flagged += 1
        out.append({
            "marker_id": m["_id"],
            "marker_set": m["_set"],
            "gene": m.get("consensus_gene_name") or "",
            "product": m.get("consensus_product") or "",
            "organism": org,
            "locus_tag": lt,
            "pfam_entries": ";".join(terms),
            "max_genes_sharing_a_domain": worst,
            "domain_paralog_flag": flag,
        })

    with open(DATA / "paralog_check.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    log.info("--- per (marker, strain) rows: %d ---", len(out))
    log.info("clean, no other gene in that genome shares a domain: %d",
             sum(1 for r in out if r["domain_paralog_flag"] == "clean"))
    log.info("shares a Pfam domain with another gene in that genome: %d", flagged)
    log.info("no Pfam annotation, so untestable this way: %d", no_pfam)

    # Roll up to the marker level: a marker is clean only if every strain is.
    by_marker: dict[tuple, list[str]] = defaultdict(list)
    for r in out:
        by_marker[(r["marker_set"], r["marker_id"], r["gene"], r["product"])].append(r["domain_paralog_flag"])
    tot = Counter()
    for k, flags in by_marker.items():
        if "shares_domain" in flags:
            tot[(k[0], "shares_domain_in_>=1_strain")] += 1
        elif all(f == "no_pfam_annotation" for f in flags):
            tot[(k[0], "no_pfam_anywhere")] += 1
        else:
            tot[(k[0], "clean")] += 1
    log.info("--- rolled up to markers ---")
    for k in sorted(tot):
        log.info("%-12s %-32s %d", k[0], k[1], tot[k])
    log.info("--- markers flagged as sharing a domain ---")
    for k, flags in sorted(by_marker.items()):
        if "shares_domain" in flags:
            log.info("   %-8s %-8s %s", k[1], k[2] or "-", k[3][:52])
    log.info("wrote paralog_check.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
