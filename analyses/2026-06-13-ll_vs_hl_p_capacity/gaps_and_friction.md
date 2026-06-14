# Gaps and friction

Transitional log of methodology / KG / tooling friction encountered during this
analysis, distinct from decisions (which live in each step's `notebook.md`).
Append-only. Each entry: date, short name, what happened, workaround, downstream
impact.

---

## 2026-06-13 — genes_by_ontology organism resolver gates on expression edges (BUG)

**What happened.** `genes_by_ontology` (via shared `_validate_organism_inputs`,
`multiomics_explorer/api/functions.py:2255`) raises
`ValueError: no organism matching '<name>' found` for *Prochlorococcus* genome
strains that lack gene **expression edges** — both genome-only strains
(experiment_count=0: MIT9515, MIT0604, MIT9202, MIT9215, SB, PAC1, MIT1327) and
metabolomics-only strains (MIT0801, experiment_count=6 but METABOLOMICS-only).
Their genomic annotations (Gene nodes, `Gene_has_cyanorak_role`,
`Gene_in_ortholog_group`) are fully present — confirmed via `run_cypher`:
e.g. MIT9515 has 29 D.1.5 genes, 1464 Cyanorak-role genes. The resolver gates a
**genomic** query on the presence of **expression** data, which is inverted for
genomic-capacity questions.

**Workaround.** `run_cypher` reaches the genomic layer for every strain and was
used to confirm the true panel (17 Cyanorak-annotated strains). For the dogfood
itself, per researcher instruction, we used the MCP tools as-is and restricted
to the 9 resolvable strains.

**Downstream impact.** Halved the achievable panel (17 → 9) and unbalanced it
(4 HL / 5 LL), weakening presence/absence power. Researcher confirmed the bug
will be fixed after this session; re-running steps 2–5 on the full 17-strain
panel is the natural follow-up once fixed.

## 2026-06-13 — Cyanorak role D.1.5 is broader than "acquisition machinery"

**What happened.** The curated role `cyanorak.role:D.1.5` ("...Phosphorus")
mixes true P-acquisition/scavenging genes (pstSCAB, phnCDE, phoBR, phoH, phoC,
ppk2, sphX, sqdB, porins) with P-stress-*responsive* but non-acquisition genes
(ribosomal proteins rplJ/L/R, dnaK3, ahpC, pentose-phosphate enzymes gnd/pgl,
glgP, galM, prfC). Using the role as-is inflates counts with regulon-responsive
genes. Not a bug — a curation-granularity nuance the framing must handle.

**Workaround / impact.** Reported the full role at step 2; the focused
acquisition subset (transporters/phosphatases/regulators/phosphonate/polyP/
sulfolipid) is a step-3 framing decision. Methodology note: when a curated role
is "stress-associated" rather than "function-defined", verify membership against
products before treating the count as a capacity measure.

## 2026-06-13 — GO/KEGG too sparse to define the P gene set in this KG

**What happened.** GO annotation in this KG tags only the Pst transporter
(~5 genes/strain; captures 4–6 of 10 core acquisition genes), missing
phosphonate transport, the phoBR two-component system, phoH, and
cyanobacteria-specific/hypothetical P genes. KEGG P-orthologs are scattered with
no single acquisition pathway. Generic ontologies undercount and, worse, could
bias an HL-vs-LL comparison if annotation completeness differs by strain.

**Workaround / impact.** Chose curated Cyanorak roles as the primary handle
(coverage QC in `2_kg_entries/data/qc_ontology_coverage.csv`); GO/KEGG retained
only to cross-validate core transporters. Methodology note: for non-model
organisms, validate ontology coverage before trusting a generic-ontology gene
set for presence/absence comparisons.
