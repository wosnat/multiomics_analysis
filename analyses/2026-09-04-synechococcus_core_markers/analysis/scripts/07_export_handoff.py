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
                "domain_paralog_check": f.get("domain_paralog_check", ""),
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

## Metadata columns — data dictionary

### Read this first: most columns describe the MARKER, not the row

Each metadata file has one row per **marker x strain**, so a five-strain marker
occupies five rows. **12 of the 20 columns are marker-level and repeat
identically on all five of its rows.** Only eight vary from row to row. If you
filter or count rows without collapsing on `marker_id` first, every marker-level
statistic is counted five times.

| Varies per row | Constant across a marker's rows |
|---|---|
| `strain`, `clade`, `organism`, `locus_tag`, `protein_accession`, `protein_length_aa`, `sequence_available`, `is_medoid` | `marker_id`, `tier`, `gene_name`, `product`, `gene_category`, `locus_block`, `mean_identity_to_siblings_pct`, `min_pairwise_identity_pct`, `domain_paralog_check`, `cross_aligns_another_marker`, `caution`, `ortholog_groups` |

### Column by column

| Column | Meaning | Watch out for |
|---|---|---|
| `marker_id` | Our arbitrary identifier, `m000`-`m052`. Stable across every file in this bundle. | Carries no biological meaning. The number is a row index, not a rank. |
| `tier` | `1_annotated` = informative gene name and a non-hypothetical product. `2_exploratory` = everything else. | Our label. Tier 2 markers are candidates, not validated markers. |
| `gene_name` | Consensus gene name from the ortholog group. Blank when the group has none. | **`unk4`, `unk7`, `unk9`, `unk11`, `unk12` are placeholders, not real gene names.** They are Cyanorak labels for uncharacterised genes in the phycobilisome region. Do not read them as characterised genes. |
| `product` | Consensus product description from the ortholog group. | "conserved hypothetical protein" and "uncharacterized conserved membrane protein" mean no functional evidence. |
| `gene_category` | Cyanorak functional role category. | Assigned by Cyanorak curation, not by us. "Unknown" is common here. |
| `strain` | Short strain label, one of the five. | |
| `clade` | Marine picocyanobacterial clade of that strain: I, II, III, IV, V. | Clade of the *reference strain*, not of anything you will find in the metagenome. |
| `organism` | Full organism name as stored in the knowledge graph. | |
| `locus_tag` | Gene identifier in that genome. | **Naming is mixed within a single strain.** WH8102 alone carries three styles: `SYNW0561`, `TX72_RS12145`, `S8102_22071`, from different annotation rounds. All valid; do not assume one prefix per genome. |
| `protein_accession` | NCBI RefSeq protein accession (`WP_...`). | **Blank on 19 of 245 rows** in the full panel. Those genes have neither accession nor sequence. |
| `protein_length_aa` | Length of the stored amino-acid sequence. | Blank wherever no sequence is stored. |
| `sequence_available` | Whether the graph holds an amino-acid sequence for this gene. | `False` on 19 of 245 rows. Those rows appear in the metadata but in no FASTA file. |
| `is_medoid` | `True` on the one ortholog chosen as that marker's representative query. | Exactly one `True` per marker for 48 of 49. Marker `m048` has **no** medoid, too few of its orthologs have sequences. |
| `locus_block` | A run of markers close together on the chromosome. See below. | Blank for 3 markers whose anchor gene has no stored coordinates. |
| `mean_identity_to_siblings_pct` | The medoid's mean percent identity to the marker's other orthologs. | Marker-level. **`0.0` means DIAMOND found no alignment at all, not "0% identical"** (marker `m008`). Blank means no medoid could be computed (`m048`). |
| `min_pairwise_identity_pct` | Lowest percent identity between any two orthologs of the marker. A tightness score. | Marker-level. Below 50% means one query will probably miss distant relatives, so prefer `_all_orthologs.faa`. Same `0.0` and blank caveats. |
| `domain_paralog_check` | Independent Pfam re-test for paralogs. See below. | Three values, not a boolean. `untested_no_pfam` is **not** a clean result. |
| `cross_aligns_another_marker` | `True` when this marker's sequences align to a *different* marker in the panel. | Our label. Markers that align to each other cannot be told apart in metagenomic reads, so treat such a pair as one marker. Five pairs affected. |
| `caution` | Free-text warning, blank for most markers. | Currently used only for `unk7`. |
| `ortholog_groups` | The ortholog groups this marker is built from, semicolon-separated. | Spans both sources and up to four taxonomic levels, e.g. `cyanorak:CK_...;eggnog:...@1129;eggnog:...@1117;eggnog:...@2`. The Bacteria-level group (`@2`) is the one carrying the specificity claim. |

**What `locus_block` means.** Our own label, not standard terminology. We placed
every marker on the WH8102 chromosome, sorted by coordinate, and started a new
block wherever the gap to the previous marker exceeded 30 kb. So a block is
simply a run of markers sitting close together.

It exists to answer one question: are two markers independent evidence? Genes
packed into 20 kb are usually one operon or one functional island. They share
promoters and regulation, and they tend to be gained, lost or replaced together,
so counting them separately overstates the evidence. Markers in *different*
blocks can fail or survive independently. The 30 kb cutoff is a judgement call,
generous enough to hold a whole cluster and tight enough that unrelated regions
do not merge.

Blocks holding more than one marker, across all 53 original markers:

| Block | Markers | Span | Contents |
|---|---|---|---|
| B19 | 9 | 19.7 kb | unk4, cpeR, unk7, unk9, mpeB, mpeA, unk11, unk12, cpeU |
| B13 | 8 | 66.9 kb | hli plus 7 unannotated |
| B14 | 5 | 10.5 kb | all unannotated |
| B04 | 3 | 16.3 kb | kaiA plus 2 unannotated |
| B06 | 3 | 1.4 kb | all unannotated |
| B08 | 3 | 17.7 kb | all unannotated |
| B12 | 3 | 21.2 kb | all unannotated |
| B11 | 2 | 21.2 kb | all unannotated |

The other 14 blocks hold one marker each. Inside B19 the packing is tight: mpeB
and mpeA are 46 bp apart and the whole run of nine spans under 20 kb.

**What `domain_paralog_check` means.** Our label. The single-copy test used to
build these markers works inside the ortholog groups, so it catches a duplicate
sharing a group with the marker but cannot see a paralog assigned to a different
group. This column is an independent re-test using Pfam domains: for each marker
gene we counted how many *other* genes in the same genome carry the same Pfam
entry.

| Value | Meaning | Panel count |
|---|---|---|
| `clean` | has Pfam annotation, no other gene in that genome shares a domain | 9 |
| `shares_domain` | another gene in at least one of the five genomes carries the same Pfam entry | 9 |
| `untested_no_pfam` | no Pfam annotation, so the check could not run — **not** a clean result | 35 |

`shares_domain` is a flag for review, not a verdict. A shared domain is far
weaker evidence than a shared ortholog group, and it catches two different
things. Phycobiliproteins (mpeA, mpeB, cpeR) trip it because every
phycobiliprotein in the genome carries the same fold, which is a gene family
rather than a duplication and is probably benign. The `hli` markers tripped it
for a real reason, since high-light inducible proteins are a genuinely expanded
family; both were dropped. Pfam reaches only 76 of 271 marker gene instances, so
this check is silent for most of the panel.

**What `is_medoid` means.** The medoid is the ortholog with the highest mean
percent identity to the marker's other four, computed by all-versus-all DIAMOND
blastp (`--very-sensitive`). It is the sequence closest to the centre of the
group, and therefore the least biased single query for finding a strain present
in none of the five reference genomes. No single strain wins the medoid across
markers, which is why the representative is chosen per marker rather than by
picking one reference strain.

### Extra columns in `panel_final.csv` (source repository, not this bundle)

`accessions_available` counts how many of the five strains have an accession
(5 for 42 markers, 4 for 6, fewer for 5). `anchor_strain` and `anchor_start` are
the genome and coordinate used to assign the locus block.
""")
    log.info("wrote %s", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
