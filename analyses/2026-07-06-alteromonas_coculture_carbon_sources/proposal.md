# Proposal — Carbon sources used by *Alteromonas* in coculture with *Prochlorococcus*

**Analysis slug:** `2026-07-06-alteromonas_coculture_carbon_sources`
**Plan locked:** 2026-07-07 (framing refined from 2026-07-06)
**KG release:** 0.1.0-alpha.6 (explorer-MCP 0.1.0a4; `kg_release_info` verdict `ok`, 16/16 asserts)

---

## Question (locked)

**Which organic carbon compounds does *Alteromonas* draw on when growing in
coculture with *Prochlorococcus*?**

Subject of interest: the Weissberg 2025 study (HOT1A3 + MED4,
`10.1101/2025.11.24.690089`). The question is **widened** to a first-class
multi-strain question — *what carbon sources does Alteromonas use in coculture
with Prochlorococcus, across all available strains* — with every other
Alteromonas–Prochlorococcus coculture treated as independent corroboration, not
pooled data.

**Inference logic.** The growth media (PRO99-lowN / Pro99) carry **no added
organic carbon** `[KG]` (medium fields on every experiment below), and the KG
holds no direct measurement of what *Prochlorococcus* exudes in coculture
(metabolomics count = 0 on all coculture experiments). So the carbon sources
cannot be read off the producer; they are inferred from the **consumer** —
which of *Alteromonas*'s own substrate-specific uptake-and-catabolism systems
turn **on** in coculture relative to axenic. `[interpretation]`

---

## KG entries (enumerated from live queries)

### In scope — presence effect (coculture vs axenic, *Alteromonas* side)

Each reported **individually**; never pooled.

| Experiment id | Strain | Partner | Omics | Scope | up/down | Note |
|---|---|---|---|---|---|---|
| `10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq` | HOT1A3 | Proch MED4 | RNA-seq | all_detected_genes (3947) | 111 / 163 | **primary**; day 11 exponential; DESeq2; has down-genes → motility check works |
| `10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_400_ez55_rnaseq` | EZ55 | Proch MIT9312 | RNA-seq | significant_only (419) | 308 / 111 | 400 ppm pCO₂; edgeR |
| `10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_800_ez55_rnaseq` | EZ55 | Proch MIT9312 | RNA-seq | significant_only (188) | 104 / 84 | 800 ppm pCO₂; edgeR |

→ **2 Alteromonas strains (HOT1A3, EZ55), 2 Prochlorococcus partners (MED4, MIT9312).**

### In scope — temporal read (Weissberg 2025 only, *Alteromonas* side)

Starvation-vs-exponential trajectories, run separately in coculture and axenic;
each reported **individually**, **same method** as the presence contrasts.

**Important — this is a difference-of-starvation-responses, not a presence
contrast.** Each arm's control is that arm's *own* PRO99-lowN exponential
baseline `[KG]`, so the coculture trajectory is "how coculture cells change as
they starve" and the axenic trajectory is "how axenic cells change as they
starve." Comparing the two isolates the coculture-specific component of the
**starvation response** — of which carbon provisioning is only one possible
cause (nitrogen exchange, altered death/lysis kinetics, or slower physiological
decline could equally produce a coculture-only ramp). It is therefore a
**weaker** handle than the day-11 presence contrast and is weighted below it: a
temporal ramp **corroborates** a module already supported by a presence
contrast, but a temporal ramp **alone does not name a carbon source**.

| Experiment id | Omics | Condition | Timepoints |
|---|---|---|---|
| `…690089_growth_state_pro99lown_nutrient_starvation_hot1a3_rnaseq_coculture` | RNA-seq | coculture | d18, 31, 60, 89 |
| `…690089_growth_state_pro99lown_nutrient_starvation_hot1a3_rnaseq_axenic` | RNA-seq | axenic | d18, 31, 60+89 |
| `…690089_growth_state_pro99lown_nutrient_starvation_hot1a3_proteomics_coculture` | Proteomics | coculture | d18, 31, 60, 89 |
| `…690089_growth_state_pro99lown_nutrient_starvation_hot1a3_proteomics_axenic` | Proteomics | axenic | d18, 31 |

### Held aside as context (not counted toward support)

- `10.1038/ismej.2016.70` — HOT1A3 + Proch **MIT9313**, RNA-seq, 2 experiments
  (low/high Alteromonas inoculum). Control is "Pro99 medium growth conditions"
  (≈ axenic, looser wording than the primary study's "Axenic"). **Reports
  up-regulated genes only** (0 down; Rockhopper) → can corroborate an UP call
  narratively but cannot run the motility-down check, and is **same Alteromonas
  strain (HOT1A3), different partner (MIT9313)** — not independent-strain
  evidence. Decision: **context only**, does not move the support count.

### Excluded, with reason

- **MIT1002 cocultures** (`10.1038/ismej.2016.82`): the Alteromonas-side
  contrasts are "24 h / 48 h after co-culturing **vs coculture**" — a
  within-coculture *time* contrast, **not** presence/absence. No clean
  coculture-vs-axenic handle on the Alteromonas side. Excluded from the
  presence set.
- **Glucose-addition proteomics** (`10.1128/spectrum.03275-22`, Moreno-Cabezuelo):
  would have been a positive control / method-calibration for the sugar branch,
  but **too few DE proteins** (4–78 detected per contrast) to be worth the
  cross-strain mapping cost. **Excluded.**
- **EZ55 + *Synechococcus*** contrasts (CC9311, WH8102, in `…00197-2`):
  off-target partner. Available as an optional *specificity* contrast (a carbon
  source that also rises with Synechococcus is not Prochlorococcus-specific),
  not part of the main claim.

### Optional / deferred (just-in-time)

- **Prochlorococcus exometabolomics** — 3 extracellular assays exist
  (`list_metabolite_assays`, MIT9301 / MIT0801 / MIT9313; 79 of 276 metabolites
  detected), but **axenic** and from **different strains** than our partners. A
  "what could be on the menu" reference, invoked only if the consumer-side
  result begs for it.
- **Ortholog-level cross-strain agreement** — a stricter complementary view to
  the substrate-matching (below), added only if the substrate-level pattern
  needs tightening.

---

## Framing

### Hypothesis

In coculture with *Prochlorococcus*, *Alteromonas* obtains its organic carbon
from compounds the cyanobacterium releases (the medium supplies none). This
appears as upregulation — coculture vs axenic — of specific **transport-system →
degradation-pathway modules**, each module standing for one substrate. The
modules that turn on reproducibly (in separate experiments, corroborated by
their catabolism and genomic neighbourhood) name the candidate carbon sources.
We expect a **limited, chemically coherent** set (recognisable marine DOM
components) rather than indiscriminate uptake, organic-carbon importers to move
**more than inorganic-ion importers**, and motility to fall (a known coculture
response). We deliberately do **not** pre-name which substrates should win — the
catalog is discovered, not confirmed against a shortlist — beyond the single
literature-anchored positive check that glycolate (a known cyanobacterial
exudate) should surface if present. `[interpretation]`

### Definitions (three nested levels)

- **Gene** — one locus tag / protein (a permease, ATPase, substrate-binding
  protein, or catabolic enzyme).
- **Transport system** — *one physical transporter*: its subunit genes grouped
  together (binding protein + permease(s) + ATPase), rebuilt from genomic
  adjacency + shared annotation. The **counting unit** — a multi-subunit
  transporter votes once.
- **Module** — *one substrate*: all the transport system(s) that import it **plus**
  that substrate's degradation pathway. The unit of the final catalog and the
  independent hypothesis ("is compound X a carbon source?"). E.g. the glucose
  module = {glucose transport system(s)} + {glucose catabolism genes}.

Hierarchy: **genes → systems → modules.** The mapping system→module is not
strictly one-to-one — a promiscuous transporter may inform more than one module,
a substrate may have several transporters; each system is assigned to a module by
its best substrate evidence, and ambiguous ones are flagged.

### Approach

The unit of analysis is the **module** (one substrate); each substrate is an
**independent** hypothesis (no aggregation across substrates). A module is scored
over its **transport systems**; the only within-system aggregation is collapsing
multi-subunit transporters into one system.

1. **Build modules + controls (per strain, from KG annotation).**
   - **Enumerate transporters** by **unioning three sources** — the BRITE
     transporters tree (`ko02000`; 310 HOT1A3 genes, hierarchical `[KG]`), the
     **TCDB** transporter classification (`genes_by_ontology(ontology="tcdb")`;
     ~10% of genes `[KG]`, coarse for ABC but purpose-built for transporters), and
     product / `function_description` annotation search — so a transporter missed
     by one handle is still caught by another. Then **reconstruct transport
     systems** by grouping subunits (binding protein
     + permease(s) + ATPase) using genomic adjacency (`gene_neighbors`; confirmed
     viable — subunits sit in consecutive locus tags, e.g. the HOT1A3 Fe³⁺ system
     `ACZ81_00580/00585/00590`) + shared substrate annotation. **Grouping needs an
     explicit boundary rule** — adjacency alone will fuse two back-to-back systems,
     or a transporter with an unrelated neighbour. The rule: group genes that are
     both adjacent (within a small locus-tag gap — the exact gap set on the real
     data in methods) **and** carry compatible transporter-component roles or
     shared substrate annotation, and **stop at (a) a role clash, (b) an annotation
     break, or (c) a repeat of an already-filled component role** — a second
     binding protein or second ATPase in the run marks the start of the next
     cassette. Rule (c) is what splits two adjacent, identically-annotated
     *unresolved* ABC cassettes (both "Putative ABC transporter"), which (a) and
     (b) miss. Confirmed on the full transporter set as the methods reconstruction
     task (decision 7).
   - **Classify each system** — importer vs exporter/efflux, and organic-carbon
     vs inorganic — from the BRITE transporter class, TCDB family, and
     product/COG/`function_description` keywords, each call carrying a
     confident-vs-inferred flag. Keep organic-C importers as candidate modules.
     This classifier is a **named output of the substrate-resolution audit**, not
     a black box: it defines both the candidate set *and* the inorganic control
     set, so the confident-flag audit that gates the controls (see Reference
     controls) applies to it too.
   - Tag each module's substrate from **product / COG / `function_description`
     (primary)** + the **BRITE transporters tree** (`ko02000`, hierarchical — its
     deeper levels name substrate classes, though many ABC leaves stay coarse,
     e.g. "Putative ABC transporter") + **TCDB where it is substrate-specific**
     (the `2.A.x` secondary-carrier families; the ABC superfamily `tcdb:3.A.1` is
     substrate-agnostic and carries no substrate signal) + **genomic neighbours**.
     Every tag carries a **confident-vs-inferred** flag.
   - **Assign the finest substrate the evidence confidently supports — and no
     finer.** If the annotation confidently pins a specific compound, use it; if
     confidence only reaches a class ("branched-chain amino acids", "hexose
     sugars"), the label **is** that class — a broad category is an honest tag, not
     a failure. **Non-specific / promiscuous transporters** (a general amino-acid
     permease, a broad sugar carrier) are tagged at their confident **class** and
     carry their **candidate substrate options listed** (e.g. Leu / Ile / Val for a
     branched-chain system), flagged *multi-substrate* — never force-collapsed onto
     one compound, never silently dropped. Broad and multi-substrate modules are
     reported distinctly, with their system count, so a reader sees they name a
     **category of carbon**, not a single named source.
   - Tag each module **C-only** (sugars, organic acids, glycolate, lipids) vs
     **dual C+N** (amino acids, peptides, nucleosides) and report the two
     distinctly, for transparency. **C+N modules do count** as candidate carbon
     sources: amino acids and peptides are carbon-bearing, and this analysis's
     working hypothesis is that **carbon acquisition** from
     Prochlorococcus-derived organic matter (exudate and/or dead-cell material)
     drives the interaction, with nitrogen recycling as a downstream by-product
     — so uptake of a C+N compound is genuine carbon acquisition, not a nitrogen
     signal to be filtered out. The distinct tag simply lets the reader see which
     candidates also carry nitrogen. Catabolism corroboration raises confidence
     for **any** module (C-only or C+N) but is not a requirement for inclusion. (The
     live-exudate vs dead-cell distinction is out of scope here — both count as
     Prochlorococcus-derived carbon.)
   - **Corroborate with breakdown (catabolism) evidence — only where the KG curates
     direction, and never as part of the ranking.** The KG can't tell breakdown from
     biosynthesis at the enzyme level: reaction direction is unreliable (that's *why*
     the KG is direction-agnostic), and GO catabolic/biosynthetic process is absent
     for **8 of the 9** glycolate enzymes tested — the one that carried a process
     term was tagged *biosynthetic* `[KG]`. Direction is curated in exactly one
     place: a **dedicated KEGG _degradation_ map** (e.g. branched-chain amino acids
     `ko00280` = 32 HOT1A3 genes; lysine `ko00310`). So:
     - **Find the most relevant _degradation_ map** for each module's substrate. The
       match may be **exact, broader (a class map for a specific substrate), or
       narrower** — record which; a broader map corroborates the *class*, not the
       specific compound. It must be a **degradation / catabolic** map — a
       direction-neutral metabolism map (e.g. glycolate's `ko00630` "glyoxylate and
       dicarboxylate metabolism") does **not** count.
     - **Test that map for upregulation** in the (experiment × timepoint): **reuse
       the genome-wide `pathway_enrichment` (ORA, proper background, step 4)** — read
       whether the map is over-represented among up-genes; for a map too small for
       ORA, fall back to the **median up-percentile** of its genes (the transport
       rank machinery). Either way the result is one **descriptive up / not-up
       flag**.
     - **Corroboration only — never in the ranking or the FDR family.** The module's
       score and significance are entirely the uptake (transport) side; the
       breakdown flag only raises or lowers confidence in the write-up.
     - **Where no degradation map exists at any granularity** (most specific
       compounds, including glycolate): breakdown direction is **"not determinable"**
       — stated plainly, and the module rests on uptake + chemical specificity. Named
       genes like `glcB` may still be reported as a **narrative soft-positive**, not
       scored.
   - **Module granularity = the finest substrate the annotation resolves.**
     Different substrates **never share a module** — a glucose transporter and a
     fructose transporter are two modules, so a flat one cannot dilute an
     up-regulated other. Systems share a module **only** as alternative routes to
     the *same* substrate. Where a transporter resolves only to a broad label
     ("carbohydrate ABC importer"), it becomes its **own** coarse-labelled module
     flagged *substrate-unresolved* — never merged with a resolved module. The
     achievable granularity is **annotation-limited and empirical**, so the
     **first methods task is a substrate-resolution audit** (per transporter:
     specific compound / narrow class / broad class / multi-substrate with options
     listed / unresolved — always the finest the evidence *confidently* supports),
     which *sets* the module boundaries; the resolution achieved is reported. The KG already
     shows this ceiling is real and uneven: in the BRITE transporters tree only
     ~104 of 310 HOT1A3 transporter genes reach the finest level, and some of
     those leaves are still substrate-agnostic `[KG]`. So the audit is expected to
     return a **mix** — some transporters resolved to a specific compound, many
     only to a class, some unresolved — and the module structure **adapts per
     transporter** to whatever the annotation supports, rather than forcing a
     uniform granularity.
   - **Guard against max inflating coarse modules.** Because the module effect is
     a *max*, a large *substrate-unresolved* module can be lit by a single strong
     member. Two guards: the matched-max null draws **same-size** random sets (so
     a big module is compared against big random sets), and unresolved/coarse
     modules are reported **separately** with their system count shown — a "hit"
     with many systems is read as a possible size artefact, not a specific carbon
     source. Checked on the toy example (a large unresolved module with one strong
     member should not beat its matched-size null).
   - **Reference controls:** inorganic-ion importers. Fe / Na / K / sulfate are
     the reference negatives (should not track carbon provisioning); inorganic
     **N and P** are flagged separately as *interaction-coupled* (themselves
     exchanged in this system), not pure negatives. Exporters/efflux also serve
     as a non-uptake reference. **Caveat:** this control is *not* independently
     derived — it is classified by the same product/COG/TCDB pipeline that
     assigns the candidate carbon modules, so a misannotated organic-C importer
     landing in the "inorganic" bucket contaminates it. Before the inorganic set
     can bound a false-positive rate, its members get a confident-flag audit;
     "reference class sharing the pipeline's failure modes," not "clean
     negatives."

2. **Score each (experiment × timepoint) independently (same method everywhere).**
   - **Rank all detected genes by the KG-provided `log2fc`** into an
     **up-percentile** (0 = most down, 1 = most up) — this orders provided DE
     output, it does not recompute DE. Fold-change is compared only *within* a
     (experiment × timepoint) through this ranking, never across experiments.
     **Why not the stored `rank_up`:** verified against the KG, `rank_up` /
     `rank_down` are populated for **significant genes only** (HOT1A3 primary:
     `rank_up` on just its 111 significant-up genes of 3947); the genome-wide
     stored field `rank_by_effect` (MCP: `rank`) is **magnitude-only, direction-
     blind**. So a *directional, genome-wide* score has to come from `log2fc`.
     `rank_up` / `rank_down` are kept only as validation handles, not the score.
   - **Subunit → system:** a system's percentile = the **median** of its subunit
     up-percentiles (subunits of one machine should co-move). Every subunit has a
     `log2fc`, so nothing drops to null.
   - **Module effect = the highest (max) system up-percentile** in the module —
     the best uptake route; an unused redundant route (low percentile) does not
     penalise it. **Significance = a matched-max permutation null:** draw many
     random same-size system sets from the scored gene universe, take each set's
     max system-percentile, build the null, compare (also vs the inorganic-control
     set). Because every detected gene carries a percentile, nothing drops out of
     the null. Permutation rather than an asymptotic test because modules are
     small (often 1–5 systems) and systems are not independent.
   - **Report the per-system distribution** (each system's percentile and
     significance call), not just the reduced score. A **1-system module cannot be
     "enriched"** — its score is that one system's percentile, weak evidence; real
     significance comes from multi-system coherence.
   - **Scope of the ranking:** genome-wide for `all_detected_genes` experiments
     (HOT1A3 — all 3947 genes have `log2fc`), but only the **significant set** for
     `significant_only` experiments (EZ55, ~300–400 genes have rows at all), where
     the ranking and the null live within that set — a genuinely weaker,
     presence-weighted signal. This is the real rankable-vs-presence distinction
     (it comes from which genes have rows, not from `rank_up`).
   - Timepoints scored **separately** (no collapsing within a time course).
     Motility validation reads the **down** end of the same ranking.

3. **Synthesise without pooling.** One module catalog **per (experiment ×
   timepoint)**. Cross-experiment / cross-strain agreement is a **side-by-side
   matrix (modules × experiment × timepoint)** read for reproducibly-up modules
   and expressed as a **count of independent results** — never a merged dataset
   or a combined p.

4. **Enrichment guard (genome-wide) — also the source of the per-module breakdown
   flag.** The KG's built-in `pathway_enrichment` (ORA) run **once per experiment on
   that experiment's full DE**, against KG ontology terms. It serves two roles: (a) a
   coarse genome-wide check that carbon / degradation pathways are over-represented
   among up-genes (guards against a single-gene or cherry-picked read); and (b) the
   read-off for each module's **breakdown flag** — whether that module's dedicated
   degradation map (step 1) came out over-represented here. It is **not** the module
   *ranking*, which is the transport side (steps 1–2). We do **not** build custom
   gene sets for our own ORA.

5. **Temporal overlay (corroboration only).** The same module method per
   time-course experiment; coculture and axenic trajectories reported
   separately; read as the difference-of-starvation-responses described above —
   it can strengthen a module already supported by a presence contrast but
   cannot name one on its own.

**Output:** a ranked catalog of candidate carbon sources, each carrying — per
(experiment × timepoint) — uptake evidence (rank/direction distribution of its systems),
the breakdown flag where a degradation map exists (else "not determinable"), C-only
vs C+N tag, annotation confidence, inorganic-control contrast, and a cross-experiment
support count.

### Statistics decision (deliberate)

- **Per-gene significance:** use the **source DE calls** as provided (DESeq2 /
  edgeR / Rockhopper adjusted p), respecting `table_scope` — `all_detected_genes`
  keeps tested-absent rows; `significant_only` does not. **No re-computed DE.**
- **Module scoring:** per (experiment × timepoint). Rank all detected genes by
  KG-provided `log2fc` into an up-percentile (**genome-wide** for
  `all_detected_genes`; **within the significant set** for `significant_only`).
  System percentile = median of its subunit percentiles; **module effect = max
  system percentile** (best route, so a redundant unused route can't penalise).
  **Significance = matched-max permutation null** (same-size random system sets,
  take their max; vs the scored universe and separately vs the inorganic-control
  set). The stored `rank_up` / `rank_down` are **significant-gene-only** (verified
  on the KG) and are used as validation handles, **not** as the genome-wide score;
  the genome-wide stored field `rank_by_effect`/`rank` is direction-blind and not
  used for scoring. Modules are defined at the finest resolvable substrate so
  different substrates never share one. Fold-change is **not** compared across
  experiments. `pathway_enrichment` ORA kept as the coarse genome-wide guard.
  Toy-tested against a hand-computed example first.
- **Multiple-testing correction (BH / FDR).** **One FDR family per (experiment ×
  timepoint), and it is the modules' _transport_ test.** The tested unit is the
  **module** (one permutation p per module, from its max-system up-percentile —
  **not** one p per transport system). Those module p-values are corrected by
  **Benjamini–Hochberg within each (experiment × timepoint)**, across the substrate
  modules tested there → q-values; a module is called up in that unit at **q <
  0.10** (discovery-catalog FDR, stated with every call). FDR not FWER because this
  is a discovery catalog and Bonferroni would waste power given small system counts
  and the permutation p-floor. Only modules with **≥2 systems** enter the FDR
  family; 1-system modules carry a bare percentile (weak descriptive evidence),
  outside the correction.
  - **The breakdown flag is supporting evidence, outside the FDR family.** A
    module's up / not-up breakdown flag (from its degradation map, step 1) is **not**
    added to the transport FDR family and gets **no** FDR correction — folding it in
    would double-correct and turn supporting evidence into a second gate. It is
    reported per module as a descriptive (uncorrected) signal.
  - The **source per-gene DE is already BH-corrected** by the original authors
    (`padj`) and is **not** re-corrected. (Permutation p-values have a floor — 10⁴
    perms → min p ≈ 10⁻⁴ — so BH ties at the floor are handled in the methods
    milestone.)
- **No pooling / no combined p.** Cross-experiment agreement is a **count** over
  independent per-experiment results (units passing FDR), not a meta-analytic
  statistic and not a further correction layer — the timepoints of one time
  course are positively dependent, so re-correcting across them would
  double-count. With a handful of heterogeneous experiments a formal combined
  test is neither warranted nor honest; the claim is "reproducible direction
  across independent studies."
- **The count's composition travels with the count.** A bare "supported in N
  experiments" can launder a weak signal, because the supports are not
  equivalent: only the HOT1A3 day-11 experiment is `all_detected_genes` and
  fully **rankable**; the two EZ55 arms are `significant_only` (presence-only,
  see scope limit). So every reported count carries its make-up — how many
  rankable vs presence-only, which strains/partners. The two **EZ55 pCO₂ arms
  (400/800)** are the same lab / strains / cultures at two CO₂ levels, so they
  count as **one** strain-partner support with pCO₂ agreement as an internal
  consistency check, **not** two independent supports. **1-system modules never
  contribute to a support count** — a count is built only from ≥2-system modules
  passing FDR (below); 1-system modules stay descriptive so uncorrected
  single-gene calls can't reach a headline count.
- **Scope limit — `significant_only` (EZ55):** only the significant genes have
  rows (~300–400), so the `log2fc` ranking and the permutation null live **within
  that set**, not genome-wide. Usable, but a weaker, presence-weighted signal than
  the `all_detected_genes` experiments; flagged wherever it contributes. (Separate
  point: the stored `rank_up` / `rank_down` are significant-only in *every*
  experiment, which is why the score is built from `log2fc`, not from them.)

### Validation set (named, expected behaviour)

| Set | KG handle | Expected in presence contrasts | Role |
|---|---|---|---|
| Motility / flagellar | HOT1A3 gene_category "Cell motility" (38 genes) | **DOWN** (Weissberg 2025 reports reduced motility) | direction sanity; testable where down-genes exist (690089, EZ55) |
| Glycolate utilization | `glcB` malate synthase G, `ACZ81_13685` (+ glycolate pathway) | **UP** if glycolate (canonical cyanobacterial exudate) is a source | positive |
| Organic-matter degradation / peptidases | function search | **UP** (Weissberg 2025 finding) | positive, broad |
| Ribosomal / translation | gene_category "Translation" | **~neutral**, not systematically up | negative (guards against reading a growth-rate shift as carbon) |
| Inorganic importers (Fe/Na/K/sulfate) | TCDB / annotation | should **not** track carbon provisioning | built-in negative class |

**Method "works" if:** motility is down; the study's own organic-matter-
degradation signal reappears; and the candidate list is **chemically coherent** —
operationally, the passing modules **concentrate in a small set of recognised
marine-DOM / known-cyanobacterial-exudate chemical classes** (organic acids
including glycolate, amino acids / peptides, sugars, osmolytes), a reference set
named from the literature **before the ranked catalog is read**, not fitted to it.
A catalog scattered evenly across unrelated substrate types, or dominated by
substrate-unresolved coarse modules, does **not** meet the bar. Organic-C modules moving more than the inorganic controls is
**supportive, not decisive** — the growth-rate confound below can also produce it,
so the carbon claim rests on specificity/coherence, not that bulk contrast.
Glycolate is a **soft** positive — its surfacing corroborates, but its
**absence is uninformative** (it may simply not be exuded under these
conditions, or glcB may be constitutively expressed), so a glycolate miss is
**not** a method failure.

### Known confounders and scope limits

Named now so they are not discovered as surprises mid-run:

- **Coculture-vs-axenic conflates carbon with everything else** — nitrogen
  exchange, oxidative-stress relief, growth-rate and cell-cycle differences. An
  upregulated importer is *candidate* evidence, never proof of carbon flux; the
  design infers from the consumer's acquisition machinery, and the claim stays
  at that strength.
- **Growth-rate / regulon confound.** Coculture may simply grow at a different
  tempo, and carbon-acquisition regulons are more growth-coupled than Fe/Na/K
  housekeeping importers — so "organic-C moves more than inorganic" can arise
  from a general anabolic upshift, not carbon-source specificity. The
  ribosomal-neutrality check guards only the crudest version. Consequently the
  carbon claim leans on **specificity and chemical coherence** (a limited,
  recognisable substrate set; glycolate surfacing) rather than the bulk
  "C > inorganic" contrast.
- **Temporal read is difference-of-starvation-responses** (see the temporal
  section) — corroboration only, weighted below the presence contrast.
- **`significant_only` scope** (EZ55) → only significant genes have rows, so its
  `log2fc` ranking and null are within-significant-set, not genome-wide; a
  weaker, presence-weighted signal.
- **Axenic proteomics is timepoint-sparse** — the axenic proteomics arm has
  effectively one informative timepoint (day 31; day 18 calls nothing) `[KG]`,
  so the proteomics temporal overlay rests on a single axenic comparison point
  and carries little weight.
- **Inorganic control shares the module pipeline's annotation failure modes**
  (see Reference controls) — needs a confident-flag audit before bounding a
  false-positive rate.
- **Breakdown direction is only knowable where the KG curates it.** The KG can't
  tell breakdown from biosynthesis at the enzyme level (reaction direction
  unreliable; GO catabolic/biosynthetic process absent for 8/9 glycolate enzymes),
  so breakdown evidence is used **only** where a dedicated KEGG _degradation_ map
  exists (class-level) — everywhere else it is "not determinable" and the module
  rests on uptake + chemical specificity. Even where a map exists, its genes being
  up does **not** escape the growth-rate/regulon confound (a transporter and its
  catabolism are regulated as a unit and can rise together under a general anabolic
  upshift), so the breakdown flag is supporting, never decisive; the carbon claim
  still rests on chemical coherence.

---

## Locked decisions (Plan phase)

1. Widen to a multi-strain question; subject = Weissberg 2025; others =
   independent corroboration.
2. Signal = **presence effect** (coculture vs axenic, primary) **+** the
   Weissberg 2025 **starvation trajectory** (corroboration only — it is a
   difference-of-starvation-responses, weighted below the presence contrast, and
   cannot name a carbon source alone).
3. Backbone = **transporter-anchored, enrichment-guarded** (approach C).
4. Substrate granularity = the **finest the annotation resolves per transporter**
   (not pre-lumped); see decision 12.
5. 2016.70 = **context only** (up-only; same strain, different partner).
6. Substrate tag = product/COG (primary) + TCDB-where-specific + neighbours,
   with confident-vs-inferred flags (TCDB is often superfamily-level for ABC).
7. Counting unit = **transport system** (subunits collapsed), reconstructed by
   adjacency **+ compatible component-role / substrate annotation with an explicit
   boundary rule** (stop at a role clash, an annotation break, or a **repeated
   component role** — the last splits tandem identical unresolved cassettes),
   confirmed on the full transporter set as a methods task. Transporters
   enumerated from the **union** of the BRITE transporters tree (`ko02000`), TCDB,
   and annotation search.
8. Dual C+N substrates **included and counted** as candidate carbon sources,
   **tagged distinctly** for transparency (they also carry N). Working
   hypothesis: carbon from Prochlorococcus-derived organic matter (exudate
   and/or dead cells) drives the interaction and N recycling is a by-product, so
   C+N uptake is genuine carbon acquisition. (Researcher decision, overriding the
   critic's exclusion suggestion — see `proposal_critical_review.md` Concern 5.)
9. **No pooling across experiments**, even within one paper — report each
   individually; agreement by count over separate results.
10. Score by **rank of KG-provided `log2fc`**, per **experiment × timepoint**
    (genome-wide for `all_detected_genes`, within the significant set for
    `significant_only`); system percentile = median of subunit percentiles;
    module effect = **max system up-percentile** (best route; redundant unused
    routes don't penalise); significance = **matched-max permutation null** (vs
    the scored universe and the inorganic controls); toy-tested first. Stored
    `rank_up` / `rank_down` are significant-only → validation handles, not the
    score.
11. Glucose-addition experiment **excluded** (too few DE proteins); exometabolomics
    and ortholog-agreement **deferred** (optional).
12. **Module granularity = finest _confidently_ resolvable substrate**
    (annotation-limited; set by a methods substrate-resolution audit that reads
    BRITE-tree levels + fused product/COG/`function_description`/TCDB). Assign the
    most specific substrate the evidence confidently supports and **no finer**;
    broad categories are valid tags. The audit returns a **mix** —
    specific-compound, class-level, **multi-substrate (options listed)**, and
    unresolved — and the module structure adapts to each: different substrates
    never share a module; **promiscuous transporters become one class-level module
    with their substrate options highlighted**; unresolved ones become own flagged
    coarse modules.
13. **Breakdown (catabolism) evidence = a qualitative flag, only where the KG
    curates direction, never in the ranking.** The KG can't separate breakdown from
    biosynthesis at the enzyme level (reaction direction unreliable; GO
    catabolic/biosynthetic process absent for 8/9 glycolate enzymes, the 1 tagged
    *biosynthetic* — query 13). Direction is curated only in **dedicated KEGG
    _degradation_ maps** (e.g. BCAA `ko00280` = 32 HOT1A3 genes, lysine `ko00310`).
    Per module: find the most relevant degradation map (match may be exact / broader
    / narrower — recorded; must be a catabolic map, not a direction-neutral
    metabolism map); test it for upregulation by **reusing the genome-wide
    `pathway_enrichment` (ORA, step 4)**, or the median up-percentile of its genes
    for a map too small for ORA → a **descriptive up / not-up flag**. **Corroboration
    only — not in the module score or FDR family.** Where no degradation map exists
    (most specific compounds, incl. glycolate) breakdown is **"not determinable"**;
    the module rests on uptake + specificity, and named genes like `glcB` are a
    narrative soft-positive, not scored. (Researcher + grounding queries 11–13.)

See `proposal_notebook.md` for the grounding queries, counts, and rejected
alternatives behind each.
