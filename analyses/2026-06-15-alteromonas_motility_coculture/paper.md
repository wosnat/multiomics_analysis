# Does Prochlorococcus feed Alteromonas? A carbon-provision read on coculture, with motility as the lead readout

## Question

When *Alteromonas* grows in coculture with *Prochlorococcus* versus alone — in
media with **no added organic carbon**, where *Prochlorococcus* photosynthate is
*Alteromonas*'s only organic-carbon source — does its physiology shift toward a
**carbon-fed** state, and how does **motility** (flagellar assembly + bacterial
chemotaxis) respond?

This is an **expression** question, answered from the differential-expression
data in the KG. It began (step 1) as "does *Alteromonas* turn motility up or down
in coculture?", motivated by motility genes being differentially expressed in
Weissberg et al. 2025. During the redo, step 2 surfaced that every usable
coculture contrast runs in a medium with no added organic carbon — reframing the
contrast as a carbon-source manipulation and the question around a carbon-provision
hypothesis, with motility kept as the lead readout.

**Scope.** All *Alteromonas* strains with a usable coculture-vs-axenic contrast;
HOT1A3 (Weissberg 2025) as the primary case, with both RNA and protein and a
starvation time-course in coculture and axenic. EZ55, MIT1002, and a glucose-fed
MarRef panel supply controls. Four experiments whose DE direction is corrupted in
the KG are excluded (see Methods).

## Background

*Alteromonas macleodii* is a copiotrophic marine heterotroph commonly studied as a
partner of the cyanobacterium *Prochlorococcus*. As a heterotroph it requires an
organic-carbon source; a long-standing hypothesis in marine microbial ecology is
that *Prochlorococcus* exudes fixed organic carbon that supports heterotrophs like
*Alteromonas* in its "phycosphere." Motility (flagella and chemotaxis) is
energetically costly and is often regulated by nutrient and social cues, making it
a plausible readout of such a relationship — and the prompt for this analysis was
that motility genes are differentially expressed in the *Prochlorococcus*–
*Alteromonas* coculture study of Weissberg et al. 2025.

**KG entries used.** The full *Alteromonas* inventory is 49 experiments across 8
strains and 10 papers (frozen in `2_kg_entries/`). The key fact: none of the
usable coculture-vs-axenic contrasts add organic carbon — the media are PRO99-lowN
(Weissberg HOT1A3), Pro99 (EZ55), or natural-seawater Pro99 (MIT1002) — so in
axenic culture *Alteromonas* has no organic-C source and in coculture the only
source is *Prochlorococcus* photosynthate. The primary case is HOT1A3 (Weissberg
2025): a MED4 coculture-vs-axenic snapshot (RNA, all genes) plus four PRO99-lowN
nutrient-starvation time-courses (RNA + protein × coculture + axenic). Organic-C-
amended experiments (MarRef + glucose; EZ55 + glucose; vesicle proteomics) provide
a "fed reference," and EZ55's *Synechococcus* contrasts a partner-specificity
control. Motility is defined as KEGG flagellar assembly (ko02040) + bacterial
chemotaxis (ko02030), with broad COG-N "Cell motility" as a sensitivity set.

## Methods

### Framing (step 3)

**Hypothesis.** In media with no added organic carbon, *Prochlorococcus* supplies
fixed organic carbon to *Alteromonas* — relieving a carbon-(and-nitrogen)-
starvation state that otherwise deepens over time in axenic culture. Motility is
the lead readout; its direction is observed, not predicted.

**Readout.** Coculture-with-*Prochlorococcus* vs axenic, read two ways. (a) A
**day-11 exponential snapshot** (HOT1A3 MED4) — both cultures growing, so a
partner-during-growth read, not fed-vs-starved. (b) The **starvation time-courses**
(day 18→89, `nutrient_limited`, RNA + protein, coculture and axenic): the
carbon-starvation signature develops in the axenic arm, and the prediction is a
coculture-vs-axenic divergence that **grows over time**. Per contrast: pathway
over-representation (the package's `pathway_enrichment`, all-genes background per
experiment), with motility called out and deep-dived by locus tag in both omics.
"Carbon-fed" = organic-C uptake / central carbon metabolism up, carbon-starvation
machinery down. (Axenic protein stops at day 31, so late-starvation comparison is
RNA-only.)

**Controls.** Genome-wide background (denominator); a glucose-fed reference
(carbon manipulated without a partner — does the coculture signature resemble it?);
*Synechococcus*-partner (Prochlorococcus-specific vs generic cross-feeding); the
axenic-starvation and MIT1002-darkness signatures (is it just stress/dormancy?);
pCO₂ as a nuisance check.

**Data-quality gate.** DE direction is trusted only where the log2FC sign
distribution is intact; 4 experiments (both 2016 *ISME J* papers) with 0% negative
log2FC across all detected genes are excluded as sign-corrupted (step 2,
`gaps_and_friction.md`).

**The confound.** PRO99-lowN is also low in nitrogen, so the carbon-provision
effect cannot be cleanly separated from nitrogen effects within Weissberg alone;
the glucose-fed references and the starvation time-course structure bound it.

### Implementation (step 4)

The method is the package's `pathway_enrichment` (one-sided Fisher per pathway,
per-cluster `table_scope` background, up/down split, Benjamini-Hochberg) — no custom
statistics — wrapped in a thin reusable `run_contrast()` driver that also pulls a
motility gene-level readout (`differential_expression_by_gene` on the flagella+
chemotaxis locus tags) and freezes everything to CSV. Enrichment is run at two
granularities chosen by `ontology_landscape`: KEGG level 2 (interpretable pathways;
~0.31 genome coverage — reflects the KEGG-annotated third) and COG category level 0
(coarse, ~0.69 coverage). Built and validated on the HOT1A3 MED4 day-11 snapshot;
step 5 reuses `run_contrast` across the starvation time-courses and controls.

On the day-11 exponential snapshot (a partner-during-growth read, not the starvation
story), motility/chemotaxis genes lean down (7 of 96 significantly down — the
chemotaxis core cheA/cheW/cheR/aer2/fliL — 1 up) while biosynthetic and transport
metabolism lean up; three metabolic pathways survive correction (purine,
2-oxocarboxylic-acid, propanoate — all up), chemotaxis does not. Directionally
consistent with a fed, growing cell, but the carbon-starvation prediction (a
divergence growing over the time-course) is untested until step 5.

## Results

**Starvation suppresses motility in both arms, more so when axenic.** In HOT1A3
RNA, flagellar/chemotaxis genes are down under starvation in coculture and axenic
alike, but more in axenic: a paired Wilcoxon on the motility set's per-gene log2FC
(coculture−axenic) is significant at day 18 (median Δ +0.43, BH p 6.0e-4) and days
60+89 (+0.55, BH p 3.5e-9), though not day 31 — so the divergence is not monotonic
(Spearman rho 0.50, p 0.67, n=3 matched timepoints). Carbon/energy pathways lean
weakly up in coculture and flat in axenic. RNA and protein are analysed separately
(direction agreement 0.68 coculture / 0.48 axenic); protein does not mirror RNA and
the axenic protein series stops at day 31. *[interpretation]* This fits coculture
relieving a starvation-driven motility shutdown, but weakly and RNA-led.

**Controls show motility is not a carbon-specific readout.** Motility-down also
occurs under MIT1002 darkness (down-fraction 0.67–0.82) and dominates both HOT1A3
starvation arms (0.93–0.97), so it is a general stress/dormancy response. The
coculture motility *direction* is strain- and partner-specific: EZ55 leans up with
Prochlorococcus (MIT9312) but down with Synechococcus (CC9311), and across strains
with Prochlorococcus the direction flips (HOT1A3+MED4 down vs EZ55+MIT9312 up). The
glucose-fed reference (MarRef proteomics) is too sparse to define a fed signature.

**Net.** The carbon-provision hypothesis has partial, within-study support (HOT1A3
motility more suppressed starved-alone than fed-in-coculture; carbon/energy pathways
weakly up in coculture), but motility is not a clean Prochlorococcus-carbon-specific
marker — it is a general stress response, strain/partner-dependent, RNA-led with
discordant protein, and without a monotonic time-trend. An open anomaly (ribosome
genes reading up in starvation-vs-exponential) is flagged for step 6.

## Discussion

The carbon-provision hypothesis — that *Prochlorococcus* supplies fixed organic
carbon that keeps *Alteromonas* less starved in coculture — receives **partial,
within-study support, but motility is not the clean carbon-specific reporter the
framing hoped for.**

The supporting evidence is real and statistically grounded: in HOT1A3, motility
(flagella + chemotaxis) is significantly more suppressed under starvation when
axenic than in coculture (paired Wilcoxon, BH p 6e-4 at day 18 and 3.5e-9 at days
60+89), and carbon/energy pathways lean up in coculture. Read alone, that fits a
fed cell maintaining more of its motility machinery than a starving one.

Three findings hold that interpretation back. (1) **Motility-down is a general
stress/dormancy response, not carbon-specific:** it occurs under *Prochlorococcus*-
absent darkness (MIT1002) and dominates both starvation arms — so a partner that
relieves starvation will relax it for reasons that need not involve carbon
specifically. The control designed to separate "carbon" from "stress" (the
glucose-fed reference) was too sparse to resolve it. (2) **The coculture motility
direction is strain- and partner-specific:** EZ55 raises motility with
*Prochlorococcus* but lowers it with *Synechococcus*, and the direction flips
between HOT1A3 and EZ55 — there is no uniform "*Prochlorococcus* effect." (3) The
signal is **RNA-led and not corroborated by protein** (direction agreement 0.48 in
axenic), and the coculture–axenic divergence is **not monotonic** over time
(significant at day 18 and late, absent at day 31; trend test underpowered, n=3).

A structural caveat frames all of this: the primary dataset (Weissberg et al.
2025) was generated to study **nitrogen recycling for prolonged survival**, in a
low-nitrogen medium with no added organic carbon. Carbon and nitrogen limitation
are therefore inseparable in the axenic arm, and our carbon-provision lens is
orthogonal to the source study's nitrogen framing. We cannot attribute the
coculture relief to carbon specifically over nitrogen within this data.

Two things are worth following up. The **EZ55 *Prochlorococcus*-vs-*Synechococcus*
motility difference** is itself a genuine partner-specific signal deserving a
dedicated analysis. And testing carbon transfer directly — via metabolite/exudate
data or organic-carbon transporter expression — would speak to provisioning far
more specifically than motility does. A coordinate up-regulation of ribosomal-
protein genes under starvation-vs-exponential (in both arms) is flagged as an open
observation; it is internally consistent with the (correct) motility polarity and
is most likely a compositional-normalization effect of broad starvation
down-regulation, but it was not run to ground.

*Methodological note (this was a dogfooding run).* The analysis surfaced a KG data
problem — log2FC sign absent across all genes in four experiments from two 2016
papers — and the discipline that caught it (checking the sign distribution over all
genes before trusting direction) is the reason the partner-specificity claim here
rests on verified-clean contrasts rather than the artefact that misled an earlier
pass. See `gaps_and_friction.md`.

## References

- Weissberg O, Aharonovich D, Sher D (2025). *Transcriptomic and proteomic analysis
  reveals nitrogen recycling as a core mechanism for Prochlorococcus prolonged
  survival.* bioRxiv. doi:10.1101/2025.11.24.690089 — **primary dataset** (HOT1A3
  MED4 coculture + PRO99-lowN starvation time-course).
- Barreto Filho MM, Lu Z, Walker M, Morris JJ (2022). *Community context and pCO₂
  impact the transcriptome of the "helper" bacterium Alteromonas in co-culture with
  picocyanobacteria.* ISME Communications. doi:10.1038/s43705-022-00197-2 — EZ55
  partner-specificity + pCO₂ controls.
- Hennon GMM, Morris JJ, Haley ST, et al. (2018). *The impact of elevated CO₂ on
  Prochlorococcus and microbial interactions with 'helper' bacterium Alteromonas.*
  ISME J. doi:10.1038/ismej.2017.189 — EZ55 carbon-stress context.
- Coe A, Braakman R, Biller SJ, et al. (2024). *Emergence of metabolic coupling to
  the heterotroph Alteromonas promotes dark survival in Prochlorococcus.* ISME
  Communications. doi:10.1093/ismeco/ycae131 — MIT1002 darkness (diel) control.
- Biller SJ, Coe A, Roggensack SE, Chisholm SW (2018). *Heterotroph interactions
  alter Prochlorococcus transcriptome dynamics during extended periods of darkness.*
  mSystems. doi:10.1128/mSystems.00040-18 — MIT1002 extended-darkness control.
- Moreno-Cabezuelo JÁ, Gómez-Baena G, Díez J, García-Fernández JM (2023).
  *Integrated proteomic and metabolomic analyses show differential effects of
  glucose availability in marine Synechococcus and Prochlorococcus.* Microbiology
  Spectrum. doi:10.1128/spectrum.03275-22 — MarRef glucose-fed reference.
- *Excluded (sign-corrupted in the KG; see gaps_and_friction.md):* Aharonovich D,
  Sher D (2016), doi:10.1038/ismej.2016.70; Biller SJ, Coe A, Chisholm SW (2016),
  doi:10.1038/ismej.2016.82.
