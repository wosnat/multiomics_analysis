"""
Step 5 (analyze) — does Alteromonas regulate motility in coculture vs alone?

HOT1A3 (all genes reported): pathway_enrichment (KEGG level 2 + COG category N),
direction both → read off flagellar assembly (ko02040), bacterial chemotaxis
(ko02030), ribosome baseline (ko03010), and COG-N "Cell motility".

EZ55 (significant-only → ORA invalid): direction-only. Count significant up/down
motility genes (KEGG flagella+chemotaxis set) in coculture, Prochlorococcus
partner vs Synechococcus partner (partner-specificity control).

Inputs: frozen step-2 CSVs. Outputs: data/*.csv, figures/*.png, log.
Run: uv run python analyses/2026-06-15-alteromonas_motility_coculture/5_analyze/scripts/01_run.py
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from multiomics_explorer import pathway_enrichment, differential_expression_by_gene, GraphConnection

ANALYSIS = Path(__file__).resolve().parents[2]
STEP = Path(__file__).resolve().parents[1]
DATA, FIG = STEP / "data", STEP / "figures"
DATA.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
EXP = ANALYSIS / "2_kg_entries" / "data" / "coculture_experiments.csv"
GENES = ANALYSIS / "2_kg_entries" / "data" / "motility_genes.csv"

WATCH = {"kegg.pathway:ko02040": "Flagellar assembly",
         "kegg.pathway:ko02030": "Bacterial chemotaxis",
         "kegg.pathway:ko03010": "Ribosome (baseline)",
         "cog.category:N": "COG-N Cell motility (broad)"}

log_lines: list[str] = []
def log(m): print(m); log_lines.append(m)


def main() -> None:
    exps = list(csv.DictReader(EXP.open()))
    genes = pd.read_csv(GENES)
    ez55_motility = set(genes[(genes.strain == "EZ55") &
                              (genes.in_kegg_flagella_chemotaxis == 1)]["locus_tag"])

    hot = [e for e in exps if e["strain"] == "HOT1A3"]
    ez = [e for e in exps if e["strain"] == "EZ55"]

    # ---------- HOT1A3 enrichment ----------
    enr_rows = []
    with GraphConnection() as conn:
        for e in hot:
            eid = e["experiment_id"]
            for ont, lvl in [("kegg", 2), ("cog_category", 0)]:
                res = pathway_enrichment(organism="HOT1A3", experiment_ids=[eid],
                                         ontology=ont, level=lvl, direction="both", conn=conn)
                df = res.results
                hit = df[df["term_id"].isin(WATCH)]
                hi = "hi-inoc" if "high" in (e["treatment"] or "").lower() else ""
                label = f"{e['coculture_partner'].split()[-1]} {hi}".strip() + \
                        f"\n{e['publication_doi'].split('/')[-1][:10]}"
                for r in hit.itertuples():
                    direction = r.cluster.split("|")[-1]
                    enr_rows.append({
                        "experiment_id": eid, "exp_label": label,
                        "partner": e["coculture_partner"], "publication": e["publication_doi"],
                        "timepoint": r.cluster.split("|")[-2], "direction": direction,
                        "term": WATCH[r.term_id], "count": r.count, "bg_count": r.bg_count,
                        "fold_enrichment": round(r.fold_enrichment, 3),
                        "pvalue": round(r.pvalue, 4), "p_adjust": round(r.p_adjust, 4),
                    })

        # ---------- EZ55 direction-only ----------
        ez_rows = []
        for e in ez:
            eid = e["experiment_id"]
            de = differential_expression_by_gene(organism="EZ55", experiment_ids=[eid],
                                                  limit=None, conn=conn)
            res = de["results"]
            mot = [g for g in res if g["locus_tag"] in ez55_motility]
            up = sum(1 for g in mot if g["expression_status"] == "significant_up")
            down = sum(1 for g in mot if g["expression_status"] == "significant_down")
            tot_up = sum(1 for g in res if g["expression_status"] == "significant_up")
            tot_down = sum(1 for g in res if g["expression_status"] == "significant_down")
            ez_rows.append({
                "partner": e["coculture_partner"],
                "partner_genus": e["partner_genus"],
                "treatment": e["treatment"],
                "motility_up": up, "motility_down": down,
                "genome_up": tot_up, "genome_down": tot_down,
                "motility_set_size": len(ez55_motility),
            })

    pd.DataFrame(enr_rows).to_csv(DATA / "hot1a3_enrichment.csv", index=False)
    pd.DataFrame(ez_rows).to_csv(DATA / "ez55_motility_direction.csv", index=False)

    log("[HOT1A3 enrichment — motility + baseline rows across experiments]")
    edf = pd.DataFrame(enr_rows)
    log(edf.to_string(index=False))
    log("\n[EZ55 motility direction — Prochlorococcus vs Synechococcus partner]")
    zdf = pd.DataFrame(ez_rows)
    log(zdf.to_string(index=False))

    # ---------- figures ----------
    # fig1: HOT1A3 — NET signed motility/ribosome genes (up - down) per experiment.
    # Shows the partner-dependent direction flip clearly.
    terms = ["Bacterial chemotaxis", "Flagellar assembly", "Ribosome (baseline)"]
    colors = {"Bacterial chemotaxis": "#d9534f", "Flagellar assembly": "#e8a33d", "Ribosome (baseline)": "#888"}
    exp_order = edf.drop_duplicates("experiment_id")["experiment_id"].tolist()
    labels = {r.experiment_id: r.exp_label for r in edf.itertuples()}
    fig, ax = plt.subplots(figsize=(9, 4.8))
    nexp = len(exp_order); width = 0.8 / len(terms)
    for ti, term in enumerate(terms):
        nets = []
        for eid in exp_order:
            g = edf[(edf.experiment_id == eid) & (edf.term == term)]
            up = g[g.direction == "up"]["count"].sum()
            down = g[g.direction == "down"]["count"].sum()
            nets.append(up - down)
        ax.bar([x + ti * width for x in range(nexp)], nets, width,
               label=term, color=colors[term], edgecolor="k", linewidth=0.3)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks([x + width for x in range(nexp)])
    ax.set_xticklabels([labels[e] for e in exp_order], fontsize=8)
    ax.set_ylabel("net significant genes in coculture\n(up minus down)")
    ax.set_title("HOT1A3: net motility direction in coculture vs alone, by experiment/partner\n"
                 "(positive = up in coculture; ribosome baseline ~ 0)", fontsize=9)
    ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "fig1_hot1a3_motility.png", dpi=300); plt.close(fig)

    # fig2: EZ55 partner-specificity — motility up/down by partner genus
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, r in enumerate(ez_rows):
        lab = f"{r['partner'].split()[-1]}\n({r['partner_genus'][:5]})"
        ax.bar(i, r["motility_up"], 0.6, color="#4a90d9", edgecolor="k", linewidth=0.3)
        ax.bar(i, -r["motility_down"], 0.6, color="#d9534f", edgecolor="k", linewidth=0.3)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_xticks(range(len(ez_rows)))
    ax.set_xticklabels([f"{r['partner'].split()[-1]}\n{r['partner_genus'][:4]}\n{r['treatment'].split('at ')[-1]}" for r in ez_rows], fontsize=7)
    ax.set_ylabel("EZ55 motility genes (up=+ blue, down=- red)")
    ax.set_title("EZ55 motility direction in coculture, by partner\n(significant-only; direction cross-check + partner specificity)", fontsize=9)
    fig.tight_layout(); fig.savefig(FIG / "fig2_ez55_partner.png", dpi=300); plt.close(fig)

    log(f"\n[outputs] hot1a3_enrichment.csv ({len(enr_rows)}), ez55_motility_direction.csv ({len(ez_rows)}); fig1, fig2")
    (DATA / "01_run.log").write_text("\n".join(log_lines) + "\n")


if __name__ == "__main__":
    main()
