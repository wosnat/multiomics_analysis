"""
Step 2 (KG entries, REDONE 2026-06-15) — full Alteromonas experiment inventory
across ALL strains, annotated for the carbon-provision reframe.

Reframe context (see 3_framing/notebook.md): the common lens is
coculture-with-Prochlorococcus vs axenic. In these media there is no added
organic carbon, so Prochlorococcus photosynthate is Alteromonas's only organic-C
source — coculture vs axenic is close to organic-C-fed vs starved. Motility
(flagella + chemotaxis) is the lead readout. Other contrasts (nutrient, carbon /
glucose, darkness, pCO2, Synechococcus partner) are controls.

This script freezes two things:
  1. The annotated experiment inventory, with two judgment-relevant annotations
     computed reproducibly (not asserted from chat):
       - added_organic_c   : rule-based from medium recipe / treatment tokens
       - direction_quality : from the log2FC sign distribution over ALL rows.
         A genuine all-genes DE table is ~symmetric around 0 (~40-55% negative).
         0% negative across all detected genes (incl. non-significant) == the sign
         was lost at ingestion -> direction UNUSABLE. (significant_only tables keep
         the sign but lack an all-genes background -> direction-only, no ORA.)
  2. The motility gene sets (KEGG flagella ko02040 + chemotaxis ko02030 primary;
     broad eggNOG COG category N sensitivity) for the strains with >=1 usable
     DE experiment.

Outputs (relative to step folder):
  data/experiment_inventory.csv   one row per Alteromonas experiment, annotated
  data/motility_genes.csv         per (strain x gene): in KEGG set / in COG-N set
  data/01_extract_entries.log
Run: uv run python analyses/2026-06-15-alteromonas_motility_coculture/2_kg_entries/scripts/01_extract_entries.py
"""
from __future__ import annotations

import csv
from pathlib import Path

from multiomics_explorer import (
    list_experiments,
    differential_expression_by_gene,
    genes_by_ontology,
    GraphConnection,
)

STEP = Path(__file__).resolve().parents[1]
DATA = STEP / "data"; DATA.mkdir(parents=True, exist_ok=True)
log_lines: list[str] = []
def log(m): print(m); log_lines.append(m)

ORGANISM_FILTER = "Alteromonas"

# --- organic-carbon classification ([interpretation], rule-based + transparent) ---
# Reduced/organic carbon supplied either in the medium recipe OR as the
# experimental treatment (e.g. a glucose amendment named in the experiment id).
ORGANIC_C_TOKENS = ["glucose", "lactate", "pyruvate", "acetate", "glycerol"]
def classify_organic_c(medium: str, exp_id: str, treatment: str) -> str:
    hay = " ".join([medium or "", exp_id or "", treatment or ""]).lower()
    if any(tok in hay for tok in ORGANIC_C_TOKENS):
        return "yes"          # organic C present (medium recipe or treatment)
    if "natural seawater" in (medium or "").lower():
        return "background"   # natural-seawater DOC; none deliberately added
    return "no"               # defined inorganic medium (Pro99 / SN / PEv ASW)

# --- data-quality flag from the log2FC sign distribution ([KG], computed) ---------
# 0% negative is only diagnostic of corruption when there are enough genes to judge;
# a handful of all-positive rows is sparse data, not a stripped sign.
MIN_GENES_FOR_SIGN_CHECK = 50
def direction_quality(neg: int, total: int, scope: str) -> str:
    if total == 0:
        return "no_de_edges"          # vesicle/compartment etc. — no DE edges
    if neg == 0 and total >= MIN_GENES_FOR_SIGN_CHECK:
        return "sign_lost"            # corrupted: 0% negative over many genes -> unusable
    if neg == 0:
        return "sparse"               # too few rows to judge direction (all-positive by chance)
    if scope == "all_detected_genes":
        return "ok_all_genes"         # both directions + valid all-genes ORA background
    return "ok_significant_only"      # direction readable, but no ORA background

def strain_of(organism_name: str) -> str:
    if "MarRef" in organism_name:
        return "MarRef"
    return organism_name.split()[-1]  # ...HOT1A3 / EZ55 / MIT1002 / BS11 ...

def partner_genus(partner: str) -> str:
    p = partner or ""
    if "Prochl" in p: return "Prochlorococcus"
    if "Synech" in p: return "Synechococcus"
    return ""

# strains carrying >=1 usable DE experiment — motility sets extracted for these
MOTILITY_STRAINS = [
    ("HOT1A3", "Alteromonas macleodii HOT1A3"),
    ("EZ55",   "Alteromonas macleodii EZ55"),
    ("MIT1002","Alteromonas macleodii MIT1002"),
]
KEGG_MOTILITY = ["kegg.pathway:ko02040", "kegg.pathway:ko02030"]
COG_MOTILITY = ["cog.category:N"]


def ontology_locus_set(ontology, term_ids, organism, conn) -> dict[str, dict]:
    r = genes_by_ontology(ontology=ontology, term_ids=term_ids, organism=organism,
                          min_gene_set_size=1, limit=None, conn=conn)
    return {row["locus_tag"]: {"gene_name": row.get("gene_name"),
                               "product": row.get("product")}
            for row in r.get("results", [])}


def main() -> None:
    exp_rows, gene_rows = [], []
    with GraphConnection() as conn:
        exps = list_experiments(organism=ORGANISM_FILTER, limit=None,
                                verbose=True, conn=conn)
        results = exps.get("results", [])
        log(f"[inventory] {len(results)} Alteromonas experiments")

        for e in results:
            eid = e["experiment_id"]
            scope = e.get("table_scope")
            # log2FC sign distribution over ALL rows (incl. non-significant)
            de = differential_expression_by_gene(experiment_ids=[eid], limit=None,
                                                  conn=conn)
            rows = de.get("results", [])
            neg = sum(1 for r in rows if (r.get("log2fc") or 0) < 0)
            pos = sum(1 for r in rows if (r.get("log2fc") or 0) > 0)
            total = len(rows)
            by_status = de.get("rows_by_status", {}) or {}
            de_exps = de.get("experiments") or []
            n_tp = len(de_exps[0].get("timepoints") or []) if de_exps else 0
            partner = e.get("coculture_partner") or ""
            tt = e.get("treatment_type")
            tt = ",".join(tt) if isinstance(tt, list) else (tt or "")
            exp_rows.append({
                "strain": strain_of(e.get("organism_name", "")),
                "organism_name": e.get("organism_name"),
                "experiment_id": eid,
                "publication_doi": e.get("publication_doi"),
                "omics_type": e.get("omics_type"),
                "table_scope": scope,
                "is_time_course": e.get("is_time_course"),
                "n_timepoints": n_tp,
                "growth_phases": ";".join(e.get("growth_phases") or []),
                "treatment_type": tt,
                "treatment": e.get("treatment"),
                "coculture_partner": partner,
                "partner_genus": partner_genus(partner),
                "prochlorococcus_coculture": int(partner_genus(partner) == "Prochlorococcus"),
                "medium": e.get("medium"),
                "added_organic_c": classify_organic_c(e.get("medium"), eid, e.get("treatment")),
                "sig_up": by_status.get("significant_up", 0),
                "sig_down": by_status.get("significant_down", 0),
                "neg_l2fc": neg,
                "pos_l2fc": pos,
                "total_l2fc": total,
                "pct_neg": (round(100.0 * neg / total, 1) if total else None),
                "direction_quality": direction_quality(neg, total, scope),
            })

        # motility gene sets for the usable strains
        for short, full in MOTILITY_STRAINS:
            kegg = ontology_locus_set("kegg", KEGG_MOTILITY, full, conn)
            cog = ontology_locus_set("cog_category", COG_MOTILITY, full, conn)
            for t in sorted(set(kegg) | set(cog)):
                meta = kegg.get(t) or cog.get(t)
                gene_rows.append({
                    "strain": short, "locus_tag": t,
                    "gene_name": meta.get("gene_name"), "product": meta.get("product"),
                    "in_kegg_flagella_chemotaxis": int(t in kegg),
                    "in_cog_n_cell_motility": int(t in cog),
                })
            log(f"[motility {short}] KEGG={len(kegg)} COG-N={len(cog)} union={len(set(kegg)|set(cog))}")

    # write inventory
    inv = DATA / "experiment_inventory.csv"
    with inv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(exp_rows[0].keys()))
        w.writeheader(); w.writerows(exp_rows)
    mot = DATA / "motility_genes.csv"
    with mot.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gene_rows[0].keys()))
        w.writeheader(); w.writerows(gene_rows)

    # console summary by data-quality and lens
    log("")
    log("[direction_quality counts]")
    for q in ("ok_all_genes", "ok_significant_only", "sign_lost", "sparse", "no_de_edges"):
        log(f"  {q:22s} {sum(1 for r in exp_rows if r['direction_quality']==q)}")
    log("")
    log("[Prochlorococcus-coculture experiments]")
    for r in sorted([r for r in exp_rows if r["prochlorococcus_coculture"]],
                    key=lambda r: (r["direction_quality"], r["strain"])):
        log(f"  {r['strain']:8s} {r['omics_type']:11s} {r['table_scope']:22s} "
            f"organicC={r['added_organic_c']:10s} {r['direction_quality']:20s} "
            f"up/down={r['sig_up']}/{r['sig_down']} pct_neg={r['pct_neg']} | {r['coculture_partner']}")
    log(f"\n[outputs] {inv.name} ({len(exp_rows)}), {mot.name} ({len(gene_rows)})")
    (DATA / "01_extract_entries.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
