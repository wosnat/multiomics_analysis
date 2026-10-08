"""Step 2c (API review I6): re-query the universe with every non-`other` role Pfam of the data-built map.

genes_by_ontology(pfam, term_ids=[all Pfams with role != other in p2_pfam_role_map.csv], size filters
off, limit=None, no duplicate (locus_tag, term_id)). Genes not yet in the universe are added with
src_pfam_role_datamap=True. Writes p2c_<tag>_universe.csv (= input universe + additions) and
p2c_<tag>_additions.csv. Run p2a + p2b again on the new universe, then p2c once more with
--check-only to confirm a second pass adds nothing (or report what it would add).
Usage: ... p2c_requery_universe.py --organism "Prochlorococcus MED4" --out-dir <dir> [--universe-file f] [--check-only]
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, genes_by_ontology, to_dataframe

from common import kf, resolve_organism, write_summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--universe-file", default=None)
    ap.add_argument("--check-only", action="store_true")
    a = ap.parse_args()
    d = Path(a.out_dir)
    rmap = pd.read_csv(d / "p2_pfam_role_map.csv")
    terms = sorted(rmap.loc[rmap.role != "other", "pfam_id"])
    log = []
    with GraphConnection() as conn:
        org, tag, _ = resolve_organism(a.organism, conn)
        uf = Path(a.universe_file) if a.universe_file else d / f"p1_{tag}_transporter_genes.csv"
        uni = pd.read_csv(uf)
        res = kf.fetch(genes_by_ontology, "genes_by_ontology(pfam, data-map role Pfams)", log, ("locus_tag", "term_id"),
                       limit_none_ok=True, strict_inputs=True, ontology="pfam", organism=org, term_ids=terms,
                       min_gene_set_size=1, max_gene_set_size=None, conn=conn)
    hits = to_dataframe({"results": res["results"]})
    new = hits[~hits.locus_tag.isin(uni.locus_tag)]
    add = (new.groupby(["locus_tag", "gene_name", "product"], dropna=False)["term_id"]
           .agg(lambda s: " | ".join(sorted(set(s)))).reset_index().rename(columns={"term_id": "role_pfam_ids"}))
    add = add.assign(src_tcdb=False, src_brite=False, src_pfam_role=False, src_pfam_role_datamap=True, src_cyanorak_q=False,
                     tcdb_class_ids=None, brite_transporter_terms=None)
    summ = {"organism": org, "role_map_hash": kf.role_map_hash(rmap), "universe_in": uf.name,
            "n_role_pfams_queried": len(terms), "n_genes_hit": int(hits.locus_tag.nunique()),
            "additions": add[["locus_tag", "gene_name", "product", "role_pfam_ids"]].to_dict("records"),
            "check_only": a.check_only, "calls": log}
    if not a.check_only:
        add.to_csv(d / f"p2c_{tag}_additions.csv", index=False)
        out = pd.concat([uni, add[[c for c in uni.columns if c in add.columns]]], ignore_index=True)
        out.to_csv(d / f"p2c_{tag}_universe.csv", index=False)
        summ["universe_out"] = f"p2c_{tag}_universe.csv"
        summ["universe_size_out"] = int(len(out))
    write_summary(d / f"p2c_{tag}_summary{'_check' if a.check_only else ''}.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k != "calls"}, default=str))


if __name__ == "__main__":
    main()
