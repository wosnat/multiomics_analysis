"""Step 3 — select the candidate conserved-hypothetical ortholog groups.

Applies the framing rules agreed with the researcher to the step-2 landscape:
  - hypothetical OG = >=80% of its Prochlorococcus members are AQ<=1
  - conserved, two tiers (denominator = 17 cyanorak strains):
        core  = present in >=14 of 17 strains
        broad = present in >=9  of 17 strains   (core is a subset of broad)
  - also tag the maximal "all-17" core spike for reference.

Input:   ../2_kg_selection/data/og_conservation_landscape.csv  (step 2)
Output:  data/candidate_ogs.csv   — one row per selected OG with tier label
         data/01_select_candidate_ogs.log (stdout tee)

Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/3_analysis_framing/scripts/01_select_candidate_ogs.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LANDSCAPE = ROOT / "2_kg_selection" / "data" / "og_conservation_landscape.csv"
DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)

FRAC_HYPO_MIN = 0.80
CORE_MIN_STRAINS = 14
BROAD_MIN_STRAINS = 9
N_STRAINS = 17  # cyanorak Prochlorococcus backbone


def main() -> None:
    df = pd.read_csv(LANDSCAPE)
    print(f"[in] {len(df)} cyanorak OGs with a Prochlorococcus member")

    hypo = df[df["frac_hypo"] >= FRAC_HYPO_MIN].copy()
    print(f"[hypothetical] frac_hypo>={FRAC_HYPO_MIN}: {len(hypo)}")

    broad = hypo[hypo["proc_strains"] >= BROAD_MIN_STRAINS].copy()
    broad["tier"] = broad["proc_strains"].apply(
        lambda s: "core" if s >= CORE_MIN_STRAINS else "broad")
    broad["is_all17"] = broad["proc_strains"] >= N_STRAINS

    broad = broad.sort_values(["proc_strains", "proc_members", "frac_hypo"],
                              ascending=False).reset_index(drop=True)
    cols = ["og_id", "consensus_product", "tier", "is_all17", "proc_strains",
            "proc_members", "proc_hypo_members", "frac_hypo",
            "total_member_count", "total_organism_count"]
    broad[cols].to_csv(DATA / "candidate_ogs.csv", index=False)

    n_core = (broad["tier"] == "core").sum()
    n_broad_only = (broad["tier"] == "broad").sum()
    n_all17 = broad["is_all17"].sum()
    print(f"[out] candidate_ogs.csv: {len(broad)} OGs "
          f"(core >=14: {n_core}; broad-only 9-13: {n_broad_only}; all-17: {n_all17})")

    print("\n[selection funnel]")
    print(f"  cyanorak OGs (Prochlorococcus)        {len(df)}")
    print(f"  -> hypothetical (frac_hypo>=0.80)     {len(hypo)}")
    print(f"  -> broad tier   (>=9/17 strains)      {len(broad)}")
    print(f"     of which core (>=14/17 strains)    {n_core}")
    print(f"     of which all-17                    {n_all17}")

    print("\n[core sample] most-conserved candidates:")
    for _, r in broad[broad["tier"] == "core"].head(10).iterrows():
        print(f"  {r['og_id']:<22} strains={int(r['proc_strains']):>2} "
              f"members={int(r['proc_members']):>3} "
              f"frac_hypo={r['frac_hypo']:.2f}  {str(r['consensus_product'])[:42]}")


if __name__ == "__main__":
    main()
