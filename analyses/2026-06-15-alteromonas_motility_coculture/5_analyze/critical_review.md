# Critical review — Step 5 (Analyze)

**Reviewer:** fresh-context critic (`critical-review` skill, general-purpose
subagent), dispatched 2026-06-17. **Context of this run:** dispatched to
*evaluate* the new critical-review skill against a completed, already-committed
step — not as part of that step's original decide phase. Dispositions below are
therefore provisional; a redo of step 5 to act on the Blockers is pending the
researcher's decision.

The critic read the step's artifacts cold (no session history) and checked
claims against the data files. Three of its file-based claims were independently
re-derived from the data after the run — results noted under each.

---

## Findings (critic verbatim)

### Blocker · data-integrity — "motility down in both arms"
**Claim/location:** notebook.md 5a ("flagellar/chemotaxis signed scores negative
throughout"); paper.md ("flagellar/chemotaxis genes are down under starvation in
coculture and axenic alike").
**Problem:** The protein axenic arm at day 31 shows flagellar assembly
significantly UP. `data/hot1a3_prot_axenic_motility_genes_de.csv`: flgH +4.81,
flaA +4.76, flgE +4.41, flaA +4.34, flgI +4.14, flgK +3.71, flgG +3.57 — all
`significant_up`. `data/pathway_trajectories.csv` prot_axenic Flagellar assembly
signed_score +1.48, p_adjust 0.033 (significant UP). `data/motility_divergence_stats.csv`
records n_ax_up=15 vs n_ax_down=15 at protein day 31. "Negative throughout / down
in both arms" is false for the protein layer.
**Recommendation:** Restrict "down in both arms" to RNA; state that axenic
protein flagellar assembly is significantly UP at day 31, and reconcile with the
carbon-provision interpretation.
**Verification (2026-06-17):** CONFIRMED EXACT. Re-derived from the file:
flgH +4.806, flaA +4.756, flgE +4.412 … 15 motility genes `significant_up`,
15 `significant_down`, 80 `not_significant` at day 31; pathway signed_score
+1.4809, p_adjust 0.0330.

### Blocker · science — contrast is starvation-vs-exponential, not coculture-vs-axenic
**Claim/location:** notebook.md 5-9; scripts/01_timecourse.py docstring
("coculture vs axenic … magnitude comparable"); the 5a divergence framing.
**Problem:** Each arm's log2FC is starvation-vs-its-own-exponential-baseline. The
Wilcoxon subtracts (coculture starvation response) − (axenic starvation response):
a difference-in-differences against two different exponential baselines. "More
suppressed in axenic" can arise from a higher axenic exponential baseline, not
from coculture relieving suppression. The causal reading is not separable from a
baseline difference.
**Recommendation:** Re-describe the contrast accurately everywhere it is called
"coculture vs axenic"; add the baseline-difference alternative as an explicit,
unresolved confound.
**Verification (2026-06-17):** SUPPORTED from files. The script's own reference
row label is `"starvation vs exp (all tp)"` (02_controls.py:88), confirming each
arm is starvation-vs-exponential; the difference-in-differences nature is real and
undisclosed in the narrative.

### Blocker · data-integrity — double-counted control reference rows
**Claim/location:** notebook.md 5b and Fig 3 — "HOT1A3 starvation coculture
177/183 = 0.97, axenic 137/147 = 0.93"; controls_motility_direction.csv.
**Problem:** `hot1a3_reference_rows()` (scripts/02_controls.py:88) sums
`significant_down` across all timepoint rows of the coculture motility file, which
contains day 60, day 89, AND a pooled "days 60+89" — so days 60/89 genes are
counted twice. 17+32+42+46+40 = 177 is a redundant per-row count, not distinct
significant genes. Same defect in axenic.
**Recommendation:** Deduplicate — drop either the pooled or the individual 60/89
rows before aggregating; report distinct-gene counts or per-timepoint.
**Verification (2026-06-17):** CONFIRMED EXACT. Re-derived down-by-timepoint:
{day 18: 17, day 31: 32, day 60: 42, day 89: 46, days 60+89: 40}, sum 177. The
pooled slice coexists with the individual day-60 and day-89 slices (94 genes each).

### Concern · science — "MIT1002 darkness" control is a genotype contrast
**Claim/location:** notebook.md 5b; paper.md — "MIT1002 darkness suppresses
motility too (diel 9/11 down)"; used to argue motility-down is general
stress/dormancy, not carbon-specific.
**Problem:** The "MIT1002 darkness (diel)" experiment is "Dark-tolerant co-culture
under 13:11 diel vs Parental co-culture under 13:11 diel" — an evolved strain vs
parental strain, both under the same diel light. The 9/11 is a genotype
comparison, not a darkness manipulation. Only the "extended darkness" row (6
genes, 4/6) is a genuine darkness contrast.
**Recommendation:** Relabel the diel row as a strain/genotype contrast; rest the
stress/dormancy argument on the extended-darkness row (n=6) alone.
**Verification (2026-06-17):** Not independently re-verified against the KG this
run — relies on the experiment naming the critic reported. Check experiment_name
via list_experiments before acting.

### Concern · science — partner-specificity rests on tiny counts
**Claim/location:** notebook.md; paper.md — "EZ55 +Prochlorococcus → up;
+Synechococcus → down … direction flips."
**Problem:** Significant-gene counts are tiny (controls_motility_direction.csv):
+Pro 7up/2down and 6up/1down; +Syn CC9311 2up/5down and 0up/2down; +Syn WH8102
0up/0down (no signal). down_fraction 1.0 is 2 genes; the second Synechococcus
strain gives zero significant motility genes, undercutting "Synechococcus → down"
as a genus pattern.
**Recommendation:** Report raw counts inline; soften to "a handful of genes, one
of two Synechococcus strains shows no signal"; flag WH8102's null.
**Verification (2026-06-17):** Not re-derived this run — check
controls_motility_direction.csv counts before acting.

### Concern · methodology — protein day-18 "significant" divergence driven by sub-threshold noise
**Claim/location:** motility_divergence_stats.csv; notebook.md (prot day 18 BH
p 0.0014, "significant"); Fig 1.
**Problem:** At protein day 18, all 55 axenic and 52/55 coculture motility genes
are individually not_significant (n_ax_down=0, n_ax_up=0). The "significant"
Wilcoxon divergence is driven by sub-threshold shifts.
**Recommendation:** Annotate that the protein day-18 divergence has zero
individually-significant motility genes in either arm.
**Verification (2026-06-17):** Not re-derived this run.

### Concern · science/methodology — time-trend tested on effectively 2 late points
**Claim/location:** notebook.md (Spearman rho 0.50, p 0.67, n=3); framing
preregistered "divergence grows over time."
**Problem:** The trend runs on n=3 RNA points because the axenic arm only has the
pooled 60+89; the preregistered "grows over time" prediction is essentially
untestable here. Honestly flagged as underpowered, but the structural reason
(axenic arm lacks separate 60/89) is not stated.
**Recommendation:** State that the axenic arm has no separate day-60/89, so the
trend is 3 points with the last a pool.
**Verification (2026-06-17):** Not re-derived this run.

### Note · methodology — column labels invite the wrong reading
Table headers "coc down/up | axenic down/up" read as coculture-vs-axenic; relabel
to make clear each count is starvation-vs-exponential within that arm.

### Note (clean spot-check)
notebook.md "axenic days 60+89: flagellar −11.0, chemotaxis −9.1" — verified
accurate against pathway_trajectories.csv (RNA axenic).

---

## Verdict (critic)

Three Blockers. Most important: the "motility down in both arms" claim — protein
axenic flagellar assembly is significantly UP at day 31, narrated as "negative
throughout." Coupled with Blocker 2 (contrast is starvation-vs-exponential per
arm → "coculture relieves suppression" is confounded) and Blocker 3 (177/137 are
double-counts). Methodology-compliance dimension otherwise reasonable: locus tags
present, computations in scripts, RNA/protein kept separate, KG release ok, no
truncation. Data-integrity and science dimensions are where the fixes are needed;
both controls (darkness, partner) are over-read relative to what the KG contrasts
actually are.

---

## Disposition

This was an evaluation run on an already-committed step, not the step's original
decide phase. No fixes applied yet. The three Blockers are real (two re-derived
exactly from the data; one supported by the script's own labels) and warrant a
redo of step 5 per the reopen/redo path in step-protocol.md — **pending
researcher decision**. Concerns 4–6 to be re-verified against the KG/CSV at redo
time.
