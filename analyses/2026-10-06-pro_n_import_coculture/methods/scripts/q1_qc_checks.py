"""QC pack for the methods milestone (v1.5.0 data). Facts only.

Checks (outputs in methods/data/qc/, figures in methods/figures/ as PNG 300 dpi + SVG, style of f1_methods_figures):
  a  gene maps of the N-relevant loci (+-8 genes): fig7_genemap_<strain>; data/qc/q1a_genemap_genes.csv
  b  curated Cyanorak transport-role (Q.*) genes x tier: fig8_q_roles_vs_tier; q1b_q_role_genes.csv,
     q1b_q_role_by_tier.csv, q1b_q_role_missed.csv (Low / not_transporter / not in universe)
  c  10 random systems per tier per strain (seed 20261008): q1c_random_systems.csv
  d  High systems, top most-specific substrates vs member products + keyword flag: q1d_high_substrate_vs_product.csv,
     q1d_disagreements.csv
  e  gap 100 / 200 / 500 sensitivity (role + cross-locus joins on; tiers recomputed with n_transport.system_tier from
     the grid variants): fig9_gap_sensitivity; q1e_tier_counts_by_gap.csv, q1e_n_relevant_membership_by_gap.csv
  f  strain consistency of shared transporters (matched by gene name; orthologs not used): q1f_strain_consistency.csv
KG calls (kg_fetch.fetch, strict inputs): genes_by_ontology(cyanorak_role, Q.1-Q.9) per strain;
  gene_details(universe) per strain (transport_substrate_resolution, for e).
Usage (repo root):
  .venv/Scripts/python.exe analyses/2026-10-06-pro_n_import_coculture/methods/scripts/q1_qc_checks.py
"""
import json
import re

import pandas as pd
from matplotlib.patches import Patch, Polygon, Rectangle
from multiomics_explorer import GraphConnection, gene_details, genes_by_ontology, to_dataframe

import f1_methods_figures as F
from common import kf, nt

plt = F.plt
D, FIG, TAGS, LABEL = F.D, F.OUT, F.TAGS, F.LABEL
QC = D / "qc"
REF = "gap200_roleT_crossT"
SEED = 20261008
ORG = {"med4": "Prochlorococcus MED4", "mit9313": "Prochlorococcus MIT9313", "natl2a": "Prochlorococcus NATL2A"}
TIER_ORDER = ["High", "Medium", "Low", "not_transporter"]
NOT_UNI = "not in universe"
LOCI = {"cyn": ["cynA", "cynB", "cynD", "cynS"], "urt": ["urtA", "urtB", "urtC", "urtD", "urtE"], "amt1": ["amt1"],
        "dpp": ["dppA", "dppB", "dppC", "ddpD"], "focA/nirA": ["focA"], "pst": ["pstS", "pstC", "pstA", "pstB"]}
FAMILIES = {"amt1": ["amt1"], "urt": ["urtA", "urtB", "urtC", "urtD", "urtE"], "pst": ["pstS", "pstC", "pstA", "pstB"],
            "dpp": ["dppA", "dppB", "dppC", "ddpD"], "mnt": ["mntA", "mntB", "mntC"], "phn": ["phnC", "phnD", "phnE"],
            "fut/idiA": ["futA", "futB", "futC", "idiA", "idiA2"], "cyn": ["cynA", "cynB", "cynD"], "sul1": ["sul1"],
            "sul3": ["sul3"], "ktr": ["ktrA", "ktrB"], "sbtA": ["sbtA"], "focA": ["focA"]}
# (d) keyword families: (substrate-name pattern, product / gene-name pattern)
KW = {
    "phosphate": (r"\bphosphate\b|orthophosphate", r"phosphate|\bpst"),
    "phosphonate": (r"phosphon", r"phosphon|\bphn"),
    "manganese": (r"mangan|\bmn\(?2", r"mangan|\bmnt"),
    "iron": (r"\biron|fe\(|\bfe[23]|ferric|ferrous|siderophore", r"iron|ferric|\bfe[23]|\bfut|\bidi"),
    "urea": (r"\burea\b", r"urea|\burt"),
    "cyanate": (r"cyanate", r"cyanate|\bcyn"),
    "ammonium": (r"ammoni|methylamine", r"ammonium|\bamt"),
    "nitrite/nitrate": (r"nitrite|nitrate", r"nitrite|nitrate|formate|\bfoc|\bnrt"),
    "peptide": (r"peptide|glutathione", r"peptide|\bdpp|\bddp|\bopp"),
    "amino acid": (r"amino acid|glutam|aspart|arginine|lysine|histidine|leucine|valine|isoleucine|glycine\b|serine|"
                   r"alanine|proline|threonine|methionine|tyrosine|phenylalanine|tryptophan|cysteine",
                   r"amino acid|glutam|polar|\bnat[a-z]?\b|\bliv|\bglt|\bhis"),
    "sugar": (r"glucose|sucrose|maltose|sugar|fructose|trehalose|galactose|xylose|ribose", r"glucose|sugar|carbohydrate|maltose|\bglc"),
    "potassium": (r"potassium|\bk\+", r"potassium|\bk\+|\btrk|\bktr|\bkdp"),
    "sodium": (r"sodium|\bna\+", r"sodium|\bna\+|\bnha|\bmrp"),
    "sulfate": (r"sulfate|sulphate", r"sulfate|\bsul"),
    "bicarbonate": (r"bicarbonate|hco3|carbon dioxide", r"bicarbonate|\bsbt|inorganic carbon|\bcmp|\bbic"),
    "magnesium": (r"magnesium|\bmg\(?2", r"magnesium|\bmg|\bcor"),
    "cobalt/B12": (r"cobalt|cobalamin|cyanocobalamin", r"cobalt|cobalamin|b12|\bcbi|\bbtu"),
    "zinc": (r"\bzinc|\bzn\(?2", r"zinc|\bznu|\bzia"),
    "molybdate": (r"molybd", r"molybd|\bmod"),
    "polyamine": (r"spermidine|putrescine|polyamine", r"spermidine|putrescine|polyamine|\bpot"),
    "osmolyte": (r"betaine|choline|glucosylglycerol|glycerol", r"betaine|choline|osmo|\bggt|glycerol"),
    "copper": (r"copper|\bcu\+|\bcu\(?2", r"copper|\bcop|\bcut|\bcta"),
}


def load(t):
    d = D / t
    co = pd.read_csv(d / "raw" / f"p3_{t}_genome_coords.csv").dropna(subset=["start"])
    co = co.sort_values(["contig", "start"]).reset_index(drop=True)
    co["rank"] = co.groupby("contig").cumcount()
    return {"coords": co, "gs": pd.read_csv(d / f"p3_{t}_gene_systems_{REF}.csv"),
            "sys": pd.read_csv(d / f"p11_{t}_systems.csv"), "roles": pd.read_csv(d / f"p2_{t}_gene_roles.csv"),
            "fl": pd.read_csv(d / f"p11_{t}_function_linked.csv"), "nl": pd.read_csv(d / f"p11_{t}_neighbour_linked.csv"),
            "cls": pd.read_csv(d / f"p12_{t}_system_substrates_classified.csv", low_memory=False)}


DATA = {t: load(t) for t in TAGS}


def kg_fetch_all():
    log, q, res = [], {}, {}
    with GraphConnection() as conn:
        for t in TAGS:
            q[t] = to_dataframe({"results": kf.fetch(
                genes_by_ontology, f"genes_by_ontology(cyanorak_role Q.1-Q.9, {t})", log, ("locus_tag", "term_id"),
                limit_none_ok=True, strict_inputs=True, ontology="cyanorak_role", organism=ORG[t],
                term_ids=[f"cyanorak.role:Q.{i}" for i in range(1, 10)], min_gene_set_size=1, max_gene_set_size=None,
                conn=conn)["results"]})
            uni = DATA[t]["roles"].locus_tag.tolist()
            res[t] = to_dataframe({"results": kf.fetch(
                gene_details, f"gene_details(universe, {t})", log, ("locus_tag",), chunk_param="locus_tags",
                chunk_size=200, limit_none_ok=True, locus_tags=uni, conn=conn)["results"]})
    return q, res, log


def top_substrates(cls, sid, n=3):
    r = cls[(cls.system_id == sid) & (cls.substrate_depth == "most_specific")]
    if r.empty:
        return []
    g = r.groupby("metabolite_name").agg(score=("tcdb_evidence_score", "max"), n=("locus_tag", "size"))
    return g.sort_values(["score", "n"], ascending=False).index[:n].tolist()


# --------------------------------------------------------------------------- a: gene maps
def loci_windows(t):
    co = DATA[t]["coords"]
    out = []
    for fam, names in LOCI.items():
        a = co[co.gene_name.isin(names)].sort_values(["contig", "rank"])
        if a.empty:
            continue
        clusters = []
        for r in a.itertuples():
            if clusters and clusters[-1]["contig"] == r.contig and r.rank - clusters[-1]["hi"] <= 8:
                clusters[-1]["hi"] = r.rank
            else:
                clusters.append({"contig": r.contig, "lo": r.rank, "hi": r.rank})
        for k, c in enumerate(clusters):
            lab = fam if len(clusters) == 1 else f"{fam} locus {k + 1}"
            out.append((lab, c["contig"], c["lo"] - 8, c["hi"] + 8))
    return out


def arrow(ax, x, y, strand, fc, hatch, ec):
    w, h, head = 0.9, 0.5, 0.22
    if strand == "+":
        pts = [(x, y - h / 2), (x + w - head, y - h / 2), (x + w, y), (x + w - head, y + h / 2), (x, y + h / 2)]
    else:
        pts = [(x + w, y - h / 2), (x + head, y - h / 2), (x, y), (x + head, y + h / 2), (x + w, y + h / 2)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=fc, hatch=hatch, edgecolor=ec, linewidth=0.6))


def fig7(t):
    x = DATA[t]
    co, gs = x["coords"], x["gs"].set_index("locus_tag")
    sy = x["sys"].set_index("system_id")
    wins = loci_windows(t)
    rows = []
    fig, axes = plt.subplots(len(wins), 1, figsize=(12, 2.0 * len(wins) + 2.0))
    if len(wins) == 1:
        axes = [axes]
    for ax, (lab, contig, lo, hi) in zip(axes, wins):
        w = co[(co.contig == contig) & (co["rank"] >= lo) & (co["rank"] <= hi)].sort_values("rank")
        sids = [s for s in dict.fromkeys(gs.system_id.get(lt) for lt in w.locus_tag) if isinstance(s, str)]
        tag_of = {s: f"S{i + 1}" for i, s in enumerate(sids)}
        nl = x["nl"][x["nl"].system_id.isin(sids)]
        fl = x["fl"][x["fl"].system_id.isin(sids)]
        for i, r in enumerate(w.itertuples()):
            sid = gs.system_id.get(r.locus_tag)
            if isinstance(sid, str):
                tier = sy.tier[sid]
                arrow(ax, i, 0, r.strand, F.TIER_C[tier], F.TIER_H[tier], F.TEXT2)
                ax.text(i + 0.45, -0.48, tag_of[sid], ha="center", va="top", fontsize=7, color=F.TEXT)
            else:
                tier = NOT_UNI
                arrow(ax, i, 0, r.strand, F.SURF, "", F.TEXT2)
            name = r.gene_name if isinstance(r.gene_name, str) and r.gene_name else r.locus_tag.split("_")[-1]
            name = re.sub(r"^.*_(RS\d+)$", r"\1", name)
            ax.text(i + 0.45, 0.36, name, ha="left", va="bottom", fontsize=6.5, rotation=40, color=F.TEXT)
            marks = []
            if r.locus_tag in set(nl.locus_tag):
                marks.append("N")
            if r.locus_tag in set(fl.locus_tag):
                marks.append("F")
            if marks:
                ax.text(i + 0.45, -0.8, "+".join(marks), ha="center", va="top", fontsize=7.5, fontweight="bold",
                        color=F.TEXT)
            rows.append({"strain": t, "locus": lab, "locus_tag": r.locus_tag, "gene_name": r.gene_name,
                         "product": r.product, "strand": r.strand, "start": r.start, "end": r.end,
                         "system_id": sid if isinstance(sid, str) else NOT_UNI, "system_tag": tag_of.get(sid, ""),
                         "tier": tier, "neighbour_linked_to": "|".join(sorted(set(nl[nl.locus_tag == r.locus_tag].system_id))),
                         "function_linked_to": "|".join(sorted(set(fl[fl.locus_tag == r.locus_tag].system_id)))})
        ent = [f"{tag_of[s]} = {s} ({sy.tier[s]}{', known FP' if bool(sy.known_false_positive[s]) else ''})" for s in sids]
        key = "\n".join("   ".join(ent[k:k + 5]) for k in range(0, len(ent), 5))
        wl = set(w.locus_tag)
        outside = sorted({f"{r2.locus_tag} {r2.enzyme_name} ({'F' if src == 'F' else 'N'} to {tag_of[r2.system_id]})"
                          for src, df_ in (("F", fl), ("N", nl)) for r2 in df_.itertuples() if r2.locus_tag not in wl})
        if outside:
            key += "\nlinked enzymes outside this window: " + "; ".join(outside)
        ax.text(0, -1.25, key, ha="left", va="top", fontsize=7, color=F.TEXT2, linespacing=1.3)
        ax.set_xlim(-0.2, len(w) + 0.2)
        ax.set_ylim(-2.1, 1.5)
        ax.set_yticks([0], [f"{lab}\n{w.locus_tag.iloc[0]}–{w.locus_tag.iloc[-1]}"], fontsize=8)
        ax.set_xticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(length=0)
    handles = [Patch(facecolor=F.TIER_C[k], hatch=F.TIER_H[k], edgecolor=F.TEXT2, linewidth=0.4, label=k)
               for k in TIER_ORDER] + [Patch(facecolor=F.SURF, edgecolor=F.TEXT2, linewidth=0.4, label=NOT_UNI)]
    fig.legend(handles=handles, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.0))
    F.head(fig, f"N-relevant loci, {LABEL[t]} (±8 genes)",
           f"Source: data/{t}/raw/p3_{t}_genome_coords.csv, p3_{t}_gene_systems_{REF}.csv, p11_{t}_systems.csv,\n"
           f"p11_{t}_neighbour_linked.csv, p11_{t}_function_linked.csv. "
           "Arrow = gene and strand (genome order, not to scale); S# = system; N / F = neighbour- / function-linked enzyme")
    fig.subplots_adjust(left=0.15, right=0.99, top=1 - 1.5 / (2.0 * len(wins) + 2.0), bottom=0.5 / (2.0 * len(wins) + 2.0),
                        hspace=0.25)
    files = F.save(fig, f"fig7_genemap_{t}")
    return rows, files


# --------------------------------------------------------------------------- b: Q-role genes x tier
def check_b(q):
    rows = []
    for t in TAGS:
        x = DATA[t]
        gs = x["gs"].set_index("locus_tag")
        sy = x["sys"].set_index("system_id")
        roles = x["roles"].set_index("locus_tag")
        for r in q[t].itertuples():
            sid = gs.system_id.get(r.locus_tag)
            inu = isinstance(sid, str)
            rows.append({"strain": t, "locus_tag": r.locus_tag, "gene_name": r.gene_name, "product": r.product,
                         "q_role": r.term_id.replace("cyanorak.role:", ""), "q_role_name": r.term_name.split(" > ")[-1],
                         "system_id": sid if inu else NOT_UNI, "tier": sy.tier[sid] if inu else NOT_UNI,
                         "tier_reason": sy.tier_reason[sid] if inu else None,
                         "system_members": sy.member_names[sid] if inu else None,
                         "known_false_positive": bool(sy.known_false_positive[sid]) if inu else None,
                         "likely_transporter": roles.likely_transporter.get(r.locus_tag) if inu else None,
                         "likely_transporter_basis": roles.likely_transporter_basis.get(r.locus_tag) if inu else None,
                         "tcdb_ids": roles.tcdb_ids.get(r.locus_tag) if inu else None})
    B = pd.DataFrame(rows)
    B.to_csv(QC / "q1b_q_role_genes.csv", index=False)
    ct = B.groupby(["strain", "q_role", "q_role_name", "tier"]).size().unstack(fill_value=0)
    ct = ct.reindex(columns=TIER_ORDER + [NOT_UNI], fill_value=0).reset_index()
    ct.to_csv(QC / "q1b_q_role_by_tier.csv", index=False)
    missed = B[B.tier.isin(["Low", "not_transporter", NOT_UNI])].sort_values(["strain", "q_role", "locus_tag"])
    missed.to_csv(QC / "q1b_q_role_missed.csv", index=False)
    # figure
    qs = sorted(B.q_role.unique(), key=lambda s: int(s.split(".")[1]))
    qn = dict(zip(B.q_role, B.q_role_name))
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
    cols = TIER_ORDER + [NOT_UNI]
    colc = {**F.TIER_C, NOT_UNI: F.SURF}
    colh = {**F.TIER_H, NOT_UNI: ""}
    xmax = int(ct[cols].sum(axis=1).max())
    for ax, t in zip(axes, TAGS):
        c = ct[ct.strain == t].set_index("q_role")
        for i, qq in enumerate(qs):
            left = 0
            for k in cols:
                v = int(c[k].get(qq, 0)) if qq in c.index else 0
                if v:
                    ax.barh(i, v, left=left, height=0.55, color=colc[k], hatch=colh[k],
                            edgecolor=F.TEXT2 if k == NOT_UNI else F.SURF, linewidth=0.6 if k == NOT_UNI else F.GAP_LW)
                    if v >= 2:
                        ax.text(left + v / 2, i, str(v), ha="center", va="center", fontsize=7, color=F.TIER_TXT.get(k, F.TEXT))
                left += v
            ax.text(left + 0.4, i, str(left), va="center", fontsize=7.5, color=F.TEXT)
        ax.set_yticks(range(len(qs)), [f"{qq} {qn[qq]}" for qq in qs], fontsize=8)
        ax.set_ylim(len(qs) - 0.4, -0.6)
        ax.set_xlim(0, xmax * 1.15)
        ax.set_title(LABEL[t], loc="left", fontsize=10)
        ax.set_xlabel("genes")
        F.xgrid(ax)
    handles = [Patch(facecolor=colc[k], hatch=colh[k], edgecolor=F.TEXT2, linewidth=0.4, label=k) for k in cols]
    fig.legend(handles=handles, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.0))
    F.head(fig, "Genes with a curated Cyanorak transport role, by the tier their system received",
           "Source: genes_by_ontology(cyanorak_role, Q.1–Q.9) per strain; data/<strain>/p3_<strain>_gene_systems_"
           f"{REF}.csv, p11_<strain>_systems.csv; data/qc/q1b_q_role_by_tier.csv")
    fig.subplots_adjust(left=0.27, right=0.98, top=0.84, bottom=0.2, wspace=0.12)
    return B, ct, missed, F.save(fig, "fig8_q_roles_vs_tier")


# --------------------------------------------------------------------------- c: random sample per tier
def check_c():
    rows = []
    for t in TAGS:
        x = DATA[t]
        prod = x["roles"].set_index("locus_tag")["product"]
        gs = x["gs"]
        for k in TIER_ORDER:
            s = x["sys"][x["sys"].tier == k]
            s = s.sample(n=min(10, len(s)), random_state=SEED) if len(s) else s
            for r in s.itertuples():
                loci = sorted(gs[gs.system_id == r.system_id].locus_tag)
                rows.append({"strain": t, "tier": k, "system_id": r.system_id, "member_names": r.member_names,
                             "member_loci": "|".join(loci), "products": " | ".join(str(prod.get(l)) for l in loci),
                             "tier_reason": r.tier_reason, "known_false_positive": bool(r.known_false_positive),
                             "top3_most_specific_substrates": " | ".join(top_substrates(x["cls"], r.system_id))})
    C = pd.DataFrame(rows)
    C.to_csv(QC / "q1c_random_systems.csv", index=False)
    return C


# --------------------------------------------------------------------------- d: High systems, substrate vs product
def families(text, side):
    tx = str(text).lower()
    return {f for f, pats in KW.items() if re.search(pats[side], tx)}


def check_d():
    rows = []
    for t in TAGS:
        x = DATA[t]
        prod = x["roles"].set_index("locus_tag")
        gs = x["gs"]
        for r in x["sys"][x["sys"].tier == "High"].itertuples():
            loci = sorted(gs[gs.system_id == r.system_id].locus_tag)
            subs = top_substrates(x["cls"], r.system_id)
            ptxt = " | ".join(f"{prod.gene_name.get(l) if isinstance(prod.gene_name.get(l), str) else ''} "
                              f"{prod['product'].get(l)}" for l in loci)
            fs, fp = families(" | ".join(subs), 0), families(ptxt, 1)
            if fs & fp:
                flag = "agree"
            elif fs and fp:
                flag = "disagree"
            elif fs:
                flag = "substrate keyword only"
            elif fp:
                flag = "product keyword only"
            else:
                flag = "no keyword"
            rows.append({"strain": t, "system_id": r.system_id, "member_names": r.member_names, "member_loci": "|".join(loci),
                         "products": ptxt, "top_most_specific_substrates": " | ".join(subs),
                         "substrate_keyword_families": "|".join(sorted(fs)), "product_keyword_families": "|".join(sorted(fp)),
                         "keyword_flag": flag})
    Dd = pd.DataFrame(rows)
    Dd.to_csv(QC / "q1d_high_substrate_vs_product.csv", index=False)
    Dd[Dd.keyword_flag == "disagree"].to_csv(QC / "q1d_disagreements.csv", index=False)
    return Dd


# --------------------------------------------------------------------------- e: gap sensitivity
def tiers_for_variant(t, vn, res):
    x = DATA[t]
    d = D / t if vn == REF else D / t / "grid"
    g = pd.read_csv(d / f"p3_{t}_gene_systems_{vn}.csv")
    s = pd.read_csv(d / f"p3_{t}_systems_{vn}.csv").set_index("system_id")
    roles = x["roles"].set_index("locus_tag")
    rs = res[t].set_index("locus_tag").transport_substrate_resolution
    out = {}
    for sid, mem in g.groupby("system_id").locus_tag:
        mem = sorted(mem)
        lts = [roles.loc[m, "likely_transporter"] for m in mem]
        mres = sorted({str(rs.get(m)) for m in mem if pd.notna(rs.get(m))})
        c123 = pd.to_numeric(roles.loc[mem, "tcdb_c123_max_score"], errors="coerce")
        c123max = None if c123.isna().all() else float(c123.max())
        curated_q = any(roles.loc[m, "likely_transporter"] == "strong"
                        and {"cyanorak", "tcdb"} <= set(str(roles.loc[m, "likely_transporter_basis"]).split("|"))
                        for m in mem)
        out[sid] = nt.system_tier(strong="strong" in lts, tcdb_only="tcdb_only" in lts,
                                  role_complete=nt.to_bool(s.loc[sid, "role_complete"]), member_resolutions=mres,
                                  c123_max_score=c123max, curated_q=curated_q)[0]
    return g, out


def check_e(res):
    variants = {100: "gap100_roleT_crossT", 200: REF, 500: "gap500_roleT_crossT"}
    tc, mem_rows, ref_check = [], [], {}
    for t in TAGS:
        x = DATA[t]
        names = x["roles"].set_index("locus_tag").gene_name
        anchors = {fam: [lt for lt in x["roles"].locus_tag if names.get(lt) in gn] for fam, gn in LOCI.items()}
        ref_sets = {}
        for gap, vn in variants.items():
            g, tiers = tiers_for_variant(t, vn, res)
            if gap == 200:
                p11 = x["sys"].set_index("system_id").tier
                ref_check[t] = int(sum(tiers[s] != p11.get(s) for s in tiers))
            for k in TIER_ORDER:
                tc.append({"strain": t, "gap_bp": gap, "tier": k, "systems": sum(v == k for v in tiers.values())})
            sid_of = dict(zip(g.locus_tag, g.system_id))
            memb = g.groupby("system_id").locus_tag.agg(lambda s: "|".join(sorted(s)))
            for fam, lts in anchors.items():
                sids = sorted({sid_of[lt] for lt in lts if lt in sid_of})
                for sid in sids:
                    key = (fam, sid)
                    rec = {"strain": t, "family": fam, "gap_bp": gap, "system_id": sid, "members": memb[sid],
                           "tier": tiers[sid]}
                    mem_rows.append(rec)
                    if gap == 200:
                        ref_sets[key] = (memb[sid], tiers[sid])
        for r in mem_rows:
            if r["strain"] == t:
                ref = [v for (f, s), v in ref_sets.items() if f == r["family"] and set(r["members"].split("|")) & set(v[0].split("|"))]
                r["same_as_gap200"] = any(r["members"] == m and r["tier"] == tr for m, tr in ref)
    TC = pd.DataFrame(tc)
    TC.to_csv(QC / "q1e_tier_counts_by_gap.csv", index=False)
    M = pd.DataFrame(mem_rows)
    M.to_csv(QC / "q1e_n_relevant_membership_by_gap.csv", index=False)
    # figure
    fig, ax = plt.subplots(figsize=(10, 5.2))
    y, ylab, ypos = 0, [], []
    for t in TAGS:
        for gap in (100, 200, 500):
            left = 0
            for k in TIER_ORDER:
                v = int(TC[(TC.strain == t) & (TC.gap_bp == gap) & (TC.tier == k)].systems.sum())
                F.seg(ax, y, left, v, F.TIER_C[k], F.TIER_H[k], h=0.6)
                if v >= 15:
                    ax.text(left + v / 2, y, str(v), ha="center", va="center", fontsize=7.5, color=F.TIER_TXT[k])
                left += v
            ax.text(left + 4, y, f"{left} systems", va="center", fontsize=8, color=F.TEXT)
            ylab.append(f"{LABEL[t]} gap {gap} bp" + (" (chosen)" if gap == 200 else ""))
            ypos.append(y)
            y += 1
        y += 0.5
    ax.set_yticks(ypos, ylab)
    ax.set_ylim(y - 0.4, -0.6)
    ax.set_xlabel("systems")
    F.xgrid(ax)
    ax.set_xlim(0, TC.groupby(["strain", "gap_bp"]).systems.sum().max() * 1.15)
    handles = [Patch(facecolor=F.TIER_C[k], hatch=F.TIER_H[k], edgecolor=F.SURF, label=k) for k in TIER_ORDER]
    fig.legend(handles=handles, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.0))
    F.head(fig, "Tier counts under the gap 100 / 200 / 500 bp grouping variants",
           "Source: data/<strain>/[grid/]p3_<strain>_{gene_systems,systems}_gap<g>_roleT_crossT.csv;\n"
           "tiers recomputed with n_transport.system_tier (gap 200 reproduces p11 exactly); data/qc/q1e_tier_counts_by_gap.csv")
    fig.subplots_adjust(left=0.22, right=0.97, top=0.82, bottom=0.17)
    return TC, M, ref_check, F.save(fig, "fig9_gap_sensitivity")


# --------------------------------------------------------------------------- f: strain consistency
def check_f():
    rows = []
    for fam, names in FAMILIES.items():
        per = {}
        for t in TAGS:
            x = DATA[t]
            gs = x["gs"]
            sy = x["sys"].set_index("system_id")
            g = gs[gs.gene_name.isin(names)]
            sids = sorted(set(g.system_id))
            per[t] = {"genes": "|".join(f"{a}:{b}" for a, b in sorted(zip(g.locus_tag, g.gene_name))),
                      "n_family_genes": len(g), "systems": "|".join(sids),
                      "tiers": "|".join(sy.tier[s] for s in sids), "member_counts": "|".join(str(sy.n_genes[s]) for s in sids)}
        present = [t for t in TAGS if per[t]["n_family_genes"]]
        flags = []
        if len(present) < len(TAGS):
            flags.append("absent in " + "/".join(LABEL[t] for t in TAGS if t not in present))
        for k, lab in (("tiers", "tier"), ("member_counts", "member count"), ("n_family_genes", "family gene count")):
            if len({str(per[t][k]) for t in present}) > 1:
                flags.append(f"{lab} differs")
        row = {"family": fam, "gene_names": "|".join(names)}
        for t in TAGS:
            for k, v in per[t].items():
                row[f"{t}_{k}"] = v
        row["mismatch"] = "; ".join(flags) or "none"
        rows.append(row)
    Ff = pd.DataFrame(rows)
    Ff.to_csv(QC / "q1f_strain_consistency.csv", index=False)
    return Ff


def main():
    QC.mkdir(parents=True, exist_ok=True)
    q, res, log = kg_fetch_all()
    files = []
    a_rows = []
    for t in TAGS:
        r, f = fig7(t)
        a_rows += r
        files += f
    A = pd.DataFrame(a_rows)
    A.to_csv(QC / "q1a_genemap_genes.csv", index=False)
    B, ct, missed, f = check_b(q)
    files += f
    C = check_c()
    Dd = check_d()
    TC, M, ref_check, f = check_e(res)
    files += f
    Ff = check_f()
    summ = {"n_transport_version": nt.__version__, "seed": SEED, "calls": log,
            "a_loci": A.groupby("strain").locus.nunique().to_dict(),
            "b_q_role_genes": B.groupby("strain").locus_tag.nunique().to_dict(),
            "b_missed": missed.groupby(["strain", "tier"]).locus_tag.nunique().reset_index().to_dict("records"),
            "c_rows": int(len(C)), "d_flags": Dd.groupby(["strain", "keyword_flag"]).size().reset_index(name="n").to_dict("records"),
            "e_ref_variant_tier_mismatches_vs_p11": ref_check,
            "e_n_relevant_rows_not_same_as_gap200": int((~M.same_as_gap200).sum()),
            "f_mismatches": Ff[Ff.mismatch != "none"][["family", "mismatch"]].to_dict("records")}
    (QC / "q1_summary.json").write_text(json.dumps(summ, indent=1, default=str), encoding="utf-8")
    for p in files:
        print(p.relative_to(F.M))
    print(json.dumps({k: v for k, v in summ.items() if k != "calls"}, indent=1, default=str))


if __name__ == "__main__":
    main()
