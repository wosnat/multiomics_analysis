"""
Step 4 methods module — genomic P-acquisition capacity metric.

Reusable gene-set operation for the LL-vs-HL comparison: from a long
(strain x gene) table restricted to a focused ortholog-group (OG) subset, build
a strain x OG presence/absence matrix and summarize capacity per ecotype.

Capacity (locked step 3): per-strain count of distinct focused-acquisition OGs
present; ecotype comparison via raw-count LL/HL ratio (benchmarked against
control categories in the analysis scripts); plus the presence/absence
repertoire (which OGs are LL-only / HL-only / universal / variable).

Pure pandas; no KG access (callers pass the frozen step-2/step-3 tables). Toy-
verified in scripts/qc_toy_verification.py (see 4_methods/notebook.md).
"""
from __future__ import annotations

import pandas as pd


def build_presence_matrix(genes: pd.DataFrame, *, og_col: str = "cyanorak_og",
                          strain_col: str = "strain",
                          meta_cols: tuple[str, ...] = ("ecotype", "clade")
                          ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Strain x OG presence/absence (1/0) matrix + per-strain metadata.

    A strain "has" an OG if >=1 of its genes maps to that OG (paralogs collapse
    to presence=1 — capacity is repertoire, not copy number).
    """
    pres = (genes[[strain_col, og_col]].drop_duplicates()
            .assign(present=1)
            .pivot(index=strain_col, columns=og_col, values="present")
            .fillna(0).astype(int))
    meta = (genes[[strain_col, *meta_cols]].drop_duplicates()
            .set_index(strain_col).reindex(pres.index))
    return pres, meta


def per_strain_counts(matrix: pd.DataFrame, meta: pd.DataFrame,
                      genome_size: pd.Series | None = None) -> pd.DataFrame:
    """Per-strain count of OGs present (+ per-1000-genes if genome_size given)."""
    out = meta.copy()
    out["n_ogs"] = matrix.sum(axis=1)
    if genome_size is not None:
        out["genome_gene_count"] = genome_size.reindex(out.index)
        out["per1k"] = (1000 * out["n_ogs"] / out["genome_gene_count"]).round(3)
    return out


def ecotype_ratio(counts: pd.DataFrame, *, ecotype_col: str = "ecotype",
                  value_col: str = "n_ogs",
                  hl: str = "HL", ll: str = "LL") -> dict:
    """HL/LL means (+ medians) of a per-strain value and the LL/HL ratio."""
    g = counts.groupby(ecotype_col)[value_col]
    hl_mean, ll_mean = g.mean().get(hl), g.mean().get(ll)
    return {
        "hl_mean": hl_mean, "ll_mean": ll_mean,
        "hl_median": g.median().get(hl), "ll_median": g.median().get(ll),
        "ll_over_hl": (ll_mean / hl_mean) if hl_mean else None,
        "n_hl": int((counts[ecotype_col] == hl).sum()),
        "n_ll": int((counts[ecotype_col] == ll).sum()),
    }


def differential_presence(matrix: pd.DataFrame, meta: pd.DataFrame, *,
                          ecotype_col: str = "ecotype",
                          hl: str = "HL", ll: str = "LL") -> pd.DataFrame:
    """Per-OG presence counts per ecotype + a repertoire category.

    Categories: universal (in every HL and every LL), LL_only (>=1 LL, 0 HL),
    HL_only (>=1 HL, 0 LL), variable (present in both ecotypes but not all
    strains of one).
    """
    hl_strains = meta.index[meta[ecotype_col] == hl]
    ll_strains = meta.index[meta[ecotype_col] == ll]
    n_hl, n_ll = len(hl_strains), len(ll_strains)

    n_hl_present = matrix.loc[hl_strains].sum(axis=0)
    n_ll_present = matrix.loc[ll_strains].sum(axis=0)

    def cat(a: int, b: int) -> str:
        if a == n_hl and b == n_ll:
            return "universal"
        if a == 0 and b > 0:
            return "LL_only"
        if b == 0 and a > 0:
            return "HL_only"
        return "variable"

    return (pd.DataFrame({"n_HL": n_hl_present, "n_LL": n_ll_present})
            .assign(category=lambda d: [cat(a, b) for a, b in zip(d.n_HL, d.n_LL)])
            .sort_values(["category", "n_HL", "n_LL"]))
