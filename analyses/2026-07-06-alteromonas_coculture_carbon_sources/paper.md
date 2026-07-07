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

*(Framing locked in the Plan phase; implementation fills in at the methods
milestone.)* Transport-system → degradation-pathway modules reconstructed from
KG annotation, scored per experiment by rank (not fold-change), with inorganic-
ion importers as reference controls. No pooling across experiments; cross-
experiment agreement by count. See `proposal.md` for the full approach and the
deliberate statistics decision.

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
