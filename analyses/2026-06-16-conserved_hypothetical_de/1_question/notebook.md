# Step 1 — Research question

## Context

First step of the analysis: turn the researcher's prompt into a locked,
answerable research question, grounded in what the KG actually holds. No
computation here — this step is a conversation plus lightweight KG grounding.

Researcher's opening prompt: *"What are the top differentially expressed
uncharacterized Prochlorococcus genes and what can we learn about them?"*

## Locked question

> Across *Prochlorococcus*, which **conserved hypothetical ortholog families** —
> no assigned function but widely conserved (many orthologs) — are
> **differentially expressed across many distinct conditions**, and what can the
> KG tell us about them?

Operational intent (exact definitions deferred to the steps that need them, per
just-in-time formalization):
- **Uncharacterized** = no assigned function (hypothetical / conserved
  hypothetical). Exact annotation field to be verified in step 2.
- **Conserved** = ortholog family with many members. Unit of analysis = the
  **ortholog group**, not the single-strain locus tag.
- **Broadly responsive** = differentially expressed across many distinct
  conditions, pooled at the ortholog-family level so all strains contribute.
- **What can we learn** = KG-held characterizing evidence — cross-organism
  homologs, conserved genomic neighborhood, co-expression cluster membership,
  ontology of neighbors / co-expressed genes, response-profile fingerprint.

## What I did

Clarifying dialogue with the researcher (brainstorming-style, three forks put as
explicit choices), each grounded against KG queries before being posed.

Researcher's choices on the three forks:
1. **Strain scope** → all *Prochlorococcus* strains (not MED4 only).
2. **Meaning of "top DE"** → broadly responsive (across many conditions), not the
   single strongest single-condition responder.
3. **"Uncharacterized"** → hypothetical / no known function (exact field to be
   verified in step 2).

Researcher then refined: focus on **conserved** hypotheticals (many orthologs),
analysis at the **ortholog level**. This refinement resolves the cross-strain
coverage tension (below) by making conservation a selection criterion and the
ortholog group the unit of analysis.

## KG context

Queries run to ground the dialogue (counts are `[KG]`):

- `kg_release_info` → KG release **0.1.0-alpha.5** (built 2026-06-09),
  explorer **0.1.0a3**, verdict **ok** (16/16 schema asserts pass). KG totals:
  120,416 genes, 197 experiments, 43 papers, 45 organisms.
- `list_experiments(organism="Prochlorococcus", summary=true)` →
  **91 DE experiments** matched. Breakdowns:

  | Strain | DE experiments |
  |---|---|
  | MED4 | 41 |
  | MIT9313 | 17 |
  | NATL2A | 9 |
  | MIT9312 | 8 |
  | SS120 (CCMP1375) | 6 |
  | MIT9301 | 4 |
  | MIT9303 | 2 |
  | MIT0801 | 2 |
  | AS9601 | 1 |
  | NATL1A | 1 |

  | Treatment type | count |   | Omics type | count |
  |---|---|---|---|---|
  | carbon | 18 |  | RNASEQ | 32 |
  | nitrogen | 12 |  | MICROARRAY | 25 |
  | light | 10 |  | PROTEOMICS | 16 |
  | compartment | 9 |  | METABOLOMICS | 12 |
  | phosphorus | 9 |  | VESICLE_PROTEOMICS | 4 |
  | growth_phase | 6 |  | VESICLE_DNASEQ | 1 |
  | coculture | 5 |  | PAIRED_RNASEQ_PROTEOME | 1 |
  | iron | 5 |  | | |
  | viral | 4 |  | | |
  | plastic | 4 |  | | |
  | salt | 3 |  | | |
  | darkness | 3 |  | | |
  | diel | 2 |  | | |
  | temperature | 1 |  | | |

  Table scope (matters for fair cross-condition comparison): `all_detected_genes`
  27, `significant_only` 20, `filtered_subset` 17, unspecified 16,
  `significant_any_timepoint` 10, `top_n` 1.

- `list_organisms` → MED4 is the deepest strain: 1,976 genes, 17 publications,
  the only strain with `PAIRED_RNASEQ_PROTEOME`, spanning treatment types
  coculture/carbon/salt/viral/phosphorus/light/iron/nitrogen/diel/growth_phase.

### Structural surprise / constraint

Most multi-condition breadth lives in **MED4** (41 of 91 DE experiments). Several
strains have only 1 experiment (AS9601, NATL1A), so a gene cannot be "responsive
across many conditions" *within* those strains. "Broadly responsive across all
strains" is therefore only coherent when responsiveness is pooled at the
**ortholog-group level**. The researcher's refinement (conserved families, ortholog
unit) aligns the question with this constraint rather than fighting it.

## Decisions

- **2026-06-16 — Unit of analysis is the ortholog group.** Driven by the
  data constraint above (condition breadth concentrated in MED4; thin per-strain
  coverage elsewhere) plus the researcher's stated interest in conserved
  hypotheticals. Single-strain locus tags roll up into ortholog families; "broadly
  responsive" and "conserved" are both measured at the family level.
- **2026-06-16 — Scope is all *Prochlorococcus* strains**, with MED4 expected to
  carry most condition breadth and other strains contributing conservation
  evidence and generality checks.

## Decide-gate checklist

- **Outputs produced** — `1_question/notebook.md` (this file); scaffold
  (`paper.md` skeleton with Question populated, `gaps_and_friction.md` header,
  `.gitignore`). No scripts/data/figures (step 1 is conversation only).
- **Results presented** — KG grounding tables above (strain / treatment / omics /
  table-scope breakdowns) shown to the researcher in chat and recorded here.
- **QC gate** — `kg_release_info` verdict = ok (16/16 asserts) → KG release matches
  explorer expectations, safe to proceed.
- **Decisions made this step** — ortholog group as unit; all-strain scope (both
  dated 2026-06-16, above).
- **Advance rationale** — the question is locked, the unit of analysis is fixed,
  and the KG demonstrably holds the data types the question needs; ready to
  enumerate specific KG entries in step 2.
