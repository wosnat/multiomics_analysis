"""Step 8: compound classes for N-class substrate groups = NAME RULES ONLY (researcher decision
2026-10-08, v1.3; the earlier pathway / family layers misassigned too often).

  class: nt.compound_class (name rules incl. the five inorganic classes, flagged analogues, the
         no-formula rule); unmatched -> "unclassified N" / "unclassified (no formula)";
  context columns (never assign a class):
    pathway_context = KEGG pathway votes of the members (list_metabolites verbose; each pathway mapped by
                      nt.pathway_class; map in p12_pathway_class_map.csv);
    family_context  = TCDB family context of the carrying rows (family name + GO links_out names; GO
                      ignored for lumping families), only when all rows agree (nt.group_family_class);
  class_caveat = "best effort: names only; KG has no chemical categories".
The pathway tie-break by curated transport class is dropped.
The KG has no ChEBI class hierarchy (kg_schema: no class node or relationship; Metabolite carries
chebi_id only), so ChEBI classes cannot be used.
KG calls (kg_fetch, strict, single call per chunk): list_metabolites(member ids, verbose);
  ontology_term_details(TCDB families of the table).
Inputs (<out-dir>): p11_<tag>_system_substrates_annotated.csv, p11_<tag>_systems.csv,
  p11_<tag>_gene_roles_cyanorak_tigr.csv, p5_<tag>_metabolite_xref.csv, p5_<tag>_lumping_families.csv.
Outputs: p12_<tag>_compound_classes.csv, p12_pathway_class_map.csv, p12_q_class_map.csv,
  p12_<tag>_family_context.csv, p12_<tag>_system_substrates_classified.csv, p12_<tag>_review_candidates.csv,
  p12_<tag>_summary.json.
Usage: ... p12_compound_classes_layered.py --organism "Prochlorococcus MED4" --out-dir <dir>
"""
import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd
from multiomics_explorer import GraphConnection, list_metabolites, ontology_term_details, to_dataframe

from common import kf, nt, resolve_organism, role_map_hash, write_summary

#: Cyanorak transport (Q) role -> compound classes it is compatible with (layer-4 tie-break only).
#: Keyed by words in the role name so it is strain-independent; reviewable as p12_q_class_map.csv.
Q_CLASS_MAP = [
    ("amino acids, peptides and amines", {"amino acids", "peptides", "amines", "polyamines"}),
    ("nucleosides, purines and pyrimidines", {"nucleobases/nucleosides"}),
    ("cations and iron carrying compounds", {"siderophore"}),
    ("anions", {"nitrate", "nitrite", "cyanate"}),
]


def q_allowed(role_names):
    out = set()
    for n in role_names:
        nl = str(n).lower()
        for key, cls in Q_CLASS_MAP:
            if key in nl:
                out |= cls
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    d = Path(a.out_dir)
    tag = a.organism.split()[-1].lower()
    ann = pd.read_csv(d / f"p11_{tag}_system_substrates_annotated.csv", low_memory=False)
    sy = pd.read_csv(d / f"p11_{tag}_systems.csv").set_index("system_id")
    roles = pd.read_csv(d / f"p11_{tag}_gene_roles_cyanorak_tigr.csv")
    xref = pd.read_csv(d / f"p5_{tag}_metabolite_xref.csv", dtype={"chebi_id": str})
    lump = set(pd.read_csv(d / f"p5_{tag}_lumping_families.csv").query("is_lumping").term_id)
    log = []
    N = ann[ann.n_status != "no_N"].copy()
    groups = sorted(set(N.equiv_group))
    mem = xref[xref.equiv_group.isin(groups)]
    fams = sorted(set(ann.tcdb_family_id.dropna()))
    with GraphConnection() as conn:
        resolve_organism(a.organism, conn)
        lm = to_dataframe({"results": kf.fetch(
            list_metabolites, "list_metabolites(N-class group member ids, verbose)", log, ("metabolite_id",),
            chunk_param="metabolite_ids", chunk_size=400, limit_none_ok=True, strict_inputs=True,
            metabolite_ids=sorted(set(mem.metabolite_id)), verbose=True, conn=conn)["results"]})
        td = kf.fetch(ontology_term_details, "ontology_term_details(table families, links_out)", log, ("term_id",),
                      chunk_param="term_ids", chunk_size=100, limit_none_ok=True, strict_inputs=True,
                      term_ids=fams, conn=conn)["results"]

    # layer 2 inputs: member pathways and the pathway -> class map
    pw = {}
    pmap_rows = {}
    for r in lm.itertuples():
        ids = nt.parse_list(getattr(r, "pathway_ids", ""))
        nms = nt.parse_list(getattr(r, "pathway_names", ""))
        pw[r.metabolite_id] = ids
        for i, pid in enumerate(ids):
            if pid not in pmap_rows:
                nm = nms[i] if i < len(nms) else ""
                cls, rule = nt.pathway_class(pid, nm)
                pmap_rows[pid] = {"pathway_id": pid, "pathway_name": nm, "class": cls or nt.NO_BASIS, "rule": rule}
    pmap_df = pd.DataFrame(sorted(pmap_rows.values(), key=lambda x: x["pathway_id"]))
    pmap_df.to_csv(d / "p12_pathway_class_map.csv", index=False)
    pmap = {r["pathway_id"]: (None if r["class"] == nt.NO_BASIS else r["class"]) for r in pmap_rows.values()}
    pd.DataFrame([{"q_role_name_contains": k, "allowed_classes": "|".join(sorted(v))} for k, v in Q_CLASS_MAP]) \
        .to_csv(d / "p12_q_class_map.csv", index=False)

    # layer 3: family context per family, then per row
    fam_rows = []
    for t in td:
        gos = [x.get("target_name") for x in (t.get("links_out") or []) if str(x.get("target_ontology", "")).startswith("go")]
        is_l = t["term_id"] in lump
        cls, txt = nt.family_context_class(t.get("name"), gos, use_go=not is_l)
        fam_rows.append({"term_id": t["term_id"], "name": t.get("name"), "is_lumping": is_l, "n_go_links": len(gos),
                         "go_names": " | ".join(sorted(set(map(str, gos))))[:2000],
                         "family_context_class": cls or nt.NO_BASIS, "matched_text": txt or nt.NO_BASIS})
    fam = pd.DataFrame(fam_rows)
    fam.to_csv(d / f"p12_{tag}_family_context.csv", index=False)
    fcls = dict(zip(fam.term_id, fam.family_context_class))
    fname = dict(zip(fam.term_id, fam.name))
    ann["tcdb_family_name_full"] = ann.tcdb_family_id.map(fname)
    ann["family_context_class"] = ann.tcdb_family_id.map(fcls).fillna(nt.NO_BASIS)
    N = ann[ann.n_status != "no_N"]

    # layer 4: Q roles of carrying systems
    cy = roles[roles.ontology_type == "cyanorak_role"]
    qnames = dict(zip(cy.term_id, cy.term_name))
    sys_q = {s: [qnames.get(q, q) for q in str(v).split("|") if q and q != nt.NO_BASIS]
             for s, v in sy.transport_class_ids.items()}

    rows = []
    by_group = N.groupby("equiv_group")
    for g in groups:
        m = mem[mem.equiv_group == g]
        if m.empty:
            m = pd.DataFrame({"metabolite_id": [g], "name": [g], "n_status": [""]})
        st = m.n_status.tolist()
        name_res = nt.compound_class(m.name.tolist(), n_status=st)
        pids = sorted({p for mid in m.metabolite_id for p in pw.get(mid, [])})
        path_res = nt.pathway_vote(pids, pmap)
        gr = by_group.get_group(g)
        rc = [None if c == nt.NO_BASIS else c for c in gr.family_context_class]
        fam_g = nt.group_family_class(rc)
        res = nt.name_class_with_context(st, name_res, path_res, fam_g)
        cls, src = res["compound_class"], res["class_source"]
        only_lump = bool(len(gr)) and all(f in lump for f in gr.tcdb_family_id.dropna())
        rows.append({"equiv_group": g, "member_ids": "|".join(sorted(m.metabolite_id)),
                     "names": "|".join(sorted(set(map(str, m.name)))), "n_status": "|".join(sorted(set(map(str, st)))),
                     "compound_class": cls, "class_source": src, "class_caveat": res["class_caveat"],
                     "pathway_context": res["pathway_context"], "family_context": res["family_context"],
                     "name_rule": name_res[1], "analogue_flag": bool(name_res[2]) if src == "name" else False,
                     "carried_only_via_lumping_families": only_lump,
                     "pathways_mapped": " | ".join(f"{p}:{pmap_rows[p]['pathway_name']}->{pmap.get(p)}"
                                                   for p in pids if pmap.get(p)) or nt.NO_BASIS,
                     "n_pathways": len(pids), "family_row_classes": json.dumps(Counter(map(str, rc))),
                     "can_use_applicable": nt.can_use_applicable(cls),
                     "n_rows": int(len(gr)), "n_systems": int(gr.system_id.nunique()),
                     "n_most_specific_rows": int((gr.substrate_depth == "most_specific").sum())})
    cc = pd.DataFrame(rows)
    cc.to_csv(d / f"p12_{tag}_compound_classes.csv", index=False)
    cm = cc.set_index("equiv_group")
    ann["compound_class_final"] = ann.equiv_group.map(cm.compound_class).where(ann.n_status != "no_N", "no_N")
    ann["class_source"] = ann.equiv_group.map(cm.class_source).where(ann.n_status != "no_N", "not_applicable")
    ann["pathway_context"] = ann.equiv_group.map(cm.pathway_context).where(ann.n_status != "no_N", "not_applicable")
    ann["family_context_group"] = ann.equiv_group.map(cm.family_context).where(ann.n_status != "no_N", "not_applicable")
    ann["can_use_applicable"] = ann.compound_class_final.map(nt.can_use_applicable)
    ann["class_caveat"] = nt.CLASS_CAVEAT   # every row (v1.4)
    ann.to_csv(d / f"p12_{tag}_system_substrates_classified.csv", index=False)

    # review candidates: unclassified N, contains_N, carried by a most_specific row of a High/Medium system,
    # NOT only via lumping families (v1.3)
    tier = sy.tier.to_dict()
    unc = set(cc[(cc.compound_class == nt.UNCLASSIFIED_N) & cc.n_status.str.contains("contains_N")
                 & ~cc.carried_only_via_lumping_families].equiv_group)
    rv = ann[ann.equiv_group.isin(unc) & (ann.substrate_depth == "most_specific")
             & ann.system_id.map(tier).isin(["High", "Medium"]) & ~ann.tcdb_family_id.isin(lump)]
    rev = (rv.groupby("equiv_group")
           .agg(names=("metabolite_name", lambda s: "|".join(sorted(set(map(str, s))))),
                metabolite_ids=("metabolite_id", lambda s: "|".join(sorted(set(s)))),
                systems=("system_id", lambda s: "|".join(sorted(set(s)))),
                tiers=("system_id", lambda s: "|".join(sorted({tier[x] for x in s}))),
                genes=("locus_tag", lambda s: "|".join(sorted(set(s)))),
                gene_names=("gene_name", lambda s: "|".join(sorted(set(map(str, s.dropna()))))),
                tcdb_families=("tcdb_family_id", lambda s: "|".join(sorted(set(s)))),
                tcdb_family_names=("tcdb_family_name_full", lambda s: " || ".join(sorted(set(map(str, s)))))).reset_index())
    rev.insert(0, "strain", tag)
    rev.to_csv(d / f"p12_{tag}_review_candidates.csv", index=False)
    summ = {"organism": a.organism, "role_map_hash": role_map_hash(d),
            "kg_chebi_class_hierarchy": "absent (kg_schema: no class node/relationship; Metabolite has chebi_id only)",
            "groups": int(len(cc)), "per_layer": cc.class_source.value_counts().to_dict(),
            "per_class": cc.compound_class.value_counts().to_dict(),
            "class_caveat": nt.CLASS_CAVEAT,
            "pathways_seen": int(len(pmap_df)), "pathways_mapped": int((pmap_df["class"] != nt.NO_BASIS).sum()),
            "families": int(len(fam)), "families_with_context": fam.family_context_class.value_counts().to_dict(),
            "review_candidates": int(len(rev)), "calls": log}
    write_summary(d / f"p12_{tag}_summary.json", summ)
    print(json.dumps({k: v for k, v in summ.items() if k not in ("calls", "per_layer_x_class")}, indent=1, default=str))


if __name__ == "__main__":
    main()
