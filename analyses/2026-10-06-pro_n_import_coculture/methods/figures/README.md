# Methods-milestone figures

Made by `scripts/f1_methods_figures.py`. The script uses matplotlib only, makes no KG calls, and reads only from `data/<strain>/` and `data/p15_*`.
Each figure is saved as PNG (300 dpi) and as SVG.

Command (run from the repo root):

```
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/f1_methods_figures.py
```

| figure | sources (data/) | helper table written next to it |
|---|---|---|
| fig1_build_funnel | <strain>/p3_<strain>_summary.json (list_organisms_gene_count), <strain>/p2c_<strain>_universe.csv, <strain>/p11_<strain>_systems.csv | none |
| fig2_n_systems_matrix | <strain>/p12_<strain>_system_substrates_classified.csv, <strain>/p11_<strain>_systems.csv, <strain>/p11_<strain>_function_linked.csv, <strain>/p11_<strain>_neighbour_linked.csv, <strain>/p18_<strain>_listing_basis.csv | fig2_cells.csv |
| fig3_tiers_tradeoff | p15_tier_counts.csv (a); <strain>/p11_<strain>_systems.csv (b) | fig3b_counts.csv |
| fig4_compound_classes | <strain>/p12_<strain>_compound_classes.csv, <strain>/p12_<strain>_system_substrates_classified.csv (no_N groups) | fig4_counts.csv |
| fig5_linking_rules_tradeoff | <strain>/p12_<strain>_system_substrates_classified.csv (linked_enzyme_loci_window / _run), <strain>/p11_<strain>_neighbour_linked.csv, <strain>/p11_<strain>_function_linked.csv, <strain>/p3_<strain>_gene_systems_gap200_roleT_crossT.csv, <strain>/raw/p3_<strain>_genome_coords.csv | fig5_values.csv |
| fig6_verification_layers | counts given by the coordinator (from methods/notebook.md and critical_review.md), hard-coded in the script | none |

Rules used:
- **fig2 (v2, "N compound classes: what the annotation supports").**
  - Rows used ("eligible"): substrate_depth most_specific, or inherited from a non-lumping family; carrying system tier High/Medium/Low; system not known_false_positive.
  - **(A) Inorganic N.** A row is usable when can_use_window is "co-located" or "elsewhere in genome".
    - Best system = highest tier among usable rows, then most non-fragment links.
    - "(+k dedicated, +k broad)" (v1.6.1) splits the other usable systems at the same tier by the (B) rule
      (nt.listing_basis, efflux-aware). It is shown in every usable cell.
    - Cell states: "usable system"; "listed, not usable" (eligible rows exist but all are can_use = no; shows up to 3 High/Medium example systems, or, if there are none, the best-tier systems labelled "best (<tier>)"); "none".
  - **(B) Organic N (v1.6).** Each cell shows two counts of High/Medium systems that list the class.
    - Pairs come from data/<strain>/p18_<strain>_listing_basis.csv: most_specific, non-lumping rows; known false positives excluded.
    - "dedicated: H k · M m": a member's product or gene name carries the class keyword, or a member has the corresponding
      curated Cyanorak role (Q.1 for amino acids / peptides / amines / polyamines; Q.5 for nucleobases/nucleosides).
      Since v1.6.1 a Q-role-only call does not count on an efflux-annotated system (it becomes broad, "Q.1 only, efflux-annotated").
      Keywords are word-bounded, with exclusions (p18_class_keyword_map.csv, column product_exclude_regex).
      The map is data/p18_class_keyword_map.csv.
    - "broad listing: H k · M m": all other High/Medium systems. Shown muted, in italic grey.
    - Up to 2 dedicated systems are given as examples. State is "dedicated listing", "broad listing only" or "none".
    - can_use is not testable for these classes.
  - figures/fig2_cells.csv has one row per cell: the eligible systems, the counts, the state, and the rule applied.
- **fig3b.** Covers only High and Medium systems. "Single-gene" means n_genes == 1.
- **fig4.** "no N" counts groups that occur only on no_N rows. The right-hand label is "unclassified: <unclassified N> N + <no-formula> no-formula, of <N + no-formula groups> groups that are N or unknown".
- **fig5.**
  - (a) and (b): the enzyme locus appears in linked_enzyme_loci_window or linked_enzyme_loci_run on that system's rows for the named substrate.
  - (c) and (d): the enzyme locus has a row in the neighbour-linked or function-linked table for that system and substrate group.
  - When only some of a case's enzymes pass a rule, the cell shows "k/n linked".
  - The "biologically expected" column is the researcher's judgement, not data.
- **fig6.** The x-axis is fixed at 0–18 (the data range).

## QC figures (scripts/q1_qc_checks.py; makes KG calls via kg_fetch; CSVs in data/qc/)

Command:

```
.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/q1_qc_checks.py
```

| figure | sources | table |
|---|---|---|
| fig7_genemap_<strain> | <strain>/raw/p3_<strain>_genome_coords.csv, p3_<strain>_gene_systems_gap200_roleT_crossT.csv, p11 systems / neighbour_linked / function_linked | qc/q1a_genemap_genes.csv |
| fig8_q_roles_vs_tier | genes_by_ontology(cyanorak_role Q.1-Q.9) per strain, p3 gene_systems, p11 systems | qc/q1b_q_role_by_tier.csv, q1b_q_role_genes.csv, q1b_q_role_missed.csv |
| fig9_gap_sensitivity | <strain>/[grid/]p3_<strain>_{gene_systems,systems}_gap{100,200,500}_roleT_crossT.csv; tiers recomputed with n_transport.system_tier | qc/q1e_tier_counts_by_gap.csv, q1e_n_relevant_membership_by_gap.csv |
