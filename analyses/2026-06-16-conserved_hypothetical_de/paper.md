# Conserved hypothetical genes that are broadly differentially expressed in Prochlorococcus

## Question

Across *Prochlorococcus*, which **conserved hypothetical ortholog families** — gene
families with no assigned function but wide conservation (many orthologs) — are
**differentially expressed across many distinct conditions**, and what can the
knowledge graph tell us about them?

Operational intent (precise definitions verified/finalized in later steps):
- **Uncharacterized** = no assigned function ("hypothetical protein" / conserved
  hypothetical / lacking a functional name). Exact annotation field verified in step 2.
- **Conserved** = the ortholog family has many members (broad conservation). The
  unit of analysis is the **ortholog group**, not the single-strain locus tag.
- **Broadly responsive** = differentially expressed across many distinct
  conditions/stresses, pooled at the ortholog-family level so coverage from all
  *Prochlorococcus* strains contributes. MED4 supplies most of the condition
  breadth; other strains test whether the response generalizes.
- **What can we learn** = the characterizing evidence the KG holds — cross-organism
  homologs, conserved genomic neighborhood, co-expression cluster membership, the
  ontology of neighbors / co-expressed genes, and the response-profile fingerprint
  across conditions.

## Background

The KG (release 0.1.0-alpha.5) holds **91 differential-expression experiments**
profiling *Prochlorococcus*, spanning 10 strains and a wide range of perturbations
(carbon, nitrogen, light, phosphorus, iron, viral infection, coculture, diel cycle,
growth phase), across RNAseq, microarray, and proteomics platforms. These
experiments come from 33 publications. MED4 dominates (41 experiments); most other
strains have far fewer, so multi-condition response breadth is concentrated in a
small number of well-studied strains.

"Uncharacterized" is operationalized as `Gene.annotation_quality <= 1` — the KG's
0–3 encoding of annotation evidence, where 0 (`no_evidence`) and 1
(`catch_all_only`) correspond to genes whose only product description is a
catch-all term ("hypothetical protein", "conserved hypothetical protein",
"uncharacterized conserved membrane protein"). Across *Prochlorococcus*, 10,130
genes meet this bar.

Conservation is measured on the **cyanorak** curated ortholog backbone (the
cyanobacteria-purpose-built grouping), which spans 17 of the 19 *Prochlorococcus*
genome strains in the KG. Of 5,732 cyanorak ortholog groups with a
*Prochlorococcus* member, 2,787 are mostly hypothetical (≥80% of their
*Prochlorococcus* members at AQ ≤ 1). Their strain coverage is bimodal: ~1,400 are
single-strain novelties, while a sharp core of **50 groups is present in all 17
strains** — maximally conserved yet functionally dark. This core, and the broader
conserved tail, is the candidate pool the analysis targets.

References for the experiments and publications cited here are enumerated in
`2_kg_selection/data/publications.csv` and resolved in the References section as
the analysis cites them.

## Methods

### Selection

Candidate ortholog families are cyanorak curated groups in which **≥80% of the
*Prochlorococcus* members carry no informative annotation** (AQ ≤ 1) and which are
**conserved across many strains** of the 17-strain cyanorak backbone, reported in
two tiers: *core* (≥14/17 strains) and *broad* (≥9/17). This yields 245 broad
families, of which 97 are core and 50 are present in all 17 strains.

Differential expression is pooled over the **74 gene-DE *Prochlorococcus*
experiments** (RNAseq / microarray / proteomics; metabolomics and
compartment-partitioning contrasts excluded) spanning **13 treatment types**.
All experiments are used regardless of `table_scope`; the resulting limitation
(significant-only tables lack a tested-but-flat denominator) is carried as a
caveat rather than gating the analysis.

### Response metric

For each family, member-level DE is retrieved with
`differential_expression_by_ortholog`, scoped to *Prochlorococcus* and the pooled
experiments, and aggregated to two independent axes:

- **Breadth** — the number of distinct treatment types in which at least one member
  is significantly differentially expressed in at least one timepoint of at least
  one experiment (0–13).
- **Prominence** — best DE rank reached in any experiment, largest |log2 fold
  change|, and the count of significant member×experiment×timepoint datapoints.

Direction (up / down / mixed) is tracked per treatment and overall. Families are
ranked primarily by breadth and secondarily by prominence.

### Controls

The metric was validated on characterized MED4 genes before application: the
broad-stress chaperone-class and high-light-inducible genes versus a
phosphate-specific marker and a housekeeping chaperone paralog. The breadth axis
correctly separated broad responders (*hli*, 5 treatment types) from narrow ones
(*htpG*, 1; *dnaK1*, 0), and the phosphate marker *pstS* (prominent in phosphorus,
moderate breadth) confirmed that breadth and prominence are independent and must be
reported separately.

## Results

<!-- Populated from step 5. -->

## Discussion

<!-- Populated from step 6. -->

## References

<!-- Accumulates as publications are cited; each resolved via list_publications. -->
