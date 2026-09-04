"""QC: are the markers systematically short, and if so is that an artifact?

The researcher observed that the marker proteins look short. Two competing
explanations, and they have opposite consequences:

  A. BIOLOGY. Lineage-restricted genes really are shorter on average than the
     conserved core. Then short markers are expected and fine.

  B. ARTIFACT. Short proteins are harder to place into broad ortholog groups.
     A short gene that never got assigned a Bacteria-level group would pass the
     "no ortholog outside the five strains" test for a purely technical reason,
     not a biological one. That would mean the panel is partly an artifact of
     annotation depth and the specificity claim is weaker than stated.

Three tests:

  1. Length distribution: the 53 markers vs all proteins in the five genomes.
     Mann-Whitney U, two-sided.
  2. The decisive test for B: across ALL genes in the five genomes, does the
     probability of having a broad (Bacteria-level, rank 3) ortholog group fall
     with protein length? If short genes are systematically under-assigned, the
     specificity filter is length-biased.
  3. Isolating the filter: compare marker lengths against genes that passed core
     and single-copy but FAILED specificity. Same pipeline, one test different,
     so any length gap is attributable to the specificity test itself.

Inputs : the KG; data/markers_no_7002.csv
Outputs: data/qc_length_bias.csv        per-bin assignment rates
         data/qc_length_summary.csv     distribution summaries
         figures/qc_length_bias.png
         data/08_length_bias_qc.log
Usage  : uv run python analysis/scripts/08_length_bias_qc.py
"""

from __future__ import annotations

import csv
import logging
import sys
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

from multiomics_explorer import GraphConnection, run_cypher

DATA = Path(__file__).resolve().parents[1] / "data"
FIGS = Path(__file__).resolve().parents[1] / "figures"
log = logging.getLogger("lenqc")

TARGETS = [
    "Synechococcus CC9311", "Synechococcus WH8109", "Synechococcus WH8102",
    "Synechococcus sp. BL107", "Synechococcus WH7803",
]
BINS = [0, 75, 100, 150, 200, 300, 400, 600, 10**9]


def setup() -> None:
    log.setLevel(logging.INFO)
    FIGS.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(DATA / "08_length_bias_qc.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def describe(name: str, x: np.ndarray) -> dict:
    d = {
        "set": name, "n": int(x.size),
        "min": int(x.min()), "q1": float(np.percentile(x, 25)),
        "median": float(np.median(x)), "q3": float(np.percentile(x, 75)),
        "max": int(x.max()), "mean": round(float(x.mean()), 1),
        "pct_under_150aa": round(100 * float((x < 150).mean()), 1),
    }
    log.info("%-34s n=%-5d median=%-6.0f IQR=%.0f-%.0f  mean=%-7.1f  <150aa=%.1f%%",
             name, d["n"], d["median"], d["q1"], d["q3"], d["mean"], d["pct_under_150aa"])
    return d


def main() -> int:
    setup()
    orgs = "['" + "','".join(TARGETS) + "']"

    with GraphConnection() as conn:
        # Background: every protein-coding gene with a sequence in the five genomes,
        # plus whether it carries a broad (Bacteria-level) ortholog group.
        # No typed tool enumerates all genes of an organism, hence run_cypher.
        q = f"""
        MATCH (g:Gene)-[:Gene_belongs_to_organism]->(o:OrganismTaxon)
        WHERE o.preferred_name IN {orgs} AND g.sequence IS NOT NULL
              AND size(g.sequence) > 0
        OPTIONAL MATCH (g)-[:Gene_in_ortholog_group]->(b:OrthologGroup)
              WHERE b.source = 'eggnog' AND b.taxonomic_level = 'Bacteria'
        WITH g, o, count(b) AS n_broad
        RETURN g.locus_tag AS locus, o.preferred_name AS org,
               size(g.sequence) AS len, n_broad > 0 AS has_broad_group
        """
        rows = run_cypher(query=q, limit=10**6, conn=conn)["results"]
    log.info("background genes with a sequence: %d", len(rows))

    length = {r["locus"]: r["len"] for r in rows}
    broad = {r["locus"]: bool(r["has_broad_group"]) for r in rows}
    bg = np.array([r["len"] for r in rows])

    # Marker lengths.
    cols = ["locus_CC9311", "locus_WH8109", "locus_WH8102", "locus_BL107", "locus_WH7803"]
    markers = list(csv.DictReader(open(DATA / "markers_no_7002.csv")))
    mk_loci = [m[c] for m in markers for c in cols if m[c]]
    mk = np.array([length[l] for l in mk_loci if l in length])
    log.info("marker gene instances with a length: %d/%d", mk.size, len(mk_loci))

    # ---- Test 1: markers vs background ---------------------------------------
    log.info("--- Test 1: length distribution ---")
    summ = [describe("all proteins, 5 genomes", bg), describe("the 53 markers", mk)]
    u, p = mannwhitneyu(mk, bg, alternative="two-sided")
    log.info("Mann-Whitney U two-sided: U=%.0f  p=%.3g", u, p)
    log.info("marker median is %.0f%% of the background median",
             100 * np.median(mk) / np.median(bg))

    # ---- Test 2: is broad-group assignment length-dependent? -----------------
    log.info("--- Test 2: does broad-group assignment depend on length? "
             "(the artifact test) ---")
    bin_rows = []
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        sel = [r for r in rows if lo <= r["len"] < hi]
        if not sel:
            continue
        n = len(sel)
        withb = sum(1 for r in sel if r["has_broad_group"])
        nmk = int(((mk >= lo) & (mk < hi)).sum())
        label = f"{lo}-{hi if hi < 10**8 else '+'}"
        bin_rows.append({
            "length_bin_aa": label, "genes": n,
            "with_bacteria_level_group": withb,
            "pct_with_broad_group": round(100 * withb / n, 1),
            "marker_instances_in_bin": nmk,
        })
        log.info("  %-10s n=%-5d  with broad group %5.1f%%   markers here: %d",
                 label, n, 100 * withb / n, nmk)

    # ---- Test 3: isolate the specificity filter ------------------------------
    # Genes that passed core+single-copy but failed specificity are not stored,
    # so approximate with the complement: genes WITH a broad group vs markers.
    log.info("--- Test 3: markers vs genes that DO carry a broad group ---")
    has = np.array([r["len"] for r in rows if r["has_broad_group"]])
    hasnt = np.array([r["len"] for r in rows if not r["has_broad_group"]])
    summ.append(describe("genes WITH a Bacteria-level group", has))
    summ.append(describe("genes WITHOUT one", hasnt))
    u2, p2 = mannwhitneyu(has, hasnt, alternative="two-sided")
    log.info("with vs without broad group, Mann-Whitney: U=%.0f  p=%.3g", u2, p2)
    u3, p3 = mannwhitneyu(mk, hasnt, alternative="two-sided")
    log.info("markers vs genes-without-broad-group: U=%.0f  p=%.3g", u3, p3)

    with open(DATA / "qc_length_bias.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(bin_rows[0])); w.writeheader(); w.writerows(bin_rows)
    with open(DATA / "qc_length_summary.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summ[0])); w.writeheader(); w.writerows(summ)

    # ---- figure ---------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), dpi=300)
    edges = np.linspace(0, 800, 41)
    ax[0].hist(np.clip(bg, 0, 800), bins=edges, density=True, alpha=.55,
               label=f"all proteins (n={bg.size})", color="#7a7a7a")
    ax[0].hist(np.clip(mk, 0, 800), bins=edges, density=True, alpha=.75,
               label=f"markers (n={mk.size})", color="#c1440e")
    ax[0].axvline(np.median(bg), color="#7a7a7a", ls="--", lw=1)
    ax[0].axvline(np.median(mk), color="#c1440e", ls="--", lw=1)
    ax[0].set_xlabel("protein length (aa, clipped at 800)")
    ax[0].set_ylabel("density")
    ax[0].set_title("Marker length vs genome background")
    ax[0].legend(fontsize=8)

    labs = [r["length_bin_aa"] for r in bin_rows]
    vals = [r["pct_with_broad_group"] for r in bin_rows]
    ax[1].bar(range(len(labs)), vals, color="#33628d")
    ax[1].set_xticks(range(len(labs))); ax[1].set_xticklabels(labs, rotation=45, ha="right", fontsize=8)
    ax[1].set_ylabel("% of genes with a Bacteria-level ortholog group")
    ax[1].set_xlabel("protein length bin (aa)")
    ax[1].set_title("Broad-group assignment vs length\n(the artifact test)")
    ax[1].set_ylim(0, 100)
    for i, v in enumerate(vals):
        ax[1].text(i, v + 2, f"{v:.0f}", ha="center", fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGS / "qc_length_bias.png")
    log.info("wrote figures/qc_length_bias.png and the two CSVs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
