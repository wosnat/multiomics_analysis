# Methods run manifest — HOT1A3 transporter table

Facts only. Produced by `build_transporter_table.py` from the cached KG pulls (`pull_transporter_raw.py`).

## What ran

- `pull_transporter_raw.py` — enumerated candidate transporter genes by unioning four KG sources for *Alteromonas macleodii HOT1A3*, then pulled per-gene annotation. Cached to `cache/`.
- `build_transporter_table.py` — reconstructed systems, resolved substrates, classified importer/organic.

## Enumeration (union of four sources)

- BRITE transporters tree `ko02000`: 310 genes
- KEGG-KO transporter-named: 219 genes (of 2296 KEGG-annotated)
- TCDB: 427 genes
- product/function search (transporter-filtered): 415 genes
- **UNION candidate transporter genes: 592**

## Systems reconstructed

- Total transporter genes (candidate set): **592**
- Total transport systems reconstructed: **532**
- Multi-gene systems: 40; single-gene systems: 492
- Adjacency gap ceiling used: 150 bp (same contig, same strand)
- System size distribution (n_genes: count): {1: 492, 2: 28, 3: 7, 4: 2, 5: 3}

## Resolution level distribution (per system)

- specific_compound: 121
- narrow_class: 13
- multi_substrate: 15
- broad_class: 20
- unresolved: 363

## Classification

- importer: 357; exporter/efflux: 114; non_transporter (import veto): 61
- organic: 71; inorganic: 108; unknown: 353
- **organic-carbon importer systems: 53**
  - by resolution level: {'multi_substrate': 13, 'broad_class': 10, 'specific_compound': 17, 'narrow_class': 13}

## Import veto — non-importer leakage removed

A donor-based veto (applied to the substrate-donor gene) moves systems that are NOT membrane solute importers out of the importer set. Rows are KEPT; the reason is recorded in the `source` column (`reclassified: ...`). Grouping/systems and the 150 bp adjacency rule are unchanged.

- Total systems reclassified out of the importer set: **73** (by reason: {'enzyme / biosynthesis': 38, "mechanosensitive ion channel; organic call is a spurious 'membrane lipid bilayer' match": 12, 'protein-export/secretion': 10, 'surface-polysaccharide / cell-envelope biosynthesis-export': 13}).
- Of these, **6** were previously counted as **organic-carbon importers** and are now removed from that set:
  - `HOT1A3_TS028` [ACZ81_01020] was `glycerol` → now `non_transporter/organic`; reason: enzyme / biosynthesis.
  - `HOT1A3_TS050` [ACZ81_02260] was `arginine` → now `non_transporter/organic`; reason: protein-export/secretion.
  - `HOT1A3_TS216` [ACZ81_07985] was `saccharide` → now `non_transporter/organic`; reason: surface-polysaccharide / cell-envelope biosynthesis-export.
  - `HOT1A3_TS318` [ACZ81_13810] was `saccharide` → now `non_transporter/organic`; reason: surface-polysaccharide / cell-envelope biosynthesis-export.
  - `HOT1A3_TS348` [ACZ81_14900] was `lipid` → now `importer/inorganic`; reason: mechanosensitive ion channel; organic call is a spurious 'membrane lipid bilayer' match.
  - `HOT1A3_TS404` [ACZ81_16815] was `lipid` → now `importer/inorganic`; reason: mechanosensitive ion channel; organic call is a spurious 'membrane lipid bilayer' match.
- The full per-system list (all reclassified systems) is in `hot1a3_transporter_table.csv` — filter `source` for the `reclassified:` prefix.

## Substrate-call source distribution (per system)

- none (unresolved): 298
- kegg_ko: 58
- kegg_ko_keyword: 57
- reclassified: enzyme / biosynthesis (not a membrane solute transporter): 38
- product: 23
- function_description: 17
- reclassified: surface-polysaccharide / cell-envelope biosynthesis-export (not a solute importer): 13
- reclassified: mechanosensitive ion channel; organic call is a spurious 'membrane lipid bilayer' match: 12
- reclassified: protein-export/secretion (not a solute importer): 10
- tcdb_family: 4
- brite_leaf: 2

## Notes, anomalies, and places the KG was ambiguous (facts only)

- **Genome:** the HOT1A3 assembly in the KG has 2 contigs; all 592 candidate genes carry coordinates, so genomic ordering is unambiguous.
- **Adjacency calibration:** on known operons (Fe `ACZ81_00580/85/90`, phosphate `04030/35/40`, nitrate `03160/65/70`, Mla `03775..03795`) within-operon intergenic gaps are <200 bp while between-system gaps are >60 kb; the 150 bp ceiling (plus same-contig + same-strand) reproduces these operons as single systems. Gray-zone neighbour pairs (150-2000 bp) were inspected and are unrelated adjacent transporters, not one system.
- **Component roles read from the KEGG KO name** (substrate-binding / permease / ATP-binding); canonical systems reconstruct with the expected role strings (Fe SBP;PERM;ATP; phosphate PERM;PERM;ATP; dipeptide ATP;ATP;PERM;PERM;SBP kept whole per the repeated-role rule).
- **Many amino-acid / peptide ABC importers appear as 1-gene systems at their substrate-binding protein.** In HOT1A3's KEGG annotation the substrate-specific KO is carried by the binding protein (e.g. 7x `ABC.PA.S` polar-amino-acid SBP), while the permease/ATPase partners carry generic 'putative ABC' KOs and are not always genomically adjacent in the candidate set. These are reported as 1-gene systems that still carry a substrate call from the SBP KO -- the substrate resolution (the audit's purpose) is preserved; the system count is conservative (partners counted separately where distal).
- **Iron/siderophore TonB-dependent receptors:** 36 systems resolve to iron/siderophore (inorganic) from KO-name keywords (e.g. 'iron complex outermembrane receptor'), which do not follow the 'X transport system' pattern -- flagged `inferred`, source `kegg_ko_keyword`.
- **Non-transporters leaked into the broad union** (glutathione S-transferase enzymes, transcriptional regulators e.g. argP, the Tat protein-export system, flagellar motor proteins, glutathione-regulated K-efflux). A regulator/enzyme/protein-export context gate keeps them `unresolved` rather than donating a spurious import substrate; they inflate the candidate-gene count but not the resolved-substrate calls.
- **Confidence semantics:** `confident` = substrate read from the structured KEGG-KO 'X transport system' phrase or a BRITE leaf; `inferred` = read from a KO-name/product word-boundary keyword scan or a TCDB 2.A.x family. Word-boundary matching is used to avoid substring errors (e.g. 'lactose' inside 'galactose').
- **Aromatic/xenobiotic importers present** (benzoate, 3-phenylpropionic acid) -- these are the proposal's pre-registered expected-negative class; recorded here, to be checked at the analysis milestone (they should not dominate the up-regulated catalog).
- **`nitrate/nitrite` is tagged `multi_substrate`** (the KO names the pair); it is inorganic and not an organic-C candidate.
