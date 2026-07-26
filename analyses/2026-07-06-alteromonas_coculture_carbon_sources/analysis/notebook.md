# Analysis milestone — notebook

Owner: main thread. Subagent authored `scripts/`, `data/`; main thread verified the
real files (DE staging spot-checked against the KG) and wrote every interpretive line.

## Context

Run the committed scorer (`methods/scripts/scoring.py`) on the real DE data, per
(experiment × timepoint), producing the module catalog, the candidate-vs-control
contrast, validation checks, and the genome-wide enrichment guard. Sequencing
(researcher-agreed): **HOT1A3 day-11 presence contrast first**, then EZ55, then the
temporal read; breakdown-map selection deferred. This entry covers the **HOT1A3
day-11 coculture-vs-axenic** contrast (primary, `all_detected_genes`, fully rankable).

## What I did

- `scripts/01_stage_de.py` → `data/de_hot1a3_day11.csv` (3947 genes).
- `scripts/02_score_modules.py` / `04_score_modules_v2.py` (imports the committed
  scorer) → `data/module_catalog_hot1a3_day11_v2.csv`, `data/system_scores_*.csv`,
  `data/qc_control_contrast.csv`.
- `scripts/03_enrichment_guard.py` → `data/qc_enrichment_guard.csv`.
- **Analysis-layer refinements** (data-driven, applied in the script; methods
  `parts_list_v2.csv` untouched): dropped TonB from scoring (control = control-ABC
  only; iron-TonB up-shift kept as a reported finding); relabelled `ACZ81_18130`
  "unresolved" → **carbohydrate (MFS)** (KG gene_category = Carbohydrate metabolism);
  resolved `ACZ81_06075` SLC13 → **di-/tricarboxylate (citrate, CitMHS/COG0471,
  organic acid)** — kept candidate; module-grouping guard confirmed (broad-class
  merges legitimate, no pseudo-label merge).
- **Main-thread QC (verified against the KG directly):** DE signs/counts match
  (`differential_expression_by_gene` on 4 anchors — 18130 l2fc 3.53, benE 2.89,
  SLC13 2.32, glcB −1.71 all match the staged CSV); percentiles track log2fc.

## Results

**DE QC:** 3947 genes; 111 up / 163 down; **54.1% negative log2fc** (sign preserved);
single timepoint "day 11".

**Validation** (up-percentile medians): motility/flagellar (n=123) **0.184** → down
(expected); ribosomal/Translation (n=198) **0.504** → neutral (expected); `glcB`
glycolate **0.028** (down); `hcaT` 0.356.

**Genome-wide enrichment guard** (KEGG L1 + EC): **up** — Carbohydrate metabolism
(padj 0.021, fold 2.49), Nucleotide metabolism (padj 0.021, fold 3.68); **down** —
Infectious disease/Immune (motility/secretion), peroxidase (oxidative-stress relief).

**Candidate catalog** (46 modules; 2 pass q<0.10, both single-gene):

| tier | q | pct | substrate | note |
|---|---|---|---|---|
| single | **0.060** | 0.999 | carbohydrate (MFS) `ACZ81_18130` l2fc 3.5 | genuine top-up carb transporter |
| single | **0.090** | 0.997 | benzoate `benE` l2fc 2.9 | the **aromatic expected-negative** |
| single | 0.101 | 0.994 | di-/tricarboxylate citrate `06075` l2fc 2.3 | organic acid, just above FDR |
| single | 0.35–0.65 | 0.9+ | L-fucose, carb-porin, nucleoside, Na-solute | plausible carbon, not passing FDR |
| multi | 0.45 | 0.802 | dipeptide (sap/dpp cassette) | |
| multi | 0.91–0.94 | 0.21–0.27 | APC / peptide-nickel cassettes | **flat/down** |

**Size-matched control contrast** (system-level median up-percentile):

| ref_class | single-gene | multi-subunit |
|---|---|---|
| candidate | 0.616 (n=54) | 0.265 (n=3) |
| control-ABC | 0.655 (n=16) | 0.481 (n=6) |

→ **Candidate organic-C systems are NOT elevated over the inorganic control-ABC set**
on a size-matched basis (candidate slightly *below* in both tiers).

## Surprises

1. **The bulk "organic-C > inorganic" contrast is null** (candidate ≤ control-ABC,
   size-matched). The proposal predicted this and pre-committed that the carbon claim
   rests on **specificity/coherence**, not the bulk contrast — so this is expected,
   but it means the bulk contrast carries no weight.
2. **Iron acquisition is induced in coculture** — iron-TonB (26 systems) median
   percentile **0.757**, the top-moving class. `[interpretation]` Real coculture
   biology (iron competition); makes iron **interaction-coupled**, not a clean
   negative (dropped from controls, reported as a finding). A result in its own right.
3. **A thin, specific signal, not a bulk one:** a few individual carbon transporters
   are among the most-up genes — carbohydrate MFS (`18130`, l2fc 3.5), citrate/
   dicarboxylate (`06075`, l2fc 2.3), plus a cluster of sugars/nucleosides at pct
   0.9+ — but only 2 pass q<0.10 and one of those is the aromatic expected-negative.
4. **`benE` benzoate (the aromatic expected-negative) is a top hit** (l2fc 2.9,
   q=0.09) — a falsification concern for the specificity story; benzoate/aromatic-acid
   uptake up in coculture is a data fact to weigh. `[interpretation]` One gene; needs
   reproducibility before it means anything.
5. **The best-annotated multi-subunit peptide systems are flat/down** (0.21–0.27) —
   peptide uptake is not up in this contrast, despite peptides being the cleanest
   multi-subunit modules.

**Reading (pre-evaluation, held lightly):** the HOT1A3 day-11 contrast alone gives a
thin, specific set of up carbon transporters against a null bulk contrast and a
strong iron confound — inconclusive by itself. The proposal's falsifiable core is
**reproducibility across independent experiments**, so the weight falls on whether
these specific hits (carbohydrate MFS, citrate, sugars) recur in EZ55 and the temporal
read. No module is claimed as a carbon source on this contrast.

## EZ55 400/800 presence contrasts (cross-strain test)

`significant_only` (400: 419 genes, 308/111; 800: 188, 104/84) — presence-weighted,
scored within the significant set. Same refinements (TonB dropped; carbohydrate-MFS
`EZ55_03747` relabelled; SLC13/CitMHS `EZ55_01261` = citrate but **not significant** in
either arm). Files `data/module_catalog_ez55_{400,800}.csv`, `qc_control_contrast_ez55.csv`,
`qc_validation_ez55.csv`. Main-thread-verified: catalogs + benE absence below.

**Candidate modules passing q<0.10 (all single-gene tier):**
- **400 ppm:** L-fucose:H⁺ (q=0.085). [then solute:Na⁺ 0.22, carb-porin 0.29, BCCT 0.34, carb-MFS 0.55]
- **800 ppm:** cation/acetate (SSS, organic acid; q=0.046). [then BCCT 0.78, maltose 0.78]

**Control contrast — degenerate for EZ55:** `significant_only` leaves ~0 single-gene
control-ABC systems scored → no usable size-matched candidate-vs-control comparison. Flagged.

**Validation:** 400 motility 0.137 → **down** (✓, testable); 800 motility 0.681 → **not
down** (✗ — the 800 arm's validation fails, weakening it). glcB/benE not in either
significant set.

## Cross-strain synthesis (HOT1A3 + EZ55) — verified

The two EZ55 arms count as **one** strain-partner support (pCO₂ agreement is internal);
HOT1A3 is the other. Reading the matrix by substrate:

- **Sugars / carbohydrate — reproduces at CLASS level.** HOT1A3: carbohydrate-MFS
  (`18130`, q<0.10) + fucose + carb-porin. EZ55: **L-fucose q<0.10 (400)**, carb-porin,
  carb-MFS, maltose. A sugar/carbohydrate uptake signal passes q<0.10 in *both* strains,
  though the **specific carrier differs** (MFS-carb vs fucose).
- **Organic acids — partial, class level.** HOT1A3: di-/tricarboxylate citrate (`06075`,
  q=0.101, just above). EZ55: **acetate (SSS) q<0.10 (800)**; the EZ55 citrate gene isn't
  significant. Different specific acids; the organic-acid/SSS class shows in both.
- **Osmolytes (BCCT)** — near-threshold in both EZ55 arms; not a HOT1A3 top hit.
- **Benzoate / aromatic — does NOT reproduce** `[verified]`. `benE` (`EZ55_00725`) is
  absent from both EZ55 significant sets. The HOT1A3 benzoate hit is strain-specific; the
  aromatic expected-negative behaves as expected (does not recur) — the method is not
  simply flagging noise.
- **Peptides** — not supported in either strain (flat in HOT1A3; not significant in EZ55).

**No single specific compound passes q<0.10 in both strains** — the reproducible signal
is a **chemically-coherent CLASS** (sugars + organic acids, recognisable marine DOM),
not a named compound. `[interpretation]` This is exactly the annotation-limited,
graded-catalog outcome the proposal predicted; the decisive test is wet-lab growth.

**Caveats carried:** EZ55 is thin/presence-weighted (few modules scored, control
contrast degenerate); the 800-arm motility validation fails; iron acquisition is up in
both strains (interaction-coupled confound); the bulk organic-C-vs-inorganic contrast is
null (HOT1A3) / uninformative (EZ55).

## Temporal read (HOT1A3 starvation trajectories, corroboration-only)

Count-per-trajectory (module up = q<0.10), each arm vs its own exponential baseline.
Files `data/temporal_module_scores.csv`, `data/qc_temporal_counts.csv`. Main-thread-verified.

| RNA timepoint | coculture-up | axenic-up | coculture-specific |
|---|---|---|---|
| day 18 | 0 | 0 | 0 |
| day 31 | 2 | 0 | **2 — L-lactate; peptide/nickel** |
| days 60+89 | 1 | 6 | 0 (axenic ramps more) |

- **Coculture-specific ramp at day 31:** **L-lactate** (organic acid; coculture q=0.037
  vs axenic ns; sustained coculture-specific through day 60, q=0.046) and **peptide/nickel**
  (coculture q=0.037 vs axenic ns). Verified.
- **Presence hits read flat/down in the coculture trajectory** (expected for constitutive
  presence-up modules, per the proposal): carbohydrate-MFS high early (0.94) → drops late;
  di-/tricarboxylate citrate **down** throughout (0.08–0.25). Non-contradictory.
- **Late starvation (60+89): axenic ramps organic modules *more* than coculture** — the
  difference-of-trajectories reverses; noisy, not coculture-exclusive.
- **Proteomics uninformative** — 24/46 modules detectable, **0 up** in any arm/timepoint;
  axenic proteomics has effectively one informative timepoint (day 31).

**Temporal corroboration (weak, corroboration-only, weighted below presence):** the
**organic-acid class** gets independent support (L-lactate coculture-specific, distinct
from the presence citrate/acetate); **peptides** get a marginal one-timepoint signal
(day 31). Sugars read flat (constitutive, non-contradictory). Thin — a single RNA
timepoint (day 31), and the late axenic ramp shows the trajectories are noisy.

## Breakdown-map flags (catabolism corroboration; decision 13)

`data/breakdown_flags.csv`. 43 distinct candidate substrates: **8 have a genuine KEGG
degradation map**, **35 are not-determinable** (feed central metabolism — all sugars, all
organic acids, nucleosides, peptides, betaine, glycerol; the expected majority per the
proposal). **On HOT1A3 (primary), every degradation map reads `not-up`** — including
benzoate `ko00362` (0/10 up, padj 1.0) and aromatic `ko01220` (padj 0.39), fatty-acid
`ko00071` (0/23, padj 1.0), BCAA `ko00280` (3/32, padj 0.30, ns). Verified.
- **So benzoate gets NO catabolism corroboration on HOT1A3** — the benE transporter is up
  but its degradation pathway is not; combined with non-reproduction in EZ55, the aromatic
  signal is incoherent across lines of evidence.
- **Caveat — EZ55-800 (secondary, genome background on a `significant_only` table):**
  benzoate `ko00362` (padj 0.007) and aromatic `ko01220` (padj 9.5e-8) read `up` — but
  benE (the transporter) is *not* in the EZ55 significant set, so transporter and catabolism
  still don't align. Recorded as a caveated secondary observation, not corroboration.

## Cross-experiment matrix (by candidate class; "up" = q<0.10)

| class | HOT1A3 d11 | EZ55 400 | EZ55 800 | temporal (cocult-specific) | breakdown |
|---|---|---|---|---|---|
| **sugars / carbohydrate** | carb-MFS **UP** | L-fucose **UP**, porin | maltose (ns) | flat (constitutive) | not-determinable |
| **organic acids** | citrate (q=0.101) | — | acetate **UP** | **L-lactate UP (d31)** | not-determinable |
| osmolytes (BCCT) | — | BCCT (ns) | BCCT (ns) | — | not-determinable |
| peptides | flat | — | — | peptide/nickel **UP (d31)** | not-determinable |
| benzoate / aromatic | benE **UP** | absent | absent | flat | not-up (A3); up-800 (caveat) |
| iron (confound) | 0.757 (up) | thin | thin | — | — |

**Composition of the "reproducible" calls (the two classes are NOT symmetric — analysis
critic, 2026-07-26):**
- **Sugars/carbohydrate — the stronger signal:** two **presence** contrasts, two strains
  (HOT1A3 carb-MFS q=0.060; EZ55-400 L-fucose q=0.085).
- **Organic acids — weaker:** **one presence** arm (EZ55-800 acetate q=0.046) **plus one
  temporal** line (L-lactate d31, corroboration-only, weighted below presence); the HOT1A3
  **presence** citrate **just-misses** (q=0.101).
- **EZ55 q<0.10 is a weaker bar than HOT1A3's.** EZ55's BH family is only **3–5 modules**
  (`significant_only`), so its permutation p's (fucose 0.017, acetate 0.0155) clear q<0.10
  there but would give q≈0.7 in HOT1A3's 46-module family. The **comparable** cross-
  experiment quantity is the within-experiment **permutation p**, not the family-size-
  dependent q. So "passes in both strains" is real but not parity.

## Compound-class aggregation (exploration, researcher-requested 2026-07-26)

`scripts/09_compound_class_picture.py`. Classifying every scored transporter by compound
class and taking the class median up-percentile is **family-size-independent** — a more
robust read than the per-module q's (which the critic flagged as small-family-dependent
for EZ55).

**HOT1A3 day-11, class median up-percentile** (inorganic control-ABC = 0.59 reference)
— **`figures/figA_compound_class_landscape.svg`**:

| class | n | median | n up (≥0.9) |
|---|---:|---:|---:|
| nucleosides/bases | 7 | **0.70** | 1 |
| sugars/carbohydrate | 9 | **0.69** | 3 |
| aromatics | 2 | 0.68 | 1 |
| osmolytes | 4 | 0.67 | 0 |
| organic acids | 10 | 0.67 | 1 |
| *inorganic (control ref)* | 12 | *0.59* | 0 |
| peptides | 4 | 0.50 | 0 |
| **amino acids** | 15 | **0.38** | 0 |
| fatty acids / glycerol | 1/1 | 0.22 / 0.20 | 0 |

- **Sugars + nucleosides most elevated** (~0.70 vs inorganic 0.59) — and **independently
  corroborated** by the genome-wide enrichment guard (Carbohydrate + Nucleotide metabolism,
  the two up pathways). Two independent angles converge.
- **Amino acids conspicuously NOT up** (0.38, below the inorganic reference) despite 15
  transporters — a clean class-level negative; coculture does not broadly induce amino-acid
  uptake. Peptides neutral (0.50).
- Shifts are **modest** (~0.1 percentile over the reference) — a real-but-modest class pattern.

**Cross-experiment candidate class medians** (**`figures/figB_cross_experiment_classes.svg`**):
sugars HOT1A3 0.77 / EZ55-400 **0.83** / EZ55-800 0.22 (reproduces in 400); nucleosides
HOT1A3 0.79 (not in EZ55 significant sets → untested); osmolytes HOT1A3 0.59 / EZ55-400 0.73;
organic acids HOT1A3 0.67 / EZ55-800 0.99 **(n=1 module — thin)**. The temporal L-lactate
coculture-vs-axenic ramp is **`figures/figC_temporal_lactate.svg`** (coculture early at day 31;
axenic catches up only at late starvation).

## Exploration figures & further caveats (2026-07-26)

Figures `figures/figD…figG.svg`, `figE2` (`scripts/09–13`; colorblind-safe, vector):
- **Fig D — transporter repertoire by class.** Amino acids are the *largest* carbon
  repertoire (14–15 systems; the two figure scripts' keyword classifiers differ by one
  borderline system) yet the class is not induced; sugars/organic acids are mid-sized
  and are the up classes. Almost all single-gene (peptides the exception). The response is
  selective, not proportional to repertoire.
- **Fig E — candidate module × experiment heatmap** (presence | RNA temporal | proteome;
  class-ordered, `*` = q<0.10). Structured pattern: sugars/nucleosides red, **BCAA blue
  (down) everywhere**, L-lactate `*` in coculture temporal.
- **Fig E2 — control modules, same scale.** **Inorganic control-ABC is neutral/mixed at
  HOT1A3 (no coordinated up)** — so the candidate structure is specific, not a global
  up-shift. **Iron (control-TonB/ambiguous-TonB) is predominantly up** (a handful down —
  4/11 at HOT1A3 d11 — but clearly the dominant confound). **Nitrate/nitrite** passes q<0.10
  in the temporal → **nitrogen interaction-coupled**
  (as the proposal flagged N/P). Late-axenic reddens controls too → that ramp is nonspecific.
- **Fig F — RNA-seq vs proteomics** (temporal coculture). **Proteomics is underpowered**:
  0 modules reach q<0.10 in any arm, and the protein median (0.82) is if anything *higher*
  than RNA (0.76) — so the transcript signal is **neither confirmed nor refuted** at the
  protein level (absence of evidence, not discordance). A few modules do show
  RNA-up/protein-flat (**cation/acetate** RNA 0.99 / protein 0.03; purine nucleoside
  0.97 / 0.25) but it is not a general pattern — e.g. **L-lactate protein 0.89 agrees with
  its RNA**. *(Corrected per the analysis delta-critic: an earlier draft mis-cited acetate's
  0.03 as L-lactate's.)*
- **Fig H — analysis funnel** (`figH_analysis_funnel.svg`). Summary: 4028 genes → 684
  transporter genes → 57 organic-C candidate systems → 46 scored → 2 pass q<0.10 → the
  reproducible class-level signal (sugars, + organic acids) → wet-lab shortlist.
- **Fig G — EZ55 vs HOT1A3** (only n=6 substrates scored in both — EZ55 sparse). Sugars
  reproduce **at class level via 2 of 4**: L-fucose (0.97/0.99) and carb-porin (0.95/0.83)
  hold, but **carbohydrate-MFS — the top HOT1A3 hit — collapses to 0.44 in EZ55, and maltose
  0.69→0.22 do not reproduce**. The **single** shared organic acid (acetate, HOT1A3 0.21 /
  EZ55 0.99) is anti-correlated — **consistent with, not establishing** (n=1), strain-specific
  use. So the reproducible cross-strain claim is genuinely *class-level and partial*, carried
  by fucose/porin.

## Synthesis (analysis milestone)

`[interpretation]` The most robust read is the **compound-class** one (family-size-
independent). The clearest coculture-induced uptake is **sugars/carbohydrates** and
**nucleosides/nucleobases** — the two most-elevated transporter classes, **converging with**
the genome-wide enrichment of Carbohydrate + Nucleotide metabolism. **Sugars reproduce**
across strains (HOT1A3 + EZ55-400 presence); nucleosides is a HOT1A3 signal (untested in
EZ55). **Organic acids** are a weaker candidate (one EZ55 presence arm + temporal lactate;
HOT1A3 presence just-misses). **Amino acids are conspicuously not up** (class median 0.38) —
an informative negative; **peptides neutral**. **No single specific compound** clears the
bar in ≥2 experiments — carriers differ (MFS-carb vs fucose; citrate vs acetate vs lactate)
— so the resolution is class-level and annotation-limited. Breakdown corroboration is
**not-determinable** for the supported classes (central metabolism), as the proposal
anticipated.

**The aromatic check is muddied, not a clean pass or fail.** benE (aromatic transporter) is
the **#2 hit in the primary, fully-rankable experiment** (q=0.090) — a partial hit of the
expected-negative in the strongest dataset — but it does **not reproduce as a transporter**
in EZ55; meanwhile **aromatic *degradation* is up in EZ55-800** (`ko00362` padj 0.007,
`ko01220` padj 9.5e-8; benA/B/C — though these are **down** in EZ55-400). So aromatic
metabolism appears in both strains but **never as a coherent transporter+catabolism unit**
in the same strain/condition → aromatics do **not** qualify as a supported carbon source,
but the expected-negative is a *partial complication*, not cleanly falsified.

**Confounds/limits carried:** iron acquisition up (interaction-coupled, not a clean
negative — Fig E2); nitrogen (nitrate) also interaction-coupled; bulk organic-C-vs-inorganic
contrast null; EZ55 presence-weighted/thin with a 3–5-module FDR family, only 6 substrates
shared with HOT1A3, and a **failed 800-arm motility validation**; the two EZ55 pCO₂ arms
**disagree on aromatic-catabolism direction** (down 400 / up 800); **proteomics is
underpowered — it neither confirms nor refutes the transcript signal** (Fig F, 0 modules
q<0.10; protein median ≥ RNA); **even sugars reproduce only 2 of 4 shared carriers and the
one shared organic acid is anti-correlated** (Fig G, n=1) — cross-strain reproducibility is
partial and class-level; peptides marginal. The
control comparison (Fig E2) does show the candidate structure (sugars up / amino-acids down)
is **specific** — inorganic controls stay neutral rather than a global up-shift.

This is the graded candidate catalog the proposal predicted — a prioritized shortlist led
by **sugars/carbohydrates**, with **organic acids** a weaker second, for the decisive
wet-lab growth test; not named carbon sources, and reproducibility caveated by the small
EZ55 family.

## Decide-gate checklist (analysis milestone)

**Outputs** (`analysis/scripts/`, `analysis/data/`): `01–08_*.py`; DE staging
(`de_hot1a3_day11`, `de_ez55_{400,800}`, `de_temporal_*`); `module_catalog_*` (HOT1A3 v2 +
EZ55 400/800); `system_scores_*`; `qc_control_contrast*`; `qc_validation*`;
`temporal_module_scores` + `qc_temporal_counts`; `breakdown_flags`; `qc_enrichment_guard`;
`09_compound_class_picture.py`, `10_figures.py` → `figures/fig{A,B,C}_*.svg` (colorblind-safe
Okabe-Ito, vector).
**Results presented:** all tables inline above (per-experiment catalogs, control contrast,
temporal counts, breakdown flags, cross-experiment matrix) — real numbers.
**QC gate:** DE signs/counts verified vs KG (54% neg, 111/163; EZ55 counts); percentiles
track log2fc (KG spot-check on 4 anchors); validation (motility down A3/EZ55-400, ribosomal
neutral; 800-motility fails — flagged); scorer math re-derived; control comparison corrected
to system-level after catching a module-grouping artifact.
**Decisions this milestone (2026-07-26):** dropped TonB (iron interaction-coupled);
relabelled 18130→carbohydrate, resolved 06075→citrate/dicarboxylate; report control
contrast system-level + tiered single/multi; temporal = count-per-trajectory; breakdown =
decision-13 (degradation maps only).
**Advance rationale:** all in-scope experiments scored, cross-experiment matrix assembled,
evidence verified against the KG; the conclusion (two reproducible class-level signals,
graded catalog) is stable across presence + temporal + breakdown. Ready for the analysis
critic, then researcher decide gate.

**Critical review (analysis milestone, data-integrity + interpretation — the heavy gate):**
`critical_review.md`. **No Blockers; data-integrity verified clean** (every number
reconciled against the files + KG). 3 interpretation Concerns + 1 Note — all about the
synthesis over-flattening a thin, asymmetric result — **all fixed by re-wording** (sugars
> organic acids; EZ55 small-family q caveat; aromatic muddied not falsified; pCO₂ arms
disagree on aromatics). The researcher-requested **compound-class aggregation**
(`09_compound_class_picture.py`) is the family-size-independent lead: sugars + nucleosides
foremost (enrichment-corroborated), amino-acids not up.

**Ready for the researcher decide gate.** paper.md Results written.
