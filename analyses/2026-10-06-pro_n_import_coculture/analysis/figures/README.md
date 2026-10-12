# Analysis milestone figures: descriptive exploration (E1–E6)

All figures are descriptive; there are no labels and no pass/fail. They use the methods f1 style (imported through `analysis/figs.py`) and are saved as PNG (300 dpi) and SVG.
- **Data:** stage-1 `analysis/data/de_long.csv.gz` with the pooled "days 60+89" slices excluded, plus the methods v1.6.1 tables.
- **Significance:** the stored `expression_status`.
- **Tables:** `analysis/data/explore/`.

Commands (repo root):

```
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e1_timecourses.py
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e2_concordance.py
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e3_comovement.py
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e4_broad_systems.py
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e4b_broad_scatter.py
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e5_late_coculture.py   # 1 KG call via kg_fetch
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e6_controls.py
.venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/analysis/tests
```

## MED4 gene sets (`explore.gene_sets`)
- **Dedicated N systems:** amt1, urt, cyn, dpp.
- **Every other High/Medium system with an N listing in p18.** These are all broad listings; efflux and known-false-positive flags are shown.
- **Linked enzymes:** the neighbour- and function-linked enzymes of the dedicated systems (fragments excluded), plus ureA–G (PMM0963–0969), cynS (PMM0373) and glsF (PMM1512).
- **Starvation markers:** glnA, ntcA, glnB, pipX.
- **Non-N systems:** pst, phn, sul1, sul3, fut/idiA2, mnt, lraI, sbtA.
- **Marker gene:** phoH.

## Figures

| Figure | What it shows | Source tables |
|---|---|---|
| e1_protein_heatmap / e1_rna_heatmap | log2FC (orange up / blue down, clipped ±4; colorbar under each panel) and rank percentile per gene × slice. Protein slices: axenic d14, d31, d89 (d31 and d89 are death phase) and coculture d18, d31, d60, d89. RNA slices: axenic d14 and coculture d18–d89. ● significant up, ▼ significant down, hatched = not detected. | explore/e1_gene_slice_long.csv |
| e1_median_percentile_lines | Median rank percentile per system over coculture days, for amt1, urt, cyn, dpp, the markers and the pooled non-N members, in protein and in RNA. | explore/e1_system_median_percentile.csv |
| e2_concordance | Protein vs RNA log2FC for genes detected in both, at axenic d14 and coculture d18–d89, with Spearman ρ. Highlighted: N regulon, broad N systems, non-N systems, ribosomal proteins; markers labelled. | explore/e2_quadrants.csv, e2_spearman.csv, e2_pairs_long.csv |
| e3_corr_protein / e3_corr_rna | Spearman ρ between log2FC trajectories within the N regulon, over 7 protein / 5 RNA slices (n ≤ 7 / 5 points per ρ), in average-linkage order. | explore/e3_corr_protein.csv, e3_corr_rna.csv |
| e3_relative_rank | Three differences over coculture days, in protein and RNA: amt1 − median(urt + cyn subunits); median cyn − median urt; median dpp − median markers. | explore/e3_relative_rank.csv |
| e4_broad_dotgrid | For each broad-only N system × listed class, at coculture d60 and d89 protein: the median protein percentile of the class's genome enzymes (dot colour, n below the dot) next to the transporter's median percentile ("T"). The Cysteine / L-Cysteine split is fixed by stereo-generic merging. | explore/e4_system_class_enzymes.csv, e4_systems.csv, e4_members.csv, e4_stereo_fix.csv |
| e4_broad_scatter | Redesign of e4_broad_dotgrid (same data; scripts/e4b_broad_scatter.py). Panels: coculture protein d60, d89 and axenic d14. Each point is one broadly-listing transporter × one listed N class: x = the transporter's median protein rank percentile; y = the median protein rank percentile of the class's detected genome enzymes. Colour = N class (fixed categorical order); triangle = efflux-annotated. Classes with no detected enzyme sit in a "no enzyme" strip below the axis (nitrate for sul1 and sul3). Dashed lines at 0.5, dotted at 0.9. Labels are placed by a greedy non-overlap routine. Known false positives are excluded (gst PMM0110/0566/0630, sodX PMM1295), and glcH PMM1323, which is not detected in protein, has no x; both are listed in the caption. The old e4_broad_dotgrid is kept for now. | explore/e4_system_class_enzymes.csv, e4_systems.csv |
| e5_late_coculture_roles | Genes at percentile ≥ 0.90 at both d60 and d89 that are not significantly up at axenic d14, in protein and RNA, counted by Cyanorak top-level role. Transporter-universe genes are listed. | explore/e5_set_protein.csv, e5_set_rna.csv, e5_role_counts.csv, e5_cyanorak_roles_level0.csv |
| e6a_tolonen_ndep_heatmap | Tolonen N deprivation, 0–48 h: log2FC (orange up / blue down, clipped ±3) and percentile, each with a colorbar, for the N subunits, markers, urease, cynS / glsF and the non-N systems. | explore/e6a_tolonen_ndep.csv |
| e6b_cyanate_vs_urea | Tolonen MED4: percentile per gene on three tables, in bar order growth on cyanate as sole N (steady state), growth on urea as sole N (steady state), N deprivation 24 h. Group headers read "short name: what it moves (class)"; a band separates N import & assimilation from the non-N reference transporters. | explore/e6b_calibration_bars.csv, e6b_cyanate_urea.csv |
| e6cd_controls | N-replete controls (MED4 ismej.2016.70; MIT9313 at both inocula): percentiles of the N-system subunits vs the non-N subunits. MIT9313 uses its own dedicated N systems (p18 dedicated + fig2 Block A usable), including natF/natG. | explore/e6cd_controls_genes.csv, e6cd_controls_summary.csv |

## Cysteine fix (E4)
- **What it does:** `explore.stereo_equivalents` merges amino-acid compound groups whose names differ only by an L-, D- or DL- prefix. It also always merges the explicit KEGG pair C00736 (Cysteine) and C00097 (L-Cysteine).
- **Scope:** it is applied only in the analysis code. The methods tables are unchanged.
- **Groups merged:**
  - Cysteine C00736 → L-Cysteine C00097: 0 → 15 genome enzymes.
  - Glutamate C00302 → C00025 / C00217: 1 → 35.
  - Alanine C01401 → C00041 / C00133: 0 → 11.
- **Effect:** among the 28 broad-only system × class cells, the cells with 0 genome enzymes go from 9 to 3.

## E7: coculture exponential baseline (scripts/e7_baseline.py)

| Figure | What it shows | Source tables |
|---|---|---|
| e7_baseline | (a) One row per gene, grouped by system with readable headers. x = log2 fold change, coculture vs axenic (same study, RNA), with a line at 0 ("← higher in axenic" / "higher in coculture →"). Hollow = d11 (exponential); filled = d18 (coculture d18 vs the axenic sample, ~d14, late decline). ↑/↓ = significant. The legend carries a worked example: cynA, 8.6× higher in coculture at d11 → 4.6× higher in axenic at d18 (fold change = 2^\|log2FC\|). No point exceeds the ±4 clip. Rank percentiles are no longer drawn; they stay in e7_gene_sets.csv. (b) Genome-wide, d11 coculture-vs-axenic log2FC against coculture d18-vs-own-exponential log2FC, with the N regulon highlighted. | explore/e7_gene_sets.csv, e7_set_medians.csv, e7_diff_of_contrasts.csv, e7_consistency.csv |

Command:

```
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e7_baseline.py
```

## E8: MIT9313 Tolonen calibration (scripts/e8_tolonen_mit9313.py; 1 list_experiments call + 3 DE calls via kg_fetch)

| Figure | What it shows | Source tables |
|---|---|---|
| e8_tolonen_mit9313 | (a) Rank percentile per gene on three MIT9313 tables, in bar order growth on nitrite as sole N, growth on urea as sole N, N deprivation 24 h; readable group headers and N / non-N bands, using MIT9313's own systems: amt1, urt, focA + nirA, dpp, natFGH + grrP, agcS, proVWX, proP, urease, the markers, and the non-N systems. (b) MIT9313 N deprivation, 0–48 h: log2FC heatmap for the same set (orange up / blue down, clipped ±3; colorbar). | data/de_long_mit9313_tolonen.csv.gz; explore/e8a_calibration_bars.csv, e8_nitrite_urea.csv, e8_calibration_rules.csv, e8_ndep.csv, e8_ndep_up_summary.csv, e8_experiments.csv |

The three MIT9313 experiments are stored in `analysis/data/de_long_mit9313_tolonen.csv.gz`. It has the same columns as `de_long.csv.gz`, which is left unchanged. Their QC rows are appended to `analysis/data/qc_slices.csv`; a re-run replaces them.


## Colour convention (revised 2026-10-11)
- Every diverging log2FC heatmap uses orange = up (positive), blue = down (negative), neutral at 0, with a colorbar naming the quantity and its clipping.
- This covers e1, e6a and e8b. The e3 correlation heatmaps use the same map, so positive ρ is orange there too.
- Rank-percentile heatmap panels (e1, e6a) use a single-hue purple ramp (light grey to dark purple; figs.PCT), so they are not confused with blue "down". They carry a "rank percentile, 0–1" colorbar.
- On cells at percentile ≥ 0.70 the ●/▼ markers are drawn white; elsewhere they are black.
- The e4 dot grid keeps the blue sequential map.
- e1 heatmaps: a thick vertical line separates the axenic columns from the coculture columns in both panels, with an "axenic" / "coculture" header over each block.
- Calibration bar subtitle: "Sole-N experiments = steady-state exponential growth on the sole N source vs N-replete Pro99 medium; N deprivation = 24 h of nitrogen deprivation vs N-replete Pro99 medium". The KG control fields read "N-replete Pro99 medium"; they don't say "ammonium-replete", so I used that wording.
- e8_tolonen_mit9313.py reads the stored de_long_mit9313_tolonen.csv.gz by default and re-queries the KG only with --pull.


## E9: published co-expression clusters (scripts/e9_clusters.py; KG calls via kg_fetch: list_clustering_analyses, genes_in_cluster x4, genes_by_ontology MIT9313 level 0, list_experiments + DE x2 for MED4 iron starvation)

| Figure | What it shows | Source tables |
|---|---|---|
| e9_cluster_profiles | Median log2FC per cluster in the clustering's own experiment (orange up / blue down, clipped ±3, values printed). MED4 N-starvation k-means (K=9) on Tolonen MED4 N deprivation; MIT9313 (K=7) on Tolonen MIT9313; MED4 iron clusters on ismej.2011.49 iron starvation (12 h, 24 h; 48 h from the second set; filtered tables). Row label = explore.classify_profile (\|0.5\| threshold). | explore/e9_cluster_profiles.csv, e9_membership.csv, e9_cluster_counts.csv |
| e9_anchor_cluster_read | MED4 N-starvation and iron clusters: median rank percentile of detected members per anchor slice (protein axenic d14/d31/d89, coculture d18–d89; RNA axenic d14, coculture d18–d89; direct contrast d11, d18), with n detected printed. Thick line = axenic \| coculture. Purple scale; genome background 0.5. | explore/e9_cluster_slice_medians.csv |

Other tables:
- explore/e9_where_genes_sit.csv: the cluster of each MED4 / MIT9313 gene-set member, or "not clustered".
- explore/e9_cyanorak_roles_level0_mit9313.csv: MIT9313 Cyanorak top-level roles.
- data/de_long_med4_iron.csv.gz: the two MED4 iron-starvation tables; their QC rows are in qc_slices.csv.


## E10: all-systems status matrix (scripts/e10_system_matrix.py; no KG calls)

Rows (80): the 73 MED4 High/Medium systems (methods v1.6.1 p11) plus 7 reference rows: glnA, ntcA, glnB and pipX (one row each), urease ureA–G (one row), cynS, glsF. Efflux-annotated and known-FP systems are kept and tagged [efflux] / [FP]; [H]/[M] = tier.
Columns, in 3 blocks:
- coculture vs axenic: Aharonovich 2016 MED4 20 h (shaded; 82% of genes negative, so "down" is mostly table-wide); direct contrast d11 and d18.
- N starvation / other N sources: Tolonen N deprivation 3–48 h; Read N-depleted 3/12/24 h (filtered tables: missing = not listed, no percentile); Tolonen growth on cyanate and on urea.
- this study: protein ax d14, d31, d89 | cc d18–d89; RNA ax d14 | cc d18–d89.
No pooled slices.

Cell status (explore.cell_status) is computed over the stored expression_status of detected subunits: up / down / mixed / ns / not detected. Count shown = number significant in the shown direction / number detected.

| Figure | What it shows | Source tables |
|---|---|---|
| e10_status_matrix | Dendrogram + (A) status + (B) median rank percentile of detected subunits (purple). Row order: average-linkage clustering, euclidean, on the B profile over the non-filtered columns; the 112 missing cells imputed with 0.5. ★ strict / ☆ loose coculture-specific candidate. | explore/e10_cells.csv, e10_rows.csv, e10_clusters.csv, e10_flags.csv |
| e10_status_matrix_grouped | Same panels; rows grouped as N dedicated / N broad / linked enzymes / markers / non-N reference / other High/Medium. "N broad" = any class listing, so sul1/sul3 sit there, not under non-N. | same |
| e10_by_class | Status only, one panel per N class (ammonium … nucleobases/nucleosides) plus non-N reference transporters. Dedicated listings first, then broad. ◆ multi-class (n) names the other classes. Organic classes come from p18 listing_basis; inorganic classes come from the fig2 Block A rows (most_specific, or inherited from a non-lumping family, High/Medium) with the p18 dedicated rule. No class was skipped; "amines" has no High/Medium system and is not in the requested order. | explore/e10_by_class.csv |
| e10_by_system_dedicated | Per gene: amt1, urt, cyn, dpp, urease ureA–G, cynS + glsF, markers. Colour = the gene's own stored status; number = its rank percentile. | explore/e10_by_gene.csv |

Flags (explore.coculture_flags):
- strict (revised E14, all axenic samples): protein cc d60 and d89 both "up"; not "up" in axenic protein d14, d31 or d89; not "up" in axenic RNA d14; no Tolonen N-dep timepoint "up".
- loose (revised E14): cc d60 or d89 "up"; ax d14 median percentile < 0.75; not "up" in axenic protein d31/d89; Tolonen N-dep max percentile < 0.90.
- e10_flags.csv = flagged rows; e10_flags_all.csv = every row. Both carry the axenic d31/d89 protein and axenic RNA d14 status and percentile, plus cc_up_subunits (the member loci "up" at cc d60 and at cc d89).


## E11: small follow-ups (scripts/e11_followups.py; KG calls via kg_fetch: genes_by_ontology(ec) + gene_ontology_terms(ec, leaf), stored and re-pulled only with --pull)

| Figure | What it shows | Source tables |
|---|---|---|
| e11_above_stimulon | (a) For every E10 row with ≥1 detected subunit at both cc d60 and d89 (64 of 80): system excess over the stimulon at protein ax d14 (x) vs the mean of cc d60 and d89 (y). Stimulon level = median percentile of the detected Tolonen MED4 c1+c2 members in each slice (13 of 21 detected; 0.973–0.988). Excess = median over subunits of (percentile − level). Dashed lines = at stimulon level; grey diagonal = equal excess. (b) Zoom on the box near y = 0, with all systems labelled. | explore/e11_stimulon_levels.csv, e11_system_excess.csv, e11_gene_excess.csv, e11_top30_genes.csv |
| e11_n_releasing | Per-gene status in the e10 style for the MED4 genes under ec:3.4.-.- (49), ec:3.5.-.- (29) and ec:4.3.1.- (2), grouped by class. Labels carry each gene's own leaf EC numbers. ★ = up in cc protein at d60 and d89, not up at protein ax d14, and not up at any Tolonen N-dep timepoint 3–48 h (3 h not shown as a column). | explore/e11_n_releasing.csv, e11_ec_sets.csv, e11_ec_leaf.csv, e11_ec_counts.csv, e11_calls.json |
| e11_n_relief | Median protein percentile of the detected members across ax d14 → cc d18/d31/d60/d89, for the N-down clusters c6–c9 (each labelled by its top Cyanorak role) and the c1+c2 stimulon. Line at 0.5. Single-cluster values match e9_cluster_slice_medians.csv (asserted). | explore/e11_n_relief.csv |


## E13: summary figure (scripts/e13_summary_figure.py; no KG calls; revised in E14)

| Figure | What it shows | Source tables |
|---|---|---|
| e13_summary | (A) Protein only, one row per route. Each row shows the median rank percentile of detected subunits at axenic d14 (hollow circle), axenic d31 and d89 (death; small grey square and diamond) and coculture d89 (orange). A line joins axenic d14 to coculture d89. Narrow panel: Tolonen MED4 N deprivation (RNA, microarray), max over 3–48 h. Routes: amt1, urt, urease, cyn, cynS, clc2 (nitrate, which MED4 can't use), dpp, PMM0561 (peptides, broad listing), the broad median (17 N systems; known FPs and murJ excluded; exploratory, decision 4), and som, bamA, tolC, acrA, murJ, plus the markers median (glnA, ntcA, glnB). ★/☆ = E14 flags. (B) Verdict text, coloured orange = up with N stress, purple = coculture-specific, grey-purple = up in coculture but unresolved or not specific, grey = no signal. (C) Calibration: ✗ / ~ / —. | explore/e13_summary.csv (from e10_cells.csv, e10_rows.csv, e10_flags_all.csv; e8_nitrite_urea.csv for the MIT9313 urt note) |


## E14: critic fixes

- Coculture flags were recomputed with all axenic samples (see E10). E10 matrices, e10_flags*.csv and the explorer (scripts/e12_build_explorer.py) were rebuilt. E11 e11_n_releasing uses the same strict rule.
- The "starvation markers" set used in E1, E3, E7 and E11 is glnA, ntcA, glnB and pipX. pipX is included. Each affected CSV now carries a `markers_set` column saying so: e1_gene_slice_long, e1_system_median_percentile, e3_relative_rank, e7_gene_sets, e7_set_medians, e7_consistency and e11_system_excess. The values are unchanged; this was checked against the previous files. The E13 markers row uses glnA, ntcA and glnB only.
- scripts/e14_marker_log2fc.py writes data/explore/e14_marker_log2fc.csv (long) and e14_marker_log2fc_wide.csv. They hold the stored protein log2FC, status and percentile of ntcA, glnA, glnB, urtA and cynA at axenic d14/d31/d89 and coculture d18/d31/d60/d89.


## E15: [external, not in KG] CC1A3 culture data (scripts/e15_external_culture.py; workbook step scripts/e15_convert_xlsx.py via `uv run --no-project --with pandas --with openpyxl`)

These are the researcher's own CC1A3 culture measurements (the same cultures as the anchor omics). They are not in the KG. Tidy data and provenance are in `data/external/cc1a3/` (README.md, cc1a3_tidy.csv, raw_sheets/). That folder is git-ignored by `analysis/.gitignore`. Helpers and quotas are in `cc1a3.py`, with tests in tests/test_cc1a3.py.

| Figure | What it shows | Source tables |
|---|---|---|
| e15_culture_n | (a) MED4 cells/ml (FCM, log), axenic and coculture. (b) HOT1A3 cells/ml, alone and coculture. Time-series bottles: points, with a line for the geometric mean of samples with >40 events. Omics bottles: diamonds. Hollow = ≤40 events; × = notebook "problematic" sample. (c) NH4 µM as used in the N budget sheet: replicates as points, mean line starting from the medium value (146.99 µM). Grey verticals = protein/RNA sampling days. | data/external/cc1a3/cc1a3_tidy.csv; explore/e15_culture_summary.csv |

Note: `data/explore/e15_culture_summary.csv` and the e15 figure also contain the external values. They are **not** git-ignored.
