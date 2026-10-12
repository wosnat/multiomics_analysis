"""E14 item 3: stored protein log2FC (and status, rank percentile) for ntcA, glnA, glnB, urtA, cynA across this study's
protein slices: axenic d14, d31, d89 and coculture d18, d31, d60, d89. No KG calls (analysis/data/de_long.csv.gz).
Output: data/explore/e14_marker_log2fc.csv (long) and e14_marker_log2fc_wide.csv.
"""
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import explore as ex  # noqa: E402

OUT = HERE.parent / "data" / "explore"
GENES = {"PMM0246": "ntcA", "PMM0920": "glnA", "PMM1463": "glnB", "PMM0970": "urtA", "PMM0370": "cynA"}
SL = ([("anchor_axenic_protein", f"day {d}", f"ax d{d}") for d in (14, 31, 89)]
      + [("anchor_cocult_protein", f"day {d}", f"cc d{d}") for d in (18, 31, 60, 89)])


def main():
    de = ex.load()["de"]
    rows = []
    for s, t, lab in SL:
        x = de[(de.short_name == s) & (de.timepoint == t)].set_index("locus_tag")
        for lt, g in GENES.items():
            r = x.loc[lt] if lt in x.index else None
            rows.append({"locus_tag": lt, "gene": g, "slice": lab, "short_name": s, "timepoint": t,
                         "log2fc": None if r is None else r.log2fc, "padj": None if r is None else r.padj,
                         "expression_status": "not detected" if r is None else r.expression_status,
                         "rank_percentile": None if r is None else r.rank_percentile})
    T = pd.DataFrame(rows)
    T.to_csv(OUT / "e14_marker_log2fc.csv", index=False)
    W = T.pivot(index=["gene", "locus_tag"], columns="slice", values="log2fc")[[x[2] for x in SL]]
    W = W.reindex([(g, lt) for lt, g in GENES.items()])
    W.to_csv(OUT / "e14_marker_log2fc_wide.csv")
    pd.set_option("display.width", 200)
    print(W.round(2).to_string())
    print(T.pivot(index="gene", columns="slice", values="expression_status")[[x[2] for x in SL]].to_string())


if __name__ == "__main__":
    main()
