"""E15 conversion step only (needs openpyxl; the analysis venv has none). Run through:
  uv run --no-project --with pandas --with openpyxl python scripts/e15_convert_xlsx.py <src_dir> <out_dir>
Reads the CC1A3 workbooks READ-ONLY and writes every sheet's cached values (and the 'N budget' / 'NH4 06112023'
formulas) as headerless CSVs. [external, not in KG]
"""
import sys
from pathlib import Path

import openpyxl
import pandas as pd

src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for f, tag in [("Osnat_CC1A3_N analysis.xlsx", "n_analysis"), ("CC1A3_N_budget.xlsx", "n_budget_34d")]:
    for sh in pd.ExcelFile(src / f).sheet_names:
        pd.read_excel(src / f, sheet_name=sh, header=None).to_csv(out / f"{tag}__{sh.replace(' ', '_')}.csv",
                                                                  index=False, header=False)
wb = openpyxl.load_workbook(src / "Osnat_CC1A3_N analysis.xlsx", read_only=True)
for sh in ("N budget", "NH4 06112023"):
    rows = [[c for c in r] for r in wb[sh].iter_rows(values_only=True)]
    pd.DataFrame(rows).to_csv(out / f"n_analysis__{sh.replace(' ', '_')}__formulas.csv", index=False, header=False)
print("converted to", out)
