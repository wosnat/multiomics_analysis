# Step 5 — Analyze

## Context

Ran the locked capacity metric (step-4 `p_capacity.py`) on the 9-strain panel
with the 23-OG focused-acquisition subset and the control suite. This step
produces the numbers; step 6 evaluates them against the preregistered predictions.

## What I did

`scripts/01_capacity_analysis.py` (imports `4_methods/p_capacity.py`; reads
frozen step-2/step-3 CSVs): per-strain focused-acquisition OG counts, focused-P
LL/HL vs controls, presence/absence repertoire, per-clade means, drop-LLIV
stability, and 3 figures.

## Results

### Per-strain focused P-acquisition OG count `[KG]`

| strain | ecotype | clade | OGs (of 23) | per-1000 genes |
|---|---|---|--:|--:|
| MED4 | HL | HLI | 13 | 6.58 |
| AS9601 | HL | HLII | 10 | 5.13 |
| MIT9301 | HL | HLII | 16 | 8.27 |
| MIT9312 | HL | HLII | 13 | 6.57 |
| NATL1A | LL | LLI | 13 | 5.84 |
| NATL2A | LL | LLI | 13 | 5.87 |
| SS120 | LL | LLII | 11 | 5.60 |
| MIT9303 | LL | LLIV | 20 | 6.42 |
| MIT9313 | LL | LLIV | 16 | 5.43 |

HL mean 13.0, LL mean 14.6, **LL/HL = 1.12** (raw count). On per-1000-genes HL is
denser (HL ~6.6 vs LL ~5.8) — consistent with the count gap being a genome-size
effect. Figure: `figures/fig3_count_by_clade.png`.

### LL/HL ratio: focused-P vs control suite `[KG]` (`fig2_llhl_ratio.png`)

| category | role | LL/HL (raw) |
|---|---|--:|
| K.2 ribosomal | invariant baseline | 1.00 |
| D.1.3 nitrogen | specificity control | 0.98 |
| D.1.2 light | positive control | 1.12 |
| D.1.7 trace-metal | specificity control | 1.14 |
| D.1.5 phosphorus (full role) | uncurated | 1.15 |
| **focused P-acquisition (23 OG)** | target | **1.12** |

Focused-P LL/HL (1.12) sits **among the trace-metal (1.14) and light (1.12)
controls**, above the ribosomal baseline (1.00) and nitrogen (0.98). Curation did
not sharpen the ratio (full role 1.15 → focused 1.12).

### Stability — drop LLIV `[KG]`

Per-clade focused count: HLI 13, HLII 13, LLI 13, LLII 11, **LLIV 18**. The LL
elevation is entirely the two LLIV strains. Removing LLIV (LL = NATL1A, NATL2A,
SS120):

| set | HL mean | LL mean | LL/HL |
|---|--:|--:|--:|
| all LL | 13.0 | 14.6 | 1.12 |
| **LL minus LLIV** | 13.0 | 12.3 | **0.95** |

Without LLIV the count difference disappears (LL slightly below HL).

### Presence/absence repertoire `[KG]` (`fig1_repertoire_heatmap.png`, `data/repertoire_by_og.csv`)

23 OGs → 10 universal, 6 variable, 5 LL-only, 2 HL-only.

| category | OGs (n_HL/n_LL) |
|---|---|
| universal (4 HL & 5 LL) | pstS, pstA, pstB, pstC, phnC, phnD, phnE, phoH, sqdB, phosphatidic-acid phosphatase |
| **LL-only** | **ptrA** Crp-family phosphate regulator (0/4); phoC acid phosphatase (0/2); ppk2 polyphosphate kinase (0/2); PAP2-superfamily phosphatase (0/2); PsiE-like (0/2) |
| HL-only | PsiP1 (1/0); putative phosphatase (1/0) |
| variable | phoB (3/3), phoR (3/4); phnD2/phnC2/phnE2/ptxD phosphonate-utilization (1 HL=MIT9301 / 1 LL=MIT9303) |

The LL-only set splits by reach: **ptrA is LL-wide** (4 of 5 LL — LLI, LLII, and
MIT9303; absent only in MIT9313 and all HL), whereas **phoC, ppk2, PAP2, PsiE-like
are LLIV-confined** (only MIT9303 + MIT9313).

## Surprises

- The strict count metric gives **no robust LL advantage**: LL/HL 1.12 is within
  the trace-metal/light control band, and the effect is entirely LLIV-driven
  (drop-LLIV → 0.95). LLI and LLII carry no more P-acquisition OGs than HL.
- The one **LL-wide** qualitative marker is `ptrA` (a Crp-family phosphate
  regulator), present in 4/5 LL and 0/4 HL — notably absent in MIT9313, the
  best-studied LL strain, but present in its LLIV sister MIT9303.
- Phosphonate-utilization paralogs (phnCDE2, ptxD) are carried by one HL (MIT9301)
  and one LL (MIT9303) — sporadic, not ecotype-linked.

## Decide-gate checklist

- **Outputs produced:** `scripts/01_capacity_analysis.py`;
  `data/focused_acquisition_counts.csv`, `llhl_ratio_vs_controls.csv`,
  `repertoire_by_og.csv`, `clade_and_stability.csv`, log; `figures/fig1–3`.
- **Results presented:** per-strain count, LL/HL-vs-controls, repertoire tables +
  3 figures (above).
- **QC gate:** focused-P LL/HL benchmarked against the validated control suite
  (ribosomal 1.00 baseline holds); drop-LLIV stability run (effect not robust);
  repertoire cross-checked against the heatmap.
- **Advance rationale:** all numbers needed to adjudicate the 3 preregistered
  predictions are produced; step 6 evaluates and harvests caveats.
