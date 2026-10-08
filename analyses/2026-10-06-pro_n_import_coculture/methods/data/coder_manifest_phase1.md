# Coder run-manifest: methods milestone, phase 1 (toy tests + pure-logic module)

Date 2026-10-07 · explorer 0.1.0-alpha.5 · KG 0.1.0-alpha.7 · facts only, no conclusions.

## Files written (A = analyses/2026-10-06-pro_n_import_coculture)
- `A/methods/n_transport.py`: module v0.1.0, pure pandas functions, no KG access.
- `A/methods/tests/test_n_transport.py`: 40 toy tests (stdlib unittest; pytest is not installed in the venv and nothing was installed).
- `A/methods/scripts/00_schema_samples.py`: schema-inspection API calls.
- `A/methods/scripts/01_smoke_raw_samples.py`: runs the module on the saved raw samples (no KG calls).
- `A/methods/scripts/README_coder.md`: coder working notes.
- `A/methods/data/raw_samples/*.json|*.csv`: 4 raw results plus their to_dataframe CSVs.

## Module functions
| function | rule (full docstring in the module) |
|---|---|
| `to_bool(x)` | bools pass; NaN/None/"" → False; "True"/"False" strings (any case), 1/0, yes/no parsed; other strings raise ValueError |
| `parse_list(x)` | list, " \| "-joined string, stringified list, scalar, NaN → list[str] |
| `tcdb_level(id)`, `tcdb_ancestor(id, L)` | level = dotted fields − 1; ancestor truncates the id, or returns None if the id is shallower |
| `pfam_role(pfam_ids)` | map via `PFAM_ROLE_MAP` (12 seed accessions); no hit → `other`; one role → that role; >1 distinct role → **`mixed`** (sixth value, added) |
| `adjacent_gaps(genes_df)` | sort by contig/start; `gap_to_next = next.start − end − 1` (negative = overlap; NaN at contig end; no circular wrap) |
| `runs(genes_df, max_gap_bp, same_strand=True, max_interlopers=1)` | blocks = chains with gap ≤ max_gap; same-strand segments bracketing ≤ max_interlopers opposite-strand genes are merged; interlopers keep their own run, flagged `opposite_strand_in_run`, `inside_run_id` |
| `group_systems(df, cross_locus=True, within_run_min_level=3, cross_locus_min_level=3)` | A: same run + shared TCDB ancestor at level ≥ 3. B (switchable): different runs + shared ancestor at level ≥ 3 + neither role-complete + role sets differ; transitive. Outputs `system_id`, `cross_locus_merged`, `n_runs`, `system_roles` |
| `classify_neighbour(row)` | precedence: has TCDB → `tcdb_transporter` (added 4th value); role Pfam or BRITE KO → `missing_subunit`; `is_linked_enzyme` → `linked_enzyme`; else `context` |
| `recruited_by(row)` | `pfam` / `ko` / `pfam+ko` / None |
| `can_use(substrate_id, metab_df, loci)` | metabolism rows only (transport rows ignored); exact id match; in loci → `co-located`, else any → `elsewhere in genome`, else `no` |
| `likely_transporter(row)` / `likely_transporter_basis(row)` | role Pfam OR BRITE KO OR TCDB class 1/2/3. Classes 4/5/8/9 alone do not count |
| `evidence_profile(rows)` | n_genes, n_genes_with_tcdb, tcdb_depth_max, tcdb_depth_min_gene, evidence, n_homology/family_inferred genes, max score, source_agreement, pfam_support, n_pfam_corroborated_genes, roles, has_*, role_complete (b+p+a, or single carrier) |

## Tests
Command (repo root):
```
.venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/methods/tests -v
```
- RED 1: module absent → `ModuleNotFoundError: No module named 'n_transport'` (1 error).
- RED 2: stub module → `Ran 40 tests ... FAILED (errors=40)` (all NotImplementedError).
- GREEN: `Ran 40 tests in 0.215s` / `OK` (all 40 pass, no warnings printed).

Covered as required: string "False" not truthy (`to_bool`, `classify_neighbour`, `likely_transporter` with `dtype=str` reads); opposite-strand gene inside a run (ureD-like) plus unbracketed and 2-gene-interloper negatives; cross-locus grouping on (6 systems) / off (9 systems); gaps from coordinates (toy + real cyn coords 30/16/32); can_use co-located / elsewhere / no (transport row ignored); superfamily-only gene (stays one-gene system; depth 2; not role-complete); TCDB-annotated non-transporter (class 4.C fadD-like → False; class 9 → False).

## Raw samples (4 calls, cyn PMM0370–0373; one more than the 1–3 suggested, because coordinates live only in gene_details)
| call | rows | key fields / types observed |
|---|---|---|
| `gene_details(locus_tags=cyn)` | 4 | `contig` str (NC_005072.1), `start`/`end` int, `strand` str '+'; `transport_substrate_resolution` str (NaN for cynS); `tcdb_evidence_score_max` float; `alternate_functional_descriptions`, `annotation_types` list → " \| " joined; `transmembrane_regions`, `gene_name_synonyms` appear in the df but not in row0 keys |
| `gene_ontology_terms(cyn, MED4, ['pfam','tcdb'], verbose=True)` | 13 (6 pfam, 7 tcdb) | `term_id` prefixed; `level` int (tcdb:3.A.1.16.1 → 4); `evidence` str; `evidence_score` float; `sources` list; `ontology_type`; TCDB-verbose: `source_agreement` (both_sources/single_source), `pfam_support` (corroborated/uncorroborated), `go_support`, `attachment_depth` (most_specific), `tier`/`identity`/`qcov`/`evalue`/`consensus_n` all NaN here |
| `metabolites_by_gene(cyn, MED4, ['N'], transport+metabolism, verbose, limit=10000)` | 16 (4 metabolism, 12 transport) | as documented; `ec_numbers` list → "4.2.1.104"; verbose adds `tcdb_level_kind` (tc_specificity), `tc_class_id`; `by_gene` in envelope |
| `gene_neighbors(['PMM0371'], window=3, limit=None)` | 6 | as documented; `same_strand` bool; `gene_name` None for hypotheticals |

Smoke (`01_smoke_raw_samples.py`, 4 genes only, not genome-wide): pfam_role cynA binding / cynB permease / cynD atpase / cynS other; runs(max_gap 300) one + run, gaps 30/16/32; evidence_profile of cynA/B/D: depth 4/4, family_inferred, max 0.8, role_complete True; can_use within this 4-gene table: cyanate co-located, nitrate `no`, nitrite `no` (only 4 genes' metabolism rows were in scope, so this says nothing about the genome).

## API behaviour that differed from expectation / docs
1. `gene_neighbors` accepted `limit=None` although the signature types it `int = 25`.
2. `gene_details` to_dataframe has two columns (`transmembrane_regions`, `gene_name_synonyms`) absent from row0's keys (present on other rows only).
3. PMM0373 cyanate appears twice in metabolism rows (one per reaction, R10079 and R03546). Any count of substrates must dedupe on (locus_tag, metabolite_id).
4. TCDB `tier` is NaN on all 7 cyn TCDB rows (all `family_inferred`); `identity`/`qcov` NaN as expected for eggNOG-only edges.
5. `cynA` reaches "Pyrimidine" (kegg C00396, N-containing) via ThiXYZ 3.A.1.17.3/.6 at 0.4, `most_specific`. It will appear in the N-substrate table.

## Open questions for the main thread
1. `pfam_role` returns a 6th value `mixed` (conflicting role domains on one gene) and `classify_neighbour` a 4th value `tcdb_transporter`; both were added so nothing is silently forced. OK to keep?
2. Cross-locus defaults: `cross_locus=True`, level ≥ 3, excludes role-complete systems, transitive merging. Transitivity could chain unrelated orphan pieces of a large subfamily (e.g. 3.A.1.5). These merges are exposed via `cross_locus_merged` / `n_runs`; should a cap or a review step be added after the pilot?
3. Within-run grouping requires a shared level-3 ancestor. Genes inside a run that share only `tcdb:3.A.1` stay separate (they would be surfaced as neighbours/`tcdb_transporter`). Agree?
4. `likely_transporter` passes any gene with a PF00005 ABC domain or a class-3 attachment. Non-transport ABC ATPases (the grounding names sufC, uvrA, minD, ftsE) would pass. Add a product/KO exclusion list after the pilot, or leave it to review via `likely_transporter_basis`?
5. `runs` default `max_gap_bp` is not set (caller must pass it); the neighbourhood window is a post-pilot decision per the notebook.
6. Not yet built: `domain_substrate_hint`, the linked-enzyme detector producing `is_linked_enzyme`, and the BRITE-KO lookup producing `brite_transporter`.
