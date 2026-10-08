# Pilot answer key: MED4 transport systems (independent verifier)

Built only from multiomics-kg MCP calls (KG 0.1.0-alpha.7, explorer 0.1.0-alpha.5, `kg_release_info` verdict ok, 17/17 asserts).
Organism for every call: `organism="MED4"` (Prochlorococcus MED4, contig NC_005072.1). No expression tools were called.
Nothing under `methods/scripts/`, `methods/tests/` or `methods/*.py` was opened.

Companion files (same folder):
- `pilot_genes.csv` — 27 rows, one per case gene.
- `pilot_substrates.csv` — 97 rows (case × gene × substrate × TCDB family).
- `_coords_from_gene_neighbors.tsv` — 186 gene coordinates transcribed from `gene_neighbors` anchor blocks.
- `build_answer_key.py` (adjacent gaps, same-strand runs, window membership), `write_csvs.py` (writes the CSVs). Run from this folder with the repo venv.

## Conventions used

- **Adjacent gap** = `next.start − prev.end − 1`, computed from anchor coordinates. Negative = overlap. This formula reproduces the tool's `bp_gap` for *adjacent* pairs (e.g. PMM0370→PMM0371: 354691−354660−1 = 30 = tool bp_gap). The tool reports 0 where genes overlap; I report the negative value.
- `gene_neighbors.bp_gap` is distance to the **anchor** (it spans any genes in between) and is never used as an adjacent gap here.
- **Neighbourhood** = union of ±8 genes (start order) around every case gene.
- **Same-strand run** = maximal stretch of adjacent genes on one strand. Run ids restart in each table.
- **N-substrate counts** come from `metabolites_by_gene(evidence_sources=['transport'], metabolite_elements=['N'])`. "distinct" = metabolites, "rows" = gene×family×metabolite rows. Every list was checked against `total_matching`. Nothing listed was truncated unless stated.
- **can_use**: genes that take part in a KEGG reaction involving the substrate, from `genes_by_metabolite(evidence_sources=['metabolism'], organism MED4)`. The CSV has three columns:
  - `can_use_expected` — my call.
  - `can_use_if_window8_rule` — mechanical: is any such gene inside the ±8 neighbourhood?
  - `can_use_if_same_strand_run_rule` — mechanical: is any such gene in the same same-strand run as the case's transporter genes?

  The two mechanical rules disagree on two cases (urea, ammonia). Use them to tell which rule a method implements.

Pfam evidence rungs: every Pfam call is `curated` except PMM0370 PF09084 (`family_inferred`), PMM0192 PF08352 (`family_inferred`) and PMM0373 PF21291 (`signature`).

---

## Case 1 — cyn (PMM0370–PMM0373)

| locus_tag | gene | product | strand | start | end | Pfam (rung) | role call (justifying domain) |
|---|---|---|---|---|---|---|---|
| PMM0370 | cynA | cyanate ABC transporter, substrate-binding protein | + | 352975 | 354660 | PF13379 NMT1-like (curated); PF09084 NMT1/THI5 like (family_inferred) | substrate-binding (NMT1-like periplasmic binding fold) |
| PMM0371 | cynB | cyanate ABC transporter, permease protein | + | 354691 | 355473 | PF00528 BPD inner membrane component (curated) | permease (PF00528) |
| PMM0372 | cynD | cyanate ABC transporter ATP-binding protein | + | 355490 | 356344 | PF00005 ABC transporter (curated) | ATPase (PF00005) |
| PMM0373 | cynS | cyanate hydratase | + | 356377 | 356820 | PF02560 cyanate lyase C-term (curated); PF21291 cyanate hydratase N-term (signature) | enzyme (PF02560) |

**TCDB leaf attachments (most_specific; verbose):**

| locus | term_id | name | lvl | evidence | sources | score | tier | src_agreement | pfam_support |
|---|---|---|---|---|---|---|---|---|---|
| PMM0370 | tcdb:3.A.1.16.1 | Four component nitrate/nitrite porter | 4 | family_inferred | eggnog | 0.6 | null | both_sources | uncorroborated |
| PMM0370 | tcdb:3.A.1.16.2 | Bispecific cyanate/nitrite transporter | 4 | family_inferred | eggnog | 0.6 | null | both_sources | uncorroborated |
| PMM0370 | tcdb:3.A.1.17.3 | Putative hydroxymethylpyrimidine transport system, ThiXYZ | 4 | family_inferred | eggnog | 0.4 | null | single_source | uncorroborated |
| PMM0370 | tcdb:3.A.1.17.6 | (same name) | 4 | family_inferred | eggnog | 0.4 | null | single_source | uncorroborated |
| PMM0371 | tcdb:3.A.1.16.1 | Four component nitrate/nitrite porter | 4 | family_inferred | eggnog | 0.8 | null | both_sources | corroborated |
| PMM0371 | tcdb:3.A.1.16.2 | Bispecific cyanate/nitrite transporter | 4 | family_inferred | eggnog | 0.8 | null | both_sources | corroborated |
| PMM0372 | tcdb:3.A.1.16.1 | Four component nitrate/nitrite porter | 4 | family_inferred | eggnog | 0.8 | null | both_sources | corroborated |
| PMM0373 | — | no TCDB terms (`no_terms`) | | | | | | | |

The same call with `include_superseded=True` adds these superseded rows:
- PMM0370: tcdb:3.A.1.16 NitT family, level 3, homology, tcdb_diamond, score 0.6, tier 2, 69.9% identity / 78.6% query coverage.
- PMM0371: tcdb:3.A.1, homology, score 0.4, tier 3.
- PMM0372: tcdb:3.A.1, homology, score 0.6, tier 3.

**Substrate block (metabolites_by_gene):** every gene `resolved`. `tcdb_evidence_score_max`: PMM0370 0.6, PMM0371 0.8, PMM0372 0.8. PMM0373 is in `not_matched` (no TCDB call).

| locus | N substrates, most_specific (distinct / rows) | inherited | most_specific N substrates |
|---|---|---|---|
| PMM0370 | 4 / 6 | 0 | nitrate chebi:14654 (16.1); Nitrite kegg.compound:C00088 (16.1, 16.2); Cyanate kegg.compound:C01417 (16.2); Pyrimidine kegg.compound:C00396 (17.3, 17.6; score 0.4) |
| PMM0371 | 3 / 4 | 0 | nitrate (16.1); Nitrite (16.1, 16.2); Cyanate (16.2) |
| PMM0372 | 2 / 2 | 0 | nitrate (16.1); Nitrite (16.1). **No cyanate**, because cynD is attached to 3.A.1.16.1 only |

**Neighbourhood** (window 8; 20 genes; one locus):

| locus_tag | gene | strand | start | end | gap to previous (bp) | case | run |
|---|---|---|---|---|---|---|---|
| PMM0368 | - | - | 349383 | 349691 |  |  | 1 |
| PMM2034 | - | - | 350136 | 350273 | 444 |  | 1 |
| PMM1830 | - | - | 350589 | 350732 | 315 |  | 1 |
| PMM1831 | - | - | 350803 | 350988 | 70 |  | 1 |
| PMM1832 | - | - | 351016 | 351153 | 27 |  | 1 |
| PMM1833 | - | - | 351526 | 351660 | 372 |  | 1 |
| PMM1834 | - | - | 351856 | 352020 | 195 |  | 1 |
| PMM0369 | - | + | 352201 | 352527 | 180 |  | 2 |
| PMM0370 | cynA | + | 352975 | 354660 | 447 | YES | 2 |
| PMM0371 | cynB | + | 354691 | 355473 | 30 | YES | 2 |
| PMM0372 | cynD | + | 355490 | 356344 | 16 | YES | 2 |
| PMM0373 | cynS | + | 356377 | 356820 | 32 | YES | 2 |
| PMM0374 | tatA | - | 356905 | 357096 | 84 |  | 3 |
| PMM0375 | - | + | 357196 | 357519 | 99 |  | 4 |
| PMM0376 | lptC | - | 357535 | 357903 | 15 |  | 5 |
| PMM0377 | - | - | 357904 | 358167 | 0 |  | 5 |
| PMM0378 | - | - | 358218 | 358490 | 50 |  | 5 |
| PMM1835 | - | - | 358796 | 358942 | 305 |  | 5 |
| PMM1837 | - | - | 359300 | 359485 | 357 |  | 5 |
| PMM1838 | - | - | 359485 | 359610 | -1 |  | 5 |

The same-strand run containing the case is PMM0369–PMM0373 (+). PMM0369 is a "conserved hypothetical protein" (category Translation) with no TCDB terms, 447 bp upstream of cynA.

**Metabolism genes for the case's most_specific N substrates:**
- cyanate C01417: PMM0373 cynS only (R03546, R10079, EC 4.2.1.104). It is in the neighbourhood, in the same run, 32 bp after cynD.
- nitrite C00088: no MED4 gene (`not_matched`).
- nitrate chebi:14654: no MED4 gene (`not_matched`). The KEGG node C00244 also has 0 metabolism rows in MED4.
- pyrimidine C00396: no MED4 gene.
- Not a substrate of this case, but present in the neighbourhood: PMM0373 also reacts with ammonia C00014 (R10079).

**Expected outcomes**
- One system: PMM0370 + PMM0371 + PMM0372 (binding protein, permease, ATPase), plus the linked enzyme PMM0373 cynS. All four sit on + in one run, with adjacent gaps 30, 16 and 32 bp. No subunit is missing.
- PMM0373 is the **linked enzyme** (cyanate hydratase), not a transporter subunit. It has no TCDB call.
- PMM0369 (upstream, same strand, 447 bp) is **context**. The PMM18xx/PMM2034 hypotheticals (− strand) and tatA/lptC are context.
- can_use:
  - cyanate = **co-located** (PMM0373)
  - nitrite = **no**
  - nitrate = **no**
  - pyrimidine = **no**. The 0.4-score ThiXYZ hits on cynA are single-source and Pfam-uncorroborated; this is the low-confidence part of the case.
- [interpretation] The TCDB family puts nitrate and nitrite next to cyanate. Only cyanate has a metabolising gene, and it is adjacent.

---

## Case 2 — urt + urease (PMM0963–PMM0974)

Gene-name mapping confirmed from the KG (gene_name and product fields on `gene_neighbors` neighbour rows and anchor blocks):

| locus_tag | gene | product | strand | start | end | Pfam (all curated) | role call |
|---|---|---|---|---|---|---|---|
| PMM0963 | ureC | urease alpha subunit | − | 921384 | 923093 | PF00449 urease α N-term; PF01979 amidohydrolase | enzyme |
| PMM0964 | ureB | urease beta subunit | − | 923099 | 923419 | PF00699 | enzyme |
| PMM0965 | ureA | urease gamma subunit | − | 923422 | 923724 | PF00547 | enzyme |
| PMM0966 | ureD | urease accessory protein UreD | − | 923785 | 924678 | PF01774 | other (accessory) |
| PMM0967 | ureE | urease accessory protein UreE | + | 924726 | 925190 | PF02814; PF05194 | other (accessory) |
| PMM0968 | ureF | urease accessory protein UreF | + | 925168 | 925854 | PF01730 | other (accessory) |
| PMM0969 | ureG | urease accessory protein UreG | + | 925858 | 926463 | PF02492 CobW/HypB/UreG | other (accessory) |
| PMM0970 | urtA | ABC-type urea transporter, substrate binding component | + | 926598 | 927887 | PF13433 periplasmic binding protein | substrate-binding |
| PMM0971 | urtB | ABC-type urea transporter, permease component | + | 927969 | 929123 | PF02653 BCAA permease | permease |
| PMM0972 | urtC | ABC-type urea transporter, membrane component | + | 929123 | 930259 | PF02653 | permease |
| PMM0973 | urtD | ABC-type urea transporter, ATP-binding component UrtD | + | 930252 | 931007 | PF00005; PF12399 | ATPase |
| PMM0974 | urtE | ABC-type urea transporter, ATPase component UrtE | + | 931010 | 931720 | PF00005 | ATPase |

The mapping matches the brief: ureC=0963, ureB=0964, ureA=0965, ureD=0966, ureE=0967, ureF=0968, ureG=0969.

**TCDB (most_specific):**
- PMM0963–PMM0969: no TCDB terms.
- PMM0970–PMM0974 are each attached to **tcdb:3.A.1.4.4** "The high-affinity (" (name truncated in the KG) and **tcdb:3.A.1.4.5** "The high affinity urea/thiourea/hydroxyurea porter". Both are level 4, family_inferred, eggnog, tier null, both_sources.
  - Scores: PMM0970 0.6 (pfam_support uncorroborated). PMM0971–0974 0.8 (pfam_support corroborated).
- PMM0974 also has **tcdb:1.B.42** LPS export porin, level 2, homology, tcdb_diamond, **score 0**, tier 3, single_source, Pfam/GO uncorroborated, 34.6% identity, qcov 94.5. This is a spurious extra hit.

With `include_superseded=True`:
- PMM0970: tcdb:3.A.1.4 HAAT, homology, 0.6, tier 2.
- PMM0971–0974: tcdb:3.A.1, homology, 0.6, tier 3.

**Substrate block:** PMM0970–0974 are all `resolved`, score_max 0.6 (urtA) or 0.8. Each has 3 distinct most_specific N substrates in 4 rows and 0 inherited:
- Urea kegg.compound:C00086 (via 4.4 and 4.5)
- Hydroxyurea kegg.compound:C07044 (4.5)
- Thiourea kegg.compound:C14415 (4.5)

PMM0963–0969 are `not_matched` on the transport arm.

**Neighbourhood** (28 genes; one locus):

| locus_tag | gene | strand | start | end | gap (bp) | case | run |
|---|---|---|---|---|---|---|---|
| PMM0956 | uppP | - | 914736 | 915536 |  |  | 1 |
| PMM0957 | - | + | 915626 | 915904 | 89 |  | 2 |
| PMM1918 | - | - | 916071 | 916196 | 166 |  | 3 |
| PMM0958 | - | - | 916287 | 916514 | 90 |  | 3 |
| PMM0959 | - | - | 916593 | 917549 | 78 |  | 3 |
| PMM0960 | gpgP | - | 917546 | 918349 | -4 |  | 3 |
| PMM0961 | gmgG | - | 918353 | 920110 | 3 |  | 3 |
| PMM0962 | gpgS | + | 920161 | 921387 | 50 |  | 4 |
| PMM0963 | ureC | - | 921384 | 923093 | -4 | YES | 5 |
| PMM0964 | ureB | - | 923099 | 923419 | 5 | YES | 5 |
| PMM0965 | ureA | - | 923422 | 923724 | 2 | YES | 5 |
| PMM0966 | ureD | - | 923785 | 924678 | 60 | YES | 5 |
| PMM0967 | ureE | + | 924726 | 925190 | 47 | YES | 6 |
| PMM0968 | ureF | + | 925168 | 925854 | -23 | YES | 6 |
| PMM0969 | ureG | + | 925858 | 926463 | 3 | YES | 6 |
| PMM0970 | urtA | + | 926598 | 927887 | 134 | YES | 6 |
| PMM0971 | urtB | + | 927969 | 929123 | 81 | YES | 6 |
| PMM0972 | urtC | + | 929123 | 930259 | -1 | YES | 6 |
| PMM0973 | urtD | + | 930252 | 931007 | -8 | YES | 6 |
| PMM0974 | urtE | + | 931010 | 931720 | 2 | YES | 6 |
| PMM1919 | - | - | 931750 | 931929 | 29 |  | 7 |
| PMM1921 | - | - | 932184 | 932354 | 254 |  | 7 |
| PMM1922 | - | + | 932754 | 932927 | 399 |  | 8 |
| PMM0975 | - | + | 932990 | 933385 | 62 |  | 8 |
| PMM0976 | evrA | + | 933470 | 934459 | 84 |  | 8 |
| PMM0977 | evrB | + | 934460 | 935251 | 0 |  | 8 |
| PMM0978 | evrC | + | 935248 | 936042 | -4 |  | 8 |
| PMM0979 | - | - | 936046 | 936336 | 3 |  | 9 |

The cluster sits on **two strands**:
- ureC-B-A-D (−, run 5) and ureE-F-G + urtA-E (+, run 6).
- ureD and ureE are divergent, 47 bp apart.
- After urtE, the run breaks at PMM1919 and PMM1921 (− strand hypotheticals).

PMM0976–0978 evrABC (viologen exporter) are a separate ABC set:
- PMM0976: tcdb:3.A.1 + 2.A.130.
- PMM0977: tcdb:3.A.1 only.
- PMM0978: tcdb:3.A.1.141.

**Metabolism genes:**
- Urea C00086: PMM0963, PMM0964, PMM0965 (R00131, EC 3.5.1.5), all inside the neighbourhood. PMM1686 speB (R01157 agmatinase) is elsewhere.
- Hydroxyurea C07044 and thiourea C14415: no MED4 gene.
- Ammonia: ureCBA also react with ammonia (R00131).

**Expected outcomes**
- One transport system: urtA-B-C-D-E (PMM0970–0974). Contiguous on +, gaps 81, −1, −8 and 2 bp; 134 bp from ureG. Complete: binding protein, 2 permeases, 2 ATPases. Nothing missing.
- **Linked enzyme:** urease PMM0963/0964/0965 (catalytic α/β/γ) with accessory proteins PMM0966–0969. These are not transporter subunits.
- **Context:** evrABC (separate ABC exporter on the same strand, past an opposite-strand break) and the gpg/gmg genes.
- can_use:
  - urea = **co-located**, via PMM0963–0965 within ±8 and about 3.5 kb from urtA. A same-strand-run rule would wrongly say "elsewhere", because ureCBA are on − and the urt genes on +.
  - hydroxyurea = **no**
  - thiourea = **no**
- PMM0974's 1.B.42 score-0 hit should not change the call. It contributes no N substrates (the N query returned only 3.A.1.4.x rows).

---

## Case 3 — amt1 (PMM0263)

| locus_tag | gene | product | strand | start | end | Pfam | role |
|---|---|---|---|---|---|---|---|
| PMM0263 | amt1 | ammonium transporter | + | 252632 | 254092 | PF00909 Ammonium Transporter Family (curated) | single carrier (PF00909) |

**TCDB:**
- most_specific = **tcdb:1.A.11** Amt family. Level 2, homology, sources eggnog + tcdb_diamond, score 0.8, tier 3, both_sources, pfam_support corroborated, identity 80.7, qcov 99.8, consensus_n 25.
- `include_superseded=True` adds nothing.
- Resolution `resolved`; score_max 0.8.

**N substrates:** 4 most_specific (4 rows), 0 inherited, all via 1.A.11:
- Ammonia kegg.compound:C00014
- Methylamine C00218
- Ethylamine C00797
- Tetramethylammonium C20292

**Neighbourhood** (17 genes):

| locus_tag | gene | strand | start | end | gap | case | run |
|---|---|---|---|---|---|---|---|
| PMM0255 | leuD | - | 244685 | 245305 |  |  | 1 |
| PMM0256 | leuC | - | 245302 | 246711 | -4 |  | 1 |
| PMM0257 | pncC | - | 246725 | 248026 | 13 |  | 1 |
| PMM0258 | glyA | - | 247995 | 249266 | -32 |  | 1 |
| PMM0259 | - | + | 249507 | 249758 | 240 |  | 2 |
| PMM0260 | - | + | 249768 | 250049 | 9 |  | 2 |
| PMM0261 | murJ | - | 250057 | 251637 | 7 |  | 3 |
| PMM0262 | sfsA | + | 251711 | 252457 | 73 |  | 4 |
| PMM0263 | amt1 | + | 252632 | 254092 | 174 | YES | 4 |
| PMM0264 | lytB | + | 254182 | 255378 | 89 |  | 4 |
| PMM0265 | - | + | 255473 | 256033 | 94 |  | 4 |
| PMM0266 | purH | - | 256035 | 257588 | 1 |  | 5 |
| PMM0267 | - | + | 257622 | 258239 | 33 |  | 6 |
| PMM0268 | - | - | 258236 | 258604 | -4 |  | 7 |
| PMM0269 | - | + | 258843 | 259979 | 238 |  | 8 |
| PMM0270 | cobS | - | 259957 | 260697 | -23 |  | 9 |
| PMM0271 | tgt | + | 260796 | 261914 | 98 |  | 10 |

amt1 sits in a + run with sfsA, lytB and PMM0265. None of these has a TCDB term (checked for PMM0262 and PMM0264) or an N-transport role.

**Metabolism genes:**
- Ammonia C00014: 36 MED4 genes (`genes_by_metabolite` gene_count 36, 58 rows, 42 reactions). Examples: glnA PMM0920, carA/carB, the gcv genes, ureCBA, cynS.
- Only **PMM0257 pncC** (nicotinamide-nucleotide amidase, R02322) falls inside amt1's ±8 window: offset −6, opposite strand, about 4.6 kb from amt1.
- Methylamine, ethylamine and tetramethylammonium: no MED4 gene.

**Expected outcomes**
- One system = amt1 alone (single carrier). No missing subunits. The neighbours are context.
- can_use:
  - ammonia = **elsewhere in genome** (my call). Ammonia has 36 reaction genes genome-wide, and pncC's position in the window is coincidental: opposite strand, unrelated reaction. **Ambiguous by rule:** a pure ±8 window rule returns "co-located" via PMM0257. A method that does so is applying the rule correctly, but the result is a false link.
  - methylamine = **no**
  - ethylamine = **no**
  - tetramethylammonium = **no**

---

## Case 4 — dpp (split across three loci)

| locus_tag | gene | product | strand | start | end | Pfam (rung) | role |
|---|---|---|---|---|---|---|---|
| PMM1049 | dppA | peptide/nickel transport system substrate-binding protein | − | 991688 | 993259 | PF00496 SBP family 5 middle (curated) | substrate-binding |
| PMM1048 | dppB | oligopeptide ABC transporter, membrane component | − | 990673 | 991695 | PF00528 (curated); PF19300 BPD membrane N-term (curated) | permease |
| PMM0421 | dppC | ABC-type oligopeptide transporter, membrane component | + | 400160 | 400903 | PF00528 (curated) | permease |
| PMM0192 | ddpD | peptide/nickel ABC transport system, ATP-binding component | + | 185245 | 186840 | PF00005 (curated); PF08352 oligopeptide/dipeptide transporter C-term (family_inferred) | ATPase |

**TCDB:**
- All four have most_specific = **tcdb:3.A.1.5** PepT family. Level 3, family_inferred, eggnog, score 0.8, tier null, both_sources, pfam_support corroborated.
- Superseded rows: tcdb:3.A.1, homology, tcdb_diamond, tier 3. Scores: PMM0192 0.6; PMM0421, PMM1048 and PMM1049 0.4.
- All `resolved`, score_max 0.8.

**N substrates:** identical for all four genes. Each has 11 rows: 7 most_specific + 4 inherited (11 distinct). Every row reports family tcdb:3.A.1.5.
- most_specific:
  - L-alanyl-L-alanine chebi:195181
  - tripeptide chebi:27138
  - Heme kegg.compound:C00032
  - EDTA C00284
  - Bradykinin C00306
  - 5-Aminolevulinate C00430
  - Stachydrine C10172
- inherited:
  - peptide chebi:14753
  - microcin c chebi:82754
  - Glutathione C00051
  - Oligopeptide C00098

  (from `top_metabolites` of the 4-gene query, total_matching 44, by_substrate_depth 28 most_specific / 16 inherited)

**Neighbourhoods** (three separate loci, 17 + 17 + 18 genes):

ddpD locus:

| locus_tag | gene | strand | start | end | gap | case | run |
|---|---|---|---|---|---|---|---|
| PMM0184 | pabC | + | 175726 | 176322 |  |  | 1 |
| PMM0185 | - | + | 176344 | 177072 | 21 |  | 1 |
| PMM0186 | hisC | - | 177069 | 178178 | -4 |  | 2 |
| PMM0187 | argS | - | 178178 | 179989 | -1 |  | 2 |
| PMM0188 | nadC | - | 180017 | 180883 | 27 |  | 2 |
| PMM0189 | trmE | - | 180959 | 182341 | 75 |  | 2 |
| PMM0190 | - | + | 182408 | 182860 | 66 |  | 3 |
| PMM0191 | spoT | - | 182880 | 185189 | 19 |  | 4 |
| PMM0192 | ddpD | + | 185245 | 186840 | 55 | YES | 5 |
| PMM0193 | rluD | - | 186826 | 187794 | -15 |  | 6 |
| PMM0194 | rbgA | - | 187791 | 188657 | -4 |  | 6 |
| PMM0195 | pgk | + | 188883 | 190091 | 225 |  | 7 |
| PMM0196 | - | - | 190093 | 190824 | 1 |  | 8 |
| PMM0197 | murG | + | 190852 | 191946 | 27 |  | 9 |
| PMM0198 | hisC/cobC | - | 191925 | 193049 | -22 |  | 10 |
| PMM0199 | pyrD | - | 193065 | 194234 | 15 |  | 10 |
| PMM0200 | rnhA | - | 194249 | 194971 | 14 |  | 10 |

dppC locus:

| locus_tag | gene | strand | start | end | gap | case | run |
|---|---|---|---|---|---|---|---|
| PMM0414 | - | + | 392828 | 393532 |  |  | 1 |
| PMM0415 | c-des | - | 393515 | 394696 | -18 |  | 2 |
| PMM0416 | - | - | 394729 | 395523 | 32 |  | 2 |
| PMM1846 | - | - | 395600 | 395773 | 76 |  | 2 |
| PMM0417 | - | + | 396030 | 396290 | 256 |  | 3 |
| PMM0418 | nifU | - | 396312 | 396557 | 21 |  | 4 |
| PMM0419 | mqoA | + | 396629 | 398122 | 71 |  | 5 |
| PMM0420 | lepA | + | 398179 | 399987 | 56 |  | 5 |
| PMM0421 | dppC | + | 400160 | 400903 | 172 | YES | 5 |
| PMM0422 | trmH | - | 400923 | 401594 | 19 |  | 6 |
| PMM1847 | - | + | 401765 | 401968 | 170 |  | 7 |
| PMM0423 | - | + | 402171 | 402563 | 202 |  | 7 |
| PMM0424 | - | + | 402566 | 402802 | 2 |  | 7 |
| TX50_RS09255 | - | + | 402806 | 402937 | 3 |  | 7 |
| PMM0425 | - | + | 402934 | 404424 | -4 |  | 7 |
| PMM0426 | sun | + | 404925 | 406238 | 500 |  | 7 |
| PMM0427 | pbp1 | - | 406258 | 408021 | 19 |  | 8 |

dppA/dppB locus:

| locus_tag | gene | strand | start | end | gap | case | run |
|---|---|---|---|---|---|---|---|
| PMM1040 | - | + | 983874 | 984734 |  |  | 1 |
| PMM1041 | - | + | 984932 | 985405 | 197 |  | 1 |
| PMM1042 | - | + | 985489 | 986007 | 83 |  | 1 |
| PMM1043 | - | - | 986019 | 986378 | 11 |  | 2 |
| PMM1044 | rbsK | - | 986582 | 987451 | 203 |  | 2 |
| PMM1045 | - | + | 987493 | 987861 | 41 |  | 3 |
| PMM1046 | - | - | 987882 | 989111 | 20 |  | 4 |
| PMM1047 | - | + | 989114 | 990676 | 2 |  | 5 |
| PMM1048 | dppB | - | 990673 | 991695 | -4 | YES | 6 |
| PMM1049 | dppA | - | 991688 | 993259 | -8 | YES | 6 |
| PMM1050 | - | - | 993281 | 993541 | 21 |  | 6 |
| PMM1051 | thrA | - | 993604 | 994905 | 62 |  | 6 |
| PMM1052 | sufE | - | 994941 | 995366 | 35 |  | 6 |
| PMM1053 | - | - | 995404 | 995961 | 37 |  | 6 |
| PMM1054 | ruvC | - | 995971 | 996444 | 9 |  | 6 |
| PMM1055 | chlI | - | 996449 | 997537 | 4 |  | 6 |
| PMM1056 | trmJ | - | 997801 | 998550 | 263 |  | 6 |
| PMM1057 | cytM | - | 998550 | 998933 | -1 |  | 6 |

dppA and dppB overlap by 8 bp (dppA start 991688 < dppB end 991695). The tool reports bp_gap 0.

Their − strand run continues without a break through PMM1050, thrA, sufE, PMM1053, ruvC, chlI, trmJ and cytM (gaps 4–263 bp). **A same-strand-run rule over-merges here.**

The neighbourhood includes two other transporter-like genes:
- PMM1046: MFS, no TCDB terms in the KG.
- PMM1047: α/β hydrolase.

**Metabolism genes for dpp substrates:**

| Substrate | MED4 metabolism genes | Inside a dpp neighbourhood? |
|---|---|---|
| Heme C00032 | PMM0525 hemH, PMM0448 ctaB, PMM1594 ho1 | no |
| 5-Aminolevulinate C00430 | PMM0215 hemB, PMM0483 hemL | no |
| Glutathione C00051 (inherited) | 8 genes: PMM0110, 0566, 0630 gst; PMM1006 gpx; PMM0567 gor; PMM0178 gshB; PMM0559 glx2; PMM0653 glx1 | no (PMM0178 is outside the ddpD window, which starts at PMM0184) |
| L-Ala-L-Ala, tripeptide, EDTA, bradykinin, stachydrine, peptide, oligopeptide, microcin c | none (`not_matched`) | — |

- PMM0184 pabC (ammonia, R00985) is in the ddpD window. Ammonia is not a dpp substrate.

**Expected outcomes**
- ONE system split across three loci (≈185 kb, ≈400 kb, ≈991 kb). dppA + dppB are adjacent (one − run). dppC and ddpD are each isolated on + with unrelated neighbours.
- No subunit is missing: SBP + 2 permeases + ATPase. ddpD carries a single ABC domain plus the oligopeptide C-terminal domain. A full Opp/Dpp set usually has two ATPases.
- Two caveats for a method:
  - [interpretation] Only one ATPase is found.
  - **No locus-based method will rebuild this system.** The KG link is only through the shared 3.A.1.5 attachment and the dpp/ddp gene names.
- Neighbours are context; none is a linked enzyme for the dpp substrates.
- can_use:
  - Heme = **elsewhere in genome**
  - 5-aminolevulinate = **elsewhere in genome**
  - Glutathione (inherited) = **elsewhere in genome**
  - L-Ala-L-Ala, tripeptide, EDTA, bradykinin, stachydrine, peptide, oligopeptide, microcin c = **no**. Ambiguity: several are chebi-namespaced, and the metabolism arm joins only through KEGG reaction compounds. "no" may be a namespace gap, not a biological absence (see Anomalies).
- [interpretation] The 3.A.1.5 substrate set under "most_specific" is dominated by non-peptide compounds (heme, EDTA, stachydrine, ALA). The generic peptide/oligopeptide entries arrive only as *inherited*. A method that keeps only most_specific substrates will report this peptide transporter as moving heme/EDTA/ALA and will drop "oligopeptide".

---

## Case 5 — pst (non-N control)

| locus_tag | gene | product | strand | start | end | Pfam (curated) | role |
|---|---|---|---|---|---|---|---|
| PMM0710 | pstS | phosphate ABC transporter, phosphate-binding protein PstS | + | 675854 | 676825 | PF12849 PBP superfamily domain | substrate-binding |
| PMM0723 | pstC | ABC-type phosphate transport system permease component | + | 685879 | 686826 | PF00528 | permease |
| PMM0724 | pstA | ABC-type phosphate transport system permease component | + | 686833 | 687726 | PF00528 | permease |
| PMM0725 | pstB | ABC-type phosphate transport system ATPase component | + | 687728 | 688537 | PF00005 | ATPase |

**TCDB:**
- All four have most_specific = **tcdb:3.A.1.7** PhoT family, level 3, score 0.8.
  - PMM0710: homology, eggnog + tcdb_diamond, tier 2, pfam_support uncorroborated, identity 85.9.
  - PMM0723, 0724, 0725: family_inferred, eggnog, tier null, corroborated.
- Superseded rows: tcdb:3.A.1, homology, tier 3. Scores: PMM0723 0.4, PMM0724 0.4, PMM0725 0.6. PMM0710 has no superseded row.
- All `resolved`, score_max 0.8.

**Substrates:**
- **0 N substrates.** All four genes are `not_matched` in the N query.
- Without the N filter: 2 most_specific each (8 rows total), both via 3.A.1.7: Orthophosphate C00009 and Triphosphate C00536.

**Neighbourhood** (35 genes; the PMM0710 and PMM0723–0725 windows overlap):

| locus_tag | gene | strand | start | end | gap | case | run |
|---|---|---|---|---|---|---|---|
| PMM0703 | - | + | 667306 | 667659 |  |  | 1 |
| PMM1877 | - | + | 667745 | 667876 | 85 |  | 1 |
| PMM0704 | - | + | 668058 | 669113 | 181 |  | 1 |
| PMM0705 | phoB | + | 669400 | 670128 | 286 |  | 1 |
| PMM0706 | phoR | + | 670125 | 671273 | -4 |  | 1 |
| PMM0707 | - | - | 671290 | 671616 | 16 |  | 2 |
| PMM0708 | - | - | 671693 | 673975 | 76 |  | 2 |
| PMM0709 | som | - | 674137 | 675495 | 161 |  | 2 |
| PMM0710 | pstS | + | 675854 | 676825 | 358 | YES | 3 |
| PMM0711 | chrA | - | 676875 | 678101 | 49 |  | 4 |
| PMM0712 | arsJ | - | 678132 | 679391 | 30 |  | 4 |
| PMM0713 | gap3 | - | 679403 | 680425 | 11 |  | 4 |
| PMM0714 | arsR | + | 680491 | 680862 | 65 |  | 5 |
| TX50_RS03815 | - | - | 680881 | 681087 | 18 |  | 6 |
| PMM0715 | - | + | 681244 | 681411 | 156 |  | 7 |
| PMM0716 | arsB | - | 681401 | 682411 | -11 |  | 8 |
| PMM0717 | - | - | 682455 | 682685 | 43 |  | 8 |
| PMM0718 | - | + | 682867 | 683403 | 181 |  | 9 |
| PMM0719 | - | + | 683454 | 683759 | 50 |  | 9 |
| TX50_RS09860 | - | + | 683763 | 683912 | 3 |  | 9 |
| PMM1880 | - | - | 684046 | 684228 | 133 |  | 10 |
| PMM0720 | - | - | 684390 | 684644 | 161 |  | 10 |
| PMM0721 | - | + | 685013 | 685351 | 368 |  | 11 |
| PMM0722 | - | - | 685369 | 685602 | 17 |  | 12 |
| PMM0723 | pstC | + | 685879 | 686826 | 276 | YES | 13 |
| PMM0724 | pstA | + | 686833 | 687726 | 6 | YES | 13 |
| PMM0725 | pstB | + | 687728 | 688537 | 1 | YES | 13 |
| PMM1881 | - | + | 688929 | 689078 | 391 |  | 13 |
| PMM0726 | - | - | 689268 | 689576 | 189 |  | 14 |
| PMM0727 | pdeM | - | 689797 | 690441 | 220 |  | 14 |
| PMM0728 | - | - | 690442 | 692919 | 0 |  | 14 |
| PMM0729 | lig | - | 692919 | 694556 | -1 |  | 14 |
| PMM0730 | - | - | 694553 | 695545 | -4 |  | 14 |
| PMM0731 | - | - | 695582 | 695992 | 36 |  | 14 |
| PMM0732 | - | - | 696077 | 696364 | 84 |  | 14 |

Layout:
- pstS (PMM0710) is **isolated** on +, between som (−) and chrA (−).
- About 9 kb and 15 genes separate pstS from pstC (PMM0723).
- pstC-A-B form a tight + run (gaps 6 and 1 bp) that continues to the hypothetical PMM1881 (391 bp).

Other transporters in the neighbourhood, from a TCDB check:
- PMM0711 chrA: 2.A.51.1
- PMM0712 arsJ: 2.A.1.83
- PMM0716 arsB: 2.A.59.1
- PMM0709 som: 1.B.23 / 3.A.23.1 / 1.B.14.1.14
- PMM0704: K+ channel, 1.A.1.x / 2.A.37 / 2.A.38

**Expected outcomes**
- One system: pstS + pstC + pstA + pstB. Split into pstS alone and the pstCAB operon. Complete.
- Expected-negative: **0 N substrates**, so it must not appear in any N-import output.
- Neighbouring arsenic/chromate transporters and the porin are **context**. They are separate systems, not missing Pst subunits.
- phoB/phoR (PMM0705/0706) are context (regulators), not linked enzymes.

---

## Case 6 — salY (PMM0913)

| locus_tag | gene | product | strand | start | end | Pfam (curated) | role |
|---|---|---|---|---|---|---|---|
| PMM0913 | salY | putative ABC efflux system | + | 874141 | 875370 | PF02687 FtsX-like permease C-term; PF12704 MacB-like periplasmic core | permease (PF02687) |

**TCDB:**
- most_specific = **tcdb:3.A.1** ABC superfamily, level 2.
  - homology; sources eggnog + tcdb_diamond; score 0.8; tier 3; both_sources; pfam_support corroborated; identity 37.5, qcov 97.8.
- `include_superseded=True` adds nothing: the gene is attached to the superfamily only.
- Resolution **family_inferred**. `metabolites_by_gene` issues its superfamily auto-warning. score_max 0.8.

**N substrates** (total_matching checked):
- **94 most_specific** (distinct = rows = 94), all at tcdb:3.A.1 itself.
- **139 inherited** (139 rows).
- Total 233 N rows / 233 distinct.

Five inherited examples (offset 0, of 139):
- alpha-amino acid chebi:10208
- alphaprodine chebi:135075
- nitrate chebi:14654
- peptide chebi:14753
- L-alanyl-L-alanine chebi:195181

Key-N check: urea, nitrite and cyanate are also inherited. Ammonia is absent.

**Neighbourhood** (17 genes):

| locus_tag | gene | strand | start | end | gap | case | run |
|---|---|---|---|---|---|---|---|
| PMM0905 | - | + | 866852 | 867187 |  |  | 1 |
| PMM0906 | psaK | + | 867252 | 867515 | 64 |  | 1 |
| PMM0907 | dxs | - | 867518 | 869431 | 2 |  | 2 |
| PMM0908 | ilvA | + | 869548 | 871089 | 116 |  | 3 |
| PMM0909 | scpB | + | 871171 | 871653 | 81 |  | 3 |
| PMM0910 | ylmG1 | + | 871685 | 871963 | 31 |  | 3 |
| PMM0911 | - | - | 871967 | 872296 | 3 |  | 4 |
| PMM0912 | pyk | + | 872358 | 874148 | 61 |  | 5 |
| PMM0913 | salY | + | 874141 | 875370 | -8 | YES | 5 |
| PMM0914 | bioY | + | 875385 | 875957 | 14 |  | 5 |
| PMM0915 | ispA | + | 875954 | 876415 | -4 |  | 5 |
| PMM0916 | - | + | 876418 | 877920 | 2 |  | 5 |
| PMM0917 | gadB | - | 878050 | 879432 | 129 |  | 6 |
| PMM0918 | cumB | + | 879496 | 879993 | 63 |  | 7 |
| PMM0919 | spt | - | 879968 | 881152 | -26 |  | 8 |
| PMM0920 | glnA | + | 881367 | 882788 | 214 |  | 9 |
| PMM0921 | - | + | 882897 | 883952 | 108 |  | 9 |

- salY overlaps pyk by 8 bp and sits in a + run (pyk, salY, bioY, ispA, PMM0916).
- bioY PMM0914, 14 bp downstream, is a transporter: TCDB 2.A.88.1 / 2.A.88.2, the biotin ECF substrate component.
- No ABC ATPase is annotated in the window.
- Ammonia-reacting genes in the window: ilvA PMM0908, cumB PMM0918, glnA PMM0920. They are irrelevant because ammonia is not a salY substrate.

**Expected outcomes**
- salY alone; its role is permease (MacB/FtsX-like). [interpretation] An ABC permease with no ATPase partner annotated nearby. Whether a partner is "missing" or elsewhere cannot be decided from the KG.
- bioY is **context**: a different transporter type (ECF, 2.A.88), not a salY subunit.
- Every N substrate is reachability only, because the gene's resolution is `family_inferred`. **No N substrate should be called a capability.** Expected: excluded from (or flagged in) the N-import list, even though 94 rows carry `substrate_depth=most_specific`.
- can_use for its inherited key-N rows:
  - urea and cyanate = elsewhere in genome (ureCBA, speB; cynS)
  - nitrate and nitrite = no

  These are moot given the superfamily-only flag.

---

## Case 7 — fadD (PMM0402)

| locus_tag | gene | product | strand | start | end | Pfam (curated) | role |
|---|---|---|---|---|---|---|---|
| PMM0402 | fadD | long-chain acyl-CoA synthetase | + | 379757 | 381682 | PF00501 AMP-binding enzyme; PF23562 AMP-binding enzyme C-terminal | **enzyme** (PF00501) |

**TCDB (most_specific):**

| term | name | lvl | evidence | sources | score | tier | agreement | pfam_support | identity / qcov |
|---|---|---|---|---|---|---|---|---|---|
| tcdb:2.A.1 | Major Facilitator Superfamily | 2 | homology | tcdb_diamond | **0** | 3 | single_source | uncorroborated | 25.6 / 48.8 (consensus_n 1) |
| tcdb:4.C.1.1 | 4.C.1.1 (name not populated) | 3 | family_inferred | eggnog | 0.8 | null | both_sources | corroborated | — |

The superseded call adds tcdb:4.C.1, "The Fatty Acid Group Translocation (FAT) Family": homology, tcdb_diamond, score 0.2, tier 3, identity 27.6 / qcov 68.6.

Resolution **resolved**. This is because 4.C.1.1 is non-lumping, even though most rows come from the MFS hit. score_max 0.8, also from 4.C.1.1.

**N substrates** (total_matching checked):
- **62 most_specific**: 60 via 2.A.1 (score 0) and 2 via 4.C.1.1 (score 0.8). The two 4.C.1.1 substrates are Carnitine C00487 and (E)-4-(Trimethylammonio)but-2-enoate C04114.
- **172 inherited**, all via 2.A.1 (score 0).
- Total 234 rows / 233 distinct.
- All transport substrates (no N filter): 482 rows / 481 distinct (111 most_specific, 371 inherited).

Five inherited examples (offset 0):
- alpha-amino acid chebi:10208
- 4-aminohippurate chebi:104011
- a beta-lactam chebi:10426
- nitrate chebi:14654
- pantothenic acid chebi:14739

**Neighbourhood** (17 genes):

| locus_tag | gene | strand | start | end | gap | case | run |
|---|---|---|---|---|---|---|---|
| PMM0394 | ylmE | + | 373571 | 374209 |  |  | 1 |
| PMM0395 | sepF | + | 374367 | 374942 | 157 |  | 1 |
| PMM0396 | proC | + | 374950 | 375756 | 7 |  | 1 |
| PMM0397 | dgdA | - | 375753 | 376919 | -4 |  | 2 |
| PMM0398 | recO | - | 377005 | 377784 | 85 |  | 2 |
| PMM0399 | deoC | - | 377785 | 378444 | 0 |  | 2 |
| PMM0400 | lrtA | - | 378453 | 379037 | 8 |  | 2 |
| PMM0401 | lipB | + | 379082 | 379726 | 44 |  | 3 |
| PMM0402 | fadD | + | 379757 | 381682 | 30 | YES | 3 |
| PMM0403 | - | + | 381740 | 382186 | 57 |  | 3 |
| PMM0404 | - | - | 382301 | 382612 | 114 |  | 4 |
| PMM1845 | - | + | 382974 | 383168 | 361 |  | 5 |
| PMM0405 | pdhC | + | 383670 | 385037 | 501 |  | 5 |
| PMM0406 | queA | + | 385044 | 386168 | 6 |  | 5 |
| PMM0407 | cysK | - | 386171 | 387157 | 2 |  | 6 |
| PMM0408 | - | - | 387242 | 388711 | 84 |  | 6 |
| PMM0409 | metB | - | 388715 | 389878 | 3 |  | 6 |

The + run lipB-fadD-PMM0403 has no TCDB terms on lipB or PMM0403.

**Expected outcomes**
- **Not a real transporter** for this analysis's purposes:
  - The Pfam domains are enzyme (AMP-binding, acyl-CoA synthetase).
  - The MFS call is a score-0, single-source, half-length DIAMOND hit, and it supplies 232 of the 234 N rows.
  - [interpretation] The 4.C.1.1 / 4.C.1 FAT-family attachment reflects TCDB's group-translocation class, which classifies FadD-type acyl-CoA ligases. It is not evidence of a membrane carrier for N compounds.
- Expected: excluded from N-import calls. Any N substrate attributed to it is a false positive, and the score-0 MFS rows especially so.
- can_use is moot. For completeness:
  - cyanate (inherited) = elsewhere (cynS)
  - nitrate, nitrite, carnitine, C04114 and the 5 examples = no

---

## Cross-case expected-outcome summary

| case | system members | linked enzyme | missing subunit | N substrates expected to pass | can_use |
|---|---|---|---|---|---|
| cyn | PMM0370, 0371, 0372 | PMM0373 cynS | none | cyanate (+ nitrite/nitrate as TCDB family substrates) | cyanate co-located; nitrite/nitrate no |
| urt+urease | PMM0970–0974 | PMM0963–0965 urease (+ accessory 0966–0969) | none | urea (hydroxyurea, thiourea as family substrates) | urea co-located; others no |
| amt1 | PMM0263 | none | none (single carrier) | ammonia, methylamine, ethylamine, TMA | ammonia elsewhere (window rule: co-located via pncC); rest no |
| dpp | PMM1049, 1048, 0421, 0192 (3 loci) | none | none by role (one ATPase only) | 7 most_specific (peptides only as inherited) | heme, ALA, GSH elsewhere; rest no |
| pst | PMM0710, 0723, 0724, 0725 | none | none | **none (expected-negative)** | — |
| salY | PMM0913 | none | [interpretation] no ATPase annotated nearby | **none as capability** (family_inferred) | moot |
| fadD | PMM0402 (enzyme) | — | — | **none** (not a transporter) | moot |

## Anomalies and tool behaviour to flag

1. **Nitrate is split across two metabolite nodes.**
   - The cyn transporter maps to `chebi:14654` "nitrate" (NO3).
   - `kegg.compound:C00244` "Nitrate" (HNO3) is a separate node, with 13 MED4 transport rows of its own. These include 8 genes under tcdb:3.E.1 (microbial rhodopsin family) that are response regulators or kinases (rpaA, rpaB, phoB, sasA, srrA …), at score 0–0.2.
   - Pantothenate is split the same way: chebi:14739 has no metabolism genes, C00864 has coaX and panC-cmk.
   - So a "no metabolism gene" result for a chebi-namespaced transport substrate can be an ID-namespace gap, not a biological absence. For nitrate the conclusion still holds, because C00244 also has 0 metabolism rows in MED4.
2. **dpp most_specific vs inherited looks inverted.** The generic peptide entries ("peptide", "Oligopeptide") come only as inherited. The most_specific set for 3.A.1.5 is heme, EDTA, ALA, stachydrine, bradykinin, Ala-Ala and tripeptide.
3. **salY: inherited rows report the attachment as their family.** salY is attached only to tcdb:3.A.1, yet 139 rows are `inherited` while also reporting `tcdb_family_id=tcdb:3.A.1`. "Inherited from where" is not visible on the row. Presumably from levels above 3.A.1; unverified.
4. **fadD reads `resolved` even though 232/234 N rows come from a score-0 MFS hit.** Gene-level `tcdb_evidence_score_max=0.8` comes from the 4.C.1.1 attachment and hides the score-0 rows. Row-level `tcdb_evidence_score` is needed to catch it.
5. **TCDB names are missing or truncated for some terms.** `tcdb:4.C.1.1` and the bare `1.A.1.x` / `2.A.88.x` terms have the ID as their name. `tcdb:3.A.1.4.4` is named "The high-affinity (".
6. **PMM0974 urtE has a spurious tcdb:1.B.42 (LPS export porin) hit** at score 0, single_source. It is harmless for N (no N rows), but it widens the gene's family list.
7. **The ReadMcpResource tool was not available in this session.** The `docs://analysis/metabolites`, `docs://ontologies/tcdb` and `gene_neighbors` docs were read from the explorer package's bundled copies (`.venv/Lib/site-packages/multiomics_explorer/skills/multiomics-kg-guide/references/`) instead. Same content source, different access path.
8. **`gene_neighbors` returns coordinates only for anchors.** Neighbour rows have no start/end. To compute adjacent gaps, every neighbour was re-queried as an anchor (`summary=True`, window 1), which returns anchor coordinates with no rows. A method that computes gaps from `bp_gap` alone will get wrong adjacent gaps for any offset beyond ±1.

## Tool calls

| # | tool | key params | total_matching / returned |
|---|---|---|---|
| 1 | kg_release_info | — | verdict ok |
| 2 | gene_neighbors | anchors PMM0370–0373, window 8, limit 200 | 64 / 64 |
| 3 | gene_neighbors | 16 cyn neighbours as anchors, window 1, summary | anchors only (16) |
| 4 | gene_neighbors | anchors PMM0963, 0974, 0263, 0710, 0723, 0725, 0913, 0402; window 8; limit 200 | 128 / 128 |
| 5 | gene_neighbors | anchors PMM1049, 1048, 0421, 0192; window 8; limit 200 | 64 / 64 |
| 6 | gene_neighbors | 80 neighbour tags (amt1, fadD, pst, salY loci + PMM0724), window 1, summary | anchors only (80) |
| 7 | gene_neighbors | 74 neighbour tags (ure/urt, dpp loci), window 1, summary | anchors only (74) |
| 8 | gene_ontology_terms | 27 case genes, ontology ['pfam'], limit 200 | 36 / 36; no_terms [] |
| 9 | gene_ontology_terms | 27 case genes, ['tcdb'], leaf, verbose | 30 / 30; no_terms = PMM0373, 0963–0969 |
| 10 | gene_ontology_terms | same + include_superseded=True | 46 / 46 |
| 11 | metabolites_by_gene | 27 genes, transport, elements ['N'], summary | 547 / 0 (by_gene complete for 15 matched; not_matched 12) |
| 12 | metabolites_by_gene | cyn 0370–0372 + urt 0970–0974 + amt1, transport, N, limit 100 | 36 / 36 |
| 13 | metabolites_by_gene | dpp 4 genes, transport, N, limit 11 | 44 / 11 (remaining identities from top_metabolites: 11 distinct, all 4 genes) |
| 14 | metabolites_by_gene | pst 4 genes, transport, no element filter | 8 / 8 |
| 15 | metabolites_by_gene | PMM0913, transport, N, depth inherited, limit 5 | 139 / 5 |
| 16 | metabolites_by_gene | PMM0402, transport, N, depth inherited, limit 5 | 172 / 5 |
| 17 | metabolites_by_gene | PMM0402, transport, N, depth most_specific, limit 5 | 62 / 5 (families: 2.A.1 = 60, 4.C.1.1 = 2) |
| 18 | metabolites_by_gene | PMM0402, transport, summary (no N filter) | 482 / 0 |
| 19 | metabolites_by_gene | PMM0913, transport, N, depth most_specific, limit 5 | 94 / 5 |
| 20 | metabolites_by_gene | PMM0913 + PMM0402, transport, ids [C00014, C00086, C01417, chebi:14654, C00088] | 7 / 7 |
| 21 | genes_by_metabolite | 20 substrate ids, MED4, metabolism, summary | 69 / 0; not_matched 15 ids |
| 22 | genes_by_metabolite | [C00086, C01417, C00032, C00430], metabolism, limit 20 | 11 / 11 |
| 23 | genes_by_metabolite | [C00014], metabolism, summary | 58 / 0; gene_count 36 (top_genes 36, not truncated) |
| 24 | genes_by_metabolite | [chebi:14753, C00098, C00051, chebi:82754], metabolism, limit 30 | 74 / 30 (GSH genes complete via top_genes = 8) |
| 25 | genes_by_metabolite | [chebi:10208, chebi:135075, chebi:104011, chebi:10426, chebi:14739], metabolism, summary | 0 / 0; all not_matched |
| 26 | genes_by_metabolite | [C00244, C00864, kegg.compound:C00244], no source filter, summary | 15 / 0 (namespace check) |
| 27 | gene_ontology_terms | 24 neighbour genes, ['tcdb'] leaf | 22 / 22; no_terms 13 genes |
