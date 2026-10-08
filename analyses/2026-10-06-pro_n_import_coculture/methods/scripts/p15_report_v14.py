"""Report for n_transport v1.4.0 (fix package 2026-10-08: catalogue-only tier Low; KO basis upgrade-only;
known_false_positive; RefSeq fragments; name rules). No KG calls. Diff is against data/v1.3.0_archive.

Writes into <data-dir>: p15_likely_transporter_changes.csv, p15_tier_changes.csv, p15_tier_counts.csv,
p15_known_false_positive.csv, p15_fragments.csv, p15_class_counts.csv, p15_class_changes.csv,
p12_review_list_unclassified_N.csv (union, regenerated), p15_review_list_diff.csv, p15_link_rows_by_tier.csv,
p15_pilot_check.csv, p15_report.json.
Usage: ... p15_report_v14.py --data-dir analyses/2026-10-06-pro_n_import_coculture/methods/data
"""
import argparse
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
                     "new": gn.loc[lt, "likely_transporter"], "basis": gn.loc[lt, "likely_transporter_basis"]})
    nn = pd.read_csv(n / f"p4_{t}_neighbour_candidates.csv").drop_duplicates("candidate").set_index("candidate")
    no = pd.read_csv(o / f"p4_{t}_neighbour_candidates.csv").drop_duplicates("candidate").set_index("candidate")
    cn = nn.index.intersection(no.index)
    m = (nn.loc[cn, "likely_transporter"].astype(str) != no.loc[cn, "likely_transporter"].astype(str)) \
        & ~nn.loc[cn, "in_universe"].astype(bool)
    for c in cn[m]:
        rows.append({"strain": t, "kind": "neighbour (non-universe)", "locus_tag": c,
                     "gene_name": nn.loc[c, "candidate_name"], "product": nn.loc[c, "candidate_product"],
                     "old": no.loc[c, "likely_transporter"], "new": nn.loc[c, "likely_transporter"], "basis": None})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    D = Path(a.data_dir)
    A = D / "v1.3.0_archive"
    lt_rows, tier_rows, tc_rows, kfp, frag, cls_rows, cls_ch, revs, lk_rows, pil = ([] for _ in range(10))
    for t in TAGS:
        n, o = D / t, A / t
        lt_rows += likely_changes(n, o, t)
        sn = pd.read_csv(n / f"p11_{t}_systems.csv").set_index("system_id")
        so = pd.read_csv(o / f"p11_{t}_systems.csv").set_index("system_id")
        for s in sorted(set(sn.index) | set(so.index)):
            old = so.tier.get(s, "absent")
            new = sn.tier.get(s, "absent")
            if old != new:
                tier_rows.append({"strain": t, "system_id": s,
                                  "member_names": sn.member_names.get(s, so.member_names.get(s)),
                                  "old": old, "new": new, "old_reason": so.tier_reason.get(s),
                                  "new_reason": sn.tier_reason.get(s),
                                  "likely_members_old": so.likely_transporter_members.get(s),
                                  "likely_members_new": sn.likely_transporter_members.get(s),
                                  "was_high_or_medium": old in ("High", "Medium")})
        for k in sorted(set(sn.tier) | set(so.tier)):
            tc_rows.append({"strain": t, "tier": k, "before": int((so.tier == k).sum()), "after": int((sn.tier == k).sum())})
        for s, r in sn[sn.known_false_positive.astype(bool)].iterrows():
            kfp.append({"strain": t, "system_id": s, "member_names": r.member_names, "tier": r.tier,
                        "tier_reason": r.tier_reason, "known_false_positive_reason": r.known_false_positive_reason})
        f = pd.read_csv(n / f"p11_{t}_fragments.csv")
        f.insert(0, "strain", t)
        frag.append(f)
        sm = json.loads((n / f"p12_{t}_summary.json").read_text(encoding="utf-8"))
        smo = json.loads((o / f"p12_{t}_summary.json").read_text(encoding="utf-8"))
        for k in sorted(set(sm["per_class"]) | set(smo["per_class"])):
            cls_rows.append({"strain": t, "compound_class": k, "before": smo["per_class"].get(k, 0),
                             "after": sm["per_class"].get(k, 0)})
        cn = pd.read_csv(n / f"p12_{t}_compound_classes.csv").set_index("equiv_group")
        co = pd.read_csv(o / f"p12_{t}_compound_classes.csv").set_index("equiv_group")
        cg = cn.index.intersection(co.index)
        ch = pd.DataFrame({"names": cn.loc[cg, "names"], "old": co.loc[cg, "compound_class"],
                           "new": cn.loc[cg, "compound_class"], "rule": cn.loc[cg, "name_rule"]}).query("old != new")
        cls_ch.append(ch.reset_index().assign(strain=t))
        revs.append(pd.read_csv(n / f"p12_{t}_review_candidates.csv"))
        for kind in ("function_linked", "neighbour_linked"):
            x = pd.read_csv(n / f"p11_{t}_{kind}.csv")
            xo = pd.read_csv(o / f"p11_{t}_{kind}.csv")
            for k, v in x.system_tier.value_counts().items():
                lk_rows.append({"strain": t, "table": kind, "system_tier": k, "rows": int(v)})
            lk_rows.append({"strain": t, "table": kind, "system_tier": "TOTAL", "rows": int(len(x)),
                            "rows_v1.3.0": int(len(xo)),
                            "rows_on_fragments": int((x.fragment_of.astype(str) != "none").sum())})
        # pilot / anchors
        gr = pd.read_csv(n / f"p2_{t}_gene_roles.csv")
        if (n / f"p11_{t}_pilot.csv").exists():
            for r in pd.read_csv(n / f"p11_{t}_pilot.csv").itertuples():
                pil.append({"strain": t, "case": r.case, "system_id": r.system_id, "tier": r.tier,
                            "tier_reason": r.tier_reason, "function_linked": r.function_linked,
                            "neighbour_linked": r.neighbour_linked})
        fl = pd.read_csv(n / f"p11_{t}_function_linked.csv")
        nl = pd.read_csv(n / f"p11_{t}_neighbour_linked.csv")
        for lt in gr[gr.gene_name.astype(str) == "focA"].locus_tag:
            s = sn[sn.member_names.str.contains(lt, na=False)]
            for sid, r in s.iterrows():
                pil.append({"strain": t, "case": "focA", "system_id": sid, "tier": r.tier, "tier_reason": r.tier_reason,
                            "function_linked": "; ".join(f"{x.locus_tag}({x.enzyme_name})->{x.substrate_names}"
                                                         for x in fl[fl.system_id == sid].itertuples()),
                            "neighbour_linked": "; ".join(f"{x.locus_tag}({x.enzyme_name})->{x.substrate_names}"
                                                          f"{'' if x.fragment_of == 'none' else ' [fragment_of ' + x.fragment_of + ']'}"
                                                          for x in nl[nl.system_id == sid].itertuples()),
                            "n_neighbour_linked_enzymes": int(r.n_neighbour_linked_enzymes),
                            "n_function_linked_enzymes": int(r.n_function_linked_enzymes)})
    L = pd.DataFrame(lt_rows); L.to_csv(D / "p15_likely_transporter_changes.csv", index=False)
    T = pd.DataFrame(tier_rows); T.to_csv(D / "p15_tier_changes.csv", index=False)
    TC = pd.DataFrame(tc_rows); TC.to_csv(D / "p15_tier_counts.csv", index=False)
    K = pd.DataFrame(kfp); K.to_csv(D / "p15_known_false_positive.csv", index=False)
    F = pd.concat(frag, ignore_index=True); F.to_csv(D / "p15_fragments.csv", index=False)
    C = pd.DataFrame(cls_rows); C.to_csv(D / "p15_class_counts.csv", index=False)
    CC = pd.concat(cls_ch, ignore_index=True); CC.to_csv(D / "p15_class_changes.csv", index=False)
    LK = pd.DataFrame(lk_rows); LK.to_csv(D / "p15_link_rows_by_tier.csv", index=False)
    P = pd.DataFrame(pil); P.to_csv(D / "p15_pilot_check.csv", index=False)
    R = pd.concat(revs, ignore_index=True)
    U = (R.groupby("equiv_group").agg(names=("names", "first"), metabolite_ids=("metabolite_ids", "first"),
                                      strains=("strain", lambda s: "|".join(sorted(set(s)))),
                                      systems=("systems", lambda s: " || ".join(map(str, s))),
                                      tiers=("tiers", lambda s: "|".join(sorted(set("|".join(s).split("|"))))),
                                      genes=("genes", lambda s: " || ".join(map(str, s))),
                                      gene_names=("gene_names", lambda s: " || ".join(map(str, s))),
                                      tcdb_families=("tcdb_families", lambda s: "|".join(sorted(set("|".join(s).split("|"))))),
                                      tcdb_family_names=("tcdb_family_names", "first")).reset_index().sort_values("names"))
    U.to_csv(D / "p12_review_list_unclassified_N.csv", index=False)
    UO = pd.read_csv(A / "p12_review_list_unclassified_N.csv")
    gone = UO[~UO.equiv_group.isin(U.equiv_group)].assign(change="removed")
    new = U[~U.equiv_group.isin(UO.equiv_group)].assign(change="added")
    RD = pd.concat([gone, new], ignore_index=True)[["change", "equiv_group", "names", "strains", "systems", "tiers",
                                                     "gene_names", "tcdb_families"]]
    RD.to_csv(D / "p15_review_list_diff.csv", index=False)
    rep = {"likely_transporter_changes": L.groupby(["strain", "kind", "old", "new"]).size().reset_index(name="n").to_dict("records") if len(L) else [],
           "tier_changes": T.groupby(["strain", "old", "new"]).size().reset_index(name="n").to_dict("records") if len(T) else [],
           "tier_counts": tc_rows, "known_false_positive": kfp, "fragments": F.to_dict("records"),
           "review_list_n": int(len(U)), "review_list_n_v1.3.0": int(len(UO)),
           "review_removed": int(len(gone)), "review_added": int(len(new)), "link_rows_by_tier": lk_rows}
    (D / "p15_report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rep, indent=1, default=str))


if __name__ == "__main__":
    main()
