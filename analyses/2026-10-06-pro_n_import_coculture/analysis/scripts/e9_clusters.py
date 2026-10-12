"""E9 published co-expression clusters as empirical gene sets (descriptive).

KG calls (methods kg_fetch.fetch; single unpaged call each; returned == total_matching; natural keys asserted):
  list_clustering_analyses(analysis_ids=4, verbose)            -> clusters, member_count, KG descriptions
  genes_in_cluster(analysis_id=..., verbose) x 4                 -> membership (key locus_tag x cluster_id)
  genes_by_ontology(cyanorak_role, MIT9313, level 0)             -> MIT9313 top-level roles (MED4 from e5)
  list_experiments + differential_expression_by_gene x 2         -> MED4 iron-starvation tables (ismej.2011.49 light,
                                                                    light_2), stored in data/de_long_med4_iron.csv.gz;
                                                                    QC rows appended to data/qc_slices.csv
Steps: membership tables (count vs member_count vs the count in the cluster name); per-cluster median log2FC profile
in the clustering's own experiment (explore.classify_profile, threshold |0.5|); top Cyanorak roles; where the MED4 /
MIT9313 gene sets sit; MED4 cluster x slice median rank percentile (explore.group_median) over anchor protein, RNA and
direct contrast, plus the iron clusters.
Outputs: data/explore/e9_*.csv; figures e9_cluster_profiles, e9_anchor_cluster_read.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from multiomics_explorer import (GraphConnection, differential_expression_by_gene, genes_by_ontology, genes_in_cluster,
                                 list_clustering_analyses, list_experiments, to_dataframe)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import explore as ex  # noqa: E402
import expr  # noqa: E402
import figs  # noqa: E402
import e8_tolonen_mit9313 as e8  # noqa: E402
from expr import kf  # noqa: E402
from figs import F, plt  # noqa: E402

DATA = HERE.parent / "data"
OUT = DATA / "explore"
AN = {"med4_N": "clustering_analysis:msb4100087:med4_kmeans_nstarvation",
      "mit9313_N": "clustering_analysis:msb4100087:mit9313_kmeans_nstarvation",
      "med4_Fe": "clustering_analysis:ismej.2011.49:med4_iron_response_clusters",
      "mit9313_Fe": "clustering_analysis:ismej.2011.49:mit9313_iron_response_clusters"}
IRON_EXPS = {"10.1038/ismej.2011.49_iron_iron_starvation_med4_med4_microarray_light": "fe_med4_light",
             "10.1038/ismej.2011.49_iron_iron_starvation_med4_med4_microarray_light_2": "fe_med4_light_2"}
ANCHOR_SLICES = ([("protein", "anchor_axenic_protein", d, f"ax d{d.split()[-1]}" + (" (death)" if d != "day 14" else ""))
                  for d in ("day 14", "day 31", "day 89")]
                 + [("protein", "anchor_cocult_protein", f"day {d}", f"cc d{d}") for d in (18, 31, 60, 89)]
                 + [("RNA", "anchor_axenic_rna", "day 14", "ax d14")]
                 + [("RNA", "anchor_cocult_rna", f"day {d}", f"cc d{d}") for d in (18, 31, 60, 89)]
                 + [("direct contrast RNA", "direct_contrast_rna", "day 11", "d11 (exp.)"),
                    ("direct contrast RNA", "direct_contrast_rna", "day 18", "d18 (N-lim.)")])


def hours(tp):
    m = re.match(r"(-?\d+(?:\.\d+)?)\s*h", str(tp))
    return float(m.group(1)) if m else np.nan


def pull(log):
    with GraphConnection() as conn:
        la = kf.fetch(list_clustering_analyses, "list_clustering_analyses(4 analyses, verbose)", log, ("analysis_id",),
                      limit_none_ok=True, analysis_ids=list(AN.values()), verbose=True, conn=conn)
        mem = {}
        for k, aid in AN.items():
            res = kf.fetch(genes_in_cluster, f"genes_in_cluster({k}, verbose)", log, ("locus_tag", "cluster_id"),
                           limit_none_ok=True, analysis_id=aid, verbose=True, conn=conn)
            env = res["envelopes"][0]
            assert not env.get("not_found_analysis") and not env.get("not_found_clusters"), env
            mem[k] = to_dataframe({"results": res["results"]}).assign(analysis=k)
        r9313 = to_dataframe({"results": kf.fetch(
            genes_by_ontology, "genes_by_ontology(cyanorak_role, MIT9313, level 0)", log, ("locus_tag", "term_id"),
            limit_none_ok=True, ontology="cyanorak_role", organism="Prochlorococcus MIT9313", level=0,
            min_gene_set_size=1, max_gene_set_size=None, conn=conn)["results"]})
        le = kf.fetch(list_experiments, "list_experiments(MED4 iron starvation x2, verbose)", log, ("experiment_id",),
                      limit_none_ok=True, strict_inputs=True, experiment_ids=list(IRON_EXPS), verbose=True, conn=conn)
        meta = {e["experiment_id"]: e for e in le["results"]}
        frames = []
        for eid, short in IRON_EXPS.items():
            res = kf.fetch(differential_expression_by_gene, f"differential_expression_by_gene({short}, verbose)", log,
                           ("locus_tag", "experiment_id", "timepoint"), limit_none_ok=True, experiment_ids=[eid],
                           verbose=True, conn=conn)
            (DATA / "raw_samples" / f"{short}.json").write_text(json.dumps(res["results"][:3], indent=1, default=str),
                                                               encoding="utf-8")
            frames.append(pd.DataFrame(res["results"]).assign(short_name=short))
    fe = pd.concat(frames, ignore_index=True)
    fe["table_scope"] = fe.experiment_id.map(lambda e: meta[e]["table_scope"])
    fe["organism"] = "Prochlorococcus MED4"
    fe["is_pooled"] = fe.timepoint.map(expr.is_pooled)
    fe = expr.add_rank_percentile(fe)
    fe.to_csv(DATA / "de_long_med4_iron.csv.gz", index=False, compression="gzip")
    q = []
    for (eid, tp), g in fe.groupby(["experiment_id", "timepoint"], dropna=False):
        m = meta[eid]
        tpm = {t["timepoint"]: t for t in (m.get("timepoints") or [])}
        expct = tpm.get(tp, {}).get("gene_count", m.get("distinct_gene_count"))
        q.append({"short_name": IRON_EXPS[eid], "experiment_id": eid, "timepoint": tp, "table_scope": g.table_scope.iloc[0],
                  "list_experiments_tp_gene_count": expct, "list_experiments_has_timepoint": tp in tpm,
                  **expr.slice_qc(g, total_matching=expct), "n_detected": int(g.n_detected_in_slice.iloc[0]),
                  "percentile_valid": bool(g.percentile_valid.iloc[0])})
    Q = pd.DataFrame(q)
    old = pd.read_csv(DATA / "qc_slices.csv")
    pd.concat([old[~old.experiment_id.isin(list(IRON_EXPS))], Q], ignore_index=True).to_csv(DATA / "qc_slices.csv", index=False)
    return la["results"], mem, r9313, fe, Q


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    log = []
    analyses, mem, r9313, fe, QFe = pull(log)
    (OUT / "e9_calls.json").write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")
    # 1 membership and counts
    M = pd.concat(mem.values(), ignore_index=True)
    M[["analysis", "cluster_id", "cluster_name", "locus_tag", "gene_name", "product"]].to_csv(OUT / "e9_membership.csv", index=False)
    cnt = []
    for a in analyses:
        k = [x for x, v in AN.items() if v == a["analysis_id"]][0]
        for c in a["clusters"]:
            n_rows = int((M.cluster_id == c["cluster_id"]).sum())
            m_name = re.search(r"\((\d+) genes\)", c["name"])
            cnt.append({"analysis": k, "cluster_id": c["cluster_id"], "cluster_name": c["name"],
                        "member_count": c["member_count"], "rows_returned": n_rows,
                        "count_in_name": int(m_name.group(1)) if m_name else None,
                        "rows_eq_member_count": n_rows == c["member_count"],
                        "name_count_differs": (int(m_name.group(1)) != c["member_count"]) if m_name else None,
                        "kg_functional_description": c.get("functional_description")})
    CN = pd.DataFrame(cnt).sort_values(["analysis", "cluster_id"])
    CN.to_csv(OUT / "e9_cluster_counts.csv", index=False)
    assert CN.rows_eq_member_count.all(), CN[~CN.rows_eq_member_count]

    # 2 profiles in own experiments
    de = pd.read_csv(DATA / "de_long.csv.gz", low_memory=False)
    de9 = pd.read_csv(DATA / "de_long_mit9313_tolonen.csv.gz", low_memory=False)
    prof_src = {"med4_N": [(de, "cal_tolonen_ndep")], "mit9313_N": [(de9, "cal_tolonen_mit9313_ndep")],
                "med4_Fe": [(fe, "fe_med4_light"), (fe, "fe_med4_light_2")]}
    roles4 = pd.read_csv(OUT / "e5_cyanorak_roles_level0.csv")
    roles = {"med4": roles4, "mit9313": r9313}
    r9313.to_csv(OUT / "e9_cyanorak_roles_level0_mit9313.csv", index=False)
    prow = []
    for k, srcs in prof_src.items():
        mk = M[M.analysis == k]
        rl = roles["med4" if k.startswith("med4") else "mit9313"]
        for src, short in srcs:
            x = src[src.short_name == short]
            tps = list(x.sort_values("timepoint_order").timepoint.drop_duplicates()) if "timepoint_order" in x else \
                sorted(x.timepoint.unique(), key=hours)
            for cid, g in mk.groupby("cluster_id"):
                meds = []
                ns = []
                for tp in tps:
                    v = x[(x.timepoint == tp) & x.locus_tag.isin(g.locus_tag)].log2fc
                    meds.append(float(v.median()) if len(v) else np.nan)
                    ns.append(int(v.notna().sum()))
                hrs = [hours(t) for t in tps]
                lab, onset, peak = ex.classify_profile(hrs, meds)
                r = rl[rl.locus_tag.isin(g.locus_tag)]
                top = r.groupby("term_name").locus_tag.nunique().sort_values(ascending=False).head(3)
                prow.append({"analysis": k, "profile_source": short, "cluster_id": cid, "n_members": int(g.locus_tag.nunique()),
                             **{f"median_log2fc_{t}": m for t, m in zip(tps, meds)},
                             **{f"n_listed_{t}": n for t, n in zip(tps, ns)},
                             "profile_label": lab, "onset_h": onset, "peak_h": peak,
                             "top_cyanorak_roles": "; ".join(f"{n} ({c})" for n, c in top.items()),
                             "kg_functional_description": CN.set_index("cluster_id").kg_functional_description.get(cid)})
    P = pd.DataFrame(prow)
    P.to_csv(OUT / "e9_cluster_profiles.csv", index=False)

    # 3 where our genes sit
    L = ex.load()
    G4 = ex.gene_sets(L)
    G4 = G4[~G4.group.str.startswith("marker: phoH")].drop_duplicates(["group", "locus_tag"])
    G9 = e8.gene_set()
    wrows = []
    for strain, G, keys in (("med4", G4, ("med4_N", "med4_Fe")), ("mit9313", G9, ("mit9313_N", "mit9313_Fe"))):
        for r in G.itertuples():
            rec = {"strain": strain, "group": r.group, "locus_tag": r.locus_tag,
                   "gene_name": (L["names"].get(r.locus_tag) if strain == "med4" else r.gene_name) or ""}
            for k in keys:
                c = M[(M.analysis == k) & (M.locus_tag == r.locus_tag)].cluster_id
                rec[f"{k}_cluster"] = "|".join(sorted(c.str.split(":").str[-1])) if len(c) else "not clustered"
                if len(c) and k.endswith("_N"):
                    lab = P[(P.analysis == k) & P.cluster_id.isin(c)].profile_label
                    rec[f"{k}_profile"] = "|".join(lab)
            wrows.append(rec)
    W = pd.DataFrame(wrows)
    W.to_csv(OUT / "e9_where_genes_sit.csv", index=False)

    # 4/5 cluster x slice medians (MED4 anchor)
    crow = []
    for k in ("med4_N", "med4_Fe"):
        mk = M[M.analysis == k][["cluster_id", "locus_tag"]]
        for block, short, tp, lab in ANCHOR_SLICES:
            v = de[(de.short_name == short) & (de.timepoint == tp)].set_index("locus_tag").rank_percentile
            gm = ex.group_median(mk, v)
            for r in gm.itertuples():
                crow.append({"analysis": k, "cluster_id": r.cluster_id, "block": block, "slice": lab, "short_name": short,
                             "timepoint": tp, "n_members": r.n_members, "n_detected": r.n_detected, "median_percentile": r.median})
    for block, short, tp, lab in ANCHOR_SLICES:
        crow.append({"analysis": "genome background", "cluster_id": "all genes", "block": block, "slice": lab,
                     "short_name": short, "timepoint": tp, "n_members": None,
                     "n_detected": int(((de.short_name == short) & (de.timepoint == tp)).sum()), "median_percentile": 0.5})
    C = pd.DataFrame(crow)
    C.to_csv(OUT / "e9_cluster_slice_medians.csv", index=False)

    # figures
    files = fig_profiles(P) + fig_anchor(C, P)
    for f in files:
        print(f.name)
    pd.set_option("display.width", 260)
    pd.set_option("display.max_colwidth", 80)
    print(CN[["analysis", "cluster_id", "member_count", "rows_returned", "count_in_name"]].to_string(index=False))
    print(QFe[["short_name", "timepoint", "rows", "total_matching", "n_sig_up", "n_sig_down"]].to_string(index=False))
    print(P.drop(columns=["kg_functional_description"]).round(2).to_string(index=False))
    print(W.to_string(index=False))
    piv = C[C.analysis != "genome background"].pivot_table(index=["analysis", "cluster_id"], columns="slice",
                                                            values="median_percentile", sort=False)
    print(piv[[s[3] for s in ANCHOR_SLICES if s[3] in piv.columns]].round(2).to_string())


def short_id(cid):
    return "c" + cid.split(":")[-1]


def fig_profiles(P):
    panels = [("med4_N", "cal_tolonen_ndep", "MED4 N-starvation clusters:\nTolonen MED4 N deprivation"),
              ("mit9313_N", "cal_tolonen_mit9313_ndep", "MIT9313 N-starvation clusters:\nTolonen MIT9313 N deprivation"),
              ("med4_Fe", "fe_med4_light", "MED4 iron clusters:\nFe starvation (48 h: 2nd set)")]
    fig, axes = plt.subplots(1, 3, figsize=(17, 6.5), gridspec_kw={"width_ratios": [1.2, 1.2, 0.6]})
    norm = figs.TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
    for ax, (k, src, ttl) in zip(axes, panels):
        x = P[(P.analysis == k) & (P.profile_source == src)].copy()
        if k == "med4_Fe":   # add the light_2 experiment's 48 h column (a separate table)
            y = P[(P.analysis == k) & (P.profile_source == "fe_med4_light_2")].set_index("cluster_id")["median_log2fc_48h"]
            x["median_log2fc_48h"] = x.cluster_id.map(y)
        x["num"] = x.cluster_id.str.split(":").str[-1].astype(int)
        x = x.sort_values("num")
        cols = [c for c in x.columns if c.startswith("median_log2fc_") and x[c].notna().any()]
        cols = sorted(cols, key=lambda c: hours(c.replace("median_log2fc_", "")))
        for i, r in enumerate(x.itertuples()):
            for j, c in enumerate(cols):
                v = getattr(r, c) if hasattr(r, c) else x.iloc[i][c]
                v = x.iloc[i][c]
                if pd.isna(v):
                    ax.add_patch(plt.Rectangle((j, i), 0.95, 0.9, facecolor=F.SURF, edgecolor=F.GRID, hatch="///", linewidth=0.3))
                    continue
                ax.add_patch(plt.Rectangle((j, i), 0.95, 0.9, facecolor=figs.DIVERGING(norm(max(-3, min(3, v)))),
                                           edgecolor=F.SURF, linewidth=0.3))
                ax.text(j + 0.47, i + 0.45, f"{v:.1f}", ha="center", va="center", fontsize=6.5, color=F.TEXT)
        ax.set_xlim(0, len(cols))
        ax.set_ylim(len(x), 0)
        ax.set_xticks([j + 0.47 for j in range(len(cols))], [c.replace("median_log2fc_", "") for c in cols], fontsize=8)
        ax.xaxis.tick_top()
        ax.set_yticks([i + 0.45 for i in range(len(x))],
                      [f"{short_id(r.cluster_id)} (n={r.n_members}): {r.profile_label}" for r in x.itertuples()], fontsize=7.5)
        ax.set_title(ttl, loc="left", fontsize=9, pad=22)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
        figs.add_cbar(fig, ax, figs.DIVERGING, norm, "median log2FC (clipped at ±3)", pad=0.05, size=0.03)
    figs.head(fig, "Published co-expression clusters: median log2FC profile in their own experiment",
              "Source: data/explore/e9_cluster_profiles.csv (membership: genes_in_cluster; profiles from analysis/data/"
              "de_long*.csv.gz). Label = explore.classify_profile (threshold |0.5|). Orange up / blue down. Iron table is "
              "significant_any_timepoint (filtered).")
    fig.subplots_adjust(left=0.12, right=0.97, top=0.8, bottom=0.14, wspace=0.75)
    return figs.save(fig, "e9_cluster_profiles")


def fig_anchor(C, P):
    slices = [s[3] for s in ANCHOR_SLICES]
    blocks = [s[0] for s in ANCHOR_SLICES]
    fig, axes = plt.subplots(2, 1, figsize=(13, 10.5), gridspec_kw={"height_ratios": [1, 1.1]})
    for ax, k, ttl in ((axes[0], "med4_N", "MED4 N-starvation clusters (Tolonen k-means)"),
                       (axes[1], "med4_Fe", "MED4 iron-response clusters (ismej.2011.49)")):
        x = C[C.analysis == k]
        prof = P[(P.analysis == k)].drop_duplicates("cluster_id").set_index("cluster_id").profile_label
        cl = sorted(x.cluster_id.unique(), key=lambda c: int(c.split(":")[-1]))
        cl = [c for c in cl if x[x.cluster_id == c].n_members.max() > 0]
        cols = []
        xpos = 0.0
        prevb = None
        for s, b in zip(slices, blocks):
            if prevb is not None and b != prevb:
                xpos += 0.35
            cols.append((xpos, s, b))
            xpos += 1
            prevb = b
        for i, c in enumerate(cl):
            for xp, s, b in cols:
                r = x[(x.cluster_id == c) & (x.slice == s) & (x.block == b)]
                v = r.median_percentile.iloc[0] if len(r) else np.nan
                n = int(r.n_detected.iloc[0]) if len(r) else 0
                if pd.isna(v):
                    ax.add_patch(plt.Rectangle((xp, i), 0.95, 0.9, facecolor=F.SURF, edgecolor=F.GRID, hatch="///", linewidth=0.3))
                    continue
                ax.add_patch(plt.Rectangle((xp, i), 0.95, 0.9, facecolor=figs.PCT(v), edgecolor=F.SURF, linewidth=0.3))
                ax.text(xp + 0.47, i + 0.45, f"{v:.2f}\nn={n}", ha="center", va="center", fontsize=5.6,
                        color=F.SURF if v >= figs.PCT_DARK else F.TEXT, linespacing=1.0)
        # dividers: axenic | coculture within protein and RNA; block gaps already
        for xp, s, b in cols:
            if s.startswith("cc d18"):
                ax.axvline(xp - 0.02, color=F.TEXT, linewidth=2)
        ax.set_xlim(0, xpos)
        ax.set_ylim(len(cl), 0)
        ax.set_xticks([xp + 0.47 for xp, _, _ in cols], [s for _, s, _ in cols], rotation=45, ha="left", fontsize=7.5)
        ax.xaxis.tick_top()
        tr = ax.get_xaxis_transform()
        for b in dict.fromkeys(blocks):
            xs = [xp for xp, _, bb in cols if bb == b]
            ax.annotate(b, xy=((min(xs) + max(xs) + 0.95) / 2, 1.0), xycoords=tr, xytext=(0, 62), textcoords="offset points",
                        ha="center", fontsize=8.5, fontweight="bold", color=F.TEXT2, annotation_clip=False)
        ax.set_yticks([i + 0.45 for i in range(len(cl))],
                      [f"{short_id(c)} (n={int(x[x.cluster_id == c].n_members.max())}): {prof.get(c, '')}" for c in cl],
                      fontsize=7.5)
        ax.set_title(ttl + " — thick line: axenic | coculture", loc="left", fontsize=9.5, pad=80)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
        figs.add_cbar(fig, ax, figs.PCT, plt.Normalize(0, 1), "median rank percentile of detected members, 0–1 "
                      "(genome background 0.5)", pad=0.04, size=0.025)
    figs.head(fig, "Cluster-level read on the anchor (MED4): median rank percentile per slice",
              "Source: data/explore/e9_cluster_slice_medians.csv (membership: genes_in_cluster; percentiles from "
              "analysis/data/de_long.csv.gz). Row label = profile in the cluster's own experiment.")
    fig.subplots_adjust(left=0.24, right=0.98, top=0.78, bottom=0.06, hspace=0.7)
    return figs.save(fig, "e9_anchor_cluster_read")


if __name__ == "__main__":
    main()
