"""Stage 2 (analysis milestone): header block - sanity gate, calibration C1-C4, P1/P2, expected-negatives 1-3, and the
(a)/(b) variant computation for the MED4 dedicated N systems. No KG calls: reads analysis/data/de_long.csv.gz (stage 1)
and methods v1.6.1 tables. Significance = stored expression_status. The pooled 'days 60+89' slice is never used.
Where the proposal leaves a rule open, every variant the coordinator listed is computed and labelled.

Outputs (analysis/data/s2_*.csv, s2_outcomes.csv, s2_summary.json).
Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/analysis/scripts/s2_header_block.py
"""
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import expr  # noqa: E402
from expr import nt  # noqa: E402

DATA = HERE.parent / "data"
MD = expr.METHODS / "data"
REF = "gap200_roleT_crossT"
COC_DAYS = ["day 18", "day 31", "day 60", "day 89"]
OUT = []   # outcome rows


def outcome(check, variant, passed, detail):
    OUT.append({"check": check, "variant": variant, "outcome": passed, "detail": detail})


def load_methods(tag):
    sy = pd.read_csv(MD / tag / f"p11_{tag}_systems.csv").set_index("system_id")
    gs = pd.read_csv(MD / tag / f"p3_{tag}_gene_systems_{REF}.csv")
    roles = pd.read_csv(MD / tag / f"p2_{tag}_gene_roles.csv").set_index("locus_tag")
    mem = gs.groupby("system_id").locus_tag.agg(lambda s: sorted(s)).to_dict()
    return sy, mem, roles


def gene_rows(de, short, tps, loci, names):
    out = []
    for tp in tps:
        x = de[(de.short_name == short) & (de.timepoint == tp)].set_index("locus_tag")
        for lt in loci:
            if lt in x.index:
                r = x.loc[lt]
                out.append({"table": short, "timepoint": tp, "locus_tag": lt, "gene_name": names.get(lt),
                            "expression_status": r.expression_status, "log2fc": r.log2fc, "padj": r.padj,
                            "rank_percentile": r.rank_percentile, "percentile_valid": r.percentile_valid})
            else:
                out.append({"table": short, "timepoint": tp, "locus_tag": lt, "gene_name": names.get(lt),
                            "expression_status": "not listed"})
    return out


def main():
    de = pd.read_csv(DATA / "de_long.csv.gz", low_memory=False)
    de = de[~de.is_pooled.astype(bool)]
    sy4, mem4, roles4 = load_methods("med4")
    n4 = roles4.gene_name.to_dict()
    co4 = pd.read_csv(MD / "med4" / "raw" / "p3_med4_genome_coords.csv").set_index("locus_tag").gene_name.to_dict()
    n4 = {**co4, **{k: v for k, v in n4.items() if isinstance(v, str)}}

    # ---------------------------------------------------------------- 1 sanity gate
    markers = {"PMM0920": "glnA", "PMM0246": "ntcA", "PMM1463": "glnB"}
    g = []
    for short, tps in (("anchor_cocult_protein", COC_DAYS), ("anchor_axenic_protein", ["day 14"]),
                       ("anchor_cocult_rna", COC_DAYS), ("anchor_axenic_rna", ["day 14"])):
        g += gene_rows(de, short, tps, list(markers), markers)
    G = pd.DataFrame(g)
    G.to_csv(DATA / "s2_sanity_grid.csv", index=False)
    prot = G[G.table.str.contains("protein")]
    up = prot.assign(up=prot.expression_status == expr.SIG_UP)
    s_pass = bool(up.up.all() and len(up) == 15)
    outcome("1 sanity gate", "S (all 3 markers sig_up in protein at all 5 slices)", s_pass,
            f"{int(up.up.sum())}/15 marker x slice protein cells significant_up")
    lres = []
    for lt in markers:
        x = up[up.locus_tag == lt]
        ax = bool(x[(x.table == "anchor_axenic_protein")].up.all())
        nco = int(x[(x.table == "anchor_cocult_protein")].up.sum())
        lres.append((lt, ax, nco))
    outcome("1 sanity gate", "L (each marker sig_up at axenic d14 and >= 3 of 4 coculture days, protein)",
            all(a and n >= 3 for _, a, n in lres),
            "; ".join(f"{markers[lt]} axenic d14 up={a}, coculture days up={n}/4" for lt, a, n in lres))

    # ---------------------------------------------------------------- 2 calibration C1-C3
    cyn, urt = mem4["sys_PMM0370"], mem4["sys_PMM0970"]
    ctx = {"PMM0373": "cynS", "PMM0963": "ureC", "PMM0964": "ureB", "PMM0965": "ureA"}
    c = []
    for short in ("cal_tolonen_cyanate", "cal_tolonen_urea"):
        rows = gene_rows(de, short, ["steady state"], cyn + urt + list(ctx), n4)
        for r in rows:
            r["system"] = "cyn" if r["locus_tag"] in cyn else ("urt" if r["locus_tag"] in urt else "context (not in rule)")
        c += rows
    Cg = pd.DataFrame(c)
    Cg.to_csv(DATA / "s2_calibration_tolonen_grid.csv", index=False)

    def med(short, loci):
        return expr.system_stats(de, short, "steady state", loci)["median_percentile"]
    cyn_cy, cyn_ur = med("cal_tolonen_cyanate", cyn), med("cal_tolonen_urea", cyn)
    urt_ur, urt_cy = med("cal_tolonen_urea", urt), med("cal_tolonen_cyanate", urt)
    outcome("2 calibration", "C1 (cyn median percentile on cyanate >= 0.90)", cyn_cy >= 0.90, f"cyn on cyanate {cyn_cy:.4f}")
    outcome("2 calibration", "C2 (urt median percentile on urea >= 0.90)", urt_ur >= 0.90, f"urt on urea {urt_ur:.4f}")
    outcome("2 calibration", "C3 (cyn(cyanate)-cyn(urea) >= 0.10 and urt(urea)-urt(cyanate) >= 0.10)",
            (cyn_cy - cyn_ur >= 0.10 - 1e-9) and (urt_ur - urt_cy >= 0.10 - 1e-9),
            f"cyn {cyn_cy:.4f} vs {cyn_ur:.4f} (diff {cyn_cy - cyn_ur:.4f}); urt {urt_ur:.4f} vs {urt_cy:.4f} "
            f"(diff {urt_ur - urt_cy:.4f})")

    # ---------------------------------------------------------------- 3 C4 acute-starvation fingerprint
    amt1 = mem4["sys_PMM0263"]
    systems_c4 = {"amt1": amt1, "urt": urt, "cyn": cyn}
    studies = {"Tolonen N deprivation": ("cal_tolonen_ndep", ["12h", "24h", "48h"]),
               "Read N-depleted (filtered)": ("cal_read_ndep", ["12h", "24h"])}
    c4 = []
    for study, (short, tps) in studies.items():
        res = {}
        for sname, loci in systems_c4.items():
            rows = gene_rows(de, short, tps, loci, n4)
            for r in rows:
                r.update({"study": study, "system": sname})
            c4 += rows
            grid = {tp: {r["locus_tag"]: r["expression_status"] for r in rows
                         if r["timepoint"] == tp and r["expression_status"] != "not listed"} for tp in tps}
            res[sname] = (expr.c4_any(grid), expr.c4_half(grid))
        for vi, vname in enumerate(("C4-any (>= 1 subunit up at >= 1 timepoint)",
                                    "C4-half (>= half of detected/listed subunits up at one timepoint)")):
            outcome("3 C4 " + study, vname, all(v[vi] for v in res.values()),
                    "; ".join(f"{s} up={v[vi]}" for s, v in res.items()))
    pd.DataFrame(c4).to_csv(DATA / "s2_c4_grid.csv", index=False)

    # ---------------------------------------------------------------- 4 P1 / P2
    p = []
    for tp in ("day 60", "day 89"):
        a = expr.system_stats(de, "anchor_cocult_rna", tp, amt1)["median_percentile"]
        pool = expr.system_stats(de, "anchor_cocult_rna", tp, urt + cyn)["median_percentile"]
        mu = expr.system_stats(de, "anchor_cocult_rna", tp, urt)["median_percentile"]
        mc = expr.system_stats(de, "anchor_cocult_rna", tp, cyn)["median_percentile"]
        sysmed = float(pd.Series([mu, mc]).median())
        p.append({"timepoint": tp, "amt1_rna_percentile": a, "urt_median": mu, "cyn_median": mc,
                  "urt_cyn_pooled_median_8_subunits": pool, "median_of_system_medians": sysmed,
                  "P1_ge_0.90": a >= 0.90, "P2_pool": a >= pool, "P2_sys": a >= sysmed})
    P = pd.DataFrame(p)
    P.to_csv(DATA / "s2_p1p2.csv", index=False)
    outcome("4 P1", "amt1 RNA percentile >= 0.90 at d60 and d89", bool(P["P1_ge_0.90"].all()),
            "; ".join(f"{r.timepoint} {r.amt1_rna_percentile:.4f}" for r in P.itertuples()))
    for col, v in (("P2_pool", "P2-pool (median over 8 urt+cyn subunits)"), ("P2_sys", "P2-sys (median of 2 system medians)")):
        for r in P.itertuples():
            ref = r.urt_cyn_pooled_median_8_subunits if col == "P2_pool" else r.median_of_system_medians
            outcome("4 P2 " + r.timepoint, v, bool(getattr(r, col)), f"amt1 {r.amt1_rna_percentile:.4f} vs {ref:.4f}")

    # ---------------------------------------------------------------- 5 expected-negative 1
    cls = pd.read_csv(MD / "med4" / "p12_med4_system_substrates_classified.csv", low_memory=False)
    nn = cls[cls.compound_class_final.isin(["nitrate", "nitrite"])]
    e1 = []
    for col in ("can_use_window", "can_use_run", "can_use_window_ms", "can_use_run_ms"):
        for k, v in nn[col].astype(str).value_counts().items():
            e1.append({"column": col, "value": k, "rows": int(v)})
    E1 = pd.DataFrame(e1)
    E1.to_csv(DATA / "s2_expneg1.csv", index=False)
    bad = nn[nn.can_use_window.astype(str).isin(["co-located", "elsewhere in genome"])
             | nn.can_use_run.astype(str).isin(["co-located", "elsewhere in genome"])]
    outcome("5 expected-negative 1", "every MED4 nitrate/nitrite row can_use False (window and run)", bool(bad.empty),
            f"{len(nn)} rows ({nn.compound_class_final.value_counts().to_dict()}); usable rows: {len(bad)}")

    # ---------------------------------------------------------------- 6 expected-negative 2
    e2 = []

    def n_systems(tag):
        lb = pd.read_csv(MD / tag / f"p18_{tag}_listing_basis.csv")
        ded = set(lb[(lb.listing_basis == "dedicated") & ~lb.known_false_positive.astype(bool)].system_id)
        f2 = pd.read_csv(expr.METHODS / "figures" / "fig2_cells.csv")
        blk = set(f2[(f2.strain == tag) & (f2.block == "inorganic") & f2.best_system.notna()].best_system)
        return sorted(ded | blk), ded, blk

    plan = {"med4": ["ctrl_med4_hot1a3"], "mit9313": ["ctrl_mit9313_inoc05e6", "ctrl_mit9313_inoc5e6"],
            "natl2a": ["ctrl_natl2a_mit1002"]}
    for tag, shorts in plan.items():
        sy, mem, roles = load_methods(tag)
        names = roles.gene_name.to_dict()
        if tag == "med4":
            sids = ["sys_PMM0263", "sys_PMM0970", "sys_PMM0370", "sys_PMM0192"]
            src = "coordinator list: amt1, urt, cyn, dpp"
        else:
            sids, ded, blk = n_systems(tag)
            src = f"p18 dedicated {sorted(ded)} + fig2 Block A usable {sorted(blk)}"
        for short in shorts:
            tps = sorted(set(de[de.short_name == short].timepoint.astype(str)),
                         key=lambda x: float(x.replace("h", "")) if x.replace("h", "").lstrip("-").replace(".", "").isdigit() else 0)
            for sid in sids:
                for r in gene_rows(de, short, tps, mem[sid], names):
                    r.update({"strain": tag, "system_id": sid, "system_members": sy.member_names[sid], "role": "N import subunit",
                              "system_source": src})
                    e2.append(r)
            if tag == "med4":
                for r in gene_rows(de, short, tps, list(ctx), n4):
                    r.update({"strain": tag, "system_id": "context", "role": "context (not in rule)"})
                    e2.append(r)
    E2 = pd.DataFrame(e2)
    E2.to_csv(DATA / "s2_expneg2_grid.csv", index=False)
    for short in sum(plan.values(), []):
        x = E2[(E2.table == short) & (E2.role == "N import subunit")]
        ups = x[x.expression_status == expr.SIG_UP]
        downs = x[x.expression_status == expr.SIG_DOWN]
        notl = x[x.expression_status == "not listed"]
        scope = "can only fail (filtered table)" if short == "ctrl_natl2a_mit1002" else "all-detected table"
        outcome("6 expected-negative 2 " + short, "fails if any N-import subunit significant_up", ups.empty,
                f"{scope}; subunit x timepoint cells {len(x)}, not listed {len(notl)}; significant_up: "
                + (", ".join(f"{r.locus_tag} {r.gene_name} {r.timepoint}" for r in ups.itertuples()) or "none")
                + "; significant_down (pointer): "
                + (", ".join(f"{r.locus_tag} {r.gene_name} {r.timepoint}" for r in downs.itertuples()) or "none"))

    # ---------------------------------------------------------------- 7 expected-negative 3 and 8 N systems (a)/(b)
    groups = {
        "P regulon (pst + phn)": ["sys_PMM0710", "sys_PMM0671"], "pst": ["sys_PMM0710"], "phn": ["sys_PMM0671"],
        "S (sul1 + sul3)": ["sys_PMM0644", "sys_PMM0214"], "sul1": ["sys_PMM0644"], "sul3": ["sys_PMM0214"],
        "Fe (fut/idiA2)": ["sys_PMM0489"],
        "Mn/Zn (mnt + lraI system)": ["sys_PMM0601", "sys_PMM1029"], "mnt": ["sys_PMM0601"], "lraI system": ["sys_PMM1029"],
        "bicarbonate (sbtA)": ["sys_PMM0213"],
    }
    ngroups = {"amt1": ["sys_PMM0263"], "urt": ["sys_PMM0970"], "cyn": ["sys_PMM0370"], "dpp": ["sys_PMM0192"]}

    def ab_rows(gdict, kind):
        rows, subs = [], []
        for name, sids in gdict.items():
            loci = sorted({m for s in sids for m in mem4[s]})
            st = {tp: expr.system_stats(de, "anchor_cocult_protein", tp, loci) for tp in ("day 60", "day 89")}
            ax = expr.system_stats(de, "anchor_axenic_protein", "day 14", loci)
            rna = {tp: expr.system_stats(de, "anchor_cocult_rna", tp, loci) for tp in ("day 60", "day 89")}
            a_any = expr.crit_a(st["day 60"], st["day 89"], rna["day 60"]["median_log2fc"], rna["day 89"]["median_log2fc"], "any")
            a_half = expr.crit_a(st["day 60"], st["day 89"], rna["day 60"]["median_log2fc"], rna["day 89"]["median_log2fc"], "half")
            b = expr.crit_b(st["day 60"]["median_percentile"], st["day 89"]["median_percentile"], ax["median_percentile"])
            rows.append({"group": name, "kind": kind, "systems": "|".join(sids), "members": "|".join(loci),
                         **{f"prot_{k}_{tp.replace(' ', '')}": v for tp in st for k, v in st[tp].items()},
                         "axenic_d14_median_percentile": ax["median_percentile"], "axenic_d14_n_detected": ax["n_detected"],
                         "margin_d60": st["day 60"]["median_percentile"] - ax["median_percentile"],
                         "margin_d89": st["day 89"]["median_percentile"] - ax["median_percentile"],
                         "rna_median_log2fc_d60": rna["day 60"]["median_log2fc"], "rna_median_log2fc_d89": rna["day 89"]["median_log2fc"],
                         "a_any": a_any, "a_half": a_half, "b": b,
                         "a_any_and_b": a_any and b, "a_half_and_b": a_half and b})
            for tb, tps in (("anchor_cocult_protein", ["day 60", "day 89"]), ("anchor_axenic_protein", ["day 14"]),
                            ("anchor_cocult_rna", ["day 60", "day 89"])):
                for r in gene_rows(de, tb, tps, loci, n4):
                    r["group"] = name
                    subs.append(r)
        return rows, subs

    r3, s3 = ab_rows(groups, "non-N reference")
    r8, s8 = ab_rows(ngroups, "MED4 dedicated N system (not labelled here)")
    R3 = pd.DataFrame(r3)
    R3.to_csv(DATA / "s2_expneg3_systems.csv", index=False)
    pd.DataFrame(s3).to_csv(DATA / "s2_expneg3_subunits.csv", index=False)
    R8 = pd.DataFrame(r8)
    R8.to_csv(DATA / "s2_nsystems_ab_variants.csv", index=False)
    pd.DataFrame(s8).to_csv(DATA / "s2_nsystems_subunits.csv", index=False)
    for R, chk in ((R3, "7 expected-negative 3"), (R8, "8 N systems (a)/(b)")):
        for r in R.itertuples():
            for v in ("a_any_and_b", "a_half_and_b"):
                outcome(f"{chk}: {r.group}", v.replace("_and_b", " + b"), bool(getattr(r, v)),
                        f"a_any={r.a_any} a_half={r.a_half} b={r.b}")
    mk = []
    for short, tps in (("anchor_cocult_protein", ["day 60", "day 89"]), ("anchor_cocult_rna", ["day 60", "day 89"])):
        mk += gene_rows(de, short, tps, ["PMM1284", "PMM1164"], {"PMM1284": "phoH", "PMM1164": "idiA2"})
    MK = pd.DataFrame(mk)
    MK["note"] = MK.locus_tag.map({"PMM1164": "idiA2 is itself a member of the Fe system sys_PMM0489", "PMM1284": ""})
    MK.to_csv(DATA / "s2_expneg3_markers.csv", index=False)

    O = pd.DataFrame(OUT)
    O.to_csv(DATA / "s2_outcomes.csv", index=False)
    summ = {"expr_version": expr.__version__, "n_transport_version": nt.__version__,
            "pooled_slice_used": False, "outcomes": OUT}
    (DATA / "s2_summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 200)
    print(O.to_string(index=False))


if __name__ == "__main__":
    main()
