# Gaps and friction

Methodology, KG, and tooling friction encountered during this analysis.

## 2026-09-04 — preflight red against a dev KG (accepted)

`./scripts/preflight.sh` exits RED with "KG credentials are not set" because
every line in the repo-root `.env` is commented out. The KG is nonetheless
reachable: both the MCP server and `GraphConnection()` from the Python package
connect, and `kg_release_info` returns verdict `ok` with 17/17 schema asserts.
This analysis runs against a local development KG (release string `0.0.0-dev`,
built 2026-08-29, explorer `0.1.0a4`), which the researcher confirmed is the
intended target for now. `.env` was left untouched and the red preflight is
accepted rather than fixed. Results are tied to that dev build and should be
re-run before being quoted against a tagged release.

## 2026-09-04 — no typed tool enumerates every gene of an organism

The orthology family is entered either by gene batch (`gene_homologs`) or by
group id (`genes_by_homolog_group`). Neither takes "give me all genes of
organism X", and `list_organisms` reports only a `gene_count`. This analysis
works around it by entering from the group side: enumerate ortholog groups with
`search_homolog_groups`, then expand members with `genes_by_homolog_group`. The
workaround is sound here because a gene with no ortholog group cannot be a
cross-strain core marker by definition, so nothing in scope is lost.

## 2026-09-04 — the `genera` field does not match `OrganismTaxon.genus`

Ortholog groups carry a `genera` list and a `has_cross_genus_members` flag.
Group `eggnog:1GYAH@1129` reports `genera: ["Synechococcus"]` while its members
include Synechococcus PCC 7002 and Synechococcus WH8102, which the KG files
under the genera `Picosynechococcus` and `Parasynechococcus`. The group-side
`genera` field therefore reflects eggNOG's taxonomy, not the KG's. Organism
membership in this analysis is resolved through member organism names, never
through `genera`.

## 2026-09-04 — no habitat or environment property on OrganismTaxon

Selecting the marine strains could not be done from the KG alone. Organism nodes
carry taxonomy, capability rollups, and a `clade` string, but no habitat field.
`clade` is populated for exactly the five marine picocyanobacterial clades and
empty elsewhere, so it served as a proxy; the marine call itself is
`[interpretation]`, not `[KG]`.
