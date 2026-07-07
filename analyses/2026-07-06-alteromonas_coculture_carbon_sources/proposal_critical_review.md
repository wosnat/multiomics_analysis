# Proposal critical review

Fresh-context critic (interpretation-only; no data yet), 2026-07-06. Verdict:
**no Blockers**; 5 Concerns, 2 Notes. KG spot-checks confirmed every factual
anchor tested (glcB = `ACZ81_13685`; primary experiment `all_detected_genes`,
3947 genes, 111↑/163↓, DESeq2; the time courses are starvation-vs-exponential,
control "PRO99-lowN exponential growth"). Findings verbatim below, each with
disposition.

---

### Concern 1 (interpretation) — temporal read is a difference-of-starvation-responses, not a presence contrast
**Critic:** Each temporal arm is starvation-vs-its-own-exponential-baseline, so
comparing coculture and axenic trajectories is a difference-of-differences that
isolates the coculture-specific component of the *starvation response*, not
carbon uptake per se — a coculture-only ramp could be carbon, nitrogen exchange,
death/lysis kinetics, or slower decline. The proposal folded both temporal and
presence signals into the same "modules that turn on" support language.
**Disposition — FIXED.** Added an explicit "difference-of-starvation-responses"
paragraph to the temporal-read section; changed Approach step 5 to "Temporal
overlay (corroboration only)"; added to Known confounders; and rewrote locked
decision 2 to weight the trajectory below the presence contrast, stating a
temporal ramp cannot name a carbon source alone.

### Concern 2 (interpretation) — growth-rate / regulon confound only partially controlled
**Critic:** Coculture changes growth tempo; carbon-acquisition regulons are more
growth-coupled than Fe/Na/K importers, so "organic-C moves more than inorganic"
can arise from a general anabolic upshift, not carbon specificity. The ribosomal
check guards only the crudest artifact; the specific alternative isn't named.
**Disposition — FIXED.** Added the growth-rate/regulon alternative to the new
Known-confounders subsection, and stated the carbon claim leans on specificity /
chemical coherence rather than the bulk C>inorganic contrast.

### Concern 3 (interpretation) — inorganic "clean negatives" overstates independence
**Critic:** The negative control is classified by the same product/COG/TCDB
pipeline that assigns candidate carbon modules (and ABC is substrate-agnostic at
the TCDB node), so a misannotated organic-C importer contaminates the control.
Not independently derived.
**Disposition — FIXED.** Softened "clean negatives" to "reference class sharing
the pipeline's failure modes" in Reference controls; added a confident-flag
audit requirement before the set can bound a false-positive rate; noted in Known
confounders.

### Concern 4 (interpretation) — "count of independent results" can launder a weak signal
**Critic:** Only the HOT1A3 day-11 experiment is fully rankable; the two EZ55
arms are `significant_only` (presence-only); the two EZ55 pCO₂ arms are the same
cultures at two CO₂ levels yet each counts as one. A bare count hides this.
**Disposition — FIXED.** Added a statistics-decision rule that the count's
composition (rankable vs presence-only, strain/partner) travels with every
reported number, and that the two EZ55 pCO₂ arms count as **one** strain-partner
support with pCO₂ as an internal consistency check.

### Concern 5 (interpretation) — C+N tagging insufficient given the nitrogen-recycling thesis
**Critic:** Amino-acid/peptide uptake up in coculture is the *predicted*
nitrogen signature of the subject study, so for the modules most likely to move
the carbon attribution is least defensible. A distinct tag records the ambiguity
but a reader will still count them; C+N modules should be excluded from the
carbon count unless carbon-specific catabolism corroborates.
**Disposition — DISPUTED (researcher), 2026-07-07.** The critic's exclusion rule
assumes the risk runs N→mislabelled-as-C. The researcher's working hypothesis is
the reverse: carbon from Prochlorococcus-derived organic matter (exudate and/or
dead cells) drives the interaction, and N recycling is a downstream by-product.
Amino acids and peptides are carbon-bearing, so their uptake **is** carbon
acquisition; excluding them would bake in the opposite causal story. Resolution:
C+N modules are **included and counted** as candidate carbon sources, kept
**tagged distinctly** so the dual nature is transparent to the reader.
Catabolism corroboration raises confidence for any module but is not an inclusion
gate. Approach step 1 and locked decision 8 updated accordingly. The critic's
underlying point — that a C+N module is *also* consistent with nitrogen
acquisition — is retained as an honest interpretation caveat via the distinct
tag, not as an exclusion.

### Note 6 (interpretation) — axenic proteomics timepoint sparsity
**Critic:** The axenic proteomics arm has one informative timepoint (day 31; day
18 calls nothing), so the proteomics temporal overlay rests on a single axenic
comparison point.
**Disposition — FIXED.** Added to Known confounders as a scope limit on the
temporal overlay.

### Note 7 (interpretation) — glycolate is a soft positive; a miss is uninformative
**Critic:** Glycolate not surfacing doesn't invalidate the method (may not be
exuded; glcB may be constitutive); the "method works if" block should say what a
miss means.
**Disposition — FIXED.** Stated in the "Method works if" block that glycolate is
a soft positive — surfacing corroborates, absence is uninformative, not a
failure.

---

**Summary (first pass).** No Blockers; Concerns 1–4 and both Notes fixed inline in
`proposal.md`; Concern 5 **disputed by the researcher** on scientific grounds
(C+N uptake is carbon acquisition under the C-driven working hypothesis) and
resolved as include-and-tag rather than exclude. The highest-value fix was
demoting the temporal read to corroboration-only. The critic-then-researcher
exchange on C+N worked as intended: the critic surfaced the C-vs-N attribution
ambiguity, and the researcher — who owns the causal hypothesis — set how to
handle it.

---

## Second pass (2026-07-07) — re-review after the scoring machinery was revised

The proposal was materially revised after the first pass (best-system scoring,
module-granularity rule, BH/FDR, C+N reversal, temporal demotion), so the critic
was re-dispatched over the new machinery. It found **2 Blockers** + 2 Concerns +
1 Note. Both Blockers **confirmed by `run_cypher`** on the primary experiment
(3947 edges; `rank_up` non-null on 111, `rank_down` on 163, `rank_by_effect` on
all 3947) and **fixed**.

### Blocker 1 (interpretation) — `rank_up` is significant-genes-only, not genome-wide
**Critic:** The scoring premise treats `rank_up` as a genome-wide rank; in fact
`rank_up` is populated only for significant-up genes (111 of 3947 in the HOT1A3
primary), so the "HOT1A3 fully rankable vs EZ55 presence-only" distinction is
false for `rank_up` (both within-significant-set), and a genome-wide matched-max
null over `rank_up` is not constructible. The genome-wide field is
`rank_by_effect` (direction-blind).
**Disposition — FIXED (confirmed).** Verified via `run_cypher` (counts above).
Re-grounded the score: rank all detected genes by KG-provided `log2fc` into an
up-percentile — genome-wide for `all_detected_genes`, within-significant-set for
`significant_only`. `rank_up`/`rank_down` demoted to validation handles. The
rankable-vs-presence distinction survives, now correctly sourced from which genes
have `log2fc` rows, not from `rank_up`. Approach step 2, statistics decision,
scope-limit, decision 10, and `proposal_notebook.md` query 9 all updated.

### Blocker 2 (interpretation) — "best (max) `rank_up`" is inverted
**Critic:** With `rank_up`=1 meaning most-up, "best" is the **min**, not the max;
as written the effect selected the least-up system.
**Disposition — FIXED (confirmed).** Switched the statistic to an **up-percentile**
(1 = most up) and defined **module effect = max percentile**, with a matched-max
null on that transform. The inversion is gone; "best route = highest percentile"
is now unambiguous. Updated everywhere the effect is defined.

### Concern A (interpretation) — max inflates large substrate-unresolved modules
**Disposition — FIXED.** Added a guard: the matched-max null draws same-size sets,
and unresolved/coarse modules are reported separately with system count shown; the
toy example checks that a large unresolved module with one strong member does not
beat its matched-size null.

### Concern B (interpretation) — 1-system-module multiple-testing leak into the support count
**Disposition — FIXED.** Added an explicit bar: 1-system modules never contribute
to a cross-experiment support count (only ≥2-system, FDR-passing modules do);
they stay descriptive.

### Note (data-integrity-adjacent) — field name `rank_by_effect` vs MCP `rank`
**Disposition — FIXED.** Corrected the field semantics in `proposal_notebook.md`
query 9 and logged the MCP-rename trap in `gaps_and_friction.md`.

**Summary (second pass).** Two real Blockers in the revised scoring — both caught
**before** any Run work, both from a cold read + a `run_cypher` spot-check the
curated MCP view had hidden. The corrected score (percentile of `log2fc`, max over
systems, matched-max null) is now internally consistent and constructible from the
actual KG fields. This is the plan-time catch the arc exists for: the error would
otherwise have surfaced only in the methods milestone as a scorer that silently
dropped non-significant transporters and selected the least-up system.

---

## Third pass (2026-07-07) — re-review after the identification + degradation machinery was revised

The identification half was materially revised (BRITE `ko02000` enumeration +
substrate source; explicit transport-system boundary rule; the importer/organic
classifier named as an audit output; CAZy right-sized; **new decision 13** — the
degradation-pathway side as two-handle graded corroboration, direction-blind), so
the critic was re-dispatched over the new machinery, interpretation only, with the
scoring treated as a trusted (already-vetted) input. It found **no Blockers**, 3
Concerns + 1 Note. The critic **spot-checked glycolate** and confirmed the
decision-13 grounding exactly (9 genes / 5 reactions for C00160 in HOT1A3, `glcB`
absent, and the set *majority glycolate-producing* — 6 producing vs 3 consuming),
which sharpened Concern 1.

### Concern 1 (interpretation) — the degradation "strong" rung over-reaches a direction-blind handle
**Critic:** The top rung read "*strong* — a coherent consuming route exists (and,
where testable, its enzymes are up …)". The co-expression clause was hedged
"where testable," so "strong" could be granted on route-existence alone — but the
proposal's own confounder text concedes the handle proves only metabolic reach,
not flux. The glycolate spot-check shows the raw chemistry arm is dominated by
*producing* reactions, so "consuming route exists" over-reaches on the very
validation compound.
**Disposition — FIXED.** Renamed and re-defined the ladder: the top rung is now
*route-present + co-expressed* with co-expression **required, not optional**;
route-present without co-expression is a distinct **weaker** rung labelled
"metabolic potential only." The label can no longer attach to genome potential
alone.

### Concern 2 (interpretation) — co-expression billed as confound-free directional evidence
**Critic:** "Co-expression … is the strongest available directional signal" is not
reconciled with the growth-rate/regulon confound in the same section — a
transporter and its catabolic enzymes are a co-regulated set and can co-rise under
a general anabolic upshift.
**Disposition — FIXED.** Qualified both the ladder and the confounder text:
co-expression separates substrate *use* from *production* (direction) but does
**not** escape the growth-rate confound, so even the top rung leans on
specificity/coherence, not co-movement. The two passages now agree.

### Concern 3 (interpretation) — boundary rule misses tandem identical unresolved cassettes
**Critic:** The stop conditions (role clash, annotation break) do not fire for two
adjacent, same-architecture ABC cassettes both annotated "Putative ABC
transporter" — all roles are valid (no clash) and annotation is identical (no
break) — so adjacency fuses them, the exact failure the rule was added to prevent.
The audit guarantees this unresolved-tandem case occurs.
**Disposition — FIXED.** Added stop condition (c): a **repeat of an already-filled
component role** (a second binding protein or second ATPase in the run) marks the
next cassette. Patched in the Approach reconstruction bullet and decision 7. Also
noted the exact locus-tag gap is set on real data in methods.

### Note (interpretation) — "chemically coherent" is a post-hoc, author-judged criterion
**Critic:** Of the three "method works if" criteria, motility-down and the
organic-matter-degradation signal are falsifiable, but "chemically coherent rather
than random" is post-hoc and a committed author can satisfy it for almost any
output — yet it carries part of the carbon claim's falsifiability.
**Disposition — FIXED.** Pre-committed an operational bar: the passing modules must
concentrate in a **small set of recognised marine-DOM / known-cyanobacterial-
exudate chemical classes** (organic acids incl. glycolate, amino acids/peptides,
sugars, osmolytes), a reference named from the literature **before the ranked
catalog is read**; a scattered catalog, or one dominated by substrate-unresolved
coarse modules, fails the bar.

**Summary (third pass).** No Blockers; all 3 Concerns and the Note fixed inline.
The critic confirmed the revised identification machinery is sound and the
inorganic-control circularity is already adequately named/downgraded (that
dimension came back clean). The highest-value fix was Concern 1 — the degradation
ladder's top label ("strong") no longer attaches to direction-blind metabolic
potential; it now requires co-expression, and the proposal states plainly that
even that does not escape the growth-rate confound. The plan is internally
consistent across the identification, scoring, and degradation machinery.
