"""
Step 5a (Analyze) — HOT1A3 nutrient-starvation time-course, coculture vs axenic,
the difference-of-trajectories test of the carbon-provision hypothesis.

Reuses the step-4 method (`run_contrast`, loaded by path) to freeze per-arm
enrichment + motility readouts into this step's data/, then composes:
  - motility (KEGG flagella+chemotaxis) gene-level divergence, coculture vs axenic,
    per matched timepoint — paired Wilcoxon signed-rank on log2FC (same study +
    platform + genes => magnitude comparable). RNA and protein tested SEPARATELY
    (low mRNA-protein agreement; see statistical-rigor.md).
  - Spearman trend of the divergence over time (flagged low-power, few timepoints).
  - RNA vs protein direction-agreement fraction (the mandated cross-omics metric).
  - pathway signed-score trajectories (motility + central-carbon pathways) per arm.
Figures: Fig 1 motility over time (RNA|protein panels, coculture vs axenic);
Fig 2 carbon/motility pathway signed scores over time.

Run: uv run python analyses/2026-06-15-alteromonas_motility_coculture/5_analyze/scripts/01_timecourse.py
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon, spearmanr
from statsmodels.stats.multitest import multipletests
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from multiomics_explorer import GraphConnection

ANALYSIS = Path(__file__).resolve().parents[1]            # 5_analyze
DATA = ANALYSIS / "data"; FIG = ANALYSIS / "figures"
DATA.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
METHOD_PATH = ANALYSIS.parent / "4_methods" / "scripts" / "01_method.py"

log_lines: list[str] = []
def log(m): print(m); log_lines.append(str(m))

# load the step-4 method by path (dir/file names aren't importable identifiers)
_spec = importlib.util.spec_from_file_location("step4_method", METHOD_PATH)
step4 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(step4)

BASE = "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_hot1a3"
ARMS = {
    "rna_coculture":  f"{BASE}_rnaseq_coculture",
    "rna_axenic":     f"{BASE}_rnaseq_axenic",
    "prot_coculture": f"{BASE}_proteomics_coculture",
    "prot_axenic":    f"{BASE}_proteomics_axenic",
}
# timepoint label -> numeric order for trend tests (pooled 60+89 sits between 60 and 89)
TP_ORDER = {"day 18": 1.0, "day 31": 2.0, "day 60": 3.0, "day 89": 4.0, "days 60+89": 3.5}
# interpretable pathways to track over time (term_id -> short label)
TRACK = {
    "kegg.pathway:ko02030": "Bacterial chemotaxis",
    "kegg.pathway:ko02040": "Flagellar assembly",
    "kegg.pathway:ko00010": "Glycolysis/Gluconeogenesis",
    "kegg.pathway:ko00020": "TCA cycle",
    "kegg.pathway:ko01200": "Carbon metabolism",
    "kegg.pathway:ko00190": "Oxidative phosphorylation",
    "kegg.pathway:ko03010": "Ribosome",
}


def freeze_arms() -> None:
    with GraphConnection() as conn:
        for label, eid in ARMS.items():
            s = step4.run_contrast(label=f"hot1a3_{label}", organism="HOT1A3",
                                   experiment_ids=[eid], strain="HOT1A3",
                                   conn=conn, outdir=DATA)
            log(f"[froze] {label}: {s}")


def motility_divergence(omics: str) -> pd.DataFrame:
    """Paired Wilcoxon (coculture-axenic) on motility-set log2FC per matched timepoint."""
    coc = pd.read_csv(DATA / f"hot1a3_{omics}_coculture_motility_genes_de.csv")
    ax = pd.read_csv(DATA / f"hot1a3_{omics}_axenic_motility_genes_de.csv")
    m = coc.merge(ax, on=["locus_tag", "timepoint"], suffixes=("_coc", "_ax"))
    rows = []
    for tp, g in m.groupby("timepoint"):
        d = (g["log2fc_coc"] - g["log2fc_ax"]).dropna()
        if len(d) < 6 or (d == 0).all():
            continue
        try:
            stat, p = wilcoxon(g["log2fc_coc"], g["log2fc_ax"], zero_method="wilcox")
        except ValueError:
            stat, p = np.nan, np.nan
        rows.append({"omics": omics, "timepoint": tp, "tp_order": TP_ORDER.get(tp, np.nan),
                     "n_genes": len(d), "median_delta_coc_minus_ax": float(d.median()),
                     "wilcoxon_p": p,
                     "n_coc_down": int((g["expression_status_coc"] == "significant_down").sum()),
                     "n_coc_up": int((g["expression_status_coc"] == "significant_up").sum()),
                     "n_ax_down": int((g["expression_status_ax"] == "significant_down").sum()),
                     "n_ax_up": int((g["expression_status_ax"] == "significant_up").sum())})
    df = pd.DataFrame(rows).sort_values("tp_order")
    if len(df):
        df["wilcoxon_p_bh"] = multipletests(df["wilcoxon_p"], method="fdr_bh")[1] \
            if df["wilcoxon_p"].notna().any() else np.nan
    return df


def direction_agreement() -> dict:
    """RNA vs protein: fraction of motility genes changing in the same direction,
    per arm, over matched (gene, timepoint) with both omics present."""
    out = {}
    for arm in ("coculture", "axenic"):
        rna = pd.read_csv(DATA / f"hot1a3_rna_{arm}_motility_genes_de.csv")
        pro = pd.read_csv(DATA / f"hot1a3_prot_{arm}_motility_genes_de.csv")
        j = rna.merge(pro, on=["locus_tag", "timepoint"], suffixes=("_rna", "_pro"))
        j = j[(j["log2fc_rna"].abs() > 0) & (j["log2fc_pro"].abs() > 0)]
        if len(j):
            agree = (np.sign(j["log2fc_rna"]) == np.sign(j["log2fc_pro"])).mean()
            out[arm] = {"n_pairs": int(len(j)), "direction_agreement": round(float(agree), 3)}
    return out


def pathway_trajectories() -> pd.DataFrame:
    """Per (arm, timepoint, tracked pathway): one signed score (direction with min p_adjust)."""
    recs = []
    for arm in ("rna_coculture", "rna_axenic", "prot_coculture", "prot_axenic"):
        f = DATA / f"hot1a3_{arm}_kegg_l2_enrichment.csv"
        if not f.exists():
            continue
        e = pd.read_csv(f)
        e = e[e["term_id"].isin(TRACK)]
        for (tp, term), g in e.groupby(["timepoint", "term_id"]):
            best = g.loc[g["p_adjust"].idxmin()]
            recs.append({"arm": arm, "omics": arm.split("_")[0],
                         "condition": arm.split("_", 1)[1], "timepoint": tp,
                         "tp_order": TP_ORDER.get(tp, np.nan), "term_id": term,
                         "pathway": TRACK[term], "signed_score": best["signed_score"],
                         "p_adjust": best["p_adjust"]})
    return pd.DataFrame(recs).sort_values(["omics", "pathway", "tp_order"])


def fig_motility(div_rna: pd.DataFrame, div_prot: pd.DataFrame) -> None:
    """Fig 1: motility-set median log2FC divergence + significant-gene counts over time."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    for col, (omics, div) in enumerate([("RNA", div_rna), ("protein", div_prot)]):
        # top: median delta (coculture - axenic) over time
        a = axes[0, col]
        if len(div):
            a.axhline(0, color="grey", lw=0.8, ls=":")
            a.plot(div["tp_order"], div["median_delta_coc_minus_ax"], "o-", color="tab:purple")
            for _, r in div.iterrows():
                mark = "*" if (pd.notna(r.get("wilcoxon_p_bh")) and r["wilcoxon_p_bh"] < 0.05) else ""
                a.annotate(f"{r['timepoint']}{mark}", (r["tp_order"], r["median_delta_coc_minus_ax"]),
                           fontsize=8, xytext=(0, 6), textcoords="offset points", ha="center")
        a.set_title(f"{omics}: motility log2FC divergence\n(coculture − axenic; * = BH p<0.05)", fontsize=10)
        a.set_xlabel("timepoint order"); a.set_ylabel("median Δ log2FC")
        # bottom: significant motility-gene counts per arm
        b = axes[1, col]
        if len(div):
            w = 0.35
            b.bar(div["tp_order"] - w/2, -div["n_coc_down"], w, color="tab:blue", label="coc down")
            b.bar(div["tp_order"] - w/2, div["n_coc_up"], w, color="tab:cyan", label="coc up")
            b.bar(div["tp_order"] + w/2, -div["n_ax_down"], w, color="tab:red", label="axenic down")
            b.bar(div["tp_order"] + w/2, div["n_ax_up"], w, color="tab:orange", label="axenic up")
            b.axhline(0, color="k", lw=0.8)
            b.legend(fontsize=7, ncol=2)
        b.set_title(f"{omics}: significant motility genes (down −, up +)", fontsize=10)
        b.set_xlabel("timepoint order"); b.set_ylabel("# genes")
    fig.suptitle("Fig 1 — HOT1A3 motility (flagella+chemotaxis) over starvation time-course", fontsize=12)
    fig.savefig(FIG / "fig1_motility_timecourse.png", dpi=140); plt.close(fig)
    log(f"[fig] {FIG/'fig1_motility_timecourse.png'}")


def fig_pathways(traj: pd.DataFrame) -> None:
    """Fig 2: tracked-pathway signed scores over time, RNA|protein panels, coculture vs axenic."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), constrained_layout=True)
    for col, omics in enumerate(["rna", "prot"]):
        a = axes[col]
        sub = traj[traj["omics"] == omics]
        cmap = plt.get_cmap("tab10")
        for i, (pw, g) in enumerate(sub.groupby("pathway")):
            for cond, ls in [("coculture", "-"), ("axenic", "--")]:
                gg = g[g["condition"] == cond].sort_values("tp_order")
                if len(gg):
                    a.plot(gg["tp_order"], gg["signed_score"], ls, color=cmap(i % 10),
                           marker="o", label=f"{pw} ({cond})")
        a.axhline(0, color="grey", lw=0.8, ls=":")
        a.set_title(f"{'RNA' if omics=='rna' else 'protein'}: pathway signed score\n(solid=coculture, dashed=axenic)", fontsize=10)
        a.set_xlabel("timepoint order"); a.set_ylabel("signed −log10(p_adjust)")
        a.legend(fontsize=6, ncol=1, loc="best")
    fig.suptitle("Fig 2 — HOT1A3 carbon + motility pathways over starvation time-course", fontsize=12)
    fig.savefig(FIG / "fig2_pathways_timecourse.png", dpi=140); plt.close(fig)
    log(f"[fig] {FIG/'fig2_pathways_timecourse.png'}")


def main() -> None:
    freeze_arms()
    div_rna = motility_divergence("rna")
    div_prot = motility_divergence("prot")
    div = pd.concat([div_rna, div_prot], ignore_index=True)
    div.to_csv(DATA / "motility_divergence_stats.csv", index=False)
    log("\n[motility divergence — coculture vs axenic, paired Wilcoxon on log2FC]")
    log(div.to_string(index=False) if len(div) else "  (no matched timepoints)")

    agree = direction_agreement()
    log(f"\n[RNA vs protein direction agreement (motility set)] {agree}")

    # trend over time (descriptive; low power)
    for omics, d in [("rna", div_rna), ("prot", div_prot)]:
        dd = d.dropna(subset=["tp_order", "median_delta_coc_minus_ax"])
        if len(dd) >= 3:
            rho, p = spearmanr(dd["tp_order"], dd["median_delta_coc_minus_ax"])
            log(f"[trend {omics}] Spearman rho={rho:.2f} p={p:.3f} (n={len(dd)} timepoints — low power)")
        else:
            log(f"[trend {omics}] too few matched timepoints ({len(dd)}) for a trend test")

    traj = pathway_trajectories()
    traj.to_csv(DATA / "pathway_trajectories.csv", index=False)

    fig_motility(div_rna, div_prot)
    fig_pathways(traj)
    (DATA / "01_timecourse.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
