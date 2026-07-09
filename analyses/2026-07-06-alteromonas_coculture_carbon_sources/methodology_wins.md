# Methodology wins — Plan→Run arc dogfood (scratch note)

Where the restructured Plan→Run arc actively helped, vs. the old 6-step flow.
Paired with `gaps_and_friction.md` (the problem log); this holds the positive
signal. Feeds the watch-list in `docs/methodology-test-brief.md`.

## Plan phase

- **Enumerated framing forced real holes open at plan time (watch-list #1).**
  Insisting the plan name a concrete approach, a statistics decision, and a
  named validation set surfaced problems *before any code ran* that a vague plan
  would have hidden:
  - the **dual C+N ambiguity** — amino-acid/peptide uptake is also the study's
    nitrogen-recycling story, so it can't be silently called "carbon"; caught
    only because we were forced to enumerate what a "carbon source" module is;
  - **TCDB coarseness** — writing "tag substrate from TCDB" made us test it, and
    the ABC superfamily lump (`3.A.1`) fell out immediately;
  - the **counting-unit trap** — enumerating the roll-up rule exposed that raw
    transporter genes aren't independent (subunits co-move), forcing the
    transport-system unit.

- **KG grounding inside the Plan conversation caught the researcher's own model
  mismatch.** The opening recollection ("one experiment; RNA + proteomics + two
  time series; a dark/light coculture") did not match the KG (10 experiments;
  proteomics is starvation-time-course not presence; whole study is continuous
  light; the dark/light set is a different paper). Grounding-before-framing
  turned that into a scope correction at plan time rather than a mid-run
  surprise — the reopen failure the arc is meant to pre-empt.

- **Collapsing question + KG entries + framing into one conversation felt
  coherent, not cramped (watch-list #3).** Each researcher refinement (TCDB,
  neighbours, substrate-class matching, rank-not-FC, no-pooling, drop-glucose)
  built directly on a freshly-grounded fact in the same thread, so the framing
  tightened continuously instead of being retrofitted.

- **Viability checks were cheap because grounding was already open.** "Can we
  reconstruct transport systems?" and "is TCDB specific enough?" were answered
  with two queries mid-conversation, so the plan commits only to what the data
  supports.

## Pre-approval researcher review (watch-list #1)

- **The approval gate — re-reading the enumerated proposal before sign-off —
  caught an unused KG handle and quantified a risk, before any Run work.** A
  targeted "is this grounded?" pass over the identification/scoring machinery
  found (a) the plan named product/COG/TCDB + adjacency but **never referenced the
  BRITE transporters tree** (`ko02000`, 310 genes, hierarchical) — a purpose-built
  handle now folded in; (b) it leaned on **CAZy** for catabolism, which is ~1%
  covered here → right-sized to KEGG/EC; and (c) the substrate-resolution ceiling
  is now a **number** (104/310 reach the finest BRITE level) rather than an
  assertion, which is what lets decision 12 say "adapts per transporter" honestly.
- Also surfaced two transport-system-definition gaps that *read* fine in prose —
  no system-boundary rule, and an un-operationalised importer/organic classifier —
  and made both explicit as methods tasks. These are exactly the "reads rigorous,
  bites in methods" holes the enumerated-plan + review-before-execute structure is
  meant to open at plan time. Cost: a few edits, no re-grounding mid-run.

## Proposal critic (watch-list #2)

- **The critic caught a real conflation a vague plan would have hidden.** Reading
  the proposal cold, it flagged that the starvation time courses are each
  *starvation-vs-their-own-exponential-baseline*, so comparing the coculture and
  axenic trajectories is a difference-of-differences (coculture-specific
  *starvation response*), not a carbon-presence contrast — the exact
  "difference-of-trajectories narrated as coculture-vs-axenic" failure the arc
  targets — landed as an inline fix *before* any Run work; a vague plan would
  have carried it into the analysis milestone and forced a redo. No Blockers;
  5 Concerns + 2 Notes.
- **The critic also triggered a productive researcher decision (watch-list #2,
  the other half).** It flagged the dual C+N attribution and *suggested*
  excluding amino-acid/peptide modules from the carbon count. The researcher
  overrode that on scientific grounds — under the C-driven working hypothesis,
  C+N uptake *is* carbon acquisition — resolving it as include-and-tag. The value
  wasn't the critic being right; it was the critic forcing the causal assumption
  into the open where the researcher (who owns it) could rule. Critic surfaces,
  researcher decides — exactly the intended division.
- Worth noting the critic could only be this sharp because the plan was
  **enumerated** — it had concrete controls, a named temporal design, and a
  stated statistics decision to bite on. A sketch would have given it nothing to
  catch.

## Second critic pass caught two hard Blockers at plan time (watch-list #2, #6)

- Re-running the critic after the scoring machinery was revised caught **two real
  Blockers** in the statistics — both confirmed by a `run_cypher` spot-check and
  fixed before any Run work:
  (1) the score was premised on `rank_up` being a genome-wide directional rank,
  but it is **significant-genes-only** (111 of 3947 edges in the primary) — a
  genome-wide null over it isn't even constructible, and non-significant
  transporters would have silently dropped out;
  (2) "best (max) `rank_up`" was **inverted** (rank 1 = most up, so "best" is the
  min) — as written the scorer selected the *least*-up system.
- This is exactly the failure the arc targets (watch-list #6, "a plan that looked
  fine but wasn't"). Both errors were invisible in prose — the plan *read*
  rigorous — and would have surfaced only in the methods milestone as a scorer
  that dropped genes and picked the wrong extreme, forcing a redo of methods +
  re-grounding. Catching them at plan time cost a few edits instead.
- Reinforces two methodology points: (a) **re-review after material revision** is
  worth it — the first pass was clean, the revision introduced the Blockers; and
  (b) an enumerated statistics plan is **falsifiable against the actual KG fields**
  — the critic could check "does `rank_up` mean what the plan says?" only because
  the plan named the field and the operation.
- Also a KG/tooling note (watch-list-adjacent): the raw-`run_cypher` check saw
  what the curated MCP view hid (the `rank_by_effect`→`rank` rename and the
  significant-only null population). Logged in `gaps_and_friction.md`.

## Third critic pass — re-review after the identification/degradation revision (watch-list #2)

- A **third** cold pass, run after this session added the transporter-ID and
  degradation machinery, caught a real over-reach in the *newly-added* scheme: the
  degradation "strong" rung could attach to direction-blind metabolic potential
  alone, contradicting the proposal's own direction-blind caveat. The critic
  sharpened it with a **glycolate spot-check** — the chemistry arm is *majority*
  glycolate-*producing* (6 of 9), so "consuming route exists" over-reached on the
  very validation compound. Fixed by requiring co-expression for the top rung.
- Reinforces the second pass's lesson a second time: **each material revision
  earns its own re-review.** Passes 1 and 2 were clean on the identification/
  degradation area because that machinery didn't exist yet or wasn't detailed;
  the third pass is where the just-added scheme got its adversarial read — and it
  found something. Cost: four inline edits, no Run-phase redo.

## Fourth critic pass — caught a Blocker at the final gate (watch-list #2, #6)

- The **final** pre-approval pass found a real **Blocker** in machinery added *by a
  previous critic pass*: the system-boundary rule (c) fragmented common ABC importers
  with two permeases / two ATPases. The critic **KG-verified** it on the
  branched-chain importer `livKHMGF` — the proposal's *own* worked example, which the
  author never checked against the rule. Classic "reads fine, breaks in methods,"
  caught at plan time instead of as a wrong system count mid-run.
- It also caught a correctness error the earlier passes missed: the ≥2-system FDR
  gate (a pass-2 disposition) rested on the false premise that a 1-system module is an
  "uncorrected single-gene call" — it structurally excluded the single-transporter
  specific substrates that *are* the deliverable. Reversed with reasoning.
- Reinforces the strongest methodology lesson of this dogfood: **each material
  revision earns its own cold re-review, and later passes catch what earlier ones
  (and prior critics' own fixes) introduced.** Four passes, four rounds of real
  catches, zero Run-phase redos so far.

## To re-evaluate after the Run phase

- Watch-list #4 (does coding-subagent delegation keep the main thread clean, or
  does the re-invoke loop drag?) — not yet exercised.
- Watch-list #5 (does the main thread catch data anomalies from returned
  artifacts, not just trust summaries?) — not yet exercised.
- Watch-list #6 (any redo from a plan that looked fine but wasn't?) — the point
  of the enumerated plan is to avoid this; check whether the methods/analysis
  milestones hold to the plan without a redo.
