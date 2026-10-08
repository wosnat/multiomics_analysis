"""Per-strain report after a pipeline run (scaling check). Facts only.

Reads <out-dir> outputs (p1..p6 summaries/tables, run_log.json) and MED4's role map (--ref-dir) for
role conflicts (M8). One KG call (kg_fetch): genes_by_metabolite(nitrate group ids + nitrite ids,
organism, metabolism arm) = every gene with a metabolism-arm reaction on nitrate / nitrite.
Writes <out-dir>/p8_<tag>_report.json, p8_<tag>_spotcheck.csv, p8_<tag>_nitrate_nitrite_metabolism_genes.csv,
p8_<tag>_role_conflicts_vs_med4.csv.
Usage: ... p8_strain_report.py --organism "Prochlorococcus MIT9313" --out-dir data/mit9313 --ref-dir data/med4
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, genes_by_metabolite, to_dataframe

from common import REF, kf, nt, resolve_organism

SPOT = {"ammonia": "ammonium", "ammonium": "ammonium", "urea": "urea", "cyanate": "cyanate",
        "nitrate": "nitrate", "nitrite": "nitrite"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ref-dir", required=True)
    a = ap.parse_args()
    d, ref = Path(a.out_dir), Path(a.ref_dir)
    tag = a.organism.split()[-1].lower()
    J = lambda f: json.loads((d / f).read_text(encoding="utf-8"))  # noqa: E731
    rep = {"organism": a.organism}
    rep["run_log"] = [{"script": x["script"], "args": [y for y in x["args"] if y.startswith("--") and y not in
                                                       ("--organism", "--out-dir")], "exit": x["exit"]}
                      for x in J("run_log.json")]
    p3 = J(f"p3_{tag}_summary.json")
    pl = pd.read_csv(d / f"p3_{tag}_no_coordinate_placeability.csv")
    rep["completeness"] = {"list_organisms_gene_count": p3["list_organisms_gene_count"],
                           "with_coordinates": p3["genes_with_coordinates"],
                           "without_coordinates": p3["genes_without_coordinates"],
                           "sum_equals_gene_count": p3["genes_with_coordinates"] + p3["genes_without_coordinates"]
                           == p3["list_organisms_gene_count"],
                           "universe_genes_without_coordinates": p3.get("universe_genes_without_coordinates")}
    rep["placeability"] = {s: {"n": int((pl.placement_status == s).sum()),
                               "examples": pl[pl.placement_status == s].locus_tag.head(6).tolist()}
                           for s in ["placed", "prefix_shared_not_within_window", "unplaceable"]}
    rep["tag_prefixes_no_coord"] = pl.tag_prefix.value_counts(dropna=False).to_dict()
    p1, p2c, p2b = J(f"p1_{tag}_summary.json"), J(f"p2c_{tag}_summary.json"), J(f"p2b_{tag}_summary.json")
    chk = J(f"p2c_{tag}_summary_check.json")
    rmap, rmed = pd.read_csv(d / "p2_pfam_role_map.csv"), pd.read_csv(ref / "p2_pfam_role_map.csv")
    conf = rmap[["pfam_id", "pfam_name", "role", "rule_matched"]].merge(
        rmed[["pfam_id", "role", "rule_matched"]], on="pfam_id", suffixes=("", "_med4"))
    conf = conf[conf.role != conf.role_med4]
    conf.to_csv(d / f"p8_{tag}_role_conflicts_vs_med4.csv", index=False)
    rep["counts"] = {"universe_p1": p1["universe_size"], "p2c_additions": p2c["additions"],
                     "universe_final": p2c.get("universe_size_out"), "second_pass_additions": chk["additions"],
                     "role_map_size": int(len(rmap)), "role_map_non_other": int((rmap.role != "other").sum()),
                     "role_map_hash": p2b["role_map_hash"], "domains_shared_with_med4": int(rmap.pfam_id.isin(rmed.pfam_id).sum()),
                     "role_conflicts_vs_med4": conf.to_dict("records"),
                     "seed_conflicts": p2b["seed_conflicts"]}
    vs = pd.read_csv(d / f"p3_{tag}_variant_summary.csv")
    rep["systems_grid"] = vs.to_dict("records")
    rep["I7_reference"] = p3["I7"][REF]

    fl = pd.read_csv(d / f"p6_{tag}_system_substrates_flagged.csv", low_memory=False)
    xr = pd.read_csv(d / f"p5_{tag}_metabolite_xref.csv", dtype={"chebi_id": str})
    gs = pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv")
    sy = pd.read_csv(d / f"p3_{tag}_systems_{REF}.csv").set_index("system_id")
    lems = pd.read_csv(d / f"p6_{tag}_linked_enzymes_ms.csv")
    spot_groups = xr[xr.name_norm.isin(SPOT)].assign(compound=lambda x: x.name_norm.map(SPOT))
    gmap = spot_groups.groupby("equiv_group").compound.first().to_dict()
    s = fl[(fl.substrate_depth == "most_specific") & (fl.n_status == "contains_N") & fl.equiv_group.isin(gmap)].copy()
    s["compound"] = s.equiv_group.map(gmap)
    rows = []
    for (sid, comp), g in s.groupby(["system_id", "compound"]):
        ms_l = lems[(lems.system_id == sid) & lems.equiv_group.isin(g.equiv_group)]
        rows.append({"compound": comp, "system_id": sid, "member_names": sy.loc[sid, "member_names"],
                     "substrate_ids": " | ".join(sorted(set(g.metabolite_id))),
                     "rows_on_loci": " | ".join(sorted(set(g.locus_tag))),
                     "tcdb_families": " | ".join(sorted(set(g.tcdb_family_id))),
                     "is_lumping_any": bool(g.is_lumping.map(nt.to_bool).any()),
                     "resolution": " | ".join(sorted(set(g.transport_substrate_resolution.astype(str)))),
                     "can_use_window": " | ".join(sorted(set(g.can_use_window))),
                     "can_use_run": " | ".join(sorted(set(g.can_use_run))),
                     "can_use_window_ms": " | ".join(sorted(set(g.can_use_window_ms))),
                     "can_use_run_ms": " | ".join(sorted(set(g.can_use_run_ms))),
                     "linked_window": " | ".join(sorted({x for v in g.linked_enzyme_loci_window.fillna("") for x in v.split("|") if x})),
                     "linked_run": " | ".join(sorted({x for v in g.linked_enzyme_loci_run.fillna("") for x in v.split("|") if x})),
                     "linked_ms": " | ".join(sorted(set(ms_l.candidate))),
                     "genome_enzyme_loci_n": len({x for v in g.genome_enzyme_loci.fillna("") for x in v.split("|") if x}),
                     "match_basis": " | ".join(sorted(set(g.match_basis.fillna(""))))})
    spot = pd.DataFrame(rows).sort_values(["compound", "system_id"]) if rows else pd.DataFrame()
    spot.to_csv(d / f"p8_{tag}_spotcheck.csv", index=False)
    rep["spotcheck"] = spot.to_dict("records")
    rep["spot_group_ids"] = spot_groups[["compound", "metabolite_id", "name", "equiv_group", "link_basis"]].to_dict("records")

    nn_ids = sorted(set(xr.loc[xr.equiv_group.isin(set(spot_groups[spot_groups.compound.isin(["nitrate", "nitrite"])]
                                                           .equiv_group)), "metabolite_id"]))
    log = []
    with GraphConnection() as conn:
        org, _, _ = resolve_organism(a.organism, conn)
        nm = to_dataframe({"results": kf.fetch(genes_by_metabolite, "genes_by_metabolite(nitrate/nitrite ids, metabolism)",
                                               log, ("locus_tag", "metabolite_id", "reaction_id"), metabolite_ids=nn_ids,
                                               organism=org, evidence_sources=["metabolism"], conn=conn)["results"]})
    keep = [c for c in ["locus_tag", "gene_name", "product", "metabolite_id", "metabolite_name", "reaction_id",
                        "reaction_name", "ec_numbers"] if c in nm.columns]
    nm = nm[keep] if len(nm) else pd.DataFrame(columns=keep)
    nm["system_id_if_member"] = nm.locus_tag.map(gs.set_index("locus_tag").system_id) if len(nm) else None
    nm.to_csv(d / f"p8_{tag}_nitrate_nitrite_metabolism_genes.csv", index=False)
    rep["nitrate_nitrite_metabolism"] = {"ids_queried": nn_ids, "n_rows": int(len(nm)),
                                         "genes": nm.drop_duplicates("locus_tag")[[c for c in ["locus_tag", "gene_name", "product"]
                                                                                   if c in nm]].to_dict("records"),
                                         "call": log}
    rep["expectation_check_nitrate_nitrite"] = J(f"p6_{tag}_summary.json")["expectation_check_nitrate_nitrite"]
    odd = {"warnings": {}, "identical_duplicates_collapsed": {}}
    for f in sorted(d.glob("p*_summary*.json")):
        for c in J(f.name).get("calls", []):
            if c.get("warnings"):
                odd["warnings"].setdefault(f.name, []).append({"call": c["call"], "warnings": [w[:160] for w in c["warnings"]]})
            if c.get("identical_duplicates_collapsed"):
                odd["identical_duplicates_collapsed"][f"{f.name}:{c['call']}"] = c["identical_duplicates_collapsed"]
    rep["odd"] = odd
    (d / f"p8_{tag}_report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rep, indent=1, default=str))


if __name__ == "__main__":
    main()
