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

Because the knowledge graph holds no *Prochlorococcus* coculture exudate
measurement, carbon use was inferred from the consumer: which of *Alteromonas*'s
substrate-specific importers switch on in coculture versus axenic growth.

*Transporter catalog (per strain).* For HOT1A3 and, separately, EZ55, candidate
transporter genes were enumerated by unioning four annotation sources (KEGG
Orthology, the BRITE transporters tree `ko02000`, TCDB, and product/function
text). Genes were grouped into physical transport systems from genomic adjacency
plus KEGG-KO-derived component roles (substrate-binding / permease / ATP-binding),
each system's substrate resolved at the finest level the annotation confidently
supported (KO name primary). Systems were classified importer vs exporter and
organic vs inorganic, and non-importer contamination (biosynthetic enzymes,
mechanosensitive channels, protein-export machinery) was removed. Organic-carbon
importer systems were grouped by shared substrate into **modules** (one substrate =
one module): 33 modules for HOT1A3, 35 for EZ55.

*Scoring (per experiment × timepoint).* All detected genes were ranked by the
KG-provided log2 fold-change into an up-percentile; a system's score is the median
of its subunit up-percentiles; a module's effect is the maximum of its systems
(best uptake route). Significance came from a matched-max permutation null (random
gene sets matched to the module's system count and subunit sizes), Benjamini–
Hochberg-corrected across all modules within each contrast (called up at q < 0.10);
inorganic-ion importers served as reference controls. No pooling across
experiments. A validation set (motility, `glcB`/glycolate, peptidases, ribosomal,
inorganic controls) and a genome-wide over-representation guard accompanied each
run. Full spec in `proposal.md`; the scoring code is toy-tested in `methods/`.

*Contrasts.* HOT1A3 + MED4 day-11 coculture-vs-axenic (genome-wide, well-powered);
the HOT1A3 coculture and axenic starvation time courses (read as a difference of
starvation responses, corroboration only); and EZ55 + MIT9312 at 400 and 800 ppm
pCO₂ (significant-genes-only).

## Results

**No coculture-specific organic-carbon source could be named.** The result is a
clean null on the best-powered contrast and weak or underpowered on the others.

*HOT1A3 day-11 presence contrast (the decisive test).* Of 33 candidate carbon
modules, exactly one passed q < 0.10: **benzoate** — and benzoate is a single gene
(`benE`, a genuine, confidently annotated benzoate/H⁺ symporter, log2FC +2.89,
padj 2.7 × 10⁻¹⁰) in the aromatic/xenobiotic class the study **pre-registered as an
expected negative** (not a plausible *Prochlorococcus* exudate). No genuine
marine-DOM candidate passed: the six-transporter polar-amino-acid module sat at the
neutral median, and sugar, peptide, and branched-chain modules ranked mid-to-low.
The validation set confirmed the contrast is real and the method sound — motility
was down (median up-percentile 0.18), ribosomal and inorganic controls neutral
(0.50) — while the positive controls were weak (peptidases only 0.57; `glcB` down,
so glycolate is not used). The genome-wide guard found central-carbon *metabolism*
maps (2-oxocarboxylic-acid, propanoate) mildly over-represented among up-genes —
internal catabolism, not uptake specificity.

*HOT1A3 starvation temporal overlay.* Coculture-specific ramps were weak and
non-reproducible: peptide/nickel (up in two coculture timepoints but with an
ambiguous substrate — nickel would be inorganic), L-lactate (one timepoint, then up
in both arms), and a coarse carbohydrate module (one timepoint). The
ribosomal-neutrality control **failed** in this contrast (up-percentile 0.66–0.79 in
both arms), so the temporal ranking is confounded by the growth-state transition
rather than reporting carbon specifically. As pre-specified, the temporal read is
corroboration only — and there was no presence-contrast hit for it to corroborate.

*EZ55 (400 / 800 ppm pCO₂).* Underpowered rather than negative: because these
datasets report significant genes only, 28–32 of the 35 modules had no scorable
gene at all. No module passed at 400 ppm; one passed at 800 ppm — Fe(3+)-dicitrate,
which the KG confirms is iron acquisition (`fecA`, a TonB-dependent ferric-citrate
transporter; the "organic" tag was a spurious "citrate" string match). There was no
agreement between the two pCO₂ arms and no overlap with any HOT1A3 candidate.

**No module met the pre-registered criteria to *name* a carbon source.** In the two
presence contrasts, the only modules to clear q < 0.10 were the two pre-registered
expected negatives (an aromatic transporter in HOT1A3; an iron transporter in EZ55).
The starvation time course did yield three coculture-specific modules at q < 0.10
(L-lactate, peptide/nickel, carbohydrate) — but, confounded by the growth-state
transition and with no presence-contrast hit to corroborate them, these are
significance that cannot name a source, exactly as the design specified for the
temporal read.

## Discussion

*Alteromonas*'s organic-carbon sources in coculture with *Prochlorococcus* could
not be identified from these transcriptomes. This is a genuine negative, not a
pipeline failure: on the well-powered day-11 contrast the method's own controls
behaved (motility down, reference importers neutral), the pre-registered
falsifiability criterion fired exactly as intended (only the expected-negative
classes reached significance), and the data-integrity checks were clean. The design
was built to distinguish "no signal" from "a signal we can name," and it returned
the former.

*Why the signal may be absent.* Several explanations are consistent with the data
and are not mutually exclusive. At exponential day-11 the cells may not yet be
carbon-limited, so uptake is not differentially regulated — the coculture effect is
clearly captured (motility falls), so it is carbon-uptake specifically that is flat,
not the contrast. Carbon acquisition may be constitutive or post-transcriptionally
regulated, invisible to differential expression. Or the exuded carbon may be handled
by broad-specificity or shared central metabolism rather than dedicated,
annotatable transporters — consistent with the faint 2-oxocarboxylic-acid /
propanoate metabolic signal that appeared while no transporter module did.

*What the method taught us (for a next attempt).* (1) In an effect-ranked catalog,
single-gene modules rise to the top and one strongly induced gene can clear FDR;
the permutation null handles this statistically, but it was the **pre-registered
expected-negative check** — not the statistics — that correctly read the sole
benzoate hit as noise-for-the-question. Both safeguards were necessary. (2) Many
*Alteromonas* ABC importers are orphan solute-binding proteins whose permease/ATPase
partners are not genomically adjacent, so multi-subunit coherence is mostly
unavailable; module-level coherence must instead come from several binding proteins
for one substrate class, which caps resolution. (3) Significant-genes-only datasets
(EZ55) are too sparse for a transporter-module method — most modules are unscorable;
this approach needs genome-wide DE. (4) The starvation-vs-exponential contrast is
confounded by the growth-state transition (a neutral control calibrated on the
presence contrast did not transfer), which is why the plan weighted it below the
presence contrast — a weighting the results vindicated.

*What would move the question.* Direct metabolomics of *Prochlorococcus* coculture
exudate (absent from the KG) would replace consumer-side inference with the menu
itself. Failing that: a genome-wide (not significant-only) coculture-vs-axenic
contrast sampled under carbon limitation, where uptake regulation is most likely to
appear; proteomics or fluxomics to catch constitutively expressed uptake; and
targeted assays for the faint candidates this analysis could not confirm — peptides,
L-lactate, and the short-chain organic acids implied by the propanoate /
2-oxocarboxylic-acid signal.

*Bottom line.* A well-posed question, a method validated on the primary contrast,
and adequate data there yielded no resolvable carbon-uptake signal; the design's own
negative controls confirm the null is real rather than an artifact. The specific
carbon compounds *Alteromonas* draws on in coculture remain unnamed by this
evidence — a bounded, honest result that points to exudate metabolomics as the
decisive next measurement.

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
