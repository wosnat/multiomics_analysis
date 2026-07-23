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

*(Fills in at the analysis milestone.)*

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
