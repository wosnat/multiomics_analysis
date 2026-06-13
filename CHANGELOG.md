# Changelog

All notable changes to the `multiomics_research_template` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

The **version triple** a tester runs — template / explorer / KG — is printed by
`./scripts/preflight.sh`. This changelog covers the **template** only; the
explorer pin lives in `pyproject.toml` and the KG version comes from
`kg_release_info`.

## [Unreleased]

### Added
- Preflight now reports which KG deployment you're connected to and warns
  (without blocking) if it isn't the production KG — so you can't unknowingly
  run an analysis against a staging or alpha database. Set `EXPECTED_KG_ROLE`
  if you mean to target a non-production KG.
- Preflight checks that the required research plugin is enabled and tells you
  how to install it if it's missing, instead of failing partway into step 1.

### Changed
- Updated to the latest knowledge-graph tools — run `uv sync` after pulling.
  This adds new lookups, including finding the genes and pathways a publication
  discusses.
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
