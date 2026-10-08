"""Writes pilot_genes.csv and pilot_substrates.csv from facts transcribed from MCP calls."""
import csv
from collections import Counter
from build_answer_key import OUT, CASES, coords, METAB_GENES, can_use, order

# same-strand contiguous runs over the fetched coordinate table (break on strand change or locus jump > 5 kb)
RUN = {}
rid = 0
for k, r in enumerate(order):
    if k == 0 or r["strand"] != order[k-1]["strand"] or r["start"] - order[k-1]["end"] > 5000:
        rid += 1
    RUN[r["locus_tag"]] = rid

TRANSPORTERS = {"cyn": ["PMM0370","PMM0371","PMM0372"], "urt_urease": ["PMM0970","PMM0971","PMM0972","PMM0973","PMM0974"],
                "amt1": ["PMM0263"], "dpp": ["PMM1049","PMM1048","PMM0421","PMM0192"],
                "pst": ["PMM0710","PMM0723","PMM0724","PMM0725"], "salY": ["PMM0913"], "fadD": ["PMM0402"]}

def can_use_run(case, mid):
    genes = METAB_GENES[mid]
    if not genes:
        return "no"
    runs = {RUN[t] for t in TRANSPORTERS[case]}
    return "co-located" if any(g in RUN and RUN[g] in runs for g in genes) else "elsewhere in genome"


# locus: (pfam_ids, role_call, [(tcdb_ms_id, evidence, score)], score_max, resolution,
#         ms_distinct, inh_distinct, ms_rows, inh_rows)   -- N-substrate counts
G = {
 "PMM0370": ("PF13379;PF09084", "substrate-binding", [("tcdb:3.A.1.16.1","family_inferred",0.6),("tcdb:3.A.1.16.2","family_inferred",0.6),("tcdb:3.A.1.17.3","family_inferred",0.4),("tcdb:3.A.1.17.6","family_inferred",0.4)], 0.6, "resolved", 4, 0, 6, 0),
 "PMM0371": ("PF00528", "permease", [("tcdb:3.A.1.16.1","family_inferred",0.8),("tcdb:3.A.1.16.2","family_inferred",0.8)], 0.8, "resolved", 3, 0, 4, 0),
 "PMM0372": ("PF00005", "ATPase", [("tcdb:3.A.1.16.1","family_inferred",0.8)], 0.8, "resolved", 2, 0, 2, 0),
 "PMM0373": ("PF02560;PF21291", "enzyme", [], None, None, 0, 0, 0, 0),
 "PMM0963": ("PF00449;PF01979", "enzyme", [], None, None, 0, 0, 0, 0),
 "PMM0964": ("PF00699", "enzyme", [], None, None, 0, 0, 0, 0),
 "PMM0965": ("PF00547", "enzyme", [], None, None, 0, 0, 0, 0),
 "PMM0966": ("PF01774", "other (urease accessory)", [], None, None, 0, 0, 0, 0),
 "PMM0967": ("PF02814;PF05194", "other (urease accessory)", [], None, None, 0, 0, 0, 0),
 "PMM0968": ("PF01730", "other (urease accessory)", [], None, None, 0, 0, 0, 0),
 "PMM0969": ("PF02492", "other (urease accessory)", [], None, None, 0, 0, 0, 0),
 "PMM0970": ("PF13433", "substrate-binding", [("tcdb:3.A.1.4.4","family_inferred",0.6),("tcdb:3.A.1.4.5","family_inferred",0.6)], 0.6, "resolved", 3, 0, 4, 0),
 "PMM0971": ("PF02653", "permease", [("tcdb:3.A.1.4.4","family_inferred",0.8),("tcdb:3.A.1.4.5","family_inferred",0.8)], 0.8, "resolved", 3, 0, 4, 0),
 "PMM0972": ("PF02653", "permease", [("tcdb:3.A.1.4.4","family_inferred",0.8),("tcdb:3.A.1.4.5","family_inferred",0.8)], 0.8, "resolved", 3, 0, 4, 0),
 "PMM0973": ("PF00005;PF12399", "ATPase", [("tcdb:3.A.1.4.4","family_inferred",0.8),("tcdb:3.A.1.4.5","family_inferred",0.8)], 0.8, "resolved", 3, 0, 4, 0),
 "PMM0974": ("PF00005", "ATPase", [("tcdb:1.B.42","homology",0.0),("tcdb:3.A.1.4.4","family_inferred",0.8),("tcdb:3.A.1.4.5","family_inferred",0.8)], 0.8, "resolved", 3, 0, 4, 0),
 "PMM0263": ("PF00909", "single carrier", [("tcdb:1.A.11","homology",0.8)], 0.8, "resolved", 4, 0, 4, 0),
 "PMM1049": ("PF00496", "substrate-binding", [("tcdb:3.A.1.5","family_inferred",0.8)], 0.8, "resolved", 7, 4, 7, 4),
 "PMM1048": ("PF00528;PF19300", "permease", [("tcdb:3.A.1.5","family_inferred",0.8)], 0.8, "resolved", 7, 4, 7, 4),
 "PMM0421": ("PF00528", "permease", [("tcdb:3.A.1.5","family_inferred",0.8)], 0.8, "resolved", 7, 4, 7, 4),
 "PMM0192": ("PF00005;PF08352", "ATPase", [("tcdb:3.A.1.5","family_inferred",0.8)], 0.8, "resolved", 7, 4, 7, 4),
 "PMM0710": ("PF12849", "substrate-binding", [("tcdb:3.A.1.7","homology",0.8)], 0.8, "resolved", 0, 0, 0, 0),
 "PMM0723": ("PF00528", "permease", [("tcdb:3.A.1.7","family_inferred",0.8)], 0.8, "resolved", 0, 0, 0, 0),
 "PMM0724": ("PF00528", "permease", [("tcdb:3.A.1.7","family_inferred",0.8)], 0.8, "resolved", 0, 0, 0, 0),
 "PMM0725": ("PF00005", "ATPase", [("tcdb:3.A.1.7","family_inferred",0.8)], 0.8, "resolved", 0, 0, 0, 0),
 "PMM0913": ("PF02687;PF12704", "permease", [("tcdb:3.A.1","homology",0.8)], 0.8, "family_inferred", 94, 139, 94, 139),
 "PMM0402": ("PF00501;PF23562", "enzyme", [("tcdb:2.A.1","homology",0.0),("tcdb:4.C.1.1","family_inferred",0.8)], 0.8, "resolved", 62, 172, 62, 172),
}
assert len(G) == 27

with open(OUT / "pilot_genes.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["case","locus_tag","gene_name","strand","start","end","pfam_ids","role_call",
                "tcdb_most_specific_ids","tcdb_evidence","tcdb_score_max","substrate_resolution",
                "n_most_specific_n_substrates","n_inherited_n_substrates","n_most_specific_n_rows","n_inherited_n_rows"])
    for case, gl in CASES.items():
        for g in gl:
            pf, role, att, smax, res, msd, inh, msr, inr = G[g]
            c = coords[g]
            w.writerow([case, g, c["gene_name"], c["strand"], c["start"], c["end"],
                        ";".join("pfam:" + p for p in pf.split(";")), role,
                        ";".join(a[0] for a in att), ";".join(f"{a[1]}({a[2]})" for a in att),
                        "" if smax is None else smax, res or "", msd, inh, msr, inr])

NAMES = {
 "chebi:14654":"nitrate","kegg.compound:C00088":"Nitrite","kegg.compound:C01417":"Cyanate","kegg.compound:C00396":"Pyrimidine",
 "kegg.compound:C00086":"Urea","kegg.compound:C07044":"Hydroxyurea","kegg.compound:C14415":"Thiourea",
 "kegg.compound:C00014":"Ammonia","kegg.compound:C00218":"Methylamine","kegg.compound:C00797":"Ethylamine","kegg.compound:C20292":"Tetramethylammonium",
 "chebi:195181":"L-alanyl-L-alanine","chebi:27138":"tripeptide","kegg.compound:C00032":"Heme","kegg.compound:C00284":"EDTA",
 "kegg.compound:C00306":"Bradykinin","kegg.compound:C00430":"5-Aminolevulinate","kegg.compound:C10172":"Stachydrine",
 "chebi:14753":"peptide","chebi:82754":"microcin c","kegg.compound:C00051":"Glutathione","kegg.compound:C00098":"Oligopeptide",
 "kegg.compound:C00487":"Carnitine","kegg.compound:C04114":"(E)-4-(Trimethylammonio)but-2-enoate",
 "chebi:10208":"alpha-amino acid","chebi:135075":"alphaprodine","chebi:104011":"4-aminohippurate","chebi:10426":"a beta-lactam","chebi:14739":"pantothenic acid",
}
METAB_GENES.update({
 "chebi:14753": [], "chebi:82754": [], "kegg.compound:C00098": [],
 "kegg.compound:C00051": ["PMM0110","PMM0566","PMM0630","PMM1006","PMM0567","PMM0178","PMM0559","PMM0653"],
 "chebi:10208": [], "chebi:135075": [], "chebi:104011": [], "chebi:10426": [], "chebi:14739": [],
})
CHEBI_NOTE = "chebi-namespaced node: metabolism arm joins KEGG reactions; 'no' may be an ID-split artefact (e.g. nitrate chebi:14654 vs kegg C00244, pantothenic acid chebi:14739 vs C00864)"

rows = []
# verifier judgement where the mechanical window rule and biology disagree
OVERRIDE = {("amt1", "kegg.compound:C00014"): "elsewhere in genome"}
OVERRIDE_NOTE = {("amt1", "kegg.compound:C00014"): "JUDGEMENT: window-8 rule hits only PMM0257 pncC (offset -6, opposite strand, ~4.6 kb; nicotinamide-nucleotide amidase) - coincidental; 36 MED4 genes react with ammonia (incl. glnA PMM0920) so the expected call is elsewhere-in-genome; AMBIGUOUS by rule"}
def add(case, g, mids, depth, fam, score, note=""):
    for m in mids:
        cu, cg = can_use(case, m)
        n = note
        if cu == "no" and m.startswith("chebi:"):
            n = (n + "; " if n else "") + CHEBI_NOTE
        exp = OVERRIDE.get((case, m), cu)
        if (case, m) in OVERRIDE:
            n = (n + "; " if n else "") + OVERRIDE_NOTE[(case, m)]
        rows.append([case, g, m, NAMES[m], depth, fam, score, exp, cg if exp == "co-located" else ";".join(METAB_GENES[m]), cu, can_use_run(case, m), n])

for g, s in [("PMM0370",0.6),("PMM0371",0.8),("PMM0372",0.8)]:
    add("cyn", g, ["chebi:14654","kegg.compound:C00088"], "most_specific", "tcdb:3.A.1.16.1", s)
for g, s in [("PMM0370",0.6),("PMM0371",0.8)]:
    add("cyn", g, ["kegg.compound:C00088","kegg.compound:C01417"], "most_specific", "tcdb:3.A.1.16.2", s)
add("cyn","PMM0370",["kegg.compound:C00396"],"most_specific","tcdb:3.A.1.17.3",0.4, "ThiXYZ family, single_source eggNOG, pfam uncorroborated")
add("cyn","PMM0370",["kegg.compound:C00396"],"most_specific","tcdb:3.A.1.17.6",0.4, "ThiXYZ family, single_source eggNOG, pfam uncorroborated")
for g, s in [("PMM0970",0.6),("PMM0971",0.8),("PMM0972",0.8),("PMM0973",0.8),("PMM0974",0.8)]:
    add("urt_urease", g, ["kegg.compound:C00086"], "most_specific", "tcdb:3.A.1.4.4", s)
    add("urt_urease", g, ["kegg.compound:C00086","kegg.compound:C07044","kegg.compound:C14415"], "most_specific", "tcdb:3.A.1.4.5", s)
add("amt1","PMM0263",["kegg.compound:C00014","kegg.compound:C00218","kegg.compound:C00797","kegg.compound:C20292"],"most_specific","tcdb:1.A.11",0.8)
DPP_MS = ["chebi:195181","chebi:27138","kegg.compound:C00032","kegg.compound:C00284","kegg.compound:C00306","kegg.compound:C00430","kegg.compound:C10172"]
DPP_IN = ["chebi:14753","chebi:82754","kegg.compound:C00051","kegg.compound:C00098"]
for g in ["PMM1049","PMM1048","PMM0421","PMM0192"]:
    add("dpp", g, DPP_MS, "most_specific", "tcdb:3.A.1.5", 0.8)
    add("dpp", g, DPP_IN, "inherited", "tcdb:3.A.1.5", 0.8, "row reports deepest attachment 3.A.1.5; substrate inherited from an ancestor's set")
SF = "superfamily-only gene (transport_substrate_resolution=family_inferred): reachability, not capability"
add("salY","PMM0913",["chebi:10208","chebi:135075","chebi:14654","chebi:14753","chebi:195181"],"inherited","tcdb:3.A.1",0.8, SF+"; first 5 inherited rows (offset 0) of 139")
add("salY","PMM0913",["kegg.compound:C00086","kegg.compound:C00088","kegg.compound:C01417"],"inherited","tcdb:3.A.1",0.8, SF+"; key-N check")
add("fadD","PMM0402",["kegg.compound:C00487","kegg.compound:C04114"],"most_specific","tcdb:4.C.1.1",0.8,"4.C.1.1 = Fatty Acid Group Translocation family; gene's Pfam is AMP-binding enzyme")
add("fadD","PMM0402",["chebi:10208","chebi:104011","chebi:10426","chebi:14654","chebi:14739"],"inherited","tcdb:2.A.1",0.0,"MFS hit score 0, single_source, 25.6% id / 48.8% qcov; first 5 inherited rows (offset 0) of 172")
add("fadD","PMM0402",["kegg.compound:C00088","kegg.compound:C01417"],"inherited","tcdb:2.A.1",0.0,"MFS score-0 hit; key-N check")

with open(OUT / "pilot_substrates.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["case","locus_tag","metabolite_id","metabolite_name","substrate_depth","tcdb_family_id",
                "tcdb_evidence_score","can_use_expected","can_use_genes","can_use_if_window8_rule","can_use_if_same_strand_run_rule","note"])
    w.writerows(rows)
print(f"pilot_substrates.csv rows: {len(rows)}")
for k, v in sorted(Counter((r[0], r[3], r[7], r[9], r[10]) for r in rows).items()):
    print(k, v)
