# Coder run-manifest: scale-out to MIT9313 and NATL2A (n_transport v1.0.1)

Date 2026-10-07 · explorer 0.1.0-alpha.5 · KG 0.1.0-alpha.7 · facts only.
- **Output directories:** `methods/data/mit9313/` and `methods/data/natl2a/`, no `--pilot`, reference parameters (gap 200, role join on, cross-locus on, lumping threshold 100), full step-3 grid.
- **Per-strain reports:** `p8_<tag>_report.json`, `p8_<tag>_spotcheck.csv`, `p8_<tag>_nitrate_nitrite_metabolism_genes.csv`, `p8_<tag>_role_conflicts_vs_med4.csv` (script `scripts/p8_strain_report.py`).

## A MED4 assumption that surfaced, and the fix (test-first, 92 tests OK)
- **What failed:** the first MIT9313 run stopped at p3 on `assert run_id.notna()`. Two **universe** genes have no coordinates in the KG: **PMT_2355** (MFS sugar porter) and **som PMT_2631**. Both are single carriers; PMT_2355 is a p2c addition.
- **Why it was missed:** in MED4 every universe gene had coordinates.
- **Fix:** `nt.attach_runs()` keeps such a gene as its own pseudo-run `nocoord_<locus>`, with `has_coordinates=False`, so it becomes a one-gene system. It is never dropped. p3 now records `universe_genes_without_coordinates`.
- **Tests:** RED 1 error → GREEN 92 OK.
- **Re-runs:** both strains were re-run from empty directories with v1.0.1. MED4 (v1.0.0) is unaffected, since the new code changes nothing when every universe gene has coordinates.

## 1. Run log: all 11 steps exit 0 for both strains
p1, p2a, p2b, p2c, p2a, p2b, p2c --check-only, p3, p4, p5, p6.

## 2. No-coordinate completeness: **hard assert passed for both**
| strain | list_organisms gene_count | with coordinates | without | sum equals count | universe genes without coordinates |
|---|---|---|---|---|---|
| MIT9313 | 2906 | 2389 | **517** | yes | PMT_2355, PMT_2631 |
| NATL2A | 2210 | 2058 | 152 | yes | none |

Placeability (window 8, against the reference systems' members):

| strain | placed | prefix shared, no member within window | unplaceable | examples |
|---|---|---|---|---|
| MIT9313 | 144 | 373 | 0 | placed PMT0064, PMT0111, PMT0167; not within window PMT0324, PMT0734 |
| NATL2A | 22 | 130 | 0 | placed PMN2A_0667, PMN2A_0844; not within window PMN2A_1907… |

- **MIT9313's 517 no-coordinate genes include ordinary named genes**, e.g. PMT0064 (aspartate-semialdehyde dehydrogenase) and PMT0111 (SecA-type translocase), not only small or hypothetical ORFs.
- **MIT9313 uses two tag prefixes:** 406 no-coordinate genes are `PMT_`, 111 are `PMT`. The same number appears in both schemes (`PMT_2239` is an alias of `PMT2239` in all_identifiers). Placement compares tags only within one prefix, so `PMT_n` and `PMTn` are not compared with each other.

## 3. Counts
| | MIT9313 | NATL2A |
|---|---|---|
| universe p1 → final (after p2c) | 524 → **528** | 374 → **379** |
| p2c additions | PMT1349 (PF13343 secreted), PMT_2355 (PF00083 MFS sugar porter), PMT_2357 (PF04966 OprB porin), PMT_2631 som (PF04966) | PMN2A_0707 (PF07690 MFS), PMN2A_0933 (PF00892 DMT), PMN2A_1057, PMN2A_1757 (PF04966 porins), PMN2A_1772 (PF13343) |
| second-pass additions | 0 | 0 |
| role map: domains / non-other / hash | 503 / 63 / `185976a9e573179e` | 402 / 53 / `5e1fa3679a78e08c` |
| domains shared with MED4's map | 352 | 349 |
| **role conflicts vs MED4 (same Pfam, different role)** | **0** | **0** |
| seed conflicts | PF08352 only (seed atpase, name rule other), as in MED4 | same |

## 4. Systems (grid; reference variant in bold)
**MIT9313**

| variant | systems | role-complete | cross-locus | sizes | max |
|---|---|---|---|---|---|
| gap100 roleT | 466 | 78 | 7 | 1:433; 2:15; 3:11; 4:3; 5:4 | 5 |
| gap100 roleF | 469 | 78 | 7 | 1:438; 2:14; 3:10; 4:3; 5:4 | 5 |
| **gap200 roleT** | **462** | **77** | **7** | **1:429; 2:14; 3:12; 4:3; 5:3; 6+:1** | **8** |
| gap200 roleF | 465 | 77 | 7 | 1:434; 2:13; 3:11; 4:3; 5:3; 6+:1 | 8 |
| gap500 roleT | 463 | 77 | 6 | 1:430; 2:14; 3:12; 4:4; 5:2; 6+:1 | 8 |
| gap500 roleF | 466 | 77 | 6 | 1:435; 2:13; 3:11; 4:4; 5:2; 6+:1 | 8 |
| gap200 cross off | 475 | 71 | 0 | 1:443; 2:19; 3:10; 4:1; 5:1; 6+:1 | 8 |

- **Largest systems (reference):**
  - 8: ATP synthase PMT1466–1472 + PMT_1473;
  - 5: pst = PMT0508 pstS + PMT0700–0702 pstB/A/C + PMT0993 pstS;
  - 5: nat = PMT0893, PMT0894 natH, PMT0896 natG, PMT0897 natF + PMT1517 grrP.
- **I7:** 7 cross-locus systems. **4 have more than one gene of the same ABC role:**
  - PMT0145 srrA + PMT0668 lacF + PMT1120 lacG + PMT1545;
  - dpp (PMT0266 dppC, PMT1145 dppA, PMT1146 dppB, PMT2110 ddpD);
  - pst (two pstS, PMT0508 and PMT0993);
  - nat (PMT0893–0897 + grrP PMT1517).

**NATL2A**

| variant | systems | role-complete | cross-locus | sizes | max |
|---|---|---|---|---|---|
| gap100 roleT | 335 | 49 | 5 | 1:310; 2:13; 3:7; 4:3; 5:2 | 5 |
| gap100 roleF | 338 | 49 | 5 | 1:315; 2:12; 3:6; 4:3; 5:2 | 5 |
| **gap200 roleT** | **332** | **49** | **5** | **1:307; 2:13; 3:7; 4:3; 5:1; 6+:1** | **8** |
| gap200 roleF | 335 | 49 | 5 | 1:312; 2:12; 3:6; 4:3; 5:1; 6+:1 | 8 |
| gap500 roleT | 332 | 49 | 5 | same as gap200 roleT | 8 |
| gap500 roleF | 335 | 49 | 5 | same as gap200 roleF | 8 |
| gap200 cross off | 339 | 45 | 0 | 1:315; 2:16; 3:5; 4:1; 5:1; 6+:1 | 8 |

- **Largest systems (reference):** 8 ATP synthase PMN2A_0980–0987; 5 urt PMN2A_1044–1048; 4 pst.
- **I7:** 5 cross-locus systems. **2 have more than one gene of the same ABC role:**
  - pst (PMN2A_0309–0311 + pstS PMN2A_0441);
  - dpp (PMN2A_0704 dppA, 0705 dppB, 1559 ddpD, 1755 dppC).

## 5. Spot-check: ammonium / urea / cyanate / nitrate / nitrite (`p8_<tag>_spotcheck.csv`)
- **Selection:** rows that are most_specific and contains_N, whose equivalence group is named ammonia/ammonium, urea, cyanate, nitrate or nitrite.
- **Ids matched:** C00014, C00086, C01417, C00088, plus the nitrate group (chebi:14654 + C00244, name_soft).

**MIT9313** (cyanate: **no rows**)

| compound | system (members) | family | window / run / window_ms / run_ms | linked (window = ms) |
|---|---|---|---|---|
| ammonium | sys_PMT1853 (amt1 PMT1853) | 1.A.11 | **co-located** / elsewhere / co-located / elsewhere | PMT1845 |
| ammonium | sys_PMT_0376 (PMT_0376) | 1.A.1 | co-located / elsewhere / co-located / elsewhere | PMT0375 |
| ammonium | PMT0515, PMT0542, ktrB/ktrA PMT1628–1629, nhaS PMT1944, PMT1974, crp PMT2151 | 1.A.1 / 2.A.37 / 2.A.36.6 | elsewhere (all four) | — |
| urea | **sys_PMT2225 (urtE/D/C/B/A PMT2225–2229)** | 3.A.1.4.4/.5 | **co-located** / elsewhere / co-located / elsewhere | **PMT2234, PMT2235, PMT2236** |
| urea | PMT0265, PMT0804, sasA PMT1099, nblS PMT1417, putP PMT1502, phoR PMT_0997 | 2.A.21 | elsewhere (all four) | — |
| nitrite | sys_PMT0189 (recQ) | 2.A.16 | elsewhere (all four); 1 genome gene | — |
| nitrate | 16 single-gene systems (recQ PMT0189, sul1 PMT0899, sul3 PMT1214, phoB/phoR, rpaA/rpaB, sasA, nblS, putP, ycf29, PMT0265/0804/0805/1097/1357) | 2.A.16 / 2.A.21 / 2.A.53.3 / 3.E.1 | **no** (all four) | — |

**NATL2A** (cyanate: **no rows**)

| compound | system (members) | family | window / run / window_ms / run_ms | linked |
|---|---|---|---|---|
| ammonium | **sys_PMN2A_1629 (amt1)** | 1.A.11 | **co-located** / elsewhere / co-located / elsewhere | PMN2A_1623 |
| ammonium | nhaS PMN2A_1175, ktrB/ktrA PMN2A_1448–1449, nhaS PMN2A_1805 | 2.A.37 / 1.A.1 | elsewhere (all four) | — |
| urea | **sys_PMN2A_1044 (urtE/D/C/B/A PMN2A_1044–1048)** | 3.A.1.4.4/.5 | **co-located** / elsewhere / co-located / elsewhere | **PMN2A_1053, 1054, 1055** |
| urea | phoR PMN2A_0437, sasA PMN2A_0674, nblS PMN2A_0912, PMN2A_1011 | 2.A.21 | elsewhere (all four) | — |
| nitrite | sys_PMN2A_0647 (crhR) | 2.A.16 | elsewhere (all four); 2 genome genes | — |
| nitrate | 12 single-gene systems (phoB, phoR, sul1, crhR, sasA, nblS, PMN2A_1011, srrA, rpaA, rpaB, ycf29, sul3) | 3.E.1 / 2.A.21 / 2.A.53.3 / 2.A.16 | **no** (all four) | — |

**Not in the most_specific spot-check, but present (inherited row, so `n/a` under the strict variant):**
- **MIT9313 focA PMT2240** (`tcdb:1.A.16`), nitrite inherited: window **co-located**, run **co-located**, linked nirA **PMT2239** (adjacent).
- **NATL2A focA PMN2A_1299** (`tcdb:1.A.16`), nitrite inherited: window and run **co-located**, linked **PMN2A_1298 and PMN2A_RS10340** (nirA).

**Every gene with a metabolism-arm reaction on nitrite (C00088) or nitrate (chebi:14654 / C00244)** (`p8_<tag>_nitrate_nitrite_metabolism_genes.csv`):

| strain | genes | on |
|---|---|---|
| MIT9313 | **PMT2239 nirA**, ferredoxin–nitrite reductase (1 row) | nitrite |
| NATL2A | **PMN2A_1298 nirA**, ferredoxin–nitrite reductase; **PMN2A_RS10340 nirA**, ferredoxin–nitrite reductase (2 rows) | nitrite |

- No gene in either strain has a metabolism-arm reaction on nitrate.
- **MIT9313 (p5's nitrate/nitrite check, all rows of the two groups):** 120 rows. Window: no 78, elsewhere 41, co-located 1 (focA). Run: the same. p5's `EN1.pass` field is therefore `false` here; see 6.
- **NATL2A:** 77 rows. Window: no 49, elsewhere 27, co-located 1 (focA). Run: the same.

## 6. Anything odd
1. **MED4 assumption, fixed:** universe genes without coordinates (above).
2. **MED4 assumption, not fixed:** p5 writes an `EN1` block with `pass` = "every nitrate/nitrite row is `no`". That is MED4's pre-registered expectation; for MIT9313 and NATL2A it reads `pass: false` because nirA exists. The numbers are correct; the label is MED4-specific. Proposal §3.5: each strain's nitrate/nitrite expectation comes from its own genome.
3. **Warnings:** only the expected transport-arm `family_inferred` warning (MIT9313 and NATL2A p5). No unexpected warning was raised.
4. **Duplicate-key assert:** never fired. No identical BRITE duplicates were collapsed; that path is only used with `--pilot`.
5. **NATL2A:**
   - **`gene_name` often holds a RefSeq locus tag** (e.g. `PMN2A_RS08290`): 95 of the 379 universe genes. Labels such as "PMN2A_1011:PMN2A_RS08290" are a gene-name field, not a second gene.
   - **`PMN2A_RS10340`** is a separate KG gene: nirA, 162 bp (1,807,114–1,807,275, +), WP_225866306.1, next to nirA PMN2A_1298 (1,805,411–1,807,072). It is annotated only by pfam/cog/kegg/brite/ec. It is counted as a second nirA in the nitrite tables.
6. **MIT9313 no-coordinate genes:** 517 (18% of the genome), including named metabolic genes, and two tag schemes (`PMT` / `PMT_`) that share numbers. Placement does not bridge the prefixes; 0 are unplaceable only because both prefixes occur among members.
7. **Noise in the nitrate/urea/ammonium rows:** most single-gene "systems" carrying these substrates are regulators or other non-transporters with a TCDB attachment in 2.A.21 / 3.E.1 / 2.A.16 (recQ, phoB/phoR, rpaA/B, sasA, nblS, crhR, crp, srrA, ycf29). They are shown as found (likely_transporter is in the full table); nothing was filtered.

## Files
- **Code:**
  - `methods/n_transport.py` (v1.0.1, `attach_runs`)
  - `tests/test_n_transport.py` (+1 test; 92 total)
  - `scripts/p3_group_systems.py` (uses `attach_runs`)
  - `scripts/p8_strain_report.py` (new)
- **Outputs:** `methods/data/mit9313/`, `methods/data/natl2a/` (full step 1–6 outputs, `run_log.json`, `p8_*`).
