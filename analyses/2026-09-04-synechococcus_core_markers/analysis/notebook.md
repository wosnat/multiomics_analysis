# Analysis milestone — notebook

**Date:** 2026-09-04
**KG:** `0.0.0-dev`, built 2026-08-29, explorer `0.1.0a4`, `kg_release_info` verdict `ok`
**Scripts:** `scripts/01_build_markers.py`, `scripts/02_diagnose_empty.py`

## Context

Executed against `proposal.md`. Two departures from the methodology, both at
researcher instruction under a time constraint, both recorded in
`gaps_and_friction.md`:

1. The pre-registered expected-negative class was dropped.
2. The fresh-context critic pass on the proposal was skipped, and the methods
   and analysis milestones were collapsed into one.

## What ran

`01_build_markers.py` builds each candidate gene's **ortholog neighbourhood**,
the union of member genes across every ortholog group the gene belongs to at
every level and from both sources, then applies three tests: core, single-copy,
and no member outside the target strains. `02_diagnose_empty.py` explains the
near-empty six-strain result.

Run twice: all six target strains, then with PCC 7002 dropped
(`--drop "Synechococcus PCC 7002"`).

## Results — filter funnel

| Stage | Six strains | Five strains (no PCC 7002) |
|---|---|---|
| Ortholog groups enumerated | 48972 | 48972 |
| Groups with `organism_count` <= 6 | 31630 | 31630 |
| Groups whose roster is a subset of the targets | 8262 | 6455 |
| Candidate genes | 8249 | 6126 |
| Rejected, ortholog outside the targets | 5543 | 4023 |
| Rejected, missing from at least one target strain | 2698 | 2039 |
| Rejected, multi-copy in at least one target strain | 2 | 64 |
| **Markers passing all three tests** | **1** | **53** |

All `[KG]`.

## Results — validation set (two-sided, as pre-registered)

Six-strain run, from `data/validation.csv` `[KG]`:

| Gene | Strains hit | Single-copy in each | Appears in marker table |
|---|---|---|---|
| gyrB | 6 | yes | no |
| recA | 6 | yes | no |
| rpoB | 6 | yes | no |
| dnaG | 6 | yes | no |

**Both sides pass.** All four housekeeping genes are present exactly once in
each of the six strains, so the membership census is working. None appears in
the marker table, so the neighbourhood closure is reaching the broad
Bacteria-level groups rather than truncating. The pre-registered failure mode
that would have inflated every count did not occur.

Note on reading `data/validation_no_7002.csv`: its `core_all_six` column is
hardcoded to test for six strains, so it reads `False` in the five-strain run
while `strains_hit` is 5. That is a label artifact, not a failure.

## Results — why six strains yields one marker

From `02_diagnose_empty.py` `[KG]`. Of 1941 distinct neighbourhoods that
contain nothing outside the six target strains, the number of target strains
each one actually covers:

| Strains covered | Neighbourhoods |
|---|---|
| 6 | 2 |
| 5 | 70 |
| 4 | 53 |
| 3 | 93 |
| 2 | 164 |
| 1 | 1559 |

Among the 70 near-misses covering five of six, the missing strain is
**PCC 7002 in 69 cases** and WH8109 in 1.

Leave-one-out marker counts `[KG]`:

| Strain dropped | Markers |
|---|---|
| PCC 7002 | 53 |
| WH8109 | 1 |
| CC9311, WH8102, BL107, WH7803 | 0 each |
| none, all six | 1 |

One of the two six-strain neighbourhoods was rejected for being multi-copy:
CC9311 contributes two genes, `sync_1297` and `sync_1299`.

## The single six-strain marker

`data/markers.csv`, one row `[KG]`:

- Groups: `cyanorak:CK_00001639`, `eggnog:1H130@1129`, `eggnog:1GA59@1117`,
  `eggnog:330UC@2`
- Product: uncharacterized conserved membrane protein; Cyanorak category
  Stress response and adaptation; no gene name
- Locus tags: `sync_2209` (CC9311), `Syncc8109_2196` (WH8109), `SYNW0561`
  (WH8102), `BL107_16315` (BL107), `SynWH7803_1952` (WH7803),
  `SYNPCC7002_A1551` (PCC 7002)

Its Bacteria-level group `eggnog:330UC@2` contains exactly these six genes and
nothing else, which is why it survives.

## Results — the 53 five-strain markers

`data/markers_no_7002.csv`. 9 of 53 carry an informative gene name and a
non-hypothetical product `[KG]`. The named ones:

| Gene | Product | Category |
|---|---|---|
| mpeA | C-phycoerythrin class II, alpha chain | Photosynthesis |
| mpeB | C-phycoerythrin class II, beta chain | Photosynthesis |
| cpeR | phycoerythrin operon regulator | Photosynthesis |
| cpeU | putative phycoerythrobilin:phycoerythrin lyase | Photosynthesis |
| apcE | phycobilisome core-membrane linker polypeptide (Lcm) | Photosynthesis |
| kaiA | circadian clock protein KaiA | Cellular processes |
| hli (x2) | high light inducible protein | Stress response and adaptation |
| unk7 | nif11-like leader peptide domain protein | Unknown |

The remaining 44 are uncharacterized or hypothetical, most of them annotated as
conserved membrane or secreted proteins.

## Surprises

**The phycoerythrin cluster came out on its own.** mpeA, mpeB, cpeR, cpeU and
apcE were not seeded, named, or searched for. They fell out of a pure
set-membership filter. `[interpretation]` Phycoerythrin is the pigment that
distinguishes marine *Synechococcus* from *Prochlorococcus*, which uses
divinyl-chlorophyll instead, so a filter asking for genes present in every
marine *Synechococcus* and absent from all 17 *Prochlorococcus* genomes
recovering the phycoerythrin machinery is the outcome a working method should
produce. This is the strongest evidence in the run that the pipeline is finding
biology rather than annotation artifacts.

**The dropped expected-negative would have been wrong.** The classes proposed
in `proposal.md` and then dropped at researcher request were the high-light
inducible protein family and the clade-variable phycobilisome rod genes. Both
appear in the 53. Had that check been retained it would have fired, and it
would have been a false alarm: the proposal's reasoning about those two classes
was mistaken. Dropping it was the right call for a reason neither side had at
the time.

**Group-specific is not family-specific.** The two hli hits are ortholog groups
whose members sit only in the five strains. The hli *family* is present in
*Prochlorococcus*, where it is expanded to many paralogs. So these rows say a
particular hli ortholog group is restricted to marine *Synechococcus*, not that
*Prochlorococcus* lacks hli genes. Any downstream use has to respect that
distinction. `[interpretation]`

## Falsifiability check, as pre-registered

The proposal named two results that would mean the method found nothing real.

1. **Empty table.** The six-strain run returns 1 marker, which is close enough
   to the empty condition to be reported as a bounded negative rather than a
   marker panel. It is not an artifact: the diagnostic shows a specific,
   attributable cause, PCC 7002, not a broken filter.
2. **Dominated by hypothetical proteins.** The five-strain table is 44 of 53
   uncharacterized, so this condition **is met on the surface**. It is not
   fatal, because the 9 annotated rows are a coherent, biologically expected
   set rather than scattered noise, and because genes restricted to one genus
   are expected to be under-annotated. It does mean the 44 unnamed rows carry
   less weight and should not be presented as validated markers.

## Decisions

1. **Report the six-strain result as a bounded negative, not a panel.** One
   marker is a real finding, and it is not a usable marker panel.
2. **Report the 53 five-strain markers as the usable output**, with PCC 7002
   named as the reason the six-strain set collapses. The researcher chose all
   six; the five-strain table is reported alongside rather than instead.
3. **Do not present the 44 unannotated rows as markers.** They are candidates.
   The 9 annotated rows carry the confidence.
4. **No candidate is marker-ready.** Specificity here means absence from 43 KG
   genomes, not from bacteria. An external database search is required before
   any of these is used.

## Advance rationale

The three pre-registered tests were applied, the validation set passed on both
sides, and the falsifiability check was run and reported honestly, including
the condition that was partially met. The near-empty six-strain result has an
identified cause rather than an unexplained one.

Not done, and gating any claim beyond "candidate": the critic pass, the
external specificity check, and a sequence-level review of the 44 unannotated
rows.

---

## Follow-up — is every marker single-copy in its genome?

Researcher question, 2026-09-04. Script: `scripts/03_paralog_check.py`,
output `data/paralog_check.csv`.

**What the pipeline actually guaranteed.** One gene per strain across the
*ortholog neighbourhood*, the union of every group the marker belongs to. Any
paralog sharing a group with the marker, including the broad Bacteria-level
group, forces that strain to contribute two genes and the row is rejected. The
test did real work: 64 neighbourhoods rejected as multi-copy in the five-strain
run, 2 in the six-strain run `[KG]`. What it cannot see is a paralog assigned
to a *different* ortholog group, or one with no group at all.

**Independent re-test.** Pfam domain content, a signal not derived from the
ortholog groups. For each marker gene, count how many genes in the same genome
carry the same Pfam entry.

| | Count |
|---|---|
| Marker gene instances tested (marker x strain) | 271 |
| Instances carrying any Pfam entry | 76 |
| Of those, no other gene in the genome shares a domain | 39 |
| Of those, another gene in the genome shares a domain | 37 |
| Instances with no Pfam annotation, untestable this way | 195 |

Rolled up to the 54 markers `[KG]`:

| Verdict | Markers |
|---|---|
| Clean, no domain-sharing gene in any strain | 9 |
| Shares a domain with another gene in at least one strain | 9 |
| No Pfam annotation anywhere, untestable | 36 |

The 9 flagged are apcE, mpeA, mpeB, cpeR, both hli rows, unk7, unk11, and one
unnamed nif11-like leader peptide protein.

**Reading the flags.** `[interpretation]` A shared Pfam domain is weaker
evidence than a shared ortholog group and the two flagged classes differ:

- **Phycobiliproteins are a false positive.** mpeA, mpeB, cpeR and apcE share
  the phycobilisome protein fold with every other phycobiliprotein in the
  genome (cpeA, cpeB, apcA, apcB and so on). They are distinct genes in
  distinct ortholog groups, not duplicates of each other. The domain check
  cannot separate a gene family from a gene duplication.
- **hli is a true multi-copy family.** The high-light inducible proteins are
  genuinely expanded in these genomes. Each hli row here is a single-copy
  *ortholog group*, not a single-copy gene family. This restates the
  group-specific versus family-specific caution above, now with a number
  behind it.

**Limit of this check.** Pfam covers only 76 of 271 marker gene instances, 28
percent, so it is silent on two thirds of the table `[gap]`. A definitive
answer needs an all-versus-all sequence comparison within each genome, which
the KG can feed via `gene_aa_sequence` but which was not run.

**Answer.** No, not all 53 are demonstrably single-copy in the genome sense.
Nine are clean on an independent check, nine carry a domain-level duplicate of
which the phycobiliprotein cases are probably benign, and 36 are untested
because they have no Pfam annotation.

---

## Follow-up — choosing query sequences for a Mediterranean metagenome search

Researcher question, 2026-09-04. Scripts: `scripts/04_pick_blast_representative.py`
(superseded), `scripts/05_handoff_accessions.py`.

### The medoid plan failed, and its output must not be used

The intended method was to pick, per marker, the member with the highest mean
percent identity to its four siblings, so the query sits at the centre of the
group's sequence space rather than carrying one strain's idiosyncrasies. That
requires sequences. The KG stores an amino-acid sequence for only **50 of 265**
marker gene instances `[KG]`, and coverage is severely strain-skewed:

| Strain | Clade | Genes | With stored AA sequence | With protein accession |
|---|---|---|---|---|
| CC9311 | I | 53 | 37 | 51 |
| WH8109 | II | 53 | 0 | 48 |
| WH8102 | III | 53 | 1 | 50 |
| BL107 | IV | 53 | 0 | 48 |
| WH7803 | V | 53 | 12 | 47 |
| **Total** | | **265** | **50** | **244** |

The medoid run therefore covered 11 markers and "chose" CC9311 for 10 of them,
purely because CC9311 is the only strain with sequences. That is an artifact of
sequence coverage, not a similarity result. `data/blast_representatives.csv` is
retained for reproducibility and **its recommendation is void**. `[gap]`

### What the handoff is instead

Protein accessions, 244 of 265 available and evenly spread, all NCBI RefSeq
`WP_` identifiers `[KG]`. 42 of 53 markers have a complete set of five.
`data/handoff_accessions.csv` (wide, five accessions per marker) and
`data/handoff_long.csv` (one row per marker x strain).

### Cross-marker alignment

All-versus-all DIAMOND over the 50 available sequences found three marker pairs
that align to each other `[KG]`:

| Pair | Max identity |
|---|---|
| m003 vs m004, both unannotated | 55.9% |
| m029 vs m041, both unannotated | 50.0% |
| m006 (mpeA) vs m007 (mpeB) | 28.9% |

`[interpretation]` The mpeA/mpeB pair is expected: the alpha and beta chains of
a phycobiliprotein are homologous, and 28.9% is low enough not to confound a
strict search. The two unannotated pairs at 50 to 56% are near-duplicates of
each other, so one of each pair should be dropped rather than counted as two
independent markers.

### Recommendation

**Send all five accessions per marker, not one.** Two reasons. The medoid
cannot be computed from this KG, so any single choice would be arbitrary. And
for recruitment against an unknown Mediterranean population, five queries
spanning clades I to V cost nothing and materially improve recall over one.

If a single representative is forced: **BL107**, clade IV, on the grounds that
it is a Mediterranean isolate from Blanes Bay `[interpretation]` — the KG
records no isolation source `[gap]`. Second choice **WH8102**, the
best-annotated of the five (2777 Cyanorak-grouped genes, the highest) and the
strain whose SYNW locus tags the literature uses.

**Tiering the 53 markers for the collaborators:**

- **Tier 1, six annotated and defensible:** mpeA, mpeB, cpeR, cpeU, apcE,
  kaiA. The phycoerythrin set is the strongest of these, since phycoerythrin is
  what distinguishes marine *Synechococcus* from *Prochlorococcus*.
- **Excluded, two:** both hli rows. The family is expanded in
  *Prochlorococcus*, so hits will not be diagnostic.
- **Tier 2, exploratory:** the remaining unannotated markers with a complete
  accession set, minus one of each near-duplicate pair. Not validated markers.

**Caveats to pass on with the file.** Specificity was established against the
43 gene-bearing genomes in this KG, not against bacteria; a metagenome carries
far more diversity, so a hit is not proof of marine *Synechococcus*.
mpeA, mpeB, cpeR and apcE share the phycobilisome fold with every other
phycobiliprotein, so a strict identity threshold or a reciprocal best-hit check
is needed. Two markers lack one accession each: apcE has no CC9311 accession,
kaiA has none for WH8109.
