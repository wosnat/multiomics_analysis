"""E8 MIT9313 Tolonen calibration (descriptive; no gate).

Data pull: the 3 MIT9313 experiments of msb4100087 (growth on nitrite, growth on urea, N deprivation 0-48 h), with the
stage-1 code path: methods kg_fetch.fetch, one unpaged differential_expression_by_gene call per experiment (natural key
locus_tag x experiment_id x timepoint, returned == total_matching), list_experiments(strict) for metadata; rank
percentiles with expr.add_rank_percentile; QC rows with expr.slice_qc. Stored SEPARATELY as
data/de_long_mit9313_tolonen.csv.gz (same columns as de_long.csv.gz) so stage-1 de_long.csv.gz stays unchanged; QC rows
are appended to data/qc_slices.csv (rows for these experiments are replaced on re-run).
Gene set (MIT9313's own methods v1.6.1 systems; markers/urease/nirA resolved by gene name / product in MIT9313 tables,
no orthologs): amt1 sys_PMT1853; urt sys_PMT2225; urease (products 'urease ...' incl. PMT2232 ureE, no coordinates);
focA sys_PMT2240 + nirA PMT2239 (linked); dpp sys_PMT0266; natFGH + grrP sys_PMT0893; agcS sys_PMT0193; proVWX
sys_PMT0553; proP sys_PMT1044; markers glnA, ntcA, glnB, pipX; non-N systems pst, phn, sul1, sul3, fut/idiA2, mnt, sbtA.
Outputs: data/de_long_mit9313_tolonen.csv.gz, data/raw_samples/<short>.json, data/explore/e8_nitrite_urea.csv,
e8_calibration_rules.csv, e8_ndep.csv, e8_ndep_up_summary.csv; figure figures/e8_tolonen_mit9313.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from multiomics_explorer import GraphConnection, differential_expression_by_gene, list_experiments

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402
import expr  # noqa: E402
import figs  # noqa: E402
from expr import kf  # noqa: E402
from figs import F, plt  # noqa: E402

DATA = HERE.parent / "data"
OUT = DATA / "explore"
EXPS = {"10.1038/msb4100087_growth_medium_growth_on_nitrite_as_mit9313_microarray": ("calibration (MIT9313)", "nitrite as sole N vs N-replete", "cal_tolonen_mit9313_nitrite"),
        "10.1038/msb4100087_growth_medium_growth_on_urea_as_mit9313_microarray": ("calibration (MIT9313)", "urea as sole N vs N-replete", "cal_tolonen_mit9313_urea"),
        "10.1038/msb4100087_nitrogen_nitrogen_deprivation_mit9313_mit9313_microarray": ("calibration (MIT9313)", "N deprivation vs N-replete", "cal_tolonen_mit9313_ndep")}
KEY = ("locus_tag", "experiment_id", "timepoint")
MD = ex.MD / "mit9313"
SYS = [("amt1", "sys_PMT1853"), ("urt", "sys_PMT2225"), ("focA", "sys_PMT2240"), ("dpp", "sys_PMT0266"),
       ("natFGH + grrP", "sys_PMT0893"), ("agcS", "sys_PMT0193"), ("proVWX", "sys_PMT0553"), ("proP", "sys_PMT1044")]
MARKER_NAMES = ["glnA", "ntcA", "glnB", "pipX"]
NONN_NAMES = r"^(pst[SCAB]|phn[CDE]|sul1|sul3|fut[ABC]|idiA2|mnt[ABC]|sbtA)$"
CAL_SUBTITLE = ("Sole-N experiments = steady-state exponential growth on the sole N source vs N-replete Pro99 medium; "
                "N deprivation = 24 h of nitrogen deprivation vs N-replete Pro99 medium (KG control / treatment fields).")


def _nonn_header(g):
    key = g.split(": ", 1)[-1]
    for pat, lab in (("pst", "pst: phosphate"), ("phn", "phn: phosphonate"), ("sul1", "sul1: sulfate"),
                     ("sul3", "sul3: sulfate"), ("fut", "fut/idiA2: iron"), ("idiA2", "fut/idiA2: iron"),
                     ("mnt", "mnt: manganese"), ("lraI", "lraI: Mn/Zn"), ("sbtA", "sbtA: bicarbonate")):
        if pat in key:
            return lab
    return g


class _Headers(dict):
    def get(self, k, d=None):
        if k in self:
            return self[k]
        return _nonn_header(k) if str(k).startswith("non-N") else d


HEADERS_MIT9313 = _Headers({
    "amt1": "amt1: ammonium transporter (ammonium)",
    "urt": "urt: urea ABC transporter (urea)",
    "focA": "focA: nitrite transporter, FNT family (nitrite)",
    "focA: linked nirA": "linked nirA: nitrite reductase (enzyme)",
    "dpp": "dpp: di/oligopeptide ABC transporter (peptides)",
    "natFGH + grrP": "natFGH + grrP: neutral amino-acid ABC transporter (amino acids)",
    "agcS": "agcS: alanine/glycine:cation symporter (amino acids)",
    "proVWX": "proVWX: glycine betaine/proline ABC transporter (osmolytes)",
    "proP": "proP: proline/betaine transporter (osmolytes)",
    "urease": "urease ureA–G: urea → ammonium (enzyme)",
    "markers": "N-starvation markers (glnA glutamine synthetase, ntcA N-control regulator, glnB PII protein, pipX NtcA co-activator)",
})


def pull():
    log, frames, totals = [], [], {}
    with GraphConnection() as conn:
        le = kf.fetch(list_experiments, "list_experiments(3 MIT9313 Tolonen experiments, verbose)", log, ("experiment_id",),
                      limit_none_ok=True, strict_inputs=True, experiment_ids=list(EXPS), verbose=True, conn=conn)
        meta = {e["experiment_id"]: e for e in le["results"]}
        assert set(meta) == set(EXPS)
        for eid, (_, _, short) in EXPS.items():
            res = kf.fetch(differential_expression_by_gene, f"differential_expression_by_gene({short}, all rows, verbose)", log,
                           KEY, limit_none_ok=True, experiment_ids=[eid], verbose=True, conn=conn)
            env = res["envelopes"][0]
            assert not env.get("not_found_experiments") and not env.get("not_matched_experiments"), env
            totals[eid] = env["total_matching"]
            (DATA / "raw_samples" / f"{short}.json").write_text(json.dumps(res["results"][:3], indent=1, default=str), encoding="utf-8")
            frames.append(pd.DataFrame(res["results"]))
    de = pd.concat(frames, ignore_index=True)
    de["role"] = de.experiment_id.map(lambda e: EXPS[e][0])
    de["arm"] = de.experiment_id.map(lambda e: EXPS[e][1])
    de["short_name"] = de.experiment_id.map(lambda e: EXPS[e][2])
    de["organism"] = de.experiment_id.map(lambda e: meta[e]["organism_name"])
    de["omics"] = de.experiment_id.map(lambda e: meta[e]["omics_type"])
    de["table_scope"] = de.experiment_id.map(lambda e: meta[e]["table_scope"])
    de["is_pooled"] = de.timepoint.map(expr.is_pooled)
    de["proposal_timepoint"] = de.timepoint.map(expr.proposal_timepoint)
    de["padj_lt_0.05"] = pd.to_numeric(de.padj, errors="coerce") < 0.05
    de = expr.add_rank_percentile(de)
    cols = ["experiment_id", "short_name", "role", "organism", "omics", "arm", "timepoint", "timepoint_order",
            "timepoint_hours", "proposal_timepoint", "is_pooled", "growth_phase", "locus_tag", "gene_name", "product",
            "log2fc", "padj", "padj_lt_0.05", "expression_status", "rank", "table_scope", "n_detected_in_slice",
            "rank_position", "rank_percentile", "percentile_valid", "percentile_note"]
    de = de[cols].sort_values(["short_name", "timepoint_order", "rank_position"])
    de.to_csv(DATA / "de_long_mit9313_tolonen.csv.gz", index=False, compression="gzip")
    qrows = []
    for (eid, tp), g in de.groupby(["experiment_id", "timepoint"], dropna=False, sort=False):
        m = meta[eid]
        tpm = {t["timepoint"]: t for t in (m.get("timepoints") or [])}
        expected = tpm.get(tp, {}).get("gene_count", m.get("distinct_gene_count"))
        q = expr.slice_qc(g, total_matching=expected)
        qrows.append({"short_name": EXPS[eid][2], "experiment_id": eid, "timepoint": tp,
                      "timepoint_order": g.timepoint_order.iloc[0], "proposal_timepoint": expr.proposal_timepoint(tp),
                      "is_pooled": expr.is_pooled(tp), "growth_phase": g.growth_phase.iloc[0],
                      "table_scope": g.table_scope.iloc[0], "list_experiments_tp_gene_count": expected,
                      "list_experiments_has_timepoint": tp in tpm, **q,
                      "n_detected": int(g.n_detected_in_slice.iloc[0]), "percentile_valid": bool(g.percentile_valid.iloc[0]),
                      "distinct_padj_values": int(pd.to_numeric(g.padj, errors="coerce").nunique())})
    Q = pd.DataFrame(qrows)
    old = pd.read_csv(DATA / "qc_slices.csv")
    old = old[~old.experiment_id.isin(list(EXPS))]
    pd.concat([old, Q], ignore_index=True).to_csv(DATA / "qc_slices.csv", index=False)
    meta_rows = [{"short_name": EXPS[e][2], "experiment_id": e, "organism": meta[e]["organism_name"], "omics": meta[e]["omics_type"],
                  "table_scope": meta[e]["table_scope"], "distinct_gene_count": meta[e].get("distinct_gene_count"),
                  "timepoints": " | ".join(f"{t['timepoint']} ({t.get('growth_phase')}, n={t['gene_count']})"
                                           for t in (meta[e].get("timepoints") or [])) or "none (single contrast)",
                  "de_rows": int((de.experiment_id == e).sum()), "total_matching": totals[e]} for e in EXPS]
    pd.DataFrame(meta_rows).to_csv(OUT / "e8_experiments.csv", index=False)
    (OUT / "e8_calls.json").write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")
    return de, Q


def gene_set():
    gs = pd.read_csv(MD / f"p3_mit9313_gene_systems_{ex.REF}.csv")
    co = pd.read_csv(MD / "raw" / "p3_mit9313_genome_coords.csv")
    nc = pd.read_csv(MD / "p3_mit9313_no_coordinate_genes.csv")
    names = {**dict(zip(co.locus_tag, co.gene_name.fillna(""))), **{lt: "" for lt in nc.locus_tag if lt not in set(co.locus_tag)}}
    prods = {**dict(zip(nc.locus_tag, nc["product"])), **dict(zip(co.locus_tag, co["product"]))}
    rows = []
    for k, sid in SYS:
        rows += [(k, lt) for lt in sorted(gs[gs.system_id == sid].locus_tag)]
        if k == "focA":
            rows.append(("focA: linked nirA", "PMT2239"))
    ure = sorted(lt for lt, p in prods.items() if str(p).lower().startswith("urease"))
    rows += [("urease", lt) for lt in ure]
    for nm in MARKER_NAMES:
        rows += [("markers", lt) for lt, n in names.items() if n == nm]
    non = gs[gs.gene_name.astype(str).str.match(NONN_NAMES)]
    for sid in sorted(set(non.system_id)):
        mem = sorted(gs[gs.system_id == sid].locus_tag)
        lab = "non-N: " + "/".join(sorted({str(n) for n in gs[gs.system_id == sid].gene_name.dropna()}))[:30]
        rows += [(lab, lt) for lt in mem]
    G = pd.DataFrame(rows, columns=["group", "locus_tag"]).drop_duplicates(["group", "locus_tag"])
    G["gene_name"] = G.locus_tag.map(names)
    names_ure = {lt: (names.get(lt) or ("ureE" if "UreE" in str(prods.get(lt)) else "")) for lt in G.locus_tag}
    G["gene_name"] = G.locus_tag.map(names_ure)
    return G


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # --pull re-queries the KG; by default the stored de_long_mit9313_tolonen.csv.gz is read (no KG call)
    if "--pull" in sys.argv or not (DATA / "de_long_mit9313_tolonen.csv.gz").exists():
        de, Q = pull()
    else:
        de = pd.read_csv(DATA / "de_long_mit9313_tolonen.csv.gz", low_memory=False)
        Q = pd.read_csv(DATA / "qc_slices.csv")
        Q = Q[Q.experiment_id.isin(list(EXPS))]
    G = gene_set()
    ni = de[de.short_name == "cal_tolonen_mit9313_nitrite"].set_index("locus_tag")
    ur = de[de.short_name == "cal_tolonen_mit9313_urea"].set_index("locus_tag")
    B = G.copy()
    nd24 = de[(de.short_name == "cal_tolonen_mit9313_ndep") & (de.timepoint == "24h")].set_index("locus_tag")
    for k, x in (("nitrite", ni), ("urea", ur), ("ndep24h", nd24)):
        B[f"{k}_pct"] = B.locus_tag.map(x.rank_percentile)
        B[f"{k}_log2fc"] = B.locus_tag.map(x.log2fc)
        B[f"{k}_status"] = B.locus_tag.map(x.expression_status).fillna("not detected")
    B.to_csv(OUT / "e8_nitrite_urea.csv", index=False)
    B[["group", "locus_tag", "gene_name"] + [f"{k}_{c}" for k in ("nitrite", "urea", "ndep24h") for c in ("pct", "status")]] \
        .to_csv(OUT / "e8a_calibration_bars.csv", index=False)

    def med(group, col):
        return float(B[B.group == group][col].median())
    focA_ni, focA_ur = med("focA", "nitrite_pct"), med("focA", "urea_pct")
    urt_ur, urt_ni = med("urt", "urea_pct"), med("urt", "nitrite_pct")
    R = pd.DataFrame([
        {"rule": "focA median percentile on nitrite >= 0.90", "value": focA_ni, "result": focA_ni >= 0.90},
        {"rule": "urt median percentile on urea >= 0.90", "value": urt_ur, "result": urt_ur >= 0.90},
        {"rule": "focA(nitrite) - focA(urea) >= 0.10", "value": focA_ni - focA_ur, "result": focA_ni - focA_ur >= 0.10 - 1e-9},
        {"rule": "urt(urea) - urt(nitrite) >= 0.10", "value": urt_ur - urt_ni, "result": urt_ur - urt_ni >= 0.10 - 1e-9},
        {"rule": "context: nirA PMT2239 percentile nitrite / urea", "value": float(ni.rank_percentile.get("PMT2239", np.nan)),
         "result": float(ur.rank_percentile.get("PMT2239", np.nan))},
        {"rule": "context: urease median percentile urea / nitrite", "value": med("urease", "urea_pct"), "result": med("urease", "nitrite_pct")},
    ])
    R["note"] = "descriptive only; MED4-style calibration rules applied to MIT9313; no gate"
    R.to_csv(OUT / "e8_calibration_rules.csv", index=False)
    nd = de[de.short_name == "cal_tolonen_mit9313_ndep"]
    tps = list(nd.sort_values("timepoint_order").timepoint.drop_duplicates())
    A = []
    for tp in tps:
        x = nd[nd.timepoint == tp].set_index("locus_tag")
        for r in G.itertuples():
            v = x.loc[r.locus_tag] if r.locus_tag in x.index else None
            A.append({"timepoint": tp, "group": r.group, "locus_tag": r.locus_tag, "gene_name": r.gene_name,
                      "log2fc": None if v is None else v.log2fc, "rank_percentile": None if v is None else v.rank_percentile,
                      "expression_status": "not detected" if v is None else v.expression_status})
    A = pd.DataFrame(A)
    A.to_csv(OUT / "e8_ndep.csv", index=False)
    up = A[A.expression_status == ex.SIG_UP].groupby(["group", "locus_tag", "gene_name"]).timepoint.agg(
        lambda s: ", ".join(sorted(s, key=lambda t: tps.index(t)))).reset_index(name="significant_up_at")
    dn = A[A.expression_status == ex.SIG_DOWN].groupby(["group", "locus_tag", "gene_name"]).timepoint.agg(
        lambda s: ", ".join(sorted(s, key=lambda t: tps.index(t)))).reset_index(name="significant_down_at")
    U = G.merge(up, how="left", on=["group", "locus_tag", "gene_name"]).merge(dn, how="left", on=["group", "locus_tag", "gene_name"])
    U.to_csv(OUT / "e8_ndep_up_summary.csv", index=False)

    # figure: (a) nitrite vs urea bars, (b) N-deprivation heatmap (log2FC)
    fig = plt.figure(figsize=(17, 14))
    gsp = fig.add_gridspec(2, 1, height_ratios=[1, 1.15], hspace=0.62)
    a = fig.add_subplot(gsp[0])
    conds = [("nitrite", "growth on nitrite as sole N (steady state)"), ("urea", "growth on urea as sole N (steady state)"),
             ("ndep24h", "N deprivation, 24 h")]
    top = figs.calibration_bars(fig, a, B.reset_index(drop=True), conds, HEADERS_MIT9313, lambda g: g.startswith("non-N"))
    h, l_ = a.get_legend_handles_labels()
    a.legend(h, l_, loc="upper left", bbox_to_anchor=(0.0, -0.2), ncol=3, fontsize=8)
    a.text(0.0, top + 0.12, "(a) rank percentile per gene: sole-N growth vs N deprivation 24 h (● / ▼ significant up / down, stored)",
           transform=a.transAxes, fontsize=9.5, ha="left", va="bottom")
    b = fig.add_subplot(gsp[1])
    norm = figs.TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
    piv = A.pivot_table(index=["group", "locus_tag"], columns="timepoint", values="log2fc", aggfunc="first")
    stp = A.pivot_table(index=["group", "locus_tag"], columns="timepoint", values="expression_status", aggfunc="first")
    order = list(dict.fromkeys(zip(G.group, G.locus_tag)))
    for i, key in enumerate(order):
        for j, tp in enumerate(tps):
            v = piv[tp].get(key, np.nan) if tp in piv.columns else np.nan
            st = stp[tp].get(key, "not detected") if tp in stp.columns else "not detected"
            if pd.isna(v):
                b.add_patch(plt.Rectangle((i, j), 0.94, 0.94, facecolor=F.SURF, edgecolor=F.GRID, hatch="///", linewidth=0.3))
                continue
            b.add_patch(plt.Rectangle((i, j), 0.94, 0.94, facecolor=figs.DIVERGING(norm(max(-3, min(3, v)))), edgecolor=F.SURF,
                                      linewidth=0.3))
            if st in (ex.SIG_UP, ex.SIG_DOWN):
                b.plot(i + 0.47, j + 0.47, marker="o" if st == ex.SIG_UP else "v", markersize=3, color=F.TEXT)
    gname = dict(zip(G.locus_tag, G.gene_name))
    b.set_xlim(0, len(order))
    b.set_ylim(len(tps), 0)
    b.set_yticks([j + 0.47 for j in range(len(tps))], tps, fontsize=8)
    b.set_xticks([i + 0.47 for i in range(len(order))], [gname.get(lt) or lt for _, lt in order], rotation=90, fontsize=6.5)
    prev = None
    for i, (g, _) in enumerate(order):
        if g != prev:
            b.text(i, -0.25, g, fontsize=6.5, rotation=30, color=F.TEXT2, ha="left", va="bottom")
        prev = g
    for s in b.spines.values():
        s.set_visible(False)
    b.tick_params(length=0)
    figs.add_cbar(fig, b, figs.DIVERGING, norm, "log2FC (clipped at ±3)", pad=0.2, size=0.025)
    b.set_title("(b) N deprivation, 0–48 h: log2FC (orange up / blue down, clipped ±3); ● / ▼ significant; "
                "hatched = not detected", loc="left", fontsize=9.5, pad=42)
    figs.head(fig, "MIT9313 Tolonen calibration on MIT9313's own systems",
              CAL_SUBTITLE + "\nSource: analysis/data/de_long_mit9313_tolonen.csv.gz (msb4100087 MIT9313: nitrite, urea, "
              "N deprivation); methods v1.6.1 MIT9313 systems; data/explore/e8a_calibration_bars.csv, e8_ndep.csv")
    fig.subplots_adjust(left=0.04, right=0.95, top=0.75, bottom=0.12)
    for f in figs.save(fig, "e8_tolonen_mit9313"):
        print(f.name)
    pd.set_option("display.width", 250)
    print(Q[["short_name", "timepoint", "rows", "total_matching", "rows_match_total", "duplicate_rows", "negative_share",
             "n_sig_up", "n_sig_down", "n_padj_lt_0.05", "distinct_padj_values", "min_abs_log2fc_significant"]].round(3).to_string(index=False))
    print(B[["group", "locus_tag", "gene_name", "nitrite_pct", "nitrite_status", "urea_pct", "urea_status"]].round(3).to_string(index=False))
    print(R.round(4).to_string(index=False))
    print(U.fillna("").to_string(index=False))


if __name__ == "__main__":
    main()
