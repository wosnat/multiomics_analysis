# Methodology retro — Plan→Run dogfood (carbon-sources analysis)

The first full run of the restructured `research-methodology` arc, end to end
(`analyses/2026-07-06-alteromonas_coculture_carbon_sources/`). The scientific result
was a **bounded negative** (carbon sources not resolvable in the KG transcriptomes) —
which stress-tested the arc harder than a positive would have. Source logs:
`gaps_and_friction.md`, `methodology_wins.md`, and the per-milestone `notebook.md`s.

## Watch-list answers (from `methodology-test-brief.md`)

1. **Did the enumerated proposal let you poke holes before running?** **Yes, strongly.**
   Four critic passes on the proposal caught real Blockers *at plan time* (mis-sourced
   `rank_up`, an inverted max/min, a transporter-counting rule that would fragment real
   ABC systems). None reached execution.
2. **Did the proposal critic catch what a vague plan would hide?** **Yes, every pass** —
   including the boundary-rule Blocker on the *final* pre-approval pass.
3. **Did question + KG-entries + framing in one conversation feel coherent?** **Yes** —
   each refinement built on a freshly-grounded KG fact (see `methodology_wins.md`).
4. **Did coding-subagent delegation keep the main thread clean?** **Net yes, but heavy.**
   The thread stayed artifact-and-decision only, but a long analysis (primary + temporal
   + EZ55, plus cleanup re-runs) meant many re-invocations, each needing real main-thread
   verification. Delegation worked; it was not "cheap."
5. **Did the main thread catch anomalies from artifacts, not just trust summaries?**
   **Yes — repeatedly and decisively.** The main thread overrode the subagent framing
   every time it mattered: "benzoate = scoring artifact" → a real +2.89/padj-1e-10
   induction; EZ55 "null" → *underpowered* (28–32/35 modules unscorable); the 1-gene
   "systems" → genuine orphan binding proteins (verified via `gene_neighbors`), not a
   reconstruction bug. This is the arc's strongest validated guarantee.
6. **Any redo from a plan that looked fine but wasn't?** **No redo.** The failure the
   restructure targets did not occur — the enumerated plan + repeated critic passes
   pre-empted it (the boundary-rule flaw would have caused a mid-run redo; caught at plan
   time).

## Skill edits applied (this retro)

- **Framing now requires a *falsifiability check* + pre-registered expected-negative**
  (`SKILL.md`, Rule 8 framing). *Why:* the run returned a null and the only thing that
  let it be read as *real* (vs a failed method) was a pre-registered expected-negative
  (aromatic/iron transporters) — which was added late by a critic, not by the framing.
  Broadly applicable, not over-fit: every framing should state what a *miss* looks like,
  not only what a hit looks like. Plus an explicit note that a null is a valid outcome.
- **Proposal review: re-run the critic after any material revision** (`SKILL.md`, Rule 8
  Plan review). *Why:* passes 2–4 each caught a Blocker the prior clean pass didn't; the
  skill previously read as a single proposal-critic pass.

## Friction logged (candidate future edits — need a 2nd occurrence before changing the skill)

Per the skill's own rule ("one occurrence is a note; process change needs the same
friction in two analyses"), these are single-occurrence and are **noted, not yet acted
on**:

- **`significant_only` datasets are unscorable by a transporter-module method** (EZ55:
  28–32/35 modules had no gene in the significant set). A presence-contrast module method
  needs genome-wide DE. → domain/KG note in `gaps_and_friction.md`.
- **Validation controls don't transfer across contrast *types*.** The ribosomal-neutrality
  control (calibrated on the presence contrast) failed in the starvation-vs-exponential
  contrast (0.66–0.79). Candidate: the skill could say validation sets are
  per-contrast-type. One occurrence.
- **Co-define/decide rhythm is heavy when a milestone has several sub-analyses.** The
  analysis milestone held three (primary, temporal, EZ55), each a co-define/decide/verify
  loop. Candidate: guidance on sub-stepping within a milestone. One occurrence.
- **Plain-language / no-coined-labels recurred** (I minted "co-expression", "corroboration
  ladder", "rung", then used them; the researcher pushed back 3×). Rule 9 already covers
  this — the failure was *execution*, not a rule gap — so no skill edit; captured instead
  as a persistent-behavior memory. Worth watching whether a rule-strengthening helps.

## One-line verdict

The restructured arc did its headline job: **it pre-empted the mid-run redo, and the
main-thread-verifies-artifacts discipline caught every subagent mischaracterization that
mattered.** The one real structural gap it exposed — no falsifiability/expected-negative
in the framing — is now closed.
