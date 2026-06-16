# Results dashboard

A repo-level, cross-analysis presentation layer over the work in `analyses/`. It is
an **additional interactive view**, not a replacement for the per-analysis papers and
static figures (which remain the source of record).

## View it

Open `dashboard/index.html` in any browser. No server needed; Plotly and DataTables
load from CDN (so an internet connection is needed the first time). The shortlist
table is sortable and searchable.

## Rebuild it

```
uv run python dashboard/build_dashboard.py
```

Reads each analysis's committed `data/*.csv` and regenerates `index.html`.

## Add the next analysis

The dashboard is built from a list of section builders in `build_dashboard.py`:

```python
SECTIONS = [selection_section, placeholder_characterization]
```

To add the characterization follow-on, write a `characterization_section()` that reads
its `data/*.csv` and returns a `Section`, then replace the placeholder in `SECTIONS`.
Existing sections are untouched.

## Current sections

- **Selection** — `analyses/2026-06-16-conserved_hypothetical_de`: conserved
  hypothetical families that are broadly / prominently differentially expressed.
  Breadth-vs-prominence scatter, the coverage-confound view, and the 85-family
  shortlist (14 core flagged ★).
- **Characterization** — placeholder for the follow-on analysis.
