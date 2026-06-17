---
name: critical-review
description: Use at the decide phase of research steps 3 (framing), 5 (analyze), and 6 (evaluate) — and on demand whenever you want an adversarial second opinion on a step's findings. Dispatches a fresh-context critic that re-checks claims against the data files, challenges the science, and audits methodology compliance before the researcher sees the step.
---

# Critical review

Dispatch a fresh-context critic to challenge a research step **before** it is
presented at the decide gate. The critic never sees your session history — it
reads the step's artifacts cold, so it cannot inherit the narrative you anchored
on while doing the work. That detachment is the entire point: the failure modes
the methodology keeps hitting (a heatmap narrated "all 5 are UP" when the data
file says otherwise; a paper from a Goldenspike microarray compared by magnitude
to an RNA-seq Rockhopper run) survive precisely because the author is committed
to the story. A reviewer reading only the data files is not.

This does not replace the researcher's decide-gate approval — it sharpens it.
The critic's findings become part of the state you present to the researcher.

## When it runs

**Automatic** — inside the **decide** phase, after `notebook.md` and the
`paper.md` section are drafted but **before** you present state to the
researcher, for:

- **Step 3 — Analysis framing** (is the hypothesis testable as framed? are the
  controls real? does the selection match the question?)
- **Step 5 — Analyze** (do the scored outputs actually say what the narrative
  claims? truncation, paralog conflation, sign-loss, cross-study comparison?)
- **Step 6 — Evaluate** (are conclusions earned by the evidence? are caveats
  honest? is anything over-claimed?)

Steps 1, 2, and 4 do **not** trigger it automatically (a question, a KG scoping
pass, a single driving-example method rarely carry the over-claim risk). Invoke
it on demand on any step when you want a second opinion — e.g. a step-2 scoping
pass that surfaced a surprising pattern, or a redo you want re-checked.

## How to dispatch

**1. Identify the step folder and analysis root** (e.g.
`analyses/<name>/3_framing/` under `analyses/<name>/`).

**2. Dispatch a `general-purpose` subagent**, filling the template at
[critical-reviewer.md](critical-reviewer.md).

Placeholders:
- `{ANALYSIS_ROOT}` — path to the analysis directory
- `{STEP_FOLDER}` — path to the step folder being reviewed
- `{STEP_NAME}` — which step (e.g. "Step 3 — Analysis framing")
- `{STEP_INTENT}` — one or two plain-language sentences on what this step set out
  to do and the main judgment calls it made (the co-define agreement)

The critic returns structured findings tagged by **dimension**
(data-integrity / science / methodology) and **severity** (Blocker / Concern /
Note), each citing a specific file and number.

**3. Write the critique to `{STEP_FOLDER}/critical_review.md`** — the critic's
findings verbatim, then your **disposition** for each: fixed (what changed),
disputed (why the critic is wrong, with the data that proves it), or deferred
(why it can wait, e.g. it belongs to a later step). This file is committed with
the step.

**4. Act before presenting:**
- **Blocker** — must be resolved (fixed or disputed with evidence) before the
  step closes. A Blocker is a claim the data contradicts, a hallucination, or
  something that would mislead the researcher.
- **Concern** — address or explicitly defer with a reason.
- **Note** — record; fix if cheap.
- **Push back when the critic is wrong.** It read the artifacts cold and may
  have missed context. Disputing with a specific data citation is a valid
  disposition — but "I'm confident" is not. Show the file and number.

**5. Present the critique alongside the decide-gate state.** The researcher sees
the findings, your dispositions, and the resulting notebook/paper — and approves,
redirects, or asks for a redo.

## What the critic is told NOT to do

- **Not to redo the analysis.** It spot-checks claims against the existing data
  files and may run small verifying queries; it does not re-run the method.
- **Not to manufacture findings.** Every finding cites a specific file and
  number. When uncertain whether something is wrong, it says "unverified —
  check X", not "this is wrong."
- **Not to rewrite anything.** It reports; the author dispositions.

## Red flags

**Never:**
- Skip the review at steps 3/5/6 because "the result is obvious."
- Close a step with an unresolved Blocker.
- Silently drop a finding — every one gets a disposition in `critical_review.md`.
- Let the critic's confidence substitute for the data — a refutation without a
  file-and-number citation is itself a finding to dispute.

See the template at [critical-reviewer.md](critical-reviewer.md).
