# Step 2 — What the KG holds for these families (coverage probe)

## Context

Step 1 locked the question: build a per-family characterization dossier for the 14
core conserved-hypothetical families. Before designing the dossier columns (step 3),
this step probes **what the KG actually returns** for these ortholog groups across
every angle, so we only build columns the data can fill. Interactive discovery step
(Rule 5 exception): exploratory probing, frozen to CSV + this notebook.

Probed on a small **driving set** — three dark core-family representatives plus the
GroEL positive control — all in *Prochlorococcus* MED4 (deepest-studied strain, so
best-case coverage):

| locus_tag | cyanorak OG | role | product |
|---|---|---|---|
| PMM0872 | CK_00000141 | dark | uncharacterized conserved secreted protein |
| PMM1028 | CK_00000141 | dark (MED4 paralog of PMM0872) | uncharacterized conserved secreted protein |
| PMM0983 | CK_00003473 | dark | uncharacterized secreted, Prochlorococcus-specific |
| PMM1683 | CK_00000498 | dark | HesB-like domain-containing protein |
| PMM1436 | CK_00008054 | **control** | groL1 / chaperonin GroEL |

## What I did

`scripts/probe_coverage.py` (run: `uv run python .../2_kg_selection/scripts/probe_coverage.py`)
runs each angle against the driving genes and freezes raw JSON + flattened CSV per
angle to `data/probe_*.{json,csv}`. Tools exercised: `genes_by_homolog_group`,
`gene_homologs(source=eggnog)`, `gene_overview`, `gene_neighbors`,
`gene_ontology_terms`, `gene_clusters_by_gene`, `gene_derived_metrics`
(+ `search_homolog_groups` to resolve the GroEL control to its cyanorak OG).

## Results — coverage map

Full map in `data/coverage_map.csv`. Verdict = how much the angle yields **for the
dark genes** (the control shows what "full" looks like):

| angle | dark-gene verdict | what it yields | dossier use |
|---|---|---|---|
| identity / annotation | thin | all `catch_all_only` (AQ 1), `cog_category=S` | baseline columns |
| **cross-organism homologs** | **discriminating** | broadest eggnog group's `genera` + `consensus_gene_name` | **KEY column** |
| genomic neighborhood | real | flanking genes on the MED4 contig | column |
| co-expression clusters | real when annotated | cluster name + functional description | column |
| ontology / domains / sequence | mixed | functional GO sparse; **SignalP + localization real** | column |
| derived metrics | real | pangenome, expr-class, localization, diel | column block |
| publication mentions | absent (0) | none for dark genes; 2 for GroEL | column (often empty) |

### The payoff angle — cross-organism homologs rescue function

cyanorak OGs are **cyanobacteria-only** (members span *Prochlorococcus* +
*Synechococcus*, never *Alteromonas*). Cross-organism reach comes from **eggnog**
groups, returned most-specific → broadest (Prochloraceae → Cyanobacteria →
Bacteria). The broadest group's `genera` and `consensus_gene_name` are the lead:

| family (rep) | broadest eggnog group | genera | rescued identity |
|---|---|---|---|
| CK_00000498 (PMM1683) | `COG0316@2` (Bacteria) | Alteromonas, Marinobacter, Pseudomonas, Shewanella, Synechococcus, … (cross-genus) | **`iscA`** — iron-sulfur cluster assembly |
| CK_00000141 (PMM0872) | `3486D@2` (Bacteria) | Prochlorococcus only | lineage-restricted (no rescue) |
| CK_00003473 (PMM0983) | `315YW@2` (Bacteria) | Prochlorococcus only | Prochlorococcus-specific (confirmed) |
| CK_00008054 (PMM1436, control) | `COG0459@2` (Bacteria) | Alteromonas, Pseudomonas, … (cross-genus) | `groEL` (control passes) |

So the homolog angle both **rescues function** for some "dark" families (CK_00000498
is IscA, not unknown) and cleanly marks others as genuinely lineage-restricted.

## Surprises

- **CK_00000498 is IscA, not dark.** The SS120 member `Pro0644` is gene-named `iscA`;
  members carry "Belongs to the HesB IscA family"; the broadest eggnog group is
  `COG0316` (iscA, FeS-cluster assembly) spanning *Alteromonas/Pseudomonas/Shewanella*.
  The "HesB-like domain-containing protein" consensus product hid a named function. A
  single look at the broadest homolog group surfaced it. `[KG]`
- **SignalP scores are stored per gene** — `gene_ontology_terms(ontology=signal_peptide_type)`
  returns SignalP probability + cleavage site, so "secreted" annotations are backed by
  real scores (PMM0983 prob 0.999 cleavage@23). A concrete sequence feature for dark
  genes. `[KG]`
- **`pangenome_membership` derived metric** (Wang 2014) labels each MED4 gene Core vs
  Flexible — directly relevant to the conservation story (PMM1028=Flexible despite a
  conserved cyanorak OG; GroEL=Core). `[KG]`
- **Publication mentions are empty for the dark genes** (count 0) but present for GroEL
  (2). The "discussed in a paper" angle will mostly be blank — recorded as a hit when
  it fires, not expected to populate broadly. `[KG]`
- **Tooling:** `to_dataframe` drops the polymorphic derived-metric `value` column (and
  nested list columns); raw JSON preserves them. Step 5 extraction must read `value`
  from JSON or `pd.DataFrame(result["results"])`, not the flattened CSV. Logged in
  `gaps_and_friction.md`.

## Decisions

- **2026-06-16 — All six angles carry enough signal to become dossier columns.** None
  is empty enough to drop. Publication mentions stay in despite being usually blank
  (cheap, and a hit is high-value).
- **2026-06-16 — Cross-organism homologs is the lead angle**, operationalized as the
  broadest eggnog group's `genera` / `has_cross_genus_members` / `consensus_gene_name`
  (function rescue), reported alongside the cyanorak (cyanobacteria) group. The
  selection analysis measured conservation on cyanorak only; this analysis adds the
  eggnog breadth axis. Carried into step-3 framing.
- **2026-06-16 — "Conserved neighborhood" needs cross-strain checking**, not just MED4
  flanks; the cross-strain conservation test is deferred to the step-4 methods module.

## Decide-gate checklist

- **Outputs produced** — `scripts/probe_coverage.py`; `data/probe_*.{json,csv}` (7
  angles); `data/coverage_map.csv` (frozen summary).
- **Results presented** — coverage map + cross-organism homolog table (above), shown
  in chat and recorded here.
- **QC gate** — probe script ran green against KG 0.1.0-alpha.6 (Neo4j reachable);
  member counts match cyanorak OG sizes (CK_00000141=28, CK_00000498=23,
  CK_00003473=20); GroEL control returns full coverage on every angle (positive
  control passes); the two Prochlorococcus-restricted families return single-genus at
  Bacteria level (negative/absence control passes).
- **Decisions made this step** — all six angles kept; homologs is the lead; conserved
  neighborhood deferred to methods (above).
- **Advance rationale** — the KG demonstrably holds fillable data for every angle and
  the discriminating signals are identified; ready to fix the dossier schema and define
  what a "lead" is in step 3.
