"""Stage 1 (analysis milestone): pull every proposal §2 experiment, all genes x timepoints, and compute rank percentiles.

KG calls (methods kg_fetch.fetch; one unpaged call per experiment, returned == total_matching asserted; natural key
(locus_tag, experiment_id, timepoint) must be unique):
  list_experiments(experiment_ids=<13 ids>, verbose=True)                    -> experiment metadata, timepoints
  differential_expression_by_gene(experiment_ids=[id], verbose=True)        -> every DE row of that experiment
Outputs (analysis/data/):
  experiments.csv                one row per experiment (role, arm, organism, omics, table_scope, n per timepoint, ...)
  de_long.csv(.gz)               one row per gene x experiment x timepoint, with rank percentile and flags
  qc_slices.csv                  QC per experiment x timepoint
  coverage_methods_universe.csv  High/Medium system members (methods v1.6.1) found in each relevant table
  checks_10.csv                  the 10 spot-check values asked for by the coordinator
  raw_samples/<exp>.json         first 3 raw rows per DE call; raw/de_raw_<n>.json.gz full dumps (gitignored)
  s1_summary.json                calls log, versions
Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/s1_pull_de.py
"""
import gzip
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import expr  # noqa: E402
from expr import kf, nt  # noqa: E402
from multiomics_explorer import GraphConnection, differential_expression_by_gene, list_experiments  # noqa: E402

DATA = HERE.parent / "data"
METHODS_DATA = expr.METHODS / "data"
P = "10.1101/2025.11.24.690089_"
# experiment_id -> (role, arm / design, short name)
EXPERIMENTS = {
    P + "growth_state_pro99lown_nutrient_starvation_med4_proteomics_coculture": ("main", "coculture culture vs own exponential", "anchor_cocult_protein"),
    P + "growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture": ("main", "coculture culture vs own exponential", "anchor_cocult_rna"),
    P + "growth_state_pro99lown_nutrient_starvation_med4_proteomics_axenic": ("reference", "axenic culture vs own exponential", "anchor_axenic_protein"),
    P + "growth_state_pro99lown_nutrient_starvation_med4_rnaseq_axenic": ("reference", "axenic culture vs own exponential", "anchor_axenic_rna"),
    P + "coculture_alteromonas_hot1a3_med4_rnaseq": ("same-study direct contrast", "coculture vs axenic", "direct_contrast_rna"),
    "10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_med4_rnaseq": ("N-replete control", "coculture vs axenic (Pro99)", "ctrl_med4_hot1a3"),
    "10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_mit9313_rnaseq_inoc_05e6": ("N-replete control", "coculture vs axenic (Pro99)", "ctrl_mit9313_inoc05e6"),
    "10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_mit9313_rnaseq_inoc_5e6": ("N-replete control", "coculture vs axenic (Pro99), high inoculum", "ctrl_mit9313_inoc5e6"),
    "10.1038/ismej.2016.82_coculture_alteromonas_macleodii_mit1002_natl2a_rnaseq": ("N-replete control", "coculture vs axenic (Pro99)", "ctrl_natl2a_mit1002"),
    "10.1038/msb4100087_growth_medium_growth_on_cyanate_as_med4_microarray": ("calibration C1", "cyanate as sole N vs N-replete", "cal_tolonen_cyanate"),
    "10.1038/msb4100087_growth_medium_growth_on_urea_as_med4_microarray": ("calibration C2", "urea as sole N vs N-replete", "cal_tolonen_urea"),
    "10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray": ("calibration C3", "N deprivation vs N-replete", "cal_tolonen_ndep"),
    "10.1038/ismej.2017.88_nitrogen_stress_ndepleted_pro99_medium_med4_rnaseq": ("calibration C4", "N-depleted vs N-replete", "cal_read_ndep"),
}
KEY = ("locus_tag", "experiment_id", "timepoint")
STRAIN_DIR = {"Prochlorococcus MED4": "med4", "Prochlorococcus MIT9313": "mit9313", "Prochlorococcus NATL2A": "natl2a"}
CHECKS = [  # (check, locus_tag, short name, timepoint label or None = single / 'latest')
    (1, "PMM0263", "anchor_cocult_protein", "day 60"), (2, "PMM0970", "anchor_cocult_rna", "day 89"),
    (3, "PMM0370", "anchor_axenic_protein", "day 14"), (4, "PMM0920", "anchor_cocult_protein", "day 18"),
    (5, "PMM0710", "anchor_cocult_rna", "day 60"), (6, "PMM0370", "cal_tolonen_cyanate", None),
    (7, "PMM0970", "cal_tolonen_urea", None), (8, "PMM0263", "cal_tolonen_ndep", "latest"),
    (9, "PMM0263", "ctrl_med4_hot1a3", None), (10, "amt1@NATL2A", "ctrl_natl2a_mit1002", "any"),
]


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "raw_samples").mkdir(exist_ok=True)
    (DATA / "raw").mkdir(exist_ok=True)
    log = []
    ids = list(EXPERIMENTS)
    frames, totals = [], {}
    with GraphConnection() as conn:
        le = kf.fetch(list_experiments, "list_experiments(13 proposal experiments, verbose)", log, ("experiment_id",),
                      limit_none_ok=True, strict_inputs=True, experiment_ids=ids, verbose=True, conn=conn)
        meta = {e["experiment_id"]: e for e in le["results"]}
        assert set(meta) == set(ids), set(ids) - set(meta)
        for i, eid in enumerate(ids):
            short = EXPERIMENTS[eid][2]
            res = kf.fetch(differential_expression_by_gene, f"differential_expression_by_gene({short}, all rows, verbose)",
                           log, KEY, limit_none_ok=True, experiment_ids=[eid], verbose=True, conn=conn)
            env = res["envelopes"][0]
            assert not env.get("not_found_experiments") and not env.get("not_matched_experiments"), env
            totals[eid] = env["total_matching"]
            rows = res["results"]
            (DATA / "raw_samples" / f"{short}.json").write_text(json.dumps(rows[:3], indent=1, default=str), encoding="utf-8")
            with gzip.open(DATA / "raw" / f"de_raw_{short}.json.gz", "wt", encoding="utf-8") as fh:
                json.dump(rows, fh, default=str)
            df = pd.DataFrame(rows)
            frames.append(df)
    de = pd.concat(frames, ignore_index=True)
    de["role"] = de.experiment_id.map(lambda e: EXPERIMENTS[e][0])
    de["arm"] = de.experiment_id.map(lambda e: EXPERIMENTS[e][1])
    de["short_name"] = de.experiment_id.map(lambda e: EXPERIMENTS[e][2])
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
    de.to_csv(DATA / "de_long.csv.gz", index=False, compression="gzip")

    # experiments table
    erows = []
    for eid, (role, arm, short) in EXPERIMENTS.items():
        m = meta[eid]
        tps = m.get("timepoints") or []
        erows.append({"short_name": short, "experiment_id": eid, "role": role, "arm": arm, "organism": m["organism_name"],
                      "omics": m["omics_type"], "table_scope": m["table_scope"],
                      "table_scope_detail": m.get("table_scope_detail"), "coculture_partner": m.get("coculture_partner"),
                      "statistical_test": m.get("statistical_test"), "control": m.get("control"),
                      "treatment": m.get("treatment"), "distinct_gene_count": m.get("distinct_gene_count"),
                      "list_experiments_timepoints": " | ".join(
                          f"{t['timepoint']} (order {t['timepoint_order']}, {t.get('growth_phase')}, n={t['gene_count']})"
                          for t in tps) or "none (single contrast)",
                      "de_timepoints": " | ".join(sorted(set(map(str, de[de.experiment_id == eid].timepoint)))),
                      "de_rows": int((de.experiment_id == eid).sum()), "de_total_matching": totals[eid]})
    E = pd.DataFrame(erows)
    E.to_csv(DATA / "experiments.csv", index=False)

    # QC per slice
    qrows = []
    for (eid, tp), g in de.groupby(["experiment_id", "timepoint"], dropna=False, sort=False):
        m = meta[eid]
        tpm = {t["timepoint"]: t for t in (m.get("timepoints") or [])}
        expected = tpm.get(tp, {}).get("gene_count", m.get("distinct_gene_count"))
        q = expr.slice_qc(g, total_matching=expected)
        qrows.append({"short_name": EXPERIMENTS[eid][2], "experiment_id": eid, "timepoint": tp,
                      "timepoint_order": g.timepoint_order.iloc[0], "proposal_timepoint": expr.proposal_timepoint(tp),
                      "is_pooled": expr.is_pooled(tp), "growth_phase": g.growth_phase.iloc[0],
                      "table_scope": g.table_scope.iloc[0], "list_experiments_tp_gene_count": expected,
                      "list_experiments_has_timepoint": tp in tpm, **q,
                      "n_detected": int(g.n_detected_in_slice.iloc[0]),
                      "percentile_valid": bool(g.percentile_valid.iloc[0]),
                      "distinct_padj_values": int(pd.to_numeric(g.padj, errors="coerce").nunique())})
    Q = pd.DataFrame(qrows).sort_values(["short_name", "timepoint_order"])
    Q.to_csv(DATA / "qc_slices.csv", index=False)

    # coverage of methods High/Medium system members
    cov = []
    for org, tag in STRAIN_DIR.items():
        sy = pd.read_csv(METHODS_DATA / tag / f"p11_{tag}_systems.csv")
        gs = pd.read_csv(METHODS_DATA / tag / f"p3_{tag}_gene_systems_gap200_roleT_crossT.csv")
        hm = set(sy[sy.tier.isin(["High", "Medium"])].system_id)
        members = set(gs[gs.system_id.isin(hm)].locus_tag)
        for eid in [e for e in ids if meta[e]["organism_name"] == org]:
            x = de[de.experiment_id == eid]
            for tp, g in x.groupby("timepoint", dropna=False):
                found = members & set(g.locus_tag)
                cov.append({"organism": org, "short_name": EXPERIMENTS[eid][2], "timepoint": tp,
                            "table_scope": meta[eid]["table_scope"], "hm_members": len(members),
                            "found": len(found), "fraction": round(len(found) / len(members), 4),
                            "missing_refseq_style": len([m for m in members - found if "_RS" in m]),
                            "missing": " ".join(sorted(members - found))[:4000]})
    C = pd.DataFrame(cov)
    C.to_csv(DATA / "coverage_methods_universe.csv", index=False)
    # locus-tag style of DE tables vs universe (RefSeq-only tags)
    idstyle = {}
    for org in STRAIN_DIR:
        lt = set(de[de.organism == org].locus_tag)
        idstyle[org] = {"de_locus_tags": len(lt), "de_refseq_style": sum("_RS" in x for x in lt)}

    # 10 checks
    chk = []
    natl2a_amt1 = None
    tag = "natl2a"
    gr = pd.read_csv(METHODS_DATA / tag / f"p2_{tag}_gene_roles.csv")
    hit = gr[gr.gene_name == "amt1"]
    natl2a_amt1 = hit.locus_tag.iloc[0] if len(hit) else None
    for n, lt, short, tp in CHECKS:
        if lt == "amt1@NATL2A":
            lt = natl2a_amt1
        x = de[(de.short_name == short) & (de.locus_tag == lt)]
        if tp == "latest" and len(x):
            x = x[x.timepoint_order == x.timepoint_order.max()]
        elif tp not in (None, "any", "latest"):
            x = x[x.timepoint == tp]
        if x.empty:
            chk.append({"check": n, "locus_tag": lt, "short_name": short, "timepoint": tp, "status": "not listed"})
        for r in x.itertuples():
            chk.append({"check": n, "locus_tag": lt, "gene_name": r.gene_name, "short_name": short, "timepoint": r.timepoint,
                        "log2fc": r.log2fc, "padj": r.padj, "expression_status": r.expression_status,
                        "rank_percentile": r.rank_percentile, "n_detected_in_slice": r.n_detected_in_slice,
                        "percentile_valid": r.percentile_valid, "status": "listed"})
    K = pd.DataFrame(chk)
    K.to_csv(DATA / "checks_10.csv", index=False)
    summ = {"expr_version": expr.__version__, "n_transport_version": nt.__version__, "de_rows": int(len(de)),
            "rows_by_experiment": de.short_name.value_counts().to_dict(), "id_style": idstyle,
            "natl2a_amt1": natl2a_amt1, "calls": log}
    (DATA / "s1_summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    print(json.dumps({k: v for k, v in summ.items() if k != "calls"}, indent=1, default=str))


if __name__ == "__main__":
    main()
