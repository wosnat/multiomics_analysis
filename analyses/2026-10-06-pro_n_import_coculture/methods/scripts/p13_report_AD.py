"""Report for researcher decisions A-D (n_transport v1.2.0) against the v1.1.0 archive. No KG calls.

Writes into <data-dir>: p13_A_likely_transporter_changes.csv, p13_A_tier_changes.csv,
p13_B_amt1_links.csv, p13_C_no_formula.csv, p12_review_list_unclassified_N.csv (union across strains),
p13_D_random_assignments.csv, p13_report.json.
Usage: ... p13_report_AD.py --data-dir analyses/2026-10-06-pro_n_import_coculture/methods/data --old v1.1.0_archive
"""
import argparse
import json
import re
from pathlib import Path

import pandas as pd

TAGS = ["med4", "mit9313", "natl2a"]
NON_TRANSPORTER_WORDS = r"regulator|regulatory|helicase|kinase|response|sensor|transcription|repressor|activator|sigma|two-component|histidine kinase"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--old", default="v1.1.0_archive")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    D = Path(a.data_dir)
    rep = {}
    lt_rows, tier_rows, amt_rows, nf_rows, rev, samp = [], [], [], [], [], []
    for t in TAGS:
        n, o = D / t, D / a.old / t
        # A: likely_transporter (universe genes) and tiers
        gn = pd.read_csv(n / f"p2_{t}_gene_roles.csv").set_index("locus_tag")
        go = pd.read_csv(o / f"p2_{t}_gene_roles.csv").set_index("locus_tag")
        com = gn.index.intersection(go.index)
        ch = com[gn.loc[com, "likely_transporter"] != go.loc[com, "likely_transporter"]]
        for lt in ch:
            prod = str(gn.loc[lt, "product"])
            lt_rows.append({"strain": t, "locus_tag": lt, "gene_name": gn.loc[lt, "gene_name"], "product": prod,
                            "likely_transporter_old": go.loc[lt, "likely_transporter"],
                            "likely_transporter_new": gn.loc[lt, "likely_transporter"],
                            "basis_new": gn.loc[lt, "likely_transporter_basis"],
                            "cyanorak_q_roles": gn.loc[lt, "cyanorak_q_roles"],
                            "non_transporter_word_in_product": bool(re.search(NON_TRANSPORTER_WORDS, prod, re.I))})
        nb_n = pd.read_csv(n / f"p4_{t}_neighbour_candidates.csv").drop_duplicates("candidate").set_index("candidate")
        nb_o = pd.read_csv(o / f"p4_{t}_neighbour_candidates.csv").drop_duplicates("candidate").set_index("candidate")
        cn = nb_n.index.intersection(nb_o.index)
        nbch = cn[(nb_n.loc[cn, "likely_transporter"].astype(str) != nb_o.loc[cn, "likely_transporter"].astype(str))
                  & ~nb_n.loc[cn, "in_universe"].astype(bool)]
        for c in nbch:
            prod = str(nb_n.loc[c, "candidate_product"])
            lt_rows.append({"strain": t, "locus_tag": c, "gene_name": nb_n.loc[c, "candidate_name"], "product": prod,
                            "likely_transporter_old": nb_o.loc[c, "likely_transporter"],
                            "likely_transporter_new": nb_n.loc[c, "likely_transporter"],
                            "basis_new": "neighbour (non-universe)", "cyanorak_q_roles": None,
                            "non_transporter_word_in_product": bool(re.search(NON_TRANSPORTER_WORDS, prod, re.I))})
        sn = pd.read_csv(n / f"p11_{t}_systems.csv").set_index("system_id")
        so = pd.read_csv(o / f"p11_{t}_systems.csv").set_index("system_id")
        cs = sn.index.intersection(so.index)
        for s in cs[(sn.loc[cs, "tier"] != so.loc[cs, "tier"])]:
            tier_rows.append({"strain": t, "system_id": s, "member_names": sn.loc[s, "member_names"],
                              "tier_old": so.loc[s, "tier"], "tier_new": sn.loc[s, "tier"],
                              "reason_new": sn.loc[s, "tier_reason"], "transport_class": sn.loc[s, "transport_class_ids"]})
        rep.setdefault("systems_only_old_or_new", {})[t] = [sorted(set(so.index) - set(sn.index)), sorted(set(sn.index) - set(so.index))]
        # B: amt1 links
        amt = sn[sn.member_names.str.contains(":amt1", na=False)].index.tolist()
        fn_n = pd.read_csv(n / f"p11_{t}_function_linked.csv")
        fn_o = pd.read_csv(o / f"p11_{t}_function_linked.csv")
        for s in amt:
            fmt = lambda f: "; ".join(sorted(f"{r.locus_tag}({r.enzyme_name})->{r.substrate_names}"
                                             + (f"[{r.link_breadth}]" if "link_breadth" in f.columns else "")
                                             for r in f[f.system_id == s].itertuples()))
            amt_rows.append({"strain": t, "system_id": s, "before": fmt(fn_o), "after": fmt(fn_n)})
        rep.setdefault("function_linked_pairs_old_new", {})[t] = [int(len(fn_o)), int(len(fn_n))]
        rep.setdefault("function_linked_breadth_new", {})[t] = fn_n.link_breadth.value_counts().to_dict()
        # C: no-formula
        co = pd.read_csv(o / f"p11_{t}_compound_classes.csv")
        cn_ = pd.read_csv(n / f"p11_{t}_compound_classes.csv")
        old_nf_other = co[(co.n_status == "no_formula") & (co.compound_class == "other N")]
        new_nf = cn_[cn_.n_status == "no_formula"].compound_class.value_counts().to_dict()
        lay = pd.read_csv(n / f"p12_{t}_compound_classes_layered.csv")
        nf_rows.append({"strain": t, "old_no_formula_groups_labelled_other_N": int(len(old_nf_other)),
                        "new_name_layer_no_formula_classes": json.dumps(new_nf),
                        "new_layered_no_formula_classes": json.dumps(lay[lay.n_status == "no_formula"].compound_class.value_counts().to_dict()),
                        "any_other_N_label_left": bool((cn_.compound_class == "other N").any() or (lay.compound_class == "other N").any())})
        # D
        sm = json.loads((n / f"p12_{t}_summary.json").read_text(encoding="utf-8"))
        rep.setdefault("D_per_layer", {})[t] = sm["per_layer"]
        rep.setdefault("D_per_class", {})[t] = sm["per_class"]
        rep.setdefault("D_pathways_seen_mapped", {})[t] = [sm["pathways_seen"], sm["pathways_mapped"]]
        rep.setdefault("D_families_context", {})[t] = sm["families_with_context"]
        rep["chebi"] = sm["kg_chebi_class_hierarchy"]
        rev.append(pd.read_csv(n / f"p12_{t}_review_candidates.csv"))
        lay["strain"] = t
        samp.append(lay)
    A1 = pd.DataFrame(lt_rows); A1.to_csv(D / "p13_A_likely_transporter_changes.csv", index=False)
    A2 = pd.DataFrame(tier_rows); A2.to_csv(D / "p13_A_tier_changes.csv", index=False)
    B = pd.DataFrame(amt_rows); B.to_csv(D / "p13_B_amt1_links.csv", index=False)
    C = pd.DataFrame(nf_rows); C.to_csv(D / "p13_C_no_formula.csv", index=False)
    R = pd.concat(rev, ignore_index=True)
    U = (R.groupby("equiv_group").agg(names=("names", "first"), metabolite_ids=("metabolite_ids", "first"),
                                      strains=("strain", lambda s: "|".join(sorted(set(s)))),
                                      systems=("systems", lambda s: " || ".join(s)), tiers=("tiers", lambda s: "|".join(sorted(set("|".join(s).split("|"))))),
                                      genes=("genes", lambda s: " || ".join(s)), gene_names=("gene_names", lambda s: " || ".join(map(str, s))),
                                      tcdb_families=("tcdb_families", lambda s: "|".join(sorted(set("|".join(s).split("|"))))),
                                      tcdb_family_names=("tcdb_family_names", "first")).reset_index()
         .sort_values("names"))
    U.to_csv(D / "p12_review_list_unclassified_N.csv", index=False)
    L = pd.concat(samp, ignore_index=True)
    # 10 random ASSIGNMENTS from the non-name layers, stratified: 5 pathway, 4 family_context, 1 tie-break
    parts = []
    for src, k in (("pathway", 5), ("family_context", 4), ("pathway+transport_class_tiebreak", 1)):
        pool = L[L.class_source == src]
        parts.append(pool.sample(n=min(k, len(pool)), random_state=a.seed))
    pick = pd.concat(parts, ignore_index=True)
    pick[["strain", "equiv_group", "names", "n_status", "compound_class", "class_source", "layer_votes",
          "pathways_mapped", "family_row_classes", "q_allowed_classes"]].to_csv(D / "p13_D_random_assignments.csv", index=False)
    rep["A"] = {"likely_transporter_changes": int(len(A1)),
                "by_change": A1.groupby(["strain", "likely_transporter_old", "likely_transporter_new"]).size().reset_index(name="n").to_dict("records") if len(A1) else [],
                "flagged_non_transporter_words": A1[A1.non_transporter_word_in_product][["strain", "locus_tag", "gene_name", "product"]].to_dict("records") if len(A1) else [],
                "tier_changes": int(len(A2))}
    rep["B"] = B.to_dict("records")
    rep["C"] = C.to_dict("records")
    rep["D_review_list_n"] = int(len(U))
    rep["D_random"] = pick[["strain", "equiv_group", "names", "compound_class", "class_source"]].to_dict("records")
    (D / "p13_report.json").write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
    print(json.dumps(rep, indent=1, default=str))


if __name__ == "__main__":
    main()
