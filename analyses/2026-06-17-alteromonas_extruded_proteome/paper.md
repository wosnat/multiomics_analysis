# Alteromonas extruded proteome — genes whose products are measured leaving the cell

## Question

Which Alteromonas genes encode products that the lab has **measured leaving the
cell** — detected either in the secreted **exoproteome** or as **membrane-vesicle
cargo** — and what is that annotated locus-tag list?

Scope: observed evidence only (exoproteomics + vesicle proteomics); no sequence-based
secretion prediction (PSORTb / SignalP) used to *define* the set. Output keyed on
locus tags, gene names as labels only. A researcher-driven extension then asked which
of the extruded proteins are **exoenzymes that break down organic compounds**, and how
that compares to the strains' full genomic repertoire.

## Background

The lab measures proteins leaving *Alteromonas macleodii* cells by two routes: the
secreted exoproteome (cell-free supernatant) and membrane-vesicle (MV) cargo. In this
KG release the two routes are measured on **disjoint strains** — exoproteome on EZ55
(Lu et al. 2025), MV cargo on six other strains (Fadeev et al. 2022). To combine across
genomes, every measured gene is mapped to its **eggNOG ortholog group at the
Alteromonadaceae level** (most-specific, single-genus), and the question is asked at the
ortholog-group (OG) level: which OGs are extruded, by which route, in how many strains.

## Methods

**KG.** multiomics-kg release `0.1.0-alpha.6` (built 2026-06-16, git ffef4007),
explorer-MCP `0.1.0a4` (release verdict ok, 16/16 schema asserts). All data via the
`multiomics_explorer` Python API / MCP tools; no external data.

**Selection (step 2).** `list_experiments(organism="Alteromonas",
omics_type=["EXOPROTEOMICS","VESICLE_PROTEOMICS"])` → 7 experiments: 1 EZ55 exoproteome
(`all_detected_genes` scope), 6 vesicle proteomes (MIT1002, BS11, ATCC27126, BGP6, AD45,
HOT1A3; `top_n` scope). Routes cover disjoint strains.

**Combining unit (step 3, verified).** eggNOG OG at specificity_rank 1 /
taxonomic_level Alteromonadaceae (`gene_homologs`, source="eggnog"). Two genes from
different strains belong to the same extruded OG iff they share this group. cyanorak
OGs are cyanobacteria-only and absent for Alteromonas.

**Extrusion definition.** An OG is extruded if it contains ≥1 gene measured leaving the
cell: **secreted** = EZ55 `exoproteome_detection_replicates ≥ 1` (tested-absent metric;
median 0 — value-0 rows were looked for and not detected), or **vesicle** = membership
in a strain's MV-cargo list (`prop_abund_mvs_percent`).

**Exoenzyme classification (step 5 extension).** Per-gene annotations via
`gene_ontology_terms`. A gene is a degradative-enzyme candidate if it carries
EC 3.1/3.2/3.4/3.5, a CAZy GH/PL/CE family, or a GO-MF/Pfam name matching a hydrolase
pattern. Export evidence (signal peptide / localization) is a confidence **tier**, not
a gate, because the protein is already measured extruded: tier A = degradative +
exported (signal peptide or OM/extracellular/periplasmic); tier B = degradative, no
export annotation; tier C = degradative + cytoplasmic (excluded as likely
contamination). Pfam is load-bearing — PhoX carries no EC/GO term, only Pfam PF05787.
The same classifier (`5_analyze/scripts/exoenzyme_lib.py`) was run on all 27,759 genes
of the 7 genomes (locus tags via `run_cypher`) as a background denominator.

**Reproduce.** `5_analyze/scripts/01_build_catalogue.py` (catalogue),
`02`/`03` (route profiles), `04`/`05`/`06` (exoenzymes: extruded, genome, OG-level).

## Results

**Extruded catalogue.** 318 measured genes → **145 extruded OGs** (0 unmapped). 74 are
single-strain, 71 recur in ≥2 strains (max 6). Secreted EZ55: 234 tested → 69 detected
(≥1 replicate). Vesicle: 15–58 MV proteins per strain.

**Composition.** Both routes are dominated by abundant cytoplasmic protein: Translation
is 39% of the secreted set (27/69) and 30% of vesicle cargo (75/249). Vesicle cargo is
more envelope-enriched than the exudate (Cell-wall-and-membrane 15% vs 6%).

**Vesicle cross-strain agreement.** 101 vesicle OGs; 63 (62%) shared by ≥2 of 6 strains;
6 OGs present in all 6; pairwise Jaccard mean 0.31. The all-6 conserved core is **mixed**
— TolC (OM efflux channel), OmpA (OM), MotA/TolQ/ExbB (inner-membrane proton channel),
PhoX (periplasmic phosphatase), glutamate–ammonia ligase (cytoplasmic glutamine
synthetase), DUF3450 (unknown): envelope-enriched (4/6 membrane/periplasmic) but not
uniformly secretion machinery.

**Cross-route corroboration.** Secreted is EZ55-only, so the "both-routes" set is
EZ55-anchored: 25 of the 69 EZ55-secreted OGs also appear in another strain's vesicle
cargo, and 23/25 are cytoplasmic by annotation — an abundance/co-detection signal, not
conserved dual export.

**Exoenzymes for organic-compound breakdown (verified).** Of the extruded set, 3 OGs
are genuine exoenzymes after KG verification:

| Function | Enzyme / OG | Route | Strains | Locus tags |
|---|---|---|---|---|
| organic-P scavenging | alkaline phosphatase **PhoX** | vesicle | all 6 | MIT1002_02422, AMBLS11_11110, MASE_11260, ALTBGP6_02414, AMBAS45_11875, ACZ81_11825 |
| proteolysis | **DegQ** serine endoprotease (EC 3.4.21.107) | secreted | EZ55 | EZ55_00820 |
| proteolysis | **M1** family aminopeptidase | secreted | EZ55 | EZ55_04077 |

(A 4th automated hit, `ALTBGP6_03431`, was verified as a TonB-dependent siderophore
receptor — its "carboxypeptidase activity" GO term derives from the non-catalytic
PF13620 regulatory-like domain — and dropped.) The verified exoenzymes split by route —
PhoX in vesicles, proteases in the exudate — but because the secreted route is measured
only on EZ55, this route split cannot be separated from the strain/method split (PhoX
appears vesicle-only because it was not among EZ55's detected exoproteins; the proteases
appear secreted-only because no other strain has exoproteome data). So the apparent
"division of labour" is consistent with, but not demonstrated over, a sampling artifact.

**Genome background.** The same classifier on all 27,759 genes yields **387 candidate
exoenzyme OGs** (200 tier A; 180 present in all 7 strains) across every substrate class.
The extruded measurement captured **3 verified OGs (~1%)**, and shows **no sign of
enrichment** for exoenzymes — if anything lower than background (tier-A rate 2.8%
extruded vs 3.9% genome; note the small extruded numerator, 9 genes). No
carbohydrate-active enzyme was captured in the extruded set despite the genomes carrying
52 carbohydrate-substrate OGs (mostly EC 3.2; ~11 with a CAZy annotation) — a sampling
gap, not a genomic absence.

## Discussion

The honest answer to "what Alteromonas genes are extruded?" is a **145-OG catalogue**,
but most of it is abundant cytoplasmic protein appearing in the exudate / vesicle
fractions — the defensible extruded signal is narrower:

1. **A reproducible vesicle core of 6 OGs** present in all 6 MV strains. It is mixed —
   envelope-enriched (the defensible members are TolC, OmpA, PhoX) but also containing
   an inner-membrane proton channel (MotA/TolQ/ExbB), a cytoplasmic glutamine synthetase,
   and an unknown (DUF3450). The envelope members are the strongest measured-extrusion
   signal; the core as a whole is not uniformly secretion machinery.
2. **A small, verified exoenzyme set:** **PhoX** (organic-phosphorus scavenging) in
   vesicles of every strain; **extracellular proteases** (DegQ, M1 aminopeptidase) in the
   EZ55 exudate. This is consistent with the marine copiotroph lifestyle (acquiring
   dissolved organic P and protein), though — as above — the route split is confounded
   with the strain/method split and cannot be read as a within-cell division of labour.

The genome comparison reframes the scope: these strains encode a broad, conserved
degradative repertoire (~387 candidate OGs, ~180 universal), of which the sampled
fractions captured ~1%. So the extruded data is a **thin, abundance-biased slice** of the
genomic exoenzyme potential, not an enriched secretome — useful for confirming specific
extruded enzymes (PhoX, DegQ), not for surveying the degradative repertoire.

**Caveats.** (1) Vesicle lists are `top_n` (15–58/strain) — recurrence and agreement are
lower bounds. (2) Secreted is EZ55-only — no within-strain dual-route comparison;
"both routes" is EZ55-anchored. (3) Extruded fractions are dominated by abundant
cytoplasmic protein — genuine cargo vs lysis/co-purification is unresolved here. (4) The
exoenzyme set is annotation-bound (Pfam load-bearing; genes with no functional term are
invisible) and is a conservative lower bound. (5) The genome denominator includes
intracellular signaling enzymes (c-di-GMP phosphodiesterases etc.) not given the
extruded set's false-positive QC, so per-substrate genome pools are upper estimates; the
tier-A "not enriched" conclusion is robust to this.

## References

- Fadeev E, Carpaneto Bastos C, Hennenfeind JH, Biller SJ, Sher D, Wietz M, Herndl GJ.
  *Characterization of membrane vesicles in Alteromonas macleodii indicates potential
  roles in their copiotrophic lifestyle.* DOI 10.1093/femsml/uqac025. (KG vesicle
  proteomes: 6 strains.)
- Lu Z, Plummer S, Kizziah J, Biller SJ, Morris JJ. *Enzymatically active exudates from
  Alteromonas facilitate Prochlorococcus survival in stationary phase.* Preprint
  DOI 10.1101/2025.05.28.656624. (KG EZ55 exudate exoproteome.)

KG release `0.1.0-alpha.6`; explorer-MCP `0.1.0a4`.
