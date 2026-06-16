# Gaps and friction

Transitional log of methodology / KG / tooling friction encountered during this
analysis, distinct from decisions (which live in each step's `notebook.md`).
Append-only, prose entries with dates.

## 2026-06-16 — MCP docs resources fail on Windows (encoding)

`ReadMcpResourceTool` on `docs://guide/conventions` and `docs://guide/python_api`
raised `'charmap' codec can't decode byte 0x90` — the MCP server reads the doc
files with the Windows default codepage instead of UTF-8. Workaround: read the
same docs from the local package install at
`.venv/Lib/site-packages/multiomics_explorer/skills/multiomics-kg-guide/references/`
(pointed out by the researcher). Downstream impact: none on results; but the
in-band docs:// route is unusable on Windows until the server opens these files as
UTF-8. Tooling fix candidate for the explorer package.

## 2026-06-16 — Scripts must run from repo root, not the analysis dir

First run of `01_de_experiments.py` was launched after `cd` into the analysis
folder; `GraphConnection` then failed to find the repo-root `.env` and tried
`localhost:7687` (connection refused). The Python-API guide says run from the repo
root. Resolution: invoke `uv run python analyses/.../scripts/NN.py` from the repo
root; scripts already use `__file__`-relative output paths so CWD only matters for
credential loading. Process note, no methodology change.

## 2026-06-16 — Scope split: selection here, characterization as a follow-on analysis

The step-1 question was two-part: (a) select broadly-DE conserved hypotheticals, and
(b) characterize what the KG can tell us about them. During step-5 co-define the
researcher decided to frame these as two separate analyses — this one ends at the
ranked shortlist (steps 5–6); the characterization (homologs, genomic neighborhood,
co-expression, ontology of neighbors) becomes a new analysis taking this shortlist as
input. Handled via the step-protocol **reopen path**: the step-1 lock was edited to
record original + trigger + evolved (selection-only) question rather than silently
rewritten. Methodology note: a naturally two-part question is cleaner as two
single-question analyses; worth watching whether this recurs as a pattern.

## 2026-06-16 — differential_expression_by_ortholog has no per-datapoint rank/magnitude

The ortholog-framed DE tool returns member **counts** per group×experiment×timepoint
(significant_up/down/not_significant); per-datapoint `log2fc` and `rank` are not in
its rows (only an aggregate `max_abs_log2fc`/`median_abs_log2fc` in the envelope).
The "highly responsive" axis (best rank, per-treatment magnitude) therefore requires
the per-gene tool `differential_expression_by_gene`, which carries `log2fc`,
`rank_up`, `rank_down`, `expression_status` per row. Resolution: use the per-gene tool
as the single scoring source; the ortholog tool is triage. (Confirmed empirically by
dumping result keys, not from the doc.)

## 2026-06-16 — differential_expression_by_gene requires experiment_ids of one organism

`differential_expression_by_gene` is single-organism and raises
`experiment_ids span multiple organisms` if passed experiment IDs from other strains.
Since candidate ortholog families span up to 17 strains, extraction must batch per
strain and pass each strain only its own pooled experiment IDs. Minor API constraint;
step 5 extraction respects it.

## 2026-06-16 — Conservation denominator is 17 strains, not 19

The KG has 19 *Prochlorococcus* genome strains, but the cyanorak ortholog backbone
annotates only 17 of them (two strains carry no cyanorak groups). "Conserved across
strains" must normalize against 17, not the headline 19. Caught during step 2 QC;
recorded so step 3's conservation cutoff uses the right denominator and the write-up
doesn't overstate coverage.

