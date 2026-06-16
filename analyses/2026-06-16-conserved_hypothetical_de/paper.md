# Conserved hypothetical genes that are broadly differentially expressed in Prochlorococcus

## Question

Across *Prochlorococcus*, which **conserved hypothetical ortholog families** — gene
families with no assigned function but wide conservation (present in many strains) —
are **broadly and/or prominently differentially expressed across many distinct
conditions**? The goal is a ranked, defensible shortlist of *interesting* conserved
hypothetical genes worth following up.

This analysis is the **selection** half of the original question. The
characterization half — what the knowledge graph can tell us about the shortlisted
genes (cross-organism homologs, genomic neighborhood, co-expression, ontology of
neighbors) — is a separate follow-on analysis that takes this shortlist as input
(scope split recorded 2026-06-16; see `1_question/notebook.md` and
`gaps_and_friction.md`).

Operational intent (precise definitions verified/finalized in later steps):
- **Uncharacterized** = no assigned function ("hypothetical protein" / conserved
  hypothetical / lacking a functional name); operationalized as annotation quality
  ≤ 1 (step 2).
- **Conserved** = the ortholog family is present in many strains. The unit of
  analysis is the **ortholog group**, not the single-strain locus tag.
- **Broadly responsive** = differentially expressed across many distinct
  conditions/stresses, pooled at the ortholog-family level so coverage from all
  *Prochlorococcus* strains contributes. **Prominently responsive** = top
  within-experiment rank, large fold change, or many significant datapoints.

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

Scoring is implemented in a small reusable module
(`4_methods/og_response_metric.py`) whose aggregation logic was verified on
hand-calculated toy data before use. Per-gene differential expression is the single
data source (`differential_expression_by_gene`, which carries log2 fold change and
within-experiment rank), extracted per strain and mapped to ortholog groups. On the
driving example family `cyanorak:CK_00000958` the metric recovered breadth 4 (down
under coculture / nitrogen / salt, up under darkness) with a maximum |log2 fold
change| of 11.8, every aggregate traceable to a source datapoint.

The metric was validated on characterized MED4 genes before application: the
broad-stress chaperone-class and high-light-inducible genes versus a
phosphate-specific marker and a housekeeping chaperone paralog. The breadth axis
correctly separated broad responders (*hli*, 5 treatment types) from narrow ones
(*htpG*, 1; *dnaK1*, 0), and the phosphate marker *pstS* (prominent in phosphorus,
moderate breadth) confirmed that breadth and prominence are independent and must be
reported separately.

## Results

All 245 conserved hypothetical families were scored, alongside the full
conservation-matched backdrop of 1,710 conserved cyanorak families (≥9/17 strains;
1,465 of them characterized), over 23,422 significant differential-expression
datapoints.

**Conserved hypotheticals respond about as broadly as characterized conserved
genes.** Median breadth is 4 treatment types for both groups; characterized families
have a slightly higher mean (4.48 vs 3.67) and a heavier broad tail, but 30 of the 245
hypotheticals respond in ≥6 of 13 conditions and the most responsive match the
broadest characterized families. The dark genes are not transcriptionally silent.

**A shortlist of 85 interesting hypothetical families** was defined as those that are
broad (≥6 treatment types; 30 families) or prominent (a top-3 within-experiment
responder, |log2 fold change| ≥ 8, or ≥30 significant datapoints; 69 families), 14
being both. The most responsive — e.g. `cyanorak:CK_00000141` and `CK_00019843`
(breadth 9, reaching rank 1) and `CK_00045754` (|log2FC| 10.8) — are as broadly and
prominently regulated as any characterized gene, yet carry no functional annotation in
any strain.

**Direction is condition-dependent.** Headline families are overall "mixed" because
their direction flips across conditions (e.g. up under darkness, down under
nitrogen/coculture/salt) — a regulatory signal in its own right, resolved per
treatment in the direction heatmap.

Figures (PNG + SVG): breadth distribution hypothetical vs characterized
(`5_analyze/figures/fig5`); the breadth-versus-prominence backdrop coloured by gene
category with direction as marker shape and characterized controls anchoring the axes
(`fig6`); and a clustered direction-by-treatment heatmap of the 85-family shortlist
(`fig7`).

## Discussion

<!-- Populated from step 6. -->

## References

<!-- Accumulates as publications are cited; each resolved via list_publications. -->
