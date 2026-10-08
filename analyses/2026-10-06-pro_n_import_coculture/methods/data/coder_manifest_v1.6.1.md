# Coder manifest: n_transport v1.6.1 (delta-critic fixes, 2026-10-08)

Facts only. Diff base: data/v1.6.0_archive.

## Changes
1. efflux_annotated (nt.efflux_annotated): product matches efflux|exporter|export|multidrug|drug resistance|RND|MATE|DevA type
   (case-insensitive, word-bounded), or gene name matches ^(devABC|evrABC|tolC|acrA|mdtA|ccmA|ycf38).
   - It is a column in p11_<tag>_systems.csv and p18_<tag>_listing_basis.csv. Flag only.
   - ccmA PMM0449/PMT1338 match by product ("ABC-type multidrug transport system...").
   - ycf38 PMM0450/PMT1337 ("ABC-2 type transporter family protein") match by gene name only.
2. p18 dedicated rule:
   - A Q-role-only call on an efflux-annotated system becomes "broad listing", detail "Q.1 only, efflux-annotated".
   - New columns: dedicated_basis (keyword | Q-role only | none) and dedicated_also_for (double counts).
   - Keyword map: word boundaries, plus a product_exclude_regex column (nitrate/sulfonate; amidotransferase | histidine kinase).
     cyanate becomes cyanate. osmo excludes OsmC. The glt gene prefix is limited to glt[S,P,I-L].
3. fig2:
   - Block A "+k" split into "(+k dedicated, +k broad)", on its own line.
   - "listed, not usable" examples are High/Medium systems only (fallback "best (<tier>)").
4. KNOWN_FALSE_POSITIVE_PRODUCTS adds MAPEG (mapeg|eicosanoid/glutathione metabolism).
5. The proV/W/X and proP double count (amino acids via 'proline' and osmolytes) is reported in the
   dedicated_also_for column and data/p19_double_dedicated.csv. It is not changed.

## Runs
- run_pipeline: all three strains, 14/14 steps, exit 0 (MED4 with --pilot).
- Tests: 193 OK:
  - test_kg_fetch: 21;
  - test_n_transport: 168;
  - test_real_data_invariants: 4, against data/v1.6.0_archive.
- Report script: scripts/p19_report_v161.py. It writes data/p19_dedicated_call_changes.csv, p19_lifted_loci_split.csv,
  p19_known_false_positive.csv, p19_mapeg_products.csv, p19_double_dedicated.csv and p19_report.json.
- f1 and q1 were re-run.
