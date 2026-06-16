# Step 4 — Methods (the scoring module)

## Context

Step 3 locked the metric (breadth + prominence + direction). Step 4 implements it as
a reusable module, verifies it on hand-built toy data, walks it through the driving
example `cyanorak:CK_00000958`, and cross-checks it against the step-3 controls. No
run over all 245 yet — that is step 5.

## Data source (resolved during this step)

The metric needs per-datapoint **rank and magnitude**, which
`differential_expression_by_ortholog` does **not** carry (its rows are member counts;
its envelope has only an aggregate `max_abs_log2fc`). The per-gene tool
`differential_expression_by_gene` carries everything per gene × experiment ×
timepoint — `log2fc`, `rank_up`, `rank_down`, `expression_status`, `treatment_type`.
So it is the single scoring source; the ortholog tool was triage only.

`differential_expression_by_gene` is single-organism **and** validates that
`experiment_ids` belong to that organism. Extraction therefore batches per strain,
passing each strain only its own pooled experiments (see
`gaps_and_friction.md` 2026-06-16).

## Module

`4_methods/og_response_metric.py` — owns the aggregation methodology only (extraction
lives in `scripts/`). Public function `aggregate_og_metrics(de)` takes a long per-gene
DE table with `og_id` attached and returns one row per ortholog group:
breadth, n_significant_datapoints, best_rank, max_abs_log2fc, direction,
direction_by_treatment, n_tested_datapoints, pct_datapoints_de, n_members_with_de.

**Toy verification** (`python og_response_metric.py` → `_verify()`): two hand-built
OGs with values computed by hand; all assertions pass (breadth, significant/tested
counts, best_rank, max|log2FC|, direction, per-treatment direction, %, ranking
order).

## Worked example — `cyanorak:CK_00000958`

`scripts/01_worked_example.py`: 18 members across 17 strains; 5 members carry DE in
the pooled experiments; 52 tested datapoints, 13 significant.

| metric | value | traces to |
|---|---|---|
| breadth | 4 | coculture, darkness, nitrogen, salt |
| n_significant_datapoints | 13 | the 13 significant rows |
| best_rank | 24 | NATL2A, extended darkness, `rank_up`=24 |
| max_abs_log2fc | 11.81 | MED4 `PMM0640`, coculture, log2FC −11.81 |
| direction | mixed | down in coculture/N/salt; up in darkness |
| direction_by_treatment | coculture↓, darkness↑, nitrogen↓, salt↓ | per-treatment |
| pct_datapoints_de | 0.25 (13/52) | caveated (significant-only tables) |

Every aggregated number traces to a per-datapoint row (full table in
`data/worked_example_CK_00000958.csv`). Note the family responds in **opposite
directions in different conditions** (down under coculture/N/salt, up under darkness)
— `direction_by_treatment` preserves that; a single overall direction would hide it.

## QC — controls through the new metric path

`scripts/qc_controls_via_metric.py` runs the new aggregation on the 5 step-3 controls
(each a singleton OG) and compares to `controls_validation.csv` (computed in step 3 by
a *different* tool, `gene_response_profile`):

| gene | breadth (metric / step3) | max\|log2FC\| (metric / step3) |
|---|---|---|
| hli | 5 / 5 | 6.04 / 6.04 |
| pstS | 3 / 3 | 4.67 / 4.67 |
| groL1/groEL | 3 / 3 | 3.08 / 3.08 |
| htpG | 1 / 1 | 2.79 / 2.79 |
| dnaK1 | 0 / 0 | — / — |

**breadth 5/5, max|log2FC| 5/5 — exact agreement.** Two independent code paths land
on the same numbers.

## Surprises

- At the family level the strongest-magnitude datapoint (|log2FC| 11.8, MED4
  coculture) and the best-rank datapoint (rank 24, NATL2A darkness) are different
  members in different conditions — magnitude and rank are genuinely distinct
  prominence facets, both worth keeping.

## Decisions

- **2026-06-16 — Scoring source = `differential_expression_by_gene`** (per gene;
  carries rank + log2fc), batched per strain with strain-specific `experiment_ids`.
  The ortholog tool lacks per-datapoint rank/magnitude, so it is triage only.

## Decide-gate checklist

- **Outputs produced** — `og_response_metric.py` (module + `_verify()`);
  `scripts/01_worked_example.py`, `scripts/qc_controls_via_metric.py`;
  `data/worked_example_CK_00000958.csv`, `..._metric.csv`,
  `data/qc_controls_via_metric.csv`; logs `data/01_worked_example.log`,
  `data/qc_controls_via_metric.log`. Command lines in script headers.
- **Results presented** — toy-verify table, worked-example metric + the 13
  significant datapoints, controls cross-check table — all inline above.
- **QC gate** —
  - toy assertions pass (hand-calculated) ✓
  - controls cross-check vs step-3: breadth 5/5, max|log2FC| 5/5 ✓
  - every worked-example aggregate traces to a source datapoint ✓
- **Decisions made this step** — scoring source + per-strain batching (dated above).
- **Advance rationale** — the metric is implemented, toy-verified, control-validated,
  and demonstrated on the driving OG; ready to run over all 245 candidates in step 5.
