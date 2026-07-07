# Handoff — continue this analysis on another clone

*Transient note for the Plan→Run dogfood. Delete once the analysis resumes.*

## Where things stand (2026-07-07)

- **Branch:** `methodology/plan-run-arc`. On the other clone: `git fetch && git
  checkout methodology/plan-run-arc && git pull`.
- **Phase:** Plan phase **drafted, self-reviewed, and critic-vetted** (two critic
  passes; the second caught and fixed two scoring Blockers). **Committed** so it
  can be continued elsewhere — but **not yet formally approved**: the researcher
  has a few remaining questions about the plan before final sign-off and starting
  the Run phase.
- **Analysis dir:** `analyses/2026-07-06-alteromonas_coculture_carbon_sources/`
  - `proposal.md` — the plan (question, KG entries, framing, scoring, stats,
    confounders, 12 locked decisions)
  - `proposal_notebook.md` — grounding queries + decisions log
  - `proposal_critical_review.md` — both critic passes + dispositions
  - `paper.md` — Question + Background seeded
  - `gaps_and_friction.md`, `methodology_wins.md` — the dogfood logs

## What the analysis is (one breath)

Infer which organic carbon compounds *Alteromonas* uses in coculture with
*Prochlorococcus*, from which of its transporter→catabolism **modules** turn on
in coculture vs axenic, across strains (HOT1A3+MED4 primary; EZ55+MIT9312
corroboration). Unit = transport system; score = rank of KG `log2fc` →
up-percentile, module effect = max system percentile, matched-max permutation
null, BH/FDR per (experiment × timepoint), no pooling. See `proposal.md`.

## Prompt to paste into a fresh Claude Code session there

> I'm continuing the Plan→Run methodology dogfood on branch
> `methodology/plan-run-arc` (see `docs/methodology-test-brief.md`). Load the
> `research-methodology` skill, then read, in
> `analyses/2026-07-06-alteromonas_coculture_carbon_sources/`: `proposal.md`,
> `proposal_notebook.md`, `proposal_critical_review.md`, `gaps_and_friction.md`,
> and `methodology_wins.md`. The Plan phase is committed and critic-vetted but I
> still have a few questions about the plan before I approve it and we start the
> Run phase. Don't start any Run work yet — answer my questions first, then on my
> approval open the **methods** milestone by co-defining it with me. The methods
> milestone's first task is the **substrate-resolution audit** (per transporter:
> how finely can we resolve its substrate) plus confirming transport-system
> reconstruction on the full transporter set. Keep delegating execution to a
> coding subagent, log friction to `gaps_and_friction.md`, and keep the wins note.

## Open threads to expect from the researcher

- A few remaining plan questions (unspecified) before final approval.
- The earlier steer "use the stored rank property" — resolved to ranking the
  provided `log2fc` instead, because the stored directional `rank_up`/`rank_down`
  are significant-genes-only (see `proposal_critical_review.md` second pass). Worth
  reconfirming they're happy with that.
