# Alteromonas extruded proteome — genes whose products are measured leaving the cell

## Question

Which Alteromonas genes encode products that the lab has **measured leaving the
cell** — detected either in the secreted **exoproteome** or as **membrane-vesicle
cargo** — and what is that annotated locus-tag list?

Scope: observed evidence only (exoproteomics + vesicle proteomics); no sequence-based
secretion prediction (PSORTb / SignalP). Output keyed on locus tags, gene names as
labels only. Strain coverage determined in step 2 from what the KG actually holds.

## Background

The lab measures proteins leaving Alteromonas cells by two routes: the secreted
exoproteome (cell-free supernatant) and membrane-vesicle (MV) cargo. In this KG
release these routes are measured on **disjoint strains** — exoproteome on EZ55
(Lu et al. 2025), MV cargo on six other *A. macleodii* strains (Fadeev et al.
2022). To combine across genomes we map every measured gene to its **eggnog
ortholog group at the Alteromonadaceae level** (specificity_rank 1) and ask which
ortholog groups are extruded, by which route, and in how many strains.

## Methods

**Proposal (steps 1–3, locked).** Unit of analysis = eggnog Alteromonadaceae-level
ortholog group. An OG is "extruded" if it contains ≥1 Alteromonas gene measured
leaving the cell: secreted = EZ55 `exoproteome_detection_replicates ≥ 1` (the
metric is tested-absent; median 0), or vesicle = membership in a strain's MV-cargo
list. Deliverable: annotated OG catalogue with route(s), recurrence (n of 7
strains), and per-strain locus tags. Positive control: TonB-dependent receptors.
Driving example: MIT1002 vesicle list.

_(extraction + OG-mapping detail populated from step 4 onward)_

## Results

_(populated from step 5 onward)_

## Discussion

_(populated at step 6)_

## References

_(publications resolved via list_publications; cited by DOI / KG experiment ID)_
