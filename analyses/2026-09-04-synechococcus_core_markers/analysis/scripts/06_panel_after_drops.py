"""Apply the researcher's drops, then check how the panel spreads across the genome.

Drops requested 2026-09-04: kaiA, both hli rows, apcE. That leaves four
annotated markers: mpeA, mpeB, cpeR, cpeU.

All four sit inside one contiguous phycobilisome gene cluster in WH8102, so they
are not four independent markers. This script quantifies that by placing every
one of the 53 markers on the WH8102 genome (CC9311 as fallback) and grouping
markers whose anchors lie within a window of each other, so the researcher can
pick queries from distinct loci rather than from one operon.

Inputs : data/markers_no_7002.csv, data/handoff_accessions.csv
Outputs: data/panel_final.csv        the panel after the drops
         data/marker_positions.csv   every marker with genome coordinates + locus block
         data/06_panel_after_drops.log
Usage  : uv run python analysis/scripts/06_panel_after_drops.py
"""

from __future__ import annotations

import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path

from multiomics_explorer import GraphConnection, gene_details

DATA = Path(__file__).resolve().parents[1] / "data"
log = logging.getLogger("panel")

# Genes the researcher dropped, by consensus_gene_name.
DROP_GENES = {"kaiA", "hli", "apcE"}

# Markers whose anchors fall within this many bp are treated as one locus block.
BLOCK_BP = 30_000

# Position anchor: prefer WH8102 (reference-quality), fall back to CC9311.
ANCHOR_COLS = [("locus_WH8102", "WH8102"), ("locus_CC9311", "CC9311")]


def setup() -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(DATA / "06_panel_after_drops.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def main() -> int:
    setup()
    markers = list(csv.DictReader(open(DATA / "markers_no_7002.csv")))
    flags = {r["marker_id"]: r for r in csv.DictReader(open(DATA / "handoff_accessions.csv"))}

    # ---- apply the drops -----------------------------------------------------
    kept, dropped = [], []
    for i, m in enumerate(markers):
        m["_id"] = f"m{i:03d}"
        (dropped if (m.get("consensus_gene_name") or "") in DROP_GENES else kept).append(m)
    log.info("markers before drops: %d", len(markers))
    log.info("dropped (%s): %d", ", ".join(sorted(DROP_GENES)), len(dropped))
    for m in dropped:
        log.info("   dropped %s %s", m["_id"], m["consensus_gene_name"])
    log.info("markers kept: %d", len(kept))

    annotated = [m for m in kept
                 if (m.get("consensus_gene_name") or "")
                 and "hypothetical" not in (m.get("consensus_product") or "").lower()]
    log.info("annotated markers remaining: %d -> %s", len(annotated),
             ", ".join(m["consensus_gene_name"] for m in annotated))

    # ---- position every marker ----------------------------------------------
    anchor_of: dict[str, tuple[str, str]] = {}
    for m in markers:
        for col, strain in ANCHOR_COLS:
            lt = (m.get(col) or "").strip()
            if lt:
                anchor_of[m["_id"]] = (lt, strain)
                break
    loci = [lt for lt, _ in anchor_of.values()]

    coords: dict[str, tuple[str, int, int, str]] = {}
    with GraphConnection() as conn:
        for i in range(0, len(loci), 200):
            for r in gene_details(locus_tags=loci[i : i + 200], conn=conn)["results"]:
                if r.get("start") is not None:
                    coords[r["locus_tag"]] = (
                        r.get("contig") or "?", int(r["start"]), int(r["end"] or r["start"]),
                        r.get("organism_name") or "",
                    )
    log.info("markers with genome coordinates: %d/%d", len(coords), len(anchor_of))

    placed = []
    for m in markers:
        mid = m["_id"]
        lt, strain = anchor_of.get(mid, ("", ""))
        c = coords.get(lt)
        placed.append({
            "marker_id": mid,
            "gene": m.get("consensus_gene_name") or "",
            "product": m.get("consensus_product") or "",
            "kept": mid in {k["_id"] for k in kept},
            "anchor_strain": strain,
            "anchor_locus_tag": lt,
            "contig": c[0] if c else "",
            "start": c[1] if c else "",
            "end": c[2] if c else "",
        })

    # ---- group into locus blocks --------------------------------------------
    by_contig: dict[str, list[dict]] = defaultdict(list)
    for p in placed:
        if p["start"] != "":
            by_contig[(p["anchor_strain"], p["contig"])].append(p)
    block_no = 0
    for key, ps in by_contig.items():
        ps.sort(key=lambda p: p["start"])
        prev_end = None
        for p in ps:
            if prev_end is None or p["start"] - prev_end > BLOCK_BP:
                block_no += 1
            p["locus_block"] = f"B{block_no:02d}"
            prev_end = max(prev_end or 0, p["end"])
    for p in placed:
        p.setdefault("locus_block", "")

    with open(DATA / "marker_positions.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(placed[0]))
        w.writeheader()
        w.writerows(sorted(placed, key=lambda p: (p["anchor_strain"], p["contig"],
                                                  p["start"] if p["start"] != "" else 0)))

    sizes = defaultdict(list)
    for p in placed:
        if p["locus_block"]:
            sizes[p["locus_block"]].append(p)
    multi = {b: ps for b, ps in sizes.items() if len(ps) > 1}
    log.info("--- genome spread of all 53 markers (window %d kb) ---", BLOCK_BP // 1000)
    log.info("distinct locus blocks: %d", len(sizes))
    log.info("blocks holding more than one marker: %d", len(multi))
    for b, ps in sorted(multi.items(), key=lambda kv: -len(kv[1])):
        names = ", ".join((p["gene"] or p["marker_id"]) for p in ps)
        log.info("   %s: %d markers -> %s", b, len(ps), names)

    kept_ids = {k["_id"] for k in kept}
    ann_ids = {m["_id"] for m in annotated}
    ann_blocks = {p["locus_block"] for p in placed if p["marker_id"] in ann_ids}
    log.info("the %d remaining annotated markers occupy %d locus block(s): %s",
             len(annotated), len(ann_blocks), ", ".join(sorted(ann_blocks)))

    # ---- final panel file ----------------------------------------------------
    pos_by_id = {p["marker_id"]: p for p in placed}
    out = []
    for m in kept:
        mid = m["_id"]
        f = flags.get(mid, {})
        p = pos_by_id[mid]
        out.append({
            "marker_id": mid,
            "tier": "1_annotated" if mid in ann_ids else "2_exploratory",
            "gene": m.get("consensus_gene_name") or "",
            "product": m.get("consensus_product") or "",
            "locus_block": p["locus_block"],
            "anchor_strain": p["anchor_strain"],
            "anchor_start": p["start"],
            "accessions_available": f.get("accessions_available", ""),
            "domain_paralog_check": f.get("domain_paralog_check", ""),
            "cross_aligns_another_marker": f.get("cross_aligns_another_marker", ""),
            "acc_CC9311": f.get("acc_CC9311", ""),
            "acc_WH8109": f.get("acc_WH8109", ""),
            "acc_WH8102": f.get("acc_WH8102", ""),
            "acc_BL107": f.get("acc_BL107", ""),
            "acc_WH7803": f.get("acc_WH7803", ""),
        })
    out.sort(key=lambda r: (r["tier"], r["locus_block"], r["gene"] or "zz"))
    with open(DATA / "panel_final.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    t1 = sum(1 for r in out if r["tier"] == "1_annotated")
    log.info("panel_final.csv: %d markers (%d tier 1, %d tier 2), %d locus blocks",
             len(out), t1, len(out) - t1, len({r["locus_block"] for r in out}))
    log.info("wrote panel_final.csv, marker_positions.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
