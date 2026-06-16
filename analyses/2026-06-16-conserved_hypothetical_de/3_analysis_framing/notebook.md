# Step 3 — Analysis framing (the research proposal, locked here)

## Context

Steps 1–2 established the question, the operational definitions, and the candidate
universe. Step 3 makes the selection concrete, defines the response metric
operationally, validates it against characterized controls, and confirms the
premise is viable. End of this step = the proposal is locked; steps 4–6 execute it.

## Selection (agreed forks)

Researcher decisions (2026-06-16): conservation in two tiers; hypothetical by
majority rule; breadth counted by distinct treatment types; **use all experiments
regardless of table scope, caveat later**.

**Candidate ortholog groups** (`scripts/01_select_candidate_ogs.py` → `data/candidate_ogs.csv`):
- hypothetical OG = **≥80%** of its *Prochlorococcus* members are AQ≤1
- conserved, two tiers (denominator = 17 cyanorak strains):
  **core** = ≥14/17 strains, **broad** = ≥9/17 strains (core ⊂ broad)

Funnel: 5,732 cyanorak OGs → 2,787 hypothetical → **245 broad (≥9/17)**, of which
**97 core (≥14/17)** and **50 present in all 17 strains**.

**Pooled experiments** (`scripts/02_pooled_experiments.py` → `data/pooled_experiments.csv`):
from the 91, keep gene-DE omics (RNASEQ/MICROARRAY/PROTEOMICS/PAIRED), drop
`compartment` contrasts → **74 experiments across 13 treatment types** (the breadth
axis). Treatment inventory in `data/treatment_type_inventory.csv`. All table scopes
kept (per researcher decision).

## The metric (operational, in KG terms)

For each candidate OG, pull member DE with
`differential_expression_by_ortholog(group_ids=[og], organisms=['Prochlorococcus'],
experiment_ids=<74 pooled>)` — scoped to *Prochlorococcus* (the tool is
cross-organism by default) and to the pooled experiments. Then aggregate to:

- **Breadth** = number of distinct treatment types with ≥1 significant member at
  ≥1 timepoint of ≥1 experiment (permissive family-level call). Range 0–13.
- **Prominence** (the researcher's "highly responsive" axis):
  - `best_de_rank` = smallest member rank-up/rank-down reached in any experiment
    (a top-ranked responder signals strong effect within its experiment),
  - `max_abs_log2fc`,
  - `n_significant_datapoints` = count of significant member × experiment × timepoint rows.
- **Direction** = per treatment and overall up / down / mixed (from the tool's
  per-datapoint `significant_up` / `significant_down` member counts).
- **% datapoints DE** = significant ÷ tested datapoints — **reported but caveated**:
  only the `all_detected_genes` experiments carry a real tested-but-flat denominator
  (carbon, nitrogen, coculture, salt have some; light/P/Fe/viral/plastic/diel/
  darkness/growth_phase/temperature have none), so for the rest "%" is an upper bound.

Ranking: primary by **breadth**, secondary by **prominence** (best rank /
n_significant_datapoints). Both axes reported because they are independent (controls
below show a prominent-but-narrow gene).

## Hypothesis

Among conserved hypothetical *Prochlorococcus* ortholog families, a subset is
**broadly responsive** (DE across many distinct stresses) and/or **prominently
responsive** (top-ranked or repeatedly significant), pointing to an unrecognized
general-stress or core cellular function — as opposed to condition-specific dark
genes. The top of the breadth×prominence ranking is the set worth characterizing
(homologs, genomic neighborhood, co-expression, ontology of neighbors).

## Controls — selected and validated (`scripts/03_controls.py` → `data/controls_validation.csv`)

Validated with `gene_response_profile` (same permissive breadth call), in MED4:

| gene | locus | role | breadth (treatments) | best DE rank | max \|log2FC\| |
|---|---|---|---|---|---|
| hli | PMM1385 | positive (broad) | **5** (carbon, coculture, light, N, viral) | 1 | 6.04 |
| pstS | PMM0710 | prominent, not broad | 3 (carbon, N, P) | 6 | 4.67 |
| groL1/groEL | PMM1436 | positive (moderate) | 3 (carbon, light, N) | 6 | 3.08 |
| htpG | PMM0901 | negative (narrow) | 1 (N) | 7 | 2.79 |
| dnaK1 | PMM1432 | negative (silent) | 0 | — | — |

The metric separates broad (hli=5) from narrow (htpG=1, dnaK1=0). **pstS** is the
key off-diagonal: highly prominent in phosphorus (log2FC 4.67) but only moderately
broad — confirming breadth and prominence must be reported separately (the
researcher's refinement).

## Viability check (premise holds)

Probed 6 core OGs with `differential_expression_by_ortholog`: **112 significant DE
rows across 26 experiments**, spanning salt, darkness, nitrogen, iron, plastic,
viral, phosphorus, coculture, carbon, light. Conserved hypotheticals do respond
broadly — the analysis is not chasing an empty premise.

Driving example for step 4: **cyanorak:CK_00000958** ("conserved hypothetical
protein", 18 members across 17 strains; responds in salt/coculture/darkness/nitrogen
incl. a clean N-starvation time course). Alternate: CK_00000498 (HesB-like, broadest
in the probe).

## Figures (`scripts/04_selection_figures.py` → `figures/`)

- `fig1_selection_funnel.png` — 5,732 → 2,787 → 245 → 97 → 50.
- `fig2_conservation_distribution.png` — strain-coverage of hypothetical OGs;
  bimodal (singleton mode + all-17 spike) with the ≥9 / ≥14 cutoffs marked.
- `fig3_breadth_axis_experiments.png` — pooled experiments per treatment type,
  split by table scope (makes the %-metric caveat visible: 8 of 13 treatments have
  zero `all_detected_genes` experiments).
- `fig4_controls_breadth_vs_prominence.png` — the 5 controls on the two axes;
  hli top-right, pstS off-diagonal, dnaK1 at the origin. Template for the step-5
  results plot.

## Surprises

- Two a-priori "broad" positive controls (htpG, dnaK1) were actually narrow/silent
  — Prochlorococcus chaperone paralogs partition into stress-induced vs housekeeping
  copies. Validation overrode assumption; controls relabeled from the data.
- pstS responds to multiple nutrient stresses (not P-only), so it is a
  prominent-but-moderate-breadth control rather than a clean narrow one — a more
  useful off-diagonal anyway.

## Decisions

- **2026-06-16 — Conservation tiers:** core ≥14/17, broad ≥9/17 strains; hypothetical
  = ≥80% Prochlorococcus members AQ≤1. (Researcher forks.)
- **2026-06-16 — All table scopes included; table-scope limitation deferred to a
  step-6 caveat** rather than gating the metric. (Researcher instruction.)
- **2026-06-16 — Metric = breadth (distinct treatment types) primary + prominence
  (best rank / n significant datapoints / max|log2FC|) secondary + direction.**
- **2026-06-16 — Ortholog DE scoped to Prochlorococcus + the 74 pooled experiments**
  (the tool is cross-organism; must be filtered).

## Decide-gate checklist

- **Outputs produced** — `scripts/01_select_candidate_ogs.py`,
  `02_pooled_experiments.py`, `03_controls.py`; `data/candidate_ogs.csv` (245),
  `data/pooled_experiments.csv` (74), `data/treatment_type_inventory.csv`,
  `data/controls_validation.csv`; `scripts/04_selection_figures.py` →
  `figures/fig{1,2,3,4}_*.png`; logs `data/0{1,2,3,4}_*.log`. Command lines in each
  script header.
- **Results presented** — selection funnel, 13-treatment breadth axis, controls
  validation table, and the 6-OG viability probe shown inline above.
- **QC gate** —
  - controls behave: breadth metric separates hli(5)/groEL(3) from htpG(1)/dnaK1(0) ✓
  - premise viable: 6 core OGs → 112 significant DE rows over 10 treatment types ✓
  - ortholog-DE cross-organism leak identified → scope to Prochlorococcus in step 4 ✓
- **Decisions made this step** — four, dated above.
- **Advance rationale** — selection, pooled experiments, metric definition, and
  controls are locked and validated; the premise holds; ready to build the scoring
  module (step 4) on driving example CK_00000958.
