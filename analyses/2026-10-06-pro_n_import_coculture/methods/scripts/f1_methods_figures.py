"""Figures for the methods-milestone review (no KG calls; reads data/<tag>/ and data/p15_* only).

Writes figures/fig1..fig6 as PNG (300 dpi) and SVG.
Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/f1_methods_figures.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402

from common import nt  # noqa: E402

HERE = Path(__file__).resolve().parent
M = HERE.parent
D = M / "data"
OUT = M / "figures"
TAGS = ["med4", "mit9313", "natl2a"]
LABEL = {"med4": "MED4", "mit9313": "MIT9313", "natl2a": "NATL2A"}
REF = "gap200_roleT_crossT"

SURF, TEXT, TEXT2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e5e4df"
CAT = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
TIERS = ["High", "Medium", "Low", "not_transporter"]
TIER_C = {"High": "#1c5cab", "Medium": "#3987e5", "Low": "#86b6ef", "not_transporter": "#d9d8d3", "none": "#f0efec"}
TIER_H = {"High": "", "Medium": "//", "Low": "..", "not_transporter": "xx", "none": ""}
TIER_SHORT = {"High": "H", "Medium": "M", "Low": "L", "not_transporter": "NT"}
TIER_TXT = {"High": SURF, "Medium": TEXT, "Low": TEXT, "not_transporter": TEXT, "none": TEXT2}
N_CLASSES = ["ammonium", "urea", "cyanate", "nitrite", "nitrate", "peptides", "amino acids", "amino sugars",
             "polyamines", "nucleobases/nucleosides", "osmolytes", "amines"]
ORGANIC = {"peptides", "amino acids", "amino sugars", "polyamines", "nucleobases/nucleosides", "osmolytes", "amines"}
GAP_LW = 1.5  # ~2 px surface gap between stacked segments

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans", "Arial"], "font.size": 9,
    "text.color": TEXT, "axes.labelcolor": TEXT, "xtick.color": TEXT2, "ytick.color": TEXT,
    "axes.edgecolor": GRID, "axes.facecolor": SURF, "figure.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False, "grid.color": GRID,
    "grid.linewidth": 0.6, "hatch.color": "#52514e", "hatch.linewidth": 0.5, "svg.fonttype": "none",
    "legend.frameon": False, "legend.fontsize": 9,
})


def head(fig, title, subtitle):
    fig.text(0.01, 0.985, title, ha="left", va="top", fontsize=12, fontweight="bold", color=TEXT)
    fig.text(0.01, 0.945, subtitle, ha="left", va="top", fontsize=9, color=TEXT2)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=300)
    plt.close(fig)
    return [OUT / f"{name}.png", OUT / f"{name}.svg"]


def xgrid(ax):
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0)


def seg(ax, y, left, width, color, hatch="", h=0.5):
    ax.barh(y, width, left=left, height=h, color=color, hatch=hatch, edgecolor=SURF, linewidth=GAP_LW)


def load(tag):
    d = D / tag
    return {
        "sys": pd.read_csv(d / f"p11_{tag}_systems.csv"),
        "cls": pd.read_csv(d / f"p12_{tag}_system_substrates_classified.csv", low_memory=False),
        "cc": pd.read_csv(d / f"p12_{tag}_compound_classes.csv"),
        "fl": pd.read_csv(d / f"p11_{tag}_function_linked.csv"),
        "nl": pd.read_csv(d / f"p11_{tag}_neighbour_linked.csv"),
        "uni": pd.read_csv(d / f"p2c_{tag}_universe.csv"),
        "p3": pd.read_json(d / f"p3_{tag}_summary.json", typ="series"),
        "coords": pd.read_csv(d / "raw" / f"p3_{tag}_genome_coords.csv"),
        "gs": pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv"),
        "lb": pd.read_csv(d / f"p18_{tag}_listing_basis.csv"),
        "roles": pd.read_csv(d / f"p2_{tag}_gene_roles.csv"),
    }


DATA = {t: load(t) for t in TAGS}


# --------------------------------------------------------------------------- fig1
def fig1():
    fig, axes = plt.subplots(3, 1, figsize=(8, 6.2), sharex=True)
    xmax = max(int(DATA[t]["p3"]["list_organisms_gene_count"]) for t in TAGS)
    for ax, t in zip(axes, TAGS):
        x = DATA[t]
        genes = int(x["p3"]["list_organisms_gene_count"])
        uni = len(x["uni"])
        nsys = len(x["sys"])
        tc = x["sys"].tier.value_counts()
        stages = [("genes in KG", genes), ("transporter universe", uni), ("systems", nsys)]
        for i, (lab, v) in enumerate(stages):
            seg(ax, i, 0, v, "#a9a8a2")
            ax.text(v + xmax * 0.01, i, f"{v:,}", va="center", color=TEXT, fontsize=9)
        left = 0
        for k in TIERS:
            v = int(tc.get(k, 0))
            seg(ax, 3, left, v, TIER_C[k], TIER_H[k])
            left += v
        ax.text(left + xmax * 0.01, 3, "   ".join(f"{TIER_SHORT[k]} {int(tc.get(k, 0))}" for k in TIERS),
                va="center", fontsize=9, color=TEXT)
        ax.set_ylim(3.85, -0.5)
        ax.set_yticks(range(4), [s[0] for s in stages] + ["systems by tier"])
        ax.set_title(LABEL[t], loc="left", fontsize=10, color=TEXT, pad=2)
        xgrid(ax)
    axes[-1].set_xlabel("count")
    axes[-1].set_xlim(0, xmax * 1.1)
    handles = [Patch(facecolor=TIER_C[k], hatch=TIER_H[k], edgecolor=SURF, label=f"{k} ({TIER_SHORT[k]})") for k in TIERS]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.0))
    head(fig, "From genome to tiered transport systems",
         "Source: data/<strain>/p3_<strain>_summary.json (genes), p2c_<strain>_universe.csv, p11_<strain>_systems.csv")
    fig.subplots_adjust(left=0.2, right=0.97, top=0.86, bottom=0.12, hspace=0.45)
    return save(fig, "fig1_build_funnel")


# --------------------------------------------------------------------------- fig2
RANK = {k: i for i, k in enumerate(TIERS)}


def short_names(member_names, n=4):
    names = []
    for m in str(member_names).split("|"):
        lt, _, g = m.partition(":")
        names.append(g if g and g != "nan" else lt)
    s = "/".join(names[:n])
    return s + ("/…" if len(names) > n else "")


def system_basis(t, sid, cls):
    """p18 rule (nt.listing_basis, efflux-aware) for any system and class; used for the Block A '+k' split."""
    x = DATA[t]
    loci = sorted(x["gs"][x["gs"].system_id == sid].locus_tag)
    r = x["roles"].set_index("locus_tag")
    qs = [q for lt in loci for q in nt.parse_list(r.cyanorak_q_roles.get(lt)) if q != nt.NO_BASIS]
    eff = bool(x["sys"].set_index("system_id").efflux_annotated[sid])
    return nt.listing_basis(cls, [r.gene_name.get(lt) for lt in loci], [r["product"].get(lt) for lt in loci], qs,
                            efflux=eff)[0]


def fig2_cells():
    """Cell states for fig2 (coordinator spec v2). Eligible rows: substrate_depth most_specific, OR inherited
    from a non-lumping family; carrying system tier High/Medium/Low; system not known_false_positive."""
    cells, notes = {}, []
    for t in TAGS:
        x = DATA[t]
        sy = x["sys"].set_index("system_id")
        a = x["cls"].copy()
        lump = a.is_lumping.astype(str).str.lower().eq("true")
        a["tier"] = a.system_id.map(sy.tier)
        a["kfp"] = a.system_id.map(sy.known_false_positive).astype(bool)
        elig = a[((a.substrate_depth == "most_specific") | ((a.substrate_depth == "inherited") & ~lump))
                 & a.tier.isin(["High", "Medium", "Low"]) & ~a.kfp]
        fl, nl = x["fl"], x["nl"]
        for c in INORG + ORG:
            r = elig[elig.compound_class_final == c]
            groups = set(r.equiv_group)
            rec = {"strain": t, "block": "inorganic" if c in INORG else "organic", "class": c,
                   "n_eligible_rows": int(len(r)), "n_eligible_systems": int(r.system_id.nunique()),
                   "eligible_systems": "|".join(sorted(set(r.system_id)))}
            if c in INORG:
                rule = ("eligible rows; usable = can_use_window in {co-located, elsewhere in genome}; "
                        "best = highest tier, then most non-fragment links")
                u = r[r.can_use_window.isin(["co-located", "elsewhere in genome"])]
                rec["n_usable_rows"] = int(len(u))
                if r.empty:
                    cell = {"state": "none", "tier": "none", "text": ""}
                elif u.empty:
                    ss = r.drop_duplicates("system_id").assign(rk=lambda d: d.tier.map(RANK)).sort_values(["rk", "system_id"])
                    hm = ss[ss.tier.isin(["High", "Medium"])]
                    if len(hm):
                        ex = [short_names(sy.member_names[s], 3) for s in hm.system_id[:3]]
                        txt = "e.g. " + "; ".join(ex)
                    else:   # v1.6.1: no High/Medium system -> best tier, labelled
                        best = ss[ss["rk"] == ss["rk"].min()]
                        ex = [short_names(sy.member_names[s], 3) for s in best.system_id[:3]]
                        txt = f"best ({best.tier.iloc[0]}): " + "; ".join(ex)
                    cell = {"state": "listed, not usable", "tier": "listed", "text": txt, "examples": "; ".join(ex)}
                else:
                    cand = pd.DataFrame({"system_id": sorted(set(u.system_id))})
                    cand["rank"] = cand.system_id.map(sy.tier).map(RANK)
                    cand["nlinks"] = [int(((fl.system_id == s) & fl.equiv_group.isin(groups) & (fl.fragment_of == "none")).sum()
                                          + ((nl.system_id == s) & nl.equiv_group.isin(groups) & (nl.fragment_of == "none")).sum())
                                      for s in cand.system_id]
                    cand = cand.sort_values(["rank", "nlinks", "system_id"], ascending=[True, False, True])
                    b = cand.iloc[0].system_id
                    same = int((cand["rank"] == cand.iloc[0]["rank"]).sum()) - 1
                    nn = sorted(set(nl[(nl.system_id == b) & nl.equiv_group.isin(groups) & (nl.fragment_of == "none")].enzyme_name.astype(str)))
                    ff = sorted(set(fl[(fl.system_id == b) & fl.equiv_group.isin(groups) & (fl.fragment_of == "none")].enzyme_name.astype(str)))
                    enz = ([("N: " + "/".join(nn))] if nn else []) + ([("F: " + "/".join(ff))] if ff else [])
                    others = cand[(cand["rank"] == cand.iloc[0]["rank"]) & (cand.system_id != b)].system_id
                    obasis = [system_basis(t, s, c) for s in others]
                    nd, nb = sum(x == "dedicated" for x in obasis), sum(x != "dedicated" for x in obasis)
                    lines = [short_names(sy.member_names[b]), f"(+{nd} dedicated, +{nb} broad)"]
                    if enz:
                        lines.append("  ".join(enz))
                    cell = {"state": "usable system", "tier": sy.tier[b], "text": "\n".join(lines), "best_system": b,
                            "best_listing_basis": system_basis(t, b, c), "same_tier_dedicated": nd, "same_tier_broad": nb,
                            "linked": "  ".join(enz), "other_usable_same_tier": same}
            else:
                rule = ("p18 listing basis: (system, class) pairs from most_specific, non-lumping rows of High/Medium "
                        "systems, known false positives excluded; dedicated = class keyword in a member product / gene "
                        "name or corresponding Cyanorak Q role (Q.1, Q.5); otherwise broad listing; can_use not testable")
                lb = x["lb"]
                z = lb[(lb.compound_class == c) & ~lb.known_false_positive.astype(bool)]
                ded, brd = z[z.listing_basis == "dedicated"], z[z.listing_basis == "broad listing"]
                dh, dm = int((ded.tier == "High").sum()), int((ded.tier == "Medium").sum())
                bh, bm = int((brd.tier == "High").sum()), int((brd.tier == "Medium").sum())
                ded = ded.assign(rk=ded.tier.map(RANK)).sort_values(["rk", "system_id"])
                ex = [short_names(m, 3) for m in ded.member_names[:2]]
                if z.empty:
                    cell = {"state": "none", "tier": "none", "text": ""}
                else:
                    lines = [f"dedicated: H {dh} · M {dm}"] + (["e.g. " + "; ".join(ex)] if ex else [])
                    cell = {"state": "dedicated listing" if len(ded) else "broad listing only", "tier": "organic",
                            "text": "\n".join(lines), "muted": f"broad listing: H {bh} · M {bm}",
                            "dedicated_H": dh, "dedicated_M": dm, "broad_H": bh, "broad_M": bm,
                            "dedicated_systems": " || ".join(ded.member_names), "broad_systems": " || ".join(brd.member_names),
                            "examples": "; ".join(ex)}
            cells[(c, t)] = cell
            notes.append({**rec, **{k: v for k, v in cell.items() if k not in ("text", "muted")}, "rule": rule})
    pd.DataFrame(notes).to_csv(OUT / "fig2_cells.csv", index=False)
    return cells


INORG = ["ammonium", "urea", "cyanate", "nitrite", "nitrate"]
ORG = ["amino acids", "peptides", "amino sugars", "polyamines", "nucleobases/nucleosides", "osmolytes", "amines"]
Q1_CLASSES = {"amino acids", "peptides", "amines", "polyamines"}
CELL_C = {**TIER_C, "listed": "#d9d8d3", "organic": "#e5e4df"}
CELL_H = {**TIER_H, "listed": "\\\\\\\\", "organic": "---"}
CELL_TXT = {**TIER_TXT, "listed": TEXT, "organic": TEXT}


def fig2():
    OUT.mkdir(parents=True, exist_ok=True)
    cells = fig2_cells()
    fig, ax = plt.subplots(figsize=(10.5, 11.5))
    rows = [("hdr", "(A) Inorganic N: best usable system (can_use tested)")] + [("c", c) for c in INORG] \
        + [("hdr", "(B) Organic N: dedicated vs broad listing (can_use not testable)")] + [("c", c) for c in ORG]
    ys, labels = [], []
    y = 0.0
    for kind, v in rows:
        if kind == "hdr":
            ax.text(-0.02, y + 0.45, v, ha="left", va="center", fontsize=10, fontweight="bold", color=TEXT,
                    transform=ax.transData)
            y += 0.6
            continue
        for j, t in enumerate(TAGS):
            cell = cells[(v, t)]
            st = cell["tier"]
            ax.add_patch(Rectangle((j + 0.02, y + 0.03), 0.96, 0.94, facecolor=CELL_C[st], hatch=CELL_H[st],
                                   edgecolor=SURF, linewidth=GAP_LW))
            tag = {"listed": "listed, not usable", "organic": cell.get("state", ""), "none": "none"}.get(st, st)
            ax.text(j + 0.05, y + 0.08, tag, ha="left", va="top", fontsize=7.5, color=CELL_TXT[st], fontweight="bold",
                    bbox=dict(facecolor=CELL_C[st], edgecolor="none", pad=1) if st in ("listed", "organic") else None)
            if cell.get("muted"):
                ax.text(j + 0.5, y + 0.86, cell["muted"], ha="center", va="center", fontsize=7.2, color=TEXT2,
                        style="italic", bbox=dict(facecolor=CELL_C[st], edgecolor="none", pad=1))
            if cell["text"]:
                ax.text(j + 0.5, y + (0.5 if cell.get("muted") else 0.6), cell["text"], ha="center", va="center", fontsize=7.8, color=CELL_TXT[st],
                        linespacing=1.25,
                        bbox=dict(facecolor=CELL_C[st], edgecolor="none", pad=1.5) if st in ("listed", "organic", "Low", "Medium") else None)
        ys.append(y + 0.5)
        labels.append(v)
        y += 1
    ax.set_xlim(0, len(TAGS))
    ax.set_ylim(y, 0)
    ax.set_xticks([j + 0.5 for j in range(len(TAGS))], [LABEL[t] for t in TAGS], fontsize=10)
    ax.xaxis.tick_top()
    ax.set_yticks(ys, labels)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    handles = [Patch(facecolor=TIER_C[k], hatch=TIER_H[k], edgecolor=TEXT2, linewidth=0.3, label=f"usable: {k}")
               for k in ("High", "Medium", "Low")] + [
        Patch(facecolor=CELL_C["listed"], hatch=CELL_H["listed"], edgecolor=TEXT2, linewidth=0.3,
              label="listed, not usable (can_use = no)"),
        Patch(facecolor=CELL_C["organic"], hatch=CELL_H["organic"], edgecolor=TEXT2, linewidth=0.3,
              label="organic N: TCDB listing only, not verified"),
        Patch(facecolor=TIER_C["none"], edgecolor=TEXT2, linewidth=0.3, label="none")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.55, 0.085))
    head(fig, "N compound classes: what the annotation supports",
         "Source: data/<strain>/p12_<strain>_system_substrates_classified.csv, p11_<strain>_systems.csv,\n"
         "p11_<strain>_function_linked.csv, p11_<strain>_neighbour_linked.csv, p18_<strain>_listing_basis.csv")
    fig.text(0.01, 0.008,
             "(A) rows: most_specific, or inherited from a non-lumping family; systems High/Medium/Low, not known false positives.\n"
             "(A) usable = can_use_window co-located or elsewhere in genome; best = highest tier, then most links; "
             "+k dedicated / +k broad = other usable systems at that tier, split by the (B) rule;\nN: neighbour-linked, F: function-linked enzymes (fragments excluded).\n"
             "(B) High/Medium systems on most_specific non-lumping rows, known false positives excluded; dedicated = class keyword in a\n"
             "member product / gene name, or curated Cyanorak Q.1 / Q.5 role unless efflux-annotated (data/p18_class_keyword_map.csv); broad (muted) = neither.\n"
             "organic N: can_use not testable (no KEGG reactions on peptides; classes by name only, KG has no chemical categories)",
             fontsize=8, color=TEXT2, ha="left", va="bottom", linespacing=1.4)
    fig.subplots_adjust(left=0.2, right=0.98, top=0.88, bottom=0.19)
    return save(fig, "fig2_n_systems_matrix")


# --------------------------------------------------------------------------- fig3
def fig3():
    tc = pd.read_csv(D / "p15_tier_counts.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(11, 5.2), gridspec_kw={"width_ratios": [1.3, 1]})
    ylabels, y = [], 0
    for t in TAGS:
        for when in ("before", "after"):
            left = 0
            for k in TIERS:
                v = int(tc[(tc.strain == t) & (tc.tier == k)][when].sum())
                seg(a, y, left, v, TIER_C[k], TIER_H[k], h=0.6)
                if v >= 12:
                    a.text(left + v / 2, y, str(v), ha="center", va="center", fontsize=7.5,
                           color=TIER_TXT[k])
                left += v
            ylabels.append(f"{LABEL[t]} {'v1.3.0' if when == 'before' else 'v1.4.0'}")
            y += 1
        y += 0.5
    ys = [0, 1, 2.5, 3.5, 5, 6]
    a.set_yticks(ys, ylabels)
    a.set_ylim(6.6, -0.6)
    a.set_xlabel("systems")
    a.set_title("(a) tiers before / after the catalogue-only fix", loc="left", fontsize=10)
    xgrid(a)
    # (b) High-tier rate within single- vs multi-gene systems (High + Medium only)
    rows = []
    for t in TAGS:
        s = DATA[t]["sys"]
        s = s[s.tier.isin(["High", "Medium"])]
        for kind, sub in (("single-gene", s[s.n_genes == 1]), ("multi-gene", s[s.n_genes > 1])):
            rows.append({"strain": t, "kind": kind, "High": int((sub.tier == "High").sum()),
                         "Medium": int((sub.tier == "Medium").sum())})
    r = pd.DataFrame(rows)
    r.to_csv(OUT / "fig3b_counts.csv", index=False)
    yb = 0
    yl, ypos = [], []
    for t in TAGS:
        for kind in ("single-gene", "multi-gene"):
            q = r[(r.strain == t) & (r.kind == kind)].iloc[0]
            n = q.High + q.Medium
            left = 0
            for k in ("High", "Medium"):
                frac = q[k] / n if n else 0
                seg(b, yb, left, frac, TIER_C[k], TIER_H[k], h=0.6)
                left += frac
            b.text(1.02, yb, f"High {q.High}/{n} ({(q.High / n if n else 0):.0%})", va="center", fontsize=8, color=TEXT)
            yl.append(f"{LABEL[t]} {kind}")
            ypos.append(yb)
            yb += 1
        yb += 0.5
    b.set_yticks(ypos, yl)
    b.set_ylim(yb - 0.4, -0.6)
    b.set_xlim(0, 1.45)
    b.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "25%", "50%", "75%", "100%"])
    b.set_xlabel("share of High + Medium systems")
    b.set_title("(b) High-tier rate, single- vs multi-gene systems", loc="left", fontsize=10)
    xgrid(b)
    handles = [Patch(facecolor=TIER_C[k], hatch=TIER_H[k], edgecolor=SURF, label=k) for k in TIERS]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.0))
    head(fig, "Tier counts and the single- vs multi-gene check",
         "Source: data/p15_tier_counts.csv (a); data/<strain>/p11_<strain>_systems.csv, tiers High + Medium (b)")
    fig.subplots_adjust(left=0.13, right=0.97, top=0.82, bottom=0.17, wspace=0.55)
    return save(fig, "fig3_tiers_tradeoff")


# --------------------------------------------------------------------------- fig4
def fig4():
    cats = N_CLASSES + ["unclassified N", "unclassified (no formula)", "no_N"]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    rows = []
    for i, t in enumerate(TAGS):
        x = DATA[t]
        cc = x["cc"].compound_class.value_counts()
        a = x["cls"]
        nN = set(a[a.n_status != "no_N"].equiv_group)
        no_n = len(set(a[a.n_status == "no_N"].equiv_group) - nN)
        classified = int(sum(cc.get(c, 0) for c in N_CLASSES))
        parts = [("classified N (12 classes)", classified), ("unclassified N", int(cc.get("unclassified N", 0))),
                 ("unclassified (no formula)", int(cc.get("unclassified (no formula)", 0))), ("no_N", no_n)]
        tot = sum(v for _, v in parts)
        left = 0
        for j, (lab, v) in enumerate(parts):
            seg(ax, i, left, v, CAT[j], ["", "//", "..", "xx"][j], h=0.55)
            ax.text(left + v / 2, i - 0.36, f"{v}", ha="center", va="bottom", fontsize=8, color=TEXT)
            left += v
        unc = parts[1][1] + parts[2][1]
        ax.text(tot + 20, i, f"unclassified: {parts[1][1]} N + {parts[2][1]} no-formula,\nof {tot - no_n} groups that are N or unknown",
                va="center", fontsize=8.5, color=TEXT)
        rows.append({"strain": t, **{lab: v for lab, v in parts}})
        _ = cats
    pd.DataFrame(rows).to_csv(OUT / "fig4_counts.csv", index=False)
    ax.set_yticks(range(3), [LABEL[t] for t in TAGS])
    ax.set_ylim(2.6, -0.7)
    ax.set_xlabel("substrate groups (equivalence groups): N, N unknown, or no N")
    mx = max(sum(v for k, v in r.items() if k != "strain") for r in rows)
    ax.set_xlim(0, mx * 1.45)
    xgrid(ax)
    handles = [Patch(facecolor=CAT[j], hatch=["", "//", "..", "xx"][j], edgecolor=SURF, label=lab)
               for j, lab in enumerate(["classified N (12 classes)", "unclassified N (formula has N)",
                                        "unclassified, no formula (N unknown)", "no N (formula without N)"])]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.0))
    head(fig, "Substrate groups by compound class",
         "Source: data/<strain>/p12_<strain>_compound_classes.csv (N groups), "
         "p12_<strain>_system_substrates_classified.csv (no_N groups)")
    fig.text(0.01, 0.885, "best effort: classes by name only (KG has no chemical categories)", fontsize=8, color=TEXT2)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.8, bottom=0.25)
    return save(fig, "fig4_compound_classes")


# --------------------------------------------------------------------------- fig5
CASES = [  # label, strain, anchor locus, enzyme gene names, substrate name, expected
    ("cynS → cyn (cyanate)", "med4", "PMM0371", ["cynS"], "Cyanate", "yes"),
    ("ureC/B/A → urt (urea)", "med4", "PMM0972", ["ureC", "ureB", "ureA"], "Urea", "yes"),
    ("pncC → amt1 (ammonia)", "med4", "PMM0263", ["pncC"], "Ammonia", "no"),
    ("glnA/glsF → amt1 (ammonia)", "med4", "PMM0263", ["glnA", "glsF"], "Ammonia", "yes (expression partner)"),
    ("nirA → focA (nitrite, MIT9313)", "mit9313", "PMT2240", ["nirA"], "Nitrite", "yes"),
]
RULES = ["(a) ±8 window", "(b) same-strand run", "(c) window minus\nubiquitous\n[neighbour-linked]",
         "(d) shared Cyanorak\nrole [function-linked,\nGS/GOGAT allow-list]"]


def fig5_values():
    out = []
    for lab, t, anchor, genes, sub, exp in CASES:
        x = DATA[t]
        sid = x["gs"].set_index("locus_tag").system_id[anchor]
        co = x["coords"]
        loci = list(co[co.gene_name.isin(genes)].locus_tag)
        a = x["cls"]
        r = a[(a.system_id == sid) & (a.metabolite_name == sub)]
        groups = set(r.equiv_group)

        def from_col(col):
            s = set()
            for v in r[col].dropna():
                s |= set(str(v).split("|"))
            return s

        w, run = from_col("linked_enzyme_loci_window"), from_col("linked_enzyme_loci_run")
        nl = x["nl"][(x["nl"].system_id == sid) & x["nl"].equiv_group.isin(groups)]
        fl = x["fl"][(x["fl"].system_id == sid) & x["fl"].equiv_group.isin(groups)]
        vals = [sum(lt in w for lt in loci), sum(lt in run for lt in loci),
                sum(lt in set(nl.locus_tag) for lt in loci), sum(lt in set(fl.locus_tag) for lt in loci)]
        out.append({"case": lab, "strain": t, "system_id": sid, "enzyme_loci": "|".join(loci), "n_enzymes": len(loci),
                    "a_window": vals[0], "b_run": vals[1], "c_neighbour_linked": vals[2], "d_function_linked": vals[3],
                    "expected": exp})
    df = pd.DataFrame(out)
    df.to_csv(OUT / "fig5_values.csv", index=False)
    return df


def fig5():
    OUT.mkdir(parents=True, exist_ok=True)
    df = fig5_values()
    fig, ax = plt.subplots(figsize=(11, 5))
    cols = ["a_window", "b_run", "c_neighbour_linked", "d_function_linked"]
    nr = len(df)
    for i, r in df.iterrows():
        for j, c in enumerate(cols):
            k, n = int(r[c]), int(r.n_enzymes)
            ok = k == n and n > 0
            part = 0 < k < n
            fc = "#86b6ef" if ok else ("#d9d8d3" if part else "#f0efec")
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=fc, edgecolor=SURF, linewidth=GAP_LW,
                                   hatch="" if ok else ("//" if part else "")))
            txt = "✓ linked" if ok else (f"{k}/{n} linked" if part else "✗ not linked")
            ax.text(j + 0.5, i + 0.5, txt, ha="center", va="center", fontsize=9, color=TEXT)
        ax.add_patch(Rectangle((4.15, i + 0.05), 1.3, 0.9, facecolor=SURF, edgecolor=GRID, linewidth=0.8))
        ax.text(4.8, i + 0.5, r.expected, ha="center", va="center", fontsize=9, color=TEXT, style="italic")
    ax.set_xlim(0, 5.5)
    ax.set_ylim(nr, 0)
    ax.set_xticks([j + 0.5 for j in range(4)] + [4.8], RULES + ["biologically\nexpected\n(researcher)"], fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(nr)], df.case)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    handles = [Patch(facecolor="#86b6ef", edgecolor=SURF, label="✓ linked (all enzymes)"),
               Patch(facecolor="#d9d8d3", hatch="//", edgecolor=SURF, label="some enzymes linked"),
               Patch(facecolor="#f0efec", edgecolor=GRID, label="✗ not linked")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.55, 0.0))
    head(fig, "Which linking rule links which enzyme",
         "(a),(b) from linked_enzyme_loci_window / _run in p12_<strain>_system_substrates_classified.csv; "
         "(c),(d) from p11_<strain>_neighbour_linked.csv / _function_linked.csv")
    fig.subplots_adjust(left=0.22, right=0.98, top=0.7, bottom=0.12)
    return save(fig, "fig5_linking_rules_tradeoff")


# --------------------------------------------------------------------------- fig6
LAYERS = [  # run order
    ("pilot vs answer key", [("issues fixed (steps 1, 3, 4, 6)", 8, 3)]),
    ("API-usage review", [("Critical", 2, 0), ("Important", 7, 1), ("Minor", 8, 2)]),
    ("fetch-helper re-review", [("Critical", 0, 0), ("Important", 2, 1), ("Minor", 7, 2)]),
    ("methods critic", [("Blocker", 2, 0), ("Concern", 8, 1), ("Note", 2, 2)]),
    ("delta critic", [("Blocker", 0, 0), ("Concern", 6, 1), ("Note", 4, 2)]),
]
SEV = {0: ("most severe (Critical / Blocker)", CAT[7], ""), 1: ("middle (Important / Concern)", CAT[3], "//"),
       2: ("least severe (Minor / Note)", CAT[0], ".."), 3: ("issue fixed (no severity scale)", CAT[2], "xx")}


def fig6():
    fig, ax = plt.subplots(figsize=(10, 4.4))
    for i, (layer, parts) in enumerate(LAYERS):
        left = 0
        for lab, v, s in parts:
            if v:
                seg(ax, i, left, v, SEV[s][1], SEV[s][2], h=0.5)
            left += v
        ax.text(left + 0.3, i, "  ".join(f"{lab} {v}" for lab, v, _ in parts), va="center", fontsize=8.5, color=TEXT)
    ax.set_yticks(range(len(LAYERS)), [x[0] for x in LAYERS])
    ax.set_ylim(len(LAYERS) - 0.4, -0.6)
    ax.set_xlim(0, 18)
    ax.set_xlabel("findings")
    xgrid(ax)
    handles = [Patch(facecolor=c, hatch=h, edgecolor=SURF, label=l) for l, c, h in SEV.values()]
    fig.legend(handles=handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.0))
    head(fig, "Findings per verification layer, in run order",
         "each layer caught a different class of error (counts from methods/notebook.md and critical_review.md)")
    fig.subplots_adjust(left=0.2, right=0.72, top=0.82, bottom=0.27)
    return save(fig, "fig6_verification_layers")


if __name__ == "__main__":
    files = []
    for f in (fig1, fig2, fig3, fig4, fig5, fig6):
        files += f()
    for p in files:
        print(p.relative_to(M))
