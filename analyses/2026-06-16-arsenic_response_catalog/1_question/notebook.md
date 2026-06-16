# Step 1 — Research question

## Context

First step of the analysis: turn the researcher's prompt into a locked,
answerable research question, grounded in what the KG actually holds. No
computation here — this step is a conversation plus a KG reachability check.

Researcher's opening prompt: *"genes responding to arsenic"* (framed as a quick
demo).

## Locked question

> Which *Prochlorococcus* genes in the KG carry a functional annotation for
> arsenic handling — e.g. arsenate reductase, arsenite efflux pumps, ars-operon
> regulators?

Operational intent (exact definitions deferred to the steps that need them, per
just-in-time formalization):
- **Arsenic handling** = annotation implicating the gene in arsenic resistance /
  metabolism — arsenate reductase (*arsC*), arsenite efflux pump (*arsB* /
  *acr3*), ars-operon regulator (*arsR*), arsenite methyltransferase, phosphate/
  arsenate transporters where flagged. Exact annotation fields and search terms
  finalized in step 2.
- **Catalogue, not response** = the unit is the annotation, not a measured
  expression change. This analysis lists genes whose function points to arsenic;
  it does **not** test whether they change under arsenic exposure.

## What I did

Clarifying dialogue with the researcher, two forks put as explicit choices:
1. **Organism scope** → *Prochlorococcus* (not Alteromonas, not "whatever has
   arsenic data").
2. **Meaning of "responding to"** → functional annotation (a catalogue of
   arsenic-handling genes), not differential expression and not "both."

The second choice narrows the literal prompt ("responding to") to "annotated
for handling." Recorded as a decision below and carried as a limitation in
`paper.md` so the writeup doesn't overstate what the catalogue shows.

## KG context

- `kg_release_info` → KG release **0.1.0-alpha.6** (built 2026-06-16),
  explorer **0.1.0a3**, verdict **ok** (16/16 schema asserts pass). KG totals:
  124,751 genes, 197 experiments, 43 papers, 47 organisms.

No data queries yet — enumerating the specific arsenic-annotated genes is step 2.

## Decisions

- **2026-06-16 — Scope is *Prochlorococcus*.** Researcher choice; Alteromonas and
  the "whichever organism has data" option were declined.
- **2026-06-16 — "Responding to" means functional annotation, not expression.**
  Researcher choice. Turns the analysis into a catalogue of arsenic-handling
  genes. Limitation (genes may not actually move under arsenic) carried into the
  paper.

## Decide-gate checklist

- **Outputs produced** — `1_question/notebook.md` (this file); scaffold
  (`paper.md` skeleton with Question populated, `gaps_and_friction.md` header,
  `.gitignore`). No scripts/data/figures (step 1 is conversation only).
- **Results presented** — KG release check shown in chat and recorded above.
- **QC gate** — `kg_release_info` verdict = ok (16/16 asserts) → KG release
  matches explorer expectations, safe to proceed.
- **Decisions made this step** — *Prochlorococcus* scope; annotation (not
  expression) meaning of "responding" (both dated 2026-06-16, above).
- **Advance rationale** — the question is locked and scoped to one organism and
  one clear data type (functional annotation); ready to enumerate the specific
  arsenic-annotated KG entries in step 2.
