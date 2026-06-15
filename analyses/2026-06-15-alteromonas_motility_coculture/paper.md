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

*(being redone against the carbon-provision framing — populated in step 4)*

## Results

*(being redone — the earlier step 4–5 results were produced "running ahead" of the
researcher and against the superseded motility-coordination framing; they are not
carried forward. New results populated in step 5 against the carbon-provision
framing and the clean usable experiment set.)*

## Discussion

*(populated in step 6)*

## References

*(accumulates as publications are cited; resolved via `list_publications`)*
