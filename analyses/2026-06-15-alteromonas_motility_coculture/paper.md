# Does Alteromonas regulate motility when living with Prochlorococcus?

## Question

When *Alteromonas* grows in coculture with *Prochlorococcus* versus alone, does
it up- or down-regulate its motility genes (flagellar assembly and bacterial
chemotaxis)?

This is an **expression** question, answered from the differential-expression
data in the KG. Motivation: motility genes are differentially expressed in
Weissberg et al. 2025, the *Prochlorococcus*–*Alteromonas* coculture study, and
we want to understand that signal across the conditions the KG holds.

**Scope.** All *Alteromonas* strains that have both a coculture and an
alone (axenic) expression measurement (HOT1A3, MIT1002, EZ55 are the likely set;
confirmed in step 2). "Motility genes" = the KG's cell-motility set (flagellar
assembly + chemotaxis); exact gene-set definition is pinned in step 2. Comparing
across strains lets us see whether the response is consistent, with a flag where
it crosses studies/platforms.

## Background

*Alteromonas macleodii* is a copiotrophic marine heterotroph commonly studied as a
partner of the cyanobacterium *Prochlorococcus*. Motility (flagella and
chemotaxis) is energetically costly and is often regulated by environmental and
social cues, making it a plausible target of the coculture relationship. The
prompt for this analysis is that motility genes are differentially expressed in
the *Prochlorococcus*–*Alteromonas* coculture study of Weissberg et al. 2025.

**KG entries used.** Two strains have a clean coculture-with-Prochlorococcus
vs alone (axenic) differential-expression contrast: HOT1A3 (Weissberg 2025 and a
second study, all detected genes reported) and EZ55 (Hennon et al. 2017, at 400
and 800 ppm CO₂, significant genes only). EZ55 additionally has
coculture-with-*Synechococcus* contrasts, usable as a partner-specificity control.
Motility is defined two ways and reported side by side: the tight KEGG set
(flagellar assembly ko02040 + bacterial chemotaxis ko02030, ~96–102 genes per
strain) and the broad eggNOG COG category N "Cell motility" (~126–131 genes,
additionally including pili/twitching motility). MIT1002 and a MarRef proteomics
panel were considered but lack the coculture-vs-alone contrast.

## Methods

### Framing (step 3)

**Hypothesis.** In coculture with Prochlorococcus vs alone, Alteromonas motility
genes are coordinately regulated — moving together more than the genome-wide
background. Direction is observed, not predicted.

**Readout.** Per coculture-vs-alone experiment and per gene set: the number of
genes significantly up vs down in coculture, and whether the set is
over-represented among differentially expressed genes relative to all detected
genes. The over-representation test requires all genes to be reported and is
therefore computed for HOT1A3; EZ55 (significant genes only) contributes a
direction-only cross-check.

**Gene sets.** Motility primary = KEGG flagellar assembly + bacterial chemotaxis;
sensitivity = broad COG-N "Cell motility". Baseline control = KEGG ribosome
(54 genes in both strains).

**Controls.** The genome-wide background (denominator); a ribosomal baseline that
should not respond to the partner (to show specificity rather than a whole-cell
shift); and, in EZ55, coculture with Synechococcus vs Prochlorococcus as a
partner-specificity control.

**Preregistered predictions.** (1) motility over-represented among coculture-DE
genes in HOT1A3 beyond background; (2) the ribosomal baseline is not; (3) the
direction is consistent across HOT1A3 experiments and agrees with EZ55; (4,
exploratory) partner-specificity reported.

### Implementation (step 4)

*(populated in step 4)*

## Results

Motility genes are differentially expressed in coculture, but the **direction is
partner- and condition-dependent rather than uniform**. In HOT1A3, motility leans
down with the MED4 partner (Weissberg 2025: chemotaxis net −4, flagellar −2,
broad COG-N −8 at day 11) and up with the MIT9313 partner (a separate study:
flagellar +8, chemotaxis +6, COG-N +12 at 20 h). Leading fold-enrichments exceed
2×, but none survives Benjamini-Hochberg correction on these small significant-gene
sets. The ribosomal baseline is flat (zero significant genes in every HOT1A3
experiment), so the motility signal — weak as it is — is specific rather than a
whole-cell shift (Figure fig1).

EZ55, examined for direction only (its table reports significant genes only),
shows partner-specificity: motility leans up with Prochlorococcus (13 up / 3 down
across two CO₂ levels) and down or flat with Synechococcus (2 up / 7 down)
(Figure fig2). Taken together, the cases that lean up are the Prochlorococcus
partners MIT9313 (HOT1A3) and MIT9312 (EZ55); the down case is HOT1A3 with MED4 —
the very experiment that motivated the analysis.

## Discussion

*(populated in step 6)*

## References

*(accumulates as publications are cited; resolved via `list_publications`)*
