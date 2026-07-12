# Handoff — continue this analysis on another clone

*Transient note for the Plan→Run dogfood. Delete once the analysis resumes.*

## Where things stand (2026-07-07)

- **Branch:** `methodology/plan-run-arc`. On the other clone: `git fetch && git
  checkout methodology/plan-run-arc && git pull`.
- **Phase:** **Plan phase APPROVED (2026-07-12)** after four critic passes. Plan
  phase closed; **Run phase open**. Next: **co-define the methods milestone** (first
  task = substrate-resolution audit + transport-system reconstruction on the full
  transporter set), delegating execution to a coding subagent.
- **What changed this session (all in `proposal.md` + logged in
  `proposal_notebook.md`):** transporter enumeration now unions BRITE `ko02000` +
  TCDB + annotation search; explicit transport-**system boundary rule** (decision
  7); substrate tag = finest the evidence *confidently* supports, promiscuous
  transporters get options listed (decision 12); the **breakdown/degradation side
  was cut down** — grounding showed the KG can't recover breakdown direction
  per-enzyme (reaction direction unreliable; GO process absent 8/9 for glycolate),
  so it's now a **qualitative up/not-up flag from a dedicated KEGG _degradation_
  map** (reusing genome-wide `pathway_enrichment` ORA), **corroboration only, not
  in the ranking/FDR**; else "not determinable" → module rests on uptake +
  specificity (decision 13). Terminology plain-language swept twice (no coined
  labels). Third critic pass in `proposal_critical_review.md`.
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

## Open threads / notes for the methods milestone

- **Start the methods milestone by co-defining it** (researcher agreement gate
  before work). First task = substrate-resolution audit (per transporter: how
  finely can we resolve substrate, via KEGG KO + BRITE + product/TCDB) + confirm
  transport-system reconstruction (incl. the boundary rule) on the full transporter
  set. Delegate execution to a coding subagent that loads `research-methodology`;
  artifacts come back, judgment stays in the main thread.
- **One statistics reversal to keep an eye on:** the fourth critic pass dropped the
  ≥2-system FDR gate (reversing a pass-2 decision) so single-transporter substrates
  can pass — researcher approved the plan as a whole; reconfirm if it resurfaces.
- Plain-language / no-coined-labels is a standing researcher preference (memory on
  the origin machine only, not in-repo).
