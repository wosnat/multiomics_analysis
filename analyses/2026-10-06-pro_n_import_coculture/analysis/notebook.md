# Analysis milestone — notebook

*Owned by the main thread. Mechanical sections paste the coding subagent's run-manifest verbatim;
interpretive sections are written here with the researcher.*

## Context

The methods milestone (`3bfe263`, `d0ec245`, `c0b83ec`; `n_transport` v1.6.1) built, per strain,
the transport systems, tiers, linked enzymes, compound classes and dedicated/broad listings, with
no expression data. This milestone reads expression for the first time, following `proposal.md`
§3.2 "Expression read", §3.3 labels, §3.4 gates, §3.5 expected-negatives, §3.6 cross-experiment
rules and §3.7 output order. The trusted inputs are the methods tables listed in
`methods/notebook.md` "Decide-gate checklist".

## Co-define (agreed 2026-10-11)

**Unchanged from the proposal:**
- **Header block first:**
  - biology sanity gate (`glnA`, `ntcA`, `glnB`);
  - calibration C1–C4 (Tolonen cyanate/urea; Tolonen and Read N starvation) and the gate outcome;
  - P1/P2 (blind RNA predictions for `amt1`);
  - expected-negatives 1–3.
- **Main read:** MED4 per system, protein and RNA, coculture d60/d89 vs. axenic d14 reference.
  Measures are rank percentiles within each experiment × timepoint, and the source paper's
  significance calls. No new p-values.
- **Labels:** stands out / stands out with caveat / elevated, not standing out / not elevated,
  with criteria (a)–(c) as pre-registered.
- **Other reads:** corroborating lines, flags, the time-matched d18 vs d14 read, the N-replete
  controls and the calibration read.
- **Other strains:** up / not significant / down per class, on each strain's own systems.

**Decisions forced by the methods results (researcher, 2026-10-11):**
1. **Systems in the evidence table: High + Medium, flags shown.**
   - All High/Medium systems with any N listing, plus the non-N reference systems.
   - Efflux-annotated and known-false-positive systems stay as rows with their flag, but never
     represent a class.
   - Low systems stay in the data, not the table.
2. **Class-level labels only for classes with a dedicated system** ("A").
   - In MED4 these are ammonium (`amt1`), urea (`urt`), cyanate (`cyn`) and peptides (`dpp`).
   - Amino acids, polyamines, amino sugars and osmolytes have only broad listings (e.g. `sul1`/`sul3`
     for amino acids). They get "no dedicated system": their systems keep their own row labels,
     but the class is not named.
   - Researcher: "We will need to do some digging in the analysis, and for multi-class
     transporters this is premature." Class attribution for multi-class systems is an exploration
     item, not a pre-set rule.
3. **Linked-enzyme corroborating line: both kinds, minus the starvation markers.**
   - Neighbour-linked and function-linked enzymes both count, shown separately.
   - The sanity-gate markers `glnA`, `ntcA` and `glnB` are excluded, because they rise with any N
     starvation. For `amt1` this leaves `glsF` alone, which is noted.
   - This widens the proposal's "co-located" line to include function-linked enzymes. Recorded as
     a change agreed before expression was read.
4. **Genome-enzyme support (methods fig11): exploratory column only.**
   - Shown beside multi-class systems; not scored and not used for any label.
   - First, fix the Cysteine / L-Cysteine ID split (kegg C00736 vs C00097) with a stereo-generic
     equivalence in the analysis-side code, documented.

**Execution plan:**
- **Stage 1: data.** Pull every experiment in proposal §2 through `kg_fetch`. Per experiment ×
  timepoint, check:
  - the row count against `total_matching`;
  - `table_scope`;
  - the timepoint labels;
  - the share of negative log2FC (~40–55% for all-detected tables).

  Compute rank percentiles. An independent verifier spot-checks about 10 gene × experiment values
  through MCP without seeing the code (the API-misuse guard the researcher asked for at methods).
- **Stage 2: header block.** Sanity gate, C1–C4, P1/P2, expected-negatives. Shown to the
  researcher before stage 3; a failed sanity gate stops the milestone.
- **Stage 3: MED4 evidence table, labels, class labels, flags, exploratory column.**
- **Stage 4: other strains** (N-replete controls).
- **Then:** explore (multi-class digging), the analysis critic (data-integrity + interpretation,
  automatic), and the decide gate.
- **Agents:** the same coder subagent (TDD for the rank/label functions), a verifier (MCP only),
  and the main thread owning this notebook and all judgment.

## What I did

**Stage 1: data pull (2026-10-11).** `analysis/expr.py` v0.1.0, `scripts/s1_pull_de.py`, 12 toy
tests OK. Coder manifest summary:
- All 13 proposal §2 experiments were pulled through methods `kg_fetch.fetch`, one unpaged call
  each. In every slice, rows = `total_matching` = the `list_experiments` gene count, with 0
  duplicated rows. Output: `data/de_long.csv.gz` (52,863 rows), `qc_slices.csv`,
  `coverage_methods_universe.csv`, `checks_10.csv`.
- **Independent check:** 10 gene × experiment × timepoint values, collected by a verifier through
  MCP only, without seeing the code, match the pipeline exactly (log2FC, padj, status).
  NATL2A `amt1` PMN2A_1629 is not listed in Biller at any timepoint.
- **Coverage of methods High/Medium members:**
  - MED4 RNA tables: 103/103.
  - MED4 anchor protein: 82/103. The 21 missing include `glcH`, `sodX`, `evrB/C`, `mntB`, `kpsD`; none
    is a dedicated N-system member.
  - MIT9313: 167/171.
  - NATL2A Biller (filtered table): 11/111.
- **Table facts that shape the reads [KG]:**
  - **Pooled slice.** Each Weissberg time course also has a pooled "days 60+89" slice. It is kept
    flagged `is_pooled` and never used in per-day reads.
  - **Axenic reference days.** Axenic RNA has only d14 and pooled d60+89. Axenic protein has d14
    (nutrient-limited), d31 and d89 (death).
  - **Stored significance includes a fold-change cutoff.** In the anchor and direct-contrast tables
    the stored significance applies |log2FC| ≥ 1 on top of padj < 0.05: the smallest |log2FC|
    among significant rows is ≈ 1.00. For example, 209 of 428 padj < 0.05 rows in coculture
    protein d60 are stored not_significant. Some stored-significant RNA rows have null padj
    (59 at coculture RNA d18). Per the proposal, "significant" = the stored call.
  - **Coarse padj.** Tolonen padj is only 0.01 or 1; Biller only 0.1 or 1.
- **Negative-share checks (sign sanity):**
  - The MED4 N-replete control (Aharonovich 2016, Rockhopper) is 82% negative, with log2FC from −15 to
    +12. Percentiles there carry little meaning. The proposal reads only up/ns/down from the
    controls, which stays usable.
  - MIT9313 controls: 70% / 67% negative.
  - Anchor coculture RNA: 56–59% negative (mild).
  - Tolonen N deprivation: 56–76% negative at most timepoints.

**Stage 2: header block (2026-10-11).** `scripts/s2_header_block.py`, 17 tests OK, no KG calls.
Where the proposal's wording left a rule open, every variant was computed
(`data/s2_outcomes.csv`).

## Results

### Header block [KG]

| Check | Outcome | Basis |
|---|---|---|
| Biology sanity gate (protein) | **pass** (strict and lenient) | `glnA`, `ntcA`, `glnB` significantly up in protein at axenic d14 and coculture d18/d31/d60/d89 (15/15 cells; percentile 0.90–1.00) |
| C1 cyanate calibration | **pass** | cyn median percentile 0.958 on cyanate |
| C2 urea calibration | **fail** | urt median 0.338 on urea |
| C3 specificity | **fail** | cyn: cyanate 0.958 vs urea 0.124 (+0.83, passes); urt: urea 0.338 vs cyanate 0.817 (−0.48, fails) |
| C4 Tolonen N deprivation 12–48 h | pass (any subunit) / fail (≥ half of subunits) | urt reaches only 2/5 subunits up at one timepoint (urtA, urtB) |
| C4 Read N-depleted 12–24 h | **fail** (both variants) | `amt1` stored not significant (log2FC +2.27/+2.26, filtered table) |
| P1 `amt1` RNA ≥ 0.90 at d60 and d89 | **fail** | 0.064 (d60), 0.656 (d89) |
| P2 `amt1` RNA ≥ median of urt + cyn | fail d60, pass d89 (both variants) | d60 0.064 vs 0.408; d89 0.656 vs 0.500 / 0.604 |
| Expected-negative 1 | **pass** | all 72 MED4 nitrate/nitrite rows `can_use` = no |
| Expected-negative 2, MED4 | **pass** | no N-import subunit up; many down (urtE −13.2, dppC −10.6, dppA −10.7, cynB −5.2; context cynS −13.4, ureC −4.6) in a table that is 82% negative |
| Expected-negative 2, MIT9313 0.5e6 | **fail** | `natF` PMT0897 up (+1.57); `natG` PMT0896 down (−3.62) in the same table |
| Expected-negative 2, MIT9313 5e6 | pass | all N-import subunits ns |
| Expected-negative 2, NATL2A | pass (can only fail) | none of 15 N-import subunits listed |
| Expected-negative 3 (non-N) | **pass** | no non-N group meets (a)+(b) under either variant; `sbtA` up at d60 only |

**Pre-computed (a)/(b) for the MED4 dedicated N systems (not yet labels):**

| System | Protein median percentile d60 / d89 | Axenic d14 | Subunits up d60 / d89 | RNA median log2FC d60 / d89 | (b) |
|---|---|---|---|---|---|
| amt1 | 0.983 / 0.976 | 0.663 | 1/1 / 1/1 | −1.54 / +0.13 | pass |
| urt | 0.935 / 0.934 | 0.787 | 4/5 / 4/5 | −0.27 / −0.57 | pass |
| cyn | 0.998 / 0.996 | 0.989 | 3/3 / 3/3 | −0.30 / +1.09 | fail (margin +0.01) |
| dpp | 0.886 / 0.819 | 0.539 | 2/4 / 1/4 | −0.15 / +0.07 | fail |

All four systems fail (a) under both variants for one reason: the RNA clause (RNA median log2FC
> 0 at both days) fails at d60.

### Surprise: protein and RNA disagree for the N-starvation markers
The sanity markers are up in protein at every coculture day. In coculture RNA they are
**down at every day**: log2FC −0.46 to −2.58, significantly down in 5 of 12 cells. In axenic d14
RNA, `glnA` and `ntcA` are up (+3.36, +3.35). The criterion-(a) RNA clause would therefore reject
the positive controls themselves. `[interpretation]` Possible readings:
- transcripts for these genes fall in prolonged coculture while the proteins persist or
  accumulate;
- normalisation to a shrinking or shifting transcript pool;
- a coculture-specific RNA effect.

The KG can't separate these.

## Surprises

### In-depth exploration E1–E6 (descriptive; no labels) [KG]

Scripts `scripts/e1…e6_*.py`; 29 tests OK; figures in `analysis/figures/e*_*.png`; tables in
`data/explore/`.

**E1. Time courses: the whole N regulon is high in protein from coculture d18.** System median
protein percentiles, d18 → d89:

| System | Coculture d18 → d89 | Axenic d14 |
|---|---|---|
| cyn | 0.998 → 0.996 | 0.989 |
| urt | 0.987 → 0.934 | 0.787 |
| markers | 0.988 → 0.935 | — |
| dpp | 0.874 → 0.819 | 0.539 |
| amt1 | **0.723 → 0.924 → 0.983 → 0.976** | 0.663 |
| non-N systems | 0.39–0.67 | — |

`amt1` is the only N system that climbs across the coculture days; it is also the lowest at d18.
Urease `ureA/B/C`, `ureG` and `cynS` are up at most coculture days. In RNA the picture is
different: the markers sit at about 0.05, and the N systems move between 0.06 and 0.94 with no
shared trend.

**E2. Protein–RNA concordance.**
- Genome-wide, Spearman ρ between protein and RNA log2FC is low: axenic d14 0.23; coculture d18
  −0.08, d31 0.10, d60 0.18, d89 0.21.
- "Protein up, RNA down" is **enriched in the N regulon**:
  - N regulon: 48–60% of genes at each coculture day, vs 4% at axenic d14;
  - all genes: 24–30%.
- Ribosomal proteins show the opposite pattern at d18/d31 (protein down, RNA up; 48/52 at d18).

**E3. Co-movement (≤ 7 protein / 5 RNA points per pair; coarse).**
- In protein, `amt1` minus the median of the urt + cyn subunits is −0.27 at d18, then about 0 at d31–d89:
  `amt1` catches up with the alternative-N systems rather than they falling back.
- cyn minus urt: +0.01 to +0.06.
- dpp minus the markers: −0.07 to −0.12 throughout.

**E4. Broad systems and their class enzymes.**
- The Cysteine fix (stereo-generic merge, C00736 ↔ C00097 and glutamate/alanine forms) cut
  zero-enzyme cells from 9 to 3 of 28.
- Amino-acid genome enzymes sit at median protein percentile 0.2–0.5 in late coculture, below
  axenic d14 (0.54–0.71).
- `sul1`/`sul3` are down (0.06–0.18).
- The highest broad systems in late coculture are:
  - `murJ` (lipid II flippase; 0.95/0.92 vs 0.36 axenic);
  - efflux PMM0954 (0.75/0.82) and PMM0561 (0.71/0.65);
  - PMM0704 (0.84/0.62);
  - `ktrAB` (0.77/0.75).

**E5. What marks late coculture protein.**
- 81 genes are in the top 10% at both d60 and d89 but not up at axenic d14.
- 14 of the 81 are Cyanorak Q (transport). They include `amt1`, `cynB`, `urtA/B/C`, `dppA`, the porin
  `som` PMM0709, `perM`, `mgtE`, `clc2`.
- Also in the set: outer-membrane/envelope export genes (`tolC`, `acrA`, `bamA`, `murJ`) and urease
  `ureB/C`.
- The RNA equivalent (49 genes) contains no N-regulon gene.

**E6. Controls and calibration in depth.**
- **Tolonen cyanate vs urea.** On cyanate the marker `glnA` is up (0.98, significant), with
  `glnB` at 0.91; on urea `glnA` is at 0.31 and `ntcA` at 0.002. Growth on cyanate is itself
  N-stressful in these data; growth on urea is not.
- **Tolonen N deprivation 0–48 h.** cyn, `urtA`, `amt1` (6 h, 24 h), `glnA/ntcA/glnB`, `glsF` and urease
  go up. **dpp is never significant.** `pstS`, `phnD`, `sul3` and `sbtA` go down.
- **MED4 N-replete control** (82% negative table). The N systems sit at the table's background:
  median percentile 0.47 vs non-N 0.46, with all-genes median log2FC −1.46. The N-gene "down" calls
  there are therefore not N-specific.
- **MIT9313 0.5e6 `natF` up.** A single subunit; `phnC` (non-N) is also up in the same table, and the
  5e6 inoculum shows nothing.

**Reading so far** `[interpretation]`. Alternatives are listed; this is not yet a conclusion.
1. **The import systems report N stress, not substrate.** Both calibrations show it: cyanate
   induces the markers along with urt, and urea induces nothing. Consistent with reading (i) of
   proposal §3.1.
2. **In protein, late coculture looks like full NtcA induction.** cyn, urt and the markers are
   maximal from d18. `amt1` is the exception: it rises from 0.72 to 0.98, so it joins late rather
   than leading.
   - Alternatives: slower `amt1` protein turnover; a later NtcA threshold for `amt1`; or
     ammonium-dependent post-translational regulation.
3. **dpp stands apart from acute starvation.** It never responds in Tolonen, sits at 0.54 in
   axenic d14, and stays at 0.82–0.89 throughout coculture.
   - Alternatives: a long-starvation (not acute) response; a stationary-phase programme; a
     partner-related signal.
   - It is the one N system elevated in coculture that the acute-starvation references don't
     predict. This is a lead for the evaluation milestone, not a finding.
4. **The RNA discordance comes largely from the reference.** See E7.

**Correction to point 3 (2026-10-11, researcher: "dpp — how is it in RNA vs protein. Tolonen is
RNA").** Point 3 compared coculture *protein* with Tolonen *RNA* (microarray) and with axenic d14
*protein*. Like with like, from `data/explore/e1_gene_slice_long.csv` [KG]:

| Subunit | Tolonen N-deprivation RNA 0–48 h | Axenic d14 RNA | Coculture RNA d18/d31/d60/d89 | Axenic d14 protein | Coculture protein d18/d31/d60/d89 |
|---|---|---|---|---|---|
| dppA PMM1049 | never significant | 0.93 (up) | 0.60 / 0.76 / 0.75 / 0.76 | 0.76 | 0.91 / 0.96↑ / 0.97↑ / 0.96↑ |
| dppB PMM1048 | never significant | 0.92 (up) | 0.83 / 0.97↑ / 0.91 / 0.95↑ | 0.53 | 0.91 / 0.92 / 0.82 / 0.77 |
| dppC PMM0421 | never significant | 0.62 | 0.26 / 0.31 / 0.24 / 0.48 | 0.55 | 0.84 / 0.84 / 0.95↑ / 0.87 |
| ddpD PMM0192 | never significant | 0.62 | 0.47 / 0.18 / 0.09↓ / 0.28 | 0.43 | 0.55 / 0.21 / 0.08 / 0.16 |

**Revised reading** `[interpretation]`:
- **dpp is starvation-responsive, on a slower timescale.** The `dppB/dppA` locus is up in axenic
  d14 RNA (days of starvation), not within Tolonen's 48 h.
- **The axenic d14 protein lags.** `dppA` is 0.76 there and significantly up by coculture d31, so
  the protein rises after the RNA.
- **"Beyond what starvation predicts" is withdrawn.**
- **The parts disagree.** The cross-locus parts `dppC` and `ddpD` do not follow `dppB/dppA` (`ddpD`
  RNA goes down). Either the parts are regulated separately, or the methods cross-locus join
  (decision 4, `dpp` from three loci) groups pieces that do not act as one system. Flagged for the
  evaluation milestone.
- **Lesson.** Compare like with like (platform and omics layer) before calling a gene
  "unexplained by starvation".

**E7. The coculture exponential baseline** (`scripts/e7_baseline.py`, figure `e7_baseline`) [KG]:
- **d11 (exponential).** The same-study direct contrast (coculture vs axenic, RNA) puts the N
  regulon near the top: markers median 0.93, dedicated N systems 0.96 (5 up, 0 down). `glnA`
  +2.44, `ntcA` +2.40, `urtA` +2.53, `cynA` +3.11, `amt1` +1.39. Ribosomal proteins sit at 0.14.
- **d18 (nutrient-limited).** The same contrast reverses: markers 0.26, N systems 0.24 (0 up,
  6 down; `amt1` −2.14, `cynA` −2.19). Non-N systems rise to 0.68 (`pstS`, `phnD`, `sul3`, `mntB`,
  `sbtA` up) and ribosomal proteins to 0.88 (44 up).
- **The four RNA tables are not independent.** [anchor coculture d18 − anchor axenic d14] equals
  [direct contrast d18 − direct contrast d11] for every one of 1849 genes, to 1e-15. The stored
  contrasts are therefore algebraically linked: one fitted model over shared samples. This
  identity implies that the axenic arm the KG labels "day 14" in the anchor and the axenic arm
  inside the direct contrast's "day 18" are the same samples `[interpretation]`. The direct
  contrast adds no information beyond the anchor RNA tables except the exponential-phase
  comparison (d11). The proposal's "time-matched read" (coculture d18 vs axenic d14) *is* the
  direct contrast at d18.

`[interpretation]` In RNA, the coculture was already N-stressed relative to axenic during
exponential growth. Its "starvation vs own exponential" RNA series therefore starts from a raised
N-regulon baseline, which explains much of the "protein up, RNA down" pattern. Two consequences:
- Coculture RNA log2FC for N genes **cannot** be read as "not induced". It is induced relative to
  axenic, but already at d11.
- By d18 the order reverses: the N regulon is lower in coculture than axenic, while P/S/Fe
  transporters and ribosomal proteins are higher. One reading is that coculture cells are less
  N-stressed than axenic ones at the nutrient-limited stage, i.e. partial relief (reading (ii)).
  Alternatives: the axenic culture is further into starvation or decline; or the coculture
  reallocates to other limitations (P, S, Fe) as N becomes less limiting relative to them.

The exponential-phase difference is plausibly competition with *Alteromonas* for N early on;
the KG can't test that.

**Correction to the E7 reading (2026-10-11).**

*Researcher's account of the culture states:*
- **Axenic d11:** exponential, beginning to run out of N.
- **Axenic "d14"** (sampled about day 14 and paired with coculture d18 as the same stage in the
  direct contrast): full decline, most cells dying, very starved.
- **Coculture:** the physiological state at these points is unknown.

This also explains the E7 identity. The axenic arm of the direct contrast's "d18" *is* the anchor's
axenic d14 sample; the KG's per-contrast day label simplifies a per-arm sampling day (see
`gaps_and_friction.md`).

*Revised reading* `[interpretation]`:
- **d11.** Both cultures are in exponential growth. The axenic culture is starting to run out of N,
  yet the coculture's N regulon is still higher than axenic. The coculture was at least as
  N-stressed as an axenic culture nearing N exhaustion.
- **d18 vs axenic d14.** The comparison is with a dying, very starved axenic culture. The coculture's
  lower N regulon and higher ribosomal and P/S/Fe transporter RNA say the coculture is *less starved
  than a dying axenic culture*. That is all the comparison can say; it can't separate partial N relief
  from "not dying". The coculture's own state is unknown, so neither reading is preferred.

**Consequence for the plan.** The proposal treated axenic d14 as the *early* starvation reference
("beyond early axenic starvation", the 0.10 margin in label (b), the "also up in early axenic
starvation" flag). It is in fact a deep-starvation, declining culture. When classification is
revisited:
- the label wording and the meaning of the margin must change (a system above axenic d14 is above
  a *dying* starved culture);
- the "early" flag needs a different reference, or a new name.

Recorded here for the decision on labels, not acted on yet.

**E9. Published co-expression clusters as empirical gene sets** (researcher suggestion;
`scripts/e9_clusters.py`, figures `e9_cluster_profiles`, `e9_anchor_cluster_read`) [KG]:
- **MED4 Tolonen k-means (9 clusters, 410 genes).** c1 (`cynA`, `glnA`, `urtA` + 2) and c2 (16, including
  `ntcA`, `glnB`, `cynB`) rise strongly within 3–6 h: this is the **N-starvation stimulon**. c4/c5
  (86/73) rise mildly. c6–c9 fall: protein synthesis (c6/c7) and photosynthesis (c8/c9).
  - `amt1` is in c5; `urtB`, `cynD` and `ureA` in c4.
  - **No dpp subunit, no `cynS`, no `urtC/D/E` and no broad N system is in any cluster.** So
    whether `dppA/dppB` co-respond with the NtcA genes can't be tested this way.
- **Cluster read on the anchor, protein (median percentile).**
  - c1/c2 are at 0.98–1.00 already in axenic d14 and stay at 0.91–1.00 through coculture d89:
    the coculture's N-stimulon protein is as high as in a late-decline axenic culture.
  - The down clusters keep falling in coculture: c7 0.12–0.35, c8 0.40 → 0.15 (photosynthesis).
  - RNA repeats the baseline effect: c1/c2 at 0.03–0.29 in coculture vs 0.97–0.99 in axenic d14;
    direct contrast 0.99 at d11 → 0.07–0.10 at d18.
- **MED4 iron clusters (Thompson 2011).** The iron-stress-up cluster c19 (59 genes; 20 detected in
  protein) is at 0.77 / 0.71 at coculture d60/d89 vs 0.52 at axenic d14; RNA 0.72 / 0.73. Note that
  `cynA` belongs to c19 too.
- **MIT9313 clusters.** c1 = `ntcA`, `urtA`, `focA`, `nirA` (+3). `amt1` and `glnA` are in c2; urease in
  c3 (up, late); `natF`, `agcS`, `proX` and `glnB` in c4 (down, late). dpp is not clustered here either.

`[interpretation]`
- Using a published stimulon instead of three hand-picked markers gives the same picture. The
  late-coculture N response in protein is at the level of a late-decline axenic culture, with no
  sign of damping.
- **Iron cluster c19 is a first hint of secondary Fe stress late in coculture**: modestly raised in
  protein (+0.2–0.25 over axenic d14) and RNA. It rests on 20 of 59 detected members, and overlaps
  the N set through `cynA`. This needs checking before it carries weight.
- The proposal's expected-negative 3 used `idiA2` alone for Fe; the cluster is a better reference.

**E10. All-systems status matrix** (researcher request; `scripts/e10_system_matrix.py`, page
`analysis/system_matrix.html`) [KG]:
- **Layout.** 80 rows: 73 High/Medium systems + 7 reference rows. Columns: coculture vs axenic
  (Aharonovich, direct contrast d11/d18), N starvation / other N sources (Tolonen deprivation 3–48 h,
  Read, Tolonen cyanate/urea), and this study's protein/RNA. Cell = system status from the stored
  significance calls (up / down / mixed / ns / n.d.). Rows are clustered on the median-percentile
  profile.
- **Top branch: the N-starvation response** (9 rows): `glnA`, `ntcA`, `glnB`, cyn, `amt1`, urease, urt,
  `cynS`, and ferritin [FP]. No other N system joins it.
- **Coculture-specific candidates (★)**, first pass, superseded by E14, which checks all axenic samples: up in cc protein at d60 and d89, not up at axenic d14 protein, and not up in Tolonen deprivation. There were 11 ★ + 1 ☆, including:
  - `som` PMM0709 porin (0.97/0.99 vs axenic 0.47);
  - `murJ` (0.95/0.92 vs 0.36);
  - `yrbG`;
  - dpp (passes on protein only; its RNA is up in axenic d14);
  - `devBCA`.

  Weaker candidates, already 0.75–0.95 in axenic d14: `tolC`, `acrA`, `bamA`, `perM`, `mgtE`,
  `clc2`.
- **Per class.** Within a class the systems disagree:
  - ammonium: only `amt1` is up;
  - peptides: only dpp is up of 11 systems;
  - amino acids: `murJ` up, `sul1/3` down.

**E11. Small follow-ups** (`scripts/e11_followups.py`):
- **Excess over the N-starvation stimulon is uninformative.** The stimulon sits at about 0.98 in
  every protein slice, so the maximum excess is about +0.02.
- **N-releasing enzymes.** Of 80 EC 3.4 / 3.5 / 4.3.1 genes, only `ureC`, `sppA` and `ispA` pass the
  coculture-specific filter, and all are already ≥ 0.88 in axenic d14. No organic-N degradation
  route is switched on beyond starvation.
- **N relief.** In protein, the protein-synthesis clusters climb partway back late in coculture
  (c7 0.12 → 0.35) while photosynthesis (c8) keeps falling (0.40 → 0.15).

`[interpretation]`
- What looks coculture-specific is mainly the **cell envelope**: porin, outer-membrane assembly,
  efflux and cell-wall synthesis, not N import.
- No organic-N route shows coordinated transporter + enzyme activity beyond starvation.
- Researcher scope note (2026-10-11): no new broad analysis here. A generic-stress score, pathway
  enrichment and a full N-relief analysis are left for a possible separate analysis.

**Refinement (researcher): "in axenic everything is faster. so day 14 is already late decline."**
- Axenic cultures move through exhaustion and decline faster than cocultures, so calendar days
  are not physiological stages.
- The proposal's "time-matched read" (coculture d18 vs axenic d14) is matched by day, not by stage:
  it pairs a late-decline axenic culture with a coculture in an unknown state.
- Any "duration-compatible" or "partner-early" call from that read must say so.

**E8. Tolonen MIT9313 calibration** (researcher: "tolonen also has 9313 experiments"; missed at
Plan, see `gaps_and_friction.md`). `scripts/e8_tolonen_mit9313.py`, figure `e8_tolonen_mit9313`,
descriptive only, no gate. Uses MIT9313's own systems [KG]:
- **Nitrite vs urea as sole N.** The nitrite system and urt are near the top on **both**
  substrates:

  | | Nitrite | Urea |
  |---|---|---|
  | `focA` | 1.000 | 0.999 |
  | `nirA` | 0.999 | 0.998 |
  | urt median | 0.982 | 0.992 |

  `ntcA` is 0.994 (significant) on nitrite and 0.960 on urea. The urease is **higher on nitrite**
  (`ureA/B/C` 0.95–0.98) than on urea (0.66–0.83). Applying the MED4 rules:
  - substrate-alone checks: both pass (`focA` on nitrite 0.9996; urt on urea 0.992);
  - specificity: both fail (differences +0.0004 and +0.010).
- **N deprivation 0–48 h.** `urtA` (from 3 h), `amt1`, `focA`, `nirA` and `ntcA` (from 6 h) and `glnA` (6–24 h) go
  up; urease only at 6 h; dpp, natFGH, agcS and proVWX never go up (natF, agcS and proX go down at 48 h).

`[interpretation]` **Two strains, three substrates, one pattern.** The import systems are induced as
a group whenever the N source is not ammonium (relative to ammonium-replete Pro99). This holds in
MIT9313 on both nitrite and urea; in MED4 it holds on cyanate but not on urea. The systems are not
specific to their own substrate. MIT9313's urease even rises more on nitrite than on urea. This
strengthens point 1 of "Reading so far": the consumer side reports N status (NtcA), not the
compound. As in MED4, dpp (and the MIT9313 amino-acid systems) is not part of the acute starvation
response.

### Provisional reading (agreed with the researcher 2026-10-11, revised after the analysis critic 2026-10-12; to be tested at the evaluation milestone)

Figure: [figures/e13_summary.png](figures/e13_summary.png) (script `scripts/e13_summary_figure.py`; flags
recomputed against all axenic samples in E14).

> MED4 raises its capacity to take up and process ammonium (`amt1`), urea (urt with urease) and
> cyanate (cyn with cyanase) as part of the N-starvation response. It sustains that capacity
> through 89 days of coculture; in the dying axenic culture these import systems fall back while
> the N-stress regulators stay up. Expression cannot name the compound used. In calibration
> experiments, urt, cyn and the nitrite system `focA` rise on substrates other than their own, so
> their expression does not report what is present; `amt1` was not calibrated. The dipeptide
> system (dpp) is raised in coculture protein but unresolved. No other nitrogen route shows a
> coculture signal beyond starvation: the nitrate channel `clc2` is irrelevant (MED4 can't use
> nitrate), and the broadly annotated routes were explored only. Envelope genes (`murJ`, and more
> weakly `tolC`, `acrA`, `bamA`) are up in coculture and not in the dying axenic culture. Because the
> axenic comparison is with a declining culture, none of these contrasts separates a partner effect
> from survival. "No signal" is not evidence that no other compound is taken up.

Supporting points, each traceable to the exploration above. All are [KG] unless tagged.

**Inorganic N** (E1, E6, E8, E9, E10, E14):
- `amt1`, urt and cyn are up in coculture protein throughout (0.93–1.00 at d89), in the
  N-starvation branch with the markers.
- In the dying axenic culture they fall back while the markers stay at 0.93–0.98:
  - urt 0.79 → 0.48 / 0.57 (d14 → d31 / d89);
  - cyn 0.99 → 0.72 / 0.67;
  - `urtA` is significantly down at d31.
- Calibration fails on specificity:
  - MED4: urt is not up on urea, and `urtA` is up on cyanate. On cyanate only `cynA`, `urtA` and
    `glnA` are significant; `amt1` (0.38) and `ntcA` (0.48) are not.
  - MIT9313: `focA` and urt are near the top on both nitrite and urea.
- `amt1` is not calibrated.
- Nitrate and nitrite can't be used by MED4.

**Urease and cyanase:**
- Up with their transporters in coculture, under the same N-stress control.
- MED4 urease is not up on urea.
- The MIT9313 urease nitrite-vs-urea difference is between non-significant values.
- `cynS` is 0.85 (not significant) on cyanate.
- `[interpretation]` Cyanase also removes internally formed cyanate.

**dpp: unresolved:**
- Coculture protein up (`dppA`, `dppC`).
- The axenic culture's own protein does not rise: `dppA` 0.76 ns at d14, 0.17 significantly down at
  d31, 0.21 at d89; `dppC` up at d31 and d89.
- `dppA/dppB` RNA is up in axenic d14.
- dpp sits outside the N-starvation branch and never responds in Tolonen deprivation.
- No peptide reactions in KEGG; no peptidase rises beyond starvation (E11).

**Other routes:**
- **Broad transporters:**
  - none shows transporter and enzymes up together (E4, exploratory per decision 4);
  - `sul1/sul3` are down;
  - `clc2` (nitrate) is up but irrelevant;
  - efflux pump PMM0561 RNA is up at d60/d89 but its protein is not.
- **N-releasing enzymes:** with the strict flag recomputed against all axenic samples, only the
  signal peptidase `sppA` passes (E11/E14).
- **Cell envelope:**
  - Strict ★ (up in coculture protein d60 and d89; not up in axenic protein d14/d31/d89, axenic
    RNA d14, or Tolonen; E14): `murJ`, `tolC`, `acrA`, `bamA`, `perM`, `mgtE`.
  - `tolC`, `acrA`, `bamA`, `perM`, `mgtE` were already high at axenic d14 (0.75–0.95).
  - The porin `som` and `yrbG` are also up in the dying axenic culture: not coculture-specific.

**RNA** (E2, E7):
- The coculture's exponential phase already had high N-regulon RNA relative to axenic (d11). This
  *contributes to* the protein-up / RNA-down pattern in coculture.
- Each culture's reference is its own d11 sample, so the same caveat applies to the axenic arm.
- In RNA the coculture changes little after exponential growth: 84 significant genes at d18, against
  877 in the axenic culture at d14. Coculture-vs-axenic RNA differences at that stage mainly reflect
  the axenic decline (researcher).
- `[interpretation]` The day-11 N-stress signature in coculture may reflect competition with the
  heterotroph for ammonium (researcher). Alternatives: faster growth or density; another partner
  effect. To test in the *Alteromonas* analysis: its amt / `glnA` / NtrBC at d11.

**Damping and iron** (E9, E14):
- No damping of the N response is detectable at the percentile ceiling.
- Marker protein log2FC is mixed late in coculture: `ntcA` 2.23 → 1.17 (d31 → d89), `glnB` 2.11 → 3.30,
  `glnA` steady.
- The iron-stress cluster is modestly raised in coculture **protein** only (0.77 / 0.71 vs 0.52; 20 of
  59 genes detected; includes `hli` and `cynA`). Its RNA is not raised.

**"No evidence" is not "evidence of absence":**
- uptake can occur without induction;
- amino-acid, polyamine and osmolyte routes have thin annotation;
- 21 transporter genes are undetected in protein;
- no coculture N measurements are in the KG (see decision 6);
- the *Alteromonas* side is the sibling analysis.

## Decisions

Taken after the header block (2026-10-11, researcher). Each departs from or fills in the
pre-registered rules after expression was seen, so each is disclosed as such:
1. **Labels use protein only; RNA becomes a corroborating line.** The criterion-(a) clause "RNA
   log2FC > 0 at d60 and d89" is dropped from the label. RNA is reported through the existing
   "RNA strength" line, shown next to the sanity markers' RNA. Reason: the positive controls
   (`glnA`, `ntcA`, `glnB`) are up in protein but down in coculture RNA, so the clause would reject
   genes known to respond to N starvation.
2. **(a) "significantly up in protein" = at least one detected subunit up at both d60 and d89,
   none down.** The "subunit coherence" line keeps the ≥ half requirement. This choice affects only
   dpp.
3. **C4 = at least one subunit per system up at ≥ 1 timepoint.** Tolonen passes; Read fails, and
   that failure is reported as a limitation.
4. **Labels are deferred** (researcher, 2026-10-11: "the classification is premature. we should
   revisit once data is available. do some in depth analysis."). Decisions 1–3 stand as the rules
   to apply later. Stage 3 (labels) waits until the in-depth exploration has been reviewed.
5. **The analysis milestone closes without the pre-registered labels** (researcher, 2026-10-11).
   The provisional reading above replaces them. Reasons:
   - The calibration gate failed (C2, C3): specificity fails in both strains.
   - The axenic "d14" reference is a late-decline culture, not early starvation, so "beyond
     early axenic starvation" and its 0.10 margin don't mean what the proposal intended.
   - Each culture's RNA is measured against its own exponential (d11) sample, and the coculture
     one was already N-stressed.

   Classification is revisited after the *Alteromonas* analysis, when both sides can be
   contrasted. Decisions 1–3 stay recorded as the rules to apply then.
6. **External culture data: explored, then excluded from this analysis** (researcher, 2026-10-12).
   - The researcher's CC1A3 culture measurements (flow-cytometry cell counts, NH₄⁺/NO₃⁻ in the medium,
     N budget; `C:\Users\oweisberg\Documents\GitHub\CC1A3\FCM\`) are not in the KG.
   - They were converted and plotted (E15), then set aside by the researcher: "the cell numbers / NH4
     are a distraction that we should deal with later and not as part of this analysis".
   - No E15 value enters the reading, the pages or `paper.md`. The E15 files stay gitignored and
     uncommitted.
   - Researcher: cell numbers are worth adding to the KG. This is hard because most papers show them
     only in figures (logged in `gaps_and_friction.md`).
7. **Stage 4 (per-class up/ns/down reads for MIT9313 and NATL2A) was not run as a separate stage.**
   Their N-replete controls are covered by expected-negative 2 (header block) and the MIT9313
   calibration by E8. The per-class tables move to the contrast analysis together with the labels.

Not a decision but a pre-registered consequence: **the calibration gate failed (C2, C3), so no
compound is named from the consumer side.** Labels report elevated import capacity only.

## Decide-gate checklist

**Outputs produced** (`analysis/`):
- **Code:** `expr.py`, `explore.py`, `figs.py`, `cc1a3.py`; `scripts/s1_pull_de.py`,
  `s2_header_block.py`, `e1`–`e14_*.py`, `e12_build_explorer.py` (+ `templates/`). The `e15_*.py`
  scripts read external data and are kept, but not used in the reading.
- **Tests:** `tests/` (60 OK, re-run by the main thread).
- **Data:** `data/de_long.csv.gz` (13 experiments), `de_long_mit9313_tolonen.csv.gz`,
  `de_long_med4_iron.csv.gz`, `qc_slices.csv`, `s2_*`, `explore/e1_*`–`e14_*`. The
  `data/external/` and `e15_*` files are gitignored (decision 6).
- **Figures:** `figures/` (PNG + SVG) with `README.md`.
- **Pages:** `analysis_review.html` (exploration and reading), `system_matrix.html` (all systems),
  `system_explorer.html` (interactive).

**Results presented:** header block; E1–E14; the provisional reading (summary figure e13).

**QC gate:**
- every slice: rows = `total_matching`, no duplicate rows (stage 1);
- an independent MCP verifier matched 10/10 values;
- rank percentiles recompute exactly (critic);
- pooled slices excluded; filtered tables flagged;
- the E7 identity was checked to 1e-15;
- the analysis critic (data-integrity + interpretation) found 2 Blockers, 10 Concerns and 4 Notes.
  All are fixed or disclosed (`critical_review.md`; code fixes in E14). The revised reading was
  approved by the researcher on 2026-10-12.

**Decisions made this milestone:** decisions 1–7 above.

**Advance rationale:**
- The data are complete and verified, and the exploration is documented.
- The provisional reading is scoped to what the data support: N-import capacity is raised and
  sustained as part of the N-starvation response; no compound can be named from expression; dpp
  is unresolved; a small coculture-specific envelope set exists, with the axenic-decline confound
  stated.
- Labels are deferred to after the *Alteromonas* analysis.
- The evaluation milestone tests the reading and collects caveats.
