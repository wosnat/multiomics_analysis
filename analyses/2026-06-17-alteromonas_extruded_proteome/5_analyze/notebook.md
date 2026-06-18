# Step 5 — Analyze (combined extruded-OG catalogue, all 7 routes)

## Funnel `[KG]`

```
secreted EZ55: 234 tested-absent rows -> 69 detected (exoproteome_detection_replicates >= 1)
vesicle MIT1002 52 | BS11 58 | ATCC27126 50 | BGP6 45 | AD45 29 | HOT1A3 15
combined extruded gene rows: 318
mapped to eggnog OG: 318 ; strain-unique (no OG): 0
distinct extruded OGs: 145
```

The secreted tested-absent guard (`min_value=1`, step-4 watch-item) works: 165 of
234 EZ55 rows were looked for and not detected, correctly excluded.

## Recurrence and route structure `[KG]`

Recurrence (distinct strains sharing an OG):

| n_strains | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| OGs | 74 | 26 | 12 | 16 | 10 | 7 |

- 74 OGs are single-strain; 71 recur in ≥2 strains. Max recurrence = 6 (no OG in
  all 7; secreted contributes only EZ55).
- OGs extruded by **both routes**: 25.
- Figure: `figures/og_recurrence.png` (recurrence distribution + route split).

## Positive control — TonB-dependent receptors `[KG]`

7 TonB-receptor OGs are in the catalogue (control passes — the pipeline captures
the expected outer-membrane cargo). 6 are vesicle-route and 1 is secreted (EZ55,
`eggnog:465WA@72275`); all are strain-diverse: recurrence ≤ 2 strains, each pair a
different strain set. `[interpretation]` The
TonB-receptor family splits into many narrow Alteromonadaceae OGs (paralog-rich),
so individual OGs recur in few strains even though the *function* is ubiquitous.

## Composition of the 25 both-routes OGs — describe first `[KG]`

Counting the 25 both-routes OG products:
- 11 ribosomal proteins (L5, L4, L10, L2, L22, L19, L20, L14, S17, S4, S16)
- 12 other cytoplasmic (HU-beta, malate dehydrogenase, ATP synthase β,
  succinate–CoA ligase β, Fe-SOD, thioredoxin, lumazine synthase, inorganic
  diphosphatase, PRPP kinase, DapD, phasin, bacterioferritin [cytoplasmic
  iron-storage])
- 2 envelope: TIGR04219 outer-membrane β-barrel, peptidoglycan-associated
  lipoprotein Pal

So 23 of 25 both-routes OGs are cytoplasmic by annotation; 2 are
envelope/outer-membrane.

**Structural confound — "both routes" is EZ55-anchored.** `[KG]` Secreted is
measured on EZ55 only, so an OG can only reach `both_routes=True` by being in the
EZ55 exudate AND in some strain's MV cargo. All 25 both-routes OGs contain EZ55.
"Both routes" therefore does **not** mean a protein seen leaving the cell by two
independent routes in the same strain — it is EZ55-secreted ∩ (any strain's MV
cargo). Cross-route co-occurrence here is not strain-independent evidence of dual
extrusion.

`[interpretation]` The both-routes "core" is dominated by abundant cytoplasmic
proteins, not secretion/export machinery. Given the EZ55 anchoring above, the
abundance-driven reading is the leading one by construction: an abundant EZ55
cytoplasmic protein in the exudate is exactly the protein most likely to also
co-purify into an MV fraction. Two non-exclusive readings, not resolved here:
1. Abundance-driven detection — highly expressed cytoplasmic proteins appear in
   both the exudate and MV fractions via lysis / co-purification (contamination).
2. Genuine cytoplasmic cargo — ribosomal proteins, EF-Tu, chaperones are reported
   as real MV/exudate cargo in the literature.
The genuinely extruded envelope proteins (TonB receptors, OmpA, Pal, OM β-barrel)
are present but tend to be **route-specific (vesicle)** and strain-diverse.

## Secreted-protein profile (researcher follow-on at decide) `[KG]`

Script `scripts/02_secreted_profile.py`. Secreted = EZ55 only, so "agreement
between strains" is reinterpreted as **cross-route corroboration** (researcher
choice): is an EZ55-secreted OG also in another strain's vesicle cargo?

**Category distribution of the 69 secreted proteins:** Translation 27 (39%),
Inorganic ion transport 7 (10%), Unknown 7 (10%), Coenzyme 5 (7%), Energy 5 (7%),
then Nucleotide / Amino-acid / Cell-wall&membrane 4 each, and 5 smaller categories.

**Cross-route corroboration:** 25 of 69 (36%) EZ55-secreted OGs also appear in
another strain's vesicle cargo; 44 secreted-only. (These 25 are exactly the
`both_routes` OGs — internal consistency check.) Corroboration concentrates in
Translation (11/27 = 41%) and Energy production (4/5 = 80%).

`[interpretation]` The secreted proteome is dominated by abundant cytoplasmic
translation machinery, and the cross-route-corroborated subset is also
predominantly translation/energy — consistent with abundance-driven co-detection
rather than selective dual export. Envelope/transport categories are a minority of
the secreted set and only modestly corroborated. Note: this follow-on was
researcher-requested after the critic pass; claims are simple distributions read
directly from script output and tagged above.

## Vesicle-protein profile (researcher follow-on at decide) `[KG]`

Script `scripts/03_vesicle_profile.py`. Vesicle is measured on 6 strains, so
"agreement between strains" is **direct** here (no reinterpretation needed).

**Category distribution of 249 vesicle genes** (secreted % in parens): Translation
75 / 30% (39%), Energy production 46 / 18% (7%), Cell wall and membrane 37 / 15%
(6%), Inorganic ion transport 18 / 7% (10%), Unknown 18 / 7%, then smaller. Vesicle
carries 2.5× more envelope protein than the secreted exudate.

**Agreement between strains (101 vesicle OGs):** 63 of 101 (62%) shared by ≥2 of 6
strains; 38 strain-unique; 6 OGs in all 6 strains; 29 in ≥4. Pairwise Jaccard on OG
sets mean 0.31 (0.12–0.61); ATCC27126/BGP6/MIT1002 agree most (0.50–0.61);
HOT1A3 and AD45 are outliers.

**All-6-strain conserved core (6 OGs):** TolC outer-membrane efflux channel, OmpA
family protein, MotA/TolQ/ExbB proton channel, PhoX alkaline phosphatase,
glutamate–ammonia ligase, DUF3450.

`[caveat]` Cross-strain agreement is confounded by uneven `top_n` cargo-list depth
(15–58 genes/strain, step-2 caveat): a small list cannot overlap much, so the
agreement figures (incl. HOT1A3/AD45 being outliers) are a **lower bound**.

`[interpretation]` The vesicle route's all-6 conserved core is genuine
outer-membrane / secretion machinery (TolC, OmpA, MotA/TolQ/ExbB, PhoX) — a
reproducible, biologically coherent extruded signature, distinct from the
abundance-driven translation signal that dominates the secreted set and the
cross-route core. This is the most defensible "extruded" signal in the analysis.

## Exoenzymes for organic-compound breakdown (researcher follow-on) `[KG]`

Script `scripts/04_exoenzymes.py`. Question: which extruded proteins are likely
exoenzymes that break down organic compounds, across both routes? Annotation-driven
(EC + CAZy + GO-MF + **Pfam**; `gene_ontology_terms` only, no gene_details — these
two ontologies also carry localization + signal peptide). Pfam is required, not
optional: PhoX carries Pfam PF05787 but no EC/GO term, so an EC-only filter missed
it (first pass found only 3; with Pfam, the real set surfaces).

Export evidence is a **confidence tier, not a gate** — the protein is already
measured leaving the cell, so cytoplasmic localization (not absence of signal) is
what flags contamination.

**Funnel:** 318 extruded → 26 degradative-enzyme annotation → 9 non-cytoplasmic
candidates (4 OGs); 17 degradative-but-cytoplasmic (tier C, likely contaminant).

**Candidates (tier A: degradative + export evidence):**

| Enzyme | Substrate | Route | Strains | Evidence |
|---|---|---|---|---|
| Alkaline phosphatase PhoX | organic phosphorus | vesicle | all 6 | Pfam PF05787 + lipoprotein signal |
| DegQ serine endoprotease | protein/peptide | secreted | EZ55 | EC 3.4.21.107 + periplasmic + signal |
| M1 family aminopeptidase | protein/peptide | secreted | EZ55 | GO-MF metallopeptidase + signal |
| TonB-receptor (flagged) | protein/peptide? | vesicle | BGP6 | GO-MF carboxypeptidase — conflicts with transporter product; likely annotation artifact |

Two false positives removed during QC: a TonB receptor matched on Pfam
"Carboxypeptidase regulatory-like domain" (structural, not catalytic) and an FKBP
peptidyl-prolyl isomerase (protein folding, not degradation) — both excluded.

`[interpretation]` The two routes carry different degradative jobs: vesicle → organic
**phosphorus scavenging** (PhoX, conserved across all 6 strains — fits the copiotroph
lifestyle); secreted → **proteolysis** (DegQ, M1 aminopeptidase in the EZ55 exudate).

`[KG gap]` Two honest negatives:
1. No carbohydrate-active enzymes (CAZy GH/PL/CE) surfaced in the extruded set,
   despite Alteromonas being a known polysaccharide degrader (annotation / `top_n`
   depth / fraction choice — undetermined).
2. Coverage-bound: degradative identity often lives only in Pfam; a phytase
   (MIT1002_00601) visible by product name did not classify. The list is a
   conservative lower bound.

Outputs: `data/exoenzyme_candidates.csv`, `data/exoenzyme_by_substrate.csv`,
`figures/exoenzymes.png`. Classifier refactored to `scripts/exoenzyme_lib.py`
(shared with the genome run below; 04 re-run after refactor reproduces 9 candidates).

## Genome-wide background — is the extruded set enriched for exoenzymes? `[KG]`

Script `scripts/05_exoenzyme_genome_background.py`. Same classifier
(`exoenzyme_lib.classify`, byte-identical) run on ALL genes of the 7 strains
(locus tags via `run_cypher`).

| | Genes | Exoenzyme candidates | tier A (exported) | rate |
|---|---|---|---|---|
| Extruded set | 318 | 9 | 9 | 2.8% |
| Full genomes (7 strains) | 27,759 | 1,918 | 1,092 | 6.9% |

Per strain: ~245–290 candidates (6.5–7.5%), uniform. Genome-wide substrate pool
(candidates): protein/peptide 885, organic-P 335, carbohydrate 264, nucleic acid
213, lipid 181, amide 146.

`[interpretation]` Three reads:
1. The extruded measurement captures a tiny slice — 9 of ~1,918 genomic candidates.
2. The extruded set is **not enriched** for exoenzymes (2.8% vs 6.9%; tier-A-only
   2.8% vs 3.9%) — consistent with extruded fractions being dominated by abundant
   cytoplasmic proteins, not selectively loaded with hydrolases. (Caveat: the
   genome candidate count includes ~826 tier-B genes lacking localization
   annotation; the tier-A comparison is the fair one and still shows no enrichment.)
3. The "no CAZymes extruded" negative is a **capture gap, not genome absence** — the
   genomes carry 264 carbohydrate-active candidates (181 tier A), none sampled.

Outputs: `data/exoenzyme_genome_background.csv`, `data/exoenzyme_genome_candidates.csv`.

### EC-missing verification (QC) `[KG]`

Double-checked the "function lives only in Pfam" claim, per-organism (first attempt
errored on a multi-organism `organism="Alteromonas macleodii"` string — corrected):
`gene_ontology_terms(ontology="ec")` returns **no EC** for PhoX (`MIT1002_02422`,
`ALTBGP6_02414`; `no_terms`, total_matching 0) but EC 3.4.21.107 for DegQ
(`EZ55_00820`). Confirmed against `gene_details.annotation_types` (PhoX lacks `ec`;
DegQ has it). So the Pfam layer is necessary, not a workaround. Gotcha logged in
`gaps_and_friction.md`: `gene_ontology_terms` is single-organism — pass a unique
organism or a whole strain's annotations silently drop. The genome script is
unaffected (it passes specific strain codes).

## Exoenzyme repertoire at OG level — genome vs extruded `[KG]`

Script `scripts/06_exoenzyme_og_level.py`. Maps the 1,918 genome-wide candidate
genes to Alteromonadaceae eggnog OGs (reusing the step-4 `map_genes_to_og`), and
compares against the extruded candidates at OG level.

- Genome-wide exoenzyme OGs: **387** (tier A: 200). 1,918 genes → 387 OGs, 0 unmapped.
- Extruded exoenzyme OGs: **4** (PhoX, DegQ, M1 aminopeptidase, TonB‡).
- Genome OGs captured in the extruded set: **4 of 387 (1%)**.

The extruded count is **9 genes → 4 OGs**: PhoX is one OG carried by 6 strains
(6 genes → 1 OG), plus DegQ, M1 aminopeptidase, and the flagged TonB receptor
(1 gene each). OG-level dedup of the 6 PhoX orthologs is what makes the
genome-vs-extruded comparison fair (the genome side is deduplicated to OGs too).

Annotation-source contribution to the 387 genome OGs (non-exclusive): EC 208,
Pfam 145, GO-MF 106, CAZy 11 — Pfam adds 145 OGs beyond EC (incl. PhoX), confirming
the Pfam layer was load-bearing. Export evidence: 200 tier A (124 signal-only,
54 signal+localization, 22 localization-only), 187 tier B (no export annotation).

By substrate (genome OGs / tier A / captured): protein/peptide 151 / 103 / 3;
nucleic acid 55 / 6 / 0; carbohydrate 52 / 36 / 0; organic phosphate 40 / 12 / 1;
lipid/ester 33 / 18 / 0; amide/C-N 30 / 19 / 0; ester-other 20 / 5 / 0; sulfate 5 / 0 / 0.

Conservation: of 387 genome exoenzyme OGs, **180 present in all 7 strains** (221 in ≥6).

`[interpretation]` The genomes encode a broad, conserved exoenzyme arsenal (~387 OGs,
~180 universal) across every substrate class; the extruded measurement captured ~1%
(proteases via the secreted route, PhoX via vesicles). The carbohydrate gap is exact:
52 genomic CAZyme OGs (36 tier A), zero captured → a sampling/measurement gap, not a
genomic absence.

‡ TonB-receptor with conflicting carboxypeptidase GO term — flagged annotation artifact.

Figures: `figures/exoenzyme_og_level.png` (6 panels: by-substrate genome vs extruded;
OG-level capture funnel; conservation histogram; degradative-annotation source;
export-evidence type; tier A/B). Outputs: `data/exoenzyme_og_genome.csv`,
`data/exoenzyme_og_comparison.csv`.

## Outputs

- `data/extruded_genes_all.csv` — 318 gene rows (locus_tag, strain, route, value, OG)
- `data/extruded_og_catalogue.csv` — 145 OGs (routes, both_routes, n_strains, locus_tags)
- `data/secreted_category_distribution.csv` — 69 secreted proteins by gene category
- `data/secreted_og_corroboration.csv` — EZ55-secreted OGs, corroborated flag, strains
- `data/vesicle_category_distribution.csv` — 249 vesicle genes by gene category
- `data/vesicle_og_strain_recurrence.csv` — 101 vesicle OGs, strain recurrence, product
- `data/exoenzyme_candidates.csv`, `data/exoenzyme_by_substrate.csv` — extruded exoenzymes
- `data/exoenzyme_genome_background.csv`, `data/exoenzyme_genome_candidates.csv` — genome-wide
- `data/exoenzyme_og_genome.csv`, `data/exoenzyme_og_comparison.csv` — OG-level
- `scripts/exoenzyme_lib.py` — shared exoenzyme classifier (used by 04 + 05)
- `figures/og_recurrence.png`, `secreted_profile.png`, `vesicle_profile.png`,
  `exoenzymes.png`, `exoenzyme_og_level.png`

## Decide

- [x] Pipeline run across all 7 routes; secreted guard validated
- [x] 0 unmapped genes; 145-OG catalogue frozen
- [x] Positive control (TonB) passes; recurrence nuance recorded
- [x] Both-routes composition described (numbers) before interpretation
- [x] Critical-review critic run on the core catalogue (data-integrity +
      interpretation): no Blockers, 2 Concerns + 2 Notes, all fixed → `critical_review.md`
- [x] Researcher-driven follow-ons added: secreted profile, vesicle agreement,
      exoenzyme analysis (extruded + genome + OG-level). Described-first, tagged;
      QC + friction logged. **Critic has NOT re-run over these expansions** — flagged
      for a re-review pass before step 6 (researcher choice).
- [x] Researcher approved → commit
