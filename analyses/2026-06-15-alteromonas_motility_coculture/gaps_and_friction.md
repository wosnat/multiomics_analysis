# Gaps and friction

Transitional log of methodology / KG / tooling friction encountered during this
analysis, distinct from decisions (which live in each step's `notebook.md`).
Append-only.

---

*(no entries yet)*

## 2026-06-15 — reinvented ORA before checking the enrichment assets

**What happened.** For step 4 I started writing a custom gene-set DE-summary
module (`geneset_de.py`) with my own Fisher exact test, before checking that the
package already provides over-representation analysis. The researcher flagged it.
The package ships `pathway_enrichment` (DE→ORA wrapper) plus `de_enrichment_inputs`
/ `fisher_ora` / `signed_enrichment_score`, documented at `docs://analysis/enrichment`.
My version also got the background wrong (used all genes in the frame rather than
the per-experiment `table_scope` quantified set).

**Workaround / impact.** Deleted the custom module; used `pathway_enrichment`.
Methodology note for the skill: before building any scoring/statistics utility,
check `docs://analysis/enrichment` and the package's analysis utilities — the
enrichment/ORA/derived-metric machinery is already there. Reinventing risks
subtle errors (here, the background denominator).
