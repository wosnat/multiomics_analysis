# Gaps and friction log

Transitional log of methodology / KG / tooling friction for
`2026-07-06-alteromonas_coculture_carbon_sources`. Append-only. Distinct from
decisions (which live in `proposal.md` / milestone `notebook.md`).

---

### 2026-07-06 — TCDB annotated at superfamily level for ABC transporters (KG annotation depth)

**What happened.** For substrate tagging of transporters we intended to lean on
TCDB families. But `genes_by_ontology(ontology="tcdb", term_ids=["tcdb:3.A.1"])`
for HOT1A3 returned 80 genes all tagged only to the ABC **superfamily** node
`3.A.1` — which lumps Fe³⁺, phosphate, nitrate, amino-acid, heme-export,
capsule-export, and multidrug-efflux systems with no substrate resolution. TCDB
*is* substrate-specific for the secondary carriers (`2.A.x`), but for ABC it
carries no substrate signal.

**Workaround.** Take substrate from `product` / COG / `function_description`
(which are substrate-bearing) as the primary handle, TCDB only where it is a
specific `2.A.x` family, plus genomic neighbours; carry a confident-vs-inferred
flag on every substrate tag.

**Downstream impact.** Methodology — the module-building step cannot treat TCDB
family as the substrate key; it must fuse multiple annotation sources. (Not a KG
bug; an annotation-granularity limit to be aware of. Candidate KG improvement:
propagate TCDB sub-family assignments for ABC systems where possible.)

### 2026-07-06 — `genes_by_function` returns zero when `search_text` + `category` are combined (MCP tool behaviour)

**What happened.** `genes_by_function(search_text="ABC transporter permease…",
organism="HOT1A3", category="Transport")` returned `total_search_hits` 9374 but
`total_matching` 0. The same search without `category` matches normally, and
`category` alone can't be queried (`search_text` is required). The text +
category AND appears to collapse to empty.

**Workaround.** Went ontology-first (`genes_by_ontology`) to enumerate
transporters instead of `genes_by_function` with a category filter.

**Downstream impact.** Tooling — flag for the explorer maintainers: either the
`search_text`+`category` intersection is over-restrictive/buggy, or the
interaction needs documenting. Low impact on this analysis (alternative path
exists).

### 2026-07-07 — DE-edge rank fields: MCP rename + significant-only population (KG / MCP semantics trap)

**What happened.** The proposal's scoring premise assumed the MCP `rank_up` field
was a genome-wide directional rank. `run_cypher` on the primary experiment showed
otherwise: of 3947 DE edges, `rank_up` is non-null on only 111 (= the significant-
up genes), `rank_down` on 163 (significant-down); the genome-wide field is
`rank_by_effect` (magnitude-only, direction-blind), which the **MCP tool surfaces
under the renamed key `rank`**. So (a) `rank_up`/`rank_down` are significant-genes-
only in *every* experiment, and (b) the MCP rename hides the underlying property
name.

**Workaround.** Score on a rank of the KG-provided `log2fc` over all detected genes
(genome-wide for `all_detected_genes`; within-significant-set for `significant_only`);
use `rank_up`/`rank_down` only as significant-gene validation handles.

**Downstream impact.** Methodology + tooling. Methodology: caught a scoring Blocker
at plan time (the second proposal critic). Tooling: worth documenting the MCP field
rename (`rank_by_effect` → `rank`) and the significant-only population of
`rank_up`/`rank_down` in `docs://tools/differential_expression_by_gene`, so callers
don't assume genome-wide directional ranks. The raw-Cypher escape hatch was needed
to see the null-population that the curated view abstracts.

### 2026-07-06 — Large `list_experiments` result exceeds the token cap (tooling)

**What happened.** `list_experiments(organism="Alteromonas", limit=49)` returned
~73k characters and was rejected/saved to a file rather than returned inline.

**Workaround.** Extracted the needed columns with `jq` from the saved
tool-result file to build a compact table.

**Downstream impact.** Process — for broad landscape scans, prefer
`summary=true` first, then targeted non-verbose pulls, or plan to `jq` the saved
file. Minor.

### 2026-07-12 — `significant_only` datasets are unscorable by a transporter-module method (data/method fit)

**What happened.** The EZ55 pCO₂ experiments are `significant_only` (only DE-significant
genes have rows, ~188–419 genes). Scoring the 35 EZ55 modules, **28/35 (400 ppm) and
32/35 (800 ppm) had no gene in the significant set** → unscorable; every scored module
rested on a single detected system. The one "hit" (Fe-dicitrate, 800 ppm) is iron
acquisition. The result is *underpowered*, not a clean negative.

**Workaround.** None available — the method needs the genes present. Reported EZ55 as
underpowered/uninformative, not null; the analysis rests on the genome-wide HOT1A3
presence contrast.

**Downstream impact.** Method-fit lesson: a presence-contrast module method (rank all
detected genes → module max) requires `all_detected_genes`; `significant_only` datasets
cannot corroborate it. Worth stating in the proposal's data-scoping when a
`significant_only` experiment is proposed as support. (Candidate methodology note — see
`docs/methodology-retro-2026-07-carbon-sources.md`.)

### 2026-07-12 — validation controls don't transfer across contrast types (methodology)

**What happened.** The ribosomal-neutrality negative control (ribosomal genes ~0.50 in
the presence contrast, confirming the up-percentile axis isn't a generic growth signal)
**failed in the starvation-vs-exponential temporal contrast** — ribosomal median
up-percentile 0.66–0.79 in both arms. So the temporal ranking is shaped by the
growth-state transition, and a control calibrated on one contrast type did not transfer.

**Workaround.** Flagged the temporal read as growth-state-confounded; scoped "method
validated" to the presence contrast only.

**Downstream impact.** Methodology: validation sets may be **per-contrast-type**, not
global. One occurrence — noted for the next analysis to confirm before any skill change
(retro doc).
