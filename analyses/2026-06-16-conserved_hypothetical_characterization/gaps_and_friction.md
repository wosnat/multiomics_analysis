# Gaps and friction

Transitional log of methodology / KG / tooling friction encountered during this
analysis. Distinct from decisions (which live in each step's `notebook.md`).

## Step 2

- **2026-06-16 — `to_dataframe` drops the polymorphic derived-metric `value` column.**
  `gene_derived_metrics` returns a `value` whose type varies (float / 'true'/'false' /
  category string); `to_dataframe` flattening warns and drops it (also drops nested list
  columns `cyanorak_roles`, `cog_categories`, `discussed_in_publications`). The raw JSON
  dump preserves everything. Mitigation: step-5 derived-metric extraction reads `value`
  from `result["results"]` directly, not from the flattened CSV.
- **2026-06-16 — `docs://guide/python_api` resource raises a charmap decode error** when
  read through `ReadMcpResourceTool` (byte 0x90). Fell back to the skill's
  `references/python-api-guide.md`, which carries the scripting discipline. Worth a fix
  upstream (non-utf8 byte in the shipped doc).

## Step 1

- **2026-06-16 — KG release moved between analyses.** The selection analysis that
  produced the input shortlist ran on KG `0.1.0-alpha.5` (built 2026-06-09); this
  characterization runs on `0.1.0-alpha.6` (built 2026-06-16). The cyanorak ortholog
  group ids are stable, but homolog / expression / cluster edges may differ. Mitigation:
  re-resolve every OG fresh in step 2 instead of trusting alpha.5-derived numbers; treat
  the carried-forward DE fingerprint as alpha.5 provenance (it is a frozen input from the
  prior analysis, not re-derived here).

