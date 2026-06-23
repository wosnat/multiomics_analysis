# Step protocol

Each analysis step advances through the rhythm **co-define → do → show → explore → decide** (phase content defined in [research-notebook.md](research-notebook.md)). This document owns **when things happen and what gates enforce them**.

The **just-in-time formalization** principle applies throughout: terms, metrics, stability checks, decisions, and caveats enter the analysis only when the data demands them. Do not pre-specify framework inventories. See [research-notebook.md](research-notebook.md) for the full principle and its application to step 3 framing.

## Commit structure

**One commit per step**, at the end of the decide phase. The commit includes everything the step produced:

- `notebook.md` (narrative + decide-gate checklist)
- `scripts/`, `data/`, `figures/` (main + `qc_*` files)
- updates to `paper.md` (the step's synthesis section)
- updates to `gaps_and_friction.md` (if the step encountered friction)

No mid-step commits, no separate "do commit + decide commit" pattern. The decide phase is the atomic step boundary.

Step 1 is a special case: the commit includes both the scaffold (analysis folder, `paper.md` skeleton, `gaps_and_friction.md` header, `1_question/notebook.md`) and step 1's own outputs. See [artifacts.md](artifacts.md) for scaffold creation.

## Before starting a step

- Previous step's commit exists
- Previous step's `notebook.md` has the decide-gate checklist populated
- Previous step's `paper.md` section is populated

If any of these is missing, close the previous step first.

## "co-define" phase

Before doing any of the step's work, propose it to the researcher in plain language: what this step should produce, the main judgment calls you expect, and why. Let the researcher adjust the scope or approach. Begin the work only once you've agreed.

This is the front-end mirror of the decide gate: decide closes a step with researcher approval; co-define opens it with researcher agreement. The point is that the researcher shapes the work, not just reviews it afterward. No artifacts are produced here — it is a short conversation that sets the step's scope.

Default to co-defining every step. The researcher may wave through routine steps, but never skip co-define for a genuine judgment call (what to compare, how to define a gene set, which controls). Keep it in plain language — no internal step-IDs or undefined jargon (see [SKILL.md Rule 9](../SKILL.md)).

## "do" phase

Do the step's work — scope depends on the step:

- **Step 1:** clarifying dialogue with the researcher (see [research-notebook.md — Using brainstorming for step 1](research-notebook.md))
- **Steps 2, 4, 5:** write and run scripts; produce data and figures
- **Steps 3, 6:** select, validate, or evaluate; produce scripts + data + figures for the QC side; write prose for the framing or evaluation side

Outputs land wherever the step naturally produces them: a conversation lands in `notebook.md`; scripts land in `scripts/`; their outputs land in `data/` and `figures/`. QC artifacts use the `qc_` filename prefix (see [artifacts.md](artifacts.md)).

No commit yet. The step's outputs are uncommitted working-tree state until decide.

## "show" phase

Populate `notebook.md` with what was produced. Recommended sections (see [research-notebook.md](research-notebook.md) for full content):

- **Context** — what this step is for; what the prior step decided
- **What I did** — scripts run with their command-line invocation for non-trivial cases; KG queries issued
- **Results** — summary tables shown inline (as markdown tables, not prose paraphrases); links to full tables in `data/` and figures in `figures/`; cited publications resolved via `list_publications` (never from memory — see [anti-hallucination.md — Category 5](anti-hallucination.md#category-5-source-of-truth-verification-failures))

Summary tables in **Results** are the same tables presented to the researcher in chat — copied as markdown into the notebook, not paraphrased.

## "explore" phase

Investigate anomalies, surprises, or gaps:

- Ask follow-up clarifying questions (step 1)
- Add `qc_*.py` checks; run sensitivity analyses; cross-validate against controls (steps 2–6)

Capture anomalies worth flagging as **Surprises** in `notebook.md`. If a researcher question during this phase produces a data point or changes interpretation, both the prose and the data live in the notebook — the narrative IS the exploration record. No separate chat-capture section.

## "decide" phase

1. **Finalize `notebook.md`:**
   - Ensure Context / What I did / Results / Surprises are populated as applicable
   - Add **Decisions** section if any forks were taken (prose + date; see [research-notebook.md](research-notebook.md))
   - Write the **decide-gate checklist** at the end of notebook.md:
     - **Outputs produced** — filenames in `scripts/`, `data/`, `figures/`, with command lines for non-trivial scripts
     - **Results presented** — summary tables shown inline; links to full tables and figures generated this step
     - **QC gate** — what was checked → result (one line per check)
     - **Decisions made this step** — prose + date, if any; omit the section if none
     - **Advance rationale** — one line, why this step is ready to close

2. **Update `paper.md`:** write the synthesis paragraph (or figure inclusion, or methods sub-section) for the section this step populates — see [research-notebook.md — paper.md growth](research-notebook.md) for the section-to-step mapping.

3. **Append to `gaps_and_friction.md`** if friction was encountered this step (KG issues, MCP schema mismatches, methodology gaps, anti-hallucination corrections).

4. **Critical review (step 5 and step 6 — automatic; other steps on demand):** before presenting to the researcher, dispatch the fresh-context critic via the `critical-review` skill. It reviews **only this step's own files** (earlier steps are trusted inputs, not re-audited) with a lens matched to the step: **step 5** gets data-integrity + interpretation (the heavy gate, where computed results first appear); **step 6** gets interpretation only (it judges whether conclusions are earned by step 5's already-vetted results). Methodology compliance is not the critic's job — it lives in your decide-gate checklist below. If the critic finds anything, write its findings and your disposition for each to `{STEP_FOLDER}/critical_review.md` and resolve every Blocker (fix, or dispute with a specific data citation) before the step closes; if it comes back clean, add a one-line `Critical review: clean (<lens>)` to `notebook.md` and write no file. See [GATE 4](#gate-4-critical-review-at-the-steps-that-make-claims).

5. **Present state to researcher:** show the `notebook.md` content, the `paper.md` diff, any `gaps_and_friction.md` additions, and — where the review produced findings — `critical_review.md` with your dispositions. Wait for explicit approval or redirect.

6. **On approval, commit.** One commit, containing all of the step's changes (including `critical_review.md` where the review produced findings).

7. Begin next step (create its folder as needed — see [artifacts.md](artifacts.md) for progressive folder creation).

## Redo path

When the researcher says "redo step N with X":

1. **do:** update script or framing; rerun; regenerate outputs. New artifacts overwrite old in the step folder.
2. **show / explore:** new tables, figures, Results; update Surprises if changed.
3. **decide:** new decide-gate checklist, new `paper.md` synthesis, new `gaps_and_friction.md` entry if the redo surfaced friction. **New commit (never amend the previous).**

The previous commit remains in git history as the record of what was tried. The working-tree `notebook.md` is overwritten because it now describes what actually happened in the successful attempt — it is not a log of prior attempts.

If the redo invalidates downstream steps, the redo's `notebook.md` must list the downstream steps that consumed its outputs. The researcher decides whether to cascade the redo.

`gaps_and_friction.md` is append-only: redo friction entries accumulate.

## Reopen path (a data reveal reopens an upstream lock)

The redo path above handles "redo step N and cascade downstream." A different
case: while *executing* a later step, the data itself contradicts an assumption
baked into an **already-locked** earlier step (typically the step-1 question or
the step-3 framing). The locks are provisional until the data behind them has
actually been pulled — "locked at end of step 3" is not "frozen against what the
data turns out to be."

When this happens: **reopen the owning step, don't paper over it.** Edit that
step's `notebook.md` to record (a) the original lock, (b) the data reveal that
triggered the reopening, and (c) the evolved question/framing — then re-lock and
continue. Add a `gaps_and_friction.md` entry. This is distinct from the redo path
(which cascades *forward* from an invalidated step); here a downstream reveal
edits an *upstream* lock.

This is the partner of the just-in-time-formalization principle: look at the data
before fixing the framing, and let the framing follow the data when execution
surfaces something the lock assumed away.

**Real example (Alteromonas coculture analysis):** the step-1 question ("does
motility go up or down in coculture?") was reopened when step 2 revealed that
every usable coculture contrast runs in a medium with no added organic carbon —
reframing it around a carbon-provision hypothesis. The step-1 lock was edited
(original + evolved question + a decision), not silently replaced.

## Hard gates

### GATE 0: Co-define before doing

The first dogfood analysis executed an internal plan and surfaced finished work for review — the researcher reacted to results instead of shaping the step. **Do not start a step's work before proposing it in plain language and getting the researcher's agreement.** Co-define opens the step; decide closes it. (Routine steps may be waved through, but genuine judgment calls never are.)

### GATE 1: Step boundary

B1 and B2 partially wrote notebooks retroactively — exploration reasoning was lost and couldn't be verified against the actual data state at the time.

**Do not start step N+1 until step N is committed, including `notebook.md`, `paper.md` updates, and `gaps_and_friction.md` updates if applicable.**

### GATE 2: Researcher approval

B2's scope drift (decisions D5–D8 added mid-execution) slipped past because there was no atomic gate between "I finished some work" and "I'm advancing." The decide phase presents state to the researcher; the researcher approves, requests a redo, or redirects.

**Do not commit the step without explicit researcher approval of the decide-gate state.**

### GATE 3: Results presented, not paraphrased

Summary tables shown in chat must also appear as markdown tables in `notebook.md`. Prose paraphrases of numbers lose precision and are unreviewable.

**Do not close the step if the Results section in `notebook.md` is prose where a table belongs.**

### GATE 4: Critical review at the steps that make claims

Across analyses, wrong narratives survived because the author was anchored to
them — a control heatmap narrated "all 5 are UP" while the data file showed them
negative; a per-arm starvation contrast narrated as "coculture vs axenic"; a
control row double-counting pooled and per-timepoint genes. The author who wrote
the story cannot reliably see its holes; a fresh reader of the data files can.

**At step 5 (analyze) and step 6 (evaluate), do not present the step to the
researcher until the `critical-review` critic has run with the step's lens and
every Blocker it raised is resolved** — fixed, or disputed with a specific
file-and-number citation (not "I'm confident"). The critic reviews only that
step's own files; earlier steps are trusted inputs. Step 5 gets data-integrity +
interpretation; step 6 gets interpretation only. Where the critic finds anything,
the findings and your dispositions are committed with the step in
`critical_review.md`; a clean review is a one-line note in the **Decide section**
of `notebook.md`. Steps 1–4 do not require it (step 3 framing may be reviewed on
demand, interpretation-only, when it rests on a non-obvious judgment call — a
constructed combining key, a derived comparison, or non-self-evident controls).
Keep it light — see the three bounding rules in the
[critical-review skill](../../critical-review/SKILL.md).

**Re-review on expansion.** The critic pass is point-in-time. If a step's computed
claims **materially expand after its pass** — follow-on analyses, new scripts, new
conclusions added during decide — re-dispatch the critic over the delta before
closing, listing the already-reviewed files as trusted inputs so it reviews only
the new work. A long exploratory step can outgrow a single up-front gate.

## Git discipline

### Per-analysis .gitignore

Created during scaffolding (at start of step 1). Default:
```
# Large intermediate data reproducible from KG
# (list specific files here, not blanket patterns)
__pycache__/
```
Everything else tracked by default. Explicit entries with a comment explaining why.

### Scaffolding

Scaffolding and step 1 land in the same commit. Claude creates the scaffold during step 1's do phase, before the dialogue begins (see [artifacts.md — Scaffold creation](artifacts.md)). No separate scaffolding commit.

### Redo commits

Redo produces new commits, not amendments. The failed attempt's commit stays in history. Within the working tree, the step's `notebook.md` is overwritten to reflect the successful attempt.
