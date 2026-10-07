# Methodology test log — round 2 (scratch note)

Answers to the watch-list in `docs/methodology-test-brief.md`, written as each
item resolves, plus where the structure actively helped (wins).
`gaps_and_friction.md` holds the problems; this holds the evidence and the
positive signal.

## Watch-list answers

*(filled in as each item resolves)*

1. Automatic methods critic —
2. Delta pass after exploration — *(Plan-level evidence, 2026-10-07)* A delta pass was run on
   the **proposal** after controls were added post-critic (the arc only describes delta passes for
   Run milestones). Scoped to the new sections, with the rest of the proposal as trusted, it cost
   ~69k subagent tokens and ~1.7 min (vs. ~92k / ~2.4 min for the full pass) and found 5 Concerns,
   two of them real rule conflicts the author had just introduced. Scoping kept it cheap; it
   earned its dispatch. A second scoped pass, over the new §3.7 output section only (~67k
   tokens, ~2 min), returned **a Blocker** (the author's own count of applicable lines was wrong,
   leaving the ranking key open to post-hoc choice) plus a structural bias toward the hypothesis
   gene. Two scoped passes, both earned. Run-milestone evidence still pending.
3. Fixture realism + spot-run on a real row —
4. Friction logged during the late milestones —
5. Does the Plan phase reach a natural stop? — *(in progress, 2026-10-06)*
   The question was reshaped mid-Plan, twice, by the researcher: proteomics
   added as main evidence, then the analysis split into a Pro side and an
   Alteromonas side (+ contrast). Both happened before any proposal text was
   written, which is the cheap place for them.
   **2026-10-07 update:** after the critic pass, the approval prompt was answered with a design
   question four times running: (1) the preprint is mine and is being rewritten, (2) don't
   preselect classes or prefilter, (3) use domain info, (4) recruit neighbours by domain or
   function. Each reopened the proposal (205 → 284 → 330 lines). Unlike round 1, nothing was
   committed as approved and then reopened: every reopening came before the single Plan commit, so
   one commit for the Plan phase still holds. But the approval prompt is where the researcher's
   design thinking actually happened. The close gate works as a design review, not a rubber stamp.
   Open question for round-2 review: should the arc expect this (present the design as a set of
   open choices at close) rather than as a finished proposal?
6. Cross-experiment comparability statement in the framing? — **Second occurrence (2026-10-07).**
   The framing *did* carry an explicit comparison section (§3.6: rank percentiles, table_scope,
   design differences), prompted by the researcher's scope choice ("anchor + other pairs as
   check"), not by the five-item floor. It still missed two comparability holes, which the
   proposal critic caught: (a) late coculture vs. early axenic mixes partner with starvation
   length; (b) every non-anchor experiment is N-replete, so none can replicate an N-limited
   finding. Same family as round 1's FDR-family-size hole: the comparability of the *design*, not
   just the metric. Evidence for a floor item: per experiment, its role and what it can/can't
   confirm.
7. Falsifiability check / expected-negative earns its place? — *(Plan-phase evidence,
   2026-10-07)* It changed the plan twice:
   - Expected-negative 1 (nitrate/nitrite in MED4) forced an explicit rule for substrates failing
     the "can use" check. Without it, the cyn system's TCDB label would have quietly let
     nitrate/nitrite through.
   - Expected-negative 2 (N-replete coculture) exposed, via the critic, that the planned
     "cross-checks" were all N-replete and could only ever be controls.

   Not ceremony at plan time. Run-phase evidence still pending.
8. Methods milestone stays minimal? — *(pending)* Set up to be tested hard:
   by the end of the Plan phase the methods milestone was committed to building
   the entity set (transport-system reconstruction, compound-class assignment,
   confidence tiers) **and** making it organism-agnostic for reuse by the
   follow-on Alteromonas analysis. That's two things beyond "an ad-hoc module
   implementing the approach". 2026-10-07: the researcher made it a discovery milestone by
   design: surface every substrate with flags, then work through the findings together at its
   decide gate (class groupings agreed there). Round 1's methods was a discovery milestone by
   accident; this one is by plan. Evidence that "methods stays minimal" doesn't hold when the
   method includes building the entity set. By Plan close the methods milestone had grown again: Pfam
   role assignment, two-kind neighbour recruitment (subunits vs. linked enzymes), flag columns,
   and three groupings (classes, tiers, what joins a system) to agree at its decide gate. All
   came from the researcher's design questions during the Plan, not from the five-item floor.
- Delegation cost —
- Unpredicted creaks —
  - 2026-10-06: the arc's skill dependency (superpowers) was not loaded in the
    clone, and preflight didn't notice (see `gaps_and_friction.md`).
  - 2026-10-07: the arc has no slot for "whose interpretation is the hypothesis".
    The anchor turned out to be the researcher's own unpublished preprint, which
    these analyses are rewriting. The critic's "same data, not independent" concern
    was right, but its meaning changed: the analysis re-derives or corrects the
    author's own prior, rather than testing an external claim. The Plan phase only
    learned this at the approval step. A one-line Question-stage prompt ("what is
    this analysis for: a standalone result, or part of a paper rewrite?") would
    have surfaced it at the start.
  - 2026-10-07: usage logging silently off (jq missing); preflight green.
    Second preflight blind spot this run.

## Wins

- **2026-10-06, Plan — grounding caught a missing data layer before framing.**
  The first grounding pass filtered on `coculture_partner` and returned RNA-seq
  only on the *Prochlorococcus* side. The researcher asked "what about
  proteomics?"; re-querying by publication showed Weissberg 2025 carries
  protein (and more RNA) data that `coculture_partner` doesn't tag, because those
  experiments are per-arm starvation time courses (coculture arm and axenic arm
  each vs. their own exponential phase), not coculture-vs-axenic contrasts. It was
  caught before any framing was written.

- **2026-10-06, Plan — MCP docs (`docs://analysis/metabolites`,
  `docs://ontologies/tcdb`) earned their read.** The researcher asked whether the
  updated assets help. They did, concretely:
  - the "Cross-feeding bridge" recipe names the three confounders this analysis
    has to handle (currency metabolites, family-level substrate breadth, no
    transport direction);
  - they state up front that metabolism edges are undirected ("involved in", not
    "produces"), which constrains how the Alteromonas producer side can be worded;
  - they predicted `gltS` falling out at `most_specific`, which happened.

  Limits: the recipe is written for the MED4->Alteromonas direction and stops at
  annotation; joining annotation to expression across organisms is left to the
  analyst.

- **2026-10-07, Plan: the researcher's domain question caught a hypothesis-favouring tier rule
  that the critic and self-review both missed.** "Should transport system analysis look at
  domain info?" led to pulling Pfam + verbose TCDB for the MED4 N transporters. TCDB is
  eggNOG-only for every ABC system but has a direct sequence hit for `amt1`, so the tier rule
  the critic had reviewed would have ranked the hypothesis gene above its competitors for
  pipeline reasons. The critic reads the proposal cold and couldn't have known the evidence-rung
  distribution. Only a KG lookup could show it. Signal for the methodology: a tier or confidence
  rule should be checked against the actual distribution of the evidence it keys on before it is
  locked.

- **2026-10-07, Plan: "what are our controls?" found a real positive control the framing floor
  had not prompted for.** The floor asks for a validation set (genes with known behaviour) and an
  expected-negative, and both were satisfied, but at the gene and annotation level, not at the
  level where the claims are made (transport-system expression). Asking the question as
  *controls* surfaced Tolonen 2006 growth-on-cyanate / growth-on-urea (known-substrate
  calibration, all blind) and a non-N transporter reference. The calibration gives a
  pre-registered gate on whether the consumer side may name a compound at all. A floor wording
  like "a positive and a negative control at the level the claim is made" would have caught it.

