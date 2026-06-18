# Step 6 — Evaluate

## Assessment against the step-3 framing

**Target — extruded OG catalogue:** delivered. 318 measured genes → 145
Alteromonadaceae-level eggnog OGs, with route, recurrence, per-strain locus tags
(`5_analyze/data/extruded_og_catalogue.csv`).

**Hypothesis** (step 3): "a core set of OGs is extruded recurrently across strains
and/or by both routes (conserved functions — OM transporters, hydrolases), against a
tail of strain/route-specific OGs."
- **Recurrence-across-strains: supported.** 71 of 145 OGs recur in ≥2 strains; the
  vesicle route has a 6-OG core present in all 6 strains.
- **Both-routes = conserved function: NOT supported as framed.** The 25 both-routes
  OGs are structurally EZ55-anchored (secreted = EZ55 only) and 23/25 are cytoplasmic
  by annotation — an abundance/contamination signal, not conserved secretion machinery.
- So the hypothesis splits: the conserved-recurrence reading holds (vesicle envelope
  core); the dual-route-core reading was an artifact of coverage + abundance.

**Positive control (TonB-dependent receptors):** passed — present in the extruded
catalogue, top vesicle cargo.

**Negative/honesty check:** cytoplasmic contamination was visible and flagged
throughout (translation 30–39% of both routes; both-routes core 23/25 cytoplasmic).

**Expected outcome:** ranked OG table ✓; TonB among top vesicle ✓; a both-routes core
✓ (reinterpreted as contamination); cytoplasmic contamination visible ✓.

## Researcher-driven extensions (beyond the original framing)

- Secreted vs vesicle category profiles; cross-route corroboration; cross-strain
  vesicle agreement (conserved envelope-enriched core).
- Exoenzyme analysis: which extruded proteins break down organic compounds.
- Genome-wide background: is the extruded set enriched for exoenzymes? (No.)

## Final exoenzyme deliverable (verified)

Manual KG verification of the 3 protein/peptide candidates resolved the flagged one:
`ALTBGP6_03431` is a TonB-dependent **siderophore receptor** (transporter); its
"carboxypeptidase activity" GO term derives from the non-catalytic PF13620
"Carboxypeptidase regulatory-like domain" — a false positive, dropped.

**Verified extruded exoenzymes — 3 OGs (8 genes):**
| Function | OG / enzyme | Route | Strains | Locus tags |
|---|---|---|---|---|
| organic-P scavenging | PhoX alkaline phosphatase | vesicle | all 6 | MIT1002_02422, AMBLS11_11110, MASE_11260, ALTBGP6_02414, AMBAS45_11875, ACZ81_11825 |
| proteolysis | DegQ serine endoprotease (EC 3.4.21.107) | secreted | EZ55 | EZ55_00820 |
| proteolysis | M1 family aminopeptidase | secreted | EZ55 | EZ55_04077 |

`[KG-verified]` So the automated pipeline's count of 4 OGs → **3 verified** (the figure
`exoenzyme_og_level.png` shows the automated 4; the captured-OG count is 3 after this
manual QC). Classifier limitation logged: a GO-MF "carboxypeptidase activity" term
sourced from PF13620 (a regulatory-like domain) is not caught by the name-based
exclusion, which only filtered the Pfam-level "...regulatory-like domain" string.

## Caveats harvested into paper.md Discussion

1. Vesicle lists are `top_n` (15–58/strain) — recurrence/agreement are lower bounds.
2. Secreted route is EZ55-only — no within-strain dual-route comparison; "both routes"
   is EZ55-anchored.
3. Extruded fractions dominated by abundant cytoplasmic proteins (lysis/co-purification
   vs genuine cargo unresolved).
4. Exoenzyme set is annotation-bound (Pfam load-bearing; genes with no functional term
   invisible) — a conservative lower bound.
5. Genome denominator includes intracellular signaling enzymes (c-di-GMP PDEs etc.)
   not given the extruded set's false-positive QC — per-substrate genome pools are
   upper estimates; the tier-A "not enriched" conclusion is robust to it.

## Decide

- [x] Results assessed against step-3 framing (hypothesis split: recurrence supported,
      dual-route-core not)
- [x] Exoenzyme deliverable verified (3 OGs; #3 dropped as KG-verified false positive)
- [x] Caveats harvested; paper.md finalized (Background/Methods/Results/Discussion/Refs)
- [x] Interpretation-only critic run: no Blockers, 2 Concerns + 2 Notes, all fixed →
      `critical_review.md` (de-cleaned the vesicle core in Discussion; carried the
      EZ55-anchoring confound into the division-of-labour claim; softened "not enriched")
- [ ] Researcher approves → commit (closes step 6 / analysis)
