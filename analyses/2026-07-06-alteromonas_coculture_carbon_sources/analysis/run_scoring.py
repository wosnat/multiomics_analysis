"""Analysis milestone: score the transporter modules on the primary experiment
(HOT1A3 + MED4 coculture-vs-axenic, day 11), run the validation-set percentile
checks, and draw the figures. Imports the COMMITTED scoring code from
methods/score_modules.py (does not reimplement it). Artifacts only.

Outputs (analysis/):
  hot1a3_day11_module_scores.csv        one row per module (sorted by effect)
  hot1a3_day11_module_scores_per_system.csv   per-system percentile distribution
  validation_checks.csv                 validation-set percentile summaries
  fig_module_catalog.png                ranked module effects, called-up marked
  fig_validation_distributions.png      motility/ribosomal/peptidase/genome
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
ANALYSIS_DIR = HERE
METHODS = os.path.abspath(os.path.join(HERE, "..", "methods"))
CACHE = os.path.join(HERE, "cache")
sys.path.insert(0, METHODS)
import score_modules as sm   # the committed scoring module

TABLE = os.path.join(METHODS, "hot1a3_transporter_table.csv")


def pct_summary(values):
    a = np.asarray([v for v in values if v is not None], dtype=float)
    if len(a) == 0:
        return dict(n=0, median=None, mean=None, q25=None, q75=None, min=None, max=None)
    return dict(n=int(len(a)), median=float(np.median(a)), mean=float(np.mean(a)),
                q25=float(np.percentile(a, 25)), q75=float(np.percentile(a, 75)),
                min=float(a.min()), max=float(a.max()))


def main():
    de = {k: float(v) for k, v in json.load(open(os.path.join(CACHE, "de_table.json"))).items()}
    meta = json.load(open(os.path.join(CACHE, "de_meta.json")))
    peptidase = set(json.load(open(os.path.join(CACHE, "peptidase_genes.json"))))

    pct = sm.up_percentile(de)     # locus_tag -> up-percentile (0=down,1=up)

    # ---- build modules + control sets ----
    modules, controls84 = sm.build_modules_from_csv(
        TABLE, exclude_interaction_coupled_controls=True)   # primary control set
    _, controls100 = sm.build_modules_from_csv(
        TABLE, exclude_interaction_coupled_controls=False)  # comparison set
    print(f"modules={len(modules)}  controls84={len(controls84)}  controls100={len(controls100)}")

    # ---- score (primary control set = 84) ----
    res84 = sm.score_modules(modules, controls84, de, scope="genome_wide",
                             n_perm=10000, seed=0)
    res100 = sm.score_modules(modules, controls100, de, scope="genome_wide",
                              n_perm=10000, seed=0)
    pctrl100 = {r["substrate_call"]: r["p_vs_control"] for r in res100}

    res84.sort(key=lambda r: (r["module_effect"] is None, -(r["module_effect"] or 0)))
    n_called = sum(1 for r in res84 if r["called_up"])

    # ---- write module scores ----
    cols = ["substrate_call", "resolution_level", "confidence_flag", "n_systems",
            "n_systems_detected", "module_effect", "p_perm", "q_perm", "called_up",
            "p_vs_control", "p_vs_control_100"]
    with open(os.path.join(ANALYSIS_DIR, "hot1a3_day11_module_scores.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in res84:
            w.writerow({
                "substrate_call": r["substrate_call"],
                "resolution_level": r["resolution_level"],
                "confidence_flag": r["confidence_flag"],
                "n_systems": r["n_systems"],
                "n_systems_detected": r["n_systems_detected"],
                "module_effect": round(r["module_effect"], 6) if r["module_effect"] is not None else None,
                "p_perm": round(r["p_perm"], 6) if r["p_perm"] is not None else None,
                "q_perm": round(r["q_perm"], 6) if r["q_perm"] is not None else None,
                "called_up": r["called_up"],
                "p_vs_control": round(r["p_vs_control"], 6) if r["p_vs_control"] is not None else None,
                "p_vs_control_100": round(pctrl100.get(r["substrate_call"]), 6)
                if pctrl100.get(r["substrate_call"]) is not None else None,
            })

    # ---- per-system distribution ----
    with open(os.path.join(ANALYSIS_DIR, "hot1a3_day11_module_scores_per_system.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["substrate_call", "system_index", "locus_tags",
                    "n_genes_used", "system_percentile"])
        for r in res84:
            for i, psd in enumerate(r["per_system"]):
                w.writerow([r["substrate_call"], i, ";".join(psd["locus_tags"]),
                            psd["n_genes_used"],
                            round(psd["percentile"], 6) if psd["percentile"] is not None else None])

    # ---- validation checks ----
    motility = [pct[g] for g, m in meta.items()
                if m.get("gene_category") == "Cell motility" and g in pct]
    translation = [pct[g] for g, m in meta.items()
                   if m.get("gene_category") == "Translation" and g in pct]
    pept = [pct[g] for g in peptidase if g in pct]
    genome = list(pct.values())
    # inorganic-control importer SYSTEM percentiles (median of subunits)
    ctrl_sys = [sm.system_percentile(c["locus_tags"], pct) for c in controls84]
    ctrl_sys = [x for x in ctrl_sys if x is not None]
    glcb = pct.get("ACZ81_13685")
    glycolate_module = [r for r in res84 if "glycolate" in r["substrate_call"].lower()]

    vsets = [
        ("motility_Cell_motility", motility, "down (low percentiles)"),
        ("ribosomal_Translation", translation, "~neutral (~0.5)"),
        ("peptidase_protease", pept, "up (high percentiles)"),
        ("inorganic_control_systems", ctrl_sys, "not high"),
        ("whole_genome_baseline", genome, "~0.5 by construction"),
    ]
    with open(os.path.join(ANALYSIS_DIR, "validation_checks.csv"),
              "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["validation_set", "n", "median_percentile", "mean_percentile",
                    "q25", "q75", "min", "max", "expected_direction"])
        for name, vals, exp in vsets:
            s = pct_summary(vals)
            w.writerow([name, s["n"],
                        _r(s["median"]), _r(s["mean"]), _r(s["q25"]), _r(s["q75"]),
                        _r(s["min"]), _r(s["max"]), exp])
        # single-gene glcB
        w.writerow(["glcB_ACZ81_13685", 1, _r(glcb), _r(glcb), _r(glcb), _r(glcb),
                    _r(glcb), _r(glcb),
                    "up if glycolate a source (soft; absence uninformative)"])

    # ---- figures ----
    _fig_catalog(res84, os.path.join(ANALYSIS_DIR, "fig_module_catalog.png"))
    _fig_validation(motility, translation, pept, ctrl_sys, genome,
                    os.path.join(ANALYSIS_DIR, "fig_validation_distributions.png"))

    # ---- console manifest ----
    print(f"\nmodules scored: {len(res84)}; called up (q<0.10): {n_called}")
    print("glcB ACZ81_13685 percentile:", _r(glcb),
          "| glycolate module present:", bool(glycolate_module))
    for name, vals, _ in vsets:
        s = pct_summary(vals)
        print(f"  {name}: n={s['n']} median_pct={_r(s['median'])}")
    # stash a small json summary for the manifest
    json.dump({
        "n_modules": len(res84), "n_called_up": n_called,
        "controls84": len(controls84), "controls100": len(controls100),
        "glcB_percentile": glcb, "glycolate_module": bool(glycolate_module),
        "validation": {name: pct_summary(vals) for name, vals, _ in vsets},
        "top_modules": [(r["substrate_call"], _r(r["module_effect"]),
                         _r(r["q_perm"]), r["called_up"], r["n_systems"])
                        for r in res84[:12]],
    }, open(os.path.join(CACHE, "scoring_summary.json"), "w"), indent=1, default=str)
    print("\nwrote module_scores, per_system, validation_checks, 2 figures.")


def _r(x):
    return round(x, 4) if isinstance(x, (int, float)) else x


def _fig_catalog(res, path):
    r = [x for x in res if x["module_effect"] is not None]
    r = sorted(r, key=lambda x: x["module_effect"])
    labels = [f'{x["substrate_call"]} (n={x["n_systems"]})' for x in r]
    eff = [x["module_effect"] for x in r]
    colors = ["#c44e52" if x["called_up"] else "#4c72b0" for x in r]
    fig, ax = plt.subplots(figsize=(8, max(6, 0.28 * len(r))))
    ax.barh(range(len(r)), eff, color=colors)
    ax.set_yticks(range(len(r)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.axvline(0.5, color="grey", ls=":", lw=1, label="genome median (0.5)")
    ax.set_xlabel("module effect (max system up-percentile)")
    ax.set_xlim(0, 1)
    ax.set_title("HOT1A3 day-11 coculture-vs-axenic: organic-C importer module catalog\n"
                 "(red = called up at q<0.10; blue = not)")
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def _fig_validation(motility, translation, pept, ctrl, genome, path):
    data = [motility, translation, pept, ctrl, genome]
    labels = [f"motility\n(n={len(motility)})", f"ribosomal\n(n={len(translation)})",
              f"peptidase\n(n={len(pept)})", f"inorg. ctrl sys\n(n={len(ctrl)})",
              f"whole genome\n(n={len(genome)})"]
    fig, ax = plt.subplots(figsize=(9, 5))
    parts = ax.violinplot(data, showmedians=True, showextrema=False)
    for pc in parts["bodies"]:
        pc.set_alpha(0.5)
    ax.axhline(0.5, color="grey", ls=":", lw=1)
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("up-percentile (0 = most down, 1 = most up)")
    ax.set_ylim(0, 1)
    ax.set_title("Validation-set up-percentile distributions\n"
                 "(HOT1A3 day-11 coculture-vs-axenic; dotted line = genome median 0.5)")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    main()
