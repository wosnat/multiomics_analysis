# Methods paper — agent-driven KG-backed research (the Plan→Run arc)

**What this is.** A methods paper describing the reusable workflow for doing
knowledge-graph-backed research with an AI coding agent — the **Plan→Run arc**
(`research-methodology` skill) — using the Alteromonas coculture carbon-sources
analysis (`analyses/2026-07-06-alteromonas_coculture_carbon_sources/`) as the
worked example.

**Scope.** The *method* is the contribution; the Alteromonas biology is the
illustration, not the result. The biological write-up lives separately in that
analysis's `paper.md`. Do not conflate the two.

**Framing.** Methods paper (the reusable workflow), not an experience report.
Honest about N: one analysis (two counting the prior dogfood) lets us *describe
and illustrate* the method, not *validate* it — the paper claims "here is the
method and a worked example," never "here is evidence it is better."

## How capture works (and doesn't gate the analysis)

- `capture.md` — running, timestamped log of process moments as they happen
  (co-define agreements, judgment calls, critic findings, friction, redos), each
  tagged with the paper section / figure it feeds. Seeded from the analysis's
  `methodology_wins.md`, `gaps_and_friction.md`, `proposal_critical_review.md`,
  and the live co-define exchanges.
- `draft.md` — the paper outline; sections drafted at each decide gate.
- `figures/` — figure drafts (mermaid source now; rendered later).

**This rides alongside the analysis and never gates it.** Capture-as-you-go is
lightweight logging + milestone figures, not a parallel writing project. If it
ever competes with the analysis for attention, the analysis wins.

## Discipline (inherited from the methodology it documents)

Describe before interpret; document what *actually* happened including dead ends,
the stale handoff, corrected wrong guesses, and the non-decisive expected outcome.
A methods paper that launders the process into a clean story is exactly the
failure the method guards against.
