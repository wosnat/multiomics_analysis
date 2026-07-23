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

### 2026-07-22 — Experiment `control` field flattens a within-coculture time contrast (KG fidelity)

**What happened.** While confirming the exclusion of the Biller 2016 MIT1002
cocultures (`10.1038/ismej.2016.82`), the two *Alteromonas*-side Experiment nodes
report `treatment` = "24 / 48 hours after co-culturing with Prochlorococcus NATL2A"
and `control` = **"Co-culture with Prochlorococcus NATL2A"** — with no reference
timepoint. The source supplementary table (moesm99) and the ingestion config are
unambiguous: the contrasts are **"log2FoldChange (24 vs 12 hrs after addition)"** and
**"(48 vs 12 hrs after addition)"** — i.e. the reference is the **12 h coculture
timepoint**, not a generic coculture state and not t0. The paper confirms there is
**no axenic *Alteromonas* arm** in the study (axenic bottles are axenic
*Prochlorococcus*; *Alteromonas* was only ever sampled in coculture). Source:
`multiomics_biocypher_kg/.../biller 2016/paperconfig.yaml` (`supp_table_3`
`statistical_analyses`: `24v12h` / `48v12h`) + the article methods (page 2832–2833).

**Workaround (this analysis).** None needed — both experiments are already **excluded**
(no coculture-vs-axenic handle on the *Alteromonas* side), so no computed output reads
them. The lossy field does not affect any result here.

**Downstream impact.** KG fidelity (upstream, not this repo). The `control` string
drops the "12 hrs after addition" reference, so a reader querying the KG alone would
misread the denominator (generic coculture, or t0) rather than the 12 h timepoint. The
"both arms are coculture" fact — the one this analysis relies on for the exclusion — is
still recoverable, so this is *lossy, not wrong*. **Recommended upstream fix:** in the
`multiomics_biocypher_kg` `paperconfig.yaml`, set `control_condition` for both MIT1002
experiments to "12 hours after co-culturing with Prochlorococcus NATL2A" and rebuild;
ideally paired with a sweep for other time-contrast experiments whose reference
timepoint is likewise collapsed into a generic `control` string. Flag to the KG
maintainer; do **not** edit the KG from this analysis clone. My earlier reading that
the reference was ≈ t0 was an `[interpretation]` corrected by the source table — a
reminder to read the ingestion config / supplement, not the flattened node field, when
a contrast's exact reference matters.
