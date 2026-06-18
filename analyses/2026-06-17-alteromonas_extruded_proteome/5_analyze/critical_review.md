# Step 5 — Critical review (data-integrity + interpretation)

Fresh-context critic, reviewing only `5_analyze/` files cold. **No Blockers.**
Data-integrity dimension came back clean — every count, the recurrence table, the
secreted funnel (234→69, confirmed non-truncated against the live KG), unmapped=0,
and the both-routes composition reproduce exactly from the data files. Two
interpretation Concerns and two Notes; all accepted.

---

## Concern · interpretation — TonB "vesicle-route" generalization

> Claim/location: notebook.md — "7 TonB-receptor OGs ... They are vesicle-route and
> strain-diverse"
> Problem: 1 of the 7 TonB OGs is secreted, not vesicle. In
> `data/extruded_og_catalogue.csv`, `eggnog:465WA@72275` (TonB-dependent receptor,
> EZ55_02282) has routes="secreted". The other 6 are vesicle. The "vesicle-route"
> generalization fails on one row. (The "recurrence ≤ 2 strains, each pair distinct"
> sub-claim is correct.)
> Recommendation: Reword to "6 vesicle-route and 1 secreted (EZ55)".

**Disposition: fixed.** Reworded to "6 are vesicle-route and 1 is secreted (EZ55,
`eggnog:465WA@72275`)". Rule 9 violation (unverified "all") — correctly caught.

---

## Concern · interpretation — "both routes" is structurally confounded with EZ55

> Claim/location: notebook.md — the "both-routes core" framing (25 OGs)
> Problem: Secreted is measured on EZ55 ONLY, so both_routes (len(routes)==2) can
> only be reached by an OG that EZ55 secretes AND that some strain puts in MVs. All
> 25 both-routes OGs contain EZ55. "Both routes" does not mean a gene seen leaving
> the cell by two independent routes in the same strain. The abundance-driven reading
> is therefore the leading explanation by construction. The notebook lists abundance
> as reading #1 but does not flag that the both-routes set cannot, by design,
> separate route-co-occurrence from EZ55-centricity.
> Recommendation: Add one sentence noting secreted=EZ55-only makes "both routes"
> EZ55-anchored, so cross-route co-occurrence is not strain-independent evidence of
> dual extrusion.

**Disposition: fixed.** Added a "Structural confound — both routes is EZ55-anchored"
paragraph stating both_routes = EZ55-secreted ∩ (any strain's MV cargo), that all 25
contain EZ55, and that the abundance reading is leading by construction. This is the
single most important framing correction; carry it into step 6 so the deliverable
does not present "both-routes core" as dual-route biology.

---

## Note · data-integrity — "~11/~11/~3" understates precision; bacterioferritin binning

> Problem: The counts are exact (11/11/3), not approximate. "bacterioferritin" is
> binned as envelope-plausible but is cytoplasmic iron-storage; moving it makes the
> split 11/12/2. Does not change the "dominated by cytoplasmic" conclusion.
> Recommendation: Drop the "~"; note bacterioferritin is cytoplasmic.

**Disposition: fixed.** Dropped the tildes; moved bacterioferritin to "other
cytoplasmic"; split is now 11/12/2 → 23 of 25 cytoplasmic, 2 envelope.

---

## Note · interpretation — max recurrence = 6 is a structural ceiling

> Problem: Correct and already honest — the parenthetical notes secreted contributes
> only EZ55. Flagging that the ceiling of 6 is a coverage artifact, not biological
> saturation. No change required.

**Disposition: accepted, no change.** Wording already attributes the ceiling to
route/strain coverage.

---

**Verdict (critic, verbatim):** No Blockers. Data-integrity essentially clean. The
one thing to fix before the decide gate is the interpretation confound — secreted is
EZ55-only, so all 25 both-routes OGs are EZ55-anchored and "two routes" is not
strain-independent evidence of dual extrusion. Positive control genuinely passes
(7 TonB OGs present, recurrence/distinct-pair claims verified).

---
---

# Step 5 — Critical review, PASS 2 (expanded follow-ons)

Re-ran the fresh-context critic over the follow-on analyses added after pass 1
(secreted profile, vesicle agreement, exoenzymes extruded + genome + OG-level).
Lens: data-integrity + interpretation. The pass-1 catalogue was a trusted input,
not re-audited. **No Blockers.** Every headline number reproduced from the CSVs; the
central "not enriched" conclusion survives (robust via the tier-A comparison). Two
data-integrity Concerns, one interpretation Concern, two Notes — all accepted.

## Concern · data-integrity — "52 CAZyme OGs" conflates substrate class with annotation source

> The "52" is OGs whose substrate class is `carbohydrate` (mostly via EC 3.2), NOT
> CAZy-database OGs. Only ~11 OGs carry a CAZy token; calling the 52 "CAZyme OGs"
> conflates substrate class with annotation source. The 52-vs-0 capture gap is
> unaffected.

**Disposition: fixed.** Reworded to "52 carbohydrate-substrate OGs (mostly EC 3.2,
~11 via CAZy)" in both the genome and OG-level sections.

## Concern · data-integrity — genome denominator never got the false-positive QC

> The 1,918-gene genome set admits intracellular signaling enzymes as "exoenzymes":
> ~105 c-di-GMP phosphodiesterases (GO-MF "cyclic-guanylate-specific phosphodiesterase
> activity"), phosphoprotein/phosphotyrosine phosphatases, chemotaxis CheX, plus
> structural-domain hits (YPEB propeptide, inter-alpha-trypsin) — mostly classified as
> organic phosphate. The 9-gene extruded set got false-positive QC; the 1,918-gene
> genome set did not. Mitigating: 98/105 c-di-GMP genes are tier B, so tier A (1,092)
> barely moves; cleaning the denominator only lowers the genome rate → extruded looks
> even less enriched, so "not enriched" is robust. But the organic-P pool (335) and
> "broad arsenal" framing are inflated.

**Disposition: accepted as caveat (per critic's own recommendation — caveat, not
re-run).** Added a "denominator hygiene" caveat to the genome section naming the
c-di-GMP / signaling contamination; softened "broad arsenal" → "broad degradative
repertoire (upper estimate)". The classifier's false-positive QC was applied to the
extruded deliverable (the 9→4 candidates, the actual answer); the genome set is a
background control and is now explicitly caveated. A cleaned re-run is optional for
step 6 and would not change the conclusion.

## Concern · interpretation — vesicle all-6 "core" over-labelled as OM/secretion

> The all-6 core is 6 OGs: TolC (OM), OmpA (OM), MotA/TolQ/ExbB (inner-membrane proton
> channel, not OM/secretion), PhoX (periplasmic), glutamate–ammonia ligase (cytoplasmic
> glutamine synthetase), DUF3450 (unknown). The sentence cited 4 of 6 and called them
> "genuine OM/secretion machinery"; 2 of 6 are not envelope, and the cytoplasmic
> glutamine synthetase re-introduces the abundance/lysis confound.

**Disposition: fixed.** Reworded the interpretation to describe the core as mixed
(2 OM, 1 IM channel, 1 periplasmic, 1 cytoplasmic, 1 unknown), envelope-enriched but
not uniformly secretion machinery; the envelope members (TolC, OmpA, PhoX) are the
defensible signal.

## Note · data-integrity — phytase false-negative reason mis-stated

> MIT1002_00601 has NO Pfam/EC/GO-MF/CAZy term (only COG + signal peptide), so it
> didn't classify because it has no functional annotation at all — not because
> "identity lives only in Pfam." The lower-bound conclusion stands; the reason was wrong.

**Disposition: fixed.** Reworded: the classifier reads annotations not product names,
and this gene carries no functional term, so it's unreachable.

## Note · data-integrity — OG-level source/export breakdowns are stdout-only

> The EC/Pfam/GO-MF/CAZy and export-evidence breakdowns are printed to stdout, not in
> a CSV; not independently checkable from committed artifacts.

**Disposition: fixed.** Added a note that these aggregate the `func_evidence` /
`export_evidence` columns in `exoenzyme_genome_candidates.csv`, so they are
recomputable from committed data.

**Verdict (pass 2, critic verbatim):** No Blockers. data-integrity reproduces but with
the CAZyme mislabel + genome-denominator Concerns and two Notes; interpretation has one
Concern (over-stated vesicle core), with the enrichment and capture-gap conclusions
adequately caveated and earned. Most important fix: genome-denominator hygiene + CAZyme
label — neither overturns a headline, both addressed by caveat/relabel above.
