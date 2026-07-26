# Analysis milestone — critical review

Fresh-context critic (data-integrity + interpretation, the heavy gate), 2026-07-26.
Scope: `analysis/` only; `proposal.md`, `methods/scoring.py`, `parts_list_v2.csv` trusted
inputs. Ran scripts, recomputed BH by hand, spot-checked DE against the KG.
Verdict: **no Blockers; 3 Concerns + 1 Note, all interpretation.**

## Data-integrity — verified clean (critic's own words)
Every number reconciled against the files and the KG: DE staging/signs (3947, 54.1% neg,
111/163; EZ55 419→308/111, 188→104/84); KG spot-check of 4 anchors (18130 +3.53, benE
+2.89, 06075 +2.32, glcB −1.71) exact; HOT1A3 BH q's recomputed (carb-MFS 0.060, benzoate
0.090, citrate 0.101) correct; EZ55 q's (fucose 0.085, acetate 0.046) correct; **benE
genuinely absent from both EZ55 significant sets**; control contrast, temporal q's,
breakdown flags, validation, enrichment guard all match; refinements applied consistently
across strains. No sign errors, no wrong q's, no false counts.

## Concerns (all interpretation; all addressed by re-wording — no re-run)

### Concern 1 — the two "reproducible classes" are asymmetric; synthesis flattened them
**Critic:** Sugars = 2 *presence* contrasts / 2 strains (carb-MFS q=0.060 + fucose q=0.085);
organic acids = **1 presence** arm (acetate 800) + **1 temporal** line (lactate, weighted
below presence per the proposal) with HOT1A3 presence citrate **just-missing** (0.101).
Don't present them as symmetric.
**Disposition — FIXED.** Synthesis reworded: sugars = best-supported (2 presence/2 strains);
organic acids = weaker (1 presence + temporal; HOT1A3 just-misses). Composition travels.

### Concern 2 — EZ55 q<0.10 is a 3–5-module FDR family, not comparable to HOT1A3's 46
**Critic:** EZ55 permutation p's (fucose 0.017, acetate 0.0155) clear q<0.10 only within a
tiny family; in a 46-module family they'd give q≈0.7. "q<0.10 in both strains" implies a
parity the family sizes don't support; the comparable quantity is the within-experiment
permutation p.
**Disposition — FIXED.** Added to the notebook: EZ55 q<0.10 is within a 3–5-module family;
the comparable cross-experiment quantity is the permutation p, not the family-size-dependent
q. The **compound-class aggregation** (exploration below) is the more robust cross-experiment
read, being family-size-independent.

### Concern 3 — the aromatic dismissal is convenient
**Critic:** benE is the **#2 hit in the primary, fully-rankable experiment** (q=0.090) — a
real partial hit of the expected-negative — resolved only by EZ55 non-reproduction of the
*transporter*; meanwhile aromatic *catabolism* is up in EZ55-800 (ko00362 padj 0.007,
ko01220 padj 9.5e-8). Aromatic metabolism appears in both strains, on different genes.
"Does not survive" is over-confident.
**Disposition — FIXED.** Reworded: benE is HOT1A3-specific and never forms a coherent
transporter+catabolism unit in one strain/condition → aromatics not a supported carbon
source, but the expected-negative is a **partial complication**, not cleanly falsified.

### Note — EZ55 pCO₂ arms disagree on aromatic-catabolism direction
**Critic:** benA/B/C down in EZ55-400 (l2fc −1.3 to −1.7), up in EZ55-800 (+1.0 to +1.5);
the "pCO₂ agreement is internal" framing doesn't surface this disagreement.
**Disposition — FIXED.** Added to the confounds/limits: the two pCO₂ arms disagree on the
aromatic genes, tempering the internal-consistency framing.

## Summary
No Blockers — the computed results are sound and verified against the KG. The milestone's
fix was entirely interpretive: stop the synthesis from flattening a genuinely asymmetric,
thin, class-level result into symmetric "reproducible across strains," and soften the
aromatic falsification claim. All applied by re-wording the synthesis; the researcher-
requested **compound-class aggregation** (see notebook) makes the honest, family-size-
independent picture the lead — sugars + nucleosides foremost (enrichment-corroborated),
amino-acids conspicuously not up, organic acids weaker.

---

## Delta review — exploration additions (2026-07-26)

Second fresh-context critic over ONLY the post-critic exploration delta (control scoring +
figs D–H, E2 + the two new caveats), with the already-reviewed analysis as trusted input.
**Verdict: 1 Blocker, 2 Concerns, 2 Notes** — all fixed by re-wording/re-rendering, no
recomputation. The control scoring (`08_score_controls.py`) came back **clean** (correct
reuse of the committed scorer on the control reference-subset; cited medians reconcile:
control-ABC @ HOT1A3 d11 0.590/0-of-16, late-axenic controls elevated, nitrate q=0.003).

### Blocker (data-integrity) — Fig F caveat cited a wrong number that inverted the module
**Critic:** notebook said "L-lactate RNA≈1.0 / protein≈0.03." Verified false — L-lactate
coculture protein is **0.58–0.89** (agrees with RNA); the 0.03 is **cation/acetate**. Worse,
the whole "protein compressed / RNA and protein disagree" framing is wrong: proteomics median
**0.82 ≥ RNA 0.76**, protein ≥ RNA in ~12–15/22 modules; proteomics reaches 0 q<0.10 because
it is **underpowered**, not discordant (absence of evidence).
**Disposition — FIXED (main-thread-verified the numbers).** Fig F title, notebook caveat,
synthesis line, and paper Fig 7 caption all reworded to "proteomics underpowered — neither
confirmed nor refuted"; the wrong L-lactate example replaced with the correct acetate one
(and L-lactate noted as protein-agrees). Re-rendered Fig F.

### Concern (interpretation) — Fig G over-reach ("sugars reproduce" / "strain-specific")
**Critic:** "sugars reproduce" glosses that **carb-MFS (top HOT1A3 hit) collapses to 0.44 in
EZ55 and maltose 0.69→0.22 don't** — sugars are 2-of-4; and "organic acids strain-specific"
rests on **n=1** (acetate).
**Disposition — FIXED.** Fig G title, notebook caveat, synthesis, and paper Fig 8 caption
reworded: reproducibility is *partial and class-level* (fucose/porin), carb-MFS/maltose
non-reproduce, acetate anti-correlation is n=1 ("consistent with, not establishing").

### Note — "iron uniformly up" overstates (4/11 down at HOT1A3 d11)
**Disposition — FIXED.** → "predominantly up" in notebook Fig E2 bullet + paper Fig 6 caption.

### Note — amino-acid count 15 (Fig A) vs 14 (Fig D), classifier keyword difference
**Disposition — FIXED.** Notebook notes the two scripts' classifiers differ by one borderline
system; the load-bearing claim (largest class, median 0.38, not induced) is unaffected.

**Summary (delta).** The exploration's underlying computation (control scoring) is sound; the
failure was interpretive — I over-read the RNA/proteomics figure into "discordance" (it is
underpowered) and over-sold "sugars reproduce" (2 of 4). Both are now stated conservatively;
the honest version already existed elsewhere in the paper ("proteomics detected no up-modules").
No recomputation needed.
