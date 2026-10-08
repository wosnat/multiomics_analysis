# Coder manifest: n_transport v1.6.0 (researcher decisions 2026-10-08)

Facts only. Diff base: data/v1.5.0_archive (data, qc and figures of v1.5.0).

## Changes
1a. Transporter universe, 4th source src_cyanorak_q: genes_by_ontology(cyanorak_role, Q.1-Q.9), strict, in p1. The column is
    carried by p2b; p2c additions get False. The added genes go through the normal role / grouping / tier rules.
1b. system_tier: when curated_q is true (a member is strong through Cyanorak Q + TCDB), the superfamily-only rule no longer applies.
    The tier reason gets "[superfamily-only overridden by curated Cyanorak transport role]".
    Such a system is Medium at most, because family_inferred is not "resolved".
    Catalogue-only (no strong member) is never lifted.
2.  Dedicated vs broad listing, new pipeline step p18_listing_basis.py (no KG calls):
    - nt.CLASS_KEYWORDS / class_keyword_table / listing_basis / substrate_breadth;
    - data/p18_class_keyword_map.csv;
    - data/<strain>/p18_<strain>_listing_basis.csv, _listing_table.csv, _expected_checks.csv, _summary.json.
    - Q.4 is not mapped to ammonium.
    - fig2 Block B now uses the p18 listing basis.

## Runs
- run_pipeline: all three strains, 14/14 steps, exit 0 (MED4 with --pilot).
- Tests: 185 OK:
  - test_kg_fetch: 21;
  - test_n_transport: 160;
  - test_real_data_invariants: 4 (renamed from test_real_data_v15; now compares against data/v1.5.0_archive).
- p17_diff_v16.py writes data/p17_universe_additions.csv, p17_membership_changes.csv, p17_tier_changes.csv,
  p17_tier_counts.csv and p17_report.json.
- f1_methods_figures.py regenerated fig1-fig6. q1_qc_checks.py regenerated data/qc/* and fig7-fig9.
