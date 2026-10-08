# Coder manifest: n_transport v1.5.0 (grouping Rule A3 + known false positives) and QC pack

Facts only. Diff base: data/v1.4.0_archive (v1.4.0 outputs plus p15 cross-strain files).

## Part 1: housekeeping
- In data/<strain>/grid/: the 6 non-chosen p3 grouping variants (edges, cross_locus_edges, gene_systems and
  systems; 24 files per strain).
- gap200_roleT_crossT stays in data/<strain>/.
- p3_group_systems.py writes the non-chosen variants to grid/ (variant_dir).
- p3_<tag>_variant_summary.csv has new columns files_dir and n_adjacent_abc_edges.
- No other script read the grid variants. p4, p5, p6, p8 and p11 read only the REF files.
- KNOWN_FALSE_POSITIVE_PRODUCTS now matches three products: ferritin; glutathione S-transferase (^glutathione s-transferase(,.*)?$);
  and nickel-type superoxide dismutase maturation protease (sodX PMM1295; the product string is specific, so no locus-tag match
  is needed). These are flags only; tiers are unchanged.

## Part 2: Rule A3 adjacent_abc (n_transport.group_systems)
- Two systems in the same run merge when two of their genes are IMMEDIATELY adjacent:
  - next_locus_tag in the genome;
  - gap_to_next <= 200 bp;
  - same strand.
- Conditions for the merge:
  - both systems are ABC-only, OR one is ABC-only and the other is a single strong 'other' gene;
  - they share a TCDB ancestor at level >= 2;
  - they are not both binding + permease + ATPase complete.
- Order of passes: ABC + ABC pairs first, then strong-'other' pairs. This makes the result independent of pair order
  (toy test TestAdjacentAbcOrder).
- A3 follows the join_within_run_by_role switch, so roleF variants do not apply it.
- attach_runs now carries next_locus_tag and strand.
- The MFP (devB) keeps role 'other'. A 'membrane_fusion' role would change the Pfam basis of likely_transporter
  for every HlyD-family gene.

## Runs
- run_pipeline: all three strains, 13/13 steps, exit 0 (MED4 with --pilot).
- Tests: 174 OK:
  - test_kg_fetch: 21;
  - test_n_transport: 149;
  - test_real_data_v15: 4. It checks that the reference systems are unchanged, that no two complete cassettes merged,
    that the nitrate/nitrite expected-negative holds, and that the pilot answer-key comparisons are unchanged.
    In p4_med4_pilot_neighbours.csv only other_system_id may change, and only for PMM0976-0978 and PMM0748-0750.
- Diff script: scripts/p16_diff_v15.py, writing data/p16_*.csv and data/p16_report.json.
- QC script: scripts/q1_qc_checks.py. It writes data/qc/q1*.csv and q1_summary.json, and the figures
  figures/fig7_genemap_<strain>, fig8_q_roles_vs_tier and fig9_gap_sensitivity.
  - KG calls: genes_by_ontology(cyanorak_role Q.1-Q.9) and gene_details(universe) per strain.
  - At gap 200, the tiers recomputed for the grid check (e) reproduce p11 exactly (0 mismatches in every strain).
