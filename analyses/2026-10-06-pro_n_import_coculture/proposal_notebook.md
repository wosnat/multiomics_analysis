# Proposal notebook — grounding, counts, rejected alternatives

Plan-phase record for `2026-10-06-pro_n_import_coculture`.
Owns the KG-grounding queries and the reasoning behind each locked decision.
The plan itself is in `proposal.md`.

**Opening prompt (researcher, 2026-10-06):** "when alteromonas and
prochlorococcus are in coculture, what are the N products in alteromonas ->
prochlorococcus cross feeding"

## KG grounding (queries + key counts)

All against KG release **0.1.0-alpha.7** (built 2026-09-22; `kg_release_info` →
`ok`, 17/17 asserts; explorer 0.1.0-alpha.5). Whole KG: 127,035 genes, 209
experiments, 49 papers, 48 organisms.

1. **`list_metabolite_assays(summary=True)`** → 14 assays, all on axenic
   *Prochlorococcus* (MIT9313 5, MIT9301 4, MIT9312 2, MIT0801 2, MIT9303 1);
   `background_factors: axenic` = 14/14. **No metabolite measurement in any
   coculture** `[KG]`: the exchanged N compounds are not measured directly
   `[gap]`. Every answer must be inferred from the organisms' gene expression.

2. **`list_experiments(organism="Prochlorococcus", coculture_partner="Alteromonas")`**
   → 5, all RNA-seq, coculture vs. axenic:
   | experiment | pair | design | table_scope | per-TP genes |
   |---|---|---|---|---|
   | `10.1101/2025.11.24.690089_coculture_alteromonas_hot1a3_med4_rnaseq` | MED4 + HOT1A3 | day 11 (exponential), day 18 (nutrient_limited) | all_detected | 1849 |
   | `10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_med4_rnaseq` | MED4 + HOT1A3 | single contrast, exponential | all_detected | 1714 |
   | `10.1038/ismej.2016.70_..._mit9313_rnaseq_inoc_05e6` | MIT9313 + HOT1A3 | single, exponential | all_detected | 2267 |
   | `10.1038/ismej.2016.70_..._mit9313_rnaseq_inoc_5e6` | MIT9313 + HOT1A3 (high inoculum) | single, exponential | all_detected | 2268 |
   | `10.1038/ismej.2016.82_coculture_alteromonas_macleodii_mit1002_natl2a_rnaseq` | NATL2A + MIT1002 | 7 TPs, −12 h to 48 h | **significant_any_timepoint** (353 genes) | 353 |

3. **`list_experiments(organism="Alteromonas", coculture_partner="Prochlorococcus")`**
   → 15. Usable as coculture vs. axenic: HOT1A3 + MED4 (Weissberg 2025; days
   11/18/31; 3947 genes, all_detected); HOT1A3 + MIT9313 ×2 (2016; all_detected);
   EZ55 + MIT9312 at 400 and 800 ppm pCO₂ (**significant_only**; 419 / 188 genes).
   Not a coculture-vs-axenic contrast: MIT1002 24 h / 48 h vs 12 h in coculture
   (growth_phase treatment); 8 MarRef-Alteromonas glucose-addition proteomics
   (16 or 54 proteins).

4. **Researcher asked "what about proteomics?"** →
   `list_experiments(publication_dois=["10.1101/2025.11.24.690089"])` → **10**
   experiments, of which 8 are **per-arm N-starvation time courses**
   (starvation vs. that arm's own exponential phase), `coculture_partner: null`
   (see `gaps_and_friction.md`):
   | organism | omics | arm | timepoints (growth phase) | genes |
   |---|---|---|---|---|
   | MED4 | proteomics | coculture | d18, d31, d60, d89, d60+89 (all nutrient_limited) | 1424 |
   | MED4 | proteomics | axenic | d14 (nutrient_limited), **d31 (death), d89 (death)** | 1424 |
   | MED4 | RNA-seq | coculture | d18, d31, d60, d89, d60+89 | 1849 |
   | MED4 | RNA-seq | axenic | d14, d60+89 | 1849 |
   | HOT1A3 | proteomics | coculture | d18, d31, d60, d89, d60+89 | 2225 |
   | HOT1A3 | proteomics | axenic | d18 (0 significant), d31 | 2225 |
   | HOT1A3 | RNA-seq | coculture | d18, d31, d60, d89, d60+89 | 3947 |
   | HOT1A3 | RNA-seq | axenic | d18, d31, d60+89 | 3947 |

   Structural facts `[KG]`: (a) these are *within-arm* contrasts, so
   coculture-vs-axenic can only be read by comparing two arms' responses, and the
   axenic and coculture timepoints only partly match (MED4 protein: d31 and d89
   are shared, but axenic MED4 is in **death** phase at both); (b) they extend
   the window to **days 60–89**, when coculture MED4 is surviving long after
   the medium's N ran out, which is the phase where cross-fed N is the only N
   supply `[interpretation]`.

5. **`list_experiments(organism="Prochlorococcus", omics_type=["PROTEOMICS"])`**
   → 16. Beyond Weissberg 2025: MED4 and SS120 in coculture with Alteromonas,
   +glucose vs. no glucose, light and dark (10.1128/spectrum.03275-22; 327 / 930
   proteins), a carbon-addition contrast, not a coculture contrast. SS120
   azaserine (N-limitation proxy) vs. control, axenic (10.1128/mSystems.00008-17;
   significant_only, 362 proteins). Pi-limitation iTRAQ (MIT9312, NATL2A, SS120)
   and light iTRAQ (MED4) are out of scope.

6. **Gene inventories (keyword search, `genes_by_function`, min_quality 2).**
   MED4 N-import routes `[KG]`: ammonium `amt1` PMM0263; urea `urtABCDE`
   PMM0970-0974 + urease `ureABC`/`DEFG` PMM0963-0969; cyanate `cynABD`
   PMM0370-0372 + cyanase `cynS` PMM0373; peptides `dppA/B/C` PMM1049/1048/0421 +
   `ddpD` PMM0192; glutamate `gltS` PMM0628. N control/assimilation: `ntcA`
   PMM0246, `glnB` PMM1463, `pipX` PMM0393, `glnA` PMM0920, `glsF` PMM1512. No
   nitrate/nitrite assimilation genes. HOT1A3 (first pass, keyword only):
   deaminases/ammonia-lyases `hutH` ACZ81_04180, `sdaA` ACZ81_10105, `ilvA`
   ACZ81_19590; glutamate dehydrogenases `gdhA` ACZ81_09410, `gdhB` ACZ81_10240;
   allantoinase `puuE` ACZ81_07815; amino-acid exporters (LysE/ArgO:
   ACZ81_11480, ACZ81_10440, ACZ81_00690); its own `amtB` ACZ81_01830 and
   cyanase `cynS` ACZ81_07385. **No urease or arginase hit** (keyword search,
   not proof of absence).

7. **Coverage check: protein detection of the MED4 N genes**
   (`differential_expression_by_gene`, 12 locus tags x the two MED4 proteomics
   time courses). All 12 detected in both arms. **Disclosure, data seen before
   the framing was written:** this call returned fold changes. In the coculture
   arm at d60/d89, `cynA`/`cynS` are the top-ranked up proteins (log2FC
   3.8-4.7, ranks 1-4), above `amt1` (~2.3), `urtA` (~2.5), `dppA` (~1.9) and
   `ureC` (1.4-1.8); `gltS` and `glsF` not significant. Axenic d14: `glnA` 2.12,
   `cynA` 2.09, `ntcA` 1.87, `cynS` 1.30 significant; `amt1` 0.27 and `urtA` 0.82
   not significant. Consequence: any cyanate-specific statement written from here
   is post hoc, not a prediction. The pre-registered hypothesis is taken from the
   anchor paper's abstract instead (item 9).

   **Every value seen** (protein log2FC from the KG; `*` = `significant_*`; ns = not
   significant). Recorded in full so the blind/not-blind boundary in `proposal.md` is checkable:

   | gene | locus | coc d18 | coc d31 | coc d60 | coc d89 | ax d14 | ax d31 (death) | ax d89 (death) |
   |---|---|---|---|---|---|---|---|---|
   | glnA | PMM0920 | 2.55* | 2.95* | 2.57* | 2.22* | 2.12* | 1.38* | 2.53* |
   | ntcA | PMM0246 | 1.76* | 2.23* | 1.34* | 1.17* | 1.87* | 3.59* | 2.68* |
   | glnB | PMM1463 | 1.35* | 2.11* | 3.00* | 3.30* | 1.27* | 1.61* | 1.33* |
   | amt1 | PMM0263 | 0.28 ns | 1.04* | 2.33* | 2.28* | 0.27 ns | 0.65 ns | 1.01* |
   | urtA | PMM0970 | 1.67* | 2.27* | 2.48* | 2.48* | 0.82 ns | −1.45* (down) | −0.78 ns |
   | ureC | PMM0963 | 1.80* | 2.67* | 1.82* | 1.44* | 0.63 ns | 1.86* | 1.82* |
   | cynA | PMM0370 | 2.45* | 3.37* | 3.86* | 3.89* | 2.09* | 0.18 ns | 0.56 ns |
   | cynS | PMM0373 | 1.71* | 2.25* | 3.76* | 4.67* | 1.30* | 0.63 ns | 1.12* |
   | dppA | PMM1049 | 0.65 ns | 1.36* | 1.87* | 1.98* | 0.42 ns | −1.12* (down) | −0.76 ns |
   | dppC | PMM0421 | 0.49 ns | 0.71 ns | 1.69* | 0.96 ns | 0.12 ns | 2.42* | 1.95* |
   | gltS | PMM0628 | 0.12 ns | −0.25 ns | 0.34 ns | 0.60 ns | −1.06 ns | 0.04 ns | −0.08 ns |
   | glsF | PMM1512 | 0.67 ns | 0.95 ns | 0.53 ns | 0.45 ns | 0.21 ns | −0.40 ns | 0.03 ns |

   No RNA values were seen. No values were seen for any gene outside these 12, or for any
   experiment outside the two MED4 proteomics time courses.

8. **Transporter annotation (TCDB via `metabolites_by_gene`,
   `evidence_sources=['transport']`, `metabolite_elements=['N']`,
   `substrate_depth=['most_specific']`)**, exercised at the researcher's request:
   - `amt1` -> ammonia (+ methylamine, ethylamine, tetramethylammonium) via
     `tcdb:1.A.11`, score 0.8, resolved.
   - `urtA-E` -> urea (+ hydroxyurea, thiourea) via `tcdb:3.A.1.4.4/.5`, 0.6-0.8.
   - **`cynA/B/D` -> nitrate and nitrite** via `tcdb:3.A.1.16.1` ("four component
     nitrate/nitrite porter"); cyanate appears only on `cynB` via `3.A.1.16.2`
     ("bispecific cyanate/nitrite"). TCDB alone would read MED4's cyn system as a
     nitrate/nitrite importer, though MED4 has no nitrate/nitrite assimilation
     (item 6). The substrate identity for this system has to come from fusing
     annotations (co-located `cynS` cyanase, absence of `narB`/`nirA`), not from
     TCDB alone.
   - `dppA/B/C`, `ddpD` -> PepT family `tcdb:3.A.1.5`: peptides plus heme, EDTA,
     bradykinin, stachydrine (a broad family substrate list).
   - `gltS` PMM0628 -> **not_matched** at most_specific (its substrates are
     inherited-only, as `docs://analysis/metabolites` itself notes).
   - Organism-level reach is uninformative: `list_metabolites(elements=['N'],
     evidence_sources=['transport'])` gives 510 N-metabolites for MED4 and
     508-510 for every listed organism (ABC-superfamily inheritance).
   - BRITE transporters tree, MED4: 57 genes in 23 level-2 terms, all
     `family_inferred` via eggNOG. **Correction (2026-10-07, methods pilot step 1):** this
     call used `genes_by_ontology`'s default `min_gene_set_size=5`, which silently drops small
     terms. With `min_gene_set_size=1, max_gene_set_size=None` the BRITE transporters tree holds
     **86** MED4 genes (87 rows). The 57 was an artefact of the default.

9. **The anchor paper's stated mechanism** (`list_publications`, 10.1101/2025.11.24.690089
   abstract) `[KG]`: Alteromonas "functions as a key nitrogen recycler, providing a
   continuous, albeit low-level, supply of bioavailable NH4+ ... through the
   remineralization of organic matter"; *Prochlorococcus* "strongly upregulates
   high-affinity N-scavenging pathways". The other three papers' abstracts do not
   name an N compound.

10. **MCP docs (the researcher asked whether the updated assets are useful).**
    Read `docs://index`, `docs://analysis/metabolites`, `docs://ontologies/tcdb`.
    What they bear on directly:
    - Track A "Cross-feeding bridge" is a ready recipe for this question shape,
      with three named confounders: currency metabolites, family-level transport
      breadth (use `most_specific` for cross-feeding inference), and **no
      transport direction** (TCDB can't say import vs. export, so annotation gives
      "compatible with", never "confirmed").
    - The **metabolism arm is permanently undirected** ("involved in", never
      "produces"), so the KG cannot say HOT1A3's deaminases *release* NH4+.
      Direction comes from enzyme class (lyase/deaminase) as `[interpretation]`
      plus DE direction.
    - Confirms there are no N-stress metabolomics experiments `[gap]`.
    - Explains `gltS` falling out at most_specific (inherited-only), so the
      candidate-set rule must say how inherited-only genes are handled.

11. **N-compound class coverage of MED4 transport annotation**
    (`genes_by_metabolite`, MED4, `evidence_sources=['transport']`, 21
    representative N compounds, summary). 347 rows, of which 297 are inherited.
    | class | compounds | most_specific rows | inherited rows | note |
    |---|---|---|---|---|
    | ammonium | ammonia | 6 | 1 | `amt1` |
    | urea | urea | 10 | 20 | `urtA-E` |
    | cyanate / nitrite / nitrate | cyanate, nitrite, nitrate | 2 / 6 / 6 | 23 / 23 / 24 | cyn system, bispecific family |
    | amino acids | Glu, Gly, Ala, Arg, Gln, Leu | 0, 0, 0, 0, 1, 3 | 4-25 each | inherited mainly via `tcdb:3.A.1` on non-importers (`sufC`, `tolC`, `uvrA`, `minD`, `lptB`, `ccmA`) |
    | amines / polyamines | putrescine, spermidine, methylamine | 1, 0, 1 | 25, 27, 4 | same pattern |
    | osmolytes | betaine, taurine | 0, 0 | 23, 23 | same pattern |
    | nucleobases / nucleosides | adenine, uracil, thymidine, cytidine, adenosine | 4, 4, 3, 3, 0 | 3, 0, 0, 0, 23 | most_specific via `2.A.1` MFS / `2.A.7` DMT on 3-4 genes |
    Also: non-transporter genes carry TCDB attachments (`fadD`, `acs`, `speE`,
    `tsf`, `ktrA`). Organic-N classes other than urea and peptides are reachable
    only through weak annotation `[gap]`. That is not evidence MED4 lacks such
    importers.

12. **TCDB annotation trust for MED4 genome-wide** (`genes_by_ontology`, tcdb,
    level 1, summary): 356 genes / 441 gene x subclass rows; evidence homology 353
    / family_inferred 88; `evidence_score` median 0.2 (min 0, max 1). Per
    `docs://analysis/annotation_evidence`: rank by `evidence_score`, never
    threshold except via `min_evidence_score`; 0 = uncorroborated, not absent.

13. **Round-1 transport-system reconstruction exists** in
    `analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/`
    (`01_enumerate_transporters.py` ... `06_build_parts_list.py`; grouping by
    consecutive locus + same strand + shared role/substrate, Pfam-based subunit
    roles). MED4's peptide system is split across loci (PMM1048/1049, PMM0421,
    PMM0192), so contiguity alone won't group it. **Researcher (2026-10-06):
    round 1 predates the stack update (it ran on KG 0.1.0-alpha.6 / explorer
    alpha.4) and may need updating.** Its workarounds (Pfam roles parsed from
    `alternate_functional_descriptions`, flat TCDB `3.A.1` tags, the old
    evidence ladder that read eggNOG-only calls as curated) target gaps the
    alpha.7 / explorer alpha.5 stack may have closed (TCDB `attachment_depth`,
    `transport_substrate_resolution`, trust axes). **Decision:** round-1 scripts
    are design input, not imported code; the methods milestone re-implements on
    the current API and records, per round-1 workaround, whether it is still
    needed.

14. **Domain annotation of the MED4 N transporters** (`gene_ontology_terms`, Pfam; and TCDB
    verbose), asked by the researcher ("should transport system analysis look at domain info?").
    Pfam (16 rows, 14 `curated`): `cynA` PF13379 NMT1-like (+ PF09084 NMT1/THI5,
    family_inferred); `cynB` PF00528 BPD permease; `cynD` PF00005 ABC; `urtA` PF13433
    periplasmic binding; `urtB` PF02653 branched-chain AA permease; `urtD` PF00005 + PF12399
    branched-chain AA ABC; `dppA` PF00496 SBP family 5; `dppB` PF00528 + PF19300; `dppC` PF00528;
    `ddpD` PF00005 + PF08352 oligopeptide C-term; `amt1` PF00909 Amt; `gltS` PF03616.
    TCDB verbose (12 rows): **10 `family_inferred` (eggNOG only), 2 `homology`** (`amt1` 0.8,
    diamond identity 80.7%, pfam/go corroborated; `gltS` 0.4, identity 31.8%, uncorroborated).
    `cynA`: 3.A.1.16.1/.2 at 0.6 with `pfam_support` uncorroborated, plus 3.A.1.17.3/.6 ThiXYZ
    (hydroxymethylpyrimidine) at 0.4. `cynB`/`cynD`: 0.8, corroborated. `urtA`: 0.6,
    uncorroborated. `dppA`: 0.8, corroborated.

15. **Neighbourhoods of the cyn and urt systems** (`gene_neighbors`, anchors PMM0371 and PMM0972,
    window 6), from the researcher's question about recruiting neighbours by domain or
    functional annotation. cyn: `cynA` PMM0370 → `cynB` PMM0371 → `cynD` PMM0372 → `cynS`
    PMM0373, all + strand, then `tatA` PMM0374 on −. Upstream PMM0369 ("conserved hypothetical",
    +); PMM1831–1834 hypotheticals on −. urt: `ureD` PMM0966 on **−**, `ureE`/`F`/`G`
    PMM0967–0969 on +, `urtA`–`E` PMM0970–0974 on +, then hypotheticals PMM1919/1921 on −,
    PMM1922 and PMM0975 (DUF2862) on +. `bp_gap` in this tool is the distance to the anchor
    (it includes genes in between), not the adjacent-gene gap.

16. **Controls (researcher, 2026-10-07: "what are we using for positive and negative controls?
    should we add P or S transporters?").**
    `list_experiments(organism="MED4", treatment_type=["nitrogen"])` → 8. Beyond the 4 anchor
    sets: Tolonen 2006 (10.1038/msb4100087; microarray, axenic, all_detected 1697) growth on
    cyanate as sole N (20 up / 23 down), growth on urea as sole N (18 / 14), N deprivation 0–48 h
    (6 timepoints, `acute_stress`); Read 2017 (10.1038/ismej.2017.88; RNA-seq, axenic,
    filtered_subset "top 50% of genes by expression level", ~850/timepoint) N-depleted 3/12/24 h.
    No values pulled. Non-N import systems from `genes_by_function` (keyword):
    `pstS` PMM0710, `pstC/A/B` PMM0723–0725, `phnC/D/E` PMM0671–0673, `sul1` PMM0644, `sul3`
    PMM0214, `citT` PMM0083 (Na/K/sulfate DASS), `futB` PMM0489, `futC` PMM0803, `mntC` PMM0601,
    `lraI` PMM1032, `sbtA` PMM0213; P-regulon marker `phoH` PMM1284.

## Clarifying exchange

- **Scope (2026-10-06):** offered (a) the N-limited MED4 + HOT1A3 system only,
  (b) that system as the anchor with the other pairs as a check, or (c) all pairs
  weighted equally. **Researcher chose (b): anchor + other pairs as check.**
  Consequence: the framing needs an explicit rule for comparing across experiments
  that differ in design (table_scope, growth phase, single contrast vs. time
  course).
- **Folder name:** first `2026-10-06-alteromonas_to_pro_n_cross_feeding`; renamed (before any commit) to `2026-10-06-pro_n_import_coculture` after the consumer/producer split. Sibling analyses planned: `..._alteromonas_n_release_coculture`, `..._n_cross_feeding_contrast`.
- **Proteomics:** raised by the researcher after the scope choice; see
  grounding item 4.
- **Role of the per-arm starvation time courses (2026-10-06):** offered (a) main
  evidence for the late window, (b) supporting only (protein confirmation of RNA
  calls), (c) arm-minus-arm difference at matched days. **Researcher chose (a):
  main evidence, late window.** Which N-uptake systems *Prochlorococcus* keeps
  elevated at days 60–89 in coculture, read with the Alteromonas N-release
  proteins from the same cultures. The axenic arm is used only while it is alive
  (MED4 d14; HOT1A3 d18/d31) as the plain-N-starvation reference. The direct
  coculture-vs-axenic RNA-seq (Weissberg d11/d18, the 2016 pairs, Biller) becomes
  the cross-check. Rejected (c) because the only matched MED4 protein days (31,
  89) find the axenic culture in death phase.
- **Approach (2026-10-06):** offered A (two-sided evidence table per candidate
  compound), B (pathway enrichment), C (consumer side only). **Researcher chose A.**
- **Transporter annotation (2026-10-06):** the researcher asked that the analysis
  exercise the KG's transporter annotation, so the candidate set is built from
  TCDB/BRITE + the gene->metabolite transport links, not keyword search (item 8).

- **Researcher's four design points (2026-10-06), raised on design part 1:**
  1. *Compound classes (amino acids, nucleotides...)*: not covered by the
     draft rule (grounding item 11). **Decision:** candidates organised by N
     compound class (ammonium, urea, cyanate, nitrate/nitrite, amino acids,
     peptides, nucleobases/nucleosides, amines/polyamines, osmolytes); every
     class is reported with its evidence strength, none silently dropped.
  2. *Separate fresh analysis for Alteromonas, then contrast.* **Decision:**
     this analysis = *Prochlorococcus* import side only; a new analysis = the
     Alteromonas release/production side, planned on its own; a short third
     analysis contrasts the two. The methods built here are organism-agnostic
     so the Alteromonas analysis reuses them; revisions there are versioned, and
     the contrast checks version compatibility ("2 analysis (A) but with
     reuse/revising").
  3. *Annotation confidence scores.* **Decision:** rank and tier, never
     threshold: high = homology + most_specific + passes the "MED4 can use it"
     check; medium = most_specific but family_inferred or low score; low =
     inherited-only. Claims rest on high; lower tiers as a sensitivity read.
  4. *Multi-gene transport systems.* **Decision:** the unit is the system
     (reconstructed from neighbourhood + shared TCDB family/role; round-1
     method as design input, re-implemented on the current stack); the substrate-binding subunit's call is preferred and
     resolved by the "can MED4 use it" check; system expression = N/M subunits
     significant + median log2FC, with the substrate-binding protein shown
     separately.
- **Design part 1 approved (2026-10-06):** consumer-side question; transport systems as the unit with N-compound classes and confidence tiers; organism-agnostic methods; ammonium hypothesis from the anchor paper, cyanate disclosed as seen-before-lock.
- **Consequence for the approach:** with the producer side moved to its own
  analysis, this analysis is consumer-side. The earlier rejection of
  "consumer side only" (it can't tell fed from hungry) is resolved by the
  split: the fed/hungry distinction is settled at the contrast. This analysis
  still reads each import system against the plain-N-starvation pattern
  (axenic d14), so it reports which routes stand out beyond general N hunger.

- **Transport systems are built per strain, not mapped by orthologs (researcher, 2026-10-07).**
  The draft part 2 mapped the cross-check strains through KG ortholog groups.
  Researcher: transport systems are identified separately for each strain.
  **Decision:** the organism-agnostic method runs on each strain's own genome
  (MED4 anchor; MIT9313 and NATL2A for the cross-check experiments), giving
  per-strain systems, classes, tiers and expected-negatives. The cross-experiment
  comparison is at the compound-class level, so no gene-to-gene mapping is
  needed. Ortholog groups are not used in the main line. Optional QC only:
  flag ortholog-group members, built separately per strain, that land in
  different classes or tiers (annotation inconsistency between genomes).

- **Purpose of the analysis (researcher, 2026-10-07):** the anchor preprint (Weissberg et al. 2025)
  is the researcher's own and won't be published as is; this and the other analyses build a more
  comprehensive rewrite. The preprint's ammonium conclusion becomes a prior interpretation to
  re-examine; `paper.md` is draft material for the rewrite.

- **No preselected classes, no prefiltering (researcher, 2026-10-07):** "surface what we find and
  then work through the findings". **Decision:** the methods milestone emits every N-containing
  substrate per system with flag columns (depth, evidence, score, `can_use`,
  `likely_transporter`); nothing is dropped. Class groupings are agreed at the methods decide
  gate from annotation only, before expression is pulled, so the blind predictions stay blind.
  The critic's nitrate/nitrite fix survives as an interpretation rule (a `can_use = False`
  substrate can't support a claim), not a filter.

- **Domain info (researcher, 2026-10-07):** Pfam domains give subunit roles (cleanly, mostly
  curated) and role completeness, but not substrates (urea system domains read as branched-chain
  amino acids; NMT1/THI5 is shared with thiamine-precursor binders), so domain-implied substrates
  are a hint column only. The check showed that a gene-level "TCDB homology = high tier" rule
  would favour `amt1` (direct hit) over every ABC system (eggNOG-only) for annotation-pipeline
  reasons. **Decision:** the tier becomes a system-level evidence profile; boundaries set at the
  methods decide gate from annotation only; fixed principle: no systematic penalty on
  multi-subunit ABC systems vs. single carriers.

- **Neighbour recruitment (researcher, 2026-10-07):** "can neighbouring genes be added to the
  transport system based on their relevant domains? what about functional annotation?"
  **Decision:** yes, as two kinds kept separate. *Missing subunits* (transporter-role Pfam
  domain or BRITE transporter KO, no TCDB call) join the system and count toward its readout.
  *Linked enzymes* (functional annotation: KO/EC, Cyanorak role, product name flagged soft) are
  attached, not merged: they upgrade `can_use` to `co-located` and get a separate readout, never
  pooled into the import signal. Opposite-strand genes inside a run are flagged, not auto-added.
  What joins is agreed at the methods decide gate from annotation only (grounding item 15).

- **Controls (researcher chose "both", 2026-10-07):** (1) positive calibration: Tolonen
  growth-on-cyanate / growth-on-urea / N-deprivation + Read N-depleted, giving known-substrate
  signatures and an independent plain-starvation fingerprint. A pre-registered specificity check
  decides whether the consumer side may name a compound at all. (2) Negative reference: non-N
  import systems (P, phosphonate, S, Fe, Mn/Zn, bicarbonate) built by the same method, adding a
  third condition to "stands out" and expected-negative 3, with two pre-registered readings if one
  stands out.

- **Output shape and scoring (researcher, 2026-10-07):** "final conclusion will be: these systems
  have evidence for elevated expression; here is corroborating evidence ... how do we score them?
  rank?" **Decision:** §3.7: three layers per system (primary label, corroborating lines,
  annotation confidence) plus "against" flags; no composite score; ordering by label → fraction of
  applicable supporting lines (denominator shown) → late protein percentile. Scoped critic pass
  over §3.7 → 1 Blocker + 6 Concerns (`proposal_critical_review.md`, "Delta pass 2"). §3.7
  rewritten: no ratio and no ranking on corroboration (ordering = label → late protein
  percentile); four independent lines with explicit platform, timepoint and against rules; flags
  separate; non-blind cells disclosed. *(The first draft's "corroboration lines fixed before any
  data" was inaccurate: some cells for the 12 peeked genes were already visible. Corrected.)*

## Rejected alternatives

- **Pathway enrichment as the main method (approach B):** names processes, not
  compounds, and can't separate a compound-specific signal from N starvation
  switching every import route on. Rejected 2026-10-06.
- **Consumer side only (approach C):** can't tell "fed X" from "hungry".
  Rejected 2026-10-06, then **superseded the same day** by the researcher's
  split into separate Pro-side and Alteromonas-side analyses (see clarifying
  exchange). The objection is answered at the contrast stage.
- **Arm-minus-arm difference at matched days:** the only matched MED4 protein
  days find the axenic culture in death phase. Rejected 2026-10-06.
- **Mapping cross-check strains to MED4 systems via ortholog groups:** systems
  are strain-specific constructions; the comparison needs class-level agreement,
  not gene identity. Rejected 2026-10-07 (researcher).
- **Predefined compound-class list and dropping substrates that fail the "can use" check:**
  hides what the annotation says and fixes groupings before the annotation is seen. Rejected
  2026-10-07 (researcher); replaced by flags plus groupings agreed at the methods decide gate.
- **Pooling linked enzymes (cyanase, urease) into the system's import readout:** they respond to
  N stress in their own right, so pooling would mix assimilation with import. Rejected
  2026-10-07; they get a separate readout.
- **Ordering by fraction of supporting corroboration lines:** structurally favours systems with
  few applicable lines (one-gene carriers, incl. the hypothesis gene) and ignores *against*.
  Rejected 2026-10-07 after the second delta pass.
- **A composite evidence score (weighted sum of lines):** weights would be set after seeing
  the data, the lines are on different platforms and scales, and a single number hides which
  line carries the claim. Rejected 2026-10-07; replaced by the §3.7 ordering.

## Plan-phase close

- **Self-review (2026-10-07):** widened the disclosure from cyanate to all 12 peeked genes;
  defined "rank percentile" exactly; stated that the "can use" check is trivial for peptides and
  amino acids; added a tie rule; removed a hidden score threshold from the medium tier.
- **Proposal critic (2026-10-07, interpretation only):** no Blockers, 8 Concerns, 2 Notes.
  All addressed in `proposal.md`; findings and dispositions in `proposal_critical_review.md`.
  Spot-check done during dispositioning: `list_experiments(verbose=True)` confirms both
  `10.1038/ismej.2016.70_..._med4_rnaseq` (Pro99, 10 µmol photons, Rockhopper) and
  `10.1038/ismej.2016.82_..._natl2a_rnaseq` (Pro99, 30 µmol photons, DESeq2) are N-replete,
  exponential `[KG]`.
- **Controls added after the critic (2026-10-07):** unlike the earlier post-critic changes, this
  one *adds* claims-bearing structure: a new condition on "stands out", a new expected-negative,
  and a calibration gate that can withhold compound naming. Run a delta critic pass over §2
  (calibration table), §3.3 (c), §3.4 (calibration) and §3.5 (expected-negative 3) before the
  Plan commit, with the rest of the proposal as already reviewed. **Done:** delta pass returned no Blockers, 5 Concerns,
  2 Notes; all fixed (`proposal_critical_review.md`, "Delta pass").
- **Tier rule changed again after the critic (2026-10-07, domain check):** the critic's pass
  reviewed a tier rule ("high = homology + most_specific") that grounding item 14 then showed
  would bias toward the hypothesis gene. It is replaced by a system-level profile with boundaries
  set at the methods decide gate. Like the flags change, this removes a rule rather than adding a
  claim, and the critic's protections stand, so there's no second pass. The methods-milestone
  critic will see the tiers as constructed.
- **No second critic pass after the flags-not-filters change (2026-10-07):** the change removes a
  filter and moves class grouping to the methods decide gate. It adds no claims, and every
  critic-requested protection survives (the `can_use = False` interpretation rule, expected-negative 1,
  the blind RNA predictions), so the critic's verdict still covers the proposal's claims. Recorded
  as a judgment call for watch-list item 2 (when does a change earn another pass?).
