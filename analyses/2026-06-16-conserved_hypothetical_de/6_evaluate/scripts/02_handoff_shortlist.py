"""Step 6 — assemble the hand-off shortlist for the characterization follow-on.

Headline = the 14 families that are BOTH broad and prominent (robust to the coverage
confound, since prominence is not coverage-driven). The 85-family shortlist is kept as
the long list. Output carries the coverage-normalized response_rate so the follow-on
can weight by the more robust signal.

Input:  data/coverage_confound.csv (245 hypotheticals + coverage/response_rate)
Output: data/handoff_shortlist.csv  (85 shortlist families, core14 flagged)
        data/01b prints the 14 core
Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/6_evaluate/scripts/02_handoff_shortlist.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

STEP = Path(__file__).resolve().parents[1]
DATA = STEP / "data"
H = pd.read_csv(DATA / "coverage_confound.csv")

KEEP = ["og_id", "tier", "proc_strains", "proc_members", "dominant_category",
        "consensus_product", "breadth", "n_treatments_tested", "response_rate",
        "n_significant_datapoints", "best_rank", "max_abs_log2fc", "direction",
        "is_broad", "is_prominent", "direction_by_treatment"]


def main() -> None:
    sl = H[H["is_highlight"]].copy()
    sl["core14"] = sl["is_broad"] & sl["is_prominent"]
    sl = sl[KEEP + ["core14"]].sort_values(
        ["core14", "breadth", "max_abs_log2fc"], ascending=False).reset_index(drop=True)
    sl.to_csv(DATA / "handoff_shortlist.csv", index=False)
    print(f"[handoff] {len(sl)} shortlist families -> data/handoff_shortlist.csv "
          f"({int(sl['core14'].sum())} core14)")

    core = sl[sl["core14"]].sort_values(["breadth", "max_abs_log2fc"], ascending=False)
    cols = ["og_id", "tier", "proc_strains", "breadth", "n_treatments_tested",
            "response_rate", "best_rank", "max_abs_log2fc", "direction",
            "consensus_product"]
    print(f"\n[CORE 14 — broad AND prominent conserved hypotheticals]")
    with pd.option_context("display.width", 200, "display.max_columns", None):
        t = core[cols].copy()
        t["consensus_product"] = t["consensus_product"].str.slice(0, 34)
        print(t.to_string(index=False))


if __name__ == "__main__":
    main()
