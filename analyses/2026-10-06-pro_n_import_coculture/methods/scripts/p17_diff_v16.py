"""Diff report v1.5.0 -> v1.6.0 (Cyanorak Q roles: 4th universe source + superfamily-only lift; listing basis).
No KG calls. Compares data/<tag>/ with data/v1.5.0_archive/<tag>/. Writes into <data-dir>:
  p17_universe_additions.csv   genes in the v1.6 universe but not in v1.5 (sources, role, likely_transporter, system, tier)
  p17_membership_changes.csv   every v1.6 system whose member set differs from every v1.5 system (locus tags)
  p17_tier_changes.csv         every locus whose system tier changed (existing loci; added loci are in the additions file)
  p17_tier_counts.csv          tier counts before / after per strain
  p17_report.json              counts
Usage: ... p17_diff_v16.py --data-dir analyses/2026-10-06-pro_n_import_coculture/methods/data
"""
import argparse
import json
from pathlib import Path

import pandas as pd

TAGS = ["med4", "mit9313", "natl2a"]
REF = "gap200_roleT_crossT"
TIERS = ["High", "Medium", "Low", "not_transporter"]


def load(base, t):
    return (pd.read_csv(base / t / f"p3_{t}_gene_systems_{REF}.csv"),
            pd.read_csv(base / t / f"p11_{t}_systems.csv").set_index("system_id"),
            pd.read_csv(base / t / f"p2_{t}_gene_roles.csv"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    D = Path(a.data_dir)
    A = D / "v1.5.0_archive"
    uni, mem_rows, tier_rows, tc_rows, rep = [], [], [], [], {}
    for t in TAGS:
        gn, sn, rn = load(D, t)
        go, so, ro = load(A, t)
        sid_n, sid_o = dict(zip(gn.locus_tag, gn.system_id)), dict(zip(go.locus_tag, go.system_id))
        add = rn[~rn.locus_tag.isin(ro.locus_tag)].copy()
        add["system_id"] = add.locus_tag.map(sid_n)
        add["system_members"] = add.system_id.map(sn.member_names)
        add["tier"] = add.system_id.map(sn.tier)
        add["tier_reason"] = add.system_id.map(sn.tier_reason)
        add.insert(0, "strain", t)
        uni.append(add[["strain", "locus_tag", "gene_name", "product", "src_tcdb", "src_brite", "src_pfam_role",
                        "src_cyanorak_q", "cyanorak_q_roles", "gene_role", "likely_transporter",
                        "likely_transporter_basis", "tcdb_ids", "system_id", "system_members", "tier", "tier_reason"]])
        mn = gn.groupby("system_id").locus_tag.agg(frozenset).to_dict()
        old_sets = set(go.groupby("system_id").locus_tag.agg(frozenset))
        for sid, m in sorted(mn.items()):
            if m in old_sets:
                continue
            parts = sorted({sid_o.get(x, "new gene") for x in m})
            mem_rows.append({"strain": t, "system_id": sid, "member_names": sn.loc[sid, "member_names"],
                             "members": "|".join(sorted(m)), "tier": sn.loc[sid, "tier"],
                             "tier_reason": sn.loc[sid, "tier_reason"], "v15_systems": "|".join(parts),
                             "v15_tiers": "|".join(str(so.tier.get(p, "-")) for p in parts),
                             "added_genes": "|".join(sorted(x for x in m if x not in sid_o))})
        for lt in sorted(set(sid_n) & set(sid_o)):
            tn, to = sn.tier[sid_n[lt]], so.tier[sid_o[lt]]
            if tn != to:
                tier_rows.append({"strain": t, "locus_tag": lt, "gene_name": rn.set_index("locus_tag").gene_name.get(lt),
                                  "old_tier": to, "new_tier": tn, "old_reason": so.tier_reason[sid_o[lt]],
                                  "new_reason": sn.tier_reason[sid_n[lt]], "system_id": sid_n[lt],
                                  "member_names": sn.member_names[sid_n[lt]]})
        for k in TIERS:
            tc_rows.append({"strain": t, "tier": k, "before": int((so.tier == k).sum()), "after": int((sn.tier == k).sum())})
        lo = ro.set_index("locus_tag").likely_transporter
        com = rn[rn.locus_tag.isin(lo.index)]
        rep[t] = {"universe_before": int(len(ro)), "universe_after": int(len(rn)), "universe_added": int(len(add)),
                  "systems_before": int(len(so)), "systems_after": int(len(sn)),
                  "likely_transporter_changes_existing_genes": int((com.likely_transporter.values
                                                                    != lo.reindex(com.locus_tag).values).sum()),
                  "membership_changed_systems": sum(1 for r in mem_rows if r["strain"] == t),
                  "existing_loci_with_tier_change": sum(1 for r in tier_rows if r["strain"] == t),
                  "added_genes_by_tier": add.tier.value_counts(dropna=False).to_dict()}
    U = pd.concat(uni, ignore_index=True)
    U.to_csv(D / "p17_universe_additions.csv", index=False)
    pd.DataFrame(mem_rows).to_csv(D / "p17_membership_changes.csv", index=False)
    T = pd.DataFrame(tier_rows)
    T.to_csv(D / "p17_tier_changes.csv", index=False)
    pd.DataFrame(tc_rows).to_csv(D / "p17_tier_counts.csv", index=False)
    rep["tier_counts"] = tc_rows
    (D / "p17_report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 70)
    print(json.dumps({k: v for k, v in rep.items() if k != "tier_counts"}, indent=1, default=str))
    print(U[["strain", "locus_tag", "gene_name", "product", "cyanorak_q_roles", "gene_role", "likely_transporter",
             "system_members", "tier"]].to_string(index=False))
    if len(T):
        print(T[["strain", "locus_tag", "gene_name", "old_tier", "new_tier", "new_reason"]].to_string(index=False))
    print(pd.DataFrame(mem_rows)[["strain", "system_id", "members", "tier", "v15_systems", "added_genes"]].to_string(index=False))


if __name__ == "__main__":
    main()
