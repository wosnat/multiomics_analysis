# Step 1 — Research question

## Context

Dogfood analysis. Researcher's opening prompt: *"are prochlorococcus LL clades
better equipped to deal with nutrient limitation (vs HL)?"*

Step 1 locks **the question** (not sub-questions, not methods). The dialogue
used `superpowers:brainstorming` with the research-methodology overrides
(capture here in `1_question/notebook.md`; KG grounding alongside the dialogue;
no writing-plans handoff — step 1 advances to step 2).

## KG context (grounding queries)

KG release verified before any scoping: `kg_release_info` → verdict **ok**,
KG `0.1.0-alpha.6` (built 2026-06-13, git `ffef4007`, production),
explorer `0.1.0a2`, 16/16 schema asserts pass. gene_count 124,751;
experiment_count 197; organism_count 47.

Queries issued to ground the dialogue:

1. `list_organisms(limit=50)` — full organism roster with clade + data counts.
2. `list_experiments(organism="Prochlorococcus", treatment_type=["nitrogen","phosphorus","iron"], summary=true)`
   — nutrient-limitation experiment landscape (26 matching).
3. `list_experiments(organism="Prochlorococcus", growth_phases=["nutrient_limited"], verbose=true)`
   — the 10 experiments tagged `nutrient_limited` growth phase.

### Prochlorococcus genome strains by ecotype `[KG]`

Grouping HL = HLI/HLII, LL = LLI/LLII/LLIV. `genes` = `gene_count`,
`exp` = `experiment_count` from `list_organisms`.

| Ecotype | Clade | Strain | genes | exp |
|---|---|---|---|---|
| HL | HLI | MED4 | 1976 | 114 |
| HL | HLI | MIT9515 | 1949 | 0 |
| HL | HLI | RSP50 | 1870 | 0 |
| HL | HLII | AS9601 | 1951 | 1 |
| HL | HLII | MIT0604 | 2137 | 0 |
| HL | HLII | MIT1314 | 1883 | 0 |
| HL | HLII | MIT9202 | 2027 | 0 |
| HL | HLII | MIT9215 | 2030 | 0 |
| HL | HLII | MIT9301 | 1935 | 8 |
| HL | HLII | MIT9312 | 1978 | 27 |
| HL | HLII | SB | 1977 | 0 |
| LL | LLI | MIT0801 | 2358 | 6 |
| LL | LLI | NATL1A | 2226 | 2 |
| LL | LLI | NATL2A | 2214 | 17 |
| LL | LLI | PAC1 | 2370 | 0 |
| LL | LLII | SS120 (CCMP1375) | 1964 | 64 |
| LL | LLIV | MIT1327 | 2452 | 0 |
| LL | LLIV | MIT9303 | 3114 | 4 |
| LL | LLIV | MIT9313 | 2948 | 38 |

11 HL strains, 8 LL strains. **All carry gene annotations** — so the genomic
comparison can use the full panel, not only strains with experiments.

### Nutrient-limitation experiment landscape `[KG]`

26 experiments with treatment ∈ {nitrogen, phosphorus, iron}:

| Nutrient | HL strains | LL strains | Note |
|---|---|---|---|
| Iron | MED4 | MIT9313 | Thompson 2011 — only study *designed* as HL-vs-LL contrast, same microarray platform |
| Nitrogen | MED4 (Read 2017; Weissberg 2025 preprint) | SS120, MIT9313 | spans studies/platforms |
| Phosphorus | MED4 (Martiny 2006), MIT9312, MIT9301 | NATL2A (Lin), MIT9313 | spans studies/platforms |

This landscape is background for the chosen genomic-capacity framing (expression
is not the data source here), and a possible step-5 cross-check.

## What I did

Two-question brainstorming dialogue, each grounded in the KG roster above:

1. **What does "better equipped" mean operationally?** → researcher chose
   **genomic capacity** (gene/ortholog presence-absence across ecotypes), over
   transcriptional-response or combined framings.
2. **Which nutrient's machinery?** → researcher chose **phosphorus**, over
   nitrogen / iron / all-three.

## Surprises

- **SS120 (LLII) is small** (1964 genes) despite being low-light, while the
  LLIV strains (MIT9313 2948, MIT9303 3114) are large. The genome-size gap that
  motivates the normalization confound is concentrated in LLIV, not LL as a
  whole — relevant when step 3 decides how to control for genome size. `[KG]`

## Locked question

> Do low-light-adapted (LL) *Prochlorococcus* ecotypes carry a greater or
> qualitatively different genomic complement of **phosphorus-acquisition /
> scavenging machinery** than high-light-adapted (HL) ecotypes — i.e., are LL
> clades better equipped at the genome level to handle P limitation?

**Scope:** *Prochlorococcus* genome strains only (no *Synechococcus*
outgroup); HL = HLI/HLII vs LL = LLI/LLII/LLIV, with a clade-resolved secondary
cut; P-acquisition/scavenging gene set (pho-regulon family), enumerated from the
KG in step 2.

**Deferred (just-in-time):** gene-set definition method (curated-by-function vs
ontology-term vs ortholog-group); genome-size normalization; whether to
cross-check capacity against the P/iron expression contrasts.

## Decisions

- **2026-06-13 — "equipped" = genomic capacity.** The question is answered from
  gene/ortholog presence across ecotype genomes, not from expression. Rejected:
  transcriptional-response framing and combined capacity+response framing.
- **2026-06-13 — nutrient scope = phosphorus.** Rejected: nitrogen, iron,
  all-three. Rationale: P is the classic, well-annotated *Prochlorococcus*
  ecotype genome-adaptation story, giving the cleanest first dogfood target.

## Decide-gate checklist

- **Outputs produced:** scaffold (`paper.md`, `gaps_and_friction.md`,
  `.gitignore`), this `1_question/notebook.md`. No scripts (step 1 is a
  conversation).
- **Results presented:** ecotype-strain table and nutrient-limitation
  landscape table (above, shown to researcher in chat); locked question + scope.
- **QC gate:** `kg_release_info` verdict ok (16/16 asserts) → grounding queries
  trusted. Strain counts cross-checked against `list_organisms` roster (11 HL,
  8 LL).
- **Decisions made this step:** two framing forks locked (see Decisions).
- **Advance rationale:** question and scope are locked and feasible from KG
  gene/ortholog data; step 2 can now enumerate the actual P gene set.
