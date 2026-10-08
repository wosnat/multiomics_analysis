"""Diff the reference variant (gap200_roleT_crossT) before/after the n_transport v0.5 cross-locus guards.

Before: p3_v0.4_archive/p3_med4_gene_systems_gap200_roleT_crossT.csv
After : p3_med4_gene_systems_gap200_roleT_crossT.csv
Output: p3_ref_diff_v0.4_to_v0.5.csv (one row per changed system membership), printed summary.
Usage (from the pilot dir): ../../../../../.venv/Scripts/python.exe ../../scripts/p3c_diff_reference.py
"""
import pandas as pd

V = "gap200_roleT_crossT"
b = pd.read_csv(f"p3_v0.4_archive/p3_med4_gene_systems_{V}.csv")
a = pd.read_csv(f"p3_med4_gene_systems_{V}.csv")


def sets(df):
    nm = dict(zip(df.locus_tag, df.gene_name.fillna("")))
    return {frozenset(g.locus_tag) for _, g in df.groupby("system_id")}, nm


sb, nm = sets(b)
sa, _ = sets(a)
fmt = lambda s: " | ".join(f"{x}:{nm.get(x, '')}" for x in sorted(s))
rows = []
for s in sorted(sb - sa, key=lambda s: sorted(s)[0]):
    after = sorted({frozenset(x) for x in sa if x & s}, key=lambda x: sorted(x)[0])
    rows.append({"before": fmt(s), "before_size": len(s), "after": " || ".join(fmt(x) for x in after),
                 "after_sizes": ",".join(str(len(x)) for x in after)})
d = pd.DataFrame(rows)
d.to_csv("p3_ref_diff_v0.4_to_v0.5.csv", index=False)
print("systems before", len(sb), "after", len(sa), "changed (before-side)", len(d))
print("new systems only in after:", len(sa - sb))
pd.set_option("display.width", 300); pd.set_option("display.max_colwidth", 200)
print(d.to_string())
