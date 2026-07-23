# Methods milestone — notebook

Owner: main thread. The coding subagent authored `scripts/`, `data/`, and a
factual run-manifest; the main thread verified the real files and wrote every
interpretive section here.

## Context

First methods task: build the "parts list" — genes → systems → modules — for both
strains, subset-first with QC (co-defined 2026-07-23). This entry covers **step 1
(identify transporter genes, both strains)** plus a **first-pass anchor system
reconstruction** (raw material for iterating the grouping rule). No substrates
resolved, no groupings finalized — those stay with the researcher.

Delegation note: the first subagent dispatch overflowed its context on a large
enumeration result and died without writing artifacts (see
`../gaps_and_friction.md`); a second dispatch, scripted results-to-disk via the
package Python API, succeeded.

## What I did

Scripts (in `scripts/`, run with the repo venv):
- `01_enumerate_transporters.py` → `data/transporter_genes.csv` (1381 rows),
  `data/qc_aromatic_importers.csv` (12 rows)
- `02_anchor_neighbors.py` → `data/anchor_neighbors.csv` (45 rows)

KG release 0.1.0-alpha.6 (verdict `ok`, 16/16). Organisms confirmed via
`list_organisms`: `Alteromonas macleodii HOT1A3` (prefix `ACZ81_`, 4028 genes),
`Alteromonas macleodii EZ55` (prefix `EZ55_`, 4136 genes).

Enumeration = union of four sources per gene (BRITE `ko02000`; KEGG-KO leaf-name
transporter regex; TCDB; `genes_by_function` keyword search with **no** category
filter, per the earlier friction). Per-gene source booleans kept.

**Main-thread verification** (not from the subagent): re-ran the per-source counts
from the CSV — they match the manifest exactly. Ran a direct Cypher check of KO
presence in HOT1A3 for the anchors + the proposal's cited substrate KOs (see
Surprises).

## Results

**Transporter enumeration — union of 4 sources (verified against the CSV):**

| Strain | BRITE | KEGG-KO | TCDB | annotation | **union** |
|---|---|---|---|---|---|
| HOT1A3 | 310 | 283 | 427 | 534 | **684** |
| EZ55 | 320 | 293 | 437 | 550 | **697** |

- BRITE HOT1A3 = 310 matches the proposal's ~310 anchor.
- Sole-source contributions (HOT1A3): BRITE-only 1, KEGG-only 11, TCDB-only 75,
  annotation-only 222. Annotation search is the widest net; TCDB adds ~75 not
  caught elsewhere; BRITE ⊂ (KEGG ∪ TCDB) almost entirely.

**Aromatic / xenobiotic scan (`qc_aromatic_importers.csv`):** 5 HOT1A3 / 7 EZ55
keyword hits, but reading the annotations, most are **not** carbon importers:
- HOT1A3: `benE` benzoate:H⁺ symporter (`ACZ81_03335`) is the only genuine
  aromatic-substrate importer; `aroE` (shikimate dehydrogenase, an enzyme),
  `tyrR` (regulator), and 2× `fiu` (catecholate-siderophore receptors — iron) are
  keyword false-positives.
- EZ55: `benE` + an MFS `benK`/`xylE` (`EZ55_04028`), ~2 genuine; `fadL`
  fatty-acid channel and the same enzyme/regulator/siderophore false-positives.
- **Net genuine aromatic importers ≈ 1 (HOT1A3), ≈ 2 (EZ55)** — confirms the
  proposal's "HOT1A3 aromatic prong near-vacuous."

**Anchor system reconstruction (HOT1A3, `anchor_neighbors.csv`):**
- **Fe³⁺ ABC — clean.** `ACZ81_00580` (substrate-binding, K02012) / `_00585`
  (permease, K02011) / `_00590` (ATP-binding, K02010), all `+` strand, consecutive,
  tiny gaps, all TCDB `3.A.1.10`. Flanking genes (hypothetical `_00575`, oxidoreductase
  `_00595`) are clearly not part of it. **Adjacency reconstruction is viable** — the
  boundary rule must stop cleanly at `_00580`/`_00590`.
- **Single-gene 2.A carrier — confirmed.** `benE` `ACZ81_03335` (K05782, TCDB
  `2.A.46.1`) is a single-polypeptide secondary carrier; no co-transporter subunits
  among its neighbors. Validates the single-gene-system path.
- **`livKHMGF` and glutamine — see Surprises** (both undercut proposal anchors).

## Results — anchor iteration v2 (Pfam roles + real cassettes)

Pfam-based `role_from_pfam` (in `anchor_neighbors_v2.csv`) resolved every previously
ambiguous transporter-subunit role; only genuine non-transporter neighbors stay
other/unclear. Verified against the KG directly (not just the subagent CSV):
`03915` → sensor-kinase (HisKA/Hpt/Response_reg), `03360` PhoR → sensor-kinase,
Fe³⁺ `00580/85/90` → SBP_bac_6 / BPD_transp_1 / ABC_tran+TOBE_2.

**Two real full-cassette organic-C anchors found** (`candidate_cassettes.csv`),
replacing the non-existent `livKHMGF`. KG-verified coordinates/strand/Pfam/TCDB:

**Cassette 01 — `ACZ81_05440–05460`, strand −, TCDB `3.A.1.5` (peptide/oligopeptide):**

| locus | role (Pfam) | intergenic gap to prev |
|---|---|---|
| 05440 | ATP-binding (ABC_tran+oligo_HPY) | — |
| 05445 | ATP-binding (ABC_tran+oligo_HPY) | 0 bp |
| 05450 | permease (BPD_transp_1+OppC_N) | 2 bp |
| 05455 | permease (BPD_transp_1) | −13 bp (overlap) |
| 05460 | substrate-binding (SBP_bac_5) | 60 bp |

→ **1 SBP + 2 permease + 2 ATPase, 5 consecutive loci, one strand** — the
multi-permease *and* multi-ATPase structure the repeated-role tiebreaker targets.
sap/dpp peptide family. **This is the primary boundary-rule anchor.**

**Cassette 02 — `ACZ81_14220–14235`, strand +, TCDB `3.A.1.5`:** 1 SBP + 2 permease
+ 1 ATPase (nik/opp family; `nikA/B` naming carries a nickel-vs-peptide substrate
ambiguity — a good multi-substrate test case, but cassette 01 is the cleaner anchor).

Subagent self-reported + fixed two script bugs (TCDB substring `3.A.1.1`→`3.A.1.10/16`
matching → digit-boundary regex; pandas `Series.product` collision → `r["product"]`);
final CSV re-verified clean, only genuine `3.A.1.5` cassettes remain.

**Boundary-rule material (for the researcher gate):** adjacency = consecutive loci,
same strand; observed within-cassette intergenic gaps range −13 to 60 bp with no
intervening non-member; repeated ATPase/permease roles co-occur in one real system
(cassette 01) sharing substrate/family → must not split.

**Rule refinement (researcher, 2026-07-23) — non-transport genes are *permeable*,
not stops.** A neighboring **catabolic enzyme must not break the cassette**: transport
operons co-locate the substrate's catabolic genes (that co-location *is* the module),
and we already surface catabolic neighbors and route them to the breakdown side — so
they can't also act as a wall (else `SBP—permease—[enzyme]—ATPase` would drop the
ATPase). Revised: the transport **system** = consecutive same-strand genes with a
transport Pfam role (SBP/permease/ATPase) sharing a substrate/family; interleaved
non-transport genes (catabolic, accessory, regulator, hypothetical, sensor kinase)
are **surfaced + tagged but permeable** — the grouping reaches across them to same-
family transport subunits (catabolic-same-substrate → breakdown side). **A co-located
catabolic enzyme is dual-purpose (researcher, 2026-07-23):** besides the breakdown
flag, it is **substrate-confirmation evidence for the transporter** — a catabolic gene
for compound X next to the transporter supports that the transporter carries X. This
feeds the substrate-resolution step as the "genomic neighbours" source already in
decision 6, and is most valuable where the transporter's own annotation is coarse
(the common case given KO sparsity). Kept as a **confident-vs-inferred** signal — a
co-located enzyme is strong but not proof (mixed operons, coincidental neighbours), so
a neighbourhood-inferred substrate is tagged *inferred*, not asserted at KO/product
confidence. Real **STOP**
conditions: strand flip; a transport subunit of a **different substrate/family** (new
system); or a **reach bound** (only a few intervening non-transport genes / a few
hundred bp with no further same-substrate transport subunit — guards against merging
an unrelated adjacent operon). To be QC'd on a system that actually interleaves
catabolic genes (e.g. a co-operonic sugar-utilisation operon).

## Results — grouping-rule QC + a transporter-inventory reveal (2026-07-23)

The grouping rule was implemented as a walker and applied genome-wide over all 29
HOT1A3 Pfam-SBP anchors (`cassettes_qc.csv`, 15 featured systems). **Rule behaved
correctly:** 6 complete cassettes grouped (SBP+permease+ATPase, stops at real
boundaries), every orphan SBP correctly refused, the 2-permease/2-ATPase peptide
cassette not split (tiebreaker held), no over-merge, no subunit left unresolved. livK
correctly stops at the sensor-kinase `03915`. The rule is **validated and lockable.**

**But the QC surfaced a genome fact that reshapes the catalog** (KG-verified, not an
adjacency artifact):

| HOT1A3 transporter inventory | count |
|---|---|
| substrate-binding proteins (SBP) | **36** (16 are SBP_bac_3 polar-AA) |
| import permeases (BPD_transp + FecCD) | **11** |
| ABC ATPases (ABC_tran, incl. non-import) | 39 |
| secondary carriers (TCDB 2.A.x, single-polypeptide) | **85** (12 MFS) |

- **36 SBPs vs only 11 import permeases** → most ABC SBPs are **orphan** — there
  aren't enough permeases to pair with them. ~8 of the 11 permeases are consumed by
  the 6 complete cassettes.
- **Complete multi-subunit ABC cassettes exist only for peptide + inorganic** (Fe,
  nitrate/bicarbonate, molybdate, ynjBCD; sap/dpp + nik peptide). **Every sugar and
  amino-acid SBP tested is orphan** (1 sugar SBP; 16 polar-AA SBP_bac_3, several
  annotated "amino acid transport **signal transduction**" — some may be sensory,
  coupled to two-component kinases like the `03910`/`03915` pair, not uptake).
- **85 secondary carriers** (single-gene 2.A.x) are a large pool — the likely route
  for much sugar / amino-acid / organic-acid uptake, all single-gene by nature.

**Implication (the reveal):** for HOT1A3 **organic carbon, single-gene units are the
norm, not the edge case** — orphan SBPs + 85 secondary carriers. Multi-subunit
complete cassettes are the exception (peptides + the inorganic controls). This
inverts the proposal's "counting unit = multi-subunit transport system" emphasis
(single-gene was the handled-but-special tier). Two consequences to bring to the
researcher: (1) the single-gene special-care rules become the **main** path for the
organic-C catalog; (2) a **structural annotation bias** — peptides get full-cassette
multi-gene coherence while sugars/AAs get thin single genes, so "peptides look
stronger" may be an annotation artifact, not biology, and must be flagged. Note also:
for an orphan SBP the binding protein is the substrate-specific, most-regulated
component, so scoring it is biologically sound despite being single-gene.

## Results — full parts list built (both strains) + curation need (2026-07-23)

`parts_list.csv` (694 HOT1A3 + 708 EZ55 gene-rows; 674 / 688 systems, 664/678
single-gene). Carrier types (HOT1A3): 21 ABC-cassette-complete (6 systems), 33
ABC-orphan-SBP, 44 secondary-carrier, 36 other-permease, **560 "other"**.

**Core carbon-candidate set (clean carriers, organic-C/dual-C+N): 44 genes / 36
systems** — interpretable: 2 peptide cassettes (dipeptide S0023, peptide/nickel
S0047), ~11–15 polar-AA orphan SBPs, livK (BCAA), ~10 sugar/organic-acid secondary
carriers (maltose, L-fucose, sugar MFS, glycoside), benzoate (benE). 23 confident / 21
inferred.

**But the automated classification has both false-positives and false-negatives — a
curation pass is needed (verified by reading the file):**
- **False-positives in the candidate set:** LacI-family transcriptional **regulators**
  (`ACZ81_11860`, `nagR` `14500`) mis-tagged `substrate-binding importer` because their
  sugar-binding domain shares the SBP fold; an **enzyme** (`08295` diguanylate cyclase);
  **exporters** — `importer_vs_exporter` caught 4 (msbA lipid-A, sugar-efflux, araJ
  arabinose-efflux) but role/product must catch the regulator/enzyme class it misses.
- **Genuine importers hiding in "other" (false-negatives, need rescue):** `cudT` (BCCT
  osmolyte betaine/choline/carnitine), `sglT` (Na/sugar symporter), `01580`
  (nucleoside/LacY sugar symporter), `dtpT` (peptide POT/MFS) — real secondary carriers
  that lack a clean TCDB `2.A.x` tag. Mixed in "other" with true noise (Tat translocase,
  Mla lipid-asymmetry, PTS regulatory proteins, GST/shikimate enzymes, regulators).

So the mechanical pass is a **draft**; the substrate-resolution audit's core job — a
curation pass (systematic filters to drop regulators/enzymes/exporters/non-uptake
families; rescue genuine carriers from "other" by family: BCCT, POT, Na-solute
symporter, MFS sugar), then main-thread review of the residual — sets the real
organic-C candidate module list. Provisional-tag choice by the subagent: peptide
cassettes tagged **dual-C+N** (carbon-bearing) not inorganic despite the peptide/nickel
family ambiguity — reasonable for a carbon analysis, main thread confirms.

## Surprises

**1. The KG's KEGG-KO annotation for HOT1A3 ABC transporters is coarser than the
proposal's examples imply — several cited substrate anchors are ABSENT in HOT1A3.**
Direct Cypher check (`Gene_has_kegg_ko` → `KeggTerm`, HOT1A3):

| KO | substrate/role | HOT1A3 genes |
|---|---|---|
| K02012 / K02011 / K02010 | iron(III) binding / permease / ATPase | 1 / 1 / 1 ✓ |
| K01999 | livK (BCAA binding) | 1 ✓ |
| **K01997 / K01998** | **livH / livM (BCAA permease)** | **0 / 0** |
| **K01995 / K01996** | **livG / livF (BCAA ATPase)** | **0 / 0** |
| **K10036 / K10037 / K10038** | **glutamine glnH/P/Q** | **0 / 0 / 0** |
| **K10552** | **fructose frcB** | **0** |
| **K05845** | **osmoprotectant opuC** | **0** |

The proposal (`proposal_notebook.md:209`) listed glutamine/fructose/osmoprotectant
KOs from the **ontology's transport-term list** (proof the KO *names* carry
substrates) — not a check that HOT1A3 carries genes for them. In HOT1A3 the KG
often annotates only the **substrate-binding** subunit of an ABC system (iron
K02012, livK K01999) and leaves permease/ATPase subunits without a specific KO, or
annotates uptake generically (polar-amino-acid `K02030`, 7 paralogs — the glutamine
"module" is not KO-resolvable as glutamine).

Consequences for the parts-list build:
- **Decision 7's `livKHMGF` worked example does not exist in HOT1A3.** The
  repeated-role tiebreaker (livH/M both permease, livG/F both ATPase) can't be
  validated here — those genes aren't annotated. We need a **different real
  multi-subunit anchor** whose permease/ATPase subunits actually carry roles, or to
  re-anchor the rule.
- **Component-role-from-KO (decision 7) will frequently be unavailable.** Grouping
  will lean more on adjacency + product/COG/`function_description` keywords than on
  KO names. The `livKHMGF` neighbourhood shows this: `_03910` (substrate-binding,
  no KO), `_03915` (annotated "ATP-binding protein / Histidine kinase" — ambiguous,
  likely a two-component sensor kinase, **not** a transport ATPase), `_03920`
  (livK). Two substrate-binding proteins adjacent, no clear permease, no clear
  transport-ATPase.
- **Substrate resolution will land coarser than the proposal's examples suggest** —
  consistent with the proposal's own "annotation-limited and empirical" caveat, but
  sharper. The substrate-resolution audit should expect this.

**1b. Resolution (researcher suggestion 2026-07-23): use `gene_summary` +
`alternate_functional_descriptions` — they largely recover what the KOs miss.**
These fields are **100% populated** in HOT1A3 (`gene_summary` 4028/4028,
`alternate_functional_descriptions` 4028/4028, `function_description` 3555/4028) and
are **source-tagged** (`[ncbi]` / `[eggnog]` / `[pfam]` / `[protein_family]`). The
**Pfam domains give component role directly**, independent of KO:
- Fe³⁺: `_00580` `SBP_bac_6` (binding), `_00585` `BPD_transp_1` (permease),
  `_00590` `ABC_tran`+`TOBE_2` (ATPase); `gene_summary` even recovered symbol `sfuB`.
- The ambiguous `_03915` ("ATP-binding protein") resolves via Pfam
  `HATPase_c/HisKA/Hpt/Response_reg/PAS_9/dCache_1` → a **two-component sensor
  histidine kinase, not a transport ATPase** — so the HOT1A3 liv neighborhood is
  `livK` (03920 binding) + an unrelated family-3 SBP (03910) + a sensor kinase
  (03915), genuinely not a reconstructable cassette (now evidenced, not guessed).
- eggNOG/COG text in these fields also carries substrate class ("branched-chain
  amino acid transport", "Fe3 transport"), often finer than the bare `product`.

**Design change:** the parts-list build should pull `gene_summary` +
`alternate_functional_descriptions` and use **Pfam domains as a primary
component-role signal** (`SBP_bac*`→binding, `BPD_transp*`/permease family→permease,
`ABC_tran`→ATPase, `HATPase_c`+`HisKA`→histidine kinase→exclude), with KO confirming
when present rather than being required. This directly mitigates Surprise 1 and
supersedes reliance on KO-role in decision 7. (Pfam is also the KG's #1
statistically-ranked ontology per the proposal, i.e. broadly populated.)

**2. The subagent's `role_first_pass` column is noisy — do not let it drive the
transport-vs-catabolic split.** It tags any gene with an enzymatic KO as
`catabolic`: e.g. `trmH` (tRNA methyltransferase), `rsmJ` (rRNA methyltransferase),
`phoR`/`phoB` (sensor kinases), and `glnA` glutamine synthetase (biosynthetic) all
land in `catabolic`. The tag means "has an enzyme annotation," not "catabolic." The
role/split logic (co-defined 2026-07-23) needs proper rules, and ambiguous cases
(like `_03915`) stop for reconsideration rather than auto-tag.

## Decisions
- **Logged 2026-07-23 (to formalize at the methods decide-gate):** component role is
  assigned **primarily from Pfam domains + eggNOG/COG in
  `alternate_functional_descriptions` / `gene_summary`**, with KO *confirming* when
  present rather than being required — because KO annotation of ABC permease/ATPase
  subunits is sparse in HOT1A3 (Surprise 1), while these fields are ~fully populated
  (Surprise 1b). This augments proposal decision 6 (substrate sources) and supersedes
  decision 7's "component role read from the KEGG KO name." Researcher: log now,
  formalize at decide.
- **Grouping rule LOCKED (2026-07-23, researcher-approved; QC-validated on 6 complete
  cassettes + all orphans):**
  - *System* = consecutive-locus, same-strand genes carrying a transport Pfam role
    (SBP `SBP_bac*`/`Peripla_BP*`; permease `BPD_transp*`/`FecCD`; ATPase `ABC_tran`)
    sharing a substrate/family. Role from Pfam primary, KO/product confirm.
  - *Neighbor-discovery*: pull in a consecutive-locus gene with a transport Pfam role
    the enumeration missed.
  - *Repeated role* (2+ permease or 2+ ATPase) does **not** split when substrate/family
    is shared (validated on the 2-permease/2-ATPase peptide cassette).
  - *Non-transport genes permeable*: catabolic/accessory/regulator/sensor-kinase are
    surfaced + tagged, reached across (not stops); catabolic-same-substrate → breakdown
    side **and** substrate-confirmation evidence (inferred-tagged).
  - *STOP* at: strand flip; a transport subunit of a different substrate/family; or a
    reach bound (~a few intervening non-transport genes / a few hundred bp — observed
    intra-cassette gaps −13 to +89 bp, so ceiling ~100–200 bp is safe).
- **Focus note, not reopen (researcher, 2026-07-23):** single-gene units are the norm
  for HOT1A3 organic-C uptake; proposal method unchanged, focus noted (added to
  proposal Known-confounders). Peptide-vs-rest annotation bias flagged.
- **Secondary carriers (85, TCDB 2.A.x) INCLUDED** as candidate single-gene modules.
- **Ambiguous polar-AA `SBP_bac_3` (16) — three-bucket classification by genomic
  context (researcher-approved):** (1) **sensory** = adjacent to a two-component kinase
  /response-regulator, no permease near → exclude from carbon candidates but surface;
  (2) **transport** = permease/ATPase adjacent or in a short window → real transporter;
  (3) **ambiguous orphan** = no kinase, no permease → candidate single-gene AA module
  flagged `transport-inferred` (low confidence). DE + catabolism corroboration
  disambiguates downstream.

## Results — v2 consolidated build (validates baseline; adopted canonical)
`parts_list_v2.csv` (full audited table, `class_`/`class_reason` per gene) +
`candidates_v2.csv`. Class tally (HOT1A3): other 218 (was 560), exporter 133,
machinery 86, enzyme 75, carrier-family 60, transport-role 59, regulator 53,
secondary-carrier-unresolved 7, sensory 3. **Diff vs baseline (main-thread-verified):
0 substrate changes; 65 "changed" = family renames only (e.g. gluconate→SLC13,
nucleoside/nucleobase split); +10 ADDED (were baseline `reconsider`); −1 REMOVED
(`EZ55_03440` bare MFS, no substrate → correctly set aside).** Retention confirmed:
the over-exclusion bug fix kept amino-acid ABC `00185/00190` and orphan SBP `02465`.
Anomaly fixes verified sensible (fecA ferric-citrate→inorganic; capsule-export
excluded; flank-export restricted to member-only).

**Candidate set v2: HOT1A3 57 systems / 65 genes; EZ55 59 / 67** (after set-asides +
the critic's `crr` PTS-EIIA drop, 2026-07-23; `reference_class=candidate`). Families:
APC 15, ABC-subunit 12, secondary-carrier-organic 8, gluconate/organic-acid 6, BCCT 4,
SSS 4, MFS-sugar 4, NCS-nucleobase 4, nucleoside-Nup 3, SLC13 2, POT/hcaT/TRAP/glycerol/
fatty-acid 1 each. Mostly single-gene (56 single / 3 multi).

**Dispositions (2026-07-23):**
- **Set aside the "antimicrobial-peptide" ABC** (`18465`/`18470`; `EZ55_03813`): KO
  K02003/K02004 = *putative* ABC (substrate unresolved), function ambiguous (peptide
  uptake vs antimicrobial-peptide resistance/efflux), and the two subunits split across
  system_ids (permease Pfam unrecognized → `other`) — not a clean candidate. Removed
  from the scored set, surfaced. (This is the one v2 addition reversed.)
- **Open call — TonB-dependent iron receptors** sit in class `other`, so the inorganic
  control set is currently 27 confident/6 inferred (genuine ABC/secondary-carrier
  inorganic importers only). Whether to fold TonB-Fe receptors into the inorganic
  control class is a researcher call (they are iron uptake, but a different
  transporter class).

## Decision — four reference classes + size-aware scoring (researcher, 2026-07-23)

System-size distribution (verified from `parts_list_v2.csv`): **candidates 95%
single-gene** (mean 1.14; only 3 multi — the 2 peptide cassettes + one 2-gene);
**inorganic-ABC control 72% single** (mean 1.50; 22% are 3-gene cassettes — Fe,
nitrate, molybdate, ynjBCD). The complete multi-subunit cassettes in this genome are
mostly inorganic → a direct candidate-vs-control contrast is size-confounded.

**TonB receptors (67 HOT1A3, all single-gene, 0 organic).** By the scorer's
`assign_reference_class` (the single source of truth, written to `reference_class` in
`parts_list_v2.csv`; corrected per the methods critic, 2026-07-23): **26 control-TonB**
(iron/siderophore keyword), **40 ambiguous-TonB** (bare "TonB-dependent receptor", no
resolved substrate → correctly the control-for-the-control), **1 interaction-coupled**
(btuB-B12). Folding the iron-TonB into the control still shifts it toward single-gene
(all TonB are single-gene), nearly matching the candidates' 95% → fixes the size-match;
the bare-substrate TonB deliberately fall to ambiguous-TonB rather than inflating the
clean control.

**Four reference classes, tracked separately:**
1. **candidates** — organic-C carbon-source candidates (test).
2. **control-ABC** — inorganic ABC/secondary-carrier importers (holds the multi-gene
   inorganic cassettes → size-partner for the multi-gene candidates).
3. **control-TonB** — iron/siderophore TonB receptors (single-gene → size-partner for
   the single-gene candidates). `btuB`-B12 / heme carved out as **interaction-coupled**
   (B12 is a known Proch–heterotroph exchange currency), like the proposal's N/P.
4. **ambiguous-TonB** — bare TonB, unknown substrate — **a control-for-the-control.**
   TonB receptors are a coordinately-regulated class (Fur/iron-starvation regulon); if
   ambiguous-TonB moves *with* iron-TonB, the TonB-control signal is class-regulon not a
   clean carbon-negative → caution. If both flat, control is clean. Tracked/reported,
   never in the candidate catalog nor used to bound the FPR.

**Size-aware scoring (confirmed, already in proposal):** multi-gene system percentile =
median of subunit percentiles; single-gene = thinnest tier, **subunit-count-matched
null** (single-gene nulled against random single genes), gene count + source `padj`
travel. Size-classes line up: single-gene candidates ↔ control-TonB; multi-gene
candidates ↔ control-ABC. Genome-wide same-size null stays the primary significance
test; the control contrasts are secondary/supportive.

## Decision — fix-and-rerun the build as one clean pipeline (researcher, 2026-07-23)
The build→curate split dropped 86% of the enumerated set (599/694) and rescued 29
genuine carriers from "other" — i.e. the classifier was doing too little and the
curation too much (recall dependent on the rescuer's imagination). Folding the
carrier-family recognition + exclusion rules + direction rule into a single
classified build makes the pipeline reproducible and defensible ("enumeration ≈
transporters"). Rerun expected to reproduce ~the current 54-system candidate set
(validation), possibly catching a few more; the current `parts_list.csv` /
`curated_candidates.csv` are kept as the **diff baseline**. Reconsider dispositions
locked: keep `hcaT` (3-phenylpropionate, aromatic-acid importer — feeds the aromatic
prong); drop `rhtA`/`ywfM`/`rarD`/`yigM` (efflux/drug/vitamin); set aside the ~18
substrate-AND-direction-unresolved MFS/DMT superfamily permeases (surfaced, excluded
from scored catalog, counted for the coarse-module falsification check).

## Scoring machinery — scope findings + build decisions (researcher-approved 2026-07-23)
- **Score = up-percentile (rank/N), kept** — N-normalized so scores are comparable
  across experiments differing ~10× in gene count (HOT1A3 3947 vs EZ55 ~350); within
  an experiment it's identical to rank.
- **Multi-system modules exist** (verified): HOT1A3 35 single-system + 7 multi-system —
  polar amino acid 6 systems, solute:Na+ 3, nucleobase 3, betaine/sugar-MFS/peptide 2.
  So module=max-over-systems is real, and the **matched (same-size) null** matters for
  the big modules (best-of-6 edge cancels). **Module-assignment rule (decision 12):**
  resolved-class labels (e.g. "polar amino acid") merge into one broad module flagged
  with system count; **`unresolved` systems each = own coarse module, never merged.**
- **EZ55 partial-coverage scope = tiny** (verified vs the EZ55 DE tables): of ~10
  multi-subunit systems, only 1 (`S0031`, inorganic control) has any subunits in the
  EZ55 presence contrasts (3/3 at 400 ppm, 1/3 at 800 ppm); every candidate
  multi-subunit system has **0** EZ55 coverage (peptide signal lives in HOT1A3). So the
  deferred rule is a minor edge case → **score on present subunits, present-count
  flagged, ≥1 present to score** (no threshold needed).
- **Toy test exercises:** tied `log2fc` (average-rank tie-handling), single-gene system,
  multi-subunit system, multi-system module (max-over-systems), a control class, and
  partial coverage — all checked against hand computation (TDD).
- Breakdown-flag: stub interface + toy-test the ORA read-off; map selection deferred to
  the analysis milestone. Scorer is built + toy-tested here, **not** run on real DE.

## Results — scoring machinery built + toy-tested (TDD), math verified (2026-07-23)
`scripts/scoring.py` + `scripts/test_scoring.py` (27 pass). **Main-thread verification
(re-derived by hand, not "tests pass"):** percentile-with-tie (g06=g07=6.5/12 ✓); BH
example q=[.005,.020,.05125,.05125,.9] exact ✓; matched-max null — a k=3 system's
median can't reach 1.0 so p hits the floor while a k=1 can (p=1/12), i.e. the
**subunit-count-variance matching genuinely works** ✓; decision-12 module build
(resolved-class merges → broad; `unresolved` each own module ✓).

**Bug caught + fixed (anomaly-catch — tests were green but wrong on real input):**
`assign_reference_class` used `bool(row["in_candidate"])`; the real CSV stores the
**string** `"False"`, and `bool("False")` is truthy → on real data every system would
collapse to `"candidate"`, destroying the reference-class structure. The 27 tests
passed only because the fixture used Python booleans. Fixed to parse the string
(`str(...).lower()=="true"`); fixture changed to the CSV string form so it guards the
regression; re-verified (inorganic control → `control-ABC`), 27 pass. Logged to
`gaps_and_friction.md`.

**Minor spec conventions the subagent resolved (researcher to confirm):** (a)
up-percentile = rank/N so most-down = 1/N (≈0), not exactly 0 — harmless for
ranking/null/FDR (monotonic); (b) `broad` = module holds >1 system. Breakdown
map-selection is a stub (deferred to analysis); only the ORA read-off is toy-tested.

## Decide-gate checklist (methods milestone)

**Outputs produced** (`methods/scripts/`, `methods/data/`):
- `01_enumerate_transporters.py` → `transporter_genes.csv`, `qc_aromatic_importers.csv`
- `02_anchor_neighbors.py`, `03_anchor_annotate_pfam.py` → `anchor_neighbors.csv`, `_v2.csv`
- `04_candidate_cassettes.py` → `candidate_cassettes.csv`
- `05_cassettes_qc.py` → `cassettes_qc.csv`
- `06_build_parts_list.py` → `parts_list.csv`, `qc_parts_list_summary.csv`
- `07_curate_candidates.py` → `curated_candidates.csv`, `qc_curation_summary.csv`
- `08_build_parts_list_v2.py` (**canonical**) → `parts_list_v2.csv`, `candidates_v2.csv`,
  `qc_v2_summary.csv`, `qc_v2_diff.csv`
- `scoring.py` + `test_scoring.py` (**27 pass**) + `qc_toy_test_report.txt`
- Run: `.venv/bin/python <script>`; tests `.venv/bin/python -m pytest scripts/test_scoring.py`

**Results presented** (tables inline above): enumeration counts (684/697); transporter
inventory (36 SBP / 11 permease / 85 secondary carriers); candidate set (57 HOT1A3 / 59 EZ55 systems,
95% single-gene) with family make-up; system-size distribution test vs control; v2 diff
(0 substrate changes, +10/−1).

**QC gate** (check → result):
- Per-source enumeration counts reconcile with the CSV → match; BRITE=310 = proposal anchor.
- Grouping rule QC on 6 complete cassettes + all orphans → grouped/refused correctly; tiebreaker held; no mis-group.
- v2 vs baseline diff → 0 substrate changes; additions/removals all legitimate; real amino-acid systems retained.
- Scorer math re-derived by hand → tie percentile, BH example, matched-null subunit-count-variance all correct.
- Anomaly-catch → `assign_reference_class` `bool("False")` bug (would collapse all classes to candidate); fixed + fixture made realistic; 27 pass.
- KG spot-checks → KO absences (glutamine/liv), TonB substrates, cassette coordinates all verified against the KG directly.

**Decisions made this milestone** (prose above, dated 2026-07-23): Pfam-role primary /
KO-confirms; grouping rule locked; single-gene-dominance focus note (→ proposal);
`livKHMGF` re-anchored (peptide cassette); curation + fix-and-rerun to v2 canonical;
four reference classes + ambiguous-TonB control-for-the-control; size-aware scoring;
score = up-percentile (rank/N); EZ55 partial-coverage = score-on-present; module
decision-12 (unresolved = own module); antimicrobial-peptide ABC set aside.

**Advance rationale.** The parts list (`parts_list_v2`, canonical, auditable) and the
toy-tested scorer are both built and independently verified; the machinery the proposal
committed to is implemented and math-checked, with no real DE run performed (that is the
analysis milestone). Ready to close on researcher approval after the critic pass.
