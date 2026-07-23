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

---

## Fourth pass (2026-07-07) — final pre-approval, after the KEGG-KO + degradation-cut + enrichment-ontology round

Re-dispatched over the machinery changed since pass 3 (breakdown cut-down, KEGG KO
promotion, enrichment-ontology decision), interpretation only; the transport-side
scoring was a trusted input. Found **1 Blocker + 3 Concerns + 2 Notes**. The Blocker
was **KG-verified** by the critic. All fixed inline.

### Blocker (interpretation) — system-boundary rule (c) fragments real ABC importers
**Critic:** Rule (c) ("stop at a repeat of an already-filled component role") splits
legitimate single ABC importers that carry two permeases and/or two ATPases — a
common class. KG-verified: branched-chain amino-acid importer `livKHMGF` has
`livH`/`livM` both permease (`K01997`/`K01998`) and `livG`/`livF` both ATP-binding
(`K01995`/`K01996`), so rule (c) fragments one physical transporter into three,
corrupting the counting unit the whole scoring rests on — and it hits the proposal's
own Leu/Ile/Val example. Rule also not well-posed against the "shared substrate
annotation" grouping clause.
**Disposition — FIXED.** Rescoped: stop only at (a) role clash or (b) annotation
break; **shared specific substrate (or a KO resolving subunits to one named system)
holds a multi-permease/multi-ATPase system together**; the repeated-role stop is
only a **tiebreaker for indistinguishable unresolved/putative cassettes**. Fixed in
the boundary-rule text and decision 7 (not deferred to methods — the rule as written
was wrong). Ironic note: rule (c) was itself a pass-3 recommendation; it over-fired.

### Concern (interpretation) — ≥2-system FDR gate sidelines single-transporter substrates
**Critic:** The gate excludes 1-system modules from FDR/count on the premise they're
"uncorrected single-gene calls" — but the same-size null is well-defined for size 1,
and a system is multi-subunit (co-moving genes, not one gene), so a 1-system module
*can* be legitimately significant. Many specific substrates (glutamine, iron,
phosphate) have exactly one transporter, so the gate structurally sidelines the
analysis's own deliverable and enriches the ≥2-system tier for coarse lumped modules.
**Disposition — FIXED (reverses pass-2 Concern B, which rested on the "single-gene"
misconception).** All modules incl. 1-system now enter the FDR family with a proper
q from their same-size null; **system count travels with every call** so thinness is
visible; single-transporter substrates are no longer structurally uncallable.
Corrected the "cannot be enriched"/"single-gene" wording. Flagged for researcher
reconfirmation on reread.

### Concern (interpretation) — "chemically coherent" is near-unfalsifiable
**Critic:** The pre-committed class set (organic acids, amino acids, peptides, sugars,
osmolytes) spans essentially all marine-heterotroph organic uptake, so "hits fall in
it" is near-guaranteed — and with breakdown mostly not-determinable and the temporal
read demoted, this weak bar is carrying load.
**Disposition — FIXED.** Downgraded chemical coherence to an explicitly weak,
near-confirmatory check; pre-committed an **expected-negative** (aromatic/xenobiotic
importers should not dominate); stated the falsifiable core is the per-module
reproducible q<0.10 calls, not class concentration.

### Concern (interpretation) — hypothesis + module definition over-claim catabolism
**Critic:** After the cut, "corroborated by their catabolism" (hypothesis) and
"plus that substrate's degradation pathway" (module definition) describe evidence the
method mostly won't have.
**Disposition — FIXED.** Both qualified to "a breakdown-pathway corroboration flag
*where a dedicated KEGG degradation map exists*"; the scored unit is the transport
system(s); glucose example updated to note glycolysis gives no usable flag.

### Note (interpretation) — breakdown flag vs guard may run at different KEGG levels
**Disposition — FIXED.** Step 4 now states the breakdown flag is read at KEGG
pathway-map level (via the median-percentile fallback if the genome-wide guard lands
on a different KEGG granularity).

### Note (interpretation) — stale notebook decision entries
**Disposition — FIXED.** Added a "later entry wins" head note to the decisions log and
struck the superseded ≥2-system line.

**Summary (fourth pass).** One real Blocker — the boundary rule that would have
mis-counted a common, important class of transporters (branched-chain and other
multi-permease ABC importers), caught by a KG spot-check the author's own worked
example should have caught but didn't. Fixed in the rule text. The most consequential
Concern was the FDR gate that structurally excluded single-transporter substrates —
the analysis's own deliverable — on a misconception; now all modules are tested and
the thinness is shown, not gated. The inorganic-control circularity again came back
clean. With these fixes the plan has no known Blockers.

---

## Fifth pass — 2026-07-22 (researcher-requested re-review, consistency/correctness)

Fresh-context critic (interpretation-only; no data yet), 2026-07-22, KG release
0.1.0-alpha.6 reachable (`kg_release_info` ok, 16/16). Requested by the researcher
before rereading the (already-approved) proposal. Confirmed the four prior passes
propagated cleanly: no stale ≥2-system FDR gate anywhere (only the two labelled
"this corrects the earlier…" back-references remain), scoring statistic is
consistently max/best, `rank_up`/`rank_down` uniformly demoted to validation
handles. Verdict: **1 Blocker, 1 Concern, 2 Notes.** Findings verbatim, each with
disposition. *(All four edits **applied** to proposal.md on 2026-07-22 at the
researcher's instruction.)*

### Blocker (interpretation) — "every subunit has a `log2fc`, so nothing drops to null" is false for `significant_only` (EZ55)
**Critic:** Approach step 2 (line 304, "same method everywhere") and the subunit→system
bullet (lines 315–317) state a system's percentile = median of its subunit
up-percentiles and "**Every subunit has a `log2fc`, so nothing drops to null.**" That
completeness claim holds only for `all_detected_genes`. The proposal's own scope
bullet (lines 337–338) says the `significant_only` experiments (EZ55 400/800 — **2 of
the 3 presence contrasts**) have "~300–400 genes [that] have rows at all," and the
Statistics decision (line 391) confirms `significant_only` does not keep tested-absent
rows. So in EZ55 a transport system's non-significant subunits have **no row and no
`log2fc`** — the median is taken over only the significant subunit(s), the
"subunits-of-one-machine-co-move" premise is untestable there, and a system can be
scored on a single significant (most-DE) binding-protein subunit, biasing its median
percentile **upward**. The plan asserts this case cannot arise and specifies no rule
for partial-subunit systems in `significant_only`; a scorer built to the literal text
would silently mishandle 2 of 3 presence experiments.
**Recommendation (critic):** Scope the "every subunit has a `log2fc`" claim to
`all_detected_genes`; add an explicit `significant_only` rule for partially-absent
subunit sets (min-present-subunits threshold, or score-on-present-with-count-shown),
acknowledging the co-movement premise degrades there.
**Disposition — FIXED (scope) + DEFERRED (exact rule → methods).** The subunit→system
bullet now scopes "every subunit has a `log2fc`, so nothing drops to null" to
`all_detected_genes`, states the `significant_only` (EZ55) partial-coverage case
explicitly (median over present/most-DE subunits → upward bias; co-movement premise
untestable), and defers the specific partial-coverage rule (min-present-subunits threshold
vs score-on-present-with-count) to the methods milestone on the real EZ55 subunit-coverage
data. The bias travels with every EZ55 system call.

### Concern (interpretation) — aromatic expected-negative is near-vacuous for the primary strain
**Critic:** The pass-4 pre-committed expected-negative — "aromatic/xenobiotic-degradation
importers should not dominate the catalog; if they do, the method is flagging noise"
(lines 477–481) — has almost no falsification power for HOT1A3. KG spot-check: HOT1A3
has essentially **one** aromatic-compound importer (`benE`, `ACZ81_03335`,
benzoate/H⁺ symporter); a Transport-category search for benzoate/aromatic/naphthalene/
xylene/toluene returned 0, the broadened search returned exactly that 1 gene. A catalog
built from ~1 aromatic candidate cannot "dominate" whether the method is signal or noise.
The coarse-module-domination prong in the same sentence still has teeth; the aromatics
prong largely does not (for the primary deliverable, HOT1A3 day-11).
**Recommendation (critic):** State the aromatic expected-negative is a cross-strain check
whose weight depends on how many aromatic importers each strain actually has (verify per
strain in the substrate-resolution audit); lean the falsifiable weight on the
coarse-module-domination prong and the per-module reproducible q<0.10 core.
**Disposition — FIXED (reframe); per-strain count confirmed in methods.** The
Validation-set section now splits the coherence "teeth" into two prongs — coarse-module
domination (real teeth) and the aromatic expected-negative reframed as a **cross-strain**
check whose weight the substrate-resolution audit sets by counting aromatic importers per
strain. HOT1A3's near-vacuous case is stated explicitly (its falsifiable weight rests on
the coarse-module prong + the reproducible-q core). The critic's 1-importer count is left
as its own spot-check to confirm in the audit, not hard-coded.

### Note (interpretation) — motility validation count is mislabeled
**Critic:** Validation table (line 463) reads "HOT1A3 gene_category 'Cell motility' (38
genes)." Per `proposal_notebook.md` query 7, 38 is the count of **flagellar** hits that
fall in Cell motility (`genes_by_function("flagellar")` → 47 hits, 38 in Cell motility),
not the size of the Cell-motility category. Harmless to the method; the number is
mislabeled.
**Disposition — FIXED (relabel).** Validation table now reads "HOT1A3 flagellar genes —
`genes_by_function("flagellar")`, 47 hits, 38 in the 'Cell motility' category."

### Note (interpretation) — temporal baseline is itself coculture-exponential
**Critic:** Each temporal arm's baseline is that arm's own PRO99-lowN exponential state
(line 53), so a carbon module that is *constitutively* up in coculture (exactly what the
day-11 presence contrast detects) reads **flat** in the temporal coculture arm — it is
already on at that arm's baseline. So the temporal read primarily captures the
starvation-*ramp*, partly orthogonal to constitutive coculture upregulation;
"corroborates the same module" may be optimistic. Only a Note because the proposal already
demotes the temporal read to corroboration-only and states a temporal miss is not
disqualifying — the mechanism just isn't spelled out.
**Disposition — FIXED (one clause).** The temporal-read section now states each arm's
baseline is its own coculture/axenic exponential state, so a constitutively-coculture-up
module reads flat across the temporal ramp — flatness is expected and non-contradictory;
the temporal read captures the starvation-ramp component, only partly aligned with
constitutive coculture upregulation.

**Summary (fifth pass).** One Blocker, both prongs of which reduce to a single missing
rule: the proposal claims genome-wide subunit completeness ("nothing drops to null") but 2
of 3 presence experiments are `significant_only`, where transport systems can have absent
subunits and the subunit-median needs a partial-coverage rule — scope the claim now, set
the rule in methods. The aromatic expected-negative being near-vacuous for HOT1A3 weakens
(but does not break) the falsifiability story; it self-corrects once the audit counts
aromatic importers per strain. Two Notes are cheap honesty fixes. Nothing here reopens the
locked question or the core method; all four are refinements at the proposal→methods seam.
