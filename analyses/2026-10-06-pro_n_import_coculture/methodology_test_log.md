# Methodology test log — round 2 (scratch note)

Answers to the watch-list in `docs/methodology-test-brief.md`, written as each
item resolves, plus where the structure actively helped (wins).
`gaps_and_friction.md` holds the problems; this holds the evidence and the
positive signal.

## Watch-list answers

*(filled in as each item resolves)*

1. Automatic methods critic — **Fired, and earned its dispatch (2026-10-07).** The methods
   milestone emitted data artifacts (per-strain transport-system tables), so the critic ran
   automatically with data-integrity + interpretation. It found **2 Blockers + 8 Concerns, all in
   the main thread's narrative, none in the data**: a curated table presented as a file view;
   "peptides: dpp" while every peptide row was `can_use = no`; a strict-variant "pass" resting on
   helicase rows; a near-circular control check. A later pass would *not* have caught these,
   because the analysis milestone would have read the methods tables and notebook as trusted
   inputs, and the class groupings would have been agreed on the over-read. Cost ~142k subagent
   tokens, ~5.6 min. The conditional ("when the milestone emits a data artifact") applied
   cleanly.
2. Delta pass after exploration — *(Plan-level evidence, 2026-10-07)* A delta pass was run on
   the **proposal** after controls were added post-critic (the arc only describes delta passes for
   Run milestones). Scoped to the new sections, with the rest of the proposal as trusted, it cost
   ~69k subagent tokens and ~1.7 min (vs. ~92k / ~2.4 min for the full pass) and found 5 Concerns,
   two of them real rule conflicts the author had just introduced. Scoping kept it cheap; it
   earned its dispatch. A second scoped pass, over the new §3.7 output section only (~67k
   tokens, ~2 min), returned **a Blocker** (the author's own count of applicable lines was wrong,
   leaving the ranking key open to post-hoc choice) plus a structural bias toward the hypothesis
   gene. Two scoped passes, both earned.
   **Run-milestone evidence (2026-10-08):** the methods milestone's claims grew after its first
   critic pass (the decide-gate build added links, tiers, classes and the review list). A delta pass
   scoped to the new tables + the Decisions section, with p1–p6 trusted, cost ~170k tokens / ~7
   min (vs. ~142k for the first full pass; the delta covered three strains' new tables). It found 0
   Blockers but 6 Concerns that changed the build:
   - the Medium tier was mostly helicases, proteases and similar;
   - ferritin was undisclosed;
   - function links were dominated by GST paralogs;
   - the record described the wrong code version.

   The scoping worked: it didn't re-audit p1–p6. It earned its dispatch; without it, the analysis
   milestone would have used "High + Medium" as its candidate set.
3. Fixture realism + spot-run on a real row — *(set-up, 2026-10-07)* The researcher asked for
   more than the arc prescribes: after the toy tests, a **step-by-step pilot** on 7 known MED4
   cases, each pipeline step checked against an expected outcome before the next ("we've seen
   before that sometimes false results come because the API was called / accessed incorrectly").
   The answer key comes from an **independent MCP-only verifier agent** that never sees the code.
   That covers what a single spot-run row can't: wrong API calls at every step (truncation, field
   semantics, wrong tool), not only the parsing layer. **Step 1 result (2026-10-07):** caught a silent API-default
   undercount (BRITE transporters 57 → 86, via `genes_by_ontology`'s `min_gene_set_size=5`) in a
   *Plan-phase* number, and two rule gaps the 40 toy tests passed over (`fadD` called a
   transporter; `pstS`'s binding domain missing from the role map). The toy suite was green
   throughout. Fixture realism worked for the parsing layer; the pilot plus answer key caught what
   fixtures structurally can't: wrong defaults and incomplete domain knowledge.
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
- Delegation cost — *(in progress, 2026-10-07)* One persistent coder carried toy tests + pilot
  steps 1–3 + one fix re-run across 5 invocations (~356k cumulative subagent tokens, ~31 min of
  agent time) without a context failure. Results go to disk; manifests come back compact. The
  independent verifier was ~362k tokens for one answer key, dominated by per-gene MCP calls and
  re-anchoring neighbours for coordinates. The main thread's per-step checks are small scripts
  over the CSVs. No overflow so far; the round-1 failure mode (a large enumeration returned
  inline) didn't recur because every enumeration writes to disk.
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

- **2026-10-07, methods: the API-usage code review (before scaling) caught what the pilot and
  answer key structurally could not.** Reading the installed package source, it found offset
  paging over a non-unique sort that silently swapped rows while every count check passed (C1),
  and a "most-specific" variant that the docs explicitly say isn't specific (C2; two of the
  eight linked enzymes the notebook reported were artefacts). Each check layer caught a
  different class of error: toy fixtures (parsing), pilot + independent answer key (wrong
  defaults, rule flaws, KG data gaps), source-level API review (tool-internal ordering, doc
  semantics the author misread). Evidence for the round-2 review: the arc's single "spot-run on
  a real row" is one of three layers this run needed.


## 2026-10-08 — Methods milestone close: researcher-asked QC round

- **What the researcher's questions earned.** At the decide gate the researcher asked about system
  sizes, the contents of Low, and "what other QC checks/graphics". A six-part QC pack ran after the
  first two critic passes had cleared the milestone. Three of its checks found real problems:
  - adjacent ABC parts left split;
  - curated transporters missed;
  - subfamily substrate lists attaching off-target N classes.

  The third pass then found three Concerns in the fixes themselves (an efflux pump called
  "dedicated"; undisclosed export promotions; fig2 "+k" counting K⁺ transporters as ammonium
  routes). Neither the pilot (designed cases) nor the earlier critic passes (narrative vs files)
  caught any of these. They were caught by checks against an independent source (product strings,
  curated roles) and by looking at a random sample of what fills each bin. This supports the
  `gaps_and_friction.md` proposal: before approving a rule, show what fills each bin.
- **Delegation cost.** Coder rounds v1.5 / v1.6 / v1.6.1 took about 415k / 489k / 533k subagent tokens
  and about 24 / 14 / 11 min. The third critic pass took about 158k tokens and 4 min. The main thread
  verified each round against the files (tests re-run, fig2 inspected, the dedicated/broad table
  cross-checked) before recording.
- **Close.** Committed and pushed at the researcher's instruction ("finish with the methods. commit
  and push"), given while the QC round was in progress. The decide-gate approval covered the
  approach agreed in chat; the final v1.6.1 state was not shown to the researcher before the
  commit, and is summarized for them on return.
