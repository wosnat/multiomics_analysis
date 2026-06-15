# Step 1 — Research question

## Context

Researcher's prompt: *"motility in alteromonas under different conditions."*
Motivation given: motility genes are differentially expressed in Weissberg et
al. 2025 (the *Prochlorococcus*–*Alteromonas* coculture study), and the
researcher wants to understand that signal. Scope guidance: "this is a dogfood
run — whatever is in the KG."

This step was co-defined with the researcher: we agreed the question is about
**expression** (when motility is regulated), settled on a coculture-vs-alone
contrast, and chose to include all strains that have both measurements.

## KG context (grounding queries)

KG release verified earlier this session: `kg_release_info` → ok, KG
0.1.0-alpha.6. Grounding queries for this analysis:

1. `list_experiments(organism="Alteromonas", summary=true)` — condition/strain
   landscape (49 matching experiments).
2. `genes_by_function(search_text="flagell* OR chemotaxis OR motility OR pili OR
   'type IV'", organism="HOT1A3", summary=true)` — motility annotation coverage.

### What the KG holds `[KG]`

- **Strains with expression data:** Alteromonas macleodii HOT1A3 (8 exp),
  MIT1002 (5), EZ55 (12), plus a MarRef reference set (20, proteomics); several
  strains have vesicle-proteomics only.
- **Conditions:** coculture (31) vs axenic/alone; carbon (24); nitrogen (4);
  darkness (2) / diel. Omics: proteomics (23), RNA-seq (19), vesicle/exo.
- **Motility annotation:** 115 HOT1A3 genes hit motility terms; 90 fall under the
  "Cell motility" gene category (flagella + chemotaxis), plus signal-transduction
  (chemotaxis) genes. Well annotated.
- **Pre-computed motility summaries exist** (derived metrics on an Alteromonas
  strain): `enrichment_flagellar_assembly`, `enrichment_bacterial_chemotaxis`,
  and diel `periodic_in_coculture` measures — potential leads for later steps.
- **Anchor:** Weissberg 2025 (DOI 10.1101/2025.11.24.690089) contributes 5
  Alteromonas experiments.

## Locked question

**Original lock (2026-06-15):**

> When *Alteromonas* grows in coculture with *Prochlorococcus* versus alone, does
> it up- or down-regulate its motility genes (flagellar assembly + chemotaxis)?

**Evolved during the redo (2026-06-15)** — step 2 surfaced that every usable
coculture contrast runs in a medium with **no added organic carbon**, where
*Prochlorococcus* photosynthate is *Alteromonas*'s only organic-C source. That
turns the coculture-vs-axenic contrast into a carbon-source manipulation, so the
question became:

> When *Alteromonas* grows with *Prochlorococcus* versus alone — in media with no
> added organic carbon — does its physiology shift toward a **carbon-fed** state,
> and how does **motility (flagella + chemotaxis)** respond? (Motility stays the
> lead readout; the carbon-provision hypothesis is the frame. See step 3.)

**Scope:** all *Alteromonas* strains with a usable coculture-vs-axenic contrast,
HOT1A3 (Weissberg) as primary; controls = glucose-fed references,
*Synechococcus*-partner, starvation/darkness. Motility gene set pinned in step 2.
4 experiments with corrupted direction dropped (step 2 / gaps_and_friction).

## Decisions

- **2026-06-15 — expression framing, coculture-vs-alone contrast.** The question
  is about regulation (differential expression), not gene presence. Rejected the
  day-night-rhythm and all-conditions-survey shapes (researcher chose the
  coculture contrast as the cleanest extension of the Weissberg anchor).
- **2026-06-15 — all strains with the contrast, not just HOT1A3.** To test
  consistency of the response across strains, accepting a cross-study/platform
  flag where relevant.
- **2026-06-15 (redo) — question evolved to a carbon-provision frame.** The medium
  finding in step 2 (no added organic C in any usable coculture contrast) reframed
  "does motility move?" into "does coculture make Alteromonas look carbon-fed, with
  motility as the lead readout?" Motility focus retained; hypothesis added. This
  is the dogfooding catch that a step-2 data reveal can legitimately reopen a
  step-1 lock — noted for the skill (lock-vs-data-reveal).

## Decide-gate checklist

- **Outputs produced:** scaffold (`paper.md`, `gaps_and_friction.md`,
  `.gitignore`) + this notebook. No scripts (step 1 is a conversation).
- **Results presented:** Alteromonas condition/strain landscape and motility
  annotation coverage (KG context above), shown to the researcher in chat;
  locked question + scope.
- **QC gate:** KG release verified ok; motility annotation confirmed present
  (90 cell-motility genes in HOT1A3); coculture and axenic conditions both
  confirmed to exist before locking a coculture-vs-alone question.
- **Decisions made this step:** framing + scope (see Decisions).
- **Advance rationale:** question and scope agreed with the researcher and
  confirmed feasible from KG expression data; step 2 can enumerate the exact
  experiments and motility gene set.
