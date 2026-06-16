# Step 1 — Research question

## Context

First step of the **characterization follow-on** analysis. The sibling selection
analysis (`analyses/2026-06-16-conserved_hypothetical_de/`) ended at a ranked
shortlist of conserved-hypothetical *Prochlorococcus* ortholog families and
explicitly spun the characterization half out to a separate analysis (see that
analysis's `1_question/notebook.md`, "Reopened 2026-06-16 — scope narrowed to
selection"). This is that separate analysis.

No computation here — step 1 is a conversation plus lightweight KG grounding.

Researcher's opening prompt: *"I identified interesting genes in
analyses/2026-06-16-conserved_hypothetical_de. What can we learn about them from
the KG?"*

Researcher steer during co-define:
1. **Family scope** → the **14 core families** first (broad AND prominent — the
   confound-resistant set), with the other 71 shortlist families as a lighter
   backdrop if useful.
2. **Angles** → all of: cross-organism homologs, genomic neighborhood,
   co-expression / cluster membership, ontology / domains / sequence, other derived
   metrics, and direct mention in the source publications.
3. **Framing** → *"I don't think these genes are related but would like to have
   info that will give me power when analysing future omics. That also include the
   DE response from the prev. analysis."* → treat the 14 as **independent
   entities** (do not hunt for a shared module); build a **per-family reference
   dossier** aimed at interpretive power for future omics; **carry the prior DE
   fingerprint forward** into each dossier.

## Locked question

> For each of the **14 core conserved-hypothetical *Prochlorococcus* ortholog
> families** — treated **independently**, not as a related set — assemble a
> **characterization dossier** from the KG that maximizes interpretive power for
> future omics: pairing each family's existing **DE response fingerprint** (breadth,
> prominence, direction-by-treatment, from the selection analysis) with everything
> the KG holds — **cross-organism homologs**, **conserved genomic neighborhood**,
> **co-expression cluster membership**, **ontology / domains / sequence features**,
> **other derived metrics**, and any **direct mention in the source publications**.

**Deliverable shape:** one reference table (one row per family; columns =
characterization axes + DE fingerprint) plus a readable per-family card — a lookup
resource, not a synthesis. The 14 are not assumed related; incidental overlaps are
noted where they occur but finding a module is not the objective.

**Interactive presentation:** results are also surfaced in the repo-level dashboard
(`dashboard/`), which the selection analysis already wired with a
`placeholder_characterization()` section and a documented plug-in pattern (README:
write a `characterization_section()` that reads this analysis's committed `data/*.csv`
and returns a `Section`, then replace the placeholder in `SECTIONS`). The
characterization section should let a researcher pick a family and see, in one view,
its DE fingerprint alongside its KG characterization panels — the per-family dossier,
made interactive. The static `paper.md` + figures remain the source of record; the
dashboard is an additional view (built post-step-6, not part of the 6-step pipeline).

## Input set — the 14 core families

From `analyses/2026-06-16-conserved_hypothetical_de/6_evaluate/data/handoff_shortlist.csv`,
rows with `core14 = True`:

| # | og_id | consensus_product | proc_strains | breadth | best_rank | max_abs_log2fc |
|---|---|---|---|---|---|---|
| 1 | cyanorak:CK_00019843 | conserved hypothetical protein | 15 | 9 | 1 | 8.66 |
| 2 | cyanorak:CK_00000141 | uncharacterized conserved secreted protein | 13 | 9 | 1 | 6.6 |
| 3 | cyanorak:CK_00001734 | conserved hypothetical protein | 17 | 7 | 2 | 9.6 |
| 4 | cyanorak:CK_00045004 | conserved hypothetical protein family PM-17 | 14 | 7 | 1 | 9.3 |
| 5 | cyanorak:CK_00004021 | uncharacterized conserved membrane protein | 14 | 7 | 3 | 7.33 |
| 6 | cyanorak:CK_00001345 | uncharacterized conserved secreted protein | 17 | 6 | 8 | 13.27 |
| 7 | cyanorak:CK_00049482 | conserved hypothetical protein | 17 | 6 | 2 | 13.05 |
| 8 | cyanorak:CK_00003473 | uncharacterized secreted protein, Prochlorococcus-specific | 17 | 6 | 2 | 12.26 |
| 9 | cyanorak:CK_00009151 | conserved hypothetical protein | 9 | 6 | 8 | 11.97 |
| 10 | cyanorak:CK_00039303 | conserved hypothetical protein | 13 | 6 | 98 | 11.5 |
| 11 | cyanorak:CK_00000498 | HesB-like domain-containing protein | 17 | 6 | 71 | 11.29 |
| 12 | cyanorak:CK_00045754 | conserved hypothetical protein | 12 | 6 | 3 | 10.81 |
| 13 | cyanorak:CK_00041192 | conserved hypothetical protein | 17 | 6 | 3 | 6.58 |
| 14 | cyanorak:CK_00000284 | Conserved hypothetical protein | 17 | 6 | 2 | 6.12 |

## KG grounding

- `kg_release_info` → KG release **0.1.0-alpha.6** (built 2026-06-16, today),
  explorer **0.1.0a3**, verdict **ok** (16/16 schema asserts pass). KG totals:
  124,751 genes, 197 experiments, 43 papers, 47 organisms.
- **Provenance note:** the selection analysis ran on **0.1.0-alpha.5** (built
  2026-06-09). This analysis runs one release newer. The cyanorak OG ids are stable
  identifiers and still resolve, but homolog/expression/cluster edges reflect
  alpha.6. Each OG is re-resolved fresh in step 2 rather than assuming the alpha.5
  metrics carry over. (Carried as a `gaps_and_friction.md` entry.)

## Decisions

- **2026-06-16 — Scope is the 14 core families** (`core14 = True`), not all 85
  shortlist families. Driven by the researcher's preference for the
  confound-resistant set (prominence is not coverage-driven; see the selection
  analysis's coverage-confound caveat). The other 71 may serve as a backdrop only.
- **2026-06-16 — The 14 are treated as independent entities.** The deliverable is a
  per-family dossier, not a cross-family synthesis; no shared-module hypothesis is
  assumed or sought.
- **2026-06-16 — The prior DE fingerprint is carried forward** into each dossier as
  a first-class column block, per researcher request.
- **2026-06-16 — Results are also presented interactively** via a
  `characterization_section()` added to the existing repo-level dashboard
  (`dashboard/build_dashboard.py`), replacing the `placeholder_characterization()`
  section, per researcher request. The dashboard is a presentation layer built after
  step 6, not part of the 6-step pipeline.

## Decide-gate checklist

- **Outputs produced** — `1_question/notebook.md` (this file); scaffold (`paper.md`
  skeleton with Question populated, `gaps_and_friction.md` header, `.gitignore`). No
  scripts/data/figures (step 1 is conversation only).
- **Results presented** — the 14-family input table and the KG release grounding
  shown to the researcher in chat and recorded here.
- **QC gate** — `kg_release_info` verdict = ok (16/16 asserts) → KG release matches
  explorer expectations, safe to proceed.
- **Decisions made this step** — 14-core scope; independent-entity framing; DE
  fingerprint carried forward (all dated 2026-06-16, above).
- **Advance rationale** — the question is locked, the input set is enumerated and
  frozen, and the KG holds the data types the dossier needs; ready to enumerate what
  the KG actually returns for these 14 OGs in step 2.
