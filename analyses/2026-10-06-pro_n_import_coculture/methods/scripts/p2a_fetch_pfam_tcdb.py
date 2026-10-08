"""Step 2a: every Pfam domain and every TCDB leaf attachment (verbose) of the universe genes.

One call per chunk of 200 locus tags with limit=None (gene_ontology_terms accepts None), returned ==
total_matching, no duplicate (locus_tag, term_id) (kg_fetch).
Usage: ... p2a_fetch_pfam_tcdb.py --organism "Prochlorococcus MED4" --out-dir <dir> [--universe-file <csv>]
  (default universe: <dir>/p1_<tag>_transporter_genes.csv; p2c passes the augmented universe)
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, gene_ontology_terms, to_dataframe

from common import kf, resolve_organism, write_summary

KEY = ("locus_tag", "term_id")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--universe-file", default=None)
    a = ap.parse_args()
    d = Path(a.out_dir)
    log = []
    with GraphConnection() as conn:
        org, tag, _ = resolve_organism(a.organism, conn)
        uf = Path(a.universe_file) if a.universe_file else d / f"p1_{tag}_transporter_genes.csv"
        loci = pd.read_csv(uf)["locus_tag"].tolist()
        pf = kf.fetch(gene_ontology_terms, "gene_ontology_terms(universe, pfam)", log, KEY, chunk_param="locus_tags",
                      chunk_size=200, limit_none_ok=True, locus_tags=loci, organism=org, ontology=["pfam"], conn=conn)
        tc = kf.fetch(gene_ontology_terms, "gene_ontology_terms(universe, tcdb, verbose)", log, KEY,
                      chunk_param="locus_tags", chunk_size=200, limit_none_ok=True, locus_tags=loci, organism=org,
                      ontology=["tcdb"], verbose=True, conn=conn)
        cy = kf.fetch(gene_ontology_terms, "gene_ontology_terms(universe, cyanorak_role)", log, KEY,
                      chunk_param="locus_tags", chunk_size=200, limit_none_ok=True, strict_inputs=True,
                      locus_tags=loci, organism=org, ontology=["cyanorak_role"], conn=conn)
    for name, res in (("pfam_terms", pf), ("tcdb_terms_verbose", tc), ("cyanorak_terms", cy)):
        to_dataframe({"results": res["results"]}).to_csv(d / "raw" / f"p2_{tag}_{name}.csv", index=False)
    write_summary(d / f"p2a_{tag}_summary.json", {"organism": org, "universe_file": str(uf.name),
                                                  "n_universe": len(loci), "calls": log})
    print(json.dumps([{k: c[k] for k in ("call", "total_matching", "returned", "n_calls")} for c in log]))


if __name__ == "__main__":
    main()
