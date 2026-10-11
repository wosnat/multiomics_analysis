"""N-class overlap within systems and a first look at metabolic support per (system, class). v1.6.1 tables only;
no KG calls, no rule changes. Facts only.

Inputs per strain (data/<strain>/):
  p18_<strain>_listing_basis.csv          (system x N class pairs, High/Medium; known false positives excluded here)
  p12_<strain>_system_substrates_classified.csv  (rows: most_specific, non-lumping, non-currency, as in p18)
  p11_<strain>_fragments.csv              (fragment loci are not counted as linked)
  raw/p3_<strain>_genome_coords.csv       (gene names of enzyme loci)
Outputs (data/qc/):
  q2_overlap_classes_per_system.csv  per strain: number of N classes per system -> number of systems
  q2_overlap_cooccurrence.csv        per strain, class x class: systems listing both (diagonal = systems listing it)
  q2_overlap_combinations.csv        per strain: each distinct class set, n systems, n with >=1 dedicated class,
                                     n efflux_annotated, member systems
  q2_overlap_systems.csv             per system: classes, n classes, dedicated classes, efflux_annotated
  q2_support_system_class.csv        per multi-class system x class: n_compounds, n_genome_enzymes, n_linked_enzymes,
                                     enzyme loci / names, listing_basis
  q2_support_shared_enzymes.csv      per system and class pair: genome-enzyme loci shared by both classes
  q2_summary.json
Figures (figures/): fig10_class_overlap, fig11_class_support (PNG 300 dpi + SVG).
Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/q2_class_overlap.py
"""
import json
from collections import Counter
from itertools import combinations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import f1_methods_figures as F
from common import nt

plt = F.plt
D, TAGS, LABEL = F.D, F.TAGS, F.LABEL
QC = D / "qc"
CLASSES = ["ammonium", "urea", "cyanate", "nitrite", "nitrate", "amino acids", "peptides", "amino sugars",
           "polyamines", "nucleobases/nucleosides", "osmolytes", "amines"]
SHORT = {"ammonium": "NH4", "urea": "urea", "cyanate": "cyanate", "nitrite": "NO2", "nitrate": "NO3",
         "amino acids": "AA", "peptides": "pept", "amino sugars": "aSug", "polyamines": "polyam",
         "nucleobases/nucleosides": "nucl", "osmolytes": "osmo", "amines": "amines"}
EXAMPLES = {"med4": ["sys_PMM0370", "sys_PMM1323"], "mit9313": ["sys_PMT1502"], "natl2a": ["sys_PMN2A_1011"]}
DED_C, BRD_C = F.TIER_C["High"], F.TIER_C["Low"]


def loci(v):
    return [x for x in nt.parse_list(v) if x and x not in (nt.NO_BASIS, nt.NOT_ELIGIBLE)]


def load(t):
    d = D / t
    lb = pd.read_csv(d / f"p18_{t}_listing_basis.csv")
    lb = lb[~lb.known_false_positive.astype(bool)]
    c = pd.read_csv(d / f"p12_{t}_system_substrates_classified.csv", low_memory=False)
    c = c[(c.substrate_depth == "most_specific") & ~c.is_lumping.map(nt.to_bool) & ~c.is_currency.map(nt.to_bool)]
    frag = set(pd.read_csv(d / f"p11_{t}_fragments.csv").locus_tag)
    co = pd.read_csv(d / "raw" / f"p3_{t}_genome_coords.csv")
    names = dict(zip(co.locus_tag, co.gene_name))
    return lb, c, frag, names


def main():
    QC.mkdir(parents=True, exist_ok=True)
    dist, cooc, comb, sysrows, sup, shared, summ = [], [], [], [], [], [], {}
    for t in TAGS:
        lb, c, frag, names = load(t)
        g = lb.groupby("system_id")
        per = pd.DataFrame({
            "classes": g.compound_class.agg(lambda s: tuple(sorted(set(s), key=CLASSES.index))),
            "dedicated_classes": g.apply(lambda x: "|".join(sorted(x.loc[x.listing_basis == "dedicated", "compound_class"])),
                                         include_groups=False),
            "member_names": g.member_names.first(), "tier": g.tier.first(),
            "efflux_annotated": g.efflux_annotated.first().astype(bool)}).reset_index()
        per["n_classes"] = per.classes.map(len)
        per.insert(0, "strain", t)
        sysrows.append(per.assign(classes=per.classes.map("|".join)))
        for k, v in per.n_classes.value_counts().sort_index().items():
            dist.append({"strain": t, "n_classes": int(k), "systems": int(v)})
        for a in CLASSES:
            for b in CLASSES:
                n = int(per.classes.map(lambda s: a in s and b in s).sum())
                cooc.append({"strain": t, "class_a": a, "class_b": b, "systems_listing_both": n})
        for cs, x in per.groupby("classes"):
            comb.append({"strain": t, "class_set": "|".join(cs), "n_classes": len(cs), "systems": len(x),
                         "with_dedicated_class": int((x.dedicated_classes != "").sum()),
                         "efflux_annotated": int(x.efflux_annotated.sum()),
                         "members": " || ".join(f"{s.system_id} ({s.member_names})" for s in x.itertuples())})
        # support for multi-class systems
        multi = per[per.n_classes >= 2]
        for s in multi.itertuples():
            rs = c[c.system_id == s.system_id]
            enz_by_cls = {}
            for cl in s.classes:
                r = rs[rs.compound_class_final == cl]
                ge = sorted({x for v in r.genome_enzyme_loci for x in loci(v)})
                lk = sorted({x for col in ("function_linked_loci", "neighbour_linked_loci") for v in r[col]
                             for x in loci(v)} - frag)
                lk = [x for x in lk if x in ge] + [x for x in lk if x not in ge]
                enz_by_cls[cl] = set(ge)
                basis = lb[(lb.system_id == s.system_id) & (lb.compound_class == cl)].listing_basis.iloc[0]
                sup.append({"strain": t, "system_id": s.system_id, "member_names": s.member_names, "tier": s.tier,
                            "efflux_annotated": s.efflux_annotated, "n_classes": s.n_classes, "compound_class": cl,
                            "listing_basis": basis, "n_compounds": int(r.equiv_group.nunique()),
                            "compounds": " | ".join(sorted(set(r.metabolite_name.astype(str))))[:300],
                            "n_genome_enzymes": len(ge), "n_linked_enzymes": len(lk),
                            "linked_not_in_genome_list": len([x for x in lk if x not in ge]),
                            "genome_enzymes": " ".join(f"{x}:{names.get(x) if isinstance(names.get(x), str) else ''}"
                                                       for x in ge[:8]) + (" ..." if len(ge) > 8 else ""),
                            "linked_enzymes": " ".join(f"{x}:{names.get(x) if isinstance(names.get(x), str) else ''}" for x in lk)})
            for a, b in combinations(s.classes, 2):
                sh = sorted(enz_by_cls[a] & enz_by_cls[b])
                if sh:
                    shared.append({"strain": t, "system_id": s.system_id, "member_names": s.member_names,
                                   "class_a": a, "class_b": b, "n_shared": len(sh),
                                   "shared_loci": " ".join(f"{x}:{names.get(x) if isinstance(names.get(x), str) else ''}"
                                                           for x in sh[:12]) + (" ..." if len(sh) > 12 else "")})
    Dd = pd.DataFrame(dist); Dd.to_csv(QC / "q2_overlap_classes_per_system.csv", index=False)
    Co = pd.DataFrame(cooc); Co.to_csv(QC / "q2_overlap_cooccurrence.csv", index=False)
    Cb = pd.DataFrame(comb).sort_values(["strain", "systems", "n_classes"], ascending=[True, False, False])
    Cb.to_csv(QC / "q2_overlap_combinations.csv", index=False)
    Sy = pd.concat(sysrows, ignore_index=True); Sy.to_csv(QC / "q2_overlap_systems.csv", index=False)
    Su = pd.DataFrame(sup); Su.to_csv(QC / "q2_support_system_class.csv", index=False)
    Sh = pd.DataFrame(shared, columns=["strain", "system_id", "member_names", "class_a", "class_b", "n_shared", "shared_loci"])
    Sh.to_csv(QC / "q2_support_shared_enzymes.csv", index=False)
    summ = {"classes_per_system": Dd.to_dict("records"),
            "top5_combinations": {t: Cb[Cb.strain == t].head(5)[["class_set", "systems", "with_dedicated_class",
                                                                  "efflux_annotated"]].to_dict("records") for t in TAGS},
            "multi_class_cells": int(len(Su)), "cells_zero_genome_enzymes": int((Su.n_genome_enzymes == 0).sum()),
            "cells_linked_gt0": int((Su.n_linked_enzymes > 0).sum()),
            "shared_enzyme_pairs": int(len(Sh)), "examples_missing": [s for t, ss in EXAMPLES.items() for s in ss
                                                                      if s not in set(Sy[Sy.strain == t].system_id)]}
    (QC / "q2_summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    files = fig10(Sy, Cb) + fig11(Su)
    for p in files:
        print(p.relative_to(F.M))
    print(json.dumps(summ, indent=1, default=str))


# --------------------------------------------------------------------------- fig10: UpSet-style per strain
def fig10(Sy, Cb, top=12):
    fig = plt.figure(figsize=(15, 7.2))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.25], hspace=0.05, wspace=0.42)
    for j, t in enumerate(TAGS):
        cb = Cb[Cb.strain == t].head(top).reset_index(drop=True)
        ax, am = fig.add_subplot(gs[0, j]), fig.add_subplot(gs[1, j])
        used = [c for c in CLASSES if any(c in s.split("|") for s in cb.class_set)]
        for i, r in cb.iterrows():
            ded, n = int(r.with_dedicated_class), int(r.systems)
            ax.bar(i, ded, width=0.6, color=DED_C, edgecolor=F.SURF, linewidth=F.GAP_LW)
            ax.bar(i, n - ded, bottom=ded, width=0.6, color=BRD_C, hatch="..", edgecolor=F.SURF, linewidth=F.GAP_LW)
            lab = str(n) + (f"\ne{int(r.efflux_annotated)}" if r.efflux_annotated else "")
            ax.text(i, n + 0.3, lab, ha="center", va="bottom", fontsize=7.5, color=F.TEXT, linespacing=1.0)
            mem = r.class_set.split("|")
            ys = [used.index(m) for m in mem]
            am.plot([i] * len(ys), ys, color=F.TEXT2, linewidth=1.2, zorder=1)
            for y in range(len(used)):
                on = used[y] in mem
                am.scatter(i, y, s=34, color=F.TEXT if on else F.GRID, zorder=2)
        ax.set_xlim(-0.6, top - 0.4)
        ax.set_ylim(0, cb.systems.max() * 1.3 + 1)
        ax.set_xticks([])
        ax.set_title(LABEL[t], loc="left", fontsize=10)
        ax.grid(axis="y", color=F.GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.spines["left"].set_color(F.GRID)
        ax.spines["bottom"].set_color(F.GRID)
        ax.tick_params(length=0)
        if j == 0:
            ax.set_ylabel("systems")
        am.set_xlim(-0.6, top - 0.4)
        am.set_ylim(len(used) - 0.5, -0.5)
        am.set_yticks(range(len(used)), used, fontsize=8)
        am.set_xticks([])
        for s in am.spines.values():
            s.set_visible(False)
        am.tick_params(length=0)
    handles = [Patch(facecolor=DED_C, edgecolor=F.SURF, label="systems with >= 1 dedicated class"),
               Patch(facecolor=BRD_C, hatch="..", edgecolor=F.SURF, label="systems with broad listings only"),
               Line2D([], [], marker="o", color=F.TEXT, linestyle="", label="class in the set")]
    fig.legend(handles=handles, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0))
    F.head(fig, "Which N classes are listed together by one system",
           f"Source: data/<strain>/p18_<strain>_listing_basis.csv (High/Medium, known false positives excluded); "
           f"top {top} class sets per strain; data/qc/q2_overlap_combinations.csv. Bar label: systems; e# = efflux-annotated systems")
    fig.subplots_adjust(left=0.11, right=0.99, top=0.86, bottom=0.1)
    return F.save(fig, "fig10_class_overlap")


# --------------------------------------------------------------------------- fig11: support grid
def fig11(Su, top=15):
    sysn = (Su.groupby(["strain", "system_id"]).agg(n=("n_classes", "first"), names=("member_names", "first"),
                                                     eff=("efflux_annotated", "first")).reset_index())
    req = {(t, s) for t, ss in EXAMPLES.items() for s in ss}
    sysn["req"] = [(a, b) in req for a, b in zip(sysn.strain, sysn.system_id)]
    sysn = sysn.sort_values(["req", "n", "strain", "system_id"], ascending=[False, False, True, True])
    pick = pd.concat([sysn[sysn.req], sysn[~sysn.req]]).head(max(top, int(sysn.req.sum())))
    pick = pick.sort_values(["n", "strain", "system_id"], ascending=[False, True, True]).reset_index(drop=True)
    used = [c for c in CLASSES if c in set(Su[Su.system_id.isin(pick.system_id)].compound_class)]
    fig, ax = plt.subplots(figsize=(13, 0.48 * len(pick) + 2.8))
    for i, r in pick.iterrows():
        x = Su[(Su.strain == r.strain) & (Su.system_id == r.system_id)].set_index("compound_class")
        for j, cl in enumerate(used):
            if cl not in x.index:
                continue
            q = x.loc[cl]
            ded = q.listing_basis == "dedicated"
            ne, nl = int(q.n_genome_enzymes), int(q.n_linked_enzymes)
            size = 60 + 260 * np.sqrt(min(ne, 40) / 40) if ne else 70
            ax.scatter(j, i, s=size, color=(DED_C if ded else BRD_C) if ne else F.SURF,
                       edgecolor=F.TEXT if nl else ((DED_C if ded else F.TEXT2) if not ne else F.SURF),
                       linewidth=2.2 if nl or (ded and not ne) else 0.8, zorder=2)
            ax.text(j + 0.32, i, str(ne) + (f"/{nl}" if nl else ""), ha="left", va="center", fontsize=7.5,
                    color=F.TEXT, fontweight="bold" if nl else "normal")
    lab = [f"{LABEL[r.strain]} {r.system_id.replace('sys_', '')} {F.short_names(r.names, 3)}" + (" [efflux]" if r.eff else "")
           for r in pick.itertuples()]
    ax.set_yticks(range(len(pick)), lab, fontsize=8)
    ax.set_xticks(range(len(used)), used, rotation=35, ha="right", fontsize=8.5)
    ax.xaxis.tick_top()
    plt.setp(ax.get_xticklabels(), rotation=35, ha="left")
    ax.set_xlim(-0.5, len(used) - 0.2)
    ax.set_ylim(len(pick) - 0.5, -0.6)
    ax.grid(color=F.GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    handles = [Line2D([], [], marker="o", color=DED_C, linestyle="", markersize=9, label="dedicated listing"),
               Line2D([], [], marker="o", color=BRD_C, linestyle="", markersize=9, label="broad listing"),
               Line2D([], [], marker="o", markerfacecolor=F.SURF, markeredgecolor=F.TEXT2, linestyle="", markersize=8,
                      label="broad, 0 genome enzymes"),
               Line2D([], [], marker="o", markerfacecolor=F.SURF, markeredgecolor=DED_C, markeredgewidth=2.2, linestyle="",
                      markersize=8, label="dedicated, 0 genome enzymes"),
               Line2D([], [], marker="o", markerfacecolor=BRD_C, markeredgecolor=F.TEXT, markeredgewidth=2.2, linestyle="",
                      markersize=9, label="ring: >= 1 linked enzyme")]
    fig.legend(handles=handles, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.0))
    F.head(fig, "Metabolic support for each class a multi-class system lists",
           "Source: data/qc/q2_support_system_class.csv (from p18 listing basis + p12 genome_enzyme_loci / function- & "
           "neighbour-linked loci). Number = genome enzymes / linked enzymes.\nGenome enzymes = genes in the strain with a "
           "KEGG reaction on a listed compound of the class (could consume it); linked = also neighbour-linked or sharing a "
           "curated role with the system.\nDot size grows with genome enzymes (capped at 40). Hollow dot = 0 genome enzymes "
           "(e.g. no KEGG reactions on peptides).")
    fig.subplots_adjust(left=0.3, right=0.98, top=1 - 2.3 / (0.48 * len(pick) + 2.8), bottom=0.7 / (0.48 * len(pick) + 2.8))
    return F.save(fig, "fig11_class_support")


if __name__ == "__main__":
    main()
