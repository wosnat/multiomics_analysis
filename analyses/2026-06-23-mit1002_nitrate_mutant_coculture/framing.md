# Framing — MIT1002 nitrate-assimilation mutants × Prochlorococcus long-term survival

**Date:** 2026-06-23 · **KG release:** 0.1.0-alpha.6 (built 2026-06-16)
**Status:** pre-analysis framing / hypothesis note (not a committed 6-step proposal)

Tags: `[KG]` = from a KG query · `[interpretation]` = reasoning from intrinsic/
literature knowledge · `[gap]` = the KG can't answer.

---

## Experimental setup (as described by researcher)

- **Heterotroph:** *Alteromonas macleodii* MIT1002, wild type vs. knockouts in its
  assimilatory nitrate/nitrite pathway.
- **KO targets** `[KG]`: `MIT1002_00700` **nasA** (nitrate reductase, KEGG K00372),
  `MIT1002_00710` **nrtB** (nitrate/nitrite ABC permease, K15577),
  `MIT1002_00711` **nasD** (nitrate/nitrite ABC ATP-binding, K15578). Same operon also
  carries `00698/00699` **nirB/nirD** (nitrite reductase), `00709` **nrtC/nrtA**
  (substrate-binding), `00694` **nasR** (regulator). KOs disable both uptake
  (nrtB/nasD) and nitrate→nitrite reduction (nasA).
- **Partners:** *Prochlorococcus* MED4, MIT1314, PAC1.
- **Medium / regime:** Pro99-lowN; long-term growth + survival after N depletion.

## Anchor: the published recycling mechanism `[KG]` (Weissberg et al. 2025, 10.1101/2025.11.24.690089)

In Pro99-lowN over ~90 days, axenic MED4 dies quickly after N is depleted; in coculture
with *Alteromonas* (HOT1A3) it survives for months. Mechanism: *Alteromonas* remineralizes
organic matter and feeds back a continuous low-level supply of **ammonium (NH₄⁺)**;
Prochlorococcus upregulates high-affinity N scavenging. The recycled currency is ammonium,
via **ammonification** — not nitrate.

## Prochlorococcus N-source capability `[KG]`

| N source | MED4 (HLI) | MIT1314 (HLII) | PAC1 (LLI) |
|---|---|---|---|
| Ammonium (*amt*) | ✓ `PMM0263` | ✓ `SOI86_RS07995` | ✓ (assumed) |
| Urea (*urt*+*ure*) | ✓ `PMM0963–0974` | ✓ `SOI86_RS013xx` | ✓ (assumed) |
| Cyanate (*cynABDS*) | ✓ `PMM0371–0373` | ✗ | ✓ `EV03_0570` |
| **Nitrite** (*nirA*,*focA*) | **✗** | **✗** | **✓** `EV03_1089/1090` |
| **Nitrate** (*narB*,*nrtP*,*moaA/C*) | **✗** | **✗** | **✓** `EV03_1106/1107/1099/1098/1101` |

Decisive split: **MED4 and MIT1314 cannot use nitrate or nitrite at all; PAC1 can use both.**

## The question

Does MIT1002's **nitrate/nitrite assimilation** participate in the recycling loop that
sustains Prochlorococcus — or is the survival-supporting N delivered as ammonium without
ever passing through nitrate? `[interpretation]` Mechanistic default: remineralization is
ammonification (organic-N → NH₄⁺ directly); routing through nitrate/nitrite needs oxidation
(nitrification), which *A. macleodii* does not perform. So unless **nitrate is present in
Pro99-lowN to begin with**, the Nas/Nrt machinery has no substrate. **Medium nitrate content
is the linchpin.**

## Hypothesis — two scenarios; the strain panel resolves which

**Scenario A — pure ammonification (nitrate pathway not involved / no nitrate present).**
*Leading expectation given the published mechanism.* The KO has little/no effect on long-term
survival for **any** strain; MIT1002 regenerates NH₄⁺ directly and *nas* genes sit idle.
MED4 ≈ MIT1314 ≈ PAC1, WT ≈ mutant. → recycled N is direct ammonium; nitrate assimilation
dispensable.

**Scenario B — nitrate/nitrite is an obligatory intermediate (or a real medium pool).**
KO strands N in oxidized form.
- **MED4 & MIT1314** (no nitrate/nitrite use) → **reduced survival** with the mutant.
- **PAC1** (uses nitrate/nitrite itself) → **buffered/rescued**: scavenges the stranded
  nitrate/nitrite directly → survival largely insensitive to the KO.
- Signature: **strain × genotype interaction**, PAC1 the outlier.

**PAC1 is the diagnostic strain:**
- mutant hurts MED4/MIT1314 but spares PAC1 → **Scenario B** (nitrate is in the loop);
- mutant hurts nobody → **Scenario A** (ammonification only);
- mutant hurts everyone incl. PAC1 → MIT1002 *nas* genes carry a **pleiotropic / non-nitrate
  role** in the partnership.

## Caveats `[gap]` / `[interpretation]`

- **Medium N composition decides A vs B before any biology.** Standard Pro99 N is ammonium;
  confirm whether the lowN base carries nitrate.
- **Strain swap:** the published recycling result is **HOT1A3**, not MIT1002. WT-MIT1002
  survival baselines per Pro strain are themselves untested.
- **No expression evidence:** MIT1314 and PAC1 have zero experiments in the KG; MIT1002's
  transcriptome is not in the KG — whether these *nas* genes are expressed under starvation
  is unknown here.
- The earlier null (NATL2A + MIT1002, no Pro N-gene response) is short-term N-replete
  exponential growth — a different regime; it does not bear on the survival phenotype.

## Provenance

KG release 0.1.0-alpha.6. Capability calls: `resolve_gene`, `gene_neighbors`,
`gene_ontology_terms` (MIT1002 operon); `genes_by_function` scoped per strain (MED4 / PAC1 /
MIT1314 nitrogen genes); `list_publications` (10.1101/2025.11.24.690089 abstract). PAC1
ammonium/urea marked "assumed" — not yet queried.
