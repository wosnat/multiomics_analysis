"""Shared helpers for the pipeline scripts (organism resolution, output layout, pilot constants).

Output layout (API review I4): ONE DIRECTORY PER ORGANISM, methods/data/<tag>/ (e.g. data/med4/),
raw API dumps under <dir>/raw/. File names keep the organism tag where they had one; every summary
JSON records organism, module versions and (from step 2 on) the Pfam role-map hash.
Pilot answer-key comparisons run only with --pilot (I5).
"""
import json
import sys
from pathlib import Path

import pandas as pd

METHODS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(METHODS))
import kg_fetch as kf  # noqa: E402
import n_transport as nt  # noqa: E402

ANSWER_KEY = METHODS / "data" / "answer_key"
PILOT = (["PMM0370", "PMM0371", "PMM0372", "PMM0373"]
         + [f"PMM{n:04d}" for n in range(963, 975)]
         + ["PMM0263", "PMM1049", "PMM1048", "PMM0421", "PMM0192",
            "PMM0710", "PMM0723", "PMM0724", "PMM0725", "PMM0913", "PMM0402"])
PILOT_ANCHORS = {"cyn": "PMM0371", "urt": "PMM0972", "dpp": "PMM1049", "amt1": "PMM0263",
                 "pst": "PMM0723", "salY": "PMM0913", "fadD": "PMM0402"}
REF = "gap200_roleT_crossT"


def resolve_organism(name, conn):
    """list_organisms(organism_names=[name]) must return exactly one row (M3). Returns (name, tag, row)."""
    from multiomics_explorer import list_organisms
    r = list_organisms(organism_names=[name], conn=conn)
    assert r["total_matching"] == 1 and len(r["results"]) == 1, f"organism {name!r} -> {r['total_matching']} rows"
    row = r["results"][0]
    return row["organism_name"], row["organism_name"].split()[-1].lower(), row


def write_summary(path, summary):
    summary = {"n_transport_version": nt.__version__, **summary}
    Path(path).write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")


def role_map_hash(out_dir):
    p = Path(out_dir) / "p2_pfam_role_map.csv"
    return kf.role_map_hash(pd.read_csv(p)) if p.exists() else None
