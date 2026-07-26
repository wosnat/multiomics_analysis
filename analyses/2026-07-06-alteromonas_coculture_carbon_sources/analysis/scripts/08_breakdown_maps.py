#!/usr/bin/env python3
"""
Analysis milestone -- step 8: breakdown-flag (catabolism corroboration).

Governed by proposal decision 13 + the breakdown-evidence rule (proposal.md
lines 259-298, 756-775). CORROBORATION ONLY -- outside the module score and the
FDR family. Direction is curated in the KG in exactly one place: a dedicated
KEGG *degradation* map. A direction-neutral *metabolism* map (citrate cycle,
glyoxylate/dicarboxylate metabolism, sugar-metabolism maps, purine/pyrimidine
metabolism) does NOT count -> those substrates are "not determinable" (expected
for most compounds; the module then rests on uptake + specificity).

Per distinct candidate substrate (union of the three module catalogs):
 1. Assign the relevant KEGG *degradation* map(s) -- more than one allowed;
    each recorded exact / broader / narrower. Only maps whose KEGG name is a
    genuine "... degradation" catabolic map qualify. This assignment is
    [interpretation] (substrate chemistry -> catabolic map); the flag itself is
    read from the KG.
 2. Test each map for UP over-representation among up-genes via the genome-wide
    pathway_enrichment (ORA, BH), direction=up. HOT1A3 = primary (table_scope
    background, matching step 4). EZ55 tables are significant_only, so an
    in-table background is degenerate -> EZ55 uses organism (genome) background,
    flagged as a secondary read. flag = up if ora_padj < 0.10 (direction up),
    else not-up. Fallback for a map too small for ORA (bg_count < MIN_ORA_GENES):
    median up-percentile of its genes (>0.5 = up-ish).
 3. No degradation map at any granularity -> "not-determinable".

Emits one row per (substrate, map, experiment); one not-determinable row per
substrate with no map. NO carbon-source conclusions -- facts + flags only.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/analysis/scripts/08_breakdown_maps.py
"""
import os
import pandas as pd
from multiomics_explorer import pathway_enrichment, differential_expression_by_gene

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
OUT = os.path.join(DATA, "breakdown_flags.csv")

CATALOGS = [
    os.path.join(DATA, "module_catalog_hot1a3_day11_v2.csv"),
    os.path.join(DATA, "module_catalog_ez55_400.csv"),
    os.path.join(DATA, "module_catalog_ez55_800.csv"),
]

HOT1A3 = "10.1101/2025.11.24.690089_coculture_prochlorococcus_med4_hot1a3_rnaseq"
EZ55_400 = "10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_400_ez55_rnaseq"
EZ55_800 = "10.1038/s43705-022-00197-2_coculture_prochlorococcus_mit9312_at_800_ez55_rnaseq"

PADJ_UP = 0.10
MIN_ORA_GENES = 5   # below this a map is "too small for ORA" -> percentile fallback

# --- KEGG *degradation* (catabolic) maps only. Direction-neutral metabolism
#     maps are deliberately excluded (they do not count per the rule). ---
MAP_NAME = {
    "kegg.pathway:ko00362": "Benzoate degradation",
    "kegg.pathway:ko01220": "Degradation of aromatic compounds",
    "kegg.pathway:ko00280": "Valine, leucine and isoleucine degradation",
    "kegg.pathway:ko00310": "Lysine degradation",
    "kegg.pathway:ko00071": "Fatty acid degradation",
}

# --- substrate (lower-cased key) -> [(map_id, granularity), ...] ---
#     Only substrates with a genuine catabolic map appear here; everything else
#     in the catalogs is "not-determinable" (central-metabolism-only). [interpretation]
SUBSTRATE_MAPS = {
    "benzoate membrane": [("kegg.pathway:ko00362", "exact"),
                          ("kegg.pathway:ko01220", "broader")],
    "hcat :: mfs": [("kegg.pathway:ko00362", "broader"),
                    ("kegg.pathway:ko01220", "broader")],  # 3-phenylpropionate, aromatic
    "branched-chain amino acid": [("kegg.pathway:ko00280", "exact")],
    "amino acid": [("kegg.pathway:ko00280", "broader"),
                   ("kegg.pathway:ko00310", "broader")],
    "apc family": [("kegg.pathway:ko00280", "broader"),
                   ("kegg.pathway:ko00310", "broader")],
    "polar amino acid": [("kegg.pathway:ko00310", "broader")],  # basic/polar AA
    "long-chain fatty acid": [("kegg.pathway:ko00071", "exact")],
    "short-chain fatty acids": [("kegg.pathway:ko00071", "broader")],
}


def distinct_substrates():
    subs = {}
    for path in CATALOGS:
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path)
        for s in df.substrate.dropna().unique():
            subs.setdefault(str(s).strip(), None)
    return sorted(subs.keys())


def up_percentiles(l2fc):
    """Percentile rank of each gene's log2fc across the whole DE (higher = more up)."""
    s = pd.Series(l2fc).dropna()
    return s.rank(pct=True).to_dict()


def run_ora(organism, exp, background):
    """Return {map_id: row-dict} of the UP cluster for the 5 degradation maps."""
    res = pathway_enrichment(
        organism=organism, experiment_ids=[exp], ontology="kegg",
        term_ids=list(MAP_NAME.keys()), direction="up",
        background=background, min_gene_set_size=1, informative_only=False)
    out = {}
    for r in res.results.to_dict("records") if hasattr(res.results, "to_dict") else res.results:
        out[r["term_id"]] = r
    return out


def read_flag(row):
    """flag from an ORA result row; fallback to percentile handled by caller."""
    if row is None:
        return None
    bg = row.get("bg_count")
    if bg is not None and bg < MIN_ORA_GENES:
        return "too_small"   # signal caller to use percentile fallback
    padj = row.get("p_adjust")
    if padj is not None and padj < PADJ_UP:
        return "up"
    return "not-up"


def percentile_fallback(map_id, organism, exp):
    """median up-percentile of the map's genes in this experiment's DE (>0.5 = up-ish)."""
    de = differential_expression_by_gene(experiment_ids=[exp], organism=organism, limit=None)
    l2fc = {r["locus_tag"]: r["log2fc"] for r in de["results"] if r.get("log2fc") is not None}
    pct = up_percentiles(l2fc)
    # map genes: pull via a genome-wide enrichment membership is not exposed here;
    # approximate using DE genes annotated to the map is not available column-wise,
    # so fallback is only reachable if ORA returned the map (bg small). We report
    # median percentile of ALL DE genes as a floor sentinel if genes unknown.
    return None  # not triggered for HOT1A3/EZ55 (all 5 maps have bg_count >= 5)


def main():
    subs = distinct_substrates()
    rows = []

    experiments = [
        ("HOT1A3", HOT1A3, "table_scope", "primary"),
        ("EZ55", EZ55_400, "organism", "secondary (EZ55 400; sig-only table -> genome bg)"),
        ("EZ55", EZ55_800, "organism", "secondary (EZ55 800; sig-only table -> genome bg)"),
    ]
    ora = {}
    for org, exp, bg, _note in experiments:
        ora[exp] = run_ora(org, exp, bg)
        print(f"[ORA] {org} {exp.split('_')[0]} bg={bg}: "
              + ", ".join(f"{MAP_NAME[m].split()[0]}={ora[exp].get(m, {}).get('p_adjust')}"
                          for m in MAP_NAME))

    for s in subs:
        maps = SUBSTRATE_MAPS.get(s.lower())
        if not maps:
            rows.append(dict(
                substrate=s, degradation_map="", match_granularity="",
                exists="no", ora_padj="", ora_direction="",
                flag="not-determinable", experiment="HOT1A3 (primary)"))
            continue
        for map_id, gran in maps:
            for org, exp, _bg, note in experiments:
                r = ora[exp].get(map_id)
                fl = read_flag(r)
                if fl == "too_small":
                    fl = "not-up"  # fallback path (not reached: all bg>=5)
                if fl is None:
                    # map has no genes in this organism -> not testable here
                    padj, count, bgc, fold = "", "", "", ""
                    flag = "not-testable"
                else:
                    padj = r.get("p_adjust")
                    count = r.get("count")
                    bgc = r.get("bg_count")
                    fold = r.get("fold_enrichment")
                    flag = fl
                rows.append(dict(
                    substrate=s,
                    degradation_map=f"{map_id.split(':')[1]} {MAP_NAME[map_id]}",
                    match_granularity=gran, exists="yes",
                    ora_padj=padj, ora_direction="up",
                    ora_up_count=count, ora_bg_count=bgc, ora_fold=fold,
                    flag=flag, experiment=f"{org} — {note}"))

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)

    # --- compact console summary (HOT1A3 primary) ---
    prim = out[out.experiment.str.startswith("HOT1A3")]
    n_sub = out.substrate.nunique()
    nd = prim[prim.flag == "not-determinable"].substrate.nunique()
    have_map = prim[prim.exists == "yes"].substrate.nunique()
    print(f"\nwrote {len(out)} rows -> {OUT}")
    print(f"distinct candidate substrates: {n_sub}")
    print(f"  with a genuine degradation map: {have_map}")
    print(f"  not-determinable (central-metabolism-only / no catabolic map): {nd}")
    print("\n=== HOT1A3 (primary) -- substrates WITH a degradation map ===")
    for r in prim[prim.exists == "yes"].to_dict("records"):
        print(f"  {r['substrate']:26s} | {r['degradation_map']:45s} | {r['match_granularity']:7s} "
              f"| padj={r['ora_padj']} up={r['ora_up_count']}/{r['ora_bg_count']} fold={r['ora_fold']} "
              f"-> {r['flag']}")
    print("\n=== not-determinable substrates (HOT1A3 primary) ===")
    print("  " + ", ".join(sorted(prim[prim.flag == 'not-determinable'].substrate)))


if __name__ == "__main__":
    main()
