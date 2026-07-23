# Methods milestone — critical review

Fresh-context critic (data-integrity + interpretation), 2026-07-23. Scope: `methods/`
(`notebook.md`, `scripts/`, `data/`) + the `## Methods` section of `paper.md`; proposal
trusted input. Ran pytest (27 pass), re-ran `assign_reference_class` on the real CSV,
recomputed every generalization. Verdict: **1 Blocker, 4 Concerns, 3 Notes.**

**Confirmed sound by the critic (verified against the rows):** the HOT1A3 class tally;
"candidates 95% single-gene" (56/59); "0 organic TonB / control-TonB single-gene"; "36
SBP / 11 permease"; the `bool("False")` regression genuinely fixed; the scorer math and
tests real (not tautological — the subunit-count-matched-null and BH tests pin real
behavior). Findings + dispositions below; main-thread-verified each before disposing.

### Blocker (data-integrity) — `crr` PTS EIIA is a false-positive candidate (both strains)
**Critic:** `ACZ81_07475`/`EZ55_01570` (`crr`, K02777, TCDB 4.A.1.1.1) sit
`in_candidate=True`, `confident`, `organic-C`, `carrier_family=MFS-sugar`. `crr`/EIIAᴳˡᶜ
is a soluble cytoplasmic phosphocarrier / catabolite-repression regulator, **not** a
membrane sugar importer (TCDB 4.A.1 is PTS; MFS is 2.A.1) — contradicts the notebook's
own rule to exclude PTS regulatory proteins. It would score as a confident sugar module.
**Disposition — FIXED (verified).** Confirmed `crr` is the only PTS-soluble component in
candidates. Build fix (`08`): soluble PTS components (EIIA/EIIB/HPr/EI) reclassified
`machinery`, dropped from candidates; a genuine PTS **EIIC** membrane permease, if any,
is kept as a sugar importer. Reran; re-verify count.

### Concern (data-integrity) — `rpfN` carbohydrate porin mislabeled MFS-sugar, placeholder substrate
**Critic:** `ACZ81_15425`/`EZ55_03195` `carrier_family=MFS-sugar`, `substrate="porin"`,
`confident`, TCDB `1.B.19.1` (OprB carbohydrate porin, not MFS). Inclusion defensible;
label wrong and "porin" isn't a substrate at confident. MFS-sugar bucket 2/4 wrong.
**Disposition — FIXED.** `carrier_family="carbohydrate-porin"`, substrate → `inferred`;
kept as candidate (porins admit sugars). The genuine MFS-sugar two (fucose, xylE) remain.

### Concern (data-integrity) — "111 secondary carriers `[KG]`" not reproducible (= 85)
**Critic:** paper.md + notebook cite 111 single-gene 2.A.x carriers; the reproducible KG
count is **85** (both `parts_list_v2` and raw `transporter_genes.csv`). Qualitative claim
survives; the specific `[KG]` number is ~30% high.
**Disposition — FIXED (verified: 85).** Correcting 111→85 in `paper.md`, `notebook.md`,
and the `proposal.md` focus-note. Origin: an earlier (06) sweep count not reproduced by
the v2 canonical build.

### Concern (interpretation) — `peptide/nickel` tagged `confident`
**Critic:** 5 rows `substrate="peptide/nickel"`, `confident`, `dual-C+N`; nickel is
inorganic and the notebook itself flags the nikA/B nickel-vs-peptide ambiguity —
`confident` overstates it. (Also: `sapC` "antimicrobial peptide" annotation sits at
confident dipeptide while the near-identical `18465` was set aside.)
**Disposition — FIXED.** `peptide/nickel` confidence → `inferred` (keep `dual-C+N`). The
sap/dpp cassette stays a resolved peptide importer (Sap/Dpp import peptides); the
"antimicrobial peptide" annotation noted in `substrate_source`. `18465` differs — a
*putative* K02003/K02004 ABC with unresolved substrate — so its set-aside stands.

### Concern (data-integrity) — scorer reference-class count ≠ the notebook's TonB narrative
**Critic:** notebook says TonB "32 confident-inorganic / 35 bare-ambiguous", but
`assign_reference_class` yields **26 control-TonB / 40 ambiguous-TonB / 1
interaction-coupled**; 17 TonB rows tagged `inorganic` route to ambiguous (no iron
keyword). `control_confident` is empty for all 67 TonB rows, so the scorer re-derives.
**Disposition — FIXED / RECONCILED (scorer behavior is design-correct).** A bare
"TonB-dependent receptor" with no resolved substrate **should** be ambiguous-TonB — that
IS the control-for-the-control; the build's optimistic `inorganic` default on bare TonB
was too generous. Writing a `reference_class` column (from the scorer's logic) into
`parts_list_v2.csv` as the single source of truth; updating the notebook's 32/50 figures
to the scorer's actual 26 control-TonB / 40 ambiguous-TonB / 1 interaction-coupled.

### Note (data-integrity) — `in_candidate=True` ≠ scored candidate (set-aside only in code)
**Disposition — FIXED.** The new `reference_class` column reflects the set-asides
(`18465`/`03813` → `set-aside`), so the CSV, not only `SET_ASIDE_LOCI` in code, carries
the final count (58/60).

### Note (interpretation) — `substrate_provisional` sometimes holds a gene-name/family string
**Critic:** `hcaT :: MFS`, `pedG ::` are labels not substrates; hcaT's KO (K05820 =
3-phenylpropionate) supports the aromatic prong but the field doesn't record it;
confidence honestly `inferred`.
**Disposition — NOTED (low impact).** Left as-is for now; the confidence is honest and
the substrate identity for the load-bearing case (hcaT aromatic) is in the KO. Cleanup
candidate at the analysis milestone.

### Note (data-integrity) — partial-coverage null wiring undecided
**Critic:** `score_system` returns `n_present` and `subunit_count`; `matched_max_null`
matches on whatever the caller passes. For a partially-covered system the observed is the
median of `n_present`, so the null must draw `n_present`-gene medians (not nominal
`subunit_count`).
**Disposition — DEFERRED to the analysis milestone, rule documented.** The analysis-run
caller must pass `n_present` to the null for partially-covered systems. Low impact here
(candidate multi-subunit systems have 0 EZ55 coverage).

**All fixes applied + main-thread-verified 2026-07-23** on the regenerated
`parts_list_v2.csv`: `crr` → `machinery`/`in_candidate=False`/`reference_class=other`
(no PTS EIIC membrane permease exists to keep); porin relabeled + inferred; peptide/nickel
→ inferred; `reference_class` column written (candidate 65 genes / 57 systems HOT1A3, 67/59
EZ55; control-ABC 33; control-TonB 26; ambiguous-TonB 40; interaction-coupled 1; set-aside
8); single-gene TCDB-2.* = 85 confirmed; `111`→`85` and TonB `32`→`26/40/1` corrected in
`paper.md` / `notebook.md` / `proposal.md`; 27 scorer tests still pass.

**Summary.** One Blocker (`crr` PTS EIIA scored as a confident sugar module) fixed by
dropping soluble PTS components; the load-bearing companion fix is the unreproducible
"111"→"85" carrier count in the paper. The remaining Concerns are honesty/label fixes
(porin, peptide/nickel confidence, the TonB control count reconciled to the scorer's
design-correct output) and are applied in the canonical build; two Notes deferred with
documented rules. The counts, generalizations, and scorer math the critic independently
recomputed all held.
