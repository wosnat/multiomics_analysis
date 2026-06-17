# Step 2 — KG entries (selection)

## Goal

Find the Alteromonas measurements that bear on "products measured leaving the
cell," and read off strain coverage (deferred from step 1).

This is an interactive discovery step (Rule 5 exception): scoping what the KG
holds, done interactively but frozen to `data/kg_entries.csv`.

## Query

`list_experiments(organism="Alteromonas", omics_type=["EXOPROTEOMICS",
"VESICLE_PROTEOMICS"], verbose=true)` → 7 experiments, no others matched.

## What's in the KG `[KG]`

**Secreted route (exoproteome) — 1 experiment, 1 strain**
- EZ55 exudate (>50 kDa cell-free supernatant) proteome — 234 genes carry
  `exoproteome_detection_replicates`. Scope `all_detected_genes`.
- Lu et al. 2025 preprint (`10.1101/2025.05.28.656624`).

**Vesicle route (MV cargo) — 6 experiments, 6 strains**
- MIT1002 (92), BS11 (90), ATCC27126 (88), BGP6 (76), AD45 (73), HOT1A3 (63)
  most-abundant MV proteins. Metrics: `log2_mv_cell_enrichment`,
  `prop_abund_mvs_percent`, `prop_abund_cells_percent`. Scope `top_n`.
- Fadeev et al. 2022 (`10.1093/femsml/uqac025`).

## Decisions forced by the data

1. **Routes cover DISJOINT strains.** Exoproteome = EZ55 only; vesicle = the
   other 6 strains. No strain measured by both routes → the "union" is two
   separate gene lists on different genomes; locus tags are not comparable
   across routes, and same-strain "secreted AND vesicle?" cannot be asked. `[KG gap]`
2. **Different completeness.** Vesicle lists are `top_n` (top abundant MV
   proteins only, 63–92/strain); exoproteome is `all_detected_genes` (complete
   for that fraction). "Extruded" is measured at different depth per route. `[KG]`

These two facts go to step 3 framing (how to present the union honestly).

## Output

- `data/kg_entries.csv` — frozen 7-experiment selection with route, scope,
  gene counts, metric handles, DOI.

## Decide

- [x] All relevant experiments found (exoproteome + vesicle); none missed
- [x] Strain scope settled: EZ55 (secreted) + 6 strains (vesicle), disjoint
- [x] Metric handles identified for step 4 extraction
- [x] Selection frozen to CSV
- [x] Researcher approves selection and the two data-shape caveats → commit

## Researcher decision → step 3 direction

- Keep **both routes, combined** (framing A).
- **Combine via ortholog groups (OG)** — all 7 strains are *A. macleodii*, so
  map each strain's extruded genes to shared OGs. The OG becomes the comparable
  unit that bridges the disjoint genomes; locus tags remain per-strain labels.
- This directly answers the disjoint-strain gap from decision 1 above.
