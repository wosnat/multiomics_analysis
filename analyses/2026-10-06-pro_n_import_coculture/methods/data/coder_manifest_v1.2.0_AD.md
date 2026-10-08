# Coder run-manifest: researcher decisions A–D (n_transport v1.2.0); all three strains re-run p1→p12

Date 2026-10-08 · explorer 0.1.0-alpha.5 · KG 0.1.0-alpha.7 · facts only.
- **Archive:** the pre-change outputs are in `data/v1.1.0_archive/`.
- **The network outage:** an earlier attempt was cut off (neo4j ServiceUnavailable; MIT9313 at p5, NATL2A at p1). MIT9313 and NATL2A were then re-run from empty directories. MED4's completed run (p1→p12) used the same code as the final runs, since nothing changed after it.
- **Exit status:** all 13 steps exit 0 for all three strains (`data/<tag>/run_log.json`).
- **Report script:** `scripts/p13_report_AD.py` writes `data/p13_*` and `data/p13_report.json`.

## Tests: **132 OK** = `test_kg_fetch` **21** + `test_n_transport` **111** (+15 since v1.1.0; RED 5 failures + 9 errors → GREEN)

## A. Curated Cyanorak transport role as a third "strong" basis
- **Implementation:**
  - `likely_transporter_basis` adds `cyanorak` (any `cyanorak.role:Q*` in the gene's `cyanorak_roles`); `strong` = pfam or ko or cyanorak.
  - `system_tier(curated_q=True)` skips the score-0-only → Low rule; the superfamily-only → Low rule still applies. The tier reason records "score-0-only overridden by curated Cyanorak transport role".
  - p2a fetches the universe's Cyanorak roles (strict) and p2b uses them; p4 adds `cyanorak_role` to the neighbour annotation.
  - `recruited_by` (missing_subunit) is **unchanged** (Pfam/KO only), so neighbour classes did not change.
- **Expected focA result: met.** focA goes Low → **Medium** in MIT9313 (sys_PMT2240) and NATL2A (sys_PMN2A_1299): strong via Q.2, role-incomplete.
- **likely_transporter changes:** **45** (`p13_A_likely_transporter_changes.csv`). All are none or tcdb_only → strong.

| strain | universe genes (tcdb_only → strong, via cyanorak) | non-universe neighbours (none → strong) |
|---|---|---|
| MED4 | 5: tolC PMM0097 (Q.9), zntA PMM0131 (Q.4), devB PMM0748 (Q.7), **ftn PMM0804 (Q.4)**, acrA PMM1139 (Q.9) | 4 |
| MIT9313 | 14: RND/MFS efflux (PMT0129, PMT0130, PMT0174, mdtA PMT1617, PMT1616), tolC PMT0182, acrA PMT1156, devB PMT0589, PMT1573, Gap/Sap glycolipid exporter PMT1106, zntA PMT1991, **ftn PMT0495, ftn PMT0499**, **focA PMT2240** | 10 |
| NATL2A | 6: devB PMN2A_0152, NRAMP PMN2A_0237, MFP PMN2A_0747, **focA PMN2A_1299**, tolC PMN2A_1465, P-type ATPase PMN2A_1497 | 6 |

- **Tier changes:** **12** (`p13_A_tier_changes.csv`). No system appeared or disappeared.
  - MED4: **ftn sys_PMM0804 Low → Medium**.
  - MIT9313: som porins sys_PMT0284, sys_PMT0802, sys_PMT0998, sys_PMT1979 Low → **High** (Q.6, single carrier, resolved); **ftn sys_PMT0495, sys_PMT0499 Low → Medium**; sys_PMT1573 Low → Medium (Q.8); focA sys_PMT2240 Low → Medium.
  - NATL2A: porins sys_PMN2A_0777, sys_PMN2A_1028 Low → High (Q.6); focA sys_PMN2A_1299 Low → Medium.
- **Non-transporters promoted to strong** by the curated basis. The KG's Cyanorak roles were checked directly; e.g. hisF has `cyanorak.role:Q.1` and an RNA-binding protein has `Q.5`. The keyword screen for regulator/helicase words found **0**, but reading the products, these are not transporters:
  - **Universe genes (tier changed): ferritin `ftn`** (Q.4) in MED4 PMM0804 and MIT9313 PMT0495 and PMT0499, now Medium.
  - **Non-universe neighbours** (likely_transporter only; no system or class change):
    - hisF (Q.1; MED4 PMM0430, MIT9313 PMT0274, NATL2A PMN2A_1761);
    - RNA-binding protein (Q.5; PMM0142, PMT2002, PMN2A_1508);
    - 4′-phosphopantetheinyl transferase domain protein (Q.9; PMM0078, PMT1621, PMN2A_1442);
    - ferritin (NATL2A PMN2A_0212);
    - FAD-dependent oxidoreductase PMT0742 (Q.9);
    - chalcone/stilbene synthase bcsA PMT0412 (Q.7);
    - ferrochelatase hemH PMT1240 (Q.4);
    - creatinine amidohydrolase PMT1814 (Q.9);
    - competence protein comA PMT_2765 (Q.5).
  - **Transport-associated, plausibly OK:** porins (som), piuC iron-uptake factor, "permease" PMT2207, efflux membrane-fusion proteins (acrA/devB/MFP), tolC.
- **No regulator or helicase was promoted.**

## B. Ubiquitous groups: assimilation allow-list
- **Implementation:** `function_links(..., ubiquity, threshold=30, gene_ecs, allow_ecs=UBIQUITOUS_ALLOWLIST_EC)`.
  - For groups with ≥ 30 reacting genes (ammonia, L-glutamate), only genes carrying **EC 6.3.1.2** (glutamine synthetase) or **EC 1.4.7.1** (ferredoxin-GOGAT) link.
  - **ECs checked in the KG:** MED4 glnA PMM0920 `ec:6.3.1.2`; glsF PMM1512 `ec:1.4.7.1` (+ `ec:1.4.1.13`).
  - New column `link_breadth` ∈ {specific, ubiquitous_allowlisted}. p11 fetches EC with the Cyanorak roles.
- **amt1 function links, before → after:**

| strain | before | after |
|---|---|---|
| MED4 | cynS, PMM0408, metB, **glnA**, carA, ureC, ureB, ureA, **glsF**, metC (all → Ammonia) | **glnA PMM0920, glsF PMM1512** (Ammonia, ubiquitous_allowlisted) |
| MIT9313 | PMT0225, metB, **glnA**, carA, **glsF**, metC, ureA, ureB, ureC, **nirA** PMT2239 | **glnA PMT0601, glsF PMT1777** |
| NATL2A | **glnA**, carA, ureA, ureB, ureC, **glsF**, metC, nirA, cynS, PMN2A_1742, metB | **glnA PMN2A_0141, glsF PMN2A_1078** |

- **All function-linked pairs, before → after:** MED4 42 → 34, MIT9313 56 → 48, NATL2A 42 → 33. In each strain 2 are `ubiquitous_allowlisted`.

## C. No-formula fix
- **Rule:** `compound_class(names, n_status)` returns **"unclassified (no formula)"** when no rule matches and every member is no_formula; contains_N leftovers are **"unclassified N"**. The label "other N" no longer exists.
- **Before:** no_formula groups labelled "other N" (v1.1.0): MED4 239, MIT9313 249, NATL2A 239.
- **After, name layer:** "unclassified (no formula)" 238 / 248 / 238.
- **After, layered:** 223 / 231 / 223; family context assigns 13 / 15 / 13 of them to "xenobiotic (efflux family)", and the pathway layer 2 to amino acids.
- **"other N" left anywhere:** none.

## D. Layered compound classifier (`scripts/p12_compound_classes_layered.py`, step 8; in `run_pipeline.py`)
- **Layer 1, name rules,** with the new gaps:
  - generic amino acids ("alpha-amino acid", "an alpha-amino acid", "polar amino acid", "Amino acid(…)");
  - 3-letter dipeptide chains (Lys-Arg, Gly-Pro-Ala);
  - aminoacyl prefixes (L-alanyl-L-alanine);
  - "…peptide";
  - new class **amines** (ethanolamine, tyramine, tryptamine, histamine, …). Amines count as organic N, so `can_use_applicable = False`.
- **Layer 2, KEGG pathways** of the group's members (`list_metabolites` verbose). Each pathway is mapped by `nt.pathway_class`:
  - by KEGG map number: amino-acid maps → amino acids; ko00230/00240 → nucleobases/nucleosides; ko00480 → peptides; ko00430 → osmolytes; cofactor maps → **cofactors/vitamins** (a class added for review);
  - by name: polyamine words → polyamines; antibiotic, polyketide, xenobiotic-degradation and drug-metabolism words → xenobiotic;
  - global maps are ignored.

  Strict majority (> 50% of mapped votes) assigns. The map is written per strain to **`data/<tag>/p12_pathway_class_map.csv`**: 287 pathways seen, 66 mapped.
- **Layer 4, tie-break only:** a pathway tie is resolved when exactly one tied class is allowed by the carrying systems' Cyanorak Q roles (`p12_q_class_map.csv`: Q.1 → amino acids/peptides/amines/polyamines; nucleosides → nucleobases; cations/iron → siderophore; anions → nitrate/nitrite/cyanate).
- **Layer 3, TCDB family context per ROW:** the family name, plus the GO `links_out` names for non-lumping families, gives `siderophore` or `xenobiotic (efflux family)`. Written per row as `family_context_class` (`p12_<tag>_system_substrates_classified.csv`; families in `p12_<tag>_family_context.csv`). A group gets the class only if **all** its rows agree.
- **Leftovers:** "unclassified N" or "unclassified (no formula)".
- **Recorded per group:** `class_source` plus `layer_votes` (every layer's vote).

**Per-layer counts (groups):**

| class_source | MED4 | MIT9313 | NATL2A |
|---|---|---|---|
| name | 99 | 110 | 102 |
| pathway | 90 | 98 | 92 |
| pathway + transport-class tie-break | 1 | 1 | 1 |
| family_context | 60 | 79 | 60 |
| none (unclassified N / no formula) | 471 (248 / 223) | 492 (261 / 231) | 467 (244 / 223) |

**Final classes:**

| class | MED4 | MIT9313 | NATL2A |
|---|---|---|---|
| amino acids | 61 | 74 | 63 |
| xenobiotic (efflux family) | 59 | 78 | 59 |
| xenobiotic | 35 | 37 | 35 |
| nucleobases/nucleosides | 30 | 31 | 30 |
| cofactors/vitamins | 19 | 19 | 19 |
| osmolytes | 10 | 12 | 12 |
| peptides | 10 | 11 | 11 |
| polyamines | 6 | 6 | 6 |
| amines | 5 | 5 | 5 |
| siderophore | 1 | 1 | 1 |

Ammonium 7, urea 4, cyanate / nitrite / nitrate 1 each, in all three.

**Family context:**
- MED4: 19 efflux + 5 siderophore families of 225.
- MIT9313: 22 + 4 of 278.
- NATL2A: 19 + 4 of 238.

**ChEBI hierarchy: confirmed absent.**
- `kg_schema` has no ChEBI/class node or relationship.
- Metabolite properties are chebi_id, elements, evidence_sources, formula, id, inchikey, mass, mnxm_id, name, pathway_ids, pathway_names and counts.
- Only KEGG pathway membership is available as a class-like annotation.

**Review list** (`data/p12_review_list_unclassified_N.csv`, union across strains): groups still "unclassified N", contains_N, carried by a most_specific row of a High or Medium system.
- **161 groups**; 138 occur in all three strains, 5 in two, 18 in one.
- **99 are carried only by lumping families** (3.A.1 superfamily-level or 2.A.1 MFS most_specific rows). Column `only_lumping_families` lets you drop them; **62 come through a non-lumping family**.
- **The 62 non-lumping groups include:**
  - drug/xenobiotic substrates of ABC exporters 3.A.1.106/.113/.203 (ampicillin, chloramphenicol, ethidium, verapamil, vinblastine, norfloxacin, Hoechst 33342, bleomycin, syringomycin) — they stay unclassified because not all rows are efflux families;
  - siderophore-like substrates of FeCT 3.A.1.14 (deferoxamine, coelichelin, chrysobactin, vibrioferrin, iron(III) hydroxamate, Fe-enterobactin);
  - osmolyte-like substrates of 3.A.1.12 (proVWX) in MIT9313: (E)-4-(trimethylammonio)but-2-enoate, acetylcholine, β-alaninebetaine;
  - PepT-family listings (bradykinin, EDTA);
  - lipids (phosphatidylethanolamine, phosphatidylcholine, phosphatidylserine) on 3.A.3 / 3.A.1;
  - sugars/glycans (chitobiose, N-acetylglucosamine, UDP-sugar).

  Full list with systems, genes and families is in the file.

**10 random layer assignments** (`data/p13_D_random_assignments.csv`; seed 7; 5 pathway, 4 family-context, 1 tie-break):

| strain | group | name | class | source | evidence |
|---|---|---|---|---|---|
| NATL2A | kegg.compound:C02918 | 1-Methylnicotinamide | cofactors/vitamins | pathway | ko00760 Nicotinate and nicotinamide metabolism (1/1) |
| NATL2A | kegg.compound:C02465 | Triiodothyronine | amino acids | pathway | ko00350 Tyrosine metabolism (1/1) |
| NATL2A | kegg.compound:C00015 | UDP | nucleobases/nucleosides | pathway | ko00240 Pyrimidine metabolism (1/1); family rows also all efflux (3) |
| MIT9313 | kegg.compound:C01829 | Thyroxine | amino acids | pathway | ko00350 Tyrosine metabolism (1/1) |
| MIT9313 | kegg.compound:C00021 | S-Adenosyl-L-homocysteine | amino acids | pathway | ko00270 + ko01230 (amino acids 2) vs ko00670 (cofactors 1) |
| MIT9313 | chebi:64608 | GDP-fucose | xenobiotic (efflux family) | family_context | 7/7 rows on efflux-named families |
| MIT9313 | kegg.compound:C06665 | Imipenem | xenobiotic (efflux family) | family_context | 10/10 rows efflux-named |
| MED4 | chebi:84880 | GDP-D-mannose | xenobiotic (efflux family) | family_context | 4/4 rows efflux-named |
| MED4 | chebi:38083 | malonate ester | xenobiotic (efflux family) | family_context | 1/1 row efflux-named |
| NATL2A | kegg.compound:C00430 | 5-Aminolevulinate | amino acids | pathway + tie-break | ko00260 (amino acids) vs ko00860 (cofactors) tie; Q.1 allows amino acids |

## Odd / worth checking
1. **Ferritin (`ftn`) is promoted to strong and Medium tier** through a Cyanorak Q.4 role. Several non-transporter neighbours also carry Q roles in the KG (hisF Q.1, RNA-binding protein Q.5, 4′-PPTase Q.9, hemH Q.4, bcsA Q.7, comA Q.5).
2. **The family-context layer labels nucleotide-sugars** (GDP-fucose, GDP-mannose) and simple esters as "xenobiotic (efflux family)" whenever every carrying row sits on an efflux/drug-named family. That reflects the carrying family, not the compound.
3. **Thyroxine and triiodothyronine → amino acids** come via KEGG "Tyrosine metabolism". This is the pathway layer's map-based rule.
4. **The review list is 161, not a few dozen;** 99 of them come only through lumping families.
5. **cofactors/vitamins** is a class I added in the pathway map, for review.

## Files
- **Code:**
  - `methods/n_transport.py` (v1.2.0)
  - `tests/test_n_transport.py` (111)
  - `scripts/p2a_fetch_pfam_tcdb.py`, `p2b_pfam_roles.py`, `p4_neighbours.py`, `p11_links_tiers_classes.py`
  - `scripts/p12_compound_classes_layered.py` (new)
  - `scripts/p13_report_AD.py` (new)
  - `scripts/run_pipeline.py` (+p12)
- **Per strain (`data/<tag>/`):**
  - `p12_<tag>_compound_classes_layered.csv`
  - `p12_<tag>_system_substrates_classified.csv`
  - `p12_<tag>_family_context.csv`
  - `p12_pathway_class_map.csv`
  - `p12_q_class_map.csv`
  - `p12_<tag>_review_candidates.csv`
  - `p12_<tag>_summary.json`
  - p11 outputs with `link_breadth`
  - `p11_<tag>_unclassified_groups.csv`
- **Across strains (`data/`):**
  - `p12_review_list_unclassified_N.csv`
  - `p13_A_likely_transporter_changes.csv`
  - `p13_A_tier_changes.csv`
  - `p13_B_amt1_links.csv`
  - `p13_C_no_formula.csv`
  - `p13_D_random_assignments.csv`
  - `p13_report.json`
