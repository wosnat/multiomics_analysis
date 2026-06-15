# Step 4 — Method (use the package's enrichment ORA)

## Context

The step-3 readout (direction + over-representation of motility genes vs the
genome background) is exactly over-representation analysis (ORA). The
`multiomics_explorer` package already ships this — `pathway_enrichment` runs the
full DE→ORA pipeline (one-sided Fisher per pathway, per-experiment `table_scope`
background, up/down direction split, Benjamini-Hochberg correction). **No custom
method is needed.** (An initial hand-rolled version was scrapped — see
`gaps_and_friction.md`; it even got the background wrong.)

## The method

For each coculture-vs-alone experiment:
- **HOT1A3** (all genes reported): `pathway_enrichment(organism, [experiment],
  ontology="kegg", level=2, direction="both")` — tests every KEGG pathway, so our
  three (flagellar assembly ko02040, bacterial chemotaxis ko02030, ribosome
  ko03010) are judged in the context of all pathways with proper background + BH.
  Repeat with `ontology="cog_category"` for the broad COG-N sensitivity check.
- **EZ55** (significant genes only): ORA is invalid (background ≈ foreground), so
  EZ55 gets **direction-only** counts from `differential_expression_by_gene` —
  handled in step 5.

## Worked example — verifies the method (anchor: HOT1A3 coculture-with-MED4 vs axenic, Weissberg 2025)

`scripts/01_worked_example.py`, KEGG level 2, direction both. Single timepoint
("day 11"), so clusters are `…|day 11|up` and `…|day 11|down`; 290 (cluster ×
pathway) tests.

| pathway | cluster | genes (count) | fold | raw p | BH p_adjust |
|---|---|--:|--:|--:|--:|
| Bacterial chemotaxis | down | 5 / 50 | 2.42 | 0.054 | 0.97 |
| Bacterial chemotaxis | up | 1 / 50 | 0.71 | 0.76 | 1.00 |
| Flagellar assembly | down | 2 / 49 | 0.99 | 0.61 | 1.00 |
| Flagellar assembly | up | 0 / 49 | 0 | 1.00 | 1.00 |
| Ribosome (baseline) | up/down | 0 | 0 | 1.00 | 1.00 |

**Reads as expected for a verification:** the ribosome baseline is flat (0 genes
either direction ✓); the tool returns per-direction enrichment with sensible
Fisher/fold/BH numbers. **Early substantive hint:** chemotaxis leans *down* in
coculture (5 genes, ~2.4× fold, raw p 0.054) but does **not** survive correction;
the significant pathways on the anchor are metabolic (purine, 2-oxocarboxylic
acid, propanoate — up), not motility. Whether the weak chemotaxis-down signal is
consistent across the other experiments is the step-5 question.

## Decisions

- **2026-06-15 — method = package `pathway_enrichment` (KEGG + COG-N), not custom
  code.** The package implements ORA with the correct per-experiment background;
  reusing it avoids a buggy reimplementation. EZ55 = direction-only (significant
  table breaks ORA).

## Decide-gate checklist

- **Outputs produced:** `scripts/01_worked_example.py` (verification; reinvented
  module deleted).
- **Results presented:** worked-example enrichment table on the anchor (above).
- **QC gate:** ribosome baseline flat (0/0) as expected; method returns
  per-direction Fisher results with BH; early read recorded (chemotaxis weakly
  down, not significant).
- **Advance rationale:** method verified on the anchor; step 5 runs it across all
  HOT1A3 experiments (+ COG-N sensitivity) and does EZ55 direction counts +
  partner-specificity.
