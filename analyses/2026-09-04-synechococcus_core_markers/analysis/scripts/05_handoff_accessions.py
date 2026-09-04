"""Build the collaborator handoff: protein accessions for all 53 markers.

Supersedes the medoid selection in 04_pick_blast_representative.py, which could
not be done honestly. The KG stores an amino-acid sequence for only 50 of the
265 marker gene instances, and 37 of those 50 are CC9311. So a "medoid" chosen
from stored sequences just picks whichever strain happens to have a sequence.
That result is an artifact and is not used.

Protein accessions are available for 244 of 265 instances, spread evenly across
the five strains, so the handoff is accessions. Collaborators fetch sequences
from NCBI.

Per marker this emits all five accessions plus the flags a bioinformatician
needs before choosing a query:
  - multi_copy_family    : the hli rows; the family is expanded in
                           Prochlorococcus, so hits are not diagnostic
  - shared_domain        : another gene in >=1 of the five genomes carries the
                           same Pfam entry (from 03_paralog_check.py)
  - cross_aligns_marker  : aligns to another marker in this panel
  - annotated            : has an informative gene name

Inputs : data/markers_no_7002.csv, data/paralog_check.csv,
         data/cross_marker_hits.csv
Outputs: data/handoff_accessions.csv   one row per marker (wide, 5 accessions)
         data/handoff_long.csv         one row per marker x strain
         data/05_handoff_accessions.log
Usage  : uv run python analysis/scripts/05_handoff_accessions.py
"""

from __future__ import annotations

import csv
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

from multiomics_explorer import GraphConnection, gene_aa_sequence, gene_details

DATA = Path(__file__).resolve().parents[1] / "data"
log = logging.getLogger("handoff")

STRAINS = [
    ("locus_CC9311", "CC9311", "Synechococcus CC9311", "I"),
    ("locus_WH8109", "WH8109", "Synechococcus WH8109", "II"),
    ("locus_WH8102", "WH8102", "Synechococcus WH8102", "III"),
    ("locus_BL107", "BL107", "Synechococcus sp. BL107", "IV"),
    ("locus_WH7803", "WH7803", "Synechococcus WH7803", "V"),
]


def setup() -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(DATA / "05_handoff_accessions.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def main() -> int:
    setup()
    markers = list(csv.DictReader(open(DATA / "markers_no_7002.csv")))
    log.info("markers: %d", len(markers))

    loci, owner = [], {}
    for i, m in enumerate(markers):
        for col, short, _full, _clade in STRAINS:
            lt = (m.get(col) or "").strip()
            if lt:
                loci.append(lt)
                owner[lt] = (f"m{i:03d}", short)

    # --- accessions + sequence availability ---------------------------------
    acc: dict[str, str] = {}
    has_seq: set[str] = set()
    with GraphConnection() as conn:
        for i in range(0, len(loci), 200):
            for r in gene_aa_sequence(locus_tags=loci[i : i + 200], limit=10**6, conn=conn)["results"]:
                if r.get("protein_id"):
                    acc[r["locus_tag"]] = r["protein_id"]
                if r.get("sequence"):
                    has_seq.add(r["locus_tag"])
        for i in range(0, len(loci), 200):
            for r in gene_details(locus_tags=loci[i : i + 200], limit=10**6, conn=conn)["results"]:
                if r.get("protein_id") and r["locus_tag"] not in acc:
                    acc[r["locus_tag"]] = r["protein_id"]
    log.info("instances with a protein accession: %d/%d", len(acc), len(loci))
    log.info("instances with a stored AA sequence: %d/%d", len(has_seq), len(loci))

    # --- flags from earlier steps -------------------------------------------
    shared_domain: dict[str, bool] = defaultdict(bool)
    p = DATA / "paralog_check.csv"
    if p.exists():
        for r in csv.DictReader(open(p)):
            if r["marker_set"] == "five_strain" and r["domain_paralog_flag"] == "shares_domain":
                shared_domain[r["locus_tag"]] = True

    cross_ids: set[str] = set()
    p = DATA / "cross_marker_hits.csv"
    if p.exists():
        for r in csv.DictReader(open(p)):
            cross_ids.add(r["marker_a"])
            cross_ids.add(r["marker_b"])

    # --- emit ----------------------------------------------------------------
    wide, long = [], []
    for i, m in enumerate(markers):
        mid = f"m{i:03d}"
        gene = m.get("consensus_gene_name") or ""
        product = m.get("consensus_product") or ""
        row = {
            "marker_id": mid,
            "gene": gene,
            "product": product,
            "category": m.get("gene_category") or "",
            "annotated": bool(gene) and "hypothetical" not in product.lower(),
            "multi_copy_family": gene == "hli",
            "cross_aligns_another_marker": mid in cross_ids,
        }
        n_acc = 0
        dom = False
        for col, short, full, clade in STRAINS:
            lt = (m.get(col) or "").strip()
            a = acc.get(lt, "")
            row[f"acc_{short}"] = a
            row[f"locus_{short}"] = lt
            if a:
                n_acc += 1
            if shared_domain.get(lt):
                dom = True
            long.append({
                "marker_id": mid, "gene": gene, "product": product,
                "strain": short, "clade": clade, "organism": full,
                "locus_tag": lt, "protein_accession": a,
                "aa_sequence_in_kg": lt in has_seq,
            })
        row["shared_domain_in_a_genome"] = dom
        row["accessions_available"] = n_acc
        row["recommended_as_query"] = (
            row["annotated"] and not row["multi_copy_family"]
            and not row["cross_aligns_another_marker"] and n_acc == 5
        )
        wide.append(row)

    wide.sort(key=lambda r: (not r["recommended_as_query"], not r["annotated"], r["gene"] or "zz"))
    with open(DATA / "handoff_accessions.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(wide[0]))
        w.writeheader()
        w.writerows(wide)
    with open(DATA / "handoff_long.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(long[0]))
        w.writeheader()
        w.writerows(long)

    log.info("--- panel composition ---")
    log.info("markers with all 5 accessions      : %d",
             sum(1 for r in wide if r["accessions_available"] == 5))
    log.info("markers with 4 accessions          : %d",
             sum(1 for r in wide if r["accessions_available"] == 4))
    log.info("markers with <4 accessions         : %d",
             sum(1 for r in wide if r["accessions_available"] < 4))
    log.info("annotated markers                  : %d", sum(1 for r in wide if r["annotated"]))
    log.info("flagged multi-copy family (hli)    : %d", sum(1 for r in wide if r["multi_copy_family"]))
    log.info("cross-aligning another marker      : %d",
             sum(1 for r in wide if r["cross_aligns_another_marker"]))
    log.info("shared domain in >=1 genome        : %d",
             sum(1 for r in wide if r["shared_domain_in_a_genome"]))
    log.info("RECOMMENDED as first-tier queries  : %d",
             sum(1 for r in wide if r["recommended_as_query"]))
    log.info("--- per-strain accession coverage ---")
    c = Counter(r["strain"] for r in long if r["protein_accession"])
    for _col, short, _f, clade in STRAINS:
        log.info("   %-8s clade %-3s %d/53", short, clade, c[short])
    log.info("wrote handoff_accessions.csv, handoff_long.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
