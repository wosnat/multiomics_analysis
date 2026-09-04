"""Pick one representative sequence per marker for a metagenome BLAST search.

Each of the 53 five-strain markers has one ortholog in each of CC9311, WH8109,
WH8102, BL107 and WH7803. For a search against an unknown Mediterranean
metagenome we want the single sequence most likely to recover distant relatives.

The principled choice is the MEDOID: the member with the highest mean percent
identity to the other four. It sits closest to the centre of the group's
sequence space, so it is the least biased starting point for finding a strain
that is in none of the five genomes. Picking a fixed strain instead builds that
strain's idiosyncrasies into every query.

Method: export amino-acid sequences, run an all-versus-all DIAMOND blastp over
the whole marker set, then per marker take the member maximising mean identity
to its four siblings. The same all-versus-all also exposes CROSS-MARKER
similarity, which matters because two markers that hit each other cannot be
told apart in metagenomic reads.

Inputs : data/markers_no_7002.csv
Outputs: data/marker_proteins.faa          all 265 sequences
         data/blast_representatives.csv    the recommendation, one row per marker
         data/blast_representatives.faa    the chosen query set, ready to use
         data/cross_marker_hits.csv        marker pairs that align to each other
         data/04_pick_blast_representative.log
Usage  : uv run python analysis/scripts/04_pick_blast_representative.py
"""

from __future__ import annotations

import csv
import logging
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from statistics import mean

from multiomics_explorer import GraphConnection, gene_aa_sequence

DATA = Path(__file__).resolve().parents[1] / "data"
log = logging.getLogger("blastrep")

STRAIN_COLS = [
    ("locus_CC9311", "CC9311"),
    ("locus_WH8109", "WH8109"),
    ("locus_WH8102", "WH8102"),
    ("locus_BL107", "BL107"),
    ("locus_WH7803", "WH7803"),
]


def setup() -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(DATA / "04_pick_blast_representative.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def main() -> int:
    setup()
    if not shutil.which("diamond"):
        log.error("diamond not found on PATH")
        return 1

    markers = list(csv.DictReader(open(DATA / "markers_no_7002.csv")))
    log.info("markers: %d", len(markers))

    # marker_id -> {strain: locus_tag}; locus_tag -> (marker_id, strain)
    members: dict[str, dict[str, str]] = {}
    owner: dict[str, tuple[str, str]] = {}
    for i, m in enumerate(markers):
        mid = f"m{i:03d}"
        members[mid] = {}
        for col, strain in STRAIN_COLS:
            lt = (m.get(col) or "").strip()
            if lt:
                members[mid][strain] = lt
                owner[lt] = (mid, strain)
    loci = sorted(owner)
    log.info("marker gene instances: %d", len(loci))

    # ---- sequences ----------------------------------------------------------
    seqs: dict[str, str] = {}
    prot_id: dict[str, str] = {}
    with GraphConnection() as conn:
        for i in range(0, len(loci), 200):
            res = gene_aa_sequence(locus_tags=loci[i : i + 200], conn=conn)
            for r in res["results"]:
                if r.get("sequence"):
                    seqs[r["locus_tag"]] = r["sequence"]
                    prot_id[r["locus_tag"]] = r.get("protein_id") or ""
            for lt in res.get("not_found", []) or []:
                log.warning("locus not found in KG: %s", lt)
            for lt in res.get("not_matched", []) or []:
                log.warning("no stored sequence for: %s", lt)
    log.info("sequences retrieved: %d/%d", len(seqs), len(loci))

    missing_by_marker = {mid: [s for s, lt in d.items() if lt not in seqs]
                         for mid, d in members.items()}
    incomplete = {mid for mid, miss in missing_by_marker.items() if miss}
    if incomplete:
        log.warning("markers missing >=1 sequence, excluded from medoid choice: %d",
                    len(incomplete))

    faa = DATA / "marker_proteins.faa"
    with open(faa, "w") as fh:
        for lt in loci:
            if lt in seqs:
                mid, strain = owner[lt]
                acc = prot_id.get(lt) or "no_accession"
                fh.write(f">{lt} {acc} {mid} {strain}\n{seqs[lt]}\n")
    log.info("wrote %s", faa.name)

    # ---- all-versus-all -----------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        db = Path(td) / "markers"
        subprocess.run(["diamond", "makedb", "--in", str(faa), "-d", str(db),
                        "--quiet"], check=True)
        hits = Path(td) / "hits.tsv"
        subprocess.run([
            "diamond", "blastp", "-q", str(faa), "-d", str(db), "-o", str(hits),
            "--outfmt", "6", "qseqid", "sseqid", "pident", "length", "evalue", "bitscore",
            "--max-target-seqs", "500", "--evalue", "1e-3",
            "--very-sensitive", "--quiet",
        ], check=True)
        pid: dict[tuple[str, str], float] = {}
        for line in open(hits):
            q, s, p, _l, _e, bits = line.rstrip("\n").split("\t")
            if q == s:
                continue
            key = (q, s)
            v = float(p)
            if v > pid.get(key, -1):
                pid[key] = v
    log.info("non-self alignment pairs: %d", len(pid))

    # ---- medoid per marker ---------------------------------------------------
    rows = []
    for mid, d in members.items():
        present = {s: lt for s, lt in d.items() if lt in seqs}
        if len(present) < 2:
            continue
        scores = {}
        for s, lt in present.items():
            others = [o for o in present.values() if o != lt]
            # A missing pair means DIAMOND found no alignment: treat as 0 identity.
            scores[s] = mean(pid.get((lt, o), 0.0) for o in others)
        best = max(scores, key=lambda s: scores[s])
        all_pairs = [pid.get((a, b), 0.0)
                     for a in present.values() for b in present.values() if a != b]
        m = markers[int(mid[1:])]
        rows.append({
            "marker_id": mid,
            "gene": m.get("consensus_gene_name") or "",
            "product": m.get("consensus_product") or "",
            "recommended_strain": best,
            "recommended_locus_tag": present[best],
            "recommended_protein_accession": prot_id.get(present[best], ""),
            "all_five_locus_tags": ";".join(f"{st}={lt}" for st, lt in present.items()),
            "all_five_protein_accessions": ";".join(
                f"{st}={prot_id.get(lt, '')}" for st, lt in present.items()),
            "protein_length": len(seqs[present[best]]),
            "mean_identity_to_siblings": round(scores[best], 1),
            "min_pairwise_identity": round(min(all_pairs), 1),
            "strains_with_sequence": len(present),
            "unaligned_pairs": sum(1 for v in all_pairs if v == 0.0),
        })

    # ---- cross-marker similarity --------------------------------------------
    cross = defaultdict(float)
    for (q, s), v in pid.items():
        mq, ms = owner[q][0], owner[s][0]
        if mq != ms:
            k = tuple(sorted((mq, ms)))
            cross[k] = max(cross[k], v)
    log.info("marker pairs with any cross-alignment: %d", len(cross))

    by_id = {r["marker_id"]: r for r in rows}
    with open(DATA / "cross_marker_hits.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["marker_a", "gene_a", "marker_b", "gene_b", "max_pident"])
        for (a, b), v in sorted(cross.items(), key=lambda kv: -kv[1]):
            w.writerow([a, by_id.get(a, {}).get("gene", ""),
                        b, by_id.get(b, {}).get("gene", ""), round(v, 1)])

    cross_ids = {m for pair in cross for m in pair}
    for r in rows:
        r["cross_hits_another_marker"] = r["marker_id"] in cross_ids

    rows.sort(key=lambda r: (-r["min_pairwise_identity"],))
    with open(DATA / "blast_representatives.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    with open(DATA / "blast_representatives.faa", "w") as fh:
        for r in rows:
            lt = r["recommended_locus_tag"]
            label = r["gene"] or r["product"].replace(" ", "_")[:40]
            acc = r["recommended_protein_accession"] or "no_accession"
            fh.write(f">{acc}|{lt} {r['marker_id']} {r['recommended_strain']} {label}\n"
                     f"{seqs[lt]}\n")

    # ---- summary -------------------------------------------------------------
    picks = defaultdict(int)
    for r in rows:
        picks[r["recommended_strain"]] += 1
    log.info("--- which strain wins the medoid, across %d markers ---", len(rows))
    for s, n in sorted(picks.items(), key=lambda kv: -kv[1]):
        log.info("   %-8s %d", s, n)
    log.info("median mean-identity-to-siblings: %.1f%%",
             sorted(r["mean_identity_to_siblings"] for r in rows)[len(rows) // 2])
    tight = sum(1 for r in rows if r["min_pairwise_identity"] >= 70)
    loose = sum(1 for r in rows if 0 < r["min_pairwise_identity"] < 50)
    unal = sum(1 for r in rows if r["unaligned_pairs"] > 0)
    log.info("markers with min pairwise identity >= 70%%: %d", tight)
    log.info("markers with min pairwise identity < 50%%: %d", loose)
    log.info("markers where at least one sibling pair did not align at all: %d", unal)
    log.info("markers cross-aligning to another marker: %d",
             sum(1 for r in rows if r["cross_hits_another_marker"]))
    no_acc = sum(1 for r in rows if not r["recommended_protein_accession"])
    log.info("recommended queries lacking a protein accession: %d", no_acc)
    log.info("wrote blast_representatives.csv / .faa, cross_marker_hits.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
