"""
Step 3 (framing) — control-suite validation. Pull per-strain gene counts for the
phosphorus role and its control categories across the 9-strain panel, so the
framing's controls are validated (distribution, ecotype behavior) before the
proposal is locked.

Categories (Cyanorak roles):
  D.1.5  Phosphorus            — the target adaptation category
  D.1.3  Nitrogen              — specificity control (sibling adaptation role)
  D.1.7  Trace metals          — specificity control (sibling adaptation role)
  D.1.2  Light                 — POSITIVE control: HL/LL are defined by light niche,
                                 so this category SHOULD differ by ecotype
  K.2    Ribosomal proteins    — INVARIANT baseline: core housekeeping, expect ~equal

Input:  ../2_kg_entries/data/strain_panel.csv (panel + genome sizes)
Output: data/control_categories_by_strain.csv, data/01_control_categories.log
Run:    uv run python analyses/2026-06-13-ll_vs_hl_p_capacity/3_framing/scripts/01_control_categories.py
"""
from __future__ import annotations

import csv
from pathlib import Path

from multiomics_explorer import genes_by_ontology, GraphConnection

STEP_DIR = Path(__file__).resolve().parents[1]
DATA = STEP_DIR / "data"
DATA.mkdir(parents=True, exist_ok=True)
PANEL = STEP_DIR.parent / "2_kg_entries" / "data" / "strain_panel.csv"

ROLES = [
    ("D.1.5_phosphorus", "cyanorak.role:D.1.5"),
    ("D.1.3_nitrogen",   "cyanorak.role:D.1.3"),
    ("D.1.7_trace_metal", "cyanorak.role:D.1.7"),
    ("D.1.2_light",      "cyanorak.role:D.1.2"),
    ("K.2_ribosomal",    "cyanorak.role:K.2"),
]

log_lines: list[str] = []
def log(m: str) -> None:
    print(m); log_lines.append(m)


def main() -> None:
    strains = []
    with PANEL.open() as fh:
        for r in csv.DictReader(fh):
            strains.append((r["ecotype"], r["clade"], r["strain"],
                            r["organism_name"], int(r["genome_gene_count"])))

    rows = []
    with GraphConnection() as conn:
        for ecotype, clade, strain, org, gsize in strains:
            rec = {"ecotype": ecotype, "clade": clade, "strain": strain,
                   "organism_name": org, "genome_gene_count": gsize}
            for label, term in ROLES:
                resp = genes_by_ontology(ontology="cyanorak_role", term_ids=[term],
                                         organism=org, min_gene_set_size=1,
                                         summary=True, limit=None, conn=conn)
                n = resp.get("total_genes", 0)
                rec[f"{label}_n"] = n
                rec[f"{label}_per1k"] = round(1000 * n / gsize, 3) if gsize else None
            rows.append(rec)
            log(f"{ecotype}/{clade:5s} {strain:8s} " +
                " ".join(f"{lab.split('_')[0]}={rec[lab+'_n']}" for lab, _ in ROLES))

    cols = (["ecotype", "clade", "strain", "organism_name", "genome_gene_count"] +
            [f"{lab}_n" for lab, _ in ROLES] + [f"{lab}_per1k" for lab, _ in ROLES])
    out = DATA / "control_categories_by_strain.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader(); w.writerows(rows)

    # ecotype means + LL/HL ratio per category (raw count and per-1000)
    def mean(vals): return sum(vals) / len(vals)
    hl = [r for r in rows if r["ecotype"] == "HL"]
    ll = [r for r in rows if r["ecotype"] == "LL"]
    log("")
    log(f"{'category':18s} {'HL_n':>6s} {'LL_n':>6s} {'LL/HL_n':>8s} {'HL_p1k':>7s} {'LL_p1k':>7s} {'LL/HL_p1k':>9s}")
    for lab, _ in ROLES:
        hn, ln = mean([r[f"{lab}_n"] for r in hl]), mean([r[f"{lab}_n"] for r in ll])
        hp, lp = mean([r[f"{lab}_per1k"] for r in hl]), mean([r[f"{lab}_per1k"] for r in ll])
        log(f"{lab:18s} {hn:6.1f} {ln:6.1f} {ln/hn:8.3f} {hp:7.2f} {lp:7.2f} {lp/hp:9.3f}")
    log("")
    log(f"[outputs] {out.relative_to(STEP_DIR)} ({len(rows)} rows)")
    (DATA / "01_control_categories.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
