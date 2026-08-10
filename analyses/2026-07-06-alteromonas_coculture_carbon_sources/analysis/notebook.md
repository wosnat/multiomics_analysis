# Analysis milestone — notebook

Main-thread-owned. Coding subagent returns artifacts (scored tables, figures, run
log); judgment and interpretation live here.

## Co-define (agreed 2026-07-12)

**First analysis step: score the primary presence contrast — HOT1A3 + MED4
coculture-vs-axenic, day 11** (`…690089_coculture_prochlorococcus_med4_hot1a3_rnaseq`;
`all_detected_genes`, ~3947 genes, DESeq2), using the committed `methods/score_modules.py`.

Produce, for this one (experiment × timepoint):
- **Scored module catalog** — each candidate carbon module: effect (best-system
  up-percentile), permutation p, BH q, called-up (q<0.10), p-vs-control, system count,
  per-system distribution. Sorted.
- **Validation set** (same DE ranking): motility (Cell motility) should be **down**;
  `glcB`/glycolate a soft positive; peptidases / organic-matter degradation **up**;
  ribosomal ~neutral; inorganic controls should **not** rank high.
- **Genome-wide guard** — `pathway_enrichment` (KEGG + EC) on the up-genes; and the
  per-module **breakdown flag** where a dedicated KEGG degradation map exists.

Two flags resolved (researcher, "go"):
1. **Controls = the clean 84-system set** (`exclude_interaction_coupled_controls=True`)
   as primary; also compute the 100-set for comparison.
2. **Permutation null** = the gene-resampling reading already in the committed code.

Scope note: EZ55 (significant_only) corroboration and the temporal overlay are
**later steps** in this milestone, after we've read the primary result.

Gate: read the real scored table + validation, catch anomalies, then decide.
Critical review (data-integrity + interpretation) runs before the decide gate.

## Do — run manifest (verified against the real files)

Experiment `…690089_…med4_hot1a3_rnaseq` (coculture-vs-**Axenic**, day 11 exp,
DESeq2, all_detected_genes). **3947 genes, sign 54.1% neg / 45.8% pos, 0 dup rows**
→ sign intact, data-integrity clean. 33 modules scored (genome-wide, n_perm=1e4,
seed 0), clean 84-system control set. Artifacts in `analysis/` (scores CSV +
per-system, validation, enrichment guard, 2 figures, cache).

## Results / what the scored table shows (main thread)

**Describe first.** Of 33 candidate carbon modules, **exactly one passes q<0.10:
benzoate** (effect 0.997, p 0.003, q 0.092, **1 system = 1 gene** `ACZ81_03335`,
log2fc **+2.89**). Next: carboxylate (q 0.102), fucose/gal/glucose (q 0.41),
aminobenzoyl-glutamate (q 0.29), carbohydrate (q 0.29). The genuine marine-DOM
candidates sit mid-to-low and **none pass**: the 6-system **polar amino acid** module
is at the neutral median (**effect 0.497**, q 0.99); sugar (4-sys) 0.66/q0.81; amino
acid (3-sys) 0.88/q0.32; peptide/dipeptide/oligopeptide non-sig; branched-chain 0.27.

**Validation — passes on the direction-sanity axis, but the positive controls are
weak** (critic-sharpened). Motility median **0.18** (down ✓ — the clean signal),
ribosomal **0.50** and inorganic controls **0.50** (neutral ✓). But the *positive*
checks under-deliver: peptidases only **0.57** (barely above the 0.50 baseline — the
study's organic-matter-degradation signal did **not** clearly reappear), and `glcB`
is **0.028** (log2fc −1.71, strongly **down** — glycolate not used; soft/uninformative
per plan). So "plumbing works" rests mainly on the motility direction-check; a
near-neutral peptidase signal at *exponential* day-11 is itself consistent with the
"signal under starvation, not exponential" idea. No glycolate uptake module exists.

**Enrichment guard:** KEGG up-over-represented = Purine / 2-oxocarboxylic-acid /
Propanoate metabolism (metabolism maps, not transporters); EC none. All 4 modules
with a dedicated degradation map (branched-chain, benzoate, aminobenzoyl-glutamate,
3-phenylpropionate) read **"tested, not enriched up."**

**Read `[interpretation]` (critic-sharpened).** The primary day-11 presence contrast
shows **no specific coculture-driven organic-carbon _uptake_ signal**: no transporter
module passes q<0.10 except benzoate, which the proposal **pre-registered as an
expected-negative** aromatic. By our own falsifiability bar (aromatics dominating ⇒
not a genuine carbon catalog), the transporter result is **null at this timepoint**.
Three qualifications so this is weighed correctly:
- **Benzoate is a real, strong, correctly-annotated induction, not a scoring/annotation
  artifact.** `ACZ81_03335` = `benE` benzoate/H⁺ symporter, log2fc **+2.89, padj
  2.7e-10** (KG-confirmed, annotation_quality 3). Its low permutation p is partly
  by-construction for a 1-gene module, but the underlying upregulation is genuine — it
  is a real benzoate-transporter induction that simply falls in the pre-registered
  expected-negative class, so it does **not** count as a *Prochlorococcus* carbon
  source under the design.
- **There _is_ up-regulated central-carbon metabolism** — the genome-wide guard found
  2-oxocarboxylic-acid (fold 6.4) and propanoate (fold 6.7) metabolism over-represented
  among up-genes. This is **internal catabolism, not uptake specificity** (no transport
  module passed), so it doesn't name a carbon source — but "no carbon signal at all"
  would over-state it.
- The motility-down check confirms the coculture effect **is** captured, so this is a
  real weak/null *uptake* result, not broken plumbing.

Plausible alternatives `[interpretation]`: carbon-uptake regulation may appear under
**starvation**, not exponential day-11 (→ the temporal overlay, still to run) — the
weak peptidase signal fits this; or uptake is constitutive.

## Decisions (decide gate)

- **Primary (day-11 presence) result accepted as a null/weak carbon-*uptake* finding**
  — critic-vetted (data-integrity clean, no Blockers; 3 interpretation concerns fixed;
  see `critical_review.md`).
- **Proceed (researcher: "1")** to the **HOT1A3 starvation temporal overlay** next
  (reuses the existing HOT1A3 module set; starvation is where carbon-hunger would show).
  Read as difference-of-starvation-responses (corroboration only, per plan).
- **EZ55 queued after** — it is a different strain and needs its **own** transporter
  table (repeat the audit) before it can be scored; sequenced after the temporal
  overlay since it is also a presence contrast (may also be weak).
- Commit held for one analysis-milestone commit (primary + temporal [+ EZ55]).

## Temporal overlay — run manifest / results (verified against the real files)

8 (arm × timepoint) pulls, all `all_detected_genes`/3947 genes, signs 48–53% neg,
intact. Axenic lacks standalone day 60/89 → coculture-specific defined at 3 shared
labels (d18, d31, d60+89). Scored with the same 33 modules + 84 clean controls.

**Coculture-specific-up (up in coculture starvation, not axenic, shared timepoints):**
- **peptide/nickel** — d31 (coc q 0.017) **and** d60+89 (coc q 0.081): most recurrent,
  but its substrate is **ambiguous** (peptide *or* nickel — nickel would be inorganic,
  not carbon).
- **L-lactate** — d31 (coc q 0.017); but up in **both** arms at d60+89 (not
  coculture-specific there); 1-gene module.
- **carbohydrate** — d18 (coc q 0.076): one timepoint, **broad/unresolved** module
  (coarse — per plan, doesn't meet the bar).

**Confound flagged (critic-relevant):** the **ribosomal-neutrality check fails** in the
temporal contrast — ribosomal (Translation) median up-percentile **0.66–0.79 in both
arms** at every timepoint (vs 0.50 in the presence contrast). So the temporal
up-percentile axis is shaped by the **growth-state (starvation) transition**, not a
clean carbon axis; the plan's own negative control does not transfer here. Peptidase
does not trend up; glcB inconsistent (0.08–0.86); motility low from d31 in both arms.

**Read `[interpretation]`.** The temporal overlay gives only **weak, growth-state-
confounded, mostly single-timepoint** coculture-specific ramps. peptide/nickel is the
most persistent but substrate-ambiguous; L-lactate is cleaner but one-timepoint-then-
shared; carbohydrate is coarse. Per the plan, temporal is corroboration-only and cannot
name a source alone — and there is **no presence-contrast hit to corroborate** (primary
was null). So nothing here meets the bar to name a carbon source.

**Combined result across both steps `[interpretation]`:** the KG expression data do
**not** identify specific organic-carbon sources *Alteromonas* uses in coculture with
*Prochlorococcus*. Presence contrast null; temporal weak/confounded/non-reproducible.
The method is validated (motility down, integrity clean), so this is a genuine
**negative / inconclusive** finding, not a pipeline failure.

## EZ55 cross-strain — results (verified against the real files)

EZ55 table built with the same committed pipeline: 599 candidate genes → 539 systems;
54 organic-C importers → **35 modules**. Scored on the two pCO₂ presence contrasts
(`significant_only`, edgeR).

- **400 ppm: 0 modules called up.** Top by effect fucose/gal/glucose (q 0.11), proline
  (q 0.30) — none pass.
- **800 ppm: 1 called up — Fe(3+) dicitrate** (q 0.070, 1 detected system) — which is
  **iron acquisition** (citrate as the iron chelator), classifier-tagged organic via
  "citrate"; effectively an expected-negative, not a carbon source.
- **Cross-arm (pCO₂) agreement: 0.** **Cross-strain overlap with any HOT1A3 candidate: 0.**
- **Severe `significant_only` sparsity:** 28/35 (400) and 32/35 (800) modules have
  **zero** genes in the significant set → unscorable; every scored module rests on a
  single detected system. The data are too thin to be informative — exactly the
  `significant_only` weakness the proposal named.

## FINAL combined result — analysis milestone `[interpretation]`

**The KG expression data do not identify specific organic-carbon sources *Alteromonas*
uses in coculture with *Prochlorococcus*.** Across two strains, three presence
contrasts, and a starvation time course:
- HOT1A3 presence (day 11): **clean null** — genome-wide, well-powered; only benzoate
  (pre-registered expected-negative) passes. *This is the strongest leg.*
- HOT1A3 starvation temporal: **weak and confounded** — peptide/nickel
  [substrate-ambiguous], L-lactate [1 tp then shared], carbohydrate [coarse]; the
  ribosomal-neutrality control **fails** here, so the axis is confounded by growth-state.
- EZ55 presence (400/800 ppm): **underpowered / uninformative, not a clean negative** —
  28–32 of 35 modules had **no** gene in the significant set (unscorable); 0 (400) and 1
  (800) called up, the 1 = Fe-citrate ≈ iron (`fecA`, KG-confirmed inorganic); no
  cross-arm agreement. An underpowered look finding little adds little.
- **No cross-strain agreement on any carbon candidate.** The only FDR-passing hits
  anywhere are the pre-registered **expected-negatives** (benzoate aromatic; Fe-citrate
  iron) — the falsification criterion working as designed.

So the strong, clean result is the **day-11 presence null**; the temporal and EZ55 legs
are weak/confounded and underpowered respectively — they don't add much independent
weight, so the overall finding is best stated as **"no carbon sources named; a clean
null on the best-powered contrast, inconclusive/underpowered elsewhere."** The method is
sound on the well-powered contrast (motility down, data-integrity clean); in the
*temporal* contrast one negative control (ribosomal-neutrality) failed, so "validated"
applies to the presence contrast, not the temporal one. A well-posed question, a working
method on adequate data, and data that do not support naming carbon sources — with faint,
non-reproducible, confounded hints (peptides/lactate under starvation) below the plan's bar.

## Decisions (analysis milestone)

- Primary + temporal + EZ55 all done and read. Combined result = **no carbon sources
  named**: a clean null on the best-powered contrast (day-11 presence), inconclusive
  (temporal, confounded) / underpowered (EZ55) elsewhere.
- Critic over the full delta (temporal + EZ55): **clean, no Blockers**; 2 wording
  concerns fixed (EZ55 "null"→"underpowered"; keep "inconclusive" beside the negative;
  "validated" scoped to the presence contrast). See `critical_review.md` second pass.
- **Analysis milestone ready to close** → one commit, then the evaluation milestone.
- **EZ55 decision (researcher): B — build the EZ55 transporter table + score it** for
  cross-strain completeness (accepting it will likely also be weak/null). EZ55 = a
  different strain (own table) scored on the two pCO₂ presence contrasts (400/800,
  `significant_only`, edgeR); per the plan the two pCO₂ arms count as **one**
  strain-partner support with pCO₂ agreement as an internal consistency check.
- Then re-run the critic over the full analysis delta (temporal + EZ55) and close the
  milestone.
