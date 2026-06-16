"""Ortholog-group response metric — the reusable scoring logic.

Methodology (agreed step 3): score each conserved-hypothetical ortholog family on
two independent axes from per-gene differential expression pooled over the 74
Prochlorococcus gene-DE experiments.

Single data source: `differential_expression_by_gene` (per gene × experiment ×
timepoint), which carries log2fc, rank_up/rank_down, and expression_status. The
caller fetches those rows (batched per strain — the tool is single-organism),
attaches each locus_tag's ortholog group id, and passes the long table here.

This module owns ONLY the aggregation methodology. Extraction (KG calls) lives in
`scripts/`. Verified on hand-built toy data in `_verify()` (run `python
og_response_metric.py`).

Metric, per ortholog group (over its member genes):
  - breadth                  = # distinct treatment types with >=1 SIGNIFICANT
                               member datapoint (permissive family-level call)
  - n_significant_datapoints = # significant member x experiment x timepoint rows
  - best_rank                = smallest rank_up/rank_down over significant rows
                               (top-ranked responder within its experiment; lower
                               = more prominent)
  - max_abs_log2fc           = largest |log2fc| over significant rows
  - direction                = overall up / down / mixed (none if not significant)
  - direction_by_treatment   = {treatment: up|down|mixed}
  - n_tested_datapoints      = # tested rows (significant OR not_significant)
  - pct_datapoints_de        = n_significant / n_tested   [CAVEAT: only meaningful
                               where table_scope keeps tested-but-flat rows; see
                               step-3 framing / step-6 caveat]

A "significant" row is expression_status in {significant_up, significant_down}.
A "tested" row is any row the DE table reports (sig or not_significant).
"""
from __future__ import annotations

import pandas as pd

SIG_UP, SIG_DOWN = "significant_up", "significant_down"
SIG = {SIG_UP, SIG_DOWN}

# Columns the long input table must carry (one row per gene x experiment x timepoint).
REQUIRED_COLS = [
    "og_id", "locus_tag", "experiment_id", "treatment_type",
    "expression_status", "log2fc", "rank_up", "rank_down",
]


def _direction(statuses: set[str]) -> str | None:
    up, down = SIG_UP in statuses, SIG_DOWN in statuses
    if up and down:
        return "mixed"
    if up:
        return "up"
    if down:
        return "down"
    return None


def _explode_treatments(df: pd.DataFrame) -> pd.DataFrame:
    """treatment_type may be a list per row; explode to one treatment per row."""
    d = df.copy()
    d["treatment_type"] = d["treatment_type"].apply(
        lambda t: t if isinstance(t, list) else [t])
    return d.explode("treatment_type")


def aggregate_og_metrics(de: pd.DataFrame) -> pd.DataFrame:
    """Long per-gene DE table (with og_id attached) -> one row per ortholog group."""
    missing = [c for c in REQUIRED_COLS if c not in de.columns]
    if missing:
        raise ValueError(f"input missing required columns: {missing}")
    if de.empty:
        return pd.DataFrame()

    ex = _explode_treatments(de)
    ex["is_sig"] = ex["expression_status"].isin(SIG)
    sig = ex[ex["is_sig"]]

    rows = []
    for og, g_all in ex.groupby("og_id"):
        g_sig = sig[sig["og_id"] == og]
        # best (smallest) rank over significant rows, across up/down rank columns
        ranks = pd.concat([g_sig["rank_up"], g_sig["rank_down"]]).dropna()
        best_rank = int(ranks.min()) if not ranks.empty else None
        max_abs = g_sig["log2fc"].abs().max() if not g_sig.empty else None
        dir_by_treatment = {
            t: _direction(set(sub["expression_status"]))
            for t, sub in g_sig.groupby("treatment_type")
        }
        # tested datapoints counted on UN-exploded rows (avoid double counting a
        # multi-treatment datapoint); use locus+experiment+timepoint identity.
        og_raw = de[de["og_id"] == og]
        n_tested = len(og_raw)
        n_sig = int(og_raw["expression_status"].isin(SIG).sum())
        rows.append({
            "og_id": og,
            "breadth": g_sig["treatment_type"].nunique(),
            "n_significant_datapoints": n_sig,
            "best_rank": best_rank,
            "max_abs_log2fc": None if max_abs is None else round(float(max_abs), 2),
            "direction": _direction(set(g_sig["expression_status"])),
            "direction_by_treatment": dir_by_treatment,
            "n_tested_datapoints": n_tested,
            "pct_datapoints_de": round(n_sig / n_tested, 3) if n_tested else None,
            "n_members_with_de": og_raw["locus_tag"].nunique(),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(["breadth", "n_significant_datapoints"],
                           ascending=False).reset_index(drop=True)


def _verify() -> None:
    """Hand-calculated toy verification (methodology gate before real data)."""
    toy = pd.DataFrame([
        # OG A: 3 significant over salt(down)/nitrogen(up)/carbon(up) -> mixed, breadth 3
        dict(og_id="A", locus_tag="a1", experiment_id="e1", treatment_type=["salt"],
             expression_status=SIG_DOWN, log2fc=-2.0, rank_up=None, rank_down=5),
        dict(og_id="A", locus_tag="a1", experiment_id="e2", treatment_type=["nitrogen"],
             expression_status=SIG_UP, log2fc=3.0, rank_up=10, rank_down=None),
        dict(og_id="A", locus_tag="a2", experiment_id="e1", treatment_type=["salt"],
             expression_status="not_significant", log2fc=0.1, rank_up=None, rank_down=None),
        dict(og_id="A", locus_tag="a2", experiment_id="e3", treatment_type=["carbon"],
             expression_status=SIG_UP, log2fc=1.5, rank_up=20, rank_down=None),
        # OG B: 2 significant, both light up -> up, breadth 1, best_rank 2
        dict(og_id="B", locus_tag="b1", experiment_id="e4", treatment_type=["light"],
             expression_status=SIG_UP, log2fc=0.8, rank_up=3, rank_down=None),
        dict(og_id="B", locus_tag="b1", experiment_id="e4b", treatment_type=["light"],
             expression_status=SIG_UP, log2fc=1.0, rank_up=2, rank_down=None),
    ])
    res = aggregate_og_metrics(toy).set_index("og_id")
    a, b = res.loc["A"], res.loc["B"]
    assert a["breadth"] == 3, a["breadth"]
    assert a["n_significant_datapoints"] == 3, a["n_significant_datapoints"]
    assert a["n_tested_datapoints"] == 4, a["n_tested_datapoints"]
    assert a["best_rank"] == 5, a["best_rank"]
    assert a["max_abs_log2fc"] == 3.0, a["max_abs_log2fc"]
    assert a["direction"] == "mixed", a["direction"]
    assert a["direction_by_treatment"] == {"salt": "down", "nitrogen": "up",
                                           "carbon": "up"}, a["direction_by_treatment"]
    assert a["pct_datapoints_de"] == 0.75, a["pct_datapoints_de"]
    assert b["breadth"] == 1 and b["direction"] == "up", (b["breadth"], b["direction"])
    assert b["best_rank"] == 2 and b["max_abs_log2fc"] == 1.0
    # ranking: A (breadth 3) before B (breadth 1)
    assert list(aggregate_og_metrics(toy)["og_id"]) == ["A", "B"]
    print("[toy verify] all assertions passed:")
    print(aggregate_og_metrics(toy).to_string(index=False))


if __name__ == "__main__":
    _verify()
