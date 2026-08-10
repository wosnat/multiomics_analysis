# Analysis milestone — run manifest (facts only)

Primary experiment scored with the committed methods code
(`methods/score_modules.py`, imported not reimplemented). No interpretation here —
the main thread owns that.

## Experiment (confirmed via `list_experiments`)

- **ID:** `10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq`
- HOT1A3 coculture with *Prochlorococcus* MED4 **vs Axenic**; day 11, exponential;
  RNASEQ; DESeq2; `table_scope = all_detected_genes`; medium PRO99-lowN; continuous
  light; 24 C. Authors: Weissberg, Aharonovich, Sher.
- `distinct_gene_count = 3947`; genes_by_status: 111 significant_up / 163
  significant_down / 3673 not_significant.

## Step 1 — per-gene DE pull (`analysis/cache/`)

- Pulled `differential_expression_by_gene(experiment_ids=[EXP], limit=None,
  verbose=True)` → **3947 genes, one row each, 0 duplicate rows**.
- **Sign distribution (all 3947 genes): 2136 negative (54.1%), 1809 positive
  (45.8%), 2 zero.** Within the healthy 40–55%-negative band → log2fc sign is
  intact (not stripped). Data-integrity check passes.
- Cached: `de_table.json` (locus_tag → log2fc), `de_meta.json` (adds gene_name,
  product, gene_category, padj, expression_status), `de_pull_log.json`,
  `peptidase_genes.json` (94 peptidase/protease genes from `genes_by_function`).

## Steps 2–3 — modules, controls, scoring

- Built from `methods/hot1a3_transporter_table.csv` via `build_modules_from_csv`:
  **33 organic-carbon-importer modules** over **53 systems**; inorganic-importer
  control set = **84** (primary, interaction-coupled N/P excluded) and **100** (all
  inorganic importers, for comparison).
- `score_modules(scope="genome_wide", n_perm=10000, seed=0)`. Output
  `hot1a3_day11_module_scores.csv` (per module) + `..._per_system.csv`.
- **Module effect range 0.132–0.997; 8 modules with effect > 0.9.**
- **Modules called up at q < 0.10: 1.** min q = 0.0924; modules with q < 0.25: 3.

| module | resolution | n_sys | effect | p_perm | q_perm | called_up | p_vs_ctrl84 | p_vs_ctrl100 |
|---|---|---|---|---|---|---|---|---|
| benzoate | specific_compound | 1 | 0.997 | 0.0028 | 0.092 | **True** | 0.026 | 0.021 |
| carboxylate | broad_class | 2 | 0.994 | 0.0062 | 0.102 | False | 0.064 | — |
| fucose/galactose/glucose | multi_substrate | 3 | 0.970 | 0.087 | 0.411 | False | 0.137 | — |
| aminobenzoyl-glutamate | specific_compound | 1 | 0.965 | 0.037 | 0.295 | False | 0.050 | — |
| carbohydrate | broad_class | 1 | 0.947 | 0.054 | 0.295 | False | 0.095 | — |

(Full 33-module catalog in the CSV, sorted by effect desc.)

## Step 4 — validation-set up-percentile distributions (`validation_checks.csv`)

Read off the SAME genome-wide up-percentile ranking (0 = most down, 1 = most up).
Numbers are distributions, not conclusions.

| set | n | median up-pct | expected |
|---|---|---|---|
| motility (`gene_category=Cell motility`) | 123 | **0.184** | down (low) |
| ribosomal (`gene_category=Translation`) | 198 | **0.504** | ~neutral |
| peptidase / protease | 93 | **0.565** | up (high) |
| inorganic-control importer **systems** | 84 | **0.503** | not high |
| whole-genome baseline | 3947 | 0.500 | ~0.5 |
| `glcB` `ACZ81_13685` (malate synthase G, single gene) | 1 | **0.028** | up if glycolate a source (soft) |

- **Glycolate module: absent** — no glycolate transporter module was built from the
  transporter table, so glycolate has no uptake module to score; `glcB`'s low
  percentile is reported as the single-gene soft check only.

## Step 5 — genome-wide enrichment guard (`enrichment_guard.csv`)

- Level pre-flight (`ontology_landscape` on this experiment): KEGG level 2 (145
  pathway-map terms) and EC level 2 (85 terms) are the pathway-level slices; the
  KEGG degradation maps are level-2 terms, so guard + breakdown flag read at KEGG
  level 2. `pathway_enrichment(direction="both", significant_only=True,
  background="table_scope")`.
- **KEGG up-direction over-represented terms (p_adj < 0.05): 3** — Purine
  metabolism (fold 5.33, p_adj 5.1e-3), 2-Oxocarboxylic acid metabolism (fold 6.38,
  p_adj 6.1e-3), Propanoate metabolism (fold 6.67, p_adj 1.0e-2).
- **EC up-direction over-represented terms: 0.**
- **Per-module breakdown flags** (only the 4 candidate modules with a dedicated
  KEGG degradation map; all others = "not determinable"):

| module | degradation map | match | flag |
|---|---|---|---|
| branched-chain amino acid | ko00280 Valine/leucine/isoleucine degradation | exact | tested, not enriched (up) |
| benzoate | ko00362 Benzoate degradation | exact | tested, not enriched (up) |
| aminobenzoyl-glutamate | ko00627 Aminobenzoate degradation | broader | tested, not enriched (up) |
| 3-phenylpropionic acid | ko01220 Degradation of aromatic compounds | broader | tested, not enriched (up) |

## Step 6 — figures (`analysis/`)

- `fig_module_catalog.png` — 33 modules ranked by effect; the 1 module at q<0.10
  (benzoate) marked red.
- `fig_validation_distributions.png` — violin plots of up-percentile for motility /
  ribosomal / peptidase / inorganic-control-systems / whole-genome.

## Anomalies / things to flag (facts, not judgments)

- Data integrity is clean: sign distribution 54.1% negative (not lost); no duplicate
  DE rows; all 3947 genes scored.
- The single module passing q < 0.10 (**benzoate**) belongs to the aromatic /
  xenobiotic class that the proposal **pre-registered as an expected-negative**.
  The two other aromatic modules (aminobenzoyl-glutamate effect 0.965 q 0.295;
  3-phenylpropionic acid effect 0.926 q 0.519) did not pass. Reported for the main
  thread's judgment; not interpreted here.
- All 4 testable breakdown maps came back "tested, not enriched (up)"; the KEGG
  up-enrichment hits are metabolism maps (purine / 2-oxocarboxylic acid /
  propanoate), not the dedicated degradation maps.
- No glycolate uptake module exists in the transporter table, so the glycolate
  positive check rests on the single gene `glcB` (percentile 0.028).
