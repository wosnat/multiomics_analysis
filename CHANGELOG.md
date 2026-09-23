# Changelog

All notable changes to the `multiomics_research_template` are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
this project adheres to [Semantic Versioning](https://semver.org/).

The **version triple** a tester runs — template / explorer / KG — is printed by
`./scripts/preflight.sh`. This changelog covers the **template** only; the
explorer pin lives in `pyproject.toml` and the KG version comes from
`kg_release_info`.

## [Unreleased]

## [0.2.0-alpha.1] — 2026-09-15

Second dogfood harvest, carried in from the consumer clone that ran the arc end
to end (which organic carbon compounds *Alteromonas* takes up in coculture with
*Prochlorococcus*). Minor bump rather than patch: the analysis folder layout
changes, which is breaking for anyone mid-analysis — existing analyses keep
their numbered structure as git history; the new arc applies to new analyses.
Ships alongside KG `0.1.0-alpha.7` and explorer `v0.1.0-alpha.5`.

### Changed
- **Research methodology restructured from a 6-step flow into a two-phase arc:
  Plan → Run.** The Plan phase is one grounded `superpowers:brainstorming`
  conversation converging on a single `proposal.md` (question + KG entries +
  *enumerated* framing — hypothesis, approach, an explicit statistics decision,
  and a named validation set), committed once. The Run phase is three milestones
  (`methods/` → `analysis/` → `evaluation/`, one commit each) advancing through
  `co-define → do → show → explore → decide`. The old `1_question/` … `6_evaluate/`
  numbered folders are replaced by `proposal.md` + the three named milestone
  folders. Execution (KG queries, scripts) is delegated to a coding subagent
  (`superpowers:subagent-driven-development`) that returns artifacts, not
  conclusions; the main thread owns `notebook.md` and all judgment. The hard
  gates were re-lettered (GATE A–E); critical review now runs on the proposal
  and at the analysis and evaluation milestones.
- **The arc hardened by its first full dogfood.** The four places it fell short
  were fixed:
  - **The methods milestone now gets an automatic critical review whenever it
    produces a data file** later milestones consume — a parts list, a curated
    candidate set, a classification table. Such a file carries claims (substrate
    labels, confidence flags, class assignments) that every downstream number
    inherits, and later milestones read it as a trusted input, so nothing else
    re-checks it. Run on demand in the dogfood, that review found a regulatory
    protein sitting in the candidate set as a confident sugar importer, plus a
    gene count cited from the KG that was 30% high and had already reached the
    paper. A methods milestone that only produces a tested function still gets
    the review only on request.
  - **A milestone that keeps producing after its review gets a second,
    delta-only pass.** Exploration happens *after* the critic by construction —
    you ask for follow-ups, and new figures and claims land during decide. In
    the dogfood the first pass came back clean and the delta pass over what
    followed caught a figure caption citing the wrong module's number, which had
    inverted the interpretation drawn from it.
  - **Toy tests use the real data's form, and one real row is spot-run by hand.**
    A green suite proves nothing when the fixture's values are the wrong type: in
    the dogfood, 27 passing tests hid a string-vs-boolean bug that would have
    collapsed every control class the moment the scorer met a real CSV.
  - **The decide gate now checks the friction log** — every friction the notebook
    points at actually exists, and a review finding that exposed a gap the plan
    didn't anticipate is logged as friction, not only as a fix. The log tends to
    go quiet in exactly the late milestones where the lessons are most expensive.
- **The framing now states what a MISS looks like, not only a HIT.** Every
  proposal names in advance the result that would signal "no real signal" and a
  pre-registered expected-negative class that should *not* score if the signal is
  genuine — so a true null and a noise result are distinguishable. Both dogfood
  runs' only clean single-module hits were expected-negatives, which is exactly
  what let a negative be read as real rather than as a failed method. A null is a
  valid outcome.
- Pinned to the latest knowledge-graph tools (explorer v0.1.0-alpha.5, paired
  with KG 0.1.0-alpha.7) — run `uv sync` after pulling. See the explorer and KG
  release notes for what the graph can now answer; the KG's `mcp_min_version`
  moves to `0.1.0a5`, so older explorer pins fail preflight's contract check.
  **Re-running an analysis written against an earlier KG will not reproduce its
  numbers.** In release QA, re-running the carbon-sources scripts against KG
  0.1.0-alpha.7 changed three things without any error:
  - **TCDB now carries many weak homology calls.** A default
    `genes_by_ontology(ontology="tcdb")` for *Alteromonas* HOT1A3 returns 1,139
    genes, up from 427; the additions are low-identity matches (median ~32%)
    that include regulators and sensor kinases. Pass a trust filter
    (`max_tier=2` gives 435; or `min_evidence_score=`) when a transporter set
    has to mean "transporter".
  - **TCDB genes attach at different levels, and family names are descriptive.**
    Code that matches TC numbers such as `3.A.1.10` in `term_name` finds nothing
    — read the number from `term_id` instead.
  - **Experiments can gain timepoints under the same ID.** The HOT1A3 coculture
    RNA-seq experiment now has days 18 and 31 alongside day 11 (day 11 is
    unchanged); a script that did not filter on `timepoint` now pulls three
    times the rows.
  Freeze KG-derived inputs to CSV (as the methodology already requires) and
  compare before trusting a re-run. Details: `docs/release-0.2.0-alpha.1-QA.md`.
- Pinned to explorer v0.1.0-alpha.4 (superseded above in the same release).
  Fixed a result-flattening bug: queries that mix different
  `gene_derived_metrics` kinds no longer silently drop the scalar `value` column
  when converting tool output to a dataframe.

### Added
- **`critical-review` skill** — a fresh-context critic subagent that re-checks a
  claim-bearing artifact against its own files, never against the author's
  narrative. Lens matched to the milestone (interpretation-only on the proposal
  and evaluation; data-integrity + interpretation on analysis and data-emitting
  methods), findings cited by file, column, and number; the author dispositions
  each one (fixed / disputed / deferred) before the researcher sees the milestone.
- `run_cypher` added to the pre-approved KG tools — the critic uses it to
  spot-check a single claim against the raw graph.
- `ontology_term_details` (new in explorer v0.1.0-alpha.5) added to the
  pre-approved KG tools, so it runs without a permission prompt like the rest.
- `docs/release-0.2.0-alpha.1-QA.md` — the release test run in a consumer clone:
  what was checked, what passed, and what was fixed before release.
- `docs/methodology-review-2026-08.md` — what the first full dogfood showed, with
  the evidence behind each of the changes above, plus four further findings that
  occurred only once and are being watched rather than acted on.
- `docs/methodology-test-brief.md` — the brief for the next round: whether the
  four changes earn their place and whether the four watch items recur.

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
