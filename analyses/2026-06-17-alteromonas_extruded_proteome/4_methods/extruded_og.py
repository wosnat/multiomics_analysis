"""extruded_og — map Alteromonas "measured-extruded" genes to ortholog groups.

Purpose
-------
Build a catalogue of ortholog groups (OGs) whose members are measured leaving an
Alteromonas cell, combining two routes that the KG measures on disjoint strains:

  * secreted  — EZ55 exoproteome; gene is extruded if
                exoproteome_detection_replicates >= 1 (the metric is
                tested-absent: edges with value 0 were looked for, not detected).
  * vesicle   — 6-strain membrane-vesicle (MV) proteomes; gene is extruded if it
                is present in the strain's MV-cargo list (has prop_abund_mvs_percent).

The combining unit is the eggnog ortholog group at the most-specific
(Alteromonadaceae) level — verified in step 3 to bridge the 7 A. macleodii strains.

Inputs : KG (multiomics-kg) via the multiomics_explorer Python API.
Outputs: pandas DataFrames (gene-level extrusion table; OG-level catalogue).

Functions
---------
extract_route_genes(strain, route, conn)  -> DataFrame[locus_tag, strain, route, product, value]
map_genes_to_og(locus_tags, conn)         -> DataFrame[locus_tag, og_group_id, og_level, og_product]
build_og_catalogue(gene_og_df)            -> DataFrame[og_group_id ... routes, n_strains, locus_tags]

Driving example (step 4): MIT1002 vesicle only. Generalized to all 7 in step 5.
"""

from __future__ import annotations

import pandas as pd

from multiomics_explorer import genes_by_numeric_metric, gene_homologs


# Route -> how "measured leaving the cell" is defined in KG terms.
ROUTE_CONFIG = {
    "vesicle": {
        "metric_types": ["prop_abund_mvs_percent"],
        "compartment": "vesicle",
        "min_value": None,  # membership = has an MV-abundance edge
    },
    "secreted": {
        "metric_types": ["exoproteome_detection_replicates"],
        "compartment": "exoproteome",
        "min_value": 1.0,   # tested-absent metric: require detection in >=1 subline
    },
}


def extract_route_genes(strain: str, route: str, conn=None) -> pd.DataFrame:
    """Return genes from `strain` measured extruded via `route` (one row per gene)."""
    cfg = ROUTE_CONFIG[route]
    res = genes_by_numeric_metric(
        metric_types=cfg["metric_types"],
        organism=strain,
        compartment=cfg["compartment"],
        min_value=cfg["min_value"],
        limit=None,
        conn=conn,
    )
    rows = [
        {
            "locus_tag": r["locus_tag"],
            "strain": r["organism_name"],
            "route": route,
            "product": r.get("product"),
            "value": r.get("value"),
        }
        for r in res["results"]
    ]
    return pd.DataFrame(rows, columns=["locus_tag", "strain", "route", "product", "value"])


def map_genes_to_og(locus_tags: list[str], conn=None) -> pd.DataFrame:
    """Map each locus tag to its most-specific eggnog OG (Alteromonadaceae level).

    gene_homologs returns rows ordered most-specific first; we keep the lowest
    specificity_rank per gene. Genes with no eggnog group (strain-unique) are
    reported with og_group_id = None.
    """
    if not locus_tags:
        return pd.DataFrame(
            columns=["locus_tag", "og_group_id", "og_level", "og_product"]
        )
    res = gene_homologs(locus_tags=locus_tags, source="eggnog", limit=None, conn=conn)
    best: dict[str, dict] = {}
    for r in res["results"]:
        lt = r["locus_tag"]
        rank = r.get("specificity_rank", 99)
        if lt not in best or rank < best[lt]["specificity_rank"]:
            best[lt] = r
    rows = []
    for lt in locus_tags:
        r = best.get(lt)
        rows.append(
            {
                "locus_tag": lt,
                "og_group_id": r["group_id"] if r else None,
                "og_level": r["taxonomic_level"] if r else None,
                "og_product": (r.get("consensus_product") if r else None),
            }
        )
    return pd.DataFrame(rows, columns=["locus_tag", "og_group_id", "og_level", "og_product"])


def build_og_catalogue(gene_og_df: pd.DataFrame) -> pd.DataFrame:
    """Collapse a gene-level extrusion+OG table to one row per ortholog group.

    Expects columns: locus_tag, strain, route, product, og_group_id, og_level,
    og_product. Genes with no OG (og_group_id NaN) are dropped from the OG
    catalogue and should be reported separately as strain-unique.
    """
    df = gene_og_df.dropna(subset=["og_group_id"]).copy()

    def _agg(g: pd.DataFrame) -> pd.Series:
        routes = sorted(g["route"].unique())
        strains = sorted(g["strain"].unique())
        return pd.Series(
            {
                "og_product": g["og_product"].dropna().iloc[0]
                if g["og_product"].notna().any()
                else None,
                "routes": ";".join(routes),
                "both_routes": len(routes) == 2,
                "n_strains": g["strain"].nunique(),
                "strains": ";".join(s.replace("Alteromonas macleodii ", "") for s in strains),
                "n_genes": len(g),
                "locus_tags": ";".join(sorted(g["locus_tag"])),
            }
        )

    cat = df.groupby("og_group_id", sort=False).apply(_agg).reset_index()
    # Most recurrent / both-routes first.
    cat = cat.sort_values(
        ["both_routes", "n_strains", "n_genes"], ascending=False
    ).reset_index(drop=True)
    return cat
