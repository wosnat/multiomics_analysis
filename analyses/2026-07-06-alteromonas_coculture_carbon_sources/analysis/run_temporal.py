"""Temporal overlay, steps 2-5: score the HOT1A3 modules per (arm x timepoint)
for the two starvation arms, build the coculture-vs-axenic side-by-side table +
the coculture_specific flag, run the per-(arm x timepoint) validation checks, and
draw the effect heatmaps. Reuses the committed methods/score_modules.py and the
same module set as the primary run. Artifacts only.

coculture_specific = module called up (q<0.10) in the COCULTURE starvation
trajectory but NOT in the AXENIC one at the same timepoint (difference-of-
starvation-responses; corroboration only, per proposal). Defined only where both
arms share the timepoint label (day 18, day 31, days 60+89); coculture-only
timepoints (day 60, day 89) carry no axenic match.

Outputs (analysis/):
  hot1a3_temporal_module_scores.csv   one row per (module x timepoint)
  temporal_validation.csv             validation-set percentiles per (arm x tp)
  fig_temporal_heatmap.png            coculture / axenic / difference heatmaps
"""
import csv
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
METHODS = os.path.abspath(os.path.join(HERE, "..", "methods"))
CACHE = os.path.join(HERE, "cache")
TCACHE = os.path.join(CACHE, "temporal")
sys.path.insert(0, METHODS)
import score_modules as sm

TABLE = os.path.join(METHODS, "hot1a3_transporter_table.csv")
COC_TPS = ["day 18", "day 31", "day 60", "day 89", "days 60+89"]
AX_TPS = ["day 18", "day 31", "days 60+89"]
Q_CUT = 0.10


def slug(tp):
    return tp.replace(" ", "_").replace("+", "and")


def load_de(arm, tp):
    p = os.path.join(TCACHE, f"{arm}__{slug(tp)}.json")
    return {k: float(v) for k, v in json.load(open(p)).items()}


def score_arm_tp(modules, controls, arm, tp):
    de = load_de(arm, tp)
    res = sm.score_modules(modules, controls, de, scope="genome_wide",
                           n_perm=10000, seed=0)
    return {r["substrate_call"]: r for r in res}, sm.up_percentile(de)


def main():
    modules, controls84 = sm.build_modules_from_csv(
        TABLE, exclude_interaction_coupled_controls=True)
    print(f"modules={len(modules)} controls84={len(controls84)}")

    # score every (arm x timepoint)
    scores = {}   # (arm, tp) -> {substrate: result}
    pcts = {}     # (arm, tp) -> pct_map
    for arm, tps in [("coculture", COC_TPS), ("axenic", AX_TPS)]:
        for tp in tps:
            scores[(arm, tp)], pcts[(arm, tp)] = score_arm_tp(
                modules, controls84, arm, tp)
            print(f"scored {arm} {tp}")

    subs = [m["substrate_call"] for m in modules]
    nsys = {m["substrate_call"]: m["n_systems"] if "n_systems" in m
            else len(m["systems"]) for m in modules}

    # ---- side-by-side table (module x timepoint) ----
    rows = []
    for tp in COC_TPS:                      # union of timepoints (coc superset)
        ax_has = tp in AX_TPS
        for s in subs:
            coc = scores[("coculture", tp)][s]
            ax = scores[("axenic", tp)][s] if ax_has else None
            coc_up = coc["called_up"]
            if ax_has:
                ax_up = ax["called_up"]
                coc_specific = bool(coc_up and not ax_up)
                coc_specific_out = coc_specific
            else:
                ax_up = None
                coc_specific_out = "no_axenic_match"
            rows.append({
                "substrate_call": s, "timepoint": tp, "n_systems": nsys[s],
                "coc_effect": _r(coc["module_effect"]), "coc_q": _r(coc["q_perm"]),
                "coc_called_up": coc_up,
                "ax_effect": _r(ax["module_effect"]) if ax_has else None,
                "ax_q": _r(ax["q_perm"]) if ax_has else None,
                "ax_called_up": ax_up,
                "coculture_specific": coc_specific_out,
            })
    cols = ["substrate_call", "timepoint", "n_systems", "coc_effect", "coc_q",
            "coc_called_up", "ax_effect", "ax_q", "ax_called_up", "coculture_specific"]
    with open(os.path.join(HERE, "hot1a3_temporal_module_scores.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    # coculture-specific counts per common timepoint
    cs_counts = {}
    for tp in AX_TPS:
        cs = [r["substrate_call"] for r in rows
              if r["timepoint"] == tp and r["coculture_specific"] is True]
        cs_counts[tp] = cs

    # ---- validation per (arm x timepoint) ----
    meta = json.load(open(os.path.join(CACHE, "de_meta.json")))
    peptidase = set(json.load(open(os.path.join(CACHE, "peptidase_genes.json"))))
    motility_g = [g for g, m in meta.items() if m.get("gene_category") == "Cell motility"]
    transl_g = [g for g, m in meta.items() if m.get("gene_category") == "Translation"]
    with open(os.path.join(HERE, "temporal_validation.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["arm", "timepoint", "set", "n", "median_up_pct", "expected"])
        for (arm, tp), pct in pcts.items():
            for name, genes, exp in [
                    ("motility_Cell_motility", motility_g, "down"),
                    ("peptidase_protease", peptidase, "up as starvation proceeds"),
                    ("ribosomal_Translation", transl_g, "~neutral")]:
                vals = [pct[g] for g in genes if g in pct]
                med = float(np.median(vals)) if vals else None
                w.writerow([arm, tp, name, len(vals), _r(med), exp])
            glcb = pct.get("ACZ81_13685")
            w.writerow([arm, tp, "glcB_ACZ81_13685", 1, _r(glcb),
                        "up if glycolate (soft)"])

    # ---- heatmap figure ----
    _heatmap(subs, nsys, scores, os.path.join(HERE, "fig_temporal_heatmap.png"))

    # ---- console + summary ----
    print("\ncoculture-specific-up modules per common timepoint:")
    for tp, cs in cs_counts.items():
        print(f"  {tp}: {len(cs)}  {cs}")
    json.dump({
        "n_modules": len(subs),
        "coc_called_up": {tp: [s for s in subs if scores[("coculture", tp)][s]["called_up"]]
                          for tp in COC_TPS},
        "ax_called_up": {tp: [s for s in subs if scores[("axenic", tp)][s]["called_up"]]
                         for tp in AX_TPS},
        "coculture_specific": {tp: cs_counts[tp] for tp in AX_TPS},
    }, open(os.path.join(CACHE, "temporal_summary.json"), "w"), indent=1, default=str)
    print("\nwrote hot1a3_temporal_module_scores.csv, temporal_validation.csv, "
          "fig_temporal_heatmap.png")


def _r(x):
    return round(x, 4) if isinstance(x, (int, float)) else x


def _heatmap(subs, nsys, scores, path):
    # order modules by mean coculture effect (desc)
    def coc_mean(s):
        return np.mean([scores[("coculture", tp)][s]["module_effect"] for tp in COC_TPS])
    order = sorted(subs, key=coc_mean, reverse=True)
    labels = [f"{s} (n={nsys[s]})" for s in order]

    coc_mat = np.array([[scores[("coculture", tp)][s]["module_effect"] for tp in COC_TPS]
                        for s in order])
    ax_mat = np.full((len(order), len(COC_TPS)), np.nan)
    for j, tp in enumerate(COC_TPS):
        if tp in AX_TPS:
            for i, s in enumerate(order):
                ax_mat[i, j] = scores[("axenic", tp)][s]["module_effect"]
    diff_mat = coc_mat - ax_mat

    coc_up = np.array([[scores[("coculture", tp)][s]["called_up"] for tp in COC_TPS]
                       for s in order])
    ax_up = np.full((len(order), len(COC_TPS)), False)
    for j, tp in enumerate(COC_TPS):
        if tp in AX_TPS:
            for i, s in enumerate(order):
                ax_up[i, j] = scores[("axenic", tp)][s]["called_up"]

    fig, axes = plt.subplots(1, 3, figsize=(15, max(7, 0.32 * len(order))),
                             sharey=True)
    for ax, mat, title, cmap, vlim, marks in [
            (axes[0], coc_mat, "coculture effect", "RdBu_r", (0, 1), coc_up),
            (axes[1], ax_mat, "axenic effect", "RdBu_r", (0, 1), ax_up),
            (axes[2], diff_mat, "coculture - axenic", "PuOr_r", (-0.6, 0.6), None)]:
        im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=vlim[0], vmax=vlim[1])
        ax.set_xticks(range(len(COC_TPS)))
        ax.set_xticklabels(COC_TPS, rotation=45, ha="right", fontsize=7)
        ax.set_title(title, fontsize=10)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        if marks is not None:                       # mark called-up cells
            for i in range(mat.shape[0]):
                for j in range(mat.shape[1]):
                    if marks[i, j]:
                        ax.text(j, i, "*", ha="center", va="center",
                                color="black", fontsize=9)
    axes[0].set_yticks(range(len(order)))
    axes[0].set_yticklabels(labels, fontsize=6)
    fig.suptitle("HOT1A3 starvation-vs-exponential module effects "
                 "(* = called up at q<0.10; effect = max system up-percentile)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(path, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
