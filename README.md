# Multi-omics research template (alpha)

A ready-to-use starting point for doing computational research on the lab's
multi-omics **knowledge graph** — without writing database queries or analysis
code yourself. The knowledge graph is the lab's integrated database for the
marine cyanobacterium *Prochlorococcus* and the heterotrophic bacterium
*Alteromonas*: their genes, gene expression measured across many experiments,
ortholog relationships, metabolites, and how these connect. You ask research
questions in plain English inside **Claude
Code** (an AI assistant that runs in the VS Code editor); it queries the
knowledge graph, runs the statistics, makes the figures, and writes up the
results following a rigorous, reproducible methodology built into this repo.

**Who this is for:** lab biologists. **No prior experience with VS Code, git,
GitHub, or the command line is assumed** — this guide walks you through the
one-time setup step by step. When something doesn't work, the lab operator (the
person who set up the knowledge graph) is your first port of call.

## What you'll actually do

1. Make your own copy of this template (a **fork**) and download it to your
   computer (a **clone**).
2. Point it at the lab's knowledge-graph database (one-time credentials).
3. Open it in VS Code and chat with Claude in plain English, e.g.
   *"What genes respond when MED4 is starved of nitrogen?"*
4. Claude does the querying, analysis, and write-up — saving everything into
   your copy as files you can revisit, share, and publish from.

You direct the research; Claude is the analyst. The methodology built into this
repo keeps the science honest: every claim is traced to the data, gene
identities aren't guessed, and statistics are done properly.

### A few terms you'll see

| Term | What it means here |
|---|---|
| **Knowledge graph (KG)** | The lab's multi-omics database — *Prochlorococcus* & *Alteromonas* genes, expression, orthologs, metabolites, and more. |
| **Claude Code** | Anthropic's AI coding assistant; runs inside VS Code. |
| **MCP server** | The bridge that lets Claude query the KG. This repo wires it up for you — you never configure it by hand. |
| **Repository ("repo")** | A project folder tracked by **git** (which records the history of your changes). This template is one. |
| **Fork / clone** | A *fork* is your own copy of the template on GitHub. A *clone* is that copy downloaded onto your laptop. |
| **`uv`** | A tool that sets up Python and installs the analysis software in one step. |

> **⚠ Your fork is public.** This is an open-science alpha: the template, all
> forks, your analyses, **and** your usage logs are public and indexable —
> including in-progress, unpublished work. Know this before you start. If a
> specific analysis must stay private, gitignore its directory locally; the
> default is public.

---

## One-time setup

### Install these first

You need the following installed once. The links go to official install
instructions for Mac, Windows, and Linux:

- **[VS Code](https://code.visualstudio.com/)** — the editor everything runs in
- **[Claude Code](https://claude.com/claude-code)** — the AI assistant (added to VS Code)
- **[git](https://git-scm.com/downloads)** — tracks and downloads your work
- **[uv](https://docs.astral.sh/uv/)** — installs Python 3.11+ and the analysis tools for you
- A free **[GitHub account](https://github.com/signup)** — to fork the template

> **New to the command line?** The steps below are commands you paste into a
> terminal. VS Code has one built in: **View → Terminal**. Open this folder in
> VS Code first, then paste each command into that terminal and press Enter.

You also need **lab-subnet (or VPN) access** to the KG box. Network details and
credentials come from the lab operator — ask them for the **KG connection
guide** (canonically `multiomics_biocypher_kg/docs/kg_mcp_guide.md`).

### 1. Fork, clone & install

Fork this repo on GitHub first (the **Fork** button, top-right of the repo
page). Then, in a terminal:

```bash
# Replace <your-fork-url> with the URL of YOUR fork (green "Code" button on your fork):
git clone <your-fork-url> && cd multiomics_research_template
git remote add upstream https://github.com/wosnat/multiomics_research_template.git   # lets you pull updates later
uv sync                       # installs the explorer tools + analysis libraries
```

### 2. Set KG credentials

Credentials come from the lab operator (see the **KG connection guide**).
**Never commit them** — the steps below keep them out of git automatically.

**Recommended — all platforms: a gitignored `.env` file in the repo root.**

```bash
cp .env.example .env     # makes your own .env; then open .env in VS Code and fill in:
#   NEO4J_URI=bolt://132.75.249.47:17687
#   NEO4J_USERNAME=explorer
#   NEO4J_PASSWORD=…
```

Claude reads `.env` automatically (the MCP server runs from this folder). This
works identically on Linux, Windows 11, and Remote-SSH.

<details>
<summary><b>Alternative — shell / OS environment</b> (if you'd rather not keep a creds file)</summary>

- **Linux:** `export NEO4J_*` in `~/.bashrc`, then launch VS Code from that
  terminal (`code .`) — a VS Code opened from the desktop icon won't inherit them.
- **Windows 11:** set them as User Environment Variables (PowerShell:
  `[Environment]::SetEnvironmentVariable("NEO4J_URI","…","User")`), then restart VS Code.
- **Windows 11 + Remote-SSH:** set them on the **remote** host (where the MCP
  runs), not on Windows — or just use the `.env` method, which is simplest here.

</details>

### 3. Open in Claude Code & trust the workspace

Open this folder in VS Code. When prompted, **trust the workspace** — this lets
the research skills load and the MCP server start. Confirm the `multiomics-kg`
server shows as connected by running `/mcp` in a Claude chat.

### 4. Preflight (the "is everything wired up?" check)

```bash
./scripts/preflight.sh        # checks versions + KG connection + a real query → green/red
```

**Green** = you're clear to start. **Red** = it tells you exactly what's wrong,
with a specific hint for the three common problems: credentials not set, not on
the lab subnet, or a version mismatch. Fix it before starting a research chat.

### 5. Start an analysis

Open a new Claude chat and ask your research question. The `research-methodology`
skill loads automatically and guides the work through a 6-step flow (question →
KG data → framing → methods → analysis → evaluation). Everything Claude produces
is saved under `analyses/` in **your** copy. Commit the `usage/` logs alongside
your analysis commits (they help improve the tools).

---

## Keeping up to date

```bash
git pull upstream main && uv sync     # preflight warns you when you're behind
```

The pull brings new skills and a possibly-updated explorer version; `uv sync`
installs it. Preflight verifies the two match.

---

**Connection specifics** — the lab Bolt URI, firewall/subnet checks, and
shared-credential handling — live in the **KG connection guide**, not here. This
README links to it rather than copying it, so the instructions never drift.
