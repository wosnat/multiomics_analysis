"""Pilot step 6: currency + most-specific flag columns on the step-5 table, and per-system evidence profiles.

Inputs (<pilot-dir>): p5_<org>_system_substrates_full.csv, p4_metabolite_xref.csv,
  p5_<org>_neighbour_candidates_step5.csv, p5_<org>_linked_enzymes.csv, p3_<org>_gene_systems_<REF>.csv,
  p3_<org>_systems_<REF>.csv, p2_<org>_gene_roles.csv, raw/p2_<org>_tcdb_terms_verbose.csv;
  [--pilot] answer key (read-only) data/answer_key/pilot_genes.csv.
KG call (kg_fetch, single call per chunk, totals asserted): gene_details(universe) for transport_substrate_resolution and
  tcdb_evidence_score_max.
Outputs (<pilot-dir>): p6_currency_list.csv, p6_<org>_system_substrates_flagged.csv,
  p6_<org>_linked_enzymes_ms.csv, p6_pilot_linked_enzymes_before_after.csv, p6_<org>_system_profiles.csv,
  p6_pilot_gene_evidence_diff.csv, p6_pilot_system_profiles.csv, p6_<org>_genome_distributions.json,
  p6_<org>_summary.json.

Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/p6_evidence_profiles.py \
      --organism MED4 --pilot-dir analyses/2026-10-06-pro_n_import_coculture/methods/data/pilot
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, gene_details, to_dataframe

from common import ANSWER_KEY, PILOT_ANCHORS, REF, kf, nt, resolve_organism, role_map_hash, write_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    d = Path(a.out_dir)
    tag = a.organism.split()[-1].lower()
    full_all = pd.read_csv(d / f"p5_{tag}_system_substrates_full.csv")
    xref = pd.read_csv(d / f"p5_{tag}_metabolite_xref.csv", dtype={"chebi_id": str})
    nb5 = pd.read_csv(d / f"p5_{tag}_neighbour_candidates_step5.csv")
    le5 = pd.read_csv(d / f"p5_{tag}_linked_enzymes.csv")
    gs = pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv")
    sy = pd.read_csv(d / f"p3_{tag}_systems_{REF}.csv").set_index("system_id")
    roles = pd.read_csv(d / f"p2_{tag}_gene_roles.csv").set_index("locus_tag")
    tcv = pd.read_csv(d / "raw" / f"p2_{tag}_tcdb_terms_verbose.csv")
    log = []

    # 1. currency + ms variant
    cur = pd.DataFrame([{"metabolite_id": k, "name": v[0], "source": v[1]} for k, v in nt.CURRENCY_METABOLITES.items()])
    gmap = dict(zip(xref.metabolite_id, xref.equiv_group))
    cur["equiv_group"] = cur.metabolite_id.map(lambda m: gmap.get(m, m))
    cur["in_N_xref"] = cur.metabolite_id.isin(xref.metabolite_id)
    cur.to_csv(d / "p6_currency_list.csv", index=False)
    cg = nt.currency_groups(xref)
    full_all["is_currency"] = full_all.equiv_group.isin(cg)
    fl_all = nt.add_ms_variant(full_all)  # C2: ms & resolved & not lumping & not currency
    fl_all.to_csv(d / f"p6_{tag}_system_substrates_flagged.csv", index=False)
    full = full_all[full_all.n_status != "no_N"]  # N-class rows (contains_N + no_formula) drive links/profiles
    fl = fl_all[fl_all.n_status != "no_N"]

    le = []
    for r in fl[fl.linked_enzyme_loci_window_ms != ""].itertuples():
        for lt in r.linked_enzyme_loci_window_ms.split("|"):
            le.append({"system_id": r.system_id, "candidate": lt, "substrate_id": r.metabolite_id,
                       "substrate_name": r.metabolite_name, "equiv_group": r.equiv_group,
                       "match_basis": r.match_basis, "in_run_ms": lt in str(r.linked_enzyme_loci_run_ms).split("|")})
    lems = pd.DataFrame(le, columns=["system_id", "candidate", "substrate_id", "substrate_name", "equiv_group",
                                     "match_basis", "in_run_ms"]).drop_duplicates(["system_id", "candidate", "equiv_group"])
    lems.to_csv(d / f"p6_{tag}_linked_enzymes_ms.csv", index=False)

    sid = gs.set_index("locus_tag").system_id
    pil_sys = {c: sid[x] for c, x in PILOT_ANCHORS.items()} if a.pilot else {}
    ba = []  # pilot only (empty dict otherwise)
    for c, s in pil_sys.items():
        b = le5[le5.system_id == s].groupby("candidate").substrate_name.agg(lambda v: " | ".join(sorted(set(v))))
        af = lems[lems.system_id == s].groupby("candidate").substrate_name.agg(lambda v: " | ".join(sorted(set(v))))
        for cand in sorted(set(b.index) | set(af.index)):
            ba.append({"case": c, "system_id": s, "candidate": cand, "before_window": b.get(cand, ""),
                       "after_window_ms": af.get(cand, "")})
    if a.pilot:
        pd.DataFrame(ba).to_csv(d / f"p6_{tag}_pilot_linked_enzymes_before_after.csv", index=False)

    # 2. per-system evidence profiles
    with GraphConnection() as conn:
        org, _, _ = resolve_organism(a.organism, conn)
        rows = kf.fetch(gene_details, "gene_details(universe)", log, ("locus_tag",), chunk_param="locus_tags",
                        chunk_size=200, limit_none_ok=True, locus_tags=roles.index.tolist(), conn=conn)["results"]
    assert len(rows) == len(roles)
    gd = to_dataframe({"results": rows}).set_index("locus_tag")

    tv = tcv[["locus_tag", "term_id", "evidence", "evidence_score", "source_agreement", "pfam_support",
              "attachment_depth"]]
    lk_w = le5.groupby("system_id").candidate.nunique()
    run_le = []
    for r in full[full.linked_enzyme_loci_run.fillna("") != ""].itertuples():
        run_le += [(r.system_id, x) for x in r.linked_enzyme_loci_run.split("|")]
    lk_r = pd.DataFrame(run_le, columns=["system_id", "c"]).groupby("system_id").c.nunique() if run_le else pd.Series(dtype=int)
    lk_wms = lems.groupby("system_id").candidate.nunique()
    lk_rms = lems[lems.in_run_ms].groupby("system_id").candidate.nunique()
    miss = nb5[nb5.neighbour_class == "missing_subunit"].groupby("system_id").candidate.agg(lambda v: "|".join(sorted(set(v))))
    msN = fl[(fl.substrate_depth == "most_specific")].groupby("system_id").equiv_group.nunique()
    msNc = fl[(fl.substrate_depth == "most_specific") & ~fl.is_currency].groupby("system_id").equiv_group.nunique()
    msS = fl[fl.can_use_window_ms != nt.NOT_ELIGIBLE].groupby("system_id").equiv_group.nunique()
    nf = fl[fl.n_status == "no_formula"].groupby("system_id").equiv_group.nunique()

    prof = []
    for s, g in gs.groupby("system_id"):
        mem = sorted(g.locus_tag)
        rws = []
        for lt in mem:
            sub = tv[tv.locus_tag == lt]
            if len(sub):
                rws.append(sub.assign(role=roles.loc[lt, "gene_role"]))
            else:
                rws.append(pd.DataFrame([{"locus_tag": lt, "role": roles.loc[lt, "gene_role"], "term_id": None}]))
        srows = pd.concat(rws, ignore_index=True)
        p = nt.evidence_profile(srows)
        t = srows.dropna(subset=["term_id"])
        sc = pd.to_numeric(t.get("evidence_score"), errors="coerce")
        hom_gt0 = t[(t.evidence == "homology") & (sc > 0)].locus_tag.nunique() if len(t) else 0
        p.update({
            "system_id": s, "member_loci": "|".join(mem),
            "member_names": "|".join(f"{x}:{roles.loc[x, 'gene_name'] if isinstance(roles.loc[x, 'gene_name'], str) else ''}" for x in mem),
            "system_type": "single_gene" if len(mem) == 1 else "multi_gene",
            "n_homology_genes_score_gt0": int(hom_gt0),
            "evidence_class": ("any_homology" if p["n_homology_genes"] > 0 else
                               "all_family_inferred" if p["n_genes_with_tcdb"] > 0 else "no_tcdb"),
            "source_agreement_counts": json.dumps(t.source_agreement.value_counts().to_dict()) if len(t) else "{}",
            "pfam_support_counts": json.dumps(t.pfam_support.value_counts().to_dict()) if len(t) else "{}",
            "transport_substrate_resolution": "|".join(sorted({str(gd.loc[x, "transport_substrate_resolution"])
                                                               for x in mem if pd.notna(gd.loc[x].get("transport_substrate_resolution"))})),
            "likely_transporter_mix": json.dumps(roles.loc[mem, "likely_transporter"].value_counts().to_dict()),
            "n_ms_N_substrate_groups": int(msN.get(s, 0)),
            "n_ms_N_substrate_groups_noncurrency": int(msNc.get(s, 0)),
            "n_specific_N_substrate_groups": int(msS.get(s, 0)),
            "n_no_formula_substrate_groups": int(nf.get(s, 0)),
            "n_linked_enzymes_window": int(lk_w.get(s, 0)), "n_linked_enzymes_run": int(lk_r.get(s, 0)),
            "n_linked_enzymes_window_ms": int(lk_wms.get(s, 0)), "n_linked_enzymes_run_ms": int(lk_rms.get(s, 0)),
            "missing_subunit_neighbours": miss.get(s, ""),
            "joined_by": sy.loc[s, "joined_by"] if isinstance(sy.loc[s, "joined_by"], str) else "",
            "cross_locus_merged": bool(sy.loc[s, "cross_locus_merged"]), "n_runs": int(sy.loc[s, "n_runs"]),
            "member_runs": sy.loc[s, "member_runs"],
        })
        prof.append(p)
    pf = pd.DataFrame(prof)
    first = ["system_id", "member_loci", "member_names", "system_type", "n_genes", "n_genes_with_tcdb",
             "n_homology_genes", "n_homology_genes_score_gt0", "n_family_inferred_genes", "evidence_class",
             "tcdb_depth_max", "tcdb_depth_min_gene", "max_tcdb_evidence_score", "source_agreement_counts",
             "pfam_support_counts", "roles", "role_complete", "likely_transporter_mix",
             "transport_substrate_resolution", "n_ms_N_substrate_groups", "n_ms_N_substrate_groups_noncurrency",
             "n_specific_N_substrate_groups", "n_no_formula_substrate_groups",
             "n_linked_enzymes_window", "n_linked_enzymes_run", "n_linked_enzymes_window_ms",
             "n_linked_enzymes_run_ms", "missing_subunit_neighbours", "joined_by", "cross_locus_merged", "n_runs",
             "member_runs"]
    pf = pf[first + [c for c in pf.columns if c not in first]]
    pf.to_csv(d / f"p6_{tag}_system_profiles.csv", index=False)
    gdiff = None
    if a.pilot:
        pf[pf.system_id.isin(pil_sys.values())].assign(case=lambda x: x.system_id.map({v: k for k, v in pil_sys.items()}))             .to_csv(d / f"p6_{tag}_pilot_system_profiles.csv", index=False)
        key = pd.read_csv(ANSWER_KEY / "pilot_genes.csv")
        out = []
        for r in key.itertuples():
            sub = tv[tv.locus_tag == r.locus_tag]
            ours_t = sorted((e, round(float(x), 3)) for e, x in zip(sub.evidence, sub.evidence_score)) if len(sub) else []
            theirs_t = sorted((x.split("(")[0], round(float(x.split("(")[1].rstrip(")")), 3))
                              for x in str(r.tcdb_evidence).split(";")) if isinstance(r.tcdb_evidence, str) else []
            our_res = gd.loc[r.locus_tag].get("transport_substrate_resolution") if r.locus_tag in gd.index else None
            our_max = float(sub.evidence_score.max()) if len(sub) else None
            out.append({"case": r.case, "locus_tag": r.locus_tag, "gene_name": r.gene_name,
                        "key_tcdb_evidence": ";".join(f"{e}({x:.1f})" for e, x in theirs_t),
                        "our_tcdb_evidence": ";".join(f"{e}({x:.1f})" for e, x in ours_t),
                        "evidence_agrees": ours_t == theirs_t, "key_score_max": r.tcdb_score_max, "our_score_max": our_max,
                        "score_agrees": (pd.isna(r.tcdb_score_max) and our_max is None)
                        or (our_max is not None and abs(our_max - r.tcdb_score_max) < 1e-9),
                        "key_resolution": r.substrate_resolution, "our_resolution": our_res,
                        "resolution_agrees": (pd.isna(r.substrate_resolution) and (our_res is None or pd.isna(our_res)))
                        or our_res == r.substrate_resolution})
        gdiff = pd.DataFrame(out)
        gdiff.to_csv(d / f"p6_{tag}_pilot_gene_evidence_diff.csv", index=False)

    # per-strain expectation table (nitrate / nitrite), all four can_use definitions
    exp = pd.read_csv(d / f"p5_{tag}_expectation_check.csv")
    etab = []
    for r in exp.itertuples():
        rows = fl[fl.equiv_group.isin(str(r.groups).split("|"))]
        chk = nt.expectation_check(rows, nt.to_bool(r.expected_usable))
        etab.append({"compound": r.compound, "groups": r.groups, "expected_usable": nt.to_bool(r.expected_usable),
                     "genome_genes": r.genome_genes, "n_rows": int(len(rows)),
                     **{f"{k}_observed": json.dumps(x["observed"]) for k, x in chk.items()},
                     **{f"{k}_pass": x["pass"] for k, x in chk.items()}})
    etab = pd.DataFrame(etab)
    etab.to_csv(d / f"p6_{tag}_expected_negative_1_table.csv", index=False)

    tl = pf[pf.likely_transporter_mix.str.contains('"strong"')]
    dist = {
        "all_systems": {"n": int(len(pf)), "role_complete": pf.role_complete.value_counts().to_dict(),
                        "role_complete_by_type": pd.crosstab(pf.system_type, pf.role_complete).to_dict(),
                        "evidence_class_by_type": pd.crosstab(pf.system_type, pf.evidence_class).to_dict()},
        "systems_with_a_strong_likely_transporter_member": {
            "n": int(len(tl)), "role_complete": tl.role_complete.value_counts().to_dict(),
            "evidence_class_by_type": pd.crosstab(tl.system_type, tl.evidence_class).to_dict(),
            "homology_score_gt0_by_type": pd.crosstab(tl.system_type, tl.n_homology_genes_score_gt0 > 0).to_dict(),
            "max_score_by_type_median": tl.groupby("system_type").max_tcdb_evidence_score.median().to_dict()},
    }
    (d / f"p6_{tag}_genome_distributions.json").write_text(json.dumps(dist, indent=1, default=str), encoding="utf-8")
    summary = {
        "organism": org, "role_map_hash": role_map_hash(d), "currency_ids": len(cur),
        "currency_in_xref": int(cur.in_N_xref.sum()), "rows_all": int(len(fl_all)), "rows_N_class": int(len(fl)),
        "is_currency_rows_N": int(fl.is_currency.sum()), "is_lumping_rows_N": int(fl.is_lumping.map(nt.to_bool).sum()),
        "can_use_window_ms_N": fl.can_use_window_ms.value_counts().to_dict(),
        "can_use_run_ms_N": fl.can_use_run_ms.value_counts().to_dict(),
        "linked_pairs_window": int(len(le5)), "linked_genes_window": int(le5.candidate.nunique()),
        "linked_pairs_ms": int(len(lems)), "linked_genes_ms": int(lems.candidate.nunique()),
        "linked_ms": lems[["system_id", "candidate", "substrate_name", "in_run_ms"]].to_dict("records"),
        "expectation_check_nitrate_nitrite": etab.to_dict("records"),
        "distributions": dist, "calls": log,
    }
    if gdiff is not None:
        summary["pilot_genes"] = {"n": int(len(gdiff)), "evidence_agree": int(gdiff.evidence_agrees.sum()),
                                  "score_agree": int(gdiff.score_agrees.sum()),
                                  "resolution_agree": int(gdiff.resolution_agrees.sum())}
    write_summary(d / f"p6_{tag}_summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "calls"}, indent=1, default=str))


if __name__ == "__main__":
    main()
