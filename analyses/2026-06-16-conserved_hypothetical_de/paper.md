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

The analysis delivers a defensible shortlist of conserved hypothetical
*Prochlorococcus* gene families worth following up. Its central, validated result is
that **conserved hypotheticals respond to perturbation about as broadly as
characterized conserved genes** — they are not transcriptionally silent passengers of
the core genome.

The most important caveat, surfaced by the evaluation, is that **response breadth is
substantially confounded by measurement coverage** (breadth correlates with the number
of conditions a family was assayed in at r = 0.90). A family appears broadly
responsive partly because it sits in well-studied strains (MED4, NATL2A) measured
across many conditions. Conservation (strain count) is itself partly a coverage proxy
(r = 0.54 with coverage), so the apparent "more conserved → more responsive" trend
(core vs broad tier: mean breadth 4.61 vs 3.05) largely reflects coverage: the
coverage-normalized response_rate gap is modest (0.85 vs 0.78). **Prominence**
(within-experiment rank and fold-change magnitude) is *not* coverage-driven and is the
more robust axis; on it, core families are genuinely stronger (mean |log2FC| 6.58 vs
4.11). For this reason the headline deliverable is the **14 families that are both
broad and prominent** — robust on the confound-resistant axis while still broadly
regulated — with the 85-family broad-or-prominent set as the long list.

Direction at the family level is predominantly "mixed" because these genes flip
direction across conditions (e.g. up under darkness, down under nitrogen/coculture/
salt) — context-dependent regulation that is itself a lead worth pursuing rather than
noise. Several top families are annotated only as "uncharacterized secreted" or
"membrane" proteins, suggesting envelope/interaction functions.

This is the **selection** half of the original question. What these genes actually do
— their cross-organism homologs, conserved genomic neighborhoods, co-expression
modules, and the ontology of their neighbors — is the subject of a separate
characterization analysis that takes `6_evaluate/data/handoff_shortlist.csv` (the 85
families, 14 flagged core) as its input.

### Limitations

Breadth is coverage-confounded (above); DE evidence is dominated by two strains;
significant-only experiments lack a tested-but-flat denominator, so absence of a
response cannot be distinguished from absence of measurement there; within-experiment
rank depends on each table's size; family-level pooling conflates paralogs and strains;
and conservation is measured against the 17-strain cyanorak backbone, not all 19
genome strains.

## References

Data source: multi-omics knowledge graph, release 0.1.0-alpha.5 (built 2026-06-09;
gene/experiment/publication counts from `kg_release_info`). Scoring used the
`multiomics_explorer` package (explorer 0.1.0a3); statistics and figures in Python
(pandas, numpy, matplotlib, seaborn). The 74 pooled gene-DE experiments derive from
the 30 publications below, resolved via `list_publications` (full metadata in
`6_evaluate/data/references.csv`; bracketed counts = pooled experiments used).

1. Tolonen et al. (2006). Global gene expression of Prochlorococcus ecotypes in response to nitrogen availability. *Molecular Systems Biology*. doi:10.1038/msb4100087 [6]
2. Martiny et al. (2006). Phosphate acquisition genes in Prochlorococcus ecotypes. *PNAS*. doi:10.1073/pnas.0601301103 [2]
3. Steglich et al. (2006). Genome-wide analysis of light sensing in Prochlorococcus. *J. Bacteriology*. doi:10.1128/JB.01097-06 [6]
4. Pandhal et al. (2007). Quantitative proteomic analysis of light adaptation in a marine cyanobacterium. *J. Proteome Research*. doi:10.1021/pr060460c [2]
5. Lindell et al. (2007). Genome-wide expression dynamics of a marine virus and host. *Nature*. doi:10.1038/nature06130 [1]
6. Zinser et al. (2009). Choreography of the transcriptome, photophysiology, and cell cycle. *PLOS ONE*. doi:10.1371/journal.pone.0005135 [1]
7. Thompson et al. (2011). Transcriptome response of high- and low-light-adapted Prochlorococcus. *ISME J.*. doi:10.1038/ismej.2011.49 [5]
8. Fuszard et al. (2012). Comparative quantitative proteomics of Prochlorococcus ecotypes. *Aquatic Biosystems*. doi:10.1186/2046-9063-8-7 [3]
9. Waldbauer et al. (2012). Transcriptome and proteome dynamics of a light-dark synchronized cell cycle. *PLoS ONE*. doi:10.1371/journal.pone.0043432 [1]
10. Wang et al. (2014). The transcriptome landscape of Prochlorococcus MED4. *BMC Microbiology*. doi:10.1186/1471-2180-14-11 [1]
11. Al-Hosani et al. (2015). Global transcriptome of salt-acclimated Prochlorococcus AS9601. *Microbiological Research*. doi:10.1016/j.micres.2015.04.006 [1]
12. Bagby et al. (2015). Response of Prochlorococcus to varying CO2:O2 ratios. *ISME J.*. doi:10.1038/ismej.2015.36 [4]
13. Lin et al. (2015). Transcriptomic response during phage infection under phosphorus stress. *Environmental Microbiology*. doi:10.1111/1462-2920.13104 [2]
14. Aharonovich et al. (2016). Transcriptional response of Prochlorococcus to co-culture with Alteromonas. *ISME J.*. doi:10.1038/ismej.2016.70 [3]
15. Biller et al. (2016). Impact of a heterotroph on the transcriptome of Prochlorococcus. *ISME J.*. doi:10.1038/ismej.2016.82 [1]
16. Thompson et al. (2016). Gene expression during light and dark cyanophage infection. *PLOS ONE*. doi:10.1371/journal.pone.0165375 [4]
17. Read et al. (2017). Nitrogen cost minimization in the transcriptome of N-depleted Prochlorococcus. *ISME J.*. doi:10.1038/ismej.2017.88 [1]
18. Domínguez-Martín et al. (2017). Quantitative proteomics of nitrogen limitation in Prochlorococcus. *mSystems*. doi:10.1128/mSystems.00008-17 [1]
19. Hennon et al. (2018). Impact of elevated CO2 on Prochlorococcus and microbial interactions. *ISME J.*. doi:10.1038/ismej.2017.189 [1]
20. Biller et al. (2018). Heterotroph interactions alter Prochlorococcus dynamics in extended darkness. *mSystems*. doi:10.1128/mSystems.00040-18 [2]
21. Tetu et al. (2019). Plastic leachates impair growth and oxygen production in Prochlorococcus. *Communications Biology*. doi:10.1038/s42003-019-0410-x [4]
22. Fang et al. (2019). Transcriptomic responses of Prochlorococcus to viral lysis products. *Environmental Microbiology*. doi:10.1111/1462-2920.14513 [1]
23. Barreto Filho et al. (2022). Community context and pCO2 impact the transcriptome of Alteromonas. *ISME Communications*. doi:10.1038/s43705-022-00197-2 [1]
24. He et al. (2022). Acclimation and stress response of Prochlorococcus to low salinity. *Frontiers in Microbiology*. doi:10.3389/fmicb.2022.1038136 [2]
25. Capovilla et al. (2023). Chitin utilization by marine picocyanobacteria. *PNAS*. doi:10.1073/pnas.2213271120 [2]
26. Alonso-Sáez et al. (2023). Transcriptional mechanisms of thermal acclimation in Prochlorococcus. *mBio*. doi:10.1128/mbio.03425-22 [1]
27. Moreno-Cabezuelo et al. (2023). Integrated proteomic and metabolomic analyses of glucose availability. *Microbiology Spectrum*. doi:10.1128/spectrum.03275-22 [8]
28. Coe et al. (2024). Metabolic coupling to Alteromonas promotes dark survival in Prochlorococcus. *ISME Communications*. doi:10.1093/ismeco/ycae131 [1]
29. Anjur-Dietrich et al. (2025). Biofilm formation and dynamics in Prochlorococcus. *bioRxiv*. doi:10.1101/2025.08.05.668435 [1]
30. Weissberg et al. (2025). Nitrogen recycling as a core mechanism in Prochlorococcus. *bioRxiv*. doi:10.1101/2025.11.24.690089 [5]
