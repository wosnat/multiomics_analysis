"""Step 2 — conserved-hypothetical ortholog-group landscape (cyanorak backbone).

Purpose:
  Show that the two operational definitions are computable at the ortholog-group
  level and characterize the candidate universe BEFORE step 3 locks thresholds:
    - "uncharacterized"  = Gene.annotation_quality <= 1  (hypothetical / catch-all)
    - "conserved"        = present in many Prochlorococcus strains (out of 19)
  Unit = cyanorak curated OrthologGroup (the cyanobacteria-purpose-built backbone).

  This is a LANDSCAPE / feasibility scan, not the final selection. No thresholds
  are committed here; we report the strain-coverage x hypothetical-fraction
  distribution so step 3 can choose defensible cutoffs.

Inputs:  KG via multiomics_explorer (run_cypher escape hatch — the per-OG strain
         count is a genuine aggregation the typed API does not expose).
Outputs:
  data/og_conservation_landscape.csv  — one row per cyanorak OG with Prochlorococcus
                                          members (strain coverage, member counts,
                                          hypothetical fraction, consensus product)
  data/02_og_conservation_landscape.log (stdout tee) — distributions

Run:  uv run python 2_kg_selection/scripts/02_og_conservation_landscape.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from multiomics_explorer import run_cypher

DATA = Path(__file__).resolve().parents[1] / "data"
DATA.mkdir(parents=True, exist_ok=True)

N_PROCHLORO_STRAINS = 19  # genome strains in the KG (verified: list_organisms / cypher)

CYPHER = """
MATCH (og:OrthologGroup {source:'cyanorak'})<-[:Gene_in_ortholog_group]-(g:Gene)
      -[:Gene_belongs_to_organism]->(o:OrganismTaxon)
WHERE o.genus = 'Prochlorococcus'
WITH og,
     count(DISTINCT o) AS proc_strains,
     count(DISTINCT g) AS proc_members,
     sum(CASE WHEN g.annotation_quality <= 1 THEN 1 ELSE 0 END) AS proc_hypo_members
RETURN og.id                AS og_id,
       og.consensus_product AS consensus_product,
       og.member_count      AS total_member_count,
       og.organism_count    AS total_organism_count,
       proc_strains,
       proc_members,
       proc_hypo_members,
       toFloat(proc_hypo_members) / proc_members AS frac_hypo
ORDER BY proc_strains DESC, frac_hypo DESC
"""


def main() -> None:
    res = run_cypher(CYPHER, limit=100000)
    df = pd.DataFrame(res["results"])
    print(f"[funnel] cyanorak OGs with >=1 Prochlorococcus member: {len(df)}")
    df.to_csv(DATA / "og_conservation_landscape.csv", index=False)
    print(f"[out] wrote {len(df)} OG rows -> data/og_conservation_landscape.csv")

    # Define a mostly-hypothetical OG as >=80% of its Prochlorococcus members
    # being AQ<=1 (a landscape lens, not the locked step-3 rule).
    hypo = df[df["frac_hypo"] >= 0.8]
    print(f"\n[hypothetical OGs] frac_hypo>=0.8: {len(hypo)} of {len(df)} cyanorak OGs")

    print("\n[strain-coverage distribution among mostly-hypothetical OGs]")
    dist = (hypo.groupby("proc_strains").size()
            .reindex(range(1, N_PROCHLORO_STRAINS + 1), fill_value=0))
    cum_ge = dist[::-1].cumsum()[::-1]  # OGs present in >= k strains
    print(f"  {'strains':>7}  {'n_OGs':>6}  {'cum(>=k)':>8}")
    for k in range(1, N_PROCHLORO_STRAINS + 1):
        print(f"  {k:>7}  {int(dist.get(k,0)):>6}  {int(cum_ge.get(k,0)):>8}")

    # A few illustrative core conserved hypotheticals (present in many strains).
    core = hypo.sort_values("proc_strains", ascending=False).head(12)
    print("\n[examples] most strain-conserved hypothetical OGs:")
    for _, r in core.iterrows():
        print(f"  {r['og_id']:<24} strains={int(r['proc_strains']):>2} "
              f"members={int(r['proc_members']):>3} "
              f"frac_hypo={r['frac_hypo']:.2f}  {str(r['consensus_product'])[:45]}")


if __name__ == "__main__":
    main()
