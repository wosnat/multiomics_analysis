"""
QC (step 2) — freeze the gene-set-handle coverage comparison that motivated
choosing the Cyanorak curated role over GO/KEGG. For the two exemplar ecotypes
(MED4 = HL, MIT9313 = LL), count P genes captured by each candidate handle and
record which core P-acquisition genes each captures.

Conclusion (see notebook): GO is precise but far too sparse in this KG — it tags
only the Pst transporter and misses phosphonate/regulator/phosphatase machinery.
Cyanorak D.1.5 is comprehensive (curated for these organisms) but broad.

Output: data/qc_ontology_coverage.csv
Run:    uv run python analyses/2026-06-13-ll_vs_hl_p_capacity/2_kg_entries/scripts/qc_ontology_coverage.py
"""
from __future__ import annotations

import csv
from pathlib import Path

from multiomics_explorer import genes_by_ontology, GraphConnection

STEP_DIR = Path(__file__).resolve().parents[1]
DATA = STEP_DIR / "data"

EXEMPLARS = [("HL", "MED4", "Prochlorococcus MED4"),
             ("LL", "MIT9313", "Prochlorococcus MIT9313")]

HANDLES = {
    "cyanorak_D.1.5": ("cyanorak_role", ["cyanorak.role:D.1.5"]),
    "GO_BP_phosphate": ("go_bp", ["go:0006817", "go:0016036", "go:0035435",
                                   "go:0055062", "go:0010966"]),
    "GO_MF_phosphate": ("go_mf", ["go:0004035", "go:0005315", "go:0015415",
                                   "go:0042301", "go:0015416", "go:0050609"]),
}

# Core P-acquisition machinery to check capture against (by gene_name).
CORE = ["pstS", "pstC", "pstA", "pstB", "phnC", "phnD", "phnE", "phoB", "phoR", "phoH"]


def fetch(ontology: str, term_ids: list[str], organism: str, conn) -> dict[str, str]:
    """Return {locus_tag: gene_name} for genes under the given terms."""
    resp = genes_by_ontology(ontology=ontology, term_ids=term_ids, organism=organism,
                             min_gene_set_size=1, limit=None, conn=conn)
    return {r["locus_tag"]: (r.get("gene_name") or "") for r in resp.get("results", [])}


def main() -> None:
    rows = []
    with GraphConnection() as conn:
        for ecotype, strain, org in EXEMPLARS:
            for handle, (ont, terms) in HANDLES.items():
                genes = fetch(ont, terms, org, conn)
                names = {n for n in genes.values() if n}
                core_hit = sorted(g for g in CORE if g in names)
                rows.append({
                    "ecotype": ecotype, "strain": strain, "handle": handle,
                    "n_genes": len(genes),
                    "n_core_acquisition_captured": len(core_hit),
                    "core_captured": "|".join(core_hit),
                    "core_missed": "|".join(g for g in CORE if g not in names),
                })
                print(f"{ecotype} {strain:8s} {handle:16s} n_genes={len(genes):3d} "
                      f"core={len(core_hit)}/{len(CORE)} ({','.join(core_hit)})")

    out = DATA / "qc_ontology_coverage.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"[outputs] {out.relative_to(STEP_DIR)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
