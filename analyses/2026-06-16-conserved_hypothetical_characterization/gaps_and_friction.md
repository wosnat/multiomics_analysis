# Gaps and friction

Transitional log of methodology / KG / tooling friction encountered during this
analysis. Distinct from decisions (which live in each step's `notebook.md`).

## Step 1

- **2026-06-16 — KG release moved between analyses.** The selection analysis that
  produced the input shortlist ran on KG `0.1.0-alpha.5` (built 2026-06-09); this
  characterization runs on `0.1.0-alpha.6` (built 2026-06-16). The cyanorak ortholog
  group ids are stable, but homolog / expression / cluster edges may differ. Mitigation:
  re-resolve every OG fresh in step 2 instead of trusting alpha.5-derived numbers; treat
  the carried-forward DE fingerprint as alpha.5 provenance (it is a frozen input from the
  prior analysis, not re-derived here).

