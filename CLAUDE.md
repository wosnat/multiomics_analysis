# CLAUDE.md

## What this repo is

Your working copy of the **multiomics research template** — a clean starting
point for KG-backed research in Claude Code. It carries the research skills and
the MCP wiring; `uv sync` pulls the explorer tools into the local venv. Your
analyses live in `analyses/` in this clone.

This is the **consumer** side of the multiomics KG. The MCP tools themselves are
built in the sibling `multiomics_explorer` package (installed via `uv sync`, not
edited here).

## Layout

```
.claude/skills/research-methodology/   # Domain rules + the Plan→Run research arc (reference skill)
.claude/skills/recipes/                # On-demand analysis protocols land here as methods are formalized (none yet)
.mcp.json                              # Registers the multiomics-kg MCP server (uv run)
.env / .env.example                    # KG credentials (gitignored; copy the example)
hooks/                                 # Usage-logging hook (writes into usage/)
scripts/preflight.sh                   # DOA gate: version triple + KG contract + API smoke
analyses/                              # YOUR research output (one dir per analysis)
usage/                                 # Usage logs (committed — ride along with your pushes)
VERSION / CHANGELOG.md                 # Template version + history
```

## Getting started

See [README.md](README.md): fork → clone → `uv sync` → set credentials →
`./scripts/preflight.sh` → start an analysis. Run preflight green before opening
a research chat.

## Research methodology

**Load the `research-methodology` skill BEFORE invoking
`superpowers:brainstorming` for the Plan phase of an analysis.** It contains the
KG usage rules, gene-identity rules, anti-hallucination patterns,
scripts-over-chat-reasoning, and the Plan→Run research arc. Loading after the
plan is committed means retrofitting.

### The research arc: Plan, then Run

Every analysis is two phases:

**Plan** — one grounded `superpowers:brainstorming` conversation converging on
`proposal.md` (one commit):
- **Question** — user prompt + clarifying questions → locked question
- **KG entries** — relevant publications, experiments, organisms, data types,
  enumerated from the KG
- **Framing** — enumerated concretely: hypothesis, approach, statistics plan (the
  specific test or a reasoned "none"), and a named validation set (check
  genes/pathways with expected behavior)

**Run** — three milestones, each in its own folder, one commit each:
- **methods** — ad-hoc Python module implementing the approach the proposal
  committed to; toy-tested (`superpowers:test-driven-development`)
- **analysis** — run the method; produce scored outputs, figures, tables
- **evaluation** — assess against the framing; harvest caveats; finalize paper

`proposal.md` is the plan (locked at the end of the Plan phase). The Run
milestones execute against it. The Plan phase collapses onto brainstorming; the
Run phase is the project's own iterate loop (it is not `executing-plans`, which
assumes a locked, pre-specified plan).

### Run-milestone rhythm: co-define → do → show → explore → decide

Each Run milestone advances through **co-define → do → show → explore → decide**,
with two researcher gates: agreement at **co-define** (before the work) and
approval at **decide** (after it). The **decide** phase produces a minimal
`notebook.md` checklist and pauses for explicit researcher approval before
committing. Execution (KG queries, scripts) is delegated to a coding subagent
(`superpowers:subagent-driven-development`) that returns artifacts, not
conclusions; the main thread owns `notebook.md` and all judgment. See
`.claude/skills/research-methodology/references/step-protocol.md` for commit
timing, the decide-gate checklist, hard gates, and the delegation rules.

### Just-in-time formalization, with enumeration

Terms, predictions, metrics, stability checks, decisions, and caveats enter the
analysis **only when the data demands them** — but within what the plan *does*
commit to, be concrete (a vague-but-approved plan forces redos). If you find
yourself listing things the analysis might need before the data has arrived, stop.

On-demand tools that remain available: `superpowers:verification-before-completion`,
`superpowers:systematic-debugging`, `superpowers:requesting-code-review`, and the
`critical-review` skill — a fresh-context critic that challenges a claim-bearing
artifact against its own files (automatic on the proposal before the Run phase,
interpretation-only; at the analysis milestone with a data-integrity +
interpretation lens; and at the evaluation milestone with interpretation only; on
demand at any point).

## MCP server & credentials

The `multiomics-kg` MCP server runs via `uv run multiomics-kg-mcp` (see
`.mcp.json`) from the repo root, so the explorer reads KG credentials from the
gitignored `.env` at the repo root. The server requires the lab Neo4j KG to be
reachable (operator-provided URI + credentials). Run `./scripts/preflight.sh`
to confirm before starting.

## Usage logging

The hook in `hooks/log-mcp-usage.sh` appends one JSON line per MCP call to
`usage/multiomics-kg-usage.jsonl` **inside this repo** (un-ignored). Commit
`usage/` alongside your per-milestone analysis commits — the logs help improve the
tools. Forks are public; see the README before you start.
