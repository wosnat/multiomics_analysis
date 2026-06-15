# Step 2 — KG entries

## Context

Step 1 locked the question: does Alteromonas turn motility genes up or down in
coculture with Prochlorococcus vs alone, across strains with the contrast? Step 2
freezes the inputs: the experiments and the motility gene sets.

This step was co-defined — we agreed to look at what data exists, then settled two
choices together: the gene-set definition and the strain set.

## What I did

Grounding queries (MCP): `list_experiments(organism="Alteromonas", ...)`,
`search_ontology(kegg, "flagellar assembly OR chemotaxis")`,
`list_derived_metrics(organism="Alteromonas", ...)`, and
`genes_by_ontology` for the COG and KEGG gene sets.

`scripts/01_extract_entries.py` froze: the coculture experiments per strain
(`data/coculture_experiments.csv`) and the motility gene sets
(`data/motility_genes.csv`, one row per strain × gene, flagged for each
definition).

## Results

### The comparison experiments `[KG]`

Coculture-with-Prochlorococcus vs alone (the primary contrast):

| strain | study (DOI) | what's compared | reported |
|---|---|---|---|
| HOT1A3 | Weissberg 2025 (10.1101/2025.11.24.690089) | with Prochlorococcus MED4 vs axenic | all genes |
| HOT1A3 | (10.1038/s43705-022-00197-2) ×2 | with Prochlorococcus vs Pro99-medium (alone) | all genes |
| EZ55 | Hennon 2017 (10.1038/ismej.2017.189) ×2 | with Prochlorococcus vs alone, at 400 & 800 ppm CO₂ | significant only |

**Reporting asymmetry:** HOT1A3 reports all detected genes (so a gene that was
measured and did not change is visible), while EZ55 reports only significant genes
(so "not listed" could mean unchanged *or* not measured). HOT1A3 is therefore the
solid case; EZ55 a cross-check.

**Control bonus:** EZ55 also has 4 coculture-*with-Synechococcus* vs alone
experiments — a partner-specificity control for step 3 (motility-to-any-partner vs
motility-to-Prochlorococcus).

### The motility gene sets `[KG]`

Per strain, two definitions (agreed: report both):

| strain | KEGG flagella+chemotaxis | COG-N "Cell motility" | union | COG-N adds |
|---|--:|--:|--:|--:|
| HOT1A3 | 96 | 126 | 144 | ~48 (pili/twitching) |
| EZ55 | 102 | 131 | 151 | ~49 |

KEGG (flagellar assembly ko02040 + bacterial chemotaxis ko02030) is the tight,
pathway-defined core matching the question wording; COG category N is the broad
eggNOG motility category, adding pili/twitching-motility genes.

### Pre-built motility measures (leads) `[KG]`

EZ55 (Hennon 2017) ships published motility enrichment sets: flagellar-assembly
(38 genes) and bacterial-chemotaxis (56 genes). MIT1002 (Aharonovich/Sher 2018)
has day-night periodicity flags in coculture — but MIT1002 lacks the
coculture-vs-alone contrast, so it stays out of scope.

## Decisions

- **2026-06-15 — gene set: both definitions, side by side.** KEGG
  flagella+chemotaxis as the primary set; broad COG-N as a sensitivity check.
- **2026-06-15 — strains: HOT1A3 + EZ55.** MIT1002 (time-course within coculture,
  no alone comparison) and the MarRef proteomics set (glucose contrasts) lack the
  clean coculture-vs-alone contrast, so they are out.

## Decide-gate checklist

- **Outputs produced:** `scripts/01_extract_entries.py`;
  `data/coculture_experiments.csv` (9 rows), `data/motility_genes.csv` (295 rows),
  log.
- **Results presented:** experiments table, gene-set coverage table, control bonus
  (above).
- **QC gate:** confirmed both strains have a coculture-vs-axenic contrast with
  Prochlorococcus before locking scope; gene-set counts cross-checked (KEGG ⊂ COG-N
  mostly, COG-N adds pili). Reporting-scope asymmetry surfaced and recorded.
- **Advance rationale:** experiments and gene sets are frozen; step 3 can frame the
  test (direction of change, baseline/controls, expected outcome).
