# Step 3 — Analysis framing (proposal lock)

## Context

Steps 1–2 established the question (per-family characterization dossier for the 14
core families) and confirmed the KG fills every angle. This step fixes the **dossier
schema**, defines what a **lead** is, and sets controls. End of this step locks the
research proposal (steps 1–3); steps 4–6 execute against it.

The framing was reshaped during co-define by the researcher's point that **the angles
are not independent columns — convergence across them is the actual signal**, and that
**descriptive labels are majority-vote and must be treated cautiously**. Those two
points drive the schema below.

## Hypothesis (plain)

Each of the 14 conserved-hypothetical families can be given at least partial functional
context from the KG. The strongest, most trustworthy leads come from **two or more
angles agreeing**, not any single column. Some families will be **function-rescued** (a
named, cross-genus homolog the consensus product hid — e.g. CK_00000498 → `iscA`);
others will be **lineage novelties** (*Prochlorococcus*-restricted) carrying only
surface/regulatory hints.

## Target

The 14 core families (`core14 = True` in `handoff_shortlist.csv`).

## Dossier schema

Frozen column spec in `data/dossier_schema.csv`. One row per family. Blocks:
identity · DE fingerprint (carried, alpha.5) · cross-organism homologs · neighborhood ·
co-expression · **convergence** · sequence/localization · derived metrics ·
publications · lead. Each field is tagged **hard / soft / carried / derived /
interpretation** so a future reader knows what to trust.

### The convergence layer (the core of this framing)

A fact in one block is weak; the same conclusion from two independent angles is strong.
The convergence layer is the heart of the dossier. Signals, brainstormed with the
researcher and tiered by power/feasibility (Tier 1–2 in scope; Tier 3 opportunistic —
computed only where the data is already in hand):

**Tier 1 — high power**

- **Phyletic profiling** (`phyletic_profile_match`) — the characterized family / pathway
  whose **strain presence-absence pattern** across the 17-strain backbone most closely
  matches this family's (the Rosetta-stone inference: co-occurrence ⇒ functional
  coupling). *Has signal only for variably-present families (broad tier, 9–13/17);
  families present in all 17 have no presence/absence variance, reported as "no phyletic
  signal."* `[interpretation]`
- **KG-scale co-response similarity** (`coresponse_top_matches`) — top **characterized**
  families by correlation of the **fine-grained per-(experiment × timepoint) log2FC
  vector**, re-pulled fresh from alpha.6 via `differential_expression_by_gene` /
  `differential_expression_by_ortholog`. **Not** computed on the collapsed
  `direction_by_treatment` (which pools experiments/timepoints into one up/down/mixed
  token and hides whether two genes co-respond in the *same* experiment). Two guards:
  (a) correlate only on **shared measured datapoints** and report the support count, so
  structured missingness (significant-only tables = blank is measured-flat *or*
  not-measured) does not fake similarity; (b) correlate on response **shape**, not
  magnitude/coverage, to avoid the breadth coverage-confound. `[interpretation]`
- **Operon triple-convergence** (`operon_triple`) — a neighbor that is same-strand +
  close gap **and** conserved-adjacent across strains **and** co-expressed: a near-certain
  operonic partner. Upgrades neighbor∩cluster with strand + synteny.

**Tier 2 — cheap and informative for this gene set**

- **neighbor ∩ cluster-mate** (`neighbor_cluster_overlap`) — genes that are *both* a
  genomic neighbor *and* a co-expression cluster-mate (position + co-regulation agree).
- **neighborhood pathway coherence** (`neighbor_pathway_dominant` / `_count`) — ≥2
  neighbors sharing one pathway/gene-category (coherent operon/island, not an isolated
  neighbor).
- **homolog ↔ context concordance** (`homolog_context_concordance`) — whether the
  eggnog-rescued function fits the neighborhood/cluster (e.g. `iscA` next to FeS genes).
  `[interpretation]`
- **secretion/surface convergence** (`secretion_convergence`) — agreement among SignalP
  score, vesicle-proteome membership, PSORTb Extracellular, and the "secreted" product
  label: four weak signals → one confident "genuinely exported" call.
- **pangenome context** (`pangenome_context`) — the family's Core/Flexible class set
  against its neighbors': Flexible-among-Flexible ⇒ genomic island / likely HGT,
  ecotype-specific; Core-among-Core ⇒ ancient core function. `[interpretation]`

**Tier 3 — opportunistic (computed where already in hand, else skipped)**

- **cross-omics agreement** — significant in both a transcriptomic and a proteomic
  experiment for one treatment; diel transcript-vs-protein lag/damping.
- **metabolic propagation** — if a strong neighbor/cluster-mate carries a
  Reaction/Metabolite, propagate that context as a tagged hypothesis. `[interpretation]`
- **diel phase concordance** — `peak_time` alignment with a known pathway.
- **internal-consistency flags** (negative convergence) — members carrying *different*
  eggnog COGs / gene names, or paralogs in different contexts, flag a heterogeneous
  "family" (divergence as a caution signal, not agreement).

`convergence_count` = how many independent angles support the leading hypothesis; it,
not any single column, drives the lead evidence grade.

### Evidence hardness (the grain-of-salt rule)

- **Hard** (trust): pfam/COG domain, SignalP score, PSORTb localization, pangenome
  Core/Flexible class, synteny conserved across strains, cross-angle convergence.
- **Soft / majority-vote** (caution): `consensus_product`, OG `consensus_gene_name`,
  cluster `functional_description` (an enrichment label about the cluster majority, not
  a fact about this gene).

A lead resting on a **single soft label is low confidence by construction** and only
promotes when hard evidence or convergence backs it.

### Lead classification

Five types — **function_rescued · neighborhood · coexpression · surface_secreted ·
lineage_novelty** — each carrying an **evidence grade**:

- **high** — hard evidence (COG/domain/synteny) and/or ≥2 angles converge
- **medium** — one hard signal, or a soft label plus one corroboration
- **low** — descriptive label only

A family may carry a **combined** lead when angles converge (e.g. "function_rescued AND
neighborhood-corroborated → high"). `lead_summary` is the one-line plain-language read
for future-omics use.

## Controls

- **Positive control — GroEL** (PMM1436 / cyanorak CK_00008054). Must populate every
  angle and classify as `function_rescued` at **high** grade (cross-genus COG0459 +
  pfam PF00118 + groES neighbor + chaperone cluster). If the pipeline can't recover a
  known gene cleanly, it isn't trustworthy on the dark ones.
- **Absence control — CK_00003473** (*Prochlorococcus*-specific secreted). Should get
  **no** cross-organism rescue (single-genus to Bacteria level) → `lineage_novelty` /
  `surface_secreted`, confirming the pipeline does not over-call function.

## Driving examples (step 4 methods)

Both, per researcher choice:
- **CK_00000498 (iscA)** — clean end-to-end function-rescue; tests homolog↔context
  concordance (rescue should agree with FeS context).
- **CK_00000141 (secreted)** — the hard case: MED4 paralogs (PMM0872, PMM1028),
  neighborhood coherence, neighbor ∩ cluster overlap, signal peptide, lineage-restriction.

## Expected outcome

A 14-row dossier table + per-family cards + an interactive dashboard section. Each
family carries a graded lead. Expectation (to be tested, not assumed): a minority
function-rescued (incl. iscA), several with neighborhood / co-expression leads, and a
set of lineage novelties (incl. CK_00003473) — each labeled with how far the KG could
take it and how much to trust that.

## Decisions

- **2026-06-16 — Convergence across angles is the primary lead signal.** Expanded with
  the researcher during co-define beyond the initial three (neighbor∩cluster, neighbor
  pathway coherence, homolog↔context concordance) to add Tier-1 phyletic profiling and
  KG-scale co-response similarity and operon triple-convergence, plus Tier-2 secretion
  and pangenome-context; Tier-3 signals computed opportunistically. Full tiered list in
  the convergence-layer section above.
- **2026-06-16 — Co-response similarity is computed on fine-grained per-(experiment ×
  timepoint) log2FC, not `direction_by_treatment`.** Researcher's point: the
  per-treatment direction roll-up pools experiments/timepoints and hides whether two
  genes co-respond in the *same* condition. The raw matrix is re-pulled from alpha.6;
  correlation runs on shared measured datapoints (guarding structured significant-only
  missingness) and on response shape (guarding the breadth coverage-confound). The
  carried `direction_by_treatment` remains only as the human-readable summary.
- **2026-06-16 — Every dossier field is tagged hard/soft**, and leads resting on soft
  (majority-vote) labels alone are graded low. Driven by researcher caution on
  descriptive cluster/OG labels.
- **2026-06-16 — Mechanistic angles (neighborhood, co-expression, sequence, derived
  metrics) are anchored on a single representative strain** (MED4 if the family is
  present there, else the best-covered strain), because co-expression/derived-metric
  data is concentrated in MED4. The DE fingerprint and homolog conservation remain
  family-level (all strains). Carried as a limitation.
- **2026-06-16 — Conserved synteny is checked across strains** (not just the rep contig)
  for the neighborhood angle; operationalized in the step-4 module.

## STATUS: co-define IN PROGRESS — proposal NOT yet locked (paused 2026-06-16)

Step 3 is **not closed**. The framing below is a working draft; the decide gate has
**not** been passed. Three refinements were agreed with the researcher in principle
during co-define but are **not yet written into the schema / pseudocode / decisions** —
they are the first task next session, before the proposal is locked.

### Open items — continue 2026-06-17

1. **Per-member, not "representative gene."** Drop the single-rep anchoring for the
   mechanistic angles. Pull **per-member across strains** for neighborhood, sequence
   features, and cluster membership; **aggregate to family-level with counts** ("signal
   peptide in 14/15 members", "neighbor `valS` adjacent in 12/15 strains"). Co-response
   and phyletic run at family level (ortholog DE / full presence vector). Derived metrics
   stay MED4-anchored *by necessity* (most are MED4-only studies) but labeled by strain;
   pull per-member to catch the few that exist off-MED4. The "conserved across N/M
   members" counts feed directly into the evidence grade (consistency = hard evidence).
   The rep survives only as a display anchor + fallback. → update schema (`rep_*` →
   per-member + count fields), pseudocode, and add a decision.
2. **Full ortholog ladder, not just the broadest group.** Q1 reads **every rung**
   (cyanorak curated + eggnog Prochloraceae→Cyanobacteria→Bacteria), not only the widest.
   Gives: (a) conservation depth = where genera stop widening — read by **genera, not the
   level name** (e.g. eggnog `3486D@2` is labeled "Bacteria" but is *Prochlorococcus*-only);
   (b) the most informative label wherever it sits on the ladder; (c) a cross-rung
   **consistency check** (rungs agree → trust rescue; disagree → over-merge caution);
   (d) within-Prochlorococcus vs across-bacteria conservation as two separate counts.
   `gene_homologs` already returns all rungs in one call — just drop the `broadest` filter.
   → update Q1 pseudocode + homolog schema fields.
3. **Fine-grained co-response** (already written into the convergence section + decisions):
   confirm the missingness + shape guards survive the per-member/family-level reconciliation.

Once these three are folded in, re-present the consolidated framing and lock the proposal
(steps 1–3), then start step 4 on the two driving families (CK_00000498, CK_00000141).

## Decide-gate checklist (DRAFT — gate not yet passed)

- **Outputs produced** — `data/dossier_schema.csv` (working column spec); this notebook.
- **Results presented** — schema, convergence layer, evidence-hardness rule, lead
  taxonomy, controls, driving examples (shown in chat and recorded here).
- **QC gate** — schema columns each map to a probed-and-confirmed tool (step 2 coverage
  map); positive (GroEL) and absence (CK_00003473) controls defined with expected
  classifications; evidence-hardness tags assigned to every field.
- **Decisions made this step** — convergence as primary signal; hard/soft tagging;
  single-rep-strain anchoring; cross-strain synteny (all dated 2026-06-16, above).
- **Advance rationale** — NOT YET. The schema and convergence layer are well developed
  and fillable from confirmed tools, but the three open items above must be folded in
  before the proposal locks. This commit is a co-define checkpoint, not a closed step.

---

**Proposal lock (steps 1–3):** question locked (step 1), KG entries confirmed (step 2),
framing **in progress** (this step — not yet locked; see Open items). Steps 4–6 do not
start until the framing locks.
