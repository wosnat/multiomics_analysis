# Methods milestone — notebook

Main-thread-owned. The coding subagent returns artifacts (scripts, tables, run
logs); judgment and interpretation live here.

## Co-define (agreed 2026-07-12)

**First and only task this round: build the HOT1A3 transporter table and assess
how specific the substrate resolution actually is.** This is the riskiest part of
the plan — the whole analysis hinges on being able to name substrates — so we look
at the real resolution before building any scoring code.

- **Scope:** HOT1A3 only (the primary experiment). EZ55 comes later, once the
  approach is shown to work here.
- **Gate:** we review the real table together and decide whether the resolution is
  good enough to proceed. **No scoring code is built until then.**
- **What the table must let us judge:** per transport system — its genes (locus
  tags), the substrate call, how specific that call is (specific compound / narrow
  class / broad class / several options / unresolved), the confidence flag, the
  source of the call, importer-vs-exporter, and organic-vs-inorganic. Plus a
  summary of the distribution (how many land at each specificity level).
- **Rules come from the approved `proposal.md`** (enumerate from KEGG KO + BRITE
  ko02000 + TCDB + annotation; reconstruct systems by adjacency + component role
  from the KO name + shared substrate, with the boundary rule; resolve substrate at
  the finest the evidence *confidently* supports; KO name is the primary substrate +
  role source).

## Do — run manifest (from the coding subagent, facts verified against the files)

Artifacts under `methods/`: `pull_transporter_raw.py`, `build_transporter_table.py`,
`hot1a3_transporter_table.csv` (532 systems), `hot1a3_transporter_gene_table.csv`
(592 genes), `run_manifest.md`, `cache/` (frozen KG pulls).

- Enumeration union (4 sources) = **592** candidate transporter genes (BRITE 310,
  KEGG-KO-named 219, TCDB 427, product/function 415).
- Systems reconstructed = **532** (492 single-gene, 40 multi-gene). Adjacency =
  same contig + strand + gap ≤150 bp, refined by KO-name role + the boundary rule.
  Canonical operons reconstruct correctly (Fe, phosphate, nitrate, Mla, 5-gene
  dipeptide kept whole).
- Resolution (all 532 systems): specific 121 / narrow 13 / multi 15 / broad 20 /
  unresolved 363.
- Classification: importer 418 / exporter 114; organic 73 / inorganic 96 /
  unknown 363.
- **Organic-carbon importer systems = 59** (the carbon catalog): specific 19,
  narrow 13, multi-substrate 13, broad 14.
- KG connection dropped partway; subagent finished from the frozen cache (no output
  depends on the live KG). Build step is fully reproducible from cache.

## What the table shows / resolution assessment (main thread)

**The carbon catalog is real and chemically coherent.** The 59 organic-C importer
systems collapse to **36 distinct candidate carbon compounds/classes**, spanning the
substrate types we'd expect a marine heterotroph to use: amino acids (arginine,
proline, glycine, branched-chain, polar-aa, ser/thr, trp/tyr), peptides
(di/oligo/peptide, peptide-nickel), sugars (fucose, xylose, gluconate, maltose,
fucose/galactose/glucose, + broad sugar/saccharide), organic acids (L-lactate,
carboxylate), osmolytes (choline, betaine/carnitine, glycine-betaine), nucleosides
& cofactors (purines, nucleoside, NMN, B12), glycerol, lipids. The pre-registered
**expected-negative aromatics** (benzoate, 3-phenylpropionic acid) are present and
flagged — the falsifiability check has something to bite on.

**How specific:** of the 59 systems, 32 (54%) resolve to a specific compound or
narrow class; 13 are multi-substrate (options listed); 14 are broad. Usable.

**Multi-system coherence (what the scoring leans on):** of the 36 candidate modules,
**15 have ≥2 transport systems** (polar amino acid 6, sugar 4, amino acid 3,
fucose/galactose/glucose 3, + 11 with 2); **21 have a single system** → thin
evidence (handled by the plan: 1-system modules pass with a proper q but carry their
system count).

**The 1-gene-system reality — verified, not a bug.** 53 of the 59 organic systems
are single-gene. I checked two polar-amino-acid binding proteins (`ACZ81_09705`,
`12280`) with `gene_neighbors`: **their neighbours are unrelated genes** (an
oxidoreductase, `rimO`; `accD`, `truA`) — no ABC permease/ATPase adjacent. So these
are genuine **orphan solute-binding proteins** (or single-gene secondary
transporters), not missed adjacency. Consequence: per-system evidence is often one
gene, so multi-subunit co-movement mostly *doesn't* apply and coherence has to come
at the **module** level (several binding proteins for one class), which works for the
15 multi-system modules and leaves the 21 single-system ones honestly thin.

**Confidence:** 29 confident / 30 inferred among the organic importers. The
"inferred" calls (keyword/product scans — e.g. fucose/galactose/glucose, gluconate,
xylose) need validation during scoring; the "confident" ones come from structured KO
"X transport system" names or BRITE leaves.

**My read:** resolution is **good enough to proceed** — coherent catalog, ~half
specific/narrow, expected classes covered, 15 modules can show coherence, and the
expected-negative aromatics are captured. No reconstruction redo needed (the 1-gene
systems are largely biological).

## Diagnostic checks (researcher questions) + cleanup pass

Researcher asked three questions before deciding; answered from the data:
1. **Are all candidate genes in a system?** Yes — 592 genes → 532 systems, **0
   dropped, 0 double-counted** (systems partition the candidate set).
2. **Neighbours / word-matching / missed partners?** Full-genome neighbourhoods of a
   12-system sample showed the single-gene systems are **mostly genuine**: ~half are
   single-gene secondary transporters (SstT, PutP, MFS, NupC — correctly one gene),
   ~half are orphan binding proteins whose ABC partners are **not adjacent**.
   Broadening word-matching would inject **false** partners (found adjacent
   "ATP-binding" genes that are a phytochrome `bphP` and an RNA helicase `dbpA`, not
   transporters). One genuine missed partner (`03920` ATPase at gap 0) — not pursued.
3. **Gap too small (150 bp)?** No — true ABC partners sit at **0–40 bp**; the
   single-gene systems' nearest neighbours are unrelated genes at 100–300 bp, so
   enlarging the gap would create **false merges**, not recover partners.

**Cleanup pass (researcher chose this, #1 only):** tightened the importer/organic
classification to drop non-importer leakage; grouping, systems, and the 150 bp gap
unchanged. **6 systems removed from the organic-C set**, all verified genuine
non-importers: `GlpK` glycerol kinase (enzyme), `TatC` (protein export — "arginine"
was the Tat motif), `GumC` + LPS-biosynthesis (surface-polysaccharide synthesis), 2
mechanosensitive ion channels ("lipid" was a spurious text match). Verified the real
glycerol facilitator `GlpF` (`15825`) is kept; no genuine importer over-dropped.

**Final HOT1A3 organic-carbon importer catalog: 53 systems → 33 candidate carbon
compounds/classes** (12 multi-system; resolution: specific 17 / narrow 13 /
multi-substrate 13 / broad 10). Chemically coherent; expected-negative aromatics
(benzoate, phenylpropionic acid) present for the analysis-milestone check.

## Decisions (decide gate)

- **Table accepted as the substrate-resolution basis** — resolution is good enough:
  ~57% specific/narrow, expected classes covered, leakage removed, coverage verified.
- Single-gene binding proteins / secondary transporters **accepted as the scorable
  unit** (the binding protein carries the substrate-specific signal; coherence lives
  at the module level for the 12 multi-system candidates). Gap left at 150 bp;
  word-matching not broadened (both would add errors).
- The ~30 "inferred" calls (keyword/product scans) **flagged for validation during
  scoring**, not audited further now.
- Proceed to build + toy-test the scoring code: **approved** ("proceed").

## Scoring code — built + toy-verified (TDD)

Files: `score_modules.py` (no KG calls), `test_score_modules.py` (toy test, written
first). **Independently re-ran: `uv run pytest` → 9 passed.** (pytest added to the
uv project as a dev dependency.)

**I verified the code against the approved spec (not just that its own tests pass):**
- up-percentile `(rank−1)/(n−1)`, 0=down/1=up, average ties ✓
- system percentile = **median** of subunit percentiles (absent subunits dropped) ✓
- module effect = **max** system percentile ✓
- matched-max permutation null = **gene-resampling matched on both the number of
  systems and each system's subunit count** (the plan's "random same-size system
  sets from the scored gene universe" reading). I re-derived the glucose case by
  hand: sizes [2,1], effect 0.9444 → analytic p = 1−(9/10)(44/45) = **0.12**,
  code = 0.1200 ✓. Seeded per module → reproducible.
- BH across **all** modules incl. 1-system → q; module is the tested unit; system
  count travels with the call (fourth-pass fixes) ✓
- Module builder on the real frozen table (structure only, no scoring): 33 organic
  modules from 53 systems (21 one-system, 12 multi); 100 inorganic controls (84 if
  the interaction-coupled N/P set is excluded).
- **Not run on the real HOT1A3 experiment** — that is the analysis milestone.

**Two implementation choices to confirm (rest are standard):**
1. **Permutation null** built by resampling *genes* (matched on system count +
   subunit sizes), not by resampling existing system percentiles — the more rigorous
   reading, and it matches the plan's "from the scored gene universe" wording.
2. **Inorganic control default includes N/P** (`exclude_interaction_coupled_controls
   =False`); the plan flags N/P as interaction-coupled (not pure negatives), so the
   analysis milestone may want to run with the 84-system clean set. Exposed as a flag.

Minor: one toy test uses `return` instead of `assert` (cosmetic pytest warning).

## Methods milestone — decide-gate checklist

- [x] Transporter table built from the approved 4-source enumeration + reconstruction
- [x] Substrate resolution audited and characterised (53 organic importers → 33
      candidates; ~57% specific/narrow); researcher-reviewed
- [x] Non-importer leakage removed; both directions verified against the real file
- [x] Scoring code implements the approved spec incl. fourth-pass fixes
- [x] Toy-tested (TDD), hand-math checked, tests pass under `uv run pytest`
- [x] No real experiment scored (correctly deferred to the analysis milestone)
- [ ] **Researcher decide-gate approval → commit the methods milestone (one commit)**
