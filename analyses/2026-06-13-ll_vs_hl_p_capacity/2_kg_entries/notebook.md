# Step 2 — KG entries

## Context

Step 1 locked the question: do LL Prochlorococcus ecotypes carry greater/different
**genomic** phosphorus-acquisition capacity than HL? Step 2 identifies the KG
entries that answer it: the organism panel, the P gene-set handle, the
cross-strain comparison unit (ortholog groups), and the relevant publications.

## KG context — gene-set handle decision

The P gene set is defined by the curated **Cyanorak functional role
`cyanorak.role:D.1.5`** ("Cellular processes > Adaptation/acclimation to atypical
conditions and detoxification > Phosphorus"). Chosen over GO/KEGG on measured
coverage (see QC below): GO is precise but far too sparse in this KG, and KEGG
P-orthologs are scattered with no single acquisition pathway. The cross-strain
comparison unit is the **curated Cyanorak ortholog group** (`source='cyanorak'`,
most-specific per gene) — curated for Prochlorococcus/Synechococcus, so a gene
family has one consistent identity across strains.

Researcher decision (step-2 dialogue): **Cyanorak backbone + focused subset** —
report the full D.1.5 role now; the focused acquisition subset is a step-3
framing decision. GO/KEGG used only to cross-validate core transporters.

## What I did

- `kg_release_info` (step 1): KG 0.1.0-alpha.6, verdict ok.
- Discovery (MCP): `search_homolog_groups`, `search_ontology` (cyanorak_role,
  kegg, go_bp, go_mf), `list_publications(treatment_type='phosphorus')`.
- **`scripts/01_extract_p_gene_entries.py`** — per-strain `genes_by_ontology`
  (cyanorak_role, D.1.5) → genes; `gene_homologs` (source=cyanorak) → most-specific
  OG; `list_organisms` → genome sizes. Outputs `data/p_role_genes_by_strain.csv`
  (319 rows), `data/strain_panel.csv` (9 rows).
- **`scripts/qc_ontology_coverage.py`** — Cyanorak vs GO coverage on MED4/MIT9313
  → `data/qc_ontology_coverage.csv`.

### Panel scope (dogfood-restricted)

The genomic ideal is all Cyanorak-annotated genome strains (17: 9 HL, 8 LL). But
`genes_by_ontology`'s organism resolver only resolves strains whose genes carry
**expression edges** — it rejects the 7 genome-only strains and the
metabolomics-only MIT0801, even though their genomic annotations are fully
present in the graph (resolver bug; see `gaps_and_friction.md`). Per researcher
instruction this dogfood uses the MCP tools as-is, restricted to the **9
resolvable strains (4 HL, 5 LL)**. RSP50 + MIT1314 are out regardless — they
carry no Cyanorak annotation at all (annotation absence ≠ biological absence).

## Results

### Strain panel (9 strains) `[KG]`

| ecotype | clade | strain | genome genes | D.1.5 genes | distinct P OGs | per 1000 genes |
|---|---|---|--:|--:|--:|--:|
| HL | HLI  | MED4    | 1976 | 31 | 29 | 15.69 |
| HL | HLII | AS9601  | 1951 | 26 | 24 | 13.33 |
| HL | HLII | MIT9301 | 1935 | 37 | 33 | 19.12 |
| HL | HLII | MIT9312 | 1978 | 37 | 32 | 18.71 |
| LL | LLI  | NATL1A  | 2226 | 35 | 30 | 15.72 |
| LL | LLI  | NATL2A  | 2214 | 35 | 30 | 15.81 |
| LL | LLII | SS120   | 1964 | 28 | 26 | 14.26 |
| LL | LLIV | MIT9303 | 3114 | 48 | 42 | 15.41 |
| LL | LLIV | MIT9313 | 2948 | 42 | 37 | 14.25 |

Raw D.1.5 counts: HL mean 32.8 (26–37), LL mean 37.6 (28–48). LL higher on raw
count, but **genome-normalized (per 1000 genes) the gap closes/reverses**: HL
mean 16.7, LL mean 15.1 — the two highest per-1000 values are HL (MIT9301 19.1,
MIT9312 18.7). The normalization confound flagged in step 1 is real and material.

### P ortholog-group inventory: 41 distinct Cyanorak OGs `[KG]`

Conserved core present in **all 9 strains** (n_strains=9): pstS, pstA, pstB, pstC
(Pi ABC transporter), phnC, phnD, phnE (phosphonate ABC transporter), phoH,
`som` (porin), sqdB (sulfolipid substitution), plus several broad/responsive
groups (rplJ/L/R, dnaK3, ahpC, gnd, pgl, glgP, galM, prfC). phoR in 7/9, phoB in
6/9 (regulatory two-component system; absences likely annotation/clustering, to
check in step 3).

Differential OGs (the "better-equipped" candidates) `[KG]`:

| OG | gene | product | n_HL (of 4) | n_LL (of 5) |
|---|---|---|--:|--:|
| CK_00000368 | spsA | sucrose-phosphate synthase/phosphatase fusion | 0 | 4 |
| CK_00001606 | ptrA | transcriptional phosphate regulator, Crp family | 0 | 4 |
| CK_00001999 | phoC | acid phosphatase | 0 | 2 |
| CK_00048151 | ppk2 | polyphosphate kinase 2 | 0 | 2 |
| CK_00001443 | mutT | NUDIX hydrolase | 0 | 2 |
| CK_00035906 | rlpA | rare lipoprotein A | 0 | 2 |
| CK_00002662 | PsiP1 | phosphate starvation inducible protein 1 | 1 | 0 |
| CK_00002826 | chrA | chromate transporter | 3 | 2 |
| CK_00006203/00008062/00048116 | phnD2/phnC2/phnE2 | phosphonate-utilization paralogs | 1 | 1 |
| CK_00056808 | ptxD | phosphonate dehydrogenase | 1 | 1 |

Full inventory in `data/p_role_genes_by_strain.csv`.

### Gene-set-handle coverage QC `[KG]` (`data/qc_ontology_coverage.csv`)

Core acquisition genes (pstSCAB, phnCDE, phoB, phoR, phoH = 10) captured per handle:

| strain | handle | n genes | core captured |
|---|---|--:|--:|
| MED4 | cyanorak D.1.5 | 31 | 10/10 |
| MED4 | GO (BP∪MF) | ~10 | 5/10 |
| MIT9313 | cyanorak D.1.5 | 42 | 10/10 |
| MIT9313 | GO (BP∪MF) | ~11 | 6/10 |

GO misses phnCD, phoB, phoH, phoR — confirming GO is unusable as the primary
handle here.

### Publications (resolved via `list_publications`) `[KG]`

P-relevant studies in the KG (treatment_type=phosphorus):

- **Martiny, Coleman & Chisholm 2006**, *PNAS*, DOI `10.1073/pnas.0601301103` —
  "Phosphate acquisition genes in Prochlorococcus ecotypes: Evidence for
  genome-wide adaptation" (MED4 vs MIT9313 microarray). Directly on-topic prior.
- **Fuszard, Wright & Biggs 2012**, *Aquatic Biosystems*, DOI `10.1186/2046-9063-8-7`
  — comparative ecotype proteomics under decreasing phosphate (MIT9312, NATL2A,
  SS120).
- **Lin, Ding & Zeng 2015**, *Environ. Microbiol.*, DOI `10.1111/1462-2920.13104`
  — NATL2A transcriptomics under P limitation (+ phage).
- **Kujawinski et al. 2023**, *mSystems*, DOI `10.1128/msystems.01261-22` —
  metabolite diversity across ecotypes (MIT0801, MIT9301, MIT9313).

## Surprises

- **Resolver bug.** `genes_by_ontology` (shared `_validate_organism_inputs`)
  resolves only organisms with expression-edge-bearing genes; genome-only and
  metabolomics-only strains fail despite full genomic annotation. Halved the
  achievable panel for this dogfood. Logged in `gaps_and_friction.md`.
- **Normalization flips the headline.** Raw P-gene counts favor LL, but per-1000
  the two top values are HL (MIT9301, MIT9312). "LL has more P genes" looks
  largely like a genome-size effect on this panel.
- **Early differential signal is regulatory/scavenging, not transporters.** The
  core Pi/phosphonate transporters are universal; the LL-only OGs are ptrA
  (regulator), phoC (acid phosphatase), ppk2 (polyP kinase). To be confirmed in
  step 5 — fragile on a 4-HL/5-LL panel.

## Decisions

- **2026-06-13 — gene-set handle = Cyanorak `D.1.5` role, OG-level comparison.**
  GO rejected (captures 4–6/10 core genes vs 10/10 for Cyanorak); KEGG scattered.
- **2026-06-13 — panel restricted to the 9 MCP-resolvable strains (4 HL, 5 LL).**
  Forced by the resolver bug + researcher instruction to use MCP tools as-is for
  the dogfood. Downstream impact: steps 3–5 run on this reduced, HL/LL-imbalanced
  panel; the full 17-strain panel is deferred until the resolver is fixed.

## Decide-gate checklist

- **Outputs produced:** `scripts/01_extract_p_gene_entries.py`,
  `scripts/qc_ontology_coverage.py`; `data/p_role_genes_by_strain.csv` (319 rows),
  `data/strain_panel.csv` (9), `data/qc_ontology_coverage.csv` (6),
  `data/01_extract_p_gene_entries.log`. Run: `uv run python <script>` from repo root.
- **Results presented:** strain-panel table, 41-OG inventory (differential subset
  shown; full in CSV), coverage-QC table, 4 resolved publications — all inline above.
- **QC gate:** ontology coverage Cyanorak 10/10 vs GO 4–6/10 core genes → Cyanorak
  handle justified. OG mapping 319/319 genes mapped (0 unmapped). Panel
  resolvability probed per strain (9/10 resolve; MIT0801 metabolomics-only fails).
  RSP50/MIT1314 excluded as annotation-absent (verified 0 Cyanorak roles via Cypher).
- **Decisions made this step:** gene-set handle; panel restriction (see Decisions).
- **Advance rationale:** entries are frozen (gene set, OGs, panel, genome sizes,
  publications); step 3 can now select controls and lock the framing
  (focused-acquisition subset + normalization choice).
