"""
Step 5b (Analyze) — controls for the carbon-provision read, motility direction only.

These are DIFFERENT studies/platforms from HOT1A3, and most are significant-only
tables, so per statistical-rigor.md they are DIRECTION-ONLY: we compare up/down
counts and the down-fraction of significant motility genes, never magnitudes or
p-values across studies. Each contrast means something different (noted in the
table); the comparison is a coarse "is motility predominantly down here?" read.

Controls:
  - Partner specificity (EZ55, RNA): coculture vs axenic with Prochlorococcus
    (MIT9312) vs Synechococcus (CC9311, WH8102), 2 pCO2 levels each. Prochlorococcus-
    specific vs generic photoautotroph cross-feeding (+ pCO2 robustness).
  - Darkness (MIT1002, RNA): darkness/diel — is motility-down a general stress/
    dormancy response rather than carbon-specific?
  - Glucose-fed reference (MarRef, proteomics): organic-C added directly — what
    "fed" looks like (sparse; proteomics, tiny significant counts).
Plus HOT1A3 reference rows (from 5a frozen motility CSVs + step-4 MED4 snapshot).

Fig 3: motility down-fraction per contrast, grouped by carbon level x coculture,
coloured by partner genus, labelled by treatment.

Run: uv run python analyses/2026-06-15-alteromonas_motility_coculture/5_analyze/scripts/02_controls.py
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from multiomics_explorer import genes_by_ontology, differential_expression_by_gene, to_dataframe, GraphConnection

ANALYSIS = Path(__file__).resolve().parents[1]
DATA = ANALYSIS / "data"; FIG = ANALYSIS / "figures"
DATA.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
log_lines: list[str] = []
def log(m): print(m); log_lines.append(str(m))

KEGG_MOTILITY = ["kegg.pathway:ko02040", "kegg.pathway:ko02030"]
S = "10.1038/s43705-022-00197-2"

# control contrasts: (label, organism, experiment_id, partner_genus, carbon_level, coculture, treatment)
CONTROLS = [
    ("EZ55 +Pro MIT9312 400", "EZ55", f"{S}_coculture_prochlorococcus_mit9312_at_400_ez55_rnaseq", "Prochlorococcus", "low", "yes", "coculture vs axenic, 400ppm"),
    ("EZ55 +Pro MIT9312 800", "EZ55", f"{S}_coculture_prochlorococcus_mit9312_at_800_ez55_rnaseq", "Prochlorococcus", "low", "yes", "coculture vs axenic, 800ppm"),
    ("EZ55 +Syn CC9311 400", "EZ55", f"{S}_coculture_synechococcus_cc9311_at_400_ez55_rnaseq", "Synechococcus", "low", "yes", "coculture vs axenic, 400ppm"),
    ("EZ55 +Syn CC9311 800", "EZ55", f"{S}_coculture_synechococcus_cc9311_at_800_ez55_rnaseq", "Synechococcus", "low", "yes", "coculture vs axenic, 800ppm"),
    ("EZ55 +Syn WH8102 400", "EZ55", f"{S}_coculture_synechococcus_wh8102_at_400_ez55_rnaseq", "Synechococcus", "low", "yes", "coculture vs axenic, 400ppm"),
    ("EZ55 +Syn WH8102 800", "EZ55", f"{S}_coculture_synechococcus_wh8102_at_800_ez55_rnaseq", "Synechococcus", "low", "yes", "coculture vs axenic, 800ppm"),
    ("MIT1002 darkness (diel)", "MIT1002", "10.1093/ismeco/ycae131_darkness_darktolerant_coculture_under_1311_mit1002_rnaseq", "none", "low", "no", "dark-tolerant vs parental, diel"),
    ("MIT1002 extended darkness", "MIT1002", "10.1128/mSystems.00040-18_darkness_extended_darkness_mit1002_rnaseq", "none", "low", "no", "extended darkness vs diel"),
    ("MarRef +glucose in MED4 (dark,5mM)", "Alteromonas (MarRef v6)", "10.1128/spectrum.03275-22_dark_high_glucose_alt_in_med4_proteomics", "Prochlorococcus", "rich", "yes", "+glucose vs no glucose"),
    ("MarRef +glucose in SS120 (dark,5mM)", "Alteromonas (MarRef v6)", "10.1128/spectrum.03275-22_dark_high_glucose_alt_in_ss120_proteomics", "Prochlorococcus", "rich", "yes", "+glucose vs no glucose"),
]


def motility_tags(organism: str, conn) -> list[str]:
    r = genes_by_ontology(ontology="kegg", term_ids=KEGG_MOTILITY, organism=organism,
                          min_gene_set_size=1, limit=None, conn=conn)
    return [row["locus_tag"] for row in r.get("results", [])]


def direction_counts(organism: str, eid: str, tags: list[str], conn) -> dict:
    de = differential_expression_by_gene(organism=organism, locus_tags=tags,
                                         experiment_ids=[eid], conn=conn)
    df = to_dataframe(de)
    if not len(df) or "expression_status" not in df:
        return {"n_set": len(tags), "n_rows": 0, "n_up": 0, "n_down": 0, "down_fraction": np.nan}
    n_up = int((df["expression_status"] == "significant_up").sum())
    n_down = int((df["expression_status"] == "significant_down").sum())
    dfrac = (n_down / (n_up + n_down)) if (n_up + n_down) else np.nan
    return {"n_set": len(tags), "n_rows": len(df), "n_up": n_up, "n_down": n_down,
            "down_fraction": dfrac}


def hot1a3_reference_rows() -> list[dict]:
    """Reference rows from 5a (RNA starvation, aggregated over timepoints) +
    step-4 MED4 snapshot — for the low-carbon side of Fig 3."""
    rows = []
    for arm, cocult, partner in [("coculture", "yes", "Prochlorococcus"), ("axenic", "no", "none")]:
        f = DATA / f"hot1a3_rna_{arm}_motility_genes_de.csv"
        if f.exists():
            df = pd.read_csv(f)
            n_up = int((df["expression_status"] == "significant_up").sum())
            n_down = int((df["expression_status"] == "significant_down").sum())
            rows.append({"label": f"HOT1A3 starvation {arm} (RNA)", "organism": "HOT1A3",
                         "partner_genus": partner, "carbon_level": "low", "coculture": cocult,
                         "treatment": "starvation vs exp (all tp)", "n_set": None,
                         "n_rows": len(df), "n_up": n_up, "n_down": n_down,
                         "down_fraction": (n_down/(n_up+n_down)) if (n_up+n_down) else np.nan})
    snap = (ANALYSIS.parent / "4_methods" / "data" / "med4_snapshot_motility_genes_de.csv")
    if snap.exists():
        df = pd.read_csv(snap)
        n_up = int((df["expression_status"] == "significant_up").sum())
        n_down = int((df["expression_status"] == "significant_down").sum())
        rows.append({"label": "HOT1A3 +MED4 snapshot (RNA, exp)", "organism": "HOT1A3",
                     "partner_genus": "Prochlorococcus", "carbon_level": "low", "coculture": "yes",
                     "treatment": "coculture vs axenic, day 11", "n_set": None, "n_rows": len(df),
                     "n_up": n_up, "n_down": n_down,
                     "down_fraction": (n_down/(n_up+n_down)) if (n_up+n_down) else np.nan})
    return rows


def fig3(df: pd.DataFrame) -> None:
    d = df[df["n_up"] + df["n_down"] > 0].copy()
    d["group"] = d["carbon_level"] + "-C / coc=" + d["coculture"].astype(str)
    d = d.sort_values(["carbon_level", "coculture", "partner_genus"])
    colors = {"Prochlorococcus": "tab:green", "Synechococcus": "tab:orange", "none": "tab:grey"}
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    y = np.arange(len(d))
    ax.barh(y, d["down_fraction"], color=[colors.get(p, "tab:blue") for p in d["partner_genus"]])
    ax.axvline(0.5, color="k", lw=0.8, ls=":")
    ax.set_yticks(y); ax.set_yticklabels(d["label"], fontsize=8)
    for i, (_, r) in enumerate(d.iterrows()):
        ax.annotate(f"  {r['carbon_level']}-C, coc={r['coculture']}  (down {r['n_down']}/{r['n_down']+r['n_up']})",
                    (max(r['down_fraction'], 0), i), fontsize=7, va="center")
    ax.set_xlabel("down-fraction of significant motility genes (n_down / (n_down+n_up))")
    ax.set_xlim(0, 1.25)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors.values()]
    ax.legend(handles, colors.keys(), title="partner", fontsize=8, loc="lower right")
    ax.set_title("Fig 3 — motility direction across conditions (direction-only; different contrasts/studies)\n"
                 "dotted line = 50% (no net direction); >0.5 = predominantly down", fontsize=11)
    fig.savefig(FIG / "fig3_motility_controls.png", dpi=140); plt.close(fig)
    log(f"[fig] {FIG/'fig3_motility_controls.png'}")


def main() -> None:
    rows = []
    with GraphConnection() as conn:
        tag_cache = {}
        for label, organism, eid, partner, carbon, cocult, treatment in CONTROLS:
            if organism not in tag_cache:
                tag_cache[organism] = motility_tags(organism, conn)
            counts = direction_counts(organism, eid, tag_cache[organism], conn)
            rows.append({"label": label, "organism": organism, "partner_genus": partner,
                         "carbon_level": carbon, "coculture": cocult, "treatment": treatment, **counts})
            log(f"[{label}] set={counts['n_set']} rows={counts['n_rows']} "
                f"up={counts['n_up']} down={counts['n_down']} down_frac={counts['down_fraction']}")
    rows += hot1a3_reference_rows()
    df = pd.DataFrame(rows)
    df.to_csv(DATA / "controls_motility_direction.csv", index=False)
    log("\n[controls motility direction table]")
    log(df[["label", "carbon_level", "coculture", "partner_genus", "n_up", "n_down", "down_fraction"]].to_string(index=False))
    fig3(df)
    (DATA / "02_controls.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
