# Evaluation milestone — notebook

Owner: main thread. Interpretation only — judges whether the analysis milestone's
(already-vetted) results earn the conclusion, against the proposal's framing. No new
computation; the analysis `data/` and figures are trusted evidence.

## Context

Close the arc: judge the conclusion against the proposal's framing ("method works if" +
validation set), write the paper Discussion + Limitations, harvest caveats, and run the
interpretation-only critic. The conclusion under judgment: a graded, class-level candidate
carbon catalog — sugars foremost, organic acids second — not named compounds; the aromatic
expected-negative a complication; iron a confound; the whole signal transcript-level.

## Framing judgment (proposal "Validation set" / "Method works if")

| Proposal check | Outcome | Verdict |
|---|---|---|
| Motility/flagellar **down** | HOT1A3 0.18, EZ55-400 0.14 (EZ55-800 0.68 fails) | **passes** (primary) |
| Ribosomal/translation **~neutral** | 0.50 | **passes** — growth-rate shift not read as carbon |
| Inorganic importers **don't track carbon** | control-ABC neutral (0.59), specific vs candidates | **passes** (but iron = interaction-coupled, dropped) |
| Glycolate `glcB` **up if source** | glcB −1.7 (down) | **uninformative** (proposal: a glycolate miss is not a failure) |
| Organic-matter-degradation signal reappears | genome guard: carbohydrate + nucleotide metabolism up | **partial** — carbon/nucleotide up; peptidases not specifically up (peptides flat) |
| Chemical coherence (marine-DOM class set) | hits = sugars / nucleosides / organic acids | **passes** — but deliberately weak/near-confirmatory, as pre-flagged |
| **Aromatic expected-negative** must **not dominate** | benE prominent in HOT1A3 but strain-specific, doesn't reproduce, no coherent transporter+catabolism unit | **passes as non-domination**, but a **partial complication** (benE #2 in the primary) — reported honestly |
| Coarse-module domination fails the bar | top hits are resolved (carbohydrate, citrate), not unresolved coarse modules | **passes** — catalog not coarse-dominated |
| **Falsifiable core:** per-module reproducible q<0.10 across independent experiments | **no single compound** reproduces; sugars reproduce at **class level, partially** (2 of 4 shared carriers) | **thin / partial** — the strict bar is not cleanly met at compound level; met at class level for sugars |

**Judgment.** The machinery validated (direction sanity, neutrality controls, specificity
vs inorganic), and the pre-committed falsification checks behaved honestly — the aromatic
expected-negative did not resolve into a supported source, and the catalog is not dominated
by coarse/unresolved modules. The strict falsifiable core (compound-level reproducibility)
is **not cleanly met**; what reproduces is a **chemically-coherent class** (sugars, with
organic acids weaker). This is exactly the graded-catalog, possibilities-not-answers
outcome the proposal committed to as acceptable at the current evidence — with wet-lab
growth as the decisive test. The method did what it promised: it **prioritized**, it did
not **decide**.

## Caveat harvest (→ paper Limitations)

Consolidated from `analysis/notebook.md` and both analysis critic passes: correlational
consumer-side inference (carbon conflated with N-exchange / growth / iron); transcript-level
(proteomics underpowered — neither confirms nor refutes); class-level resolution only (no
specific compound reproduces); thin/heterogeneous evidence (one fully-rankable experiment;
EZ55 `significant_only`, 3–5-module family, 6 shared substrates, failed 800-motility);
no producer-side exometabolome in the KG; KG-bounded annotation depth; catabolism direction
knowable only where a degradation map exists.

## Decisions
- Foreground **sugars** as the lead candidate but state reproducibility as *partial and
  class-level* (not "reproducible across strains" unqualified) — per the analysis delta-critic.
- Present the amino-acids-not-induced and iron-up results as first-class findings (informative
  negatives / confound), not footnotes.
- Frame the deliverable as a **wet-lab shortlist**, never as identified carbon sources.

## Decide-gate checklist (evaluation milestone)
- **Outputs:** paper.md **Discussion** + **Limitations** written; this framing-judgment notebook.
- **Results presented:** framing-judgment table above; conclusion consistent with the
  analysis figures/matrix (no new numbers introduced).
- **QC gate:** every Discussion claim traces to an analysis result already verified against
  the KG; no compound-level or causal over-claim; caveats carried.
- **Advance rationale:** the conclusion is earned by the vetted analysis and honestly
  hedged; ready for the evaluation (interpretation-only) critic, then researcher approval.

**Critical review (evaluation, interpretation only):** `critical_review.md`. **No Blockers**;
1 Concern + 2 Notes, all minor wording, all fixed — motility "passed where testable" → names
the EZ55-800 failure; sugars "top class" → "among the most-induced (near-tied with
nucleosides)"; citrate → "just below the FDR bar". The critic confirmed the conclusion is
earned and every hedge carried. **Ready for researcher approval + commit — closes the arc.**
