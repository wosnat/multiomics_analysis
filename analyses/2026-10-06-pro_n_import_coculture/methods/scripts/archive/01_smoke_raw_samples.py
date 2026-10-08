"""Smoke: run n_transport pure functions on the saved real raw samples (no KG calls)."""
import sys
from pathlib import Path
import pandas as pd

M = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(M))
import n_transport as nt

RAW = M / "data" / "raw_samples"
got = pd.read_csv(RAW / "gene_ontology_terms_cyn_pfam_tcdb_verbose.csv")
pf = got[got.ontology_type == "pfam"].groupby("locus_tag")["term_id"].agg(" | ".join)
print("pfam_role:", {k: nt.pfam_role(v) for k, v in pf.items()})
gd = pd.read_csv(RAW / "gene_details_cyn.csv")
print(nt.runs(gd, max_gap_bp=300)[["locus_tag", "strand", "gap_to_next", "run_id", "opposite_strand_in_run"]].to_string())
tc = got[got.ontology_type == "tcdb"].copy()
tc["role"] = tc["locus_tag"].map(lambda x: nt.pfam_role(pf.get(x)))
print(nt.evidence_profile(tc))
mbg = pd.read_csv(RAW / "metabolites_by_gene_cyn_N_transport_verbose.csv")
for sub in ["kegg.compound:C01417", "chebi:14654", "kegg.compound:C00088"]:
    print(sub, nt.can_use(sub, mbg, {"PMM0370", "PMM0371", "PMM0372", "PMM0373"}))
