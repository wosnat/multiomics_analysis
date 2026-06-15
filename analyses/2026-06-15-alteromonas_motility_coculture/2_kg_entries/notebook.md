# Step 2 — KG entries (redone 2026-06-15)

## Context

This step was redone after the reframe (see step 1 and step 3 notebooks). The
original step 2 froze a narrow slice — 9 coculture-with-*Prochlorococcus* DE
contrasts for HOT1A3 + EZ55 — pulled with a `treatment_type=["coculture"]`
filter. That filter hid the time-courses and the control contrasts, and it
swept in experiments whose direction turns out to be unreadable. Redone: pull
**every** *Alteromonas* experiment across all strains, then annotate each for the
two things the reframe actually turns on — **whether organic carbon is added to
the medium**, and **whether the differential-expression direction is
trustworthy**.

co-defined with the researcher: common lens = coculture-with-*Prochlorococcus*
vs axenic; in these media *Prochlorococcus* photosynthate is *Alteromonas*'s only
organic-carbon source, so the contrast is close to organic-C-fed vs starved;
motility is the lead readout; other contrasts are controls; drop the corrupted
experiments.

## What I did

`scripts/01_extract_entries.py` (a3 Python API) froze:
- `data/experiment_inventory.csv` — one row per *Alteromonas* experiment (49),
  with `medium`, `added_organic_c`, `growth_phases`, `n_timepoints`, the log2FC
  sign distribution (`neg_l2fc`/`pos_l2fc`/`pct_neg`), and a computed
  `direction_quality` flag.
- `data/motility_genes.csv` — motility gene sets (KEGG flagella ko02040 +
  chemotaxis ko02030 primary; broad COG-N sensitivity) for the three strains
  with ≥1 usable DE experiment (HOT1A3, EZ55, MIT1002).

Two annotations are **computed, not asserted from chat**:
- `added_organic_c` — rule-based from medium-recipe / treatment tokens
  (glucose, lactate, pyruvate, acetate, glycerol → `yes`; "natural seawater" →
  `background`; defined inorganic media → `no`). `[interpretation]`, transparent
  in the script.
- `direction_quality` — from the sign of `log2_fold_change` over **all** DE rows.
  A genuine all-genes table is ~symmetric around 0; 0% negative across ≥50 genes
  means the sign was lost (unusable for direction). `[KG]`, computed.

The narrow `coculture_experiments.csv` from the first pass was removed
(superseded).

## Results

### The full landscape `[KG]`

49 *Alteromonas* experiments, 8 strains, 10 papers. By data quality:

| direction_quality | n | meaning |
|---|--:|---|
| `ok_all_genes` | 23 | both directions + valid all-genes background (ORA-ready) |
| `ok_significant_only` | 12 | direction readable, but no all-genes background (direction-only) |
| `sign_lost` | 4 | 0% negative over hundreds–thousands of genes → **corrupted, drop** |
| `sparse` | 2 | all-positive but only ~4 genes → too few to judge |
| `no_de_edges` | 8 | vesicle/compartment proteomics — no DE edges |

### The medium / organic-carbon finding `[KG]` + `[interpretation]`

Per the `medium` field, with organic-carbon classification:

| medium | n | added organic C? |
|---|--:|---|
| PRO99-lowN (Weissberg HOT1A3) | 5 | **no** — low-N, inorganic |
| Pro99 / Pro99 medium (Aharonovich, Barreto Filho) | 18 | **no** (pCO₂ "carbon" treatment is inorganic) |
| Pro99 natural seawater (MIT1002) | 4 | **no added** (background DOC) |
| PEv 1/25 Pro99 artificial SW (EZ55 2017) | 2 | **no** |
| SN / Pro99 + glucose (spectrum MarRef) | 12 | **yes** — glucose amendment |
| AMP1 + lactate/pyruvate/acetate/glycerol (femsml vesicle) | 6 | **yes** |
| Pro99 + 0.1% glucose (EZ55 compartment) | 2 | **yes** |

**The load-bearing fact:** none of the coculture-vs-axenic contrasts we'd use
(HOT1A3, EZ55, MIT1002) have added organic carbon. *Alteromonas* is a heterotroph
needing an organic-C source, so in axenic PRO99-lowN it has none; in coculture the
only organic carbon is *Prochlorococcus* photosynthate. This is what makes the
contrast a carbon-provision test (step 3). `[interpretation]`

### The usable coculture-with-*Prochlorococcus* set `[KG]`

- **HOT1A3 / Weissberg 2025 (primary).** MED4 coculture-vs-axenic — a single
  **day-11 exponential** snapshot (RNA, all genes, 111↑/163↓, `ok_all_genes`) —
  plus four PRO99-lowN starvation **time-courses** running **day 18→89**
  (`nutrient_limited`; RNA + protein × coculture + axenic; RNA 5/3 timepoints,
  protein 5/2; all `ok_all_genes`). The growth-phase split matters for the framing
  (step 3): the snapshot is a partner-during-growth read, the time-courses are
  where starvation develops. Note the **axenic protein series stops at day 31**.
- **EZ55 / Barreto Filho 2022.** MIT9312 coculture, 2 pCO₂ levels (`significant_only`
  → direction-only). Synechococcus contrasts (CC9311, WH8102) = partner control.
- **MarRef / spectrum 2022.** *Prochlorococcus*-coculture proteomics — but these are
  **glucose-amended** (organic-C-replete), so they're a "fed reference," not the
  no-added-C contrast; counts tiny.
- **Direction-limited context only:** MIT1002 NATL2A coculture (`significant_any`).

### Dropped for corruption (`sign_lost`) `[KG]`

The 4 experiments from the two 2016 *ISME J* papers — HOT1A3+MIT9313 (Aharonovich
& Sher 2016, ×2) and MIT1002+NATL2A (ismej.2016.82, ×2) — have 0% negative log2FC
across all detected genes. Out of the analysis entirely. Cause unresolved; logged
in `gaps_and_friction.md`.

### Motility gene sets `[KG]`

| strain | KEGG flagella+chemotaxis | COG-N | union |
|---|--:|--:|--:|
| HOT1A3 | 96 | 126 | 144 |
| EZ55 | 102 | 131 | 151 |
| MIT1002 | 83 | 114 | 130 |

## Decisions

- **2026-06-15 — full cross-strain inventory replaces the coculture-only slice.**
  The reframe needs the control contrasts and time-courses the old filter hid.
- **2026-06-15 — drop the 4 `sign_lost` experiments** (both 2016 papers) — direction
  unreadable.
- **2026-06-15 — annotate `added_organic_c` and `direction_quality` in-script** so
  the carbon-provision framing and the usable set rest on reproducible columns,
  not chat assertions.

## Decide-gate checklist

- **Outputs produced:** `scripts/01_extract_entries.py`;
  `data/experiment_inventory.csv` (49), `data/motility_genes.csv` (425), log.
- **Results presented:** landscape-by-quality, medium/organic-C table, usable
  Prochlorococcus-coculture set, dropped-for-corruption set, motility counts (all
  shown to researcher in chat).
- **QC gate:** `direction_quality` computed from log2FC signs over all rows
  (corruption caught reproducibly, with a ≥50-gene threshold to avoid flagging
  sparse data); KG release verified ok on explorer a3 (preflight green).
- **Advance rationale:** experiments, media, data-quality, and gene sets are frozen;
  step 3 frames the carbon-provision test on the clean usable set.
