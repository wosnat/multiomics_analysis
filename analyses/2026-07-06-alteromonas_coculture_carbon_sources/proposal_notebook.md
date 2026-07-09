# Proposal notebook — grounding, counts, rejected alternatives

Plan-phase record for `2026-07-06-alteromonas_coculture_carbon_sources`.
Owns the KG-grounding queries and the reasoning behind each locked decision.
The plan itself is in `proposal.md`.

## KG grounding (queries + key counts)

All against KG release **0.1.0-alpha.6** (`kg_release_info` → `ok`, 16/16 asserts;
explorer-MCP 0.1.0a4). Whole-KG: 124,751 genes, 197 experiments, 43 papers,
47 organisms.

1. **`list_experiments(organism="Alteromonas", treatment_type=["coculture"])`** →
   31 coculture experiments. Surfaced the two design families: coculture-vs-
   axenic transcriptomes, and glucose-addition proteomics.

2. **`list_experiments(publication_doi=["10.1101/2025.11.24.690089"])`** →
   **10** experiments (not 1, as initially remembered). Alteromonas side (5):
   - `…_coculture_prochlorococcus_med4_hot1a3_rnaseq` — coc-vs-axenic RNA, day 11
     exponential, all_detected_genes (3947), 111↑/163↓. **[primary presence]**
   - `…_growth_state_pro99lown_nutrient_starvation_hot1a3_rnaseq_coculture` —
     starvation-vs-exp RNA time course (d18,31,60,89), coculture.
   - `…_..._hot1a3_rnaseq_axenic` — same, axenic (d18,31,60+89).
   - `…_..._hot1a3_proteomics_coculture` — proteomics time course (d18,31,60,89).
   - `…_..._hot1a3_proteomics_axenic` — proteomics time course (d18,31).
   Plus 5 mirror experiments on the Prochlorococcus MED4 side.
   **Correction captured:** the study is RNA **and** proteomics, but the
   proteomics/time-course contrasts are *starvation-vs-exponential*, not
   coculture-vs-axenic; the only direct presence contrast is the day-11 RNA one.
   The whole study is **continuous light** — the "dark/light Alteromonas
   coculture" the researcher recalled is the separate Moreno-Cabezuelo glucose
   paper, not this study.

3. **`list_experiments(organism="Alteromonas")`** (all contexts) → **49**
   experiments across 10 papers. Full compact table extracted via `jq` from the
   saved result (the raw call exceeded the token cap — see friction log).
   Alteromonas–Prochlorococcus cocultures identified across strains: HOT1A3+MED4
   (690089), HOT1A3+MIT9313 (2016.70), MIT1002+Proch (2016.82 / mSystems /
   ycae131), EZ55+MIT9312 (s43705 / 2017.189).

4. **`list_experiments(publication_doi=["10.1038/ismej.2016.70","10.1038/ismej.2016.82"])`,
   verbose** → control/partner reconciliation:
   - 2016.70 HOT1A3+MIT9313: control "Pro99 medium growth conditions"; **0
     down-genes** in both (188↑/0, 30↑/0); Rockhopper. → up-only; context only.
   - 2016.82 MIT1002: Alteromonas-side contrasts are "24h/48h after co-culturing
     **vs coculture**" — within-coculture time, **not** presence/absence. The
     coculture-vs-axenic contrast in that paper is on the *Prochlorococcus*
     (NATL2A) side. → MIT1002 excluded from the presence set.
   - EZ55+MIT9312 (s43705): coc-vs-axenic at 400/800 pCO₂, significant_only,
     308↑/111↓ and 104↑/84↓. → in scope.

5. **`list_metabolite_assays(organism="Prochlorococcus", compartment="extracellular")`**
   → **3** extracellular assays (MIT9301, MIT0801, MIT9313), 79/276 metabolites
   detected, all **axenic**. Corrects the earlier claim that Prochlorococcus
   exometabolomics was absent — it exists, but axenic and off-partner-strain →
   optional reference only.

6. **`list_filter_values(gene_category)`** → 26 categories; carbon-relevant:
   Transport (1856), Carbohydrate metabolism (4735), Amino acid metabolism
   (7593), Lipid metabolism (3133), Energy production (5124), Cell motility
   (1992), Inorganic ion transport (3921).

7. **Validation-gene existence (HOT1A3):**
   - `genes_by_function("flagellar", organism="HOT1A3")` → 47 hits, 38 in "Cell
     motility". Motility validation grounded.
   - `genes_by_function("glycolate", organism="HOT1A3")` → `glcB` malate
     synthase G (`ACZ81_13685`, "glycolate utilization"), plus glycolate-
     biosynthesis genes. Glycolate validation grounded.

8. **TCDB / system-reconstruction viability
   (`genes_by_ontology(ontology="tcdb", term_ids=["tcdb:3.A.1"], organism="HOT1A3")`,
   `gene_ontology_terms`):**
   - TCDB is populated (12,902 terms). Specific families exist for secondary
     carriers (`2.A.3` APC amino-acid/polyamine, `1.B.3` sugar porin, `2.A.126`
     fatty-acid exporter, …).
   - **But** ABC transporters are annotated only at the **superfamily** node
     `tcdb:3.A.1`, which lumps Fe³⁺, phosphate, nitrate, amino-acid, heme-export,
     capsule-export, and multidrug-efflux systems together → **substrate-
     agnostic for ABC**. Substrate for ABC systems must come from product / COG /
     `function_description` (which are substrate-bearing, e.g. "ABC-type
     branched-chain amino acid transport", "Fe³⁺ transport"). Confirms the
     researcher's caution that TCDB substrate calls are often inferred/coarse.
   - **System reconstruction viable:** subunits sit in consecutive locus tags —
     Fe³⁺ `ACZ81_00580/00585/00590`, nitrate `03160/03165/03170`, phosphate
     `04030/04035/04040`, Mla phospholipid `03775…03795`. Grouping by adjacency +
     shared annotation will rebuild systems.
   - The pulled set also made plain that most ABC systems are inorganic or
     export → the method needs an explicit importer-only, organic-C-only filter,
     and amino-acid/peptide importers are dual C+N (relevant to the study's
     nitrogen story).

9. **Stored DE-edge rank fields — semantics (verified via `run_cypher` on the
   primary experiment, 2026-07-07):** 3947 total edges; `rank_up` non-null on
   **111** (= the significant-up count), `rank_down` on **163** (= significant-
   down), **`rank_by_effect` on all 3947**. So:
   - `rank_up` / `rank_down` are **significant-genes-only** — a within-significant-
     set directional rank, populated in *every* experiment only for its
     significant genes (not genome-wide even in `all_detected_genes`).
   - the genome-wide stored field is **`rank_by_effect`** (the MCP tool surfaces it
     as `rank`) — **magnitude-only, direction-blind**.
   - the MCP tool also exposes per-gene `log2fc` (the raw edge stores it under a
     different key than `log2fc`).
   → **Correction (from the second proposal critic).** An earlier draft wrongly
   treated `rank_up` as genome-wide in the `all_detected_genes` primary. The
   genome-wide *directional* score is instead built by ranking **all detected
   genes on `log2fc`** (genome-wide for `all_detected_genes`; within-significant-
   set for `significant_only`, which has rows only for its significant genes).
   `rank_up` / `rank_down` demoted to validation handles. This is the corrected
   basis of the module scorer.

10. **Annotation-source landscape for transporter ID + catabolism (HOT1A3),
    2026-07-07** (`ontology_landscape`, `list_filter_values(brite_tree)`):
    - **BRITE transporters tree `ko02000`** exists and is purpose-built: 310
      HOT1A3 transporter genes, 3 hierarchical levels (L0 6 classes — ABC 79, MFS
      11, "Other" 205; L1 23 terms; L2 51 terms). It was **not** referenced in the
      first draft — folded in as the transporter enumeration seed and a
      hierarchical substrate source.
    - **Substrate-resolution ceiling quantified:** only **104 of 310** transporter
      genes reach the finest level (L2), and some L2 leaves are still
      substrate-agnostic ("Putative ABC transporter" 7, "ABC-2 type transporter"
      8). Confirms — with numbers — that the substrate-resolution audit must
      expect a *mix* (specific / class / unresolved), not uniform resolution. This
      is the empirical basis for decision 12's "adapts per transporter."
    - **Catabolism-pairing handles:** KEGG coverage ~31%, EC ~35% of genes → the
      workable degradation handles. **CAZy is sparse (~1%)** → right-sized from a
      listed backbone to a where-present bonus.
    - **TCDB coverage ~10%** genome-wide — reinforces query 8 (thin + coarse for
      ABC), so no single ontology resolves substrate; the fused product/COG/
      function + BRITE + TCDB approach stands.

11. **Degradation-pathway handle — chemistry layer viability + direction limit
    (HOT1A3), 2026-07-07** (`list_metabolites`, `gene_ontology_terms`,
    `genes_by_metabolite`, `search_ontology(kegg)`):
    - **Substrate→gene handle exists:** glycolate is a KG metabolite
      (`kegg.compound:C00160`), and `genes_by_metabolite` (metabolism arm) returns
      **9 HOT1A3 enzymes / 5 reactions** for it. So a resolved substrate can be
      paired to its catabolic genes directly — the handle the first draft named
      only vaguely ("KEGG/EC + neighbours").
    - **Two limits that shape the design:** (a) **direction-agnostic** — the 9
      genes mix glycolate-*consuming* reactions (glycolate oxidase, `ghrA`, `hprA`)
      with glycolate-*producing* ones (`gph` phosphoglycolate phosphatase,
      haloacid dehalogenase); the KG cannot tell catabolism from biosynthesis
      (KEGG equation order unreliable upstream, per the tool contract). (b)
      **single-step** — the query returns only reactions the compound itself joins,
      so the validation gene **`glcB` (malate synthase, `ACZ81_13685`) is NOT
      returned** for glycolate; `glcB` acts on glyoxylate, one step downstream, and
      is reached only via the pathway route (GO:0006097 glyoxylate cycle / KEGG
      `ko00630`, both confirmed on the gene via `gene_ontology_terms`).
    - **No universal "degradation" ontology:** `search_ontology(kegg,
      "degradation")` → 35 dedicated `…degradation` maps, but skewed to
      aromatics/xenobiotics (benzoate, xylene, lysine…); core substrates' catabolism
      lives in general metabolism maps. So the handle is substrate-anchored
      chemistry + pathway-anchored KEGG/EC/GO, not a "find the degradation map"
      lookup.
    - → **Decision 13**: degradation = graded corroboration (strong / class-level /
      none) via the two handles, direction-blind caveat named as a confounder,
      never an inclusion gate.

12. **Breakdown-gene set — how big, across compound types (HOT1A3), 2026-07-07**
    (`search_ontology`, `genes_by_ontology`, `list_metabolites`): tested whether the
    "metabolite-connected ∪ pathway-anchored" set is tractable across a specific
    compound, a broad class, and a hub sugar.
    - **Specific organic acid — glycolate:** chemistry layer → 9 genes (query 11);
      its whole KEGG map `ko00630` (glyoxylate/dicarboxylate) → **42** HOT1A3 genes
      (17 energy, 9 amino-acid, …). So even a "peripheral" compound's map is ~5×
      its real breakdown set → **can't use the whole map**.
    - **Broad class — branched-chain amino acids:** a **dedicated KEGG _degradation_
      map** exists, `ko00280` (distinct from biosynthesis `ko00290`) → **32** HOT1A3
      genes. Clean class-level gene set where a dedicated breakdown map exists.
    - **Hub sugar — glucose:** the compound touches **393 genes across 35 KEGG maps**
      (`D-Glucose C00031`; many maps irrelevant — eukaryotic signalling/disease
      `ko04xxx`/`ko05xxx`). Also multiple glucose nodes (`chebi:14313` transport-only
      993 genes; `C00031` metabolism+transport; UDP/ADP/CDP/dTDP-glucose = nucleotide
      sugars, biosynthetic). → (a) pick the right node (`C00031`); (b) a hub sugar's
      breakdown = glycolysis/PPP (shared, always-on) is **not diagnostic** for that
      sugar specifically.
    - → **Design:** breakdown-gene set = enzymes on the compound's
      **entry-and-breakdown steps**, curated per module, **not** the whole map nor
      the full metabolite-connection set; broad classes may use a dedicated breakdown
      map; hub/core-metabolism compounds are downgraded on the breakdown side.
      Folded into the degradation bullet + decision 13.

13. **Breakdown direction is not recoverable per-enzyme — forces the simplification
    (HOT1A3), 2026-07-07** (`gene_ontology_terms` go_bp on glycolate's 9
    chemistry-layer genes): **8 of 9 have no GO biological-process term at all**
    (incl. all three consuming enzymes `ghrA`/`hprA`/glycolate oxidase); the **1**
    annotated (`ACZ81_10870`, a `gph`) is tagged **`go:0046295` glycolate
    _biosynthetic_ process** — a *producing* gene. So GO catabolic/biosynthetic
    process does **not** give direction here (coverage ~1/9, and the one hit points
    the wrong way for "breakdown"). Combined with reaction direction being unreliable
    (the reason the KG is direction-agnostic) and glycolate having no dedicated KEGG
    *degradation* map (its map `ko00630` is direction-neutral), **breakdown direction
    is not determinable for specific compounds**. → **Decision 13 rewritten:**
    breakdown evidence used **only** where a dedicated KEGG degradation map exists
    (class-level, direction curated); read as an up/not-up flag by reusing the
    genome-wide `pathway_enrichment` (ORA) or the map's median up-percentile;
    **corroboration only, never in the ranking/FDR**; else "not determinable" and the
    module rests on uptake + specificity. The per-compound chemistry-layer breakdown
    set, the trimming, the direction filter, and the four-level percentile scoring
    were all **removed**.

14. **KEGG KO carries transporter substrate + component role (HOT1A3),
    2026-07-07** (`gene_ontology_terms` kegg on 5 transporter genes; `search_ontology`
    kegg): each test transporter gene has a KO whose name gives **both substrate and
    role** — Fe³⁺ system `ACZ81_00580/00585/00590` → `K02012` iron(III) **substrate-
    binding** / `K02011` **permease** / `K02010` **ATP-binding**; nitrate `ACZ81_03160`
    → `K15576`; phosphate `ACZ81_04030` → `K02037` permease (all KO level 3). Search
    confirms substrate-specific transporter KOs for our organic-C importers —
    arginine `K09996`, histidine `K10014`, glutamine `K10036`, ribose `K10439`,
    fructose `K10552`, osmoprotectant `K05845`, phosphonate `K02044`, … (1696 "transport
    system substrate-binding protein" KOs). → **KO promoted to a primary substrate +
    component-role source** (tag / classify / boundary-rule / decisions 6–7). Caveats:
    KO overlaps BRITE `ko02000` (BRITE is KO-derived), so it widens *tagging*, not the
    enumeration count; an uncharacterised ("putative") KO yields no substrate → the
    unresolved case; genome-wide KO coverage ~31%, but strong for transporters (5/5
    here).

## Rejected / deferred alternatives

- **Enrichment-scan-only backbone (approach A):** under-resolves "which specific
  carbon compound." Kept only as the coarse guard.
- **Curated substrate panel (approach B):** hand-defined gene sets → confirmation-
  bias risk. Rejected in favour of annotation-driven modules.
- **Pre-defined broad substrate classes:** bakes in lumping before seeing data.
  Rejected — use annotation-family granularity, roll up only if forced.
- **Cross-strain merge by ortholog as primary:** too strict (different strains
  use different transporters for the same compound). Replaced by substrate-
  matching; ortholog agreement kept as an optional stricter complement.
- **Fold-change for cross-experiment comparison:** not comparable across
  DESeq2/edgeR/Rockhopper/proteomics. Replaced by rank.
- **Pooling experiments within a paper:** rejected — report each experiment
  individually; agreement by count over separate results.
- **Glucose-addition experiment as a control:** it is a *positive* manipulation,
  not a negative; excluded outright because too few DE proteins (4–78). The true
  negative control is the inorganic-ion importer class.
- **Prochlorococcus exometabolomics in the core pipeline:** deferred (axenic,
  off-partner-strain; optional reference).

## Decisions log

- **2026-07-06** — Question widened from "what's happening in Weissberg 2025" to
  multi-strain "carbon sources used by Alteromonas in coculture with
  Prochlorococcus"; Weissberg 2025 remains the subject, others independent
  corroboration. (Researcher.)
- **2026-07-06** — MIT1002 dropped from the presence set: its 2016.82 contrasts
  are within-coculture time, not presence/absence. (Grounding query 4.)
- **2026-07-06** — 2016.70 held as context only: up-only, Rockhopper, same
  strain / different partner. (Researcher + query 4.)
- **2026-07-06** — Counting unit = transport system (subunits collapsed);
  adopted pending a full-transporter viability confirmation in methods.
  (Researcher.)
- **2026-07-06** — Dual C+N substrates included but tagged distinctly.
  (Researcher.)
- **2026-07-06** — No pooling across experiments; rank not fold-change.
  (Researcher.)
- **2026-07-06** — Glucose experiment excluded (low DE-protein count).
  (Researcher.)
- **2026-07-07** — C+N modules **included and counted** (not excluded), tagged
  distinctly; researcher override of proposal critic Concern 5 on the C-driven
  working hypothesis. (Researcher.)
- **2026-07-07** — Scoring: use stored DE-edge `rank_up`/`rank_down` per
  (experiment × timepoint); module effect = median `rank_up` of its systems,
  significance = permutation null vs genome and vs inorganic controls; subunits
  collapsed to systems; toy-tested first. (Researcher.)
- **2026-07-07** — Multiple testing: BH/FDR on module permutation p-values
  **within each (experiment × timepoint)**, q < 0.10; ≥2-system modules only;
  source per-gene DE not re-corrected; cross-unit agreement is a count, not a
  further correction. (Researcher.)
- **2026-07-07** — Module granularity = finest resolvable substrate; different
  substrates never share a module (a flat fructose transporter must not dilute an
  up glucose one); unresolved transporters become own flagged coarse modules.
  Achievable resolution is annotation-limited → set by a **substrate-resolution
  audit** as the first methods task. (Researcher: "it all hinges on substrate
  specificity.")
- **2026-07-07** — Module effect switched from **median** to **best (max)** of
  the module's systems, with a **matched-max** permutation null — one working
  uptake route is enough, so an unused redundant paralog must not lower the score.
  (Researcher.)
- **2026-07-07 (pre-approval researcher review)** — Folded in grounding query 10:
  **BRITE transporters tree `ko02000`** added as the transporter enumeration seed
  and a hierarchical substrate source (identification step + decisions 7, 12);
  **CAZy right-sized** to a where-present bonus (KEGG/EC are the primary catabolism
  handles). Two transport-system-definition points made explicit rather than left
  implicit: (a) an **explicit boundary rule** for grouping subunits into systems
  (adjacency + compatible role/annotation; stop at role clash or annotation break),
  confirmed on the full set as a methods task; (b) the **importer/exporter +
  organic/inorganic classifier** named as an audit output that also gates the
  inorganic control. No change to the scoring logic. (Researcher + grounding query
  10.)
- **2026-07-07 (pre-approval researcher review, degradation side)** — Defined the
  **degradation-pathway handle** at plan time (decision 13): substrate-anchored
  chemistry (`genes_by_metabolite`) + pathway-anchored KEGG/EC/GO, graded
  strong/class-level/none, with the **direction-agnostic** limit named as a
  confounder. Grounded on glycolate (grounding query 11): the chemistry arm works
  but is direction-blind and single-step, and misses the downstream validation
  gene `glcB` — which is exactly why the pathway-anchored handle is needed
  alongside it. Symmetric to the transporter substrate-resolution audit: define
  the fallback for non-specific cases now, not mid-run. (Researcher + query 11.)
- **2026-07-07 (third proposal critic, identification/degradation)** — Re-review
  over the just-added ID + degradation machinery: no Blockers, 3 Concerns + 1 Note,
  all fixed inline (see `proposal_critical_review.md` third pass). Key fix: the
  degradation "strong" rung now requires the **breakdown genes to be up in the same
  comparison** as the transporter (was grantable on route-existence alone, which a
  direction-blind handle can't support); qualified as direction-not-specificity;
  boundary rule gained a repeated-role stop for tandem unresolved cassettes;
  "chemically coherent" given a pre-committed operational bar. (Researcher + critic.)
- **2026-07-07 (plain-language sweep, breakdown evidence)** — Rewrote the
  degradation-evidence section in plain words at the researcher's request: dropped
  "corroboration ladder / rung / route / consuming" for a spelled-out four-level
  scale (best / weaker / vaguer / none). Swept the same wording through decision 13,
  the FDR note, the confounder, and the bullet header. No change to the method, only
  the words. (Researcher: "I don't understand terminology.")
- **2026-07-07 (FDR family pinned)** — Made the multiple-testing family explicit:
  **one FDR family per (experiment × timepoint)**, and it is the modules' **transport**
  test — one permutation p **per module** (from its max-system percentile), not per
  system; BH within the unit across ≥2-system modules → q<0.10. **Degradation
  percentiles are corroboration, outside the FDR family** (no parallel correction —
  would double-correct and re-gate); 1-system modules likewise stay descriptive.
  No pooling across units; cross-unit agreement is the composition-tagged count.
  (Researcher question: one run? FDR per each? once per experiment×timepoint?)
- **2026-07-07 (enrichment-guard ontology)** — Decided the *principle* now, deferred
  the *tunable* to the pre-flight tool. Breakdown-flag role = **KEGG forced** (the
  degradation maps are KEGG). Genome-wide guard = **metabolism/pathway ontologies
  KEGG (primary) + EC**, optionally GO-BP — **not** PFam/GO-MF, which `ontology_landscape`
  ranks most statistically suitable (PFam #1, GO-MF #2, EC #9, KEGG #12; grounding
  query 10) but are domain/molecular-function, not "pathways," so wrong for the
  guard's question. Exact **level** within KEGG/EC set **later in methods** via
  `ontology_landscape` per experiment (weighted by quantified genes) + coverage
  check. (Researcher.)
- **2026-07-07 (KEGG KO promoted to primary substrate + role source)** — Grounding
  query 14 showed KO names carry transporter substrate **and** component role at a
  specific level (finer than TCDB's ABC lump). Promoted KEGG KO to a **primary**
  source in the substrate-tag step, the importer/organic classifier, and the
  system-reconstruction **boundary rule** (component roles read straight from the KO
  name); added to the enumeration union and decisions 6–7. Billed as a tagging win,
  not net-widening (KO overlaps BRITE `ko02000`, which is KO-derived). (Researcher.)
- **2026-07-07 (breakdown side cut down to a degradation-map flag)** — After
  grounding query 13 showed breakdown direction is not recoverable per-enzyme (GO
  process absent 8/9; reaction direction unreliable), **removed** the per-compound
  breakdown scoring entirely (chemistry-layer set, trimming, direction filter,
  four-level percentile). Replaced with: **per module, find the most relevant
  _degradation_ map** (exact / broader / narrower, recorded; must be catabolic) and
  read one **up / not-up flag** by reusing the genome-wide `pathway_enrichment` (ORA)
  or the map's median up-percentile if too small for ORA — **corroboration only, not
  in the ranking/FDR**. No degradation map → "not determinable"; module rests on
  uptake + specificity (`glcB`-type genes = narrative soft-positive, not scored).
  Simpler and honest. Degradation bullet, step 4, decision 13, FDR note, confounder,
  Output all updated. (Researcher.)
- **2026-07-07 (breakdown-gene set grounded across compound types)** — Grounded the
  set definition on three compound types (query 12): specific acid (glycolate; map
  ko00630 = 42 genes vs ~3–9 real), broad class (BCAA; dedicated map ko00280 = 32),
  hub sugar (glucose; 393 genes / 35 maps, many irrelevant). Definition fixed to
  **two sources trimmed to the entry-and-breakdown steps** — not the whole KEGG map,
  not the full metabolite-connection set; broad classes may use a dedicated breakdown
  map; **hub/core-metabolism compounds downgraded** (glycolysis is shared/always-on,
  not diagnostic). Also: pick the right metabolite node (`D-Glucose C00031`, not
  `UDP-glucose`). Degradation bullet + decision 13 updated. (Researcher: "union of
  what? match to example compounds and broad classes? ground in KG reality.")
- **2026-07-07 (degradation scoring pinned)** — Clarified how degradation evidence
  is scored, which the plan had left implicit. The degradation route is a **gene
  set** (plausibly-consuming catabolic enzymes via `genes_by_metabolite` metabolism
  arm + KEGG/EC/GO), scored by the **same up-percentile as transport systems**
  (median percentile) — one scoring method across the analysis; this materialises
  "also up" in the corroboration ladder. **No custom ORA** (catabolic sets are tiny,
  ~3 genes for glycolate → underpowered; Rule 5 says don't hand-roll Fisher). The KG
  `pathway_enrichment` (step 4) is a **separate genome-wide guard** on the full DE,
  not the per-module score. Degradation bullet, step 4, and decision 13 updated.
  (Researcher questions: label vs gene-set? run enrichment? on what input? custom
  ORA? rank-score?) (Researcher.)
- **2026-07-07 (substrate specificity = confidence-gated)** — Substrate tag =
  **finest the evidence _confidently_ supports, no finer**; broad categories are
  valid, not failures. **Promiscuous / non-specific transporters** tagged at their
  confident class with **candidate substrate options listed** (e.g. Leu/Ile/Val),
  flagged *multi-substrate* — never force-collapsed to one compound, never dropped;
  reported distinctly with system count. Tag bullet, audit ladder, and decision 12
  updated. (Researcher.)
- **2026-07-07 (enumeration source)** — Added **TCDB**
  (`genes_by_ontology(ontology="tcdb")`) as a third transporter-enumeration source,
  unioned with the BRITE tree and annotation search, so enumeration doesn't depend
  on any single handle's coverage. (Researcher.)
- **2026-07-07 (terminology)** — Replaced the word "co-expression" throughout
  `proposal.md` with the accurate plain phrase "breakdown genes up in the same
  comparison." Rationale: the primary experiment is a single coculture-vs-axenic
  snapshot (one `log2fc` per gene), so there is no cross-sample correlation to
  compute; "co-expression" borrowed the credibility of a correlation we don't have.
  What we actually test is same-direction-in-the-same-contrast. (Researcher.)
- **2026-07-07 (correction, second proposal critic)** — The two entries above
  named `rank_up` as the scoring field and "max `rank_up`" as the effect. Both
  wrong: `rank_up` is significant-genes-only (not genome-wide; verified via
  `run_cypher`), and with rank 1 = most-up, "max rank_up" selects the *least*-up
  system. **Corrected:** score = rank of KG-provided `log2fc` → up-percentile
  (genome-wide for `all_detected_genes`, within-significant-set for
  `significant_only`); module effect = **max system up-percentile**; matched-max
  null on that. `rank_up`/`rank_down` → validation handles only. See query 9 and
  `proposal_critical_review.md` second pass.
