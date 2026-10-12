# *Prochlorococcus* sustains its nitrogen-starvation import machinery in long-term coculture with *Alteromonas*, but its expression does not identify the nitrogen source

*Draft manuscript section for the rewrite of Weissberg et al. (2025). Working record and audit trail:
`paper.md`, `methods/`, `analysis/`, `evaluation/`.*

## Abstract

In nitrogen-limited coculture with the heterotroph *Alteromonas macleodii* HOT1A3, *Prochlorococcus*
MED4 survives for months, whereas axenic cultures die within weeks (Weissberg et al. 2025). We asked
which nitrogen compounds MED4 is equipped to take up in this coculture.

*Approach.*
- We reconstructed all 73 MED4 transport systems from the genome annotation.
- We followed their protein and RNA abundance over 89 days of coculture.
- We compared them with three references:
  - the axenic culture;
  - published acute nitrogen-starvation and single-nitrogen-source experiments;
  - nitrogen-replete cocultures.

*Results.*
- The ammonium (*amt1*), urea (*urtA–E* with urease) and cyanate (*cynABD* with cyanase) import
  systems are among the most up-regulated proteins throughout the coculture, together with the
  nitrogen-starvation regulators GlnA, NtcA and GlnB.
- These are the systems switched on by acute nitrogen starvation, and they are not induced by
  coculture in nitrogen-replete medium.
- The declining axenic culture loses the cyanate system's elevation, which the coculture keeps.
- The dipeptide transporter is raised in coculture.
- No amino-acid, polyamine or osmolyte transporter responds.
- In calibration experiments, however, the urea system was not induced by urea but was induced by
  cyanate, and in MIT9313 the urea and nitrite systems rose on both substrates.

*Conclusion.* Transporter expression reports the cell's nitrogen status rather than the substrate
present. MED4's proteome shows a sustained nitrogen-starvation response, but cannot identify which
nitrogen compound, if any, it receives from its partner.

## Introduction

In coculture with *Alteromonas* HOT1A3, *Prochlorococcus* MED4 survives long after the nitrogen in its
medium is exhausted, whereas axenic cultures decline and die (Weissberg et al. 2025). That study
proposed that *Alteromonas* recycles organic matter and supplies low levels of ammonium, and that
MED4 responds by up-regulating high-affinity nitrogen scavenging. Which nitrogen compounds actually
pass between the two organisms has not been measured in these cultures. Here we ask what MED4's own
expression can say about it.

MED4 encodes import systems for:
- ammonium (Amt1);
- urea (the UrtABCDE ABC transporter, with urease UreA–G);
- cyanate (CynABD, with cyanase CynS);
- di- and oligopeptides (Dpp).

It lacks nitrate and nitrite assimilation. Other organic nitrogen classes (amino acids, polyamines,
osmolytes) are reachable only through broad, family-level transporter annotation. Many of these genes
are controlled by the global nitrogen regulator NtcA, so induction of a transporter need not indicate
that its substrate is present.

We therefore combined the coculture time courses with reference experiments in which the nitrogen
condition is known:
- acute nitrogen deprivation and growth on single nitrogen sources (Tolonen et al. 2006; Read et
  al. 2017);
- nitrogen-replete cocultures with *Alteromonas* (Aharonovich and Sher 2016; Biller et al. 2016).

## Methods

**Data.** All data were obtained from the multiomics knowledge graph (release 0.1.0-alpha.7; accessed
through `multiomics_explorer` 0.1.0-alpha.5) [citation to verify]. Table 1 lists the experiments.
Differential expression values (log2 fold change, adjusted p-value and the source study's significance
call) were used as published; no replicate-level data were re-analysed.

**Table 1. Experiments used.**

| Study | Strain(s) | Comparison | Platform | Timepoints | Role |
|---|---|---|---|---|---|
| Weissberg et al. 2025 | MED4 + HOT1A3 | Coculture vs. own exponential phase | Proteome; RNA-seq | d18, 31, 60, 89 | Main data |
| Weissberg et al. 2025 | MED4 | Axenic vs. own exponential phase | Proteome; RNA-seq | Protein d14, 31, 89; RNA d14 | Axenic reference |
| Weissberg et al. 2025 | MED4 + HOT1A3 | Coculture vs. axenic | RNA-seq | d11 (exponential), d18 | Direct contrast |
| Tolonen et al. 2006 | MED4; MIT9313 | N deprivation vs. N-replete | Microarray | 0–48 h | Acute N starvation |
| Tolonen et al. 2006 | MED4 | Cyanate or urea as sole N vs. N-replete | Microarray | Steady state | Substrate calibration |
| Tolonen et al. 2006 | MIT9313 | Nitrite or urea as sole N vs. N-replete | Microarray | Steady state | Substrate calibration |
| Read et al. 2017 | MED4 | N-depleted vs. N-replete | RNA-seq (top 50% of genes) | 3, 12, 24 h | Acute N starvation |
| Aharonovich and Sher 2016 | MED4; MIT9313 (+ HOT1A3) | Coculture vs. axenic, N-replete | RNA-seq | Exponential | N-replete control |
| Biller et al. 2016 | NATL2A (+ MIT1002) | Coculture vs. axenic, N-replete | RNA-seq (significant genes only) | −12 to 48 h | N-replete control |
| Thompson et al. 2011 | MED4 | Iron starvation; co-expression clusters | Microarray | 12–48 h | Iron-stress reference |

**Transport systems.** Transporter genes were collected per strain from four sources:
- TCDB family assignments [citation to verify];
- the KEGG BRITE transporter catalogue [citation to verify];
- Pfam domains with a transporter role [citation to verify];
- curated Cyanorak transport roles [citation to verify].

Genes were grouped into systems by genomic position and shared transporter family. Separated parts
of an ABC transporter were joined when they had complementary subunit roles. No ortholog mapping was
used.

Each system was rated by annotation support:
- *high*: a transporter domain or curated role, all required subunits, and a specific family call;
- *medium*: a missing subunit;
- *low*: family-level evidence only.

The analyses below use the 73 high- and medium-confidence systems. A system's listing of a nitrogen
class was marked *dedicated* when its gene names or products name the class, and *broad* otherwise.
Details, validation against an independently built answer key, and known false positives are given
in the Supplementary Methods.

**Expression comparison.** Because platforms and normalisations differ between studies, genes were
compared by rank rather than by fold change. Within each experiment and timepoint, genes were ranked
by log2 fold change and converted to a rank percentile (1.0 = the most up-regulated detected gene).

A gene was called up or down using the source study's significance call. In the Weissberg et al.
tables this corresponds to adjusted p < 0.05 and |log2 fold change| ≥ 1. A system was called up when
at least one detected subunit was up and none was down. Its rank is the median over detected subunits.

For tables listing only a subset of genes (Read et al. 2017; Biller et al. 2016), only "up" calls
were interpreted. The nitrogen-starvation co-expression clusters of Tolonen et al. (2006) and the
iron-response clusters of Thompson et al. (2011) were used as published gene sets.

**Analysis plan and deviations.** The analysis plan, including the calibration criteria and blind
predictions, was written before expression data were examined (except a disclosed check of protein
values for 12 genes); it is reported in the supplementary
record. Two deviations followed from the data:
- **Per-system classification dropped.** The planned classification of systems as "standing out
  beyond early axenic starvation" was not applied. The axenic sample used as the early reference
  (day 14) was already in late decline.
- **RNA not used for labels.** RNA was used only as supporting evidence. Coculture RNA is compared
  with an exponential phase that was itself nitrogen-stressed (see Results).

## Results

**The nitrogen-starvation response is present and sustained in coculture protein.** The
nitrogen-starvation regulators GlnA, NtcA and GlnB were significantly up at every coculture timepoint
(days 18–89) and in the axenic sample (15 of 15 tests). The two Tolonen et al. (2006) co-expression
clusters that rise first under nitrogen deprivation stayed at median ranks of 0.91–1.00 throughout
the coculture.

The ammonium, urea and cyanate import systems were among the most up-regulated proteins
(Fig. 1):
- the cyanate system ranked in the top 1% from day 18;
- the urea system ranked in the top 1–7% from day 18;
- the ammonium transporter Amt1 entered later, at 0.92 on day 31 and 0.98 on days 60–89.

Urease and cyanase followed their transporters.

**The same systems mark acute nitrogen starvation, not coculture as such.** In acute nitrogen
deprivation (Tolonen et al. 2006; Read et al. 2017), the ammonium, urea and cyanate systems, urease
and the regulators GlnA and NtcA were induced within 3–24 h (GlnB in Tolonen et al. only). In nitrogen-replete coculture (Aharonovich and
Sher 2016), none of them was up in MED4. One subunit of a neutral amino-acid transporter (*natF*) was
up in one of two MIT9313 cultures.

**The axenic culture loses part of the response as it declines.** In the axenic culture, which
declined from about day 14, the regulators remained high (0.93–0.98), but the import systems did
not stay together:
- the cyanate system fell from 0.99 to mid-rank (0.67–0.71);
- the urea transporter was down on day 31;
- Amt1 rose only on day 89, in death phase;
- urease stayed up.

**Import systems do not report their substrate** (Fig. 2). In MED4 grown on a single nitrogen source
(Tolonen et al. 2006):
- the urea system was not induced by urea (median rank 0.34), but UrtA was induced on cyanate;
- the cyanate system was induced on cyanate (0.96) and not on urea (0.12);
- on cyanate, the starvation marker *glnA* was also induced.

In MIT9313, the nitrite system (FocA with nitrite reductase NirA) and the urea system ranked ≥ 0.98
on both nitrite and urea. Amt1 was not tested on its substrate in any experiment. A blind prediction
that *amt1* RNA would rank in the top 10% of coculture transcripts at days 60 and 89 failed (0.06 and
0.66).

**Coculture RNA is measured against an already nitrogen-stressed baseline** (Fig. 3). In protein, the
regulators were up throughout the coculture; in RNA they were down relative to the coculture's own
exponential phase. The direct comparison of the two cultures in exponential growth (day 11) explains
part of this: coculture N-regulon transcripts were already well above axenic levels (*glnA* +2.4,
*cynA* +3.1, *urtA* +2.5 log2 fold change). After exponential growth, coculture RNA changed little (84
significant genes at day 18 vs. 877 in the axenic culture at day 14). The coculture-versus-axenic RNA
difference at that stage therefore mainly reflects the axenic decline.

**Other nitrogen routes.**
- The dipeptide transporter was raised in coculture protein (median rank 0.82–0.89). In the axenic
  culture only one subunit (DppC) rose, late. It was not induced by acute nitrogen deprivation.
- No transporter with only a broad amino-acid, polyamine or osmolyte annotation responded
  consistently: 2 of 15 detected systems were up late in coculture, and 2 of 18 in any acute-starvation
  reference.
- None of the genome's 80 peptidases, C–N hydrolases and ammonia-lyases rose in coculture without
  also rising in the axenic culture or in acute starvation, apart from a signal peptidase.

**Coculture-specific changes outside nitrogen import.** A small set of membrane genes was up in late
coculture protein but in no axenic sample and no acute-starvation reference:
- the lipid II flippase MurJ;
- the efflux and outer-membrane proteins TolC, AcrA and BamA;
- PerM and MgtE.

Most of these were already high in the axenic day-14 sample. An iron-starvation co-expression cluster
(Thompson et al. 2011) was modestly raised in coculture protein (median rank 0.71–0.77, vs. 0.52 in
the axenic sample), but not in RNA.

## Discussion

Over three months of nitrogen-limited coculture, MED4 maintains a full nitrogen-starvation response in
its proteome. Its ammonium, urea and cyanate import systems, with urease and cyanase, stay among its
most abundant proteins. These are the systems acute nitrogen starvation switches on and nitrogen-
replete coculture does not, so the coculture response reflects nitrogen limitation rather than a
general response to the partner.

This supports the description in Weissberg et al. (2025) of MED4 up-regulating nitrogen scavenging,
with three qualifications:
- it holds in protein, not in RNA;
- the affinity of the systems was not tested;
- it reflects nitrogen status rather than a specific supplied compound.

The calibration experiments show why expression cannot name the nitrogen source. The urea system did
not respond to urea and did respond to cyanate, and in MIT9313 the urea and nitrite systems responded
to both substrates. This is consistent with their shared control by NtcA. A sustained
nitrogen-starvation response is equally expected whether the partner supplies too little nitrogen to
relieve starvation or none at all. Weak signs of partial relief appear late in coculture:
- NtcA protein eases;
- protein-synthesis genes partly recover.

The import systems themselves sit at the top of the rank scale, where damping cannot be detected.

The comparison with the axenic culture is limited because that culture declines from about day 14.
Differences such as the coculture keeping its cyanate system elevated may reflect the partner, or
simply that the coculture stays alive.

Within these limits, no nitrogen route other than the starvation-induced systems responds
specifically in coculture. The dipeptide transporter is the one possible exception, and the
consistency of its subunits remains to be resolved. Absence of induction does not exclude uptake,
however: transporters already present can carry substrate, and amino-acid, polyamine and osmolyte
routes are poorly annotated in MED4.

Identifying the compounds exchanged will therefore require the producer side: the *Alteromonas*
expression data from the same cultures. It will also require direct measurements of nitrogen
compounds in the medium.

**Limitations.**
- The axenic references are in late decline or death.
- The RNA references differ between cultures.
- Significance calls follow the source studies and include a fold-change threshold.
- Transporter substrate annotation applies to whole families rather than individual genes.
- No nitrogen-compound measurements from these cultures were included.

## Figure legends

**Figure 1. Nitrogen import routes in coculture compared with reference conditions.**
- Rows: import routes, plus the nitrogen-starvation regulators.
- Columns: late coculture (protein, days 60–89); the declining axenic culture (protein); acute
  nitrogen starvation (RNA; Tolonen et al. 2006; Read et al. 2017); nitrogen-replete coculture (RNA;
  Aharonovich and Sher 2016).
- Colours: orange, up or kept; light orange, up only late; light blue, dropped or down; grey, not up.
- In the nitrogen-replete table 82% of genes have negative fold changes, so "down" there largely
  reflects the whole table.
- File: `analysis/figures/e16_conclusion.png`; per-timepoint version: `e16_conclusion_detail.png`.

**Figure 2. Calibration with single nitrogen sources.**
- (a) MED4 grown on cyanate or urea as the sole nitrogen source, and after 24 h of nitrogen
  deprivation (Tolonen et al. 2006). Bars show each gene's rank percentile.
- (b) MIT9313 grown on nitrite or urea.
- Files: `analysis/figures/e6b_cyanate_vs_urea.png`, `e8_tolonen_mit9313.png`.

**Figure 3. Coculture and axenic RNA during exponential growth and early decline.**
- Coculture-versus-axenic log2 fold change on day 11 (exponential) and day 18 (coculture day 18 vs.
  the axenic culture in late decline), for the nitrogen regulon, nitrogen import systems and
  non-nitrogen transporters.
- File: `analysis/figures/e7_baseline.png`.

## References

- Aharonovich D, Sher D (2016). Transcriptional response of *Prochlorococcus* to co-culture with a
  marine *Alteromonas*: differences between strains and the involvement of putative infochemicals.
  *ISME J*. doi:10.1038/ismej.2016.70
- Biller SJ, Coe A, Chisholm SW (2016). Torn apart and reunited: impact of a heterotroph on the
  transcriptome of *Prochlorococcus*. *ISME J*. doi:10.1038/ismej.2016.82
- Read RW, Berube PM, Biller SJ, Neveux I, Cubillos-Ruiz A, Chisholm SW, Grzymski JJ (2017). Nitrogen
  cost minimization is promoted by structural changes in the transcriptome of N-deprived
  *Prochlorococcus* cells. *ISME J*. doi:10.1038/ismej.2017.88
- Thompson AW, Huang K, Saito MA, Chisholm SW (2011). Transcriptome response of high- and
  low-light-adapted *Prochlorococcus* strains to changing iron availability. *ISME J*.
  doi:10.1038/ismej.2011.49
- Tolonen AC, Aach J, Lindell D, Johnson ZI, Rector T, Steen R, Church GM, Chisholm SW (2006). Global
  gene expression of *Prochlorococcus* ecotypes in response to changes in nitrogen availability.
  *Mol Syst Biol*. doi:10.1038/msb4100087
- Weissberg O, Aharonovich D, Sher D (2025). Transcriptomic and proteomic analysis reveals nitrogen
  recycling as a core mechanism for *Prochlorococcus* prolonged survival. *bioRxiv*.
  doi:10.1101/2025.11.24.690089

All six publications were checked against the knowledge graph's publication records (authors,
title, year, journal, DOI) on 2026-10-12.

**To add, citations not verified (not in the knowledge graph):** TCDB; KEGG/BRITE; Pfam; Cyanorak;
the multiomics knowledge graph and `multiomics_explorer`.
