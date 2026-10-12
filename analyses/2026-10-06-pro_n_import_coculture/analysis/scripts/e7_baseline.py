"""E7 coculture exponential baseline (descriptive). Same-study direct contrast (coculture vs axenic, RNA),
10.1101/2025.11.24.690089_coculture_alteromonas_hot1a3_med4_rnaseq, day 11 (exponential) and day 18 (nutrient_limited).
1. Per gene set (markers; dedicated N systems by subunit; linked enzymes incl. urease, cynS, glsF; broad N systems;
   non-N systems; ribosomal proteins): log2FC, status, percentile at d11 and d18; set median percentile. The median
   percentile over all genes is 0.5 by construction (within-slice ranks).
2. Consistency check, planned as NOT an identity: per gene, [anchor coculture RNA d18 - anchor axenic RNA d14] (each
   vs its own exponential) vs [direct contrast d18 - direct contrast d11]; Spearman rho genome-wide and for the N
   regulon, plus the max absolute difference. The two differ in nominal day (d14 vs d18) and reference, but the stored
   values satisfy the equation to floating-point precision (see e7_consistency.csv).
Outputs: data/explore/e7_gene_sets.csv, e7_set_medians.csv, e7_diff_of_contrasts.csv, e7_consistency.csv;
figure figures/e7_baseline.
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
DC = "direct_contrast_rna"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    de, names, prods = L["de"], L["names"], L["prods"]
    G = ex.gene_sets(L)
    G["set"] = np.select([G.group.str.startswith("starvation markers"), G.group.str.startswith("N dedicated"),
                          G.group.str.startswith("linked"), G.group.str.startswith("N broad"), G.group.str.startswith("non-N")],
                         ["markers", "dedicated N systems", "linked enzymes", "broad N systems", "non-N systems"], "other")
    G = G[G.set != "other"]
    ribo = sorted(lt for lt in names if (names[lt] or "").lower().startswith(("rps", "rpl"))
                  or "ribosomal protein" in str(prods.get(lt, "")).lower())
    G = pd.concat([G, pd.DataFrame({"group": "ribosomal proteins", "system_id": "", "locus_tag": ribo, "set": "ribosomal proteins"})],
                  ignore_index=True)
    d11, d18 = ex.slice_values(de, DC, "day 11"), ex.slice_values(de, DC, "day 18")
    rows = []
    for r in G.itertuples():
        rec = {"set": r.set, "group": r.group, "locus_tag": r.locus_tag, "gene_name": names.get(r.locus_tag, "")}
        for lab, x in (("d11", d11), ("d18", d18)):
            if r.locus_tag in x.index:
                rec.update({f"{lab}_log2fc": x.loc[r.locus_tag, "log2fc"], f"{lab}_status": x.loc[r.locus_tag, "expression_status"],
                            f"{lab}_pct": x.loc[r.locus_tag, "rank_percentile"]})
            else:
                rec[f"{lab}_status"] = "not detected"
        rows.append(rec)
    T = pd.DataFrame(rows)
    T.assign(markers_set=ex.MARKERS_NOTE).to_csv(OUT / "e7_gene_sets.csv", index=False)
    med = T.drop_duplicates(["set", "locus_tag"]).groupby("set").agg(
        n=("locus_tag", "nunique"), d11_median_pct=("d11_pct", "median"), d18_median_pct=("d18_pct", "median"),
        d11_n_up=("d11_status", lambda s: int((s == ex.SIG_UP).sum())), d11_n_down=("d11_status", lambda s: int((s == ex.SIG_DOWN).sum())),
        d18_n_up=("d18_status", lambda s: int((s == ex.SIG_UP).sum())), d18_n_down=("d18_status", lambda s: int((s == ex.SIG_DOWN).sum()))
    ).reset_index()
    med = pd.concat([med, pd.DataFrame([{"set": "all genes (0.5 by construction)", "n": int(d11.log2fc.notna().sum()),
                                         "d11_median_pct": float(d11.rank_percentile.median()),
                                         "d18_median_pct": float(d18.rank_percentile.median()),
                                         "d11_n_up": int((d11.expression_status == ex.SIG_UP).sum()),
                                         "d11_n_down": int((d11.expression_status == ex.SIG_DOWN).sum()),
                                         "d18_n_up": int((d18.expression_status == ex.SIG_UP).sum()),
                                         "d18_n_down": int((d18.expression_status == ex.SIG_DOWN).sum())}])], ignore_index=True)
    med.assign(markers_set=ex.MARKERS_NOTE).to_csv(OUT / "e7_set_medians.csv", index=False)
    # 2. consistency check
    cc18 = ex.slice_values(de, "anchor_cocult_rna", "day 18").log2fc
    ax14 = ex.slice_values(de, "anchor_axenic_rna", "day 14").log2fc
    lhs = ex.aligned_difference(cc18, ax14)
    rhs = ex.aligned_difference(d18.log2fc, d11.log2fc)
    j = lhs.index.intersection(rhs.index)
    D = pd.DataFrame({"locus_tag": j, "gene_name": [names.get(x, "") for x in j],
                      "anchor_cc_d18_minus_axenic_d14": lhs.loc[j].values, "direct_d18_minus_d11": rhs.loc[j].values})
    nreg = set(G[G.set.isin(["markers", "dedicated N systems", "linked enzymes"])].locus_tag)
    D["in_N_regulon"] = D.locus_tag.isin(nreg)
    D.to_csv(OUT / "e7_diff_of_contrasts.csv", index=False)
    crow = []
    for lab, x in (("genome-wide", D), ("N regulon (markers + dedicated N + linked)", D[D.in_N_regulon]),
                   ("non-N systems", D[D.locus_tag.isin(set(G[G.set == "non-N systems"].locus_tag))])):
        rho, n = ex.spearman(x.anchor_cc_d18_minus_axenic_d14, x.direct_d18_minus_d11)
        crow.append({"scope": lab, "n": n, "spearman_rho": rho,
                     "note": "planned as a consistency check (d14 vs d18; different references); see the max-difference "
                             "row: the stored values satisfy it to floating-point precision"})
    # also: direct d11 vs anchor coculture d18 (panel b)
    j2 = d11.log2fc.dropna().index.intersection(cc18.dropna().index)
    rho_b, n_b = ex.spearman(d11.log2fc.loc[j2], cc18.loc[j2])
    rho_bn, n_bn = ex.spearman(d11.log2fc.reindex(sorted(nreg & set(j2))), cc18.reindex(sorted(nreg & set(j2))))
    crow += [{"scope": "panel b: direct d11 vs anchor coculture d18 RNA, genome-wide", "n": n_b, "spearman_rho": rho_b, "note": ""},
             {"scope": "panel b: direct d11 vs anchor coculture d18 RNA, N regulon", "n": n_bn, "spearman_rho": rho_bn, "note": ""}]
    diff = (D.anchor_cc_d18_minus_axenic_d14 - D.direct_d18_minus_d11).abs()
    crow.append({"scope": "genome-wide: max |(anchor cc d18 - axenic d14) - (direct d18 - d11)|", "n": int(len(D)),
                 "spearman_rho": float(diff.max()),
                 "note": f"value column holds the max absolute difference; genes with |difference| < 1e-6: {int((diff < 1e-6).sum())}"})
    C = pd.DataFrame(crow)
    C.assign(markers_set=ex.MARKERS_NOTE).to_csv(OUT / "e7_consistency.csv", index=False)
    # figure (revised 2026-10-11): panel (a) on the log2FC scale; percentiles stay in e7_gene_sets.csv only
    fig, (a, b) = plt.subplots(1, 2, figsize=(16, 10), gridspec_kw={"width_ratios": [1.1, 1]})
    CLIP = 4.0
    HDR = {"starvation markers": "N-starvation markers (glnA, ntcA, glnB, pipX)",
           "N dedicated: amt1": "amt1: ammonium transporter (ammonium)",
           "N dedicated: urt": "urt: urea ABC transporter (urea)",
           "N dedicated: cyn": "cyn: cyanate ABC transporter (cyanate)",
           "N dedicated: dpp": "dpp: di/oligopeptide ABC transporter (peptides)",
           "urease": "urease ureA–G: urea → ammonium (enzyme)",
           "cynS / glsF": "cynS: cyanase (enzyme); glsF: glutamate synthase (enzyme)",
           "non-N: pst": "pst: phosphate", "non-N: phn": "phn: phosphonate", "non-N: sul1": "sul1: sulfate",
           "non-N: sul3": "sul3: sulfate", "non-N: fut/idiA2": "fut/idiA2: iron", "non-N: mnt": "mnt: manganese",
           "non-N: lraI": "lraI: Mn/Zn", "non-N: sbtA": "sbtA: bicarbonate"}
    sel = T[T.set.isin(["markers", "dedicated N systems", "linked enzymes", "non-N systems"])].drop_duplicates(["set", "locus_tag"]).copy()
    sel["sub"] = sel.group
    sel.loc[sel.set == "linked enzymes", "sub"] = np.where(sel.loc[sel.set == "linked enzymes", "locus_tag"].isin(ex.UREASE),
                                                         "urease", "cynS / glsF")
    order = ["markers", "dedicated N systems", "linked enzymes", "non-N systems"]
    sub_order = list(dict.fromkeys(sel.assign(o=sel.set.map(order.index)).sort_values(["o"])["sub"]))
    sel = sel.assign(o=sel.set.map(order.index), so=sel["sub"].map(sub_order.index)).sort_values(["o", "so", "locus_tag"]).reset_index(drop=True)
    ys, y, prev = [], 0.0, None
    heads = []
    for g in sel["sub"]:
        if g != prev:
            y += 1.1 if prev is not None else 0.6
            heads.append((g, y - 0.75))
        ys.append(y)
        y += 1
        prev = g
    sel["y"] = ys
    clipped = False
    for r in sel.itertuples():
        c = F.CAT[order.index(r.set)]
        v11, v18 = float(np.clip(r.d11_log2fc, -CLIP, CLIP)), float(np.clip(r.d18_log2fc, -CLIP, CLIP))
        a.plot([v11, v18], [r.y, r.y], color=F.GRID, linewidth=1.6, zorder=1)
        a.scatter(v11, r.y, s=28, facecolor=F.SURF, edgecolor=c, linewidth=1.4, zorder=2)
        a.scatter(v18, r.y, s=32, color=c, zorder=3)
        for raw, v, st in ((r.d11_log2fc, v11, r.d11_status), (r.d18_log2fc, v18, r.d18_status)):
            if st in (ex.SIG_UP, ex.SIG_DOWN):
                a.text(v, r.y - 0.42, "↑" if st == ex.SIG_UP else "↓", ha="center", fontsize=7, color=F.TEXT)
            if abs(raw) > CLIP:
                clipped = True
                a.text(v + (0.15 if raw > 0 else -0.15), r.y, "»" if raw > 0 else "«", va="center",
                       ha="left" if raw > 0 else "right", fontsize=8, color=F.TEXT)
    a.set_yticks(sel.y, [f"{g or lt} {lt}" for g, lt in zip(sel.gene_name, sel.locus_tag)], fontsize=6.5)
    for g, yy in heads:
        a.text(-0.01, yy, HDR.get(g, g), transform=a.get_yaxis_transform(), ha="right", va="center", fontsize=7,
               fontweight="bold", color=F.TEXT2)
    a.set_ylim(y, -0.6)
    a.set_xlim(-CLIP - 0.2, CLIP + 0.2)
    a.axvline(0, color=F.TEXT, linewidth=1.0)
    a.set_xlabel("log2 fold change, coculture vs axenic (same study, RNA)" + (f"; clipped at ±{CLIP:g} («/»)" if clipped else ""))
    a.text(0.0, -0.06, "← higher in axenic", transform=a.transAxes, ha="left", va="top", fontsize=8, color=F.TEXT2)
    a.text(1.0, -0.06, "higher in coculture →", transform=a.transAxes, ha="right", va="top", fontsize=8, color=F.TEXT2)
    cy = sel[sel.locus_tag == "PMM0370"].iloc[0]
    fc11, fc18 = 2 ** abs(cy.d11_log2fc), 2 ** abs(cy.d18_log2fc)
    w11 = "higher in coculture" if cy.d11_log2fc > 0 else "higher in axenic"
    w18 = "higher in coculture" if cy.d18_log2fc > 0 else "higher in axenic"
    from matplotlib.lines import Line2D
    example = f"worked example — cynA: {fc11:.1f}× {w11} at d11 → {fc18:.1f}× {w18} at d18"
    fig.legend(handles=[Line2D([], [], marker="o", markerfacecolor=F.SURF, markeredgecolor=F.TEXT2, linestyle="", label="d11, exponential"),
                        Line2D([], [], marker="o", color=F.TEXT2, linestyle="",
                               label="d18, coculture d18 vs axenic (~d14 sample), late decline"),
                        Line2D([], [], linestyle="", label=example)],
               loc="lower left", bbox_to_anchor=(0.01, 0.0), ncol=3, fontsize=8, handletextpad=0.3, columnspacing=1.5)
    a.set_title("(a) per gene: coculture vs axenic at d11 and d18 (↑/↓ significant, stored)", loc="left", fontsize=9)
    a.grid(axis="x", color=F.GRID, linewidth=0.5)
    for sp in ("left", "bottom"):
        a.spines[sp].set_color(F.GRID)
    a.tick_params(length=0)
    other = [x for x in j2 if x not in nreg]
    b.scatter(d11.log2fc.loc[other].clip(-6, 6), cc18.loc[other].clip(-6, 6), s=6, color=F.GRID, label="other genes")
    nn = sorted(nreg & set(j2))
    b.scatter(d11.log2fc.loc[nn].clip(-6, 6), cc18.loc[nn].clip(-6, 6), s=28, color=F.CAT[1], edgecolor=F.SURF, linewidth=0.4,
              label="N regulon", zorder=3)
    for lt in nn:
        if lt in ex.MARKERS or lt == "PMM0263":
            b.annotate(names.get(lt) or lt, (np.clip(d11.log2fc[lt], -6, 6), np.clip(cc18[lt], -6, 6)), fontsize=7,
                       xytext=(3, 3), textcoords="offset points", color=F.TEXT)
    b.axhline(0, color=F.TEXT2, linewidth=0.6)
    b.axvline(0, color=F.TEXT2, linewidth=0.6)
    b.set_xlabel("log2 fold change, coculture vs axenic at d11 (exponential; same study, RNA)")
    b.set_ylabel("log2 fold change, coculture d18 vs coculture exponential (RNA)")
    b.text(0.0, -0.08, "← higher in axenic", transform=b.transAxes, ha="left", va="top", fontsize=8, color=F.TEXT2)
    b.text(1.0, -0.08, "higher in coculture →", transform=b.transAxes, ha="right", va="top", fontsize=8, color=F.TEXT2)
    b.set_title(f"(b) ρ = {rho_b:.2f} genome-wide (n = {n_b}); N regulon ρ = {rho_bn:.2f} (n = {n_bn})", loc="left", fontsize=9)
    b.grid(color=F.GRID, linewidth=0.5)
    b.set_axisbelow(True)
    for sp in ("left", "bottom"):
        b.spines[sp].set_color(F.GRID)
    b.tick_params(length=0)
    b.legend(fontsize=8, loc="lower right")
    figs.head(fig, "Coculture exponential baseline: the same-study direct contrast",
              "Source: analysis/data/de_long.csv.gz (direct_contrast_rna d11 / d18; anchor_cocult_rna d18); data/explore/e7_*.csv "
              "(rank percentiles are in e7_gene_sets.csv). Fold change = 2^|log2FC|.")
    fig.subplots_adjust(left=0.22, right=0.98, top=0.9, bottom=0.12, wspace=0.18)
    for f in figs.save(fig, "e7_baseline"):
        print(f.name)
    pd.set_option("display.width", 250)
    print(med.round(3).to_string(index=False))
    print(C.round(3).to_string(index=False))
    print(T[T.set.isin(["markers", "dedicated N systems", "linked enzymes"])][["set", "locus_tag", "gene_name", "d11_log2fc", "d11_status",
                                                                              "d11_pct", "d18_log2fc", "d18_status", "d18_pct"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
