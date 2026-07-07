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
- **2026-07-07 (correction, second proposal critic)** — The two entries above
  named `rank_up` as the scoring field and "max `rank_up`" as the effect. Both
  wrong: `rank_up` is significant-genes-only (not genome-wide; verified via
  `run_cypher`), and with rank 1 = most-up, "max rank_up" selects the *least*-up
  system. **Corrected:** score = rank of KG-provided `log2fc` → up-percentile
  (genome-wide for `all_detected_genes`, within-significant-set for
  `significant_only`); module effect = **max system up-percentile**; matched-max
  null on that. `rank_up`/`rank_down` → validation handles only. See query 9 and
  `proposal_critical_review.md` second pass.
