# Process capture log

Timestamped process moments for the methods paper. Factual — what happened and
the methodological point it illustrates. Each entry tags the paper section /
figure it feeds. Seeded retrospectively from the analysis's committed artifacts;
live from 2026-07-22 onward.

Sources drawn on: `analyses/2026-07-06-alteromonas_coculture_carbon_sources/`
(`proposal.md`, `proposal_notebook.md`, `proposal_critical_review.md`,
`gaps_and_friction.md`, `methodology_wins.md`) and the git history on
`methodology/plan-run-arc`.

---

### Plan phase — question reopened by a data reveal (2026-07-06/07) → §3, Fig 1
The starting question ("does motility go up or down in coculture?") was **reopened**
during Plan-phase enumeration when live KG queries showed every usable
Alteromonas–Prochlorococcus coculture contrast runs in a medium (PRO99-lowN / Pro99)
with **no added organic carbon**, and no coculture metabolomics exists. The locked
question was edited (original + evolved question + decision recorded), not silently
replaced — the "reopen the upstream lock, don't paper over it" path. Illustrates:
grounding the plan in live counts catches framing errors at plan time; the lock is
provisional until the data behind it is pulled.

### Plan phase — enumerated proposal + six critic passes (2026-07-06 → 07-23) → §3, Fig 4
`proposal.md` converged through **six fresh-context critic passes**. What each pass
changed (for the convergence figure):
- Pass 1–3 (2026-07-06→07-12): temporal read reframed as a difference-of-starvation-
  responses (not a presence contrast); growth-rate/regulon confound named; inorganic
  "clean negatives" softened to a control sharing the pipeline's failure modes;
  chemical-coherence downgraded to near-confirmatory with a pre-committed
  expected-negative; breakdown/catabolism evidence cut to a qualitative flag only
  where a KEGG degradation map curates direction.
- Pass 4 (pre-approval): a Blocker in the system-boundary rule (would have mis-split
  multi-permease/multi-ATPase ABC importers like `livKHMGF`) — caught by a KG
  spot-check the author's own worked example missed; the ≥2-system FDR gate reversed
  (single-transporter substrates no longer structurally excluded).
- Approved 2026-07-12.
- Pass 5 (2026-07-22, researcher-requested re-review): Blocker — "every subunit has a
  log2fc, so nothing drops to null" was false for the 2 EZ55 `significant_only`
  experiments; scoped + partial-coverage rule deferred to methods. Aromatic
  expected-negative reframed per-strain (HOT1A3 near-vacuous, ~1 aromatic importer).
  Two Notes fixed.
- Pass 6 (2026-07-23, delta review of post-pass-5 edits): 2 consistency slips from
  the author's own edits (an FDR-paragraph rationale not propagated to match a
  scoped sibling; "strain-partner" looser than the governing "strain/partner/
  condition") — both fixed.
Illustrates: the enumerated proposal made holes pokeable *before* anything ran; the
cold critic repeatedly caught what the anchored author could not, including a
self-inflicted inconsistency introduced the same session.

### Plan phase — researcher-directed refinements at the Plan→methods seam (2026-07-22/23) → §3
Between approval and the Run phase, several refinements were made live with the
researcher and re-critiqued (pass 6): more than one KEGG degradation map allowed per
substrate (corroboration-only); transcriptomics/proteomics of one contrast treated as
separate scored units but one support (cross-platform agreement, not two studies);
single-gene transport systems kept and tested but flagged the thinnest tier with a
subunit-count-matched null; the "method works" bar reframed away from a decisive
answer toward a graded candidate catalog whose decisive follow-up is wet-lab growth
assays. Illustrates: just-in-time refinement continues at the seam, each change gated
by the critic before it lands.

### Cross-repo fact-check corrected a KG-derived reading (2026-07-23) → §2 (domain rules), §4
While confirming an excluded experiment (Biller 2016 MIT1002), the KG's `control`
field ("Co-culture with Prochlorococcus NATL2A") was found to flatten the real
contrast; the source supplementary table (in the sibling KG-build repo) showed it is
"24 vs 12 hrs after addition" and "48 vs 12 hrs" — reference = the 12 h coculture
timepoint, and no axenic Alteromonas arm exists in the study. An earlier
`[interpretation]` (reference ≈ t0) was corrected by the primary source. Logged as a
KG-fidelity note in `gaps_and_friction.md`. Illustrates: source-tagging discipline
(interpretation flagged, then corrected against the primary source, not defended);
and a real limit of reading a curated field without the ingestion provenance.

### Run phase — methods milestone co-defined before any work (2026-07-23) → §3, Fig 2
The methods milestone opened with a plain-language co-define (GATE A): first task =
build the parts list (genes → systems → modules) for both strains, subset-first with
QC, iterating the system-grouping rule before finalizing. Researcher shaped it live —
added both-strains scope, multi-step-with-QC, neighbor discovery during system-
building (adjacency recovers subunits the ontology lists miss), and a surface-all-
then-split table with a role column (ambiguous splits stop for reconsideration rather
than auto-guess). Only on agreement was the coding subagent dispatched. Illustrates:
co-define opens the milestone with researcher agreement; the researcher actively
shaped scope rather than reacting to finished work.

### Run phase — delegation instance (2026-07-23) → §3, Fig 3
Step 1 (enumerate transporter genes, both strains) + pulling anchor transporters and
their genomic neighbors was delegated to a coding subagent loaded with the domain
rules, instructed to return frozen CSVs + a factual manifest (counts, what it found)
and to make **no** substrate decisions or grouping-rule finalization.

**First attempt failed (2026-07-23).** The subagent ran ~30 min, wrote a 107 KB
transcript, then terminated without delivering results or writing any artifact (the
`methods/` dir was never created). Diagnosis: it almost certainly pulled a large
enumeration result (hundreds of transporter genes with full annotations) into its own
context and overflowed — the exact large-result trap already logged in
`gaps_and_friction.md` (list_experiments 73 KB rejection). Re-dispatched with
guardrails: **script the enumeration through the package Python API so results write
straight to CSV on disk**, fetch details in small batches, write incrementally, and
return only compact summaries. Illustrates (methodology finding, watch-list #4/#5):
delegation of a broad enumeration needs a "results-to-disk, not results-to-context"
guardrail — the anomaly-catch guarantee (artifacts up, judgment stays) presupposes the
artifacts actually get written; a context-overflow kills both the work and the manifest
silently, with no completion notification. Worth a `gaps_and_friction.md` entry.

### Methods milestone — data-led refinement + repeated anomaly-catches (2026-07-23) → §3, §4, Fig 3/5
The methods milestone's first task (the transporter parts list) was planned as a
bounded substrate-resolution audit; the **data kept forcing refinement**, and the
main-thread-owns-judgment / delegate-execution split is what made that safe. Arc, as a
worked example of the delegation pattern (Fig 3) and just-in-time formalization (Fig 5):
- **Data contradicted the plan's own grounding, caught by verification.** The proposal
  cited glutamine `K10036`, fructose, osmoprotectant and the `livKHMGF` component KOs as
  HOT1A3 anchors; a main-thread KG check found them **absent** (the proposal had listed
  them from the KEGG ontology, not verified in-genome). Recovered by switching component
  role to Pfam domains (`gene_summary`/`alternate_functional_descriptions`, ~100%
  populated) — a researcher suggestion. The planned `livKHMGF` boundary-rule anchor
  didn't exist in the genome and had to be re-anchored on a real peptide cassette.
- **A structural reveal reshaped the catalog, handled as a focus note not a reopen.**
  HOT1A3 has 36 substrate-binding proteins but only 11 import permeases + 111 single-gene
  secondary carriers → organic-C uptake is dominated by single-gene units; complete
  multi-subunit cassettes are mostly inorganic + peptide. The proposal's single-gene tier
  went from edge case to the norm. Recorded as a proposal *focus note* (method unchanged).
- **Pipeline quality caught by looking back.** The first parts-list build dropped 86% of
  the enumerated set in a downstream curation and *rescued* genuine carriers from an
  "other" bucket — the researcher asked whether a rebuild would be cleaner; it was
  (enumeration ≈ transporters, `class_`/`class_reason` per gene), and the v2 diff (0
  substrate changes) *validated* the earlier result rather than changing it.
- **Design co-invented at the gate.** The four reference classes — candidates,
  control-ABC, control-TonB, and **ambiguous-TonB as a "control-for-the-control"** (does
  the TonB receptor class move as a coordinated iron regulon?) — came out of the
  researcher reading the system-size distribution, not from the plan.

**Anomaly-catches (watch-list #5) — the payoff of "artifacts back, judgment in the main
thread":** across the milestone the main thread caught, by reading the real files, what
the subagent's manifests/tests glossed: a noisy first-pass `role` column (enzymes tagged
"catabolic"); the KO absences above; and — the sharpest — a **scorer bug that the passing
test suite hid**: `assign_reference_class` used `bool(row["in_candidate"])`, and the real
CSV stores the string `"False"` (truthy), so on real data every system would collapse to
"candidate"; the 27 tests passed only because the fixture used Python booleans. Caught by
re-running the helper on a real CSV row, not by trusting green tests. This is the single
best illustration for the paper that "tests pass" ≠ correct-on-real-input, and why the
main thread must re-derive/spot-run rather than accept the subagent's summary. The
delegation ran as **one kept-alive subagent across ~8 invocations** (context persists),
returning artifacts + factual manifests only; every classification, exclusion, and
substrate decision was made in the main thread with the researcher.
