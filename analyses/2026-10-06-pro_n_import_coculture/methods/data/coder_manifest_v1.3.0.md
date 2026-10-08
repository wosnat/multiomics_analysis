# Coder manifest: n_transport v1.3.0 (researcher decisions 1-3, 2026-10-08)

Facts only; no biological conclusions.

## Changes
1. likely_transporter: a curated Cyanorak Q role counts as "strong" only together with a TCDB class 1-3
   attachment (it upgrades tcdb_only -> strong). It never turns none -> strong.
   p11 curated_q (overrides the score-0-only Low rule) = a member with likely strong and basis containing {cyanorak, tcdb}.
2. Compound class comes from the name rules only (nt.name_class_with_context).
   - KEGG pathway votes and the carrying TCDB family are now context columns: pathway_context and family_context.
   - The pathway tie-break is gone.
   - Groups with no matching name rule become "unclassified N" or "unclassified (no formula)".
   - Every group carries class_caveat = "best effort: names only; KG has no chemical categories".
   - Output renamed: p12_<tag>_compound_classes.csv (it was _layered).
   - New column carried_only_via_lumping_families.
3. Review list = unclassified N groups that contain N and are carried by a most_specific row of a
   High/Medium system, excluding groups carried only through lumping families and excluding lumping-family rows.
   It is the union across strains: data/p12_review_list_unclassified_N.csv (92 groups).

## Runs
- Tests: 137 OK (test_kg_fetch 21, test_n_transport 116).
- run_pipeline: all three strains, 13 steps, exit 0 (MED4 with --pilot).
- Archive of the previous version: data/v1.2.0_archive.

## Report: scripts/p14_report_v13.py (no KG calls)
| file | contents |
|---|---|
| data/p14_promotions_vs_v1.1.0.csv | every likely_transporter change vs v1.1.0 (all tcdb_only -> strong) |
| data/p14_ftn_status.csv | ferritin genes: likely_transporter, basis, tier |
| data/p14_class_counts.csv | compound_class x strain |
| data/p14_diff_vs_v1.2.0.json | per-strain changes in likely_transporter, tiers, links, classes, files |
| data/p12_review_list_unclassified_N.csv | review union with names, systems, tiers, genes, gene_names, TCDB families |
| data/p14_report.json | summary |
