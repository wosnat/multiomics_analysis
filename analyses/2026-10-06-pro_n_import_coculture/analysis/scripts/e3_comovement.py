"""E3 co-movement within the MED4 N regulon (descriptive). Spearman correlation between log2FC trajectories across the
7 protein slices and, separately, the 5 RNA slices (pairwise, over slices where both genes are detected; n <= 7 / 5,
so each rho rests on very few points). Clustered heatmaps (average linkage on 1 - rho). Relative-rank series over
coculture days (protein and RNA): amt1 - median(urt + cyn subunits); median(cyn) - median(urt);
median(dpp) - median(markers).
Outputs: data/explore/e3_corr_protein.csv, e3_corr_rna.csv, e3_relative_rank.csv; figures e3_corr_protein,
e3_corr_rna, e3_relative_rank.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"


def gene_list(L):
    mem = L["mem"]
    loci = mem[ex.DEDICATED["amt1"]] + mem[ex.DEDICATED["urt"]] + mem[ex.DEDICATED["cyn"]] + mem[ex.DEDICATED["dpp"]]
    loci += [u for u in ex.UREASE if u in L["names"]] + ["PMM0373", "PMM1512"] + list(ex.MARKERS)
    return list(dict.fromkeys(loci))


def corr_matrix(L, loci, slices):
    M = pd.DataFrame({ex.SLICE_LABEL[s]: ex.slice_values(L["de"], *s).reindex(loci).log2fc for s in slices})
    C = pd.DataFrame(np.nan, index=loci, columns=loci)
    N = pd.DataFrame(0, index=loci, columns=loci)
    for a in loci:
        for b in loci:
            rho, n = ex.spearman(M.loc[a], M.loc[b])
            C.loc[a, b], N.loc[a, b] = rho, n
    return M, C, N


def heat(C, N, L, name, omics, nslices):
    keep = [g for g in C.index if C.loc[g].notna().sum() > 1]
    C2 = C.loc[keep, keep]
    D = (1 - C2.fillna(0)).to_numpy(copy=True)
    np.fill_diagonal(D, 0)
    order = [keep[i] for i in leaves_list(linkage(squareform(D, checks=False), "average"))]
    C2 = C2.loc[order, order]
    lab = [f"{L['names'].get(g) or g} {g}" for g in order]
    n = len(order)
    fig, ax = plt.subplots(figsize=(0.32 * n + 3, 0.32 * n + 2.2))
    im = ax.imshow(C2.values, cmap=figs.DIVERGING, vmin=-1, vmax=1)
    ax.set_xticks(range(n), lab, rotation=90, fontsize=6.5)
    ax.set_yticks(range(n), lab, fontsize=6.5)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("Spearman ρ", fontsize=8)
    cb.outline.set_visible(False)
    figs.head(fig, f"Co-movement within the N regulon, {omics}",
              f"Source: analysis/data/de_long.csv.gz; data/explore/{name}.csv.\nρ between log2FC trajectories across "
              f"{nslices} {omics} slices (n ≤ {nslices} points per ρ); average-linkage order.")
    fig.subplots_adjust(left=0.2, right=0.92, top=0.9, bottom=0.2)
    return figs.save(fig, name)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    loci = gene_list(L)
    files = []
    hl = []
    for omics, slices, name in (("protein", ex.PROT_SLICES, "e3_corr_protein"), ("RNA", ex.RNA_SLICES, "e3_corr_rna")):
        M, C, N = corr_matrix(L, loci, slices)
        C.index = C.columns = [f"{g}:{L['names'].get(g, '')}" for g in loci]
        out = C.stack().rename("rho").reset_index().rename(columns={"level_0": "gene_a", "level_1": "gene_b"})
        out["n_slices"] = N.values.flatten()
        out.to_csv(OUT / f"{name}.csv", index=False)
        M.to_csv(OUT / f"{name}_log2fc_matrix.csv")
        Cn = C.copy()
        Cn.index = Cn.columns = loci
        files += heat(Cn, N, L, name, omics, len(slices))
        x = out[out.gene_a < out.gene_b].dropna()
        for g in ("PMM0263:amt1",):
            y = x[(x.gene_a == g) | (x.gene_b == g)].sort_values("rho")
            hl.append((omics, g, y.head(4).values.tolist(), y.tail(4).values.tolist()))
    # relative ranks
    rows = []
    mem = L["mem"]
    for omics, short in (("protein", "anchor_cocult_protein"), ("RNA", "anchor_cocult_rna")):
        for d in (18, 31, 60, 89):
            x = ex.slice_values(L["de"], short, f"day {d}").rank_percentile
            amt1 = x.get("PMM0263", np.nan)
            uc = x.reindex(mem[ex.DEDICATED["urt"]] + mem[ex.DEDICATED["cyn"]]).dropna()
            cyn = x.reindex(mem[ex.DEDICATED["cyn"]]).dropna()
            urt = x.reindex(mem[ex.DEDICATED["urt"]]).dropna()
            dpp = x.reindex(mem[ex.DEDICATED["dpp"]]).dropna()
            mk = x.reindex(list(ex.MARKERS)).dropna()
            rows.append({"omics": omics, "day": d, "amt1": amt1, "median_urt_cyn_subunits": uc.median(),
                         "median_cyn": cyn.median(), "median_urt": urt.median(), "median_dpp": dpp.median(),
                         "median_markers": mk.median(),
                         "amt1_minus_urt_cyn": ex.relative_rank(amt1, uc), "cyn_minus_urt": ex.relative_rank(cyn.median(), urt),
                         "dpp_minus_markers": ex.relative_rank(dpp.median(), mk)})
    RR = pd.DataFrame(rows)
    RR.assign(markers_set=ex.MARKERS_NOTE).to_csv(OUT / "e3_relative_rank.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, omics in zip(axes, ("protein", "RNA")):
        y = RR[RR.omics == omics]
        for i, (c, lab) in enumerate((("amt1_minus_urt_cyn", "amt1 − median(urt+cyn subunits)"),
                                      ("cyn_minus_urt", "median cyn − median urt"),
                                      ("dpp_minus_markers", "median dpp − median markers"))):
            ax.plot(y.day, y[c], marker="o", color=F.CAT[i], linewidth=2, label=lab)
        ax.axhline(0, color=F.TEXT2, linewidth=0.7)
        ax.set_xticks([18, 31, 60, 89], ["d18", "d31", "d60", "d89"])
        ax.set_title(f"coculture, {omics}", loc="left", fontsize=10)
        ax.grid(axis="y", color=F.GRID, linewidth=0.6)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(F.GRID)
        ax.tick_params(length=0)
    axes[0].set_ylabel("difference in rank percentile")
    axes[0].legend(fontsize=7.5, loc="lower left")
    figs.head(fig, "Relative ranks within the N regulon over coculture days",
              "Source: data/explore/e3_relative_rank.csv (rank percentiles from analysis/data/de_long.csv.gz)")
    fig.subplots_adjust(left=0.09, right=0.98, top=0.8, bottom=0.12, wspace=0.08)
    files += figs.save(fig, "e3_relative_rank")
    for f in files:
        print(f.name)
    pd.set_option("display.width", 250)
    print(RR.round(3).to_string(index=False))
    for h in hl:
        print(h)


if __name__ == "__main__":
    main()
