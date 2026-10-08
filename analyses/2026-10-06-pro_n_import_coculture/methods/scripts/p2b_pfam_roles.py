"""Step 2b: data-built Pfam role map applied to the universe. No KG calls.

Inputs (<out-dir>): universe file (default p1_<tag>_transporter_genes.csv; p2c passes the augmented
  one), raw/p2_<tag>_pfam_terms.csv, raw/p2_<tag>_tcdb_terms_verbose.csv; with --pilot also
  raw/p1_<tag>_pilot_gene_ontology_terms.csv and raw/p1_<tag>_pilot_gene_details.csv.
Outputs: p2_<tag>_pfam_domains.csv, p2_pfam_role_map.csv, p2_<tag>_gene_roles.csv,
  [--pilot] p2_pilot_roles.csv, p2b_<tag>_summary.json (with the role-map hash).
Usage: ... p2b_pfam_roles.py --organism "Prochlorococcus MED4" --out-dir <dir> [--universe-file f] [--pilot]
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from common import PILOT, kf, nt, write_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--universe-file", default=None)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    d = Path(a.out_dir)
    tag = a.organism.split()[-1].lower()
    uf = Path(a.universe_file) if a.universe_file else d / f"p1_{tag}_transporter_genes.csv"
    uni = pd.read_csv(uf)
    pf = pd.read_csv(d / "raw" / f"p2_{tag}_pfam_terms.csv")
    tc = pd.read_csv(d / "raw" / f"p2_{tag}_tcdb_terms_verbose.csv")
    cyf = d / "raw" / f"p2_{tag}_cyanorak_terms.csv"
    cyr = pd.read_csv(cyf) if cyf.exists() and cyf.stat().st_size > 2 else pd.DataFrame(columns=["locus_tag", "term_id"])
    cyg = cyr.groupby("locus_tag")["term_id"].agg(lambda s: " | ".join(sorted(set(s)))) if len(cyr) else pd.Series(dtype=str)
    assert not pf.duplicated(["locus_tag", "term_id"]).any() and not tc.duplicated(["locus_tag", "term_id"]).any()

    dom = (pf.groupby(["term_id", "term_name"])["locus_tag"]
           .agg(n_genes="nunique", example_loci=lambda s: " | ".join(sorted(set(s))[:5]))
           .reset_index().rename(columns={"term_id": "pfam_id", "term_name": "pfam_name"})
           .sort_values(["n_genes", "pfam_id"], ascending=[False, True]))
    assert dom["pfam_id"].is_unique
    dom.to_csv(d / f"p2_{tag}_pfam_domains.csv", index=False)
    rmap = nt.build_pfam_role_map(dom)
    cols = ["pfam_id", "pfam_name", "role", "rule_matched", "name_rule_role", "name_rule", "name_rule_text",
            "seed_role", "seed_conflict", "n_genes", "example_loci"]
    rmap[cols].to_csv(d / "p2_pfam_role_map.csv", index=False)
    rm = nt.role_map_dict(rmap)

    gp = pf.groupby("locus_tag")["term_id"].agg(lambda s: " | ".join(sorted(s)))
    tcg = tc.groupby("locus_tag")
    rows = []
    for r in uni.itertuples():
        pids = gp.get(r.locus_tag, "")
        per = " | ".join(f"{nt._pfam_acc(p)}:{rm.get(nt._pfam_acc(p), 'other')}" for p in nt.parse_list(pids))
        has_t = r.locus_tag in tcg.groups
        tcdb_ids = " | ".join(sorted(tcg.get_group(r.locus_tag)["term_id"])) if has_t else ""
        ev = (nt.tcdb_transporter_evidence(tcg.get_group(r.locus_tag)) if has_t
              else {"tcdb_c123_max_score": None, "tcdb_c123_source_agreement": ""})
        brite = nt.to_bool(r.src_brite)
        cyro = cyg.get(r.locus_tag, "")
        lt_row = {"pfam_ids": pids, "brite_transporter": brite, "tcdb_ids": tcdb_ids, "cyanorak_roles": cyro}
        rows.append({"locus_tag": r.locus_tag, "gene_name": r.gene_name, "product": r.product,
                     "pfam_ids": pids, "pfam_roles": per, "gene_role": nt.pfam_role(pids, rm),
                     "seed_map_role": nt.pfam_role(pids),
                     "likely_transporter": nt.likely_transporter(lt_row, rm),
                     "likely_transporter_basis": nt.likely_transporter_basis(lt_row, rm),
                     "src_tcdb": nt.to_bool(r.src_tcdb), "src_brite": brite,
                     "src_pfam_role": nt.to_bool(r.src_pfam_role),
                     "src_pfam_role_datamap": nt.to_bool(getattr(r, "src_pfam_role_datamap", False)),
                     "src_cyanorak_q": nt.to_bool(getattr(r, "src_cyanorak_q", False)),
                     "tcdb_ids": tcdb_ids, "tcdb_class_ids_p1": r.tcdb_class_ids,
                     "cyanorak_roles": cyro or nt.NO_BASIS,
                     "cyanorak_q_roles": " | ".join(x for x in nt.parse_list(cyro) if x.startswith("cyanorak.role:Q"))
                     or nt.NO_BASIS, **ev})
    g = pd.DataFrame(rows)
    g.to_csv(d / f"p2_{tag}_gene_roles.csv", index=False)

    summ = {"organism": a.organism, "universe_file": uf.name, "role_map_hash": kf.role_map_hash(rmap),
            "n_universe_genes": int(len(g)), "n_domains": int(len(dom)),
            "domains_by_role": rmap.role.value_counts().to_dict(),
            "genes_by_role": g.gene_role.value_counts().to_dict(),
            "likely_transporter_counts": g.likely_transporter.value_counts().to_dict(),
            "seed_conflicts": rmap.loc[rmap.seed_conflict, ["pfam_id", "pfam_name", "seed_role",
                                                            "name_rule_role"]].to_dict("records")}
    if a.pilot:
        pg = pd.read_csv(d / "raw" / f"p1_{tag}_pilot_gene_ontology_terms.csv")
        pg = pg[pg.ontology_type == "pfam"].groupby("locus_tag")["term_id"].agg(lambda s: " | ".join(sorted(s)))
        names = pd.read_csv(d / "raw" / f"p1_{tag}_pilot_gene_details.csv").set_index("locus_tag")["gene_name"]
        gi = g.set_index("locus_tag")
        prow = []
        for lt in PILOT:
            if lt in gi.index:
                x = gi.loc[lt]
                prow.append({"locus_tag": lt, "in_universe": True, "gene_name": x.gene_name, "pfam_ids": x.pfam_ids,
                             "gene_role": x.gene_role, "likely_transporter": x.likely_transporter,
                             "tcdb_c123_max_score": x.tcdb_c123_max_score,
                             "tcdb_c123_source_agreement": x.tcdb_c123_source_agreement})
            else:
                pids = pg.get(lt, "")
                prow.append({"locus_tag": lt, "in_universe": False, "gene_name": names.get(lt), "pfam_ids": pids,
                             "gene_role": nt.pfam_role(pids, rm)})
        pd.DataFrame(prow).to_csv(d / "p2_pilot_roles.csv", index=False)
    write_summary(d / f"p2b_{tag}_summary.json", summ)
    print(json.dumps(summ, default=str)[:1200])


if __name__ == "__main__":
    main()
