# Upstream tickets — from the Alteromonas coculture analysis

Three items to file outside this repo. Copy each block into its tracker; the full
incident record stays in
[`analyses/2026-07-06-alteromonas_coculture_carbon_sources/gaps_and_friction.md`](../analyses/2026-07-06-alteromonas_coculture_carbon_sources/gaps_and_friction.md)
and is linked per ticket rather than restated.

Observed 2026-07-06 → 07-23. KG release recorded at the methods milestone:
`0.1.0-alpha.6` (verdict `ok`, 16/16).

Filing order: **2 first** — it caused a plan-time Blocker and will mislead the
next caller the same way. 1 and 3 are lower-severity but cheap.

---

## 1 → `multiomics_explorer` · `genes_by_function` returns 0 when `search_text` and `category` are combined

**Type:** bug (or missing documentation) · **Severity:** low-medium — a silent
zero, not an error

**Repro**

```python
genes_by_function(search_text="ABC transporter permease…",
                  organism="HOT1A3",
                  category="Transport")
# → total_search_hits: 9374,  total_matching: 0
```

The same `search_text` without `category` matches normally. `category` alone
cannot be queried — `search_text` is required — so there is no way to isolate
which side collapses from the caller's seat.

**Expected:** the intersection of a matching text search and a valid category
returns the genes in both, or an explicit error/warning if the combination is
unsupported.

**Actual:** `total_search_hits` is large and `total_matching` is 0. A caller who
doesn't check both fields reads this as "no transporters in this organism" — a
wrong answer that looks like a real one.

**Ask:** either fix the over-restrictive AND, or document the interaction and
have the tool signal the empty intersection rather than returning a bare zero.

**Workaround used:** went ontology-first (`genes_by_ontology`) to enumerate
transporters.

---

## 2 → `multiomics_explorer` · DE rank fields: undocumented rename + significant-only population

**Type:** documentation (and a naming trap) · **Severity:** high — caused a
plan-time Blocker; a scoring method built on the documented reading would be
silently wrong

Two things about the rank fields on DE edges are invisible from the MCP surface:

1. **`rank_up` / `rank_down` are populated on significant genes only.** In the
   primary experiment: of 3947 DE edges, `rank_up` is non-null on **111** (the
   significant-up genes) and `rank_down` on **163**. They are not genome-wide
   directional ranks.
2. **The genome-wide field is `rank_by_effect`** (magnitude-only,
   direction-blind), and the **MCP tool surfaces it under the renamed key
   `rank`** — so the underlying property name never appears to the caller.

**Why it matters:** a scoring plan premised on `rank_up` being a genome-wide
directional rank is not merely imprecise — a genome-wide null over it isn't
constructible, and every non-significant gene silently drops out of the ranking.
Caught here only because a plan-time critic checked the field against the KG with
raw `run_cypher`; the curated MCP view abstracts away exactly the null-population
that reveals it.

**Ask:** document both in `docs://tools/differential_expression_by_gene` — the
`rank_by_effect` → `rank` rename, and the significant-only population of
`rank_up`/`rank_down`. Consider surfacing a non-null count, or naming the fields
so the restriction is visible (`rank_up_significant`).

**Workaround used:** scored on a rank of the KG-provided `log2fc` over all
detected genes; used `rank_up`/`rank_down` only as significant-gene validation
handles.

---

## 3 → `multiomics_biocypher_kg` · Biller 2016 `control` string drops the reference timepoint

**Type:** ingestion fidelity · **Severity:** low-medium — lossy, not wrong; no
computed output in this analysis reads it

**Publication:** Biller 2016, `10.1038/ismej.2016.82` (MIT1002 cocultures)

The two *Alteromonas*-side Experiment nodes report:

- `treatment` = "24 / 48 hours after co-culturing with *Prochlorococcus* NATL2A"
- `control` = **"Co-culture with *Prochlorococcus* NATL2A"** — no reference
  timepoint

The source is unambiguous that the contrasts are **24 vs 12 h** and **48 vs 12 h**
after addition: `paperconfig.yaml` `supp_table_3` → `statistical_analyses`
(`24v12h` / `48v12h`), and the article methods (pp. 2832–2833). There is **no
axenic *Alteromonas* arm** in the study — axenic bottles are axenic
*Prochlorococcus*; *Alteromonas* was only ever sampled in coculture.

**Impact:** a reader querying the KG alone misreads the denominator as a generic
coculture state, or as t0, rather than the 12 h coculture timepoint. The fact this
analysis actually relied on — that both arms are coculture — is still recoverable,
so the field is lossy rather than incorrect. Both experiments were **excluded**
here (no coculture-vs-axenic handle on the *Alteromonas* side), so nothing
computed depends on it.

**Ask:** set `control_condition` for both MIT1002 experiments to "12 hours after
co-culturing with *Prochlorococcus* NATL2A" and rebuild. Ideally paired with a
**sweep for other time-contrast experiments** whose reference timepoint is
likewise collapsed into a generic `control` string — the failure mode is
systematic, not specific to this paper.

*(Do not edit the KG from an analysis clone — this is a maintainer action.)*
