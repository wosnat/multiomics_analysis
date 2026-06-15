"""
Step 2 (KG entries) — freeze the inputs for the coculture-vs-alone motility
comparison: the experiments and the motility gene sets, for HOT1A3 + EZ55.

Gene-set definitions (agreed step-2 dialogue):
  primary  = KEGG flagellar assembly (ko02040) + bacterial chemotaxis (ko02030)
  sensitivity = eggNOG COG category N "Cell motility" (broad: + pili/twitching)

Experiments: coculture-with-Prochlorococcus vs alone (axenic). EZ55 also has
coculture-with-Synechococcus contrasts — captured separately as a potential
"partner-specificity" control for step 3.

Outputs (relative to step folder):
  data/coculture_experiments.csv   the DE experiments (id, partner, control, omics, scope)
  data/motility_genes.csv          per (strain x gene): in KEGG set / in COG-N set
  data/01_extract_entries.log
Run: uv run python analyses/2026-06-15-alteromonas_motility_coculture/2_kg_entries/scripts/01_extract_entries.py
"""
from __future__ import annotations

import csv
from pathlib import Path

from multiomics_explorer import list_experiments, genes_by_ontology, GraphConnection

STRAINS = [("HOT1A3", "Alteromonas macleodii HOT1A3"),
           ("EZ55", "Alteromonas macleodii EZ55")]
KEGG_MOTILITY = ["kegg.pathway:ko02040", "kegg.pathway:ko02030"]
COG_MOTILITY = ["cog.category:N"]

STEP = Path(__file__).resolve().parents[1]
DATA = STEP / "data"; DATA.mkdir(parents=True, exist_ok=True)
log_lines: list[str] = []
def log(m): print(m); log_lines.append(m)


def ontology_locus_set(ontology, term_ids, organism, conn) -> dict[str, dict]:
    r = genes_by_ontology(ontology=ontology, term_ids=term_ids, organism=organism,
                          min_gene_set_size=1, limit=None, conn=conn)
    out = {}
    for row in r.get("results", []):
        out[row["locus_tag"]] = {"gene_name": row.get("gene_name"),
                                 "product": row.get("product")}
    return out


def main() -> None:
    exp_rows, gene_rows = [], []
    with GraphConnection() as conn:
        for short, full in STRAINS:
            cc = list_experiments(organism=full, treatment_type=["coculture"],
                                  verbose=True, limit=None, conn=conn)
            for e in cc.get("results", []):
                partner = e.get("coculture_partner") or ""
                exp_rows.append({
                    "strain": short, "experiment_id": e["experiment_id"],
                    "coculture_partner": partner,
                    "partner_genus": "Prochlorococcus" if "Prochl" in partner
                                     else ("Synechococcus" if "Synech" in partner else "other"),
                    "omics_type": e.get("omics_type"), "table_scope": e.get("table_scope"),
                    "treatment": e.get("treatment"), "control": e.get("control"),
                    "publication_doi": e.get("publication_doi"),
                })

            kegg = ontology_locus_set("kegg", KEGG_MOTILITY, full, conn)
            cog = ontology_locus_set("cog_category", COG_MOTILITY, full, conn)
            all_tags = sorted(set(kegg) | set(cog))
            for t in all_tags:
                meta = kegg.get(t) or cog.get(t)
                gene_rows.append({
                    "strain": short, "locus_tag": t,
                    "gene_name": meta.get("gene_name"), "product": meta.get("product"),
                    "in_kegg_flagella_chemotaxis": int(t in kegg),
                    "in_cog_n_cell_motility": int(t in cog),
                })
            log(f"[{short}] coculture experiments={len(cc.get('results', []))}; "
                f"KEGG motility genes={len(kegg)}; COG-N motility genes={len(cog)}; "
                f"union={len(all_tags)}; KEGG-only={len(set(kegg)-set(cog))}; "
                f"COG-only={len(set(cog)-set(kegg))}")

    with (DATA / "coculture_experiments.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(exp_rows[0].keys())); w.writeheader(); w.writerows(exp_rows)
    with (DATA / "motility_genes.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gene_rows[0].keys())); w.writeheader(); w.writerows(gene_rows)

    # coculture-vs-axenic (Prochlorococcus partner) — the primary contrasts
    log("")
    log("[primary contrasts: coculture-with-Prochlorococcus vs alone]")
    for r in exp_rows:
        if r["partner_genus"] == "Prochlorococcus" and "axen" in (r["control"] or "").lower() + (r["treatment"] or "").lower() or \
           (r["partner_genus"] == "Prochlorococcus"):
            pass
    proc = [r for r in exp_rows if r["partner_genus"] == "Prochlorococcus"]
    syn = [r for r in exp_rows if r["partner_genus"] == "Synechococcus"]
    for r in proc:
        log(f"  {r['strain']:7s} {r['omics_type']:8s} {r['table_scope']:22s} {r['treatment'][:32]:32s} | {r['control'][:30]}")
    log(f"[control candidates: coculture-with-Synechococcus] {len(syn)} experiments (EZ55)")
    log(f"\n[outputs] coculture_experiments.csv ({len(exp_rows)}), motility_genes.csv ({len(gene_rows)})")
    (DATA / "01_extract_entries.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
