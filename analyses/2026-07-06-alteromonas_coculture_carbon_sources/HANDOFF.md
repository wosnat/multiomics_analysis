# Handoff — continue this analysis on another clone

*Transient note for the Plan→Run dogfood. Delete once the analysis resumes.*

## Where things stand (2026-07-07)

- **Branch:** `methodology/plan-run-arc`. On the other clone: `git fetch && git
  checkout methodology/plan-run-arc && git pull`.
- **Phase:** Plan phase committed, then **refined through a researcher
  pre-approval review** (this session) and **critic-vetted a third time** (clean of
  Blockers). **Still not formally approved** — researcher is going to **reread the
  revised `proposal.md`** before sign-off, then Run phase.
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

## Open threads to expect from the researcher

- **Researcher still needs to reread the revised `proposal.md`** (went home
  mid-read) before approving. Approval → open the **methods** milestone by
  co-defining it (first task: substrate-resolution audit + transport-system
  reconstruction on the full transporter set).
- The earlier steer "use the stored rank property" — resolved to ranking the
  provided `log2fc` instead (stored `rank_up`/`rank_down` are significant-genes-only;
  `proposal_critical_review.md` second pass).
- The breakdown/degradation cut-down (decision 13) was agreed in-session but the
  researcher hasn't reread the final wording — worth a confirm.
