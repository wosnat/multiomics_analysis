"""E4 multi-class / broad-only systems (descriptive; the 'digging'). MED4.

Systems: every High/Medium system whose N-class listings (methods p18) are ALL "broad listing" (no dedicated class);
efflux_annotated and known_false_positive shown. For each system: protein / RNA log2FC and percentile at coculture
d60, d89 and axenic d14 (system median over detected members, plus per member).
For each (system, listed N class): the class's genome enzymes = genes with a KEGG reaction on a listed compound
(p12 classified genome_enzyme_loci; rows most_specific, non-lumping, non-currency, as p18). Cysteine fix: each listed
equiv_group is extended by its stereo-generic equivalents (explore.stereo_equivalents: "X" ~ "L-X"/"D-X"/"DL-X" for
amino-acid names, plus kegg C00736 <-> C00097), and their genome enzymes are added. Before/after counts reported.
Then the median protein percentile of the detected genome enzymes at d60 / d89 / axenic d14 next to the transporter's.
Outputs: data/explore/e4_systems.csv, e4_members.csv, e4_system_class_enzymes.csv, e4_stereo_fix.csv;
figure e4_broad_dotgrid.
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
SL = {"p60": ("anchor_cocult_protein", "day 60"), "p89": ("anchor_cocult_protein", "day 89"),
      "p14ax": ("anchor_axenic_protein", "day 14"), "r60": ("anchor_cocult_rna", "day 60"),
      "r89": ("anchor_cocult_rna", "day 89"), "r14ax": ("anchor_axenic_rna", "day 14")}


def loci_of(v):
    return [x for x in ex.nt.parse_list(v) if x and x not in ("none", "not_eligible")]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    sy, mem, lb, names = L["sy"], L["mem"], L["lb"], L["names"]
    cls = pd.read_csv(ex.MD / "med4" / "p12_med4_system_substrates_classified.csv", low_memory=False)
    cls = cls[(cls.substrate_depth == "most_specific") & ~cls.is_lumping.map(ex.nt.to_bool) & ~cls.is_currency.map(ex.nt.to_bool)]
    # genome enzymes per equiv group (system-independent)
    ge_by_group = cls.groupby("equiv_group").genome_enzyme_loci.agg(lambda s: set(x for v in s for x in loci_of(v))).to_dict()
    groups_all = cls[["equiv_group", "metabolite_name", "compound_class_final"]].rename(
        columns={"metabolite_name": "name", "compound_class_final": "compound_class"}).drop_duplicates()
    allp12 = pd.read_csv(ex.MD / "med4" / "p12_med4_system_substrates_classified.csv", low_memory=False,
                         usecols=["equiv_group", "metabolite_name", "compound_class_final", "genome_enzyme_loci"])
    for g, s in allp12.groupby("equiv_group").genome_enzyme_loci.agg(lambda s: set(x for v in s for x in loci_of(v))).items():
        ge_by_group.setdefault(g, s)
    pool = allp12.rename(columns={"metabolite_name": "name", "compound_class_final": "compound_class"})[
        ["equiv_group", "name", "compound_class"]].drop_duplicates()
    eqv = ex.stereo_equivalents(groups_all, all_groups=pool)
    fix = [{"equiv_group": g, "names": "|".join(sorted(set(pool[pool.equiv_group == g].name))),
            "stereo_equivalents": "|".join(sorted(s - {g})),
            "genome_enzymes_before": len(ge_by_group.get(g, set())),
            "genome_enzymes_after": len(set().union(*(ge_by_group.get(x, set()) for x in s)))}
           for g, s in eqv.items() if len(s) > 1]
    FX = pd.DataFrame(fix)
    FX.to_csv(OUT / "e4_stereo_fix.csv", index=False)

    vals = {k: ex.slice_values(L["de"], *v) for k, v in SL.items()}
    basis = lb.groupby("system_id").listing_basis.agg(set)
    broad_only = sorted(s for s, b in basis.items() if b == {"broad listing"})
    srows, mrows, crows = [], [], []
    for sid in broad_only:
        m = mem[sid]
        rec = {"system_id": sid, "member_names": sy.loc[sid, "member_names"], "tier": sy.loc[sid, "tier"],
               "efflux_annotated": bool(sy.loc[sid, "efflux_annotated"]),
               "known_false_positive": bool(sy.loc[sid, "known_false_positive"]),
               "classes": "|".join(sorted(lb[lb.system_id == sid].compound_class))}
        for k, v in vals.items():
            x = v.reindex(m)
            rec[f"{k}_median_pct"] = x.rank_percentile.median()
            rec[f"{k}_median_log2fc"] = x.log2fc.median()
            rec[f"{k}_n_detected"] = int(x.log2fc.notna().sum())
            rec[f"{k}_n_up"] = int((x.expression_status == ex.SIG_UP).sum())
            rec[f"{k}_n_down"] = int((x.expression_status == ex.SIG_DOWN).sum())
        srows.append(rec)
        for lt in m:
            mr = {"system_id": sid, "locus_tag": lt, "gene_name": names.get(lt, "")}
            for k, v in vals.items():
                if lt in v.index:
                    mr.update({f"{k}_log2fc": v.loc[lt, "log2fc"], f"{k}_pct": v.loc[lt, "rank_percentile"],
                               f"{k}_status": v.loc[lt, "expression_status"]})
                else:
                    mr[f"{k}_status"] = "not detected"
            mrows.append(mr)
        for c in sorted(lb[lb.system_id == sid].compound_class):
            r = cls[(cls.system_id == sid) & (cls.compound_class_final == c)]
            grp = sorted(set(r.equiv_group))
            before = set().union(*(ge_by_group.get(g, set()) for g in grp)) if grp else set()
            after = set().union(*(ge_by_group.get(x, set()) for g in grp for x in eqv.get(g, {g}))) if grp else set()
            cr = {"system_id": sid, "member_names": rec["member_names"], "efflux_annotated": rec["efflux_annotated"],
                  "known_false_positive": rec["known_false_positive"], "compound_class": c,
                  "compounds": " | ".join(sorted(set(r.metabolite_name.astype(str))))[:250],
                  "n_genome_enzymes_before_fix": len(before), "n_genome_enzymes_after_fix": len(after),
                  "genome_enzymes": " ".join(f"{e}:{names.get(e, '')}" for e in sorted(after))[:600]}
            for k in ("p60", "p89", "p14ax"):
                cr[f"transporter_{k}_pct"] = rec[f"{k}_median_pct"]
                e = vals[k].reindex(sorted(after)).rank_percentile.dropna()
                cr[f"enzymes_{k}_median_pct"] = e.median() if len(e) else np.nan
                cr[f"enzymes_{k}_n_detected"] = int(len(e))
                cr[f"enzymes_{k}_n_up"] = int((vals[k].reindex(sorted(after)).expression_status == ex.SIG_UP).sum())
            crows.append(cr)
    S, M, C = pd.DataFrame(srows), pd.DataFrame(mrows), pd.DataFrame(crows)
    S.to_csv(OUT / "e4_systems.csv", index=False)
    M.to_csv(OUT / "e4_members.csv", index=False)
    C.to_csv(OUT / "e4_system_class_enzymes.csv", index=False)

    # figure: dot grid (rows systems, columns classes) for d60 and d89
    classes = [c for c in ["ammonium", "urea", "nitrate", "nitrite", "amino acids", "peptides", "amino sugars", "polyamines",
                           "nucleobases/nucleosides", "osmolytes"] if c in set(C.compound_class)]
    sys_order = list(S.system_id)
    lab = [f"{ex.F_short(r.member_names)} ({r.system_id.replace('sys_', '')})"
           + (" [efflux]" if r.efflux_annotated else "") + (" [known FP]" if r.known_false_positive else "")
           for r in S.itertuples()]
    fig, axes = plt.subplots(1, 2, figsize=(14, 0.5 * len(sys_order) + 3.2), sharey=True)
    for ax, k, ttl in ((axes[0], "p60", "coculture d60 protein"), (axes[1], "p89", "coculture d89 protein")):
        for i, sid in enumerate(sys_order):
            for j, c in enumerate(classes):
                x = C[(C.system_id == sid) & (C.compound_class == c)]
                if x.empty:
                    continue
                x = x.iloc[0]
                e = x[f"enzymes_{k}_median_pct"]
                if pd.isna(e):
                    ax.scatter(j, i, s=110, facecolor=F.SURF, edgecolor=F.TEXT2, linewidth=0.9)
                    txt = f"n=0"
                else:
                    ax.scatter(j, i, s=110, color=figs.SEQ(e), edgecolor=F.TEXT2, linewidth=0.4)
                    txt = f"E {e:.2f} (n={int(x[f'enzymes_{k}_n_detected'])})"
                ax.text(j, i + 0.32, txt, fontsize=5.8, color=F.TEXT, va="center", ha="center")
            tp = S.set_index("system_id").loc[sid, f"{k}_median_pct"]
            ax.text(len(classes) - 0.3, i, "T " + ("n.d." if pd.isna(tp) else f"{tp:.2f}"), fontsize=7, va="center",
                    color=F.TEXT, fontweight="bold")
        ax.set_xticks(range(len(classes)), classes, rotation=35, ha="left", fontsize=8)
        ax.xaxis.tick_top()
        ax.set_xlim(-0.5, len(classes) + 0.3)
        ax.set_ylim(len(sys_order) - 0.5, -0.6)
        ax.set_title(ttl, loc="left", fontsize=10, pad=50)
        ax.grid(color=F.GRID, linewidth=0.5)
        ax.set_axisbelow(True)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
    axes[0].set_yticks(range(len(sys_order)), lab, fontsize=7.5)
    sm = plt.cm.ScalarMappable(cmap=figs.SEQ, norm=plt.Normalize(0, 1))
    cb = fig.colorbar(sm, cax=fig.add_axes([0.35, 0.045, 0.4, 0.01]), orientation="horizontal")
    cb.set_label("median protein percentile of the class's genome enzymes (E)", fontsize=8)
    cb.outline.set_visible(False)
    figs.head(fig, "Broad-only N listings: transporter vs the genome enzymes of each listed class",
              "Source: data/explore/e4_system_class_enzymes.csv (methods p18/p12 + analysis/data/de_long.csv.gz; Cysteine / "
              "L-Cysteine merged).\nDot colour = E (median protein percentile of the class's detected genome enzymes, n below the dot); 'T' = transporter median protein percentile; hollow = no detected enzyme.")
    fig.subplots_adjust(left=0.2, right=0.98, top=1 - 2.6 / (0.5 * len(sys_order) + 3.2), bottom=0.11, wspace=0.12)
    for f in figs.save(fig, "e4_broad_dotgrid"):
        print(f.name)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    print(FX.to_string(index=False))
    print("cells 0 enzymes before/after:", int((C.n_genome_enzymes_before_fix == 0).sum()), int((C.n_genome_enzymes_after_fix == 0).sum()), "of", len(C))
    print(S[["system_id", "member_names", "efflux_annotated", "known_false_positive", "classes", "p60_median_pct", "p89_median_pct",
             "p14ax_median_pct", "r60_median_log2fc", "r89_median_log2fc"]].round(3).to_string(index=False))
    print(C[["system_id", "compound_class", "n_genome_enzymes_before_fix", "n_genome_enzymes_after_fix", "transporter_p60_pct",
             "enzymes_p60_median_pct", "transporter_p89_pct", "enzymes_p89_median_pct", "transporter_p14ax_pct",
             "enzymes_p14ax_median_pct"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
