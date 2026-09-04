"""Export the collaborator handoff: short and full marker lists.

Produces, under data/handoff/:

  SHORT list (9 markers) — the recommended panel.
    5 annotated survivors of the researcher's drops (mpeA, mpeB, cpeR, cpeU,
    unk7), all in the phycobilisome locus block B19, plus 4 unannotated
    candidates chosen from four DIFFERENT locus blocks so the panel does not
    rest on a single operon.

  FULL list (49 markers) — everything left after the drops of kaiA, hli, apcE.

For each list, three files:
  *_medoid.faa       one sequence per marker, the medoid (most central of the
                     five orthologs). Use when one query per marker is wanted.
  *_all_orthologs.faa  all available orthologs, up to five per marker. Better
                     recall against an unknown population.
  *_accessions.txt   plain NCBI RefSeq protein accessions, one per line.
  *_metadata.csv     one row per marker x strain: strain, clade, gene, product,
                     locus tag, accession, protein length, medoid flag, locus
                     block, and the quality flags.

Inputs : data/panel_final.csv, data/markers_no_7002.csv,
         data/blast_representatives.csv, data/marker_positions.csv,
         data/handoff_accessions.csv
Outputs: data/handoff/ (see above) + data/handoff/README.md
Usage  : uv run python analysis/scripts/07_export_handoff.py
"""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path

from multiomics_explorer import GraphConnection, gene_aa_sequence

DATA = Path(__file__).resolve().parents[1] / "data"
OUT = DATA / "handoff"
log = logging.getLogger("export")

STRAINS = [
    ("CC9311", "Synechococcus CC9311", "I"),
    ("WH8109", "Synechococcus WH8109", "II"),
    ("WH8102", "Synechococcus WH8102", "III"),
    ("BL107", "Synechococcus sp. BL107", "IV"),
    ("WH7803", "Synechococcus WH7803", "V"),
]

# The short panel: 5 annotated survivors + 4 spread candidates from other blocks.
SHORT_ANNOTATED = ["mpeA", "mpeB", "cpeR", "cpeU", "unk7"]
SHORT_SPREAD = ["m034", "m027", "m042", "m038"]
# Markers carrying a caution, surfaced in the metadata rather than silently dropped.
CAUTION = {
    "unk7": "73 aa and 48% minimum pairwise identity; short and divergent, weak query",
}


def setup() -> None:
    log.setLevel(logging.INFO)
    OUT.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(DATA / "07_export_handoff.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def main() -> int:
    setup()
    panel = list(csv.DictReader(open(DATA / "panel_final.csv")))
    markers = {f"m{i:03d}": m for i, m in
               enumerate(csv.DictReader(open(DATA / "markers_no_7002.csv")))}
    med = {r["marker_id"]: r for r in csv.DictReader(open(DATA / "blast_representatives.csv"))}
    flags = {r["marker_id"]: r for r in csv.DictReader(open(DATA / "handoff_accessions.csv"))}
    log.info("markers in panel_final (after drops): %d", len(panel))

    # ---- sequences. NOTE limit is explicit: the package defaults to 25. -----
    loci = []
    for mid, m in markers.items():
        for short, _f, _c in STRAINS:
            lt = (m.get(f"locus_{short}") or "").strip()
            if lt:
                loci.append(lt)
    seq: dict[str, str] = {}
    acc: dict[str, str] = {}
    with GraphConnection() as conn:
        for i in range(0, len(loci), 200):
            r = gene_aa_sequence(locus_tags=loci[i : i + 200], limit=10**6, conn=conn)
            assert r["returned"] == r["total_matching"], "paginated: raise limit"
            for x in r["results"]:
                if x.get("sequence"):
                    seq[x["locus_tag"]] = x["sequence"]
                if x.get("protein_id"):
                    acc[x["locus_tag"]] = x["protein_id"]
    log.info("sequences: %d/%d   accessions: %d/%d", len(seq), len(loci), len(acc), len(loci))

    # ---- pick the two lists --------------------------------------------------
    by_gene = {r["gene"]: r for r in panel if r["gene"]}
    by_id = {r["marker_id"]: r for r in panel}
    short_ids, seen = [], set()
    for g in SHORT_ANNOTATED:
        r = by_gene.get(g)
        if r and r["marker_id"] not in seen:
            short_ids.append(r["marker_id"]); seen.add(r["marker_id"])
        elif not r:
            log.warning("short-list gene not in panel: %s", g)
    for mid in SHORT_SPREAD:
        if mid in by_id and mid not in seen:
            short_ids.append(mid); seen.add(mid)
        elif mid not in by_id:
            log.warning("short-list marker not in panel: %s", mid)
    full_ids = [r["marker_id"] for r in panel]
    log.info("SHORT list: %d markers -> %s", len(short_ids), ", ".join(short_ids))
    log.info("FULL list : %d markers", len(full_ids))

    # ---- writers -------------------------------------------------------------
    def rows_for(mid: str):
        m, p = markers[mid], by_id[mid]
        f, mm = flags.get(mid, {}), med.get(mid, {})
        out = []
        for short, full, clade in STRAINS:
            lt = (m.get(f"locus_{short}") or "").strip()
            if not lt:
                continue
            s = seq.get(lt, "")
            out.append({
                "marker_id": mid,
                "tier": p["tier"],
                "gene_name": p["gene"],
                "product": p["product"],
                "gene_category": m.get("gene_category") or "",
                "strain": short,
                "clade": clade,
                "organism": full,
                "locus_tag": lt,
                "protein_accession": acc.get(lt, ""),
                "protein_length_aa": len(s) if s else "",
                "sequence_available": bool(s),
                "is_medoid": mm.get("recommended_locus_tag") == lt,
                "locus_block": p["locus_block"],
                "mean_identity_to_siblings_pct": mm.get("mean_identity_to_siblings", ""),
                "min_pairwise_identity_pct": mm.get("min_pairwise_identity", ""),
                "shared_domain_in_a_genome": f.get("shared_domain_in_a_genome", ""),
                "cross_aligns_another_marker": f.get("cross_aligns_another_marker", ""),
                "caution": CAUTION.get(p["gene"], ""),
                "ortholog_groups": m.get("group_ids", ""),
            })
        return out

    def write_list(name: str, ids: list[str]) -> None:
        meta = [r for mid in ids for r in rows_for(mid)]
        with open(OUT / f"{name}_metadata.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(meta[0]))
            w.writeheader(); w.writerows(meta)

        with open(OUT / f"{name}_medoid.faa", "w") as fh:
            n = 0
            for r in meta:
                if r["is_medoid"] and r["sequence_available"]:
                    label = r["gene_name"] or r["marker_id"]
                    fh.write(f">{r['protein_accession']} {r['marker_id']} {label} "
                             f"{r['strain']}|clade_{r['clade']} {r['locus_tag']} "
                             f"block_{r['locus_block']} {r['product']}\n"
                             f"{seq[r['locus_tag']]}\n")
                    n += 1
        medoid_n = n

        with open(OUT / f"{name}_all_orthologs.faa", "w") as fh:
            n = 0
            for r in meta:
                if r["sequence_available"]:
                    label = r["gene_name"] or r["marker_id"]
                    fh.write(f">{r['protein_accession']} {r['marker_id']} {label} "
                             f"{r['strain']}|clade_{r['clade']} {r['locus_tag']} "
                             f"block_{r['locus_block']} {r['product']}\n"
                             f"{seq[r['locus_tag']]}\n")
                    n += 1
        all_n = n

        accs = sorted({r["protein_accession"] for r in meta if r["protein_accession"]})
        with open(OUT / f"{name}_accessions.txt", "w") as fh:
            fh.write("\n".join(accs) + "\n")
        med_accs = sorted({r["protein_accession"] for r in meta
                           if r["is_medoid"] and r["protein_accession"]})
        with open(OUT / f"{name}_accessions_medoid.txt", "w") as fh:
            fh.write("\n".join(med_accs) + "\n")

        log.info("%s: %d markers, %d metadata rows, %d medoid seqs, %d all-ortholog seqs, "
                 "%d accessions (%d medoid)", name, len(ids), len(meta), medoid_n, all_n,
                 len(accs), len(med_accs))

    write_list("short_panel", short_ids)
    write_list("full_panel", full_ids)

    (OUT / "README.md").write_text(f"""# Marker handoff — single-copy core genes specific to marine *Synechococcus*

Generated 2026-09-04 from a Prochlorococcus/Synechococcus multi-omics knowledge
graph (release `0.0.0-dev`, built 2026-08-29).

## What these genes are

Ortholog groups holding **exactly one gene in each of five marine
*Synechococcus*** — CC9311 (clade I), WH8109 (II), WH8102 (III), BL107 (IV),
WH7803 (V) — and **no gene in any of the other 38 gene-bearing genomes** in that
knowledge graph, 17 of which are *Prochlorococcus*.

## Read this before using them

1. **Specificity was tested against 43 genomes, not against bacteria.** A
   metagenome carries far more diversity. A hit is not proof of marine
   *Synechococcus*. An external database check is still needed.
2. **The short list is concentrated in one operon.** The five annotated markers
   (mpeA, mpeB, cpeR, cpeU, unk7) all sit in locus block B19, the phycobilisome
   gene cluster. They are not five independent markers: they share a promoter, a
   regulator and an evolutionary fate. The four unannotated markers in the short
   list (m034, m027, m042, m038) were added from four other locus blocks
   specifically to break that dependence.
3. **Pigment type varies in the wild.** Phycoerythrin-II genes are not carried
   by every marine *Synechococcus* pigment type, so a panel resting on the
   phycobilisome locus will under-count some lineages. All five reference
   genomes carry the locus, so the knowledge graph cannot quantify this.
4. **Phycobiliproteins share a fold.** mpeA, mpeB, cpeR and apcE align to
   cpeA, cpeB, apcA and the other phycobiliproteins. Use a strict identity
   threshold or a reciprocal best-hit check.
5. **Most markers are unannotated.** 44 of the 53 original markers are
   hypothetical or uncharacterized proteins. They are candidates, not validated
   markers.
6. **Group tightness varies a lot.** Median mean identity among the five
   orthologs of a marker is 64.9%, and 22 markers fall below 50% minimum
   pairwise identity. For those, one query will likely miss distant relatives —
   prefer the `_all_orthologs.faa` file.

## Files

| File | Contents |
|---|---|
| `short_panel_*` | 9 markers: the 5 annotated survivors plus 4 spread candidates |
| `full_panel_*` | 49 markers: everything after dropping kaiA, hli (x2) and apcE |
| `*_medoid.faa` | one sequence per marker, the most central of its five orthologs |
| `*_all_orthologs.faa` | every available ortholog, up to five per marker (better recall) |
| `*_accessions.txt` | all NCBI RefSeq protein accessions, one per line |
| `*_accessions_medoid.txt` | just the medoid accessions |
| `*_metadata.csv` | one row per marker x strain, with every field below |

## Metadata columns

`marker_id`, `tier`, `gene_name`, `product`, `gene_category`, `strain`, `clade`,
`organism`, `locus_tag`, `protein_accession`, `protein_length_aa`,
`sequence_available`, `is_medoid`, `locus_block`,
`mean_identity_to_siblings_pct`, `min_pairwise_identity_pct`,
`shared_domain_in_a_genome`, `cross_aligns_another_marker`, `caution`,
`ortholog_groups`.

`locus_block` groups markers within 30 kb of each other on the WH8102 genome.
Markers sharing a block are physically linked and not independent.
`is_medoid` marks the ortholog with the highest mean identity to the other four,
computed by all-versus-all DIAMOND blastp (`--very-sensitive`).
""")
    log.info("wrote %s", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
