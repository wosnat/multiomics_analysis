"""Report for n_transport v1.3.0 (curated basis upgrade-only; name-only compound classes). No KG calls.

Promotions are measured against v1.1.0 (before any curated basis); the diff is against v1.2.0.
Writes into <data-dir>: p14_promotions_vs_v1.1.0.csv, p14_ftn_status.csv, p14_class_counts.csv,
p12_review_list_unclassified_N.csv (union, restricted), p14_diff_vs_v1.2.0.json, p14_report.json.
Usage: ... p14_report_v13.py --data-dir analyses/2026-10-06-pro_n_import_coculture/methods/data
"""
import argparse
import filecmp
import json
from pathlib import Path

import pandas as pd

TAGS = ["med4", "mit9313", "natl2a"]


def likely_changes(n, o, t):
    rows = []
    gn = pd.read_csv(n / f"p2_{t}_gene_roles.csv").set_index("locus_tag")
    go = pd.read_csv(o / f"p2_{t}_gene_roles.csv").set_index("locus_tag")
    com = gn.index.intersection(go.index)
    for lt in com[gn.loc[com, "likely_transporter"] != go.loc[com, "likely_transporter"]]:
        rows.append({"strain": t, "kind": "universe", "locus_tag": lt, "gene_name": gn.loc[lt, "gene_name"],
                     "product": gn.loc[lt, "product"], "old": go.loc[lt, "likely_transporter"],
                     "new": gn.loc[lt, "likely_transporter"], "basis_new": gn.loc[lt, "likely_transporter_basis"],
                     "cyanorak_q_roles": gn.loc[lt, "cyanorak_q_roles"] if "cyanorak_q_roles" in gn else None})
    nn = pd.read_csv(n / f"p4_{t}_neighbour_candidates.csv").drop_duplicates("candidate").set_index("candidate")
    no = pd.read_csv(o / f"p4_{t}_neighbour_candidates.csv").drop_duplicates("candidate").set_index("candidate")
    cn = nn.index.intersection(no.index)
    m = (nn.loc[cn, "likely_transporter"].astype(str) != no.loc[cn, "likely_transporter"].astype(str)) & ~nn.loc[cn, "in_universe"].astype(bool)
    for c in cn[m]:
        rows.append({"strain": t, "kind": "neighbour (non-universe)", "locus_tag": c, "gene_name": nn.loc[c, "candidate_name"],
                     "product": nn.loc[c, "candidate_product"], "old": no.loc[c, "likely_transporter"],
                     "new": nn.loc[c, "likely_transporter"], "basis_new": None, "cyanorak_q_roles": None})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    D = Path(a.data_dir)
    rep, prom, ftn, cls_rows, revs, diff = {}, [], [], [], [], {}
    for t in TAGS:
        n, o11, o12 = D / t, D / "v1.1.0_archive" / t, D / "v1.2.0_archive" / t
        prom += likely_changes(n, o11, t)
        gn = pd.read_csv(n / f"p2_{t}_gene_roles.csv")
        sy = pd.read_csv(n / f"p11_{t}_systems.csv")
        for r in gn[gn.gene_name.astype(str).str.fullmatch("ftn") | gn["product"].astype(str).str.fullmatch("ferritin")].itertuples():
            s = sy[sy.member_names.str.contains(r.locus_tag, na=False)]
            ftn.append({"strain": t, "locus_tag": r.locus_tag, "likely_transporter": r.likely_transporter,
                        "basis": r.likely_transporter_basis, "cyanorak_q_roles": r.cyanorak_q_roles, "tcdb_ids": r.tcdb_ids,
                        "tier": s.tier.iloc[0] if len(s) else None, "tier_reason": s.tier_reason.iloc[0] if len(s) else None})
        nb = pd.read_csv(n / f"p4_{t}_neighbour_candidates.csv").drop_duplicates("candidate")
        for r in nb[(nb.candidate_product.astype(str) == "ferritin") & ~nb.in_universe.astype(bool)].itertuples():
            ftn.append({"strain": t, "locus_tag": r.candidate, "likely_transporter": r.likely_transporter,
                        "basis": "neighbour (non-universe)", "cyanorak_q_roles": None, "tcdb_ids": r.tcdb_ids,
                        "tier": "not a system member", "tier_reason": None})
        sm = json.loads((n / f"p12_{t}_summary.json").read_text(encoding="utf-8"))
        for k, v in sm["per_class"].items():
            cls_rows.append({"strain": t, "compound_class": k, "groups": v})
        revs.append(pd.read_csv(n / f"p12_{t}_review_candidates.csv"))
        # diff vs v1.2.0
        lc = likely_changes(n, o12, t)
        so = pd.read_csv(o12 / f"p11_{t}_systems.csv").set_index("system_id")
        sn = sy.set_index("system_id")
        cs = sn.index.intersection(so.index)
        tch = [{"system_id": s, "member_names": sn.loc[s, "member_names"], "old": so.loc[s, "tier"], "new": sn.loc[s, "tier"],
                "reason_new": sn.loc[s, "tier_reason"]} for s in cs[sn.loc[cs, "tier"] != so.loc[cs, "tier"]]]
        lk = {}
        for kind in ("function_linked", "neighbour_linked"):
            a_ = pd.read_csv(o12 / f"p11_{t}_{kind}.csv"); b_ = pd.read_csv(n / f"p11_{t}_{kind}.csv")
            ka = set(zip(a_.system_id, a_.equiv_group, a_.locus_tag)); kb = set(zip(b_.system_id, b_.equiv_group, b_.locus_tag))
            lk[kind] = {"old": len(ka), "new": len(kb), "only_old": sorted(ka - kb), "only_new": sorted(kb - ka)}
        co = pd.read_csv(o12 / f"p12_{t}_compound_classes_layered.csv").set_index("equiv_group")
        cn = pd.read_csv(n / f"p12_{t}_compound_classes.csv").set_index("equiv_group")
        cg = co.index.intersection(cn.index)
        moved = (pd.DataFrame({"old": co.loc[cg, "compound_class"], "old_source": co.loc[cg, "class_source"],
                               "new": cn.loc[cg, "compound_class"]})
                 .query("old != new").groupby(["old_source", "old", "new"]).size().reset_index(name="groups"))
        fo = {p.relative_to(o12).as_posix() for p in o12.rglob("*") if p.is_file()}
        fn = {p.relative_to(n).as_posix() for p in n.rglob("*") if p.is_file()}
        same = sorted(f for f in fo & fn if filecmp.cmp(o12 / f, n / f, shallow=False))
        diff[t] = {"likely_transporter_changes_vs_v1.2.0": lc, "tier_changes": tch, "links": lk,
                   "class_changes": moved.to_dict("records"),
                   "files_identical": len(same), "files_differing": sorted((fo & fn) - set(same)),
                   "only_old": sorted(fo - fn), "only_new": sorted(fn - fo),
                   "identical_upstream": [f for f in same if f.startswith(("p1_", "p2_", "p2a_", "p2c_", "p3_", "raw/p1", "raw/p2", "raw/p3"))][:5]}
    P = pd.DataFrame(prom); P.to_csv(D / "p14_promotions_vs_v1.1.0.csv", index=False)
    F = pd.DataFrame(ftn); F.to_csv(D / "p14_ftn_status.csv", index=False)
    C = pd.DataFrame(cls_rows).pivot_table(index="compound_class", columns="strain", values="groups", fill_value=0).astype(int)
    C.to_csv(D / "p14_class_counts.csv")
    R = pd.concat(revs, ignore_index=True)
    U = (R.groupby("equiv_group").agg(names=("names", "first"), metabolite_ids=("metabolite_ids", "first"),
                                      strains=("strain", lambda s: "|".join(sorted(set(s)))),
                                      systems=("systems", lambda s: " || ".join(f"{x}" for x in s)),
                                      tiers=("tiers", lambda s: "|".join(sorted(set("|".join(s).split("|"))))),
                                      genes=("genes", lambda s: " || ".join(map(str, s))),
                                      gene_names=("gene_names", lambda s: " || ".join(map(str, s))),
                                      tcdb_families=("tcdb_families", lambda s: "|".join(sorted(set("|".join(s).split("|"))))),
                                      tcdb_family_names=("tcdb_family_names", "first")).reset_index().sort_values("names"))
    U.to_csv(D / "p12_review_list_unclassified_N.csv", index=False)
    (D / "p14_diff_vs_v1.2.0.json").write_text(json.dumps(diff, indent=1, default=str), encoding="utf-8")
    rep = {"promotions_vs_v1.1.0": P.groupby(["strain", "kind", "old", "new"]).size().reset_index(name="n").to_dict("records"),
           "ftn": F.to_dict("records"), "class_counts": C.to_dict(), "review_list_n": int(len(U))}
    (D / "p14_report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rep, indent=1, default=str))


if __name__ == "__main__":
    main()
