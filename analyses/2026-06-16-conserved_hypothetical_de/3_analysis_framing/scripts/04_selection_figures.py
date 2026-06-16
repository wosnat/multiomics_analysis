"""Step 3 — figures describing the selection.

Four panels, each from a frozen step-2/step-3 CSV:
  fig1_selection_funnel.png            — OG funnel to the candidate set
  fig2_conservation_distribution.png   — strain-coverage of hypothetical OGs
  fig3_breadth_axis_experiments.png    — pooled experiments per treatment type
  fig4_controls_breadth_vs_prominence.png — control genes on the two metric axes

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/3_analysis_framing/scripts/04_selection_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

STEP = Path(__file__).resolve().parents[1]
ROOT = STEP.parent
DATA = STEP / "data"
FIG = STEP / "figures"
FIG.mkdir(parents=True, exist_ok=True)

BROAD_MIN, CORE_MIN, N_STRAINS = 9, 14, 17


def savefig(fig, stem: str, **kw) -> None:
    """Write both PNG (300 DPI) and publication SVG."""
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{stem}.{ext}", dpi=300, **kw)
    plt.close(fig)


def fig_funnel() -> None:
    stages = ["cyanorak OGs\n(Prochlorococcus)", "hypothetical\n(≥80% AQ≤1)",
              "broad\n(≥9/17 strains)", "core\n(≥14/17)", "all 17 strains"]
    vals = [5732, 2787, 245, 97, 50]
    colors = ["#b0bec5", "#90a4ae", "#5c9ccc", "#3a7ca5", "#16425b"]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(range(len(stages))[::-1], vals, color=colors)
    ax.set_yticks(range(len(stages))[::-1])
    ax.set_yticklabels(stages)
    ax.set_xlabel("number of ortholog groups")
    ax.set_title("Selection funnel: conserved hypothetical ortholog families")
    for b, v in zip(bars, vals):
        ax.text(v + 60, b.get_y() + b.get_height() / 2, f"{v:,}",
                va="center", fontsize=9)
    ax.set_xlim(0, 6200)
    fig.tight_layout()
    savefig(fig, "fig1_selection_funnel")


def fig_conservation() -> None:
    df = pd.read_csv(DATA.parent.parent / "2_kg_selection" / "data"
                     / "og_conservation_landscape.csv")
    hypo = df[df["frac_hypo"] >= 0.8]
    counts = (hypo.groupby("proc_strains").size()
              .reindex(range(1, N_STRAINS + 1), fill_value=0))
    fig, ax = plt.subplots(figsize=(7.5, 4))
    colors = ["#16425b" if k >= CORE_MIN else "#5c9ccc" if k >= BROAD_MIN
              else "#b0bec5" for k in counts.index]
    ax.bar(counts.index, counts.values, color=colors)
    ax.axvline(BROAD_MIN - 0.5, ls="--", color="#5c9ccc", lw=1)
    ax.axvline(CORE_MIN - 0.5, ls="--", color="#16425b", lw=1)
    ax.text(BROAD_MIN, counts.max() * 0.9, "broad ≥9", color="#5c9ccc", fontsize=9)
    ax.text(CORE_MIN, counts.max() * 0.78, "core ≥14", color="#16425b", fontsize=9)
    ax.set_xlabel("number of Prochlorococcus strains (of 17) the family is present in")
    ax.set_ylabel("number of hypothetical OGs")
    ax.set_title("Conservation of hypothetical ortholog families (≥80% members AQ≤1)")
    ax.set_xticks(range(1, N_STRAINS + 1))
    fig.tight_layout()
    savefig(fig, "fig2_conservation_distribution")


def fig_breadth_axis() -> None:
    inv = pd.read_csv(DATA / "treatment_type_inventory.csv").sort_values(
        "n_experiments", ascending=True)
    other = inv["n_experiments"] - inv["n_all_detected"]
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.barh(inv["treatment_type"], inv["n_all_detected"], color="#3a7ca5",
            label="all_detected_genes (real tested denominator)")
    ax.barh(inv["treatment_type"], other, left=inv["n_all_detected"],
            color="#cbb09c", label="other scopes (significant-only etc.)")
    ax.set_xlabel("number of pooled experiments")
    ax.set_title("Breadth axis: 13 treatment types in the pooled gene-DE set (n=74)")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    savefig(fig, "fig3_breadth_axis_experiments")


def fig_controls() -> None:
    df = pd.read_csv(DATA / "controls_validation.csv")
    df["y"] = df["max_abs_log2fc"].fillna(0.0)
    role_color = {"positive_broad": "#16425b", "positive_moderate": "#3a7ca5",
                  "prominent_not_broad": "#d1495b", "negative_narrow": "#9e9e9e"}
    fig, ax = plt.subplots(figsize=(7, 5))
    for _, r in df.iterrows():
        ax.scatter(r["breadth_n_treatments"], r["y"],
                   s=60 + 22 * (r["n_significant_timepoints"] or 0),
                   color=role_color.get(r["role"], "#777"),
                   edgecolor="black", lw=0.6, zorder=3)
        ax.annotate(f"{r['gene']}", (r["breadth_n_treatments"], r["y"]),
                    textcoords="offset points", xytext=(7, 4), fontsize=9)
    handles = [plt.Line2D([0], [0], marker="o", ls="", mfc=c, mec="black",
                          label=role.replace("_", " "))
               for role, c in role_color.items()]
    ax.legend(handles=handles, fontsize=8, loc="upper left", title="control role")
    ax.set_xlabel("breadth (distinct treatment types responded)")
    ax.set_ylabel("prominence (max |log2 fold change|)")
    ax.set_title("Control validation — breadth and prominence are independent axes\n"
                 "(marker size ∝ # significant datapoints)")
    ax.set_xlim(-0.5, 6)
    ax.margins(y=0.15)
    fig.tight_layout()
    savefig(fig, "fig4_controls_breadth_vs_prominence")


def main() -> None:
    fig_funnel()
    fig_conservation()
    fig_breadth_axis()
    fig_controls()
    print("[out] wrote 4 figures to figures/:")
    for p in sorted(FIG.glob("*.png")):
        print(f"  {p.name}")


if __name__ == "__main__":
    main()
