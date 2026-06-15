# Step 6 — Evaluate

## Context

Assess the step-5 results against the step-3 predictions, resolve/harvest caveats,
and finalise `paper.md` (Discussion + References). Interpretive vocabulary is
allowed from this step on (Rule 9).

## Ribosome-up anomaly — resolved (documented, not a bug)

Checked the ribosomal set (KEGG ko03010, 54 genes) directly in both HOT1A3
starvation RNA arms (`differential_expression_by_gene`): 48–51 of 54 genes have
positive log2FC, median ~+0.9 to +1.4, with 17–32 significant-up per timepoint, in
**both** arms. So the up-direction is **coordinate and real in the data**, not a
sign-convention artefact — and it is internally consistent with the (correct)
motility-down polarity, which cross-checks against the MED4 snapshot and Weissberg.

`[interpretation]` Most likely a **compositional-normalization effect**: starvation
drives broad down-regulation, so library-size normalization lifts the remaining
genes (incl. ribosomal) into apparent up. A genuine stress-translation maintenance
is also possible. Not run to ground; recorded as an open observation. It does **not**
affect the motility finding, which is a between-arm comparison sharing the same
normalization.

## Assessment against step-3 predictions

| # | Prediction (step 3) | Verdict | Evidence |
|---|---|---|---|
| 1 | Starvation relief, time-resolved (divergence grows) | **Partial** | Motility more suppressed in axenic — sig day 18 (BH 6e-4) & 60+89 (3.5e-9), **not** day 31; trend ns (n=3). Carbon/energy pathways weakly up in coculture. |
| 2 | Partner effect during growth (day-11 snapshot) | **Observed** | Motility down, biosynthesis/transport up in coculture; 3 metabolic pathways survive BH. |
| 3 | Motility readout shifts; direction observed | **Yes** | Down under starvation (both arms, more in axenic); strain/partner-specific in controls. |
| 4 | Carbon, not just stress (resembles fed > stress) | **Not supported** | Motility-down also under darkness; glucose-fed reference too sparse to test resemblance. |
| 5 | Prochlorococcus-specific vs generic (exploratory) | **Reported, mixed** | EZ55 up with Prochlorococcus, down with Synechococcus; direction flips HOT1A3 vs EZ55 — no uniform effect. |

## Net evaluation

The hypothesis holds **partially and only within HOT1A3**: coculture relieves the
starvation-driven motility shutdown, with carbon/energy pathways leaning up. But
motility is **not a carbon-specific reporter** — it is a general stress/dormancy
response (prediction 4 fails), strain/partner-dependent in direction (prediction 5
mixed), RNA-led without protein support, and without a monotonic time-trend
(prediction 1 partial). The C/N confound is structural: the source dataset
(Weissberg et al. 2025) is a nitrogen-recycling study in low-N, no-added-C medium,
so carbon and nitrogen relief are inseparable here.

## Caveats harvested (into paper Discussion)

- C/N confound (structural; source study is N-focused).
- Motility-down is general stress/dormancy, not carbon-specific (darkness control).
- Coculture motility direction strain/partner-specific (no uniform effect).
- RNA–protein discordance (axenic 0.48); axenic protein only to day 31.
- Non-monotonic divergence; trend test underpowered (n=3).
- Ribosome-up: coordinate, likely compositional-normalization; open.
- 4 experiments excluded for sign-corruption (KG data bug).

## Next-steps recorded (not in scope here)

- Dedicated analysis of the EZ55 *Prochlorococcus*-vs-*Synechococcus* motility difference.
- Direct test of carbon transfer: metabolite/exudate data + organic-C transporter expression.
- Resolve the ribosome-up observation (compositional vs biological).

## Decide-gate checklist

- **Outputs produced:** this notebook; finalised `paper.md` (Discussion + References).
- **Results presented:** ribosome resolution, prediction scorecard, net evaluation (shown in chat).
- **QC gate:** ribosome anomaly checked directly (not assumed); predictions scored against frozen step-5 stats; caveats traced to specific results; references resolved via `list_publications` with correct authors/years; 2016 exclusions noted.
- **Analysis complete:** all six steps closed. Remaining work is methodology consolidation (gaps + skill), not analysis.
