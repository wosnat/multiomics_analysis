"""Report for n_transport v1.6.1 (delta-critic fixes). No KG calls. Compares with data/v1.6.0_archive.

Writes into <data-dir>:
  p19_dedicated_call_changes.csv   every (system, class) pair whose listing_basis changed vs v1.6.0 (or appeared/vanished)
  p19_lifted_loci_split.csv        the v1.6 Low->Medium loci (p17_tier_changes.csv) split into efflux_annotated /
                                   DMT/EamA (product matches EamA|DMT|drug/metabolite) / other
  p19_known_false_positive.csv     systems flagged known_false_positive (all strains)
  p19_mapeg_products.csv           every gene (genome-wide coords) whose product mentions MAPEG / eicosanoid, with
                                   universe membership and flag
  p19_double_dedicated.csv         systems dedicated for more than one class (p18 dedicated_also_for)
  p19_report.json
Usage: ... p19_report_v161.py --data-dir analyses/2026-10-06-pro_n_import_coculture/methods/data
"""
import argparse
import json
import re
from pathlib import Path

import pandas as pd

TAGS = ["med4", "mit9313", "natl2a"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    a = ap.parse_args()
    D = Path(a.data_dir)
    A = D / "v1.6.0_archive"
    ch, split, kfp, mapeg, dbl, rep = [], [], [], [], [], {}
    T = pd.read_csv(D / "p17_tier_changes.csv")
    for t in TAGS:
        n = pd.read_csv(D / t / f"p18_{t}_listing_basis.csv")
        o = pd.read_csv(A / t / f"p18_{t}_listing_basis.csv")
        m = n.merge(o[["system_id", "compound_class", "listing_basis", "basis_detail"]], on=["system_id", "compound_class"],
                    how="outer", suffixes=("", "_v160"), indicator=True)
        c = m[(m._merge != "both") | (m.listing_basis != m.listing_basis_v160)]
        ch.append(c.assign(strain=t)[["strain", "system_id", "member_names", "compound_class", "listing_basis_v160",
                                      "listing_basis", "basis_detail_v160", "basis_detail", "_merge"]])
        sy = pd.read_csv(D / t / f"p11_{t}_systems.csv").set_index("system_id")
        roles = pd.read_csv(D / t / f"p2_{t}_gene_roles.csv").set_index("locus_tag")
        for r in T[T.strain == t].itertuples():
            prod = str(roles["product"].get(r.locus_tag))
            if bool(sy.efflux_annotated[r.system_id]):
                cat = "efflux_annotated"
            elif re.search(r"eama|\bdmt\b|drug/metabolite", prod.lower()):
                cat = "DMT/EamA"
            else:
                cat = "other"
            split.append({"strain": t, "locus_tag": r.locus_tag, "gene_name": r.gene_name, "product": prod,
                          "system_id": r.system_id, "tier": sy.tier[r.system_id], "category": cat})
        k = sy[sy.known_false_positive.astype(bool)].reset_index()
        kfp.append(k.assign(strain=t)[["strain", "system_id", "member_names", "tier", "known_false_positive_reason"]])
        co = pd.read_csv(D / t / "raw" / f"p3_{t}_genome_coords.csv")
        mp = co[co["product"].astype(str).str.contains(r"mapeg|eicosanoid", case=False, regex=True)]
        for r in mp.itertuples():
            inu = r.locus_tag in roles.index
            sid = None
            if inu:
                gs = pd.read_csv(D / t / f"p3_{t}_gene_systems_gap200_roleT_crossT.csv").set_index("locus_tag")
                sid = gs.system_id.get(r.locus_tag)
            mapeg.append({"strain": t, "locus_tag": r.locus_tag, "product": r.product, "in_universe": inu,
                          "system_id": sid, "known_false_positive": bool(sy.known_false_positive[sid]) if sid else None})
        d = n[(n.listing_basis == "dedicated") & (n.dedicated_also_for != "none")]
        dbl.append(d.assign(strain=t)[["strain", "system_id", "member_names", "compound_class", "dedicated_basis",
                                       "dedicated_also_for", "basis_detail"]])
        rep[t] = {"efflux_annotated_systems": int(sy.efflux_annotated.astype(bool).sum()),
                  "dedicated_pairs": int((n.listing_basis == "dedicated").sum()),
                  "dedicated_basis": n.dedicated_basis.value_counts().to_dict()}
    C = pd.concat(ch, ignore_index=True)
    C.to_csv(D / "p19_dedicated_call_changes.csv", index=False)
    S = pd.DataFrame(split)
    S.to_csv(D / "p19_lifted_loci_split.csv", index=False)
    pd.concat(kfp, ignore_index=True).to_csv(D / "p19_known_false_positive.csv", index=False)
    pd.DataFrame(mapeg).to_csv(D / "p19_mapeg_products.csv", index=False)
    pd.concat(dbl, ignore_index=True).to_csv(D / "p19_double_dedicated.csv", index=False)
    rep["dedicated_call_changes"] = C[["strain", "system_id", "compound_class", "listing_basis_v160", "listing_basis"]].to_dict("records")
    rep["lifted_loci_split"] = S.category.value_counts().to_dict()
    rep["mapeg"] = mapeg
    (D / "p19_report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rep, indent=1, default=str))


if __name__ == "__main__":
    main()
