"""Step 6 — evaluation: coverage confound + conservation-by-tier.

Two linked checks on the shortlist's robustness:

(1) COVERAGE CONFOUND. Breadth could be inflated by how many conditions a family
    was MEASURED in (more strains tested -> more chances to be significant). We pull
    tested coverage (differential_expression_by_ortholog, significant_only=False) and
    test whether breadth just tracks n_treatments_tested, and whether conservation
    (proc_strains) is itself mostly a coverage proxy.

(2) CONSERVATION BY TIER. Using our two tiers (core >=14/17, broad 9-13), do the
    more-conserved core families respond more broadly/prominently — and does any
    difference survive normalizing by coverage (response_rate = breadth /
    n_treatments_tested)? Also check OG size (proc_members, paralog count).

Scope: the 245 hypothetical candidates (our families); the characterized backdrop is
used only for the breadth comparison already in step 5.

Inputs:  5_analyze/data/conserved_og_scores.csv; 3_analysis_framing/data/pooled_experiments.csv
Outputs: data/coverage_confound.csv, data/conservation_tier_summary.csv,
         figures/fig8_breadth_vs_coverage.(png|svg),
         figures/fig9_conservation_by_tier.(png|svg), data/01_*.log

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/6_evaluate/scripts/01_coverage_and_conservation.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from multiomics_explorer import differential_expression_by_ortholog

STEP = Path(__file__).resolve().parents[1]
ROOT = STEP.parent
DATA = STEP / "data"
FIG = STEP / "figures"
DATA.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

SCORES = pd.read_csv(ROOT / "5_analyze" / "data" / "conserved_og_scores.csv")
POOLED = pd.read_csv(ROOT / "3_analysis_framing" / "data" / "pooled_experiments.csv")
POOLED_IDS = POOLED["experiment_id"].tolist()


def savefig(fig, stem, **kw):
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{stem}.{ext}", dpi=300, **kw)
    plt.close(fig)


def tested_coverage(og_ids: list[str]) -> pd.DataFrame:
    """n distinct treatment types each family was MEASURED in (sig or not)."""
    r = differential_expression_by_ortholog(
        group_ids=og_ids, organisms=["Prochlorococcus"],
        experiment_ids=POOLED_IDS, significant_only=False, limit=None)
    rows = pd.DataFrame(r["results"])
    rows = rows[rows["genes_with_expression"] > 0].copy()
    rows["treatment_type"] = rows["treatment_type"].apply(
        lambda t: t[0] if isinstance(t, list) and t else t)
    cov = (rows.groupby("group_id")["treatment_type"].nunique()
           .rename("n_treatments_tested").reset_index()
           .rename(columns={"group_id": "og_id"}))
    return cov


def main() -> None:
    hyp = SCORES[SCORES["is_hypothetical"]].copy()
    cov = tested_coverage(hyp["og_id"].tolist())
    h = hyp.merge(cov, on="og_id", how="left")
    h["n_treatments_tested"] = h["n_treatments_tested"].fillna(0).astype(int)
    h["response_rate"] = np.where(h["n_treatments_tested"] > 0,
                                  h["breadth"] / h["n_treatments_tested"], np.nan)
    h.to_csv(DATA / "coverage_confound.csv", index=False)

    # (1) confound correlations
    def corr(a, b):
        m = h[[a, b]].dropna()
        return m[a].corr(m[b]) if len(m) > 2 else float("nan")
    print("[coverage confound] Pearson r")
    print(f"  breadth ~ n_treatments_tested : {corr('breadth','n_treatments_tested'):.2f}")
    print(f"  proc_strains ~ n_treatments_tested (conservation IS coverage): "
          f"{corr('proc_strains','n_treatments_tested'):.2f}")
    print(f"  breadth ~ proc_strains : {corr('breadth','proc_strains'):.2f}")
    print(f"  response_rate ~ proc_strains (conservation beyond coverage?): "
          f"{corr('response_rate','proc_strains'):.2f}")

    # (2) tier summary (core vs broad) within hypotheticals
    rows = []
    for tier in ("core", "broad"):
        s = h[h["tier"] == tier]
        rows.append(dict(
            tier=tier, n=len(s),
            mean_breadth=round(s["breadth"].mean(), 2),
            median_breadth=int(s["breadth"].median()),
            mean_treatments_tested=round(s["n_treatments_tested"].mean(), 2),
            mean_response_rate=round(s["response_rate"].mean(), 3),
            mean_max_abs_log2fc=round(s["max_abs_log2fc"].mean(), 2),
            mean_proc_members=round(s["proc_members"].mean(), 1),
            n_shortlist=int(s["is_highlight"].sum())))
    tier_sum = pd.DataFrame(rows)
    tier_sum.to_csv(DATA / "conservation_tier_summary.csv", index=False)
    print("\n[conservation by tier — hypotheticals]")
    print(tier_sum.to_string(index=False))

    # OG size (paralog count) relationship
    print(f"\n[OG size] breadth ~ proc_members r = {corr('breadth','proc_members'):.2f}; "
          f"max|log2FC| ~ proc_members r = {corr('max_abs_log2fc','proc_members'):.2f}")

    # ---- fig8: breadth vs coverage, and conservation vs coverage ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    rng = np.random.default_rng(0)
    jit = lambda v: v + rng.uniform(-0.18, 0.18, len(v))
    for ax, xcol, xlab in [(axes[0], "n_treatments_tested", "treatments tested (coverage)"),
                           (axes[1], "proc_strains", "strains present (conservation)")]:
        for tier, c in [("core", "#16425b"), ("broad", "#5c9ccc")]:
            s = h[h["tier"] == tier]
            ax.scatter(jit(s[xcol]), jit(s["breadth"]), s=22, alpha=0.6,
                       color=c, label=f"{tier} (n={len(s)})")
        ax.plot([0, 13], [0, 13], ls=":", color="#999", lw=1)
        ax.set_xlabel(xlab)
        ax.set_ylabel("breadth (treatments responded)")
        ax.legend(fontsize=8, title="tier")
    axes[0].set_title(f"Breadth vs coverage (r={corr('breadth','n_treatments_tested'):.2f})")
    axes[1].set_title(f"Breadth vs conservation (r={corr('breadth','proc_strains'):.2f})")
    fig.suptitle("Coverage confound: breadth tracks how broadly a family was measured",
                 y=1.02)
    fig.tight_layout()
    savefig(fig, "fig8_breadth_vs_coverage", bbox_inches="tight")

    # ---- fig9: tier comparison (breadth + response_rate) ----
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
    for ax, col, lab in [(axes[0], "breadth", "breadth (treatments responded)"),
                         (axes[1], "response_rate", "response rate (breadth / tested)")]:
        data = [h[h["tier"] == t][col].dropna() for t in ("broad", "core")]
        bp = ax.boxplot(data, tick_labels=["broad\n(9-13)", "core\n(14-17)"],
                        patch_artist=True, widths=0.6)
        for patch, c in zip(bp["boxes"], ["#5c9ccc", "#16425b"]):
            patch.set_facecolor(c); patch.set_alpha(0.7)
        ax.set_ylabel(lab)
    axes[0].set_title("Response breadth by conservation tier")
    axes[1].set_title("Coverage-normalized response by tier")
    fig.suptitle("Do more-conserved (core) hypotheticals respond more?", y=1.02)
    fig.tight_layout()
    savefig(fig, "fig9_conservation_by_tier", bbox_inches="tight")

    print("\n[out] figures: fig8_breadth_vs_coverage, fig9_conservation_by_tier (png+svg)")


if __name__ == "__main__":
    main()
