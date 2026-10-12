"""E6 controls and calibration in depth (descriptive).
(a) Tolonen N deprivation 0-48 h: log2FC / percentile heatmap for the MED4 dedicated N-system subunits, markers,
    urease, cynS, glsF and the non-N systems.
(b) Tolonen cyanate vs urea: percentile per gene, same set incl. markers.
(c) MED4 N-replete control ismej.2016.70: percentiles of the N-system subunits vs non-N subunits vs all genes.
(d) MIT9313, both inocula: its own dedicated N systems (methods p18 dedicated + fig2 Block A usable, as in stage 2)
    incl. natF/natG, vs its own non-N systems (pst, phn, sul1, sul3, fut/idiA2, mnt, lraI, sbtA by member gene name).
Percentiles are within-table ranks, so a table-wide negative skew moves all genes alike; group medians are compared
with the table median (0.5 by construction) and with the non-N group.
Outputs: data/explore/e6a_tolonen_ndep.csv, e6b_cyanate_urea.csv, e6cd_controls_genes.csv, e6cd_controls_summary.csv;
figures e6a_tolonen_ndep_heatmap, e6b_cyanate_vs_urea, e6cd_controls.
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
NONN_NAMES = r"^(pst[SCAB]|phn[CDE]|sul1|sul3|fut[ABC]|idiA2|mnt[ABC]|lraI|sbtA)$"
CAL_SUBTITLE = ("Sole-N experiments = steady-state exponential growth on the sole N source vs N-replete Pro99 medium; "
                "N deprivation = 24 h of nitrogen deprivation vs N-replete Pro99 medium (KG control / treatment fields).")
HEADERS_MED4 = {
    "amt1": "amt1: ammonium transporter (ammonium)",
    "urt": "urt: urea ABC transporter (urea)",
    "cyn": "cyn: cyanate ABC transporter (cyanate)",
    "dpp": "dpp: di/oligopeptide ABC transporter (peptides)",
    "urease": "urease ureA–G: urea → ammonium (enzyme)",
    "cynS / glsF": "cynS: cyanase, cyanate → ammonium (enzyme); glsF: glutamate synthase (enzyme)",
    "markers": "N-starvation markers (glnA glutamine synthetase, ntcA N-control regulator, glnB PII protein, pipX NtcA co-activator)",
    "non-N: pst": "pst: phosphate", "non-N: phn": "phn: phosphonate", "non-N: sul1": "sul1: sulfate",
    "non-N: sul3": "sul3: sulfate", "non-N: fut/idiA2": "fut/idiA2: iron", "non-N: mnt": "mnt: manganese",
    "non-N: lraI": "lraI: Mn/Zn", "non-N: sbtA": "sbtA: bicarbonate",
}


def med4_set(L):
    mem = L["mem"]
    rows = []
    for k, sid in ex.DEDICATED.items():
        rows += [(k, m) for m in mem[sid]]
    rows += [("urease", u) for u in ex.UREASE if u in L["names"]]
    rows += [("cynS / glsF", "PMM0373"), ("cynS / glsF", "PMM1512")]
    rows += [("markers", m) for m in ex.MARKERS]
    for k, sid in ex.NON_N.items():
        rows += [("non-N: " + k, m) for m in mem[sid]]
    return pd.DataFrame(rows, columns=["group", "locus_tag"])


def mit9313_sets():
    md = ex.MD / "mit9313"
    sy = pd.read_csv(md / "p11_mit9313_systems.csv").set_index("system_id")
    gs = pd.read_csv(md / f"p3_mit9313_gene_systems_{ex.REF}.csv")
    lb = pd.read_csv(md / "p18_mit9313_listing_basis.csv")
    ded = set(lb[(lb.listing_basis == "dedicated") & ~lb.known_false_positive.astype(bool)].system_id)
    f2 = pd.read_csv(ex.expr.METHODS / "figures" / "fig2_cells.csv")
    blk = set(f2[(f2.strain == "mit9313") & (f2.block == "inorganic") & f2.best_system.notna()].best_system)
    nsys = sorted(ded | blk)
    nonn_sys = sorted(set(gs[gs.gene_name.astype(str).str.match(NONN_NAMES)].system_id) - set(nsys))
    rows = [("N: " + ex.F_short(sy.loc[s, "member_names"]), r.locus_tag, r.gene_name) for s in nsys
            for r in gs[gs.system_id == s].itertuples()]
    rows += [("non-N: " + ex.F_short(sy.loc[s, "member_names"]), r.locus_tag, r.gene_name) for s in nonn_sys
             for r in gs[gs.system_id == s].itertuples()]
    return pd.DataFrame(rows, columns=["group", "locus_tag", "gene_name"])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    de, names = L["de"], L["names"]
    S = med4_set(L)
    S["gene_name"] = S.locus_tag.map(names)
    # (a)
    tps = ["0h", "3h", "6h", "12h", "24h", "48h"]
    a = []
    for tp in tps:
        x = ex.slice_values(de, "cal_tolonen_ndep", tp)
        for r in S.itertuples():
            v = x.loc[r.locus_tag] if r.locus_tag in x.index else None
            a.append({"timepoint": tp, "group": r.group, "locus_tag": r.locus_tag, "gene_name": r.gene_name,
                      "log2fc": None if v is None else v.log2fc, "rank_percentile": None if v is None else v.rank_percentile,
                      "expression_status": "not detected" if v is None else v.expression_status})
    A = pd.DataFrame(a)
    A.to_csv(OUT / "e6a_tolonen_ndep.csv", index=False)
    G = S.reset_index(drop=True)
    ys, y, prev = [], 0.0, None
    for g in G.group:
        if prev is not None and g != prev:
            y += 0.7
        ys.append(y)
        y += 1
        prev = g
    G["y"] = ys
    h = 0.17 * y + 2.2
    fig, axes = plt.subplots(1, 2, figsize=(10, h), sharey=True)
    norm = figs.TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
    for ax, (val, cmap, nrm, ttl) in zip(axes, (("log2fc", figs.DIVERGING, norm, "log2FC (clipped ±3)"),
                                                 ("rank_percentile", figs.PCT, None, "rank percentile"))):
        for j, tp in enumerate(tps):
            sub = A[A.timepoint == tp].set_index(["group", "locus_tag"])
            for r in G.itertuples():
                v = sub[val].get((r.group, r.locus_tag), np.nan)
                st = sub.expression_status.get((r.group, r.locus_tag), "not detected")
                if pd.isna(v):
                    ax.add_patch(plt.Rectangle((j, r.y), 0.96, 0.92, facecolor=F.SURF, edgecolor=F.GRID, hatch="///", linewidth=0.4))
                    continue
                vv = max(-3, min(3, v)) if val == "log2fc" else v
                ax.add_patch(plt.Rectangle((j, r.y), 0.96, 0.92, facecolor=cmap(nrm(vv)) if nrm else cmap(vv),
                                           edgecolor=F.SURF, linewidth=0.3))
                if st in (ex.SIG_UP, ex.SIG_DOWN):
                    ax.plot(j + 0.48, r.y + 0.46, marker="o" if st == ex.SIG_UP else "v", markersize=3,
                            color=figs.marker_color(vv, val == "rank_percentile"))
        ax.set_xlim(0, len(tps))
        ax.set_ylim(y, -0.5)
        ax.set_xticks([j + 0.48 for j in range(len(tps))], tps, fontsize=8)
        ax.xaxis.tick_top()
        ax.set_title(ttl, loc="left", fontsize=9, pad=18)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
    figs.add_cbar(fig, axes[0], figs.DIVERGING, norm, "log2FC (clipped at ±3)", pad=0.03)
    figs.add_cbar(fig, axes[1], figs.PCT, plt.Normalize(0, 1), "rank percentile, 0–1", pad=0.03)
    axes[0].set_yticks(G.y + 0.46, [f"{g or ''} {lt}".strip() for g, lt in zip(G.gene_name, G.locus_tag)], fontsize=6.5)
    for g, yy in G.groupby("group").y.min().items():
        axes[0].text(-0.06, yy - 0.15, g, transform=axes[0].get_yaxis_transform(), ha="right", va="bottom",
                     fontsize=6.8, fontweight="bold", color=F.TEXT2)
    figs.head(fig, "Tolonen N deprivation, 0–48 h (MED4 microarray)",
              "Source: analysis/data/de_long.csv.gz (cal_tolonen_ndep); data/explore/e6a_tolonen_ndep.csv.\n"
              "log2FC orange up / blue down; ● significant up, ▼ significant down (stored); hatched = not detected.")
    fig.subplots_adjust(left=0.28, right=0.99, top=1 - 1.4 / h, bottom=0.9 / h, wspace=0.05)
    files = figs.save(fig, "e6a_tolonen_ndep_heatmap")
    # (b) cyanate vs urea vs N deprivation 24 h (revised 2026-10-11: third bar, readable headers, N / non-N bands)
    cy = ex.slice_values(de, "cal_tolonen_cyanate", "steady state")
    ur = ex.slice_values(de, "cal_tolonen_urea", "steady state")
    nd24 = ex.slice_values(de, "cal_tolonen_ndep", "24h")
    B = S.copy()
    for k, x in (("cyanate", cy), ("urea", ur), ("ndep24h", nd24)):
        B[f"{k}_pct"] = B.locus_tag.map(x.rank_percentile)
        B[f"{k}_log2fc"] = B.locus_tag.map(x.log2fc)
        B[f"{k}_status"] = B.locus_tag.map(x.expression_status).fillna("not detected")
    B.to_csv(OUT / "e6b_cyanate_urea.csv", index=False)
    B[["group", "locus_tag", "gene_name"] + [f"{k}_{c}" for k in ("cyanate", "urea", "ndep24h") for c in ("pct", "status")]] \
        .to_csv(OUT / "e6b_calibration_bars.csv", index=False)
    fig, ax = plt.subplots(figsize=(16, 6.4))
    conds = [("cyanate", "growth on cyanate as sole N (steady state)"), ("urea", "growth on urea as sole N (steady state)"),
             ("ndep24h", "N deprivation, 24 h")]
    figs.calibration_bars(fig, ax, B, conds, HEADERS_MED4, lambda g: g.startswith("non-N"))
    h, l_ = ax.get_legend_handles_labels()
    fig.legend(h, l_, loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, 0.0))
    figs.head(fig, "Tolonen MED4 calibration: rank percentile per gene",
              CAL_SUBTITLE + "\nSource: analysis/data/de_long.csv.gz (cal_tolonen_cyanate, cal_tolonen_urea, cal_tolonen_ndep 24h); "
              "data/explore/e6b_calibration_bars.csv. ● / ▼ significant up / down (stored); dashed 0.5, dotted 0.9.")
    fig.subplots_adjust(left=0.05, right=0.94, top=0.55, bottom=0.2)
    files += figs.save(fig, "e6b_cyanate_vs_urea")
    # (c) + (d)
    ms = mit9313_sets()
    rows, summ = [], []
    tables = [("ctrl_med4_hot1a3", "MED4 ismej.2016.70", S.assign(kind=np.where(S.group.str.startswith("non-N"), "non-N",
                                                                                   np.where(S.group.isin(["urease", "cynS / glsF", "markers"]), "linked / markers", "N systems"))))]
    for short in ("ctrl_mit9313_inoc05e6", "ctrl_mit9313_inoc5e6"):
        tables.append((short, "MIT9313 " + short.split("_")[-1], ms.assign(kind=np.where(ms.group.str.startswith("non-N"), "non-N", "N systems"))))
    for short, lab, T in tables:
        x = ex.slice_values(de, short, x_tp := de[de.short_name == short].timepoint.iloc[0])
        for r in T.itertuples():
            v = x.loc[r.locus_tag] if r.locus_tag in x.index else None
            rows.append({"table": lab, "short_name": short, "group": r.group, "kind": r.kind, "locus_tag": r.locus_tag,
                         "gene_name": r.gene_name, "log2fc": None if v is None else v.log2fc,
                         "rank_percentile": None if v is None else v.rank_percentile,
                         "expression_status": "not detected" if v is None else v.expression_status})
        allg = x.rank_percentile
        summ.append({"table": lab, "kind": "all genes", "n": int(allg.notna().sum()), "median_pct": float(allg.median()),
                     "share_pct_le_0.25": float((allg <= 0.25).mean()), "median_log2fc": float(x.log2fc.median()),
                     "share_negative_log2fc": float((x.log2fc < 0).mean())})
    C = pd.DataFrame(rows)
    C.to_csv(OUT / "e6cd_controls_genes.csv", index=False)
    for (lab, kind), g in C.groupby(["table", "kind"]):
        p = g.rank_percentile.dropna()
        summ.append({"table": lab, "kind": kind, "n": int(len(p)), "median_pct": float(p.median()),
                     "share_pct_le_0.25": float((p <= 0.25).mean()), "median_log2fc": float(g.log2fc.median()),
                     "share_negative_log2fc": float((g.log2fc.dropna() < 0).mean()),
                     "n_sig_up": int((g.expression_status == ex.SIG_UP).sum()), "n_sig_down": int((g.expression_status == ex.SIG_DOWN).sum())})
    SM = pd.DataFrame(summ)
    SM.to_csv(OUT / "e6cd_controls_summary.csv", index=False)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), sharey=True)
    kinds = ["N systems", "linked / markers", "non-N"]
    for ax, (short, lab, _) in zip(axes, tables):
        x = C[C.table == lab]
        for i, k in enumerate(kinds):
            y = x[x.kind == k]
            if y.empty:
                continue
            jit = (np.arange(len(y)) % 7 - 3) * 0.05
            ax.scatter(i + jit, y.rank_percentile, s=26, color=F.CAT[i], edgecolor=F.SURF, linewidth=0.4,
                       marker=["o", "s", "^"][i], zorder=3)
            for yy, xx, r in zip(y.rank_percentile, i + jit, y.itertuples()):
                if r.expression_status in (ex.SIG_UP, ex.SIG_DOWN) or str(r.gene_name).startswith(("nat", "amt", "urtA", "cynA")):
                    ax.annotate(f"{r.gene_name or r.locus_tag}{'↑' if r.expression_status == ex.SIG_UP else '↓' if r.expression_status == ex.SIG_DOWN else ''}",
                                (xx, yy), fontsize=6.3, xytext=(4, 0), textcoords="offset points", va="center", color=F.TEXT)
            ax.plot([i - 0.3, i + 0.3], [y.rank_percentile.median()] * 2, color=F.TEXT, linewidth=1.5)
        ax.axhline(0.5, color=F.TEXT2, linewidth=0.8, linestyle="--")
        sm_all = SM[(SM.table == lab) & (SM.kind == "all genes")].iloc[0]
        ax.set_title(f"{lab}\nall genes: {sm_all.share_negative_log2fc:.0%} negative log2FC", loc="left", fontsize=9)
        ax.set_xticks(range(3), kinds, fontsize=8)
        ax.set_ylim(0, 1.02)
        ax.grid(axis="y", color=F.GRID, linewidth=0.6)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(F.GRID)
        ax.tick_params(length=0)
    axes[0].set_ylabel("rank percentile within the table")
    figs.head(fig, "N-replete controls: where the N-system subunits sit within each table",
              "Source: data/explore/e6cd_controls_genes.csv / _summary.csv (analysis/data/de_long.csv.gz; methods v1.6.1 systems). "
              "Dashed = table median (0.5); bar = group median; ↑/↓ significant (stored).")
    fig.subplots_adjust(left=0.06, right=0.99, top=0.78, bottom=0.08, wspace=0.08)
    files += figs.save(fig, "e6cd_controls")
    for f in files:
        print(f.name)
    pd.set_option("display.width", 250)
    print(SM.round(3).to_string(index=False))
    print(B[["group", "locus_tag", "gene_name", "cyanate_pct", "cyanate_status", "urea_pct", "urea_status"]].round(3).to_string(index=False))
    piv = A.pivot_table(index=["group", "locus_tag", "gene_name"], columns="timepoint", values="expression_status", aggfunc="first")[tps]
    print(piv.replace({"significant_up": "UP", "significant_down": "DOWN", "not_significant": "."}).to_string())


if __name__ == "__main__":
    main()
