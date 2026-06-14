"""
Step 5 (analyze) — run the locked capacity metric on the 9-strain panel.

Produces:
  data/focused_acquisition_counts.csv   per-strain focused-acquisition OG count (+per1k)
  data/llhl_ratio_vs_controls.csv       focused-P LL/HL vs control categories
  data/repertoire_by_og.csv             per-OG presence + repertoire category
  data/clade_and_stability.csv          per-clade means + drop-LLIV stability
  figures/fig1_repertoire_heatmap.png   strain x 23-OG presence/absence
  figures/fig2_llhl_ratio.png           LL/HL ratio: focused-P vs controls
  figures/fig3_count_by_clade.png       per-strain focused count by clade/ecotype
  data/01_capacity_analysis.log

Imports the step-4 module. Reads frozen step-2/step-3 CSVs (no KG access).
Run: uv run python analyses/2026-06-13-ll_vs_hl_p_capacity/5_analyze/scripts/01_capacity_analysis.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ANALYSIS = Path(__file__).resolve().parents[2]
STEP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS / "4_methods"))
from p_capacity import (build_presence_matrix, per_strain_counts,
                        ecotype_ratio, differential_presence)

DATA, FIG = STEP / "data", STEP / "figures"
DATA.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)

GENES = ANALYSIS / "2_kg_entries" / "data" / "p_role_genes_by_strain.csv"
PANEL = ANALYSIS / "2_kg_entries" / "data" / "strain_panel.csv"
CLASS = ANALYSIS / "3_framing" / "data" / "p_og_classification.csv"
CONTROLS = ANALYSIS / "3_framing" / "data" / "control_categories_by_strain.csv"

CLADE_ORDER = ["HLI", "HLII", "LLI", "LLII", "LLIV"]
log_lines: list[str] = []
def log(m: str) -> None:
    print(m); log_lines.append(m)


def main() -> None:
    genes = pd.read_csv(GENES)
    panel = pd.read_csv(PANEL)
    classif = pd.read_csv(CLASS)
    controls = pd.read_csv(CONTROLS)

    gsize = panel.set_index("strain")["genome_gene_count"]
    acq_ogs = set(classif.loc[classif["class"] == "acquisition", "cyanorak_og"])
    log(f"[input] {len(acq_ogs)} focused-acquisition OGs; "
        f"{genes['strain'].nunique()} strains")

    # --- focused-acquisition presence matrix + per-strain counts ---
    acq_genes = genes[genes["cyanorak_og"].isin(acq_ogs)].copy()
    matrix, meta = build_presence_matrix(acq_genes)
    counts = per_strain_counts(matrix, meta, genome_size=gsize)
    counts = counts.reset_index().sort_values(
        ["ecotype", "clade", "strain"]).set_index("strain")
    counts.to_csv(DATA / "focused_acquisition_counts.csv")
    log("\n[per-strain focused-acquisition counts]")
    log(counts[["ecotype", "clade", "n_ogs", "genome_gene_count", "per1k"]].to_string())

    foc = ecotype_ratio(counts)
    log(f"\n[focused subset] HL mean={foc['hl_mean']:.2f} LL mean={foc['ll_mean']:.2f} "
        f"LL/HL={foc['ll_over_hl']:.3f} (n_HL={foc['n_hl']}, n_LL={foc['n_ll']})")

    # --- LL/HL ratio vs controls (raw counts) ---
    def ratio_from_controls(col: str) -> tuple[float, float, float]:
        g = controls.groupby("ecotype")[col].mean()
        return g["HL"], g["LL"], g["LL"] / g["HL"]
    rows = [("focused_P_acquisition", foc["hl_mean"], foc["ll_mean"], foc["ll_over_hl"], "23-OG curated subset")]
    cat_labels = {
        "D.1.5_phosphorus_n": "full D.1.5 role (uncurated)",
        "K.2_ribosomal_n": "invariant baseline",
        "D.1.3_nitrogen_n": "specificity control",
        "D.1.7_trace_metal_n": "specificity control",
        "D.1.2_light_n": "positive control",
    }
    for col, role in cat_labels.items():
        hn, ln, r = ratio_from_controls(col)
        rows.append((col[:-2] if col.endswith("_n") else col, hn, ln, r, role))
    ratio_df = pd.DataFrame(rows, columns=["category", "HL_mean", "LL_mean", "LL_over_HL", "role"])
    ratio_df.to_csv(DATA / "llhl_ratio_vs_controls.csv", index=False)
    log("\n[LL/HL ratio: focused-P vs controls]")
    log(ratio_df.round(3).to_string(index=False))

    # --- repertoire by OG ---
    rep = differential_presence(matrix, meta)
    name_map = (classif.set_index("cyanorak_og")[["og_gene_name", "og_product"]])
    rep = rep.join(name_map)
    rep.to_csv(DATA / "repertoire_by_og.csv")
    cat_counts = rep["category"].value_counts().to_dict()
    log(f"\n[repertoire categories] {cat_counts}")
    for cat in ("LL_only", "HL_only"):
        sub = rep[rep["category"] == cat]
        log(f"  {cat}: " + ", ".join(
            f"{r.og_gene_name or r.og_product[:20]}({r.n_HL}HL/{r.n_LL}LL)"
            for r in sub.itertuples()))

    # --- clade view + drop-LLIV stability ---
    clade_mean = counts.groupby("clade")["n_ogs"].agg(["mean", "size"]).reindex(CLADE_ORDER)
    log("\n[per-clade focused-acquisition count]")
    log(clade_mean.to_string())
    no_lliv = counts[counts["clade"] != "LLIV"]
    foc_nolliv = ecotype_ratio(no_lliv)
    log(f"\n[stability: drop LLIV] LL becomes n={foc_nolliv['n_ll']} "
        f"(NATL1A,NATL2A,SS120); HL mean={foc_nolliv['hl_mean']:.2f} "
        f"LL mean={foc_nolliv['ll_mean']:.2f} LL/HL={foc_nolliv['ll_over_hl']:.3f}")
    stab = pd.DataFrame([
        {"set": "all_LL", "HL_mean": foc["hl_mean"], "LL_mean": foc["ll_mean"], "LL_over_HL": foc["ll_over_hl"]},
        {"set": "LL_minus_LLIV", "HL_mean": foc_nolliv["hl_mean"], "LL_mean": foc_nolliv["ll_mean"], "LL_over_HL": foc_nolliv["ll_over_hl"]},
    ])
    clade_mean.to_csv(DATA / "clade_and_stability.csv")
    stab.to_csv(DATA / "clade_and_stability.csv", mode="a")

    # ---------- figures ----------
    # fig1: presence/absence heatmap, OGs (rows) x strains (cols), ordered
    order = counts.index.tolist()  # already ecotype/clade sorted
    rep_sorted = rep.sort_values(["category", "n_LL", "n_HL"])
    m = matrix.loc[order, rep_sorted.index].T  # OG x strain
    ylabels = [f"{(rep.loc[og,'og_gene_name'] if pd.notna(rep.loc[og,'og_gene_name']) else og)}" for og in m.index]
    fig, ax = plt.subplots(figsize=(7, 9))
    ax.imshow(m.values, aspect="auto", cmap="Greens", vmin=0, vmax=1)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(
        [f"{s}\n{counts.loc[s,'ecotype']}/{counts.loc[s,'clade']}" for s in order],
        rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(ylabels))); ax.set_yticklabels(ylabels, fontsize=6)
    # separate HL|LL with a line
    n_hl_cols = (counts.loc[order, "ecotype"] == "HL").sum()
    ax.axvline(n_hl_cols - 0.5, color="red", lw=1.5)
    ax.set_title("Focused P-acquisition repertoire (23 OGs)\npresence=green; red line = HL|LL", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "fig1_repertoire_heatmap.png", dpi=300); plt.close(fig)

    # fig2: LL/HL ratio bar chart
    order_cats = ["K.2_ribosomal", "D.1.3_nitrogen", "D.1.2_light", "D.1.7_trace_metal",
                  "D.1.5_phosphorus", "focused_P_acquisition"]
    rd = ratio_df.set_index("category").reindex(order_cats)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#888"]*1 + ["#4a90d9"]*1 + ["#7cb342"]*1 + ["#4a90d9"]*1 + ["#bbb"]*1 + ["#d9534f"]*1
    ax.bar(range(len(rd)), rd["LL_over_HL"], color=colors)
    ax.axhline(1.0, color="k", ls="--", lw=1, label="LL/HL = 1 (no difference)")
    ax.set_xticks(range(len(rd))); ax.set_xticklabels(
        [c.replace("_", "\n") for c in rd.index], fontsize=7)
    ax.set_ylabel("LL/HL ratio (raw count)")
    ax.set_title("Ecotype LL/HL gene-count ratio: focused P-acquisition vs control suite", fontsize=9)
    for i, v in enumerate(rd["LL_over_HL"]):
        ax.text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=7)
    ax.legend(fontsize=7); fig.tight_layout()
    fig.savefig(FIG / "fig2_llhl_ratio.png", dpi=300); plt.close(fig)

    # fig3: per-strain focused count by clade/ecotype
    fig, ax = plt.subplots(figsize=(7, 4))
    cmap = {"HL": "#d9534f", "LL": "#4a90d9"}
    xs = range(len(order))
    ax.bar(xs, counts.loc[order, "n_ogs"], color=[cmap[counts.loc[s,"ecotype"]] for s in order])
    ax.set_xticks(list(xs)); ax.set_xticklabels(
        [f"{s}\n{counts.loc[s,'clade']}" for s in order], rotation=45, ha="right", fontsize=7)
    ax.set_ylabel("focused P-acquisition OGs present")
    ax.axhline(foc["hl_mean"], color="#d9534f", ls=":", lw=1, label=f"HL mean {foc['hl_mean']:.1f}")
    ax.axhline(foc["ll_mean"], color="#4a90d9", ls=":", lw=1, label=f"LL mean {foc['ll_mean']:.1f}")
    ax.set_title("Per-strain focused P-acquisition OG count", fontsize=9)
    ax.legend(fontsize=7); fig.tight_layout()
    fig.savefig(FIG / "fig3_count_by_clade.png", dpi=300); plt.close(fig)

    log(f"\n[outputs] 4 CSVs + 3 figures in {STEP.name}/")
    (DATA / "01_capacity_analysis.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
