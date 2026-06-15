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

## 2026-06-15 — Aharonovich & Sher 2016 HOT1A3 experiments report up-regulated genes only

**What happened.** The two HOT1A3 coculture-with-MIT9313 experiments
(10.1038/ismej.2016.70) have table_scope `all_detected_genes` but report
`significant_down = 0` for the whole experiment (188↑/0↓ and 30↑/0↓) — only
up-regulated genes are captured. The original step-5 read "motility direction
flips by partner (MED4 down, MIT9313 up)" was partly an artifact: down-regulation
is structurally invisible in the MIT9313 dataset, so its "up" lean cannot be
compared on equal footing with the both-direction MED4 (Weissberg) and EZ55 data.

**Workaround / impact.** Treat the 2016 MIT9313 experiments as up-only (not usable
for direction comparison). Caught only when we stopped to read each experiment's
setup before choosing the method. Methodology note: check `genes_by_status` /
what each experiment actually reports (not just `table_scope`) before comparing
directions across experiments — `all_detected_genes` does not guarantee both
directions are present.

## 2026-06-15 — "up-only" experiments: log2FC sign absent across ALL genes (4 experiments, two 2016 papers)

**What happened.** Following up on the up-only pattern, counted the sign of
`log2_fold_change` on every stored `Changes_expression_of` edge, per experiment
(`run_cypher`). Four experiments have **0% negative log2FC across all stored
genes** — significant *and* non-significant:

| experiment | table_scope | rollup up/down | neg / total edges |
|---|---|---|---|
| ismej.2016.70 MIT9313 (high inoc.) | all_detected_genes | 188 / 0 | 0 / 1879 |
| ismej.2016.70 MIT9313 | all_detected_genes | 30 / 0 | 0 / 2295 |
| ismej.2016.82 MIT1002 24h | significant_any_timepoint | 458 / 0 | 0 / 740 |
| ismej.2016.82 MIT1002 48h | significant_any_timepoint | 455 / 0 | 0 / 740 |

A full DE table with zero negative fold-changes across thousands of genes
(including 2265 / 282 *non-significant* ones) is not biology — the sign is gone
(stored as |log2FC|, `expression_direction` forced to "up").

**Diagnosis / what the metadata says.** This is **not an MCP rollup bug**: for
clean experiments (Weissberg HOT1A3 45–54% neg; EZ55 significant-only, where
`significant_down_count` exactly equals the negative-edge count) the rollup
faithfully reflects stored signs. The problem is in the stored edges for these
four. `table_scope_detail` is **empty** for all four, and `reports_fold_change`
is true. For ismej.2016.70 this is internally contradictory: scope
`all_detected_genes` + reports_fc=true vs. 0/2295 negative cannot both hold.

**Cause unresolved** (researcher did not know): either (a) ingestion sign-loss
(data bug), or (b) the 2016 papers tabulated only up-regulated genes (source
limitation) — which the schema cannot express: there is **no `table_scope`
value for "up-regulated only,"** and `table_scope_detail` is blank where that
nuance would live. To report to the KG team either way.

**Workaround / impact.** Drop all four from any direction analysis. Reusable
diagnostic: **`0% negative log2FC across all detected genes`** is the tell for
sign-loss — `significant_down = 0` alone is not (several spectrum.03275-22
proteomics contrasts have `down = 0` but real negative log2FC edges; they simply
have no *significant* down genes). Methodology candidate: before trusting
direction, check the log2FC sign distribution over all genes, not the rollup
counts.

## 2026-06-15 — a step-2 data reveal legitimately reopened the step-1 "locked" question

**What happened.** The skill treats steps 1–3 as a *research proposal* that is
**locked at the end of step 3**, and provides a redo path only for *downstream*
steps a later finding invalidates. This analysis hit a case the model doesn't
cover: a discovery while *executing* reopened an *upstream* lock. The step-1
question was "does Alteromonas turn motility up/down in coculture?" When step 2
pulled the full inventory, two data facts surfaced that the locked framing had
assumed away — (1) every usable coculture contrast runs in a medium with **no
added organic carbon**, making coculture-vs-axenic a carbon-source manipulation;
(2) the only direct coculture-vs-axenic contrast is a single **exponential**
snapshot, while starvation only develops over a separate time-course. Together
these reframed the question into a **carbon-provision** hypothesis (motility kept
as the lead readout). The step-1 lock had to be edited, not just step 4.

**Workaround / impact.** Recorded the evolution in `1_question/notebook.md`
(original lock + evolved question + a decision noting the reopening) rather than
pretending the original lock still held. No tooling broke; the gap is in the
*methodology model*.

**Methodology candidate (lock-vs-data-reveal).** "Locked at end of step 3" is too
strong: the data that would justify the framing often isn't seen until step 2/4
actually touches it. The skill needs an explicit, lightweight path for *a
downstream data reveal reopening an upstream lock* — re-open, record the trigger
and the before/after question in the owning step's notebook, re-lock — distinct
from the existing "redo invalidated downstream steps" path. Pairs with the
just-in-time-formalization principle (look at the data before fixing the framing):
the lock should be provisional until the data behind it has actually been pulled.
Seen once so far (this analysis); promote to the skill if a second analysis hits
the same friction.
