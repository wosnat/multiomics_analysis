"""E4b: redesign of e4_broad_dotgrid as a scatter (presentation only; same data, data/explore/e4_system_class_enzymes.csv).

Panels: coculture protein d60, d89, and axenic d14. x = transporter's median protein rank percentile; y = median protein
rank percentile of the class's detected genome enzymes. One point per transporter x listed N class; colour = class
(fixed categorical order), marker = efflux-annotated or not. Known false positives excluded (listed in the caption).
Classes with 0 detected enzymes are drawn in a strip below the axis ("no enzyme"); transporters not detected in protein
are listed in the caption. Labels: transporter name, placed by a small greedy repel (no extra package).
Usage (repo root): .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e4b_broad_scatter.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"
CLASSES = ["ammonium", "nitrate", "amino acids", "peptides", "amino sugars", "polyamines"]
STRIP_Y = -0.13


def short(member_names):
    return ex.F_short(member_names, 2)


def repel(ax, texts, anchors):
    """Greedy label placement: for each label (in order of crowding), try offsets around its point at growing radii and
    keep the first whose box overlaps no placed label and no point marker; draw a leader line when the label is moved
    away from the default offset. No extra package."""
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    pts = [ax.transData.transform(a) for a in anchors]
    from matplotlib.transforms import Bbox
    pboxes = [Bbox.from_bounds(px - 7, py - 7, 14, 14) for px, py in pts]
    axbox = ax.get_window_extent(renderer=r)
    placed = []
    dirs = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
    order = sorted(range(len(texts)), key=lambda i: -sum(np.hypot(*(pts[i] - q)) < 40 for q in pts))
    inv = ax.transData.inverted()
    for i in order:
        t = texts[i]
        w = t.get_window_extent(renderer=r)
        bw, bh = w.width, w.height
        px, py = pts[i]
        chosen = None
        for rad in (6, 14, 24, 36, 50, 66, 84):
            for dx, dy in dirs:
                x0 = px + dx * rad - (bw if dx < 0 else (bw / 2 if dx == 0 else 0))
                y0 = py + dy * rad - (bh if dy < 0 else (bh / 2 if dy == 0 else 0))
                bb = Bbox.from_bounds(x0, y0, bw, bh)
                inside = axbox.x0 <= bb.x0 and bb.x1 <= axbox.x1 and axbox.y0 <= bb.y0 and bb.y1 <= axbox.y1
                if inside and not any(bb.overlaps(o) for o in placed) and not any(bb.overlaps(o) for j, o in enumerate(pboxes) if j != i):
                    chosen = (bb, rad)
                    break
            if chosen:
                break
        if chosen is None:
            chosen = (Bbox.from_bounds(px + 6, py + 6, bw, bh), 6)
        bb, rad = chosen
        placed.append(bb)
        t.set_ha("left")
        t.set_va("bottom")
        t.set_position(inv.transform((bb.x0, bb.y0)))
        if rad > 6:
            cx, cy = inv.transform(((bb.x0 + bb.x1) / 2, (bb.y0 + bb.y1) / 2))
            ax.plot([anchors[i][0], cx], [anchors[i][1], cy], color=F.TEXT2, linewidth=0.4, zorder=1)


def main():
    C = pd.read_csv(OUT / "e4_system_class_enzymes.csv")
    S = pd.read_csv(OUT / "e4_systems.csv")
    fp = S[S.known_false_positive.astype(bool)]
    nd = S[~S.known_false_positive.astype(bool) & S.p60_median_pct.isna()]
    X = C[~C.known_false_positive.astype(bool) & C.transporter_p60_pct.notna()].copy()
    X["name"] = X.member_names.map(short)
    colors = {c: F.CAT[i] for i, c in enumerate(CLASSES)}
    panels = [("p60", "coculture protein, day 60"), ("p89", "coculture protein, day 89"), ("p14ax", "axenic protein, day 14")]
    fig, axes = plt.subplots(1, 3, figsize=(18, 7), sharey=True)
    for ax, (k, ttl) in zip(axes, panels):
        texts, anchors = [], []
        for r in X.itertuples():
            x = getattr(r, f"transporter_{k}_pct")
            e = getattr(r, f"enzymes_{k}_median_pct")
            y = STRIP_Y if pd.isna(e) else e
            mk = "^" if r.efflux_annotated else "o"
            ax.scatter(x, y, s=60, color=colors.get(r.compound_class, F.TEXT2), marker=mk, edgecolor=F.SURF,
                       linewidth=0.6, zorder=3)
            texts.append(ax.text(x + 0.012, y + 0.012, r.name, fontsize=6.8, color=F.TEXT, zorder=4,
                                 bbox=dict(facecolor=F.SURF, edgecolor='none', pad=0.3, alpha=0.8)))
            anchors.append((x, y))
        for v in (0.5,):
            ax.axvline(v, color=F.TEXT2, linewidth=0.8, linestyle="--")
            ax.axhline(v, color=F.TEXT2, linewidth=0.8, linestyle="--")
        ax.axvline(0.9, color=F.TEXT2, linewidth=0.8, linestyle=":")
        ax.axhline(0.9, color=F.TEXT2, linewidth=0.8, linestyle=":")
        ax.axhspan(STRIP_Y - 0.05, STRIP_Y + 0.05, color=F.GRID, alpha=0.5, zorder=0)
        ax.text(1.01, 1.0, "transporter and its class\nenzymes both high", ha="right", va="top", fontsize=7, color=F.TEXT2,
                bbox=dict(facecolor=F.SURF, edgecolor="none", pad=1))
        ax.set_xlim(0, 1.02)
        ax.set_ylim(STRIP_Y - 0.07, 1.02)
        ax.set_yticks([STRIP_Y, 0, 0.2, 0.4, 0.6, 0.8, 1.0], ["no enzyme", "0", "0.2", "0.4", "0.6", "0.8", "1.0"])
        ax.set_title(ttl, loc="left", fontsize=10)
        ax.set_xlabel("transporter: median protein rank percentile")
        ax.grid(color=F.GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(F.GRID)
        ax.tick_params(length=0)
        repel(ax, texts, anchors)
    axes[0].set_ylabel("class's genome enzymes: median protein rank percentile")
    handles = [Line2D([], [], marker="o", color=colors[c], linestyle="", markersize=7, label=c)
               for c in CLASSES if c in set(X.compound_class)]
    handles += [Line2D([], [], marker="o", color=F.TEXT2, linestyle="", markersize=7, label="not efflux-annotated"),
                Line2D([], [], marker="^", color=F.TEXT2, linestyle="", markersize=7, label="efflux-annotated")]
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), bbox_to_anchor=(0.5, 0.0), fontsize=8.5)
    figs.head(fig, "Do the enzymes that would use a broadly-listed N class rise with the transporter?",
              "Each point is one broadly-listing transporter × one N class it lists: x = the transporter's median protein "
              "rank percentile, y = the median for the genes in the genome with a KEGG reaction on that class's listed compounds. "
              "Dashed 0.5 = genome middle; dotted 0.9.")
    fig.text(0.01, 0.065,
             "Excluded as known false positives: " + ", ".join(f"{short(m)} {s.replace('sys_', '')}" for m, s in zip(fp.member_names, fp.system_id))
             + ". Not detected in protein (no x): " + (", ".join(f"{short(m)} {s.replace('sys_', '')}" for m, s in zip(nd.member_names, nd.system_id)) or "none")
             + ". Source: data/explore/e4_system_class_enzymes.csv (Cysteine / L-Cysteine merged).",
             fontsize=7.5, color=F.TEXT2)
    fig.subplots_adjust(left=0.06, right=0.99, top=0.84, bottom=0.2, wspace=0.08)
    for f in figs.save(fig, "e4_broad_scatter"):
        print(f.name)


if __name__ == "__main__":
    main()
