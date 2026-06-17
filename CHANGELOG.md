# Changelog

All notable changes to the `multiomics_research_template` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

The **version triple** a tester runs — template / explorer / KG — is printed by
`./scripts/preflight.sh`. This changelog covers the **template** only; the
explorer pin lives in `pyproject.toml` and the KG version comes from
`kg_release_info`.

## [Unreleased]

### Changed
- Pinned to the latest knowledge-graph tools (explorer v0.1.0-alpha.4) — run
  `uv sync` after pulling. Fixes a result-flattening bug: queries that mix
  different `gene_derived_metrics` kinds no longer silently drop the scalar
  `value` column when converting tool output to a dataframe.

### Fixed
- Preflight no longer crashes on Windows when printing its success line — the
  Python check block now forces UTF-8 output so the ✓/⚠ status glyphs render on
  cp1252 consoles instead of raising `UnicodeEncodeError` after all checks pass.

## [0.1.0-alpha.2] — 2026-06-16

First update after the initial clone target, harvesting lessons from the first
two dogfood analyses (P-acquisition capacity in Prochlorococcus ecotypes;
motility regulation in an Alteromonas coculture).

### Added
- Preflight now reports which KG deployment you're connected to and warns
  (without blocking) if it isn't the production KG — so you can't unknowingly
  run an analysis against a staging or alpha database. Set `EXPECTED_KG_ROLE`
  if you mean to target a non-production KG.
- Preflight checks that the required research plugin is enabled and tells you
  how to install it if it's missing, instead of failing partway into step 1.
- Research-methodology guidance harvested from the first real analyses:
  - **Co-define each step before doing it.** The flow now opens with a
    plain-language proposal you agree to (a `co-define` phase + GATE 0), so you
    shape each step rather than reacting to finished work.
  - **Reach for the highest-level tool first** (Rule 5) — don't hand-roll or
    re-wrap analysis the package already ships (e.g. call `pathway_enrichment`
    rather than rebuilding Fisher ORA).
  - **Plain language with the researcher** (Rule 9) — no internal codes,
    step-IDs, or undefined jargon in conversation.
  - **Direction (up/down) claims need a present sign** (anti-hallucination 3.4)
    — check the all-gene log2FC sign distribution before comparing direction; a
    table can read all-positive because the sign was lost, not because biology
    went one way.
  - **Reopen path** — when a later step's data contradicts an already-locked
    earlier step, edit the lock instead of papering over it; locks are
    provisional until their data has been pulled.

### Changed
- Pinned to the latest knowledge-graph tools (explorer v0.1.0-alpha.3) — run
  `uv sync` after pulling. Adds new lookups (finding the genes and pathways a
  publication discusses) plus two fixes that bit the first dogfood:
  genome-only and metabolomics-only strains now resolve in the single-organism
  tools (e.g. `genes_by_ontology`) instead of being wrongly rejected, and gene
  lookups no longer error on genes that have no expression data.
- A typical analysis now runs without a permission prompt at nearly every step:
  the full set of read-only KG tools is pre-approved out of the box.
- A fresh clone no longer needs a manual plugin install — the research plugin is
  enabled automatically when you trust the workspace.

### Fixed
- Corrected the per-timepoint and pathway-background gene-count guidance in the
  research methodology so it points at the real data fields (counts that were
  attributed to a field name that doesn't exist).
- Usage logging no longer fails on machines without `jq` installed.
- The setup instructions use a placeholder KG address instead of a hardcoded one.

## [0.1.0-alpha.1] — 2026-06-10

Initial alpha template — clean clone target for lab testers.

### Added
- Research skills (`research-methodology` + recipes) under `.claude/skills/`,
  auto-loading on workspace trust (no plugin install).
- `.mcp.json` registering the `multiomics-kg` MCP server via `uv run` (creds via `.env`).
- `pyproject.toml` pinning the explorer to `v0.1.0-alpha.1` via git tag.
- `scripts/preflight.sh` — DOA gate: version triple, KG compatibility contract,
  Python API smoke call, and staleness check.
- Usage-logging hook writing JSONL into the repo's `usage/` (committed, attributable per fork).
- Tester onboarding `README.md`, `.env.example`, and an empty `analyses/` scaffold.
