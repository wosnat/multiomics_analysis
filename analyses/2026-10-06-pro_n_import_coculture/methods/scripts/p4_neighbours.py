"""Step 4: neighbour candidates of every reference system, with their own metabolism-arm chemistry.

Positions from the genome coordinate table (never gene_neighbors.bp_gap). Roles ONLY from the step-2
map; neighbourhood-only Pfams get an unverified role_hint. Classes: no_coordinates > other_system >
tcdb_transporter > missing_subunit > enzyme_candidate > context (linked_enzyme is set in step 5).
KG calls via kg_fetch (single call per chunk, totals, no duplicate natural key):
  gene_ontology_terms(candidates, [pfam, kegg, ec]); gene_details(candidates);
  metabolites_by_gene(enzyme candidates, metabolism arm, NO element filter (I1)), key
  (locus_tag, metabolite_id, reaction_id); list_metabolites(those ids, verbose) for n_status.
Outputs (<out-dir>): p4_<tag>_neighbour_candidates.csv, p4_<tag>_enzyme_candidate_metabolites.csv (all
  statuses, n_status column), p4_<tag>_neighbourhood_only_pfam_hints.csv, [--pilot] p4_<tag>_pilot_neighbours.csv,
  p4_<tag>_summary.json. (The metabolite equivalence table moved to step 5, which sees both arms.)
Usage: ... p4_neighbours.py --organism "Prochlorococcus MED4" --out-dir <dir> [--window 8] [--pilot]
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import (GraphConnection, gene_details, gene_ontology_terms, list_metabolites,
                                 metabolites_by_gene, to_dataframe)

from common import PILOT_ANCHORS, REF, kf, nt, resolve_organism, role_map_hash, write_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--window", type=int, default=8)
    ap.add_argument("--gap", type=int, default=200)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    d = Path(a.out_dir)
    log = []
    with GraphConnection() as conn:
        org, tag, _ = resolve_organism(a.organism, conn)
        gs = pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv")
        runs = pd.read_csv(d / f"p3_{tag}_genome_runs_gap{a.gap}.csv")
        nocoord = pd.read_csv(d / f"p3_{tag}_no_coordinate_genes.csv")
        roles = pd.read_csv(d / f"p2_{tag}_gene_roles.csv").set_index("locus_tag")
        rmap_df = pd.read_csv(d / "p2_pfam_role_map.csv")
        members = gs[["locus_tag", "system_id"]]
        cand = nt.neighbour_candidates(runs, members, window=a.window).assign(has_coordinates=True)
        ncand = nt.no_coordinate_candidates(members, nocoord.locus_tag.tolist(), window=a.window) \
            .assign(has_coordinates=False)
        allc = pd.concat([cand, ncand], ignore_index=True)
        genes = sorted(set(allc.candidate))
        got = to_dataframe({"results": kf.fetch(
            gene_ontology_terms, "gene_ontology_terms(candidates, pfam/kegg/ec)", log, ("locus_tag", "term_id"),
            chunk_param="locus_tags", chunk_size=300, limit_none_ok=True, locus_tags=genes, organism=org,
            ontology=["pfam", "kegg", "ec", "cyanorak_role"], conn=conn)["results"]})
        det = to_dataframe({"results": kf.fetch(gene_details, "gene_details(candidates)", log, ("locus_tag",),
                                                chunk_param="locus_tags", chunk_size=300, limit_none_ok=True,
                                                locus_tags=genes, conn=conn)["results"]}).set_index("locus_tag")
        ann = {o: got[got.ontology_type == o].groupby("locus_tag")["term_id"].agg(lambda s: " | ".join(sorted(set(s))))
               for o in ("pfam", "kegg", "ec", "cyanorak_role")}
        rm = nt.role_map_dict(rmap_df)
        pf = got[got.ontology_type == "pfam"][["term_id", "term_name"]].drop_duplicates()
        new = pf[~pf.term_id.isin(rmap_df.pfam_id)].rename(columns={"term_id": "pfam_id", "term_name": "pfam_name"})
        if len(new):
            hr = new.pfam_name.map(nt.pfam_name_role)
            new = new.assign(hint_role=hr.map(lambda x: x[0]), hint_rule=hr.map(lambda x: x[1]),
                             hint_text=hr.map(lambda x: x[2]))
        new.to_csv(d / f"p4_{tag}_neighbourhood_only_pfam_hints.csv", index=False)
        hint_of = dict(zip(new.pfam_id.map(nt._pfam_acc), new.hint_role)) if len(new) else {}
        sys_of = gs.set_index("locus_tag")["system_id"]
        rows = []
        for r in allc.itertuples(index=False):
            g = r.candidate
            inu = g in roles.index
            pids, ec, ko = ann["pfam"].get(g, ""), ann["ec"].get(g, ""), ann["kegg"].get(g, "")
            rc = det.loc[g, "reaction_count"] if g in det.index and "reaction_count" in det.columns else 0
            rc = 0 if pd.isna(rc) else int(rc)
            tcdb = roles.loc[g, "tcdb_ids"] if inu and isinstance(roles.loc[g, "tcdb_ids"], str) else ""
            brite = nt.to_bool(roles.loc[g, "src_brite"]) if inu else False
            other_sys = sys_of.get(g)
            row = {"pfam_ids": pids, "brite_transporter": brite, "tcdb_ids": tcdb,
                   "cyanorak_roles": ann["cyanorak_role"].get(g, ""),
                   "is_enzyme_candidate": bool(ec) or rc > 0, "has_coordinates": r.has_coordinates,
                   "member_of_system": other_sys}
            hints = [f"{nt._pfam_acc(x)}:{hint_of[nt._pfam_acc(x)]}" for x in nt.parse_list(pids)
                     if hint_of.get(nt._pfam_acc(x), "other") != "other"]
            rows.append({**r._asdict(),
                         "candidate_name": det.loc[g, "gene_name"] if g in det.index and "gene_name" in det.columns else None,
                         "candidate_product": det.loc[g, "product"] if g in det.index else None,
                         "in_universe": inu, "other_system_id": other_sys, "role": nt.pfam_role(pids, rm),
                         "role_hint_unverified": " | ".join(hints),
                         "likely_transporter": roles.loc[g, "likely_transporter"] if inu else nt.likely_transporter(row, rm),
                         "pfam_ids": pids, "kegg_ko": ko, "ec": ec, "reaction_count": rc, "tcdb_ids": tcdb,
                         "brite_transporter": brite, "is_enzyme_candidate": row["is_enzyme_candidate"],
                         "recruited_by": nt.recruited_by(row, rm), "neighbour_class": nt.classify_neighbour(row, rm)})
        nb = pd.DataFrame(rows)
        nb.to_csv(d / f"p4_{tag}_neighbour_candidates.csv", index=False)
        enz = sorted(set(nb.loc[nb.neighbour_class == "enzyme_candidate", "candidate"]))
        mb = to_dataframe({"results": kf.fetch(
            metabolites_by_gene, "metabolites_by_gene(enzyme candidates, metabolism, no element filter)", log,
            ("locus_tag", "metabolite_id", "reaction_id"), chunk_param="locus_tags", chunk_size=50,
            locus_tags=enz, organism=org, evidence_sources=["metabolism"], conn=conn)["results"]})
        mids = sorted(set(mb.metabolite_id))
        lm = to_dataframe({"results": kf.fetch(list_metabolites, "list_metabolites(enzyme-side ids, verbose)", log,
                                               ("metabolite_id",), chunk_param="metabolite_ids", chunk_size=400,
                                               limit_none_ok=True, metabolite_ids=mids, verbose=True,
                                               conn=conn)["results"]})
    assert set(mids) <= set(lm.metabolite_id), "metabolite ids missing from list_metabolites"
    nst = {m: nt.n_status(e, f) for m, e, f in zip(lm.metabolite_id, lm.get("elements"), lm.get("formula"))}
    mb.to_csv(d / "raw" / f"p4_{tag}_enzyme_candidate_metabolism_raw.csv", index=False)
    lm.to_csv(d / "raw" / f"p4_{tag}_enzyme_side_list_metabolites.csv", index=False)
    nmet = (mb.groupby(["locus_tag", "metabolite_id", "metabolite_name"], dropna=False)
            .agg(n_reactions=("reaction_id", "nunique"),
                 reaction_ids=("reaction_id", lambda s: " | ".join(sorted(set(map(str, s))))))
            .reset_index())
    nmet["n_status"] = nmet.metabolite_id.map(nst)
    nmet.to_csv(d / f"p4_{tag}_enzyme_candidate_metabolites.csv", index=False)
    pl = pd.read_csv(d / f"p3_{tag}_no_coordinate_placeability.csv")
    summ = {
        "organism": org, "role_map_hash": role_map_hash(d), "window": a.window, "runs_gap": a.gap,
        "n_systems": int(gs.system_id.nunique()), "n_candidate_rows": int(len(nb)),
        "n_candidate_genes": int(nb.candidate.nunique()),
        "rows_by_class": nb.neighbour_class.value_counts().to_dict(),
        "genes_by_class": nb.drop_duplicates("candidate").neighbour_class.value_counts().to_dict(),
        "missing_subunit_genes": sorted(nb.loc[nb.neighbour_class == "missing_subunit", "candidate"].unique()),
        "no_coordinate_genes_total": int(len(nocoord)),
        "no_coordinate_placeability": pl.placement_status.value_counts().to_dict(),
        "no_coordinate_candidate_rows": int(len(ncand)),
        "enzyme_candidate_genes": len(enz), "enzyme_metabolite_rows": int(len(nmet)),
        "enzyme_metabolite_rows_by_n_status": nmet.n_status.value_counts().to_dict(),
        "calls": log}
    if a.pilot:
        sid = gs.set_index("locus_tag").system_id
        nm = nmet[nmet.n_status != "no_N"].groupby("locus_tag").metabolite_name.agg(lambda s: " | ".join(sorted(set(map(str, s)))))
        pil = []
        for case, anchor in PILOT_ANCHORS.items():
            sub = nb[nb.system_id == sid[anchor]].copy()
            sub.insert(0, "case", case)
            sub["N_or_noformula_metabolites"] = sub.candidate.map(nm)
            pil.append(sub)
        pd.concat(pil, ignore_index=True).to_csv(d / f"p4_{tag}_pilot_neighbours.csv", index=False)
    write_summary(d / f"p4_{tag}_summary.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k != "calls"}, default=str, indent=1))


if __name__ == "__main__":
    main()
