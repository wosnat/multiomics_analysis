"""Step 2 coverage probe — what does the KG actually return for these OGs?

Discovery step (research-methodology Rule 5 interactive-discovery exception):
runs each characterization angle against a small set of DRIVING genes — three
dark core-family representatives plus the GroEL positive control — and freezes
the raw per-angle output to data/ so the coverage findings are reproducible.

Driving genes (all Prochlorococcus MED4, the deepest-studied strain):
  PMM0872  cyanorak:CK_00000141  uncharacterized conserved secreted protein
  PMM1028  cyanorak:CK_00000141  (MED4 paralog of PMM0872)
  PMM0983  cyanorak:CK_00003473  uncharacterized secreted, Prochlorococcus-specific
  PMM1683  cyanorak:CK_00000498  HesB-like domain  (-> eggnog COG0316 = iscA)
  PMM1436  cyanorak:CK_00008054  groL1 / chaperonin GroEL   [CONTROL]

Angles probed (one frozen CSV each):
  members      genes_by_homolog_group   (OG -> member genes, all organisms)
  homologs     gene_homologs(eggnog)    (cross-organism reach: genera, cross_genus)
  neighbors    gene_neighbors           (genomic neighborhood, MED4)
  ontology     gene_ontology_terms      (GO/pfam/role/signalp/localization)
  clusters     gene_clusters_by_gene    (co-expression cluster guilt-by-association)
  metrics      gene_derived_metrics     (pangenome, expr class, diel, localization)
  publications discussed_by_publication-side: gene_overview discussed flags

Run from repo root:
  uv run python analyses/2026-06-16-conserved_hypothetical_characterization/2_kg_selection/scripts/probe_coverage.py

Neo4j must be reachable (same .env as the MCP server).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import (
    gene_clusters_by_gene,
    gene_derived_metrics,
    gene_homologs,
    gene_neighbors,
    gene_ontology_terms,
    gene_overview,
    genes_by_homolog_group,
    to_dataframe,
)

DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)

# driving genes
DARK = ["PMM0872", "PMM1028", "PMM0983", "PMM1683"]
CONTROL = ["PMM1436"]
ALL_GENES = DARK + CONTROL
DARK_OGS = ["cyanorak:CK_00000141", "cyanorak:CK_00003473", "cyanorak:CK_00000498"]


def _frame(result) -> pd.DataFrame:
    """Flatten a result to a DataFrame, preferring the package converter."""
    try:
        df = to_dataframe(result)
        if isinstance(df, pd.DataFrame) and len(df.columns):
            return df
    except Exception:
        pass
    return pd.DataFrame(result.get("results", []))


def dump(name: str, result, df: pd.DataFrame) -> None:
    (DATA / f"probe_{name}.json").write_text(
        json.dumps(result, indent=2, default=str), encoding="utf-8")
    df.to_csv(DATA / f"probe_{name}.csv", index=False)
    print(f"[{name:12s}] rows={len(df):3d}  cols={len(df.columns)}  "
          f"-> data/probe_{name}.csv")


def main() -> None:
    # 1. members of the dark OGs (cyanorak)
    members = genes_by_homolog_group(group_ids=DARK_OGS, verbose=True, limit=None)
    dump("members", members, _frame(members))

    # 2. cross-organism reach via eggnog (genera / has_cross_genus_members)
    homologs = gene_homologs(locus_tags=ALL_GENES, source="eggnog",
                             verbose=True, limit=None)
    dump("homologs_eggnog", homologs, _frame(homologs))

    # 3. data-availability triage across every angle in one call
    overview = gene_overview(locus_tags=ALL_GENES, verbose=True)
    dump("overview", overview, _frame(overview))

    # 4. genomic neighborhood (MED4)
    neighbors = gene_neighbors(locus_tags=ALL_GENES, window=3, limit=None)
    dump("neighbors", neighbors, _frame(neighbors))

    # 5. ontology / domains / sequence features
    ontology = gene_ontology_terms(locus_tags=ALL_GENES, organism="MED4", limit=None)
    dump("ontology", ontology, _frame(ontology))

    # 6. co-expression cluster membership
    clusters = gene_clusters_by_gene(locus_tags=ALL_GENES, verbose=True, limit=None)
    dump("clusters", clusters, _frame(clusters))

    # 7. derived metrics
    metrics = gene_derived_metrics(locus_tags=ALL_GENES, verbose=True, limit=None)
    dump("metrics", metrics, _frame(metrics))

    print("\nDriving genes:", ", ".join(ALL_GENES))
    print("Coverage findings summarized in ../data/coverage_map.csv and the notebook.")


if __name__ == "__main__":
    main()
