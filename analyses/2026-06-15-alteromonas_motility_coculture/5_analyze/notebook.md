# Step 5 — Analyze (redone 2026-06-15)

## Context

Run the step-4 method (`run_contrast`, reused by path) across the HOT1A3 starvation
time-course (coculture vs axenic, RNA and protein) and compose the
difference-of-trajectories test of the carbon-provision hypothesis, then place it
against controls. co-defined with the researcher: RNA and protein computed
separately (low mRNA–protein agreement); figures distinguish coculture/not,
carbon-rich/low, timepoint, treatment; statistical tests added.

## What I did

- `scripts/01_timecourse.py` — froze per-arm enrichment + motility readouts
  (4 arms), then: motility-set paired **Wilcoxon signed-rank** (coculture−axenic
  log2FC) per matched timepoint, **separately for RNA and protein**; **Spearman**
  trend of the divergence over time; **RNA–protein direction agreement**; pathway
  signed-score trajectories. Figs 1–2.
- `scripts/02_controls.py` — motility **direction-only** counts (cross-study, per
  statistical-rigor.md) for EZ55 ±Prochlorococcus/±Synechococcus, MIT1002 darkness,
  MarRef +glucose; HOT1A3 reference rows. Fig 3.

Old-run files (`01_run.py`, old fig1/fig2, old data CSVs) removed — superseded.

## Results

### 5a — HOT1A3 starvation time-course (RNA, the well-powered layer) `[KG]`

Motility (KEGG flagella+chemotaxis) is down under starvation in **both** arms
(flagellar/chemotaxis signed scores negative throughout; e.g. axenic days 60+89:
flagellar −11.0, chemotaxis −9.1). It is suppressed **more in axenic than
coculture** — paired Wilcoxon on per-gene log2FC (coculture−axenic):

| timepoint | median Δ (coc−ax) | BH p | coc down/up | axenic down/up |
|---|--:|--:|--:|--:|
| day 18 | +0.43 | 6.0e-4 | 17 / 2 | 45 / 4 |
| day 31 | −0.10 | 0.76 (ns) | 32 / 4 | 30 / 3 |
| days 60+89 | +0.55 | 3.5e-9 | 40 / 0 | 62 / 3 |

Significant at day 18 and days 60+89, **not** day 31 → the divergence is **not
monotonic**; Spearman trend rho 0.50, p 0.67 (n=3, underpowered). Carbon/energy
pathways lean weakly up in coculture, flat in axenic (RNA): oxidative
phosphorylation coculture +1.3→+2.0, glycolysis +0.5→+0.7, vs ~0 axenic (Fig 2).

**RNA vs protein** (not pooled): direction agreement 0.68 (coculture) / **0.48
(axenic)** — protein does not mirror RNA, especially axenic; the motility signal is
RNA-led, protein limited (axenic protein stops at day 31).

`[interpretation]` Within HOT1A3, the data fit "coculture relieves the
starvation-driven motility shutdown" — fed cells keep motility relatively higher —
but the time-trend is not clean and protein does not corroborate.

### 5b — controls (direction-only, cross-study) `[KG]`

- **Motility-down is a general stress/dormancy response, not carbon-specific.**
  MIT1002 darkness suppresses motility too (diel 9/11 down = 0.82; extended 4/6 =
  0.67); HOT1A3 starvation drives motility down in both arms (coculture 177/183 =
  0.97, axenic 137/147 = 0.93).
- **Coculture motility direction is strain/partner-specific, not uniform.** EZ55
  +Prochlorococcus MIT9312 → motility up (down-frac 0.14–0.22); EZ55 +Synechococcus
  CC9311 → down (0.71–1.0). Across strains with Prochlorococcus the direction flips
  (HOT1A3+MED4 snapshot down 0.875 vs EZ55+MIT9312 up). This is the sign-verified
  version of what the old (corrupted-data) analysis mis-claimed.
- **Glucose-fed reference too sparse** (MarRef proteomics: 1 significant motility
  gene) to define "carbon-fed motility."

### Net `[interpretation]`

Partial, within-study support for carbon provision: HOT1A3 motility is
significantly more suppressed starved-alone than fed-in-coculture (5a), and
carbon/energy pathways lean weakly up in coculture. **But** motility is not a clean
Prochlorococcus-carbon-specific readout — it is a general stress/dormancy response,
strain/partner-dependent in direction, RNA-led with discordant protein, and without
a monotonic time-trend.

## Statistical tests used

Paired Wilcoxon signed-rank (within-platform, within-study log2FC, motility set,
per timepoint; BH across timepoints); Spearman trend (flagged low-power); RNA–protein
direction-agreement fraction; pathway-level Fisher+BH from `pathway_enrichment`.
Cross-study controls are direction-only (no magnitude / p comparison).

## Figures

- `figures/fig1_motility_timecourse.png` — motility log2FC divergence + significant-gene counts over time (RNA | protein, coculture vs axenic).
- `figures/fig2_pathways_timecourse.png` — carbon + motility pathway signed scores over time (RNA | protein, coculture vs axenic).
- `figures/fig3_motility_controls.png` — motility down-fraction across conditions (carbon level × coculture × partner).

## Decisions

- **2026-06-15 — RNA and protein analysed separately** (direction agreement 0.48–0.68; not pooled).
- **2026-06-15 — controls are direction-only** (cross-study); ORA/magnitude confined within HOT1A3 (same study+platform).
- **2026-06-15 — carbon-provision recorded as partially supported, motility not carbon-specific** — controls (darkness, partner, cross-strain) require this hedge.

## Caveats / open items carried to step 6

- C-vs-N confound (starvation is N-limitation; C co-limits in axenic) — unresolved.
- No monotonic time-trend (n=3 matched RNA timepoints; day 31 dips); Spearman ns.
- RNA–protein discordance, axenic 0.48; axenic protein only to day 31.
- Motility-down is general stress/dormancy (darkness control) — not carbon-specific.
- Coculture motility direction is strain/partner-specific (HOT1A3 vs EZ55; Pro vs Syn).
- **Anomaly (open):** ribosome genes read up in starvation-vs-exponential in both arms — unchecked (direction-convention vs real).
- **Next-step:** the EZ55 Prochlorococcus-vs-Synechococcus motility difference is itself a partner-specific signal worth a dedicated look.

## Decide-gate checklist

- **Outputs produced:** `scripts/01_timecourse.py`, `scripts/02_controls.py`; 5a/5b data CSVs + logs; Figs 1–3. Old-run files removed.
- **Results presented:** 5a (divergence + stats) and 5b (controls) shown to researcher in chat.
- **QC gate:** stats chosen per statistical-rigor.md (within-study Wilcoxon, cross-study direction-only, RNA/protein separate); motility polarity cross-checked vs MED4 snapshot + Weissberg; non-monotonic trend and protein discordance reported honestly; ribosome anomaly flagged.
- **Advance rationale:** the analysis is complete and frozen with figures + tests; step 6 evaluates against the step-3 predictions, harvests caveats, finalises the paper.
