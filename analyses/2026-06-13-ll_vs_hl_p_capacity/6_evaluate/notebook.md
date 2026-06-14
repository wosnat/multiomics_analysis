# Step 6 — Evaluate

## Context

Adjudicate the three preregistered predictions (step 3) against the step-5
results, harvest caveats, and finalize `paper.md`.

## Preregistered predictions — verdicts

**Prediction 1 (more): LL focused-acquisition count > HL, ratio above the
ribosomal and nitrogen baselines.** → **Not supported (as a robust effect).**
LL/HL = 1.12 is technically above ribosomal (1.00) and nitrogen (0.98), but the
excess is small, per-1000-genes HL is denser (6.6 vs 5.8), and the difference is
**entirely LLIV-driven** — dropping the two LLIV strains gives LL/HL = 0.95. LLI
and LLII carry no more P-acquisition OGs than HL. The raw count excess is a
genome-size effect localized to one clade, not an LL-wide capacity advantage.

**Prediction 2 (different): ≥1 acquisition OG LL-present/HL-absent (ptrA, phoC,
ppk2).** → **Supported, with structure.** `ptrA` (Crp-family transcriptional
phosphate regulator) is present in 4/5 LL and 0/4 HL — a genuine, LL-wide
qualitative marker (LLI, LLII, and one LLIV). `phoC` (acid phosphatase), `ppk2`
(polyphosphate kinase), a PAP2-superfamily phosphatase, and a PsiE-like protein
are LL-only but LLIV-confined (MIT9303 + MIT9313 only). So LL strains do carry P
machinery HL lack — a regulator genome-wide, and scavenging/storage in LLIV.

**Prediction 3 (P-specific): the P difference ≥ trace-metal and > nitrogen.** →
**Not supported.** Focused-P LL/HL (1.12) is below trace-metal (1.14) and equal to
light (1.12); only nitrogen (0.98) is lower. The count-level LL adaptation
expansion is shared across several adaptation categories (P, trace-metal, light)
and is not phosphorus-specific. (As flagged at preregistration, full-role P ≈
trace-metal already foreshadowed this.)

## Answer to the research question

*Are LL Prochlorococcus ecotypes better equipped at the genome level to handle P
limitation?* `[interpretation]`

- **By quantity of acquisition machinery: no.** No robust, P-specific, LL-wide
  excess of P-acquisition ortholog groups. The small raw difference is genome-size
  (LLIV) and is matched by other adaptation categories.
- **By repertoire: partially, and largely clade-specific.** LL strains carry a
  phosphate regulator (`ptrA`) that HL lack (LL-wide); the LLIV clade additionally
  carries acid phosphatase, polyphosphate kinase, and extra phosphatases absent in
  HL. So a qualitative regulatory/scavenging difference exists, strongest in LLIV,
  rather than a broad "more transporters" advantage.

This is consistent with the Martiny et al. (2006) finding that *Prochlorococcus*
P-gene content tracks the source-water phosphorus regime more than the HL/LL
light ecotype: here the sharpest differentiation is clade-level (LLIV) and
regulatory, not a clean LL-vs-HL acquisition-capacity gradient. `[interpretation]`

## Caveats (harvested)

1. **Tiny, imbalanced, MCP-restricted panel (4 HL, 5 LL).** Forced by the
   `genes_by_ontology` resolver bug (only 9 of 17 Cyanorak-annotated strains
   resolvable). LLIV findings rest on 2 strains; LLII on 1 (SS120). The full
   17-strain panel (9 HL, 8 LL) re-run is the priority follow-up post-bugfix.
2. **LLIV genome-size confound.** LLIV strains have the largest genomes; their
   elevated P-OG count co-occurs with genome-wide expansion. Only the LLI/LLII
   `ptrA` presence is clearly *not* a size artifact.
3. **Asymmetric controls.** Focused-P is a curated 23-OG subset; the N/trace-metal
   controls are full Cyanorak roles. The ribosomal invariant baseline (1.00) and
   the qualitative repertoire findings are robust to this, but the fine specificity
   ranking (P 1.12 vs trace-metal 1.14) is not — a matched comparison would curate
   each control identically. Logged in `gaps_and_friction.md`.
4. **Presence ≠ function.** Genomic presence does not establish the genes are
   expressed or functional under P limitation; the genomic-capacity framing is
   explicitly upstream of the expression-response question (deferred at step 1).
5. **Subset-definition judgment.** The 23-OG focused subset involved curation
   (borderline phosphatases included by researcher call); robustness to subset
   definition was not formally swept.
6. **`ptrA` absent in MIT9313**, the best-studied LL strain — a caution against
   over-generalizing the LL-wide marker.

## Decide-gate checklist

- **Outputs produced:** this evaluation `notebook.md`; `paper.md` Discussion +
  References finalized. (No new scripts/data — step 6 is assessment.)
- **Results presented:** prediction verdicts (1 not-supported, 2 supported,
  3 not-supported), question answer, 6 caveats (above).
- **QC gate:** verdicts trace to step-5 frozen numbers (LL/HL 1.12; drop-LLIV
  0.95; ptrA 4/5 LL vs 0/4 HL); no claim exceeds the data.
- **Advance rationale:** predictions adjudicated, caveats harvested, paper
  complete — analysis closed.
