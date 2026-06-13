# Template gaps & TODOs

Living feedback log from dogfooding the **multiomics research template**. One row
per gap found while using the template for real. Findings here are meant to flow
**upstream** into the template repo (and/or the explorer package), not to be
fixed only in this clone.

- **Status**: `open` · `in-progress` · `fixed` · `wontfix` · `needs-decision`
- **Where**: `template` (this repo's tracked files) · `explorer` (sibling package) · `kg` (release/deploy) · `docs`
- Started: 2026-06-11 · first dogfood run · template `0.1.0-alpha.1` / explorer `0.1.0a1` / KG `0.1.0-alpha.5`

---

## Open

> **Headline (first deliberate pass, 2026-06-11):** the template's documented
> step-1 flow can't run out of the box — it hard-depends on the `superpowers`
> plugin, which the template neither declares nor installs (**G2**). Everything
> else is smaller. **Static review complete (2026-06-12):** README, CLAUDE.md,
> `.claude/settings.json`, `research-methodology/SKILL.md` + all seven
> `references/*.md`, hooks, preflight, pyproject, .gitignore. The reference files
> are well-built and internally consistent; remaining gaps are smaller (G10–G12).
> Not yet done: dynamic gaps from actually running an analysis (needs G2 fixed),
> and verification of the explorer-contract claims in G10 (deferred — pending the
> explorer origin pull).
>
> **Upstream fix pass (2026-06-12):** G2–G12 fixed in the template repo (not this
> clone). Resolutions: **G2** — `superpowers` declared via `enabledPlugins` in
> `.claude/settings.json` (auto-enables on trust; official marketplace is a
> built-in default), README install note + manual fallback, and a preflight
> check 0.5 that goes RED if the plugin doesn't resolve. **G3** — Edit-path bug
> fixed *by removing* the rule entirely (a consumer template shouldn't grant
> itself write to its own reference skill). **G4** — allow-list expanded to all
> 39 read-only KG tools; `run_cypher` excluded. **G5** — leaked Bolt IP →
> `bolt://HOST:PORT`. **G6** — `pyproject` → `0.1.0a1` (VERSION canonical).
> **G7** — recipes docs softened. **G8** — usage hook guards missing `jq`.
> **G9** — clone `cd` note. **G11** — Category-5 anchors added (incl. one the
> log missed, in `step-protocol.md`). **G12** — `slug` = full dir name
> everywhere. Still open: **G1** (needs-decision) and **G10** (deferred).
>
> **Upgrade pass (2026-06-13):** explorer pulled to `v0.1.0-alpha.2` (0.1.0a2)
> against KG `0.1.0-alpha.6`; preflight green, `kg_release_info` ok (16/16). This
> unblocked the two remaining gaps. **G1** — decided & fixed: `production` is the
> desired `deployment_role`; preflight now echoes it and warns (non-blocking) on
> anything else. **G10** — no longer deferred: the explorer is now pulled, so the
> contract-symbol verification can run against the live `docs://` + package; the
> `discussed_by_publication` surface the note predicted is confirmed present (and
> allow-listed in `.claude/settings.json`). **G10 — done same day:** verified the
> full contract against explorer `0.1.0a2`; everything held except one drifted field
> name (`tp_gene_count` → `timepoints[].gene_count` / `distinct_gene_count`), now
> fixed in the methodology. **All gaps G1–G12 are now resolved.**
>
> **Runtime/plumbing pass (2026-06-13):** first dogfood that exercises the live
> runtime rather than static files. Preflight green; MCP transport
> (`kg_release_info` over MCP) returns `ok` 16/16; the usage hook fires on a real
> MCP call and writes well-formed JSONL. G1's role gate confirmed live (KG on the
> alpha port `17687` self-declares `production`, gate echoes it cleanly). One new
> gap: preflight's green rests only on the Python-API import path and never starts
> the MCP server or the hook (**G13**, needs-decision).

### G2 — `superpowers` plugin is a hard dependency but undeclared & uninstalled for the clone
- **Where**: template (`CLAUDE.md`, `SKILL.md`, `references/research-notebook.md`) · **severity: HIGH — blocks step 1**
- **Found**: skill-availability cross-check, first dogfood run
- **What**: CLAUDE.md and the methodology skill instruct loading
  `superpowers:brainstorming` for step 1 ("uses brainstorming with overrides"),
  and also name `superpowers:verification-before-completion`,
  `superpowers:systematic-debugging`, `superpowers:requesting-code-review`, and
  `superpowers:writing-plans` ("skip this"). None appear in this session's
  available skills. `installed_plugins.json` shows
  `superpowers@claude-plugins-official` v5.1.0 installed with **`scope: project`
  pinned to `/home/osnat/github/multiomics_explorer`** — the sibling explorer
  repo — not to this template clone. It's available when working in the explorer
  repo, invisible here. The plugin **is** published in the official Claude plugin
  marketplace (`claude-plugins-official`), so installing it is a one-liner — the
  template just never tells the tester to.
- **Impact**: A lab biologist who forks+clones the template fresh (the documented
  path) has no `superpowers` plugin. Step 1 as written cannot proceed; the 6-step
  flow stalls at the first gate. Single thing most likely to break a real tester.
- **Note**: `superpowers` IS published in the official `claude-plugins-official`
  marketplace, so this is fixable — the template just needs to declare/install it.
  Likely resolution (not yet decided/implemented): add a README install step +
  project-scope enablement, and a preflight assertion that fails RED if the
  required `superpowers:*` skills don't resolve. Removing/inlining is the
  alternative if zero-plugin-install is a hard requirement.
- **Status**: fixed (template, 2026-06-12)

### G3 — `Edit` permission path in `.claude/settings.json` likely doesn't match
- **Where**: template (`.claude/settings.json`) · severity: medium
- **What**: the rule is `Edit(/.claude/skills/research-methodology/**)` — a
  **single** leading slash. The absolute-path convention (per `~/.claude/settings.json`,
  which uses `Read(//home/osnat/...)`) is a **double** slash; project-relative
  rules have no leading slash. A single `/` is neither, so it probably fails to
  match the project file. Secondary question: should a *consumer* template grant
  itself write access to its own reference skill at all?
- **Proposed fix**: change to relative `Edit(.claude/skills/research-methodology/**)`
  (or drop the rule if write access isn't intended). Verify against current
  permission-matching semantics.
- **Status**: fixed (template, 2026-06-12)

### G4 — MCP allow-list covers only 6 of 40 KG tools (permission-prompt friction)
- **Where**: template (`.claude/settings.json`) · severity: medium
- **What**: `permissions.allow` pre-approves only `kg_release_info`,
  `gene_overview`, `gene_aa_sequence`, `differential_expression_by_ortholog`,
  `genes_by_homolog_group`, `search_homolog_groups`. The server exposes 40 tools.
  Core tools a real run hits — `resolve_gene`, `list_experiments`,
  `list_publications`, `differential_expression_by_gene`, `pathway_enrichment`,
  `cluster_enrichment`, etc. — are **not** listed, so the researcher gets a
  permission prompt on nearly every step. The chosen 6 look like an arbitrary
  leftover, not a principled read-only set.
- **Impact**: constant prompting during analysis; undercuts the "ask in plain
  English, Claude does the rest" promise for non-technical testers.
- **Proposed fix**: allow-list the full set of **read-only** KG tools (everything
  except `run_cypher`, reasonably gated as arbitrary-query); or document the
  subset. Consider generating the list from the server's tool manifest so it can't
  drift. (`/fewer-permission-prompts` could seed this.)
- **Status**: fixed (template, 2026-06-12)

### G5 — README hardcodes a real lab Bolt URI, contradicting its own no-drift principle
- **Where**: template (`README.md`) · severity: medium (info-exposure + drift)
- **What**: the credentials block shows `NEO4J_URI=bolt://132.75.249.47:17687` — a
  concrete internal IP — while `.env.example` correctly uses `bolt://HOST:PORT`.
  The README's own closing section says connection specifics "live in the KG
  connection guide, not here … so the instructions never drift," and it warns the
  repo is **public and indexable**. Hardcoding the IP violates both.
- **Proposed fix**: replace with the `.env.example` placeholder and point to the
  KG connection guide for the real value.
- **Status**: fixed (template, 2026-06-12)

### G6 — Version source-of-truth is split three ways
- **Where**: template (`pyproject.toml` vs `VERSION`) · severity: low
- **What**: `pyproject.toml` declares `project.version = "0.1.0"` (plain), while
  `VERSION` (read by preflight + the usage hook) is `0.1.0-alpha.1`, and the
  explorer pin tag is `v0.1.0-alpha.1`. Three strings, one disagreeing.
- **Proposed fix**: align `project.version` to `0.1.0a1`, or comment that it is
  intentionally unused (repo is explicitly not a buildable package) and `VERSION`
  is canonical.
- **Status**: fixed (template, 2026-06-12)

### G7 — `recipes` skill dir ships empty but is advertised
- **Where**: template (`.claude/skills/recipes/`) · severity: low
- **What**: the dir contains only `.gitkeep`, yet CLAUDE.md and the layout describe
  "recipes (one per method) — on-demand analysis protocols." No recipe ships.
  Expected for alpha, but the docs promise a capability that isn't present.
- **Proposed fix**: ship one starter recipe, or soften the docs to "recipes land
  here as methods are formalized (none yet)."
- **Status**: fixed (template, 2026-06-12)

### G8 — Usage hook hard-depends on `jq` under `set -euo pipefail`
- **Where**: template (`hooks/log-mcp-usage.sh`) · severity: low
- **What**: the hook pipes every MCP event through `jq`; with `set -euo pipefail`
  and no `jq` presence check, a machine without `jq` fails the hook on every KG
  call. The README prerequisites (VS Code, Claude Code, git, uv, GitHub) omit `jq`.
- **Proposed fix**: guard with `command -v jq || exit 0` (degrade silently) and/or
  add `jq` to the prerequisites list.
- **Status**: fixed (template, 2026-06-12)

### G9 — README clone step assumes the directory name
- **Where**: template (`README.md` §1) · severity: low
- **What**: `git clone <your-fork-url> && cd multiomics_research_template`. Forks
  usually keep the upstream name so this often works, but if the fork is renamed
  (this clone is `multiomics_analysis`), the `cd` target is wrong.
- **Proposed fix**: `cd` into the directory `git clone` created, or note "the
  folder name matches your fork."
- **Status**: fixed (template, 2026-06-12)

### G10 — Explorer-contract claims in the methodology need verification against explorer latest
- **Where**: template (`references/kg-rules.md`, `python-api-guide.md`, `statistical-rigor.md`, `anti-hallucination.md`) · severity: unknown until verified · **status: deferred (pending origin pull)**
- **What**: the reference files name a number of explorer Python-API symbols, MCP
  response fields, and `docs://` resources. These are *correctly* delegated (the
  files say the contract is explorer-owned and served at `docs://guide/python_api`),
  but the specific names must be confirmed to exist/match in explorer latest before
  the template ships — otherwise the methodology points testers at symbols that
  drifted. This is a **verification TODO, not a confirmed bug.** Per session
  decision, deferred until the explorer is pulled from origin. Symbols to check:
  - **Python API utilities** (`kg-rules.md`, `python-api-guide.md`):
    `gene_response_profile`, `response_matrix()`, `gene_set_compare()`,
    `to_dataframe()`, `differential_expression_by_gene` (+ its `experiment_ids`/
    `locus_tags=None` broadening behavior), top-level import surface.
  - **Enrichment building blocks** (`statistical-rigor.md`): `de_enrichment_inputs`,
    `cluster_enrichment_inputs`, `fisher_ora`, `signed_enrichment_score`,
    `EnrichmentResult`.
  - **MCP response fields / semantics** (`anti-hallucination.md`,
    `python-api-guide.md`): `tp_gene_count` vs `gene_count`,
    `groups_tested_not_responded`, `not_known` / tested-absent rows, `table_scope`,
    `pathway_enrichment` accepting `term_ids`, `truncated` / `total_matching`.
  - **docs:// resources** referenced as authoritative: `docs://guide/python_api`,
    `docs://guide/conventions`, `docs://guide/start_here`, `docs://analysis/enrichment`,
    `docs://tools/{tool_name}`.
- **Note**: explorer `main` (c1d1a4d, "docs(mcp): correctness pass on outfacing
  docs") is 8 commits ahead of the pinned tag and adds a `discussed_by_publication`
  surface — so the docs the methodology points at have themselves just changed.
  Verify the template references against the *pulled* explorer, not the stale pin.
- **Verification (2026-06-13, against explorer 0.1.0a2 + KG 0.1.0-alpha.6):**
  Ran the full checklist against the installed package (import/signature
  introspection), the live `docs://` resources, and live tool calls.
  - **Python API (10/10 present)**: `gene_response_profile`, `response_matrix`,
    `gene_set_compare`, `to_dataframe`, `differential_expression_by_gene`,
    `de_enrichment_inputs`, `cluster_enrichment_inputs`, `fisher_ora`,
    `signed_enrichment_score`, `EnrichmentResult` — all importable top-level.
  - **Signatures hold**: `differential_expression_by_gene(organism, locus_tags=None,
    experiment_ids, …, limit=None)` (the `locus_tags=None` broadening is real);
    `pathway_enrichment(…, term_ids=None, …)` (confirms the documented correction —
    `term_ids` IS supported); `gene_response_profile(locus_tags, …, limit)`;
    `to_dataframe(result)`.
  - **docs:// (5/5 resolve)**: `guide/python_api`, `guide/conventions`,
    `guide/start_here`, `analysis/enrichment`, `tools/{tool_name}`.
  - **MCP response fields confirmed real**: `total_matching`/`truncated`/`returned`,
    `table_scope` (semantics match exactly), `groups_tested_not_responded`
    (gene_response_profile field), `not_known` (real `response_matrix` cell value;
    envelope field is `groups_not_known`).
  - **ONE DRIFT FOUND & FIXED**: `tp_gene_count` does not exist. Per-TP counts live
    in `timepoints[].gene_count`; the distinct-gene denominator for detection-power /
    pathway-background sizing is the top-level `distinct_gene_count`. Cumulative
    top-level `gene_count` claim was correct. Ironically the stale field name sat
    inside anti-hallucination §5.3 ("Field semantics from memory") itself — corrected
    there (lines ~359, ~364) and in `research-notebook.md` (~147).
- **Status**: fixed (template, 2026-06-13)

### G11 — Several cross-reference links omit their anchor fragment
- **Where**: template (`references/research-notebook.md`, `artifacts.md`) · severity: low
- **What**: links that name a specific section resolve only to the file top, not
  the section, because the `#anchor` is missing. Examples:
  `research-notebook.md` lines 59, 104, 119, 147 (all `[anti-hallucination.md —
  Category 5.x](anti-hallucination.md)` with no `#`), and `artifacts.md` line 170.
  Anchors that *are* specified elsewhere (e.g. SKILL.md → `#26-...`, kg-rules →
  `#51-...`) resolve correctly, so it's an omission, not a broken-anchor pattern.
- **Proposed fix**: add the section anchors (`#category-5-...`, `#52-...`, etc.).
- **Status**: fixed (template, 2026-06-12)

### G12 — "slug" is used with two different meanings
- **Where**: template (`references/artifacts.md` vs `research-notebook.md`) · severity: low
- **What**: `artifacts.md` line 34 writes `analyses/YYYY-MM-DD-<slug>/` (slug = the
  descriptor only), but line 54 defines "Slug format: `YYYY-MM-DD-<descriptor>`"
  (slug = the whole dir name), and `research-notebook.md` uses `analyses/<slug>/`
  (slug = whole dir name). The term flips between "the descriptor" and "the full
  directory name," which can confuse scaffold naming.
- **Proposed fix**: pick one definition (recommend slug = full `YYYY-MM-DD-descriptor`
  dir name) and use it consistently.
- **Status**: fixed (template, 2026-06-12)

### G1 — Preflight can't tell which release/container the Bolt URI points at
- **Where**: template (`scripts/preflight.sh`) · severity: low-medium
- **Found**: setup verification, first dogfood run
- **What**: Three Neo4j containers run side by side — `deploy` (prod, `7474/7687`),
  `alpha-deploy` (`17474/17687`), `staging-deploy` (`27474/27687`) — all carrying the
  same schema shape. Preflight asserts version-compat + a round-trip, so it passes
  **identically** against any of the three. Nothing in the gate pins you to the
  *intended* release; the port→container→role mapping is a manual cross-check.
- **Impact**: A researcher could run a full analysis against prod or staging
  without preflight objecting. The version triple wouldn't necessarily reveal it.
- **Proposed fix**: optional. Either (a) add a soft assertion that the URI port
  matches an expected release (configurable, e.g. `EXPECTED_KG_ROLE=alpha`), or
  (b) have `kg_release_info` surface a deployment/role tag the gate can echo and
  check. Needs a decision on whether role-pinning belongs in the gate at all.
- **Decision (2026-06-13)**: `production` is the desired role; anything else must
  warn and be surfaced to the user. Both (a) and (b) landed together — KG
  `0.1.0-alpha.6`'s `kg_release_info` now returns `deployment_role`, and preflight
  echoes it in the version triple (`KG role <role> (expected: production)`) and
  emits a loud, **non-blocking** yellow warning when `deployment_role != production`.
  Expectation overridable via `EXPECTED_KG_ROLE` for intentional alpha/staging runs.
  Verified both paths: production → clean; forced mismatch → warns and still proceeds.
  Note: the current KG sits on port `17687` (alpha port in the legacy map) but
  self-declares role `production`, so the authoritative role tag — not the port —
  drives the gate.
- **Status**: fixed (template, 2026-06-13)

### G13 — Preflight green doesn't exercise the MCP server or the usage hook
- **Where**: template (`scripts/preflight.sh`) · severity: low
- **Found**: runtime/plumbing dogfood, 2026-06-13
- **What**: preflight's checks 1–3 run via `uv run python - <<PY` and import
  `multiomics_explorer` directly (`GraphConnection`, `gene_overview`, …). That
  validates the Python-API path, but an analysis chat reaches the KG through a
  *different* entry point — the MCP server `uv run multiomics-kg-mcp` (`.mcp.json`)
  — and every KG call is wrapped by the PostToolUse usage hook
  (`hooks/log-mcp-usage.sh`). Neither the MCP transport nor the hook is touched by
  the gate. The gate's closing line ("you're clear to start an analysis") therefore
  over-claims: it certifies the library, not the two pieces the researcher actually
  uses.
- **Impact**: a broken/mis-pinned console-script entry point, an MCP startup error,
  or a hook regression (e.g. the G8 `jq` guard removed, a bad `jq` filter, a
  `set -euo pipefail` trip) would all leave preflight **green** and only surface
  mid-analysis — exactly when a non-technical tester is least equipped to diagnose
  it. Today both paths work (verified this pass), so severity is low, but the gate
  gives false assurance about coverage it doesn't have.
- **Proposed fix** (needs-decision — does spinning the server belong in the gate?):
  (a) lightest — have preflight assert the `multiomics-kg-mcp` console script
  *resolves* (e.g. `uv run multiomics-kg-mcp --help` or an entry-point check),
  short of a full MCP handshake; (b) add a tiny hook self-test (feed a synthetic
  PostToolUse event JSON to `log-mcp-usage.sh` and assert one well-formed line
  lands in `usage/`), which also catches a missing `jq`; (c) leave as-is and just
  soften the closing line to "library round-trip OK" so it stops implying the MCP
  path was checked. (a)+(b) are cheap and offline; (c) is zero-cost honesty.
- **Status**: needs-decision

---

## Resolved

_(none yet)_
