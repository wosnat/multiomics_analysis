# Step 3 — How we'll test it (framing)

## Context

Steps 1–2 locked the question and froze the inputs (HOT1A3 + EZ55; motility gene
sets KEGG flagella+chemotaxis and COG-N). Step 3 sets the test, co-defined with
the researcher: direction-agnostic, with a ribosomal baseline control.

## The test

**Hypothesis.** In coculture with Prochlorococcus vs alone, Alteromonas motility
genes (flagella + chemotaxis) are *coordinately* regulated — they move together,
more than the genome-wide background. Direction (up or down) is **observed, not
predicted** (researcher's call: stay agnostic).

**What we measure**, per coculture-vs-alone experiment and per gene set:
- **Direction** — how many motility genes are significantly up vs down in
  coculture (and the typical fold-change).
- **More than background?** — whether motility genes are over-represented among
  the genes that change, compared with all detected genes (an over-representation
  test). This needs all genes reported, so it is computed for **HOT1A3**; EZ55
  reports significant genes only, so EZ55 gives **direction only** (a cross-check).

**Gene sets.**
- Motility, primary: KEGG flagellar assembly + bacterial chemotaxis (~96–102/strain).
- Motility, sensitivity: broad COG-N "Cell motility" (~126–131/strain).
- Baseline control: KEGG ribosome (54 genes in both strains) — see below.

**Controls and what each rules out.**
- *Genome-wide background* — the fair denominator for "more than expected."
- *Ribosomal baseline* (KEGG ribosome, 54 genes both strains, confirmed) — a
  "shouldn't-care-about-the-partner" set. If motility moves but ribosomal genes
  don't, the motility signal is specific, not a whole-cell shift.
- *Partner-specificity* (EZ55 only) — coculture with Prochlorococcus vs with
  Synechococcus. Tells whether motility responds to this partner specifically or
  to any partner.

**Expected outcome (operational).** In HOT1A3: motility genes over-represented
among coculture-vs-alone DE genes beyond background, with a consistent direction
across its experiments; the ribosomal set not over-represented. EZ55: significant
motility genes lean the same direction. Partner-specificity: reported.

**Preregistered predictions** (tested in step 6):
1. **(coordinated)** Motility genes (KEGG set) are over-represented among
   coculture-vs-alone DE genes in HOT1A3, beyond the genome-wide background.
2. **(specific)** The ribosomal baseline is *not* over-represented — the motility
   response is not just a whole-cell shift.
3. **(consistent)** The direction is consistent across HOT1A3's experiments and
   agrees with EZ55's significant motility genes.
4. **(partner — exploratory)** Motility responds to Prochlorococcus; whether it
   also responds to Synechococcus (EZ55) is reported, not predicted.

## Decisions

- **2026-06-15 — direction-agnostic.** Predict coordinated regulation and report
  the observed direction; do not preregister up or down.
- **2026-06-15 — controls = genome background + ribosomal baseline + EZ55
  partner-specificity.** Ribosomal = KEGG ribosome ko03010 (54 genes both strains).

## Caveats carried forward

- EZ55 reports significant genes only → no clean over-representation test there
  (direction-only cross-check).
- Two strains, partly different studies/platforms → cross-strain agreement is
  suggestive, not definitive.

## Decide-gate checklist

- **Outputs produced:** this framing notebook (no scripts; baseline validated via
  MCP `genes_by_ontology`).
- **Results presented:** the test, controls, predictions (above), and baseline
  gene-set counts (54 both strains).
- **QC gate:** ribosomal baseline confirmed present and equal-sized in both
  strains; over-representation test scoped to the all-genes strain (HOT1A3);
  EZ55 limitation recorded.
- **Advance rationale:** hypothesis, metric, controls, and predictions are set and
  KG-grounded → proposal locked; step 4 builds the gene-set DE-summary method.
