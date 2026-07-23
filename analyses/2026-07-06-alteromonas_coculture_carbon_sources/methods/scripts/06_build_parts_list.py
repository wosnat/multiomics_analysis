#!/usr/bin/env python3
"""
Methods follow-up -- full parts-list sweep, BOTH strains, applying the LOCKED
grouping rule genome-wide. Writes data/parts_list.csv (one row per strain,gene)
incrementally per strain, and data/qc_parts_list_summary.csv.

LOCKED rule (see coordinator msg):
 - System = consecutive-locus, same-strand genes with a transport Pfam role
   (SBP: SBP_bac*/Peripla_BP*; permease: BPD_transp*/FecCD; ATPase: ABC_tran)
   sharing substrate/family. Pfam role primary; KO/product/TCDB confirm.
 - Neighbor-discovery: include a consecutive-locus gene with a transport Pfam role
   even if enumeration/TCDB missed it.
 - Repeated role does NOT split when family shared.
 - Non-transport genes are PERMEABLE (reached across, tagged, not stops); a
   co-located catabolic gene for the substrate -> recorded as catabolic_neighbor.
 - STOP at: strand flip; a transport subunit of a different substrate/family;
   or reach bound (gap > GAP_REACH bp with no further same-family subunit).
 - Single-gene systems valid (orphan SBPs, secondary carriers) -> own system_id.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/06_build_parts_list.py
"""
import os
import re
import pandas as pd
from multiomics_explorer import gene_neighbors, gene_details, GraphConnection
from pfam_roles import pfam_domains, role_from_pfam

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
TG = os.path.join(DATA, "transporter_genes.csv")
OUT = os.path.join(DATA, "parts_list.csv")
QC = os.path.join(DATA, "qc_parts_list_summary.csv")

STRAINS = {"Alteromonas macleodii HOT1A3": "ACZ81", "Alteromonas macleodii EZ55": "EZ55"}
GAP_REACH = 200          # bp; join ABC subunits within this gap (permeable across small genes)
SBP3_WINDOW = 3          # +/- genes to inspect for SBP_bac_3 bucket
ABC_SUBUNIT = {"substrate-binding", "permease", "ATP-binding"}

CATAB_RE = re.compile(
    r"dehydrogenase|oxidase|reductase|hydrolase|synthase|synthetase|lyase|"
    r"aldolase|decarboxylase|hydratase|isomerase|deaminase|peptidase|hydroxylase|"
    r"dioxygenase|monooxygenase|esterase|amidase|racemase|epimerase|thiolase|"
    r"carboxylase|mutase|oxidoreductase|aminotransferase|dehydratase|kinase|"
    r"transaldolase|transketolase|cyclase|nuclease|glycosyltransferase", re.I)

INORGANIC = re.compile(
    r"iron|ferric|ferrous|fe\(iii\)|fe3|zinc|manganese|molybdate|tungstate|sulfate|"
    r"sulfite|phosphate|phosphonate|phosphite|nitrate|nitrite|bicarbonate|cyanate|"
    r"potassium|sodium|calcium|magnesium|cobalt|nickel|copper|chloride|ammoni|"
    r"\bmetal\b|heme|siderophore|cobalamin|thiamin|vitamin|biotin|riboflavin|"
    r"selenat|arsen|chromate|fluoride|silica", re.I)
DUAL_CN = re.compile(
    r"amino acid|peptide|oligopeptide|dipeptide|glutamine|glutamate|arginine|"
    r"histidine|lysine|ornithine|cystine|methionine|proline|leucine|isoleucine|"
    r"valine|branched-chain|polar amino|nucleoside|purine|pyrimidine|spermidine|"
    r"putrescine|polyamine|betaine|choline|taurine|urea|glutathione|opine|"
    r"ectoine|creatine|carnitine|sarcosine|nickel/peptide", re.I)
ORGANIC_C = re.compile(
    r"sugar|maltose|maltodextrin|glucose|fructose|ribose|arabinose|xylose|rhamnose|"
    r"galactose|trehalose|lactose|mannose|monosaccharide|polyol|glycerol|sorbitol|"
    r"mannitol|inositol|carbohydrate|gluconate|glucuronate|lactate|citrate|malate|"
    r"succinate|fumarate|alpha-ketoglutarate|pyruvate|acetate|benzoate|carboxylate|"
    r"organic acid|fatty acid|lipid|glycolate|dicarboxylate|tartrate|C4-dicarboxylate|"
    r"phenylpropionate|xylose:h", re.I)
EXPORT = re.compile(
    r"efflux|export|exporter|secretion|extrusion|multidrug|macb|rnd\b|\bmfp\b|"
    r"lipoprotein-releasing|lipid.*export|o-antigen|capsul|lps|lipid a export|"
    r"drug resistance|resistance protein|toxin", re.I)


def famset(tcdb):
    return set(re.findall(r"3\.A\.1\.\d+", str(tcdb)))


def substrate_from_text(text, allow_generic=False):
    """Extract a substrate phrase from a KO name / product string."""
    if not text or str(text) == "nan":
        return None
    for part in str(text).split(" ; "):
        p = part
        if ";" in p:
            p = p.split(";", 1)[1]
        p = p.strip()
        seg = re.split(r"\btransport system\b|\btransporter\b|\btransport\b|"
                       r"\bpermease\b|\buptake\b|\bABC\b|\bsubstrate-binding\b|"
                       r"\breceptor\b|\bsymporter\b|\bantiporter\b|\bfacilitator\b",
                       p, maxsplit=1)
        cand = seg[0].strip(" ,-")
        if not cand:
            continue
        if re.search(r"putative|multidrug|^drug$|hypothetical|uncharacter|^ABC$|"
                     r"^MFS$|domain-containing|family protein|^ATP-binding", cand, re.I):
            if not allow_generic:
                continue
        if len(cand) > 2:
            return cand
    return None


def organic_class(*texts):
    # Carbon-bearing calls take precedence over inorganic: a carbon molecule whose
    # name also carries a metal/phosphate (e.g. peptide/nickel Opp-Nik ABC,
    # glycerol-3-phosphate) is still carbon. Pure inorganic importers (Fe, sulfate,
    # phosphate) carry no organic/peptide word so still land 'inorganic'.
    # PROVISIONAL -- the main thread finalizes; the dual peptide/nickel ambiguity is
    # surfaced, not hidden.
    t = " ".join(str(x) for x in texts if x and str(x) != "nan").lower()
    if not t.strip():
        return "ambiguous"
    if DUAL_CN.search(t):
        return "dual-C+N"
    if ORGANIC_C.search(t):
        return "organic-C"
    if INORGANIC.search(t):
        return "inorganic"
    return "ambiguous"


def build_strain(org, prefix, tg, conn, write_header):
    h = tg[tg.organism_name == org].copy()
    tp = h.locus_tag.tolist()
    ko_name = dict(zip(h.locus_tag, h.kegg_ko_name.fillna("")))
    ko_id = dict(zip(h.locus_tag, h.kegg_ko_id.fillna("")))
    tcdb_map = dict(zip(h.locus_tag, h.tcdb_family.fillna("")))

    # neighbor-discovery (limit=None! avoid the 25-row truncation)
    nb = gene_neighbors(locus_tags=tp, window=4, limit=None, conn=conn)
    neigh = {r["neighbor_locus_tag"] for r in nb.get("results", [])}
    allg = sorted(set(tp) | neigh)
    det = gene_details(locus_tags=allg, limit=None, conn=conn)

    G = {}
    for r in det.get("results", []):
        lt = r["locus_tag"]
        pf = pfam_domains(r.get("alternate_functional_descriptions") or [])
        prod = r.get("product")
        role = role_from_pfam(pf)
        is_sensor = (role == "sensor-kinase-EXCLUDE")
        is_catab = (role in ("other/unclear",) and prod is not None
                    and bool(CATAB_RE.search(prod)) and not is_sensor)
        G[lt] = dict(
            locus_tag=lt, contig=r.get("contig"), start=r.get("start"),
            end=r.get("end"), strand=r.get("strand"), role=role,
            pfam=" ; ".join(pf), summary=r.get("gene_summary"), product=prod,
            ko_id=ko_id.get(lt, ""), ko_name=ko_name.get(lt, ""),
            tcdb=tcdb_map.get(lt, ""), is_sensor=is_sensor, is_catab=is_catab,
            in_tp=(lt in set(tp)),
        )

    # genome-ordered list per contig (all genes we know coords for)
    ordered = sorted([g for g in G.values() if g["start"] is not None],
                     key=lambda x: (x["contig"], x["start"]))
    idx_of = {g["locus_tag"]: i for i, g in enumerate(ordered)}

    # ---- form ABC-subunit systems by walking subunit genes in genomic order ----
    subunits = [g for g in ordered if g["role"] in ABC_SUBUNIT]
    systems = []            # list of list-of-locus_tags
    cur = []
    for g in subunits:
        if not cur:
            cur = [g]
            continue
        last = cur[-1]
        gap = g["start"] - last["end"]
        same = (g["contig"] == last["contig"]) and (g["strand"] == last["strand"])
        sysfam = set().union(*[famset(m["tcdb"]) for m in cur]) if cur else set()
        gf = famset(g["tcdb"])
        clash = bool(gf) and bool(sysfam) and gf.isdisjoint(sysfam)
        if same and gap <= GAP_REACH and not clash:
            cur.append(g)
        else:
            systems.append(cur)
            cur = [g]
    if cur:
        systems.append(cur)

    # assign system ids
    sysid_of = {}
    sys_members = {}
    n = 0
    for s in systems:
        n += 1
        sid = f"{prefix}_S{n:04d}"
        for m in s:
            sysid_of[m["locus_tag"]] = sid
        sys_members[sid] = [m["locus_tag"] for m in s]
    # secondary carriers + other transporters -> own single-gene systems
    for lt in tp:
        if lt in sysid_of:
            continue
        n += 1
        sid = f"{prefix}_S{n:04d}"
        sysid_of[lt] = sid
        sys_members[sid] = [lt]

    # catabolic neighbors per system (catabolic genes within system span +/-1 gene)
    catab_by_sys = {}
    for sid, members in sys_members.items():
        mrows = [G[m] for m in members if m in G and G[m]["start"] is not None]
        if not mrows:
            catab_by_sys[sid] = []
            continue
        contig = mrows[0]["contig"]
        lo = min(m["start"] for m in mrows)
        hi = max(m["end"] for m in mrows)
        cats = []
        # scan ordered genes near the span
        i0 = min(idx_of[m["locus_tag"]] for m in mrows)
        i1 = max(idx_of[m["locus_tag"]] for m in mrows)
        for j in range(max(0, i0 - 1), min(len(ordered), i1 + 2)):
            gj = ordered[j]
            if gj["contig"] == contig and gj["is_catab"] and gj["locus_tag"] not in members:
                cats.append(gj["locus_tag"])
        catab_by_sys[sid] = cats

    def sbp3_bucket(lt):
        g = G[lt]
        if "SBP_bac_3" not in g["pfam"]:
            return "NA"
        i = idx_of.get(lt)
        if i is None:
            return "transport-inferred"
        has_perm = has_kinase = False
        for j in range(max(0, i - SBP3_WINDOW), min(len(ordered), i + SBP3_WINDOW + 1)):
            if j == i:
                continue
            gj = ordered[j]
            if gj["contig"] != g["contig"]:
                continue
            if gj["role"] in ("permease", "ATP-binding"):
                has_perm = True
            if gj["is_sensor"]:
                has_kinase = True
        if has_kinase and not has_perm:
            return "sensory"
        if has_perm:
            return "transport"
        return "transport-inferred"

    # ---- assemble output rows (every tp gene + any discovered subunit member) ----
    out_tags = set(tp) | {m for s in systems for m in [x["locus_tag"] for x in s]}
    rows = []
    for lt in sorted(out_tags):
        if lt not in G:
            continue
        g = G[lt]
        sid = sysid_of.get(lt)
        members = sys_members.get(sid, [lt])
        mroles = [G[m]["role"] for m in members if m in G]
        complete = (("substrate-binding" in mroles) and ("permease" in mroles)
                    and ("ATP-binding" in mroles))
        size = len(members)
        role = g["role"]
        # carrier_type
        if role in ABC_SUBUNIT and complete:
            carrier = "ABC-cassette-complete"
        elif role == "substrate-binding":
            carrier = "ABC-orphan-SBP"
        elif role == "secondary-carrier":
            carrier = "secondary-carrier"
        elif role in ("permease", "ATP-binding"):
            carrier = "other-permease"
        else:
            carrier = "other"
        # substrate provisional (KO first -> confident; else product/eggNOG -> inferred)
        sub = substrate_from_text(g["ko_name"])
        if sub:
            conf, src = "confident", "KO"
        else:
            sub = substrate_from_text(g["product"]) or substrate_from_text(g["summary"])
            if sub:
                conf, src = "inferred", "product/eggNOG"
            else:
                # borrow from a system member with a substrate
                borrowed = None
                for m in members:
                    b = substrate_from_text(G[m]["ko_name"]) if m in G else None
                    if b:
                        borrowed = b
                        break
                if borrowed:
                    sub, conf, src = borrowed, "inferred", "neighbor"
                else:
                    sub, conf, src = "unresolved", "inferred", "none"
        oc = organic_class(g["ko_name"], g["product"], g["summary"], g["tcdb"])
        exp = "exporter" if EXPORT.search(
            f"{g['ko_name']} {g['product']} {g['summary']}".lower()) else "importer"
        rows.append(dict(
            organism_name=org, locus_tag=lt, system_id=sid, system_size=size,
            carrier_type=carrier, role_from_pfam=role, pfam_domains=g["pfam"],
            gene_summary=g["summary"], kegg_ko_id=g["ko_id"], tcdb_family=g["tcdb"],
            substrate_provisional=sub, substrate_confidence=conf, substrate_source=src,
            organic_c_vs_inorganic=oc, importer_vs_exporter=exp,
            sbp_bac3_bucket=sbp3_bucket(lt),
            catabolic_neighbors="|".join(catab_by_sys.get(sid, [])),
        ))
    df = pd.DataFrame(rows)
    cols = ["organism_name", "locus_tag", "system_id", "system_size", "carrier_type",
            "role_from_pfam", "pfam_domains", "gene_summary", "kegg_ko_id", "tcdb_family",
            "substrate_provisional", "substrate_confidence", "substrate_source",
            "organic_c_vs_inorganic", "importer_vs_exporter", "sbp_bac3_bucket",
            "catabolic_neighbors"]
    df[cols].to_csv(OUT, mode="w" if write_header else "a", header=write_header, index=False)
    print(f"{org}: {len(df)} gene-rows, {df.system_id.nunique()} systems -> appended")
    return df[cols]


def main():
    tg = pd.read_csv(TG)
    dfs = []
    first = True
    with GraphConnection() as conn:
        for org, prefix in STRAINS.items():
            dfs.append(build_strain(org, prefix, tg, conn, write_header=first))
            first = False

    full = pd.concat(dfs, ignore_index=True)

    # ---- QC summary ----
    qc_rows = []
    for org in STRAINS:
        d = full[full.organism_name == org]
        sysdf = d.drop_duplicates("system_id")
        sys_sizes = d.groupby("system_id").size()
        rec = {"organism_name": org,
               "total_gene_rows": len(d),
               "total_systems": d.system_id.nunique(),
               "single_gene_systems": int((sys_sizes == 1).sum()),
               "multi_subunit_systems": int((sys_sizes > 1).sum())}
        for ct, c in d.drop_duplicates("locus_tag").carrier_type.value_counts().items():
            rec[f"carrier__{ct}"] = int(c)
        for oc, c in d.organic_c_vs_inorganic.value_counts().items():
            rec[f"organicC__{oc}"] = int(c)
        for cf, c in d.substrate_confidence.value_counts().items():
            rec[f"conf__{cf}"] = int(c)
        for bk, c in d[d.sbp_bac3_bucket != "NA"].sbp_bac3_bucket.value_counts().items():
            rec[f"sbp3__{bk}"] = int(c)
        arom = d[d.gene_summary.fillna("").str.contains("benzoate|aromatic|naphthalene|xylene|toluene", case=False)
                 | d.substrate_provisional.fillna("").str.contains("benzoate|aromatic", case=False)]
        rec["aromatic_importer_genes"] = int(len(arom))
        qc_rows.append(rec)
    qc = pd.DataFrame(qc_rows).fillna(0)
    qc.to_csv(QC, index=False)
    print(f"\nwrote {QC}")
    # compact print
    for rec in qc_rows:
        print(f"\n### {rec['organism_name']}")
        for k, v in rec.items():
            if k != "organism_name":
                print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
