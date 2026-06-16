"""Step 3 — select and validate breadth/prominence controls (characterized genes).

The metric (steps 4-5) ranks conserved-hypothetical ortholog families by
RESPONSE BREADTH (distinct treatment types with a significant member) and
PROMINENCE (best DE rank / largest |log2FC| / count of significant datapoints).
Before trusting it, validate on characterized genes whose behavior we can judge:

  positive (expect broad)   : hli PMM1385, groEL/groL1 PMM1436
  negative (expect narrow)  : htpG PMM0901, dnaK1 PMM1432
  off-diagonal (prominent,  : pstS PMM0710  (strong single-stress responder —
    not broad)                shows why breadth and prominence are separate axes)

All experiments are used regardless of table_scope (researcher decision
2026-06-16); the table_scope caveat is recorded for step 6, not gated here.

Uses gene_response_profile (group_by treatment_type) — the same permissive
"responded if significant in >=1 timepoint of >=1 experiment" call the OG metric
will use. No reinvention: breadth = len(groups_responded).

Input:   KG via multiomics_explorer
Output:  data/controls_validation.csv
         data/03_controls.log (stdout tee)

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/3_analysis_framing/scripts/03_controls.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from multiomics_explorer import gene_response_profile

DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)

CONTROLS = {
    "PMM1385": ("hli", "positive_broad"),
    "PMM1436": ("groL1/groEL", "positive_moderate"),
    "PMM0901": ("htpG", "negative_narrow"),
    "PMM1432": ("dnaK1", "negative_narrow"),
    "PMM0710": ("pstS", "prominent_not_broad"),
}


def prominence(summary: dict) -> tuple[int | None, float | None, int]:
    """Best (smallest) DE rank, largest |log2FC|, count of responding timepoints."""
    best_rank, max_abs_fc, sig_tps = None, None, 0
    for grp in summary.values():
        for rk in (grp.get("up_best_rank"), grp.get("down_best_rank")):
            if rk is not None:
                best_rank = rk if best_rank is None else min(best_rank, rk)
        for fc in (grp.get("up_max_log2fc"), grp.get("down_max_log2fc")):
            if fc is not None:
                max_abs_fc = abs(fc) if max_abs_fc is None else max(max_abs_fc, abs(fc))
        sig_tps += (grp.get("timepoints_up") or 0) + (grp.get("timepoints_down") or 0)
    return best_rank, max_abs_fc, sig_tps


def main() -> None:
    res = gene_response_profile(locus_tags=list(CONTROLS), organism="MED4",
                               group_by="treatment_type")
    rows = []
    for r in res["results"]:
        lt = r["locus_tag"]
        gene, role = CONTROLS[lt]
        responded = r.get("groups_responded", [])
        best_rank, max_abs_fc, sig_tps = prominence(r.get("response_summary", {}))
        rows.append({
            "locus_tag": lt, "gene": gene, "role": role,
            "breadth_n_treatments": len(responded),
            "treatments_responded": " | ".join(responded),
            "best_de_rank": best_rank,
            "max_abs_log2fc": None if max_abs_fc is None else round(max_abs_fc, 2),
            "n_significant_timepoints": sig_tps,
        })
    df = (pd.DataFrame(rows)
          .sort_values("breadth_n_treatments", ascending=False)
          .reset_index(drop=True))
    df.to_csv(DATA / "controls_validation.csv", index=False)

    print("[controls validation] breadth = # distinct treatment types responded\n")
    with pd.option_context("display.width", 160, "display.max_columns", None):
        print(df.to_string(index=False))

    print("\n[read] hli broad+prominent; groEL moderate; htpG/dnaK1 narrow; "
          "pstS prominent (high |log2FC|/low rank) but narrow -> breadth and "
          "prominence are independent axes, both reported.")


if __name__ == "__main__":
    main()
