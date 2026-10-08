# Coder run-manifest: decide-gate build (n_transport v1.1.0): links, transport class, tiers, compound classes

Date 2026-10-08 · explorer 0.1.0-alpha.5 · KG 0.1.0-alpha.7 · facts only. Decisions: `methods/notebook.md` § Decisions.

## Tests: **117 OK** = `test_kg_fetch` 21 + `test_n_transport` 96 (+9, test-first; RED 9 errors → GREEN)
New module functions:
- **`function_links`:** a non-member gene with a reaction on a carried group, sharing ≥ 1 non-Q Cyanorak role with the system.
- **`neighbour_links`:** window enzymes with a reaction on a carried group, excluding groups with ubiquity ≥ threshold.
- **`transport_class`:** the union of members' `cyanorak.role:Q*` roles.
- **`system_tier`.**
- **`compound_class`:** ordered name rules (`COMPOUND_RULES`).
- **`can_use_applicable`.**

Toy cases: the pncC-like gene (B.11 only) is not function-linked; a gene sharing only Q.1 is not linked; a member is excluded; ammonia is excluded from neighbour links at threshold 30 but kept at 40; salY → Low, fadD-like → Low (score-0), mixed resolutions → High (flagged); `S-Adenosyl-L-methionine` → other N (no substring matching).

## Pipeline
- **New step:** `scripts/p11_links_tiers_classes.py`, file prefix `p11_` (p7–p10 are helper scripts). It is added to `run_pipeline.py` after p6.
- **One KG call:** `gene_ontology_terms(['cyanorak_role','tigr_role'], leaf)` via `kg_fetch`, strict inputs, key (locus_tag, term_id), over universe genes + every gene with a metabolism-arm reaction on a carried group + every window enzyme_candidate.
- **Runner check:** the full MED4 run through `run_pipeline.py` reproduced all 9 `p11_med4_*.csv` files exactly (then deleted).
- **Runs:** p11 run on MED4 (`--pilot`), MIT9313 and NATL2A (on the v1.0.3 p1–p6 outputs).

### Rules as implemented
- **Carried groups (for both link kinds):** substrate rows with `n_status` ≠ no_N, not lumping, not currency, any depth (so inherited focA→nitrite counts).
- **Function-linked:** any gene of the strain with a metabolism-arm reaction on a carried group (from `raw/p5_<tag>_genome_metabolism_for_substrates.csv`), not a system member, sharing ≥ 1 Cyanorak role with the union of the members' roles, excluding ids starting `cyanorak.role:Q`. **Leaf Cyanorak roles, exact id match** (no roll-up, so E.4.x would not match E.4).
- **Neighbour-linked:** step-4 `enzyme_candidate` neighbours (±8 genes, either strand) with a reaction on a carried group whose ubiquity (genes in the strain reacting with the group) is **< threshold**.
- **Tier** (per system; `system_tier`, applied in this order):
  1. **Low:** every TCDB member is family_inferred.
  2. **Low:** the system's max class 1–3 TCDB score (`tcdb_c123_max_score` over members) is 0.
  3. **High:** strong + role_complete + resolved.
  4. **Medium:** strong (incomplete, or complete without any TCDB resolution), or tcdb_only + resolved.
  5. **not_transporter:** no member is strong or tcdb_only.

  **Mixed member resolutions** (resolved + family_inferred) count as resolved, and `tier_reason` says "mixed member resolutions". Members without TCDB don't vote.
- **Compound classes:** an ordered, anchored name rule over all member names of an equivalence group, in this order: nitrite, nitrate, cyanate, urea (exact), urea analogue (flag), ammonium (exact), ammonium analogue (flag: (mono/di/tri/tetra)(methyl/ethyl)amine/ammonium, "ammonium ion derivative"), osmolytes, polyamines, peptides ("peptide" substring, glutathione, aminoacyl- prefixes), nucleobases/nucleosides, amino acids (20 + ornithine, citrulline, homoserine, β-alanine, GABA, selenocysteine, homocysteine, "amino acid"), else **other N**.
  - **Names only:** the KG's Metabolite rows carry no ChEBI/KEGG class hierarchy (list_metabolites exposes ids, formula, elements, pathways).
  - **Not applicable to can_use:** organic classes (amino acids, peptides, polyamines, nucleobases/nucleosides, osmolytes) get `can_use_applicable = False`; can_use stays visible.

## Ubiquity and proposed threshold (`p11_<tag>_substrate_ubiquity.csv`)
**Proposed: ubiquitous = ≥ 30 genes with a metabolism-arm reaction** (parameter `--ubiquity-threshold`, run at 30). Below the currency compounds there is a clear gap in all three strains:

| rank (non-currency) | MED4 | MIT9313 | NATL2A |
|---|---|---|---|
| 1 | Ammonia 36 | L-Glutamate 40 | Ammonia 37 |
| 2 | L-Glutamate 34 | Ammonia 39 | L-Glutamate 34 |
| *gap* | | | |
| 3 | SAM 23 / L-Gln 23 | SAM 25 / L-Gln 25 | SAM 23 / L-Gln 23 |
| next | Pyruvate 21, Oxygen 20, Acetyl-CoA 20, Gly 18, SAH 17 | Oxygen 24, Pyruvate 21, Acetyl-CoA 20, SAH 19 | Pyruvate 20, Oxygen 20, Acetyl-CoA 19, Gly 18, SAH 17 |

- **Excluded at 30, non-currency:** **Ammonia and L-Glutamate**, in every strain.
- **Top 20 (MED4), counts with currency marked (c):** H2O 178c, ATP 129c, H+ 106c, Pi 84c, ADP 76c, NAD+ 58c, NADH 51c, CO2 45c, NADPH 42c, **Ammonia 36**, **L-Glutamate 34**, SAM 23, L-Gln 23, CoA 23c, Pyruvate 21, GTP 21c, Oxygen 20, Acetyl-CoA 20, Glycine 18, SAH 17. MIT9313 and NATL2A are in the summaries; same order of magnitude, Diphosphate 93c in MIT9313.

## Pilot (MED4) vs expectations (`p11_med4_pilot.csv`)
| case | expected | observed |
|---|---|---|
| cyn function-linked | cynS | **cynS** (Cyanate, via E.4) ✓ |
| urt function-linked | ureC/B/A (± ureD–G if they react) | **ureC, ureB, ureA** (Urea, via D.1.3 + E.4) ✓. ureD–G have no metabolism-arm reaction, so they can't link |
| amt1 function-linked | glnA, glsF (+ any other E.4 gene with an ammonia reaction; full list) | **glnA PMM0920, glsF PMM1512**, plus cynS PMM0373, ureC/B/A PMM0963–0965, carA PMM0951, metB PMM0409, PMM0408 (MetB-like), metC PMM1670; all via E.4, all with an Ammonia reaction ✓ |
| pncC → amt1 | NOT linked | **not linked** (pncC has B.11 only) ✓ |
| regulator / helicase-only links | none | **none.** All 22 function-linked enzymes in MED4 are metabolic: the amt1 set above, glutathione enzymes (gst ×3, gshB, gor, gpx, glx1, glx2), heme (ctaB, hemH), glmU, galE |
| neighbour-linked | cynS, urease; not pncC | **cyn ← cynS; urt ← ureC/B/A**; pncC **not** (ammonia excluded as ubiquitous) ✓. Also: sys_PMM0566 ← glx2 (Glutathione), sys_PMM1260 ← rfbB (dTDP-glucose) |
| transport class | dpp Q.1, amt1 Q.4, pst Q.2 | amt1 **Q.4** ✓; pst **Q.2** ✓; **dpp Q.1 + Q.4 + Q.7** (union: dppA/dppB Q.1; ddpD Q.1 + Q.4; dppC **Q.7 "Sugars"**). Q.1 is present but not alone |
| tiers | amt1, cyn, urt, dpp, pst High; salY Low; fadD Low or Medium | amt1, cyn, urt, dpp, pst **High** ✓; salY **Low** (superfamily-only) ✓; **fadD Low** |

**Why fadD is Low.** Its only class 1–3 TCDB attachment is `tcdb:2.A.1` at score 0.0 (homology, single source). Its 0.8 call is in class 4 (`4.C.1.1`), which doesn't count toward transporter evidence. "Score-0-only" is evaluated on the class 1–3 attachments, the same ones that make it `tcdb_only`. Under a reading that uses all classes it would be Medium (tcdb_only + resolved).

## Per strain
| | MED4 | MIT9313 | NATL2A |
|---|---|---|---|
| function-linked pairs / systems / enzymes | 42 / 12 / 22 | 56 / 17 / 28 | 42 / 14 / 26 |
| neighbour-linked pairs / systems / enzymes | 6 / 4 / 6 | 17 / 10 / 14 | 9 / 6 / 8 |
| (system, group, enzyme) function-only / neighbour-only / both | 38 / 2 / 4 | 50 / 11 / 6 | 37 / 4 / 5 |
| tiers High / Medium / Low / not_transporter | 39 / 121 / 63 / 93 | 60 / 166 / 106 / 130 | 40 / 127 / 73 / 92 |
| High: single / multi-gene | 30 / 9 | 47 / 13 | 31 / 9 |
| systems with >1 Q class / no Q class | 1 / 264 | 4 / 371 | 1 / 274 |

**focA** (MIT9313 sys_PMT2240, NATL2A sys_PMN2A_1299):
- **Function-linked** to nirA via nitrite through `cyanorak.role:D.1.3` (PMT2239; PMN2A_1298) ✓.
- **Neighbour-linked** to nirA (rank −2) ✓. In NATL2A it is also neighbour-linked to the 162-bp `PMN2A_RS10340` nirA (rank −1); that gene has no Cyanorak role, so it is not function-linked.
- **Tier Low** in both (score-0-only: class 1–3 max score 0), transport class **Q.2**.

**Compound classes** (equivalence groups carried, N-containing + no-formula):

| class | MED4 | MIT9313 | NATL2A |
|---|---|---|---|
| ammonium (incl. analogues) | 7 | 7 | 7 |
| urea (incl. analogues) | 4 | 4 | 4 |
| cyanate / nitrite / nitrate | 1 / 1 / 1 | 1 / 1 / 1 | 1 / 1 / 1 |
| amino acids | 35 | 44 | 37 |
| peptides | 7 | 7 | 7 |
| polyamines | 6 | 6 | 6 |
| nucleobases/nucleosides | 18 | 19 | 18 |
| osmolytes | 9 | 9 | 9 |
| **other N** | **632** | **681** | **631** |

- **Analogues flagged (MED4):** ammonium = ammonium ion derivative, methylamine, ethylamine, tetraethylammonium, triethylamine, tetramethylammonium; urea = N-acylurea, hydroxyurea, thiourea.
- **Every other-N group** is listed for review in `p11_<tag>_other_N_groups.csv`, with names, n_status and counts of rows, systems and most-specific rows; sort by most-specific rows to see the ones carried specifically. Most are the broad substrate lists of superfamily or lumping families.

## Odd / worth checking
1. **amt1's function-linked set** goes beyond glnA/glsF to every E.4 enzyme with an ammonia reaction: cynS, urease, carA, metB, PMM0408, metC. The rule is as specified; whether E.4 is narrow enough is your call.
2. **dpp's transport class is Q.1 + Q.4 + Q.7.** dppC carries only Q.7 "Sugars". The class is a union over members, as specified.
3. **Leaf-mode Cyanorak roles are matched exactly**, with no roll-up. All roles that mattered here were level 1–2 (E.4, D.1.3, B.9, D.1.4, …).
4. **"other N" is large** (632–681 groups) and needs your review before the analysis milestone. The rule is names-only.

## Files
- **Code:**
  - `methods/n_transport.py` (v1.1.0)
  - `tests/test_n_transport.py` (96)
  - `scripts/p11_links_tiers_classes.py` (new)
  - `scripts/run_pipeline.py` (+p11)
- **Outputs (per strain, `data/<tag>/`):**
  - `p11_<tag>_function_linked.csv`
  - `p11_<tag>_neighbour_linked.csv`
  - `p11_<tag>_substrate_ubiquity.csv`
  - `p11_<tag>_compound_classes.csv`
  - `p11_<tag>_other_N_groups.csv`
  - `p11_<tag>_system_substrates_annotated.csv` (every row; compound_class, analogue_flag, can_use_applicable, function_linked_loci, function_linked_shared_roles, neighbour_linked_loci; `not_eligible` on lumping/currency/no_N rows, `none` where nothing links)
  - `p11_<tag>_systems.csv` (tier, tier_reason, transport_class_ids/names, link counts)
  - `p11_<tag>_gene_roles_cyanorak_tigr.csv`
  - `p11_<tag>_summary.json`
  - MED4 also: `p11_med4_pilot.csv`
