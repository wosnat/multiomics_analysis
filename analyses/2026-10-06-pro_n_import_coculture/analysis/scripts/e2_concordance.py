"""E2 protein-RNA concordance, genome-wide (descriptive). For axenic d14 and coculture d18/d31/d60/d89: genes detected
in both protein and RNA; Spearman rho of log2FC; quadrant counts by stored significance and by sign, per gene group.
Gene groups: all; N regulon (starvation markers + dedicated N systems amt1/urt/cyn/dpp + linked enzymes); broad
N-listing systems; non-N reference systems; ribosomal proteins (gene name ^rps|^rpl or product 'ribosomal protein');
genes significantly up in protein at that slice.
Outputs: data/explore/e2_quadrants.csv, e2_spearman.csv, e2_pairs_long.csv; figure e2_concordance.
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"
PAIRS = [("ax d14", ("anchor_axenic_protein", "day 14"), ("anchor_axenic_rna", "day 14"))] + [
    (f"cc d{d}", ("anchor_cocult_protein", f"day {d}"), ("anchor_cocult_rna", f"day {d}")) for d in (18, 31, 60, 89)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    G = ex.gene_sets(L)
    nreg = set(G[G.group.str.startswith(("N dedicated", "linked enzymes", "starvation markers"))].locus_tag)
    broad = set(G[G.group.str.startswith("N broad")].locus_tag)
    nonn = set(G[G.group.str.startswith("non-N")].locus_tag)
    names, prods = L["names"], L["prods"]
    ribo = {lt for lt in names if (names[lt] or "").lower().startswith(("rps", "rpl"))
            or "ribosomal protein" in str(prods.get(lt, "")).lower()}
    qrows, srows, long = [], [], []
    for lab, (ps, pt), (rs, rt) in PAIRS:
        p = ex.slice_values(L["de"], ps, pt)
        r = ex.slice_values(L["de"], rs, rt)
        both = sorted(set(p.index) & set(r.index))
        df = pd.DataFrame({"locus_tag": both, "lfc_p": p.loc[both, "log2fc"].values, "lfc_r": r.loc[both, "log2fc"].values,
                           "st_p": p.loc[both, "expression_status"].values, "st_r": r.loc[both, "expression_status"].values,
                           "pct_p": p.loc[both, "rank_percentile"].values, "pct_r": r.loc[both, "rank_percentile"].values})
        df["slice"] = lab
        df["gene_name"] = df.locus_tag.map(names)
        df["group"] = ["N regulon" if x in nreg else "N broad listing" if x in broad else "non-N reference" if x in nonn
                       else "ribosomal protein" if x in ribo else "other" for x in df.locus_tag]
        long.append(df)
        groups = {"all genes": df, "N regulon (markers + dedicated N + linked)": df[df.locus_tag.isin(nreg)],
                  "N broad listing systems": df[df.locus_tag.isin(broad)], "non-N reference systems": df[df.locus_tag.isin(nonn)],
                  "ribosomal proteins": df[df.locus_tag.isin(ribo)], "significantly up in protein": df[df.st_p == ex.SIG_UP]}
        for gname, x in groups.items():
            rho, n = ex.spearman(x.lfc_p, x.lfc_r)
            srows.append({"slice": lab, "group": gname, "n_both": n, "spearman_rho": rho})
            for mode in ("sig", "sign"):
                q = ex.quadrants(x, mode=mode)
                qrows.append({"slice": lab, "group": gname, "mode": mode, **q})
    Q = pd.DataFrame(qrows)
    Q.to_csv(OUT / "e2_quadrants.csv", index=False)
    S = pd.DataFrame(srows)
    S.to_csv(OUT / "e2_spearman.csv", index=False)
    LG = pd.concat(long, ignore_index=True)
    LG.to_csv(OUT / "e2_pairs_long.csv", index=False)
    # figure
    fig, axes = plt.subplots(1, 5, figsize=(17, 4.4), sharex=True, sharey=True)
    style = {"other": (F.GRID, 6, "o"), "ribosomal protein": (F.CAT[3], 14, "s"), "N broad listing": (F.CAT[4], 16, "D"),
             "non-N reference": (F.CAT[2], 22, "^"), "N regulon": (F.CAT[1], 26, "o")}
    for ax, (lab, _, _) in zip(axes, PAIRS):
        x = LG[LG.slice == lab]
        for g in ("other", "ribosomal protein", "N broad listing", "non-N reference", "N regulon"):
            y = x[x.group == g]
            c, s, m = style[g]
            ax.scatter(y.lfc_r.clip(-6, 6), y.lfc_p.clip(-6, 6), s=s, color=c, marker=m, linewidths=0.3,
                       edgecolor=F.SURF if g != "other" else "none", label=g, zorder=3 if g != "other" else 1)
        for lt, nm in ex.MARKERS.items():
            y = x[x.locus_tag == lt]
            if len(y):
                ax.annotate(nm, (y.lfc_r.clip(-6, 6).iloc[0], y.lfc_p.clip(-6, 6).iloc[0]), fontsize=6.5, color=F.TEXT,
                            xytext=(3, 3), textcoords="offset points")
        rho = S[(S.slice == lab) & (S.group == "all genes")].spearman_rho.iloc[0]
        n = S[(S.slice == lab) & (S.group == "all genes")].n_both.iloc[0]
        ax.set_title(f"{lab}   ρ = {rho:.2f} (n = {n})", loc="left", fontsize=9)
        ax.axhline(0, color=F.TEXT2, linewidth=0.6)
        ax.axvline(0, color=F.TEXT2, linewidth=0.6)
        ax.grid(color=F.GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        ax.set_xlabel("RNA log2FC (clipped ±6)")
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(F.GRID)
        ax.tick_params(length=0)
    axes[0].set_ylabel("protein log2FC (clipped ±6)")
    h, l_ = axes[0].get_legend_handles_labels()
    fig.legend(h, l_, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.0), fontsize=8)
    figs.head(fig, "Protein vs RNA log2FC, genes detected in both",
              "Source: analysis/data/de_long.csv.gz (anchor protein and RNA, same culture and day); data/explore/e2_*.csv. "
              "Spearman ρ over all genes detected in both; markers labelled.")
    fig.subplots_adjust(left=0.05, right=0.99, top=0.8, bottom=0.25, wspace=0.08)
    for f in figs.save(fig, "e2_concordance"):
        print(f.name)
    pd.set_option("display.width", 250)
    print(S.pivot(index="group", columns="slice", values="spearman_rho").round(3).to_string())
    for mode in ("sig", "sign"):
        z = Q[Q["mode"] == mode]
        print(mode)
        print(z[["slice", "group", "n", "up/up", "up/down", "down/up", "down/down", "share_up/down"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
