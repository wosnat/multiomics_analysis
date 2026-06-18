"""Step 5 follow-on: which EXTRUDED proteins are likely exoenzymes that break down
organic compounds (both routes)? Classifier lives in exoenzyme_lib.py (shared with
05 genome background). See that module for the function/export/tier definitions.

Inputs: ../data/extruded_genes_all.csv (frozen).
Outputs (../data/): exoenzyme_candidates.csv, exoenzyme_by_substrate.csv
Figure (../figures/): exoenzymes.png

Run: uv run python analyses/2026-06-17-alteromonas_extruded_proteome/5_analyze/scripts/04_exoenzymes.py
"""

from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from multiomics_explorer import GraphConnection
from exoenzyme_lib import classify

DATA = Path(__file__).resolve().parents[1] / "data"
FIG = Path(__file__).resolve().parents[1] / "figures"


def main() -> None:
    genes = pd.read_csv(DATA / "extruded_genes_all.csv")
    genes["strain_short"] = genes["strain"].str.replace("Alteromonas macleodii ", "", regex=False)

    with GraphConnection() as conn:
        genes = classify(genes, conn)

    cand = genes[genes["is_exoenzyme"]].copy()
    n_deg = int(genes["is_degradative"].sum())
    n_A = int((genes["tier"] == "A: degradative + exported").sum())
    n_B = int((genes["tier"] == "B: degradative, export uncertain").sum())
    n_C = int((genes["tier"] == "C: degradative + cytoplasmic (likely contaminant)").sum())
    print(f"[funnel] extruded genes: {len(genes)}")
    print(f"[funnel] degradative-enzyme annotation (EC/CAZy/GO-MF/Pfam): {n_deg}")
    print(f"[tier A] degradative + exported (high confidence): {n_A}")
    print(f"[tier B] degradative, export uncertain:            {n_B}")
    print(f"[tier C] degradative + cytoplasmic (contaminant):  {n_C}")
    print(f"[candidates] exoenzyme (non-cytoplasmic): {len(cand)}")

    exploded = cand.assign(substrate=cand["substrates"].str.split(";")).explode("substrate")
    by_sub = (exploded.groupby("substrate")
              .agg(n_genes=("locus_tag", "nunique"), n_ogs=("og_group_id", "nunique"),
                   n_tierA=("tier", lambda s: (s == "A: degradative + exported").sum()),
                   routes=("route", lambda s: ";".join(sorted(set(s)))))
              .reset_index().sort_values("n_genes", ascending=False))
    print("\n[exoenzyme candidates by organic-substrate class]")
    print(by_sub.to_string(index=False))

    og_view = (cand.groupby("og_product")
               .agg(substrates=("substrates", "first"), best_tier=("tier", "min"),
                    routes=("route", lambda s: ";".join(sorted(set(s)))),
                    n_strains=("strain_short", "nunique"),
                    strains=("strain_short", lambda s: ";".join(sorted(set(s)))),
                    func_evidence=("func_evidence", "first"))
               .reset_index().sort_values(["substrates", "n_strains"], ascending=[True, False]))
    print("\n[candidate exoenzymes — OG level]")
    print(og_view.to_string(index=False))

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    funnel = [len(genes), n_deg, len(cand), n_A]
    ax[0].bar(["extruded", "degradative", "exoenzyme\ncandidate", "tier A\n(+exported)"],
              funnel, color=["#cccccc", "#d8a13b", "#d83b5e", "#3b7dd8"])
    for i, v in enumerate(funnel):
        ax[0].text(i, v + 3, str(v), ha="center")
    ax[0].set_ylabel("genes"); ax[0].set_title("Exoenzyme funnel (extruded set)")
    b = by_sub.sort_values("n_genes")
    ax[1].barh(b["substrate"], b["n_genes"], color="#d8a13b", label="candidate (A+B)")
    ax[1].barh(b["substrate"], b["n_tierA"], color="#3b7dd8", label="tier A (+exported)")
    ax[1].set_xlabel("candidate exoenzyme genes"); ax[1].set_title("By organic-substrate class")
    ax[1].legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "exoenzymes.png", dpi=300)
    print("\n[written] figures/exoenzymes.png")

    out_cols = ["locus_tag", "strain_short", "route", "product", "substrates", "tier",
                "func_evidence", "export_evidence", "og_group_id", "og_product"]
    cand[out_cols].sort_values(["substrates", "tier"]).to_csv(
        DATA / "exoenzyme_candidates.csv", index=False)
    by_sub.to_csv(DATA / "exoenzyme_by_substrate.csv", index=False)
    print("[written] data/exoenzyme_candidates.csv, data/exoenzyme_by_substrate.csv")


if __name__ == "__main__":
    main()
