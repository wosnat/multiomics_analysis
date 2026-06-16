# Step 6 — Evaluate & finalize

## Context

Closes the selection analysis. Evaluates the shortlist against the step-3 framing,
tests the coverage confound and the conservation effect (using our two tiers),
harvests caveats, assembles the hand-off to the characterization follow-on, and
finalizes `paper.md`.

## Did the framing hold?

- **Premise (conserved hypotheticals are broadly responsive): held.** 243/245
  respond; breadth median 4, the same as characterized conserved families — dark
  genes are not transcriptionally quiet (step 5, `fig5`).
- **Controls: held.** The metric ranked characterized controls as predicted (hli
  broad+prominent, htpG/dnaK1 narrow, pstS prominent-not-broad), validated twice —
  by `gene_response_profile` (step 3) and the scoring path (step 4, 5/5 agreement).

## Coverage confound (the key check)

`scripts/01_coverage_and_conservation.py`. Pearson r among the 245 hypotheticals:

| relationship | r | reading |
|---|---|---|
| breadth ~ treatments tested | **0.90** | breadth largely tracks how broadly a family was *measured* |
| proc_strains ~ treatments tested | 0.54 | conservation is itself partly a coverage proxy |
| breadth ~ proc_strains | 0.55 | more conserved → broader (moderate) |
| response_rate ~ proc_strains | **0.22** | once normalized by coverage, conservation adds little to *breadth* |

**Breadth is substantially a coverage artifact** (`fig8`): a family looks broadly
responsive partly because it was assayed in more conditions (more strains → more
experiments). This is the single most important caveat on the breadth ranking.
**Prominence (best rank, max|log2FC|) is not coverage-driven** and is the more robust
axis — which is why the headline is the families that are *both* broad and prominent.

## Conservation by tier (core ≥14 vs broad 9–13)

| tier | n | mean breadth | treatments tested | response_rate | mean max\|log2FC\| | shortlist |
|---|---|---|---|---|---|---|
| core (≥14) | 97 | 4.61 | 5.40 | 0.850 | 6.58 | 45 |
| broad (9–13) | 148 | 3.05 | 3.89 | 0.785 | 4.11 | 40 |

Core families respond more broadly **and** more prominently, but the breadth gap is
mostly coverage (they're tested in more conditions); the coverage-normalized
response_rate gap is modest (0.85 vs 0.78; `fig9`). The **prominence** gap (6.58 vs
4.11) is the robust part — core conserved hypotheticals reach larger fold changes.
Gene-family size (paralog count) also tracks responsiveness (breadth ~ proc_members
r=0.61), but proc_members co-varies with strain count, so the same coverage caveat
applies.

## Headline deliverable — the core 14

`scripts/02_handoff_shortlist.py` → `data/handoff_shortlist.csv` (85 families, the 14
"both broad and prominent" flagged `core14`). The 14 are the robust selection: broad
*and* prominent (best rank 1–3 for most; |log2FC| up to 13.3), nearly all core-tier,
several annotated only as "uncharacterized secreted/membrane protein". This is the
input set for the characterization follow-on.

| og_id | tier | strains | breadth | best_rank | max\|log2FC\| | product |
|---|---|---|---|---|---|---|
| CK_00019843 | core | 15 | 9 | 1 | 8.66 | conserved hypothetical protein |
| CK_00000141 | broad | 13 | 9 | 1 | 6.60 | uncharacterized conserved secreted |
| CK_00001345 | core | 17 | 6 | 8 | 13.27 | uncharacterized conserved secreted |
| CK_00049482 | core | 17 | 6 | 2 | 13.05 | conserved hypothetical protein |
| CK_00003473 | core | 17 | 6 | 2 | 12.26 | uncharacterized secreted protein |
| … (14 total in `handoff_shortlist.csv`, `core14=True`) | | | | | | |

## Caveats harvested

1. **Breadth is coverage-confounded (r=0.90).** Rank families by prominence /
   response_rate, not raw breadth, when robustness matters. Carried into the paper.
2. **Strain-coverage bias.** DE evidence is dominated by MED4 and NATL2A; most
   "breadth" comes from a few well-studied strains. Other strains contribute
   conservation, not response evidence.
3. **Table-scope limitation (deferred from step 3).** Significant-only experiments
   lack a tested-but-flat denominator; the significant-only scoring pass means
   `pct_datapoints_de` was not computed and absent rows can't be read as "tested flat".
4. **Rank depends on each experiment's table size** — a top rank in a small
   significant-only table is not equivalent to one in a full table.
5. **Family-level pooling conflates paralogs and strains** — an OG "responds" if any
   member does; direction is "mixed" at the family level by construction.
6. **Conservation denominator is 17 (cyanorak), not 19** genome strains.

## Decisions

- **2026-06-16 — Headline = the 14 broad-AND-prominent families**; 85 kept as the long
  list. Prominence is the confound-robust axis, so the intersection is the defensible
  core. (Researcher decision.)
- **2026-06-16 — Conservation analyzed by our two tiers** (core/broad), within the
  scored conserved set (no extension to <9 strains). (Researcher decision.)

## Decide-gate checklist

- **Outputs produced** — `scripts/01_coverage_and_conservation.py`,
  `02_handoff_shortlist.py`, `03_references.py`; `data/coverage_confound.csv`,
  `conservation_tier_summary.csv`, `handoff_shortlist.csv`, `references.csv`;
  `figures/fig8_breadth_vs_coverage`, `fig9_conservation_by_tier` (png+svg); logs.
- **Results presented** — confound correlation table, tier table, core-14 table —
  inline above.
- **QC gate** —
  - premise + controls held (cross-checked steps 3–5) ✓
  - confound quantified (breadth~coverage r=0.90) and reflected in the headline choice ✓
  - 30 references resolved via `list_publications`, not_found=[] ✓
- **Decisions made this step** — headline = core 14; conservation by tier (dated above).
- **Advance rationale** — the analysis is evaluated, caveated, and the hand-off
  shortlist is frozen; `paper.md` is complete. The selection analysis is done; the
  characterization follow-on (and the cross-analysis dashboard) start from
  `handoff_shortlist.csv`.
