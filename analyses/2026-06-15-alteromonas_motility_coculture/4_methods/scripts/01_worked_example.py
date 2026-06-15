"""
Step 4 worked example — verify the package's pathway_enrichment does what the
framing needs, on the anchor experiment (HOT1A3 coculture-with-MED4 vs axenic,
Weissberg 2025). No custom method: the package's DE->ORA pipeline (one-sided
Fisher per pathway, per-experiment table_scope background, up/down direction, BH)
is the method.

Checks: run full KEGG level-2 enrichment (direction both) and read off our three
pathways (flagellar assembly ko02040, bacterial chemotaxis ko02030, ribosome
ko03010) — confirming the motility pathways surface with a direction and the
ribosome behaves as a baseline.

Run: uv run python analyses/2026-06-15-alteromonas_motility_coculture/4_methods/scripts/01_worked_example.py
"""
from __future__ import annotations

from multiomics_explorer import pathway_enrichment

ANCHOR = "10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq"
WATCH = {"kegg.pathway:ko02040": "Flagellar assembly",
         "kegg.pathway:ko02030": "Bacterial chemotaxis",
         "kegg.pathway:ko03010": "Ribosome (baseline)"}


def main() -> None:
    res = pathway_enrichment(organism="HOT1A3", experiment_ids=[ANCHOR],
                             ontology="kegg", level=2, direction="both")
    df = res.results
    print(f"clusters: {sorted(df['cluster'].unique())}")
    print(f"total (cluster x pathway) tests: {len(df)}")
    cols = ["cluster", "term_id", "term_name", "count", "bg_count",
            "fold_enrichment", "pvalue", "p_adjust"]
    sub = df[df["term_id"].isin(WATCH)][cols].sort_values(["term_id", "cluster"])
    print("\n[our pathways across up/down clusters]")
    print(sub.to_string(index=False) if len(sub) else "  (none of the watch terms tested)")
    # also show what WAS significant, for context
    sig = df[df["p_adjust"] < 0.05][["cluster", "term_name", "count", "fold_enrichment", "p_adjust"]]
    print(f"\n[significant pathways at p_adjust<0.05: {len(sig)}]")
    print(sig.sort_values("p_adjust").head(15).to_string(index=False) if len(sig) else "  (none)")


if __name__ == "__main__":
    main()
