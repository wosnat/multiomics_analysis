"""E16 conclusion figure: one at-a-glance status grid for the N import routes (no KG calls).

Values: data/explore/e10_cells.csv (system status from stored expression_status of detected subunits, E10 rule; median
rank percentile of detected subunits). Broad row = E10 "N broad" systems, known false positives excluded, summarised as
"n up / n detected" per column. Regulators row = glnA, ntcA, glnB combined with the same rule (explore.combine_labels);
number = median of the three percentiles.
Outputs: data/explore/e16_conclusion.csv; figures/e16_conclusion.png/svg.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"
# (group, subgroup, e10 column, header)
COLS = ([("Coculture (this study)", "protein", f"protein cc d{d}", f"d{d}") for d in (18, 31, 60, 89)]
        + [("Axenic, declining (this study)", "protein", c, h) for c, h in
           (("protein ax d14", "d14"), ("protein ax d31 (death)", "d31"), ("protein ax d89 (death)", "d89"))]
        + [("Acute N starvation", "Tolonen 2006 (microarray)", f"Tolonen N-dep {t}", t) for t in ("6h", "12h", "24h", "48h")]
        + [("Acute N starvation", "Read 2017\n(RNA-seq, filtered;\nonly 'up' readable)", f"Read N-depleted {t} (filtered)", t)
           for t in ("3h", "12h", "24h")]
        + [("N-replete coculture", "Aharonovich 2016\n(MED4, 20 h)", "Aharonovich 2016 (N-replete, 20 h)*", "MED4")])
ROWS = [("Ammonium", "amt1 transporter", ["sys_PMM0263"], "up in coculture; late; rises in dying axenic too", "amt"),
        ("Urea", "urt transporter", ["sys_PMM0970"], "kept in coculture; urt dips in dying axenic, urease stays", "urea"),
        ("Urea", "urease (urea → ammonium)", ["ref_ureA-G"], None, "urea"),
        ("Cyanate", "cyn transporter", ["sys_PMM0370"], "kept in coculture; transporter drops in dying axenic", "cyn"),
        ("Cyanate", "cyanase cynS (cyanate → ammonium)", ["ref_cynS"], None, "cyn"),
        ("Dipeptides", "dpp transporter", ["sys_PMM0192"], "up in coculture; one subunit late in axenic", "dpp"),
        ("Amino acids, polyamines, osmolytes", "broad listings: n up / n detected", "BROAD", "no consistent signal", "broad"),
        ("N-starvation regulators", "glnA, ntcA, glnB", ["ref_glnA", "ref_ntcA", "ref_glnB"],
         "N-starvation response in all N-stress conditions", "reg")]
STATUS_C = {"up": F.CAT[1], "down": F.CAT[0], "mixed": "#9a8fb0", "ns": "#dcdbd6", "not detected": F.SURF,
            "not listed": F.SURF, "summary": "#ecebe7"}


def build():
    C = pd.read_csv(OUT / "e10_cells.csv")
    R = pd.read_csv(OUT / "e10_rows.csv")
    S = C.pivot_table(index="row_id", columns="column", values="status", aggfunc="first")
    P = C.pivot_table(index="row_id", columns="column", values="median_percentile", aggfunc="first")
    broad = [r for r, cat, tags in zip(R.row_id, R.category, R.tags.fillna("")) if cat == "N broad" and "[FP]" not in tags]
    out = []
    for grp, lab, ids, reading, key in ROWS:
        for g, sub, col, hdr in COLS:
            filt = col.startswith("Read")
            if ids == "BROAD":
                labs = list(S.loc[broad, col])
                nu, nd = ex.count_up(labs)
                st, pct, txt = "summary", np.nan, f"{nu}/{nd}"
                n_sys = len(broad)
            else:
                labs = list(S.loc[ids, col])
                st = ex.combine_labels(labs) if len(ids) > 1 else labs[0]
                pct = np.nan if filt else float(np.nanmedian(P.loc[ids, col])) if P.loc[ids, col].notna().any() else np.nan
                txt = ("n.l." if st == "not listed" else "n.d." if st == "not detected" else
                       "" if pct != pct else f"{pct:.2f}")
                n_sys = len(ids)
            out.append({"route": grp, "row": lab, "members": "|".join(broad if ids == "BROAD" else ids), "n_members": n_sys,
                        "column_group": g, "column_subgroup": sub.replace("\n", " "), "e10_column": col, "header": hdr,
                        "status": st, "rank_percentile": pct, "cell_text": txt,
                        "member_statuses": "|".join(labs), "reading": reading or ""})
    return pd.DataFrame(out)


def draw(D):
    rows = list(dict.fromkeys(D.row))
    nr, nc = len(rows), len(COLS)
    xs, x, prev = [], 0.0, None
    for g, sub, col, hdr in COLS:
        if prev is not None and (g, sub) != prev:
            x += 0.75 if g != prev[0] else 0.3
        xs.append(x)
        x += 1
        prev = (g, sub)
    W = x
    fig = plt.figure(figsize=(21, 9))
    ax = fig.add_axes([0.255, 0.1, 0.52, 0.56])
    axR = fig.add_axes([0.785, 0.1, 0.21, 0.56])
    for a in (ax, axR):
        a.set_ylim(nr, 0)
    Di = D.set_index(["row", "e10_column"])
    for i, r in enumerate(rows):
        for j, (g, sub, col, hdr) in enumerate(COLS):
            c = Di.loc[(r, col)]
            st = c.status
            hatch = "///" if st in ("not detected", "not listed") else ""
            ax.add_patch(plt.Rectangle((xs[j], i + 0.06), 0.92, 0.86, facecolor=STATUS_C[st], hatch=hatch,
                                       edgecolor=F.GRID if hatch else F.SURF, linewidth=0.5))
            ax.text(xs[j] + 0.46, i + 0.5, c.cell_text, ha="center", va="center", fontsize=10.5,
                    color=F.SURF if st in ("up", "down") else F.TEXT)
    ax.set_xlim(-0.1, W)
    ax.axis("off")
    # row labels
    groups_seen = {}
    for i, r in enumerate(rows):
        route = D[D.row == r].route.iloc[0]
        first = route not in groups_seen
        groups_seen.setdefault(route, i)
        ax.text(-0.35, i + 0.5, r, ha="right", va="center", fontsize=11, color=F.TEXT2)
        if first:
            n_in = sum(1 for q in rows if D[D.row == q].route.iloc[0] == route)
            ax.annotate(route.replace(", osmolytes", ","+chr(10)+"osmolytes"), xy=(0, i + n_in / 2), xycoords=("figure fraction", "data"),
                        xytext=(14, 0), textcoords="offset points", ha="left", va="center", fontsize=12, fontweight="bold",
                        color=F.TEXT, annotation_clip=False)
        if i and first:
            ax.plot([-W * 0.47, W], [i, i], color=F.TEXT2, linewidth=0.8, clip_on=False)
            axR.axhline(i, color=F.TEXT2, linewidth=0.8, clip_on=False)
    # column headers: header row, subgroup, group
    for j, (g, sub, col, hdr) in enumerate(COLS):
        ax.text(xs[j] + 0.46, -0.12, hdr, ha="center", va="bottom", fontsize=10.5, color=F.TEXT)
    spans = {}
    for j, (g, sub, col, hdr) in enumerate(COLS):
        spans.setdefault(g, []).append(j)
        spans.setdefault((g, sub), []).append(j)
    for k, js in spans.items():
        x0, x1 = xs[js[0]], xs[js[-1]] + 0.92
        if isinstance(k, tuple):
            if k[1] == "protein":
                continue
            ax.text((x0 + x1) / 2, -0.62, k[1], ha="center", va="bottom", fontsize=9.5, color=F.TEXT2, linespacing=1.05)
            ax.plot([x0, x1], [-0.55, -0.55], color=F.TEXT2, linewidth=0.8, clip_on=False)
        else:
            ytop = -1.75
            lab = {"Coculture (this study)": "Coculture"+chr(10)+"(this study)",
                   "Axenic, declining (this study)": "Axenic, declining"+chr(10)+"(this study)",
                   "N-replete coculture": "N-replete"+chr(10)+"coculture"}.get(k, k)
            ax.text((x0 + x1) / 2, ytop + 0.06, lab, ha="center", va="bottom", fontsize=12, fontweight="bold", color=F.TEXT,
                    linespacing=1.05)
            ax.plot([x0, x1], [ytop + 0.2, ytop + 0.2], color=F.TEXT, linewidth=1.4, clip_on=False)
    for j in range(1, nc):
        if COLS[j][0] != COLS[j - 1][0]:
            ax.axvline(xs[j] - 0.27, color=F.TEXT, linewidth=1.6, ymin=0, ymax=1)
    ja = [j for j, c in enumerate(COLS) if c[0] == "N-replete coculture"][0]
    ax.text(xs[ja] + 0.46, nr + 0.12, "table 82% negative;\n'down' mostly\ntable-wide", ha="center", va="top",
            fontsize=8.5, color=F.TEXT2, style="italic")
    # reading column
    axR.axis("off")
    axR.set_xlim(0, 1)
    axR.text(0.02, -0.12, "Reading", fontsize=12, fontweight="bold", va="bottom")
    for route, i0 in groups_seen.items():
        n_in = sum(1 for r in rows if D[D.row == r].route.iloc[0] == route)
        reading = D[(D.route == route) & (D.reading != "")].reading.iloc[0]
        axR.text(0.02, i0 + n_in / 2, reading, va="center", fontsize=10.5, color=F.TEXT, wrap=True)
    handles = [Patch(facecolor=STATUS_C[k], edgecolor=F.GRID, hatch="///" if k == "not detected" else "", label=lab)
               for k, lab in (("up", "up"), ("down", "down"), ("mixed", "subunits disagree (up and down)"),
                              ("ns", "not significant"), ("not detected", "not detected / not listed"),
                              ("summary", "count: n systems up / n detected"))]
    fig.legend(handles=handles, loc="lower left", ncol=6, bbox_to_anchor=(0.2, 0.0), fontsize=10, frameon=False)
    figs.head(fig, "Which N import routes are up in coculture, and in which reference conditions",
              "Protein (this study) and RNA (references); orange = up, blue = down, grey = not significant, "
              "hatched = not detected/listed; number = rank (1 = most up-regulated).\n"
              "Source: data/explore/e16_conclusion.csv (from e10_cells.csv; system status = stored significance calls of "
              "detected subunits; number = median rank percentile of detected subunits).")
    return figs.save(fig, "e16_conclusion")


def main():
    D = build()
    D.to_csv(OUT / "e16_conclusion.csv", index=False)
    files = draw(D)
    print([f.name for f in files])
    W = D.assign(v=D.status.str.replace("not detected", "nd").str.replace("not listed", "nl") + " " + D.cell_text)
    W = W.pivot_table(index="row", columns="e10_column", values="v", aggfunc="first")[[c[2] for c in COLS]]
    W = W.reindex(list(dict.fromkeys(D.row)))
    W.columns = [f"{c[0][:4]}|{c[3]}" for c in COLS]
    pd.set_option("display.width", 300)
    print(W.to_string())


if __name__ == "__main__":
    main()
