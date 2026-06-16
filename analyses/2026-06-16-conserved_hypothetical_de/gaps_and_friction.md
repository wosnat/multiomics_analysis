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

## 2026-06-16 — Conservation denominator is 17 strains, not 19

The KG has 19 *Prochlorococcus* genome strains, but the cyanorak ortholog backbone
annotates only 17 of them (two strains carry no cyanorak groups). "Conserved across
strains" must normalize against 17, not the headline 19. Caught during step 2 QC;
recorded so step 3's conservation cutoff uses the right denominator and the write-up
doesn't overstate coverage.

