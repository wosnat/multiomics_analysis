# Carbon sources used by *Alteromonas* in coculture with *Prochlorococcus*

*Working paper — grows across the analysis arc. Sections fill in at the Plan
commit and each Run milestone's decide phase.*

## Question

Which organic carbon compounds does *Alteromonas* draw on when growing in
coculture with *Prochlorococcus*? The growth media used across the relevant
experiments carry no added organic carbon, so any organic carbon *Alteromonas*
uses in coculture must originate from the cyanobacterial partner. Because the
knowledge graph holds no direct measurement of *Prochlorococcus* coculture
exudates, the carbon sources are inferred from the consumer side — which of
*Alteromonas*'s substrate-specific uptake-and-catabolism systems are switched on
in coculture relative to axenic growth, across the available Alteromonas–
Prochlorococcus coculture datasets.

## Background

*Prochlorococcus*, the dominant cyanobacterium of the oligotrophic ocean, has a
streamlined genome and depends on heterotrophic partners for survival under
stress; *Alteromonas* is a model "helper" heterotroph in this interaction. In
the Weissberg 2025 study (the subject of this analysis), *Alteromonas* HOT1A3 in
coculture with *Prochlorococcus* MED4 under extended nitrogen limitation shows
transcriptional and translational changes consistent with increased organic-
matter degradation and reduced motility, and is proposed to act as a nitrogen
recycler. That organic-matter-degradation signal is the entry point for the
carbon question addressed here.

Datasets bearing on the question (all inferring carbon use from *Alteromonas*'s
own expression): the Weissberg 2025 HOT1A3 + MED4 coculture-vs-axenic
transcriptome and its coculture/axenic starvation time courses; the EZ55 +
MIT9312 coculture-vs-axenic transcriptomes at two pCO₂ levels; and, as context,
the HOT1A3 + MIT9313 cocultures. Full enumeration, scope, and exclusions are in
`proposal.md` / `proposal_notebook.md`.

## Methods

**Transporter enumeration and system reconstruction.** Transporter genes were
enumerated per strain from the union of four KG annotation sources — the BRITE
`ko02000` transporters tree, KEGG-KO transporter terms, the TCDB classification, and
product/function-description keyword search — giving 684 (HOT1A3) and 697 (EZ55)
candidate transporter genes `[KG]`. Because KEGG-KO annotation of ABC permease/ATPase
subunits is sparse in these genomes (iron and the branched-chain `livK` binding
protein carry specific KOs, but the `liv` permease/ATPase and the glutamine, fructose
and osmoprotectant systems have no HOT1A3 gene `[KG]`), component role was assigned
primarily from Pfam domains (`SBP_bac*`/`Peripla_BP*` = substrate-binding;
`BPD_transp*`/`FecCD` = permease; `ABC_tran` = ATPase) carried in the near-fully
populated `alternate_functional_descriptions` field, with KO/TCDB confirming where
present. Multi-subunit systems were reconstructed by grouping consecutive-locus,
same-strand genes sharing a transport role and substrate/family; a repeated permease
or ATPase role does not split a system whose subunits share a substrate (validated on
a peptide ABC importer with two permeases and two ATPases), and non-transport
neighbours are surfaced but do not break a cassette — a co-located catabolic gene is
recorded as both breakdown-side evidence and genomic-neighbourhood substrate support.

A genome feature shapes the analysis: HOT1A3 carries 36 substrate-binding proteins but
only 11 import permeases, alongside 85 single-gene secondary carriers `[KG]`. Complete
multi-subunit ABC cassettes therefore exist mainly for peptides and inorganic
substrates, while organic-carbon uptake (sugars, amino acids, organic acids) is
dominated by orphan binding proteins and secondary carriers. The scored unit — the
transport system — is thus single-gene for the majority of organic-carbon candidates.

**Candidate and control sets.** Each transporter gene was classified (transport-role /
carrier-family / regulator / enzyme / machinery / exporter / sensory / unresolved) with
a recorded reason, dropping non-uptake genes and recognising organic-carbon carrier
families the ABC/TCDB net alone missed (BCCT osmolyte, POT peptide, Na-solute
symporter, TRAP, nucleobase/nucleoside, SLC13 dicarboxylate, MFS sugar/organic-acid),
yielding 57 (HOT1A3) / 59 (EZ55) candidate organic-carbon systems. Four reference classes are
tracked separately: candidates; inorganic ABC/secondary-carrier importers
(`control-ABC`); iron/siderophore TonB receptors (`control-TonB`, single-gene,
size-matched to the candidates); and bare unresolved TonB receptors (`ambiguous-TonB`,
a control-for-the-control that flags whether the TonB receptor class moves as a
coordinated iron regulon). B12/heme receptors are held out as interaction-coupled.

**Scoring.** Per (experiment × timepoint), all detected genes are ranked by the
KG-provided log2 fold-change into an up-percentile (rank/N; genome-wide for
all-detected-genes experiments, within the significant set for significant-only
experiments; ties take the average rank). A system's score is the median of its subunit
percentiles (single-gene systems score on their one gene; partially covered systems on
present subunits, count flagged); a module's effect is the maximum system percentile.
Significance is a matched-max permutation null with random system-sets drawn matched on
system count *and* each system's subunit count — a single-gene system compared against
random single genes, a k-subunit system against random k-gene medians — and module
p-values are Benjamini–Hochberg-corrected within each (experiment × timepoint), a module
called up at q < 0.10. Degradation-pathway evidence is read off the genome-wide
`pathway_enrichment` ORA as a per-module up/not-up flag, corroboration-only, outside the
FDR family. The scoring module was verified against hand-computed toy data before use.
No fold-changes are compared across experiments; cross-experiment agreement is a count
of independent results. See `proposal.md` for the full approach and `methods/notebook.md`
for the build, the reveals, and the decisions.

## Results

Scoring the *Alteromonas* transporter modules per (experiment × timepoint) recovers the
expected controls: in the primary HOT1A3 day-11 coculture-vs-axenic contrast
(`all_detected_genes`, 111 up / 163 down) motility/flagellar transporters sit at the down
end (median up-percentile 0.18) and ribosomal genes are neutral (0.50), while the
genome-wide pathway guard finds **Carbohydrate metabolism** and **Nucleotide metabolism**
over-represented among up-genes (padj 0.021 each).

At the module level the signal is thin: only 2 of 46 candidate modules pass q < 0.10
(a carbohydrate MFS transporter, log2FC 3.5; and `benE` benzoate, log2FC 2.9), with a
citrate/dicarboxylate importer just above (q = 0.10). On a size-matched basis the
candidate organic-carbon systems are **not** elevated over the inorganic control set
(single-gene medians 0.62 vs 0.66), so the bulk organic-vs-inorganic contrast carries no
weight — as anticipated, the carbon signal is specificity-based, not bulk.

Aggregating transporters by **compound class** (a family-size-independent read) gives a
clearer picture (Fig. 1). The most-elevated classes are **sugars/carbohydrates** and
**nucleosides/nucleobases** (class median up-percentile ≈ 0.70 vs the inorganic reference
0.59), converging with the genome-wide enrichment of carbohydrate and nucleotide
metabolism. Organic acids and osmolytes are modestly elevated; **amino-acid transporters
are conspicuously not induced** (class median 0.38, below the inorganic reference, across
15 transporters) and peptides are neutral. The shifts are modest (~0.1 percentile).

Across strains, the **sugar/carbohydrate** signal reproduces (Fig. 2): it passes q < 0.10 in
both HOT1A3 (carbohydrate MFS) and the EZ55 400-ppm arm (L-fucose), and is the top class by
median percentile in each (0.77, 0.83) — though EZ55 is `significant_only` and its
q-values arise within a much smaller (3–5-module) test family than HOT1A3's, so the
comparable quantity is the within-experiment permutation p. The **organic-acid** class is
a weaker second: supported by the EZ55 800-ppm arm (acetate) and by the HOT1A3 starvation
time course, where L-lactate rises coculture-specifically at day 31 (coculture q = 0.037
vs axenic n.s., sustained to day 60; axenic catches up only at late starvation — Fig. 3)
while the day-11 citrate hit reads flat across the ramp (expected for a constitutively
coculture-induced module). The temporal read is
corroboration-only and thin (a single informative RNA timepoint; proteomics detected no
up-modules).

Degradation-pathway (breakdown) corroboration is **not determinable** for sugars and
organic acids, which feed central metabolism with no dedicated catabolic map (35 of 43
candidate substrates); of the 8 with a genuine degradation map none is over-represented
among up-genes in the primary strain. The aromatic **`benE`** hit does not resolve into a
supported carbon source: it is the HOT1A3-specific #2 module but is absent from both EZ55
significant sets, and aromatic *degradation* is over-represented only in the EZ55 800-ppm
arm — transporter and catabolism never co-occur in one strain/condition. Finally, iron
acquisition (TonB/siderophore receptors) is the single most up-regulated transporter class
in coculture (median 0.76), indicating that iron is interaction-coupled rather than a
clean negative control.

### Figures

- **Fig. 1** (`analysis/figures/figA_compound_class_landscape.svg`) — Transporter compound
  classes ranked by median coculture-vs-axenic up-percentile in HOT1A3 day-11, against the
  inorganic-control reference (0.59). Sugars/carbohydrates and nucleosides are the most
  induced; amino-acid transporters sit well below the reference; iron receptors (dropped
  from scoring, shown as a confound) are the single most up-regulated class.
- **Fig. 2** (`figB_cross_experiment_classes.svg`) — Candidate class median up-percentile
  across HOT1A3, EZ55-400 and EZ55-800; the sugar/carbohydrate class is elevated in both
  HOT1A3 and EZ55-400 (EZ55 arms are `significant_only` and thin — some bars are single
  modules).
- **Fig. 3** (`figC_temporal_lactate.svg`) — L-lactate transporter up-percentile across the
  HOT1A3 starvation time course: coculture rises early (day 31, q<0.10) while the axenic
  arm reaches comparable levels only at late starvation (days 60+89) — a coculture-specific
  *earlier* ramp, corroboration-only.
- **Fig. 4** (`figD_transporter_landscape.svg`) — the *Alteromonas* candidate carbon-transporter
  repertoire by compound class (HOT1A3), single- vs multi-subunit: amino acids are the largest
  class yet are not induced; the response is selective, not proportional to repertoire.
- **Fig. 5** (`figE_experiment_substrate_heatmap.svg`) — candidate module up-percentile across
  all experiments/timepoints (presence | RNA-seq temporal | proteomics temporal), class-ordered,
  `*` = q<0.10. Sugars/nucleosides are consistently up, branched-chain amino acids consistently
  down; the late-axenic ramp reddens broadly.
- **Fig. 6** (`figE2_control_heatmap.svg`) — the same for the control classes on the same scale:
  inorganic (control-ABC) transporters are neutral, iron/siderophore (TonB) receptors are
  predominantly up (interaction-coupled), and nitrate passes q<0.10 — so the candidate structure
  in Fig. 5 is specific, not a global up-shift.
- **Fig. 7** (`figF_rna_vs_proteomics.svg`) — RNA-seq vs proteomics up-percentile per module
  (coculture temporal): proteomics is underpowered (0 modules reach q<0.10 in any arm; protein
  median ≥ RNA), so the transcript-level signal is neither confirmed nor refuted at the protein
  level; a few modules (e.g. acetate) show RNA-up/protein-flat.
- **Fig. 8** (`figG_ez55_vs_hot1a3.svg`) — module up-percentile in EZ55 vs HOT1A3 for the six
  substrates scored in both strains (EZ55 sparse): fucose and carbohydrate-porin reproduce, but
  carbohydrate-MFS and maltose do not, and the single shared organic acid (acetate) is
  anti-correlated — cross-strain reproducibility is partial and class-level.
- **Fig. 9** (`figH_analysis_funnel.svg`) — analysis funnel: 4028 genes → 684 transporter genes →
  57 organic-C candidate systems (curated) → 46 modules scored → 2 pass q<0.10 → the reproducible
  class-level signal (sugars, + organic acids), a prioritized shortlist for wet-lab growth assays.

## Discussion

*(Fills in at the evaluation milestone.)*

## References

*(Accumulates as publications are cited; each resolved via `list_publications`
by DOI / KG experiment id.)*

- Weissberg O., Aharonovich D., Sher D. *Transcriptomic and Proteomic Analysis
  Reveals Nitrogen Recycling as a Core Mechanism for Prochlorococcus Prolonged
  Survival.* bioRxiv 2025. DOI `10.1101/2025.11.24.690089`.
- Barreto Filho M.M., Lu Z., Walker M., Morris J.J. *Community context and pCO₂
  impact the transcriptome of the "helper" bacterium Alteromonas in co-culture
  with picocyanobacteria.* DOI `10.1038/s43705-022-00197-2`.
- Aharonovich D., Sher D. *Transcriptional response of Prochlorococcus to
  co-culture with a marine Alteromonas.* ISME J 2016. DOI `10.1038/ismej.2016.70`
  *(context dataset).*
