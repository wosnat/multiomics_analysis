# Step 3 — Analysis framing (research proposal lock)

## Context

Steps 1–2 locked the question (genomic P-acquisition capacity, LL vs HL) and the
entries (curated Cyanorak D.1.5 role at OG level; 9-strain MCP-resolvable panel,
4 HL / 5 LL). Step 3 selects controls, defines the focused acquisition subset and
the capacity metric, states the hypothesis and expected outcome, and preregisters
predictions. End of step 3 locks the proposal; steps 4–6 execute against it.

## What I did

- **`scripts/01_control_categories.py`** — per-strain counts for the target role
  and the control suite across all 9 strains → `data/control_categories_by_strain.csv`.
- **`scripts/02_classify_p_ogs.py`** — classify the D.1.5 OGs into
  acquisition / responsive_other / unclear → `data/p_og_classification.csv`.

## Results

### Control-suite validation `[KG]` (raw-count ecotype means; full roles)

| Cyanorak role | role plays | HL mean | LL mean | LL/HL |
|---|---|--:|--:|--:|
| K.2 ribosomal | invariant baseline | 61.0 | 61.0 | **1.00** |
| D.1.3 nitrogen | specificity control | 16.2 | 16.0 | 0.99 |
| D.1.2 light | positive control | 33.8 | 37.8 | 1.12 |
| D.1.7 trace metal | specificity control | 37.5 | 42.6 | 1.14 |
| D.1.5 phosphorus | target | 32.8 | 37.6 | 1.15 |

Controls behave as intended: ribosomal is exactly flat (clean invariant baseline);
light varies strongly and clade-structured (LLI 57–60 vs LLIV 21 — the positive
control confirms the method resolves real ecotype differences). On the **full**
role, P expansion in LL (1.15) is no larger than trace-metal (1.14) and N is flat
— so any P signal must come from the focused subset, not the whole role.

> **Note on per-1000 normalization.** Fixed-core categories (ribosomal: 61 in
> both ecotypes) do *not* scale with genome size, so per-1000 LL/HL ratios are
> all < 1 (a bigger LL genome dilutes a fixed core) and conflate "fixed core" with
> "no expansion." Decision: the primary capacity metric is the **raw-count LL/HL
> ratio benchmarked against the control suite**; per-1000 is reported as secondary.

### Focused P-acquisition subset `[KG]` (`data/p_og_classification.csv`)

48 distinct D.1.5 OGs → **23 acquisition**, 16 responsive-other, 9 unclear
(after the step-3 decide reclassification — see Decisions). The 23 acquisition OGs:

- **10 universal** (all 4 HL & all 5 LL): pstS, pstA, pstB, pstC, phnC, phnD,
  phnE, phoH, sqdB, "possible phosphatidic acid phosphatase" — the conserved core.
- **LL-only:** ptrA (Crp-family phosphate regulator) 0 HL / 4 LL; phoC (acid
  phosphatase) 0/2; ppk2 (polyphosphate kinase) 0/2; PsiE-like 0/2; PAP2-superfamily
  phosphatase 0/2.
- **HL-only:** PsiP1 (P-starvation-inducible protein 1) 1 HL / 0 LL;
  "putative phosphatase" 1/0.
- **Sparse/shared:** phnC2/phnD2/phnE2, ptxD (phosphonate-utilization paralogs)
  1 HL / 1 LL; phoB 3/3; phoR 3/4.

Researcher decision at the decide gate: include the clear phosphatase-family OGs
(PAP2-superfamily, "putative phosphatase") in acquisition (21 → 23); leave the
PIN/PhoH-domain protein and the generic `som` porin in `unclear`. `spsA` (sucrose
metabolism, "...phosphatase fusion") stays responsive-other (keyword guarded).

## Framing

**Hypothesis.** LL ecotypes carry greater and/or qualitatively different genomic
P-acquisition capacity than HL — i.e., more acquisition ortholog groups and/or
LL-specific acquisition machinery.

**Capacity metric (locked).** Per strain, the count of focused P-acquisition OGs
present (the 23-OG subset). Ecotype comparison via the **raw-count LL/HL ratio**,
read against the control suite; plus the **presence/absence repertoire** (which
acquisition OGs are LL-only vs HL-only). Secondary: per-1000-genes count.

**Controls and the role each plays.**
- *Invariant baseline (negative)* — K.2 ribosomal: LL/HL ≈ 1.00. P "capacity"
  counts only if its LL/HL exceeds this.
- *Specificity* — D.1.3 nitrogen and D.1.7 trace-metal adaptation. P is *specific*
  only if its LL/HL exceeds these; if P ≈ trace-metal, the effect is a general
  "LL carries more adaptation machinery" trait, not P-specific.
- *Positive (method validation)* — D.1.2 light: confirmed to vary by ecotype/clade,
  so the method can detect a true ecotype difference.

**Expected outcome (KG-operational).** In the step-5 per-strain focused-acquisition
table: LL mean OG count > HL mean; LL/HL > 1.0 and > the ribosomal (≈1.00) and
nitrogen (≈0.99) ratios; the presence/absence matrix shows ptrA/phoC/ppk2 as
LL-present / HL-absent rows.

**Preregistered predictions** (named; tested in step 6):
1. **(more)** LL focused-acquisition OG count > HL, with LL/HL ratio above the
   ribosomal invariant baseline and the nitrogen specificity control.
2. **(different)** ≥1 acquisition OG is present across LL and absent across HL —
   the regulatory/scavenging candidates ptrA, phoC, ppk2 (not the core transporters).
3. **(P-specific?)** the LL-vs-HL P-acquisition difference is at least as large as
   trace-metal and larger than nitrogen. *On the full-role preview P ≈ trace-metal,
   so this prediction may fail — it is the genuine specificity test.*

## Surprises

- On the full role, P expansion in LL is indistinguishable from trace-metal
  adaptation, and nitrogen does not expand at all. "LL better equipped" is, at the
  role level, neither P-specific nor adaptation-general — it tracks a subset of
  adaptation categories (P, trace-metal, light), not all.
- The candidate LL signal is regulatory/scavenging (ptrA regulator, phoC acid
  phosphatase, ppk2 polyphosphate kinase), not the core uptake transporters, which
  are universal.

## Decisions

- **2026-06-14 — capacity metric = focused 21-OG acquisition subset, raw-count
  LL/HL benchmarked against control suite; per-1000 secondary.** Rationale:
  fixed-core categories break per-1000; the full role is contaminated by responsive
  non-acquisition genes.
- **2026-06-14 — control suite = K.2 ribosomal (invariant) + D.1.3 N + D.1.7
  trace-metal (specificity) + D.1.2 light (positive).** Expanded from the
  researcher-approved N+trace-metal to add ribosomal baseline and light positive
  control.
- **2026-06-14 — focused acquisition subset = 23 OGs.** Researcher included the
  two clear phosphatase-family OGs (PAP2-superfamily, "putative phosphatase") from
  the borderline set; PIN/PhoH-domain protein and the generic `som` porin remain
  excluded as unclear.

## Decide-gate checklist

- **Outputs produced:** `scripts/01_control_categories.py`,
  `scripts/02_classify_p_ogs.py`; `data/control_categories_by_strain.csv` (9),
  `data/p_og_classification.csv` (48), 2 logs.
- **Results presented:** control-validation table, focused-subset repertoire (above).
- **QC gate:** invariant baseline ribosomal LL/HL = 1.00 (control behaves) →
  baseline valid. Positive control (light) varies by clade → method sensitive.
  Classification reviewable in CSV; borderline OGs flagged.
- **Decisions made this step:** metric, control suite, focused subset (above).
- **Advance rationale:** hypothesis, metric, controls, predictions and the focused
  subset are defined and KG-grounded → proposal locked; step 4 builds the metric
  module with a worked example.
