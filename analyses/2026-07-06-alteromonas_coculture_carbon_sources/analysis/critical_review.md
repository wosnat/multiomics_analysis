# Analysis-milestone critical review

Fresh-context critic, **data-integrity + interpretation** lens, over the `analysis/`
folder only (proposal + methods = trusted inputs). 2026-07-12.

**Data-integrity dimension: CLEAN.** Every headline number reproduced against the
files: `de_table.json` 3947 genes, 54.1% negative (sign intact); benzoate row
effect 0.997 / p_perm 0.0028 / q 0.0924 / called_up True / 1 system; exactly one
module q<0.10; benzoate gene `ACZ81_03335` log2fc +2.89 / padj 2.7e-10; validation
medians (motility 0.184, ribosomal 0.504, peptidase 0.565, inorganic 0.503, glcB
0.028); enrichment-guard params match the proposal; all 3947 genes scored, no
duplication. **KG spot-check:** `ACZ81_03335` = `benE` benzoate/H⁺ symporter,
annotation_quality 3 — a genuine, confident benzoate transporter, not a
misannotation. **No Blockers.**

### Concern 1 (interpretation) — "single-gene artifact" framing conflates scoring with biology
**Critic:** the notebook called benzoate a "single-gene artifact / curiosity," but the
KG + `de_meta.json` show it is a bona-fide benzoate/H⁺ symporter induced **+2.89, padj
2.7e-10** (top-of-genome). Its low permutation p is partly by-construction for a 1-gene
module, but the induction is real, strong, and correctly annotated — not an artifact.
**Disposition — FIXED.** Reworded the notebook read: benzoate is a **real, strong,
correctly-annotated benzoate-transporter induction** that falls in the pre-registered
expected-negative class (so it does not count as a *Prochlorococcus* carbon source),
**not** noise/artifact. The pre-registered falsification reading is retained.

### Concern 2 (interpretation) — positive controls weak; "plumbing works" leans on motility
**Critic:** peptidases 0.565 (barely above 0.500) — the study's organic-matter-
degradation signal did not clearly reappear; glcB down (0.028). Only the negative-
direction motility check (0.184) landed clean. "Validation plumbing works" over-weights
the one clean hit.
**Disposition — FIXED.** Notebook now states validation passes on the direction-sanity
axis (motility-down) but the **positive controls are weak** (peptidase near-neutral,
glcB down), and notes a near-neutral peptidase at exponential day-11 is itself
consistent with the "signal under starvation" hypothesis.

### Concern 3 (interpretation) — up-regulated central-carbon metabolism glossed by "no carbon signal"
**Critic:** the guard found 2-oxocarboxylic-acid (fold 6.4) and propanoate (fold 6.7)
metabolism over-represented among up-genes — carbon-metabolism maps. "Essentially no
organic-carbon signal" reads too absolute.
**Disposition — FIXED.** Notebook now scopes the null claim to **uptake** and adds that
central-carbon *metabolism* is up-enriched — framed explicitly as internal catabolism,
not uptake specificity (no transport module passed), so it doesn't name a source.

### Note — scoring presentation (effect-sort favours 1-system modules)
Catalog sorted by MAX system-percentile puts 1-system modules on top; decisions
correctly rest on **q**. The carboxylate near-miss (q 0.102) is a coarse
substrate-unresolved module → reinforces the null per the proposal's "coarse modules
don't meet the bar." **Disposition — noted**; decisions rest on q, not effect rank.

### Note — peptidase count 94 vs 93 (one gene lacks a DE row). Trivial. **Noted.**

**Summary.** No Blockers; data-integrity clean; three interpretation concerns fixed
inline (benzoate is a real induction not an artifact; validation is direction-sanity-
only with weak positives; central-carbon metabolism is up but is not uptake). The core
conclusion — **null/weak carbon-*uptake* at day-11, only the pre-registered
expected-negative passing q<0.10** — is well-supported and honestly falsifiable.

---

## Second pass (2026-07-12) — temporal + EZ55 delta

Re-dispatched over the newly-added temporal overlay and EZ55 files (the primary day-11
run + proposal + methods = trusted inputs). **Data-integrity: clean, no Blockers** —
every delta number verified: temporal coculture-specific calls (peptide/nickel d31
q0.0165 + d60+89 q0.0808; L-lactate d31 only, shared at 60+89; carbohydrate d18 only),
all 8 pulls all_detected_genes with 48–53% neg signs, ribosomal 0.66–0.79 both arms
(the confound); EZ55 400ppm 0 up / 800ppm 1 up (Fe-citrate q0.070), sparsity 28/35 and
32/35 unscorable, cross-arm 0. **KG-confirmed** the EZ55 hit `EZ55_02117` = `fecA`
K16091 TonB-dependent ferric-dicitrate transporter, gene_category "Inorganic ion
transport" — iron acquisition, the "organic" tag a spurious "citrate" match.

### Concern A (interpretation) — "robust negative" leans on the day-11 null alone
**Critic:** the robustness is carried by the trusted, well-powered primary null; the
EZ55 leg is underpowered and the temporal axis is confounded (ribosomal control fails),
so they add little independent weight. **Disposition — FIXED.** Reframed: the clean,
well-powered result is the day-11 presence null; temporal = weak/confounded, EZ55 =
underpowered. Overall stated as "no carbon sources named; clean null on the best-powered
contrast, inconclusive/underpowered elsewhere," with "inconclusive" kept attached.

### Concern B (interpretation) — EZ55 "null" overstates an underpowered look
**Critic:** pairing "null" with "too sparse to score" (28–32/35 modules unscorable) is
near-contradictory — an underpowered result is not a clean negative. **Disposition —
FIXED.** EZ55 relabelled **underpowered / uninformative**, not null, in the combined read.

### Note — "method is validated" is strong for the temporal contrast
The temporal contrast's ribosomal-neutrality control failed, so "validated" is scoped to
the presence contrast. **Disposition — FIXED.** Notebook now scopes it.

**Summary (second pass).** No Blockers; data-integrity clean across the whole delta
including a KG annotation check; interpretation was already well-hedged, tightened only
so the one-line summaries don't read stronger than the evidence. The analysis milestone's
finding stands: **no carbon sources named — a clean null on the best-powered (day-11)
contrast, inconclusive/underpowered on the corroboration legs**, the only FDR hits being
the pre-registered expected-negatives.
