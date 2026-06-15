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

*(populated in steps 3–4)*

## Results

*(populated in step 5)*

## Discussion

*(populated in step 6)*

## References

*(accumulates as publications are cited; resolved via `list_publications`)*
