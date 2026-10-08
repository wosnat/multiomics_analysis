"""Step 3: coordinates, runs and grouping into systems (grid of variants).

KG calls (kg_fetch: one call per chunk, returned == total, no duplicate natural key):
  gene_details(universe), tiled gene_neighbors sweep per contig (window 250; a contig-wide window
  exceeds the server memory limit), gene_details(sweep genes), and (I2) a read-only run_cypher for the
  organism's genes with null start. HARD ASSERT: sweep genes with coordinates + no-coordinate genes ==
  list_organisms gene_count, and the two sets are disjoint.
Variant files: the chosen variant (common.REF, gap200_roleT_crossT) in <out-dir>; the other six in <out-dir>/grid/.
Outputs (<out-dir>): p3_<tag>_systems_<variant>.csv, p3_<tag>_gene_systems_<variant>.csv, p3_<tag>_edges_<variant>.csv,
  p3_<tag>_cross_locus_edges_<variant>.csv, p3_<tag>_variant_summary.csv, p3_<tag>_genome_runs_gap<g>.csv,
  p3_<tag>_no_coordinate_genes.csv, p3_<tag>_no_coordinate_placeability.csv, [--pilot] p3_<tag>_pilot_systems.csv,
  p3_<tag>_summary.json (role-map hash; I7 metrics).
Usage: ... p3_group_systems.py --organism "Prochlorococcus MED4" --out-dir <dir> [--pilot] [--variants ...]
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, gene_details, gene_neighbors, run_cypher, to_dataframe

from common import PILOT_ANCHORS, REF, kf, nt, resolve_organism, role_map_hash, write_summary

WINDOW = 250
GAPS = (100, 200, 500)
DETAIL_COLS = ["locus_tag", "gene_name", "product", "contig", "start", "end", "strand"]
ABC = ("substrate_binding", "permease", "atpase")
CASES = {"cyn": ["PMM0370", "PMM0371", "PMM0372", "PMM0373"], "urt": [f"PMM{n:04d}" for n in range(970, 975)],
         "dpp": ["PMM1049", "PMM1048", "PMM0421", "PMM0192"], "amt1": ["PMM0263"],
         "pst": ["PMM0710", "PMM0723", "PMM0724", "PMM0725"], "salY": ["PMM0913"], "fadD": ["PMM0402"]}


def variant_dir(d, vn):
    """The chosen variant (REF) stays in <out-dir>; the grid variants go to <out-dir>/grid/ (v1.5)."""
    if vn == REF:
        return d
    (d / "grid").mkdir(exist_ok=True)
    return d / "grid"


def vname(gap, role, cross):
    return f"gap{gap}_role{'T' if role else 'F'}_cross{'T' if cross else 'F'}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--variants", nargs="*", default=None)
    a = ap.parse_args()
    d = Path(a.out_dir)
    log = []
    with GraphConnection() as conn:
        org, tag, orow = resolve_organism(a.organism, conn)
        roles = pd.read_csv(d / f"p2_{tag}_gene_roles.csv")
        uni = roles.locus_tag.tolist()
        ud = to_dataframe({"results": kf.fetch(gene_details, "gene_details(universe)", log, ("locus_tag",),
                                               chunk_param="locus_tags", chunk_size=200, limit_none_ok=True,
                                               locus_tags=uni, conn=conn)["results"]})
        nocoord_univ = ud[ud.get("start").isna()].locus_tag.tolist() if "start" in ud else uni
        contigs = ud.dropna(subset=["contig"]).groupby("contig")["locus_tag"].min()
        genome_tags = set()
        for contig, anchor in contigs.items():
            seen, frontier = {anchor}, [anchor]
            while frontier:
                anc = frontier.pop()
                nb = kf.fetch(gene_neighbors, f"gene_neighbors({anc}, window {WINDOW})", log,
                              ("anchor_locus_tag", "neighbor_locus_tag"),  # limit 10**6 (signature int)
                              locus_tags=[anc], window=WINDOW, conn=conn)["results"]
                new = {r["neighbor_locus_tag"] for r in nb} - seen
                seen |= new
                for side in (min, max):
                    if nb:
                        far = side(nb, key=lambda r: r["rank_offset"])
                        if far["neighbor_locus_tag"] in new and abs(far["rank_offset"]) == WINDOW:
                            frontier.append(far["neighbor_locus_tag"])
            genome_tags |= seen
        gd = to_dataframe({"results": kf.fetch(gene_details, "gene_details(sweep genes)", log, ("locus_tag",),
                                               chunk_param="locus_tags", chunk_size=200, limit_none_ok=True,
                                               locus_tags=sorted(genome_tags), conn=conn)["results"]})
        q = (f"MATCH (g:Gene) WHERE g.organism_name = '{org}' AND g.start IS NULL "
             "RETURN g.locus_tag AS locus_tag, g.product AS product, g.gene_category AS gene_category")
        nc = to_dataframe({"results": kf.fetch(run_cypher, "run_cypher(genes with null start)", log, ("locus_tag",),
                                               limit_none_ok=True, query=q, conn=conn)["results"]})
    gene_count = int(orow["gene_count"])
    with_coords = gd.dropna(subset=["start", "end", "strand"])
    assert set(with_coords.locus_tag).isdisjoint(set(nc.locus_tag)), "gene both with and without coordinates"
    assert len(with_coords) + len(nc) == gene_count, \
        f"sweep {len(with_coords)} + no-coordinate {len(nc)} != list_organisms gene_count {gene_count}"
    assert not nocoord_univ or set(nocoord_univ) <= set(nc.locus_tag)
    nc.assign(status="no_coordinates").to_csv(d / f"p3_{tag}_no_coordinate_genes.csv", index=False)
    gd[DETAIL_COLS].to_csv(d / "raw" / f"p3_{tag}_genome_coords.csv", index=False)
    genome = with_coords[DETAIL_COLS]

    variants = [(g, r, True) for g in GAPS for r in (True, False)] + [(200, True, False)]
    if a.variants:
        variants = [v for v in variants if vname(*v) in a.variants]
    summ_rows, pilot_rows, run_cache, i7 = [], [], {}, {}
    for gap, role_join, cross in variants:
        vn = vname(gap, role_join, cross)
        if gap not in run_cache:
            rr = nt.runs(genome, max_gap_bp=gap, same_strand=True)
            rr.to_csv(d / f"p3_{tag}_genome_runs_gap{gap}.csv", index=False)
            run_cache[gap] = rr.set_index("locus_tag")
        rr = run_cache[gap]
        t = roles[["locus_tag", "gene_name", "product", "gene_role", "likely_transporter", "tcdb_ids"]].copy()
        t["tcdb_ids"] = t["tcdb_ids"].fillna("")
        t["role"] = t["gene_role"]
        t = nt.attach_runs(t, rr)  # universe genes without coordinates kept as own pseudo-run
        assert set(t.loc[~t.has_coordinates, "locus_tag"]) <= set(nc.locus_tag)
        g, e = nt.group_systems(t, cross_locus=cross, join_within_run_by_role=role_join, return_edges=True,
                                join_adjacent_abc=role_join)  # A3 (v1.5) follows the role-join switch
        vd = variant_dir(d, vn)
        g.to_csv(vd / f"p3_{tag}_gene_systems_{vn}.csv", index=False)
        e.to_csv(vd / f"p3_{tag}_edges_{vn}.csv", index=False)
        e[e.label == "cross_locus"].to_csv(vd / f"p3_{tag}_cross_locus_edges_{vn}.csv", index=False)

        def agg(x):
            rs = set(x["role"])
            return pd.Series({
                "n_genes": len(x), "member_loci": " | ".join(sorted(x["locus_tag"])),
                "member_names": " | ".join(f"{lt}:{n}" for lt, n in sorted(zip(x.locus_tag, x.gene_name.fillna("")))),
                "roles": "|".join(sorted(rs)), "role_complete": nt._role_complete(rs),
                "joined_by": x["joined_by"].iloc[0], "cross_locus_merged": bool(x["cross_locus_merged"].iloc[0]),
                "n_runs": int(x["n_runs"].iloc[0]), "member_runs": x["member_runs"].iloc[0],
                "tcdb_ids": " | ".join(sorted({i for s in x["tcdb_ids"] for i in nt.parse_list(s)})),
                "likely_transporter": "|".join(sorted(set(x["likely_transporter"]))),
                "max_same_abc_role": max([int((x.role == r).sum()) for r in ABC]),
            })
        sy = g.groupby("system_id").apply(agg, include_groups=False).reset_index()
        sy.to_csv(vd / f"p3_{tag}_systems_{vn}.csv", index=False)
        sizes = sy.n_genes.clip(upper=6).value_counts().sort_index()
        summ_rows.append({"variant": vn, "files_dir": "." if vn == REF else "grid", "max_gap_bp": gap, "join_within_run_by_role": role_join, "cross_locus": cross,
                          "n_systems": len(sy), "n_role_complete": int(sy.role_complete.sum()),
                          "n_cross_locus_merged_systems": int(sy.cross_locus_merged.sum()),
                          "n_cross_locus_edges": int((e.label == "cross_locus").sum()),
                          "n_role_join_edges": int((e.label == "role").sum()),
                          "n_adjacent_abc_edges": int((e.label == "adjacent_abc").sum()),
                          "size_distribution": "; ".join(f"{'6+' if k == 6 else k}:{v}" for k, v in sizes.items()),
                          "max_system_size": int(sy.n_genes.max())})
        clm = sy[sy.cross_locus_merged]
        i7[vn] = {"max_system_size": int(sy.n_genes.max()),
                  "largest_systems": sy.nlargest(3, "n_genes")[["system_id", "n_genes", "member_names"]].to_dict("records"),
                  "cross_locus_merged_systems": int(len(clm)),
                  "cross_locus_merged_with_gt1_gene_same_abc_role": int((clm.max_same_abc_role > 1).sum()),
                  "those_systems": clm[clm.max_same_abc_role > 1][["system_id", "member_names", "roles"]].to_dict("records")}
        if a.pilot:
            gi, sym = g.set_index("locus_tag"), sy.set_index("system_id")
            for case, loci in CASES.items():
                for lt in loci:
                    inu = lt in gi.index
                    sid = gi.loc[lt, "system_id"] if inu else None
                    pilot_rows.append({"variant": vn, "case": case, "locus_tag": lt, "in_universe": inu,
                                       "system_id": sid,
                                       "system_members": sym.loc[sid, "member_names"] if inu else None,
                                       "joined_by": sym.loc[sid, "joined_by"] if inu else None})
    pd.DataFrame(summ_rows).to_csv(d / f"p3_{tag}_variant_summary.csv", index=False)
    if a.pilot:
        pd.DataFrame(pilot_rows).to_csv(d / f"p3_{tag}_pilot_systems.csv", index=False)
    # I3: placeability of no-coordinate genes against the reference systems' members
    refg = pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv")
    pl = nt.no_coordinate_placeability(refg[["locus_tag", "system_id"]], nc.locus_tag.tolist(), window=8)
    pl.to_csv(d / f"p3_{tag}_no_coordinate_placeability.csv", index=False)
    write_summary(d / f"p3_{tag}_summary.json", {
        "organism": org, "role_map_hash": role_map_hash(d), "list_organisms_gene_count": gene_count,
        "genes_with_coordinates": int(len(with_coords)), "genes_without_coordinates": int(len(nc)),
        "universe_genes_without_coordinates": sorted(set(uni) & set(nc.locus_tag)),
        "no_coordinate_placeability_window8": pl.placement_status.value_counts().to_dict(),
        "variants": summ_rows, "I7": i7, "calls": log})
    print(json.dumps({"gene_count": gene_count, "with_coords": len(with_coords), "no_coords": len(nc),
                      "placeability": pl.placement_status.value_counts().to_dict(), "variants": summ_rows,
                      "I7_ref": i7.get(REF)}, default=str, indent=1))


if __name__ == "__main__":
    main()
