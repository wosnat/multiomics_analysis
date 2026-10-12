"""Analysis-side helpers for the expression read (analysis milestone, pro_n_import_coculture).

Imports the methods module and kg_fetch from ../methods (never copied). Facts only.

Rank percentile (proposal §3.3): within one experiment x timepoint slice, detected genes (non-null log2FC) are
sorted by log2FC descending; percentile = 1 - (position - 1) / n_detected. Ties get the MEAN of the positions they
occupy (pandas rank method="average"), so tied genes share one percentile. 1.0 = most up-regulated gene.
Filtered or significant-only tables (table_scope other than all_detected_genes) are ranked too, but flagged
percentile_valid=False with the note "filtered table: positive evidence only".
"""
import re
import sys
from pathlib import Path

import pandas as pd

ANALYSIS = Path(__file__).resolve().parent
METHODS = ANALYSIS.parent / "methods"
for p in (METHODS, METHODS / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import kg_fetch as kf  # noqa: E402,F401
import n_transport as nt  # noqa: E402,F401

__version__ = "0.1.0"
ALL_DETECTED = "all_detected_genes"
FILTERED_NOTE = "filtered table: positive evidence only"
SLICE = ["experiment_id", "timepoint"]
NEG_SHARE_RANGE = (0.40, 0.55)


def is_pooled(label) -> bool:
    """True for a pooled timepoint label such as 'days 60+89'."""
    return isinstance(label, str) and "+" in label


def proposal_timepoint(label) -> str:
    """Map a KG timepoint label to the proposal's naming: 'day 14' -> 'd14', '12h' -> '12 h',
    'days 60+89' -> combined, None -> 'single contrast'."""
    if label is None or (isinstance(label, float) and pd.isna(label)) or str(label).strip() == "":
        return "single contrast"
    s = str(label).strip()
    if is_pooled(s):
        return "d" + re.sub(r"[^0-9+]", "", s) + " (combined; not used by the proposal)"
    m = re.fullmatch(r"days?\s*(\d+)", s)
    if m:
        return f"d{m.group(1)}"
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*h", s)
    if m:
        return f"{m.group(1)} h"
    return s


def add_rank_percentile(df: pd.DataFrame, slice_cols=SLICE) -> pd.DataFrame:
    """Add rank_position (mean position for ties), n_detected_in_slice, rank_percentile, percentile_valid,
    percentile_note per slice. Rows with null log2fc are not ranked (NaN) and not counted."""
    out = df.copy()
    keys = [c if c in out.columns else None for c in slice_cols]
    keys = [k for k in keys if k]
    tmp = out[keys].fillna("__none__")
    grp = out.groupby([tmp[k] for k in keys], sort=False)["log2fc"]
    out["rank_position"] = grp.rank(method="average", ascending=False)
    out["n_detected_in_slice"] = grp.transform(lambda s: int(s.notna().sum()))
    out["rank_percentile"] = 1 - (out["rank_position"] - 1) / out["n_detected_in_slice"]
    filt = (out["table_scope"] != ALL_DETECTED) if "table_scope" in out.columns else pd.Series(False, index=out.index)
    out["percentile_valid"] = ~filt
    out["percentile_note"] = filt.map({True: FILTERED_NOTE, False: ""})
    return out


def slice_qc(df: pd.DataFrame, total_matching: int) -> dict:
    """QC facts for one slice: rows vs total_matching, duplicated (locus_tag) rows, negative-log2FC share
    (range check only for all_detected tables), padj < 0.05 vs stored significance, smallest |log2FC| among
    significant rows, and the padj < 0.05 rows stored not_significant (extra fold-change cutoff)."""
    st = df.get("expression_status", pd.Series([None] * len(df), index=df.index)).astype(str)
    padj = pd.to_numeric(df.get("padj", pd.Series([None] * len(df), index=df.index)), errors="coerce")
    lfc = pd.to_numeric(df["log2fc"], errors="coerce")
    sig = st.str.startswith("significant")
    neg = float((lfc < 0).sum() / lfc.notna().sum()) if lfc.notna().any() else None
    scope = df["table_scope"].iloc[0] if "table_scope" in df.columns and len(df) else None
    gap = (padj < 0.05) & ~sig
    return {
        "rows": int(len(df)), "total_matching": int(total_matching), "rows_match_total": int(len(df)) == int(total_matching),
        "duplicate_rows": int(df.duplicated(subset=["locus_tag"]).sum()),
        "negative_share": neg,
        "negative_share_ok": (NEG_SHARE_RANGE[0] <= neg <= NEG_SHARE_RANGE[1]) if (scope == ALL_DETECTED and neg is not None) else None,
        "n_padj_lt_0.05": int((padj < 0.05).sum()), "n_status_significant": int(sig.sum()),
        "n_sig_up": int((st == "significant_up").sum()), "n_sig_down": int((st == "significant_down").sum()),
        "n_padj_lt_0.05_not_significant": int(gap.sum()),
        "min_abs_log2fc_significant": float(lfc[sig].abs().min()) if sig.any() else None,
        "max_abs_log2fc_padj_sig_but_not_significant": float(lfc[gap].abs().max()) if gap.any() else None,
    }


# --------------------------------------------------------------------------- stage 2 helpers (header block)
SIG_UP, SIG_DOWN = "significant_up", "significant_down"


def system_stats(de: pd.DataFrame, short: str, timepoint, members) -> dict:
    """Facts for one system (member locus tags) in one slice (short_name, timepoint): members, detected (rows with a
    log2fc), significant up / down (stored expression_status), median subunit rank percentile, median log2FC,
    members not detected. Never pass a pooled timepoint."""
    members = list(dict.fromkeys(members))
    x = de[(de.short_name == short) & (de.timepoint == timepoint) & de.locus_tag.isin(members)]
    x = x[x.log2fc.notna()]
    st = x.expression_status.astype(str)
    return {"n_members": len(members), "n_detected": int(len(x)), "n_up": int((st == SIG_UP).sum()),
            "n_down": int((st == SIG_DOWN).sum()),
            "median_percentile": float(x.rank_percentile.median()) if len(x) else float("nan"),
            "median_log2fc": float(x.log2fc.median()) if len(x) else float("nan"),
            "not_detected": " ".join(m for m in members if m not in set(x.locus_tag))}


def up_any(s: dict, require_no_down: bool = False) -> bool:
    """>= 1 detected subunit significant_up (optionally and none significant_down)."""
    return s["n_up"] >= 1 and (not require_no_down or s["n_down"] == 0)


def up_half(s: dict) -> bool:
    """>= half of the detected subunits significant_up (False when nothing is detected)."""
    return s["n_detected"] > 0 and s["n_up"] >= s["n_detected"] / 2


def crit_a(s60: dict, s89: dict, rna_med60, rna_med89, variant: str) -> bool:
    """Proposal §3.3 (a) under a variant: 'any' = >= 1 detected subunit significant_up and none significant_down at
    both d60 and d89 (protein); 'half' = >= half of the detected subunits significant_up at both days. Both also need
    the RNA median log2FC > 0 at both days."""
    if variant == "any":
        prot = up_any(s60, True) and up_any(s89, True)
    elif variant == "half":
        prot = up_half(s60) and up_half(s89)
    else:
        raise ValueError(variant)
    rna = all(not pd.isna(v) and v > 0 for v in (rna_med60, rna_med89))
    return bool(prot and rna)


def crit_b(med60, med89, ax14, threshold: float = 0.90, margin: float = 0.10) -> bool:
    """Proposal §3.3 (b): median subunit percentile >= threshold at d60 and d89 (protein), and each >= axenic d14 +
    margin (a small tolerance absorbs float error at exactly the margin)."""
    vals = (med60, med89, ax14)
    if any(pd.isna(v) for v in vals):
        return False
    eps = 1e-9
    return bool(med60 >= threshold and med89 >= threshold and med60 - ax14 >= margin - eps and med89 - ax14 >= margin - eps)


def c4_any(grid: dict) -> bool:
    """grid: timepoint -> {locus: status} over the detected/listed subunits. >= 1 subunit up at >= 1 timepoint."""
    return any(v == SIG_UP for tp in grid.values() for v in tp.values())


def c4_half(grid: dict) -> bool:
    """>= half of the detected/listed subunits significant_up at the same timepoint, at >= 1 timepoint."""
    return any(len(tp) > 0 and sum(v == SIG_UP for v in tp.values()) >= len(tp) / 2 for tp in grid.values())
