# Agent-driven knowledge-graph research: the Plan→Run arc

*Methods paper — draft outline. Sections filled at each analysis decide gate.*

## Abstract (stub)

Large-language-model assistants make knowledge-graph-backed biological research
faster but introduce characteristic failure modes: ungrounded claims from
training knowledge, gene-name/paralog conflation, premature interpretation, and
vague analysis plans that look fine yet force expensive redos mid-execution. We
describe a disciplined human-in-the-loop workflow — the **Plan→Run arc** — that
structures such an analysis into a grounded planning phase converging on a single
enumerated proposal, and an execution phase of three gated milestones, with
computation delegated to a coding subagent while judgment stays with the
researcher. We illustrate the workflow on a worked example: inferring the organic
carbon sources a marine heterotroph (*Alteromonas*) draws on in coculture with
*Prochlorococcus*, from a multi-omics knowledge graph.

## 1. Motivation

- The promise and the failure modes of LLM-assisted KG research (hallucination,
  source conflation, premature conclusions, vague-plan redos).
- Why ad-hoc prompting is insufficient; the need for a repeatable, gated workflow.

## 2. The method: the Plan→Run arc

- **Domain rules** (the non-negotiable floor): KG as sole data source; locus tags
  not gene names; source tagging ([KG]/[interpretation]/[gap]); scripts over
  chat-computed statistics; statistical rigor; plain-language / describe-before-
  interpret.  → **Fig: rule stack**
- **Plan phase** — one grounded brainstorming conversation → a single
  `proposal.md` with *enumerated* framing (hypothesis, approach, an explicit
  statistics decision, a named validation set). Closes on self-review → automatic
  interpretation-only critic → researcher approval.  → **Fig 1 (arc)**
- **Run phase** — `methods → analysis → evaluation`, each a
  co-define → do → show → explore → decide loop with two researcher gates.
  → **Fig 2 (milestone loop)**
- **Delegation** — a coding subagent authors scripts/data/figures and returns a
  factual manifest; the main thread owns the notebook and all judgment.
  → **Fig 3 (delegation)**
- **Just-in-time formalization, with enumeration** — terms/metrics/decisions
  enter only when the data demands them, but what the plan *does* commit to is
  stated concretely.  → **Fig 5 (formalization ladder)**
- **The fresh-context critic** — a cold reader of the artifact's own files at
  each claim-bearing gate; lens matched to the milestone.

## 3. Worked example: Alteromonas coculture carbon sources

- The question and its **reopening** when enumeration revealed every usable
  coculture contrast runs in a medium with no added organic carbon (upstream lock
  edited by a downstream data reveal).
- The enumerated proposal and its **six critic passes** — what tightened each
  pass.  → **Fig 4 (proposal convergence)**
- Methods milestone: co-define; delegation; the genes→systems→modules parts-list
  build as a concrete instance of just-in-time formalization.
- (Analysis + evaluation milestones — filled as they happen.)

## 4. Evaluation (against the dogfood watch-list)

Did enumeration let holes be poked *before* anything ran? Did the critic catch
what a vague plan would hide? Did delegation keep the thread clean? Did the main
thread catch data anomalies from returned artifacts, not just trust summaries?
Any redo caused by a plan that looked fine but wasn't?

## 5. Limitations

N = 1 (2). Human-in-the-loop dependence. Generalization beyond this KG/domain.
Describes and illustrates the method; does not validate it.

## 6. Conclusion

## Figures

1. The Plan→Run arc (phases, milestones, gates) — `figures/fig1_plan_run_arc.md`
2. The Run-milestone loop (co-define→do→show→explore→decide, two gates)
3. Delegation (main thread ↔ subagent; artifacts up, judgment stays)
4. Proposal convergence across six critic passes
5. Formalization ladder (genes→systems→modules)
