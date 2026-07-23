#!/usr/bin/env python3
"""
Methods follow-up -- consolidated rebuild (replaces 06 build + 07 curate).
One classified pipeline: enumerate transporter universe (4-source union), CLASSIFY
every gene with a reason, build systems (LOCKED grouping rule), resolve provisional
substrate, emit the organic-C candidate set. Both strains.

Baselines parts_list.csv / curated_candidates.csv are LEFT UNTOUCHED; v2 files written.

Outputs:
  data/parts_list_v2.csv   full audited table (one row per gene) + class/class_reason/in_candidate
  data/candidates_v2.csv   organic-C candidate set only
  data/qc_v2_summary.csv    class tally + candidate make-up + inorganic-control tally
  data/qc_v2_diff.csv       ADDED / REMOVED / CHANGED vs curated_candidates.csv (keep+rescue)

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/08_build_parts_list_v2.py
"""
import os
import re
import pandas as pd
from multiomics_explorer import gene_neighbors, gene_details, GraphConnection
from pfam_roles import pfam_domains, role_from_pfam
from scoring import assign_reference_class

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
TG = os.path.join(DATA, "transporter_genes.csv")
BASELINE = os.path.join(DATA, "curated_candidates.csv")
OUT_FULL = os.path.join(DATA, "parts_list_v2.csv")
OUT_CAND = os.path.join(DATA, "candidates_v2.csv")
OUT_QC = os.path.join(DATA, "qc_v2_summary.csv")
OUT_DIFF = os.path.join(DATA, "qc_v2_diff.csv")

STRAINS = {"Alteromonas macleodii HOT1A3": "ACZ81", "Alteromonas macleodii EZ55": "EZ55"}
GAP_REACH = 200
SBP3_WINDOW = 3
ABC_SUBUNIT = {"substrate-binding", "permease", "ATP-binding"}

# ---- exclude detectors (on gene_summary) ----
REGULATOR = re.compile(
    r"transcriptional regulator|dna-binding|helix-turn-helix|\bHTH\b|\bLacI\b|\bGntR\b|"
    r"\bAraC\b|\bTetR\b|\bIclR\b|\bDeoR\b|\bMarR\b|\bLysR\b|transcription factor|"
    r"repressor|antiterminator|sigma factor|anti-sigma", re.I)
ENZYME = re.compile(
    r"dehydrogenase|synthetase|synthase|cyclase|\btransferase|\bkinase\b|phosphatase|"
    r"hydrolase|\blyase|reductase|oxidase|isomerase|mutase|carboxylase|dioxygenase|"
    r"deaminase|aldolase|hydratase|epimerase|racemase|decarboxylase|aminotransferase|"
    r"\bnuclease|peptidase|glutathione s-transferase|adenosyltransferase|pyrophosphatase|"
    r"methyltransferase|amidase|ligase|oxidoreductase|dehydratase", re.I)
EXPORTER = re.compile(
    r"efflux|\bexport|exporter|multidrug|\bmsbA\b|\baraJ\b|sugar efflux|extrusion|"
    r"secretion|drug resistance|resistance protein|\bRND\b|toxin|colicin|"
    r"lipoprotein-releasing|o-antigen|capsul|lipid a export|bacteriocin|\bazlC\b|"
    r"\bazlD\b|AzlC family|AzlD|\bygaZ\b|\bygaH\b|azaleucine", re.I)
MACHINERY = re.compile(
    r"translocase|\btat[ABC]?\b|twin-arginine|preprotein|\bsec[DYEFG]\b|\bmla[A-E]?\b|"
    r"ttg2|lipid asymmetry|mechanosensitive|\bmsc[LS]\b|signal peptidase|\bptsN\b|"
    r"\bptsP\b|nitrogen regulatory|\bpts\b.*regulat|cell division|\bftsX\b|\bftsE\b|"
    r"competence|conjug|pilus|flagell|sensor histidine kinase|two-component|murein|"
    r"\bMurJ\b|flippase|peptidoglycan|lipid II|\bmotX\b|\bmotY\b|flagellar motor", re.I)
# secondary carriers resolved to drug/vitamin/efflux -> exclude (DMT direction rule)
DRUG_VITAMIN = re.compile(
    r"\bDME\b|drug/metabolite|drug metabolite|\bbiotin\b|riboflavin|thiamine|folate|"
    r"\bvitamin|threonine.*efflux|homoserine|\brhtA\b|\bywfM\b|\brarD\b|\byigM\b|"
    r"\bsugE\b|chloramphenicol|quaternary ammonium|arsenite|tellurite", re.I)

FAMILY_PATTERNS = [
    ("BCCT", r"\bBCCT\b|betaine/carnitine/choline|glycine betaine|carnitine|"
             r"choline transport|\bcudT\b|\bbetT\b|\bopuD\b|proline/betaine"),
    ("POT", r"\bPOT family\b|\bPTR family\b|proton-dependent oligopeptide|\bdtpT\b|"
            r"peptide:h|di-/tripeptide|oligopeptide:h"),
    ("SSS", r"sodium/solute symporter|\bSSS family\b|sodium:solute|na\+?/solute|"
            r"solute:sodium|\bsglT\b|sodium/glucose|sodium/proline|sodium.*symporter"),
    ("TRAP", r"\bTRAP\b|tripartite atp-independent|c4-dicarboxylate|\bdctP\b|\bdctQ\b|"
             r"\bdctM\b|dctPQM|trap-type"),
    ("NCS-nucleobase", r"\bNCS1\b|\bNCS2\b|nucleobase|xanthine|uracil|allantoin|\bxanQ\b|"
                       r"\bybbW\b|\byjcD\b|cytosine.*permease|hydroxymethylpyrimidine"),
    ("nucleoside-Nup", r"nucleoside|\bNupC\b|\bNupG\b|concentrative nucleoside|"
                       r"equilibrative nucleoside|purine.*permease|pyrimidine.*permease"),
    ("MFS-sugar", r"sugar porter|sugar:h\+|\bLacY\b|MFS transporter, SP family|"
                  r"glucose/galactose|xylose:h|sugar transporter|sugar/proton|"
                  r"arabinose.*permease|hexose|carbohydrate porin|"
                  r"carbohydrate-selective porin|\bOprB\b|fucose permease|melibiose"),
    ("APC", r"\bAPC\b|amino acid permease|amino-acid transporter|amino acid:polyamine|"
            r"amino acid transporter|aromatic amino acid transport|amino acid carrier|"
            r"glutamate.*permease|serine/threonine|amino acid ABC transporter|"
            r"amino acid.*substrate-binding|amino-acid.*substrate-binding|amino acid transport"),
    ("gluconate/organic-acid",
     r"gluconate|\bgntP\b|\bgntT\b|l-lactate|\blldP\b|lactate permease|malate|"
     r"citrate.*transport|alpha-ketoglutarate|2-oxoglutarate|tartrate|acetate.*transport|"
     r"\bactP\b|short-chain fatty acid|\batoE\b|carboxylate transport"),
    ("SLC13-dicarboxylate", r"\bSLC13\b|di- and tricarboxylate|dicarboxylate|tricarboxylate|"
                            r"C4-dicarboxylate"),
    ("glycerol/glp", r"glycerol|\bglpT\b|\bglpF\b|\bugpA?\b|sn-glycerol|glycerophospho"),
    ("fatty-acid", r"\bfadL\b|OmpP1/FadL|long-chain fatty acid|fatty acid transport"),
    ("phenylpropionate-hcaT", r"phenylpropion|\bhcaT\b|3-phenylpropionic"),
]
ORGANIC_FAMS = {k for k, _ in FAMILY_PATTERNS}

INORGANIC = re.compile(
    r"iron|ferric|ferrous|fe\(iii\)|fe3|zinc|manganese|molybdate|tungstate|sulfate|"
    r"sulfite|phosphate|phosphonate|phosphite|nitrate|nitrite|bicarbonate|cyanate|"
    r"potassium|sodium|calcium|magnesium|cobalt|nickel|copper|chloride|ammoni|\bmetal\b|"
    r"heme|siderophore|cobalamin|thiamin|vitamin|biotin|riboflavin|selenat|arsen|"
    r"chromate|fluoride|silica", re.I)
DUAL_CN = re.compile(
    r"amino acid|peptide|oligopeptide|dipeptide|glutamine|glutamate|arginine|histidine|"
    r"lysine|ornithine|cystine|methionine|proline|leucine|isoleucine|valine|"
    r"branched-chain|polar amino|nucleoside|nucleobase|purine|pyrimidine|xanthine|uracil|"
    r"spermidine|putrescine|polyamine|betaine|choline|taurine|urea|glutathione|opine|"
    r"ectoine|creatine|carnitine|sarcosine", re.I)
ORGANIC_C = re.compile(
    r"sugar|maltose|maltodextrin|glucose|fructose|ribose|arabinose|xylose|rhamnose|"
    r"galactose|trehalose|lactose|mannose|monosaccharide|polyol|glycerol|sorbitol|"
    r"mannitol|inositol|carbohydrate|gluconate|glucuronate|lactate|citrate|malate|"
    r"succinate|fumarate|alpha-ketoglutarate|pyruvate|acetate|benzoate|carboxylate|"
    r"organic acid|fatty acid|lipid|glycolate|dicarboxylate|tartrate|phenylpropion|fucose", re.I)
EXPORT_DIR = re.compile(
    r"efflux|\bexport|exporter|multidrug|extrusion|resistance|drug/metabolite|\bDME\b", re.I)
# surface / secreted polymers -- these are EXPORT/biogenesis substrates, never
# carbon uptake, and their ABC ATPase/permease subunits carry generic names.
NONUPTAKE = re.compile(
    r"capsular|capsule|lipopolysaccharide|\bLPS\b|o-antigen|o antigen|exopolysaccharide|"
    r"teichoic|lipid a export|colanic|surface polysaccharide|polysaccharide export|"
    r"\bwza\b|\bkps[A-Z]\b|lipooligosaccharide", re.I)
CATAB_RE = re.compile(
    r"dehydrogenase|oxidase|reductase|hydrolase|synthase|synthetase|lyase|aldolase|"
    r"decarboxylase|hydratase|isomerase|deaminase|peptidase|hydroxylase|dioxygenase|"
    r"monooxygenase|esterase|amidase|racemase|epimerase|thiolase|carboxylase|mutase|"
    r"oxidoreductase|aminotransferase|dehydratase|kinase|transaldolase|transketolase|"
    r"cyclase|glycosyltransferase", re.I)


def famset(tcdb):
    return set(re.findall(r"3\.A\.1\.\d+", str(tcdb)))


def substrate_from_text(text):
    if not text or str(text) == "nan":
        return None
    for part in str(text).split(" ; "):
        p = part.split(";", 1)[1].strip() if ";" in part else part.strip()
        seg = re.split(r"\btransport system\b|\btransporter\b|\btransport\b|\bpermease\b|"
                       r"\buptake\b|\bABC\b|\bsubstrate-binding\b|\breceptor\b|"
                       r"\bsymporter\b|\bantiporter\b|\bfacilitator\b", p, maxsplit=1)
        cand = seg[0].strip(" ,-")
        if cand and not re.search(r"putative|multidrug|^drug$|hypothetical|uncharacter|"
                                  r"^ABC$|^MFS$|domain-containing|family protein|"
                                  r"^ATP-binding", cand, re.I) and len(cand) > 2:
            return cand
    return None


# iron-chelate / siderophore uptake reads inorganic even though the chelator
# (citrate, catecholate) is organic -- the transported cargo is Fe.
FERRIC = re.compile(
    r"ferric|fe\(3\+?\)|fe3\+|fe\(iii\)|iron\(iii\)|iron complex|siderophore|"
    r"dicitrate|ferrichrome|enterobactin|catecholate|hydroxamate|ferrioxamine|"
    r"iron.*citrate|\bfhu|\bfec[A-E]\b|\bfep[A-G]\b", re.I)


def organic_class(*texts):
    t = " ".join(str(x) for x in texts if x and str(x) != "nan").lower()
    if not t.strip():
        return "ambiguous"
    if FERRIC.search(t):
        return "inorganic"
    if DUAL_CN.search(t):
        return "dual-C+N"
    if ORGANIC_C.search(t):
        return "organic-C"
    if INORGANIC.search(t):
        return "inorganic"
    return "ambiguous"


def organic_family(text):
    for fam, pat in FAMILY_PATTERNS:
        if re.search(pat, text, re.I):
            return fam
    return None


# soluble PTS phosphocarriers/regulators (EIIA/EIIB/HPr/EI, crr K02777) -- cytoplasmic,
# NOT membrane importers. The membrane EIIC permease is the actual importer and is KEPT.
PTS_SOLUBLE = re.compile(
    r"phosphocarrier|\bHPr\b|phosphoenolpyruvate-protein phosphotransferase|\benzyme I\b|"
    r"\bcrr\b|\bEIIA\b|\bEIIB\b|(?:pts|phosphotransferase)[^.]{0,50}(?:IIA|IIB|component ii[ab])|"
    r"\bK02777\b|component IIA|component IIB|subunit IIA|subunit IIB", re.I)
PTS_EIIC = re.compile(r"\bIIC\b|\bEIIC\b|enzyme IIC|component IIC|membrane|permease", re.I)
# carbohydrate-selective outer-membrane porins (TCDB 1.B.x, OprB/rpfN) -- non-specific
# sugar entry, not a substrate-specific carrier.
CARB_PORIN = re.compile(r"carbohydrate porin|carbohydrate-selective porin|\bOprB\b|\brpfN\b", re.I)


def classify(g):
    """Return (cls, reason, carrier_family)."""
    gs = str(g["summary"] or "")
    role = g["role"]
    text = f"{gs} {g['ko_name']} {g.get('ko_id', '')}"
    fam = organic_family(f"{gs} {g['pfam']} {g['ko_name']}")

    # ---- EXCLUDE classes (surfaced, not dropped) ----
    if REGULATOR.search(gs):
        return "regulator", "DNA-binding/transcriptional regulator (SBP-fold mis-tag)", fam or "regulator"
    if role != "ATP-binding" and ENZYME.search(gs):
        return "enzyme", "metabolic enzyme (not a transporter)", fam or "enzyme"
    if PTS_SOLUBLE.search(text) and not PTS_EIIC.search(text):
        return "machinery", "PTS soluble phosphocarrier/regulator, not a membrane importer", "PTS-soluble"
    if MACHINERY.search(gs):
        return "machinery", "non-metabolite-uptake machinery", fam or "machinery"
    if g["importer_vs_exporter"] == "exporter" or EXPORTER.search(gs):
        return "exporter", "efflux/export", fam or "exporter"
    if g["sbp3_bucket"] == "sensory":
        return "sensory", "SBP_bac_3 adjacent to two-component kinase, no permease near", "SBP_bac_3-sensory"

    # ---- genuine transporter ----
    if role in ABC_SUBUNIT:
        return "transport-role", f"ABC {role} (Pfam)", fam or "ABC-subunit"

    if role == "secondary-carrier":
        # DMT/EamA direction rule
        if DRUG_VITAMIN.search(gs) or EXPORT_DIR.search(gs):
            return "exporter", "secondary carrier resolved to drug/vitamin/efflux", fam or "exporter"
        if fam:
            return "carrier-family", f"recognized secondary carrier family {fam}", fam
        resolved = substrate_from_text(g["ko_name"]) or substrate_from_text(gs)
        if resolved:
            oc = organic_class(g["ko_name"], gs)
            if oc in ("organic-C", "dual-C+N"):
                return "carrier-family", f"resolved carbon-import secondary carrier ({resolved})", "secondary-carrier-organic"
            return "carrier-family", f"resolved inorganic secondary carrier ({resolved})", "secondary-carrier-inorganic"
        return "secondary-carrier-unresolved", "bare MFS/DMT/EamA, no KO/TCDB substrate", "secondary-carrier-unresolved"

    # non-ABC, non-secondary transport gene (TonB receptor, TRAP permease, porin, ...)
    if CARB_PORIN.search(gs) or re.search(r"1\.B\.", str(g["tcdb"])) and re.search(
            r"carbohydrate|sugar", gs, re.I):
        return "carrier-family", "carbohydrate-selective porin (non-specific sugar entry)", "carbohydrate-porin"
    if fam:
        return "carrier-family", f"recognized carrier family {fam}", fam
    return "other", "unclassified transporter (e.g. TonB receptor / porin / RND subunit)", "other"


def build_strain(org, prefix, tg, conn, write_header):
    h = tg[tg.organism_name == org].copy()
    tp = h.locus_tag.tolist()
    ko_name = dict(zip(h.locus_tag, h.kegg_ko_name.fillna("")))
    ko_id = dict(zip(h.locus_tag, h.kegg_ko_id.fillna("")))
    tcdb_map = dict(zip(h.locus_tag, h.tcdb_family.fillna("")))

    nb = gene_neighbors(locus_tags=tp, window=4, limit=None, conn=conn)
    neigh = {r["neighbor_locus_tag"] for r in nb.get("results", [])}
    det = gene_details(locus_tags=sorted(set(tp) | neigh), limit=None, conn=conn)

    G = {}
    for r in det.get("results", []):
        lt = r["locus_tag"]
        pf = pfam_domains(r.get("alternate_functional_descriptions") or [])
        prod = r.get("product")
        role = role_from_pfam(pf)
        G[lt] = dict(
            locus_tag=lt, contig=r.get("contig"), start=r.get("start"), end=r.get("end"),
            strand=r.get("strand"), role=role, pfam=" ; ".join(pf),
            summary=r.get("gene_summary"), product=prod, ko_id=ko_id.get(lt, ""),
            ko_name=ko_name.get(lt, ""), tcdb=tcdb_map.get(lt, ""),
            is_sensor=(role == "sensor-kinase-EXCLUDE"),
            is_catab=(role == "other/unclear" and prod is not None
                      and bool(CATAB_RE.search(prod))),
            in_tp=(lt in set(tp)),
        )

    ordered = sorted([g for g in G.values() if g["start"] is not None],
                     key=lambda x: (x["contig"], x["start"]))
    idx_of = {g["locus_tag"]: i for i, g in enumerate(ordered)}

    # LOCKED grouping over ABC subunit genes
    subunits = [g for g in ordered if g["role"] in ABC_SUBUNIT]
    systems, cur = [], []
    for g in subunits:
        if not cur:
            cur = [g]; continue
        last = cur[-1]
        gap = g["start"] - last["end"]
        same = g["contig"] == last["contig"] and g["strand"] == last["strand"]
        sysfam = set().union(*[famset(m["tcdb"]) for m in cur]) if cur else set()
        gf = famset(g["tcdb"])
        clash = bool(gf) and bool(sysfam) and gf.isdisjoint(sysfam)
        if same and gap <= GAP_REACH and not clash:
            cur.append(g)
        else:
            systems.append(cur); cur = [g]
    if cur:
        systems.append(cur)

    sysid_of, sys_members, n = {}, {}, 0
    for s in systems:
        n += 1
        sid = f"{prefix}_S{n:04d}"
        for m in s:
            sysid_of[m["locus_tag"]] = sid
        sys_members[sid] = [m["locus_tag"] for m in s]
    for lt in tp:
        if lt in sysid_of:
            continue
        n += 1
        sid = f"{prefix}_S{n:04d}"
        sysid_of[lt] = sid
        sys_members[sid] = [lt]

    catab_by_sys = {}
    for sid, members in sys_members.items():
        mrows = [G[m] for m in members if m in G and G[m]["start"] is not None]
        if not mrows:
            catab_by_sys[sid] = []; continue
        i0 = min(idx_of[m["locus_tag"]] for m in mrows)
        i1 = max(idx_of[m["locus_tag"]] for m in mrows)
        contig = mrows[0]["contig"]
        catab_by_sys[sid] = [ordered[j]["locus_tag"] for j in range(max(0, i0 - 1),
                             min(len(ordered), i1 + 2))
                             if ordered[j]["contig"] == contig and ordered[j]["is_catab"]
                             and ordered[j]["locus_tag"] not in members]

    def sbp3_bucket(lt):
        g = G[lt]
        if "SBP_bac_3" not in g["pfam"]:
            return "NA"
        i = idx_of.get(lt)
        if i is None:
            return "transport-inferred"
        has_perm = has_kin = False
        for j in range(max(0, i - SBP3_WINDOW), min(len(ordered), i + SBP3_WINDOW + 1)):
            if j == i or ordered[j]["contig"] != g["contig"]:
                continue
            if ordered[j]["role"] in ("permease", "ATP-binding"):
                has_perm = True
            if ordered[j]["is_sensor"]:
                has_kin = True
        return "sensory" if (has_kin and not has_perm) else ("transport" if has_perm else "transport-inferred")

    # system-level exporter propagation, MEMBER-ONLY: an ABC EXPORT cassette whose
    # export/surface-polymer label sits on a SIBLING SUBUNIT of the same walked
    # system (not on an unrelated genomic neighbor -- flank scanning proved fragile,
    # spuriously matching adjacent enzymes like 'lipid A deacylase'). Per-gene
    # EXPORTER/NONUPTAKE guards (below) catch the remaining export ATPases via their
    # own borrowed substrate (e.g. 'capsular polysaccharide').
    sys_exporter = set()
    for sid, members in sys_members.items():
        if len(members) < 2:
            continue
        if any(m in G and (EXPORTER.search(str(G[m]["summary"] or ""))
                           or NONUPTAKE.search(str(G[m]["summary"] or "")))
               for m in members):
            sys_exporter.add(sid)

    out_tags = set(tp) | {x["locus_tag"] for s in systems for x in s}
    rows = []
    for lt in sorted(out_tags):
        if lt not in G:
            continue
        g = G[lt]
        g["importer_vs_exporter"] = "exporter" if EXPORT_DIR.search(
            f"{g['ko_name']} {g['summary']}".lower()) else "importer"
        g["sbp3_bucket"] = sbp3_bucket(lt)
        sid = sysid_of.get(lt)
        members = sys_members.get(sid, [lt])
        mroles = [G[m]["role"] for m in members if m in G]
        complete = all(r in mroles for r in ABC_SUBUNIT)
        # substrate (KO -> confident; else product/eggnog -> inferred; else borrow)
        sub = substrate_from_text(g["ko_name"])
        if sub:
            conf, src = "confident", "KO"
        else:
            sub = substrate_from_text(g["product"]) or substrate_from_text(g["summary"])
            if sub:
                conf, src = "inferred", "product/eggNOG"
            else:
                borrowed = next((substrate_from_text(G[m]["ko_name"]) for m in members
                                 if m in G and substrate_from_text(G[m]["ko_name"])), None)
                sub, conf, src = (borrowed, "inferred", "neighbor") if borrowed else \
                                 ("unresolved", "inferred", "none")
        oc = organic_class(g["ko_name"], g["product"], g["summary"], g["tcdb"])
        cls, reason, cfam = classify(g)
        gs_l = str(g["summary"] or "").lower()
        # Fix 2: carbohydrate porins are non-specific -> confidence inferred
        if cfam == "carbohydrate-porin":
            conf = "inferred"
            sub = "carbohydrate (non-specific porin)"
            src = "TCDB-porin"
        # Fix 3: peptide/nickel (nikA/B) identity unresolved -> demote to inferred
        if sub and "nickel" in str(sub).lower() and oc == "dual-C+N":
            conf = "inferred"
        if "antimicrobial peptide" in gs_l:
            src = (src + "|antimicrobial-peptide") if src else "antimicrobial-peptide"
        nonuptake = bool(NONUPTAKE.search(f"{g['summary']} {sub} {g['ko_name']}"))
        in_cand = (cls in ("transport-role", "carrier-family")
                   and oc in ("organic-C", "dual-C+N")
                   and g["importer_vs_exporter"] == "importer"
                   and sid not in sys_exporter
                   and not nonuptake)
        if sid in sys_exporter and cls in ("transport-role", "carrier-family"):
            reason = reason + " [system has an export-annotated subunit -> excluded]"
        is_inorg_control = (oc == "inorganic" and cls in ("transport-role", "carrier-family")
                            and g["importer_vs_exporter"] == "importer" and sid not in sys_exporter)
        rows.append(dict(
            organism_name=org, locus_tag=lt, system_id=sid, system_size=len(members),
            class_=cls, class_reason=reason, carrier_family=cfam,
            carrier_type_abc=("ABC-cassette-complete" if (g["role"] in ABC_SUBUNIT and complete)
                              else ("ABC-orphan-SBP" if g["role"] == "substrate-binding" else "")),
            role_from_pfam=g["role"], pfam_domains=g["pfam"], gene_summary=g["summary"],
            kegg_ko_id=g["ko_id"], tcdb_family=g["tcdb"], substrate_provisional=sub,
            substrate_confidence=conf, substrate_source=src, organic_c_vs_inorganic=oc,
            importer_vs_exporter=g["importer_vs_exporter"], sbp_bac3_bucket=g["sbp3_bucket"],
            catabolic_neighbors="|".join(catab_by_sys.get(sid, [])),
            control_confident=("" if not is_inorg_control
                               else ("confident" if conf == "confident" else "inferred")),
            in_candidate=in_cand,
            reference_class=assign_reference_class(dict(
                locus_tag=lt, class_=cls, gene_summary=g["summary"],
                organic_c_vs_inorganic=oc, importer_vs_exporter=g["importer_vs_exporter"],
                in_candidate=in_cand)),
        ))
    df = pd.DataFrame(rows)
    df.to_csv(OUT_FULL, mode="w" if write_header else "a", header=write_header, index=False)
    print(f"{org}: {len(df)} rows, {df.system_id.nunique()} systems, "
          f"{int(df.in_candidate.sum())} candidate genes -> appended")
    return df


def main():
    tg = pd.read_csv(TG)
    dfs, first = [], True
    with GraphConnection() as conn:
        for org, prefix in STRAINS.items():
            dfs.append(build_strain(org, prefix, tg, conn, write_header=first))
            first = False
    full = pd.concat(dfs, ignore_index=True)

    cand = full[full.in_candidate].copy()
    cand.to_csv(OUT_CAND, index=False)
    print(f"\nwrote {OUT_CAND}: {len(cand)} candidate genes")

    # QC summary
    qc_rows = []
    for org in STRAINS:
        d = full[full.organism_name == org]
        c = d[d.in_candidate]
        rec = {"organism_name": org, "total_rows": len(d), "candidate_genes": len(c),
               "candidate_systems": c.system_id.nunique(),
               "cand_single": int((c.system_size == 1).sum()),
               "cand_multi": int((c.system_size > 1).sum()),
               "cand_confident": int((c.substrate_confidence == "confident").sum()),
               "cand_inferred": int((c.substrate_confidence == "inferred").sum())}
        for cl, n in d.class_.value_counts().items():
            rec[f"class__{cl}"] = int(n)
        for fam, n in c.carrier_family.value_counts().items():
            rec[f"candfam__{fam}"] = int(n)
        inorg = d[d.control_confident != ""]
        rec["inorg_confident"] = int((inorg.control_confident == "confident").sum())
        rec["inorg_inferred"] = int((inorg.control_confident == "inferred").sum())
        qc_rows.append(rec)
    pd.DataFrame(qc_rows).fillna(0).to_csv(OUT_QC, index=False)
    print(f"wrote {OUT_QC}")

    # ---- DIFF vs baseline (curated_candidates keep+rescue) ----
    base = pd.read_csv(BASELINE)
    base_keep = base[base.curation.isin(["keep", "rescue"])].copy()
    base_genes = dict(zip(base_keep.locus_tag,
                          zip(base_keep.substrate_provisional.fillna(""),
                              base_keep.carrier_family.fillna(""),
                              base_keep.system_id)))
    v2_genes = dict(zip(cand.locus_tag, zip(cand.substrate_provisional.fillna(""),
                                            cand.carrier_family.fillna(""), cand.system_id,
                                            cand.organism_name)))
    diff = []
    for lt, (sub, fam, sid, org) in v2_genes.items():
        if lt not in base_genes:
            diff.append(dict(change="ADDED", organism_name=org, locus_tag=lt, system_id=sid,
                             carrier_family=fam, substrate=sub, baseline_family="", baseline_substrate=""))
    for lt, (bsub, bfam, bsid) in base_genes.items():
        if lt not in v2_genes:
            org = base_keep[base_keep.locus_tag == lt].organism_name.iloc[0]
            diff.append(dict(change="REMOVED", organism_name=org, locus_tag=lt, system_id=bsid,
                             carrier_family="", substrate="", baseline_family=bfam, baseline_substrate=bsub))
        else:
            sub, fam, sid, org = v2_genes[lt]
            if sub != bsub or fam != bfam:
                diff.append(dict(change="CHANGED", organism_name=org, locus_tag=lt, system_id=sid,
                                 carrier_family=fam, substrate=sub, baseline_family=bfam,
                                 baseline_substrate=bsub))
    dd = pd.DataFrame(diff)
    dd.to_csv(OUT_DIFF, index=False)
    print(f"wrote {OUT_DIFF}: {len(dd)} gene-level diffs")

    # compact print
    for rec in qc_rows:
        print(f"\n### {rec['organism_name']}")
        print("  classes:", {k.replace('class__', ''): v for k, v in rec.items() if k.startswith('class__')})
        print(f"  candidate systems={rec['candidate_systems']} genes={rec['candidate_genes']} "
              f"(single={rec['cand_single']} multi={rec['cand_multi']}; "
              f"confident={rec['cand_confident']} inferred={rec['cand_inferred']})")
        print("  candidate families:", {k.replace('candfam__', ''): v for k, v in rec.items() if k.startswith('candfam__')})
        print(f"  inorganic control: confident={rec['inorg_confident']} inferred={rec['inorg_inferred']}")
    if len(dd):
        print("\n=== DIFF vs baseline (candidate systems) ===")
        for ch in ["ADDED", "REMOVED", "CHANGED"]:
            sub = dd[dd.change == ch]
            print(f"  {ch}: {len(sub)} genes / {sub.system_id.nunique()} systems")


if __name__ == "__main__":
    main()
