---
name: critical-review
description: Use at the decide phase of research step 5 (analyze) and step 6 (evaluate) — and on demand on any step — to get an adversarial second opinion before the researcher sees the step. Dispatches a fresh-context critic that re-checks the step's own claims against its own data files. Step 5 gets a data-integrity + interpretation pass; step 6 gets interpretation only. The critic reviews only that step's files; earlier steps are trusted inputs, not re-audited.
---

# Critical review

Dispatch a fresh-context critic to challenge a research step **before** it is
presented at the decide gate. The critic never sees your session history — it
reads the step's artifacts cold, so it cannot inherit the narrative you anchored
on while doing the work. That detachment is the point: the failure modes the
methodology keeps hitting (a heatmap narrated "all 5 are UP" when the data file
says otherwise; a difference-of-trajectories narrated as "coculture vs axenic"
when each arm is starvation-vs-its-own-baseline) survive precisely because the
author is committed to the story. A reviewer reading only the data files is not.

This does not replace the researcher's decide-gate approval — it sharpens it.
The critic's findings, where any exist, become part of the state you present.

## Keep it light — three rules that bound the cost

1. **Match the lens to what the step produces.** Don't run every dimension on
   every step.
2. **Review only this step's own files.** Earlier steps already passed their own
   review — treat their outputs as trusted inputs, not as things to re-audit.
3. **Write an artifact only when there are findings.** A clean step gets one line
   in `notebook.md`, not a file.

## When it runs, and with which lens

**Step 5 — Analyze (automatic; the one heavy gate).** This is where computed
results first appear, so it gets the full pass: **data-integrity + interpretation**.
The data-integrity half is what pays off here — it opens the CSVs and checks the
signs, counts, truncation, and conflation that the narrative glosses.

The pass is point-in-time, but step 5 often keeps growing during decide (the
researcher asks for follow-on analyses, new scripts and claims land after the
critic already ran). **If a step's computed claims materially expand after its
critic pass** — new analyses, new data files, new conclusions added during decide
— **re-run the critic over the delta before closing the step.** Tell the
re-dispatch which prior files are already-reviewed (list them as trusted inputs)
so it reviews only the new work, not the whole step again.

**Step 6 — Evaluate (automatic; light).** Step 6 produces conclusions, not new
computation, so a data-integrity sweep has little to bite. Run **interpretation
only**: is each conclusion earned by step 5's results? are caveats honest? is
anything over-claimed, causal-from-correlational, or compared across platforms?
Step 6 reads step 5's outputs as **trusted evidence** — it judges whether the
conclusions follow from them; it does not re-open step 5's files hunting for new
data defects (step 5's review already did that).

**Step 3 — Framing (on demand; interpretation only).** Few data claims live here,
so it is not automatic — and its lens is **interpretation only** (no data files to
integrity-check; the critic weighs controls, testability, and confounders). Steps
1–3 are the locked proposal, so a flawed framing propagates into 4–6 and is
expensive to unwind. Invoke it when the framing rests on a judgment call that is
not self-evidently sound: a **non-obvious combining key** (e.g. mapping disjoint
strains onto shared ortholog groups), a **derived or constructed comparison**, or
**controls whose validity is not obvious** (is the positive control really
independent? is the negative control the contrast it is labelled as?).

**Any step, on demand.** A step-2 scoping pass that surfaced a surprising pattern,
or a redo you want re-checked, can be reviewed at will.

**Not run by a subagent:** routine **methodology compliance** (locus tags present,
computations in scripts, results tabled not paraphrased, decide-gate checklist
populated). These are mechanical self-checks — they belong in the author's
decide-gate checklist ([step-protocol.md](../research-methodology/references/step-protocol.md)),
not a fresh-context dispatch.

## How to dispatch

**1. Identify the step folder and analysis root** (e.g.
`analyses/<name>/5_analyze/` under `analyses/<name>/`).

**2. Dispatch a `general-purpose` subagent**, filling the template at
[critical-reviewer.md](critical-reviewer.md).

Placeholders:
- `{ANALYSIS_ROOT}` — path to the analysis directory
- `{STEP_FOLDER}` — path to the step folder being reviewed (the **only** files in
  review scope)
- `{STEP_NAME}` — which step (e.g. "Step 5 — Analyze")
- `{STEP_INTENT}` — one or two plain-language sentences on what this step set out
  to do and the main judgment calls it made (the co-define agreement)
- `{REVIEW_LENS}` — which dimensions to apply: `data-integrity + interpretation`
  for step 5; `interpretation only` for step 6 and for on-demand step-3 framing
  reviews; for other on-demand runs, choose by what the step produced (data files
  → include data-integrity; conclusions only → interpretation only)
- `{TRUSTED_INPUTS}` — prior-step output files this step builds on, which the
  critic reads as evidence but does **not** re-audit (e.g. step 5's data/ for a
  step-6 review). Empty for step 5.

**3. Handle the result by what it found:**
- **Findings exist** → write the critic's findings verbatim to
  `{STEP_FOLDER}/critical_review.md`, each with your **disposition**: fixed (what
  changed), disputed (why the critic is wrong, with the file-and-number that
  proves it), or deferred (why it can wait). Commit it with the step.
- **Clean** → no file. Add one line to the **Decide section** of `notebook.md`:
  `Critical review: clean (data-integrity + interpretation)` or `(interpretation)`
  — so the clean verdict sits with the decide-gate checklist, not floating elsewhere.

**4. Act before presenting:**
- **Blocker** — must be resolved (fixed or disputed with a specific data
  citation, not "I'm confident") before the step closes.
- **Concern** — address or explicitly defer with a reason.
- **Note** — record; fix if cheap.
- **Push back when the critic is wrong.** It read the artifacts cold and may have
  missed context — but disputing requires a file-and-number, not confidence.

**5. Present to the researcher** alongside the decide-gate state: the
`critical_review.md` with your dispositions (or the one-line clean note).

## What the critic is told NOT to do

- **Not to review anything outside `{STEP_FOLDER}`.** Trusted inputs are read for
  evidence, never re-audited.
- **Not to redo the analysis.** It spot-checks the step's claims against the
  step's files; it does not re-run the method.
- **Not to manufacture findings.** Every finding cites a specific file, the
  literal column name, and the number. "Unverified — check X" beats a confident
  guess. A clean dimension is a valid verdict.
- **Not to rewrite anything.** It reports; the author dispositions.

## Red flags

**Never:**
- Skip the step-5 review because "the result is obvious."
- Close a step with an unresolved Blocker.
- Re-audit an already-reviewed earlier step as part of a later step's review.
- Let the critic's confidence substitute for the data — a refutation without a
  file-and-number citation is itself a finding to dispute.

See the template at [critical-reviewer.md](critical-reviewer.md).
