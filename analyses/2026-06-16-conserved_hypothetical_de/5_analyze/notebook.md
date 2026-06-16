# Step 5 — Analyze (score the candidates against a conserved-OG backdrop)

## Context

Step 4 built and validated the metric. Step 5 runs it. Per a researcher decision this
step, we score not just our 245 hypothetical families but the **whole conserved set**
(1,710 cyanorak families ≥9/17 strains) so the hypotheticals can be judged against
characterized conserved families. Output = a ranked shortlist of interesting
hypotheticals plus the comparison backdrop.

Scope note (this analysis = selection only): characterization of the shortlisted
genes is a separate follow-on analysis (step-1 reopen, 2026-06-16).

## What I did

```
uv run python .../5_analyze/scripts/01_score_conserved_ogs.py
uv run python .../5_analyze/scripts/02_shortlist_and_figures.py
```

- `01` — members + gene_category for all 1,710 conserved OGs (one
  `genes_by_homolog_group` call), then per-gene **significant** DE over the pooled
  experiments batched per strain (`differential_expression_by_gene`,
  `significant_only=True`), aggregated with the step-4 module. Output
  `data/conserved_og_scores.csv`. (Tested-denominator / % datapoints not computed in
  this significant-only pass — nulled; it is heavily table_scope-caveated and not
  needed for breadth/prominence/direction.)
- `02` — shortlist from the hypothetical subset + the three result figures.

A family is a **headline hit** if BROAD or PROMINENT:
breadth ≥ 6, **or** best_rank ≤ 3 / max|log2FC| ≥ 8 / ≥30 significant datapoints.

## Results

23,422 significant datapoints over 1,705 of 1,710 conserved families.

### Conserved hypotheticals respond about as broadly as characterized genes

| group | n | mean breadth | median | broad (≥6) |
|---|---|---|---|---|
| hypothetical | 245 | 3.67 | 4 | 30 |
| characterized | 1,465 | 4.48 | 4 | 326 |

Same median (4); characterized have a slightly heavier broad tail. The dark genes are
**not** transcriptionally quiet — 30 conserved hypotheticals respond in ≥6 of 13
conditions, and the top ones match the broadest characterized families. (Figure
`fig5`.)

### Shortlist — 85 interesting hypothetical families

30 broad, 69 prominent, 14 both (full list `data/shortlist.csv`). Top by breadth then
prominence:

| og_id | tier | strains | category | breadth | best_rank | max\|log2FC\| | dir | product |
|---|---|---|---|---|---|---|---|---|
| CK_00000141 | broad | 13 | Unknown | 9 | 1 | 6.60 | mixed | uncharacterized conserved secreted |
| CK_00019843 | core | 15 | Unknown | 9 | 1 | 8.66 | mixed | conserved hypothetical protein |
| CK_00055271 | core | 17 | Unknown | 8 | 4 | 3.49 | mixed | conserved hypothetical protein |
| CK_00045004 | core | 14 | Unknown | 7 | 1 | 9.30 | mixed | conserved hypothetical protein family |
| CK_00001734 | core | 17 | Unknown | 7 | 2 | 9.60 | mixed | conserved hypothetical protein |
| CK_00046153 | core | 17 | Unknown | 7 | 17 | 7.80 | mixed | conserved hypothetical protein |
| CK_00004021 | core | 14 | Unknown | 7 | 3 | 7.33 | mixed | uncharacterized conserved membrane |
| CK_00045754 | broad | 12 | Unknown | 6 | 3 | 10.81 | mixed | conserved hypothetical protein |

Several reach **rank 1** (the single most-regulated gene in some experiment) and
|log2FC| up to 10.8 — as prominent as any characterized gene. The driving example
`CK_00000958` scores breadth 4 (in the broad body of the distribution, not the top).

### Direction is context-dependent (and that's the point)

Every top family is overall "mixed", because direction flips by condition. The
**clustered** per-treatment heatmap (`fig7`, the 85-family shortlist with rows and
treatments hierarchically clustered) shows the structure: a block of families is
strongly **down** in salt/coculture/nitrogen; treatments separate into a
response-dense group (salt, coculture, nitrogen, plastic, carbon) and a sparse group
(darkness, light, diel, phosphorus, iron). A family up under one stress and down under
another is itself an interesting regulatory signal, not noise.

### Figures

All figures are written as both PNG (300 DPI) and SVG (publication).

- `fig5_breadth_hypo_vs_characterized` — breadth distributions overlap; dark genes
  are comparably responsive.
- `fig6_backdrop_breadth_vs_prominence` — all 1,710 conserved families; colour =
  gene_category, marker = direction (▲up/▼down/●mixed), hypotheticals outlined,
  controls (hli/groEL/pstS/htpG/dnaK1) as gold stars anchoring the axes.
- `fig7_direction_clustermap_shortlist` — clustered direction × treatment heatmap for
  the 85-family shortlist (rows + treatments hierarchically clustered).

## Surprises

- Characterized conserved families are only marginally broader than hypotheticals
  (mean 4.48 vs 3.67) — the gap is smaller than expected; conserved dark genes behave
  much like conserved known genes in responsiveness.
- `CK_00046153` and `CK_00001473` are broad (7) but their best rank is modest
  (17, 14) — broad without being top-ranked; conversely the prominent-only set (55
  families) is broad-tail-light. Breadth and prominence pick different families, as
  the controls predicted.

## Decisions

- **2026-06-16 — Score the full conserved backdrop (1,710 ≥9/17), not just the 245
  hypotheticals**, so responsiveness is judged relative to characterized conserved
  families (researcher request). Hypotheticals flagged `is_hypothetical`.
- **2026-06-16 — Significant-only scoring pass** for breadth/prominence/direction;
  tested-denominator/% deferred (not needed, heavily caveated).
- **2026-06-16 — Headline shortlist = broad (≥6) OR prominent (rank≤3 / |log2FC|≥8 /
  ≥30 sig datapoints)** → 85 families. Direction encoded as marker/heatmap (mixed kept
  as meaningful).

## Decide-gate checklist

- **Outputs produced** — `scripts/01_score_conserved_ogs.py`,
  `scripts/02_shortlist_and_figures.py`; `data/conserved_og_scores.csv` (1,710),
  `data/shortlist.csv` (85), `data/de_long_significant.csv` (gitignored, 4.7MB);
  `figures/fig5,6,7` (PNG + SVG; fig7 a seaborn clustermap); logs. Command lines above.
- **Results presented** — hypothetical-vs-characterized breadth table, top-shortlist
  table, three figures — inline above.
- **QC gate** —
  - controls land as expected on `fig6` (hli broad/high; pstS off-diagonal; dnaK1 at
    origin) ✓
  - driving OG `CK_00000958` reproduces its step-4 breadth (4) ✓
  - 1,705/1,710 families have ≥1 significant response (coverage sane) ✓
- **Decisions made this step** — three, dated above.
- **Advance rationale** — the scored ranking, shortlist, and backdrop comparison are
  produced and sanity-checked; ready for step 6 to evaluate against the framing,
  harvest caveats, and finalize the selection paper.
