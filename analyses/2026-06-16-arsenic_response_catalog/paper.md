# Prochlorococcus genes annotated for arsenic handling

## Question

Which *Prochlorococcus* genes in the KG carry a functional annotation for arsenic
handling — e.g. arsenate reductase, arsenite efflux pumps, ars-operon regulators?

This is a **catalogue** question: it identifies genes whose annotation implicates
them in arsenic metabolism, not genes whose expression has been shown to change
under arsenic exposure. "Responding to arsenic" (the researcher's opening prompt)
was narrowed to "annotated for arsenic handling" at step 1; whether these genes
actually move under arsenic is out of scope and flagged as a limitation.

## Background

The KG (release 0.1.0-alpha.6) holds **48 arsenic-named ontology terms**, all in the
enzyme / transporter / function ontologies (GO molecular function 14, EC 10, KEGG 8,
BRITE 5, TCDB 5, GO biological process 4, Pfam 2); the role-based (Cyanorak, TIGR,
COG) and localization ontologies carry none. Combining a free-text gene search (gene
name / product / functional description) with these ontology terms across the **19
*Prochlorococcus* genome strains** yields **61 arsenic-handling genes**, every one at
the highest annotation quality.

The canonical arsenic operon is well represented: **arsC (arsenate reductase) and
arsR (ArsR-family regulator) are near-universal** (19 and 16 of 19 strains), **arsB
(arsenate efflux / ACR3) is present in ~7 strains**, and **arsM (arsenite
methyltransferase) is named in only one strain (MIT1327)** — though an ontology-anchored
search reveals an unnamed "methyltransferase domain protein" mapped to the arsenite
methyltransferase KO/EC in ~13 further strains. Genes are reported strict (43; product
or name directly arsenic, or a canonical ars gene) vs broad (18; pulled in by a looser
link, including ArsR/SmtB-family regulators and — flagged — 2 ptxD phosphonate
dehydrogenases caught by ambiguous "phosphorus or arsenic" parent terms).

## Methods

The catalogue unions two sources, deduplicated by locus tag (script:
`2_kg_entries/scripts/01_arsenic_catalog.py`, built only from the dedicated KG tools —
no raw Cypher):

1. **Gene text** — `genes_by_function` over gene name / product / functional
   description for arsenic words and canonical ars gene names, one call across all
   strains; kept rows with a real `ars` token to drop fuzzy-scoring noise.
2. **Ontology links** — `genes_by_ontology` for the 48 arsenic-named terms, looped
   over the 19 strains × 6 ontologies that carry an arsenic term (the tool is
   single-organism; `min_gene_set_size=0`).

`gene_details` backfilled authoritative `organism_name` / `annotation_quality`.
Each gene is tagged **strict** (product or name directly arsenic, or a canonical ars
gene) vs **broad** (looser link only).

## Results

**61 genes across all 19 strains, all `annotation_quality = 3`** (frozen in
`2_kg_entries/data/arsenic_genes.csv`; gene × term evidence in `arsenic_gene_terms.csv`):

- **Strict (43):** arsC in all 19 strains, arsR in 16, arsB in 7, arsM named in 1.
- **Broad (18):** 13 unnamed methyltransferase-domain proteins mapped to the arsenite
  methyltransferase KO/EC (candidate arsM across ~13 strains), 3 ArsR/SmtB-family
  regulators, and 2 ptxD phosphonate dehydrogenases (phosphorus genes, flagged — pulled
  in by ambiguous "phosphorus or arsenic" parent terms).

The single most useful effect of casting the net broad: arsM, named in only MIT1327,
is recoverable as a function in ~14 strains once ontology annotation (not just gene
names) is searched.

## Discussion

The KG holds a coherent, high-confidence arsenic-detoxification gene set in
*Prochlorococcus* — arsenate reductase (arsC) and its ArsR regulator in essentially
every strain, an arsenite efflux pump (arsB/ACR3) in a subset, and an arsenite
methyltransferase (arsM) whose presence is far wider than its naming suggests.

This is a **catalogue, not a response**: the researcher narrowed "responding to arsenic"
to "annotated for arsenic handling" at step 1, so the deliverable lists genes whose
function points to arsenic — it does **not** show that any of them change expression
under arsenic exposure (the KG has no arsenic-exposure experiment in scope here).
Demonstrating an actual response would require differential-expression data under
arsenic, which this analysis does not assess.

### Limitations

Annotation-based, not expression-based (above). Two `arsC`-named genes (RSP50, MIT1314)
are likely Spx/MgsR redox regulators misfiled under the arsC name; the broad set
includes 2 phosphorus genes (flagged) and ArsR/SmtB-family regulators that may sense
metals other than arsenic. This analysis was run as a quick demo and stops at the
step-2 catalogue by researcher decision; framing, response testing, and ortholog-level
consolidation (steps 3–6) were not performed.

## References

Data source: multi-omics knowledge graph, release 0.1.0-alpha.6 (built
2026-06-16; counts from `kg_release_info`).
