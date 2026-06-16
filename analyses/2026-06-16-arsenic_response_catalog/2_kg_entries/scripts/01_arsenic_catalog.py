"""Step 2 — enumerate the Prochlorococcus arsenic-handling gene catalogue.

Built entirely from the dedicated KG tools (no run_cypher escape hatch):
  (A) genes_by_function  — free-text over gene name / product / functional
      description, one call across all Prochlorococcus strains.
  (B) genes_by_ontology  — forward term -> gene lookup for every arsenic-named
      ontology term, looped over the 19 Prochlorococcus strains x the 6
      ontologies that carry an arsenic term (GO MF, GO BP, EC, KEGG, TCDB, Pfam).
      Single-organism enforced, so we loop strains; min_gene_set_size=0 so small
      arsenic gene sets are not filtered out.

Genes are deduplicated by locus_tag, matched ontology terms rolled up per gene,
and each gene tagged strict vs broad:
  strict = product or function_description names arsenic directly, OR gene_name is
           a canonical ars gene (arsA/B/C/D/H/M/R, acr3).
  broad  = pulled in only via a looser link (ArsR/SmtB-family regulator that may
           sense other metals, Spx/MgsR mislabelled arsC, arsenate-transferring
           GAPDH, etc.).

Inputs:  KG via multiomics_explorer (Neo4j creds from repo-root .env).
Outputs:
  data/arsenic_genes.csv      — one row per gene (the frozen catalogue)
  data/arsenic_gene_terms.csv — one row per gene x matched ontology term (long)
  data/01_arsenic_catalog.log — stdout tee (funnel + breakdowns)

Run:  uv run python analyses/2026-06-16-arsenic_response_catalog/2_kg_entries/scripts/01_arsenic_catalog.py
      (from the repo root, so .env credentials load)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from multiomics_explorer import (
    GraphConnection, list_organisms, genes_by_function, genes_by_ontology,
    gene_details,
)

DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)

CANONICAL_ARS = {"arsA", "arsB", "arsC", "arsD", "arsH", "arsM", "arsR", "acr3"}

# Arsenic-named terms found via search_ontology (step-2 discovery), grouped by the
# ontology that genes_by_ontology must be called with.
ARSENIC_TERMS: dict[str, list[str]] = {
    "go_mf": ["go:0030791", "go:0030611", "go:0015105", "go:0008794", "go:0030612",
              "go:0050611", "go:0102100", "go:1901683", "go:0008490", "go:0015446",
              "go:0030613", "go:0030614", "go:0050499", "go:0052882"],
    "go_bp": ["go:0015700", "go:0046685", "go:0071243", "go:0071722"],
    "ec":    ["ec:1.2.1.107", "ec:1.20.-.-", "ec:1.20.2.1", "ec:1.20.4.1",
              "ec:1.20.4.4", "ec:1.20.9.1", "ec:1.20.99.1", "ec:2.1.1.137",
              "ec:2.8.4.2", "ec:7.3.2.7"],
    "kegg":  ["kegg.orthology:K00537", "kegg.orthology:K01551", "kegg.orthology:K03325",
              "kegg.orthology:K03741", "kegg.orthology:K03892", "kegg.orthology:K03893",
              "kegg.orthology:K07755", "kegg.orthology:K11811"],
    "tcdb":  ["tcdb:2.A.119", "tcdb:2.A.131", "tcdb:2.A.45", "tcdb:2.A.59", "tcdb:3.A.4"],
    "pfam":  ["pfam:PF02040", "pfam:PF06953"],
}

TEXT_SEARCH = ("arsenic OR arsenate OR arsenite OR arsenical OR acr3 "
               "OR arsA OR arsB OR arsC OR arsD OR arsH OR arsM OR arsR")

BASE_COLS = ["locus_tag", "gene_name", "product", "function_description",
             "organism_name", "annotation_quality", "gene_category"]


def _s(x) -> str:
    return x.lower() if isinstance(x, str) else ""


def is_strict(product, function_description, gene_name) -> bool:
    if "arsen" in _s(product) or "arsen" in _s(function_description):
        return True
    return gene_name in CANONICAL_ARS


def main() -> None:
    with GraphConnection() as conn:
        orgs = list_organisms(limit=None, conn=conn)["results"]
        strains = sorted(o["organism_name"] for o in orgs
                         if str(o.get("genus")) == "Prochlorococcus"
                         or o["organism_name"].startswith("Prochlorococcus"))
        print(f"[scope] {len(strains)} Prochlorococcus strains")

        # (A) Text source — one call, all strains.
        text_res = genes_by_function(search_text=TEXT_SEARCH, organism="Prochlorococcus",
                                     limit=None, verbose=True, conn=conn)
        text = pd.DataFrame(text_res["results"])
        # genes_by_function uses fuzzy Lucene scoring; keep rows with a real 'ars'
        # token in product / function description / summary, or a canonical ars
        # gene_name. This keeps ArsR/SmtB-family regulators (broad) while dropping
        # loose scoring noise (e.g. PTOX, alternative oxidase) that has no 'ars'.
        def ars_token(r) -> bool:
            blob = " ".join(_s(r.get(c)) for c in ("product", "function_description", "gene_summary"))
            return "ars" in blob or r.get("gene_name") in CANONICAL_ARS
        text = text[text.apply(ars_token, axis=1)].copy()
        print(f"[funnel] gene-text matches (ars-confirmed): {text['locus_tag'].nunique()} genes")

        # (B) Ontology source — loop strain x ontology.
        onto_rows: list[dict] = []
        for ont, term_ids in ARSENIC_TERMS.items():
            for strain in strains:
                res = genes_by_ontology(ontology=ont, organism=strain, term_ids=term_ids,
                                        min_gene_set_size=0, max_gene_set_size=100000,
                                        limit=5000, verbose=True, conn=conn)
                for row in res["results"]:
                    onto_rows.append({**row, "ontology": ont})
        onto = pd.DataFrame(onto_rows)
        print(f"[funnel] ontology-link matches: "
              f"{onto['locus_tag'].nunique() if len(onto) else 0} genes "
              f"({len(onto)} gene x term rows)")

        # Authoritative per-gene fields for the full union. genes_by_ontology rows
        # omit organism_name / annotation_quality, so look every gene up once via
        # gene_details (the deep-dive tool) to get consistent base columns.
        text_hits = set(text["locus_tag"])
        onto_hits = set(onto["locus_tag"]) if len(onto) else set()
        all_tags = sorted(text_hits | onto_hits)
        info = pd.DataFrame(gene_details(locus_tags=all_tags, limit=len(all_tags),
                                         conn=conn)["results"])

    # ---- merge, dedup, classify ----
    base = info[[c for c in BASE_COLS if c in info.columns]].drop_duplicates(
        subset=["locus_tag"]).reset_index(drop=True)

    if len(onto):
        onto.to_csv(DATA / "arsenic_gene_terms.csv", index=False)
        term_rollup = (onto.groupby("locus_tag")
                       .agg(n_ontology_terms=("term_id", "nunique"),
                            ontologies=("ontology", lambda s: " | ".join(sorted(set(s)))),
                            matched_terms=("term_name", lambda s: " | ".join(sorted(set(map(str, s))))))
                       .reset_index())
    else:
        term_rollup = pd.DataFrame(columns=["locus_tag", "n_ontology_terms",
                                            "ontologies", "matched_terms"])

    base["matched_via_text"] = base["locus_tag"].isin(text_hits)
    base["matched_via_ontology"] = base["locus_tag"].isin(onto_hits)
    base["match_source"] = base.apply(
        lambda r: "both" if r["matched_via_text"] and r["matched_via_ontology"]
        else ("text" if r["matched_via_text"] else "ontology"), axis=1)

    cat = base.merge(term_rollup, on="locus_tag", how="left")
    cat["n_ontology_terms"] = cat["n_ontology_terms"].fillna(0).astype(int)
    cat["scope"] = cat.apply(
        lambda r: "strict" if is_strict(r["product"], r["function_description"],
                                        r["gene_name"]) else "broad", axis=1)
    cat = cat.sort_values(["scope", "gene_name", "organism_name"],
                          na_position="last").reset_index(drop=True)
    cat.to_csv(DATA / "arsenic_genes.csv", index=False)
    print(f"[out] wrote {len(cat)} genes -> data/arsenic_genes.csv")

    print("\n[scope]");        print(cat["scope"].value_counts().to_string())
    print("\n[match_source]"); print(cat["match_source"].value_counts().to_string())
    print("\n[gene_name] (strict only)")
    print(cat[cat["scope"] == "strict"]["gene_name"].fillna("(none)").value_counts().to_string())
    print("\n[per strain]");  print(cat["organism_name"].value_counts().to_string())
    print("\n[annotation_quality]")
    print(cat["annotation_quality"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
