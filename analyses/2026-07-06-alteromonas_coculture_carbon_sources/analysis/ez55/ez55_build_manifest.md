# EZ55 transporter table — build manifest (facts only)

Built by `build_ez55_table.py`, which reuses the committed HOT1A3 pipeline verbatim (same enumeration union, 150 bp adjacency + KO-name role boundary rule, finest-confident substrate resolution, and non-importer veto) applied to **Alteromonas macleodii EZ55** (locus-tag prefix `EZ55_`). `methods/` code unchanged.

## Enumeration (union of four sources)

- BRITE transporters tree `ko02000`: 320 genes
- KEGG-KO transporter-named: 228 genes (of 2362 KEGG-annotated)
- TCDB: 437 genes
- product/function search (transporter-filtered): 424 genes
- **UNION candidate transporter genes: 599**

## Systems reconstructed

- Candidate transporter genes: **599**
- Transport systems reconstructed: **539** (size dist n_genes:count = {1: 499, 2: 28, 3: 7, 4: 2, 5: 3})
- Adjacency gap ceiling: 150 bp (same contig, same strand)

## Resolution level distribution (per system)

- specific_compound: 126
- narrow_class: 13
- multi_substrate: 16
- broad_class: 19
- unresolved: 365

## Classification

- importer: 366; exporter/efflux: 113; non_transporter (import veto): 60
- organic: 72; inorganic: 110; unknown: 357
- **organic-carbon importer systems: 54** (by resolution level: {'multi_substrate': 14, 'broad_class': 10, 'specific_compound': 18, 'narrow_class': 12})
- import veto reclassified 70 systems out of the importer set (by reason: {'enzyme / biosynthesis': 39, 'protein-export/secretion': 11, "mechanosensitive ion channel; organic call is a spurious 'membrane lipid bilayer' match": 10, 'surface-polysaccharide / cell-envelope biosynthesis-export': 10}).
