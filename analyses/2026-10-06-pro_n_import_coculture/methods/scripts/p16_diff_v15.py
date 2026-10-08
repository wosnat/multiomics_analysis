"""Diff report v1.4.0 -> v1.5.0 (grouping Rule A3 adjacent_abc; known false positives gst + sodX). No KG calls.

Compares data/<tag>/ with data/v1.4.0_archive/<tag>/. Writes into <data-dir>:
  p16_membership_changes.csv  every v1.5 system whose member set differs from every v1.4 system (locus tags),
                              with the v1.4 systems it was built from and their tiers;
  p16_tier_changes.csv        every locus whose system tier changed;
  p16_tier_counts.csv         tier counts before / after per strain;
  p16_known_false_positive.csv  systems flagged in v1.5 (and whether they were flagged in v1.4);
  p16_report.json             counts.
Usage: ... p16_diff_v15.py --data-dir analyses/2026-10-06-pro_n_import_coculture/methods/data
"""
import argparse
import json
from pathlib import Path

import pandas as pd

TAGS = ["med4", "mit9313", "natl2a"]
REF = "gap200_roleT_crossT"


def load(base, t):
    g = pd.read_csv(base / t / f"p3_{t}_gene_systems_{REF}.csv")
    sy = pd.read_csv(base / t / f"p11_{t}_systems.csv").set_index("system_id")
    return g, sy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    D = Path(a.data_dir)
    A = D / "v1.4.0_archive"
    mem_rows, tier_rows, tc_rows, kfp_rows, rep = [], [], [], [], {}
    for t in TAGS:
        gn, sn = load(D, t)
        go, so = load(A, t)
        mn = gn.groupby("system_id").locus_tag.agg(frozenset).to_dict()
        mo = go.groupby("system_id").locus_tag.agg(frozenset).to_dict()
        old_sets = set(mo.values())
        sys_old = dict(zip(go.locus_tag, go.system_id))
        for sid, m in sorted(mn.items()):
            if m in old_sets:
                continue
            parts = sorted({sys_old.get(x, "absent") for x in m})
            jb = gn[gn.system_id == sid].joined_by.iloc[0]
            mem_rows.append({"strain": t, "system_id": sid, "member_names": sn.loc[sid, "member_names"],
                             "members": "|".join(sorted(m)), "n_genes": len(m), "joined_by": jb,
                             "tier": sn.loc[sid, "tier"], "tier_reason": sn.loc[sid, "tier_reason"],
                             "v14_systems": "|".join(parts),
                             "v14_members": " || ".join(so.member_names.get(p, p) for p in parts),
                             "v14_tiers": "|".join(str(so.tier.get(p)) for p in parts)})
        tn = dict(zip(gn.locus_tag, gn.system_id.map(sn.tier)))
        to = dict(zip(go.locus_tag, go.system_id.map(so.tier)))
        for lt in sorted(set(tn) | set(to)):
            if tn.get(lt) != to.get(lt):
                tier_rows.append({"strain": t, "locus_tag": lt, "old_tier": to.get(lt), "new_tier": tn.get(lt),
                                  "old_system": sys_old.get(lt), "new_system": dict(zip(gn.locus_tag, gn.system_id)).get(lt)})
        for k in ["High", "Medium", "Low", "not_transporter"]:
            tc_rows.append({"strain": t, "tier": k, "before": int((so.tier == k).sum()), "after": int((sn.tier == k).sum())})
        for sid, r in sn[sn.known_false_positive.astype(bool)].iterrows():
            kfp_rows.append({"strain": t, "system_id": sid, "member_names": r.member_names, "tier": r.tier,
                             "reason": r.known_false_positive_reason,
                             "flagged_in_v1.4.0": bool(so.known_false_positive.get(sid, False))})
        rep[t] = {"systems_before": len(so), "systems_after": len(sn),
                  "membership_changed_systems": sum(1 for r in mem_rows if r["strain"] == t),
                  "loci_with_tier_change": sum(1 for r in tier_rows if r["strain"] == t),
                  "known_false_positive_systems": sum(1 for r in kfp_rows if r["strain"] == t)}
    pd.DataFrame(mem_rows).to_csv(D / "p16_membership_changes.csv", index=False)
    pd.DataFrame(tier_rows, columns=["strain", "locus_tag", "old_tier", "new_tier", "old_system", "new_system"]) \
        .to_csv(D / "p16_tier_changes.csv", index=False)
    pd.DataFrame(tc_rows).to_csv(D / "p16_tier_counts.csv", index=False)
    pd.DataFrame(kfp_rows).to_csv(D / "p16_known_false_positive.csv", index=False)
    rep["tier_counts"] = tc_rows
    (D / "p16_report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print(json.dumps(rep, indent=1))
    print(pd.DataFrame(mem_rows)[["strain", "system_id", "members", "joined_by", "tier", "v14_tiers"]].to_string(index=False))
    print(pd.DataFrame(tier_rows).to_string(index=False))
    print(pd.DataFrame(kfp_rows)[["strain", "system_id", "member_names", "tier", "reason"]].to_string(index=False))


if __name__ == "__main__":
    main()
