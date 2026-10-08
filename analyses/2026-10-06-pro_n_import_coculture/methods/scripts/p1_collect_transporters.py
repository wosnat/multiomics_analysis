"""Step 1: collect the transporter-gene universe of one organism.

Universe = union of
  (a) tcdb      : every gene with a TCDB attachment   genes_by_ontology(tcdb, level=0)
  (b) brite     : BRITE `transporters` tree members    genes_by_ontology(brite, tree='transporters', level=0)
  (c) pfam_role : genes carrying a PFAM_ROLE_MAP seed Pfam  genes_by_ontology(pfam, term_ids=[seeds])
  (d) cyanorak_q: genes with a curated Cyanorak transport role Q.1-Q.9   genes_by_ontology(cyanorak_role,
                  term_ids=[Q.1..Q.9]) (v1.6.0, researcher decision 2026-10-08: rescue path; the genes then go
                  through the normal role / grouping / tier rules)
Size filters off (min_gene_set_size=1, max_gene_set_size=None). Every call: one call (limit=None),
returned == total_matching, no duplicate (locus_tag, term_id) (kg_fetch). The data-built role map
re-query (I6) happens in p2c.
--pilot: also writes the pilot-gene raw rows, status and the gene-anchored cross-check.

Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/p1_collect_transporters.py \
      --organism "Prochlorococcus MED4" --out-dir analyses/2026-10-06-pro_n_import_coculture/methods/data/med4 [--pilot]
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, gene_details, gene_ontology_terms, genes_by_ontology, to_dataframe

from common import PILOT, kf, nt, resolve_organism, write_summary

KEY = ("locus_tag", "term_id")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--pilot", action="store_true")
    a = ap.parse_args()
    out = Path(a.out_dir); (out / "raw").mkdir(parents=True, exist_ok=True)
    log = []
    sizes = dict(min_gene_set_size=1, max_gene_set_size=None)
    with GraphConnection() as conn:
        org, tag, orow = resolve_organism(a.organism, conn)
        src = {
            "tcdb": kf.fetch(genes_by_ontology, "genes_by_ontology(tcdb, level 0)", log, KEY, limit_none_ok=True,
                             ontology="tcdb", organism=org, level=0, conn=conn, **sizes),
            "brite": kf.fetch(genes_by_ontology, "genes_by_ontology(brite transporters, level 0)", log, KEY,
                              limit_none_ok=True, ontology="brite", organism=org, tree="transporters", level=0,
                              conn=conn, **sizes),
            "pfam_role": kf.fetch(genes_by_ontology, "genes_by_ontology(pfam, seed role Pfams)", log, KEY,
                                  limit_none_ok=True, strict_inputs=True, ontology="pfam", organism=org,
                                  term_ids=[f"pfam:{p}" for p in nt.PFAM_ROLE_MAP], conn=conn, **sizes),
            "cyanorak_q": kf.fetch(genes_by_ontology, "genes_by_ontology(cyanorak_role, Q.1-Q.9)", log, KEY,
                                   limit_none_ok=True, strict_inputs=True, ontology="cyanorak_role", organism=org,
                                   term_ids=[f"cyanorak.role:Q.{i}" for i in range(1, 10)], conn=conn, **sizes),
        }
        if a.pilot:
            pgot = kf.fetch(gene_ontology_terms, "gene_ontology_terms(pilot, tcdb/pfam/brite)", log,
                            ("locus_tag", "term_id"), limit_none_ok=True, allow_identical_duplicates=True, locus_tags=PILOT, organism=org,
                            ontology=["tcdb", "pfam", "brite"], conn=conn)
            pgd = kf.fetch(gene_details, "gene_details(pilot)", log, ("locus_tag",), limit_none_ok=True,
                           locus_tags=PILOT, conn=conn)
    dfs = {}
    for k, res in src.items():
        (out / "raw" / f"p1_{tag}_{k}.json").write_text(json.dumps(res["results"], default=str), encoding="utf-8")
        dfs[k] = to_dataframe({"results": res["results"]})
        dfs[k].to_csv(out / "raw" / f"p1_{tag}_{k}.csv", index=False)
    tc, br, pf, cq = dfs["tcdb"], dfs["brite"], dfs["pfam_role"], dfs["cyanorak_q"]
    names = pd.concat([d[["locus_tag", "gene_name", "product"]] for d in (tc, br, pf, cq)]).drop_duplicates("locus_tag") \
        .set_index("locus_tag")
    agg = lambda s: " | ".join(sorted(set(s)))  # noqa: E731
    tcdb_cls = tc.groupby("locus_tag")["term_id"].agg(agg)
    brite_terms = br.groupby("locus_tag")["term_name"].agg(agg)
    pfam_ids = pf.groupby("locus_tag")["term_id"].agg(agg)
    u = names.copy()
    u["src_tcdb"] = u.index.isin(tcdb_cls.index)
    u["src_brite"] = u.index.isin(brite_terms.index)
    u["src_pfam_role"] = u.index.isin(pfam_ids.index)
    u["src_pfam_role_datamap"] = False  # set by p2c (I6)
    cq_ids = cq.groupby("locus_tag")["term_id"].agg(agg)
    u["src_cyanorak_q"] = u.index.isin(cq_ids.index)
    u["cyanorak_q_ids_p1"] = cq_ids.reindex(u.index)
    u["tcdb_class_ids"] = tcdb_cls.reindex(u.index)
    u["brite_transporter_terms"] = brite_terms.reindex(u.index)
    u["role_pfam_ids"] = pfam_ids.reindex(u.index)
    u = u.reset_index().sort_values("locus_tag")
    u.to_csv(out / f"p1_{tag}_transporter_genes.csv", index=False)

    summ = {"organism": org, "tag": tag, "universe_size": int(len(u)),
            "by_source_genes": {"tcdb": int(u.src_tcdb.sum()), "brite": int(u.src_brite.sum()),
                                "pfam_role": int(u.src_pfam_role.sum()), "cyanorak_q": int(u.src_cyanorak_q.sum())},
            "only_cyanorak_q": u.loc[u.src_cyanorak_q & ~u.src_tcdb & ~u.src_brite & ~u.src_pfam_role,
                                     ["locus_tag", "gene_name", "product"]].to_dict("records"),
            "tcdb_class_counts": tc.term_id.value_counts().to_dict(),
            "brite_level0_terms": br.term_name.value_counts().to_dict(),
            "pfam_term_gene_counts": pf.term_id.value_counts().to_dict(), "calls": log}
    if a.pilot:
        got, gd = to_dataframe({"results": pgot["results"]}), to_dataframe({"results": pgd["results"]})
        got.to_csv(out / "raw" / f"p1_{tag}_pilot_gene_ontology_terms.csv", index=False)
        gd.to_csv(out / "raw" / f"p1_{tag}_pilot_gene_details.csv", index=False)
        pd.concat([d[d.locus_tag.isin(PILOT)].assign(source=k) for k, d in dfs.items()]) \
            .to_csv(out / "p1_raw_pilot_rows.csv", index=False)
        ui = u.set_index("locus_tag")
        ind_tcdb = set(got[got.ontology_type == "tcdb"].locus_tag)
        ind_brite = set(got[(got.ontology_type == "brite") & (got.get("tree") == "transporters")].locus_tag)
        rows = []
        for lt in PILOT:
            inu = lt in ui.index
            rows.append({"locus_tag": lt, "in_universe": inu,
                         "src_tcdb": bool(ui.loc[lt, "src_tcdb"]) if inu else False,
                         "src_brite": bool(ui.loc[lt, "src_brite"]) if inu else False,
                         "src_pfam_role": bool(ui.loc[lt, "src_pfam_role"]) if inu else False,
                         "xcheck_has_tcdb": lt in ind_tcdb, "xcheck_brite": lt in ind_brite})
        ps = pd.DataFrame(rows)
        ps["xcheck_agrees"] = (ps.src_tcdb == ps.xcheck_has_tcdb) & (ps.src_brite == ps.xcheck_brite)
        ps.to_csv(out / f"p1_{tag}_pilot_status.csv", index=False)
        summ["pilot_absent"] = ps.loc[~ps.in_universe, "locus_tag"].tolist()
        summ["pilot_xcheck_disagree"] = ps.loc[~ps.xcheck_agrees, "locus_tag"].tolist()
    write_summary(out / f"p1_{tag}_summary.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k != "calls"}, default=str)[:1500])


if __name__ == "__main__":
    main()
