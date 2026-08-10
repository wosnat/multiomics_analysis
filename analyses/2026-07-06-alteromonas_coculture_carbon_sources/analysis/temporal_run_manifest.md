# Temporal overlay — run manifest (facts only)

HOT1A3 starvation-vs-exponential temporal overlay, RNA-seq only. Same modules and
committed scoring code as the primary run (`methods/score_modules.py`,
`build_modules_from_csv`). Difference-of-starvation-responses; corroboration only —
no carbon source is named here (that is the researcher's call, and the design says
temporal alone cannot name one).

## Experiments (confirmed via KG)

Both arms: `treatment = PRO99-lowN nutrient starvation` vs `control = PRO99-lowN
exponential growth`, RNASEQ, DESeq2, `table_scope = all_detected_genes` → scope
`genome_wide` for every timepoint.

- **coculture arm** `…_growth_state_pro99lown_nutrient_starvation_hot1a3_rnaseq_coculture`
  — 5 timepoints: day 18, day 31, day 60, day 89, **days 60+89** (a pooled contrast).
- **axenic arm** `…_growth_state_pro99lown_nutrient_starvation_hot1a3_rnaseq_axenic`
  — 3 timepoints: day 18, day 31, **days 60+89**.
- **Timepoint mismatch (KG reality):** the axenic arm has no standalone day 60 / day 89
  contrasts — only the pooled `days 60+89`. So the coculture-vs-axenic comparison
  (and the `coculture_specific` flag) is defined only at the **3 common labels**
  (day 18, day 31, days 60+89). Coculture day 60 / day 89 rows are scored and
  reported but carry `coculture_specific = no_axenic_match`.

## Step 1 — per-(arm × timepoint) DE pulls (`analysis/cache/temporal/`)

All pulls: 3947 genes, `all_detected_genes`, no lost signs (sign distribution
48–53 % negative throughout — healthy).

| arm | timepoint | n_genes | % negative |
|---|---|---|---|
| coculture | day 18 | 3947 | 48.7 |
| coculture | day 31 | 3947 | 51.1 |
| coculture | day 60 | 3947 | 48.3 |
| coculture | day 89 | 3947 | 50.1 |
| coculture | days 60+89 | 3947 | 48.1 |
| axenic | day 18 | 3947 | 52.2 |
| axenic | day 31 | 3947 | 53.2 |
| axenic | days 60+89 | 3947 | 48.6 |

## Steps 2–3 — scoring + side-by-side (`hot1a3_temporal_module_scores.csv`)

33 modules, clean 84-system inorganic controls, `scope="genome_wide"`,
`n_perm=10000`, `seed=0`. One row per (module × timepoint) with coculture
effect/q, axenic effect/q, n_systems, and `coculture_specific`.

**Modules called up (q<0.10) per timepoint:**

| arm | day 18 | day 31 | day 60 | day 89 | days 60+89 |
|---|---|---|---|---|---|
| coculture | carbohydrate | L-lactate, peptide/nickel | L-lactate, peptide/nickel | L-lactate | L-lactate, peptide/nickel |
| axenic | — | — | (no axenic contrast) | (no axenic contrast) | L-lactate |

**Coculture-specific-up** (up in coculture but NOT axenic, at a common timepoint):

- **day 18: 1** — carbohydrate
- **day 31: 2** — L-lactate, peptide/nickel
- **days 60+89: 1** — peptide/nickel  *(L-lactate is up in BOTH arms at days 60+89,
  so it is not coculture-specific there.)*

## Step 4 — validation per (arm × timepoint) (`temporal_validation.csv`)

Median up-percentile (0 = most down, 1 = most up).

| arm | tp | motility | peptidase | ribosomal | glcB |
|---|---|---|---|---|---|
| coculture | day 18 | 0.489 | 0.522 | 0.792 | 0.778 |
| coculture | day 31 | 0.231 | 0.570 | 0.767 | 0.122 |
| coculture | day 60 | 0.186 | 0.494 | 0.658 | 0.860 |
| coculture | day 89 | 0.189 | 0.533 | 0.781 | 0.699 |
| coculture | days 60+89 | 0.178 | 0.495 | 0.733 | 0.806 |
| axenic | day 18 | 0.173 | 0.431 | 0.746 | 0.270 |
| axenic | day 31 | 0.182 | 0.496 | 0.781 | 0.082 |
| axenic | days 60+89 | 0.111 | 0.463 | 0.731 | 0.202 |

## Step 5 — figure

`fig_temporal_heatmap.png` — 3 panels (coculture effect / axenic effect /
coculture−axenic), modules ordered by mean coculture effect, `*` on cells called
up at q<0.10; axenic day 60 / day 89 columns are blank (no such contrast).

## Anomalies / things to flag (facts, not judgments)

- **Ribosomal (Translation) is NOT neutral in the temporal contrast:** median
  up-percentile 0.66–0.79 in **both** arms at every timepoint. The
  ribosomal-neutrality check was calibrated on the day-11 presence contrast (median
  0.50 there); in the starvation-vs-exponential contrast ribosomal genes rank high
  in both arms. Reported for the main thread; not interpreted.
- **Peptidase does not trend strongly up:** median hovers 0.43–0.57 across arms and
  timepoints (no clear rise as starvation proceeds), unlike the presence-contrast
  expectation.
- **Motility** is low (~0.11–0.23) at day 31 onward in both arms; coculture day 18
  is near-neutral (0.489) while axenic day 18 is already low (0.173).
- **glcB** (`ACZ81_13685`) percentile is inconsistent across timepoints
  (0.08–0.86), no monotone pattern; there is no glycolate uptake module to score.
- **Timepoint structure differs between arms** (axenic lacks standalone day 60 /
  day 89) — handled by restricting `coculture_specific` to the 3 common labels and
  tagging coculture-only rows `no_axenic_match`.
- Data integrity clean: all 8 pulls 3947 genes, signs intact (48–53 % negative), no
  empty pulls, no duplicate handling needed (one row per gene per timepoint).
