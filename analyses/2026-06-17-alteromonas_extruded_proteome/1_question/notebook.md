# Step 1 — Research question

## Prompt

Researcher: "what alteromonas genes are extruded?"

## Co-define — disambiguating "extruded"

"Extruded" maps to three distinct KG constructs, which would yield different
gene lists:

1. **Secreted (exoproteome)** — proteins measured outside the cell by mass-spec
   (`EXOPROTEOMICS`; `exoproteome_detection_status` metric). Observed.
2. **Vesicle cargo** — products packaged into extruded membrane vesicles
   (`VESICLE_PROTEOMICS`; vesicle/cell enrichment metric). Observed.
3. **Predicted exported** — sequence prediction of extracellular / outer-membrane
   localization (PSORTb) and/or signal peptide (SignalP). Genome-wide, predicted.

**Researcher decision:** "Measured, either route" — the union of (1) secreted and
(2) vesicle cargo. Observed evidence only; prediction (3) excluded.

## Locked research question

Which Alteromonas genes encode products that the lab has **measured leaving the
cell** — detected either in the secreted **exoproteome** or as **membrane-vesicle
cargo** — and what is that annotated locus-tag list?

- `[KG]` Observed evidence only: exoproteomics + vesicle proteomics. No PSORTb/SignalP.
- Output keyed on **locus tags** (Rule 2); gene names as labels only.
- Strain scope deferred to step 2 — determined from which Alteromonas strains
  actually carry exoproteome / vesicle measurements in the KG (just-in-time, not assumed).

## KG release

`0.1.0-alpha.6`, built 2026-06-16, git ffef4007. `kg_release_info` verdict: ok
(explorer 0.1.0a4, 16/16 schema asserts pass).

## Decide

- [x] "Extruded" disambiguated and locked with researcher (measured, either route)
- [x] Locus-tag-keyed output agreed (Rule 2)
- [x] Strain scope explicitly deferred to step 2 (just-in-time)
- [x] Scaffold created; ready to commit step 1
