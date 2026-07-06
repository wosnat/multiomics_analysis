# Methodology test brief — Plan→Run arc dogfood

**Purpose.** Dogfood the restructured `research-methodology` (the Plan→Run arc,
committed on branch `methodology/plan-run-arc`) by running one real analysis
through it and recording where the new structure helps or creaks. This is a
methodology test as much as a scientific one.

**Before you start (in the new chat):**

- Confirm you're on the right branch — `git branch --show-current` must read
  `methodology/plan-run-arc`, not `main`. On `main` the old 6-step methodology
  loads instead.
- Open with the research question. The `research-methodology` skill loads
  automatically and should walk the arc:
  - **Plan phase** — one `superpowers:brainstorming` conversation converging on
    `proposal.md` (question + KG entries + *enumerated* framing: hypothesis,
    approach, an explicit statistics decision, a named validation set). Closes on
    self-review → automatic interpretation-only proposal critic → your approval.
  - **Run phase** — `methods/` → `analysis/` → `evaluation/`, each advancing
    co-define → do → show → explore → decide, one commit each. Execution delegated
    to a coding subagent; the main thread owns `notebook.md` and all judgment.

**Watch-list — what we're testing (record answers as you go):**

1. Did the enumerated `proposal.md` let you poke holes in the plan *before*
   anything ran?
2. Did the proposal critic catch anything a vague plan would have hidden?
3. Did collapsing question + KG entries + framing into one conversation feel
   coherent, or cramped?
4. Did the coding-subagent delegation keep the main thread clean — or did the
   re-invoke exploration loop drag?
5. Did the main thread reliably catch data anomalies from the subagent's returned
   artifacts (not just trust its summary)?
6. Any redo caused by a plan that looked fine but wasn't? (the failure the whole
   restructure targets)

**Where to log:**

- **Friction** → `analyses/<slug>/gaps_and_friction.md` (as the methodology
  already prescribes).
- **Wins** (where the new structure actively helped vs. the old flow) → a short
  scratch note for this run; `gaps_and_friction.md` is a problem log and won't
  hold positive signal.

**After the run:** bring the friction notes + watch-list answers back to the
methodology chat; we fold what creaked into the next revision of the skill.
