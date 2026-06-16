"""Step 6 — resolve the publications behind the pooled experiments (References).

Every reference must be resolved through list_publications, never drafted from memory
(anti-hallucination Category 5.2). We take the DOIs of the 74 pooled gene-DE
experiments actually used for scoring and resolve their publication metadata.

Input:  3_analysis_framing/data/pooled_experiments.csv
Output: data/references.csv  (doi, year, journal, title, authors, n_pooled_experiments)
        printed reference list for paper.md
Run (from repo root):
  uv run python analyses/2026-06-16-conserved_hypothetical_de/6_evaluate/scripts/03_references.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from multiomics_explorer import list_publications, to_dataframe

STEP = Path(__file__).resolve().parents[1]
ROOT = STEP.parent
DATA = STEP / "data"
POOLED = pd.read_csv(ROOT / "3_analysis_framing" / "data" / "pooled_experiments.csv")


def first_author(authors: str) -> str:
    if not isinstance(authors, str) or not authors.strip():
        return "[authors n/a]"
    return authors.split("|")[0].strip().split(",")[0].strip()


def main() -> None:
    counts = POOLED["publication_doi"].value_counts()
    dois = [d for d in counts.index if isinstance(d, str) and d]
    res = list_publications(publication_dois=dois)
    df = to_dataframe(res)
    df["n_pooled_experiments"] = df["doi"].map(counts).fillna(0).astype(int)
    keep = [c for c in ["doi", "year", "journal", "title", "authors",
                        "n_pooled_experiments"] if c in df.columns]
    df = df[keep].sort_values(["year", "doi"], na_position="last")
    df.to_csv(DATA / "references.csv", index=False)
    print(f"[references] resolved {len(df)} publications behind {len(POOLED)} pooled "
          f"experiments; not_found={res.get('not_found')}")

    print("\n--- References (paste into paper.md) ---")
    for i, (_, r) in enumerate(df.iterrows(), 1):
        yr = "" if pd.isna(r.get("year")) else int(r["year"])
        jr = r.get("journal") or ""
        print(f"{i}. {first_author(r.get('authors'))} et al. ({yr}). "
              f"{str(r.get('title'))[:90]}. *{jr}*. doi:{r['doi']} "
              f"[{r['n_pooled_experiments']} exp]")


if __name__ == "__main__":
    main()
