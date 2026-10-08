# Coder notes (coding subagent's working memory; not the notebook)

Run everything from the repo root with `.venv/Scripts/python.exe` (Windows, Git Bash).

## Phase 1 (2026-10-07): toy tests + pure-logic module. DONE
- `methods/n_transport.py` v0.1.0: pure functions, no KG access.
- `methods/tests/test_n_transport.py`: 40 tests, stdlib `unittest` (pytest is NOT in the venv).
  Command: `.venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/methods/tests -v`
- `scripts/00_schema_samples.py`: 4 small API calls on cyn PMM0370-0373 -> `data/raw_samples/`.
- `scripts/01_smoke_raw_samples.py`: module on the raw samples (no KG calls).

## API facts learned (explorer 0.1.0-alpha.5, KG 0.1.0-alpha.7)
- Coordinates come from `gene_details` (contig, start, end, strand); `gene_neighbors` has no coords.
- `gene_neighbors.bp_gap` = distance to the ANCHOR. Adjacent gap = next.start - end - 1
  (checked: cynA/cynB 30 = the tool's bp_gap for that adjacent pair).
- `gene_neighbors(limit=None)` worked even though the signature says `limit: int = 25`.
- `metabolites_by_gene` rejects `limit=None` per the docs; use `limit=10_000`.
- `gene_ontology_terms(ontology=["pfam","tcdb"], verbose=True)`: one long table, `ontology_type`
  separates them; TCDB verbose columns (`source_agreement`, `pfam_support`, `attachment_depth`,
  `tier`, ...) are NaN on Pfam rows. `term_id` is prefixed (`pfam:PF13379`, `tcdb:3.A.1.16.1`).
- Pfam `evidence` values seen: `curated`, `family_inferred`, `signature`.
- `source_agreement` and `pfam_support` are on `gene_ontology_terms` verbose, NOT on `metabolites_by_gene`.
- to_dataframe list join is " | " (e.g. `sources`, `annotation_types`, `ec_numbers`).
- metabolism rows can repeat a metabolite once per reaction (PMM0373 cyanate via R10079 and R03546).

## Coordinator answers (2026-10-07)
Keep `mixed` and `tcdb_transporter`. Cross-locus merging stays on with no cap; merges stay visible.
`join_within_run_by_role` (default True) was added, with `joined_by` and `member_runs` -> module v0.2.0, 43 tests OK.
No exclusion list for likely_transporter. No default gap. Build the linked-enzyme, BRITE and domain-hint pieces in their pilot steps.
Dedupe substrate counts on (locus_tag, metabolite_id). Keep oddities such as cynA Pyrimidine.

## Pilot step 1: DONE (awaiting the answer-key check; do NOT start step 2 until told)
`scripts/p1_collect_transporters.py --organism MED4 --out-dir methods/data/pilot`. Universe 357.
Manifest: `data/pilot/coder_manifest_p1.md`. Gotcha: genes_by_ontology needs
min_gene_set_size=1, max_gene_set_size=None, or small terms are silently dropped.
Open: fadD passes likely_transporter via a class-2 attachment. pstS PF12849 and salY PF02687/PF12704 are not in PFAM_ROLE_MAP.

## Step 1 answer-key check: PASS (coordinator)

## Pilot step 2: DONE (awaiting the answer-key check; do NOT start step 3 until told)
Module v0.3.0, 50 tests OK. likely_transporter is three-valued (strong / tcdb_only / none);
tcdb_transporter_evidence gives the class 1-3 max score and agreement, no threshold.
`role_map=` parameter added throughout. PFAM_NAME_RULES ordered: enzyme_guard > binding > single > permease > atpase.
Scripts: p2a_fetch_pfam_tcdb.py (KG), p2b_pfam_roles.py (no KG). Manifest: data/pilot/coder_manifest_p2.md.
Use the data-built map from here on: `nt.role_map_dict(pd.read_csv("data/pilot/p2_pfam_role_map.csv"))`.
Leaf TCDB ids per gene are in p2_med4_gene_roles.csv (tcdb_ids). Step 3 grouping should use those, not class ids.

## Step 2 answer-key check: PASS. Keep non-transport ABC ATPases and the ECF/Mla/crcB `other` roles.

## Pilot step 3: DONE (awaiting the answer-key check; do NOT start step 4 until told)
Module v0.4.0 (group_systems return_edges), 52 tests OK. Script p3_group_systems.py. Manifest: data/pilot/coder_manifest_p3.md.
Gotchas:
- A single gene_neighbors call with a huge window hits the server's memory limit; use the tiled sweep (window 250).
- 91 MED4 genes have no coordinates; 1,877 have them; list_organisms says 1,973.
- Chaining: six `mixed` fused ABC exporters were merged through sodX (`other`), giving sys_PMM0065.
- With alternating strands, runs() can make a gene both a run member and an interloper (Mn/Zn PMM1028-1033).

## Step 3 check: PASS 7/7. Rule fix -> v0.5.0 (55 tests OK)
- All-'other' pieces never join cross-locus; 'mixed' counts as role-complete.
- Re-ran the reference variant only (gap200_roleT_crossT). Pilot unchanged. Only sys_PMM0065 (sodX chain) and sys_PMM0125 (ECF) split. 313 systems, 43 complete, 10 cross-locus joins.
- v0.4 outputs are in data/pilot/p3_v0.4_archive/. Manifest: data/pilot/coder_manifest_p3_v05.md.
- STEP 4 RULE: neighbour candidates among data/pilot/p3_med4_no_coordinate_genes.csv (91; 5 more unidentified) must be reported as `no_coordinates`, never dropped.
- Do NOT start step 4 until told.

## Pilot step 4: DONE (v0.6.0, 60 tests). Awaiting check; do NOT start step 5.
p4_neighbours.py, window 8. Manifest: data/pilot/coder_manifest_p4.md.
WRITE FILES WITH encoding="utf-8" and LF (a cp1252 write broke n_transport.py once).
Open issues:
- The name rule maps "X substrate binding domain" of enzymes/regulators to substrate_binding.
- tcdb_transporter precedence labels tatA and evrABC.
- The KG xrefs don't link nitrate chebi:14654 to C00244 (name only).

## Step 4 fixes -> v0.7.0 (64 tests). Re-run done; do NOT start step 5 until told.
- Roles only from the step-2 map, plus `role_hint_unverified`.
- other_system class.
- equiv_groups (id, then name_soft) over all 1,693 KG N-metabolites in p4_metabolite_xref.csv. Nitrate C00244 ~ chebi:14654 via name_soft.
- missing_subunit genes: PMM0440, PMM1046, PMM1119.
- The no-coordinate list has 96 rows: the +5 are PMM50003/50022/50028/50029 and PMM_50048, found by run_cypher tag-form count. They can't be placed as neighbours.
- Manifest: data/pilot/coder_manifest_p4_v07.md.

## Pilot step 5: DONE (v0.8.0, 70 tests). Do NOT start step 6 until told.
- p5_substrates.py -> 6,220-row full table. Expected-negative 1 PASS (72 rows, both definitions `no`).
- Pilot: 97/97 rows found, depth 97/97, rule agreement 92/97 for each definition.
- Disagreements: 5 rows via the name_soft peptide link (pip PMM0356), plus amt1 ammonia vs the "ambiguous" expected call.
- Currency N compounds (ATP, ADP, NAD+, CoA) generate many linked enzymes.
- Manifest: data/pilot/coder_manifest_p5.md.

## Pilot step 6: DONE (v0.9.0, 74 tests). The pilot is complete. Next: API-usage review before scaling.
- p6_evidence_profiles.py. CURRENCY_METABOLITES has 16 ids; examples/metabolites.py is NOT shipped, so the list comes from the docs.
- Under the ms variant, linked enzymes fall from 68 pairs to 8.
- Pilot gene evidence agrees with the key 27/27.
- Manifest: data/pilot/coder_manifest_p6.md.

## API-review fixes -> n_transport v1.0.0 + kg_fetch.py (91 tests). Full MED4 re-run done.
- ALL KG calls go through kg_fetch.fetch:
  - single call per chunk, NO offset paging;
  - natural-key duplicate check;
  - expected-warning patterns.
- BRITE gene_ontology_terms emits identical rows per KO (PMM0192): use allow_identical_duplicates=True there only.
- Layout: one dir per organism (data/<tag>/).
- Runner: scripts/run_pipeline.py --organism "<full name>" --out-dir data/<tag> [--pilot].
- Diff vs archive: scripts/p7_diff_vs_archive.py.
- Lumping threshold 100 (tc_family). The MED4 lumping families are 3.A.1, 2.A.1, 2.A.7, 2.A.6.
- The metabolite xref is now built in p5 (p5_<tag>_metabolite_xref.csv).
- Manifest: data/med4/coder_manifest_v1.0.md.
- Archive: data/pilot_v0.9_archive/.
- Next: MIT9313 / NATL2A, only after the check.

## Scale-out (v1.0.1, 92 tests): MIT9313 + NATL2A done (data/mit9313, data/natl2a). Stop until checked.
- New: attach_runs keeps universe genes without coordinates (MIT9313 PMT_2355 and PMT_2631) as their own pseudo-run.
- Report: scripts/p8_strain_report.py. Manifest: data/coder_manifest_scaleout_v1.0.1.md.
- The p5 EN1 "pass" field is MED4-specific; for the other strains read the numbers.

## Re-review fixes -> v1.0.2 (105 tests: kg_fetch 21 + n_transport 84). All 3 strains re-run; tables unchanged.
- strict_inputs is on for curated inputs (7 calls/strain) and never fired.
- Lumping coverage is asserted.
- BRITE-only identical-row collapse.
- Per-strain expectation table: p6_<tag>_expected_negative_1_table.csv (replaces the EN1 label).
- One-off scripts are in scripts/archive/.
- Manifest: data/coder_manifest_v1.0.2_review_fixes.md.
- Next: the methods critic (main thread).

## NA-collision fix -> v1.0.3 (108 tests: kg_fetch 21 + n_transport 87)
- Strict columns use "not_eligible" (was "n/a").
- match_basis, link_basis and link_basis_group use "none" (was "").
- p5 -> p6 re-run for all strains; only renames changed.
- Open decision: "" category values written in p2-p4 (joined_by, likely_transporter_basis, recruited_by, ...).
- Manifest: data/coder_manifest_v1.0.3_na_values.md.

## Decide-gate build -> v1.1.0 (117 tests: kg_fetch 21 + n_transport 96). p11 step added to run_pipeline.
- Function-linked = reaction on a carried group (non-lumping, non-currency) + a shared non-Q Cyanorak role (leaf, exact id).
- Neighbour-linked = window enzyme + reaction on a carried group with ubiquity < 30 (Ammonia and L-Glutamate are excluded).
- Tiers: system_tier. fadD -> Low (class 1-3 score-0-only).
- Compound classes are name rules; "other N" goes to the researcher for review.
- Manifest: data/coder_manifest_v1.1.0_decide_gate.md. Stop until checked.

## Decisions A-D -> v1.2.0 (132 tests: kg_fetch 21 + n_transport 111). All strains re-run p1 -> p12 (13 steps).
- A: Cyanorak Q role is a third "strong" basis, and it overrides the score-0 Low rule. Watch for ferritin and other Q-annotated non-transporters.
- B: allow-list EC 6.3.1.2 / 1.4.7.1 for ubiquitous groups; link_breadth column.
- C: "unclassified (no formula)".
- D: p12 layered classifier; review list in data/p12_review_list_unclassified_N.csv.
- Report: scripts/p13_report_AD.py. Manifest: data/coder_manifest_v1.2.0_AD.md.

## Decisions 1-3 -> v1.3.0 (137 tests: kg_fetch 21 + n_transport 116). All strains re-run.
- 1: the Cyanorak Q role only upgrades tcdb_only -> strong (needs TCDB class 1-3); no none -> strong.
- 2: compound class = name rules only. pathway_context and family_context are context columns; class_caveat column; no tie-break.
  p12 now writes p12_<tag>_compound_classes.csv.
- 3: the review list excludes groups carried only through lumping families.
- Report: scripts/p14_report_v13.py. Manifest: data/coder_manifest_v1.3.0.md.

## Fix package -> v1.4.0 (158 tests). catalogue-only tier is Low; the KO basis only upgrades; known_false_positive (ferritin);
RefSeq fragments (p11_<tag>_fragments.csv, not counted in link counts); name rules (+ amino sugars).
Report: scripts/p15_report_v14.py. Manifest: data/coder_manifest_v1.4.0.md. Archive of v1.3.0: data/v1.3.0_archive.

## v1.5.0 (174 tests)
- grid variants are in data/<strain>/grid/.
- Rule A3 adjacent_abc.
- known FP now covers gst + sodX.
- diff: scripts/p16_diff_v15.py; QC pack: scripts/q1_qc_checks.py (data/qc/, fig7-9).
- Manifest: data/coder_manifest_v1.5.0.md. Archive: data/v1.4.0_archive.

## v1.6.0 (185 tests)
- Cyanorak Q is a universe source and lifts superfamily-only.
- New p18 listing basis (dedicated / broad).
- Diff: scripts/p17_diff_v16.py.
- Manifest: data/coder_manifest_v1.6.0.md. Archive: data/v1.5.0_archive.

## v1.6.1 (193 tests)
- efflux_annotated flag.
- Tightened class keywords; Q-only dedicated calls not on efflux systems.
- MAPEG known false positive.
- Report: scripts/p19_report_v161.py. Manifest: data/coder_manifest_v1.6.1.md. Archive: data/v1.6.0_archive.

## Next phases (from the main thread's plan)
Pilot one step at a time on MED4 cases: cyn PMM0370-0373; urt+urease PMM0963-0974; amt1 PMM0263;
dpp PMM1049/1048/0421/0192; pst PMM0710, PMM0723-0725; salY PMM0913; fadD PMM0402.
Steps: 1 collect transporter genes, 2 Pfam roles, 3 group, 4 neighbours, 5 substrates + flags,
6 evidence profile.
Not yet implemented: `domain_substrate_hint`; the linked-enzyme detector (KO/EC -> Cyanorak role ->
product) that produces `is_linked_enzyme`; the BRITE-transporter KO lookup that produces
`brite_transporter`.
