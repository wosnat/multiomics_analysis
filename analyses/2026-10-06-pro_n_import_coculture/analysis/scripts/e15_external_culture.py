"""E15 [external, not in KG] CC1A3 culture data: tidy conversion, summary, figure.

Source (read-only): C:/Users/oweisberg/Documents/GitHub/CC1A3/FCM/ - the researcher's CC1A3 experiment (same cultures as
the anchor omics). Workbooks are converted by scripts/e15_convert_xlsx.py run through
`uv run --no-project --with pandas --with openpyxl` (the analysis venv has no openpyxl); everything else runs here.
Derivations (N quotas, DON by difference) follow the source workbook formulas; see analysis/cc1a3.py.
Outputs: data/external/cc1a3/{raw_sheets/*.csv, cc1a3_tidy.csv, README.md}; data/explore/e15_culture_summary.csv;
figures/e15_culture_n.png/svg. data/external/ is git-ignored (analysis/.gitignore).
Run (repo root): .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/e15_external_culture.py [--convert]
"""
import subprocess
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
A = HERE.parent
sys.path.insert(0, str(A))
import cc1a3 as cc  # noqa: E402
import figs  # noqa: E402
from figs import F, plt  # noqa: E402

SRC = Path("C:/Users/oweisberg/Documents/GitHub/CC1A3/FCM")
EXT = A / "data" / "external" / "cc1a3"
RAW = EXT / "raw_sheets"
OUT = A / "data" / "explore"
NA_FILE, NB_FILE = "Osnat_CC1A3_N analysis.xlsx", "CC1A3_N_budget.xlsx"
COLS = ["source_file", "source_sheet", "condition", "sample_id", "bottle", "replicate", "day", "day_rounded", "quantity",
        "organism", "value", "unit", "kind", "derivation", "notes", "run", "used_in_n_budget"]
PROBLEMATIC = {"P0A-d33-sybr", "A0B-d15-sybr", "C0C-d15-sybr", "P0A-d33", "C0C-d15", "P7A-d6-sybr", "P7A-d6"}
DERIV_BIOMASS = {"MED4": "cells/ml * 12.5 fg N/cell / 14 * 1e-9 * 1e3 (Qp; notebook cell 56/58; sheet '=G*8.92857E-10*1000')",
                 "HOT1A3": "cells/ml * 25 fg N/cell / 14 * 1e-9 * 1e3 (Qh; notebook cell 56/58; sheet '=F*1.78571E-09*1000')"}
DERIV_DON = "DON(t) = Total N(t0) - (N biomass HOT1A3 + N biomass MED4 + NH4)(t); sheet '=$L$t0 - SUM(H:J)'; closed system, NO3 not included"
COND_COL = {"axenic MED4": F.CAT[2], "coculture": F.CAT[6], "HOT1A3 alone": F.CAT[3]}


def convert(force=False):
    if force or not RAW.exists() or not any(RAW.glob("*.csv")):
        cmd = ["uv", "run", "--no-project", "--with", "pandas", "--with", "openpyxl", "python",
               str(HERE / "e15_convert_xlsx.py"), str(SRC), str(RAW)]
        subprocess.run(cmd, check=True)


def raw(name):
    return pd.read_csv(RAW / name, header=None)


def row(**kw):
    d = {c: None for c in COLS}
    d.update(kw)
    if d["sample_id"] is not None and d["condition"] is None:
        p = cc.parse_sample(d["sample_id"])
        if p:
            d["condition"], d["bottle"], d["replicate"] = cc.CONDITION[p[0]], p[1], p[2]
    if d["day"] is not None and d["day"] == d["day"]:
        d["day_rounded"] = cc.day_rounded(float(d["day"]))
    return d


def nh4_rows(budget_nh4):
    """Instrument runs (1:100 dilution; uM = reading * 100) + the rerun sheet (1:500)."""
    out = []
    r1 = raw("n_analysis__231106_Osnat_NH4.run_RRR.csv")
    r2 = raw("n_analysis__231106_Osnat_NH4_contR1_RRR.csv")
    samples = raw("n_analysis__samples.csv").iloc[1:, :3].dropna()
    day_of = dict(zip(samples[0], samples[2].astype(float)))
    runs = [("231106_Osnat_NH4.run (1:100)", r1.iloc[20:50], 1, 9, "231106_Osnat_NH4.run RRR"),
            ("231106_Osnat_NH4 contR1 (1:100)", r2.iloc[15:38], 1, 8, "231106_Osnat_NH4 contR1 RRR")]
    for run, df, kc, vc, sheet in runs:
        for k, v in zip(df[kc], df[vc]):
            if pd.isna(v) or str(k).strip() in ("Cal.", "Drift", "Baseline", "cal 1", "cal 2", "Primer", "B"):
                continue
            k = str(k).strip()
            if k == "SW":
                out.append(row(source_file=NA_FILE, source_sheet=sheet, condition="dilution seawater", sample_id="SW",
                               quantity="NH4_uM", value=float(v), unit="uM (reading of the diluent, not x100)",
                               kind="measured", run=run, notes="June filtered SW used for the 1:100 dilution"))
                continue
            sid = "P3A" if k == "P3A #2" else k
            if k == "blank":
                val = float(v) * 100
                out.append(row(source_file=NA_FILE, source_sheet=sheet, condition="medium (PRO99-lowN)",
                               sample_id="medium ('blank' in run; 'P99' in rerun sheet)", day=0.0, quantity="NH4_uM",
                               value=val, unit="uM", kind="measured", run=run,
                               used_in_n_budget=bool(abs(val - budget_nh4.get("t0", np.nan)) < 1e-6),
                               notes="starting medium; sheet notes say 100 uM NH4 was added"))
                continue
            val = float(v) * 100
            used = sid in budget_nh4 and abs(val - budget_nh4[sid]) < 1e-6
            out.append(row(source_file=NA_FILE, source_sheet=sheet, sample_id=sid, day=day_of.get(sid),
                           quantity="NH4_uM", value=val, unit="uM", kind="measured", run=run, used_in_n_budget=used,
                           notes=("second measurement of P3A ('P3A #2')" if k == "P3A #2" else None)))
    rr = raw("n_analysis__NH4_rerun.csv")
    for i in (5, 6):
        sid = rr.iloc[i, 0]
        for col, run, dil in ((3, "rerun (1:500)", 500), (6, "previous run (1:100) as quoted in rerun sheet", 100)):
            val = float(rr.iloc[i, col])
            is_med = sid == "P99"
            used = abs(val - budget_nh4.get("t0" if is_med else sid, np.nan)) < 1e-6
            out.append(row(source_file=NA_FILE, source_sheet="NH4 rerun",
                           condition="medium (PRO99-lowN)" if is_med else None,
                           sample_id="medium ('blank' in run; 'P99' in rerun sheet)" if is_med else sid,
                           day=0.0 if is_med else 89.0, quantity="NH4_uM", value=val, unit="uM", kind="measured",
                           run=run, used_in_n_budget=used, notes=f"dilution 1:{dil}"))
    return out


def no3_rows():
    d = raw("n_analysis__NO3_06112023.csv").iloc[2:13]
    return [row(source_file=NA_FILE, source_sheet="NO3 06112023", sample_id=s, day=float(dy), quantity="NO3_uM",
                value=float(v), unit="uM", kind="measured", run="231106_Osnat_NO3R1 (non-diluted)",
                notes="no nitrate/nitrite was added to the medium (sheet note)")
            for s, dy, v in zip(d[0], d[3], d[4])]


def fcm_rows():
    out = []
    a = pd.read_csv(SRC / "data" / "CC1A3_FCM_PRO_nosybr.csv")
    for r in a.itertuples():
        out.append(row(source_file="data/CC1A3_FCM_PRO_nosybr.csv", source_sheet=None, sample_id=r.patient_id,
                       condition=cc.CONDITION[r.condition], bottle=r.bottle, replicate=r.replicate, day=float(r.Day),
                       quantity="cells_per_ml", organism="MED4", value=r.PRO_nosybr, unit="cells/ml", kind="measured",
                       notes=f"FCM no SYBR, PRO gate; events {r.events}; sample {r.sample_id}"
                             + ("; events<=40 (notebook plotting filter)" if r.events <= 40 else "")
                             + ("; notebook 'problematic_samples'" if r.sample_id in PROBLEMATIC else "")))
    b = pd.read_csv(SRC / "data" / "CC1A3_FCM_sybr.csv")
    b = b[(b.cluster_id == "ALT") & b.condition.isin(["A", "C"])]
    for r in b.itertuples():
        out.append(row(source_file="data/CC1A3_FCM_sybr.csv", source_sheet=None, sample_id=r.patient_id,
                       condition=cc.CONDITION[r.condition], bottle=r.bottle, replicate=r.replicate, day=float(r.Day),
                       quantity="cells_per_ml", organism="HOT1A3", value=r.cells, unit="cells/ml", kind="measured",
                       notes=f"FCM SYBR, ALT cluster; events {r.Freq}; sample {r.sample_id}"
                             + ("; events<=40 (notebook plotting filter)" if r.Freq <= 40 else "")
                             + ("; notebook 'problematic_samples'" if r.sample_id in PROBLEMATIC else "")))
    return out


def budget_rows():
    """'N budget' sheet (omics bottles + t0 estimates) and CC1A3_N_budget.xlsx (biomass for every FCM sample)."""
    nb = raw("n_analysis__N_budget.csv")
    nb.columns = list(nb.iloc[0])[:len(nb.columns)]
    nb = nb.iloc[1:].dropna(subset=["condition"])
    for c in ["Day", "cells/ml HOT1A3", "cells/ml med4", "N biomass HOT1A3", "N biomass med4", "NH4", "DON", "Total N"]:
        nb[c] = pd.to_numeric(nb[c], errors="coerce")
    out, budget_nh4, checks = [], {}, []
    for cond in ("A", "C", "P"):
        z = nb[nb.condition == cond]
        t0 = z[z.Sample == "estimated"].iloc[0]
        tot0 = cc.total_n0(t0.NH4, t0.DON, t0["N biomass HOT1A3"], t0["N biomass med4"])
        checks.append(abs(tot0 - t0["Total N"]))
        budget_nh4["t0"] = t0.NH4
        base = dict(source_file=NA_FILE, source_sheet="N budget", condition=cc.CONDITION[cond], sample_id="estimated",
                    day=0.0)
        for org, col in (("HOT1A3", "cells/ml HOT1A3"), ("MED4", "cells/ml med4")):
            if t0[col] == t0[col]:
                out.append(row(**base, quantity="cells_per_ml", organism=org, value=t0[col], unit="cells/ml",
                               kind="derived", derivation="assumed inoculum (sheet 'estimated' row)"))
                out.append(row(**base, quantity="N_biomass_uM", organism=org, value=t0[f"N biomass {'med4' if org == 'MED4' else 'HOT1A3'}"],
                               unit="uM N", kind="derived", derivation=DERIV_BIOMASS[org] + "; inoculum assumed"))
        out.append(row(**base, quantity="DON_uM", value=t0.DON, unit="uM N", kind="derived",
                       derivation="assumed DON at t0 = 20 uM (sheet 'estimated' row)"))
        out.append(row(**base, quantity="total_N_uM", value=t0["Total N"], unit="uM N", kind="derived",
                       derivation="Total N(t0) = NH4(medium, 146.99 measured) + DON(t0, 20 assumed) + biomass(t0 inoculum); "
                                  "sheet '=SUM(H:K)'; held constant (closed system)"))
        for r in z[z.Sample != "estimated"].itertuples(index=False):
            r = dict(zip(z.columns, r))
            sid = r["Sample"]
            budget_nh4[sid] = r["NH4"]
            don = cc.don_by_difference(tot0, r["N biomass HOT1A3"], r["N biomass med4"], r["NH4"])
            checks.append(abs(don - r["DON"]))
            b = dict(source_file=NA_FILE, source_sheet="N budget", sample_id=sid, day=float(r["Day"]))
            out.append(row(**b, quantity="DON_uM", value=r["DON"], unit="uM N", kind="derived", derivation=DERIV_DON,
                           notes="NEGATIVE: biomass + NH4 exceed the t0 total" if r["DON"] < 0 else None))
            for org, cc_col, nb_col in (("HOT1A3", "cells/ml HOT1A3", "N biomass HOT1A3"), ("MED4", "cells/ml med4", "N biomass med4")):
                if r[cc_col] == r[cc_col]:
                    checks.append(abs(cc.n_biomass_uM(r[cc_col], org) - r[nb_col]))
                    out.append(row(**b, quantity="cells_per_ml", organism=org, value=r[cc_col], unit="cells/ml",
                                   kind="measured", notes="as entered in the N budget sheet (FCM)"))
                    out.append(row(**b, quantity="N_biomass_uM", organism=org, value=r[nb_col], unit="uM N",
                                   kind="derived", derivation=DERIV_BIOMASS[org]))
    assert max(checks) < 1e-6, max(checks)
    # CC1A3_N_budget.xlsx: biomass for every FCM sample
    s = raw("n_budget_34d__Sheet1.csv")
    s.columns = list(s.iloc[0])
    s = s.iloc[1:]
    for org, c1, c2 in (("HOT1A3", "cells/ml HOT1A3", "N biomass HOT1A3"), ("MED4", "cells/ml med4", "N biomass med4")):
        z = s.dropna(subset=[c2])
        for r in z.itertuples(index=False):
            r = dict(zip(s.columns, r))
            v, cells = float(r[c2]), float(r[c1])
            assert abs(cc.n_biomass_uM(cells, org) - v) < 1e-6
            out.append(row(source_file=NB_FILE, source_sheet="Sheet1", sample_id=r["Sample"],
                           condition=cc.CONDITION[r["condition"]], day=float(r["Day"]), quantity="N_biomass_uM",
                           organism=org, value=v, unit="uM N", kind="derived", derivation=DERIV_BIOMASS[org],
                           notes=f"from cells/ml {cells:.6g}"))
    return out, budget_nh4, len(checks)


def don_rate_rows():
    d = raw("n_analysis__DON2DIN_rate.csv").iloc[1:]
    out = []
    for r in d.itertuples(index=False):
        if pd.isna(r[7]):
            continue
        out.append(row(source_file=NA_FILE, source_sheet="DON2DIN rate", condition=cc.CONDITION[r[1]], day=float(r[2]),
                       quantity="DON_log_change_rate", value=float(r[7]), unit="per s", kind="derived",
                       derivation="(ln mean DON(t) - ln mean DON(t-1)) / (t - t-1), t in s; sheet 'DON2DIN rate'"))
    return out


def summary(T):
    s = T[T.source_sheet.eq("N budget") | T.quantity.isin(["NO3_uM"]) | (T.quantity.eq("NH4_uM") & T.used_in_n_budget.eq(True))].copy()
    s = s[s.sample_id.ne("estimated") & s.condition.isin(list(cc.CONDITION.values()))]
    s["q"] = np.where(s.quantity.eq("cells_per_ml"), "cells_" + s.organism.fillna(""), s.quantity)
    s = s[s.q.isin(["cells_MED4", "cells_HOT1A3", "NH4_uM", "NO3_uM", "DON_uM"])]
    rows = []
    for (cond, dr, bottle), g in s.groupby(["condition", "day_rounded", "bottle"]):
        d = {"condition": cond, "day_rounded": dr, "bottle": bottle,
             "days_as_given": "|".join(sorted({f"{x:g}" for x in g.day})),
             "omics_sampling_day": cc.is_omics_day({v: k for k, v in cc.CONDITION.items()}[cond], dr),
             "samples": "|".join(sorted(set(g.sample_id)))}
        for q in ["cells_MED4", "cells_HOT1A3", "NH4_uM", "NO3_uM", "DON_uM"]:
            v = g[g.q == q].value.astype(float)
            d[f"{q}_mean"], d[f"{q}_min"], d[f"{q}_max"], d[f"{q}_n"] = (v.mean(), v.min(), v.max(), len(v)) if len(v) else (np.nan,) * 3 + (0,)
        rows.append(d)
    S = pd.DataFrame(rows).sort_values(["condition", "day_rounded", "bottle"])
    S.insert(0, "provenance", "[external, not in KG] CC1A3 (researcher's experiment); N budget sheet samples")
    return S


def figure(T, budget_nh4):
    fig, axs = plt.subplots(3, 1, figsize=(11, 11), sharex=True, gridspec_kw={"hspace": 0.12})
    omics = {11: "cc", 14: "ax", 18: "cc", 31: "ax+cc", 60: "cc", 89: "ax+cc"}
    for ax in axs:
        for dday in omics:
            ax.axvline(dday, color=F.GRID, linewidth=1.4, zorder=0)
    for k, (dday, who) in enumerate(omics.items()):
        axs[0].text(dday, 1.02, who, transform=axs[0].get_xaxis_transform(), ha="center", fontsize=7.5, color=F.TEXT2)
    axs[0].text(0, 1.09, "grey verticals = protein/RNA sampled (ax = axenic MED4, cc = coculture)",
                transform=axs[0].transAxes, fontsize=8, color=F.TEXT2)
    fc = T[T.quantity.eq("cells_per_ml") & T.source_file.str.startswith("data/")].copy()
    fc["low"] = fc.notes.str.contains("events<=40")
    fc["bad"] = fc.notes.str.contains("problematic")
    for ax, org, conds in ((axs[0], "MED4", ["axenic MED4", "coculture"]), (axs[1], "HOT1A3", ["HOT1A3 alone", "coculture"])):
        for cond in conds:
            z = fc[(fc.organism == org) & (fc.condition == cond)]
            col = COND_COL[cond]
            ts = z[z.bottle == 0]
            ok = ts[~ts.low & ~ts.bad & (ts.value > 0)]
            m = ok.groupby("day").value.apply(lambda v: np.exp(np.log(v).mean()))
            ax.plot(m.index, m.values, color=col, linewidth=1.6, label=f"{cond}: time-series bottles (geometric mean of samples >40 events)")
            for low in (False, True):
                q = ts[(ts.low == low) & ~ts.bad]
                ax.scatter(q.day, q.value, s=10, color=col if not low else "none", edgecolor=col, linewidth=0.6, alpha=0.6, zorder=2)
            q = z[z.bad]
            ax.scatter(q.day, q.value, s=22, marker="x", color=col, linewidth=0.9, zorder=2)
            ob = z[z.bottle != 0]
            ax.scatter(ob.day, ob.value, s=34, marker="D", color=np.where(ob.low, "none", col).tolist(), edgecolor=col,
                       linewidth=0.9, zorder=3, label=f"{cond}: omics-sampling bottles")
        ax.set_yscale("log")
        ax.set_ylabel(f"{org} cells/ml (FCM, log)", fontsize=8.5)
        ax.legend(fontsize=7, frameon=False, loc="lower left", ncol=2)
    axs[0].set_ylim(10, 3e8)
    axs[1].set_ylim(1e4, 1e8)
    axs[0].text(0.99, 0.97, "hollow = ≤40 FCM events (notebook's plotting filter); × = notebook 'problematic' sample", transform=axs[0].transAxes,
                ha="right", va="top", fontsize=7, color=F.TEXT2)
    # NH4
    ax = axs[2]
    nh = T[T.quantity.eq("NH4_uM") & T.used_in_n_budget.eq(True) & T.condition.isin(list(cc.CONDITION.values()))]
    for cond, col in COND_COL.items():
        z = nh[nh.condition == cond]
        ax.scatter(z.day, z.value, s=26, color=col, zorder=3, edgecolor=F.SURF, linewidth=0.5)
        m = z.groupby("day_rounded").agg(day=("day", "mean"), v=("value", "mean")).sort_values("day")
        med = budget_nh4["t0"]
        ax.plot([0] + list(m.day), [med] + list(m.v), color=col, linewidth=1.6, label=cond)
    p1a = nh[nh.sample_id == "P1A"]
    if len(p1a):
        ax.annotate("P1A", (p1a.day.iloc[0], p1a.value.iloc[0]), xytext=(6, 4), textcoords="offset points", fontsize=7.5)
    ax.axhline(budget_nh4["t0"], color=F.TEXT2, linestyle="--", linewidth=0.9)
    ax.text(91, budget_nh4["t0"] + 4, f"medium start {budget_nh4['t0']:.0f} µM (rerun 163; 100 µM NH4 added per sheet note)",
            ha="right", fontsize=7.5, color=F.TEXT2)
    ax.set_ylabel("NH₄⁺ (µM)", fontsize=8.5)
    ax.set_xlabel("day", fontsize=8.5)
    ax.set_ylim(0, 300)
    ax.legend(fontsize=7.5, frameon=False, loc="upper left", title="replicates = points; line = mean (from the medium value at day 0)",
              title_fontsize=7.5)
    axs[2].set_xlim(-1, 93)
    for a_, lab in zip(axs, "abc"):
        a_.text(-0.07, 1.0, f"({lab})", transform=a_.transAxes, fontsize=10, fontweight="bold", va="top")
        a_.tick_params(labelsize=8)
        for s_ in ("top", "right"):
            a_.spines[s_].set_visible(False)
    figs.head(fig, "[external, not in KG] CC1A3 culture N budget",
              "Source: researcher's CC1A3 experiment (same cultures as the anchor omics), CC1A3/FCM/: FCM CSVs (cells), "
              "'Osnat_CC1A3_N analysis.xlsx'\n(NH4, values used in the N budget sheet). "
              "Tidy copy: analysis/data/external/cc1a3/cc1a3_tidy.csv (git-ignored)." "\n"
              "Time-series bottles (bottle 0) were sampled repeatedly; "
              "omics bottles were harvested once (axenic bottle 7 was sampled days 3–14).")
    fig.subplots_adjust(top=0.86, left=0.1, right=0.98, bottom=0.06)
    return figs.save(fig, "e15_culture_n")


README = """# CC1A3 culture data — [external, not in KG]

The researcher's own CC1A3 bottle experiment: MED4 axenic (P), HOT1A3 alone (A), and coculture (C), in PRO99-lowN.
These are the same cultures as the anchor omics. The researcher authorised using these data in this analysis.
**Not in the knowledge graph. Not for publication until the researcher decides.**
`analysis/data/external/` is git-ignored.

- Converted: {today} by `analysis/scripts/e15_external_culture.py`. The workbook step is `scripts/e15_convert_xlsx.py`, run via `uv run --no-project --with pandas --with openpyxl`.
- Source folder (read-only, not modified): `C:/Users/oweisberg/Documents/GitHub/CC1A3/FCM/`
  - `Osnat_CC1A3_N analysis.xlsx`, sheets:
    - N budget
    - NH4 06112023
    - NO3 06112023
    - NH4 rerun
    - samples
    - DON2DIN rate
    - the instrument run sheets 231106_Osnat_NH4.run RRR, 231106_Osnat_NH4 contR1 RRR and 231106_Osnat_NO3R1 RRR
  - `CC1A3_N_budget.xlsx`: cells/ml and N biomass for every FCM sample. It was written by `cc1A3 notebook.ipynb` cell 64.
  - `data/CC1A3_FCM_PRO_nosybr.csv`: MED4 counts, PRO gate, no SYBR.
  - `data/CC1A3_FCM_sybr.csv`: HOT1A3 counts, SYBR, ALT cluster.
  - Notebooks `cc1A3 notebook.ipynb` and `cc1A3 N budget.ipynb`. These were read for the derivations below.

## Files
- `raw_sheets/*.csv`: every workbook sheet as cached values, headerless. Also the formulas of 'N budget' and 'NH4 06112023' (`*__formulas.csv`).
- `cc1a3_tidy.csv` has one value per row.
  - Columns: source_file, source_sheet, condition, sample_id, bottle, replicate, day (as given), day_rounded, quantity, organism, value, unit, kind (measured | derived), derivation, notes, run, used_in_n_budget.
  - Quantities: cells_per_ml (FCM), NH4_uM, NO3_uM, N_biomass_uM, DON_uM, total_N_uM, DON_log_change_rate.

## Derivations (quoted from the sources)
- **N quotas**, from notebook cell 56: `Qp = 12.5 * 1e-9 / 14`, `Qh = 25 * 1e-9 / 14`. That is 12.5 fg N per MED4 cell and 25 fg N per HOT1A3 cell, converted to µmol per cell.
- **N biomass**, from notebook cell 58: `ref_Bp = cells/ml * Q * 1e3`, in µmol N per L. The same formula is in the sheet: `=G*8.92857142857143E-10*1000` for MED4 and `=F*1.78571428571428E-09*1000` for HOT1A3.
- **Total N at t0**, sheet: `=SUM(H:K)`. This is NH4 of the medium (146.99 µM, measured) + DON(t0) (20 µM, assumed) + biomass of the assumed inoculum (1e7 HOT1A3 and 1e6 MED4 cells/ml).
- **DON**, sheet: `=$L$t0 - SUM(H:J)`. It is DON by difference: Total N(t0) − N biomass HOT1A3 − N biomass MED4 − NH4. This assumes a closed system with constant total N. NO3 is not included. Negative values are flagged in `notes`.
- **NH4**, sheet: `=VLOOKUP(sample, 'NH4 06112023'!A:F, 6, FALSE)`. This takes the first matching row. Readings were taken at 1:100 dilution, so µM = reading × 100.
- **DON2DIN rate**: Δ ln(mean DON) / Δt, with t in seconds.

## NH4 runs (reported, not reconciled)
Every instrument value is kept. `used_in_n_budget` marks the value the N budget sheet takes.
- **Medium:** 146.99 µM in contR1 (the "blank"); 163 µM in the 1:500 rerun ("P99"). The N budget uses 146.99.
- **A5A:** 275.26 µM in run 1; 271.5 µM in the rerun. The N budget uses 275.26.
- **A5B:** 244.83 µM in run 1; 254.85 µM in contR1. The N budget uses 244.83, which is the first VLOOKUP match.
- **P3A:** 20.84 µM in run 1; 39.86 µM in contR1 ("P3A #2"). The N budget uses 39.86, which is hard-coded in the NH4 sheet.
"""


def main():
    convert("--convert" in sys.argv)
    EXT.mkdir(parents=True, exist_ok=True)
    b_rows, budget_nh4, n_checks = budget_rows()
    rows = fcm_rows() + nh4_rows(budget_nh4) + no3_rows() + b_rows + don_rate_rows()
    T = pd.DataFrame(rows, columns=COLS)
    T.to_csv(EXT / "cc1a3_tidy.csv", index=False)
    (EXT / "README.md").write_text(README.format(today=date.today().isoformat()), encoding="utf-8")
    S = summary(T)
    S.to_csv(OUT / "e15_culture_summary.csv", index=False)
    files = figure(T, budget_nh4)
    print([f.name for f in files], "rows", len(T), "formula checks", n_checks)
    return T, S


if __name__ == "__main__":
    T, S = main()
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(T.groupby(["quantity", "kind"]).size().to_string())
    print(S[["condition", "day_rounded", "bottle", "days_as_given", "omics_sampling_day", "cells_MED4_mean", "cells_MED4_min",
             "cells_MED4_max", "cells_HOT1A3_mean", "NH4_uM_mean", "NH4_uM_min", "NH4_uM_max", "NO3_uM_mean", "DON_uM_mean",
             "DON_uM_min", "DON_uM_max"]].to_string(index=False, float_format=lambda x: f"{x:.4g}"))
