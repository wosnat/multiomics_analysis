"""E13 one summary figure for the provisional reading (no KG calls; existing tables only). Revised in E14.

Values: data/explore/e10_cells.csv (median rank percentile of detected subunits per row x slice), e10_rows.csv and
e10_flags_all.csv (E14 flags, all axenic samples). Panel A = protein only: axenic d14, axenic d31 (death), axenic d89
(death), coculture d89. Separate narrow panel: Tolonen MED4 N deprivation (RNA, microarray) = max over 3-48 h of the
row's median percentile. Broad row = median over the "N broad" E10 systems, known false positives and murJ excluded
(murJ shown under cell envelope); per column, over systems detected in that column; exploratory (decision 4).
Markers row = median of glnA, ntcA, glnB row values (pipX not included here).
Calibration column: e10_cells / e10_by_gene (Tolonen MED4 cyanate, urea) and e8_nitrite_urea.csv (MIT9313).
Outputs: data/explore/e13_summary.csv; figures/e13_summary.png/svg.
"""
import sys
from pathlib import Path

import pandas as pd
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"
AX14, AX31, AX89, CC = "protein ax d14", "protein ax d31 (death)", "protein ax d89 (death)", "protein cc d89"
NDEP = [f"Tolonen N-dep {t}" for t in ("3h", "6h", "12h", "24h", "48h")]
ORANGE, PURPLE, GREYPURPLE, GREY = F.CAT[1], "#6a4fc4", "#8f86a6", "#9a9893"
ENVELOPE = ["sys_PMM0709", "sys_PMM1338", "sys_PMM0097", "sys_PMM1139", "sys_PMM0261"]
INORG = "Inorganic / simple N (N-starvation response)"
ENV = "Cell envelope"

# (group, row_id or special, label, verdict, verdict colour, calibration symbol, calibration text)
ROWS = [
    (INORG, "sys_PMM0263", "ammonium: amt1 (PMM0263)", "up · part of N-stress response", ORANGE,
     "—", "not up on cyanate; not calibrated otherwise"),
    (INORG, "sys_PMM0970", "urea: urt (PMM0970–0974)", "up · part of N-stress response", ORANGE,
     "✗", "MED4: not up on urea; MIT9313: up on urea and on nitrite"),
    (INORG, "ref_ureA-G", "urea → ammonium: urease ureA–G (enzyme)", "up · part of N-stress response", ORANGE,
     "✗", "not up on urea"),
    (INORG, "sys_PMM0370", "cyanate: cyn (PMM0370–0372)", "up · part of N-stress response", ORANGE,
     "~", "up on cyanate (cynA only significant); glnA and urtA also up"),
    (INORG, "ref_cynS", "cyanate → ammonium: cyanase cynS (PMM0373, enzyme)", "up · part of N-stress response", ORANGE,
     "✗", "not significant on cyanate"),
    (INORG, "sys_PMM1701", "nitrate, which MED4 can't use: clc2 (PMM1701)", "up in coculture · also up in axenic RNA d14",
     GREYPURPLE, "", ""),
    ("Peptides", "sys_PMM0192", "dipeptides: dpp (4 subunits, 3 loci: dppA+dppB adjacent)", "up in coculture protein · unresolved",
     GREYPURPLE, "—", "not tested; never responds in N deprivation"),
    ("Peptides", "sys_PMM0561", "peptides (broad listing): efflux pump PMM0561", "RNA up at d60/d89 · protein not",
     GREY, "", ""),
    ("Broadly listed routes", "BROAD", None, "no signal", GREY, "", ""),
    (ENV, "sys_PMM0709", "outer membrane porin som (PMM0709)", "up in coculture and in dying axenic · not specific",
     GREYPURPLE, "", ""),
    (ENV, "sys_PMM1338", "outer membrane insertion bamA (PMM1338)", "up in coculture · already high in axenic d14",
     PURPLE, "", ""),
    (ENV, "sys_PMM0097", "outer membrane efflux tolC (PMM0097)", "up in coculture · already high in axenic d14",
     PURPLE, "", ""),
    (ENV, "sys_PMM1139", "RND efflux pump acrA (PMM1139)", "up in coculture · already high in axenic d14",
     PURPLE, "", ""),
    (ENV, "sys_PMM0261", "lipid II flippase murJ (PMM0261)", "up in coculture only · not N-specific", PURPLE, "", ""),
    ("Reference", "MARKERS", "N-starvation markers (glnA, ntcA, glnB; median)", "reference", F.TEXT, "", ""),
]


def values(C, R, FL):
    P = C.pivot_table(index="row_id", columns="column", values="median_percentile", aggfunc="first")
    rows = R.set_index("row_id")
    fl = FL.set_index("row_id")
    broad_ids = [r for r in rows.index if rows.category[r] == "N broad" and "[FP]" not in str(rows.tags[r])
                 and r not in ENVELOPE]
    out = []
    for grp, rid, lab, verdict, col, sym, ctext in ROWS:
        if rid == "BROAD":
            sub = P.loc[broad_ids]
            lab = (f"amino acids, polyamines, osmolytes, amino sugars…" + chr(10)
                   + f"(median of {len(broad_ids)} N systems; exploratory, decision 4)")
            members, star = "|".join(broad_ids), ""
        elif rid == "MARKERS":
            sub, members, star = P.loc[["ref_glnA", "ref_ntcA", "ref_glnB"]], "ref_glnA|ref_ntcA|ref_glnB", ""
        else:
            sub, members = P.loc[[rid]], rid
            star = "★ " if fl.flag_strict.get(rid, False) else ("☆ " if fl.flag_loose.get(rid, False) else "")
        out.append({"group": grp, "row": star + lab, "members": members,
                    "axenic_d14_protein": sub[AX14].median(), "axenic_d31_protein_death": sub[AX31].median(),
                    "axenic_d89_protein_death": sub[AX89].median(), "coculture_d89_protein": sub[CC].median(),
                    "tolonen_ndep_max_3_48h_rna": sub[NDEP].max(axis=1).median(),
                    "n_detected_ax_d14": int(sub[AX14].notna().sum()), "n_detected_cc_d89": int(sub[CC].notna().sum()),
                    "n_members": len(sub), "e14_flag": star.strip(), "verdict": verdict,
                    "calibration_symbol": sym, "calibration_note": ctext, "vcolor": col})
    return pd.DataFrame(out)


def main():
    C = pd.read_csv(OUT / "e10_cells.csv")
    R = pd.read_csv(OUT / "e10_rows.csv")
    FL = pd.read_csv(OUT / "e10_flags_all.csv")
    V = values(C, R, FL)
    V.drop(columns="vcolor").to_csv(OUT / "e13_summary.csv", index=False)

    ys, y, prev, gstart = [], 0.0, None, {}
    for g in V.group:
        if prev is not None and g != prev:
            y += 0.7
        if g != prev:
            gstart[g] = y
        ys.append(y)
        y += 1
        prev = g
    V["y"] = ys
    n = y
    H = 0.42 * n + 2.8
    fig = plt.figure(figsize=(19, H))
    top, bot = 1 - 1.6 / H, 1.0 / H
    axA = fig.add_axes([0.255, bot, 0.25, top - bot])
    axN = fig.add_axes([0.515, bot, 0.06, top - bot])
    axB = fig.add_axes([0.585, bot, 0.18, top - bot])
    axC = fig.add_axes([0.775, bot, 0.22, top - bot])
    for ax in (axA, axN, axB, axC):
        ax.set_ylim(n - 0.3, -1.1)
    for g, gy in gstart.items():
        if gy > 0:
            for ax in (axA, axN, axB, axC):
                ax.axhline(gy - 0.35, color=F.GRID, linewidth=0.9, clip_on=False)
        axA.annotate(g, xy=(0, gy - 0.5), xycoords=("figure fraction", "data"), xytext=(10, 0), textcoords="offset points",
                     fontsize=9, fontweight="bold", color=F.TEXT2, va="center", annotation_clip=False)
    # panel A: protein only
    for ax in (axA, axN):
        ax.axvline(0.5, color=F.TEXT2, linestyle="--", linewidth=0.9, zorder=0)
        ax.axvline(0.9, color=F.TEXT2, linestyle=":", linewidth=0.9, zorder=0)
        ax.set_xlim(0, 1.03)
        ax.tick_params(length=0, labelsize=8)
        for s_ in ("top", "right", "left"):
            ax.spines[s_].set_visible(False)
    axA.text(0.5, -0.95, "genome middle", ha="center", fontsize=8, color=F.TEXT2)
    axA.text(0.9, -0.95, "top 10%", ha="center", fontsize=8, color=F.TEXT2)
    for r in V.itertuples():
        ref = r.group == "Reference"
        axA.plot([r.axenic_d14_protein, r.coculture_d89_protein], [r.y, r.y], color=F.GRID, linewidth=2.2, zorder=1)
        axA.scatter(r.axenic_d31_protein_death, r.y, marker="s", s=16, color=GREY, zorder=2)
        axA.scatter(r.axenic_d89_protein_death, r.y, marker="D", s=16, color=GREY, zorder=2)
        axA.scatter(r.coculture_d89_protein, r.y, s=80, color=F.TEXT if ref else ORANGE, zorder=3)
        axA.scatter(r.axenic_d14_protein, r.y, s=110, facecolor="none", edgecolor=GREY, linewidth=1.8, zorder=4)
        axN.scatter(r.tolonen_ndep_max_3_48h_rna, r.y, marker="^", s=45, color=GREY, zorder=3)
    axA.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    axA.set_xlabel("protein rank percentile (0 = lowest, 1 = highest in the sample)", fontsize=8.5)
    axA.set_yticks(V.y, V.row, fontsize=8.5)
    for t, r in zip(axA.get_yticklabels(), V.itertuples()):
        if r.group == "Reference":
            t.set_style("italic")
            t.set_color(F.TEXT2)
    axA.set_title("A. Where each route ranks (protein)", loc="left", fontsize=10, fontweight="bold", pad=24)
    axN.set_xticks([0, 0.5, 1.0], ["0", ".5", "1"])
    axN.set_yticks([])
    axN.set_xlabel("percentile", fontsize=8)
    axN.set_title("acute N starvation\n(RNA, microarray;\nmax 3–48 h)", loc="left", fontsize=8, color=F.TEXT2, pad=6)
    axA.legend(handles=[
        Line2D([], [], marker="o", linestyle="", markerfacecolor="none", markeredgecolor=GREY, markersize=9,
               markeredgewidth=1.8, label="axenic day 14 (late decline)"),
        Line2D([], [], marker="s", linestyle="", color=GREY, markersize=4.5, label="axenic day 31 (death)"),
        Line2D([], [], marker="D", linestyle="", color=GREY, markersize=4.5, label="axenic day 89 (death)"),
        Line2D([], [], marker="o", linestyle="", color=ORANGE, markersize=8, label="coculture day 89")],
        loc="upper left", bbox_to_anchor=(-0.05, -0.07 * 15 / n), ncol=4, fontsize=8, frameon=False, columnspacing=1.0)
    # panel B
    for r in V.itertuples():
        axB.text(0.02, r.y, r.verdict, va="center", fontsize=7.8, color=r.vcolor,
                 fontweight="bold" if r.vcolor != F.TEXT else "normal", style="italic" if r.vcolor == F.TEXT else "normal")
    axB.set_title("B. Reading", loc="left", fontsize=10, fontweight="bold", pad=24)
    axB.axis("off")
    # panel C
    for r in V.itertuples():
        if r.calibration_symbol:
            axC.text(0.02, r.y, r.calibration_symbol, va="center", ha="center", fontsize=11, color=F.TEXT)
            axC.text(0.07, r.y, r.calibration_note, va="center", fontsize=7.5, color=F.TEXT2)
    axC.text(0.0, -0.75, "✗ no   ~ partly / confounded   — not tested", fontsize=7.5, color=F.TEXT2)
    axC.set_title("C. Tracks its own substrate in calibration?", loc="left", fontsize=10, fontweight="bold", pad=24)
    axC.set_xlim(0, 1)
    axC.axis("off")
    figs.head(fig, "MED4 raises nitrogen-import capacity as part of the starvation response; expression can't say which compound it uses",
              "Source: data/explore/e13_summary.csv (from e10_cells.csv: median rank percentile of detected subunits; this study's "
              "proteome; Tolonen MED4 N deprivation and sole-N growth; e8_nitrite_urea.csv for MIT9313).\n"
              "Verdict colours: orange = up with N stress, purple = coculture-specific, grey-purple = up in coculture but "
              "unresolved / not specific, grey = no signal. ★ / ☆ = E14 strict / loose flag (all axenic samples).")
    return figs.save(fig, "e13_summary"), V


if __name__ == "__main__":
    files, V = main()
    pd.set_option("display.width", 250)
    print([f.name for f in files])
    print(V.drop(columns=["vcolor", "y", "members", "calibration_note"]).round(3).to_string(index=False))
