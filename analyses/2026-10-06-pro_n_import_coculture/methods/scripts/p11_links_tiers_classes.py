"""Step 7 (decide gate 2026-10-08): function-/neighbour-linked enzymes, curated transport class, tiers,
compound classes. File prefix p11_ (p7-p10 are diff/report helpers).

Inputs (<out-dir>): p6_<tag>_system_substrates_flagged.csv, p5_<tag>_metabolite_xref.csv,
  raw/p5_<tag>_genome_metabolism_for_substrates.csv (every strain gene with a metabolism-arm reaction on
  any member of a carried substrate group), p4_<tag>_neighbour_candidates.csv (window +-8, either strand),
  p3_<tag>_gene_systems_<REF>.csv, p6_<tag>_system_profiles.csv, p2_<tag>_gene_roles.csv.
KG call (kg_fetch, strict inputs, key (locus_tag, term_id)): gene_ontology_terms(universe + every
  enzyme gene, ['cyanorak_role', 'tigr_role'], leaf).
Rules (n_transport): function_links, neighbour_links (ubiquity threshold --ubiquity-threshold; groups with
  >= that many reacting genes are excluded), transport_class, system_tier, compound_class,
  can_use_applicable. Carried groups for linking = substrate rows with n_status != no_N, not lumping,
  not currency, any depth.
v1.4 (2026-10-08): RefSeq fragments (nt.refseq_fragments on raw/p3_<tag>_genome_coords.csv; aliases from
  gene_details(RS-tagged genes) all_identifiers) -> p11_<tag>_fragments.csv; fragment loci stay in the link
  tables (fragment_of) but are not counted in n_*_linked_enzymes; link rows carry the system tier and
  system_is_transporter_candidate (High/Medium); systems carry known_false_positive (+ reason).
Outputs: p11_<tag>_fragments.csv, p11_<tag>_function_linked.csv, p11_<tag>_neighbour_linked.csv, p11_<tag>_substrate_ubiquity.csv,
  p11_<tag>_compound_classes.csv, p11_<tag>_system_substrates_annotated.csv, p11_<tag>_systems.csv,
  p11_<tag>_gene_roles_cyanorak_tigr.csv, [--pilot] p11_<tag>_pilot.csv, p11_<tag>_summary.json.
Usage: ... p11_links_tiers_classes.py --organism "Prochlorococcus MED4" --out-dir <dir> [--ubiquity-threshold 30] [--pilot]
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, gene_details, gene_ontology_terms, to_dataframe

from common import PILOT_ANCHORS, REF, kf, nt, resolve_organism, role_map_hash, write_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ubiquity-threshold", type=int, default=30)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    d = Path(a.out_dir)
    tag = a.organism.split()[-1].lower()
    fl = pd.read_csv(d / f"p6_{tag}_system_substrates_flagged.csv", low_memory=False)
    xref = pd.read_csv(d / f"p5_{tag}_metabolite_xref.csv", dtype={"chebi_id": str})
    gm = pd.read_csv(d / "raw" / f"p5_{tag}_genome_metabolism_for_substrates.csv")
    nb = pd.read_csv(d / f"p4_{tag}_neighbour_candidates.csv")
    gs = pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv")
    prof = pd.read_csv(d / f"p6_{tag}_system_profiles.csv").set_index("system_id")
    roles2 = pd.read_csv(d / f"p2_{tag}_gene_roles.csv").set_index("locus_tag")
    log = []
    grp_of = dict(zip(xref.metabolite_id, xref.equiv_group))
    gm["equiv_group"] = gm.metabolite_id.map(lambda m: grp_of.get(m, m))
    gene_groups = gm.groupby("locus_tag").equiv_group.agg(set).to_dict()
    ubiq = gm.groupby("equiv_group").locus_tag.nunique().to_dict()

    loci = sorted(set(gs.locus_tag) | set(gm.locus_tag) | set(nb.loc[nb.neighbour_class == "enzyme_candidate", "candidate"]))
    with GraphConnection() as conn:
        org, _, _ = resolve_organism(a.organism, conn)
        rr = to_dataframe({"results": kf.fetch(
            gene_ontology_terms, "gene_ontology_terms(universe + enzymes, cyanorak_role/tigr_role, leaf)", log,
            ("locus_tag", "term_id"), chunk_param="locus_tags", chunk_size=300, limit_none_ok=True, strict_inputs=True,
            locus_tags=loci, organism=org, ontology=["cyanorak_role", "tigr_role", "ec"], conn=conn)["results"]})
        coords = pd.read_csv(d / "raw" / f"p3_{tag}_genome_coords.csv")
        rs_tags = sorted(t for t in coords.locus_tag if nt.is_refseq_only(t))
        gd = kf.fetch(gene_details, "gene_details(RefSeq-tagged genes, aliases)", log, ("locus_tag",),
                      chunk_param="locus_tags", chunk_size=200, limit_none_ok=True, locus_tags=rs_tags,
                      conn=conn)["results"]
    assert {g["locus_tag"] for g in gd} == set(rs_tags), "gene_details did not return every RefSeq-tagged gene"
    aliases = {g["locus_tag"]: list(g.get("all_identifiers") or []) for g in gd}
    frag = nt.refseq_fragments(coords, aliases)
    frag.to_csv(d / f"p11_{tag}_fragments.csv", index=False)
    frag_of = dict(zip(frag.locus_tag, frag.fragment_of))
    rr.to_csv(d / f"p11_{tag}_gene_roles_cyanorak_tigr.csv", index=False)
    gene_ecs = rr[rr.ontology_type == "ec"].groupby("locus_tag").term_id.agg(set).to_dict()
    cy = rr[rr.ontology_type == "cyanorak_role"]
    gene_roles = cy.groupby("locus_tag").term_id.agg(set).to_dict()
    role_names = dict(zip(cy.term_id, cy.term_name))

    # compound classes for every N-class group carried in the table
    Nrows = fl[fl.n_status != "no_N"]
    groups = sorted(set(Nrows.equiv_group))
    xg = xref[xref.equiv_group.isin(groups)].groupby("equiv_group")
    cc = []
    for g in groups:
        sub = xg.get_group(g) if g in xg.groups else pd.DataFrame({"metabolite_id": [g], "name": [g], "n_status": [""]})
        cls, rule, analogue = nt.compound_class(sub.name.tolist(), n_status=sub.n_status.tolist())
        cc.append({"equiv_group": g, "member_ids": "|".join(sorted(sub.metabolite_id)),
                   "names": "|".join(sorted(set(map(str, sub.name)))), "n_status": "|".join(sorted(set(map(str, sub.n_status)))),
                   "compound_class": cls, "rule_matched": rule, "analogue_flag": analogue,
                   "can_use_applicable": nt.can_use_applicable(cls)})
    cc = pd.DataFrame(cc)
    cc.to_csv(d / f"p11_{tag}_compound_classes.csv", index=False)

    # ubiquity table
    cur_g = set(fl.loc[fl.is_currency.map(nt.to_bool), "equiv_group"])
    names_g = xref.groupby("equiv_group").name.first()
    ub = pd.DataFrame({"equiv_group": list(ubiq), "n_genes_with_reaction": list(ubiq.values())})
    ub["name"] = ub.equiv_group.map(names_g)
    ub["is_currency"] = ub.equiv_group.isin(cur_g)
    ub["carried_N_class"] = ub.equiv_group.isin(groups)
    ub["excluded_as_ubiquitous"] = ub.n_genes_with_reaction >= a.ubiquity_threshold
    ub = ub.sort_values("n_genes_with_reaction", ascending=False)
    ub.to_csv(d / f"p11_{tag}_substrate_ubiquity.csv", index=False)

    # links
    elig = Nrows[~Nrows.is_lumping.map(nt.to_bool) & ~Nrows.is_currency.map(nt.to_bool)]
    carried = elig.groupby("system_id").equiv_group.agg(set).to_dict()
    members = gs.groupby("system_id").locus_tag.agg(set).to_dict()
    enz = nb[nb.neighbour_class == "enzyme_candidate"]
    window = enz.groupby("system_id").candidate.agg(set).to_dict()
    nbi = nb.set_index(["system_id", "candidate"])
    gname = gm.drop_duplicates("locus_tag").set_index("locus_tag")
    fl_rows, nl_rows = [], []
    for sid, mem in members.items():
        sys_roles = set().union(*(gene_roles.get(m, set()) for m in mem))
        cg = carried.get(sid, set())
        for r in nt.function_links(sys_roles, cg, gene_groups, gene_roles, mem, ubiquity=ubiq,
                                   threshold=a.ubiquity_threshold, gene_ecs=gene_ecs):
            pos = nbi.loc[(sid, r["locus_tag"])] if (sid, r["locus_tag"]) in nbi.index else None
            fl_rows.append({"system_id": sid, **r,
                            "shared_role_names": "|".join(role_names.get(x, x) for x in r["shared_role_ids"].split("|")),
                            "enzyme_name": gname.gene_name.get(r["locus_tag"]) if "gene_name" in gname else None,
                            "enzyme_product": gname["product"].get(r["locus_tag"]) if "product" in gname else None,
                            "in_window8": pos is not None, "rank_offset": None if pos is None else pos["rank_offset"]})
        for r in nt.neighbour_links(cg, window.get(sid, set()), gene_groups, ubiq, a.ubiquity_threshold):
            pos = nbi.loc[(sid, r["locus_tag"])]
            nl_rows.append({"system_id": sid, **r, "enzyme_name": pos["candidate_name"],
                            "rank_offset": pos["rank_offset"], "gap_to_nearest_member": pos["gap_to_nearest_member"],
                            "same_strand": pos["same_strand"], "in_system_run": pos["in_system_run"]})
    fcols = ["system_id", "equiv_group", "locus_tag", "link_breadth", "shared_role_ids", "shared_role_names",
             "enzyme_name", "enzyme_product", "in_window8", "rank_offset"]
    ncols = ["system_id", "equiv_group", "locus_tag", "enzyme_name", "rank_offset", "gap_to_nearest_member",
             "same_strand", "in_system_run"]
    fdf = pd.DataFrame(fl_rows, columns=fcols)
    ndf = pd.DataFrame(nl_rows, columns=ncols)
    for df_ in (fdf, ndf):
        df_["substrate_names"] = df_.equiv_group.map(names_g)
        df_["fragment_of"] = df_.locus_tag.map(frag_of).fillna(nt.NO_BASIS)
    n_fl, n_nl = nt.link_counts(fdf, set(frag_of)), nt.link_counts(ndf, set(frag_of))

    # annotate the substrate table (every row kept)
    ccm = cc.set_index("equiv_group")
    fl["compound_class"] = fl.equiv_group.map(ccm.compound_class).where(fl.n_status != "no_N", "no_N")
    fl["compound_rule"] = fl.equiv_group.map(ccm.rule_matched).where(fl.n_status != "no_N", "not_applicable")
    fl["analogue_flag"] = fl.equiv_group.map(ccm.analogue_flag).fillna(False).astype(bool)
    fl["can_use_applicable"] = fl.compound_class.map(lambda c: nt.can_use_applicable(c))
    eligible_row = (fl.n_status != "no_N") & ~fl.is_lumping.map(nt.to_bool) & ~fl.is_currency.map(nt.to_bool)
    fl["link_eligible_row"] = eligible_row
    fk = fdf.groupby(["system_id", "equiv_group"]).agg(function_linked_loci=("locus_tag", lambda s: "|".join(sorted(set(s)))),
                                                      function_linked_shared_roles=("shared_role_ids", lambda s: "|".join(sorted(set("|".join(s).split("|"))))))
    nk = ndf.groupby(["system_id", "equiv_group"]).locus_tag.agg(lambda s: "|".join(sorted(set(s)))).rename("neighbour_linked_loci")
    key = list(zip(fl.system_id, fl.equiv_group))
    fl["function_linked_loci"] = [fk.function_linked_loci.get(k, nt.NO_BASIS) for k in key]
    fl["function_linked_shared_roles"] = [fk.function_linked_shared_roles.get(k, nt.NO_BASIS) for k in key]
    fl["neighbour_linked_loci"] = [nk.get(k, nt.NO_BASIS) for k in key]
    for c in ("function_linked_loci", "function_linked_shared_roles", "neighbour_linked_loci"):
        fl[c] = fl[c].where(eligible_row, nt.NOT_ELIGIBLE)
    fl.to_csv(d / f"p11_{tag}_system_substrates_annotated.csv", index=False)

    # systems: transport class + tier
    srows = []
    for sid, mem in members.items():
        mem = sorted(mem)
        q_ids, q_names = nt.transport_class({m: gene_roles.get(m, set()) for m in mem}, role_names)
        lts = [roles2.loc[m, "likely_transporter"] for m in mem]
        res = [roles2.loc[m, "tcdb_ids"] for m in mem]
        p = prof.loc[sid]
        member_res = [r for r in str(p.transport_substrate_resolution).split("|") if r and r != "nan"]
        c123 = pd.to_numeric(roles2.loc[mem, "tcdb_c123_max_score"], errors="coerce")
        c123max = None if c123.isna().all() else float(c123.max())
        # curated override only where the Cyanorak Q role actually upgraded a catalogue-listed member
        # (likely_transporter strong with basis cyanorak + tcdb; v1.3)
        curated_q = any(roles2.loc[m, "likely_transporter"] == "strong"
                        and {"cyanorak", "tcdb"} <= set(str(roles2.loc[m, "likely_transporter_basis"]).split("|"))
                        for m in mem)
        tier, why = nt.system_tier(strong="strong" in lts, tcdb_only="tcdb_only" in lts,
                                   role_complete=nt.to_bool(p.role_complete), member_resolutions=member_res,
                                   c123_max_score=c123max, curated_q=curated_q)
        srows.append({"system_id": sid, "member_names": p.member_names, "n_genes": len(mem), "tier": tier,
                      "tier_reason": why, "likely_transporter_members": "|".join(sorted(set(lts))),
                      "role_complete": nt.to_bool(p.role_complete), "member_resolutions": "|".join(sorted(set(member_res))) or nt.NO_BASIS,
                      "c123_max_score": c123max, "max_tcdb_evidence_score": p.max_tcdb_evidence_score,
                      "evidence_class": p.evidence_class, "transport_class_ids": q_ids, "transport_class_names": q_names,
                      "n_function_linked_enzymes": n_fl.get(sid, 0),
                      "n_neighbour_linked_enzymes": n_nl.get(sid, 0)})
        _ = res
        kfp, kfp_why = nt.known_false_positive([roles2.loc[m, "product"] for m in mem],
                                               [roles2.loc[m, "gene_name"] for m in mem])
        srows[-1].update({"known_false_positive": kfp, "known_false_positive_reason": kfp_why,
                          "efflux_annotated": nt.efflux_annotated([roles2.loc[m, "product"] for m in mem],
                                                                  [roles2.loc[m, "gene_name"] for m in mem]),
                          "n_fragment_links_not_counted": int(fdf[(fdf.system_id == sid) & (fdf.fragment_of != nt.NO_BASIS)].locus_tag.nunique()
                                                              + ndf[(ndf.system_id == sid) & (ndf.fragment_of != nt.NO_BASIS)].locus_tag.nunique())})
    sy = pd.DataFrame(srows).sort_values(["tier", "system_id"])
    sy.to_csv(d / f"p11_{tag}_systems.csv", index=False)
    tier_of = sy.set_index("system_id").tier
    for df_ in (fdf, ndf):
        df_["system_tier"] = df_.system_id.map(tier_of)
        df_["system_is_transporter_candidate"] = df_.system_tier.map(nt.is_transporter_candidate)
    fdf.to_csv(d / f"p11_{tag}_function_linked.csv", index=False)
    ndf.to_csv(d / f"p11_{tag}_neighbour_linked.csv", index=False)

    other_n = cc[cc.compound_class.isin([nt.UNCLASSIFIED_N, nt.UNCLASSIFIED_NO_FORMULA])][
        ["equiv_group", "member_ids", "names", "n_status", "compound_class"]].copy()
    rc = fl[fl.n_status != "no_N"].groupby("equiv_group").agg(
        n_rows=("locus_tag", "size"), n_systems=("system_id", "nunique"),
        n_most_specific_rows=("substrate_depth", lambda s: int((s == "most_specific").sum())))
    other_n = other_n.join(rc, on="equiv_group").sort_values(["n_most_specific_rows", "n_rows"], ascending=False)
    other_n.to_csv(d / f"p11_{tag}_unclassified_groups.csv", index=False)  # superseded by p12 layered classes
    summ = {"organism": org, "role_map_hash": role_map_hash(d), "ubiquity_threshold": a.ubiquity_threshold,
            "ubiquity_top20": ub.head(20)[["equiv_group", "name", "n_genes_with_reaction", "is_currency",
                                           "excluded_as_ubiquitous"]].to_dict("records"),
            "excluded_non_currency": ub[ub.excluded_as_ubiquitous & ~ub.is_currency][["equiv_group", "name", "n_genes_with_reaction"]].to_dict("records"),
            "function_linked": {"pairs": int(len(fdf)), "systems": int(fdf.system_id.nunique()), "enzymes": int(fdf.locus_tag.nunique())},
            "neighbour_linked": {"pairs": int(len(ndf)), "systems": int(ndf.system_id.nunique()), "enzymes": int(ndf.locus_tag.nunique())},
            "tiers": sy.tier.value_counts().to_dict(),
            "fragments": frag.to_dict("records"),
            "function_link_rows_by_tier": fdf.system_tier.value_counts().to_dict(),
            "neighbour_link_rows_by_tier": ndf.system_tier.value_counts().to_dict(),
            "known_false_positive_systems": sy[sy.known_false_positive][["system_id", "member_names", "tier"]].to_dict("records"),
            "tiers_by_type": sy.assign(t=sy.n_genes.map(lambda n: "single_gene" if n == 1 else "multi_gene"))
                               .groupby(["t", "tier"]).size().unstack(fill_value=0).to_dict(),
            "compound_classes_groups": cc.compound_class.value_counts().to_dict(),
            "compound_classes_rows": fl[fl.n_status != "no_N"].compound_class.value_counts().to_dict(),
            "analogue_groups": cc[cc.analogue_flag][["equiv_group", "names", "compound_class"]].to_dict("records"),
            "name_layer_unclassified_groups_n": int(len(other_n)), "calls": log}
    if a.pilot:
        sid_of = gs.set_index("locus_tag").system_id
        pil = []
        for case, anchor in PILOT_ANCHORS.items():
            s = sid_of[anchor]
            r = sy.set_index("system_id").loc[s]
            pil.append({"case": case, "system_id": s, "tier": r.tier, "tier_reason": r.tier_reason,
                        "transport_class": r.transport_class_ids,
                        "function_linked": "; ".join(f"{x.locus_tag}({x.enzyme_name})->{x.substrate_names} via {x.shared_role_ids}"
                                                     for x in fdf[fdf.system_id == s].itertuples()),
                        "neighbour_linked": "; ".join(f"{x.locus_tag}({x.enzyme_name})->{x.substrate_names}"
                                                      for x in ndf[ndf.system_id == s].itertuples())})
        pd.DataFrame(pil).to_csv(d / f"p11_{tag}_pilot.csv", index=False)
        summ["pilot"] = pil
    write_summary(d / f"p11_{tag}_summary.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k != "calls"}, indent=1, default=str))


if __name__ == "__main__":
    main()
