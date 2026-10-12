# Analysis milestone — critical review (2026-10-12)

**Scope.** `analysis/`: notebook, the review pages, `data/`, `scripts/`, `figures/`. Trusted inputs: the
proposal, `methods/` and `gaps_and_friction.md`.

**Lens.** Data-integrity + interpretation. Fresh-context critic.

**Result.** 2 Blockers, 10 Concerns, 4 Notes.

**What checked out.** The data plumbing is clean: every rank percentile recomputes exactly, pooled
slices are excluded, and filtered tables are flagged. The quoted numbers reproduce: sanity gate,
P1/P2, E1, E2, E7 (identity to 1.8e-15), E8, E9, E11. The findings concern the claims built on that
data. Dispositions were applied in E14 (code/figures) and in the notebook and pages (wording); the
researcher approved the revised reading on 2026-10-12.

---

**B1. Blocker: "cell envelope = coculture-specific" ignored axenic d31/d89.**
The coculture-specific flag checked only axenic d14 protein. The porin `som` is significantly up in
axenic protein d31 (0.99) and d89 (0.88) and in axenic RNA d14 (0.95); likewise `yrbG` and `dppC`.
**Disposition: fixed (E14).**
- The flag now requires "not up" in axenic protein d14/d31/d89, axenic RNA d14 and Tolonen.
- Strict ★ went from 12 to 6: `murJ`, `tolC`, `acrA`, `bamA`, `perM`, `mgtE`.
- `som` and `yrbG` are relabelled "up in coculture and in dying axenic · not specific".
- The reading now names `murJ` (and, more weakly, `tolC`/`acrA`/`bamA`), and says every axenic
  contrast is with a declining culture.
- E11 knock-on: `ureC` and `ispA` drop out; only `sppA` passes.

**B2. Blocker: dpp "slow starvation response" rested on axenic RNA vs coculture protein.**
In the axenic culture's own protein, `dppA` never rises (0.76 ns → 0.17 significantly down at d31).
dpp is outside the N-starvation branch and never responds in Tolonen deprivation.
**Disposition: fixed.**
- dpp is "up in coculture protein · unresolved", in the reading, the notebook, the pages and e13.
- The "protein lags RNA" sentence is removed.

**C1. Concern: "track N status, not substrate" over-reached.**
On MED4 cyanate only `cynA`, `urtA` and `glnA` are significant; `amt1` (0.38) and `ntcA` (0.48) are not.
`amt1` and dpp were never calibrated. The MIT9313 urease difference is between non-significant
values.
**Disposition: fixed.**
- Narrowed to "specificity fails for urt, cyn and focA, so expression can't report the compound;
  amt1 was not calibrated".
- The significant genes are named. The urease claim is softened.

**C2. Concern: the envelope list promoted the notebook's own "weaker candidates", and devBCA rests on
1 of 3 subunits.**
**Disposition: fixed.**
- "More weakly `tolC`, `acrA`, `bamA`" (already high in axenic d14).
- devBCA is dropped from the reading.
- Per-subunit carriers are listed in `e10_flags.csv` (`cc_up_subunits`).
- The different-reference limitation for protein is stated: each culture against its own
  exponential phase, and there is no protein direct contrast.

**C3. Concern: "the d11 baseline explains most of the protein/RNA mismatch".**
A raised baseline explains near-zero log2FC, not a decline below it. The protein side of the d11
baseline is unmeasured.
**Disposition: fixed.**
- Now "contributes to".
- Both arms' references are their own d11 samples.
- Researcher addition: the d18 RNA contrast mainly reflects the axenic decline (877 vs 84
  significant genes).

**C4. Concern: iron hint "raised in protein and RNA".**
The RNA part is contradicted: c19 RNA is lower in coculture (0.72 / 0.73) than axenic (0.77).
**Disposition: fixed.** Protein-only, with the `hli`/`cynA` membership and 20/59 detection stated.

**C5. Concern: "no sign of damping" at a percentile ceiling.**
**Disposition: fixed.** Now "no damping detectable at the percentile ceiling", with the marker
log2FC trend reported (E14: `ntcA` 2.23 → 1.17, `glnB` 2.11 → 3.30).

**C6. Concern: "no other route" silently dropped clc2, moved murJ, and missed PMM0561 RNA. The
reading used E4, which decision 4 made exploratory.**
**Disposition: fixed.**
- `clc2` (nitrate, unusable), `murJ` (envelope) and PMM0561 (RNA up, protein not) are named in the
  reading and in e13.
- E4 is labelled exploratory.

**C7. Concern: e13 mixed protein and Tolonen microarray RNA on one axis.**
**Disposition: fixed.**
- Panel A is protein only, adding axenic d31/d89.
- Tolonen RNA has its own column.

**C8. Concern: "12 ★" was 11 ★ + 1 ☆.**
**Disposition: fixed.** The notebook marks the first pass as superseded; the current count is 6 ★
+ 3 ☆ (E14).

**C9. Concern: stage 4 (per-class reads for other strains) dropped without disclosure.**
**Disposition: disclosed.** Decision 7: covered partly by expected-negative 2 and E8; the per-class
tables move to the contrast analysis.

**C10. Concern (E9 part): the iron RNA claim, as in C4.** **Disposition: fixed** with C4.

**N1. Note: the E7 identity also implies each arm's reference is its own d11 sample.**
**Disposition: stated** (notebook RNA paragraph; decision 5).

**N2. Note: the "markers" set includes `pipX` in E1/E3/E7/E11.**
**Disposition: disclosed.** `markers_set` column added (E14); e13 uses `glnA`/`ntcA`/`glnB`.

**N3. Note: stale text** ("exploration below"; script list e1…e7; early "partial relief" and dpp
readings).
**Disposition: fixed or marked superseded.** Earlier exploration paragraphs are kept as the record,
with dated corrections beneath them.

**N4. Note: sul1/sul3 counted as both non-N reference and broad N.**
**Disposition: disclosed** in the README; no conclusion depends on it.
