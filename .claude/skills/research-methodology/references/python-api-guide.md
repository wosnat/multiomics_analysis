# Python API: scripting discipline

The **API contract** — the import surface, function signatures, return
shapes, and `to_dataframe` — is owned by the explorer package and served
live by the MCP server at **`docs://guide/python_api`** (also shipped in
the package under `multiomics_explorer/skills/multiomics-kg-guide/`). It
is version-matched to the explorer your `uv sync` installed. Read it for
mechanics; do **not** re-derive imports or return shapes from memory.

This doc covers only what that reference can't: how to script *carefully*
against the API — where to run, verifying before scripting, preferring the
API over raw Cypher, and the gotchas that silently produce wrong results.

For **which** interface to use (browse in MCP vs extract in Python), see
[KG rules — MCP vs Python API](kg-rules.md#mcp-vs-python-api).

---

## Where to run scripts

- **Run from the template repo root (your clone).** The explorer is
  installed into this project's venv by `uv sync`. Use `uv run script.py`
  or `.venv/bin/python script.py`.
- **Do not** use `uv run --directory /path/to/multiomics_explorer` — that
  runs in the wrong environment. There is no sibling explorer clone in the
  template model; the explorer lives in your venv.
- **Neo4j must be reachable** — same connection as the MCP server,
  configured via the gitignored `.env` at the repo root (see the README).

## MCP tools and Python API functions are the same code

Same names, same parameters, same return-dict structure. A tool you used
interactively (`gene_response_profile`, `differential_expression_by_gene`)
is importable from `multiomics_explorer` with an identical signature. The
authoritative import surface is in `docs://guide/python_api` — import from
the top-level `multiomics_explorer` namespace only; deeper paths
(`.api`, `.analysis.frames`, …) are internal implementation detail the
package explicitly tells you not to import from.

`to_dataframe(result)` is the single entry point for turning any result
into a flat, CSV-safe DataFrame — it auto-dispatches on result shape. Don't
reach for per-shape converters or hand-flatten nested fields.

## Pre-script checklist (verify before scripting)

Computations go in scripts, not chat (SKILL.md Rule 5) — but a script
built on guessed field names or an unchecked result size produces
confident, wrong output. Before writing any extraction script, verify
interactively:

1. **Import works:**
   ```python
   from multiomics_explorer import gene_response_profile
   ```
2. **Return schema** — inspect a small call before trusting field names:
   ```python
   result = gene_response_profile(locus_tags=["PMM0370"], limit=1)
   print(result.keys())                 # envelope fields
   print(result["results"][0].keys())   # per-row fields
   print(result["results"][0])          # actual values and types
   ```
3. **Column names** — verify against actual output, never guess:
   ```python
   import pandas as pd
   df = pd.DataFrame(result["results"])
   print(df.columns.tolist())
   ```
4. **Dataset size** — check `total_matching` to decide whether `limit=None`
   is safe or you need to filter upstream:
   ```python
   print(result["total_matching"])
   ```

## Before reaching for `run_cypher`

Function names reflect the most common use case, not the only one. Several
`_by_X` functions accept filters for adjacent entities with `None`
defaults — they double as broader queries when those filters are supplied
alone. For example, `differential_expression_by_gene(experiment_ids=[exp_id],
limit=None)` (with `locus_tags` left at default `None`) returns every DE row
for an experiment; the locus-tag set is one set-comprehension away, with no
Cypher required.

**Default approach:** before writing Cypher, inspect the existing API
signatures —
```python
import inspect
from multiomics_explorer import differential_expression_by_gene
print(inspect.signature(differential_expression_by_gene))
```
Look for `_by_X` functions that accept `experiment_ids`, `organism`, or
other adjacent-entity filters at `None` default. Reach for `run_cypher`
only when the question genuinely requires relationship traversals or
aggregations the API doesn't expose.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `uv run --directory /path/to/multiomics_explorer script.py` | Run from the template repo root — the explorer is in this project's venv (see above). |
| Guessing column names (`product`, `is_significant`) | Test with `result["results"][0].keys()` first (pre-script checklist). |
| Hand-flattening nested fields, then `.to_csv()` breaks | Use `to_dataframe(result)` — handles all flattening; see `docs://guide/python_api`. |
| Setting an arbitrarily high `limit=10000` | Use `limit=None` to get all results without guessing. |
| Writing raw `run_cypher` when an API function would cover it | Inspect `_by_X` signatures first (see above). |
| Treating `not_known` cells as "not measured" | `not_known` may mean "measured but not significant" — check `groups_tested_not_responded` for genes confirmed tested with no response, and `list_experiments` for the treatment type's `table_scope`. See [anti-hallucination.md — 4.4](anti-hallucination.md#44-measurement-failure-vs-biological-absence). |
| Extracting with `verbose=True` but not joining `product`/`gene_category` into gene-level outputs | Join metadata immediately — don't defer annotation to a separate step. Unnamed genes in signature CSVs are opaque. |
| Not checking for `timepoint=single` or null after extraction | After extraction, explicitly check for experiments with single/null timepoints and confirm they're handled correctly in downstream scripts (plotting, groupby). |
