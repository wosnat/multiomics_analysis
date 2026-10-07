# Proposal critical review — interpretation only (2026-10-07)

Fresh-context critic over `proposal.md` (with `proposal_notebook.md` as its grounding record).
Lens: interpretation only. Result: **no Blockers, 8 Concerns, 2 Notes.** The critic spot-checked
KG metadata only: all 17 locus tags resolve as named; the anchor timepoint/growth-phase claims
match; the NH4+ quote matches the Weissberg abstract; the 2016 experiments are exponential in
Pro99.

Findings are condensed from the critic's report. Each carries the author's disposition.

---

**1. Concern — the step 3 / step 4 contradiction lets nitrate/nitrite reach "stands out".**
Step 3 dropped substrates that fail the "can use" check, but step 4 kept them at medium tier, and
§3.3 judged a class on its highest-tier system without requiring high tier. The medium-tier cyn
system, the top responder in the peek, could therefore have produced a nitrate/nitrite "stands
out" verdict. Expected-negative 1 only forbade a *high*-tier call.
**Disposition: fixed.** Failing substrates are now dropped from class assignment (visible in the
parts list, flagged, never feeding a verdict) (§3.2 step 3b). The medium tier is now
`most_specific` + `family_inferred` only. Expected-negative 1 now requires no nitrate/nitrite
system at any tier and no class label (§3.5). *Amended 2026-10-07 (researcher: no prefiltering):*
failing substrates are now kept and flagged `can_use = False` instead of dropped. The protection
is unchanged in effect: such a substrate can never support a claim, and expected-negative 1
requires every MED4 nitrate/nitrite row to carry `can_use = False`. *Amended again 2026-10-07 (domain check):* the fixed tier ladder (high/medium/low) is replaced by a system-level evidence profile with boundaries set at the methods decide gate, because the ladder favoured `amt1` (TCDB direct hit) over every ABC system (eggNOG-only); see notebook item 14.

**2. Concern — the "binding subunit preferred" rule leaves cyn's class undefined.** `cynA`
(binding) carries only nitrate/nitrite; cyanate is on `cynB` (notebook item 8). There was no
fallback rule, which invites a post-hoc choice on the system the author already knows is the top
responder.
**Disposition: fixed.** Pre-specified (§3.2 step 3c): the system class = the passing substrates
from any subunit; the binding subunit only resolves conflicts between passing classes; if its
only substrates fail, fall back to other subunits; the tier is that of the carrying call. A
worked case for cyn is written in. The §3.4 validation no longer pre-asserts tiers. *Amended 2026-10-07:* with flags instead of filters, the
"fallback" becomes simpler. All subunits' substrates are shown, and only `can_use = True` rows can
carry a claim; for cyn that is cyanate (`cynB`).

**3. Concern — late coculture vs. axenic d14 mixes coculture with starvation length.** Rule (b)
needed the coculture percentile to be only "above" axenic d14, with no margin. Any NtcA target
that climbs with deeper starvation would pass. The axenic d14 response is shallow (40 up / 95
down of 1424). The time-matched coculture d18 vs. axenic d14 was used only for "trajectory".
**Disposition: fixed.** Starvation length is named as an alternative explanation (§3.5). There
is now a 0.10 percentile margin in (b), a time-matched read (coculture d18 vs. axenic d14) as part
of the expression read, flags for "also up in early axenic starvation" and "up early in
coculture", and a "duration-compatible" label. The label is now "stands out beyond **early**
axenic starvation". The residual confound is tagged `[gap]` (no axenic culture survives to d60).

**4. Concern — the ammonium hypothesis cannot fail in practice.** `amt1` is a one-gene system;
its protein numbers were seen; the only blind bar was "RNA log2FC > 0"; "relies on" implies
primacy, but classes are judged independently, and urea and cyanate likely stand out too.
**Disposition: fixed.** §3.1 now states two competing readings of the ammonium hypothesis, (i)
all NtcA systems up and (ii) alternative-N systems damped, plus two blind RNA-level predictions:
P1 (`amt1` RNA percentile ≥ 0.90 at d60 and d89) and P2 (`amt1` ≥ the median urea and cyanate
system percentiles). It also lists explicitly what counts against ammonium as the primary
consumer-side route.

**5. Concern — "imports" and "relies on" overstate transporter-expression evidence.** Rising
transporter levels are N-starvation regulation, not evidence of substrate presence or uptake. The
ammonium hypothesis's prediction for the non-ammonium systems was unstated.
**Disposition: fixed.** The question is now "elevate import capacity"; the preamble states what
the analysis can and can't say; §3.1 gives the predictions for the urea and cyanate systems under
both readings.

**6. Concern — the cross-checks can't replicate an N-limited finding.** All three 2016
experiments are N-replete exponential Pro99; expected-negative 2 itself predicts they show
nothing. The only N-limited direct contrast (Weissberg d11/d18) is from the same study and not
independent, and it was missing from the cross-check discussion.
**Disposition: fixed.** Verified that Biller NATL2A is also Pro99, exponential (`list_experiments`
verbose). The secondary question is reframed as "is the pattern specific to N limitation"; the
2016 sets plus Biller become **N-replete controls**, not replicates. The same-study contrast is
labelled as the only N-limited direct comparison and as not independent (§2, §3.6).
Cross-strain replication under N limitation is recorded as `[gap]`.

**7. Concern — expected-negative 2's consequence clause ignores the anchor's baseline
structure.** The anchor compares the coculture culture with its own coculture exponential phase,
so a coculture-wide induction would largely cancel; the test was also one-sided (it never said
what *down* means). The 2016 MED4 set is 272 down vs. 24 up.
**Disposition: fixed.** The consequence clause is rewritten (§3.5, expected-negative 2): "up" =
coculture alone triggers scavenging, carried as an alternative into the contrast, and it doesn't
directly undermine the anchor because of the baseline structure; "down" = compatible with partner
N damping NtcA targets, recorded as a pointer for the contrast. The light/tool differences are
stated in §2 and §3.6.

**8. Concern — the hypothesis comes from the same data it's tested on.** The paper's NH4+
conclusion was drawn from these proteomics and RNA data, so an ammonium "pass" partly restates the
paper.
**Disposition: fixed, then reframed (2026-10-07).** §3.1 says this is a re-analysis on the same
data. The researcher then clarified that the anchor is their own unpublished preprint, and that
these analyses build its rewrite. So the caveat now reads: a pass re-derives the preprint's
reading more rigorously but is not independent confirmation; a fail is a correction the rewrite
must carry.

**9. Note — the biology-check claim was not backed by the grounding record.** Notebook item 7
gave only axenic d14 `glnA`/`ntcA`; no `glnB`, no coculture values.
**Disposition: fixed.** Item 7 now carries the full table of every value seen (12 genes × 7
timepoints, both cultures) and states that no RNA and no other genes or experiments were seen.

**10. Note — the disclosure omitted that `cynA`/`cynS` are already up at axenic d14.**
**Disposition: fixed.** Added to the §3.1 disclosure: cyanate responds in plain starvation too.

---

**Critic's verdict (verbatim):** "No Blockers. The most important things to fix before the
decide gate are the tier/rule logic in §3.2–3.3 [...] Both should be pinned down now, while the
methods are still blind." Both are fixed above.

---

# Delta pass — controls added after the first review (2026-10-07)

Scope: §2 calibration table, §3.2 step 5 + calibration/negative-reference reads, §3.3 (c), §3.4
positive calibration, §3.5 expected-negative 3; the rest of the proposal as trusted. Lens:
interpretation only. The critic verified the four calibration experiments' metadata
(`list_experiments` verbose: Tolonen urea/cyanate are steady-state exponential, 400 µM urea /
800 µM cyanate as sole N vs. ammonium-replete Pro99; Read is filtered_subset, top 50%, ~840–853
genes; Tolonen and Read timepoints `acute_stress`). Result: **no Blockers, 5 Concerns, 2 Notes.**

**D1. Concern — (c) penalises N claims whenever secondary limitation sets in.** A plausible
secondary P limitation (pst + phn counted twice) would automatically downgrade every N class,
contradicting expected-negative 3's own two-reading logic.
**Disposition: fixed.** (c) now runs over *eligible regulons*: co-regulated systems count once,
and a regulon explained as secondary limitation by expected-negative 3 (evaluated first) doesn't
count against N classes.

**D2. Concern — undetected non-N proteins.** No rule for non-N systems absent from the 1424-
protein tables; treating them as "not exceeding" would weaken (c) under measurement failure.
**Disposition: fixed.** (c) is evaluated over detected regulons, with the count reported; fewer
than 3 eligible regulons → "not evaluable".

**D3. Concern — the specificity gate tests a different contrast, and what a pass permits is
unspecified.** Tolonen is high-substrate, non-starved exponential growth; the anchor is trace
supply on months of starvation. "Resembles" was unconstrained, and cyn is expected up in both the
cyanate and starvation fingerprints.
**Disposition: fixed.** The gate states what it tests and that a pass is necessary, not
sufficient. Naming a compound now needs gate pass + "stands out" + departure from co-induction
(out-ranking the other NtcA import systems by ≥ 0.10 in protein at d60 and d89, same direction in
RNA). The fingerprint-resemblance read is exploratory only.

**D4. Concern — gate scope vs. P1/P2; reading (ii) untested.**
**Disposition: fixed.** P1/P2 are reported as written under any gate outcome; a gate failure with
co-rising cyn and urt is reported as evidence of shared NtcA control (reading (i)). The absence of
any calibration for partial-relief damping is stated as `[gap]`.

**D5. Concern — the starvation fingerprint doesn't separate "not up" from "not measured"; no
per-check failure consequences; timescale mismatch.**
**Disposition: fixed.** Read 2017 is positive-evidence-only (also added to §3.6); C1–C4 each have
a pre-registered consequence; the fingerprint is labelled acute (hours).

**D6. Note — the specificity check compares rank percentiles across experiments.**
**Disposition: fixed.** Declared as an exception (same study, platform, control, gene universe),
with a 0.10 margin.

**D7. Note — secondary-limitation markers only for P.**
**Disposition: fixed.** Added `idiA2` PMM1164 for Fe (from grounding item 16's keyword list);
S, Mn/Zn and bicarbonate are unresolved by design and therefore count against N classes in (c).
Whether the Fe set has a binding subunit is left to the method's build.

**Critic's verdict (condensed):** the controls are real, correctly identified and independent; two
new rules interacted badly with the existing framework, and the calibration's pass consequence
was unconstrained. All fixable with wording/conditionality; none needed new data. All fixed above.

---

# Delta pass 2 — §3.7 "Output and ordering" (2026-10-07)

Scope: §3.7 only; the rest of the proposal as trusted. Lens: interpretation only. Result: **1
Blocker, 6 Concerns, 2 Notes. Not clean.** §3.7 was rewritten in response; dispositions below.

**E1. Blocker — the applicable-line count contradicted the table.** The prose said `amt1` has "3
applicable lines of 6"; the table had 8 lines, two of which (flags) could never be *supports*.
amt1's maximum was 3/5 under the formula and 3/3 under the prose, so the ranking key could be
chosen after the data.
**Disposition: fixed.** No ratio is computed. Corroboration is shown as three counts
(supports / against / applicable) and never used for ordering. Flags were moved out of the line
set.

**E2. Concern — three lines restated the label or existing flags** (RNA agreement = §3.3 (a);
the non-N line = (c)'s failure; the early-axenic line = an existing flag already used by (b)'s
margin). That added automatic supports or againsts.
**Disposition: fixed.** RNA is now *strength* (rank percentile ≥ 0.90, not just > 0); the non-N
and early-axenic results are flags, not lines.

**E3. Concern — a supports-only fraction favoured single-gene carriers (`amt1`, the hypothesis
gene),** contradicting §3.2 step 4's no-penalty principle; it also ignored *against*.
**Disposition: fixed.** Ordering is label → late protein percentile only; corroboration counts
are displayed, not ranked, so no denominator structure can favour either system type.

**E4. Concern — asymmetric and ambiguous line rules.** N-replete "not significant = supports"
scored a null result as evidence; calibration C3 failure was *neutral*; the linked-enzyme rule was
undefined for multi-gene enzymes and had no timepoint for *against*; platforms were unstated.
**Disposition: fixed.** N-replete status and calibration are flags reported as observed; every
line now has a stated platform, timepoints, a supports rule, an against rule, and against wins on
conflict; linked enzyme = ≥ half of detected linked-enzyme genes, protein, d60 and d89.

**E5. Concern — some line outcomes were known before the lines were chosen**, and the notebook
said "fixed before any data".
**Disposition: fixed.** §3.7 lists the non-blind cells (persistence, early-axenic and
linked-enzyme cells for the peeked genes); the notebook wording is corrected.

**E6. Concern — "best-supported system" could be read as chosen after the data.**
**Disposition: fixed.** "Best system by annotation tier, fixed at the methods decide gate; never
chosen by expression or corroboration."

**E7. Concern — the time-matched guard had no column; "duration-compatible" was defined twice.**
**Disposition: fixed.** Added the time-matched flag (coculture d18 vs. axenic d14, "partner-early"
at a ≥ 0.10 margin); "duration-compatible" keeps §3.5's definition only.

**E8. Note — calibration is a method property, not a corroborating line.**
**Disposition: fixed.** Moved to the flags group, labelled as a method property.

**E9. Note — scope gaps** (other strains, non-N rows, where P1/P2 and the sanity gate are
reported, the (c)-not-evaluable ceiling).
**Disposition: fixed.** Header block lists the gates and predictions; non-N systems get rows; other
strains are reported per class as up / not significant / down; "*elevated* at most" when (c) is
not evaluable.

