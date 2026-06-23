# Predator / grazing perspective — KG curation report

**Date:** 2026-06-23
**Purpose:** A selection worklist for adding a *predation / grazing* perspective to the
multi-omics KG (which is centered on Prochlorococcus and organized around per-gene
expression, metabolomics, and orthologs). Scope of this report = **Path 2: protist
grazing** (heterotrophic nanoflagellates, dinoflagellates, ciliates, microzooplankton).
The viral/phage axis (Path 1) is out of scope here.

**Provenance:** All entries below are from a verified web-literature search
(`[verified, web]`), **not** from the KG. The search fanned out across 5 angles, fetched
20 sources, extracted 90 candidate claims, and adversarially fact-checked 25 (21
confirmed, 4 killed). Before curating any paper, confirm it actually ships reusable
per-gene / per-metabolite tables — several full texts were access-blocked during
verification, so data-availability is provisional.

---

## Bottom line (read before selecting)

The omics data this KG would ideally ingest **does not exist in the published literature** —
this is a true literature gap, not a "we just haven't curated it yet" gap:

- **Tier A — Prochlorococcus's own omics response to grazing: 0 papers.** No one has
  measured the transcriptome / proteome / metabolome of Prochlorococcus responding to a
  grazer or grazing cue.
- **Tier B — grazer-side omics while eating picocyanobacteria: 0 papers.** The methods are
  mature, but every grazer-transcriptomics study used the *wrong prey* (eukaryotic algae or
  heterotrophic bacteria).
- **Tier C — grazing-rate / mortality / ecology: this is where all the evidence lives.**
  These document predation magnitude and grazer identity but do **not** map onto a
  gene-centric schema.

**Implication for selection:** nothing here is a drop-in omics import. The real choices are
(1) curate Tier C as a non-omics "predation context" layer, (2) treat the one cultured
Prochlorococcus–grazer system as a platform to *generate* the missing data, and/or (3) defer
Path 2 and prioritize the viral axis. See *Recommended selection* at the end.

---

## Priority legend

| Tag | Meaning |
|-----|---------|
| **P1** | Add first — highest value for a predation layer (Prochlorococcus-specific or the headline quantitative context) |
| **P2** | Add if building out the layer — useful grazer-identity / rate context |
| **P3** | Optional / supporting — Synechococcus-only or redundant context |
| **—** | Do **not** curate into this KG (wrong prey, or already present) — keep only as a methods reference |

**Schema fit** = does the paper produce per-gene / per-metabolite data that maps onto the KG's
expression/metabolomics core? (`omics` = yes; `rate/ecology` = no, would need a new node/metric type.)

---

## Tier A — Prochlorococcus prey-side omics response to grazing

**No papers exist.** This is the primary target and it is empty in the literature.

The closest prey-side omics study is in Tier B-adjacent territory (Synechococcus, and a null
result for grazing) — see *cyanovirocell* row below.

---

## Tier B — grazer-side omics while consuming picocyanobacteria

**No papers exist with picocyanobacterial prey.** The studies below are correct in *method*
(grazer transcriptomics) but feed the protist the wrong prey, so they are **not** curation
targets — listed only as methodological precedent for a future experiment.

| Paper | Grazer / Prey | Data type | Schema fit | Link | Priority | Notes |
|-------|---------------|-----------|------------|------|----------|-------|
| Rubin et al. 2019, *Front. Mar. Sci.* 6:246 | *Oxyrrhis marina* / *Heterosigma akashiwo*, *Isochrysis galbana* (algae) | OMICS (transcriptomics) | omics | [link](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2019.00246/full) | — | Wrong prey (eukaryotic algae). Method template only. |
| *Cafeteria burkhardae* study 2020, *ISME J* | *Cafeteria burkhardae* / *Dokdonia* sp. MED134 (flavobacterium) | OMICS (transcriptomics, 2056 DEGs) | omics | [link](https://pmc.ncbi.nlm.nih.gov/articles/PMC7852580/) | — | Wrong prey (heterotrophic bacterium). Method template only. |
| Zou et al. 2020, *Microorganisms* | *Tetrahymena thermophila* / *E. coli*, *Bacillus* + 13 strains | OMICS (transcriptomics) | omics | [link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7232342/) | — | Wrong prey. Method template only. |

---

## Tier B-adjacent — closest existing prey-side omics (still not a clean grazing dataset)

| Paper | Prey / Grazer | Data type | Schema fit | Link | Priority | Notes |
|-------|---------------|-----------|------------|------|----------|-------|
| Howard-Varona et al. 2022, *ISME Communications* 2(1):94; DOI 10.1038/s43705-022-00169-6 | *Synechococcus* WH8102 / *Oxyrrhis marina* (dinoflagellate) | OMICS (transcripts + endometabolites) | omics | [link](https://academic.oup.com/ismecommun/article/2/1/94/7461047) | P3 | "Protist impacts on marine cyanovirocell metabolism." **Grazing had NO measurable effect on uninfected Synechococcus** — host response appeared only in cyanophage-infected cells. Synechococcus, not Pro. Best existing *template* for a prey-side grazing-omics design. |

---

## Tier C — grazing-rate / mortality / ecology

These are rate/ecology studies. They document *why predation matters* and *who the grazers
are*, but carry no per-gene data — curating them means a new "predation context" node/metric
type, not an expression import.

| Paper | Prey / Grazer | Data type | Schema fit | Link | Priority | Notes |
|-------|---------------|-----------|------------|------|----------|-------|
| Beatty, Stewart, Turk-Kubo, Lindell & Caron **2025**, *Front. Microbiol.* 16:1706193; DOI 10.3389/fmicb.2025.1706193 | **Prochlorococcus MED4** / *Paraphysomonas bandaiensis* (HNF) | RATE/ECOLOGY (FLB, dilution, flow cytometry) | rate/ecology | [link](https://pmc.ncbi.nlm.nih.gov/articles/PMC12714900/) | **P1** | The **only cultured Prochlorococcus–grazer pairing**. FLB underestimated mortality ~27%, dilution ~54%. No omics — but this is the experimental system that could *generate* the missing Tier A/B data. Lindell lab. |
| Nat. Commun. **2024**, s41467-024-46165-3 (PMC10920773) | Prochlorococcus / heterotrophic nanoflagellates (in situ) | RATE/ECOLOGY (modeling: SeaFlow + iPolony + nanoflagellate counts) | rate/ecology | [link](https://www.nature.com/articles/s41467-024-46165-3) | **P1** | Headline mortality partitioning: **~87–89% of Pro losses to grazing vs ~6% viral** (NPSG surface). The quantitative justification for a predation layer. Geographically bounded. |
| Frias-Lopez, Thompson, Waldbauer & Chisholm **2009**, *Environ. Microbiol.* 11(2):512–525; DOI 10.1111/j.1462-2920.2008.01793.x | Pro, Syn / 4 protist groups | RATE/ECOLOGY (RNA-SIP, 18S labelling) | rate/ecology | [link](https://pmc.ncbi.nlm.nih.gov/articles/PMC2702499/) | P2 | In situ active grazers: Prymnesiophyceae, Dictyochophyceae, Bolidomonas, Dinoflagellata (3 framed as putative mixotrophs). Chisholm lab — provenance consistent with KG. Best grazer-identity source. |
| Guillou, Jacquet, Chrétiennot-Dinet & Vaulot **2001**, *Aquat. Microb. Ecol.* 26:201–207 | Pro, Syn / *Picophagus flagellatus*, *Symbiomonas scintillans* | RATE/ECOLOGY (ingestion, flow cytometry) | rate/ecology | [link](https://www.researchgate.net/publication/200146637_Guillou_L_Jacquet_S_Chretiennot-Dinet_MJ_Vaulot_D_Grazing_impact_of_two_small_heterotrophic_flagellates_on_Prochlorococcus_and_Synechococcus_Aquat_Microb_Ecol_26_201-207) | P2 | Named flagellate predators of Pro; ~2 doublings/d on Pro; carbon-transfer efficiency 23% (Pro) vs <1% (Syn). |
| Apple, Strom, Palenik & Brahamsha **2011**, *Appl. Environ. Microbiol.* 77(9):3074–3084; DOI 10.1128/AEM.02241-10 | **Synechococcus** (WH8102, CC9605, CC9311, CC9902) / *Oxyrrhis marina* | RATE/ECOLOGY (ingestion) | rate/ecology | [link](https://journals.asm.org/doi/full/10.1128/aem.02241-10) | P3 | Strain-variable grazing susceptibility; WH8102 grazed least. Synechococcus, not Pro. |
| Worden & Binder **2003**, *Aquat. Microb. Ecol.* 30:159–174 | Pro, Syn / community | RATE/ECOLOGY (dilution / Landry–Hagström) | rate/ecology | [link](https://www.researchgate.net/publication/200146984_Application_of_dilution_experiments_for_measuring_growth_and_mortality_rates_among_Prochlorococcus_and_Synechococcus_populations_in_oligotrophic_environments) | P3 | Grazing mortality 0.25–0.85 d⁻¹ (Pro), 0.13–0.51 d⁻¹ (Syn). **Cite as *Aquat. Microb. Ecol.* 30:159–174** — an ASLO/L&O attribution for these numbers failed verification. |
| Ribalet et al. **2015**, *PNAS* 112(26):8008–8012 (PMC4491802) | Prochlorococcus / community | RATE/ECOLOGY (continuous flow cytometry, SeaFlow) | rate/ecology | [link](https://www.pnas.org/doi/10.1073/pnas.1424279112) | P3 | Diel division/loss modeling; lumps grazing + viral into one net mortality. **Do not** carry the "strict night-gated, 90° phase-lag mortality" framing — adversarially refuted. |

---

## Additional fetched sources — not individually characterized

These were retrieved during the search (grazer-taxa / prey-defense and review angles) but did
not yield separately verified claims, so their details are **not** confirmed here. Worth a
look if building out the layer; do not cite without checking.

| Source | Angle | Type | Link |
|--------|-------|------|------|
| *FEMS Microbiol. Ecol.* 92(11):fiw154 (2016) | Grazer taxa / prey defense | primary | [link](https://academic.oup.com/femsec/article/92/11/fiw154/2402901) |
| PMC10756674 | Grazer taxa / prey defense | primary | [link](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10756674/) |
| PubMed 16011757 | Grazer taxa / prey defense | primary | [link](https://pubmed.ncbi.nlm.nih.gov/16011757/) |
| PubMed 29215213 | Grazer taxa / prey defense | primary | [link](https://pubmed.ncbi.nlm.nih.gov/29215213/) |
| *Trends Microbiol.* S0966-842X(24)00313-5 | Gap assessment | review (secondary) | [link](https://www.cell.com/trends/microbiology/abstract/S0966-842X(24)00313-5) |
| *Trends Microbiol.* S0966-842X(23)00258-5 | Gap assessment | review (secondary) | [link](https://www.cell.com/trends/microbiology/abstract/S0966-842X(23)00258-5) |

---

## Already in the KG (not a new add)

- **Aharonovich & Sher 2016, *ISME J*** (MED4 / MIT9313 vs *Alteromonas macleodii* HOT1A3) —
  DOI 10.1038/ismej.2016.70. A heterotrophic-bacterium **co-culture**, not predation; already
  curated. Flagged here only because the search surfaced it as the lone Prochlorococcus
  omics-of-biotic-interaction study.

---

## Claims NOT to carry into curation (adversarially refuted)

- "Heterotrophic nanoflagellates feed *indiscriminately* on multiple Prochlorococcus prey
  classes" — refuted 0–3.
- "Prochlorococcus mortality is strictly night-restricted with a fixed 90° phase lag and no
  daytime mortality" (over-reading of Ribalet 2015) — refuted 0–3.
- Worden & Binder numbers attributed to an ASLO/L&O page — refuted 1–2 on venue; the same
  numbers verified from *Aquat. Microb. Ecol.* 30:159–174.

---

## Recommended selection

Given the gap, three coherent packages (not mutually exclusive):

1. **Minimal context layer (P1 only):** add Beatty 2025 + Nat. Commun. 2024 as a small
   non-omics "predation context" — the cultured system + the headline mortality numbers.
   Lowest effort; documents *that* predation matters and *that* a Pro–grazer system exists.
2. **Full grazing-context layer (P1 + P2 + P3):** the whole Tier C set as a predation
   node/metric type — grazer taxa, rates, mortality partitioning. Needs schema work; gives a
   complete ecological picture but stays disconnected from the gene-expression core.
3. **Generate, don't curate:** treat Beatty 2025's MED4 × *Paraphysomonas* system + the
   Howard-Varona 2022 cyanovirocell design as a blueprint to run the missing Tier A
   experiment and produce a genuinely novel prey-side grazing transcriptome.

**Open question for the researcher:** is the goal to *represent* predation pressure in the KG
(→ package 1 or 2), or to *fill the omics gap* (→ package 3, a wet-lab project)? That decision
determines whether any of these papers get curated at all.
