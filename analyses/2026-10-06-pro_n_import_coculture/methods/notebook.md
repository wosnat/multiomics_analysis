# Methods milestone — notebook

*Owned by the main thread. Mechanical sections paste the coding subagent's run-manifest verbatim;
interpretive sections are written here with the researcher.*

## Context

The Plan commit (`7bca4cc`) locked `proposal.md`. This milestone implements §3.2 steps 1–6 as an
organism-agnostic module (`methods/n_transport.py`), surfacing every N-containing substrate of
every transport system, with flag columns and no filtering. It runs on MED4, MIT9313 and NATL2A
and builds the non-N import systems as the reference. **No expression data is pulled in this
milestone.** Class groupings, tier boundaries and which neighbours join are agreed at this
milestone's decide gate, from annotation only.

## Co-define (agreed 2026-10-07)

**Scope:** the module + toy tests + per-strain output tables (systems; system × subunit ×
substrate with flags; candidate neighbours; QC validation checks from proposal §3.4; audit of
which round-1 workarounds are still needed).

**Researcher's additions to the plan:**
- *Step-by-step pilot before scaling.* "We've seen before that sometimes false results come
  because the API was called / accessed incorrectly." After the toy tests, build the pipeline one
  step at a time on known MED4 systems, checking each step against expected outcomes before
  moving on:
  - pilot cases: cyn PMM0370–0373; urt + urease PMM0963–0974; `amt1` PMM0263; dpp
    PMM1049/1048/0421/0192 (split across loci); pst PMM0710, PMM0723–0725 (non-N); `salY`
    PMM0913 (ABC superfamily only); `fadD` PMM0402 (TCDB call on a non-transporter);
  - steps: 1 collect transporter genes · 2 Pfam roles · 3 group into systems · 4 neighbours ·
    5 substrates + flags · 6 evidence profile.
- *Judgment calls after the pilot:* how to surface inherited superfamily rows, and the
  neighbourhood window, are decided once the pilot shows real sizes.

**Agent split (agreed):**
- **Coder:** one persistent subagent; TDD; returns scripts, data, raw API samples and a manifest;
  draws no conclusions.
- **Verifier:** an independent subagent, MCP only, never sees the code; builds an answer key for
  the pilot cases.
- **Main thread:** compares every pilot step to the answer key; mismatches stop the build and are
  classified as API misuse / code bug / real data difference.
- **On mismatch:** `systematic-debugging` by the coder.
- **Before scaling:** one API-usage code review against `docs://guide/python_api`.
- **At the end:** the methods critic (automatic, since this milestone emits data).

## What I did

### Toy tests (coder phase 1, 2026-10-07)

`.venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/methods/tests -v`
→ `Ran 40 tests ... OK` (re-run by the main thread: 40/40 OK; after the step-1 module change, 43/43).
Fixtures are CSV text read with `pd.read_csv(io.StringIO)`; the string-`"False"` trap is tested on a
`dtype=str` column. Module `methods/n_transport.py` v0.2.0. Full manifest:
`methods/data/coder_manifest_phase1.md`.

### Answer key (verifier, 2026-10-07)

An independent MCP-only agent (never saw the code) built `methods/data/answer_key/`
(`pilot_answer_key.md`, `pilot_genes.csv` 27 rows, `pilot_substrates.csv` 97 rows), from 27 MCP
calls.

### Pilot step 1: collect transporter genes (MED4)

`.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/p1_collect_transporters.py --organism MED4 --out-dir analyses/2026-10-06-pro_n_import_coculture/methods/data/pilot`

Run-manifest (coder, verbatim excerpt):

| source | call | total_matching (rows) | returned | pages | genes |
|---|---|---|---|---|---|
| tcdb | genes_by_ontology(tcdb, level=0) | 430 | 430 | 3 | 356 |
| brite | genes_by_ontology(brite, tree='transporters', level=0) | 87 | 87 | 1 | 86 |
| pfam_role | genes_by_ontology(pfam, 12 PFAM_ROLE_MAP ids; all found) | 46 | 46 | 1 | 42 |
| cross-check | gene_ontology_terms(27 pilot genes, [tcdb, pfam, brite]) | 93 | 93 | 1 | 27 |

Universe: 357 genes. All `genes_by_ontology` calls used `min_gene_set_size=1,
max_gene_set_size=None`. The defaults (5 / 500) silently drop small terms.

**Main-thread check against the answer key** (comparison run on `pilot/p1_med4_pilot_status.csv`
vs. `answer_key/pilot_genes.csv`):
- all 27 pilot genes present on both sides;
- Pfam domain sets identical for 27/27;
- TCDB classes consistent for 27/27 (step 1 queried at class level, the key lists leaves; the
  leaf comparison belongs to steps 5–6);
- not in the universe: cynS and ureA–G (8 genes), which the key calls enzymes. As expected.

| finding | classified as | action |
|---|---|---|
| `fadD` PMM0402 `likely_transporter = True` (key: enzyme) | rule design: a score-0, single-source class-2 TCDB hit is enough | flag made three-valued (strong / tcdb_only / none); tcdb_only surfaced for review |
| `pstS` PMM0710 role `other` (key: binding); `salY` PMM0913 `other` (key: permease) | code gap: the 12-accession seed map is incomplete (PF12849, PF02687, PF12704 missing) | step 2 builds the role map from all Pfam domains on the universe genes |
| BRITE 86 genes vs. 57 in Plan grounding item 8 | **API misuse in the Plan phase (main thread):** grounding call used the default `min_gene_set_size=5` | grounding item 8 corrected; friction logged |

Step 1: **pass**, with the two rule fixes carried into step 2.

### Pilot step 2: Pfam roles (MED4, whole 357-gene universe)

Commands (coder): `p2a_fetch_pfam_tcdb.py --organism MED4 ...` (KG fetch), `p2b_pfam_roles.py`
(no KG calls). Module v0.3.0; tests 50/50 OK (re-run by the main thread).

Run-manifest (coder, verbatim excerpt):

| call | total_matching | returned | pages | genes | terms | genes with no terms |
|---|---|---|---|---|---|---|
| pfam | 607 | 607 | 4 | 357 | 393 | 0 |
| tcdb, verbose | 597 | 597 | 3 | 356 | 277 | 1 (PMM0589, the BRITE-only gene) |

Role map built from all 393 domains by an ordered name rule (enzyme words → other; binding;
named single-carrier families; permease; ATPase; else other), with the 12 seed accessions as
overrides. One seed conflict: PF08352 (seed atpase, name rule other). Every assignment is in
`pilot/p2_pfam_role_map.csv` with the rule that decided it. Genes by role: other 274,
single_carrier 29, atpase 21, permease 19, substrate_binding 8, mixed 6 (fused exporter-type
ABC). `likely_transporter`: strong 103, tcdb_only 159, none 95.

**Main-thread check against the answer key:** gene roles match for 18/19 transporter pilot genes.
The 19th is `fadD`: key "enzyme", module "other" (the module has no enzyme role; vocabulary only).
`fadD` comes out `tcdb_only`, as the step-1 fix intended. TCDB leaf sets match for 19/19. `pstS` is
now substrate_binding (PF12849) and `salY` permease (PF02687 + PF12704).

**Carried to the decide gate (surfaced, not decided):**
- non-transport ABC proteins come out atpase/strong (`sufC` PMM0072, `ftsE` PMM0434, `uvrA`
  PMM1712, ABC-F PMM0089, `mkl` PMM0290, `modF` PMM0807, PMM0666; PF12848 named exactly "ABC
  transporter");
- the role vocabulary is ABC-shaped: ECF parts (`cbiQ` PMM0392, `bioY` PMM0914), `MlaD` (`ycf22`
  PMM0289) and fluoride exporters (`crcB1` PMM1632, PMM1631) get role `other` though BRITE calls
  them transporters (20 genes `other` by Pfam, `strong` by KO). This affects role completeness for
  those families, not the pilot N systems;
- `idiA2` PMM1164 (the §3.5 Fe marker) is substrate_binding; PMM0717 ("conserved hypothetical") is
  a permease.

Step 2: **pass**.

### Pilot step 3: group into systems (MED4)

Command (coder): `p3_group_systems.py --organism MED4 ...`. Module v0.4.0; tests 52/52 OK
(re-run by the main thread). Coordinates: `gene_details` for all 357 universe genes (357/357);
genome coordinates by a tiled `gene_neighbors` sweep (window 250, 8 calls) + `gene_details`,
giving 1,877 of 1,973 MED4 genes. A single `gene_neighbors(window=10000)` call failed with a
server `MemoryPoolOutOfMemoryError`. Of the 96 genes not covered, **91 exist in the KG with no
coordinate fields** and 5 weren't reached; none is a universe gene.

Grid run-manifest (coder, verbatim excerpt, `p3_variant_summary.csv`):

| variant | systems | role-complete | cross-locus merged systems | cross-locus edges | role-join edges | max size |
|---|---|---|---|---|---|---|
| gap100 / role on / cross on | 306 | 37 | 8 | 18 | 3 | 7 |
| gap100 / role off / cross on | 309 | 37 | 8 | 18 | 0 | 7 |
| gap200 / role on / cross on (reference) | 305 | 37 | 8 | 18 | 3 | 8 |
| gap200 / role off / cross on | 308 | 37 | 8 | 18 | 0 | 8 |
| gap500 / role on / cross on | 304 | 37 | 8 | 18 | 3 | 8 |
| gap500 / role off / cross on | 307 | 37 | 8 | 18 | 0 | 8 |
| gap200 / role on / cross off | 321 | 33 | 0 | 0 | 3 | 8 |

**Main-thread check against the answer key** (reference variant, `p3_med4_gene_systems_*.csv`):
cyn = PMM0370–0372; urt = PMM0970–0974; dpp = PMM1049/1048/0421/0192 (3 runs); `amt1` alone; pst =
PMM0710/0723/0724/0725 (2 runs; pstS→pstC 9,054 bp, 15 genes apart); `salY` alone; `fadD` alone.
**7/7 cases match, member for member**, identically in all six cross-locus-on variants (parameters
not tuned). With cross-locus off, dpp and pst split, as expected.

**Mismatch found outside the pilot, classified as a rule flaw:** `sys_PMM0065` chains six fused
ABC exporters (role `mixed`; PMM0065, 0561, 0827, 0954, 1099, 1239) through **`sodX` PMM1295**, a
protease with role `other`. Each exporter qualifies for a cross-locus join with `sodX` (both
"incomplete", role sets differ, shared `tcdb:3.A.1.106`). The ECF system chains the same way
through `cbiQ` PMM0392 (`other`). **Fix sent to the coder:** an `other`-only piece can't bridge a
cross-locus join, and a `mixed` (fused) exporter counts as role-complete. Step 3 is re-run before
step 4.

Also noted: the Mn/Zn locus (strands alternate) is labelled cross-locus though its genes are
neighbours (label only; grouping role-complete); 44 universe genes carry opposite-strand
interloper flags (flags only).

**Bears on the proposal (carried to the decide gate):** `idiA2` PMM1164 is grouped into the Fe
uptake system (`futB`–`futC`–`idiA2`, shared `tcdb:3.A.1.10`). Proposal §3.5 expected-negative 3
uses `idiA2` as the *independent* co-regulated marker to tell secondary Fe limitation from a
non-specific readout. As a member of the Fe system it isn't independent of the system it
checks, so either a different Fe marker is needed or the Fe case is "unresolved by design", like
S and Mn/Zn. Annotation-level fact, found before any expression is pulled.

Step 3: **pilot pass; genome-wide rule fix pending re-run.**

**Re-run after the fix (module v0.5.0, reference variant only).** The fix was written test-first
from CSV-text fixtures reproducing the sodX and ECF chains; tests 55/55 OK (re-run by the main
thread). The v0.4 outputs are archived in `pilot/p3_v0.4_archive/`. Diff
(`pilot/p3_ref_diff_v0.4_to_v0.5.csv`, checked by the main thread): **exactly two systems
changed**:
- the sodX chain: 7 genes → 7 one-gene systems;
- the ECF chain (`ecfA1` PMM0125, `cbiQ` PMM0392, PMM0666): 3 genes → 3 one-gene systems.

Pilot unchanged, 7/7. Reference counts: systems 305 → 313; role-complete 37 → 43 (the six fused
exporters); cross-locus joins 18 → 10, now in 6 systems (dpp, pst, Fe, Mn/Zn, lpt, and
`sys_PMM0289`, where `ycf22`'s piece also holds the ATPase `mkl`, so it isn't all-`other`).
`pilot/p3_med4_no_coordinate_genes.csv` lists 91 genes for step 4; 5 more remain unidentified.

Step 3: **pass.**

### Pilot step 4: neighbours (MED4, v0.5 systems, window ±8)

Command (coder): `p4_neighbours.py --organism MED4 ... --window 8`. Module v0.6.0; tests 60/60 OK
(re-run by the main thread; module file checked as clean UTF-8 with LF after a coder repair of a
cp1252 / doubled-CR write).

Run-manifest (coder, verbatim excerpt):

| call | total_matching / returned | pages |
|---|---|---|
| gene_ontology_terms(1684 candidates, [pfam, kegg, ec]) | 4467 / 4467 | 23 |
| gene_details(1684) | 1684 / 1684 | 9 |
| metabolites_by_gene(624 enzyme candidates, metabolism arm, N) | 2175 / 2175 | 5 (271 genes not matched) |
| list_metabolites(528 ids, verbose) | 528 / 528 | 3 |

5,137 candidate rows over 1,684 genes: context 1998, enzyme_candidate 1962, tcdb_transporter 1129,
missing_subunit 27 (9 genes), no_coordinates 21 (10 genes, none near a pilot system).

**Main-thread check against the answer key** (`pilot/p4_pilot_neighbours.csv`):
- `cynS` PMM0373 at +1, 32 bp, same strand, in the cyn run, EC 4.2.1.104, cyanate;
- `ureC/B/A` PMM0963–0965 at −7/−6/−5 on − (urt on +), EC 3.5.1.5, urea;
- `ureD` (−) / `ureE` (+) facing away, 47 bp apart;
- `pncC` PMM0257 at −6, opposite strand, 4,605 bp, EC 3.5.1.42, ammonia;
- `bioY` PMM0914 adjacent to `salY`.

Position, strand, gap and chemistry match for all four cases. Label mismatch: `tatA` PMM0374 and
`evrABC` are `tcdb_transporter` (key: context), because they belong to other systems.

| problem | classified as | action |
|---|---|---|
| 5 of 9 `missing_subunit` genes are enzymes/regulators (LysR PF03466, RmlD PF04321, TilS PF09179, MRM3-like PF22435: "substrate binding domain" names) | rule flaw: the name rule applied to domains outside the transporter-learned map | roles only from the step-2 map; neighbourhood-only domains get an unverified `role_hint` |
| `tatA`, `evrABC` and 1,129 rows labelled `tcdb_transporter` | rule precedence | new class `other_system` (member of another system) |
| nitrate `kegg.compound:C00244` and `chebi:14654` share **no** ChEBI / MetaNetX / InChIKey cross-reference, only the name | **KG data gap** (worse than the answer key suggested) | name-based soft link, flagged `name_soft`; expected-negative 1 depends on it |
| 5 MED4 genes unidentified | possibly RefSeq-tagged (`TX50_RS…`, cf. `run_TX50_RS09710`) | coder checks |

Step 4: **pilot positions and chemistry pass; three fixes pending re-run.**

**Re-run after the fixes (module v0.7.0).** Tests 64/64 OK (re-run by the main thread). v0.6
outputs are archived in `pilot/p4_v0.6_archive/`.
- **Roles only from the step-2 map:** `missing_subunit` went from 9 genes to 3 (PMM1046 MFS
  PF07690, `som` PMM1119 porin PF04966, PMM0440 PF13343). The four enzyme/regulator false
  positives and `rbcR` left the class; neighbourhood-only domains carry `role_hint_unverified`.
- **New class `other_system`:** 1,131 rows / 334 genes (all former `tcdb_transporter` rows). In
  the pilot, 23 rows changed, all tcdb_transporter → other_system (`tatA`, `evrABC`, `phoB/R`,
  `bioY`, …). `cynS`, urease, `pncC` and PMM1046 are unchanged.
- **Metabolite equivalence groups** over all 1,693 N-containing KG metabolites: 7 groups linked by
  shared ID (incl. one generic-protein collision, apo-ACP = lipoyl-carrier protein) and 4 by
  normalised name only (`name_soft`): acyl-CoA, chitin, **nitrate**, peptide. Main thread
  confirmed `kegg.compound:C00244` and `chebi:14654` share `equiv_group = chebi:14654` with
  `link_basis = name_soft`.
- **The 5 unidentified genes:** a read-only `run_cypher` count found them (`PMM50003`,
  `PMM50022`, `PMM50028`, `PMM50029`, `PMM_50048`, all conserved hypothetical, no coordinates).
  Tag forms total 1,973 = `list_organisms`. The no-coordinate list is now 96 genes; step-4
  candidates are unchanged with it.

Step 4: **pass.**

### Pilot step 5: substrates + flags (MED4, v0.7 systems)

Command (coder): `p5_substrates.py --organism MED4 ...`. Module v0.8.0; tests 70/70 OK (re-run by
the main thread).

| call | total_matching / returned | pages |
|---|---|---|
| metabolites_by_gene(357 universe genes, transport arm, N, verbose, both depths) | 6220 / 6220 | 7 (197 genes no N substrate) |
| genes_by_metabolite(all ids in the substrates' equivalence groups, MED4, metabolism arm) | 1370 / 1370 | 2 |

Full table `pilot/p5_med4_system_substrates_full.csv`: **6,220 rows** (main thread confirmed;
inherited 3,710 / most_specific 2,510), 160 genes in 140 systems. The 13 superfamily-only
(`family_inferred`) genes contribute 2,464 rows (40%). Summary view (`..._summary.csv`, 3,769 rows)
collapses them to one line each. can_use_window: no 4,818 / elsewhere 1,335 / co-located 67;
can_use_run: no 4,818 / elsewhere 1,377 / co-located 25. Name-soft matches: 65 rows ("peptide" →
`pip` PMM0356 via KEGG C00012; "acyl-CoA" → `plsX/Y`, `plsC1/2`).

**Expected-negative 1: PASS** (main thread verified `pilot/p5_expected_negative_1.csv`): 72 MED4 rows
over `chebi:14654`, `kegg.compound:C00244` and `kegg.compound:C00088`, all `no` under both
definitions; no MED4 gene has a metabolism-arm reaction on any of them.

**Main-thread check against the answer key** (`pilot/p5_pilot_substrate_diff.csv`): 97/97 key rows
found; depth agrees 97/97; can_use agrees with the key's own rule columns 92/97 (window) and
92/97 (run). Every disagreement is explained:

| case | rows | ours vs key | cause |
|---|---|---|---|
| dpp, salY "peptide" | 5 | elsewhere vs no | by design: the name_soft link joins TCDB's generic "peptide" to KEGG C00012 (`pip`); the verifier applied no name links. The proposal already treats peptides' can_use as trivial |
| `amt1` ammonia | 1 | co-located (window) / elsewhere (run) vs key "expected: elsewhere" | the known ambiguity: `pncC` PMM0257, −6, opposite strand. Ours matches the key's rule columns |
| urt urea | 10 | elsewhere (run) vs key "expected: co-located" | the known ambiguity: urease is on the opposite strand. Ours matches the key's run-rule column |

**For the decide gate:** window vs. run for `can_use`. Window links urea to its urease but also
ammonia to an unrelated `pncC`; run avoids `pncC` but loses urease. Also, linked enzymes found
via broad inherited substrates (`salY` → `glnA`, `spt`, `gadB`, `ilvA`; `fadD` → `pdhC`, `cysK`,
`proC`) and currency compounds (ATP, ADP, NAD+, CoA, GTP) look like noise. Step 6 adds a currency
flag and most-specific-only co-location columns (flags, not filters).

Step 5: **pass.**

### Pilot step 6: evidence profiles + currency / most-specific flags (MED4)

Command (coder): `p6_evidence_profiles.py --organism MED4 ...`. Module v0.9.0; tests 74/74 OK
(re-run by the main thread). Currency list: 16 IDs (the docs' minimal-8 set plus H+, CoA, FAD,
GTP, GDP; Glu/Gln deliberately excluded), as module constant `CURRENCY_METABOLITES` and
`pilot/p6_currency_list.csv`. (`docs://examples/metabolites.py` is not shipped in the installed
package; the list came from `docs://analysis/metabolites`.)

New columns on the 6,220-row table (`pilot/p6_med4_system_substrates_flagged.csv`, nothing
filtered): `is_currency` (65 rows True); `can_use_window_ms` / `can_use_run_ms`, where co-location
can come only from a most-specific, non-currency substrate row (others `n/a`). **Linked enzymes
under this variant: 8 pairs over 8 genes** (main thread verified): `pncC`→ammonia (amt1),
`cynS`→cyanate (cyn), `ureC/B/A`→urea (urt), PMM0559→glutathione, PMM1682→L-valine,
PMM1711→UDP-glucose. The noise links via inherited and currency rows (`salY` → `glnA`/`spt`/
`gadB`/`ilvA`; `fadD` → `pdhC`/`cysK`/`proC`) are gone in this variant and still visible in the
window variant. **Correction (API-usage review, 2026-10-07):** that claim is
false for 2 of the 8. PMM1682→L-valine comes via `speE` PMM1685, whose "most-specific" row is at
`tcdb:2.A.1`; PMM1711→UDP-glucose comes via `uvrA` PMM1712 at `tcdb:3.A.1`. Both genes are
`transport_substrate_resolution = family_inferred` (main thread verified in
`pilot/p6_med4_system_substrates_flagged.csv`). Per `docs://analysis/metabolites` §g,
`most_specific` at a lumping superfamily is not a specific call. Fix sent: the variant also
requires a `resolved` gene and a non-lumping family.

System profiles: `pilot/p6_med4_system_profiles.csv` (313 systems). **Main-thread check against the
answer key** (`pilot/p6_pilot_gene_evidence_diff.csv`): evidence, max score and substrate resolution
agree for **27/27** pilot genes. (Correction to my own instruction: I had said `amt1` is the only
homology call. The key and the data also give `pstS` and `salY` homology(0.8). `amt1` is the only
score > 0 homology call *among the N systems*. The key was right.)

**Genome-wide numbers that bear on the decide gate** (`pilot/p6_med4_genome_distributions.json`,
the 75 systems with ≥ 1 `strong` member): a direct TCDB sequence hit with score > 0 occurs in
**34/60 single-gene systems (57%) vs 6/15 multi-gene systems (40%)**; median max TCDB score is
single 0.6 / multi 0.8; role_complete is 43 / 32. A tier keyed on TCDB evidence rung would
penalise multi-subunit ABC systems, so the proposal's no-ABC-penalty principle is confirmed in
the data.

Step 6: **pass. Pilot complete (steps 1–6).**

### Pilot summary

| step | result vs. answer key | problems caught (class) |
|---|---|---|
| 1 collect | 27/27 genes; Pfam 27/27 | BRITE undercount from a Plan-phase API default (**API misuse**); `fadD` called a transporter (rule); seed role map incomplete (code gap) |
| 2 roles | 18/19 (fadD vocabulary only); TCDB leaves 19/19 | — (non-transport ABC ATPases and ECF roles surfaced) |
| 3 systems | 7/7 cases, member for member, parameter-invariant | sodX and ECF chains through `other` genes (rule); 96 genes without coordinates (KG) |
| 4 neighbours | 4/4 position/strand/gap/chemistry | false missing subunits via enzyme "substrate binding" domains (rule); class precedence (rule); nitrate IDs share no cross-reference (**KG**) |
| 5 substrates | 97/97 rows; depth 97/97; can_use 92/97, all 5 explained | — (EN1 passes) |
| 6 profiles | 27/27 evidence/score/resolution | noise linked enzymes via inherited/currency rows (rule → flag columns) |



### API-usage review (2026-10-07, before scaling)

A fresh reviewer subagent (`superpowers:requesting-code-review` template, read-only) checked
every API call in `n_transport.py` v0.9.0 and scripts p1–p6 against `docs://guide/python_api`,
the conventions and the installed package source. Verdict: **"Ready to scale: with fixes."**

**Critical (both confirmed by the main thread with its own API calls):**
- **C1: offset paging over a non-unique sort order silently swaps rows.** In the installed
  source, `metabolites_by_gene` sorts the metabolism arm by (locus order, locus_tag,
  metabolite_id) and the transport arm by (depth, score, locus order, locus_tag,
  metabolite_id); neither includes `reaction_id` / `tcdb_family_id`. Paging with SKIP/LIMIT
  therefore duplicated some rows and dropped others at page boundaries while
  `total_matching == rows collected` still held. Main-thread check vs. a single call:
  PMM0331 98 = 98 rows, 1 duplicated + 1 missing; PMM1590 16 = 16, 2 duplicated + 2 missing.
  Step-4 reaction counts for those pairs are wrong; no (gene, metabolite) pair was lost this
  time. The row-count assertion can't detect this class of error.
- **C2: "most-specific" ≠ specific** (see the correction under step 6).

**Important:**
- I1: `metabolite_elements=['N']` drops formula-less substrates (amino acid, branched-chain
  amino acid, dipeptide, polyamine, purine, cyclic nucleotide, protein, siderophores; 249
  metabolites / 4,105 MED4 transport rows have no formula).
- I2: the no-coordinate list was built by hand, not scripted (MIT9313: 517 genes, 18%; NATL2A:
  152).
- I3: tag-number placement breaks on MIT9313's mixed `PMT`/`PMT_` tags.
- I4: output files without a strain tag would mix strains.
- I5: MED4 pilot constants hard-coded.
- I6: the universe was drawn from the 12 seed Pfams, not the data-built role map (MED4: 3 genes
  missed).
- I7: cross-locus scale risk (unverified).

Minor M1–M8, including three `bool()` / `astype(bool)` casts of the round-1 kind.

**Disposition:** all Critical and Important findings, plus M1–M6, sent to the coder, followed
by a full MED4 re-run p1→p6 with diffs against the pilot outputs and re-checks against the
answer key, before MIT9313/NATL2A.

### MED4 full re-run after the review fixes (module v1.0.0 + `kg_fetch.py`)

Command: `scripts/run_pipeline.py` (p1→p6, all steps exit 0, ~70 s), outputs in `data/med4/`,
archive of the pilot in `data/pilot_v0.9_archive/`. Tests **91/91 OK** (re-run by the main
thread; 21 new for `kg_fetch`). The fixes, in brief:
- **Fetching:** one tested fetch helper, no offset paging. Single call per chunk; asserts on
  totals, truncation and natural-key duplicates; expected-warning check.
- **C2:** strict most-specific variant (resolved gene, non-lumping family, non-currency).
- **I1:** no element prefilter, with an `n_status` flag.
- **I2:** scripted no-coordinate list with a hard completeness assert (1,877 + 96 = 1,973).
- **I3:** placeability (10 placed / 85 same-prefix, no member near / 1 unplaceable).
- **I4:** per-strain directory and a role-map hash.
- **I5:** `--pilot` switch.
- **I6:** universe re-query (+PMM0440, PMM1046, `som` PMM1119 → 360 genes).

**Main-thread checks:**
- Lumping families: `tcdb:3.A.1` (554 substrates), `2.A.1` (476), `2.A.7` (135), `2.A.6` (130);
  next family 50. Threshold 100 sits in the gap.
- Strict linked enzymes = **6**: `pncC`→ammonia, `cynS`→cyanate, `ureC/B/A`→urea,
  PMM0559→glutathione. The valine and UDP-glucose artefacts are gone.

Coder's diff vs. v0.9 (`data/med4/p7_med4_diff_vs_v0.9.json`):
- no existing system changed membership; +3 one-gene systems from the I6 additions;
- contains-N substrate rows are identical (6,220), with identical can_use;
- the full table now has 14,978 rows (+4,105 no-formula, +4,653 no-N);
- name-soft groups 4 → 8 (adds protein, amino acid, heme, purine);
- the archived paged raw file holds exactly the 3 duplicated keys the reviewer predicted.

Pilot re-checks vs. the answer key: identical to v0.9 at every step. **EN1: PASS** (72/72 `no`).

**Carried to the decide gate:** the no-formula substrates added to dpp via `tcdb:3.A.1.5`
include sugars (mannose, maltooligosaccharides, galactoside…) as most-specific rows, so the
"peptide" class grouping needs care. *(Superseded: see the dpp/peptides bullet under Results.)* I7: max system 8 (F-ATP synthase); the 2 cross-locus
systems with a repeated ABC role are dpp and pst (two permeases each: expected heterodimeric
permeases, not chaining).

### Scoped re-review of the fetch helper and the C2 fix (2026-10-07)

Fresh reviewer, scope = `kg_fetch.py`, its tests, every `fetch(` call site, and
`add_ms_variant` / lumping logic. Verdict: **C1 and C2 fixes correct; no new Critical issues;
"safe to scale: with fixes."** Each tool's natural key was checked against its row grain in the
installed source. Chunking can't lose rows. Limits are correct per signature. Live logs: totals
equal on every call, no not_found, only the 6 expected `family_inferred` warnings. The KG's own
family_inferred calls agree with the lumping set.

Important (both guards; neither fires on current outputs):
- a TCDB family missing from `ontology_term_details`, or with a non-numeric
  `metabolite_count`, would silently count as non-lumping, re-opening the C2 failure. Fix: assert
  coverage and numeric counts;
- `fetch` only logs not_found / wrong_ontology / wrong_level. Fix: a `strict_inputs` option, on
  for curated-input calls (p1 seed Pfams, p2c role-map Pfams, p5 metabolite ids).

Minor: `gene_neighbors(limit=None)` relies on an implementation detail (use 10**6); the
identical-row collapse should be scoped to BRITE rows only; `find_duplicates` should assert key
columns exist; a `total_matching: None` guard; `p4d_probe_refseq_tags.py` (not in the pipeline)
still pages. **The fetch test file has 14 tests, not the 21 the coder reported**; untested paths
(empty chunk, cross-chunk duplicate, envelope without total_matching) to be added.

**Disposition:** applied after the MIT9313/NATL2A run returns, then all three strains re-run.

### Scale-out to MIT9313 and NATL2A (module v1.0.1)

`run_pipeline.py --organism "Prochlorococcus MIT9313"` / `"Prochlorococcus NATL2A"`, outputs in
`data/mit9313/`, `data/natl2a/`; all steps exit 0. One MED4 assumption surfaced and was fixed
test-first (92 OK): two MIT9313 universe genes have **no coordinates** (PMT_2355 MFS sugar porter,
`som` PMT_2631). They now become one-gene pseudo-run systems instead of failing an assert.

| | MIT9313 | NATL2A |
|---|---|---|
| genes / with coordinates / without (assert passed) | 2906 / 2389 / 517 | 2210 / 2058 / 152 |
| no-coordinate placement: placed / same prefix, out of window / unplaceable | 144 / 373 / 0 | 22 / 130 / 0 |
| universe (after re-query) | 528 | 379 |
| role map domains / role conflicts vs MED4 | 503 / **0** (352 shared) | 402 / **0** (349 shared) |
| systems / role-complete / max size | 462 / 77 / 8 | 332 / 49 / 8 |
| cross-locus systems / with a repeated ABC role | 7 / 4 | 5 / 2 |

**Main-thread checks against the KG** (`genes_by_function`, `genes_by_ontology`, `gene_neighbors`):
- MIT9313: `focA` PMT2240 (FNT nitrite transporter), `nirA` PMT2239, `amt1` PMT1853, `urtA–E`
  PMT2225–2229; no cyanase. Matches the pipeline (amt1 → ammonium, urt → urea with linked
  enzymes PMT2234–2236, no cyanate rows).
- NATL2A: `focA` PMN2A_1299, `nirA` PMN2A_1298 + a second `nirA` node PMN2A_RS10340, `amt1`
  PMN2A_1629, `urtA–E` PMN2A_1044–1048, **and cyanase `cynS` PMN2A_1390**. The pipeline reports
  no cyanate rows. Checked: NATL2A has **no genes in `tcdb:3.A.1.16`** (NitT/TauT, MED4's cyn
  family), and `cynS`'s ±5 neighbours are hypotheticals. So this is cyanase with no annotated
  importer `[KG]`, and the pipeline is correct.
- No gene reacts with nitrate in any of the three strains. Nitrite: `nirA` in MIT9313 and NATL2A
  only.

**Pipeline vs. this biology:**
- In both strains `focA`'s nitrite row is co-located under window **and** run (linked to the
  adjacent `nirA`). So expected-negative 1 holds per genome, as the proposal specified: nitrite is
  usable in MIT9313/NATL2A, and nitrate in none. The step-5 `EN1.pass` label hard-codes MED4's
  expectation (it reads `false` for these strains). Fix sent: derive the expectation per strain.
- **The strict (most-specific) variant misses this true case:** `focA`'s nitrite row is
  *inherited* within the non-lumping FNT family `tcdb:1.A.16`, so it gets `n/a`. Decide-gate
  item: whether the strict rule should require most-specific depth, or only resolved +
  non-lumping + non-currency.
- Many single-gene ammonium/urea/nitrate "systems" in both strains are regulators or
  non-transporters with a TCDB hit (`recQ`, `phoB/R`, `rpaA/B`, `sasA`, `nblS`, `crhR`, `crp`),
  shown as found.
- NATL2A `gene_name` holds a RefSeq tag for 95/379 universe genes. MIT9313's `PMT_2239` is an
  alias of `PMT2239` (two tag schemes).

### Re-review fixes + three-strain re-run (module v1.0.2)

All nine re-review items applied test-first. Tests **105/105 OK** (main thread re-ran;
`test_kg_fetch` 21 + `test_n_transport` 84. The coder's earlier per-file split was misreported;
the totals were right). Every active pipeline script reaches the KG only through
`kg_fetch.fetch`. No offset paging is left (main-thread grep). Scripts that bypass it moved to
`scripts/archive/`. `strict_inputs` (7 curated-input calls per strain) never fired. Per-strain
diffs vs. v1.0.1 (`data/<tag>/p9_<tag>_diff_vs_v1.0.1.json`): **every analysis table is
unchanged**; only the new expectation files, an added `compound` / `has_coordinates` column and
the logs differ. Lumping sets: MED4 and NATL2A {3.A.1, 2.A.1, 2.A.7, 2.A.6}; MIT9313 adds
`2.A.66` (106 substrates).

## Results

### Per-strain build (reference variant: gap 200 bp, role join on, cross-locus on; ±8 neighbours)

| | MED4 | MIT9313 | NATL2A |
|---|---|---|---|
| genes in KG / without coordinates | 1973 / 96 | 2906 / 517 | 2210 / 152 |
| transporter universe | 360 | 528 | 379 |
| role-map domains (conflicts vs MED4) | 394 | 503 (0) | 402 (0) |
| systems / role-complete | 316 / 45 | 462 / 77 | 332 / 49 |
| cross-locus systems | 6 | 7 | 5 |

### Nitrogen import systems: what the files contain (data-driven), then a curated view

**From the files** (`data/<tag>/p6_<tag>_system_substrates_flagged.csv`, rows matched on
`equiv_group`; main thread computed, 2026-10-07). "Strong" = `likely_transporter = strong`.

| strain | compound | all rows | most-specific rows | most-specific genes | of which strong | strong genes |
|---|---|---|---|---|---|---|
| MED4 | ammonia | 7 | 6 | 4 | 4 | `amt1`, `ktrA`, `nhaS`, PMM0704 |
| MED4 | urea | 30 | 10 | 5 | 5 | `urtA–E` |
| MED4 | cyanate | 25 | 2 | 2 | 2 | `cynA`, `cynB` |
| MED4 | nitrite | 29 | 6 | 4 | 3 | `cynA/B/D` |
| MED4 | nitrate | 43 | 15 | 14 | 5 | `cynA/B/D`, `sul1`, `sul3` |
| MIT9313 | ammonia | 10 | 8 | 8 | 7 | `amt1`, `ktrA`, `nhaS`, PMT0515, PMT0542, PMT1974, PMT_0376 |
| MIT9313 | urea | 45 | 16 | 11 | 6 | `urtA–E`, `putP` |
| MIT9313 | cyanate | 40 | 0 | 0 | 0 | — |
| MIT9313 | nitrite | 42 | 1 | 1 | 0 | — (`recQ`, tcdb_only) |
| MIT9313 | nitrate | 78 | 20 | 16 | 3 | `sul1`, `sul3`, `putP` |
| NATL2A | ammonia | 6 | 5 | 4 | 4 | `amt1`, `ktrA`, `nhaS` |
| NATL2A | urea | 34 | 14 | 9 | 6 | `urtA–E`, PMN2A_1011 |
| NATL2A | cyanate | 26 | 0 | 0 | 0 | — |
| NATL2A | nitrite | 28 | 1 | 1 | 0 | — (`crhR`, tcdb_only) |
| NATL2A | nitrate | 49 | 16 | 12 | 3 | `sul1`, `sul3`, PMN2A_1011 |

Most-specific rows also sit on regulators and non-transporters with a TCDB hit, at
`tcdb_evidence_score` 0–0.2 (`rpaA/B`, `phoB/R`, `sasA`, `nblS`, `srrA`, `ycf29`, `crhR`, `recQ`,
`crp`), **in MED4 as well as the other two strains**. These rows pass the strict variant
(`resolved`, non-lumping). Only `likely_transporter` separates them.

**Curated view (author's reading, `[interpretation]`, not a file view):** the canonical N import
systems are `amt1` (ammonium) and `urtA–E` (urea) in all three strains; cyn (`cynA/B/D` + `cynS`)
in MED4 only; `focA` + `nirA` (nitrite) in MIT9313 and NATL2A, via an inherited row at
`tcdb:1.A.16`. Specific wording corrections after the methods critic:
- **NATL2A cyanate:** no *most-specific* cyanate rows; 26 *inherited* lumping-family rows
  (`tcdb:3.A.1` ×20, `2.A.1` ×6) are flagged `elsewhere in genome` via cyanase `cynS` PMN2A_1390,
  which has no annotated importer. MIT9313: 40 inherited cyanate rows, all `no`.
- **NATL2A "second `nirA`":** PMN2A_RS10340 is a 53-aa fragment starting 42 bp after `nirA`
  PMN2A_1298 and matching its C-terminus (critic, `gene_details`). Treat it as an annotation
  fragment, not a second nitrite reductase. RefSeq-only fragment nodes also take neighbour-rank
  slots in the ±8 window.
- **Peptides (dpp)** — every peptide row is `no` (data, all three strains, systems `sys_PMM0192`,
  `sys_PMT0266`, `sys_PMN2A_0704`): most-specific `dipeptide`, `tripeptide`,
  `L-alanyl-L-alanine` and inherited `Oligopeptide` are `no`. The only usable peptide row is the
  inherited generic `peptide` (`chebi:14753`, `match_basis = name_soft` → KEGG C00012 → `pip`):
  `elsewhere in genome` in MED4 and NATL2A, **`no` in MIT9313**. The usable most-specific
  substrates of dpp are Maltose, Melibiose, Raffinose (+ Cellobiose in MIT9313/NATL2A), Heme and
  5-Aminolevulinate. Its most-specific set at the family-level node `tcdb:3.A.1.5` also holds EDTA,
  Stachydrine, Bradykinin and Nickel(2+). This replaces my earlier line "the proposal treats
  peptides' can_use as trivial", which the data contradict: peptides do **not** pass the check
  trivially.
- **"Linked enzyme"** means a gene with a metabolism-arm reaction on the substrate within ±8 genes,
  in any direction (biosynthesis included). It is not an operon partner. The strict list still
  holds coincidences: `pncC` → ammonia in all three strains (PMM0257, PMT1845, PMN2A_1623); in
  MIT9313, `ribD` PMT0375 → ammonia for the K⁺ channel PMT_0376, and `hisD` PMT1510 (histidine
  *biosynthesis*) → `putP` PMT1502 at 12,337 bp and → the nat system via `grrP`.
  `in_run_ms` is True only for cyn.
- **`role_complete = True`** for one-gene single carriers is a vocabulary result, not evidence of
  function.

### Expected-negative 1, per genome (`data/<tag>/p6_<tag>_expected_negative_1_table.csv`, main thread verified)

| strain | nitrate expected / observed | nitrite expected / observed | pass, all 4 definitions |
|---|---|---|---|
| MED4 | not usable / all `no` (43) | not usable / all `no` (29) | yes |
| MIT9313 | not usable / all `no` (78) | usable (`nirA`) / 41 elsewhere + 1 co-located | yes |
| NATL2A | not usable / all `no` (49) | usable (`nirA`; RS10340 is a fragment) / 27 elsewhere + 1 co-located | yes |

**How to read this table (methods critic):**
- For MIT9313 and NATL2A the check is **close to circular**: `expected_usable` and `can_use` come
  from the same metabolism arm, so for window/run it tests equivalence-group plumbing, not
  biology. The 41/27 "elsewhere" nitrite rows are inherited lumping-family rows (`salY`, `sufC`,
  `fadD`, `acs`, …). The informative rows are `focA` (co-located) and, for MED4, the cyn
  nitrate/nitrite rows, whose expectation has an independent anchor (no `narB`/`nirA`, proposal
  grounding item 6).
- **Under the strict definitions, the MIT9313/NATL2A nitrite "pass" rests on one row each, a
  helicase**: `recQ` PMT0189 (ATP-dependent DNA helicase) and `crhR` PMN2A_0647 (RNA helicase),
  both `tcdb:2.A.16`, `tcdb_only`. The real case, `focA`, is not evaluated (inherited). The strict
  variant therefore **misses the true positive**, and its "pass" is not validation.

### Proposal §3.4 method checks (MED4)

| check | result |
|---|---|
| `urtA–E` → one system, urea `can_use` True | pass (window co-located; run elsewhere: urease on opposite strand) |
| `amt1` → ammonium `can_use` True | **trivially satisfied**: "elsewhere" holds for ammonia in any genome, and "co-located" comes only via the coincidental `pncC`. Tests nothing |
| cyn → one system; cyanate `can_use` True, nitrate/nitrite False | pass (cyanate co-located via `cynS`; nitrate/nitrite `no`) |
| dpp split across loci → one system | pass (cross-locus join on `tcdb:3.A.1.5`) |

### Audit: which round-1 workarounds the alpha.7 stack still needs

| round-1 workaround (KG alpha.6) | still needed? | evidence this milestone |
|---|---|---|
| Pfam subunit roles parsed from `alternate_functional_descriptions` text | **no** | `gene_ontology_terms(ontology='pfam')` returns domains directly (14/16 curated on the MED4 N transporters) |
| TCDB treated as flat `3.A.1` superfamily tags | **partly** | `attachment_depth`, `transport_substrate_resolution` and subfamily specificity nodes now exist (urea `3.A.1.4.x`, cyanate/nitrite `3.A.1.16.x`). But "most-specific" at a lumping family is not specific: 13 MED4 genes are superfamily-only, and a lumping-family rule is still required (C2) |
| evidence ladder that read eggNOG-only calls as curated | **no** | alpha.7 reads eggNOG-only calls as `family_inferred`; the evidence profile uses it directly |
| grouping by consecutive locus + same strand | **yes, but insufficient** | needed for runs, but systems also need cross-locus joining (dpp: 3 loci; pst: `pstS` 15 genes away), and same-strand-only misses urease next to urt |
| substrate taken from product / COG text for ABC systems | **mostly no, with a residual ambiguity** | TCDB specificity nodes give substrates for the N systems, but the NitT/TauT family is bispecific (cyn → nitrate/nitrite/cyanate), so the `can_use` fusion rule is still needed |

### Methods critic (2026-10-07): data-integrity + interpretation

Not clean: **2 Blockers, 8 Concerns, 2 Notes**, all against the notebook's narrative, none
against the data files. The critic confirmed that the tables are mechanically sound: no duplicate
natural keys in the three flagged tables (14,978 / 27,013 / 17,022 rows), counts reproduce, and
system memberships match the KG. Findings and dispositions: `methods/critical_review.md`. Both
Blockers were verified by the main thread against the files and are fixed in the text above.

Main-thread addition while dispositioning: **the strict-variant value `"n/a"` is read as NaN by
pandas' default `read_csv`** (it's in pandas' default NA strings), so a consumer can't tell "not
eligible" from "missing". Fix sent to the coder: rename the value to `not_eligible` and add a
test that reads the written CSV with default pandas settings.

## Surprises

## Decisions

**Decide gate, 2026-10-08 (researcher), from annotation only, before any expression is pulled:**

1. **Linked enzymes: two kinds, each its own column** (researcher: "not sure I want to drop the
   distance; maybe we need 2 different kinds"). Purpose, in the researcher's words: (1) expression
   evidence that strengthens or weakens the transporter call; (2) stronger evidence of what a
   promiscuous or hard-to-pin transporter carries.
   - **Neighbour-linked** (genomic; mainly purpose 2): the enzyme has a KEGG reaction on a
     compound the transporter is annotated to carry, within ±8 genes, either strand. Ubiquitous
     compounds (ammonia-type, reacted on by a large share of the genome's enzymes) can't create the
     link (researcher's choice "window, minus ubiquitous"). The ubiquity list is data-derived and
     shown.
   - **Function-linked** (curated; mainly purpose 1): the enzyme has a KEGG reaction on a carried
     compound **and** shares a curated Cyanorak role with the transporter outside the transport (Q)
     branch, at any distance. Evidence (MCP, `gene_ontology_terms` cyanorak_role): `amt1`,
     `cynA`/`cynS`, `urtA`/`urtE`/`ureC`/`ureG`, `glnA`, `glsF` share "N metabolism" (E.4);
     `focA`/`nirA` (MIT9313) share "N acclimation" (D.1.3); `pncC` is "cofactor biosynthesis"
     (B.11) only. KEGG pathways were checked and rejected as the shared annotation: `amt1` and
     `focA` have no KEGG terms, and `urtA` sits only in "ABC transporters" (ko02010).
   - In both kinds: no giant catch-all families (the lumping set) and no cofactors.
     Inherited-from-family listings are allowed (so `focA`→nitrite counts). This **supersedes the
     strict variant** (its columns stay in the files for transparency but aren't used for claims).
2. **Curated transport class** (new column): each system's Cyanorak transport (Q) roles, e.g.
   Q.1 "amino acids, peptides and amines" (`dppA`, `urtA`, `cynA`), Q.4 "cations" (`amt1`), Q.2
   "anions" (`focA`, `pstS`). Coarse but curated and independent of TCDB, it's the only
   annotation leaning dpp toward peptides rather than the sugars/heme its PepT family lists.
3. **Organic N classes (peptides, amino acids, polyamines, nucleosides): "can_use not testable"**
   (the check has no teeth for organic N: no KEGG reaction on dipeptide/tripeptide in any of the
   three genomes). These classes are reported from transport annotation + tier + curated transport
   class, labelled `can_use not applicable`. dpp's sugar/heme listings are flagged as PepT family
   breadth.
4. **Tiers (system level):**
   - *High* = `likely_transporter` strong + role-complete + `resolved`;
   - *Medium* = strong but incomplete, or `tcdb_only` + `resolved`;
   - *Low* = superfamily-only (`family_inferred`) or score-0-only.

   Evidence rung and `tcdb_evidence_score` order systems within a tier and never set it
   (direct-sequence-hit rates are 57% single-gene vs 40% multi-gene systems, so the rung can't be
   the key without penalising ABC systems).
5. **Compound classes:** ammonium, urea, cyanate, nitrite and nitrate are each their own class;
   annotated analogues (methylamine-type amines; thio-/hydroxyurea) are kept and flagged. Organic
   N classes come from a documented name/ChEBI rule (built by the coder), reviewed by the
   researcher before the analysis milestone.
6. **Neighbours that join a system:** none left. All missing-subunit candidates were absorbed by
   the universe re-query (0 in all three strains). Linked enzymes stay attached, not merged.
7. **Inherited superfamily rows:** the full table is kept; the reading view collapses each
   superfamily-only gene to one line; such rows can't support a claim.
8. **Empty category cells written by steps 2–4** (`joined_by`, `likely_transporter_basis`, …):
   left as is ("none"; harmless).

**Decide gate, continued (2026-10-08), after the v1.1.0 build** (117 tests OK; the pilot met the
expectations):
9. **Curated Cyanorak transport role counts as transporter evidence** (a third basis for
   `strong`, alongside a role Pfam or a BRITE transporter KO), overriding "score-0-only → Low".
   Reason: `focA`, the curated nitrite transporter in MIT9313/NATL2A, landed Low because its only
   TCDB hit scores 0 and its domain isn't in the role map.
10. **Function links via ubiquitous compounds (≥ 30 genes: ammonia, L-glutamate) count only for
    the assimilation enzymes GS/GOGAT** (`glnA`, `glsF`; an EC-keyed allow-list, organism-agnostic),
    with a `link_breadth` column. Before this, `amt1`'s function-linked set was every
    N-metabolism enzyme touching ammonia (`cynS`, urease, `carA`, `metB`, `metC`, …).
11. **Ubiquity threshold ≥ 30 genes** (coder-proposed; a clean gap in all three strains: ammonia /
    L-glutamate 34–40 vs. next 23–25).
12. **Compound classes: a layered classifier with provenance** (researcher: "do we have a way to
    link these to compound classes? is there matching KG info?"). Layers, first match wins, all
    votes recorded:
    1. name rules (with fixes);
    2. the compound's KEGG `pathway_ids` (a reviewable pathway→class map);
    3. the carrying transporter family's TCDB name + GO links (efflux/drug → xenobiotic;
       siderophore families → siderophore);
    4. the curated transport class as a tie-break.

    Leftovers → "unclassified N". The researcher reviews only the leftovers that are
    N-containing and carried by a most-specific row of a High/Medium system.
    Also: no-formula groups no rule classifies → "unclassified (no formula)". This fixes a
    v1.1.0 bug that labelled N-free sugars and ions (D-galactose, fructose, calcium ion) "other N".
    Note: dpp's curated transport class came out Q.1 + Q.4 + **Q.7 sugars** (`dppC`), so curated
    annotation doesn't settle peptides vs. sugars for dpp either.

**Decide gate, final rules (v1.3.0 → v1.4.0, 2026-10-08).** These supersede decision 12's layers
2–4 and qualify decision 9:
13. **Compound class = curated name rules only** (researcher: "names decide; rest = context").
    KEGG pathway membership and the carrying-family context were tried as classifiers and
    rejected: about half of the sampled assignments were wrong (thyroxine → amino acids;
    bacitracin → amino acids; UDP-GlcNAc and GDP-sugars → xenobiotic). Both are kept as context
    columns. Every class row and substrate row carries `class_caveat = "best effort: names only;
    KG has no chemical categories"` (researcher: "do best effort with caveats"; the KG
    enhancement is logged in `gaps_and_friction.md`). Name-rule additions after the delta pass:
    betaines/carnitines/ectoine → osmolytes; cystine, hydroxyproline, seleno-amino acids →
    amino acids; bradykinin/microcin/bacitracin → peptides; a new **amino sugars** class
    (GlcNAc, glucosamine, chitobiose, neuraminates). Quaternary ammoniums were removed from the
    ammonium analogues (methylamine and ethylamine kept).
14. **Annotation bases only upgrade catalogue-listed genes.** A curated Cyanorak transport role
    or a BRITE transporter KO makes a gene `strong` only if it also has a TCDB class 1–3
    attachment (`tcdb_only → strong`); never `none → strong`. A role Pfam alone still counts.
15. **Tiers (final):** High = a strong member + role-complete + resolved; Medium = a strong
    member, role-incomplete; Low = superfamily-only, or score-0-only (overridden by a curated
    upgrade), or **catalogue-only** (TCDB hit with no domain/KO/curated support).
    Before → after the catalogue-only fix: Medium 122 → 32 (MED4), 170 → 45 (MIT9313),
    128 → 35 (NATL2A); High unchanged at 39 / 64 / 42 (`data/p15_tier_counts.csv`).
16. **Known false positives, disclosed, not removed:**
    - **ferritin** `ftn` (MED4 PMM0804; MIT9313 PMT0495, PMT0499): a curated Q.4 role + a score-0
      TCDB `1.A.155` hit make it `strong`/Medium. It can't be separated from `focA` (also
      score 0) by rule. Flag `known_false_positive`;
    - **glutathione S-transferases** (MED4 PMM0110/0566/0630, MIT9313 PMT0471/1961/2104, NATL2A
      PMN2A_0002/0069/1478) stay `strong`/Medium because TCDB lists them under the CLIC family
      `1.A.12`;
    - **`sodX`** PMM1295 stays `strong`/Medium via ABC-exporter TCDB families;
    - collateral of decision 14: **`ictB`** (MIT9313 PMT1821, a bicarbonate transporter) dropped
      to not_transporter (KO + Cyanorak only, no TCDB). Not an N transporter.
17. **RefSeq fragment nodes** are flagged `fragment_of` and excluded from link counts (NATL2A
    PMN2A_RS10340 → `nirA` PMN2A_1298; `focA`'s neighbour-linked count 2 → 1).

**Decide-gate QC round (v1.5.0 → v1.6.0, 2026-10-08).** Asked for by the researcher before approval
("what other QC checks/graphics to check for results correctness?"). The QC pack is
`scripts/q1_qc_checks.py` → `data/qc/`, figures fig7–fig9:
- (a) gene maps of the N loci (fig7);
- (b) curated Cyanorak transport-role genes by tier (fig8);
- (c) a random sample of 10 systems per tier;
- (d) substrate vs product for High systems;
- (e) gap 100/200/500 sensitivity (fig9);
- (f) strain consistency by gene name (orthologs not used).

18. **Adjacent ABC parts join (v1.5.0, rule "adjacent_abc").** A same-strand, directly adjacent
    gene (gap ≤ 200 bp) joins an ABC-only system when they share a TCDB ancestor at level ≥ 2,
    even if it repeats a role (a second permease). A strong 'other' gene (membrane-fusion `devB`)
    may also join. Two complete cassettes never merge. Found by checking adjacent transporter
    genes that ended in different systems:
    - `evrA/B` + `evrC` (MED4 PMM0976–0978);
    - `devB` + `devC/A` in all three strains.

    Merged: MED4 devBCA, evrABC; MIT9313 devACB, PMT1573–1575 (researcher: keep); NATL2A devBCA.
    Tier changes: PMM0748, PMT1574 and PMT1575 go Low → Medium. No N system changed
    (`data/p16_*`).
19. **Curated transport role as a rescue path (v1.6.0; researcher: "Yes, both").**
    - (a) Genes with a Cyanorak Q.1–Q.9 role are a 4th universe source: +6 / +11 / +9 genes.
      Two gain a transporter tier: MIT9313 PMT2207 ("permease") and NATL2A PMN2A_2187 (CLC), both
      Medium. The rest end up not_transporter: no role Pfam, no TCDB. They include
      `hisF`, `hemH`, `metC`, the Q.5 RNA-binding protein, and the porins `som` PMM1121 /
      PMN2A_0440. The porins are therefore outside the High/Medium candidate set the analysis
      milestone will read, although outer-membrane porins pass small N solutes.
    - (b) A curated role lifts "superfamily-only" from Low to Medium; catalogue-only is never
      lifted (decision 14 stands). 23 loci go Low → Medium (4 / 17 / 2), including MIT9313
      ggtA–D PMT0691–0694, PMT1576 and the ccmA genes. Most of the 23 are efflux/export proteins
      (decision 21).

    High counts are unchanged at 39 / 64 / 42. Medium is now 34 / 58 / 37 (`data/p17_*`).
    After v1.6 no curated-role gene sits in Low or outside the universe (q1b).
20. **Dedicated vs broad listing (v1.6.0; researcher: "Split dedicated vs. broad").** QC check (d)
    showed that TCDB substrate lists describe the subfamily, not the gene. In MED4, `sul1`/`sul3`
    list amino acids and nitrate, and `ktrA` and `nhaS` list ammonium. Each (High/Medium system,
    N class) pair from most-specific, non-lumping rows is now marked as one of:
    - **dedicated**: a class keyword appears in a member product or gene name
      (`data/p18_class_keyword_map.csv`), or the member has a curated Q.1 / Q.5 role. Q.4 is not
      mapped to ammonium.
    - **broad listing**: neither.

    Each system also records `substrate_breadth`. Nothing is removed. Fig2 Block B shows the two
    separately. All expected cases match where the pair exists (`p18_<strain>_expected_checks.csv`):
    - amt1 is dedicated for ammonium; ktrA and nhaS are broad;
    - sul1/sul3 are broad;
    - dpp is dedicated for peptides; urt is dedicated for urea;
    - putP (MIT9313) and PMN2A_RS08290 (NATL2A) are broad for urea.

    Result [KG], High/Medium, known false positives excluded:

    | Class | MED4 | MIT9313 | NATL2A |
    |---|---|---|---|
    | amino acids, dedicated | 0 | 4 (e.g. `agcS`, `proV/W/X`) | 1 |
    | amino acids, broad listing | 8 H + 1 M | 18 H + 6 M | 11 H + 2 M |
    | peptides, dedicated | `dpp` | `dpp` | `dpp` |
    | osmolytes, dedicated | 0 | 2 (`proV/W/X`, `proP`) | 0 |

    (v1.6.1 values.) Amino sugars and polyamines have broad listings only in all strains;
    nucleobases have broad listings only in MED4 and MIT9313 and none in NATL2A. MIT9313
    `proV/W/X` (PMT0553–0555) and `proP` (PMT1044) are dedicated for both amino acids (via
    "proline") and osmolytes (`data/p19_double_dedicated.csv`), i.e. one osmoprotectant system
    counted in two classes.
    The keyword rule is a screen: a dedicated call means "the annotation names this class", not
    "the gene transports it".

21. **Critic fixes (v1.6.1; third critic pass, `critical_review.md`).**
    - An `efflux_annotated` system flag marks a member product that names efflux, export,
      multidrug or RND, or a dev/evr/tolC/acrA/mdtA/ccmA/ycf38 gene. Counts: 20 / 32 / 19 systems.
      Flag only.
    - The 23 loci the curated role lifted to Medium split as follows (`data/p19_lifted_loci_split.csv`):
      - **12 efflux-annotated**: ccmA/ycf38 in MED4 and MIT9313; MIT9313 RND and MFS
        multidrug pumps; DevA-type PMT1576.
      - **6 DMT/EamA permeases** of unclear direction.
      - **5 import-type**: ggtA–D and PMT1237.

      So most of what the curated role adds is export machinery. Any import reading of a
      lifted system must check this flag.
    - A curated Q.1/Q.5 role alone no longer makes an efflux-annotated system "dedicated". This
      moved MIT9313 sys_PMT0977 (an "ABC multidrug efflux transporter" with a Q.1 role on PMT0978)
      from dedicated to broad for amino acids and peptides. No other dedicated call changed. Every
      remaining dedicated call rests on a keyword (`dedicated_basis`). Q.1 ("amino acids, peptides
      and amines") cannot tell those classes apart. It is also on urtA–E, cynA and hisF.
    - Keyword patterns now use word boundaries and exclusions (cyanophycin, nitrate/sulfonate,
      histidine kinase, OsmC, amidotransferase, gltX/A/B).
    - Fig2 Block A splits the "+k other usable systems" into dedicated vs broad. Ammonium is
      "+0 dedicated, +4 / +7 / +3 broad"; the broad systems are all K⁺/Na⁺ transporters (ktrAB,
      nhaS, K⁺ channels). Block A examples are restricted to High/Medium, so the helicase crhR no
      longer appears as a nitrite example.
    - The MAPEG glutathione protein MIT9313 PMT1025 is flagged as a known false positive. MED4
      PMM1015 and NATL2A PMN2A_0464 are not in the universe.

**Other QC results (no rule change):**
- **Gap sensitivity (e):** the N-relevant systems are identical at 100 / 200 / 500 bp. Tier counts
  move by ≤ 4 systems.
- **Strain consistency (f):** amt1, urt, dpp, mnt, phn, fut/idiA, sul1, sul3 and ktr have the same
  tier and member count in all strains. MIT9313 pst has 5 members (two `pstS`, PMT0508 + PMT0993).
  cyn is absent in MIT9313 and NATL2A (NATL2A has `cynS` without `cynABD`); focA is absent in MED4;
  sbtA is absent in NATL2A.
- **Random sample (c):** sodX and a GST appeared in the MED4 Medium sample. Both are flagged.
- **Known false-positive flag** now covers glutathione S-transferases and `sodX` as well as
  ferritin (product match; `data/p16_known_false_positive.csv`).
- **Housekeeping:** the 6 grouping settings not chosen moved to `data/<strain>/grid/`.

**"Linked enzyme" means co-annotation, not co-regulation:** an enzyme with a KEGG reaction on a
compound the system carries and either a shared curated Cyanorak role (function-linked) or
position within ±8 genes (neighbour-linked). In each strain only about 6 rows concern N import
(`glnA`, `glsF`, `cynS`, `nirA`, `ureA/B/C`). Most other function links connect glutathione
S-transferase paralogs. Link tables carry the system tier and `system_is_transporter_candidate`.

**Design targets vs. independent checks (delta critic, F6).** The pilot outcomes `focA` →
Medium and `amt1` ← `glnA`/`glsF` only are **design targets**: decisions 9 and 10 were adopted to
produce them, so they don't validate anything. The independent checks are: `pncC` unlinked;
`salY` Low; amt1/cyn/urt/dpp/pst High (unchanged since v1.1.0); and the per-genome
nitrate/nitrite expected-negative. The fixes in decisions 14–16 were driven by checks that
weren't design targets (helicases in Medium, ferritin).

**Review list** (`data/p12_review_list_unclassified_N.csv`, rule: unclassified N, N-containing,
carried by a most-specific row of a High/Medium system, **not only via lumping families**,
union of strains): **76 groups**. Contents are mostly drugs on ABC exporters (3.A.1.106/.113/.203),
siderophores and cobalamin on FeCT (3.A.1.14), vitamins on ECF (3.A.1.25…), phospholipids on
3.A.3, bile-acid conjugates (2.A.28), plus a few single N compounds (cyanide on `sul1`/`sul3`,
tetramethylammonium on `amt1`). None is an obvious N-nutrient class missing from the rules.
Best effort: reviewed for classes at this level, not compound by compound.

**To-do for the sibling Alteromonas analysis:** redefine function-linked enzymes and the curated
transport class there. Cyanorak covers cyanobacteria only, so use TIGR roles and/or KEGG
pathways, which cover heterotrophs better.

## Decide-gate checklist

**Outputs produced** (`methods/`):
- Code: `n_transport.py` v1.6.1, `kg_fetch.py`, `scripts/p1…p12` + `run_pipeline.py` (KG
  calls only through `kg_fetch.fetch`), report scripts p7–p17 + p19, `p18_listing_basis.py`, QC pack `q1_qc_checks.py`; archived probes in
  `scripts/archive/`.
- Tests: `tests/` (193 OK, including real-data invariant tests against the v1.6.0 archive).
- Per strain, `data/{med4,mit9313,natl2a}/`: transporter universe, Pfam role map, systems
  (reference + grid), neighbour candidates, substrate tables (large ones gitignored, regenerable),
  expectation/expected-negative tables, `p11_*` links/tiers, `p12_*` classes.
- Across strains: the review list, the p7–p17 reports, `data/qc/` (QC pack), `figures/` fig1–fig9 + `methods_review.html`.
- `data/answer_key/` (independent verifier).
- Regeneration: `.venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/run_pipeline.py --organism "Prochlorococcus MED4" --out-dir analyses/2026-10-06-pro_n_import_coculture/methods/data/med4 --pilot`
  (same for MIT9313 and NATL2A, without `--pilot`).

**Results presented:** Results section tables (per-strain build; data-driven N-substrate table +
labelled curated view; expected-negative 1 per genome; §3.4 method checks; round-1 workaround
audit); Decisions 1–21; tier counts; the QC pack (fig7–fig9) and the review page.

**QC gate:**
- toy tests in real CSV-text form, including the `bool("False")` trap and a default-pandas
  round-trip → 158/158 OK (main thread re-ran);
- six-step pilot vs. the independent MCP-only answer key → all steps pass after fixes (step
  table in "Pilot summary");
- API-usage review → 2 Critical (paging swaps rows; most-specific ≠ specific), both fixed and
  confirmed by main-thread calls; scoped re-review of the fetch helper → fixes applied;
  `strict_inputs` never fired;
- completeness asserts: genes with + without coordinates = `list_organisms` count in all three
  strains;
- expected-negative 1 per genome → pass (nitrate unusable in all three; nitrite usable only
  where `nirA` exists);
- methods critic (data-integrity + interpretation) → 2 Blockers + 8 Concerns, all on the
  narrative, all fixed (`critical_review.md`);
- delta critic on the decide-gate build → 6 Concerns + 4 Notes, fixed or disclosed
  (`critical_review.md`, "Delta pass: decide-gate build");
- no-NaN check on the strict / category columns under default `read_csv` → 0 NaN;
- decide-gate QC pack (a–f) → found the evr/dev splits, curated-role misses and broad listings;
  fixed in decisions 18–20. Real-data invariants hold after both: N systems unchanged,
  expected-negative holds, pilot unchanged (main thread re-ran the 193 tests);
- third critic pass (delta: QC round + v1.5/v1.6) → 0 Blockers, 3 Concerns, 4 Notes; all fixed
  or disclosed in v1.6.1 (`critical_review.md`, "Delta pass: QC round").

**Decisions made this milestone:** Decisions 1–21 (2026-10-07/08), above.

**Advance rationale:** the per-strain transport-system, substrate, link, tier and class tables
are built, checked against an independent answer key, reviewed for API use and by two critic
passes, with every remaining limit disclosed. They are ready for the analysis milestone to pull
expression against, as best effort pending the open KG items (`gaps_and_friction.md`, "Open
items").
