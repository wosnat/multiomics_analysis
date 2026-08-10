"""Temporal overlay, step 1: pull per-(arm x timepoint) DE for the two HOT1A3
starvation-vs-exponential RNA-seq arms (coculture, axenic) and cache each. Both
arms are all_detected_genes -> scope genome_wide. Sign distribution reported per
timepoint as a data-integrity check.

Run from repo root: uv run analyses/.../analysis/pull_temporal.py
"""
import json
import os
from collections import Counter
from multiomics_explorer import differential_expression_by_gene

ORG = "Alteromonas macleodii HOT1A3"
ARMS = {
    "coculture": "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_hot1a3_rnaseq_coculture",
    "axenic": "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_hot1a3_rnaseq_axenic",
}
HERE = os.path.dirname(os.path.abspath(__file__))
TCACHE = os.path.join(HERE, "cache", "temporal")
os.makedirs(TCACHE, exist_ok=True)


def slug(tp):
    return tp.replace(" ", "_").replace("+", "and")


def main():
    log = {"arms": {}}
    for arm, exp in ARMS.items():
        r = differential_expression_by_gene(organism=ORG, experiment_ids=[exp],
                                            limit=None)
        rows = r["results"]
        scope = list(r.get("by_table_scope", {}).keys())
        # group by timepoint label
        by_tp = {}
        for row in rows:
            by_tp.setdefault(row["timepoint"], {})[row["locus_tag"]] = row["log2fc"]
        arm_log = {"experiment_id": exp, "table_scope": scope,
                   "total_rows": r["total_matching"], "timepoints": {}}
        for tp, de in sorted(by_tp.items()):
            n = len(de)
            neg = sum(1 for v in de.values() if v < 0)
            pos = sum(1 for v in de.values() if v > 0)
            zero = sum(1 for v in de.values() if v == 0)
            json.dump(de, open(os.path.join(TCACHE, f"{arm}__{slug(tp)}.json"), "w"))
            arm_log["timepoints"][tp] = {
                "n_genes": n, "negative": neg, "positive": pos, "zero": zero,
                "pct_negative": round(100 * neg / n, 2) if n else None}
            print(f"{arm:9} | {tp:12} | n={n} scope={scope} "
                  f"neg={neg} ({100*neg/n:.1f}%) pos={pos} zero={zero}")
        log["arms"][arm] = arm_log
    json.dump(log, open(os.path.join(TCACHE, "temporal_pull_log.json"), "w"),
              indent=1)
    print("\ncached per-(arm x timepoint) de tables + temporal_pull_log.json")


if __name__ == "__main__":
    main()
