"""Figure helpers for the analysis milestone: the methods f1 style (imported, not copied), saving to analysis/figures/."""
import sys
from pathlib import Path

ANALYSIS = Path(__file__).resolve().parent
sys.path.insert(0, str(ANALYSIS.parent / "methods" / "scripts"))
import f1_methods_figures as F  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402,F401

plt = F.plt
FIG = ANALYSIS / "figures"
# researcher request 2026-10-11: orange = up (positive), blue = down (negative), neutral at 0
DIVERGING = LinearSegmentedColormap.from_list("div", ["#2a78d6", "#f0efec", "#eb6834"])   # down (blue) - 0 - up (orange)
SEQ = LinearSegmentedColormap.from_list("seq", ["#f0efec", "#86b6ef", "#1c5cab"])          # percentile 0 -> 1 (blue)
# rank-percentile heatmaps (researcher request 2026-10-11): single-hue purple, distinct from the orange/blue diverging ends
PCT = LinearSegmentedColormap.from_list("pct", ["#f0efec", "#a99bd6", "#4a3aa7", "#2a1d6e"])
PCT_DARK = 0.70   # percentile above which markers are drawn white


def marker_color(val, is_pct):
    return F.SURF if (is_pct and val == val and val >= PCT_DARK) else F.TEXT


def block_divider(ax, n_left, n_total, left="axenic", right="coculture", offset_pts=46):
    """Thick divider between the first n_left columns and the rest, with a block header over each side."""
    ax.axvline(n_left - 0.02, color=F.TEXT, linewidth=2.2, zorder=5)
    tr = ax.get_xaxis_transform()
    for x0, x1, lab in ((0, n_left, left), (n_left, n_total, right)):
        if x1 > x0:
            ax.annotate(lab, xy=((x0 + x1) / 2, 1.0), xycoords=tr, xytext=(0, offset_pts), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=F.TEXT2, annotation_clip=False)


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=300)
    plt.close(fig)
    return [FIG / f"{name}.png", FIG / f"{name}.svg"]


head = F.head


def add_cbar(fig, ax, cmap, norm, label, where="bottom", size=0.012, pad=0.035):
    """Horizontal colorbar under (or above) one heatmap panel, labelled with the quantity and its clipping."""
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    y = -pad - size if where == "bottom" else 1 + pad
    cax = ax.inset_axes([0.0, y, 1.0, size])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_label(label, fontsize=8)
    cb.ax.tick_params(labelsize=7, length=2)
    cb.outline.set_visible(False)
    return cb


# --------------------------------------------------------------------------- calibration bar panels (e6b, e8a)
NON_N_BAND = "non-N reference transporters"
N_BAND = "nitrogen import & assimilation"


def calibration_bars(fig, ax, B, conds, headers, is_non_n, sig_up="significant_up", sig_down="significant_down",
                     colors=None, hatches=("", "//", "..")):
    """Grouped percentile bars per gene for several conditions.

    B: rows in display order with columns group, locus_tag, gene_name, and for each condition key k in conds:
       k_pct, k_status. conds: list of (key, legend label). headers: group -> header text ("short: what (class)").
    is_non_n: function(group) -> bool (decides the band). Group headers are placed on stacked levels so that no two
    headers overlap (greedy, measured with the renderer); a bracket under each header spans its group.
    """
    import numpy as np
    colors = colors or [F.CAT[0], F.CAT[1], F.CAT[2]]
    n = len(conds)
    w = 0.8 / n
    xs = np.arange(len(B))
    for i, (k, lab) in enumerate(conds):
        off = (i - (n - 1) / 2) * w
        ax.bar(xs + off, B[f"{k}_pct"].fillna(0), width=w * 0.95, color=colors[i], hatch=hatches[i], edgecolor=F.SURF,
               linewidth=0.8, label=lab)
        for x, (v, st) in enumerate(zip(B[f"{k}_pct"], B[f"{k}_status"])):
            if st in (sig_up, sig_down):
                ax.text(x + off, (0 if v != v else v) + 0.015, "●" if st == sig_up else "▼", ha="center", va="bottom",
                        fontsize=6, color=F.TEXT)
            elif st == "not detected":
                ax.text(x + off, 0.02, "n.d.", ha="center", va="bottom", fontsize=5, color=F.TEXT2, rotation=90)
    ax.axhline(0.5, color=F.TEXT2, linewidth=0.7, linestyle="--")
    ax.axhline(0.9, color=F.TEXT2, linewidth=0.7, linestyle=":")
    ax.set_xticks(xs, [g if isinstance(g, str) and g else lt for g, lt in zip(B.gene_name, B.locus_tag)], rotation=90,
                  fontsize=6.8)
    ax.set_xlim(-0.6, len(B) - 0.4)
    ax.set_ylim(0, 1.04)
    ax.set_ylabel("rank percentile within the table")
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color(F.GRID)
    ax.tick_params(length=0)
    # group spans
    spans, prev = [], None
    for i, g in enumerate(B.group):
        if g != prev:
            spans.append([g, i, i])
        else:
            spans[-1][2] = i
        prev = g
    for g, a, b in spans[1:]:
        ax.axvline(a - 0.5, color=F.GRID, linewidth=0.7)
    first_non = next((a for g, a, b in spans if is_non_n(g)), None)
    if first_non is not None:
        ax.axvline(first_non - 0.5, color=F.TEXT2, linewidth=1.6)
    # headers on stacked levels (axes-fraction y above the plot), greedy non-overlap in display space
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    level_end = {}
    trans = ax.get_xaxis_transform()
    base, step = 1.04, 0.075
    placed = []
    for g, a, b in spans:
        txt = headers.get(g, g)
        for lev in range(12):
            y = base + step * lev
            t = ax.text(a - 0.45, y + 0.012, txt, transform=trans, fontsize=6.6, color=F.TEXT, ha="left", va="bottom",
                        clip_on=False)
            bb = t.get_window_extent(renderer=rend)
            if bb.x0 > level_end.get(lev, -1e9) + 4:
                level_end[lev] = bb.x1
                ax.plot([a - 0.42, b + 0.42], [y, y], transform=trans, color=F.TEXT2, linewidth=0.8, clip_on=False)
                placed.append((g, lev))
                break
            t.remove()
    top = base + step * (max(lv for _, lv in placed) + 1) + 0.03
    # band labels
    n_end = (first_non - 0.5) if first_non is not None else len(B) - 0.5
    ax.text((-0.5 + n_end) / 2, top, N_BAND, transform=trans, ha="center", va="bottom", fontsize=8.5, fontweight="bold",
            color=F.TEXT2, clip_on=False)
    if first_non is not None:
        ax.text((first_non - 0.5 + len(B) - 0.5) / 2, top, NON_N_BAND, transform=trans, ha="center", va="bottom",
                fontsize=8.5, fontweight="bold", color=F.TEXT2, clip_on=False)
    return top
