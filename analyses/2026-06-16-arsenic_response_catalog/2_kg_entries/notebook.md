# Step 2 — KG entries (the arsenic-handling gene catalogue)

## Context

Step 1 locked the question to a **catalogue** of *Prochlorococcus* genes annotated
for arsenic handling. This step enumerates those genes from the KG and freezes them.
Researcher steer for this step: cast the net **broad** — search **all ontologies**
and **multiple gene fields**, not just genes whose product names an arsenic enzyme.

Tooling steer: use the dedicated KG tools (`genes_by_function`, `genes_by_ontology`),
**not** the `run_cypher` escape hatch.

## What I did

Two sources, unioned and deduplicated by locus tag (script:
`2_kg_entries/scripts/01_arsenic_catalog.py`, run from repo root):

1. **Gene text** — `genes_by_function(search_text="arsenic OR arsenate OR arsenite
   OR arsenical OR acr3 OR arsA..arsR", organism="Prochlorococcus")`, one call over
   all strains, searching gene name / product / functional description. Kept rows
   with a real `ars` token (drops fuzzy-scoring noise like PTOX / alternative
   oxidase). → **46 genes**.
2. **Ontology links** — for the 48 arsenic-named terms found via `search_ontology`
   (below), `genes_by_ontology(...)` looped over the **19 *Prochlorococcus* strains
   × 6 ontologies** that carry an arsenic term (`genes_by_ontology` is
   single-organism, so strains are looped; `min_gene_set_size=0`). → **58 genes**
   (226 gene × term rows).

Authoritative `organism_name` / `annotation_quality` / `gene_category` for every
gene were backfilled with `gene_details` (the ontology tool omits them).

### Ontology term inventory (`search_ontology`, term-name match on `arsen*`)

48 arsenic-named terms exist in the KG, all in the enzyme/transporter/function
ontologies; the role-based (Cyanorak/TIGR/COG) and localization ontologies carry
none.

| Ontology | Arsenic terms |
|---|---|
| GO molecular function | 14 |
| EC number | 10 |
| KEGG orthology | 8 |
| BRITE | 5 |
| TCDB transporter | 5 |
| GO biological process | 4 |
| Pfam | 2 |
| go_cc / cog / cyanorak / tigr / cazy / localization / signal peptide | 0 each |
| **Total** | **48** |

## Results

**61 genes** across all **19 *Prochlorococcus* strains**; every gene is
`annotation_quality = 3` (highest). Frozen to `data/arsenic_genes.csv` (one row per
gene) and `data/arsenic_gene_terms.csv` (one row per gene × matched ontology term).

### Strict vs broad

`strict` = product or functional description names arsenic directly, or gene_name is
a canonical ars gene (arsA/B/C/D/H/M/R, acr3). `broad` = pulled in only via a looser
link.

| scope | genes |
|---|---|
| strict | 43 |
| broad | 18 |

### Canonical ars genes (strict) — strain coverage

| gene | product | strains |
|---|---|---|
| arsC | arsenate reductase (ArsC family) | 19 (all) |
| arsR | ArsR-family transcriptional regulator | 16 |
| arsB | arsenate efflux pump / ACR3 | 7 |
| arsM | arsenite methyltransferase | 1 (MIT1327 only) |

So **arsC and arsR are near-universal**, **arsB is present in ~7 of 19 strains**, and
**arsM is named in only one strain**.

### What the broad net added (18 broad genes)

| broad group | n | how matched | note |
|---|---|---|---|
| methyltransferase-domain proteins | 13 | ontology → arsenite methyltransferase KO/EC (K07755 / 2.1.1.137) | candidate **arsM** in ~13 strains that text missed (only MIT1327 is *named* arsM) |
| ArsR/SmtB-family regulators (czrA + 2 unnamed) | 3 | text → "ArsR family" product | ArsR/SmtB is a broad metal-sensing family; may regulate Zn/Co, not only arsenic |
| ptxD phosphonate dehydrogenase | 2 | ontology → generic "phosphorus **or** arsenic in donors" parent GO/EC terms | **phosphorus genes, not arsenic** — false positives from ambiguous parent terms |

### match_source

| source | genes |
|---|---|
| both (text + ontology) | 43 |
| ontology only | 15 |
| text only | 3 |

The ontology-only set (15) is exactly the broad value-add: 13 unnamed arsM
candidates + 2 ptxD. The text-only set (3) is the ArsR-family regulators with no
arsenic-specific ontology edge.

## Surprises

- **arsM hides under a generic name.** Only MIT1327 carries the `arsM` gene name, but
  13 more strains have a "methyltransferase domain protein" mapped to the arsenite
  methyltransferase KO/EC. The broad ontology net is what surfaced them — a text-only
  search would have reported arsM in 1 strain instead of ~14.
- **The "phosphorus or arsenic" parent terms leak phosphorus genes.** GO/EC terms
  like *oxidoreductase activity, acting on phosphorus or arsenic in donors* are not
  arsenic-specific; walking down from them pulled 2 ptxD phosphonate dehydrogenases.
  Tagged `broad` and flagged, not silently included as arsenic genes.
- **Two arsC entries are likely Spx/MgsR regulators** (RSP50, MIT1314): gene_name
  arsC and "Belongs to the ArsC family", but product is "Spx/MgsR family RNA
  polymerase-binding regulatory protein". ArsC and Spx are homologous; these may be
  redox regulators misfiled under the arsC name. Kept as strict (the rule keys on
  gene_name) but noted.

## Decisions

- **2026-06-16 — Keep broad hits, tag rather than drop.** Per the researcher's "broad"
  steer, ArsR-family regulators, unnamed arsM candidates, and the phosphorus-ambiguous
  ptxD genes are retained in the catalogue with a `scope=broad` tag and transparent
  `matched_terms`, rather than filtered out. The strict subset (43) is the defensible
  core; the broad subset (18) is the exploratory edge.

## Decide-gate checklist

- **Outputs produced** —
  `2_kg_entries/scripts/01_arsenic_catalog.py`;
  `2_kg_entries/data/arsenic_genes.csv` (61 genes),
  `2_kg_entries/data/arsenic_gene_terms.csv` (226 gene × term rows),
  `2_kg_entries/data/01_arsenic_catalog.log`.
  Run: `uv run python analyses/2026-06-16-arsenic_response_catalog/2_kg_entries/scripts/01_arsenic_catalog.py`
- **Results presented** — ontology-term inventory, strict/broad split, per-gene strain
  coverage, broad-net breakdown, match_source — all shown inline above and in chat.
- **QC gate** — all 61 genes resolve to a strain and `annotation_quality=3` via
  `gene_details` (no orphan/blank rows) → catalogue is complete and high-quality.
  Net cross-checked: text recovers named ars genes; ontology recovers unnamed arsM
  candidates; the only contamination (2 ptxD) is identified and tagged.
- **Decisions made this step** — keep-and-tag broad hits (2026-06-16, above).
- **Advance rationale** — the arsenic-handling gene set is enumerated, frozen, and
  QC'd, with strict/broad transparency.

## Analysis stop (2026-06-16)

Per researcher decision, this quick-demo analysis **ends at the step-2 catalogue**.
Steps 3–6 (framing, methods, analyze, evaluate) are not performed — the frozen
catalogue is the deliverable. `paper.md` was finalized as a short catalogue paper with
the annotation-vs-response limitation made explicit.
