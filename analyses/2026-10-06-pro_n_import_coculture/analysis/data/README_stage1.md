# Stage 1 data (analysis milestone): regeneration

Run from the repo root (KG reachable, preflight green):

```
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/s1_pull_de.py
.venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/analysis/tests
```

## KG calls
All calls go through `methods/kg_fetch.fetch`: one unpaged call each, with `returned == total_matching` asserted and a unique natural key.
- One `list_experiments` call for the 13 proposal §2 experiments (strict inputs, verbose).
- One `differential_expression_by_gene` call per experiment (verbose). Natural key: (locus_tag, experiment_id, timepoint).

## Files
- `de_long.csv.gz` (gzip, 2.5 MB): one row per gene × experiment × timepoint.
  - `is_pooled` is True for the pooled "days 60+89" slices. These get their own percentiles and must not be mixed with single days.
  - `padj_lt_0.05` is shown next to the stored `expression_status`. The status is the source paper's call; it is not padj alone.
  - `rank_percentile`: within each slice, `1 − (position − 1)/n_detected`, with log2FC sorted in descending order.
    - Ties take the mean position.
    - Rows with null log2FC are not ranked.
    - Filtered and significant-only tables are ranked but carry `percentile_valid=False` and "filtered table: positive evidence only".
- `experiments.csv`: metadata per experiment, plus the timepoints and per-timepoint gene counts from `list_experiments`.
- `qc_slices.csv`: QC per experiment × timepoint.
- `coverage_methods_universe.csv`: methods v1.6.1 High/Medium system members found in each table.
- `checks_10.csv`: the 10 spot checks.
- `raw_samples/<short>.json`: the first 3 raw rows of each DE call.
- `raw/de_raw_<short>.json.gz`: the full raw DE dumps (2.4 MB in total). Below the 5 MB threshold, so not gitignored.
- `s1_summary.json`: versions and the call log.
