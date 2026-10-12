"""E5 what else marks late coculture (descriptive). MED4.

Set (protein): rank percentile >= 0.90 at BOTH coculture d60 and d89 (protein), and NOT significant_up at axenic d14
protein (genes not detected at axenic d14 are kept and flagged). Same for RNA (coculture RNA d60/d89; axenic RNA d14).
Cyanorak top-level roles: one KG call through methods kg_fetch.fetch, genes_by_ontology(cyanorak_role, MED4,
level=0) (natural key locus_tag x term_id); a gene with several top-level roles is counted under each; genes without a
role are 'no Cyanorak role'. Transporter-universe membership from methods p2_med4_gene_roles.csv (v1.6.1).
Outputs: data/explore/e5_set_protein.csv, e5_set_rna.csv, e5_role_counts.csv, e5_cyanorak_roles_level0.csv;
figure e5_late_coculture_roles.
"""
import sys
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, genes_by_ontology, to_dataframe

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import figs  # noqa: E402
from expr import kf  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"


def build(L, short_cc, short_ax, roles, uni, Gs):
    a = ex.slice_values(L["de"], short_cc, "day 60")
    b = ex.slice_values(L["de"], short_cc, "day 89")
    ax = ex.slice_values(L["de"], short_ax, "day 14")
    both = set(a.index[a.rank_percentile >= 0.90]) & set(b.index[b.rank_percentile >= 0.90])
    rows = []
    for lt in sorted(both):
        st = ax.expression_status.get(lt, "not detected")
        if st == ex.SIG_UP:
            continue
        rows.append({"locus_tag": lt, "gene_name": L["names"].get(lt, ""), "product": L["prods"].get(lt),
                     "pct_d60": a.loc[lt, "rank_percentile"], "pct_d89": b.loc[lt, "rank_percentile"],
                     "status_d60": a.loc[lt, "expression_status"], "status_d89": b.loc[lt, "expression_status"],
                     "axenic_d14_status": st, "axenic_d14_pct": ax.rank_percentile.get(lt),
                     "in_transporter_universe": lt in uni.index,
                     "tier_of_system": uni.get(lt, {}) if False else None,
                     "cyanorak_top_roles": "|".join(sorted(roles.get(lt, ["no Cyanorak role"]))),
                     "gene_set_group": "|".join(sorted(set(Gs[Gs.locus_tag == lt].group))) or ""})
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ex.load()
    log = []
    with GraphConnection() as conn:
        res = kf.fetch(genes_by_ontology, "genes_by_ontology(cyanorak_role, MED4, level 0)", log, ("locus_tag", "term_id"),
                       limit_none_ok=True, ontology="cyanorak_role", organism="Prochlorococcus MED4", level=0,
                       min_gene_set_size=1, max_gene_set_size=None, conn=conn)
    R = to_dataframe({"results": res["results"]})
    R.to_csv(OUT / "e5_cyanorak_roles_level0.csv", index=False)
    roles = R.groupby("locus_tag").apply(lambda x: [f"{t.split(':')[-1]} {n}" for t, n in zip(x.term_id, x.term_name)],
                                         include_groups=False).to_dict()
    uni = pd.read_csv(ex.MD / "med4" / "p2_med4_gene_roles.csv").set_index("locus_tag")
    gs = pd.read_csv(ex.MD / "med4" / f"p3_med4_gene_systems_{ex.REF}.csv").set_index("locus_tag").system_id
    Gs = ex.gene_sets(L)
    sets = {}
    for omics, cc, axs in (("protein", "anchor_cocult_protein", "anchor_axenic_protein"),
                           ("RNA", "anchor_cocult_rna", "anchor_axenic_rna")):
        S = build(L, cc, axs, roles, uni, Gs)
        S["system_id"] = S.locus_tag.map(gs)
        S["system_tier"] = S.system_id.map(L["sy"].tier)
        S["system_members"] = S.system_id.map(L["sy"].member_names)
        S.drop(columns=["tier_of_system"]).to_csv(OUT / f"e5_set_{omics.lower()}.csv", index=False)
        sets[omics] = S
    rc = []
    for omics, S in sets.items():
        for _, r in S.iterrows():
            for role in r.cyanorak_top_roles.split("|"):
                rc.append({"omics": omics, "role": role, "locus_tag": r.locus_tag, "transporter": r.in_transporter_universe})
    RC = pd.DataFrame(rc).groupby(["omics", "role"]).agg(genes=("locus_tag", "nunique"),
                                                          in_transporter_universe=("transporter", "sum")).reset_index()
    RC.to_csv(OUT / "e5_role_counts.csv", index=False)
    # figure
    fig, axes = plt.subplots(1, 2, figsize=(15, 7.5))
    for ax, omics in zip(axes, ("protein", "RNA")):
        x = RC[RC.omics == omics].sort_values("genes")
        y = range(len(x))
        ax.barh(y, x.genes, height=0.55, color=F.CAT[0], edgecolor=F.SURF, linewidth=F.GAP_LW, label="genes")
        ax.barh(y, x.in_transporter_universe, height=0.55, color=F.CAT[1], hatch="//", edgecolor=F.SURF,
                linewidth=F.GAP_LW, label="of which in the transporter universe")
        for yy, g, t in zip(y, x.genes, x.in_transporter_universe):
            ax.text(g + 0.3, yy, f"{g}" + (f" ({t} transp.)" if t else ""), va="center", fontsize=7.5, color=F.TEXT)
        ax.set_yticks(list(y), [r[:48] for r in x.role], fontsize=7.5)
        S = sets[omics]
        ax.set_title(f"{omics}: {len(S)} genes ≥ 0.90 at d60 and d89, not up at axenic d14", loc="left", fontsize=9.5)
        tr = S[S.in_transporter_universe]
        lines = [f"{r.locus_tag} {r.gene_name or ''} ({r.system_tier or '-'})" for r in tr.itertuples()]
        ax.text(0.98, 0.02, "transporter-universe genes in the set:\n" + ("\n".join(lines) if lines else "none"),
                transform=ax.transAxes, ha="right", va="bottom", fontsize=7, color=F.TEXT,
                bbox=dict(facecolor=F.SURF, edgecolor=F.GRID, linewidth=0.6))
        ax.grid(axis="x", color=F.GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(F.GRID)
        ax.tick_params(length=0)
        ax.set_xlabel("genes")
    h, l_ = axes[0].get_legend_handles_labels()
    fig.legend(h, l_, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 0.92), fontsize=8)
    figs.head(fig, "What else marks late coculture: Cyanorak top-level roles",
              "Source: data/explore/e5_set_protein.csv, e5_set_rna.csv, e5_role_counts.csv (analysis/data/de_long.csv.gz; "
              "roles from genes_by_ontology(cyanorak_role, level 0)). A gene with several roles counts under each.")
    fig.subplots_adjust(left=0.2, right=0.98, top=0.82, bottom=0.08, wspace=0.75)
    for f in figs.save(fig, "e5_late_coculture_roles"):
        print(f.name)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 70)
    print(RC.pivot_table(index="role", columns="omics", values=["genes", "in_transporter_universe"], fill_value=0).to_string())
    for omics, S in sets.items():
        print(omics, len(S), "genes; not detected at axenic d14:", int((S.axenic_d14_status == "not detected").sum()))
        print(S[S.in_transporter_universe | (S.gene_set_group != "")][["locus_tag", "gene_name", "product", "pct_d60", "pct_d89",
                                                                       "axenic_d14_status", "system_tier", "gene_set_group"]].round(3).to_string(index=False))
    print(log[0] if log else "")


if __name__ == "__main__":
    main()
