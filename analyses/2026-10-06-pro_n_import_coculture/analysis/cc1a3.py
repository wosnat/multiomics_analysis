"""Helpers for the external CC1A3 culture data (E15; [external, not in KG]).

N quotas and formulas as in the source workbook / notebook (CC1A3/FCM/cc1A3 notebook.ipynb cell 56, cell 58;
'Osnat_CC1A3_N analysis.xlsx' sheet 'N budget'):
  Qp = 12.5 fg N per MED4 cell, Qh = 25 fg N per HOT1A3 cell; Q [umol N/cell] = fg * 1e-9 / 14
  N biomass [umol N / L] = cells/ml * Q * 1e3
  Total N(t0) = NH4(medium) + DON(t0, assumed 20 uM) + biomass(t0 inoculum)
  DON(t) = Total N(t0) - (N biomass HOT1A3 + N biomass MED4 + NH4)(t)       [closed system; NO3 not included]
"""
import math
import re

CONDITION = {"P": "axenic MED4", "C": "coculture", "A": "HOT1A3 alone"}
Q_FG_N = {"MED4": 12.5, "HOT1A3": 25.0}
# anchor omics sampling days in the KG (protein/RNA): axenic d14 (protein+RNA), d31, d89 (protein);
# coculture d11 (direct-contrast RNA), d18, d31, d60, d89
OMICS_DAYS = {"P": {14, 31, 89}, "C": {11, 18, 31, 60, 89}, "A": set()}


def parse_sample(s):
    m = re.match(r"^([PCA])(\d)([ABC])\b", str(s))
    return (m.group(1), int(m.group(2)), m.group(3)) if m else None


def n_biomass_uM(cells_per_ml, organism):
    q = Q_FG_N[organism] * 1e-9 / 14
    return cells_per_ml * q * 1e3


def _z(x):
    return 0.0 if x is None or x != x else x


def total_n0(nh4_medium, don0, biomass_h, biomass_p):
    return nh4_medium + don0 + _z(biomass_h) + _z(biomass_p)


def don_by_difference(total0, biomass_h, biomass_p, nh4):
    return total0 - (_z(biomass_h) + _z(biomass_p) + nh4)


def first_match(rows, key):
    """Excel VLOOKUP(..., FALSE) semantics: value of the first row whose key matches."""
    for k, v in rows:
        if k == key:
            return v
    return None


def day_rounded(day):
    return int(math.floor(day + 0.5))


def is_omics_day(cond, day_r):
    return day_r in OMICS_DAYS[cond]
