# Step 3 — Analysis framing (research proposal lock)

## (a) Selection — from step 2

7 experiments: EZ55 exoproteome (secreted, complete `all_detected_genes`) + 6
vesicle proteomes (MV cargo, `top_n`) for MIT1002, BS11, ATCC27126, BGP6, AD45,
HOT1A3. Routes cover disjoint strains. See `../2_kg_selection/data/kg_entries.csv`.

## Feasibility probe — does the OG bridge exist? `[KG, verified]`

Pulled real loci from each route and looked up ortholog groups
(`gene_homologs`, verbose). Evidence frozen in `data/og_bridge_probe.csv`.

- Source is **eggnog** (cyanorak is cyanobacteria-only; absent for Alteromonas).
- Each gene maps to 3 nested groups: rank 1 = `Alteromonadaceae` (`...@72275`),
  rank 2 = `Proteobacteria`, rank 3 = `Bacteria`.
- The rank-1 `Alteromonadaceae` group has 3–10 *Alteromonas* members,
  single-genus — the right level to combine the 7 strains without pulling in
  Pseudomonas/Shewanella.

**Combining key (locked):** eggnog OG at specificity_rank 1 / taxonomic_level
`Alteromonadaceae`. Two genes (different strains) belong to the same extruded OG
iff they share this group.

## Two data-shape facts the probe surfaced

1. **Exoproteome metric is tested-absent.** `exoproteome_detection_replicates`
   spans 234 genes, median value = 0 — most were looked for and NOT detected.
   "Secreted" = value ≥ 1 (detected in ≥1 of 3 sublines), not table presence. `[KG]`
2. **Cytoplasmic proteins appear in both routes** (EF-Tu, thioredoxin, RidA,
   Dps). Known "cytoplasmic proteins in secretomes / MVs" issue — genuine cargo
   vs lysis. Flagged for step 6, not silently dropped. `[interpretation]`

## (b) Framing

**Target — "extruded OG":** an Alteromonadaceae-level eggnog group containing
≥1 Alteromonas gene measured leaving the cell, by either route:
- secreted — EZ55 gene with `exoproteome_detection_replicates ≥ 1`, or
- vesicle — gene present in any of the 6 strains' MV-cargo lists.

**Deliverable:** annotated OG catalogue — one row per extruded OG with consensus
product/function, route(s) (secreted / vesicle / both), recurrence (n of 7
strains), per-strain locus tags (Rule 2).

**Hypothesis:** a core set of OGs is extruded recurrently across strains and/or
by both routes (conserved extruded functions — outer-membrane transporters,
hydrolases), against a tail of strain- or route-specific OGs.

**Positive control:** TonB-dependent receptors (classic OM/MV cargo; already the
top vesicle hits in the probe). Must land in the extruded set and recur across
strains — if not, the pipeline is broken.

**Negative-control / honesty check:** the bulk of each genome is in no extruded
list (background). Cytoplasmic-protein presence flagged, not assumed clean.

**Expected outcome:** ranked OG table; TonB receptors among top recurrent OGs; a
small both-routes core; cytoplasmic contamination visible and flagged.

## Driving example for step 4

MIT1002 vesicle list (has a clean rankable abundance metric,
`prop_abund_mvs_percent`) → build extract → OG-map → annotate pipeline on one
strain, then generalize to all 7.

## Decisions locked

- Combining unit = eggnog Alteromonadaceae-level OG (rank 1).
- Secreted threshold = `exoproteome_detection_replicates ≥ 1`.
- Vesicle membership = presence in the strain's MV-cargo list (top-N as given).
- Both-routes / recurrence computed at the OG level.

## Decide

- [x] OG bridge verified (rank-1 Alteromonadaceae, eggnog) before framing on it
- [x] Target, hypothesis, controls, expected outcome stated in KG terms
- [x] Tested-absent (secreted ≥1) and cytoplasmic-contamination caveats recorded
- [x] Driving example chosen (MIT1002 vesicle)
- [x] Researcher approved framing → proposal locked, commit (closes steps 1–3)
