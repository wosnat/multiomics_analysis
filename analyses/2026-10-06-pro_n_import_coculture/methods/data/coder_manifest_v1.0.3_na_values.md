# Coder run-manifest: NA-colliding category values (n_transport v1.0.3); p5 → p6 re-run for all three strains

Facts only. The pre-change outputs are in `methods/data/v1.0.2_archive/{med4,mit9313,natl2a}/`.

## Test count
**108 OK** = `test_kg_fetch` 21 + `test_n_transport` 87 (+3 new). Six existing tests were updated to the new values first (RED: 8 failures), then GREEN.

New tests (`TestNoNaCollidingCategories`):
- **Strict columns round-trip:** writes the flagged table (`add_ms_variant`) to CSV, reads it back with **default `pd.read_csv`**, and asserts `can_use_window_ms` / `can_use_run_ms` hold no NaN and contain `not_eligible` (4 of 5 rows).
- **Basis columns round-trip:** `link_basis` (equiv_groups) and `match_basis` (can_use_equiv) read back as `none`, not NaN.
- **NA-set check:** none of the category values used (`not_eligible`, `none`, `no`, `co-located`, `elsewhere in genome`) is in pandas' default NA set.

## Changes
- **New module constants:** `NOT_ELIGIBLE = "not_eligible"` (strict-variant can_use columns, and the not-considered value in `expectation_check`) and `NO_BASIS = "none"`.
- **`NO_BASIS` is used for:**
  - `match_basis` when no genome gene reacts with the substrate group;
  - `link_basis` / `link_basis_group` for singleton equivalence groups (`equiv_groups`, `can_use_equiv`, and p5's no_N rows).
- **Scripts:** p5 and p6 use the constants. No `"n/a"` literal remains in code (one explanatory comment only).

## Scan for NA-colliding values (all CSVs of the three strains, read as raw text)
- **Non-empty values in pandas' default NA set:** **only `"n/a"`**, in `can_use_window_ms` / `can_use_run_ms` of `p6_<tag>_system_substrates_flagged.csv`. No "NA", "null", "None", "nan", "-", "N/A" or "#N/A" anywhere.
- **Empty strings `""`** (also in the NA set) appear in many columns. Renamed where `""` was a category value in the p5/p6 outputs: `match_basis`, `link_basis`, `link_basis_group` → `none`.
- **Found but NOT renamed:** they are written by steps 2–4, which were to stay unchanged, or they are list / optional fields where NaN means "empty".
  - **Category-like `""` (step-2/3/4 outputs, copied into some p6 tables):**
    - `joined_by` (one-gene systems; also in `p6_<tag>_system_profiles.csv`);
    - `likely_transporter_basis` (no basis);
    - `recruited_by` (neighbour table);
    - `name_rule_text`, `seed_role`, `tcdb_c123_source_agreement`;
    - `missing_subunit_neighbours` (p6 profiles).

    A decision is needed if these should also get an explicit value; it would change p2–p4 outputs.
  - **`expectation_check` `pass`** would be written as empty (→ NaN) when a definition is not evaluable. That case did not occur (all pass values are True).
  - **List / optional fields** (gene_name, ec, kegg_ko, pfam_ids, tcdb_ids, linked_enzyme_loci_*, genome_enzyme_loci, other_system_id, …): `""` = empty list / absent value, so NaN on read is the intended meaning.

## Re-run
p5 and p6 for all three strains (MED4 with `--pilot`), plus p8 for MIT9313 / NATL2A (it reads p6). All exit 0. p1–p4 were not re-run.

## Strict-column value counts, before → after (raw text; and NaN count when read with default `pd.read_csv`)
| strain | column | before | after | NaN on default read, before → after |
|---|---|---|---|---|
| MED4 | can_use_window_ms | n/a 13,982; no 827; elsewhere 154; co-located 15 | **not_eligible 13,982**; no 827; elsewhere 154; co-located 15 | 13,982 → **0** |
| MED4 | can_use_run_ms | n/a 13,982; no 827; elsewhere 167; co-located 2 | **not_eligible 13,982**; no 827; elsewhere 167; co-located 2 | 13,982 → **0** |
| MIT9313 | can_use_window_ms | n/a 25,206; no 1,472; elsewhere 309; co-located 26 | **not_eligible 25,206**; no 1,472; elsewhere 309; co-located 26 | 25,206 → **0** |
| MIT9313 | can_use_run_ms | n/a 25,206; no 1,472; elsewhere 335 | **not_eligible 25,206**; no 1,472; elsewhere 335 | 25,206 → **0** |
| NATL2A | can_use_window_ms | n/a 15,814; no 967; elsewhere 224; co-located 17 | **not_eligible 15,814**; no 967; elsewhere 224; co-located 17 | 15,814 → **0** |
| NATL2A | can_use_run_ms | n/a 15,814; no 967; elsewhere 241 | **not_eligible 15,814**; no 967; elsewhere 241 | 15,814 → **0** |

These counts cover all rows (all n_status). The p6 summary's `*_N` counts (N-class rows only) changed only in the key name.

## Diff vs v1.0.2 (`scripts/p10_verify_na_rename.py` → `data/<tag>/p10_<tag>_na_rename_check.json`)
- **Every differing CSV:** same rows, same columns; **every changed cell is an allowed rename**:
  - `n/a` → `not_eligible` in the two strict columns;
  - `""` → `none` in match_basis / link_basis / link_basis_group.
- **The only cells outside that rule:** the `*_ms_observed` columns of `p6_<tag>_expected_negative_1_table.csv`. These are JSON-encoded counts whose key changed `"n/a"` → `"not_eligible"`, with the counts identical. Pass values are unchanged.
- **Files:** no file was added or removed.
- **JSON summaries:** identical apart from n_transport_version, the renamed keys (`xref_link_basis`, `can_use_*_ms_N`, the expectation block) and p8's `spot_group_ids`.
  - **`spot_group_ids`:** the old report showed **NaN** for the singleton groups' `link_basis` (C00014, C00086, C00088, C01417), because p8 read the xref with default NA handling. They now read `none`. This is an instance of the reported bug.
- **No row or count changed anywhere.**

## Files
- **Code:**
  - `methods/n_transport.py` (v1.0.3)
  - `tests/test_n_transport.py` (87)
  - `scripts/p5_substrates.py`
  - `scripts/p6_evidence_profiles.py`
  - `scripts/p10_verify_na_rename.py` (new)
- **Outputs:** `data/{med4,mit9313,natl2a}/` p5_*, p6_*, p8_* (MIT9313/NATL2A), `p10_<tag>_na_rename_check.json`.
- **Archive:** `data/v1.0.2_archive/`.
