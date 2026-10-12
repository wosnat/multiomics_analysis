# Methodology review — round 2 (testing the revised arc)

**Date:** 2026-10-12
**Subject analysis:** `analyses/2026-10-06-pro_n_import_coculture`. This is the consumer side of
"which N compounds does *Alteromonas* pass to *Prochlorococcus*". It ran the full arc: Plan →
methods → analysis → evaluation.
**Stack:** template 0.2.0-alpha.1 · `multiomics_explorer` 0.1.0-alpha.5 · KG 0.1.0-alpha.7 ·
superpowers 6.4.1
**Brief this answers:** [`docs/methodology-test-brief.md`](methodology-test-brief.md)
**Evidence:** the analysis folder's `methodology_test_log.md` (watch-list answers and wins),
`gaps_and_friction.md` (29 dated friction entries, 2026-10-06 → 10-12), the critic files, and the
notebooks.

**Run in one paragraph.**
- **Plan.** One Plan commit, after one full critic pass and two scoped delta passes.
- **Methods.** A discovery milestone: a reusable transport-system module, going from v1.0 to v1.6.1.
  It needed 21 decisions, a step-by-step pilot against an independent answer key, an API-usage
  review, three critic passes, and a QC round the researcher asked for.
- **Analysis.** The researcher deferred the pre-registered labels and asked for in-depth exploration
  instead (E1–E16). Two critic Blockers changed the reading.
- **Evaluation.** The critic found three Blockers. The researcher then rejected the
  critic-hardened conclusion as unreadable and approved a findings-table version.
- **Outputs.** A journal-style `manuscript.md` was written at the end. All commits are on `main`.

---

## 1. Watch-list verdicts

### A1. Automatic methods critic when the milestone emits data — **Works; keep**
It fired, because the methods milestone emitted per-strain transport-system tables. The first pass
found 2 Blockers and 8 Concerns, all in the narrative and none in the data:
- a curated table presented as a file view;
- "peptides: dpp" while every peptide row was unusable;
- a strict-variant "pass" that rested on helicase rows.

A later pass would not have caught these, because the analysis milestone reads methods outputs as
trusted inputs. Cost: about 142k tokens, 5.6 min. The conditional applied cleanly.

### A2. Delta pass after exploration — **Works; extend to the Plan phase**
It was dispatched at every point where claims grew after a pass:
- Plan: two scoped passes (about 69k and 67k tokens; 5 Concerns, and 1 Blocker);
- methods: one, after the decide-gate build (about 170k; 6 Concerns that changed the tiers);
- methods: one more, after the QC round (about 158k; 3 Concerns).

Scoping to the delta, with earlier files trusted, kept each pass at about 1.5–7 min and stopped it
re-auditing. New: the arc describes delta passes only for Run milestones, but this Plan phase needed
two.

### A3. Fixture realism + spot-run on a real row — **Fixtures work; a single spot-run is too thin for entity-set construction**
Real-serialization fixtures caught two bugs: the `bool("False")` trap and pandas reading "n/a" as
NaN. Neither the fixtures nor a spot-run could catch three other error classes. Each needed its own
layer:
- **Wrong API defaults and rule gaps** were caught by a step-by-step pilot against an independent,
  MCP-only answer key. Examples: a `min_gene_set_size` default undercounting BRITE (57 vs 86), `fadD`
  called a transporter, and `pstS`'s domain missing.
- **Tool-internal behaviour** was caught by a source-level API-usage review. Examples: offset paging
  over a non-unique sort silently swapping rows while every count check passed, and a
  "most-specific" variant that isn't specific.
- **Rules that look right but fill bins wrongly** were caught by looking at a random sample of each
  bin. Example: the Medium tier was mostly helicases and proteases.

### A4. Friction logged through the late milestones — **Fixed**
`gaps_and_friction.md` has entries dated through 2026-10-12, covering the analysis milestone
(linked contrasts, missed experiments, external culture data). Evaluation-milestone lessons went to
the test log. Round 1's three-day silence did not recur.

### B5. Does the Plan phase reach a natural stop? — **Second occurrence: yes, but the close gate is a design review**
"One commit for the Plan phase" held (`7bca4cc`). Nothing was committed as approved and then
reopened. But the approval prompt was answered with a design question four times running:
- this is my own preprint;
- don't preselect classes;
- use domain information;
- recruit neighbours by function.

Each answer reopened the proposal (205 → 330 lines). As in round 1, the approval gate is where the
researcher's design thinking happens.

### B6. Cross-experiment comparability in the framing — **Second occurrence → change**
The framing had an explicit comparison section, prompted by the researcher, not by the floor. It
still missed design-comparability holes. Plan time (caught by the proposal critic):
- late coculture vs early axenic mixes partner with starvation length;
- every non-anchor experiment was N-replete.

Run time (caught by the data or the researcher):
- the axenic "early" reference was a late-decline culture;
- each arm's RNA reference was its own, already N-stressed, exponential phase;
- the coculture-vs-axenic contrasts were algebraically one fitted model.

Same family as round 1's FDR-family hole: the comparability of the design, not only of the metric.

### B7. Does the falsifiability check / expected-negative earn its place? — **Yes, with one caveat**
- **Plan:** it changed the plan twice. The nitrate/nitrite expected-negative forced the "can use"
  rule; the N-replete expected-negative exposed that the planned cross-checks were all controls.
- **Run:** expected-negative 1 validated the `can_use` check, and expected-negative 2 produced an
  informative MIT9313 exception.
- **Caveat:** the falsifiability statement depended on the class labels. When the labels were
  deferred, the author declared a "bounded negative" anyway. The evaluation critic caught it (B2):
  the check had not been evaluated.

### B8. Does "the methods milestone stays minimal" hold? — **Second occurrence → change**
This methods milestone was a discovery milestone by design:
- the method built the entity set (transport systems, tiers, classes, links);
- 21 decisions across seven versions;
- four critic or review passes and a QC round;
- about 10 coder rounds.

Round 1's was a discovery milestone by accident. When the method constructs the entity set,
"minimal" does not describe it.

### Delegation cost — **Clean at scale**
One persistent coding subagent carried every milestone (more than 25 invocations, usually 250k–950k
tokens each, 3–24 min) with no context failure. Results went to disk and compact manifests came
back. Two independent verifiers (362k and 87k tokens) and seven critic passes (67k–172k) ran
cleanly. The main thread re-ran tests and re-read data after each round, and caught several coder
errors by doing so: a mis-stated "4 loci" twice, overstated figure readings, and a superseded flag
count.

### Unpredicted creaks
1. **Preflight blind spots.** Preflight was green while superpowers was absent from the clone and
   `jq` was missing, so usage logging was silently off.
2. **"Whose hypothesis is it?"** The anchor was the researcher's own unpublished preprint, which these
   analyses are rewriting. The Plan learned this only at approval.
3. **Experiments missed at Plan.** The grounding listed experiments by organism and role, so three
   MIT9313 experiments of a chosen publication (Tolonen 2006) were missed. The researcher caught it
   during the analysis milestone.
4. **Layer and platform mixing recurred.** Protein was compared with microarray RNA for dpp, twice
   (once caught by the researcher, once by the critic).
5. **Reference-culture physiology isn't in the KG.** That the axenic sample was in late decline, and
   that axenic cultures move faster, came from the researcher. It changed how half the reads were
   interpreted.
6. **The pre-registered classification was premature.** The researcher deferred the labels: "the
   classification is premature … do some in-depth analysis". Exploration then exceeded the plan by
   a lot (E1–E16), which is welcome, but the arc has no slot for "explore before labelling".
7. **Critic-hardened prose becomes unreadable.** After the evaluation critic, every caveat was folded
   into the conclusion. The researcher: "hard to follow … a long paragraph that says we know
   nothing". A findings table plus numbered meanings fixed it.
8. **Figure iteration took many turns.** These covered:
   - colour direction (orange = up);
   - colorbars and a non-blue rank scale;
   - an axenic/coculture divider;
   - readable group labels;
   - rank percentiles replaced by fold change with labelled ends;
   - a dense grid replaced by a one-word table.

   Each was a researcher request.
9. **`paper.md` drifted into a process record.** It had internal vocabulary, file paths and an
   incomplete reference list (2 cited papers missing, 1 used but uncited). A separate journal-style
   `manuscript.md` was needed.
10. **External data outside the KG.** The researcher's culture measurements (cell counts, NH₄⁺) were
    brought in, then set aside as out of scope. The KG has no culture-measurement layer, and most
    papers publish cell counts only in figures.
11. **Tooling.**
    - Inline shell heredocs with prose broke on quoting, repeatedly; writing script files worked.
    - A Windows default-encoding write corrupted a file once.
    - `openpyxl` was absent from the analysis environment.

---

## 2. Findings — what to change

**Change now (second occurrence):**

- **A. Add a design-comparability floor item (B6).** For each experiment used, state:
  - its role;
  - what each arm is compared against (its reference sample and that sample's physiological
    state);
  - whether contrasts share samples or a fitted model;
  - what the experiment can and cannot confirm.

  Ask the researcher about the culture states the KG doesn't hold.
- **B. Recognise entity-set construction as a discovery milestone (B8).** When the method builds
  the entity set, plan the methods milestone as discovery. Budget for decisions at its decide gate,
  and require the verification layers in C.
- **C. Layered verification for entity-set construction (A3).** Replace the single spot-run with:
  1. real-serialization fixtures;
  2. a step-by-step pilot against an independent MCP-only answer key;
  3. a source-level API-usage review before scaling;
  4. a random sample of what fills each bin before any classification or tier rule is approved.
- **D. Treat the Plan close as a design review (B5).** Present the proposal at approval as a short
  set of open choices, not a finished document. Expect a scoped delta critic pass after the
  changes (A2).

**Notes (first occurrence; confirm in the next analysis):**

- **E. Question-stage purpose prompt.** Ask whether this is a standalone result or part of a paper
  rewrite, and whose hypothesis it is.
- **F. Enumerate whole publications.** When a publication is chosen for a role, list all of its
  experiments and say why each is used or not.
- **G. Guard comparisons across layers and platforms.** Comparison helpers should refuse
  protein-vs-RNA or microarray-vs-proteome comparisons unless they are explicitly labelled.
- **H. Falsifiability depends on labels.** If the labels are deferred, say "not evaluated as
  pre-registered"; don't substitute a post-hoc criterion silently.
- **I. Allow exploration before labelling.** Let the analysis milestone run an exploratory
  sub-phase before the pre-registered classification is applied, with the classification
  explicitly re-confirmed afterwards.
- **J. Conclusion format.** The evaluation conclusion leads with a findings table (route ×
  reference) and numbered meanings; caveats sit in their own short section.
- **K. Figure conventions in the template.**
  - Diverging colours: orange = up, blue = down. Use a non-blue sequential scale for ranks.
  - Every heatmap has a colorbar and dividers between condition blocks.
  - Prefer fold change with labelled axis ends over rank percentiles.
  - Keep summary figures to one word per cell.
- **L. A manuscript output alongside `paper.md`.** At evaluation, produce a journal-style
  manuscript with references checked against the KG; keep `paper.md` as the record.
- **M. Preflight.** Check that the arc's skill dependencies are present and that usage logging works
  (e.g. `jq`).

**KG / explorer tickets** (from `gaps_and_friction.md`):
- **Metabolites:**
  - chemical categories (ChEBI hierarchy);
  - generic ↔ stereo-specific compound equivalence (Cysteine / L-Cysteine);
  - a cross-reference between the two nitrate nodes.
- **Experiments:**
  - sampling day and growth state per arm;
  - a shared-model identifier for linked contrasts;
  - culture-level measurements (a node type for cell counts and medium nutrients; figure
    extraction).
- **Tool bugs:**
  - offset paging over a non-unique sort;
  - `gene_neighbors` crashes with large windows;
  - silent `min_gene_set_size` defaults.
- **Annotation:** TCDB substrate lists are per subfamily, not per gene.

## 3. What held and should not be touched

- **Plan → proposal → critic → approval.** The proposal critic and its scoped delta passes caught
  framing holes the self-review missed, every time.
- **Automatic critics at data-emitting milestones, and delta passes.** Every pass earned its
  dispatch. Blockers were found in a Plan delta pass and at the methods (2), analysis (2) and
  evaluation (3) milestones, and every pass also raised Concerns that changed the work. None was
  manufactured.
- **One persistent coding subagent, artifacts not conclusions, and a main thread that re-reads the
  files.** The main thread caught coder errors repeatedly by re-checking data, not by trusting
  manifests.
- **The decide gate as the researcher's steering point.** Every major redirection came there: labels
  deferred, the dpp correction, the culture-state facts, the conclusion rewrite.
- **Pre-registered calibration and expected-negatives.** The calibration gate's failure was the
  analysis's most important result, and it was pre-registered rather than argued after the fact.
- **Plain-language rules.** The researcher repeatedly rejected jargon and dense prose. The rule is
  right; the critic pass needs it applied to its own output too (J).

## 4. Disposition

- **Skill changes A–D:** apply to `research-methodology` (step-protocol, framing floor) and to
  `critical-review` (Plan-phase delta passes).
- **Notes E–M:** carry to round 3; a second occurrence promotes them.
- **KG / explorer tickets:** file upstream.
- **Next analysis that will test these:** the *Alteromonas* N-release analysis (sibling).
