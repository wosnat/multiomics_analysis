# Step 2 — KG entries

## Context

Step 1 locked the question: across *Prochlorococcus*, which conserved hypothetical
ortholog families (no known function, widely conserved) are differentially
expressed across many conditions. Unit of analysis = ortholog group; scope = all
strains; conservation = shared across many *Prochlorococcus* strains.

This step enumerates the **KG entries** the question needs and verifies the two
operational definitions are computable at the ortholog-group level:
- **uncharacterized** = `Gene.annotation_quality <= 1`
- **conserved** = present in many *Prochlorococcus* strains (cyanorak OG backbone)

No thresholds are locked here — that is step 3 (selection + framing). This step
characterizes the candidate universe so step 3 can choose defensible cutoffs.

## What I did

Two extraction scripts (run from the **repo root** so the root `.env` KG
credentials load; outputs are `__file__`-relative):

```
uv run python analyses/2026-06-16-conserved_hypothetical_de/2_kg_selection/scripts/01_de_experiments.py
uv run python analyses/2026-06-16-conserved_hypothetical_de/2_kg_selection/scripts/02_og_conservation_landscape.py
```

- `01_de_experiments.py` → `data/de_experiments.csv` (91 experiments),
  `data/publications.csv` (33 publications).
- `02_og_conservation_landscape.py` → `data/og_conservation_landscape.csv`
  (5,732 cyanorak OGs with ≥1 Prochlorococcus member; per-OG strain coverage,
  member counts, hypothetical fraction, consensus product).

Operational definitions verified by direct query before scripting:
- **AQ contract** (from `genes_by_function` doc + `conventions.md`): AQ is a 0–3
  encoding of `annotation_state` — 0 `no_evidence`, 1 `catch_all_only`,
  2 `informative_single`, 3 `informative_multi`; `min_quality=2` is the documented
  "skip hypothetical proteins" filter. Confirmed against Prochlorococcus genes:
  AQ≤1 rows carry products like "hypothetical protein" / "conserved hypothetical
  protein" / "uncharacterized conserved membrane protein".

## Results

### The conditions universe — 91 Prochlorococcus DE experiments

| Strain | experiments |   | Treatment | n |   | Omics | n |
|---|---|---|---|---|---|---|---|
| MED4 | 41 |  | carbon | 18 |  | RNASEQ | 32 |
| MIT9313 | 17 |  | nitrogen | 12 |  | MICROARRAY | 25 |
| NATL2A | 9 |  | light | 10 |  | PROTEOMICS | 16 |
| MIT9312 | 8 |  | compartment | 9 |  | METABOLOMICS | 12 |
| SS120 | 6 |  | phosphorus | 9 |  | VESICLE_PROTEOMICS | 4 |
| MIT9301 | 4 |  | growth_phase | 6 |  | VESICLE_DNASEQ | 1 |
| MIT9303 | 2 |  | coculture | 5 |  | PAIRED_RNASEQ_PROTEOME | 1 |
| MIT0801 | 2 |  | iron | 5 |  | | |
| AS9601 | 1 |  | viral | 4 |  | | |
| NATL1A | 1 |  | plastic, salt, darkness, diel, temperature | ≤4 each | | | |

Table scope (fairness for "tested vs flat"): `all_detected_genes` **27**,
`significant_only` 20, `filtered_subset` 17, unspecified 16,
`significant_any_timepoint` 10, `top_n` 1.

Gene-anchored vs not: 12 of 91 are **METABOLOMICS** (anchored on metabolites, no
gene DE) and 9 are `compartment` contrasts (vesicle/exoproteome partitioning, not
stress response). The gene-level **stress-response** DE universe step 3 will pool
is therefore the RNASEQ / MICROARRAY / PROTEOMICS subset minus the compartment
contrasts — to be finalized in step 3.

Publications: 33 distinct DOIs behind these experiments (full list in
`data/publications.csv`). Largest contributors: `10.1128/spectrum.03275-22` (8 exp),
`10.1111/1462-2920.15834`, `10.1128/JB.01097-06`, `10.1038/msb4100087`,
`10.1128/msystems.01261-22` (6 each).

### The conserved-hypothetical OG landscape (cyanorak backbone)

- 5,732 cyanorak OGs have ≥1 Prochlorococcus member.
- **2,787** are mostly hypothetical (≥80% of Prochlorococcus members AQ≤1).
- Effective conservation denominator = **17 strains** (cyanorak spans 17 of the
  19 Prochlorococcus genome strains).

Strain-coverage distribution among the 2,787 mostly-hypothetical OGs:

| strains present | n OGs | cumulative (≥ k strains) |
|---|---|---|
| 1 | 1402 | 2787 |
| 2 | 471 | 1385 |
| 3 | 258 | 914 |
| 4 | 229 | 656 |
| 5 | 67 | 427 |
| ... | ... | ... |
| 9 | 88 | 245 |
| 14 | 28 | 97 |
| 17 (all) | **50** | 50 |

Shape: ~half (1,402) are single-strain novelties — *not* conserved — and there is a
sharp **core spike of 50 OGs present in all 17 strains**. Examples of the core set:
`cyanorak:CK_00046153`, `CK_00055728`, `CK_00001506`, `CK_00000498` (HesB-like
domain-containing protein), `CK_00001680` ("conserved hypothetical protein specific
to marine..."). These are strong step-3 candidates: maximally conserved yet
functionally dark.

## Surprises

- **Cyanorak caps at 17, not 19 strains.** Two genome strains carry no cyanorak
  ortholog annotation, so conservation must be normalized against 17. Honest
  denominator; flagged so step 3 doesn't over-count.
- **Conservation breadth (17 strains) ≫ responsiveness breadth (≤10 strains with
  DE, mostly MED4).** The two evidence axes have different denominators by design —
  conservation from genomes, responsiveness from the subset with expression data.
- **Bimodal conservation:** a large single-strain mode (novel ORFans) and a clear
  core mode. The question targets the core mode.

## Decisions

None locked this step. Thresholds (hypothetical-fraction rule, conservation cutoff,
gene-DE experiment subset, broad-responsiveness metric) are deferred to step 3 per
just-in-time formalization. One observation recorded for step 3: the gene-level DE
universe excludes the 12 metabolomics experiments and the 9 compartment contrasts.

## Decide-gate checklist

- **Outputs produced** —
  `scripts/01_de_experiments.py`, `scripts/02_og_conservation_landscape.py`;
  `data/de_experiments.csv`, `data/publications.csv`,
  `data/og_conservation_landscape.csv`; logs
  `data/01_de_experiments.log`, `data/02_og_conservation_landscape.log`.
  Command lines above.
- **Results presented** — strain/treatment/omics/table-scope breakdown tables and
  the OG strain-coverage distribution shown inline above; full tables in `data/`.
- **QC gate** —
  - AQ definition cross-checked against product text on AQ≤1 genes → match (all
    "hypothetical"/"conserved hypothetical"/"uncharacterized") ✓
  - Conservation denominator queried directly → cyanorak spans 17 Prochlorococcus
    strains (not 19) ✓
  - Experiment count reconciles with the step-1 grounding (91) ✓
- **Advance rationale** — the conditions universe, publications, organisms, data
  types, and the conserved-hypothetical OG landscape are frozen to CSV; both
  operational definitions are computable; ready for step 3 to select the final OG
  set and frame the hypothesis + controls.
