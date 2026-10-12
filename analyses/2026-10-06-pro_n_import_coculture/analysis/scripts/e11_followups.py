"""E11 small follow-ups (MED4; descriptive).

1. Above the N-starvation stimulon (no KG calls). Stimulon level per protein slice = median rank percentile of the
   detected members of MED4 Tolonen N-starvation clusters c1+c2 (data/explore/e9_membership.csv). Gene excess =
   percentile - level; system excess = median subunit excess (explore.system_excess). Tables: (a) E10 rows (High/Medium
   systems + markers + linked enzymes) ranked by mean excess at cc d60/d89 (both needed); (b) top 30 genes genome-wide
   by the same mean, restricted to genes not "up" at protein ax d14.
2. N-releasing enzymes. KG calls through methods kg_fetch.fetch (stored; re-pull with --pull):
   genes_by_ontology(ec, MED4, term_ids [ec:3.5.-.-, ec:4.3.1.-, ec:3.4.-.-], min size 1, no max) -> gene set per input
   class (rows are bound to the input term); gene_ontology_terms(ec, leaf) on those genes -> each gene's own EC numbers.
   Status heatmap in the e10 style; flag = up in cc protein d60 and d89, not up at protein ax d14, not up at any
   Tolonen N-dep timepoint (3-48 h), not up in axenic protein d31/d89 or axenic RNA d14 (E14;
   explore.coculture_flags strict).
3. N relief: median protein percentile over ax d14 -> cc d18..d89 for the N-down clusters c6-c9 and the stimulon c1+c2.
Outputs: data/explore/e11_*.csv, e11_calls.json; figures e11_above_stimulon, e11_n_releasing, e11_n_relief.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import explore as ex  # noqa: E402
import figs  # noqa: E402
import e10_system_matrix as e10  # noqa: E402
from e4b_broad_scatter import repel  # noqa: E402
from expr import kf  # noqa: E402
from figs import F, plt  # noqa: E402

OUT = HERE.parent / "data" / "explore"
PROT = [("anchor_axenic_protein", "day 14", "ax d14")] + [("anchor_cocult_protein", f"day {d}", f"cc d{d}") for d in (18, 31, 60, 89)]
CL_PREFIX = "cluster:msb4100087:med4_kmeans_nstarvation:"
EC_TERMS = ["ec:3.5.-.-", "ec:4.3.1.-", "ec:3.4.-.-"]
E11_COLNAMES = (["Aharonovich 2016 (N-replete, 20 h)*", "same study d11 (exponential)", "same study d18 (cc d18 vs ax ~d14)"]
                + [f"Tolonen N-dep {t}" for t in ("6h", "12h", "24h", "48h")]
                + ["Tolonen growth on cyanate", "Tolonen growth on urea", "protein ax d14"]
                + [f"protein cc d{d}" for d in (18, 31, 60, 89)] + ["RNA ax d14"] + [f"RNA cc d{d}" for d in (18, 31, 60, 89)])
E11_COLS = [c for c in e10.COLS if c[3] in E11_COLNAMES]
NDEP_ALL = [c for c in e10.COLS if c[1] == "cal_tolonen_ndep"]   # 3-48 h, for the flag


def pct_series(de, s, t):
    x = de[(de.short_name == s) & (de.timepoint == t)].set_index("locus_tag")
    return x.rank_percentile.where(x.percentile_valid.astype(bool)), x.expression_status


# --------------------------------------------------------------------------- 1. above stimulon
def above_stimulon(L, mem9, R):
    de = L["de"]
    stim = sorted(set(mem9[mem9.cluster_id.isin([CL_PREFIX + "1", CL_PREFIX + "2"])].locus_tag))
    lev, P, S = [], {}, {}
    for s, t, lab in PROT:
        p, st = pct_series(de, s, t)
        P[lab], S[lab] = p, st
        lev.append({"slice": lab, "short_name": s, "timepoint": t, "n_members": len(stim),
                    "n_detected": int(p.reindex(stim).notna().sum()), "stimulon_level": ex.stimulon_level(p, stim)})
    LV = pd.DataFrame(lev).set_index("slice")
    LV.to_csv(OUT / "e11_stimulon_levels.csv")
    # (a) systems
    rows = []
    for r in R.itertuples():
        d = {"row_id": r.row_id, "label": r.label, "category": r.category, "n_members": len(r.loci)}
        for lab in P:
            d[f"excess_{lab}"] = ex.system_excess(P[lab], LV.stimulon_level[lab], r.loci)
            d[f"n_det_{lab}"] = int(P[lab].reindex(r.loci).notna().sum())
        d["mean_excess_cc_d60_d89"] = ex.mean_pair(d["excess_cc d60"], d["excess_cc d89"])
        rows.append(d)
    A = pd.DataFrame(rows).sort_values("mean_excess_cc_d60_d89", ascending=False, na_position="last")
    A.insert(0, "rank", range(1, len(A) + 1))
    A.loc[A.mean_excess_cc_d60_d89.isna(), "rank"] = np.nan
    A.assign(markers_set=ex.MARKERS_NOTE).to_csv(OUT / "e11_system_excess.csv", index=False)
    # (b) genes
    G = pd.DataFrame({f"pct_{lab}": P[lab] for lab in P})
    for lab in P:
        G[f"excess_{lab}"] = G[f"pct_{lab}"] - LV.stimulon_level[lab]
    G["status_ax_d14"] = S["ax d14"].reindex(G.index).fillna("not detected")
    for lab in ("cc d60", "cc d89"):
        G[f"status_{lab}"] = S[lab].reindex(G.index).fillna("not detected")
    G["mean_excess_cc_d60_d89"] = [ex.mean_pair(a, b) for a, b in zip(G["excess_cc d60"], G["excess_cc d89"])]
    info = de.drop_duplicates("locus_tag").set_index("locus_tag")[["gene_name", "product"]]
    roles = pd.read_csv(OUT / "e5_cyanorak_roles_level0.csv").groupby("locus_tag").term_name.agg(lambda x: "|".join(sorted(set(x))))
    G = G.join(info).assign(cyanorak_role_level0=lambda d: d.index.map(roles).fillna("no Cyanorak role"))
    G["in_stimulon_c1c2"] = G.index.isin(stim)
    G.index.name = "locus_tag"
    G.to_csv(OUT / "e11_gene_excess.csv")
    B = (G[(G.status_ax_d14 != expr_up()) & G.mean_excess_cc_d60_d89.notna()]
         .sort_values("mean_excess_cc_d60_d89", ascending=False).head(30).reset_index())
    B.insert(0, "rank", range(1, len(B) + 1))
    B.to_csv(OUT / "e11_top30_genes.csv", index=False)
    return LV, A, B, G


def expr_up():
    return ex.SIG_UP


ZOOM = (-0.70, 0.05, -0.10, 0.04)   # x0, x1, y0, y1 for panel (b)


def fig_above(A, LV, flagged):
    a = A.dropna(subset=["mean_excess_cc_d60_d89"]).copy()
    cats = {"N dedicated": F.CAT[1], "N broad": F.CAT[3], "linked enzymes": F.CAT[2], "markers": F.CAT[4],
            "non-N reference": F.CAT[0], "other High/Medium": "#b9b8b2"}
    others = a[a.category == "other High/Medium"]
    lab_ids = set(a[a.category != "other High/Medium"].row_id) | set(others.nlargest(10, "mean_excess_cc_d60_d89").row_id)         | (set(flagged) & set(a.row_id))
    fig, axs = plt.subplots(1, 2, figsize=(20, 9.5), gridspec_kw={"width_ratios": [1, 1.15], "wspace": 0.12})
    x0, x1, y0, y1 = ZOOM
    inz = (a["excess_ax d14"].between(x0, x1)) & (a.mean_excess_cc_d60_d89.between(y0, y1))
    for k, ax in enumerate(axs):
        ax.axhline(0, color=F.TEXT2, linewidth=0.9, linestyle="--", zorder=1)
        ax.axvline(0, color=F.TEXT2, linewidth=0.9, linestyle="--", zorder=1)
        for c, col in cats.items():
            z = a[a.category == c]
            ax.scatter(z["excess_ax d14"], z.mean_excess_cc_d60_d89, s=34 if c != "other High/Medium" else 22, color=col,
                       edgecolor=F.SURF, linewidth=0.5, label=f"{c} ({len(z)})", zorder=3)
        if k == 0:
            lo = min(a["excess_ax d14"].min(), a.mean_excess_cc_d60_d89.min()) - 0.05
            hi = max(a["excess_ax d14"].max(), a.mean_excess_cc_d60_d89.max()) + 0.05
            ax.set_xlim(lo, hi)
            ax.set_ylim(lo, hi)
            ax.plot([lo, hi], [lo, hi], color=F.GRID, linewidth=0.8, zorder=0)
            ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, edgecolor=F.TEXT2, linewidth=0.8, linestyle=":"))
            ax.text(x0, y1 + 0.01, "zoomed in (b)", fontsize=7.5, color=F.TEXT2, va="bottom")
            sub = a[a.row_id.isin(lab_ids) & ~inz]
            ttl = "(a) all systems with ≥1 detected subunit at cc d60 and cc d89"
        else:
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            sub = a[inz]
            ttl = "(b) zoom: near the stimulon level at cc d60/d89 (all systems in the box labelled)"
        ax.text(0.01, 0, "at stimulon level (cc d60/d89)", transform=ax.get_yaxis_transform(), va="bottom", ha="left",
                fontsize=7.5, color=F.TEXT2)
        ax.text(0, 0.01, "at stimulon level (ax d14) ", transform=ax.get_xaxis_transform(), va="bottom", ha="right",
                rotation=90, fontsize=7.5, color=F.TEXT2)
        texts, anchors = [], []
        for rid, label, x, y in zip(sub.row_id, sub.label, sub["excess_ax d14"], sub.mean_excess_cc_d60_d89):
            nm = label.split(":")[0].replace("urease ureA–G", "urease")
            texts.append(ax.text(x, y, ("★ " if rid in flagged else "") + nm, fontsize=7, color=F.TEXT))
            anchors.append((x, y))
        repel(ax, texts, anchors)
        ax.set_title(ttl, loc="left", fontsize=9)
        ax.set_xlabel("system excess over stimulon, protein ax d14 (median subunit percentile − stimulon level)", fontsize=8.5)
        ax.set_ylabel("system excess over stimulon, protein cc d60/d89 (mean of the two days)", fontsize=8.5)
        ax.tick_params(labelsize=7.5)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    axs[0].legend(fontsize=7.5, frameon=False, loc="lower right", bbox_to_anchor=(0.9, 0.0))
    lv = "; ".join(f"{k} {v:.3f}" for k, v in LV.stimulon_level.items())
    figs.head(fig, "MED4 systems relative to the N-starvation stimulon level (protein)",
              "Source: data/explore/e11_system_excess.csv, e11_stimulon_levels.csv. Stimulon level = median rank percentile of "
              "the detected Tolonen MED4 cluster c1+c2 members per slice (13 of 21 detected):\n" + lv + ". Labelled in (a): every "
              "N / reference row, the 10 highest other systems, and E10 ★ strict systems (outside the zoom box). "
              "Grey diagonal = equal excess.")
    fig.subplots_adjust(top=0.88, left=0.05, right=0.99, bottom=0.07)
    return figs.save(fig, "e11_above_stimulon")


# --------------------------------------------------------------------------- 2. N-releasing enzymes
def pull_ec(log):
    from multiomics_explorer import GraphConnection, gene_ontology_terms, genes_by_ontology, to_dataframe
    with GraphConnection() as conn:
        res = kf.fetch(genes_by_ontology, "genes_by_ontology(ec, MED4, 3.5 / 4.3.1 / 3.4, min 1, no max)", log,
                       ("locus_tag", "term_id"), limit_none_ok=True, strict_inputs=True, ontology="ec",
                       organism="Prochlorococcus MED4", term_ids=EC_TERMS, min_gene_set_size=1, max_gene_set_size=None,
                       conn=conn)
        env = res["envelopes"][0]
        assert not env.get("filtered_out"), env.get("filtered_out")
        sets = to_dataframe({"results": res["results"]})
        genes = sorted(set(sets.locus_tag))
        res2 = kf.fetch(gene_ontology_terms, "gene_ontology_terms(ec, leaf, MED4 N-releasing genes)", log,
                        ("locus_tag", "term_id"), limit_none_ok=True, locus_tags=genes, organism="Prochlorococcus MED4",
                        ontology="ec", conn=conn)
        leaf = to_dataframe({"results": res2["results"]})
    sets.to_csv(OUT / "e11_ec_sets.csv", index=False)
    leaf.to_csv(OUT / "e11_ec_leaf.csv", index=False)
    (OUT / "e11_calls.json").write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")


def n_releasing(L):
    if "--pull" in sys.argv or not (OUT / "e11_ec_sets.csv").exists():
        pull_ec([])
    sets = pd.read_csv(OUT / "e11_ec_sets.csv")
    leaf = pd.read_csv(OUT / "e11_ec_leaf.csv")
    set_class = {"ec:3.5.-.-": "EC 3.5 C-N hydrolases (non-peptide)", "ec:4.3.1.-": "EC 4.3.1 ammonia-lyases",
                 "ec:3.4.-.-": "EC 3.4 peptidases"}
    counts = sets.groupby("term_id").locus_tag.nunique().rename("n_genes").reset_index()
    leaf["ec_class"] = leaf.term_id.map(ex.ec_class)
    rows = []
    for lt, g in sets.groupby("locus_tag"):
        lv = leaf[leaf.locus_tag == lt]
        inc = lv[lv.ec_class.notna()]
        classes = sorted(set(sets[sets.locus_tag == lt].term_id.map(set_class)))
        rows.append({"locus_tag": lt, "gene_name": g.gene_name.iloc[0] if "gene_name" in g else "",
                     "product": g["product"].iloc[0] if "product" in g else "",
                     "ec_class": classes[0], "ec_classes_all": "|".join(classes),
                     "ec_numbers": "|".join(sorted(inc.term_id)), "other_ec_numbers": "|".join(sorted(lv[lv.ec_class.isna()].term_id)),
                     "leaf_class_matches_set": set(inc.ec_class) <= set(classes) and len(inc) > 0})
    E = pd.DataFrame(rows)
    de = L["de"]
    slices = {(s, t): de[(de.short_name == s) & (de.timepoint == t)].set_index("locus_tag") for _, s, t, _ in e10.COLS}
    recs_all, items, flags = {}, [], []
    for r in E.itertuples():
        recs = e10.cell_records(slices, r.locus_tag, [r.locus_tag])
        recs_all[r.locus_tag] = {x["column"]: x for x in recs}
    for r in E.itertuples():
        c = recs_all[r.locus_tag]
        d = {"cc_d60_status": c["protein cc d60"]["status"], "cc_d89_status": c["protein cc d89"]["status"],
             "ax_d14_status": c["protein ax d14"]["status"], "ax_d31_status": c["protein ax d31 (death)"]["status"],
             "ax_d89_status": c["protein ax d89 (death)"]["status"], "ax_rna_d14_status": c["RNA ax d14"]["status"],
             "ndep_statuses": [c[x[3]]["status"] for x in NDEP_ALL],
             "ax_d14_pct": c["protein ax d14"]["median_percentile"], "ndep_max_pct": np.nan}
        flags.append(ex.coculture_flags(d)[0])
    E["flag_cc_specific"] = flags
    for col in E11_COLNAMES:
        E[f"status | {col}"] = [recs_all[lt][col]["status"] for lt in E.locus_tag]
        E[f"pct | {col}"] = [recs_all[lt][col]["median_percentile"] for lt in E.locus_tag]
    E = E.sort_values(["ec_class", "ec_numbers", "locus_tag"])
    E.to_csv(OUT / "e11_n_releasing.csv", index=False)
    counts.to_csv(OUT / "e11_ec_counts.csv", index=False)
    for cls, g in E.groupby("ec_class", sort=True):
        items.append(("panel", f"{cls} ({len(g)} genes)"))
        for r in g.itertuples():
            recs = [recs_all[r.locus_tag][col] for col in E11_COLNAMES]
            texts = ["" if x["median_percentile"] != x["median_percentile"] else f"{x['median_percentile']:.2f}".lstrip("0")
                     for x in recs]
            ecs = r.ec_numbers.replace("ec:", "").replace("|", ", ") or "(no leaf in class)"
            gn = r.gene_name if isinstance(r.gene_name, str) and r.gene_name not in ("", "nan") else ""
            lab = ("★ " if r.flag_cc_specific else "") + f"{r.locus_tag} {gn}  [{ecs}]  {str(r.product)[:38]}"
            items.append(("row", lab, recs, texts))
    files = e10.draw_panels(items, "e11_n_releasing", "MED4 N-releasing enzymes (EC 3.5, 4.3.1, 3.4): per-gene status",
                            "Source: data/explore/e11_n_releasing.csv (KG: genes_by_ontology(ec, term_ids ec:3.5.-.-, ec:4.3.1.-, "
                            "ec:3.4.-.-) + gene_ontology_terms(ec, leaf); analysis/data/de_long.csv.gz). Colour = the gene's own "
                            "stored status; number = rank percentile.\n★ = up in coculture protein d60 and d89, not up in axenic protein "
                            "d14/d31/d89 or axenic RNA d14, not up at any Tolonen N-dep timepoint (3–48 h; 3 h and axenic d31/d89 not shown). " + e10.AHARONOVICH_NOTE,
                            label_w=0.34, width=19, cols=E11_COLS)
    return E, counts, files


# --------------------------------------------------------------------------- 3. relief
def relief(L, mem9, prof):
    de = L["de"]
    groups = {"c1+c2 N-starvation stimulon (up)": [CL_PREFIX + "1", CL_PREFIX + "2"]}
    top = prof.set_index("cluster_id").top_cyanorak_roles
    for k in (6, 7, 8, 9):
        cid = CL_PREFIX + str(k)
        groups[f"c{k} (down): {top[cid].split(' (')[0]}"] = [cid]
    rows = []
    for name, cids in groups.items():
        m = sorted(set(mem9[mem9.cluster_id.isin(cids)].locus_tag))
        for s, t, lab in PROT:
            p, _ = pct_series(de, s, t)
            rows.append({"group": name, "slice": lab, "n_members": len(m), "n_detected": int(p.reindex(m).notna().sum()),
                         "median_percentile": ex.stimulon_level(p, m)})
    RL = pd.DataFrame(rows)
    RL.to_csv(OUT / "e11_n_relief.csv", index=False)
    # cross-check single clusters against e9
    e9 = pd.read_csv(OUT / "e9_cluster_slice_medians.csv")
    e9 = e9[(e9.block == "protein")]
    chk = []
    for k in (6, 7, 8, 9):
        name = [g for g in groups if g.startswith(f"c{k} ")][0]
        for lab in [x[2] for x in PROT]:
            a = RL[(RL.group == name) & (RL.slice == lab)].median_percentile.iloc[0]
            b = e9[(e9.cluster_id == CL_PREFIX + str(k)) & (e9.slice == lab)].median_percentile.iloc[0]
            chk.append(abs(a - b))
    assert max(chk) < 1e-12, max(chk)
    fig, ax = plt.subplots(figsize=(10, 6.2))
    xs = range(len(PROT))
    cols = [F.TEXT] + [F.CAT[0], F.CAT[6], F.CAT[2], F.CAT[3]]
    for (name, g), c in zip(RL.groupby("group", sort=False), cols):
        ax.plot(list(xs), g.median_percentile, marker="o", color=c, linewidth=2.2 if "stimulon" in name else 1.6,
                label=f"{name} (n {g.n_members.iloc[0]}; detected {g.n_detected.min()}–{g.n_detected.max()})")
    ax.axhline(0.5, color=F.TEXT2, linestyle="--", linewidth=0.9)
    ax.text(len(PROT) - 0.6, 0.505, "genome median (0.5)", fontsize=7.5, color=F.TEXT2, ha="right", va="bottom")
    ax.axvline(0.5, color=F.TEXT, linewidth=1.4)
    ax.set_xticks(list(xs), [x[2] for x in PROT], fontsize=8.5)
    ax.text(0, 1.02, "axenic", transform=ax.get_xaxis_transform(), ha="center", fontsize=8.5, fontweight="bold", color=F.TEXT2)
    ax.text(2.5, 1.02, "coculture", transform=ax.get_xaxis_transform(), ha="center", fontsize=8.5, fontweight="bold", color=F.TEXT2)
    ax.set_ylim(0, 1)
    ax.set_ylabel("median protein rank percentile of detected members", fontsize=8.5)
    ax.tick_params(labelsize=8)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    figs.head(fig, "Tolonen N-starvation clusters in this study's proteome: axenic d14 and coculture d18–d89",
              "Source: data/explore/e11_n_relief.csv (data/explore/e9_membership.csv; analysis/data/de_long.csv.gz).\n"
              "Down clusters labelled by their top Cyanorak role (e9_cluster_profiles.csv).\n'Relief' would show the down "
              "clusters (c6–c9) rising back toward 0.5 or above over time. Each slice is ranked within itself.")
    fig.subplots_adjust(top=0.8, left=0.08, right=0.56, bottom=0.1)
    return RL, figs.save(fig, "e11_n_relief")


def main():
    L = ex.load()
    mem9 = pd.read_csv(OUT / "e9_membership.csv")
    mem9 = mem9[mem9.analysis == "med4_N"]
    prof = pd.read_csv(OUT / "e9_cluster_profiles.csv")
    R = e10.rows_table(L, e10.class_listing(L))
    LV, A, B, G = above_stimulon(L, mem9, R)
    strict = set(pd.read_csv(OUT / "e10_flags.csv").query("flag_strict").row_id)
    files = fig_above(A, LV, strict)
    E, counts, f2 = n_releasing(L)
    RL, f3 = relief(L, mem9, prof)
    files += f2 + f3
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    for f in files:
        print(f.name)
    print(LV.round(3).to_string())
    print(A.head(15)[["rank", "label", "category", "excess_ax d14", "excess_cc d60", "excess_cc d89",
                      "mean_excess_cc_d60_d89"]].round(3).to_string(index=False))
    print("n systems with mean:", A.mean_excess_cc_d60_d89.notna().sum(), "n > 0:", (A.mean_excess_cc_d60_d89 > 0).sum())
    print(B.head(15)[["rank", "locus_tag", "gene_name", "product", "cyanorak_role_level0", "status_ax_d14", "excess_ax d14",
                      "mean_excess_cc_d60_d89", "in_stimulon_c1c2"]].round(3).to_string(index=False))
    print(counts.to_string(index=False))
    print(E.ec_class.value_counts().to_string())
    print("leaf mismatch:", E[~E.leaf_class_matches_set][["locus_tag", "gene_name", "ec_classes_all", "ec_numbers", "other_ec_numbers"]].to_string(index=False))
    print("multi-class:", E[E.ec_classes_all.str.contains(r"\|")][["locus_tag", "gene_name", "ec_classes_all"]].to_string(index=False))
    print(E[E.flag_cc_specific][["locus_tag", "gene_name", "product", "ec_numbers", "pct | protein ax d14", "pct | protein cc d60",
                                 "pct | protein cc d89"]].round(3).to_string(index=False))
    print(RL.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
