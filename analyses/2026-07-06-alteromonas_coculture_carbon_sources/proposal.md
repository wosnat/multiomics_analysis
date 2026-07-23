# Proposal — Carbon sources used by *Alteromonas* in coculture with *Prochlorococcus*

**Analysis slug:** `2026-07-06-alteromonas_coculture_carbon_sources`
**Plan locked:** 2026-07-07 (framing refined from 2026-07-06)
**Approved:** 2026-07-12 — researcher-approved after four critic passes; Run phase open.
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
contrast, but a temporal ramp **alone does not name a carbon source**. Note too
that each arm's baseline is its *own coculture (or axenic) exponential* state, so a
module that is **constitutively up in coculture** — exactly what the day-11 presence
contrast detects — is already "on" at the coculture arm's baseline and reads **flat**
across the temporal ramp. Temporal flatness of a presence-up module is therefore
**expected and non-contradictory**; the temporal read captures the starvation-ramp
component, which is only partly aligned with constitutive coculture upregulation.

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

- **MIT1002 cocultures** (`10.1038/ismej.2016.82`, Biller 2016): the
  *Alteromonas*-side DE is, per the source supplementary table (moesm99),
  **"log2FoldChange (24 vs 12 hrs after addition)"** and **"(48 vs 12 hrs after
  addition)"** — i.e. a within-coculture *time* contrast against the **12 h
  coculture timepoint**, **not** presence/absence. The KG's `control` field flattens
  this to "Co-culture with Prochlorococcus NATL2A" (reference timepoint dropped — see
  `gaps_and_friction.md` 2026-07-22); the source table is unambiguous. Critically,
  **the study has no axenic *Alteromonas* arm at all** (the axenic bottles are axenic
  *Prochlorococcus*; *Alteromonas* was only ever sampled in coculture), so **no
  presence contrast is constructible.** Excluded from the presence set.
  - **Also excluded from the temporal corroboration** — it is *not* the equivalent of
    the Weissberg 2025 temporal read. That read is a **difference of two trajectories**
    (coculture *and* axenic, each vs its own exponential baseline); the subtraction is
    what isolates the coculture-specific component. Biller MIT1002 is a **single
    coculture-only trajectory** with no axenic arm to difference against, so a
    12h→24h/48h rise cannot be separated from generic post-transfer adaptation and
    growth recovery. And the confound is concrete: Fig 1a shows *Alteromonas* abundance
    **declined the first day after introduction, then grew**, so the 12 h reference
    sits near the growth trough and 24v12h / 48v12h are effectively a
    **growth-recovery-vs-trough** contrast — the growth-rate/regulon confound (named
    under Known confounders), here uncontrolled. On top of that it is a **third strain
    (MIT1002) and third partner (NATL2A)** outside the current scope, and
    **direction-incomplete** (0 significant-down genes → no motility check). It is
    therefore *weaker* than the already-weak Weissberg temporal read, not equivalent to
    it. At most a growth-recovery-confounded narrative aside for a module already named
    on stronger evidence; **not scored, not counted.**
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
appears as upregulation — coculture vs axenic — of specific **transport-system
modules** (one module = one substrate), **with a breakdown-pathway corroboration
flag where a dedicated KEGG degradation map exists** (not determinable for most
compounds — see the breakdown-evidence rule). The modules that turn on reproducibly
(in separate experiments, and where testable corroborated by their catabolism and
genomic neighbourhood) name the candidate carbon sources.
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
- **Module** — *one substrate*: all the transport system(s) that import it, **plus a
  breakdown-pathway corroboration flag where a dedicated KEGG degradation map exists**
  (absent for most compounds). The *scored* unit is the transport system(s); the
  breakdown flag is corroboration only. The unit of the final catalog and the
  independent hypothesis ("is compound X a carbon source?"). E.g. the glucose module
  = {glucose transport system(s)} + (glycolysis is shared/always-on → no usable
  breakdown flag).

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
   - **Enumerate transporters** by **unioning four sources** — the BRITE
     transporters tree (`ko02000`; 310 HOT1A3 genes, hierarchical `[KG]`), **KEGG
     KO** (`gene_ontology_terms` / `genes_by_ontology(ontology="kegg")`; the KO name
     carries substrate **and** component role — see the tag step — though it overlaps
     BRITE, which is KO-derived), the **TCDB** transporter classification
     (`genes_by_ontology(ontology="tcdb")`; ~10% of genes `[KG]`, coarse for ABC but
     purpose-built for transporters), and product / `function_description`
     annotation search — so a transporter missed by one handle is still caught by
     another. Then **reconstruct transport systems** by grouping subunits (binding
     protein
     + permease(s) + ATPase) using genomic adjacency (`gene_neighbors`; confirmed
     viable — subunits sit in consecutive locus tags, e.g. the HOT1A3 Fe³⁺ system
     `ACZ81_00580/00585/00590`) + shared substrate annotation. **Grouping needs an
     explicit boundary rule** — adjacency alone will fuse two back-to-back systems,
     or a transporter with an unrelated neighbour. The rule: group genes that are
     both adjacent (within a small locus-tag gap — the exact gap set on the real
     data in methods) **and** carry compatible transporter-component roles —
     **read directly from the KEGG KO name where present** ("substrate-binding" /
     "permease" / "ATP-binding", grounded on the Fe³⁺ system `K02010/11/12` `[KG]`) —
     or shared substrate annotation, and **stop at (a) a role clash or (b) an
     annotation break**. **Shared specific-substrate annotation (or a KO that
     resolves the subunits to one named system) holds a system together even when a
     component role repeats** — many real ABC importers legitimately carry two
     permeases and/or two ATPases (e.g. the branched-chain amino-acid importer
     `livKHMGF`: `livH`/`livM` both permease `K01997`/`K01998`, `livG`/`livF` both
     ATP-binding `K01995`/`K01996` `[KG]`), and must **not** be split. Only as a
     **tiebreaker for indistinguishable cassettes** — two adjacent subunits that are
     both *unresolved / putative* (e.g. both "Putative ABC transporter") and share
     **no** specific substrate — does a **repeat of an already-filled role** (a
     second binding protein or ATPase) mark a new cassette. The small locus-tag gap
     and this tiebreaker are confirmed on the full transporter set in methods
     (decision 7).
   - **Classify each system** — importer vs exporter/efflux, and organic-carbon
     vs inorganic — from the **KEGG KO** / BRITE transporter class, TCDB family, and
     product/COG/`function_description` keywords, each call carrying a
     confident-vs-inferred flag. Keep organic-C importers as candidate modules.
     This classifier is a **named output of the substrate-resolution audit**, not
     a black box: it defines both the candidate set *and* the inorganic control
     set, so the confident-flag audit that gates the controls (see Reference
     controls) applies to it too.
   - Tag each module's substrate from **KEGG KO + product / COG /
     `function_description` (primary)** — the KO name usually gives the substrate at
     a specific level (grounded: `K02012` iron(III), `K10036` glutamine, `K10552`
     fructose, `K05845` osmoprotectant `[KG]`), often finer than TCDB — plus the
     **BRITE transporters tree** (`ko02000`, hierarchical; some ABC leaves stay
     coarse, e.g. "Putative ABC transporter") + **TCDB where it is substrate-specific**
     (the `2.A.x` secondary-carrier families; the ABC superfamily `tcdb:3.A.1` is
     substrate-agnostic and carries no substrate signal) + **genomic neighbours**.
     Every tag carries a **confident-vs-inferred** flag; an uncharacterised
     ("putative") KO simply yields no substrate → the unresolved case.
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
     - **Find the relevant _degradation_ map(s)** for each module's substrate —
       **more than one is allowed.** A single map is the common case, but multiple are
       genuinely relevant when (i) a **multi-substrate / promiscuous** module's options
       degrade through *different* maps (e.g. an amino-acid permease spanning lysine
       `ko00310` + histidine `ko00340`), (ii) one substrate has **parallel catabolic
       routes**, or (iii) both an **exact** and a **broader class** map exist and both
       inform. Each map's match is recorded as **exact, broader (a class map for a
       specific substrate), or narrower** — a broader map corroborates the *class*, not
       the specific compound. Every map must be a **degradation / catabolic** map — a
       direction-neutral metabolism map (e.g. glycolate's `ko00630` "glyoxylate and
       dicarboxylate metabolism") does **not** count.
     - **Test each map for upregulation** in the (experiment × timepoint): **reuse
       the genome-wide `pathway_enrichment` (ORA, proper background, step 4)** — read
       whether the map is over-represented among up-genes; for a map too small for
       ORA, fall back to the **median up-percentile** of its genes (the transport
       rank machinery). Each map yields **one descriptive up / not-up flag**, reported
       **per map with its granularity** — never collapsed to "the best one." The
       module-level breakdown read then **shows its composition** ("2 of 3 degradation
       maps up"), never a bare "breakdown corroborated": "at least one of several maps
       up" is *weaker* corroboration than "the single most-relevant map up," so the
       denominator travels with the flag (the same composition-travels-with-the-count
       discipline used for the cross-experiment support count). Because the flag stays
       corroboration-only (below), multiple maps raise **no** multiple-testing concern
       in the FDR family.
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
   - **Guard against a big vague module scoring high just for being big.** The
     module's score is its **best (highest-ranked) system**, so a module holding
     **many** systems has an unfair edge — the best of 20 tends to beat the best of
     2 purely because you took more tries (like keeping the highest of more dice).
     The **unresolved / coarse** modules are exactly the big ones, so they're most
     at risk of a fake hit. Two guards: (1) each module is compared against **random
     sets of the _same_ number of systems** (the same-size comparison used
     throughout) — both sides get the same "more tries → higher best" boost, so it
     cancels, and only a genuinely high best passes; (2) unresolved / coarse modules
     are **reported separately, with their system count shown**, so a hit with many
     systems is read as a possible size effect, not a named carbon source. Checked
     on a hand-built toy: a large unresolved module with one strong member and the
     rest flat should **not** beat its same-size comparison.
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
     up-percentiles (subunits of one machine should co-move). In the
     **`all_detected_genes`** experiments every subunit has a `log2fc`, so nothing
     drops to null. In the **`significant_only`** experiments (EZ55) only significant
     genes have rows, so a system can have subunits with **no row** — the median is
     then taken over the present (most-DE) subunits, which biases it **upward** and
     leaves the co-movement premise untestable there. The rule for scoring
     partial-coverage systems in `significant_only` (a minimum-present-subunits
     threshold, or score-on-present with the present-subunit count shown) is set in
     **methods** on the real EZ55 subunit-coverage data — a just-in-time call, not
     guessed now. This is a genuinely weaker, presence-weighted signal (already
     flagged), and the partial-coverage bias travels with every EZ55 system call.
   - **Module effect = the highest (max) system up-percentile** in the module —
     the best uptake route; an unused redundant route (low percentile) does not
     penalise it. **Significance = a matched-max permutation null:** draw many
     random same-size system sets from the scored gene universe, take each set's
     max system-percentile, build the null, compare (also vs the inorganic-control
     set). **"Matched" means matched on system *structure*, not just system count:**
     each drawn system mirrors a real system's **subunit count**, so a single-gene
     system is compared against random **single genes** and a k-subunit system
     against random **k-gene medians**. This matters for single-gene secondary
     carriers (below): without subunit-count matching, a single gene's unsmoothed
     (higher-variance) percentile would be judged against median-smoothed multi-gene
     systems and look more significant than it is. Because every detected gene
     carries a percentile, nothing drops out of the null. Permutation rather than an
     asymptotic test because modules are small (often 1–5 systems) and systems are
     not independent. (The exact same-size, subunit-count-matched draw is fixed and
     toy-tested in methods.)
   - **Report the per-system distribution** (each system's percentile and
     significance call), not just the reduced score. A **1-system module is scored
     and tested like any other** — its same-size null is well-defined (draw random
     single systems), and *when the system is multi-subunit* it is itself several
     co-moving subunits, so a single reproducibly-up system *can* be significant. Its
     evidence is simply **thinner** than a multi-system coherent module, so its
     **system count travels with the call** and multi-system coherence reads as
     stronger — but a 1-system module is **not** excluded from testing.
   - **Single-gene systems (special care).** Many secondary carriers (TCDB `2.A.x`)
     are **single-polypeptide** transporters, so a system — and hence a whole module —
     can rest on **one gene**. This is the genuinely thin case: the module effect is
     that one gene's percentile, with no co-movement and no median smoothing (it is
     *not* covered by the "a system is several subunits" argument above). It is
     **kept in the catalog and tested like any other** (pass-4 decision: don't
     structurally exclude single-transporter substrates), with three cares:
     (1) its null is **subunit-count-matched** to random single genes (above);
     (2) it is flagged the **thinnest evidence tier** — a **gene count** (not just a
     system count) and the **source per-gene DE `padj` + direction** travel with the
     call, because a rank-of-`log2fc` percentile can be high without the source
     authors calling the gene significant, so both are shown; (3) it **does not
     headline on its own** and reads as needing corroboration. That corroboration
     genuinely can arrive — a single-gene uptake call **paired with an up
     degradation map** for the same substrate (breakdown flag, step 1) is materially
     stronger than the gene alone, since the catabolism side is independent evidence;
     likewise cross-experiment reproducibility, chemical coherence, or a **confident**
     (not inferred) substrate tag. So a single-gene module **can** be a real,
     reportable call — it simply carries its thinness visibly and leans on the
     corroborating lines.
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
   or a combined p. **Different omics platforms are different experiments.** A
   paper that ran both transcriptomics and proteomics on the same contrast (e.g.
   the HOT1A3 starvation trajectory has separate `…_rnaseq_*` and
   `…_proteomics_*` experiment ids `[KG]`) contributes **separate**
   `(experiment × timepoint)` units — each scored, ranked, and FDR-corrected on
   its own — and they are **reported separately**, never collapsed into one
   omics-agnostic module call. Their agreement is read from the matrix as
   cross-platform corroboration (see the composition rule below), not by merging.
   The "counted once" below is per **strain-partner-condition (biological) contrast**
   — so it collapses only RNA and protein of the *same* contrast, never the day-11
   presence contrast and the starvation-trajectory temporal read (different
   conditions, weighted differently).

4. **Enrichment guard (genome-wide) — also the source of the per-module breakdown
   flag.** The KG's built-in `pathway_enrichment` (ORA) run **once per experiment on
   that experiment's full DE**. It serves two roles: (a) a coarse genome-wide check
   that carbon / degradation pathways are over-represented among up-genes (guards
   against a single-gene or cherry-picked read); and (b) the read-off for each
   module's **breakdown flag** — whether that module's dedicated degradation map
   (step 1) came out over-represented here. It is **not** the module *ranking*,
   which is the transport side (steps 1–2). We do **not** build custom gene sets for
   our own ORA.
   - **Which ontology.** Role (b) is **forced to KEGG** — the breakdown maps *are*
     KEGG pathways. Role (a) runs on **metabolism / pathway ontologies — KEGG
     (primary, so it matches the breakdown maps and reads directly as "carbon
     pathways") + EC**, optionally GO **BP** for process level. **Not** PFam / GO-MF:
     the KG's `ontology_landscape` pre-flight ranks those most *statistically*
     suitable (PFam #1, GO-MF #2, EC #9, KEGG #12 in HOT1A3 `[KG]`), but they are
     protein-domain / molecular-function, not *pathways*, so they can't answer the
     guard's question. The **exact level** within KEGG / EC is set **later, in
     methods**, by running `ontology_landscape` **per experiment** (weighted by that
     experiment's quantified genes) and confirming coverage — a just-in-time call the
     tool makes on the real data, not guessed now. **The two roles may run at
     different KEGG levels:** the breakdown flag (b) is read at **KEGG pathway-map
     level** (where the degradation maps like `ko00280` are terms) — via the
     median-up-percentile fallback if the genome-wide guard (a) settles on a
     different KEGG granularity — so methods must not assume one `ontology_landscape`
     level serves both.

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
  and the permutation p-floor. **All modules — including 1-system modules — enter
  the FDR family** and get a proper q from their same-size null (a 1-system module is
  *not* an uncorrected single-gene call: its null is well-defined, and *when the system
  is multi-subunit* it is several co-moving subunits; a **single-gene** system instead
  relies on its subunit-count-matched null and is flagged the thinnest tier — see
  "Single-gene systems" above). Their evidence is thinner, so **every call carries its
  system count** and multi-system coherence reads as stronger — but single-transporter
  substrates (glutamine, iron, phosphate — one transporter each) are **not**
  structurally excluded from the catalog. *(This corrects the earlier ≥2-system-only
  gate — see `proposal_critical_review.md` fourth pass.)*
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
  rankable vs presence-only, which strains/partners, **which omics**. The two
  **EZ55 pCO₂ arms (400/800)** are the same lab / strains / cultures at two CO₂
  levels, so they count as **one** strain-partner support with pCO₂ agreement as an
  internal consistency check, **not** two independent supports. **The same applies
  across omics platforms:** transcriptomics and proteomics of the *same* biological
  contrast (same strain / partner / condition) are **one** strain-partner support
  measured on two molecular layers — scored and reported separately, but counted
  **once**, with transcript↔protein agreement carried as **cross-platform
  corroboration** in the composition (a genuine strengthener — two layers, not a
  near-replicate), **not** as two independent supports. Counting RNA and protein of
  one contrast as two studies would launder a single result into two. **A 1-system module that
  passes FDR does contribute to a support count**, but its **system count travels
  with it** — a count made of thin 1-system supports is read as weaker than one from
  multi-system coherent modules. (The earlier rule excluded 1-system modules on the
  false premise that they were uncorrected single-gene calls; they get a proper q,
  so the honest fix is to show the composition, not to exclude them.) **For
  single-gene systems/modules the composition goes one level finer:** a **gene count**
  (not just a system count) and the **source per-gene DE `padj` + direction** travel
  with the call — the thinnest tier, shown as such. Such a call still counts and can
  be real, but a support made of single-gene modules reads as weaker than one of
  multi-subunit or multi-system modules, and it leans on its corroborating lines
  (an up degradation map for the same substrate especially, plus cross-experiment
  reproducibility, chemical coherence, or a confident substrate tag).
- **Scope limit — `significant_only` (EZ55):** only the significant genes have
  rows (~300–400), so the `log2fc` ranking and the permutation null live **within
  that set**, not genome-wide. Usable, but a weaker, presence-weighted signal than
  the `all_detected_genes` experiments; flagged wherever it contributes. (Separate
  point: the stored `rank_up` / `rank_down` are significant-only in *every*
  experiment, which is why the score is built from `log2fc`, not from them.)

### Validation set (named, expected behaviour)

| Set | KG handle | Expected in presence contrasts | Role |
|---|---|---|---|
| Motility / flagellar | HOT1A3 flagellar genes — `genes_by_function("flagellar")`, 47 hits, 38 in the "Cell motility" category | **DOWN** (Weissberg 2025 reports reduced motility) | direction sanity; testable where down-genes exist (690089, EZ55) |
| Glycolate utilization | `glcB` malate synthase G, `ACZ81_13685` (+ glycolate pathway) | **UP** if glycolate (canonical cyanobacterial exudate) is a source | positive |
| Organic-matter degradation / peptidases | function search | **UP** (Weissberg 2025 finding) | positive, broad |
| Ribosomal / translation | gene_category "Translation" | **~neutral**, not systematically up | negative (guards against reading a growth-rate shift as carbon) |
| Inorganic importers (Fe/Na/K/sulfate) | TCDB / annotation | should **not** track carbon provisioning | built-in negative class |

**What "the method works" means — two separate questions, and neither one is
"did we get a decisive answer."**

**(1) Is the machinery trustworthy?** These are sanity checks on the *pipeline*,
not on the biology: motility is **down** where down-genes exist; the study's own
organic-matter-degradation / peptidase signal reappears **up**; ribosomal /
translation stays **~neutral** (a growth-rate shift isn't being read as carbon);
inorganic importers don't track carbon provisioning; and the catalog is **not**
dominated by substrate-unresolved coarse modules or by the aromatic expected-negative.
If these hold, the pipeline is behaving and its output can be trusted; if they fail,
the pipeline itself is suspect. Within this, the **chemical-coherence check is
deliberately weak and near-confirmatory** — the marine-DOM class set (organic acids
incl. glycolate, amino acids / peptides, sugars, osmolytes) spans nearly all
characterised marine-heterotroph organic uptake, so "the hits fall in it" is almost
guaranteed and is **not** load-bearing. To give it teeth we pre-commit two sharper
checks. (a) **Coarse-module domination** — a catalog dominated by substrate-unresolved
coarse modules does **not** meet the bar (real teeth: the audit is expected to return
many coarse modules). (b) An **expected-negative**, **aromatic / xenobiotic-degradation
importers** (benzoate, naphthalene, halo-aromatics — not plausible *Prochlorococcus*
exudates) should **not** dominate the catalog; if they do, the method is flagging
noise. This aromatic prong is a **cross-strain** check whose weight depends on how many
aromatic importers each strain actually has — the **substrate-resolution audit counts
them per strain**, so its falsification power is set there, not assumed. (For HOT1A3 in
particular it may be near-vacuous — very few aromatic importers — so the prong leans on
strains that have more, while HOT1A3's falsifiable weight rests on the coarse-module
prong and the reproducible-q core.) A catalog scattered evenly across unrelated
substrate types also fails the bar. Organic-C modules moving more than the inorganic
controls is **supportive, not decisive** — the growth-rate confound (below) can also
produce it, so the carbon claim rests on specificity/coherence, not that bulk contrast.
Glycolate is a **soft** positive — its surfacing corroborates, but its **absence is
uninformative** (it may simply not be exuded here, or glcB may be constitutive), so a
glycolate miss is **not** a method failure.

**(2) What a trustworthy run delivers — and it is deliberately *not* a decisive
answer.** Even with the machinery validated, the evidence is KG-only,
coculture-vs-axenic **confounded** (carbon is entangled with nitrogen exchange,
oxidative-stress relief, and growth-rate differences — see Known confounders), and
**annotation-limited**. So the honest expected output is a **graded candidate catalog,
not a list of named carbon sources**: a handful of better-supported modules
(reproducible q<0.10 across independent experiments, ideally with an up degradation map
and a confident substrate tag), **many tentative "possible" modules**, and honest
**"not determinable"** cases. **Ending with ranked possibilities rather than answers is
an expected and acceptable result at the current evidence, not a method failure** — an
upregulated importer is *candidate* evidence, never proof of carbon flux. The
falsifiable core remains the per-module reproducible q<0.10 calls; everything above it
is prioritization, tagged with its uncertainty.

**(3) The decisive test is wet-lab — and prioritizing it is the point, not a
shortfall.** Whether *Alteromonas* actually **grows on** a candidate compound (as sole
or supplemented carbon source, under coculture-relevant conditions) is answerable only
by a **growth experiment**, which the KG cannot stand in for. A ranked,
uncertainty-tagged shortlist that nominates the highest-value compounds for such assays
is therefore a **legitimate deliverable in its own right** — the intended output of
this analysis, and the natural hand-off to follow-up growth experiments.

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
6. Substrate tag = **KEGG KO** + product/COG (primary) + BRITE + TCDB-where-specific
   + neighbours, with confident-vs-inferred flags. KO names carry substrate **and**
   component role at a specific level (e.g. iron(III) / glutamine / fructose /
   osmoprotectant transport systems), usually finer than TCDB's ABC superfamily lump;
   an uncharacterised ("putative") KO yields no substrate.
7. Counting unit = **transport system** (subunits collapsed), reconstructed by
   adjacency **+ compatible component-role / substrate annotation with an explicit
   boundary rule** (component roles read from the **KEGG KO** name where present —
   substrate-binding / permease / ATP-binding; stop at a role clash or an annotation
   break). **A repeated role does _not_ split a system that shares a specific
   substrate** — real ABC importers often have two permeases / two ATPases (e.g.
   branched-chain `livKHMGF`); the repeated-role stop is only a **tiebreaker for
   indistinguishable unresolved/putative cassettes**. Confirmed on the full
   transporter set as a methods task. Transporters enumerated from the **union** of
   BRITE (`ko02000`), **KEGG KO**, TCDB, and annotation search.
8. Dual C+N substrates **included and counted** as candidate carbon sources,
   **tagged distinctly** for transparency (they also carry N). Working
   hypothesis: carbon from Prochlorococcus-derived organic matter (exudate
   and/or dead cells) drives the interaction and N recycling is a by-product, so
   C+N uptake is genuine carbon acquisition. (Researcher decision, overriding the
   critic's exclusion suggestion — see `proposal_critical_review.md` Concern 5.)
9. **No pooling across experiments**, even within one paper — report each
   individually; agreement by count over separate results. **Different omics
   platforms are different experiments:** transcriptomics and proteomics of the
   same contrast are separate `(experiment × timepoint)` units, scored and reported
   separately, but counted **once** per strain-partner-**condition** (biological)
   contrast with transcript↔protein agreement as cross-platform corroboration (same
   treatment as the EZ55 pCO₂ arms; does **not** collapse the presence contrast and
   the temporal read). (Researcher, 2026-07-23.)
10. Score by **rank of KG-provided `log2fc`**, per **experiment × timepoint**
    (genome-wide for `all_detected_genes`, within the significant set for
    `significant_only`); system percentile = median of subunit percentiles;
    module effect = **max system up-percentile** (best route; redundant unused
    routes don't penalise); significance = **matched-max permutation null** (vs
    the scored universe and the inorganic controls); toy-tested first. Stored
    `rank_up` / `rank_down` are significant-only → validation handles, not the
    score. **"Matched" includes subunit count:** a single-gene system is nulled
    against random single genes, a k-subunit system against random k-gene medians.
    **Single-gene systems/modules** (common for TCDB `2.A.x` secondary carriers) are
    **kept and tested** but flagged the **thinnest tier** — gene count + source
    per-gene `padj`/direction travel with the call, they don't headline alone, and
    they lean on corroboration (an up degradation map especially, cross-experiment
    reproducibility, chemical coherence, or a confident substrate tag). (Researcher,
    2026-07-23.)
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
    Per module: find the relevant degradation map(s) — **more than one is allowed**
    (a multi-substrate module whose options span different maps, a substrate with
    parallel catabolic routes, or an exact + broader-class pair; each match recorded
    exact / broader / narrower; every map must be catabolic, not a direction-neutral
    metabolism map); test **each** for upregulation by **reusing the genome-wide
    `pathway_enrichment` (ORA, step 4)**, or the median up-percentile of its genes
    for a map too small for ORA → **one descriptive up / not-up flag per map**,
    reported per map with its granularity and — where a module has several — with the
    **composition shown** ("2 of 3 maps up"), never collapsed to the best one.
    **Corroboration only — not in the module score or FDR family** (so multiple maps
    raise no multiple-testing concern). Where no degradation map exists (most specific
    compounds, incl. glycolate) breakdown is **"not determinable"**; the module rests
    on uptake + specificity, and named genes like `glcB` are a narrative soft-positive,
    not scored. (Researcher + grounding queries 11–13; multi-map allowance 2026-07-23.)

See `proposal_notebook.md` for the grounding queries, counts, and rejected
alternatives behind each.
