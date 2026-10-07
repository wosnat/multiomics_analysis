# Research proposal — nitrogen import capacity of *Prochlorococcus* in coculture with *Alteromonas*

**Status:** revised after the proposal critic (dispositions in `proposal_critical_review.md`);
awaiting researcher approval.
**KG:** 0.1.0-alpha.7 (built 2026-09-22) · explorer 0.1.0-alpha.5 · template 0.2.0-alpha.1.
Grounding queries, counts and rejected alternatives: `proposal_notebook.md`.
Tags: `[KG]` from a KG query · `[interpretation]` reasoning beyond the KG · `[gap]` the KG can't answer.

This is the first of three analyses. It covers the **consumer side**: which nitrogen import routes
*Prochlorococcus* turns up. A sibling analysis (`..._alteromonas_n_release_coculture`) covers
the producer side, and a short third analysis (`..._n_cross_feeding_contrast`) compares the two.
**What this analysis can and can't say:**
- Higher transporter protein or RNA is evidence of **elevated import capacity**, which is
  largely driven by N-starvation regulation (NtcA/PII).
- It is **not** evidence that a compound was present or taken up, nor of who supplied it.

---

## 1. Question

In long-term N-limited coculture with *Alteromonas* HOT1A3, **for which nitrogen-compound
classes does *Prochlorococcus* MED4 elevate import capacity beyond what early axenic N
starvation shows?** Judged from its transport systems' protein and RNA at days 60–89 in
coculture.

**Secondary:** is that pattern specific to N limitation? That is, is it absent when the same
strain, and other strains, are cocultured with *Alteromonas* in N-replete medium?

**Compound classes are not preselected.** The methods milestone surfaces every N-containing
substrate the strain's transport annotation reaches, and the groupings are agreed with the
researcher at the methods decide gate, from the annotation alone, before any expression data is
pulled. Grounding suggests what to expect (ammonium, urea, cyanate, nitrate/nitrite, peptides,
amino acids, nucleobases/nucleosides, amines/polyamines, osmolytes; notebook item 11), but that
list is not a filter.

## 2. KG entries

**No N compound is measured in any coculture.** All 14 metabolite assays in the KG are on
axenic *Prochlorococcus* `[KG]`, so everything here is inferred from gene expression `[gap]`.

**Anchor: Weissberg et al. 2025** (10.1101/2025.11.24.690089; the researcher's own preprint,
which these analyses are rebuilding), MED4 + HOT1A3, Pro99-lowN, ~90 days `[KG]`. Its abstract
proposes that *Alteromonas* supplies "a continuous, albeit
low-level, supply of bioavailable NH4+" through remineralization.

| role | experiment_id (prefix `10.1101/2025.11.24.690089_`) | design | timepoints used |
|---|---|---|---|
| **main**, protein | `growth_state_pro99lown_nutrient_starvation_med4_proteomics_coculture` | coculture culture, starvation vs. own exponential phase | d60, d89 (main); d18, d31 (trajectory) |
| **main**, RNA | `growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture` | same, RNA | d60, d89 (main); d18, d31 |
| reference, protein | `growth_state_pro99lown_nutrient_starvation_med4_proteomics_axenic` | axenic culture, starvation vs. own exponential phase | **d14 only** (d31, d89 are death phase) |
| reference, RNA | `growth_state_pro99lown_nutrient_starvation_med4_rnaseq_axenic` | same, RNA | **d14 only** |
| same-study direct contrast | `coculture_alteromonas_hot1a3_med4_rnaseq` | coculture vs. axenic, RNA | d11 (exponential), d18 (nutrient_limited) |

All anchor tables are `all_detected_genes` (MED4: 1424 proteins, 1849 transcripts per timepoint)
`[KG]`. The same-study direct contrast is the **only N-limited coculture-vs-axenic comparison**
in the KG. It comes from the same study as the anchor, so it is **not independent** of it.

**N-replete controls** (coculture vs. axenic, RNA-seq; all Pro99, exponential, `[KG]` from
`list_experiments` verbose):

| experiment_id | strain + partner | table_scope | conditions |
|---|---|---|---|
| `10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_med4_rnaseq` | MED4 + HOT1A3 | all_detected (1714) | Pro99, 10 µmol photons, Rockhopper, single contrast |
| `10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_mit9313_rnaseq_inoc_05e6` | MIT9313 + HOT1A3 | all_detected (2267) | Pro99, exponential |
| `10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_mit9313_rnaseq_inoc_5e6` | MIT9313 + HOT1A3, high inoculum | all_detected (2268) | Pro99, exponential |
| `10.1038/ismej.2016.82_coculture_alteromonas_macleodii_mit1002_natl2a_rnaseq` | NATL2A + MIT1002 | **significant_any_timepoint** (353) | Pro99, 30 µmol photons, DESeq2, −12 h to 48 h |

**Positive calibration: MED4 with a known N source, or plainly N-starved** (axenic; independent
studies; none of these data seen) `[KG]`:

| experiment_id | design | table_scope | role |
|---|---|---|---|
| `10.1038/msb4100087_growth_medium_growth_on_cyanate_as_med4_microarray` | growth on cyanate as sole N vs. N-replete Pro99 | all_detected (1697) | known substrate: cyanate |
| `10.1038/msb4100087_growth_medium_growth_on_urea_as_med4_microarray` | growth on urea as sole N vs. N-replete Pro99 | all_detected (1697) | known substrate: urea |
| `10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray` | N deprivation vs. N-replete, 0–48 h | all_detected (1697) | plain N starvation, independent study |
| `10.1038/ismej.2017.88_nitrogen_stress_ndepleted_pro99_medium_med4_rnaseq` | N-depleted vs. N-replete Pro99, 3/12/24 h | **filtered_subset** (top 50% by expression, ~850) | plain N starvation, positive evidence only |

**Replicating the anchor finding in another strain under N limitation is not possible with this
KG** `[gap]`. The other strains appear only in N-replete cocultures.

**Not used:** García-Fernández 2022 glucose-addition proteomics (a carbon contrast); the
Alteromonas-side experiments (sibling analysis); Pi- and light-limitation iTRAQ sets.

## 3. Framing

### 3.1 Hypothesis

**Prior interpretation, from the anchor preprint:** *Alteromonas* supplies low-level ammonium.
The preprint is the researcher's own earlier reading of these data; it is not being published as
is. This analysis is one of several that build the evidence for a more comprehensive rewrite.
The ammonium reading is therefore **re-examined on the same data it came from**:
- a pass re-derives it more rigorously (system-level, tiered, with blind RNA predictions), but is
  not independent confirmation;
- a fail is a correction the rewrite must carry.

Claims in the rewrite should stand on these analyses, not on the preprint.

The ammonium-supply reading gives two competing predictions for MED4's import side
`[interpretation]`:
- **(i) Supply too low to relieve N stress.** All NtcA-controlled import systems (ammonium,
  urea, cyanate) stay up together. The consumer side is then uninformative about the compound's
  identity.
- **(ii) Supply partly relieves N stress.** The ammonium route stays up, and the alternative-N
  systems (urea, cyanate) are damped relative to plain starvation.

**Pre-registered blind predictions for the ammonium reading** (RNA was not seen):
- **P1:** `amt1` PMM0263 RNA rank percentile ≥ 0.90 at both d60 and d89 in the coculture
  culture.
- **P2 (separates (i) from (ii)):** at d60 and d89 in coculture RNA, `amt1`'s rank percentile is
  ≥ the median percentile of the urea (`urtA–E`) and cyanate (`cynABD`) systems.

**What counts against ammonium as the primary route on the consumer side:**
- P1 fails (the ammonium route is not strongly up at the transcript level in the late window), or
- P2 fails in both d60 and d89 (alternative-N systems out-rank the ammonium route). That is
  consistent with (i), or with a non-ammonium source.

Either outcome is reported. Neither refutes Alteromonas N supply, which is the sibling
analysis's question.

**Disclosed, seen before this framing was written** (`proposal_notebook.md` grounding item 7): a
coverage check returned **protein** fold changes, in both MED4 cultures, for 12 genes: `amt1`,
`urtA`, `ureC`, `cynA`, `cynS`, `dppA`, `dppC`, `gltS`, `glnA`, `ntcA`, `glsF`, `glnB`.
- Coculture d60/d89: `cynA`/`cynS` are among the top up proteins (log2FC 3.8–4.7), above `urtA`
  (~2.5) and `amt1` (~2.3, significant).
- Axenic d14: `cynA` (2.09) and `cynS` (1.30) are **already significantly up**; `amt1` is not
  significant.

Consequences:
- Cyanate is an observation to explain, not a prediction, and it responds to plain starvation
  too.
- The protein-level ammonium test is not blind. The protein pattern already leans towards
  reading (i).
- The **blind** parts are: all RNA; the system-level aggregation (subunits, tiers, classes);
  every gene outside the 12; all N-replete controls; and the expected-negative 1 annotation
  check.

### 3.2 Approach

**Unit = transport system, built per strain from that strain's own annotation** (methods
milestone). It is one organism-agnostic module, run separately on MED4, MIT9313 and NATL2A, and
reused (versioned) by the Alteromonas analysis.

1. **Enumerate transporter genes** from TCDB (`genes_by_ontology`, `metabolites_by_gene` transport
   arm) plus the BRITE `transporters` tree.
2. **Group genes into systems** using genome neighbourhood plus shared TCDB family and subunit
   role. **Subunit role comes from Pfam domains** (`gene_ontology_terms(ontology='pfam')`; on the
   MED4 N transporters 14/16 calls are curated): substrate-binding (e.g. PF13379, PF13433,
   PF00496), permease (PF00528, PF02653), ATPase (PF00005), single carrier (PF00909 Amt, PF03616).
   Each system records its **role completeness** (binding + permease + ATPase for ABC).

   **Neighbours are recruited in two kinds, kept separate** (`gene_neighbors`; every candidate
   neighbour is surfaced with its evidence, and what joins is agreed at the methods decide gate
   from annotation only):
   - **Missing subunit:** a neighbour with a transporter-role Pfam domain (binding / permease /
     ATPase) or a transporter KO in the BRITE `transporters` tree, but no TCDB call. It **joins
     the system**, and its expression counts toward the system's readout. `recruited_by` records
     pfam / ko.
   - **Linked enzyme:** a neighbour whose functional annotation (KO/EC first, then Cyanorak role,
     then product name, which is flagged as soft) makes it the enzyme acting on the system's
     substrate, e.g. `cynS` beside cyn, urease beside urt. It is **attached, not merged.** It sets
     `can_use = co-located` (stronger than a match elsewhere in the genome), and its expression is
     shown as a separate readout beside the system, never pooled into the import signal, because
     cyanase and urease are also N-stress responsive.
   - Other neighbours (hypotheticals, unrelated genes) are listed as context only.

   Runs are read on the same strand by default; opposite-strand genes inside a run are surfaced
   flagged, not auto-added (MED4's `ureD` PMM0966 sits on the − strand inside the + strand
   urease/urt cluster). `gene_neighbors.bp_gap` is distance to the anchor gene, so adjacent gaps
   are computed from coordinates. Single-gene carriers are one-gene systems. Round 1's system reconstruction
   (`analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/`, KG alpha.6) is
   design input, not imported code. Each round-1 workaround is re-checked against the current
   stack and recorded as still needed or obsolete.
3. **Surface every N-containing substrate per system, with flags, not filters.** One row per
   system × subunit × substrate (`metabolite_elements=['N']`, both depths). Nothing is dropped.
   Columns:
   - subunit and its role (substrate-binding / permease / ATPase / single carrier);
   - `substrate_depth`, `evidence`, `tcdb_evidence_score`, `transport_substrate_resolution`,
     and the TCDB edge's `source_agreement` and `pfam_support` (does the gene carry the domains
     its TCDB family is built from);
   - the gene's Pfam domains and evidence rung;
   - **`domain_substrate_hint`**: any substrate implied by domain names, shown but never used
     for the substrate call. Domains give roles, not substrates: the urea system's domains are
     named for branched-chain amino acids (its transporter family), and `cynA`'s NMT1/THI5 domain
     is shared with thiamine-precursor binders (TCDB also gives `cynA` a ThiXYZ call at 0.4);
   - **`can_use`** (`co-located` / `elsewhere in genome` / `no`): does a gene of the same strain
     take part in a reaction with this substrate (KEGG metabolism arm), and is that gene a linked
     enzyme of this system? E.g. urease for urea, cyanase for cyanate, nitrate/nitrite reductase
     for nitrate/nitrite. This check has teeth only for simple inorganic and small N compounds;
     for peptides and amino acids every genome passes it trivially;
   - **`likely_transporter`**: is the gene a plausible transporter at all? Grounding item 11
     found TCDB attachments on `fadD`, `acs`, `speE` and `tsf`.

   **Interpretation rule (pre-specified, not a filter):** a substrate flagged `can_use = False`
   can never be the basis of a claim about that system. It stays visible in the table. *(Worked
   case: MED4's cyn system surfaces nitrate/nitrite on `cynA` with `can_use = False`, since MED4
   has no nitrate/nitrite reductase (item 6), and cyanate on `cynB` with `can_use = True` via
   `cynS`. Only cyanate can carry a claim.)*

   **Grouping substrates into classes happens after this table is surfaced:** the researcher and
   author work through it at the methods decide gate, from the annotation alone. Expression is
   pulled only in the analysis milestone, after the groupings are agreed.
4. **Evidence profile per system × substrate** (columns, not a filter): TCDB depth and
   `evidence` (`homology` / `family_inferred`), `tcdb_evidence_score`, `source_agreement`,
   `pfam_support`, Pfam role domains and their rung, and role completeness. **Tier boundaries are
   set at the methods decide gate**, from annotation alone, before expression is pulled (the same
   logic as the class groupings). One principle is fixed now: **the tier must not systematically
   penalise multi-subunit ABC systems relative to single-gene carriers.** Grounding item 14
   shows why: on MED4's N transporters, TCDB is eggNOG-only (`family_inferred`) for cyn, urt and
   dpp, but has a direct sequence hit for `amt1`. A gene-level "homology = high" rule would
   favour the hypothesis gene for annotation-pipeline reasons. `tcdb_evidence_score` orders rows
   within a tier; every row is kept.
5. **Non-N import systems are built by the same method**, as the negative reference: phosphate
   (`pstS` PMM0710, `pstC/A/B` PMM0723–0725), phosphonate (`phnC/D/E` PMM0671–0673), sulfate
   (`sul1` PMM0644, `sul3` PMM0214), iron (`futB` PMM0489, `futC` PMM0803), Mn/Zn (`mntC`
   PMM0601, `lraI` PMM1032) and bicarbonate (`sbtA` PMM0213) (keyword-grounded locus tags; the
   method's own build is authoritative, and the final set is agreed at the methods decide gate).
6. **Context genes** (not import systems): `glnA` PMM0920, `glsF` PMM1512, `ntcA` PMM0246, `glnB`
   PMM1463, `pipX` PMM0393, urease `ureA–G`, `cynS` PMM0373.

**Expression read (analysis milestone):**
- For each system, per experiment and timepoint: subunits significant / total, median log2FC,
  and median **rank percentile** (§3.3). The substrate-binding protein is shown separately.
- **Main read:** protein and RNA in the coculture culture at d60 and d89, against the axenic d14
  reference.
- **Time-matched read:** coculture d18 vs. axenic d14 (both early, N-limited). This separates "up
  because of the partner" from "up because starvation is longer" (§3.5).
- **Controls read:** the same tables on each N-replete experiment, using that strain's own
  systems.
- **Calibration read:** the same tables on the Tolonen and Read MED4 experiments. This answers
  two things: does a known N source give a system-specific signature, and what does plain N
  starvation look like across three studies (anchor axenic d14, Tolonen N-deprivation, Read
  N-depleted)?
- **Negative-reference read:** the non-N import systems in every table, as the "transporters in
  general" baseline.

**Annotation limits carried into every claim** (`docs://analysis/metabolites`):
- TCDB has no import/export direction.
- Transport annotation gives "compatible with", never "confirmed".
- Weak annotation for a class (in MED4, amino acids, polyamines and osmolytes are reachable only
  via inherited rows; grounding item 11) means the KG can't name an importer `[gap]`. It does
  not mean the strain lacks one.

### 3.3 Statistics plan

**No new formal test.** The KG holds per-gene summary results (log2FC, adjusted p,
`expression_status`) from each paper, not replicate-level data, so no valid new test can be
computed. Significance = the source paper's call stored in the KG (padj < 0.05). This analysis
adds no p-values, and no p-values are compared across studies.

**Rank percentile** = the gene's position when all detected genes in that experiment × timepoint
are sorted by log2FC (descending), as `1 − (position − 1) / n_detected`. 1.0 is the most
up-regulated gene; ≥ 0.90 is the top 10% of all detected genes.

**Pre-registered labels**, applied in the analysis milestone to each class grouping agreed at the
methods decide gate (MED4; judged on the class's best-supported system under the tiers agreed
there, among rows with `can_use = True` where the check applies; every system's numbers still
shown):
- **Stands out beyond early axenic starvation:**
  - (a) significantly up in **protein** in the coculture culture at **both d60 and d89**, with RNA
    log2FC > 0 at both; **and**
  - (b) median subunit rank percentile ≥ 0.90 at both d60 and d89 in protein, **and** ≥ 0.10
    above that system's own percentile in the axenic d14 protein reference. The margin keeps a
    gene that merely holds its rank from passing.
  - (c) its median rank percentile exceeds that of **every eligible non-N import regulon** at
    both d60 and d89 in protein. If exactly one eligible regulon exceeds it, the label becomes
    **"stands out, with caveat"**, naming it.
    - *Regulon, not system:* co-regulated non-N systems count once (pst + phn = one P regulon).
    - *Eligible* = detected in that protein table **and not explained as secondary limitation**
      by expected-negative 3, which is evaluated first. A non-N regulon that stands out because
      its own nutrient became limiting says nothing about whether the N signal is specific, so it
      doesn't count against N classes. It is reported in its own right.
    - *Detection:* (c) is evaluated over non-N regulons detected in that table; the number
      detected is reported. With fewer than 3 eligible regulons, (c) is **"not evaluable"**, never
      passed by default.
- **Elevated, not standing out:** passes (a), fails (b) or (c).
- **Not elevated:** fails (a).
- Each label carries a flag: **"also up in early axenic starvation"** (significant up in axenic
  d14 protein) and **"up early in coculture"** (significant up in coculture d18 protein).

### 3.4 Validation set

*Method checks (methods milestone; MED4):*
- `urtA–E` (PMM0970–0974) → one system whose urea rows have `can_use = True` (urease).
- `amt1` (PMM0263) → ammonium row with `can_use = True`.
- `cynA/B/D` (PMM0370–0372) → one system; its cyanate row has `can_use = True` and its
  nitrate/nitrite rows have `can_use = False` (§3.2 step 3). TCDB alone calls the binding subunit
  a nitrate/nitrite porter.
- `dppA/B` (PMM1049/1048), `dppC` (PMM0421), `ddpD` (PMM0192), split across loci → regroup as one
  system carrying peptide substrates.

*Tiers aren't pre-asserted.* They come from the KG calls; the check is that the grouping and the
`can_use` flags are right.

*Positive calibration (analysis milestone; blind).* **What it tests:** whether MED4's import
systems respond to their substrate when it is present at high concentration in exponential, non-
starved growth (Tolonen: 400 µM urea or 800 µM cyanate as sole N vs. ammonium-replete Pro99,
`exponential` `[KG]`). It does **not** test whether a trace substrate is readable on top of a
months-long starvation response. A pass is necessary for naming a compound, not sufficient.
- **C1, cyanate:** cyn system median rank percentile ≥ 0.90 on cyanate.
- **C2, urea:** urt system median rank percentile ≥ 0.90 on urea.
- **C3, specificity:** cyn's percentile on cyanate exceeds its percentile on urea by ≥ 0.10, and
  urt's on urea exceeds its on cyanate by ≥ 0.10. *(A declared exception to "compare within an
  experiment only" (§3.6): same study, platform, control and 1697-gene universe. The margin guards
  against noise-level differences, since both sets have few significant genes, 20 up / 23 down and
  18 up / 14 down.)*
- **C4, acute starvation fingerprint** (Tolonen N deprivation 12–48 h; Read 12–24 h, both
  `acute_stress` / early `nutrient_limited`, *hours*, not months): `amt1`, urt and cyn
  significantly up. **Read 2017 is positive evidence only** (top-50% subset): a missing gene is
  "not listed", not "not up".

**Pre-registered consequences, per check:**
- **C1, C2 or C3 fails → the gate fails.** MED4's import systems don't demonstrably report their
  substrate, so the analysis reports **elevated import capacity only and names no compound from
  the consumer side.** P1/P2 are still reported as written. A gate failure in which cyn and urt
  rise together on either substrate is itself evidence of shared NtcA control (reading (i) of
  §3.1) and is reported as such.
- **C4 fails** (or the needed genes are not listed) → the plain-starvation reference rests on
  the anchor's axenic d14 alone; stated as a limitation.
- **Gate passes → a compound may be named only if all three hold:**
  1. its class "stands out" (§3.3);
  2. in the anchor's late window, its system out-ranks the median of the *other* NtcA-controlled
     import systems (ammonium, urea, cyanate) by ≥ 0.10 in protein at both d60 and d89. That is
     a departure from co-induction, in the direction its own calibration showed;
  3. the same holds in RNA, in direction.

  Any qualitative "which fingerprint does it resemble" comparison is **exploratory** only and
  can't support naming.
- **Not tested by any calibration:** reading (ii)'s partial-relief damping (no ammonium-limited or
  partial-supply experiment in the KG) `[gap]`.

*Biology checks (analysis milestone; a data-sanity gate, not evidence for the hypothesis):*
- `glnA` PMM0920, `ntcA` PMM0246 and `glnB` PMM1463 are significantly up in protein under N
  starvation in **both** cultures (coculture d18–d89; axenic d14).
- These were in the disclosed peek (values in `proposal_notebook.md` item 7), so they're not
  blind.
- If they fail, the data don't show a usable N-starvation response and every downstream call is
  suspect.

### 3.5 Falsifiability

**What "nothing real" looks like:** no class grouping earns "stands out beyond early axenic starvation",
and every N import system moves in lockstep with the starvation markers (`glnA`, `ntcA`, `glnB`).
That is reported as a **bounded negative**: MED4's import side carries no class-specific signal
in these data, consistent with reading (i) of §3.1. The compound question then passes to the
Alteromonas analysis and the contrast.

**Named alternative explanation: starvation length, not the partner.** Coculture d60/d89 is
60–89 days into N limitation; the axenic reference is day 14. Any NtcA target that keeps climbing
as starvation deepens would look partner-driven. The axenic d14 response is shallow (40 up / 95
down of 1424 proteins, vs. coculture d60 145 / 74 and d89 161 / 92) `[KG]`. Guards:
- the 0.10 margin in (b);
- the time-matched coculture d18 vs. axenic d14 read;
- the "also up in early axenic starvation" flag.

A class that stands out late but sits level with axenic in the time-matched read is reported as
**"duration-compatible"**, not partner-specific. The KG cannot fully separate the two `[gap]`: no
axenic culture survives to d60.

**Pre-registered expected-negatives:**
1. **Nitrate/nitrite in MED4.** MED4 has no nitrate/nitrite assimilation (grounding item 6), so
   **every** nitrate/nitrite row surfaced for MED4 must carry `can_use = False`, and so can't
   support any label. A nitrate/nitrite row with `can_use = True` means the check is broken. This is not trivial:
   TCDB's most-specific call for the binding subunit of MED4's most responsive system is a
   nitrate/nitrite porter. Each control strain's nitrate/nitrite expectation comes from its own
   genome.
2. **MED4 N import systems in N-replete coculture** (`10.1038/ismej.2016.70_..._med4_rnaseq`):
   no MED4 N import system is significantly **up** in coculture vs. axenic. The same is expected
   for MIT9313 and NATL2A in their N-replete cocultures, on their own systems. Reading the
   result:
   - **Up** would mean coculture alone triggers N scavenging even in replete medium (e.g. partner
     competition for ammonium). That alternative is then carried into the contrast analysis. It
     doesn't directly undermine the anchor read, because the anchor compares the coculture
     culture to its own coculture exponential phase, so a coculture-wide effect would partly
     cancel there.
   - **Down** (significant down in coculture) would be compatible with partner N supply damping
     NtcA targets even in replete medium. It is recorded as a pointer for the contrast analysis,
     not a finding here.

3. **Non-N import systems in the late coculture window.** No phosphate, phosphonate, sulfate,
   iron, Mn/Zn or bicarbonate import system meets "stands out" (a)+(b). If one does, two readings
   are pre-registered: (i) the readout picks up a general transporter or stationary-phase
   programme, which weakens every N-class claim; or (ii) that nutrient became secondarily limiting
   over ~90 days `[interpretation]` (P is the likeliest). They're told apart, as far as the KG
   allows, by whether that regulon's classic co-regulated marker moves with it: `phoH` PMM1284 for
   P; `idiA2` PMM1164 (iron deficiency-induced protein A) for Fe. No marker is named for S, Mn/Zn
   or bicarbonate, so those cases are **unresolved** by design and count against N classes in (c)
   (they can't be excused as secondary limitation). The Fe set lists `futB`/`futC` only; whether
   a binding subunit exists is left to the method's own build.

### 3.6 Comparing across experiments

- Systems are **built per strain**, never mapped from MED4 by orthologs. Comparisons are at the
  **compound-class** level, each on that strain's own systems in that strain's own experiment.
- Compare **rank percentiles within an experiment**, never raw log2FC: platforms (proteomics vs.
  RNA-seq), normalisation, statistical tool (Rockhopper vs. DESeq2) and detection depth differ.
- **Significant-only or filtered tables** (Biller NATL2A, 353 genes; Read 2017, top-50% subset):
  positive evidence only; a missing gene
  is "not listed", not "unchanged". This table can't confirm expected-negative 2 for NATL2A; it
  can only fail it (by listing a significantly-up N import gene).
- **Roles, not replication.** The anchor answers the question. The Tolonen and Read MED4
  experiments are calibration (known substrate; plain starvation) on other platforms
  (microarray; RNA-seq top-50% subset), compared only through rank percentiles within each. The same-study direct contrast is
  a non-independent consistency check. The N-replete experiments are controls for "is this N
  limitation-specific", not replicates. Each result is reported with its design next to it; no
  pooled score.
- Optional QC: ortholog-group members, built separately per strain, that land in different
  classes or tiers are flagged as annotation inconsistency, never used as an input.


### 3.7 Output and ordering

**The conclusion is a ladder, not one verdict:** a system's expression is elevated → its class
stands out (§3.3) → a compound is named (only through the §3.4 gate). Each rung is reported
separately.

**Header block, reported before any table** (so none can be dropped quietly): the biology
sanity gate (§3.4); calibration checks C1–C4 and the gate outcome (§3.4); P1 and P2 (§3.1); the
three expected-negatives (§3.5).

**MED4 evidence table: one row per transport system, N and non-N alike** (non-N systems are
the reference, laid out the same way). Columns, in four groups:

1. **Primary label** (§3.3): *stands out beyond early axenic starvation* / *stands out, with
   caveat* / *elevated, not standing out* / *not elevated*. If (c) is *not evaluable*, the label
   can reach *elevated* at most.

2. **Corroborating lines.** Independent of the label's own conditions; each is *supports* /
   *against* / *neutral* / *not applicable* / *not measured*. If a system meets both its supports
   and its against condition, **against wins**. A gene missing from a table is *not measured*,
   never *against*.

   | line | platform, timepoints | supports | against | not applicable |
   |---|---|---|---|---|
   | RNA strength | RNA, coculture d60 and d89 | median subunit RNA rank percentile ≥ 0.90 at both | any subunit significantly down at either | — |
   | Persistence | protein, coculture d31 | median subunit significantly up | any subunit significantly down | — |
   | Subunit coherence | protein, coculture d60 and d89 | ≥ half of detected subunits significantly up at both | any subunit significantly down at either | one-gene systems |
   | Linked enzyme | protein, coculture d60 and d89 | ≥ half of the detected co-located linked-enzyme genes significantly up at both | any linked-enzyme gene significantly down at either | no co-located linked enzyme |

   Shown as **three counts: supports / against / applicable.** No ratio is computed. The counts
   are **not used for ordering**, because systems differ in how many lines can apply (a one-gene
   carrier with no linked enzyme has 2; a full ABC system with a linked enzyme has 4).

3. **Flags** (reported as observed; not scored, not used for ordering):
   - *Early axenic:* significantly up in axenic d14 protein.
   - *Time-matched:* coculture d18 vs. axenic d14 protein median rank percentile. "Partner-early"
     if coculture d18 ≥ axenic d14 + 0.10. "Duration-compatible" is reserved for §3.5's
     definition (stands out late, but level with axenic in this time-matched read).
   - *Non-N reference:* the outcome of §3.3 (c), naming any eligible regulon that out-ranks it.
   - *N-replete coculture:* the system's status in `10.1038/ismej.2016.70_..._med4_rnaseq`
     (up / not significant / down), reported as observed. Up is relevant to expected-negative 2;
     down is a pointer for the contrast analysis (§3.5).
   - *Calibration:* the C1–C3 outcome for systems with a calibration substrate (cyn, urt); "none"
     otherwise. A property of the method, not evidence about coculture.

4. **Annotation confidence:** the system-level evidence profile and tier (§3.2 step 4).

**Ordering (presentation only, no claim of magnitude):** primary label, then median protein rank
percentile at d60/d89. Nothing else enters the ordering.

**Class level:** each class is represented by its best system **by annotation tier, fixed at the
methods decide gate** (§3.2 step 4). It is never chosen by expression or corroboration. Every
system's row stays visible.

**Other strains (secondary question):** for MIT9313 and NATL2A, each N-replete experiment is
reported per class on that strain's own systems as up / not significant / down (NATL2A positive
evidence only, §3.6). They get no labels and no corroboration lines, because those need the
anchor's design.

**Not blind, disclosed** (`proposal_notebook.md` item 7): for the 12 peeked genes, these cells
were visible before §3.7 was written:
- *Persistence:* `amt1`, `urtA`, `cynA` and `dppA` are significantly up at d31.
- *Early axenic flag:* `cynA` is up at d14; `amt1` and `urtA` are not.
- *Linked enzyme:* `cynS` is up at d60/d89; urease is seen only through `ureC`.

All RNA cells, the time-matched read and all other genes are blind.

---

**Sub-questions deferred to the Run phase** (noted, not committed): whether the cyanate signal
tracks the ammonium system over d18→d89; whether urea and cyanate systems co-move (shared NtcA
control `[interpretation]`).
