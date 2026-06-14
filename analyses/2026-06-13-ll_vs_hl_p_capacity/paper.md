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

The capacity metric is implemented in `4_methods/p_capacity.py` (pure pandas over
the frozen gene tables). It builds a strain × ortholog-group presence/absence
matrix (paralogs collapse to presence — capacity is repertoire breadth, not copy
number), counts focused-acquisition OGs per strain, computes the ecotype LL/HL
ratio, and categorizes each OG as universal / LL-only / HL-only / variable. The
logic is verified against hand-computed toy data
(`4_methods/scripts/qc_toy_verification.py`) before application.

## Results

On the 9-strain panel, LL strains carry slightly more focused P-acquisition
ortholog groups than HL (mean 14.6 vs 13.0; LL/HL = 1.12, raw count). But this
ratio sits within the control band — trace-metal adaptation 1.14, light 1.12 —
and above only the invariant ribosomal baseline (1.00) and nitrogen (0.98). It is
not specific to phosphorus, and per-1000-genes HL is actually denser (≈6.6 vs
5.8). The count difference is **entirely driven by the LLIV clade**: per-clade
means are HLI 13, HLII 13, LLI 13, LLII 11, LLIV 18; removing the two LLIV strains
collapses the ratio to LL/HL = 0.95 (Figures fig2, fig3).

The presence/absence repertoire shows a qualitative difference that the counts do
not. Of 23 focused-acquisition OGs, 10 are universal (the core Pi transporter
pstSCAB, phosphonate transporter phnCDE, phoH, sulfolipid sqdB, a
phosphatidic-acid phosphatase). Five are LL-only and two HL-only. The strongest
LL-wide marker is `ptrA`, a Crp-family transcriptional phosphate regulator,
present in 4 of 5 LL strains (LLI, LLII, and one LLIV) and absent from all 4 HL —
though notably absent in MIT9313. Deeper scavenging/storage machinery — acid
phosphatase (phoC), polyphosphate kinase (ppk2), a PAP2-superfamily phosphatase,
and a PsiE-like protein — is LL-only but confined to the LLIV clade (MIT9303,
MIT9313). Phosphonate-utilization paralogs (phnCDE2, ptxD) are carried sporadically
by one HL (MIT9301) and one LL (MIT9303), not ecotype-linked (Figure fig1).

## Discussion

The genomic evidence does not support a simple "LL ecotypes are better equipped
for phosphorus limitation" conclusion at the level of acquisition-gene quantity.
Of the three preregistered predictions, only the qualitative-repertoire
prediction held. LL strains do not carry robustly more P-acquisition ortholog
groups than HL: the raw LL/HL count ratio (1.12) sits inside the control band set
by trace-metal (1.14) and light (1.12) adaptation, exceeds only the invariant
ribosomal baseline (1.00) and nitrogen (0.98), reverses to 0.95 when the
large-genome LLIV clade is removed, and inverts entirely on a per-genome basis.
The count-level expansion is therefore neither phosphorus-specific nor LL-wide —
it is a genome-size effect concentrated in LLIV.

What does differentiate the ecotypes is repertoire, not count. A Crp-family
transcriptional phosphate regulator (`ptrA`) is present across LL (4 of 5 strains,
all three LL clades represented) and absent from every HL strain — an LL-wide
qualitative marker not attributable to genome size. Additional scavenging and
storage machinery — acid phosphatase, polyphosphate kinase, and accessory
phosphatases — is LL-only but confined to the deep-branching LLIV clade. The core
high-affinity uptake systems (the Pst phosphate transporter and the Phn
phosphonate transporter) are universal across both ecotypes, as expected for an
oligotroph.

These patterns fit the picture from Martiny, Coleman & Chisholm (2006): in
*Prochlorococcus*, phosphorus-gene content is governed more by the phosphorus
regime of a strain's source environment than by its high-light/low-light niche.
Here the sharpest genomic differentiation is clade-level (LLIV) and regulatory
rather than a clean light-ecotype acquisition gradient. The most defensible
statement is narrow: **LL genomes carry a phosphate regulator and (in LLIV)
extra scavenging/storage enzymes that HL lack, but not a broadly larger
P-acquisition transporter complement.**

Two limits bound these conclusions. First, the panel is small and imbalanced
(4 HL, 5 LL) because a tool bug restricted it to expression-bearing strains; the
LLIV findings rest on two genomes and the full 17-strain re-run is the priority
follow-up. Second, genomic presence is upstream of function — whether LL strains
*deploy* this machinery more effectively under P limitation is the
expression-response question deliberately deferred at the outset, and the natural
next analysis. Full caveats are in `6_evaluate/notebook.md`.

## References

Resolved via `list_publications` (cited by DOI):

1. Martiny AC, Coleman ML, Chisholm SW (2006). Phosphate acquisition genes in
   *Prochlorococcus* ecotypes: evidence for genome-wide adaptation. *PNAS*.
   DOI: 10.1073/pnas.0601301103.
2. Fuszard MA, Wright PC, Biggs CA (2012). Comparative quantitative proteomics of
   *Prochlorococcus* ecotypes to a decrease in environmental phosphate
   concentrations. *Aquatic Biosystems*. DOI: 10.1186/2046-9063-8-7.
3. Lin X, Ding H, Zeng Q (2015). Transcriptomic response during phage infection of
   a marine cyanobacterium under phosphorus-limited conditions. *Environmental
   Microbiology*. DOI: 10.1111/1462-2920.13104.
4. Kujawinski EB, Braakman R, Longnecker K, et al. (2023). Metabolite diversity
   among representatives of divergent *Prochlorococcus* ecotypes. *mSystems*.
   DOI: 10.1128/msystems.01261-22.

Data source: multiomics-kg KG release 0.1.0-alpha.6 (built 2026-06-13, git
ffef4007); explorer 0.1.0a2. Gene set: curated Cyanorak role `cyanorak.role:D.1.5`
at Cyanorak ortholog-group level.
