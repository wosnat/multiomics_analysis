"""
Step 4 (Methods, redone 2026-06-15) — the per-contrast method, built on the
driving example (HOT1A3 coculture-with-MED4 vs axenic, day-11 exponential).

No custom statistics: the method IS the package's `pathway_enrichment` (one-sided
Fisher per pathway, per-cluster table_scope background, up/down split, BH) — see
the earlier reinvented-ORA friction note. This module is a thin, reusable driver
that (a) runs enrichment at two granularities and (b) pulls the motility gene-level
readout, then FREEZES both to CSV so step 5 can reuse `run_contrast` across all
usable contrasts.

Two granularities (chosen via ontology_landscape, step-4 notebook):
  - KEGG level 2 (pathways): fine, interpretable — motility (ko02040/ko02030),
    glycolysis, TCA, carbon metabolism. Coverage ~0.31 of the genome (caveat).
  - COG category level 0: coarse functional overview, coverage ~0.69.
Motility gene-level readout: per-gene log2FC/status for the KEGG flagella+chemotaxis
set, the carbon-provision lead readout.

Outputs (relative to step folder), per contrast `label`:
  data/{label}_kegg_l2_enrichment.csv
  data/{label}_cog_l0_enrichment.csv
  data/{label}_motility_genes_de.csv
  data/01_method.log
Run: uv run python analyses/2026-06-15-alteromonas_motility_coculture/4_methods/scripts/01_method.py
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from multiomics_explorer import (
    pathway_enrichment,
    differential_expression_by_gene,
    to_dataframe,
    GraphConnection,
)

STEP = Path(__file__).resolve().parents[1]
DATA = STEP / "data"; DATA.mkdir(parents=True, exist_ok=True)
MOTILITY_CSV = STEP.parent / "2_kg_entries" / "data" / "motility_genes.csv"

log_lines: list[str] = []
def log(m): print(m); log_lines.append(m)

ENRICH_COLS = ["cluster", "direction", "timepoint", "term_id", "term_name",
               "count", "bg_count", "gene_ratio", "fold_enrichment",
               "pvalue", "p_adjust", "signed_score"]


def motility_tags(strain: str, which: str = "in_kegg_flagella_chemotaxis") -> list[str]:
    """Locus tags of the motility set for a strain (default: KEGG flagella+chemotaxis)."""
    m = pd.read_csv(MOTILITY_CSV)
    return m[(m["strain"] == strain) & (m[which] == 1)]["locus_tag"].tolist()


def run_contrast(label: str, organism: str, experiment_ids: list[str],
                 strain: str, *, conn, outdir: Path = DATA) -> dict:
    """Run the per-contrast method: KEGG-L2 + COG-L0 enrichment + motility
    gene-level readout. Freezes three CSVs prefixed by `label` into `outdir`
    (default: this step's data/). Returns a small summary dict for the notebook.
    `outdir` lets later steps reuse this exact method into their own folder."""
    outdir.mkdir(parents=True, exist_ok=True)
    out = {"label": label}

    # (1) + (2) pathway enrichment at two granularities
    for oname, ont, level in [("kegg_l2", "kegg", 2), ("cog_l0", "cog_category", 0)]:
        res = pathway_enrichment(organism=organism, experiment_ids=experiment_ids,
                                 ontology=ont, level=level, direction="both", conn=conn)
        df = res.results
        keep = [c for c in ENRICH_COLS if c in df.columns]
        df[keep].sort_values("p_adjust").to_csv(outdir / f"{label}_{oname}_enrichment.csv", index=False)
        n_sig = int((df["p_adjust"] < 0.05).sum())
        out[f"{oname}_tests"] = len(df); out[f"{oname}_sig"] = n_sig
        log(f"[{label}/{oname}] {len(df)} tests, {n_sig} significant (p_adjust<0.05)")

    # (3) motility gene-level readout (KEGG flagella+chemotaxis set)
    tags = motility_tags(strain)
    de = differential_expression_by_gene(organism=organism, locus_tags=tags,
                                          experiment_ids=experiment_ids, verbose=True, conn=conn)
    mdf = to_dataframe(de)
    mcols = [c for c in ["locus_tag", "gene_name", "product", "timepoint", "log2fc",
                         "padj", "expression_status", "experiment_id"] if c in mdf.columns]
    (mdf[mcols] if len(mdf) else mdf).to_csv(outdir / f"{label}_motility_genes_de.csv", index=False)
    by_status = (mdf["expression_status"].value_counts().to_dict() if "expression_status" in mdf else {})
    out["motility_n"] = len(tags); out["motility_rows"] = len(mdf); out["motility_by_status"] = by_status
    log(f"[{label}/motility] {len(tags)} genes in set, {len(mdf)} DE rows, by_status={by_status}")
    return out


def main() -> None:
    # Driving example: HOT1A3 coculture-with-MED4 vs axenic, day-11 exponential.
    with GraphConnection() as conn:
        summary = run_contrast(
            label="med4_snapshot",
            organism="HOT1A3",
            experiment_ids=["10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq"],
            strain="HOT1A3",
            conn=conn,
        )
    log("")
    log(f"[summary] {summary}")
    (DATA / "01_method.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
