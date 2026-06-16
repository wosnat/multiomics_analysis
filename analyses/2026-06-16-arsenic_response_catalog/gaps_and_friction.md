# Gaps and friction

Transitional log of methodology / KG / tooling friction encountered during this
analysis, distinct from decisions (which live in each step's `notebook.md`).
Append-only, prose entries with dates.

## 2026-06-16 — genes_by_ontology omits organism_name / annotation_quality

Rows from `genes_by_ontology` (even `verbose=True`) carry the matched term and the
gene's locus_tag/product but **not** `organism_name` or `annotation_quality`. A
catalogue that unions ontology hits with text hits therefore undercounts per-strain
breakdowns and loses the AQ field for ontology-only genes. Resolution: backfill the
authoritative per-gene fields with one `gene_details` call over the full locus-tag
union. Minor tooling gap; no result impact once backfilled.

## 2026-06-16 — "phosphorus or arsenic" parent terms leak phosphorus genes

GO/EC carry generic parent terms (e.g. *oxidoreductase activity, acting on phosphorus
or arsenic in donors*, `ec:1.20.-.-`) that are not arsenic-specific. Walking DOWN from
them via `genes_by_ontology` pulled 2 `ptxD` phosphonate dehydrogenases into an
arsenic catalogue. Lesson for any broad ontology-anchored search: parent terms that
name two elements/substrates are ambiguous; tag or exclude them rather than treating
their descendants as on-target. Handled here by `scope=broad` + transparent
`matched_terms`, and flagged in the paper.

## 2026-06-16 — OneDrive/Excel file lock blocked CSV write (Windows)

Writing `arsenic_gene_terms.csv` raised `PermissionError [Errno 13]` because the path
is under OneDrive-synced `Documents` and the file was open in Excel. Process note:
close spreadsheet viewers / let OneDrive settle before re-running a script that
overwrites its outputs. No code change.
