"""Byte-level diff of a re-run directory against an archived run (recursive). No KG calls.
For each file: identical / differs / only_old / only_new. For differing CSVs, also report whether the
content is equal after reading with pandas (same rows and columns) and row counts; for JSON, the top-level
keys whose values differ.
Usage: ... p9_diff_dirs.py --old <dir> --new <dir> --out <json>
"""
import argparse
import filecmp
import json
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True); ap.add_argument("--new", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    o, n = Path(a.old), Path(a.new)
    fo = {p.relative_to(o).as_posix() for p in o.rglob("*") if p.is_file()}
    fn = {p.relative_to(n).as_posix() for p in n.rglob("*") if p.is_file()}
    res = {"only_old": sorted(fo - fn), "only_new": sorted(fn - fo), "identical": 0, "differs": {}}
    for f in sorted(fo & fn):
        if filecmp.cmp(o / f, n / f, shallow=False):
            res["identical"] += 1
            continue
        info = {}
        if f.endswith(".csv"):
            a_, b_ = pd.read_csv(o / f, low_memory=False), pd.read_csv(n / f, low_memory=False)
            info = {"rows_old": len(a_), "rows_new": len(b_), "cols_added": sorted(set(b_) - set(a_)),
                    "cols_removed": sorted(set(a_) - set(b_))}
            common = [c for c in a_.columns if c in b_.columns]
            info["equal_on_common_columns"] = len(a_) == len(b_) and a_[common].astype(str).equals(b_[common].astype(str))
        elif f.endswith(".json"):
            ja, jb = json.loads((o / f).read_text(encoding="utf-8")), json.loads((n / f).read_text(encoding="utf-8"))
            if isinstance(ja, dict) and isinstance(jb, dict):
                info = {"keys_differ": sorted(k for k in set(ja) | set(jb) if ja.get(k) != jb.get(k))}
        res["differs"][f] = info
    Path(a.out).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
