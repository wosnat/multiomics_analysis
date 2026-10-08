# Coder run-manifest: scoped re-review fixes (kg_fetch + C2), n_transport v1.0.2; all three strains re-run

Date 2026-10-07 · explorer 0.1.0-alpha.5 · KG 0.1.0-alpha.7 · facts only.
- **Archive:** the pre-fix outputs are in `methods/data/v1.0.1_archive/{med4,mit9313,natl2a}/`. MED4's copy is the v1.0.0 run; MIT9313 and NATL2A are v1.0.1.

## Exact test counts (from the runner)
- **Before the fixes:** **92** = `test_kg_fetch` **14** + `test_n_transport` **78**. My earlier "21 kg_fetch / 70 n_transport" split was wrong; the total (91, then 92) was right.
- **After:** **105 OK** = `test_kg_fetch` **21** (+7) + `test_n_transport` **84** (+6).
```
.venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/methods/tests -v
```

## Fixes (test-first; RED → GREEN for each new behaviour)
1. **Lumping coverage.** `nt.lumping_families(td, threshold, required_ids=...)` raises `ValueError` if a required family is missing from ontology_term_details or has a non-numeric / NaN `metabolite_count`. A family is never defaulted to non-lumping. p5 passes `required_ids` = every TCDB family in the substrate table. Tests: missing raises, NaN raises, all present OK.
2. **`strict_inputs=True`** in `kg_fetch.fetch` raises `StrictInputError` if not_found, wrong_ontology or wrong_level is non-empty in any envelope. It handles list- and dict-shaped fields, and ignores None values (e.g. `organism: None`). Enabled on:
   - p1 seed Pfams (`genes_by_ontology`);
   - p2c role-map Pfams (first pass and the --check-only pass);
   - p5 `list_metabolites(metabolite_ids)`;
   - p5 `genes_by_metabolite` (substrate groups);
   - the two new p5 nitrate / nitrite expectation calls.
   - That is **7 strict calls per strain.**
3. **`gene_neighbors`** now uses `limit=10**6` (the fetch default), not None.
4. **Identical-row collapse** applies only to rows with `ontology_type == 'brite'`. A test checks that identical non-BRITE rows still raise.
5. **`find_duplicates`** raises `KeyError` if a natural-key field is absent from a row (tested).
6. **total_matching None guard:** an envelope with `total_matching: None`, or without the key, counts the returned rows (tested both).
7. **New kg_fetch tests:** empty chunked input (0 calls, n_calls 0); duplicate key created across chunks (raises); envelope without total_matching; list-shaped not_found (logged; raises under strict). The empty-chunk and cross-chunk tests passed without code changes and now guard existing behaviour.
8. **One-off scripts:** `p4d_probe_refseq_tags.py` moved to `scripts/archive/`, with `archive/README.md` noting that these scripts bypass `kg_fetch` and must not be run as pipeline steps.
   - Also moved: `00_schema_samples.py`, `01_smoke_raw_samples.py`, `p3c_diff_reference.py`, `p4c_diff_step4.py`.
   - Every active script calls the KG only through `kg_fetch.fetch`, except `common.resolve_organism`'s single `list_organisms` call, which asserts exactly one row.
9. **Per-strain expected-negative 1.** The MED4-specific `EN1.pass` block is gone.
   - **p5:** for nitrate (group(s) named nitrate) and nitrite, a separate strict `genes_by_metabolite(group ids, metabolism)` call gives `expected_usable` = any gene of the strain reacts with the group. `nt.expectation_check` then compares can_use with it: `pass` = all non-n/a values are `no` if not usable, else no non-n/a value is `no`; `None` if nothing is evaluable.
   - **Outputs:** p5 writes `p5_<tag>_expectation_check.csv` (window / run). p6 writes **`p6_<tag>_expected_negative_1_table.csv`** with all four definitions. `p5_<tag>_expected_negative_1.csv` gains a `compound` column.
- **Also:** `p8_strain_report.py` reads the new table, and reads the flagged table with `low_memory=False` (silences a pandas mixed-dtype warning; no change to values).

## Re-run (all three strains, from empty directories)
- **Runs:** MED4 with `--pilot` (as before); MIT9313 and NATL2A without. **All 11 steps exit 0 for every strain.**
- **MED4 directory:** it could not be removed itself (a shell's working directory), but all its contents were cleared first. Every file in it carries this run's timestamp.
- **Diff script:** `scripts/p9_diff_dirs.py` (new) does a byte-level comparison; for differing CSVs it also compares content on common columns, and for JSON it lists top-level keys.

## Per-strain diff vs the archive (`data/<tag>/p9_<tag>_diff_vs_v1.0.1.json`)
| strain | identical files | differing files (all explained) | only in archive | only new |
|---|---|---|---|---|
| MED4 | 73 | 7 `p3_med4_gene_systems_<variant>.csv`: + `has_coordinates` column, **all other columns equal** (MED4's archive predates v1.0.1's `attach_runs`); `p5_med4_expected_negative_1.csv`: + `compound`, others equal (72 rows); summaries: `calls`, `n_transport_version`, `EN1` → `expectation_check_nitrate_nitrite`, `universe_genes_without_coordinates` (p3); `run_log.json` | `coder_manifest_v1.0.md`, `p7_*` (diff reports of the previous turn; still in the archive) | `p5_med4_expectation_check.csv`, `p6_med4_expected_negative_1_table.csv` |
| MIT9313 | 68 | `p5_mit9313_expected_negative_1.csv` (+ `compound`, others equal, 120 rows); summaries (as above); `run_log.json` | `p8_*` (regenerated afterwards; **p8 spot-check identical**) | the 2 expectation files |
| NATL2A | 68 | `p5_natl2a_expected_negative_1.csv` (+ `compound`, 77 rows); summaries; `run_log.json` | `p8_*` (regenerated; **spot-check identical**) | the 2 expectation files |

- **Call logs:** for every strain, every call has the same (call, total_matching, returned) as before. The only additions are the two new expectation calls in p5:
  - nitrate 0 rows in all three strains;
  - nitrite 0 / 1 / 2 rows in MED4 / MIT9313 / NATL2A.
- **Other differences in call logs:** only the new `strict_inputs` field and the gene_neighbors limit.
- **All analysis tables are unchanged:** systems, neighbours, the substrate table, flags, linked enzymes, profiles.

## Per-strain expected-negative 1 table (`p6_<tag>_expected_negative_1_table.csv`)
| strain | compound | expected_usable (genome genes) | rows | window | run | window_ms | run_ms | pass (w / r / w_ms / r_ms) |
|---|---|---|---|---|---|---|---|---|
| MED4 | nitrate (`chebi:14654` group incl. C00244) | **False** (none) | 43 | no 43 | no 43 | n/a 28, no 15 | n/a 28, no 15 | T / T / T / T |
| MED4 | nitrite (C00088) | **False** (none) | 29 | no 29 | no 29 | n/a 23, no 6 | n/a 23, no 6 | T / T / T / T |
| MIT9313 | nitrate | **False** (none) | 78 | no 78 | no 78 | n/a 58, no 20 | n/a 58, no 20 | T / T / T / T |
| MIT9313 | nitrite | **True** (PMT2239 nirA) | 42 | elsewhere 41, co-located 1 | elsewhere 41, co-located 1 | n/a 41, elsewhere 1 | n/a 41, elsewhere 1 | T / T / T / T |
| NATL2A | nitrate | **False** (none) | 49 | no 49 | no 49 | n/a 33, no 16 | n/a 33, no 16 | T / T / T / T |
| NATL2A | nitrite | **True** (PMN2A_1298, PMN2A_RS10340 nirA) | 28 | elsewhere 27, co-located 1 | elsewhere 27, co-located 1 | n/a 27, elsewhere 1 | n/a 27, elsewhere 1 | T / T / T / T |

The co-located nitrite row in MIT9313 and NATL2A is focA (inherited, so `n/a` under the ms variants), as reported before.

## strict_inputs
**It never fired.** 7 strict calls per strain, every run exit 0. StrictInputError is raised, never logged, so a firing would have stopped the run.

## Also noted
- **MIT9313's lumping set has a fifth family:** `tcdb:2.A.66` (tc_family, 106 substrates, just above the threshold of 100). It was already in v1.0.1, and the file is unchanged.
- MED4 and NATL2A: {3.A.1, 2.A.1, 2.A.7, 2.A.6}.

## Files
- **Code:**
  - `methods/kg_fetch.py`
  - `methods/n_transport.py` (v1.0.2)
  - `tests/test_kg_fetch.py` (21)
  - `tests/test_n_transport.py` (84)
  - `scripts/p1_collect_transporters.py`, `p2c_requery_universe.py`, `p3_group_systems.py`, `p5_substrates.py`, `p6_evidence_profiles.py`, `p8_strain_report.py`
  - `scripts/p9_diff_dirs.py` (new)
  - `scripts/archive/` (5 scripts + README)
- **Outputs:** `methods/data/{med4,mit9313,natl2a}/` (re-run; `p9_<tag>_diff_vs_v1.0.1.json`; MIT9313 / NATL2A `p8_*` regenerated).
- **Archive:** `methods/data/v1.0.1_archive/`.
