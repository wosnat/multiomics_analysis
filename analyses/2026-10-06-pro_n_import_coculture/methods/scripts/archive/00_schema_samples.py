"""Phase-1 schema inspection: tiny API calls to learn real field names/types.

Saves raw JSON + to_dataframe CSV under methods/data/raw_samples/.
Run from repo root: .venv/Scripts/python.exe <this file>
No expression/DE tools are called.
"""
import json
from pathlib import Path

from multiomics_explorer import (
    GraphConnection, gene_details, gene_ontology_terms, metabolites_by_gene,
    gene_neighbors, to_dataframe,
)

OUT = Path(__file__).resolve().parents[1] / "data" / "raw_samples"
OUT.mkdir(parents=True, exist_ok=True)
CYN = ["PMM0370", "PMM0371", "PMM0372", "PMM0373"]


def save(name, res):
    (OUT / f"{name}.json").write_text(json.dumps(res, indent=2, default=str))
    df = to_dataframe(res)
    df.to_csv(OUT / f"{name}.csv", index=False)
    print(f"== {name}: envelope keys={list(res.keys())}")
    print(f"   total_matching={res.get('total_matching')} returned={res.get('returned')} truncated={res.get('truncated')}")
    if res.get("results"):
        print("   row0 types:", {k: type(v).__name__ for k, v in res["results"][0].items()})
    print("   df columns:", df.columns.tolist(), "dtypes:", dict(df.dtypes.astype(str)))


with GraphConnection() as conn:
    save("gene_details_cyn", gene_details(locus_tags=CYN, conn=conn))
    save("gene_ontology_terms_cyn_pfam_tcdb_verbose",
         gene_ontology_terms(locus_tags=CYN, organism="MED4", ontology=["pfam", "tcdb"],
                             verbose=True, conn=conn))
    save("metabolites_by_gene_cyn_N_transport_verbose",
         metabolites_by_gene(locus_tags=CYN, organism="MED4", metabolite_elements=["N"],
                             evidence_sources=["transport", "metabolism"], verbose=True,
                             limit=10_000, conn=conn))
    save("gene_neighbors_PMM0371_w3", gene_neighbors(locus_tags=["PMM0371"], window=3, limit=None, conn=conn))
