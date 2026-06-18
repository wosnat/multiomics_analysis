"""Step 5 follow-on (control): run the SAME exoenzyme classifier on the FULL genomes
of all 7 strains, to get the genome-wide denominator — is the extruded set enriched
for exoenzymes, or just sampling them at the background rate?

Uses exoenzyme_lib.classify (byte-identical to the extruded run in 04).
Gene lists pulled per strain via run_cypher.

Outputs (../data/): exoenzyme_genome_background.csv (per-strain + total counts),
                    exoenzyme_genome_candidates.csv (the genome-wide candidate genes)

Run: uv run python analyses/2026-06-17-alteromonas_extruded_proteome/5_analyze/scripts/05_exoenzyme_genome_background.py
"""

from pathlib import Path

import pandas as pd

from multiomics_explorer import GraphConnection, run_cypher
from exoenzyme_lib import classify

DATA = Path(__file__).resolve().parents[1] / "data"

STRAINS = ["EZ55", "MIT1002", "BS11", "ATCC27126", "BGP6", "AD45", "HOT1A3"]


def all_loci(strain: str) -> pd.DataFrame:
    org = f"Alteromonas macleodii {strain}"
    res = run_cypher(
        query=("MATCH (g:Gene) WHERE g.organism_name = '%s' "
               "RETURN g.locus_tag AS locus_tag" % org),
        limit=10000,
    )
    df = pd.DataFrame(res["results"])
    df["strain_short"] = strain
    return df


def main() -> None:
    genome = pd.concat([all_loci(s) for s in STRAINS], ignore_index=True)
    print(f"[genome] total genes across {len(STRAINS)} strains: {len(genome)}")

    with GraphConnection() as conn:
        g = classify(genome, conn)

    # per-strain rollup
    rows = []
    for strain, sub in g.groupby("strain_short"):
        deg = int(sub["is_degradative"].sum())
        tierA = int((sub["tier"] == "A: degradative + exported").sum())
        cand = int(sub["is_exoenzyme"].sum())
        rows.append({"strain": strain, "n_genes": len(sub), "degradative": deg,
                     "tierA_exported": tierA, "exoenzyme_candidates": cand,
                     "pct_candidates": round(100 * cand / len(sub), 2)})
    roll = pd.DataFrame(rows).sort_values("strain")
    total = {"strain": "TOTAL", "n_genes": len(g),
             "degradative": int(g["is_degradative"].sum()),
             "tierA_exported": int((g["tier"] == "A: degradative + exported").sum()),
             "exoenzyme_candidates": int(g["is_exoenzyme"].sum()),
             "pct_candidates": round(100 * int(g["is_exoenzyme"].sum()) / len(g), 2)}
    roll = pd.concat([roll, pd.DataFrame([total])], ignore_index=True)
    print("\n[genome-wide exoenzyme candidates per strain]")
    print(roll.to_string(index=False))

    # substrate breakdown genome-wide (candidates)
    cand = g[g["is_exoenzyme"]].copy()
    exploded = cand.assign(substrate=cand["substrates"].str.split(";")).explode("substrate")
    by_sub = (exploded.groupby("substrate")
              .agg(n_genes=("locus_tag", "nunique"),
                   n_tierA=("tier", lambda s: (s == "A: degradative + exported").sum()))
              .reset_index().sort_values("n_genes", ascending=False))
    print("\n[genome-wide candidates by substrate class]")
    print(by_sub.to_string(index=False))

    roll.to_csv(DATA / "exoenzyme_genome_background.csv", index=False)
    cand[["locus_tag", "strain_short", "substrates", "tier",
          "func_evidence", "export_evidence"]].sort_values(["strain_short", "substrates"]).to_csv(
        DATA / "exoenzyme_genome_candidates.csv", index=False)
    print("\n[written] data/exoenzyme_genome_background.csv, data/exoenzyme_genome_candidates.csv")


if __name__ == "__main__":
    main()
