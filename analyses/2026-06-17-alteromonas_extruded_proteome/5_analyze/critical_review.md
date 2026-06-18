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
