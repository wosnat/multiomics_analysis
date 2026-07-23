#!/usr/bin/env python3
"""
Methods follow-up -- Task 2.

Find real full-cassette ABC importers for an ORGANIC-CARBON substrate in HOT1A3
(binding + permease + ATPase all adjacent AND all Pfam-role-confirmed), to replace
livKHMGF as the boundary-rule anchor. Surfaces adjacent runs with Pfam roles; does
NOT finalize grouping (main thread sets the gap + tiebreaker).

Method:
  1. Seeds = HOT1A3 transporter genes whose TCDB family is an organic-C ABC family
     3.A.1.1 (sugar) / .2 (carbohydrate) / .3 (polar AA) / .4 (branched AA) /
     .5 (peptide/oligopeptide).  (from data/transporter_genes.csv)
  2. gene_neighbors (window=3) for all seeds -> union of window genes (catches
     subunits that lack a TCDB tag).
  3. gene_details for coords + alternate_functional_descriptions -> Pfam roles.
  4. Segment into same-contig, same-strand runs with gap <= GAP_MAX; keep runs that
     contain an organic-C SBP member AND >=1 permease AND >=1 ATP-binding (Pfam).

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/04_candidate_cassettes.py
"""
import os
import re
import pandas as pd
from multiomics_explorer import gene_neighbors, gene_details, GraphConnection
from pfam_roles import pfam_domains, role_from_pfam

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
TG = os.path.join(DATA, "transporter_genes.csv")
OUT = os.path.join(DATA, "candidate_cassettes.csv")

ORGANIC_FAMS = ["3.A.1.1", "3.A.1.2", "3.A.1.3", "3.A.1.4", "3.A.1.5"]
FAM_SUBSTRATE = {
    "3.A.1.1": "sugar/maltose (ABC)", "3.A.1.2": "carbohydrate/polyol (ABC)",
    "3.A.1.3": "polar amino acid (ABC)", "3.A.1.4": "branched-chain amino acid (ABC)",
    "3.A.1.5": "peptide/oligopeptide (ABC)",
}
GAP_MAX = 250  # bp; generous, actual gap_to_prev reported per gene (main thread sets final)


# match a family token exactly at the family level: "3.A.1.1" must NOT match
# "3.A.1.10" / "3.A.1.16" (negative lookahead for a trailing digit). "3.A.1.5"
# still matches subfamily "3.A.1.5.5" (next char is '.', not a digit).
_FAM_RE = {f: re.compile(re.escape(f) + r"(?!\d)") for f in ORGANIC_FAMS}


def organic_fam(tcdb_str):
    s = str(tcdb_str)
    for f in ORGANIC_FAMS:
        if _FAM_RE[f].search(s):
            return f
    return None


def substrate_hint(gene_summary, product, tcdb_str):
    fam = organic_fam(tcdb_str)
    base = FAM_SUBSTRATE.get(fam, "") if fam else ""
    txt = f"{gene_summary or ''} {product or ''}".lower()
    for kw in ["branched-chain amino acid", "polar amino acid", "oligopeptide", "dipeptide",
               "peptide", "maltose", "maltodextrin", "glucose", "ribose", "arabinose",
               "xylose", "sn-glycerol", "glycerol", "spermidine", "putrescine",
               "amino acid", "sugar", "carbohydrate", "nickel", "opine"]:
        if kw in txt:
            return f"{kw}" + (f" [{base}]" if base else "")
    return base or "(unresolved)"


def main():
    tg = pd.read_csv(TG)
    h = tg[tg.organism_name.str.contains("HOT1A3")].copy()
    seeds = h[h.tcdb_family.fillna("").apply(lambda s: organic_fam(s) is not None)]
    seed_tags = seeds.locus_tag.tolist()
    print(f"organic-C ABC seed genes: {len(seed_tags)}")

    with GraphConnection() as conn:
        nb = gene_neighbors(locus_tags=seed_tags, window=3, conn=conn)
        window = set(seed_tags)
        for r in nb.get("results", []):
            window.add(r["neighbor_locus_tag"])
        window = sorted(window)
        det = gene_details(locus_tags=window, limit=None, conn=conn)

    dmap = {r["locus_tag"]: r for r in det.get("results", [])}
    tcdb_map = dict(zip(h.locus_tag, h.tcdb_family))
    kegg_map = dict(zip(h.locus_tag, h.kegg_ko_id))

    recs = []
    for lt in window:
        d = dmap.get(lt, {})
        if d.get("start") is None:
            continue
        alt = d.get("alternate_functional_descriptions") or []
        pf = pfam_domains(alt)
        recs.append({
            "locus_tag": lt,
            "contig": d.get("contig"),
            "start": d.get("start"),
            "end": d.get("end"),
            "strand": d.get("strand"),
            "product": d.get("product"),
            "gene_summary": d.get("gene_summary"),
            "pfam_domains": " ; ".join(pf),
            "role_from_pfam": role_from_pfam(pf),
            "kegg_ko_id": kegg_map.get(lt),
            "tcdb_family": tcdb_map.get(lt) if lt in tcdb_map else None,
        })
    g = pd.DataFrame(recs).sort_values(["contig", "start"]).reset_index(drop=True)

    # segment into same-contig/same-strand runs with gap <= GAP_MAX
    run_id = 0
    g["gap_to_prev"] = None
    g["_run"] = -1
    prev = None
    for i in range(len(g)):
        row = g.iloc[i]
        if prev is not None and row.contig == prev.contig and row.strand == prev.strand:
            gap = int(row.start - prev.end)
            g.iat[i, g.columns.get_loc("gap_to_prev")] = gap
            if gap <= GAP_MAX:
                g.iat[i, g.columns.get_loc("_run")] = run_id
                g.iat[i - 1, g.columns.get_loc("_run")] = run_id if g.iloc[i-1]._run == -1 else g.iloc[i-1]._run
            else:
                run_id += 1
                g.iat[i, g.columns.get_loc("_run")] = run_id
        else:
            run_id += 1
            g.iat[i, g.columns.get_loc("_run")] = run_id
        prev = g.iloc[i]

    # keep runs that are real organic-C ABC cassettes
    out = []
    label_n = 0
    for rid, sub in g.groupby("_run"):
        roles = list(sub.role_from_pfam)
        has_sbp = "substrate-binding" in roles
        has_perm = "permease" in roles
        has_atp = "ATP-binding" in roles
        organic = any(organic_fam(x) for x in sub.tcdb_family)
        if not (organic and has_sbp and has_perm and has_atp):
            continue
        label_n += 1
        fam = next((organic_fam(x) for x in sub.tcdb_family if organic_fam(x)), None)
        label = f"HOT1A3_cassette_{label_n:02d}_{fam}"
        for r in sub.sort_values("start").to_dict("records"):
            out.append({
                "system_label": label,
                "locus_tag": r["locus_tag"], "contig": r["contig"],
                "start": r["start"], "end": r["end"], "strand": r["strand"],
                "gap_to_prev": r["gap_to_prev"],
                "product": r["product"], "gene_summary": r["gene_summary"],
                "pfam_domains": r["pfam_domains"], "role_from_pfam": r["role_from_pfam"],
                "kegg_ko_id": r["kegg_ko_id"], "tcdb_family": r["tcdb_family"],
                "substrate_hint": substrate_hint(r["gene_summary"], r["product"], r["tcdb_family"]),
            })

    res = pd.DataFrame(out)
    res.to_csv(OUT, index=False)
    print(f"wrote {len(res)} rows across {res.system_label.nunique() if len(res) else 0} "
          f"candidate cassettes -> {OUT}\n")

    for label, sub in res.groupby("system_label"):
        roles = sub.role_from_pfam.value_counts().to_dict()
        gaps = [int(x) for x in sub.gap_to_prev.dropna()]
        comp = " + ".join(f"{v} {k}" for k, v in roles.items())
        print(f"=== {label} === ({len(sub)} genes; strand {sub.strand.iloc[0]}; "
              f"gaps={gaps}; substrate~{sub.substrate_hint.iloc[0]})")
        print(f"    composition: {comp}")
        for rec in sub.to_dict("records"):
            print(f"    {rec['locus_tag']} [{rec['start']}-{rec['end']}] "
                  f"{str(rec['role_from_pfam']):18s} KO={rec['kegg_ko_id']} "
                  f"TCDB={rec['tcdb_family']} | {rec['product']}")


if __name__ == "__main__":
    main()
