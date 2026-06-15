# Step 3 — How we'll test it (framing, redone 2026-06-15)

## Context

Redone after the reframe. The original framing tested whether motility genes are
*coordinately regulated* in coculture (an over-representation question, HOT1A3 +
EZ55). Step 2's full inventory changed the picture: the medium in every usable
coculture contrast has **no added organic carbon**, which turns the
coculture-vs-axenic contrast into a carbon-source manipulation. The framing now
tests a specific ecological hypothesis, with motility as the lead readout.

co-defined with the researcher across this session.

## The hypothesis

> In media with no added organic carbon, **Prochlorococcus supplies fixed organic
> carbon to Alteromonas.** If so, coculture should make Alteromonas look
> *carbon-fed* relative to axenic — and motility (flagella + chemotaxis) is a
> candidate readout of that shift. `[interpretation]`

Why the data can speak to it `[interpretation]`: *Alteromonas* is a heterotroph
that needs an organic-C source. In axenic PRO99-lowN it has none added; in
coculture the only organic carbon on offer is *Prochlorococcus* photosynthate.

**Time-resolved form (refined 2026-06-15).** Starvation is not a fixed state here —
it *develops*. The durations (step 2) show the direct coculture-vs-axenic contrast
is a single **exponential** snapshot (day 11, 264h: both cultures still growing —
so axenic is not yet carbon-starved, it is living on residual/inoculum carbon),
whereas genuine starvation only sets in over the **day-18→89 time-course**
(`nutrient_limited`, ~3 months). So the sharp prediction is a **divergence that
grows over time**: as the axenic culture exhausts its carbon it should show a
*rising* carbon-starvation signature, while coculture — fed by ongoing
photosynthate — should not. *Prochlorococcus* relieves a carbon-(and-nitrogen)-
starvation state that otherwise deepens in axenic culture. `[interpretation]`

## What we measure

The common lens is **coculture-with-Prochlorococcus vs axenic**, read two ways:
- **Partner effect during growth** — HOT1A3 MED4 coculture-vs-axenic, day-11
  **exponential** snapshot (RNA, all genes). Both cultures are growing, so this is
  *not* fed-vs-starved — it is "what does the partner change while Alteromonas is
  still growing." Reported as its own read, not part of the starvation story.
- **Starvation relief over time (the core)** — HOT1A3 PRO99-lowN time-courses, RNA
  and protein, run separately in coculture and axenic (days 18→89,
  `nutrient_limited`). The starvation signature develops in the **axenic** arm;
  the coculture-vs-axenic *difference of trajectories*, and especially how it
  **grows from day 18 to day 89**, is the carbon-provision read.
  **Ceiling:** the axenic **protein** series stops at day 31, so the late-starvation
  (day 60/89) fed-vs-starved comparison exists for **RNA only**; protein
  difference-of-trajectories is limited to days 18–31.

Per contrast: pathway-level over-representation (the package's `pathway_enrichment`
DE→ORA, all-genes background per experiment — **not** a hand-rolled test), with
motility called out and deep-dived gene-by-gene (locus tags, both omics).

**What "carbon-fed" should look like** `[interpretation]` (described before
interpreting any result): in coculture, expect **up** — organic-C uptake/transport
and central carbon metabolism (glycolysis/ED, TCA); **down** — carbon-starvation /
stringent-response machinery. Motility direction is **observed, not predicted**.

## Controls — and what each rules out

- **Genome-wide background** — the fair denominator for over-representation
  (all-genes-scope experiments only).
- **Glucose-fed reference** — the organic-C-amended experiments (spectrum MarRef
  high/low glucose; EZ55 +0.1% glucose; femsml AMP1+organics). If the coculture
  signature *resembles* the glucose-fed signature, that supports "the effect is
  carbon provision" rather than something else. These manipulate carbon **without**
  a partner.
- **Partner specificity** — EZ55 coculture with *Synechococcus* (CC9311, WH8102)
  vs *Prochlorococcus* (MIT9312). Tests whether provisioning is
  *Prochlorococcus-specific* or generic photoautotroph cross-feeding (both
  photosynthesize and exude C). Direction-only (significant-only tables).
- **Stress / dormancy lens** — the axenic starvation trajectory itself, and the
  MIT1002 darkness time-course. If the "coculture" signature is really a generic
  starvation/dormancy response, these reveal it.
- **pCO₂ nuisance** — EZ55 400 vs 800 ppm, a robustness check.

## The confound (stated up front)

PRO99-low**N** means coculture may also change **nitrogen** availability, so within
Weissberg alone "fed organic carbon" cannot be cleanly separated from nitrogen
effects. The glucose-fed references (carbon manipulated without a partner) and the
N-starvation time-course structure **bound** this confound; they do not eliminate
it. This is a limitation to carry, not a problem to assume away. `[interpretation]`

## Driving example for step 4

HOT1A3 MED4 coculture-vs-axenic (RNA, all genes, `ok_all_genes`) — the simplest
clean contrast — to build the `pathway_enrichment` ORA *mechanics* on. Note this
is the day-11 "partner effect during growth" read; the **core carbon-starvation**
read (the starvation time-courses, difference of trajectories) is applied in
step 5 once the method works.

## Preregistered expectations (tested in step 6)

1. **(starvation relief, time-resolved)** Over the axenic time-course, a
   carbon-starvation signature (e.g. stringent/stationary-phase machinery up,
   central carbon metabolism down) **rises from day 18 to day 89**; in coculture it
   stays flatter — so the coculture-vs-axenic divergence **grows over time**.
2. **(partner effect during growth)** At the day-11 exponential snapshot, coculture
   shifts organic-C uptake / central carbon metabolism relative to axenic — but
   both are growing, so this is reported as a growth-phase partner effect, not
   starvation relief.
3. **(motility readout)** Motility (KEGG flagella+chemotaxis) shifts with coculture;
   direction observed, reported with locus tags, across snapshot and time-course.
4. **(carbon, not just stress)** The coculture/late-axenic-vs-coculture signature
   resembles the glucose-fed reference more than the darkness signature.
5. **(specificity — exploratory)** Whether the response is Prochlorococcus-specific
   vs shared with Synechococcus (EZ55) is reported, not predicted.

## Decisions

- **2026-06-15 — reframed to a carbon-provision hypothesis** (from "is motility
  coordinately regulated"). Motivated by the step-2 medium finding (no added
  organic C in any usable coculture contrast).
- **2026-06-15 — coculture-with-Prochlorococcus is the lens; nutrient/carbon/
  darkness/partner contrasts are controls.**
- **2026-06-15 — ORA via the package's `pathway_enrichment`, all-genes background**
  (per the earlier reinvented-ORA friction note).
- **2026-06-15 — N/C confound named and bounded, not assumed away.**

## Caveats carried forward

- C-vs-N confound in Weissberg (the time-course is labelled nutrient/N starvation;
  C-starvation co-occurs in the axenic arm but isn't separable within Weissberg).
- The day-11 coculture-vs-axenic snapshot is **exponential** — a partner-during-
  growth read, not fed-vs-starved.
- **Protein ceiling:** axenic protein stops at day 31, so late-starvation (day
  60/89) fed-vs-starved is RNA-only; protein difference-of-trajectories ends at
  day 31.
- EZ55 and MIT1002-darkness are significant-only → direction-only, no ORA background.
- Cross-strain / cross-platform comparison is suggestive, not definitive.
- 4 corrupted experiments excluded (step 2 / gaps_and_friction).

## Decide-gate checklist

- **Outputs produced:** this framing notebook (no scripts; gene sets + backgrounds
  validated in step 2).
- **Results presented:** hypothesis, the two readouts, controls, the confound, the
  driving example, expectations — co-defined in chat.
- **QC gate:** every named contrast traced to a `direction_quality` ≥ `ok` row in
  the step-2 inventory; the "fed reference" and "partner" controls confirmed to
  exist; confound explicitly recorded.
- **Advance rationale:** hypothesis, metric, controls, confound, and driving example
  are set and KG-grounded → proposal locked; step 4 builds the method on the HOT1A3
  MED4 contrast.
