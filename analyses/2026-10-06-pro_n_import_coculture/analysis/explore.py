"""Descriptive exploration helpers (analysis milestone, deferred-label exploration). Facts only; no labels.

Functions (toy-tested in tests/test_explore.py):
  spearman(x, y)            Spearman rho over pairs where both are present; NaN when n < 3 or a side is constant.
  quadrants(df, mode)       protein vs RNA quadrant counts / shares: mode "sign" (by log2FC sign; zero -> 'zero') or
                            "sig" (stored expression_status; rows not significant on both sides -> 'not both significant').
  relative_rank(a, others)  a - median(others), NaN-safe.
  stereo_key(name) / stereo_equivalents(groups)
                            stereo-generic equivalence for amino-acid compound names: "X", "L-X", "D-X", "DL-X" share a key;
                            plus the explicit KEGG pair C00736 (Cysteine) <-> C00097 (L-Cysteine). Only groups whose
                            compound class is "amino acids" are merged.
Loader: load() returns the shared tables (stage-1 DE without pooled slices, methods v1.6.1 tables).
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ANALYSIS = Path(__file__).resolve().parent
sys.path.insert(0, str(ANALYSIS))
import expr  # noqa: E402
from expr import nt  # noqa: E402

__version__ = "0.1.0"
SIG_UP, SIG_DOWN = expr.SIG_UP, expr.SIG_DOWN
EXPLICIT_PAIRS = [("kegg.compound:C00736", "kegg.compound:C00097")]
QUADS = ["up/up", "up/down", "down/up", "down/down"]


def spearman(x, y):
    a = pd.Series(list(x), dtype=float)
    b = pd.Series(list(y), dtype=float)
    ok = a.notna() & b.notna()
    a, b = a[ok], b[ok]
    n = int(len(a))
    if n < 3 or a.nunique() < 2 or b.nunique() < 2:
        return float("nan"), n
    return float(a.rank().corr(b.rank())), n


def quadrants(df, mode="sign", lp="lfc_p", lr="lfc_r", sp="st_p", sr="st_r"):
    out = {"n": int(len(df))}
    if mode == "sign":
        p, r = df[lp], df[lr]
        out["up/up"] = int(((p > 0) & (r > 0)).sum())
        out["up/down"] = int(((p > 0) & (r < 0)).sum())
        out["down/up"] = int(((p < 0) & (r > 0)).sum())
        out["down/down"] = int(((p < 0) & (r < 0)).sum())
        out["zero"] = int(((p == 0) | (r == 0)).sum())
    elif mode == "sig":
        p, r = df[sp].astype(str), df[sr].astype(str)
        out["up/up"] = int(((p == SIG_UP) & (r == SIG_UP)).sum())
        out["up/down"] = int(((p == SIG_UP) & (r == SIG_DOWN)).sum())
        out["down/up"] = int(((p == SIG_DOWN) & (r == SIG_UP)).sum())
        out["down/down"] = int(((p == SIG_DOWN) & (r == SIG_DOWN)).sum())
        out["not both significant"] = out["n"] - sum(out[q] for q in QUADS)
    else:
        raise ValueError(mode)
    for q in QUADS:
        out[f"share_{q}"] = out[q] / out["n"] if out["n"] else float("nan")
    return out


def relative_rank(a, others):
    o = pd.Series(list(others), dtype=float).dropna()
    if pd.isna(a) or o.empty:
        return float("nan")
    return float(a - o.median())


def stereo_key(name) -> str:
    s = str(name).strip().lower()
    return re.sub(r"^(dl|l|d)-(?=[a-z])", "", s)


def stereo_equivalents(groups: pd.DataFrame, all_groups: pd.DataFrame | None = None) -> dict:
    """groups / all_groups: equiv_group, name, compound_class. Returns equiv_group -> set of stereo-equivalent groups
    (itself included). Name keys merge only within compound class 'amino acids'; EXPLICIT_PAIRS always merge."""
    pool = pd.concat([groups, all_groups], ignore_index=True) if all_groups is not None else groups
    pool = pool.drop_duplicates(["equiv_group", "name"])
    aa = pool[pool.compound_class == "amino acids"]
    by_key = aa.groupby(aa.name.map(stereo_key)).equiv_group.agg(set).to_dict()
    out = {}
    for g in groups.equiv_group.unique():
        s = {g}
        for nm in pool.loc[(pool.equiv_group == g) & (pool.compound_class == "amino acids"), "name"]:
            s |= by_key.get(stereo_key(nm), set())
        for a, b in EXPLICIT_PAIRS:
            if g in (a, b):
                s |= {a, b} & set(pool.equiv_group) | {g}
        out[g] = s
    return out


# --------------------------------------------------------------------------- shared loader / gene sets (MED4)
MD = expr.METHODS / "data"
REF = "gap200_roleT_crossT"
PROT_SLICES = [("anchor_axenic_protein", "day 14"), ("anchor_axenic_protein", "day 31"), ("anchor_axenic_protein", "day 89"),
               ("anchor_cocult_protein", "day 18"), ("anchor_cocult_protein", "day 31"), ("anchor_cocult_protein", "day 60"),
               ("anchor_cocult_protein", "day 89")]
RNA_SLICES = [("anchor_axenic_rna", "day 14"), ("anchor_cocult_rna", "day 18"), ("anchor_cocult_rna", "day 31"),
              ("anchor_cocult_rna", "day 60"), ("anchor_cocult_rna", "day 89")]
SLICE_LABEL = {("anchor_axenic_protein", "day 14"): "ax d14", ("anchor_axenic_protein", "day 31"): "ax d31 (death)",
               ("anchor_axenic_protein", "day 89"): "ax d89 (death)", ("anchor_axenic_rna", "day 14"): "ax d14"}
for _s, _d in PROT_SLICES + RNA_SLICES:
    SLICE_LABEL.setdefault((_s, _d), "cc " + _d.replace("day ", "d"))
MARKERS = {"PMM0920": "glnA", "PMM0246": "ntcA", "PMM1463": "glnB", "PMM0393": "pipX"}
DEDICATED = {"amt1": "sys_PMM0263", "urt": "sys_PMM0970", "cyn": "sys_PMM0370", "dpp": "sys_PMM0192"}
NON_N = {"pst": "sys_PMM0710", "phn": "sys_PMM0671", "sul1": "sys_PMM0644", "sul3": "sys_PMM0214",
         "fut/idiA2": "sys_PMM0489", "mnt": "sys_PMM0601", "lraI": "sys_PMM1029", "sbtA": "sys_PMM0213"}
LINKED_EXTRA = {"PMM0373": "cynS", "PMM1512": "glsF"}
UREASE = [f"PMM{n:04d}" for n in range(963, 970)]
PHOH = "PMM1284"


def load():
    de = pd.read_csv(expr.ANALYSIS / "data" / "de_long.csv.gz", low_memory=False)
    de = de[~de.is_pooled.astype(bool)].copy()
    sy = pd.read_csv(MD / "med4" / "p11_med4_systems.csv").set_index("system_id")
    gs = pd.read_csv(MD / "med4" / f"p3_med4_gene_systems_{REF}.csv")
    mem = gs.groupby("system_id").locus_tag.agg(lambda s: sorted(s)).to_dict()
    lb = pd.read_csv(MD / "med4" / "p18_med4_listing_basis.csv")
    coords = pd.read_csv(MD / "med4" / "raw" / "p3_med4_genome_coords.csv")
    names = {r.locus_tag: (r.gene_name if isinstance(r.gene_name, str) else "") for r in coords.itertuples()}
    prods = dict(zip(coords.locus_tag, coords["product"]))
    fl = pd.read_csv(MD / "med4" / "p11_med4_function_linked.csv")
    nl = pd.read_csv(MD / "med4" / "p11_med4_neighbour_linked.csv")
    return {"de": de, "sy": sy, "mem": mem, "lb": lb, "names": names, "prods": prods, "fl": fl, "nl": nl}


def gene_sets(L):
    """Ordered (group, system_id or '', locus_tag) rows for the MED4 gene sets used throughout."""
    sy, mem, lb = L["sy"], L["mem"], L["lb"]
    rows = []
    for k, sid in DEDICATED.items():
        rows += [("N dedicated: " + k, sid, m) for m in mem[sid]]
    broad = sorted(set(lb.system_id) - set(DEDICATED.values()))
    for sid in broad:
        flags = [f for f, c in (("efflux", "efflux_annotated"), ("known FP", "known_false_positive")) if bool(sy.loc[sid, c])]
        tag = (f"N broad: {F_short(sy.loc[sid, 'member_names'])} ({sid.replace('sys_', '')})"
               + (f" [{', '.join(flags)}]" if flags else ""))
        rows += [(tag, sid, m) for m in mem[sid]]
    linked = set()
    for df_ in (L["fl"], L["nl"]):
        x = df_[df_.system_id.isin(DEDICATED.values()) & (df_.fragment_of.astype(str) == "none")]
        linked |= set(x.locus_tag)
    linked |= set(LINKED_EXTRA) | (set(UREASE) & set(L["names"]))
    linked -= set(MARKERS)
    rows += [("linked enzymes", "", m) for m in sorted(linked)]
    rows += [("starvation markers", "", m) for m in MARKERS]
    for k, sid in NON_N.items():
        rows += [("non-N: " + k, sid, m) for m in mem[sid]]
    rows += [("marker: phoH", "", PHOH)]
    return pd.DataFrame(rows, columns=["group", "system_id", "locus_tag"])


def F_short(member_names, n=3):
    parts = []
    for m in str(member_names).split("|"):
        lt, _, g = m.partition(":")
        parts.append(g or lt)
    return "/".join(parts[:n]) + ("/…" if len(parts) > n else "")


def slice_values(de, short, tp):
    return de[(de.short_name == short) & (de.timepoint == tp)].set_index("locus_tag")


def aligned_difference(a: pd.Series, b: pd.Series) -> pd.Series:
    """a - b for loci (index) present and non-null in both (E7 difference-of-contrasts)."""
    j = a.dropna().index.intersection(b.dropna().index)
    return (a.loc[j] - b.loc[j]).sort_index()


def classify_profile(hours, medians, thr: float = 0.5):
    """Descriptive label of a median log2FC profile over ordered timepoints (E9).
    Returns (label, onset_hour, peak_hour). |m| < thr everywhere -> 'flat'. Up only (max >= thr, min > -thr):
    'up, early' if the first point >= thr falls in the first half of the time course, else 'up, late';
    'up, transient' if the last point is < thr/2 after a peak >= thr. Down only: the mirror image. Both directions:
    'mixed: up then down' / 'mixed: down then up' by which threshold is crossed first. NaN points are skipped."""
    pts = [(h, m) for h, m in zip(hours, medians) if m == m]
    if not pts:
        return "no data", None, None
    hs = [h for h, _ in pts]
    ms = [m for _, m in pts]
    half = len(pts) / 2
    peak_i = max(range(len(ms)), key=lambda i: abs(ms[i]))
    up = [i for i, m in enumerate(ms) if m >= thr]
    dn = [i for i, m in enumerate(ms) if m <= -thr]
    if not up and not dn:
        return "flat", None, hs[peak_i]
    if up and dn:
        lab = "mixed: up then down" if up[0] < dn[0] else "mixed: down then up"
        return lab, hs[min(up[0], dn[0])], hs[peak_i]
    idx, sign = (up, 1) if up else (dn, -1)
    word = "up" if sign > 0 else "down"
    if abs(ms[-1]) < thr / 2 or sign * ms[-1] < thr / 2:
        return f"{word}, transient", hs[idx[0]], hs[peak_i]
    return (f"{word}, early" if idx[0] < half else f"{word}, late"), hs[idx[0]], hs[peak_i]


def group_median(members: pd.DataFrame, values: pd.Series, key: str = "cluster_id") -> pd.DataFrame:
    """Per group (key): n_members, n_detected (members with a value), median of values over detected members."""
    rows = []
    for g, x in members.groupby(key):
        v = values.reindex(x.locus_tag).dropna()
        rows.append({key: g, "n_members": int(x.locus_tag.nunique()), "n_detected": int(len(v)),
                     "median": float(v.median()) if len(v) else float("nan")})
    return pd.DataFrame(rows)


def cell_status(statuses, filtered: bool = False):
    """(status, n_up, n_down, n_detected) for one system x table cell from the stored statuses of its detected subunits.
    up = >=1 significant_up and none significant_down; down = the reverse; mixed = both; ns = detected, none
    significant; no subunit in the table -> 'not detected' ('not listed' for filtered tables)."""
    st = [str(x) for x in statuses]
    nu, nd = st.count(SIG_UP), st.count(SIG_DOWN)
    if not st:
        return ("not listed" if filtered else "not detected"), 0, 0, 0
    lab = "mixed" if nu and nd else "up" if nu else "down" if nd else "ns"
    return lab, nu, nd, len(st)


def coculture_flags(d: dict):
    """Strict: cc protein up at d60 AND d89; not up in axenic protein d14, d31, d89; not up in axenic RNA d14; not up
    at any Tolonen N-dep timepoint. Loose: cc up at d60 OR d89; axenic d14 protein percentile < 0.75; not up in axenic
    d31/d89 protein; Tolonen N-dep max percentile < 0.90 (or not evaluable). All keys are required."""
    ax_death = [d["ax_d31_status"], d["ax_d89_status"]]
    strict = (d["cc_d60_status"] == "up" and d["cc_d89_status"] == "up" and d["ax_d14_status"] != "up"
              and "up" not in ax_death and d["ax_rna_d14_status"] != "up" and "up" not in d["ndep_statuses"])
    ax, nmax = d["ax_d14_pct"], d["ndep_max_pct"]
    loose = ((d["cc_d60_status"] == "up" or d["cc_d89_status"] == "up") and ax == ax and ax < 0.75
             and "up" not in ax_death and (nmax != nmax or nmax < 0.90))
    return bool(strict), bool(loose)


def up_loci(statuses: pd.Series, loci) -> list:
    """Member loci whose stored status is significant_up, in member order."""
    return [lt for lt in loci if statuses.get(lt) == SIG_UP]


# --------------------------------------------------------------------------- E11
def stimulon_level(pct: pd.Series, members) -> float:
    """Median rank percentile of the members detected in one slice (pct indexed by locus_tag; NaN = not detected)."""
    v = pct.reindex(list(members)).dropna()
    return float(v.median()) if len(v) else float("nan")


def system_excess(pct: pd.Series, level: float, loci) -> float:
    """Median over detected subunits of (percentile - stimulon level)."""
    v = pct.reindex(list(loci)).dropna()
    if not len(v) or level != level:
        return float("nan")
    return float((v - level).median())


def mean_pair(a, b) -> float:
    return float("nan") if (a != a or b != b) else (a + b) / 2


EC_CLASSES = {("3", "5"): "EC 3.5 C-N hydrolases (non-peptide)", ("3", "4"): "EC 3.4 peptidases",
              ("4", "3", "1"): "EC 4.3.1 ammonia-lyases"}


def ec_class(ec_id):
    """N-releasing EC class of an EC id (field-wise match), or None."""
    if not ec_id or not isinstance(ec_id, str):
        return None
    f = ec_id.split(":", 1)[-1].split(".")
    for key, lab in EC_CLASSES.items():
        if tuple(f[:len(key)]) == key:
            return lab
    return None


MARKERS_NOTE = ("starvation markers = glnA PMM0920, ntcA PMM0246, glnB PMM1463, pipX PMM0393 (pipX included; "
                "E10/E13 marker medians use glnA/ntcA/glnB only where stated)")


# --------------------------------------------------------------------------- E16
def combine_labels(labels) -> str:
    """Combine per-gene/system status labels with the E10 rule (up only / down only / both = mixed)."""
    labels = list(labels)
    det = [x for x in labels if x not in ("not detected", "not listed")]
    if not det:
        return "not listed" if "not listed" in labels else "not detected"
    nu, nd = det.count("up"), det.count("down")
    return "mixed" if nu and nd else "up" if nu else "down" if nd else "ns"


def count_up(labels):
    """(n with status up, n detected/listed) over system labels."""
    det = [x for x in labels if x not in ("not detected", "not listed")]
    return det.count("up"), len(det)


def _undet(x):
    return x in ("not detected", "not listed")


def axenic_word(d14, d31, d89) -> str:
    """kept = up at d31 and d89; dropped = up at d14 but not at both later; late = up at d89 only; else not up."""
    if all(_undet(x) for x in (d14, d31, d89)):
        return "n.d."
    if d31 == "up" and d89 == "up":
        return "kept"
    if d14 == "up":
        return "dropped"
    if d89 == "up":
        return "late"
    return "not up"


def cc_late_word(d60, d89) -> str:
    if _undet(d60) and _undet(d89):
        return "n.d."
    return "up" if d60 == "up" and d89 == "up" else "not up"


def any_up_word(labels) -> str:
    labels = list(labels)
    if all(_undet(x) for x in labels):
        return "n.l." if "not listed" in labels else "n.d."
    return "up" if "up" in labels else "not up"
