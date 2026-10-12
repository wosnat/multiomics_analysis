# Evaluation milestone — notebook

*Owned by the main thread. No new computation: the analysis milestone's outputs are the trusted
evidence (`analysis/notebook.md`, `analysis/data/`, `analysis/critical_review.md`). Revised after
the evaluation critic (`evaluation/critical_review.md`).*

## Co-define (2026-10-12)

The researcher said "ok. go" to the routine evaluation scope:
1. assess the provisional reading against each framing item in `proposal.md`;
2. collect the caveats in one place;
3. write the paper's Discussion and conclusion;
4. run an interpretation-only critic;
5. show the conclusion to the researcher, then commit.

## 1. The framing, item by item

Outcomes are [KG] from the analysis milestone; the "Reading" column is the assessment.

| Framing item (proposal) | Outcome | Reading |
|---|---|---|
| **Question:** which N classes does MED4 raise import capacity for beyond early axenic starvation? | The "early axenic" reference is a late-decline culture (researcher). Labels deferred (analysis decisions 4–5). | **Not answerable as posed** with these references. In protein, ammonium, urea and cyanate import capacity is raised and **sustained** in coculture (amt1 from d31; it lags at d18). In the dying axenic culture, the **urea and cyanate systems fall to mid-rank** (urt 0.79 → 0.48/0.57; cyn 0.99 → 0.72/0.67), while **amt1 and urease do not fall** (amt1 0.66 → 0.69 → 0.78) and the regulators stay high. |
| **Hypothesis readings:** (i) supply too low to relieve N stress, all NtcA systems up together; (ii) partial relief, alternative-N systems damped | In protein, urt, cyn, urease and cynS are in the top 10% from d18, amt1 from d31, clustered with the markers. Damping can't be detected at the percentile ceiling. | **(i) and (ii) are not distinguishable here.** (i) is also what no supply at all would produce. Weak hints in the (ii) direction: P2 passes at d89; `ntcA` protein log2FC eases 2.23 → 1.17 (d31 → d89); the protein-synthesis cluster c7 climbs back 0.12 → 0.35. There is no partial-supply calibration in the KG (a pre-registered gap). |
| **P1** (blind): amt1 RNA ≥ 0.90 at d60 and d89 | **Fail** (0.064, log2FC −1.54; 0.656) | Per the pre-registration, this counts against ammonium as the primary route at the transcript level. Caveat: coculture RNA is measured against an exponential phase that was already N-stressed, so P1 can't separate "not induced" from "induced early". |
| **P2** (blind): amt1 ≥ median of urt + cyn in RNA | Fail d60, pass d89 | Mixed; not the "both days fail" outcome. |
| **Calibration gate C1–C3** | C1 pass; **C2, C3 fail** | Per the pre-registration: **no compound named from the consumer side.** The failure is driven by urt: not up on urea, and `urtA` up on cyanate. cyn *was* specific in its one test (cyanate 0.96 vs urea 0.12). In MIT9313, urt and focA are not specific (E8). `amt1` is not up on cyanate (0.38) although `glnA` is. |
| **C4** (acute starvation fingerprint) | Tolonen passes only under the relaxed rule of decision 3 (≥ 1 subunit; the ≥ half variant fails, urt 2/5); Read fails | The plain-starvation reference rests on axenic d14 + Tolonen. |
| **Biology sanity gate** | Pass in protein (15/15) | A usable N-starvation response in protein. |
| **Expected-negative 1** (nitrate/nitrite unusable in MED4) | Pass (72/72) | The `can_use` check works. |
| **Expected-negative 2** (N-replete cocultures: no N system up) | Pass for MED4 (in a table that is 82% negative, which may limit "up" calls) and NATL2A (can only fail). **Fails in one MIT9313 inoculum:** `natF` PMT0897 +1.57, padj 2e-12; `natG` down in the same table; the 5e6 inoculum is null. | For MED4, coculture alone does not induce the N systems in replete medium. Per the pre-registration, the MIT9313 "up" and the MED4 "down" pointers (urtE, dppA, cynS strongly down in that skewed table) pass to the contrast analysis. |
| **Expected-negative 3** (non-N systems don't stand out late) | Pass | No general transporter programme. The iron cluster is modestly raised in protein (a hint only). |
| **Falsifiability: "nothing real"** = no class stands out AND every N system moves with the markers | **Not evaluated as pre-registered.** The first condition needs the labels, which were deferred. Under the rules adopted for later (decisions 1–2), amt1 (0.98/0.98 vs axenic d14 0.66; +0.32) and urt (0.93/0.93 vs 0.79; +0.15) pass criteria (a) and (b). Criterion (c) was not computed. | Against a dying reference, passing (a)/(b) means "higher than in a dying culture", which can't be read as partner-specific. Post hoc only: no N route is coculture-specific in the stricter E14 sense (not up in any axenic sample or in Tolonen). |
| **Named alternative: starvation length, not partner** | No surviving late axenic sample. | **Cannot be separated** (anticipated in §3.5). amt1 rises over time in *both* cultures, which fits the duration alternative. |
| **Secondary question:** N-limitation-specific? | Expected-negative 2: MED4 pass; one MIT9313 inoculum fails. Per-class tables for other strains deferred (decision 7). | For MED4, coculture does not induce the N systems in N-replete exponential growth. In this study's low-N medium, though, the same-study d11 contrast shows the coculture N regulon above axenic already in exponential growth (`glnA` +2.44, `cynA` +3.11). For MIT9313 the answer is mixed. |

## 2. Conclusion (approved by the researcher, 2026-10-12)

**What we tested.** We built MED4's 73 transport systems from its own annotation and read their
protein and RNA through 89 days of N-limited coculture with *Alteromonas*. We compared them with
three kinds of reference:
- the axenic culture of the same study (already declining by day 14);
- acute N starvation (Tolonen 2006: N deprivation, and growth on cyanate or urea);
- N-replete cocultures (Aharonovich 2016; Biller 2016).

**What was up in coculture** (protein; rank 1.0 = most up-regulated gene):

| N route | Coculture (d18–d89) | Axenic (declining, d14–d89) | Acute N starvation | N-replete coculture |
|---|---|---|---|---|
| Ammonium (`amt1`) | Up from day 31; top 2% by day 60 (0.98) | Not up at d14–d31; up at d89 (death) | Up | Not up |
| Urea (urt + urease) | Up; top 1–7% | urt drops (down at d31); urease stays up | Up | Not up |
| Cyanate (cyn + cyanase) | Up; top 1% | Up at d14, then mid-rank (0.67–0.71) | Up | Not up |
| Dipeptides (dpp) | Up (`dppA`, `dppC`; 0.82–0.89) | Only `dppC`, late | Not up | Not up |
| Amino acids, polyamines, osmolytes (broad listings) | No consistent signal | No signal | Not up | Not up |
| N-starvation regulators (`glnA`, `ntcA`, `glnB`) | Up | Up | Up | Not up |

**What it means:**
1. MED4 runs a full N-starvation response throughout the coculture. Its ammonium, urea and cyanate
   import machinery stays among its most abundant proteins for 89 days.
2. These are the systems that acute N starvation switches on and that N-replete coculture does not.
   The coculture response matches N limitation rather than a general partner effect.
3. The coculture keeps the urea and cyanate systems that the declining axenic culture lets drop. The
   ammonium transporter comes up later in both.
4. Dipeptide import is raised mainly in coculture, but its subunits don't move together.
5. No amino-acid, polyamine or osmolyte route responds.

**What it can't tell us.** The import systems don't report their own substrate. In calibration
experiments the urea system rose on cyanate, not on urea. So expression can't name the compound MED4
takes up. That question goes to the *Alteromonas* analysis.

Caveats in brief:
- the axenic culture is declining, so "kept in coculture" may also mean "kept alive";
- RNA is measured against a reference that was already N-stressed in coculture;
- the pre-registered class labels were deferred.

Details: Discussion and `evaluation/notebook.md`.

**Implication for the preprint rewrite** `[interpretation]`:
- The claim that MED4 "up-regulates high-affinity nitrogen scavenging" holds in **protein**, as
  maintenance of the N-starvation response.
- It does not hold in RNA, which is flat or down against an N-stressed reference.
- "High-affinity" was not tested, and "89 days" is culture age, not time under N limitation.
- It is not evidence of a specific supplied compound. The blind ammonium test (P1) failed with a
  caveat, so the consumer side gives no positive support to the ammonium-supply reading.
- Any statement about supply needs the producer side.

## 3. Caveats (consolidated)

**Data and design:**
1. All axenic samples are late decline or death, so partner effects are confounded with survival.
2. Each culture's RNA is compared with its own d11 sample. The coculture d11 was already
   N-stressed relative to axenic. The protein d11 baseline is unmeasured.
3. The anchor RNA contrasts are algebraically linked (one fitted model). The d18 contrast mainly
   reflects the axenic decline (877 vs 84 significant genes).
4. Stored significance includes |log2FC| ≥ 1; some significant RNA rows have null padj; Tolonen and
   Biller padj are coarse.
5. Rank percentiles at the ceiling (~0.98) can't detect damping or excess over the stimulon.

**Annotation:**
6. TCDB substrate lists are per subfamily; dedicated vs broad comes from name keywords; some routes
   are reachable only by family-level listing.
7. 21 MED4 transporter genes are undetected in protein.
8. KG generic vs stereo-specific compounds (Cysteine) are fixed in analysis code only.

**Inference:**
9. Expression measures capacity, not use; uptake can occur without induction.
10. `amt1` and dpp were not calibrated on their own substrates; there is no partial-supply
    calibration.
11. Deviations from the pre-registered plan are disclosed in analysis decisions 1–7: labels
    deferred, protein-only rule, relaxed C4, flags redefined. Falsifiability could not be evaluated
    as pre-registered.

**Outside the KG:**
12. No N compounds measured in the coculture are in the KG; the researcher's culture measurements
    were deliberately left out.

## 4. Hand-offs

- **Alteromonas analysis:**
  - N-release routes;
  - test d11 competition (amt / `glnA` / NtrBC at d11);
  - reuse the methods module with the non-Cyanorak redefinitions.
- **Contrast analysis:**
  - the per-class tables for MIT9313/NATL2A (decision 7);
  - the deferred labels, including computing criterion (c);
  - the pre-registered expected-negative-2 pointers: the MIT9313 `natF` "up" and the MED4 "down"
    calls.
- **KG:**
  - culture measurements and cell counts (node type; figure extraction);
  - generic ↔ stereo-specific compound equivalence;
  - per-arm sampling days;
  - a shared-model identifier for linked contrasts.
- **Possible separate analyses:** the envelope set (`murJ`; `tolC`/`acrA`/`bamA`/`perM`/`mgtE`); the
  iron hint; a generic-stress score; pathway enrichment; the researcher's culture N budget.
