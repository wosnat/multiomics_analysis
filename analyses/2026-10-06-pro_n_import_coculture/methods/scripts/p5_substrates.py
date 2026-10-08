"""Step 5: substrates per system x subunit gene (all elements, n_status), flags, can_use two ways.

KG calls via kg_fetch (single call per chunk, totals, no duplicate natural key, expected warnings only):
  metabolites_by_gene(universe, transport arm, NO element filter (I1), verbose, both depths),
    key (locus_tag, metabolite_id, tcdb_family_id);
  list_metabolites(elements=['N'], verbose) + list_metabolites(every id seen in either arm, verbose):
    the metabolite xref; n_status per id; equivalence groups (id, then name_soft) over contains_N and
    no_formula ids (no_N ids are their own group);
  ontology_term_details(the table's TCDB families): level_kind + metabolite_count -> lumping families
    (tc_family with >= --lumping-threshold substrates; C2), flagged per row (is_lumping);
  genes_by_metabolite(every id of every substrate group, metabolism arm), key
    (locus_tag, metabolite_id, reaction_id).
Outputs (<out-dir>): p5_<tag>_system_substrates_full.csv (every row, all statuses), p5_<tag>_system_substrates_summary.csv,
  p5_<tag>_metabolite_xref.csv, p5_<tag>_xref_name_soft_groups.csv, p5_<tag>_lumping_families.csv,
  p5_<tag>_linked_enzymes.csv, p5_<tag>_neighbour_candidates_step5.csv, p5_<tag>_expected_negative_1.csv,
  [--pilot] p5_<tag>_pilot_substrate_diff.csv, p5_<tag>_pilot_rows_not_in_key.csv, p5_<tag>_summary.json.
Usage: ... p5_substrates.py --organism "Prochlorococcus MED4" --out-dir <dir> [--lumping-threshold 100] [--pilot]
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import (GraphConnection, genes_by_metabolite, list_metabolites, metabolites_by_gene,
                                 ontology_term_details, to_dataframe)

from common import ANSWER_KEY, REF, kf, nt, resolve_organism, role_map_hash, write_summary

FI_WARNING = [r"transport_substrate_resolution is `family_inferred`"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--lumping-threshold", type=int, default=100)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    d = Path(a.out_dir)
    log = []
    with GraphConnection() as conn:
        org, tag, _ = resolve_organism(a.organism, conn)
        gs = pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv")
        roles = pd.read_csv(d / f"p2_{tag}_gene_roles.csv").set_index("locus_tag")
        doms = pd.read_csv(d / f"p2_{tag}_pfam_domains.csv").set_index("pfam_id")["pfam_name"]
        rmap = nt.role_map_dict(pd.read_csv(d / "p2_pfam_role_map.csv"))
        tcv = pd.read_csv(d / "raw" / f"p2_{tag}_tcdb_terms_verbose.csv")
        nb = pd.read_csv(d / f"p4_{tag}_neighbour_candidates.csv")
        enz_m = pd.read_csv(d / f"p4_{tag}_enzyme_candidate_metabolites.csv")
        tr = to_dataframe({"results": kf.fetch(
            metabolites_by_gene, "metabolites_by_gene(universe, transport, all elements, verbose)", log,
            ("locus_tag", "metabolite_id", "tcdb_family_id"), chunk_param="locus_tags", chunk_size=40,
            expected_warnings=FI_WARNING, locus_tags=roles.index.tolist(), organism=org,
            evidence_sources=["transport"], verbose=True, conn=conn)["results"]})
        nlist = to_dataframe({"results": kf.fetch(list_metabolites, "list_metabolites(elements=N, verbose)", log,
                                                  ("metabolite_id",), limit_none_ok=True, elements=["N"],
                                                  verbose=True, conn=conn)["results"]})
        seen_ids = sorted((set(tr.metabolite_id) | set(enz_m.metabolite_id)) - set(nlist.metabolite_id))
        other = to_dataframe({"results": kf.fetch(list_metabolites, "list_metabolites(other seen ids, verbose)", log,
                                                  ("metabolite_id",), chunk_param="metabolite_ids", chunk_size=400,
                                                  limit_none_ok=True, strict_inputs=True, metabolite_ids=seen_ids, verbose=True,
                                                  conn=conn)["results"]}) if seen_ids else pd.DataFrame()
        fams = sorted(set(tr.tcdb_family_id.dropna()))
        td = to_dataframe({"results": kf.fetch(ontology_term_details, "ontology_term_details(table families)", log,
                                               ("term_id",), chunk_param="term_ids", chunk_size=200,
                                               limit_none_ok=True, term_ids=fams, conn=conn)["results"]})
        lm = pd.concat([nlist, other], ignore_index=True)
        assert lm.metabolite_id.is_unique
        assert set(tr.metabolite_id) | set(enz_m.metabolite_id) <= set(lm.metabolite_id)
        lm["n_status"] = [nt.n_status(e, f) for e, f in zip(lm.get("elements"), lm.get("formula"))]
        lm["chebi_id"] = lm.chebi_id.map(lambda v: None if pd.isna(v) else str(v).split(".")[0])
        eq = nt.equiv_groups(lm[lm.n_status != "no_N"])
        non = lm[lm.n_status == "no_N"].assign(equiv_group=lambda x: x.metabolite_id, link_basis=nt.NO_BASIS,
                                               equiv_group_size=1)
        non["name_norm"] = non.name.map(nt._norm_name)
        xref = pd.concat([eq, non], ignore_index=True)
        xref["kegg_compound_id"] = xref.metabolite_id.map(
            lambda m: m.split(":", 1)[1] if str(m).startswith("kegg.compound:") else None)
        xi = xref.set_index("metabolite_id")
        grp_ids = sorted(set(xref.loc[xref.equiv_group.isin(set(xi.loc[list(set(tr.metabolite_id)), "equiv_group"])),
                                      "metabolite_id"]))
        gm = to_dataframe({"results": kf.fetch(
            genes_by_metabolite, "genes_by_metabolite(substrate group ids, metabolism)", log,
            ("locus_tag", "metabolite_id", "reaction_id"), chunk_param="metabolite_ids", chunk_size=200,
            strict_inputs=True, metabolite_ids=grp_ids, organism=org, evidence_sources=["metabolism"],
            conn=conn)["results"]})
        # Per-strain expectation (replaces MED4's fixed EN1): expected_usable for the nitrate and nitrite
        # groups from the strain's own genome, by a separate metabolism-arm query per compound.
        expect = {}
        for comp in ("nitrate", "nitrite"):
            gids = set(xref.loc[xref.name_norm == comp, "equiv_group"])
            ids = sorted(set(xref.loc[xref.equiv_group.isin(gids), "metabolite_id"]))
            gg = kf.fetch(genes_by_metabolite, f"genes_by_metabolite({comp} group ids, metabolism)", log,
                          ("locus_tag", "metabolite_id", "reaction_id"), strict_inputs=True, metabolite_ids=ids,
                          organism=org, evidence_sources=["metabolism"], conn=conn)["results"]
            expect[comp] = {"groups": sorted(gids), "ids": ids, "expected_usable": bool(gg),
                            "genome_genes": sorted({r["locus_tag"] for r in gg})}
    tr.to_csv(d / "raw" / f"p5_{tag}_transport_raw.csv", index=False)
    gm.to_csv(d / "raw" / f"p5_{tag}_genome_metabolism_for_substrates.csv", index=False)
    xcols = ["metabolite_id", "name", "kegg_compound_id", "chebi_id", "mnxm_id", "inchikey", "name_norm", "formula",
             "elements", "n_status", "evidence_sources", "equiv_group", "link_basis", "equiv_group_size"]
    xref[[c for c in xcols if c in xref]].to_csv(d / f"p5_{tag}_metabolite_xref.csv", index=False)
    soft = xref[xref.link_basis.fillna("").str.contains("name_soft")].sort_values(["equiv_group", "metabolite_id"])
    soft[[c for c in xcols if c in soft]].to_csv(d / f"p5_{tag}_xref_name_soft_groups.csv", index=False)

    lump = nt.lumping_families(td, a.lumping_threshold, required_ids=fams)  # raises on missing/NaN count
    td.assign(is_lumping=td.term_id.isin(lump))[["term_id", "level", "level_kind", "metabolite_count",
                                                "direct_gene_count", "is_lumping"]] \
        .sort_values("metabolite_count", ascending=False).to_csv(d / f"p5_{tag}_lumping_families.csv", index=False)
    gbg = nt.genes_by_group(gm, xref)
    tv = tcv.rename(columns={"term_id": "tcdb_family_id"})[["locus_tag", "tcdb_family_id", "evidence", "evidence_score",
                                                           "source_agreement", "pfam_support", "attachment_depth"]]
    t = tr.merge(tv, on=["locus_tag", "tcdb_family_id"], how="left", indicator=True)
    unjoined = int((t._merge == "left_only").sum())
    t = t.drop(columns="_merge")
    t["system_id"] = t.locus_tag.map(gs.set_index("locus_tag").system_id)
    t["subunit_role"] = t.locus_tag.map(roles.gene_role)
    t["likely_transporter"] = t.locus_tag.map(roles.likely_transporter)

    def hint(lt):
        ids = nt.parse_list(roles.loc[lt, "pfam_ids"]) if isinstance(roles.loc[lt, "pfam_ids"], str) else []
        return " | ".join(doms.get(p, p) for p in ids if rmap.get(nt._pfam_acc(p), "other") != "other")
    t["domain_substrate_hint"] = t.locus_tag.map(hint)
    t["n_status"] = t.metabolite_id.map(xi.n_status)
    t["equiv_group"] = t.metabolite_id.map(xi.equiv_group)
    t["link_basis_group"] = t.metabolite_id.map(xi.link_basis).fillna(nt.NO_BASIS)
    t["is_lumping"] = t.tcdb_family_id.isin(lump)
    enz = nb[nb.neighbour_class == "enzyme_candidate"]
    win = enz.groupby("system_id").candidate.agg(set).to_dict()
    run = enz[enz.in_system_run.map(nt.to_bool)].groupby("system_id").candidate.agg(set).to_dict()
    cache, res = {}, []
    for r in t[["system_id", "metabolite_id"]].itertuples(index=False):
        k = (r.system_id, r.metabolite_id)
        if k not in cache:
            cache[k] = nt.can_use_equiv(r.metabolite_id, xi, gbg, win.get(r.system_id, set()), run.get(r.system_id, set()))
        res.append(cache[k])
    t = pd.concat([t.reset_index(drop=True), pd.DataFrame(res).drop(columns="equiv_group")], axis=1)
    cols = ["system_id", "locus_tag", "gene_name", "subunit_role", "metabolite_id", "metabolite_name", "n_status",
            "equiv_group", "link_basis_group", "substrate_depth", "tcdb_family_id", "tcdb_level_kind", "is_lumping",
            "evidence", "tcdb_evidence_score", "evidence_score", "source_agreement", "pfam_support",
            "attachment_depth", "transport_substrate_resolution", "likely_transporter", "domain_substrate_hint",
            "can_use_window", "linked_enzyme_loci_window", "can_use_run", "linked_enzyme_loci_run", "match_basis",
            "genome_enzyme_loci"]
    full = t[cols].sort_values(["system_id", "locus_tag", "substrate_depth", "metabolite_name"])
    full.to_csv(d / f"p5_{tag}_system_substrates_full.csv", index=False)
    Nv = full[full.n_status != "no_N"]
    fi = Nv[Nv.transport_substrate_resolution == "family_inferred"]
    coll = (fi.groupby(["system_id", "locus_tag", "gene_name"], dropna=False)
            .agg(n_most_specific=("substrate_depth", lambda s: int((s == "most_specific").sum())),
                 n_inherited=("substrate_depth", lambda s: int((s == "inherited").sum())),
                 example_substrates=("metabolite_name", lambda s: " | ".join(sorted(set(map(str, s)))[:5])))
            .reset_index().assign(collapsed=True, transport_substrate_resolution="family_inferred"))
    pd.concat([Nv[Nv.transport_substrate_resolution != "family_inferred"].assign(collapsed=False), coll],
              ignore_index=True).to_csv(d / f"p5_{tag}_system_substrates_summary.csv", index=False)
    le = []
    for r in Nv[Nv.linked_enzyme_loci_window.fillna("") != ""].itertuples():
        for lt in r.linked_enzyme_loci_window.split("|"):
            le.append({"system_id": r.system_id, "candidate": lt, "substrate_id": r.metabolite_id,
                       "substrate_name": r.metabolite_name, "equiv_group": r.equiv_group, "match_basis": r.match_basis})
    led = pd.DataFrame(le, columns=["system_id", "candidate", "substrate_id", "substrate_name", "equiv_group",
                                    "match_basis"]).drop_duplicates(["system_id", "candidate", "equiv_group"])
    led.to_csv(d / f"p5_{tag}_linked_enzymes.csv", index=False)
    lk = led.groupby(["system_id", "candidate"]).substrate_name.agg(lambda s: " | ".join(sorted(set(map(str, s)))))
    nb5 = nb.copy()
    nb5["linked_substrates"] = [lk.get(k) for k in zip(nb5.system_id, nb5.candidate)]
    nb5["is_linked_enzyme"] = nb5.linked_substrates.notna()
    nb5["neighbour_class_step5"] = nb5.neighbour_class.where(~nb5.is_linked_enzyme, "linked_enzyme")
    nb5.to_csv(d / f"p5_{tag}_neighbour_candidates_step5.csv", index=False)
    nn = set(xref.loc[xref.name_norm.isin(["nitrate", "nitrite"]), "equiv_group"])
    en = full[full.equiv_group.isin(nn)].copy()
    en["compound"] = en.equiv_group.map({g: c for c, v in expect.items() for g in v["groups"]})
    en.to_csv(d / f"p5_{tag}_expected_negative_1.csv", index=False)
    exp_rows = []
    for comp, v in expect.items():
        chk = nt.expectation_check(en[en.compound == comp], v["expected_usable"], defs=("can_use_window", "can_use_run"))
        exp_rows.append({"compound": comp, "groups": "|".join(v["groups"]), "expected_usable": v["expected_usable"],
                         "genome_genes": "|".join(v["genome_genes"]), "n_rows": int((en.compound == comp).sum()),
                         **{f"{k}_observed": json.dumps(x["observed"]) for k, x in chk.items()},
                         **{f"{k}_pass": x["pass"] for k, x in chk.items()}})
    pd.DataFrame(exp_rows).to_csv(d / f"p5_{tag}_expectation_check.csv", index=False)
    fi_fams = set(tv[tv.locus_tag.isin(roles.index[roles.index.isin(full.loc[full.transport_substrate_resolution ==
                                                                              "family_inferred", "locus_tag"])])].tcdb_family_id)
    summ = {
        "organism": org, "role_map_hash": role_map_hash(d), "lumping_threshold": a.lumping_threshold,
        "lumping_families": sorted(lump),
        "family_inferred_gene_attachments_not_flagged_lumping": sorted(fi_fams - lump),
        "rows_full": int(len(full)), "rows_by_n_status": full.n_status.value_counts().to_dict(),
        "rows_N_or_noformula": int(len(Nv)), "rows_by_depth_N": Nv.substrate_depth.value_counts().to_dict(),
        "genes": int(full.locus_tag.nunique()), "systems": int(full.system_id.nunique()),
        "family_inferred_genes": int(fi.locus_tag.nunique()), "tcdb_verbose_unjoined_rows": unjoined,
        "xref_rows": int(len(xref)), "xref_link_basis": xref.link_basis.fillna("").value_counts().to_dict(),
        "name_soft_groups": sorted(set(soft.equiv_group)),
        "can_use_window_N": Nv.can_use_window.value_counts().to_dict(),
        "can_use_run_N": Nv.can_use_run.value_counts().to_dict(),
        "linked_pairs": int(len(led)), "linked_genes": int(led.candidate.nunique()),
        "expectation_check_nitrate_nitrite": exp_rows,
        "calls": log}
    if a.pilot:
        key = pd.read_csv(ANSWER_KEY / "pilot_substrates.csv")
        kk = ["locus_tag", "metabolite_id", "tcdb_family_id"]
        m = key.merge(full, on=kk, how="left", suffixes=("_key", ""), indicator=True)
        m["row_found"] = m._merge == "both"
        m["depth_agrees"] = m.substrate_depth_key == m.substrate_depth
        m["window_vs_rule"] = m.can_use_if_window8_rule == m.can_use_window
        m["run_vs_rule"] = m.can_use_if_same_strand_run_rule == m.can_use_run
        m["window_vs_expected"] = m.can_use_expected == m.can_use_window
        m["run_vs_expected"] = m.can_use_expected == m.can_use_run
        m.drop(columns="_merge").to_csv(d / f"p5_{tag}_pilot_substrate_diff.csv", index=False)
        ours = full[full.locus_tag.isin(set(key.locus_tag)) & (full.n_status != "no_N")]
        ex = ours.merge(key[kk], on=kk, how="left", indicator=True)
        ex[ex._merge == "left_only"].drop(columns="_merge").to_csv(d / f"p5_{tag}_pilot_rows_not_in_key.csv", index=False)
        summ["pilot"] = {k: int(v) for k, v in {"key_rows": len(m), "found": m.row_found.sum(),
                                                "depth_agree": m.depth_agrees.sum(), "window_vs_rule": m.window_vs_rule.sum(),
                                                "run_vs_rule": m.run_vs_rule.sum(),
                                                "window_vs_expected": m.window_vs_expected.sum(),
                                                "run_vs_expected": m.run_vs_expected.sum()}.items()}
    write_summary(d / f"p5_{tag}_summary.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k != "calls"}, default=str, indent=1))


if __name__ == "__main__":
    main()
