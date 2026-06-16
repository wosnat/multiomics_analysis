"""Step 5 — shortlist of interesting hypotheticals + backdrop figures.

Shortlist (from the 245 hypothetical families): a family is a headline hit if BROAD
or PROMINENT (breadth and prominence are independent — see controls):
  is_broad     = breadth >= 6
  is_prominent = best_rank <= 3  OR  max_abs_log2fc >= 8  OR  n_significant_datapoints >= 30

Figures use the full conserved backdrop (1,710 families) so the hypotheticals are seen
against characterized families:
  fig5  breadth: hypothetical vs characterized (are dark genes as responsive?)
  fig6  breadth vs prominence — colour = gene_category, marker = direction
        (^ up / v down / o mixed), hypotheticals highlighted, controls overlaid
  fig7  direction-by-treatment heatmap, top hypothetical families

Inputs:  data/conserved_og_scores.csv (step 5);
         ../4_methods/data/qc_controls_via_metric.csv (controls overlay)
Outputs: data/shortlist.csv; figures/fig5,6,7 ; data/02_shortlist_and_figures.log

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/5_analyze/scripts/02_shortlist_and_figures.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

STEP = Path(__file__).resolve().parents[1]
ROOT = STEP.parent
DATA = STEP / "data"
FIG = STEP / "figures"
FIG.mkdir(parents=True, exist_ok=True)

def savefig(fig, stem: str, **kw) -> None:
    """Write both PNG (300 DPI) and publication SVG."""
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{stem}.{ext}", dpi=300, **kw)
    plt.close(fig)


BROAD_MIN, RANK_MAX, FC_MIN, NSIG_MIN = 6, 3, 8.0, 30
DIR_MARKER = {"up": "^", "down": "v", "mixed": "o"}
TREATMENTS = ["nitrogen", "carbon", "light", "phosphorus", "iron", "coculture",
              "viral", "plastic", "darkness", "salt", "diel", "growth_phase",
              "temperature"]


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA / "conserved_og_scores.csv")
    df["max_abs_log2fc"] = pd.to_numeric(df["max_abs_log2fc"], errors="coerce")
    df["best_rank"] = pd.to_numeric(df["best_rank"], errors="coerce")
    return df


def add_shortlist(df: pd.DataFrame) -> pd.DataFrame:
    h = df["is_hypothetical"]
    df["is_broad"] = df["breadth"] >= BROAD_MIN
    df["is_prominent"] = ((df["best_rank"] <= RANK_MAX)
                          | (df["max_abs_log2fc"] >= FC_MIN)
                          | (df["n_significant_datapoints"] >= NSIG_MIN))
    df["is_highlight"] = h & (df["is_broad"] | df["is_prominent"])
    return df


def fig_breadth(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    bins = np.arange(-0.5, df["breadth"].max() + 1.5)
    for is_h, lbl, c in [(False, "characterized (n=1465)", "#b0bec5"),
                         (True, "hypothetical (n=245)", "#d1495b")]:
        sub = df[df["is_hypothetical"] == is_h]["breadth"]
        ax.hist(sub, bins=bins, density=True, alpha=0.6, color=c, label=lbl)
    ax.axvline(BROAD_MIN, ls="--", color="#333", lw=1)
    ax.set_xlabel("breadth (distinct treatment types responded, of 13)")
    ax.set_ylabel("fraction of families (density)")
    ax.set_title("Are conserved hypotheticals as broadly responsive as known genes?")
    ax.legend()
    ax.set_xticks(range(0, int(df["breadth"].max()) + 1))
    fig.tight_layout()
    savefig(fig, "fig5_breadth_hypo_vs_characterized")


def fig_scatter(df: pd.DataFrame) -> None:
    cats = sorted(df["dominant_category"].dropna().unique())
    palette = plt.cm.tab20(np.linspace(0, 1, len(cats)))
    cat_color = dict(zip(cats, palette))
    rng = np.random.default_rng(0)

    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    d = df.copy()
    d["y"] = d["max_abs_log2fc"].fillna(0).clip(upper=12)
    d["x"] = d["breadth"] + rng.uniform(-0.18, 0.18, len(d))
    for direction, marker in DIR_MARKER.items():
        sub = d[d["direction"] == direction]
        char = sub[~sub["is_hypothetical"]]
        hypo = sub[sub["is_hypothetical"]]
        ax.scatter(char["x"], char["y"], marker=marker, s=16, alpha=0.45,
                   c=[cat_color[c] for c in char["dominant_category"]],
                   edgecolor="none", zorder=2)
        ax.scatter(hypo["x"], hypo["y"], marker=marker, s=70,
                   c=[cat_color.get(c, "#999") for c in hypo["dominant_category"]],
                   edgecolor="black", lw=0.8, zorder=4)
    # controls overlay
    ctrl = pd.read_csv(ROOT / "4_methods" / "data" / "qc_controls_via_metric.csv")
    ax.scatter(ctrl["breadth"], ctrl["max_abs_log2fc_metric"].fillna(0),
               marker="*", s=240, color="gold", edgecolor="black", lw=0.8,
               zorder=5, label="characterized controls")
    for _, r in ctrl.iterrows():
        ax.annotate(r["gene"], (r["breadth"], (r["max_abs_log2fc_metric"] or 0)),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)

    cat_handles = [plt.Line2D([0], [0], marker="s", ls="", mfc=cat_color[c],
                   mec="none", label=c) for c in cats]
    dir_handles = [plt.Line2D([0], [0], marker=m, ls="", mfc="#555", mec="black",
                   label=f"{d}") for d, m in DIR_MARKER.items()]
    leg1 = ax.legend(handles=cat_handles, title="gene_category (colour)",
                     fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0))
    ax.add_artist(leg1)
    ax.legend(handles=dir_handles, title="direction (marker)", fontsize=8,
              loc="lower left", bbox_to_anchor=(1.01, 0.0))
    ax.set_xlabel("breadth (distinct treatment types responded, of 13)")
    ax.set_ylabel("prominence (max |log2 fold change|, clipped at 12)")
    ax.set_title("Conserved families: breadth vs prominence\n"
                 "colour = category, marker = direction; hypotheticals outlined (large)")
    fig.tight_layout()
    savefig(fig, "fig6_backdrop_breadth_vs_prominence", bbox_inches="tight")


def fig_direction_heatmap(df: pd.DataFrame) -> None:
    """Clustered heatmap of direction-by-treatment for the shortlist (85 families).

    Rows (families) and columns (treatments) are hierarchically clustered so that
    families with similar response signatures group together. Encoding for both
    colour and clustering: up=+1, down=-1, mixed=0, no-significant-response=NaN
    (filled with 0 for the linkage, masked white in the display).
    """
    hyp = df[df["is_highlight"]].copy()
    code = {"up": 1, "down": -1, "mixed": 0}
    rows = {}
    for _, r in hyp.iterrows():
        dbt = r["direction_by_treatment"]
        dbt = ast.literal_eval(dbt) if isinstance(dbt, str) and dbt.startswith("{") else {}
        rows[r["og_id"].replace("cyanorak:", "")] = {
            t: code.get(dbt.get(t)) for t in TREATMENTS if dbt.get(t) in code}
    mat = pd.DataFrame(rows).T.reindex(columns=TREATMENTS)
    mat = mat.dropna(axis=1, how="all")  # drop treatments no family responds to
    mask = mat.isna()

    cmap = matplotlib.colors.ListedColormap(["#3a7ca5", "#cccccc", "#d1495b"])  # -1 down=blue, 0 mixed, +1 up=red
    g = sns.clustermap(
        mat.fillna(0), mask=mask, cmap=cmap, vmin=-1, vmax=1,
        row_cluster=True, col_cluster=True, metric="euclidean", method="average",
        linewidths=0.4, linecolor="white", figsize=(9, 14),
        cbar_pos=None, dendrogram_ratio=(0.12, 0.06),
        xticklabels=True, yticklabels=True)
    g.ax_heatmap.set_facecolor("white")
    g.ax_heatmap.set_xlabel("treatment type")
    g.ax_heatmap.set_ylabel("hypothetical family (cyanorak OG)")
    g.ax_heatmap.tick_params(axis="y", labelsize=6)
    g.ax_heatmap.tick_params(axis="x", labelsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in
               ["#d1495b", "#3a7ca5", "#cccccc", "white"]]
    g.ax_heatmap.legend(handles, ["up", "down", "mixed", "no sig. response"],
                        loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8,
                        frameon=True, edgecolor="#999")
    g.figure.suptitle("Direction by treatment — shortlist of interesting hypothetical "
                      "families\n(clustered; red=up, blue=down, grey=mixed)",
                      y=1.01, fontsize=11)
    for ext in ("png", "svg"):
        g.savefig(FIG / f"fig7_direction_clustermap_shortlist.{ext}", dpi=300,
                  bbox_inches="tight")
    plt.close(g.figure)


def main() -> None:
    df = add_shortlist(load())
    df.to_csv(DATA / "conserved_og_scores.csv", index=False)  # re-save with flags
    hl = df[df["is_highlight"]].sort_values(
        ["breadth", "n_significant_datapoints"], ascending=False)
    keep = ["og_id", "tier", "proc_strains", "dominant_category", "breadth",
            "n_significant_datapoints", "best_rank", "max_abs_log2fc", "direction",
            "is_broad", "is_prominent", "consensus_product"]
    hl[keep].to_csv(DATA / "shortlist.csv", index=False)

    h = df[df["is_hypothetical"]]
    print(f"[shortlist] {len(hl)} headline hypothetical families of {len(h)}")
    print(f"  broad (>=6): {int((h['is_broad']).sum())} | "
          f"prominent: {int((h['is_prominent']).sum())} | "
          f"both: {int((h['is_broad'] & h['is_prominent']).sum())}")
    print("\n[top 12 shortlist]")
    with pd.option_context("display.width", 200, "display.max_columns", None):
        t = hl[keep].head(12).copy()
        t["consensus_product"] = t["consensus_product"].str.slice(0, 32)
        print(t.to_string(index=False))

    fig_breadth(df)
    fig_scatter(df)
    fig_direction_heatmap(df)
    print("\n[out] figures:", ", ".join(p.name for p in sorted(FIG.glob("*.png"))))


if __name__ == "__main__":
    main()
