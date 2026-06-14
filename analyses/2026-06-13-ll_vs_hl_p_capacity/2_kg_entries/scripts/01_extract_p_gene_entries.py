"""
Step 2 (KG entries) — extract the phosphorus-adaptation gene set across the
(dogfood-restricted) Prochlorococcus genome-strain panel, grouped HL vs LL,
each gene mapped to its most-specific curated Cyanorak ortholog group (the
cross-strain comparison unit).

Gene-set handle (locked step-2 dialogue): curated Cyanorak role
`cyanorak.role:D.1.5` ("...Adaptation/acclimation... > Phosphorus"), FULL role
(the focused acquisition subset is a step-3 decision, not applied here).

PANEL — dogfood scope decision (2026-06-13): the ideal panel is all
Cyanorak-annotated genome strains (17: 9 HL, 8 LL). But genes_by_ontology's
organism resolver only resolves strains whose genes carry expression edges
(logged as a bug in gaps_and_friction.md; fix pending) — it rejects genome-only
strains AND metabolomics-only strains (e.g. MIT0801) even though their genomic
annotations are fully present. Per researcher instruction, this dogfood uses the
MCP tools as-is and restricts to the 9 strains the tools resolve (4 HL, 5 LL).
Deferred until the resolver is fixed: 7 annotated genome-only strains (MIT9515,
MIT0604, MIT9202, MIT9215, SB, PAC1, MIT1327) and metabolomics-only MIT0801.
RSP50 + MIT1314 lack Cyanorak annotation entirely and are out regardless.

Tools used (all MCP-equivalent API; no run_cypher): genes_by_ontology,
gene_homologs, list_organisms.

Outputs (relative to step folder):
  data/p_role_genes_by_strain.csv  — one row per (strain x D.1.5 gene), OG-annotated
  data/strain_panel.csv            — one row per panel strain: genome size + counts
  data/01_extract_p_gene_entries.log

Run from repo root:
  uv run python analyses/2026-06-13-ll_vs_hl_p_capacity/2_kg_entries/scripts/01_extract_p_gene_entries.py
"""
from __future__ import annotations

import csv
from pathlib import Path

from multiomics_explorer import genes_by_ontology, gene_homologs, list_organisms, GraphConnection

P_ROLE = "cyanorak.role:D.1.5"

# 9 MCP-resolvable strains (expression-bearing + Cyanorak-annotated).
# (ecotype, clade, strain_label, full_organism_name)
STRAINS = [
    ("HL", "HLI",  "MED4",    "Prochlorococcus MED4"),
    ("HL", "HLII", "AS9601",  "Prochlorococcus AS9601"),
    ("HL", "HLII", "MIT9301", "Prochlorococcus MIT9301"),
    ("HL", "HLII", "MIT9312", "Prochlorococcus MIT9312"),
    ("LL", "LLI",  "NATL1A",  "Prochlorococcus NATL1A"),
    ("LL", "LLI",  "NATL2A",  "Prochlorococcus NATL2A"),
    ("LL", "LLII", "SS120",   "Prochlorococcus marinus subsp. marinus CCMP1375 (SS120)"),
    ("LL", "LLIV", "MIT9303", "Prochlorococcus MIT9303"),
    ("LL", "LLIV", "MIT9313", "Prochlorococcus MIT9313"),
]

STEP_DIR = Path(__file__).resolve().parents[1]
DATA = STEP_DIR / "data"
DATA.mkdir(parents=True, exist_ok=True)

log_lines: list[str] = []
def log(msg: str) -> None:
    print(msg)
    log_lines.append(msg)


def most_specific_cyanorak_group(rows: list[dict]) -> dict | None:
    if not rows:
        return None
    return sorted(rows, key=lambda r: (r.get("specificity_rank") if r.get("specificity_rank") is not None else 99))[0]


def main() -> None:
    with GraphConnection() as conn:
        # genome sizes (normalization-confound input)
        org_resp = list_organisms(organism_names=[s[3] for s in STRAINS], limit=60, conn=conn)
        size_by_name = {r["organism_name"]: r["gene_count"] for r in org_resp["results"]}
        log(f"[genome sizes] resolved {len(size_by_name)}/{len(STRAINS)}; "
            f"not_found={org_resp.get('not_found')}")

        # per-strain P-role gene extraction via genes_by_ontology (MCP tool)
        gene_rows: list[dict] = []
        per_strain_tags: dict[str, list[str]] = {}
        for ecotype, clade, strain, org_name in STRAINS:
            resp = genes_by_ontology(
                ontology="cyanorak_role", term_ids=[P_ROLE], organism=org_name,
                min_gene_set_size=1, limit=None, conn=conn,
            )
            results = resp.get("results", [])
            per_strain_tags[strain] = [r["locus_tag"] for r in results]
            for r in results:
                gene_rows.append({
                    "ecotype": ecotype, "clade": clade, "strain": strain,
                    "organism_name": org_name, "locus_tag": r["locus_tag"],
                    "gene_name": r.get("gene_name"), "product": r.get("product"),
                    "gene_category": r.get("gene_category"),
                })
            log(f"[D.1.5] {ecotype}/{clade:5s} {strain:8s} resolved={resp.get('organism_name')!r:58s} genes={resp.get('total_genes', len(results))}")

        # map each gene to its most-specific curated Cyanorak OG via gene_homologs (MCP tool)
        all_tags = [g["locus_tag"] for g in gene_rows]
        og_by_tag: dict[str, dict] = {}
        no_group: list[str] = []
        CHUNK = 200
        for i in range(0, len(all_tags), CHUNK):
            batch = all_tags[i:i + CHUNK]
            hg = gene_homologs(locus_tags=batch, source="cyanorak", limit=None, conn=conn)
            by_tag: dict[str, list[dict]] = {}
            for row in hg.get("results", []):
                by_tag.setdefault(row["locus_tag"], []).append(row)
            for tag in batch:
                grp = most_specific_cyanorak_group(by_tag.get(tag, []))
                (og_by_tag.__setitem__(tag, grp) if grp else no_group.append(tag))
        log(f"[OG mapping] {len(og_by_tag)}/{len(all_tags)} genes mapped to a cyanorak group; {len(no_group)} unmapped")

        for g in gene_rows:
            grp = og_by_tag.get(g["locus_tag"])
            g["cyanorak_og"] = grp["group_id"] if grp else None
            g["og_gene_name"] = grp.get("consensus_gene_name") if grp else None
            g["og_product"] = grp.get("consensus_product") if grp else None
            g["og_specificity_rank"] = grp.get("specificity_rank") if grp else None

    # per-gene CSV
    gene_csv = DATA / "p_role_genes_by_strain.csv"
    gcols = ["ecotype", "clade", "strain", "organism_name", "locus_tag", "gene_name",
             "product", "gene_category", "cyanorak_og", "og_gene_name", "og_product",
             "og_specificity_rank"]
    with gene_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=gcols)
        w.writeheader(); w.writerows(gene_rows)

    # per-strain panel
    panel_csv = DATA / "strain_panel.csv"
    with panel_csv.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ecotype", "clade", "strain", "organism_name", "genome_gene_count",
                    "n_p_role_genes", "n_distinct_p_ogs", "p_role_genes_per_1000"])
        for ecotype, clade, strain, org_name in STRAINS:
            tags = per_strain_tags[strain]
            ogs = {og_by_tag[t]["group_id"] for t in tags if t in og_by_tag}
            gsize = size_by_name.get(org_name)
            per_1k = round(1000 * len(tags) / gsize, 3) if gsize else None
            w.writerow([ecotype, clade, strain, org_name, gsize, len(tags), len(ogs), per_1k])

    # funnel
    hl = [s for s in STRAINS if s[0] == "HL"]; ll = [s for s in STRAINS if s[0] == "LL"]
    hlc = sorted(len(per_strain_tags[s[2]]) for s in hl)
    llc = sorted(len(per_strain_tags[s[2]]) for s in ll)
    log("")
    log(f"[funnel] panel={len(STRAINS)} strains (HL={len(hl)}, LL={len(ll)}); total gene rows={len(gene_rows)}")
    log(f"[funnel] HL P-role genes: min={hlc[0]} median={hlc[len(hlc)//2]} max={hlc[-1]} mean={sum(hlc)/len(hlc):.1f}")
    log(f"[funnel] LL P-role genes: min={llc[0]} median={llc[len(llc)//2]} max={llc[-1]} mean={sum(llc)/len(llc):.1f}")
    log(f"[outputs] {gene_csv.relative_to(STEP_DIR)} ({len(gene_rows)} rows); {panel_csv.relative_to(STEP_DIR)} ({len(STRAINS)} rows)")

    (DATA / "01_extract_p_gene_entries.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
