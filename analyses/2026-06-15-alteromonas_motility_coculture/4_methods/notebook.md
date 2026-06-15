# Step 4 — Method (redone 2026-06-15)

## Context

The step-3 readout — per-pathway over-representation, direction-split, plus a
motility gene-level deep-dive — is exactly what the package's `pathway_enrichment`
does (one-sided Fisher per pathway, per-cluster `table_scope` background, up/down
split, Benjamini-Hochberg). **No custom statistics** (an early hand-rolled ORA was
scrapped — see `gaps_and_friction.md`). This step is a thin reusable driver around
`pathway_enrichment` + `differential_expression_by_gene` that *freezes* outputs, so
step 5 can reuse it across every usable contrast.

co-defined with the researcher: use `pathway_enrichment` directly (not a wrapper of
its primitives); two granularities; motility gene-level readout as a first-class
output; build on the MED4 snapshot, extend to the time-courses in step 5.

## The method

`scripts/01_method.py` — `run_contrast(label, organism, experiment_ids, strain)`:
1. **KEGG level 2** enrichment (`direction="both"`) — fine, interpretable pathways
   (motility ko02040/ko02030, glycolysis, TCA, carbon metabolism).
2. **COG category level 0** enrichment — coarse functional overview.
3. **Motility gene-level readout** — `differential_expression_by_gene` on the KEGG
   flagella+chemotaxis locus tags (per-gene log2FC, padj, status).

Freezes three CSVs per contrast. `signed_score` (= sign·−log10 padj) carries
direction for later visualisation.

### Ontology + level chosen via `ontology_landscape` (not guessed) `[KG]`

Scouted HOT1A3, weighted by the MED4 experiment. Motility lives at **KEGG level 2**
(pathways) and **COG level 0** (category N). Genome coverage:

| ontology / level | genome coverage | role |
|---|--:|---|
| KEGG L2 (pathways) | **~0.31** | fine, interpretable — the main run (coverage caveat below) |
| COG category L0 | **~0.69** | coarse functional companion |
| (pfam L0 0.65, GO-MF L3 0.54) | — | higher coverage but less directly interpretable for a carbon signature |

**Coverage caveat:** KEGG annotates only ~⅓ of HOT1A3's genome, so KEGG enrichment
reflects that annotated third. COG L0 (~0.69) is the higher-powered coarse check.

## Driving example — HOT1A3 coculture-with-MED4 vs axenic (day-11, exponential)

This is the **partner-during-growth** read (both cultures growing), not the
carbon-starvation story — used here to validate the method mechanics. Single
timepoint → clusters `…|day 11|up` and `…|day 11|down`.

**Numbers first** `[KG]` (`data/med4_snapshot_*`):
- **KEGG L2:** 290 tests, **3** significant (p_adjust<0.05), all *up* in coculture:
  purine metabolism (padj 0.005), 2-oxocarboxylic-acid metabolism (0.006),
  propanoate metabolism (0.010). Trending up (ns): carbon metabolism, TCA,
  amino-acid biosynthesis. Trending down (ns): glycolysis, Calvin-cycle carbon
  fixation, **bacterial chemotaxis** (ko02030: 5 genes, 2.4×, p 0.054, padj 0.97).
- **COG L0:** 36 tests, **1** significant: post-translational modification /
  chaperones *down* (padj 0.029). Trending: carbohydrate + inorganic-ion + amino-acid
  transport *up*; cell motility + signal transduction *down* (ns).
- **Motility gene-level (96 KEGG flagella+chemotaxis genes, 94 DE rows):**
  **7 significant down, 1 up.** Down = the chemotaxis core: cheA (ACZ81_01465,
  ACZ81_05280), cheW, cheR, aer2, fliL (log2FC −1.0 to −2.4); up = cheB.

**Description, then interpretation.** At day-11 exponential, motility/chemotaxis
genes lean down and biosynthetic/transport metabolism leans up in coculture.
`[interpretation]` This is directionally consistent with a fed, growing cell that
down-regulates foraging — and with the original Weissberg "motility down with MED4"
observation — but it is the exponential snapshot, most pathways do not survive BH,
and the carbon-starvation prediction (a divergence that *grows* over the
time-course) is untested until step 5. No claim of significance for motility here
(chemotaxis does not survive correction).

**Noise to ignore** `[interpretation]`: KEGG maps some flagellar/chemotaxis genes to
human-disease pathways (Salmonella infection, NOD-like receptor, HIF-1) — cross-
annotations, not biology for a marine bacterium. Filter these in step 5 reporting.

## Decisions

- **2026-06-15 — method = `pathway_enrichment` called directly** (KEGG L2 + COG L0),
  plus `differential_expression_by_gene` for the motility readout. No wrapper of the
  ORA primitives (would duplicate the tool).
- **2026-06-15 — ontology/level via `ontology_landscape`**, not guessed: KEGG L2
  (interpretable, ~0.31 coverage) + COG L0 (~0.69). Coverage caveat recorded.
- **2026-06-15 — `run_contrast` is reusable** so step 5 applies it across all
  contrasts (time-courses, EZ55 direction-only, controls).

## Decide-gate checklist

- **Outputs produced:** `scripts/01_method.py`; `data/med4_snapshot_kegg_l2_enrichment.csv`,
  `_cog_l0_enrichment.csv`, `_motility_genes_de.csv`, log. (Old `01_worked_example.py`
  removed.)
- **Results presented:** ontology scout, KEGG-L2 / COG-L0 / motility tables on the
  driving example (above).
- **QC gate:** ontology/level chosen on coverage evidence (not guessed); motility
  pathways confirmed present at KEGG L2; method returns per-direction Fisher + BH;
  KEGG human-disease cross-annotations identified as noise; coverage caveat logged.
- **Advance rationale:** the per-contrast method is built, validated, and freezing
  CSVs; step 5 runs `run_contrast` across the time-courses (difference of
  trajectories) + EZ55/MIT1002 controls and composes the carbon-starvation read.
