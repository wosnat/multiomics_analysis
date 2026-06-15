# Step 5 — Analyze

## Context

Ran the locked method (package `pathway_enrichment` for HOT1A3; direction-only
counts for EZ55) across all coculture-vs-alone experiments. Step 6 evaluates
against the predictions.

## What I did

`scripts/01_run.py` (imports the package; reads frozen step-2 CSVs):
- HOT1A3 (3 experiments): `pathway_enrichment` KEGG level 2 + COG category N,
  direction both → flagellar assembly, bacterial chemotaxis, ribosome baseline,
  COG-N rows. → `data/hot1a3_enrichment.csv`, `figures/fig1_hot1a3_motility.png`.
- EZ55 (6 experiments): `differential_expression_by_gene` → up/down counts of the
  KEGG motility set, Prochlorococcus vs Synechococcus partner. →
  `data/ez55_motility_direction.csv`, `figures/fig2_ez55_partner.png`.

## Results

### HOT1A3 — motility direction depends on partner/study `[KG]`

Net significant motility genes in coculture (up − down); raw p / BH p_adjust for
the dominant direction:

| experiment (partner, study) | chemotaxis | flagellar | COG-N motility | ribosome | best raw p | survives BH? |
|---|--:|--:|--:|--:|--:|---|
| MED4 (Weissberg 2025), day 11 | **−4** (5↓/1↑) | −2 | −8 | 0 | 0.054 (chemotaxis ↓) | no (p_adj 0.97) |
| MIT9313 hi-inoc (ismej.2016), 20h | **+6** (6↑) | **+8** (8↑) | +12 | 0 | 0.016 (flagellar ↑) | no (p_adj 0.78) |
| MIT9313 (ismej.2016), 20h | +1 | +1 | +2 | 0 | 0.35 | no |

The direction **flips**: motility leans **down** with the MED4 partner (Weissberg)
and **up** with the MIT9313 partner (a different study). Fold-enrichments are
>2 for the leading sets, but **nothing survives multiple-testing correction** on
these small significant-gene sets. The **ribosome baseline is flat (0 genes) in
every experiment** — motility moves where housekeeping does not (fig1).

### EZ55 — motility leans up with Prochlorococcus, down/flat with Synechococcus `[KG]`

Significant motility genes (KEGG set, 102 genes), direction-only:

| partner | genus | up | down |
|---|---|--:|--:|
| MIT9312, 400 ppm | Prochlorococcus | 7 | 2 |
| MIT9312, 800 ppm | Prochlorococcus | 6 | 1 |
| CC9311, 400 ppm | Synechococcus | 2 | 5 |
| CC9311, 800 ppm | Synechococcus | 0 | 2 |
| WH8102, 400 ppm | Synechococcus | 0 | 0 |
| WH8102, 800 ppm | Synechococcus | 0 | 0 |

With Prochlorococcus, motility leans **up** (13 up / 3 down across the two CO₂
levels); with Synechococcus, **down or flat** (2 up / 7 down) — a partner-specific
contrast (fig2). (Significant-only table → direction is interpretable but no
over-representation test.)

## Surprises

- The headline "is it up or down" has **no single answer**: direction is
  partner/condition-dependent. The one experiment that motivated the analysis
  (Weissberg, MED4) is the *down* case, while the MIT9313 and EZ55-Prochlorococcus
  cases lean *up*.
- EZ55's partner-specificity (up with Prochlorococcus, down with Synechococcus) is
  the most coherent signal, but rests on small significant-gene counts.
- Statistical support is weak throughout — no BH-significant motility enrichment.
  The signal is directional trend, not a hard result.

## Decide-gate checklist

- **Outputs produced:** `scripts/01_run.py`; `data/hot1a3_enrichment.csv` (16),
  `data/ez55_motility_direction.csv` (6), log; `figures/fig1`, `fig2`.
- **Results presented:** HOT1A3 enrichment table, EZ55 direction table, 2 figures.
- **QC gate:** ribosome baseline flat (0/0) in all HOT1A3 experiments → motility
  signal is specific, not a whole-cell shift; EZ55 handled direction-only as
  framed (no ORA on significant-only tables); experiments kept distinct (fixed an
  initial merge of the two MIT9313 experiments).
- **Advance rationale:** all numbers needed to judge the predictions are in; step 6
  adjudicates and harvests caveats.
