"""
Toy-data verification for p_capacity.py (step 4). Hand-computed expectations
checked against the module. See 4_methods/notebook.md for the worked numbers.

Run: uv run python analyses/2026-06-13-ll_vs_hl_p_capacity/4_methods/scripts/qc_toy_verification.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from p_capacity import (build_presence_matrix, per_strain_counts,
                        ecotype_ratio, differential_presence)

# Toy panel: 2 HL (HL_a, HL_b), 1 LL (LL_x).
# OGs: og1 in all 3 (universal); og2 in LL_x only (LL_only); og3 in HL_a only
# (HL_only); og2 also has a paralog in LL_x (two gene rows -> presence still 1).
toy = pd.DataFrame([
    ("HL", "HLI",  "HL_a", "og1"), ("HL", "HLI", "HL_a", "og3"),
    ("HL", "HLII", "HL_b", "og1"),
    ("LL", "LLI",  "LL_x", "og1"), ("LL", "LLI", "LL_x", "og2"),
    ("LL", "LLI",  "LL_x", "og2"),  # paralog -> must collapse to presence=1
], columns=["ecotype", "clade", "strain", "cyanorak_og"])

gsize = pd.Series({"HL_a": 1000, "HL_b": 2000, "LL_x": 2000})

matrix, meta = build_presence_matrix(toy)
counts = per_strain_counts(matrix, meta, genome_size=gsize)
ratio = ecotype_ratio(counts)
diff = differential_presence(matrix, meta)

# --- hand-computed expectations ---
# presence: HL_a{og1,og3}=2, HL_b{og1}=1, LL_x{og1,og2}=2 (paralog collapsed)
assert matrix.loc["LL_x", "og2"] == 1, "paralog must collapse to presence=1"
assert counts.loc["HL_a", "n_ogs"] == 2
assert counts.loc["HL_b", "n_ogs"] == 1
assert counts.loc["LL_x", "n_ogs"] == 2
# per1k: HL_a 2/1000*1000=2.0 ; LL_x 2/2000*1000=1.0
assert counts.loc["HL_a", "per1k"] == 2.0
assert counts.loc["LL_x", "per1k"] == 1.0
# ecotype: HL mean=(2+1)/2=1.5 ; LL mean=2 ; LL/HL=1.333...
assert ratio["hl_mean"] == 1.5
assert ratio["ll_mean"] == 2.0
assert abs(ratio["ll_over_hl"] - 4 / 3) < 1e-9
assert ratio["n_hl"] == 2 and ratio["n_ll"] == 1
# differential categories
assert diff.loc["og1", "category"] == "universal"   # 2 HL, 1 LL = all
assert diff.loc["og2", "category"] == "LL_only"      # 0 HL, 1 LL
assert diff.loc["og3", "category"] == "HL_only"      # 1 HL, 0 LL

print("toy verification PASSED")
print(matrix.to_string())
print(counts.to_string())
print("ratio:", {k: round(v, 4) if isinstance(v, float) else v for k, v in ratio.items()})
print(diff.to_string())
