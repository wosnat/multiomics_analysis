"""Verify the NA-collision rename (n_transport v1.0.3) against the archived v1.0.2 outputs. No KG calls.

For every CSV in both directories, read old and new as raw text (dtype=str, keep_default_na=False) and
check: same rows and columns; every differing cell is an allowed rename
  "n/a" -> "not_eligible" (any column), "" -> "none" (match_basis, link_basis, link_basis_group only);
plus JSON-summary differences listed by top-level key. Also: value counts of the strict columns
before/after (raw text), the same columns read with DEFAULT pd.read_csv (NaN count), and a scan of the
new outputs for any non-empty value in pandas' default NA set.
Usage: ... p10_verify_na_rename.py --old <archive dir> --new <dir> --tag <tag> --out <json>
"""
import argparse
import json
from pathlib import Path

import pandas as pd
from pandas._libs.parsers import STR_NA_VALUES

ALLOWED = {("n/a", "not_eligible"): None, ("", "none"): {"match_basis", "link_basis", "link_basis_group"}}
STRICT = ["can_use_window_ms", "can_use_run_ms"]


def main():
    ap = argparse.ArgumentParser()
    for a_ in ("--old", "--new", "--tag", "--out"):
        ap.add_argument(a_, required=True)
    a = ap.parse_args()
    o, n = Path(a.old), Path(a.new)
    res = {"csv": {}, "json": {}, "only_old": [], "only_new": []}
    fo = {p.relative_to(o).as_posix() for p in o.rglob("*") if p.is_file()}
    fn = {p.relative_to(n).as_posix() for p in n.rglob("*") if p.is_file()}
    res["only_old"], res["only_new"] = sorted(fo - fn), sorted(fn - fo)
    for f in sorted(fo & fn):
        if (o / f).read_bytes() == (n / f).read_bytes():
            continue
        if f.endswith(".csv"):
            A = pd.read_csv(o / f, dtype=str, keep_default_na=False)
            B = pd.read_csv(n / f, dtype=str, keep_default_na=False)
            info = {"rows_old": len(A), "rows_new": len(B), "same_columns": list(A.columns) == list(B.columns)}
            changes, bad = {}, {}
            if len(A) == len(B) and info["same_columns"]:
                for c in A.columns:
                    m = A[c] != B[c]
                    if not m.any():
                        continue
                    pairs = pd.Series(list(zip(A.loc[m, c], B.loc[m, c]))).value_counts()
                    for (x, y), k in pairs.items():
                        cols_ok = ALLOWED.get((x, y), "NOT_ALLOWED")
                        ok = cols_ok is None or (cols_ok != "NOT_ALLOWED" and c in cols_ok)
                        (changes if ok else bad)[f"{c}: {x!r} -> {y!r}"] = int(k)
            info["allowed_changes"], info["other_changes"] = changes, bad
            res["csv"][f] = info
        elif f.endswith(".json"):
            ja, jb = json.loads((o / f).read_text(encoding="utf-8")), json.loads((n / f).read_text(encoding="utf-8"))
            res["json"][f] = sorted(k for k in set(ja) | set(jb) if ja.get(k) != jb.get(k)) if isinstance(ja, dict) else "differs"
    t = a.tag
    fl_o = pd.read_csv(o / f"p6_{t}_system_substrates_flagged.csv", dtype=str, keep_default_na=False, usecols=STRICT)
    fl_n = pd.read_csv(n / f"p6_{t}_system_substrates_flagged.csv", dtype=str, keep_default_na=False, usecols=STRICT)
    fl_def = pd.read_csv(n / f"p6_{t}_system_substrates_flagged.csv", usecols=STRICT)  # DEFAULT NA handling
    fl_def_old = pd.read_csv(o / f"p6_{t}_system_substrates_flagged.csv", usecols=STRICT)
    res["strict_value_counts"] = {c: {"before": fl_o[c].value_counts().to_dict(), "after": fl_n[c].value_counts().to_dict(),
                                      "nan_default_read_before": int(fl_def_old[c].isna().sum()),
                                      "nan_default_read_after": int(fl_def[c].isna().sum())} for c in STRICT}
    na = set(STR_NA_VALUES) - {""}
    scan = {}
    for p in sorted(n.glob("*.csv")):
        d = pd.read_csv(p, dtype=str, keep_default_na=False)
        for c in d.columns:
            hit = d[c][d[c].isin(na)].value_counts().to_dict()
            if hit:
                scan[f"{p.name}:{c}"] = hit
    res["nonempty_na_values_remaining"] = scan
    Path(a.out).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
