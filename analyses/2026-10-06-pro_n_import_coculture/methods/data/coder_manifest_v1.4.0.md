# Coder manifest: n_transport v1.4.0 (fix package, researcher-approved 2026-10-08)

Facts only; no biological conclusions. Diff base: data/v1.3.0_archive.

## Changes
a. system_tier: if no member is strong but some member is tcdb_only, the system is Low with reason
   "catalogue-only (TCDB hit, no domain/KO/curated support)". Medium now means strong only.
   The superfamily-only and score-0-only reasons are still checked first.
b. likely_transporter: a BRITE KO counts as strong only together with a TCDB class 1-3 attachment (same rule as
   the Cyanorak basis). A role Pfam alone still counts as strong.
c. systems carry known_false_positive and known_false_positive_reason. The flag is keyed by product name (ferritin), so it works for any organism.
d. RefSeq fragments (nt.refseq_fragments):
   - criteria: an *_RS locus tag with no PMx-style alias (KG all_identifiers via gene_details); same contig and strand;
     same product, excluding generic products; gap <= 100 bp or overlapping; the parent must not itself be RefSeq-only.
   - Output: p11_<tag>_fragments.csv. The link tables carry a fragment_of column.
   - n_*_linked_enzymes no longer count fragments.
e. Name rules:
   - osmolytes: betaines, carnitines, trimethylammonio names, ectoines, hypotaurine;
   - amino acids: added the approved list;
   - peptides: bradykinin, microcin, bacitracin;
   - polyamines: sym-homospermidine;
   - nucleobases/nucleosides: 5-fluorouridine, 'a purine nucleobase';
   - new class 'amino sugars' (can_use_applicable False; it also applies to no_formula groups);
   - ammonium analogues are now only methyl- and ethylamine/-ammonium (plus the generic 'ammonium ion derivative' and 'alkylamine').
     Tetramethyl- and tetraethylammonium get no class.
     Triethylamine, dimethylamine, trimethylamine and diethylamine go to 'amines'. They are tertiary or secondary alkylamines,
     not methylammonium-type ammonium analogues.
Also:
- p12 system_substrates_classified has a class_caveat column on every row.
- p11 function_linked and neighbour_linked tables have system_tier and system_is_transporter_candidate (High/Medium) columns.

## Runs
- Tests: 158 OK (21 + 137).
- run_pipeline: all three strains, exit 0.
- After the fragment-parent fix, p11 and p12 were re-run on their own (run_log.json does not record that re-run).
- Report script: scripts/p15_report_v14.py, writing data/p15_*.csv and data/p15_report.json, and regenerating data/p12_review_list_unclassified_N.csv.
