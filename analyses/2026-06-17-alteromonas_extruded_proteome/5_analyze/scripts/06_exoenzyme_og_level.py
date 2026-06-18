"""Step 5 follow-on: convert the exoenzyme results to OG level and compare the
genome-wide candidate repertoire against what the extruded set captured.

Unit = Alteromonadaceae-level eggnog OG (the step-3 combining key). Reuses the
step-4 mapper (map_genes_to_og) so OG assignment is identical to the catalogue.

Inputs (frozen):
  ../data/exoenzyme_genome_candidates.csv   (1,918 genome-wide candidate genes)
  ../data/exoenzyme_candidates.csv          (9 extruded candidate genes, already OG-mapped)
Outputs (../data/):
  exoenzyme_og_genome.csv        genome-wide exoenzyme OGs (substrate, tier, conservation)
  exoenzyme_og_comparison.csv    by-substrate: genome OGs vs tierA vs extruded-captured
Figures (../figures/):
  exoenzyme_og_level.png

Run: uv run python analyses/2026-06-17-alteromonas_extruded_proteome/5_analyze/scripts/06_exoenzyme_og_level.py
"""

import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "4_methods"))
from extruded_og import map_genes_to_og  # noqa: E402

from multiomics_explorer import GraphConnection  # noqa: E402

DATA = Path(__file__).resolve().parents[1] / "data"
FIG = Path(__file__).resolve().parents[1] / "figures"

TIER_A = "A: degradative + exported"


def primary_substrate(s: str) -> str:
    """A gene may carry several substrate tags; pick the first for OG labelling."""
    return s.split(";")[0] if isinstance(s, str) and s else "unknown"


def og_rollup(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse OG-mapped candidate genes to one row per OG."""
    df = df.dropna(subset=["og_group_id"]).copy()
    df["substrate"] = df["substrates"].map(primary_substrate)
    return (df.groupby("og_group_id")
            .agg(og_product=("og_product", "first"),
                 substrate=("substrate", lambda s: s.mode().iloc[0]),
                 best_tier=("tier", "min"),
                 n_strains=("strain_short", "nunique"),
                 strains=("strain_short", lambda s: ";".join(sorted(set(s)))),
                 n_genes=("locus_tag", "size"))
            .reset_index())


def main() -> None:
    genome = pd.read_csv(DATA / "exoenzyme_genome_candidates.csv")
    extruded = pd.read_csv(DATA / "exoenzyme_candidates.csv")
    print(f"[in] genome candidate genes: {len(genome)} | extruded candidate genes: {len(extruded)}")

    # --- map genome candidates to OGs (batched) ---
    loci = genome["locus_tag"].tolist()
    maps = []
    with GraphConnection() as conn:
        for i in range(0, len(loci), 600):
            maps.append(map_genes_to_og(loci[i:i + 600], conn=conn))
    og_map = pd.concat(maps, ignore_index=True)
    genome = genome.merge(og_map, on="locus_tag", how="left")
    n_no_og = genome["og_group_id"].isna().sum()
    print(f"[map] genome candidates mapped to OG: {len(genome) - n_no_og}; "
          f"strain-unique (no OG): {n_no_og}")

    g_og = og_rollup(genome)
    e_og = og_rollup(extruded)
    captured = set(e_og["og_group_id"])
    g_og["captured_in_extruded"] = g_og["og_group_id"].isin(captured)

    print(f"\n[OG level] genome-wide exoenzyme OGs: {len(g_og)} "
          f"(tier A: {(g_og['best_tier'] == TIER_A).sum()})")
    print(f"[OG level] extruded exoenzyme OGs: {len(e_og)}")
    print(f"[OG level] genome OGs captured in extruded set: {int(g_og['captured_in_extruded'].sum())} "
          f"({100*g_og['captured_in_extruded'].sum()/len(g_og):.1f}%)")

    # --- by-substrate comparison ---
    g_by = g_og.groupby("substrate").agg(
        genome_OGs=("og_group_id", "nunique"),
        genome_tierA_OGs=("best_tier", lambda s: (s == TIER_A).sum()),
        captured_OGs=("captured_in_extruded", "sum")).reset_index()
    e_by = e_og.groupby("substrate").agg(extruded_OGs=("og_group_id", "nunique")).reset_index()
    comp = g_by.merge(e_by, on="substrate", how="left").fillna({"extruded_OGs": 0})
    comp["extruded_OGs"] = comp["extruded_OGs"].astype(int)
    comp = comp.sort_values("genome_OGs", ascending=False)
    print("\n[by substrate — OG level] genome vs extruded")
    print(comp.to_string(index=False))

    # conservation of genome exoenzyme OGs (how many strains share an OG)
    print("\n[conservation] genome exoenzyme OGs by strain count:")
    print(g_og["n_strains"].value_counts().sort_index().to_string())

    # --- OG-level evidence breakdown (degradative source + export evidence) ---
    gm = genome.dropna(subset=["og_group_id"]).copy()
    gm["func_evidence"] = gm["func_evidence"].fillna("")
    gm["export_evidence"] = gm["export_evidence"].fillna("")
    gm["ev_ec"] = gm["func_evidence"].str.contains("EC ", regex=False)
    gm["ev_cazy"] = gm["func_evidence"].str.contains("CAZy", regex=False)
    gm["ev_gomf"] = gm["func_evidence"].str.contains("GO-MF", regex=False)
    gm["ev_pfam"] = gm["func_evidence"].str.contains("Pfam", regex=False)
    gm["ev_signal"] = gm["export_evidence"].str.contains("signal:", regex=False)
    gm["ev_loc"] = gm["export_evidence"].str.contains("loc:", regex=False)
    og_ev = gm.groupby("og_group_id")[
        ["ev_ec", "ev_cazy", "ev_gomf", "ev_pfam", "ev_signal", "ev_loc"]].any()
    deg_src = og_ev[["ev_ec", "ev_cazy", "ev_gomf", "ev_pfam"]].sum()

    def exp_cat(r):
        if r["ev_signal"] and r["ev_loc"]:
            return "signal + localization"
        if r["ev_signal"]:
            return "signal only"
        if r["ev_loc"]:
            return "localization only"
        return "none (tier B)"

    og_ev["export_cat"] = og_ev.apply(exp_cat, axis=1)
    exp_counts = og_ev["export_cat"].value_counts()
    print("\n[degradative annotation source — genome exoenzyme OGs, non-exclusive]")
    print(deg_src.rename({"ev_ec": "EC", "ev_cazy": "CAZy", "ev_gomf": "GO-MF",
                          "ev_pfam": "Pfam"}).to_string())
    print("\n[export evidence — genome exoenzyme OGs]")
    print(exp_counts.to_string())

    # --- figures ---
    fig, ax = plt.subplots(2, 3, figsize=(18, 10))

    # (1) by-substrate: genome vs tierA vs extruded OGs (legend moved right)
    c = comp.sort_values("genome_OGs")
    y = range(len(c)); h = 0.27
    ax[0, 0].barh([i + h for i in y], c["genome_OGs"], height=h, color="#d8a13b", label="genome OGs")
    ax[0, 0].barh(list(y), c["genome_tierA_OGs"], height=h, color="#3b7dd8", label="genome tier A")
    ax[0, 0].barh([i - h for i in y], c["extruded_OGs"], height=h, color="#d83b5e", label="extruded (captured)")
    ax[0, 0].set_yticks(list(y)); ax[0, 0].set_yticklabels(c["substrate"])
    ax[0, 0].set_xlabel("ortholog groups"); ax[0, 0].set_title("Exoenzyme OGs by substrate")
    ax[0, 0].legend(fontsize=8, loc="center left", bbox_to_anchor=(1.0, 0.5))

    # (2) capture funnel at OG level
    funnel = [len(g_og), int((g_og["best_tier"] == TIER_A).sum()), len(e_og)]
    ax[0, 1].bar(["genome\nexoenzyme OGs", "genome\ntier A", "extruded\ncaptured"], funnel,
                 color=["#d8a13b", "#3b7dd8", "#d83b5e"])
    for i, v in enumerate(funnel):
        ax[0, 1].text(i, v + 2, str(v), ha="center")
    ax[0, 1].set_ylabel("ortholog groups"); ax[0, 1].set_title("OG-level capture funnel")

    # (3) conservation of genome exoenzyme OGs
    rec = g_og["n_strains"].value_counts().sort_index()
    ax[0, 2].bar(rec.index.astype(str), rec.values, color="#6a51a3")
    ax[0, 2].set_xlabel("strains sharing the OG (of 7)")
    ax[0, 2].set_ylabel("genome exoenzyme OGs")
    ax[0, 2].set_title("Conservation of genome exoenzyme OGs")

    # (4) degradative annotation source (non-exclusive)
    src_labels = {"ev_ec": "EC", "ev_cazy": "CAZy", "ev_gomf": "GO-MF", "ev_pfam": "Pfam"}
    ds = deg_src.rename(index=src_labels).sort_values()
    ax[1, 0].barh(ds.index, ds.values, color="#2c7fb8")
    for i, v in enumerate(ds.values):
        ax[1, 0].text(v + 1, i, str(int(v)), va="center", fontsize=8)
    ax[1, 0].set_xlabel("genome exoenzyme OGs (non-exclusive)")
    ax[1, 0].set_title("Degradative annotation source")

    # (5) export evidence type
    order = ["signal + localization", "signal only", "localization only", "none (tier B)"]
    ev = exp_counts.reindex(order).fillna(0)
    ax[1, 1].bar(range(len(ev)), ev.values,
                 color=["#238b45", "#74c476", "#bae4b3", "#cccccc"])
    ax[1, 1].set_xticks(range(len(ev)))
    ax[1, 1].set_xticklabels(order, rotation=20, ha="right", fontsize=8)
    for i, v in enumerate(ev.values):
        ax[1, 1].text(i, v + 1, str(int(v)), ha="center", fontsize=8)
    ax[1, 1].set_ylabel("genome exoenzyme OGs"); ax[1, 1].set_title("Export evidence")

    # (6) candidate OGs by tier
    nA = int((g_og["best_tier"] == TIER_A).sum())
    nB = len(g_og) - nA
    ax[1, 2].bar(["tier A\n(exported)", "tier B\n(uncertain)"], [nA, nB],
                 color=["#3b7dd8", "#cccccc"])
    for i, v in enumerate([nA, nB]):
        ax[1, 2].text(i, v + 2, str(v), ha="center")
    ax[1, 2].set_ylabel("genome exoenzyme OGs"); ax[1, 2].set_title("Candidate OGs by tier")

    fig.tight_layout()
    fig.savefig(FIG / "exoenzyme_og_level.png", dpi=300, bbox_inches="tight")
    print("\n[written] figures/exoenzyme_og_level.png")

    g_og.sort_values(["substrate", "n_strains"], ascending=[True, False]).to_csv(
        DATA / "exoenzyme_og_genome.csv", index=False)
    comp.to_csv(DATA / "exoenzyme_og_comparison.csv", index=False)
    print("[written] data/exoenzyme_og_genome.csv, data/exoenzyme_og_comparison.csv")


if __name__ == "__main__":
    main()
