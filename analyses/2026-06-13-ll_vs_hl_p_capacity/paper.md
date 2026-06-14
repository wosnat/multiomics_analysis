# Are low-light Prochlorococcus ecotypes better equipped at the genome level to handle phosphorus limitation?

## Question

Do low-light-adapted (LL) *Prochlorococcus* ecotypes carry a greater or
qualitatively different genomic complement of **phosphorus-acquisition and
-scavenging machinery** than high-light-adapted (HL) ecotypes — i.e., are LL
clades *better equipped at the genome level* to handle phosphorus (P)
limitation?

This is a **comparative-genomics** question (gene/ortholog presence across
ecotypes), not an expression-response question. It is answered from the gene
complements of *Prochlorococcus* genome strains in the KG, grouped HL
(HLI, HLII) vs LL (LLI, LLII, LLIV).

**Scope.** *Prochlorococcus* genome strains only (no *Synechococcus*
outgroup). P-acquisition/scavenging gene set (pho-regulon family). Gene-set
definition method, genome-size normalization, and any cross-check against
expression contrasts are deferred to later steps (just-in-time).

**A priori tension.** The classic *Prochlorococcus* P-gene literature reports
that P-acquisition gene content tracks the phosphorus regime of a strain's
source water, which can cut across the HL/LL ecotype split. So "LL is better
equipped" is a genuine hypothesis that may not hold. *[interpretation]*

**Confound to control.** LL genomes are larger than HL genomes (e.g. MIT9313
≈ 2,948 genes vs MED4 ≈ 1,976) *[KG]*, so a raw count of P genes may favor LL
trivially. Handling this is a step-3 framing decision.

## Background

Phosphorus-acquisition gene content is a textbook case of *Prochlorococcus*
ecotype genome adaptation: Martiny, Coleman & Chisholm (2006) showed that the
pho regulon and accessory P-acquisition genes vary across strains in a way that
tracks the phosphorus regime of the source water, comparing the HL strain MED4
and the LL strain MIT9313. Subsequent work compared ecotype P responses at the
protein level (Fuszard et al. 2012; MIT9312/NATL2A/SS120) and transcriptome
level (Lin et al. 2015; NATL2A). This analysis asks the genomic-capacity
question directly across an ecotype panel: do LL genomes carry more or different
P machinery than HL?

**KG entries used.** P machinery is defined by the curated Cyanorak functional
role `cyanorak.role:D.1.5` (phosphorus adaptation/acclimation) and compared
across strains at the level of curated Cyanorak ortholog groups. This handle was
chosen over GO and KEGG on measured coverage: in *Prochlorococcus* the Cyanorak
role captures all 10/10 core acquisition genes (pstSCAB, phnCDE, phoB, phoR,
phoH) per strain, whereas GO captures only 4–6/10 (the Pst transporter and
little else) and KEGG has no single P-acquisition pathway. The trade-off is that
the Cyanorak role is *broad* — it also includes P-stress-responsive but
non-acquisition genes (ribosomal proteins, chaperones, pentose-phosphate
enzymes) — handled by reporting a focused acquisition subset (step 3).

**Panel.** The comparison ideally spans all 17 Cyanorak-annotated genome strains
(9 HL, 8 LL). For this (dogfood) run it is restricted to the 9 strains the MCP
`genes_by_ontology` tool can resolve (4 HL: MED4, AS9601, MIT9301, MIT9312; 5 LL:
NATL1A, NATL2A, SS120, MIT9303, MIT9313) — the resolver requires
expression-bearing genes, excluding genome-only and metabolomics-only strains
(see `gaps_and_friction.md`). RSP50 and MIT1314 carry no Cyanorak annotation and
are excluded throughout.

## Methods

### Framing (step 3)

**Hypothesis.** LL ecotypes carry greater and/or qualitatively different genomic
P-acquisition capacity than HL — more acquisition ortholog groups and/or
LL-specific acquisition machinery.

**Gene set.** The curated Cyanorak D.1.5 role is broader than acquisition (it
includes P-stress-responsive ribosomal/PPP/chaperone genes). Its 48 ortholog
groups were classified into a **focused acquisition subset (23 OGs)** —
Pi/phosphonate transport (pstSCAB, phnCDE and paralogs), phosphatases (acid
phosphatase phoC, phosphatidic-acid and PAP2-superfamily phosphatases), the pho
two-component regulator (phoB/phoR) and a Crp-family phosphate regulator (ptrA),
P-starvation-inducible proteins (phoH, PsiP1, PsiE-like), polyphosphate kinase
(ppk2), and sulfolipid substitution (sqdB) — vs responsive-other (16) and unclear
(9, excluded conservatively). Classification is explicit and reproducible
(`3_framing/scripts/02_classify_p_ogs.py`).

**Capacity metric.** Per strain, the count of focused-acquisition OGs present,
compared between ecotypes as the raw-count LL/HL ratio benchmarked against a
control suite, plus the presence/absence repertoire. Per-1000-genes is secondary
(fixed-core categories do not scale with genome size, so per-1000 conflates fixed
core with no expansion).

**Controls.** K.2 ribosomal proteins as an invariant baseline (observed LL/HL =
1.00); D.1.3 nitrogen and D.1.7 trace-metal adaptation as specificity controls;
D.1.2 light adaptation as a positive control (varies by ecotype/clade, confirming
the method detects real ecotype differences).

**Preregistered predictions.** (1) LL focused-acquisition count > HL, ratio above
the ribosomal/nitrogen baselines; (2) ≥1 acquisition OG LL-present/HL-absent
(candidates ptrA, phoC, ppk2); (3) the P difference is ≥ trace-metal and >
nitrogen (genuine specificity test — may fail, since on the full role P ≈
trace-metal).

### Implementation (step 4)

*(populated in step 4)*

## Results

*(populated in step 5)*

## Discussion

*(populated in step 6)*

## References

*(accumulates as publications are cited; every reference resolved via
`list_publications` and cited by DOI / KG experiment ID)*
