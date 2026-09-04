# Marker handoff — single-copy core genes specific to marine *Synechococcus*

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
| `SUMMARY_AND_METHODS.md` | executive summary plus the full methods write-up — **read this first** |
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

**What `locus_block` means.** It is our own label, not standard terminology.
We placed every marker on the WH8102 chromosome, sorted them by coordinate, and
started a new block whenever the gap to the previous marker exceeded 30 kb. So a
block is simply a run of markers that sit close together on the chromosome; `B19`
is the leftmost such run in coordinate order after `B01`, and so on.

It exists to answer one question: are two markers independent? Genes packed into
20 kb are usually one operon or one functional island. They share promoters and
regulation, and they tend to be gained, lost or replaced together. Counting them
as separate markers overstates how much evidence you have. Markers in *different*
blocks are far enough apart to fail or survive independently.

The 30 kb cutoff is a judgement call, not a derived threshold. It is generous
enough to hold a whole biosynthetic cluster and tight enough that unrelated
regions do not merge.
`is_medoid` marks the ortholog with the highest mean identity to the other four,
computed by all-versus-all DIAMOND blastp (`--very-sensitive`).
