"""E10 all-systems status matrix (MED4; descriptive). No KG calls: analysis/data/de_long.csv.gz + methods v1.6.1.

Rows: every High/Medium MED4 system (p11), plus reference rows: glnA, ntcA, glnB, pipX (one row each), urease ureA-G
(one row), cynS, glsF. Efflux-annotated and known-false-positive systems kept, marked [efflux] / [FP].
Columns (3 blocks): coculture vs axenic (ismej.2016.70 MED4 20h; direct contrast d11, d18) | N starvation / other N
sources (Tolonen N deprivation 3-48 h; Read N-depleted 3/12/24 h, filtered; Tolonen cyanate; Tolonen urea) | this study
(protein ax d14, d31, d89 | cc d18-d89; RNA ax d14 | cc d18-d89). No pooled slices.
Cell status: explore.cell_status over the stored expression_status of detected subunits; median rank percentile over
detected subunits (NaN for filtered tables). Clustering: average linkage, euclidean, on the percentile profile over the
non-filtered columns, missing imputed with 0.5. Flags: explore.coculture_flags (strict / loose).

Add-ons: (A) e10_by_class: one panel per N class (+ non-N reference). Organic classes: p18 listing_basis rows.
Inorganic classes: fig2 Block A eligible rows (p12 classified rows, most_specific or inherited from a non-lumping
family, High/Medium) with the p18 rule (f1.system_basis) for dedicated / broad. (B) e10_by_system_dedicated: one row
per gene, the gene's own stored status and rank percentile.

Outputs: data/explore/e10_cells.csv, e10_rows.csv, e10_flags.csv, e10_clusters.csv, e10_by_class.csv,
e10_by_gene.csv; figures e10_status_matrix, e10_status_matrix_grouped, e10_by_class, e10_by_system_dedicated.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"
COLS = ([("coculture vs axenic", "ctrl_med4_hot1a3", "20h", "Aharonovich 2016 (N-replete, 20 h)*"),
         ("coculture vs axenic", "direct_contrast_rna", "day 11", "same study d11 (exponential)"),
         ("coculture vs axenic", "direct_contrast_rna", "day 18", "same study d18 (cc d18 vs ax ~d14)")]
        + [("N starvation / other N sources", "cal_tolonen_ndep", t, f"Tolonen N-dep {t}") for t in ("3h", "6h", "12h", "24h", "48h")]
        + [("N starvation / other N sources", "cal_read_ndep", t, f"Read N-depleted {t} (filtered)") for t in ("3h", "12h", "24h")]
        + [("N starvation / other N sources", "cal_tolonen_cyanate", "steady state", "Tolonen growth on cyanate"),
           ("N starvation / other N sources", "cal_tolonen_urea", "steady state", "Tolonen growth on urea")]
        + [("this study (Weissberg)", "anchor_axenic_protein", d, f"protein ax d{d.split()[-1]}" + ("" if d == "day 14" else " (death)"))
           for d in ("day 14", "day 31", "day 89")]
        + [("this study (Weissberg)", "anchor_cocult_protein", f"day {d}", f"protein cc d{d}") for d in (18, 31, 60, 89)]
        + [("this study (Weissberg)", "anchor_axenic_rna", "day 14", "RNA ax d14")]
        + [("this study (Weissberg)", "anchor_cocult_rna", f"day {d}", f"RNA cc d{d}") for d in (18, 31, 60, 89)])
COLNAMES = [c[3] for c in COLS]
BLOCKS = [c[0] for c in COLS]
DIVIDE_BEFORE = {"protein cc d18", "RNA ax d14", "RNA cc d18"}
NAMED = {"sys_PMM0263": "amt1: ammonium transporter (ammonium)", "sys_PMM0970": "urt: urea ABC transporter (urea)",
         "sys_PMM0370": "cyn: cyanate ABC transporter (cyanate)", "sys_PMM0192": "dpp: di/oligopeptide ABC transporter (peptides)",
         "sys_PMM0710": "pst: phosphate", "sys_PMM0671": "phn: phosphonate", "sys_PMM0644": "sul1: sulfate",
         "sys_PMM0214": "sul3: sulfate", "sys_PMM0489": "fut/idiA2: iron", "sys_PMM0601": "mnt: manganese",
         "sys_PMM1029": "lraI: Mn/Zn", "sys_PMM0213": "sbtA: bicarbonate"}
DEDICATED_IDS = {"sys_PMM0263", "sys_PMM0970", "sys_PMM0370", "sys_PMM0192"}
NON_N_IDS = ["sys_PMM0710", "sys_PMM0671", "sys_PMM0644", "sys_PMM0214", "sys_PMM0489", "sys_PMM0601", "sys_PMM1029",
             "sys_PMM0213"]
CLASS_ORDER = ["ammonium", "urea", "cyanate", "nitrite", "nitrate", "peptides", "amino acids", "polyamines", "osmolytes",
               "amino sugars", "nucleobases/nucleosides"]
INORG = ["ammonium", "urea", "cyanate", "nitrite", "nitrate"]
STATUS_C = {"up": F.CAT[1], "down": F.CAT[0], "mixed": "#9a8fb0", "ns": "#dcdbd6", "not detected": F.SURF, "not listed": F.SURF}
ROWH = 0.19


# --------------------------------------------------------------------------- data
def class_listing(L):
    """(system_id, class, listing_basis) for H/M systems: organic from p18; inorganic from fig2 Block A rows."""
    out = [(r.system_id, r.compound_class, r.listing_basis, "p18")
           for r in L["lb"].itertuples() if r.compound_class not in INORG]
    x = F.DATA["med4"]
    a = x["cls"].copy()
    sy = x["sys"].set_index("system_id")
    lump = a.is_lumping.astype(str).str.lower().eq("true")
    a["tier"] = a.system_id.map(sy.tier)
    e = a[((a.substrate_depth == "most_specific") | ((a.substrate_depth == "inherited") & ~lump)) & a.tier.isin(["High", "Medium"])]
    for c in INORG:
        for sid in sorted(set(e[e.compound_class_final == c].system_id)):
            out.append((sid, c, F.system_basis("med4", sid, c), "fig2 Block A"))
    return pd.DataFrame(out, columns=["system_id", "compound_class", "listing_basis", "class_source"])


def rows_table(L, CL):
    sy, mem = L["sy"], L["mem"]
    roles = pd.read_csv(ex.MD / "med4" / "p2_med4_gene_roles.csv").set_index("locus_tag")
    rows = []
    for sid, r in sy[sy.tier.isin(["High", "Medium"])].iterrows():
        loci = mem[sid]
        tags = (" [efflux]" if bool(r.efflux_annotated) else "") + (" [FP]" if bool(r.known_false_positive) else "")
        classes = [c for c in CLASS_ORDER if c in set(CL[CL.system_id == sid].compound_class)]
        if sid in NAMED:
            base = NAMED[sid]
        else:
            nm = ex.F_short(r.member_names, 3)
            if not nm.startswith("PMM"):
                nm = f"{nm} {sid[4:]}"
            prod = str(roles["product"].get(loci[0], "")).split(",")[0][:34].rstrip(" (")
            base = f"{nm}: {prod}"
        lab = base + (f" (N: {', '.join(classes)})" if classes and sid not in NAMED else "")
        cat = ("N dedicated" if sid in DEDICATED_IDS else "N broad" if classes else
               "non-N reference" if sid in NON_N_IDS else "other High/Medium")
        rows.append({"row_id": sid, "label": lab + tags + f" [{r.tier[0]}]", "base": base, "category": cat, "loci": loci,
                     "tier": r.tier, "classes": classes, "tags": tags})
    ref = [("ref_ureA-G", "urease ureA–G: urea → ammonium (enzyme)", [u for u in ex.UREASE if u in L["names"]], "linked enzymes"),
           ("ref_cynS", "cynS: cyanase, cyanate → ammonium (enzyme)", ["PMM0373"], "linked enzymes"),
           ("ref_glsF", "glsF: glutamate synthase (enzyme)", ["PMM1512"], "linked enzymes")]
    what = {"glnA": "glutamine synthetase", "ntcA": "N-control regulator", "glnB": "PII protein", "pipX": "NtcA co-activator"}
    for lt, nm in ex.MARKERS.items():
        ref.append((f"ref_{nm}", f"{nm}: {what[nm]} (N-starvation marker)", [lt], "markers"))
    for rid, lab, loci, cat in ref:
        rows.append({"row_id": rid, "label": lab, "base": lab, "category": cat, "loci": loci, "tier": "reference",
                     "classes": [], "tags": ""})
    return pd.DataFrame(rows)


def cell_records(slices, row_id, loci, cols=None):
    out = []
    for blk, s, t, lab in (cols or COLS):
        x = slices[(s, t)].reindex(loci).dropna(subset=["log2fc"])
        filt = s == "cal_read_ndep"
        st, nu, nd, n = ex.cell_status(list(x.expression_status), filtered=filt)
        out.append({"row_id": row_id, "block": blk, "column": lab, "short_name": s, "timepoint": t, "status": st,
                    "n_up": nu, "n_down": nd, "n_detected": n, "n_members": len(loci),
                    "median_percentile": np.nan if (filt or n == 0) else float(x.rank_percentile.median())})
    return out


# --------------------------------------------------------------------------- drawing helpers
def col_x(cols=None):
    cols = cols or COLS
    xs, x, prev = [], 0.0, None
    for blk, lab in ((c[0], c[3]) for c in cols):
        if prev is not None and blk != prev:
            x += 0.6
        elif lab in DIVIDE_BEFORE:
            x += 0.25
        xs.append(x)
        x += 1
        prev = blk
    return xs, x


def decorate(ax, xs, W, n, title, hdr_offset=128, cols=None):
    cols = cols or COLS
    COLNAMES, BLOCKS = [c[3] for c in cols], [c[0] for c in cols]
    ax.set_xlim(0, W)
    ax.set_ylim(n, 0)
    ax.set_xticks([xx + 0.47 for xx in xs], COLNAMES, rotation=55, ha="left", fontsize=7)
    ax.xaxis.tick_top()
    for s_ in ax.spines.values():
        s_.set_visible(False)
    ax.tick_params(length=0)
    tr = ax.get_xaxis_transform()
    for b in dict.fromkeys(BLOCKS):
        bx = [xx for xx, bb in zip(xs, BLOCKS) if bb == b]
        ax.annotate(b, xy=((min(bx) + max(bx) + 0.94) / 2, 1.0), xycoords=tr, xytext=(0, hdr_offset), textcoords="offset points",
                    ha="center", fontsize=8.5, fontweight="bold", color=F.TEXT2, annotation_clip=False)
    for xx, lab in zip(xs, COLNAMES):
        if lab in DIVIDE_BEFORE:
            ax.axvline(xx - 0.12, color=F.TEXT, linewidth=1.6)
    for xx, b, prev in zip(xs[1:], BLOCKS[1:], BLOCKS[:-1]):
        if b != prev:
            ax.axvline(xx - 0.3, color=F.TEXT, linewidth=2.6)
    ax.axvspan(xs[0] - 0.03, xs[0] + 0.97, color=F.GRID, alpha=0.6, zorder=0)   # Aharonovich column shading
    ax.get_xticklabels()[0].set_bbox(dict(facecolor=F.GRID, edgecolor="none", pad=1.5))
    if title:
        ax.set_title(title, loc="left", fontsize=9, pad=hdr_offset + 22)


def status_cell(ax, x, y, rec, text):
    st = rec["status"]
    hatch = "///" if st in ("not detected", "not listed") else ""
    ax.add_patch(plt.Rectangle((x, y), 0.94, 0.9, facecolor=STATUS_C[st], edgecolor=F.GRID if hatch else F.SURF,
                               hatch=hatch, linewidth=0.3, zorder=2))
    if text:
        ax.text(x + 0.47, y + 0.47, text, ha="center", va="center", fontsize=7, zorder=3,
                color=F.SURF if st in ("up", "down") else F.TEXT)


def count_text(rec):
    if not rec["n_detected"]:
        return ""
    k = rec["n_down"] if rec["status"] == "down" else rec["n_up"]
    return f"{k}/{rec['n_detected']}"


def status_legend(fig, y=0.0):
    handles = [Patch(facecolor=STATUS_C[k], edgecolor=F.GRID, hatch="///" if k == "not detected" else "", label=k)
               for k in ("up", "down", "mixed", "ns", "not detected")]
    fig.legend(handles=handles, loc="lower left", ncol=5, bbox_to_anchor=(0.01, y), fontsize=8, frameon=False,
               title="status from stored expression_status (filtered Read tables: hatched = not listed)", title_fontsize=8)


AHARONOVICH_NOTE = "* Aharonovich 2016 column (shaded): 82% of genes negative; 'down' mostly table-wide."


# --------------------------------------------------------------------------- figure 1/2: the matrix
def draw_matrix(C, R, lab_of, Z, ids, mode):
    if mode == "clustered":
        order = dendrogram(Z, no_plot=True, labels=ids)["ivl"]
    else:
        cats = ["N dedicated", "N broad", "linked enzymes", "markers", "non-N reference", "other High/Medium"]
        order = list(R.assign(c=R.category.map(cats.index)).sort_values(["c", "label"]).row_id)
    n = len(order)
    xs, W = col_x()
    h = ROWH * n + 5.2
    fig = plt.figure(figsize=(26, h))
    bot, top = 1.2 / h, 1 - 3.6 / h
    axA = fig.add_axes([0.235, bot, 0.37, top - bot])
    axB = fig.add_axes([0.62, bot, 0.37, top - bot])
    if mode == "clustered":
        axd = fig.add_axes([0.005, bot, 0.045, top - bot])
        dendrogram(Z, orientation="left", ax=axd, no_labels=True, link_color_func=lambda k: F.TEXT2)
        axd.set_ylim(n * 10, 0)
        axd.axis("off")
    Ci = C.set_index(["row_id", "column"])
    for i, rid in enumerate(order):
        for j, col in enumerate(COLNAMES):
            rec = Ci.loc[(rid, col)]
            status_cell(axA, xs[j], i, rec, count_text(rec))
            v = rec.median_percentile
            axB.add_patch(plt.Rectangle((xs[j], i), 0.94, 0.9, facecolor=figs.PCT(v) if v == v else F.SURF,
                                        edgecolor=F.SURF if v == v else F.GRID, hatch="" if v == v else "///",
                                        linewidth=0.3, zorder=2))
    decorate(axA, xs, W, n, "A. status (count = n significant in the shown direction / n detected subunits)")
    decorate(axB, xs, W, n, "B. median rank percentile of detected subunits (hatched = not detected / filtered table)")
    axA.set_yticks([i + 0.45 for i in range(n)], [lab_of[r] for r in order], fontsize=7)
    axB.set_yticks([])
    if mode == "grouped":
        cat = R.set_index("row_id").category
        starts = [0] + [i for i in range(1, n) if cat[order[i]] != cat[order[i - 1]]]
        for i in starts:
            if i:
                for ax in (axA, axB):
                    ax.axhline(i - 0.05, color=F.TEXT, linewidth=1.2)
            axd = fig.add_axes([0.005, bot, 0.03, top - bot])
            axd.set_ylim(n, 0)
            axd.axis("off")
            axd.text(0, i + 0.45, cat[order[i]], fontsize=8, fontweight="bold", color=F.TEXT, va="center")
    status_legend(fig)
    figs.add_cbar(fig, axB, figs.PCT, plt.Normalize(0, 1), "median rank percentile, 0–1", pad=0.55 / (ROWH * n), size=0.15 / (ROWH * n))
    head = ("Rows ordered by average-linkage clustering (euclidean) on panel B over the non-filtered columns; missing values "
            "imputed with 0.5 (data/explore/e10_clusters.csv). " if mode == "clustered" else
            "Rows grouped by category: N dedicated / N broad / linked enzymes / markers / non-N reference / other High/Medium. ")
    figs.head(fig, f"MED4 transport systems: status across all experiments ({mode})",
              "Source: data/explore/e10_cells.csv (analysis/data/de_long.csv.gz; methods v1.6.1 High/Medium systems + reference rows). "
              "Status from stored expression_status of detected subunits. " + AHARONOVICH_NOTE + "\n" + head
              + "★ strict / ☆ loose coculture-specific candidate, all axenic samples considered (data/explore/e10_flags.csv). [efflux], [FP] = methods flags; [H]/[M] = tier.")
    return figs.save(fig, "e10_status_matrix" + ("" if mode == "clustered" else "_grouped"))


# --------------------------------------------------------------------------- add-on figures (panel lists)
def draw_panels(items, name, title, subtitle, label_w=0.30, width=17, cols=None):
    """items: ("panel", text) | ("sep", text) | ("row", label, [records], [texts])."""
    xs, W = col_x(cols)
    n = (sum(1 for it in items if it[0] == "row") + 1.35 * sum(1 for it in items if it[0] == "panel")
         + 0.7 * sum(1 for it in items if it[0] == "sep"))
    h = ROWH * n + 5.0
    fig = plt.figure(figsize=(width, h))
    bot, top = 1.0 / h, 1 - 3.6 / h
    ax = fig.add_axes([label_w, bot, 0.985 - label_w, top - bot])
    y, ticks, labs, first_sep = 0.0, [], [], True
    for it in items:
        if it[0] == "panel":
            y += 0.3 if y else 0
            ax.annotate(it[1], xy=(0, y + 0.45), xycoords=("figure fraction", "data"), xytext=(8, 0),
                        textcoords="offset points", ha="left", va="center", fontsize=8.5, fontweight="bold", color=F.TEXT)
            ax.axhline(y + 0.85, color=F.TEXT, linewidth=1.0, xmin=-(label_w - 0.005) / (0.985 - label_w), clip_on=False)
            y += 1.05
            first_sep = True
        elif it[0] == "sep":
            if not first_sep:
                ax.axhline(y + 0.05, color=F.TEXT2, linewidth=0.6, linestyle="--",
                           xmin=-(label_w - 0.02) / (0.985 - label_w), clip_on=False)
            ax.annotate(it[1], xy=(0, y + 0.4), xycoords=("figure fraction", "data"), xytext=(20, 0),
                        textcoords="offset points", ha="left", va="center", fontsize=7, style="italic", color=F.TEXT2)
            y += 0.7
            first_sep = False
        else:
            _, lab, recs, texts = it
            for j, (rec, t) in enumerate(zip(recs, texts)):
                status_cell(ax, xs[j], y, rec, t)
            ticks.append(y + 0.45)
            labs.append(lab)
            y += 1
    decorate(ax, xs, W, y, None, cols=cols)
    ax.set_yticks(ticks, labs, fontsize=7)
    status_legend(fig)
    figs.head(fig, title, subtitle)
    return figs.save(fig, name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    de = L["de"]
    CL = class_listing(L)
    R = rows_table(L, CL)
    slices = {(s, t): de[(de.short_name == s) & (de.timepoint == t)].set_index("locus_tag") for _, s, t, _ in COLS}
    C = pd.DataFrame([c for r in R.itertuples() for c in cell_records(slices, r.row_id, r.loci)])
    C = C.merge(R[["row_id", "label", "category"]], on="row_id")
    C.to_csv(OUT / "e10_cells.csv", index=False)
    P = C.pivot_table(index="row_id", columns="column", values="median_percentile", aggfunc="first").reindex(columns=COLNAMES)
    S = C.pivot_table(index="row_id", columns="column", values="status", aggfunc="first").reindex(columns=COLNAMES)
    valid_cols = [c[3] for c in COLS if c[1] != "cal_read_ndep"]
    n_imputed = int(P[valid_cols].isna().sum().sum())
    Z = linkage(P[valid_cols].fillna(0.5).values, method="average", metric="euclidean")
    # flags (E14: all axenic samples)
    frows, ndep_cols = [], [c for c in COLNAMES if c.startswith("Tolonen N-dep")]
    AX31, AX89, AXR = "protein ax d31 (death)", "protein ax d89 (death)", "RNA ax d14"
    cc_st = {d_: slices[("anchor_cocult_protein", f"day {d_}")].expression_status for d_ in (60, 89)}
    loci_of = dict(zip(R.row_id, R.loci))
    for rid in R.row_id:
        d = {"cc_d60_status": S.loc[rid, "protein cc d60"], "cc_d89_status": S.loc[rid, "protein cc d89"],
             "ax_d14_status": S.loc[rid, "protein ax d14"], "ax_d31_status": S.loc[rid, AX31],
             "ax_d89_status": S.loc[rid, AX89], "ax_rna_d14_status": S.loc[rid, AXR],
             "ndep_statuses": list(S.loc[rid, ndep_cols]),
             "ax_d14_pct": P.loc[rid, "protein ax d14"], "ndep_max_pct": P.loc[rid, ndep_cols].max()}
        strict, loose = ex.coculture_flags(d)
        u60, u89 = (ex.up_loci(cc_st[k], loci_of[rid]) for k in (60, 89))
        frows.append({"row_id": rid, "flag_strict": strict, "flag_loose": loose,
                      "cc_d60_protein": d["cc_d60_status"], "cc_d89_protein": d["cc_d89_status"],
                      "cc_d60_pct": P.loc[rid, "protein cc d60"], "cc_d89_pct": P.loc[rid, "protein cc d89"],
                      "ax_d14_protein": d["ax_d14_status"], "ax_d14_pct": d["ax_d14_pct"],
                      "ax_d31_protein": d["ax_d31_status"], "ax_d31_pct": P.loc[rid, AX31],
                      "ax_d89_protein": d["ax_d89_status"], "ax_d89_pct": P.loc[rid, AX89],
                      "ax_rna_d14": d["ax_rna_d14_status"], "ax_rna_d14_pct": P.loc[rid, AXR],
                      "ndep_statuses": "|".join(d["ndep_statuses"]), "ndep_max_pct": d["ndep_max_pct"],
                      "rna_cc_d60": S.loc[rid, "RNA cc d60"], "rna_cc_d89": S.loc[rid, "RNA cc d89"],
                      "direct_d11": S.loc[rid, "same study d11 (exponential)"],
                      "direct_d18": S.loc[rid, "same study d18 (cc d18 vs ax ~d14)"],
                      "n_members": len(loci_of[rid]),
                      "cc_up_subunits": f"d60: {', '.join(u60) or 'none'}; d89: {', '.join(u89) or 'none'}"})
    FL = pd.DataFrame(frows).merge(R[["row_id", "label", "category"]], on="row_id")
    R = R.merge(FL[["row_id", "flag_strict", "flag_loose"]], on="row_id")
    R["mark"] = np.where(R.flag_strict, "★ ", np.where(R.flag_loose, "☆ ", ""))
    FL[FL.flag_strict | FL.flag_loose].to_csv(OUT / "e10_flags.csv", index=False)
    FL.to_csv(OUT / "e10_flags_all.csv", index=False)
    R.assign(loci=R.loci.map("|".join), classes=R.classes.map("|".join)).to_csv(OUT / "e10_rows.csv", index=False)
    ids = list(P.index)
    CLU = pd.DataFrame({"row_id": ids, "n_imputed_cells_total": n_imputed,
                        **{f"branch_k{k}": fcluster(Z, k, criterion="maxclust") for k in (2, 3, 4, 6)}})
    CLU["leaf_order"] = CLU.row_id.map({r: i for i, r in enumerate(dendrogram(Z, no_plot=True, labels=ids)["ivl"])})
    CLU = CLU.merge(R[["row_id", "label", "category"]], on="row_id").sort_values("leaf_order")
    CLU.to_csv(OUT / "e10_clusters.csv", index=False)
    lab_of = dict(zip(R.row_id, R["mark"] + R.label))
    files = draw_matrix(C, R, lab_of, Z, ids, "clustered") + draw_matrix(C, R, lab_of, None, ids, "grouped")

    # ---- add-on A: by class
    Ci = C.set_index(["row_id", "column"])
    Rr = R.set_index("row_id")
    recs_of = {rid: [Ci.loc[(rid, c)] for c in COLNAMES] for rid in R.row_id}
    items, bc_rows, skipped = [], [], []
    basis_rank = {"dedicated": 0, "broad listing": 1}
    for c in CLASS_ORDER + ["non-N reference transporters"]:
        if c == "non-N reference transporters":
            sel = pd.DataFrame({"system_id": NON_N_IDS, "listing_basis": "non-N reference", "class_source": "e6b map"})
        else:
            sel = CL[CL.compound_class == c].drop_duplicates("system_id").copy()
            sel = sel[sel.system_id.isin(Rr.index)]
            if sel.empty:
                skipped.append(c)
                continue
            sel = sel.assign(k=sel.listing_basis.map(basis_rank)).sort_values(["k", "system_id"])
        items.append(("panel", c))
        prev = None
        for s in sel.itertuples():
            if c != "non-N reference transporters" and s.listing_basis != prev:
                items.append(("sep", "dedicated" if s.listing_basis == "dedicated" else "broad listing"))
                prev = s.listing_basis
            r = Rr.loc[s.system_id]
            others = [k for k in r.classes if k != c]
            lab = (r["mark"] + r.base + r.tags + f" [{r.tier[0]}]"
                   + (f"  ◆ multi-class ({len(r.classes)}): {', '.join(others)}" if len(r.classes) > 1 else ""))
            items.append(("row", lab, recs_of[s.system_id], [count_text(x) for x in recs_of[s.system_id]]))
            bc_rows.append({"class": c, "system_id": s.system_id, "system": r.base, "listing_basis": s.listing_basis,
                            "class_source": s.class_source, "tier": r.tier, "tags": r.tags.strip(),
                            "multiclass": "|".join(r.classes) if len(r.classes) > 1 else "",
                            "flag": r["mark"].strip(), **{col: x["status"] for col, x in zip(COLNAMES, recs_of[s.system_id])}})
    BC = pd.DataFrame(bc_rows)
    BC.to_csv(OUT / "e10_by_class.csv", index=False)
    files += draw_panels(items, "e10_by_class", "MED4 transport systems by N class: status across all experiments",
                         "Source: data/explore/e10_by_class.csv (data/explore/e10_cells.csv; methods v1.6.1). Organic classes: "
                         "p18 listing basis (High/Medium). Inorganic classes (ammonium–nitrate): fig2 Block A rows (most_specific "
                         "or inherited from a non-lumping family, High/Medium) with the p18 dedicated rule.\n"
                         "A system appears in every class it lists; ◆ multi-class (n) names the other classes. "
                         "Cell = count significant in the shown direction / n detected subunits. " + AHARONOVICH_NOTE
                         + (f" No High/Medium system: {', '.join(skipped)}." if skipped else
                            " Every class listed has ≥1 High/Medium system (none skipped).")
                         + "\n★ strict / ☆ loose coculture-specific candidate, all axenic samples considered (e10_flags.csv). [efflux], [FP] = methods flags; [H]/[M] = tier.",
                         label_w=0.40, width=20)

    # ---- add-on B: per gene
    roles = pd.read_csv(ex.MD / "med4" / "p2_med4_gene_roles.csv").set_index("locus_tag")
    panels = [("amt1: ammonium transporter", L["mem"]["sys_PMM0263"]), ("urt: urea ABC transporter", L["mem"]["sys_PMM0970"]),
              ("cyn: cyanate ABC transporter", L["mem"]["sys_PMM0370"]),
              ("dpp: di/oligopeptide ABC transporter", L["mem"]["sys_PMM0192"]),
              ("urease ureA–G (urea → ammonium)", [u for u in ex.UREASE if u in L["names"]]),
              ("cynS (cyanase) + glsF (glutamate synthase)", ["PMM0373", "PMM1512"]),
              ("N-starvation markers", list(ex.MARKERS))]
    items, gene_rows = [], []
    for title, loci in panels:
        items.append(("panel", title))
        for lt in loci:
            recs = cell_records(slices, lt, [lt])
            texts = ["" if r_["median_percentile"] != r_["median_percentile"] else f"{r_['median_percentile']:.2f}".lstrip("0")
                     for r_ in recs]
            g = L["names"].get(lt, "")
            g = g if isinstance(g, str) and g and g != "nan" else str(roles["gene_name"].get(lt, "")).replace("nan", "")
            items.append(("row", f"{lt} {g}".strip(), recs, texts))
            gene_rows += [{"panel": title, "locus_tag": lt, "gene_name": g, **rec} for rec in recs]
    pd.DataFrame(gene_rows).rename(columns={"median_percentile": "rank_percentile"}).to_csv(OUT / "e10_by_gene.csv", index=False)
    files += draw_panels(items, "e10_by_system_dedicated", "MED4 dedicated N systems, linked enzymes and markers: per-gene status",
                         "Source: data/explore/e10_by_gene.csv (analysis/data/de_long.csv.gz). One row per gene; cell colour = the "
                         "gene's own stored expression_status;\nnumber = its rank percentile in that slice (none for filtered Read "
                         "tables). " + AHARONOVICH_NOTE, label_w=0.20, width=17)

    for f in files:
        print(f.name)
    print("rows", len(R), "imputed cells", n_imputed, "skipped classes", skipped)
    for k in ("branch_k2", "branch_k4", "branch_k6"):
        for b, g in CLU.groupby(k, sort=False):
            print(k, b, len(g), " ; ".join(g.label))
    pd.set_option("display.width", 300)
    print(FL[FL.flag_strict | FL.flag_loose].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
