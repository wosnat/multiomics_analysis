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
.claude/skills/research-methodology/   # Domain rules + the 6-step research flow (reference skill)
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
`superpowers:brainstorming` for step 1 of an analysis.** It contains the KG
usage rules, gene-identity rules, anti-hallucination patterns,
scripts-over-chat-reasoning, and the 6-step research flow. Loading after step 1
is committed means retrofitting.

### The 6-step flow

Every research analysis advances through 6 steps:

1. **Research question** — user prompt + clarifying questions → locked question
   (uses `superpowers:brainstorming` with overrides)
2. **KG entries** — relevant publications, experiments, organisms, data types
3. **Analysis framing** — selection + framing (hypothesis, controls, expected
   outcome) in KG terms
4. **Methods** — ad-hoc Python module using one item from step 3 as a driving example
5. **Analyze** — run the method; produce scored outputs, figures, tables
6. **Evaluate** — assess against framing; harvest caveats; finalize paper

Steps 1–3 form the research proposal (locked at end of step 3). Steps 4–6
execute against it.

### Intra-step rhythm: do → show → explore → decide

Every step advances through **do → show → explore → decide**. The **decide**
phase produces a minimal `notebook.md` checklist and pauses for explicit
researcher approval before committing. One commit per step, at decide close. See
`.claude/skills/research-methodology/references/step-protocol.md` for commit
timing, the decide-gate checklist, and hard gates.

### Just-in-time formalization

Terms, predictions, metrics, stability checks, decisions, and caveats enter the
analysis **only when the data demands them**. Nothing is enumerated in advance
"just in case." If you find yourself listing things the analysis might need
before the data has arrived, stop.

On-demand tools that remain available: `superpowers:brainstorming` (step 1),
`superpowers:verification-before-completion`, `superpowers:systematic-debugging`,
`superpowers:requesting-code-review`, and the `critical-review` skill — a
fresh-context critic that challenges a step's claims against its data files
(automatic in the decide phase at steps 3/5/6; on demand on any step).

## MCP server & credentials

The `multiomics-kg` MCP server runs via `uv run multiomics-kg-mcp` (see
`.mcp.json`) from the repo root, so the explorer reads KG credentials from the
gitignored `.env` at the repo root. The server requires the lab Neo4j KG to be
reachable (operator-provided URI + credentials). Run `./scripts/preflight.sh`
to confirm before starting.

## Usage logging

The hook in `hooks/log-mcp-usage.sh` appends one JSON line per MCP call to
`usage/multiomics-kg-usage.jsonl` **inside this repo** (un-ignored). Commit
`usage/` alongside your per-step analysis commits — the logs help improve the
tools. Forks are public; see the README before you start.
