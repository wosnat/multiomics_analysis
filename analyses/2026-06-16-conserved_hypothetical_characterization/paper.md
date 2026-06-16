# Characterization of 14 core conserved-hypothetical Prochlorococcus gene families

## Question

For each of the **14 core conserved-hypothetical *Prochlorococcus* ortholog
families** — the families found to be both broadly **and** prominently
differentially expressed in the selection analysis
(`analyses/2026-06-16-conserved_hypothetical_de/`,
`6_evaluate/data/handoff_shortlist.csv`, rows with `core14 = True`) — assemble a
**characterization dossier** from the knowledge graph that maximizes interpretive
power for **future omics** work.

The 14 families are treated as **14 independent entities**, not a related set: the
goal is not to find a shared pathway or module, but to give each gene family enough
KG-held context that, when it reappears in a future dataset, it can be interpreted
rather than ignored. Incidental overlaps (two families sharing a neighbor or a
co-expression cluster) are noted where they occur but are not the objective.

Each dossier pairs the family's existing **DE response fingerprint** — breadth,
prominence, and direction-by-treatment, carried forward from the selection analysis
— with everything the KG holds about it:

- **Cross-organism homologs** — homologs in *Alteromonas* or other KG organisms
  beyond *Prochlorococcus*.
- **Conserved genomic neighborhood** — the genes flanking family members, and
  whether the neighborhood is conserved across strains.
- **Co-expression / cluster membership** — which co-expression clusters members
  fall in and what characterized genes share them (guilt-by-association).
- **Ontology / domains / sequence** — GO terms, protein domains, and sequence
  features (length, membrane/secreted signals) for members and their neighbors.
- **Other derived metrics** — any KG-held per-gene derived metrics.
- **Publication mentions** — whether any source publication discusses these genes
  directly.

**Deliverable:** one reference table (one row per family, columns = the
characterization axes + the DE fingerprint) plus a readable per-family card —
built as a lookup resource for future analyses. Results are additionally surfaced
in the repo-level interactive dashboard (`dashboard/`) as a `characterization`
section that lets a researcher pick a family and view its DE fingerprint alongside
its KG characterization panels; the static paper and figures remain the source of
record.

## Background

The 14 families were selected on the **cyanorak** curated ortholog backbone, which is
**cyanobacteria-only** — its members span *Prochlorococcus* and *Synechococcus* but
never *Alteromonas* or other genera. Cross-organism reach in this KG therefore comes
from the **eggnog** ortholog groups, which a gene belongs to at several nested
taxonomic levels (Prochloraceae → Cyanobacteria → Bacteria); the broadest group's
member genera and consensus gene name are what reveal whether a "dark" family is
deeply conserved across bacteria or restricted to *Prochlorococcus*.

A coverage probe on three dark representatives plus a GroEL positive control
(`2_kg_selection/`) established that all six characterization angles return fillable
data for these families, with different yield:

- **Cross-organism homologs** discriminate sharply and can **rescue function**: the
  HesB-like family CK_00000498 resolves through its broadest eggnog group (`COG0316`)
  to **`iscA`** (iron-sulfur cluster assembly) spanning *Alteromonas*, *Pseudomonas*
  and *Shewanella*, while CK_00000141 and CK_00003473 are single-genus
  (*Prochlorococcus*) even at the Bacteria level.
- **Genomic neighborhood**, **co-expression cluster membership**, and **derived
  metrics** (pangenome Core/Flexible, expression-level class, predicted localization,
  diel rhythmicity) all return real per-gene signal.
- **Ontology** yields only uninformative functional terms for the dark genes, but
  real **sequence features** — SignalP signal-peptide scores and PSORTb localization —
  back the "secreted"/"membrane" labels.
- **Direct publication mention** is absent for the dark genes (present for the GroEL
  control), so that axis is recorded as a hit when it fires rather than expected to
  populate.

Counts and per-angle evidence are in `2_kg_selection/data/coverage_map.csv`. The KG
release is 0.1.0-alpha.6 (built 2026-06-16); the input shortlist was produced on
0.1.0-alpha.5, so every ortholog group is re-resolved fresh here.

## Methods

### Dossier schema and the convergence principle

Each family is characterized by a row in a fixed schema (frozen in
`3_analysis_framing/data/dossier_schema.csv`) with blocks for identity, the carried
DE fingerprint, cross-organism homologs, genomic neighborhood, co-expression cluster
membership, sequence/localization features, derived metrics, and direct publication
mention. The organizing principle is that **these angles are not independent facts to
be read side by side — agreement across them is the lead.** A dedicated convergence
layer captures this. Its strongest signals are (i) **phyletic profiling** — the
characterized family whose strain presence-absence pattern most closely matches the
target (co-occurrence implying functional coupling, informative only for the
variably-present families); (ii) **KG-scale co-response similarity** — correlation of
the target's fine-grained per-(experiment × timepoint) log2 fold-change vector against
characterized families, computed on shared measured datapoints and on response shape
(not on the collapsed per-treatment direction summary, and guarded against the breadth
coverage-confound); and (iii) **operon triple-convergence** — a neighbor that is
same-strand, conserved-adjacent across strains, and co-expressed. Further signals are
neighbor-and-cluster-mate overlap, neighborhood pathway coherence, homolog-context
concordance, secretion convergence (SignalP + vesicle proteome + localization + label),
and pangenome context (whether the family and its neighbors are core or flexible). The
number of independent angles that agree, not any single column, sets the confidence.

### Evidence hardness and confidence

Every field is tagged **hard** or **soft**. Hard evidence (Pfam/COG domain, SignalP
score, PSORTb localization, pangenome class, synteny conserved across strains, and
cross-angle convergence) is trusted; soft evidence — `consensus_product`, ortholog-group
`consensus_gene_name`, and cluster `functional_description` — is majority-vote
descriptive labelling about a group rather than a measured fact about the individual
gene, and is treated cautiously. Each family is assigned a lead of one or more of five
types (function-rescued, neighborhood, co-expression, surface/secreted, lineage-novelty)
with an evidence grade of high (hard evidence and/or multi-angle convergence), medium,
or low (a descriptive label alone).

### Cross-organism homologs

Because the cyanorak backbone is cyanobacteria-only, cross-organism reach is read from
eggnog ortholog groups at their broadest taxonomic level: a family is bacteria-wide,
cyanobacteria-restricted, or *Prochlorococcus*-restricted according to the genera in
that group, and where the broadest group carries a COG/gene symbol that identity is
recovered (function rescue).

### Representative strain, controls, and driving examples

Mechanistic angles (neighborhood, co-expression, sequence, derived metrics) are anchored
on one representative strain per family (MED4 where present, else the best-covered
strain), since co-expression and derived-metric data concentrate in MED4; the DE
fingerprint and homolog conservation remain family-level. GroEL (cyanorak CK_00008054)
is a positive control that must classify as a high-grade known gene; the
*Prochlorococcus*-specific family CK_00003473 is an absence control that must not be
over-called. The extraction/classification module was developed on two driving families
— CK_00000498 (a clean function-rescue) and CK_00000141 (paralogs plus neighborhood and
cluster convergence) — before application to all 14.

## Results

<!-- populated at step 5 decide -->

## Discussion

<!-- populated at step 6 decide -->

## References

<!-- resolved via list_publications as the analysis cites them -->
