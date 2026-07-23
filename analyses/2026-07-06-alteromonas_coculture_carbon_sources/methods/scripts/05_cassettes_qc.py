#!/usr/bin/env python3
"""
Methods follow-up -- QC of the provisional cassette-grouping rule on TWO more
substrate types (sugar/carbohydrate and amino-acid), by IMPLEMENTING the rule as
a walker and APPLYING it (not just listing genes).

Provisional rule (as given):
 1. Adjacency = consecutive loci, same strand; membership by Pfam transport role
    (SBP_bac*/Peripla_BP* = SBP; BPD_transp* = permease; ABC_tran = ATPase).
    Neighbor-discovery: pull in a consecutive-locus gene carrying a transport Pfam
    role even if enumeration/TCDB missed it.
 2. Repeated ATPase/permease roles do NOT split when members share substrate/family.
 3. STOP at: strand flip; role clash (sensor kinase / non-transport gene);
    substrate-class / annotation break.

Because "consecutive loci" needs TRUE genomic order, the walker uses gene_neighbors
rank_offset (±1, ±2, ...) and walks outward from an SBP anchor, applying the STOPs.

Writes data/cassettes_qc.csv: one row per gene in each grouped system, same columns
as candidate_cassettes.csv PLUS `rule_check`.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/05_cassettes_qc.py
"""
import os
import re
import pandas as pd
from multiomics_explorer import gene_neighbors, gene_details, GraphConnection
from pfam_roles import pfam_domains, role_from_pfam

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
TG = os.path.join(DATA, "transporter_genes.csv")
OUT = os.path.join(DATA, "cassettes_qc.csv")

ABC_ROLES = {"substrate-binding", "permease", "ATP-binding"}

SUBSTRATE_KW = {
    "sugar/carbohydrate": ["sugar", "maltose", "maltodextrin", "ribose", "arabinose",
                           "xylose", "glucose", "fructose", "rhamnose", "galactose",
                           "trehalose", "lactose", "monosaccharide", "polyol", "glycerol",
                           "sn-glycerol", "carbohydrate", "myo-inositol", "fructo"],
    "amino_acid": ["amino acid", "glutamine", "arginine", "histidine", "lysine",
                   "branched-chain", "polar amino", "glutamate", "aspartate",
                   "ornithine", "cystine", "methionine", "proline", "glycine betaine"],
    "peptide": ["peptide", "oligopeptide", "dipeptide", "nickel", "opine"],
    "polyamine": ["spermidine", "putrescine", "polyamine"],
    "phosphate/phosphonate": ["phosphate", "phosphonate", "phosphite"],
    "iron/metal/inorganic": ["iron", "ferric", "fe3", "zinc", "manganese", "molybdate",
                             "sulfate", "sulfonate", "taurine", "nitrate", "bicarbonate",
                             "cobalt", "nickel transport", "heme", "thiamine", "cobalamin",
                             "vitamin b12"],
}


def classify_substrate(texts):
    t = " ".join(x for x in texts if x).lower()
    for cls, kws in SUBSTRATE_KW.items():
        if any(k in t for k in kws):
            return cls
    return "unresolved"


def main():
    tg = pd.read_csv(TG)
    h = tg[tg.organism_name.str.contains("HOT1A3")].copy()
    ko_name = dict(zip(h.locus_tag, h.kegg_ko_name.fillna("")))
    ko_id = dict(zip(h.locus_tag, h.kegg_ko_id.fillna("")))
    tcdb_map = dict(zip(h.locus_tag, h.tcdb_family.fillna("")))
    all_tp = h.locus_tag.tolist()

    with GraphConnection() as conn:
        # details (coords + pfam) for all transporter genes to find SBP anchors
        det0 = gene_details(locus_tags=all_tp, limit=None, conn=conn)
        role0, strand0 = {}, {}
        pf0, summ0, prod0 = {}, {}, {}
        coord = {}  # lt -> (contig, start, end, strand)

        def _ingest(r):
            lt = r["locus_tag"]
            pf = pfam_domains(r.get("alternate_functional_descriptions") or [])
            role0[lt] = role_from_pfam(pf)
            strand0[lt] = r.get("strand")
            pf0[lt] = " ; ".join(pf)
            summ0[lt] = r.get("gene_summary")
            prod0[lt] = r.get("product")
            coord[lt] = (r.get("contig"), r.get("start"), r.get("end"), r.get("strand"))

        for r in det0.get("results", []):
            _ingest(r)
        sbp_anchors = [lt for lt in all_tp if role0.get(lt) == "substrate-binding"]
        print(f"HOT1A3 SBP anchors (Pfam): {len(sbp_anchors)}")

        # one gene_neighbors call for all anchors (ordered neighbors, window 6)
        nb = gene_neighbors(locus_tags=sbp_anchors, window=6, limit=None, conn=conn)
        # anchor coords
        anchor_meta = {a["locus_tag"]: a for a in nb.get("anchors", [])}
        by_anchor = {}
        neigh_all = set()
        for r in nb.get("results", []):
            by_anchor.setdefault(r["anchor_locus_tag"], []).append(r)
            neigh_all.add(r["neighbor_locus_tag"])

        # details for neighbors not already fetched
        missing = sorted(neigh_all - set(role0))
        if missing:
            det1 = gene_details(locus_tags=missing, limit=None, conn=conn)
            for r in det1.get("results", []):
                _ingest(r)

    def walk(anchor):
        """Apply the rule outward from an SBP anchor along rank_offset. Returns
        (member_locus_tags_ordered, stop_left_reason, stop_right_reason)."""
        rows = by_anchor.get(anchor, [])
        astr = strand0.get(anchor)
        # map offset -> neighbor
        off = {r["rank_offset"]: r for r in rows}
        members = {0: anchor}
        # walk right (+1,+2,...) then left (-1,-2,...)
        stops = {}
        for direction in (1, -1):
            k = direction
            reason = "window-end"
            while k in off:
                nb_lt = off[k]["neighbor_locus_tag"]
                nb_role = role0.get(nb_lt, "other/unclear")
                nb_strand = strand0.get(nb_lt)
                if nb_strand != astr:
                    reason = f"strand-flip@{nb_lt}"
                    break
                if nb_role == "sensor-kinase-EXCLUDE":
                    reason = f"role-clash-sensor-kinase@{nb_lt}"
                    break
                if nb_role not in ABC_ROLES:
                    reason = f"non-transport@{nb_lt}({nb_role})"
                    break
                members[k] = nb_lt
                k += direction
            stops["right" if direction == 1 else "left"] = reason
        ordered = [members[i] for i in sorted(members)]
        return ordered, stops["left"], stops["right"]

    # build cassette catalog
    seen = set()
    systems = []  # list of dict(system genes + meta)
    for anchor in sbp_anchors:
        if anchor in seen:
            continue
        members, sl, sr = walk(anchor)
        for m in members:
            seen.add(m)
        roles = [role0.get(m) for m in members]
        has = lambda x: x in roles
        complete = has("substrate-binding") and has("permease") and has("ATP-binding")
        # substrate class
        texts = []
        for m in members:
            texts += [ko_name.get(m, ""), prod0.get(m, ""), summ0.get(m, ""), tcdb_map.get(m, "")]
        sclass = classify_substrate(texts)
        systems.append(dict(anchor=anchor, members=members, roles=roles,
                            complete=complete, stop_left=sl, stop_right=sr, sclass=sclass))

    # ---- report + pick featured sugar & AA ----
    complete_sys = [s for s in systems if s["complete"]]
    print(f"\ncomplete ABC cassettes (SBP+permease+ATPase adjacent): {len(complete_sys)}")
    from collections import Counter
    print("  by substrate class:", dict(Counter(s["sclass"] for s in complete_sys)))
    print("  orphan SBP anchors (no cassette formed):",
          sum(1 for s in systems if not s["complete"]))

    # Featured: the two required substrate types + any complete organic cassette
    featured = []
    # sugar family anchor(s) 3.A.1.1/3.A.1.2 and AA family anchors 3.A.1.3/3.A.1.4
    def fam(s, fams):
        return any(re.search(re.escape(f) + r"(?!\d)", str(s)) for f in fams)
    for s in systems:
        fams_here = " ".join(tcdb_map.get(m, "") for m in s["members"])
        is_sugar_fam = fam(fams_here, ["3.A.1.1", "3.A.1.2"])
        is_aa_fam = fam(fams_here, ["3.A.1.3", "3.A.1.4"])
        if is_sugar_fam or is_aa_fam or s["complete"]:
            s["_feat_reason"] = ("sugar-family " if is_sugar_fam else "") + \
                                ("AA-family " if is_aa_fam else "") + \
                                (f"complete-cassette-{s['sclass']}" if s["complete"] else "orphan-SBP")
            featured.append(s)

    # assemble output rows
    out = []
    for si, s in enumerate(featured, 1):
        members = s["members"]
        # rule_check text (same for all rows of a system)
        n_sbp = s["roles"].count("substrate-binding")
        n_perm = s["roles"].count("permease")
        n_atp = s["roles"].count("ATP-binding")
        if s["complete"]:
            verdict = (f"GROUPED complete cassette ({n_sbp} SBP + {n_perm} permease + "
                       f"{n_atp} ATPase); stops L={s['stop_left']} R={s['stop_right']}; "
                       f"substrate~{s['sclass']}")
        else:
            verdict = (f"NO cassette formed -- orphan SBP ({n_sbp} SBP, {n_perm} permease, "
                       f"{n_atp} ATPase); STOP fired immediately L={s['stop_left']} "
                       f"R={s['stop_right']}; rule correctly refused to group")
        label = f"HOT1A3_qc_{si:02d}_{s['sclass']}"
        for m in members:
            c = coord.get(m, (None, None, None, strand0.get(m)))
            out.append(dict(
                system_label=label, locus_tag=m,
                contig=c[0], start=c[1], end=c[2], strand=c[3],
                gap_to_prev=None,
                product=prod0.get(m), gene_summary=summ0.get(m),
                pfam_domains=pf0.get(m), role_from_pfam=role0.get(m),
                kegg_ko_id=ko_id.get(m, ""), tcdb_family=tcdb_map.get(m, ""),
                substrate_hint=s["sclass"], rule_check=verdict,
                feat_reason=s.get("_feat_reason", "").strip(),
            ))
    res = pd.DataFrame(out)
    # fill gap_to_prev within each system (needs sorted by start)
    res = res.sort_values(["system_label", "contig", "start"]).reset_index(drop=True)
    for lab, sub in res.groupby("system_label"):
        idxs = sub.index.tolist()
        prev_end = None
        for ix in idxs:
            st = res.at[ix, "start"]
            if prev_end is not None and pd.notna(st) and pd.notna(prev_end):
                res.at[ix, "gap_to_prev"] = int(st - prev_end)
            prev_end = res.at[ix, "end"]
    res.to_csv(OUT, index=False)
    print(f"\nwrote {len(res)} rows / {res.system_label.nunique()} featured systems -> {OUT}\n")

    for lab, sub in res.groupby("system_label"):
        r0 = sub.iloc[0]
        print(f"=== {lab} === feat={r0['feat_reason']}")
        print(f"    rule_check: {r0['rule_check']}")
        for rec in sub.to_dict("records"):
            print(f"    {rec['locus_tag']} {rec['strand']} gap={rec['gap_to_prev']} "
                  f"{str(rec['role_from_pfam']):18s} [{rec['pfam_domains']}] | {rec['product']}")


if __name__ == "__main__":
    main()
