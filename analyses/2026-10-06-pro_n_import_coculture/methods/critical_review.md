# Methods milestone: critical review (2026-10-07)

Fresh-context critic over `methods/` (notebook + per-strain data files; code for reference only).
Lens: **data-integrity + interpretation**. Trusted inputs: `proposal.md`,
`proposal_critical_review.md`, `proposal_notebook.md`. Result: **2 Blockers, 8 Concerns, 2 Notes:
all on the narrative; the data files stand.**

The critic checked and found clean: no duplicate natural keys or full-row duplicates in the
three flagged tables; no PMT/PMT_ collisions in the MIT9313 universe; no RefSeq-tag locus tags in
the NATL2A universe; per-strain counts reproduce (systems 316/462/332, role-complete 45/77/49,
cross-locus 6/7/5, universe 360/528/379, role-map domains 394/503/402); 13 MED4 family_inferred
genes; EN1 row counts; urt/cyn/amt1/dpp memberships; the `focA` nitrite row inherited at
`tcdb:1.A.16` (non-lumping), co-located under window and run; strict MED4 linked list = 6.

---

**B1. Blocker: "peptides: dpp (4 genes)" hides that every peptide row is `can_use = no`.**
In all three strains, most-specific `dipeptide`, `tripeptide`, `L-alanyl-L-alanine` and inherited
`Oligopeptide` are `no`. The only usable row is the inherited generic `peptide` (`chebi:14753`,
name_soft → `pip`): `elsewhere` in MED4/NATL2A, `no` in MIT9313. dpp's usable most-specific
substrates are sugars, heme and 5-aminolevulinate. The step-5 line "the proposal already treats
peptides' can_use as trivial" is contradicted by the data. The verifier's answer key had flagged
this (`pilot_answer_key.md` lines 398, 632).
**Disposition: fixed.** Main thread verified (20 peptide rows per strain; usable most-specific =
5-Aminolevulinate, Heme, Maltose, Melibiose, Raffinose, + Cellobiose in MIT9313/NATL2A). Notebook
rewritten. "How peptides get `can_use` (and whether a name_soft inherited row may rescue it)" is
now an explicit decide-gate item.

**B2. Blocker: strict-definition "pass" for nitrite in MIT9313/NATL2A rests on a helicase.**
`recQ` PMT0189 / `crhR` PMN2A_0647 (`tcdb:2.A.16`, `tcdb_only`) is the only non-`n/a` row; `focA`
is `n/a`.
**Disposition: fixed.** Main thread verified. The notebook now states that the strict variant's
pass is not validation and that the strict variant misses the true positive. This feeds the
decide-gate item on the strict rule.

**C1. Concern: expected-negative 1 is close to circular for the control strains** (expectation and
`can_use` share the metabolism arm).
**Disposition: accepted, reworded.** Relabelled as an internal-consistency check for
MIT9313/NATL2A; the informative rows (`focA`; MED4 cyn nitrate/nitrite with the independent
grounding-item-6 anchor) are named.

**C2. Concern: the N-systems table was curated, not a file view; it hid cyn's nitrate/nitrite
most-specific rows and regulator rows (in MED4 too).**
**Disposition: fixed.** Replaced with a data-driven table (all / most-specific / strong rows and
genes per compound per strain, computed from the flagged tables), followed by an explicitly
labelled curated view.

**C3. Concern: strict ≠ transporter; regulator/helicase rows pass the strict filter.**
**Disposition: fixed** (noted in the notebook). At the decide gate `likely_transporter` will be
shown beside the strict columns.

**C4. Concern: the strict linked-enzyme list still holds artefacts** (`pncC` ×3 strains; MIT9313
`ribD`, `hisD` via `putP`/`grrP` at 12 kb).
**Disposition: fixed.** "Linked enzyme" is now defined in the notebook as a reaction-sharing gene
within ±8 in any direction, not an operon partner; the coincidences are listed.

**C5. Concern: PMN2A_RS10340 is a 53-aa nirA fragment, not a second nirA; it also takes ±8 rank
slots.**
**Disposition: fixed** (wording; rank-slot effect noted). No data change. Whether RefSeq-only
fragment nodes should be excluded from rank windows is a decide-gate note.

**C6. Concern: "NATL2A: no cyanate rows" is false; there are 26 inherited lumping-family rows
flagged `elsewhere` via `cynS`.**
**Disposition: fixed** (reworded to "no most-specific cyanate rows; 26 inherited…").

**C7. Concern: the `amt1` §3.4 check is trivially satisfied; the dpp most-specific set is broader
than "sugars".**
**Disposition: fixed.** §3.4 row relabelled "trivially satisfied"; the full dpp most-specific set
(EDTA, Heme, Stachydrine, 5-Aminolevulinate, Bradykinin, Nickel(2+), sugars) is listed for the
class-grouping decision.

**C8 (main-thread addition while dispositioning). Strict-variant value `"n/a"` is parsed as NaN
by default `pd.read_csv`.**
**Disposition: fix sent to the coder** (rename to `not_eligible`, and a default-pandas read test).
This is the same class of bug as round 1's `bool("False")`.

**N1. Note: `role_complete = True` for single carriers is vocabulary, not function.**
**Disposition: noted in the notebook.**

**N2. Note: the audit claim "14/16 curated" is unverified.**
**Disposition: disputed with citation.** `proposal_notebook.md` grounding item 14 records the
`gene_ontology_terms(ontology=['pfam'])` call on the 12 MED4 N-transporter genes: 16 rows, 14
`curated` (by_evidence curated 14, family_inferred 2). It was verified at the Plan phase, from
that call's envelope.

---

# Delta pass: decide-gate build (2026-10-08)

Scope: the delta after the first pass, i.e. the Decisions section, the p11 link/tier tables, the
p12 classes and review list, and the p14 reports (v1.3.0). Steps p1–p6 and the first-pass
dispositions were treated as trusted. Lens: data-integrity + interpretation. Result: **0
Blockers, 6 Concerns, 4 Notes. Mechanically sound** (no duplicates in the link or classified
tables; no currency or ubiquitous leaks; counts match; the pilot reproduces; the ≥30 ubiquity
cutoff is supported; multi-gene systems are favoured, not penalised: High 36–39% of multi-gene
vs 10–12% of single-gene). The problems are in meaning and in the record.

**F1. Concern: the Medium tier is mostly catalogue-only hits, many plainly non-transporters.**
`tcdb_only + resolved` supplies 88/122, 123/170 and 92/128 Medium systems; at least 37/51/39 are
helicases (`recQ`, `crhR`, `recG`, `ruvA`), Clp proteases, `dnaK2`, GAPDH, `topA`, sensor kinases,
`sufC`. Glutathione S-transferases and `sodX` reach Medium via a BRITE KO. A helicase outranks the
real permease `salY`.
**Disposition: fixed (researcher-approved package a + b).** Catalogue-only systems go to Low; a
KEGG transporter KO, like a curated role, only upgrades catalogue-listed genes. This was a design
flaw in the author's tier proposal and is logged as friction.

**F2. Concern: Decisions 9 and 12 describe v1.2.0, not the v1.3.0 code that wrote the files**
(names-only classes; the Q role AND TCDB rule).
**Disposition: fixed (f).** Decisions 13+ record the v1.3.0/v1.4.0 rules; Decision 12's layers are
marked superseded.

**F3. Concern: ferritin is "strong"/Medium via a curated Q.4 role + a score-0 TCDB 1.A.155 hit,
and the notebook doesn't say so.**
**Disposition: disclosed (c).** It can't be separated from `focA` (also score 0) by rule, so a
`known_false_positive` flag is added and the case is disclosed. Also noted: most curated-path
promotions are efflux systems (`tolC`, `acrA`, `mdtA`, `devB`, RND/MFS), so any import reading must
say so.

**F4. Concern: most function links are glutathione S-transferase paralogs and non-transporter
systems.** Only about 6 rows per strain concern N import.
**Disposition: fixed in part.** Fix b removes GSTs from "strong" unless TCDB lists them; link
rows now carry the system tier and a `system_is_transporter_candidate` flag. The notebook now
states that function-linked means "shares a curated role and a KEGG compound", with no implied
co-regulation.

**F5. Concern: the NATL2A `nirA` fragment PMN2A_RS10340 is counted as a second neighbour-linked
enzyme.**
**Disposition: fixed (d).** RefSeq fragment nodes are flagged `fragment_of` and excluded from link
counts.

**F6. Concern: the "pilot met expectations" check is partly circular.** Decisions 9/10 were adopted
to produce the `focA`-Medium and `amt1` ← GS/GOGAT outcomes the pilot then checks.
**Disposition: accepted.** The notebook now separates design targets (`focA` tier, `amt1` links)
from independent checks (`pncC` unlinked, `salY` Low, cyn/urt/dpp/pst High). The independent
checks this pass found (ferritin, helicase-Medium) are what drove fixes a/b/c.

**N1. Note: name-rule misses** (cystine, betaines/carnitines, ectoine, selenoamino acids, bradykinin,
amino sugars; quaternary ammoniums wrongly counted as ammonium analogues).
**Disposition: fixed (e).**

**N2. Note: the review-list rule omits "non-lumping".** **Disposition: fixed (f),** rule documented.

**N3. Note: no `class_caveat` column on the substrate rows.** **Disposition: fixed** (column added).

**N4. Note: "57% vs 40%" was not recomputed in this pass.** **Disposition: verified at pilot step 6**
(`data/pilot/p6_med4_genome_distributions.json`, main thread), cited in the notebook.

---

# Delta pass: QC round and v1.5.0 / v1.6.0 (2026-10-08)

Scope: the notebook's "Decide-gate QC round" section and decisions 18–20, `data/qc/`, p16–p18 outputs,
fig2/fig7–fig9, and the new rules in `n_transport.py`. Earlier passes and decisions 1–17 trusted.
Lens: data-integrity + interpretation. Result: **0 Blockers, 3 Concerns, 4 Notes. Every number
checked matches the files**; adjacent_abc merges are correct by the rule; no current dedicated call
is a keyword false positive.

**C1. Concern: a curated Q.1 role made a multidrug efflux pump "dedicated" for amino acids and
peptides** (MIT9313 sys_PMT0977, "ABC multidrug efflux transporter", TCDB exporter families). Q.1 is
not class-specific (it is also on urtA–E, cynA, hisF).
**Disposition: fixed (v1.6.1).** Q-role-only dedicated calls are barred for efflux-annotated systems.
PMT0977 is now broad for both classes; no other call changed; every dedicated call now rests on a
keyword. Q.1's lack of specificity is stated in decision 21.

**C2. Concern: the curated-role lift mostly promotes efflux/export proteins, undisclosed** (12 of
23 efflux, 6 DMT/EamA, 5 import-type), repeating the pattern disclosed under F3. Several now feed N
results (MIT9313 Medium broad amino-acid and urea listings).
**Disposition: fixed + disclosed (v1.6.1).** A new `efflux_annotated` system flag is carried in the
p11 and p18 tables, and the breakdown, confirmed at 12 / 6 / 5, is in decision 21 and
`data/p19_lifted_loci_split.csv`.

**C3. Concern: fig2 Block A "+k" presented K⁺/Na⁺ transporters as extra usable ammonium routes**,
contradicting decision 20.
**Disposition: fixed (v1.6.1).** Block A now shows "+k dedicated, +k broad". Ammonium is +0 dedicated
in all strains.

**N1. Note: a Low-tier helicase (crhR) appeared as a nitrite example.** **Fixed:** examples are
High/Medium only.

**N2. Note: MAPEG glutathione protein PMT1025 was not flagged.** **Fixed:** it is now a known false
positive. The MED4/NATL2A MAPEG genes are not in the universe.

**N3. Note: the keyword map was latently fragile; proV/W/X and proP were double-counted** (amino
acids + osmolytes). **Fixed:** word boundaries and exclusions, with toy tests. The double count is
disclosed (`data/p19_double_dedicated.csv`) and left as is.

**N4. Note: wording.** Nucleobases are "none" in NATL2A, not broad; the porins are outside the
candidate set. **Fixed** in the notebook.

