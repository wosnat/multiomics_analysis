"""E1 time courses (descriptive): heatmaps of log2FC and rank percentile, gene x slice, for the MED4 gene sets, plus
system-median percentile lines over coculture days. No pooled slices; significance = stored expression_status.
Outputs: data/explore/e1_gene_slice_long.csv, e1_system_median_percentile.csv; figures e1_protein_heatmap,
e1_rna_heatmap, e1_median_percentile_lines.
Usage (repo root): .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e1_timecourses.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"


def long_table(L, G, slices, omics):
    rows = []
    for short, tp in slices:
        x = ex.slice_values(L["de"], short, tp)
        for r in G.itertuples():
            v = x.loc[r.locus_tag] if r.locus_tag in x.index else None
            rows.append({"omics": omics, "slice": ex.SLICE_LABEL[(short, tp)], "short_name": short, "timepoint": tp,
                         "group": r.group, "system_id": r.system_id, "locus_tag": r.locus_tag,
                         "gene_name": L["names"].get(r.locus_tag, ""),
                         "log2fc": None if v is None else v.log2fc, "rank_percentile": None if v is None else v.rank_percentile,
                         "expression_status": "not detected" if v is None else v.expression_status})
    return pd.DataFrame(rows)


def heatmap(T, slices, omics, name):
    labels = [ex.SLICE_LABEL[s] for s in slices]
    G = T.drop_duplicates(["group", "locus_tag"])[["group", "locus_tag", "gene_name"]].reset_index(drop=True)
    # y positions with a gap between groups
    ys, y, prev = [], 0.0, None
    for g in G.group:
        if prev is not None and g != prev:
            y += 0.8
        ys.append(y)
        y += 1
        prev = g
    G["y"] = ys
    h = 0.13 * y + 2.5
    fig, axes = plt.subplots(1, 2, figsize=(13, h), sharey=True)
    norm = figs.TwoSlopeNorm(vmin=-4, vcenter=0, vmax=4)
    for ax, (val, cmap, nrm, ttl) in zip(axes, (("log2fc", figs.DIVERGING, norm, "log2FC (clipped at ±4)"),
                                                 ("rank_percentile", figs.PCT, None, "rank percentile"))):
        for j, lab in enumerate(labels):
            sub = T[T.slice == lab].set_index(["group", "locus_tag"])
            for r in G.itertuples():
                key = (r.group, r.locus_tag)
                v = sub[val].get(key, np.nan) if key in sub.index else np.nan
                st = sub.expression_status.get(key, "not detected") if key in sub.index else "not detected"
                if pd.isna(v):
                    ax.add_patch(plt.Rectangle((j, r.y), 0.96, 0.92, facecolor=F.SURF, edgecolor=F.GRID, linewidth=0.4,
                                               hatch="///"))
                    continue
                vv = max(-4, min(4, v)) if val == "log2fc" else v
                col = cmap(nrm(vv)) if nrm else cmap(vv)
                ax.add_patch(plt.Rectangle((j, r.y), 0.96, 0.92, facecolor=col, edgecolor=F.SURF, linewidth=0.3))
                if st in (ex.SIG_UP, ex.SIG_DOWN):
                    ax.plot(j + 0.48, r.y + 0.46, marker="o" if st == ex.SIG_UP else "v", markersize=2.6,
                            color=figs.marker_color(vv, val == "rank_percentile"), linestyle="")
        ax.set_xlim(0, len(labels))
        ax.set_ylim(y, -0.5)
        ax.set_xticks([j + 0.48 for j in range(len(labels))], labels, rotation=45, ha="left", fontsize=7.5)
        ax.xaxis.tick_top()
        figs.block_divider(ax, sum(lb.startswith("ax") for lb in labels), len(labels), offset_pts=44)
        ax.set_title(ttl, loc="left", fontsize=9, pad=62)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
    figs.add_cbar(fig, axes[0], figs.DIVERGING, norm, "log2FC (clipped at ±4)", pad=0.25 / h * 4)
    figs.add_cbar(fig, axes[1], figs.PCT, plt.Normalize(0, 1), "rank percentile, 0–1", pad=0.25 / h * 4)
    axes[0].set_yticks(G.y + 0.46, [f"{n or lt} {lt if n else ''}".strip() for n, lt in zip(G.gene_name, G.locus_tag)],
                       fontsize=5.8)
    first = G.groupby("group").y.min()
    for g, yy in first.items():
        axes[0].text(-0.08, yy - 0.15, g, transform=axes[0].get_yaxis_transform(), ha="right", va="bottom",
                     fontsize=6.3, fontweight="bold", color=F.TEXT2)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    handles = [Line2D([], [], marker="o", color=F.TEXT, linestyle="", markersize=4, label="significant up (stored)"),
               Line2D([], [], marker="v", color=F.TEXT, linestyle="", markersize=4, label="significant down (stored)"),
               Patch(facecolor=F.SURF, edgecolor=F.GRID, hatch="///", label="not detected")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.6, 0.0), fontsize=8)
    # (colorbars sit just under each panel; the marker legend is below them)
    figs.head(fig, f"MED4 gene sets over time, {omics}",
              f"Source: analysis/data/de_long.csv.gz ({omics}; no pooled slices) + methods v1.6.1 systems; "
              f"data/explore/e1_gene_slice_long.csv. Left: log2FC, orange up / blue down; right: rank percentile.")
    fig.subplots_adjust(left=0.33, right=0.99, top=1 - 2.4 / h, bottom=1.9 / h, wspace=0.05)
    return figs.save(fig, name)


def lines(M):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    series = ["amt1", "urt", "cyn", "dpp", "starvation markers", "non-N systems"]
    for ax, omics in zip(axes, ("protein", "RNA")):
        x = M[M.omics == omics]
        for i, s in enumerate(series):
            y = x[x.series == s].sort_values("day")
            ls = "--" if s in ("starvation markers", "non-N systems") else "-"
            ax.plot(y.day, y.median_percentile, marker="o", color=F.CAT[i], linewidth=2, linestyle=ls, markersize=5,
                    label=s)
            ax.text(y.day.iloc[-1] + 1.5, y.median_percentile.iloc[-1], s, fontsize=7.5, color=F.TEXT, va="center")
        ax.set_xticks([18, 31, 60, 89], ["d18", "d31", "d60", "d89"])
        ax.set_xlim(14, 108)
        ax.set_ylim(0, 1.02)
        ax.set_title(f"coculture, {omics}", loc="left", fontsize=10)
        ax.grid(axis="y", color=F.GRID, linewidth=0.6)
        ax.spines["left"].set_color(F.GRID)
        ax.spines["bottom"].set_color(F.GRID)
        ax.tick_params(length=0)
    axes[0].set_ylabel("median rank percentile")
    axes[0].legend(loc="lower left", fontsize=7.5, ncol=2)
    figs.head(fig, "System-median rank percentile over coculture days",
              "Source: data/explore/e1_system_median_percentile.csv (median over detected subunits / genes; non-N = all "
              "members of pst, phn, sul1, sul3, fut/idiA2, mnt, lraI, sbtA pooled)")
    fig.subplots_adjust(left=0.08, right=0.97, top=0.82, bottom=0.12, wspace=0.08)
    return figs.save(fig, "e1_median_percentile_lines")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    G = ex.gene_sets(L)
    P = long_table(L, G, ex.PROT_SLICES, "protein")
    R = long_table(L, G, ex.RNA_SLICES, "RNA")
    T = pd.concat([P, R], ignore_index=True)
    T.assign(markers_set=ex.MARKERS_NOTE).to_csv(OUT / "e1_gene_slice_long.csv", index=False)
    rows = []
    sets = {**{k: L["mem"][s] for k, s in ex.DEDICATED.items()}, "starvation markers": list(ex.MARKERS),
            "non-N systems": sorted({m for s in ex.NON_N.values() for m in L["mem"][s]})}
    for omics, short in (("protein", "anchor_cocult_protein"), ("RNA", "anchor_cocult_rna")):
        for d in (18, 31, 60, 89):
            x = ex.slice_values(L["de"], short, f"day {d}")
            for k, loci in sets.items():
                v = x.reindex(loci).rank_percentile.dropna()
                rows.append({"omics": omics, "day": d, "series": k, "n_detected": int(len(v)),
                             "median_percentile": float(v.median()) if len(v) else np.nan})
    M = pd.DataFrame(rows)
    M.assign(markers_set=ex.MARKERS_NOTE).to_csv(OUT / "e1_system_median_percentile.csv", index=False)
    files = heatmap(P, ex.PROT_SLICES, "protein", "e1_protein_heatmap") + heatmap(R, ex.RNA_SLICES, "RNA", "e1_rna_heatmap") + lines(M)
    for f in files:
        print(f.name)
    print(M.pivot_table(index=["omics", "series"], columns="day", values="median_percentile").round(3).to_string())


if __name__ == "__main__":
    main()
