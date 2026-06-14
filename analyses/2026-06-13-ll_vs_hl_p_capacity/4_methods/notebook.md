# Step 4 — Methods (capacity-metric module)

## Context

Step 3 locked the metric: per-strain count of focused-acquisition OGs (23-OG
subset), ecotype LL/HL ratio benchmarked against controls, plus presence/absence
repertoire. Step 4 implements the reusable gene-set logic as a small module and
verifies it on hand-computed toy data. Step 5 imports it to run on the real panel.

## Module: `p_capacity.py`

Pure-pandas, no KG access (callers pass the frozen step-2/step-3 CSVs). Four
functions:

- `build_presence_matrix(genes)` → strain × OG 0/1 matrix + per-strain metadata.
  A strain "has" an OG if ≥1 of its genes maps to it — **paralogs collapse to
  presence=1** (capacity = repertoire, not copy number; locked step-3 choice).
- `per_strain_counts(matrix, meta, genome_size)` → per-strain OG count (+ per-1000).
- `ecotype_ratio(counts)` → HL/LL means, medians, LL/HL ratio, n per ecotype.
- `differential_presence(matrix, meta)` → per-OG ecotype presence counts +
  category {universal, LL_only, HL_only, variable}.

## Toy verification (`scripts/qc_toy_verification.py`)

Toy panel: HL_a {og1,og3}, HL_b {og1}, LL_x {og1, og2, og2-paralog}; genome
sizes 1000/2000/2000.

| quantity | hand-computed | module | ✓ |
|---|--:|--:|---|
| LL_x og2 presence (paralog) | 1 | 1 | ✓ collapses |
| n_ogs HL_a / HL_b / LL_x | 2 / 1 / 2 | 2 / 1 / 2 | ✓ |
| per1k HL_a / LL_x | 2.0 / 1.0 | 2.0 / 1.0 | ✓ |
| HL mean / LL mean | 1.5 / 2.0 | 1.5 / 2.0 | ✓ |
| LL/HL ratio | 1.333 | 1.333 | ✓ |
| og1 / og2 / og3 category | universal / LL_only / HL_only | same | ✓ |

`toy verification PASSED`. Edge cases covered: paralog collapse, per-1000 with
differing genome sizes, ecotype means with unequal group sizes, all three
repertoire categories.

## Sanity check vs known biology

Quick real-data peek (full run in step 5) confirms the metric tracks biology:
the core Pi transporter `pstSCAB` and phosphonate `phnCDE` classify as
**universal** (every Prochlorococcus carries the high-affinity uptake system, as
expected), while the regulatory/scavenging `ptrA`/`phoC`/`ppk2` classify as
**LL_only** — the metric separates conserved core from differential periphery,
which is what the hypothesis is about.

## Decisions

- **2026-06-14 — paralog collapse to presence/absence.** Capacity is repertoire
  breadth (distinct OGs), not gene copy number. A strain with two pstS copies
  counts the pstS OG once. (Copy-number is a separate question, out of scope.)

## Decide-gate checklist

- **Outputs produced:** `p_capacity.py` (module); `scripts/qc_toy_verification.py`.
- **Results presented:** toy verification table (above), all assertions pass.
- **QC gate:** hand-computed toy values match module output on all 6 checks incl.
  paralog collapse and the three repertoire categories → metric logic verified
  before real-data use.
- **Advance rationale:** metric module is verified and importable; step 5 runs it
  on the 9-strain panel with the locked 23-OG subset and control suite.
