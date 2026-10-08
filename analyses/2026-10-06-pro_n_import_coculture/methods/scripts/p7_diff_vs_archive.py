"""Diff the v1.0 MED4 run (data/med4) against the archived v0.9 pilot outputs (data/pilot_v0.9_archive).

No KG calls. Writes data/med4/p7_med4_diff_vs_v0.9.json and per-step CSVs (p7_med4_diff_*.csv), plus
the no-formula (I1) additions per pilot system.
Usage (repo root): .venv/Scripts/python.exe .../scripts/p7_diff_vs_archive.py --new-dir .../data/med4 --old-dir .../data/pilot_v0.9_archive
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from common import PILOT_ANCHORS, REF


def partition(df):
    return {frozenset(g.locus_tag) for _, g in df.groupby("system_id")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new-dir", required=True)
    ap.add_argument("--old-dir", required=True)
    a = ap.parse_args()
    n, o = Path(a.new_dir), Path(a.old_dir)
    out = {}

    # step 1 / 2c: universe
    u_old = set(pd.read_csv(o / "p1_med4_transporter_genes.csv").locus_tag)
    u_p1 = set(pd.read_csv(n / "p1_med4_transporter_genes.csv").locus_tag)
    u_new = set(pd.read_csv(n / "p2c_med4_universe.csv").locus_tag)
    out["step1"] = {"old": len(u_old), "new_p1": len(u_p1), "p1_identical": u_old == u_p1,
                    "new_after_p2c": len(u_new), "added": sorted(u_new - u_old), "removed": sorted(u_old - u_new)}

    # step 2: role map + gene roles
    rm_o, rm_n = pd.read_csv(o / "p2_pfam_role_map.csv"), pd.read_csv(n / "p2_pfam_role_map.csv")
    m = rm_o[["pfam_id", "role"]].merge(rm_n[["pfam_id", "role"]], on="pfam_id", how="outer", suffixes=("_old", "_new"))
    g_o, g_n = pd.read_csv(o / "p2_med4_gene_roles.csv"), pd.read_csv(n / "p2_med4_gene_roles.csv")
    gm = g_o[["locus_tag", "gene_role", "likely_transporter"]].merge(
        g_n[["locus_tag", "gene_role", "likely_transporter"]], on="locus_tag", how="outer", suffixes=("_old", "_new"))
    ch = gm[(gm.gene_role_old != gm.gene_role_new) | (gm.likely_transporter_old != gm.likely_transporter_new)]
    ch.to_csv(n / "p7_med4_diff_step2_gene_roles.csv", index=False)
    out["step2"] = {"domains_old": len(rm_o), "domains_new": len(rm_n),
                    "domains_added": m[m.role_old.isna()][["pfam_id", "role_new"]].to_dict("records"),
                    "domain_role_changed": m[m.role_old.notna() & m.role_new.notna() & (m.role_old != m.role_new)]
                    .to_dict("records"),
                    "genes_changed_or_added": ch.to_dict("records")}

    # step 3: reference partition
    s_o = pd.read_csv(o / f"p3_med4_gene_systems_{REF}.csv")
    s_n = pd.read_csv(n / f"p3_med4_gene_systems_{REF}.csv")
    po, pn = partition(s_o), partition(s_n)
    gone, new = po - pn, pn - po
    out["step3"] = {"systems_old": len(po), "systems_new": len(pn),
                    "systems_only_old": [sorted(x) for x in gone], "systems_only_new": [sorted(x) for x in new]}

    # step 4: neighbour classes
    k = ["system_id", "candidate"]
    nb_o = pd.read_csv(o / "p4_med4_neighbour_candidates.csv")[k + ["neighbour_class"]]
    nb_n = pd.read_csv(n / "p4_med4_neighbour_candidates.csv")[k + ["neighbour_class", "candidate_name"]]
    mm = nb_o.merge(nb_n, on=k, how="outer", suffixes=("_old", "_new"), indicator=True)
    mm.to_csv(n / "p7_med4_diff_step4_neighbours.csv", index=False)
    both = mm[mm._merge == "both"]
    out["step4"] = {"rows_old": len(nb_o), "rows_new": len(nb_n),
                    "rows_only_old": int((mm._merge == "left_only").sum()),
                    "rows_only_new": int((mm._merge == "right_only").sum()),
                    "rows_only_new_systems": sorted(set(mm[mm._merge == "right_only"].system_id)),
                    "class_transitions_on_common_rows":
                        both.groupby(["neighbour_class_old", "neighbour_class_new"]).size()
                        .reset_index(name="n").query("neighbour_class_old != neighbour_class_new").to_dict("records")}
    # enzyme-side N metabolites: C1 check (old paged run vs new single calls)
    eo = pd.read_csv(o / "p4_med4_enzyme_candidate_n_metabolites.csv")
    en = pd.read_csv(n / "p4_med4_enzyme_candidate_metabolites.csv")
    en_N = en[en.n_status == "contains_N"]
    ko, kn = set(zip(eo.locus_tag, eo.metabolite_id)), set(zip(en_N.locus_tag, en_N.metabolite_id))
    raw_old = pd.read_csv(o / "raw" / "p4_med4_enzyme_candidate_metabolism_N_raw.csv")
    out["step4_metabolism_arm"] = {
        "old_N_pairs": len(ko), "new_N_pairs": len(kn), "only_old": sorted(ko - kn)[:20], "only_new": sorted(kn - ko)[:20],
        "old_raw_rows": len(raw_old),
        "old_raw_duplicates_on_locus_metabolite_reaction": int(raw_old.duplicated(["locus_tag", "metabolite_id",
                                                                                 "reaction_id"]).sum()),
        "new_rows_by_n_status": en.n_status.value_counts().to_dict()}

    # step 5: substrate rows (contains_N subset vs old N table)
    kk = ["locus_tag", "metabolite_id", "tcdb_family_id"]
    f_o = pd.read_csv(o / "p5_med4_system_substrates_full.csv")
    f_n = pd.read_csv(n / "p5_med4_system_substrates_full.csv")
    f_nN = f_n[f_n.n_status == "contains_N"]
    raw5 = pd.read_csv(o / "raw" / "p5_med4_transport_N_raw.csv")
    j = f_o.merge(f_nN, on=kk, how="outer", suffixes=("_old", "_new"), indicator=True)
    jb = j[j._merge == "both"]
    cu = {c: int((jb[f"{c}_old"].fillna("") != jb[f"{c}_new"].fillna("")).sum())
          for c in ("can_use_window", "can_use_run", "substrate_depth", "system_id", "match_basis")}
    jch = jb[(jb.can_use_window_old != jb.can_use_window_new) | (jb.can_use_run_old != jb.can_use_run_new)
             | (jb.system_id_old != jb.system_id_new)]
    jch[kk + ["system_id_old", "system_id_new", "can_use_window_old", "can_use_window_new", "can_use_run_old",
              "can_use_run_new", "match_basis_old", "match_basis_new"]].to_csv(n / "p7_med4_diff_step5_changed_rows.csv",
                                                                               index=False)
    out["step5"] = {"old_rows": len(f_o), "new_rows_all": len(f_n), "new_rows_by_n_status": f_n.n_status.value_counts().to_dict(),
                    "contains_N_only_old": int((j._merge == "left_only").sum()),
                    "contains_N_only_new": int((j._merge == "right_only").sum()),
                    "old_raw_duplicates_on_natural_key": int(raw5.duplicated(kk).sum()),
                    "changed_on_common_rows": cu}
    nf = f_n[f_n.n_status == "no_formula"]
    sid = s_n.set_index("locus_tag").system_id
    nfp = []
    for case, anchor in PILOT_ANCHORS.items():
        x = nf[nf.system_id == sid[anchor]]
        nfp.append({"case": case, "system_id": sid[anchor], "no_formula_rows": len(x),
                    "no_formula_groups": int(x.equiv_group.nunique()),
                    "most_specific_rows": int((x.substrate_depth == "most_specific").sum()),
                    "examples": " | ".join(sorted(set(map(str, x.metabolite_name)))[:8])})
    pd.DataFrame(nfp).to_csv(n / "p7_med4_no_formula_pilot.csv", index=False)
    out["I1_no_formula_pilot"] = nfp

    # step 6: linked enzymes (ms) + profiles
    lo = pd.read_csv(o / "p6_med4_linked_enzymes_ms.csv")
    ln = pd.read_csv(n / "p6_med4_linked_enzymes_ms.csv")
    a_, b_ = set(zip(lo.system_id, lo.candidate, lo.substrate_name)), set(zip(ln.system_id, ln.candidate, ln.substrate_name))
    po6 = pd.read_csv(o / "p6_med4_system_profiles.csv").set_index("member_loci")
    pn6 = pd.read_csv(n / "p6_med4_system_profiles.csv").set_index("member_loci")
    common = po6.index.intersection(pn6.index)
    cols = ["n_homology_genes", "n_family_inferred_genes", "tcdb_depth_max", "max_tcdb_evidence_score", "role_complete",
            "n_linked_enzymes_window", "n_linked_enzymes_window_ms", "n_ms_N_substrate_groups"]
    diffs = {c: int((po6.loc[common, c].astype(str) != pn6.loc[common, c].astype(str)).sum()) for c in cols}
    out["step6"] = {"linked_ms_old": len(a_), "linked_ms_new": len(b_), "linked_ms_only_old": sorted(a_ - b_),
                    "linked_ms_only_new": sorted(b_ - a_), "profiles_old": len(po6), "profiles_new": len(pn6),
                    "profile_column_changes_on_common_systems": diffs}
    (n / "p7_med4_diff_vs_v0.9.json").write_text(json.dumps(out, indent=1, default=str), encoding="utf-8")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
