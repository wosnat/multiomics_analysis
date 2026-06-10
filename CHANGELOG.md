# Changelog

All notable changes to the `multiomics_research_template` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

The **version triple** a tester runs — template / explorer / KG — is printed by
`./scripts/preflight.sh`. This changelog covers the **template** only; the
explorer pin lives in `pyproject.toml` and the KG version comes from
`kg_release_info`.

## [Unreleased]

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
