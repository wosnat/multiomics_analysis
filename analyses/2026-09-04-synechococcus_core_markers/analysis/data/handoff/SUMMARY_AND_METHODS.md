# Marker genes for marine *Synechococcus* — summary and methods

Prepared 2026-09-04 for a planned search against a new Mediterranean metagenome.

---

## Executive summary

We set out to find genes that could act as fingerprints for marine
*Synechococcus*, a group of photosynthetic bacteria that is one of the main
drivers of ocean productivity. A useful fingerprint gene has to satisfy three
conditions at once: every strain of the group must carry it, each strain must
carry exactly one copy so that counting genes means counting cells, and no other
organism should carry it, so that a match is unambiguous. Searching a curated
database of 43 bacterial genomes, we found 53 genes meeting all three conditions
across the five marine *Synechococcus* strains available, and confirmed the
method works by checking that four standard reference genes behave exactly as
they should. The most informative hits are the genes for phycoerythrin, the
red pigment that distinguishes marine *Synechococcus* from its closest relative
*Prochlorococcus*; these emerged from the analysis on their own, without being
looked for, which is good evidence the method is finding real biology rather
than database artifacts. Two limitations should travel with these results. The
uniqueness test was run against 43 genomes rather than against all known
bacteria, so a match in seawater is strong evidence but not proof, and most of
the 53 genes have never been functionally characterised. We recommend a short
panel of nine genes for the first search, deliberately spread across different
parts of the genome so that no single genomic accident can invalidate the whole
result.

---

## Methods

### Data source

All gene and orthology data came from a curated *Prochlorococcus* /
*Synechococcus* multi-omics knowledge graph (release `0.0.0-dev`, built
2026-08-29; accessed through the `multiomics_explorer` Python package version
`0.1.0a4`). No sequence data or gene calls were taken from any other source.

The graph holds 48 organism nodes, of which **43 carry genes**. Eight are
*Synechococcus*-named and **17 are *Prochlorococcus***, the closest relatives
and therefore the hardest specificity test any candidate faces.

### Target organisms

Five marine picocyanobacterial *Synechococcus*, one per clade:

| Strain | Clade | Genes |
|---|---|---|
| CC9311 | I | 3038 |
| WH8109 | II | 2681 |
| WH8102 | III | 2830 |
| BL107 | IV | 2567 |
| WH7803 | V | 2590 |

A sixth strain, PCC 7002, was included in a first pass and then set aside; see
"Why five and not six" below.

### Orthology model

Each gene in the graph belongs to up to four nested ortholog groups: one
Cyanorak curated group (rank 0, covering *Prochlorococcus* and the five
picocyanobacterial *Synechococcus* only), and up to three eggNOG groups at the
*Synechococcus* (taxid 1129), Cyanobacteria (1117) and Bacteria (2) levels.
48,972 groups in total.

**Design constraint.** Membership in a genus-level group is *not* evidence of
genus-restriction. For example the gene `atp1` belongs to an 8-member
*Synechococcus*-level group and also to 17-member Cyanobacteria- and
Bacteria-level groups spanning three genera. Specificity must therefore be read
from the **broadest** group a gene belongs to, never the narrowest.

### Marker definition

We define a gene's **ortholog neighbourhood** as the union of member genes
across *every* ortholog group it belongs to, at every level and from both
sources. A gene qualifies as a marker when its neighbourhood contains exactly
one gene from each target strain and nothing else. Concretely, three tests:

1. **Core** — present in all five target strains.
2. **Single-copy** — exactly one gene per strain within the neighbourhood.
3. **Specific** — zero members in any of the other 38 gene-bearing genomes.

Neighbourhoods were closed iteratively: candidate genes found from narrow groups
were re-queried for *all* their group memberships, and any newly seen group was
expanded, until no new group appeared. Group membership was always expanded
**without an organism filter**, since filtering there would hide non-target
members and manufacture false specificity.

### Filter funnel

| Stage | Count |
|---|---|
| Ortholog groups enumerated | 48,972 |
| Groups with 6 or fewer member organisms | 31,630 |
| Groups whose whole roster is inside the target set | 6,455 |
| Candidate genes | 6,126 |
| Rejected: ortholog outside the target strains | 4,023 |
| Rejected: missing from at least one target strain | 2,039 |
| Rejected: multi-copy in at least one target strain | 64 |
| **Markers passing all three tests** | **53** |

### Statistics

None, deliberately. Every step is exact set membership over a closed, fully
enumerated graph. There is no sampling, no estimation and no null model, so a
p-value would carry no meaning. Counts and the filter funnel are reported
instead.

### Validation

Four universally conserved single-copy housekeeping genes — **gyrB, recA, rpoB,
dnaG** — were used as a pre-registered two-sided control. Both sides passed:

- Each resolved to **exactly one locus tag in every target strain**, confirming
  the membership census works.
- **None appeared in the marker table**, confirming the neighbourhood closure
  reaches the broad Bacteria-level groups rather than truncating. A truncating
  closure would have inflated every count, and this is the test that rules it
  out.

### Why five strains and not six

A first pass included PCC 7002, a coastal euryhaline strain, and returned
**one** marker rather than 53. A leave-one-out diagnostic attributed this to
PCC 7002 specifically: of 70 ortholog neighbourhoods covering five of the six
strains and nothing outside them, PCC 7002 was the missing strain in **69**.
Dropping any of the other five instead yields zero or one marker. PCC 7002 also
carries no Cyanorak curated groups at all.

### Paralogy re-check

The single-copy test above operates within the ortholog neighbourhood, so it
catches any duplicate sharing a group but cannot see a paralog placed in a
different group. We re-tested with Pfam domain content, a signal independent of
the ortholog groups: for each marker gene, how many genes in the *same* genome
carry the same Pfam entry.

Results are reported in the `domain_paralog_check` column as three values, not a
boolean, because a gene with no Pfam annotation was never tested and must not be
recorded as clean. Across the 49 panel markers: **9 shares_domain, 9 clean, 35
untested_no_pfam**. Pfam covers only 76 of 271 marker gene instances, so this
check is silent for most of the panel. The flagged nine split into two kinds. The phycobiliprotein hits
(mpeA, mpeB, cpeR, apcE) are probably benign, since every phycobiliprotein in
the genome carries that same fold and the check cannot distinguish a gene family
from a gene duplication. The `hli` hits are real: high-light inducible proteins
are a genuinely expanded family, so each `hli` row is a single-copy *ortholog
group* rather than a single-copy gene. Both `hli` markers were subsequently
dropped.

### Representative selection (the medoid)

Amino-acid sequences were exported for all 244 marker gene instances that carry
one, and an all-versus-all **DIAMOND blastp** (`--very-sensitive`, e-value 1e-3)
was run over the set. For each marker, the **medoid** is the member with the
highest mean percent identity to its siblings, i.e. the sequence closest to the
centre of the group. It is the least biased single query for finding a strain
present in none of the five reference genomes.

No single strain dominates the medoid, which is the direct argument against
picking one reference strain for every marker:

| Strain | Clade | Markers where it is the medoid |
|---|---|---|
| WH8109 | II | 18 |
| WH8102 | III | 16 |
| BL107 | IV | 7 |
| WH7803 | V | 6 |
| CC9311 | I | 5 |

Group tightness varies widely. Median mean identity to siblings is **64.9%**;
six markers sit at or above 70% minimum pairwise identity, while **22 fall below
50%** and three contain a sibling pair DIAMOND could not align. For those loose
groups a single query will very likely miss distant relatives, and the
`*_all_orthologs.faa` file should be used instead of `*_medoid.faa`.

The same all-versus-all also exposed cross-marker similarity. Five marker pairs
align to each other; the strongest are two unannotated pairs at 50–56% identity,
which should be treated as one marker each rather than two.

### Genomic independence (locus blocks)

Every marker was placed on the WH8102 genome (CC9311 as fallback) and grouped
into **locus blocks**, markers within 30 kb of one another counting as one
block. The 53 markers span **22 blocks**, but they are unevenly distributed: one
block, `B19`, holds nine of them and is the phycobilisome gene cluster. Within
12 kb of `mpeA` sit cpeA, cpeB, cpeC, cpeE, cpeS, cpeT, cpeY, cpeZ, mpeC, mpeD,
mpeU, mpeY, cpcA, cpcB, pebA and pebB.

The term `locus_block` is ours, not standard usage: markers were sorted by
chromosome coordinate and a new block started wherever the gap to the previous
marker exceeded 30 kb. The 30 kb cutoff is a judgement call, generous enough to
hold a whole cluster and tight enough that unrelated regions do not merge.

Blocks holding more than one marker:

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

The remaining 14 blocks hold one marker each. Inside B19 the packing is tight:
mpeB and mpeA are 46 bp apart, cpeR and unk7 are adjacent, and the whole run of
nine spans under 20 kb.

This matters for panel design. Markers sharing a block share a promoter region,
a regulatory input and an evolutionary fate; they are not independent
observations. The short panel therefore deliberately mixes `B19` markers with
markers drawn from four other blocks.

### Panel construction

Four markers were dropped at the researcher's request (`kaiA`, both `hli` rows,
`apcE`), leaving 49. Of these, five are annotated — mpeA, mpeB, cpeR, cpeU,
unk7 — and **all five lie in block `B19`**. The short panel adds the
highest-minimum-identity unannotated marker with a complete accession set from
each of four other blocks: `m034` (B08), `m027` (B12), `m042` (B04), `m038`
(B06).

| List | Markers | Blocks |
|---|---|---|
| Short | 9 | B19, B08, B12, B04, B06 |
| Full | 49 | 21 |

### Limitations

1. **Specificity was tested against 43 genomes, not against all bacteria.** A
   metagenome carries far more diversity than the reference set. A hit is strong
   evidence, not proof. An external database search is still required before any
   of these is used as a validated marker.
2. **Most markers are uncharacterised.** 44 of the original 53 are hypothetical
   or uncharacterised proteins. They are candidates.
3. **Pigment type varies in wild populations.** Phycoerythrin-II genes are not
   carried by every marine *Synechococcus* pigment type, so a panel resting on
   the phycobilisome locus will systematically under-count some lineages. All
   five reference genomes carry the locus, so the knowledge graph cannot
   quantify this risk.
4. **Phycobiliproteins share a fold.** mpeA, mpeB and cpeR align to cpeA, cpeB,
   apcA and other phycobiliproteins. Use a strict identity threshold or a
   reciprocal best-hit check.
5. **Sequence and accession coverage is incomplete.** 244 of 265 marker gene
   instances carry both an amino-acid sequence and an NCBI RefSeq protein
   accession; 21 carry neither. Consequently the full panel yields 48 medoid
   sequences rather than 49, and 226 ortholog sequences rather than 245.
6. **`unk7` is a weak query.** At 73 residues with 48% minimum pairwise
   identity, it is both short and divergent. It is included in the short panel
   with a caution flag rather than silently dropped.

### Reproducibility

Scripts, logs and intermediate data are in the source repository under
`analyses/2026-09-04-synechococcus_core_markers/analysis/`. The pipeline is
`01_build_markers.py` (marker discovery), `02_diagnose_empty.py` (the PCC 7002
diagnostic), `03_paralog_check.py` (Pfam re-check),
`04_pick_blast_representative.py` (medoid selection),
`05_handoff_accessions.py`, `06_panel_after_drops.py` (drops and locus blocks)
and `07_export_handoff.py` (this handoff). Every script logs its own filter
funnel.

### File index

See `README.md` in this folder for the file-by-file listing and the metadata
column definitions.
