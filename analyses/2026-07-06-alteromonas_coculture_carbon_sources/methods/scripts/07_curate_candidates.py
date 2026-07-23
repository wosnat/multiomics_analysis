#!/usr/bin/env python3
"""
Methods follow-up -- curation pass. Reads data/parts_list.csv (READ-ONLY) and
produces the curated organic-carbon candidate set with a reason for every
keep/rescue/drop/reconsider, plus an inorganic-control confident flag.

Writes:
  data/curated_candidates.csv     (one row per gene considered)
  data/qc_curation_summary.csv    (counts per strain)

Curation is PROVISIONAL; borderline cases are flagged 'reconsider' with a reason,
not force-decided. No carbon-source conclusions.

Run from repo root:
  .venv/bin/python analyses/2026-07-06-alteromonas_coculture_carbon_sources/methods/scripts/07_curate_candidates.py
"""
import os
import re
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
IN = os.path.join(DATA, "parts_list.csv")
OUT = os.path.join(DATA, "curated_candidates.csv")
QC = os.path.join(DATA, "qc_curation_summary.csv")

# ---- DROP detectors (on gene_summary) ----
REGULATOR = re.compile(
    r"transcriptional regulator|dna-binding|helix-turn-helix|\bHTH\b|"
    r"\bLacI\b|\bGntR\b|\bAraC\b|\bTetR\b|\bIclR\b|\bDeoR\b|\bMarR\b|\bLysR\b|"
    r"transcription factor|repressor|antiterminator|sigma factor|anti-sigma", re.I)
ENZYME = re.compile(
    r"dehydrogenase|synthetase|synthase|cyclase|\btransferase|\bkinase\b|phosphatase|"
    r"hydrolase|\blyase|reductase|oxidase|isomerase|mutase|carboxylase|dioxygenase|"
    r"deaminase|aldolase|hydratase|epimerase|racemase|decarboxylase|aminotransferase|"
    r"\bnuclease|peptidase|glutathione s-transferase|adenosyltransferase|"
    r"pyrophosphatase|methyltransferase|amidase|ligase|oxidoreductase|dehydratase", re.I)
EXPORTER = re.compile(
    r"efflux|\bexport|exporter|multidrug|\bmsbA\b|\baraJ\b|sugar efflux|extrusion|"
    r"secretion|drug resistance|resistance protein|\bRND\b|toxin|colicin|"
    r"lipoprotein-releasing|o-antigen|capsul|lipid a export|bacteriocin|"
    r"\bazlC\b|\bazlD\b|AzlC family|AzlD|\bygaZ\b|\bygaH\b|azaleucine", re.I)
MACHINERY = re.compile(
    r"translocase|\btat[ABC]?\b|twin-arginine|preprotein|\bsec[DYEFG]\b|"
    r"\bmla[A-E]?\b|ttg2|lipid asymmetry|mechanosensitive|\bmsc[LS]\b|"
    r"signal peptidase|\bptsN\b|\bptsP\b|nitrogen regulatory|\bpts\b.*regulat|"
    r"cell division|\bftsX\b|\bftsE\b|competence|conjug|pilus|flagell|"
    r"sensor histidine kinase|two-component|murein|\bMurJ\b|flippase|"
    r"peptidoglycan|lipid II|\bmotX\b|\bmotY\b|flagellar motor", re.I)

# ---- carrier-family detectors (on gene_summary + pfam + substrate) ----
FAMILY_PATTERNS = [
    ("BCCT", r"\bBCCT\b|betaine/carnitine/choline|glycine betaine|carnitine|"
             r"choline transport|\bcudT\b|\bbetT\b|\bopuD\b|proline/betaine"),
    ("POT", r"\bPOT family\b|\bPTR family\b|proton-dependent oligopeptide|"
            r"\bdtpT\b|peptide:h|di-/tripeptide|oligopeptide:h"),
    ("SSS", r"sodium/solute symporter|\bSSS family\b|sodium:solute|na\+?/solute|"
            r"solute:sodium|\bsglT\b|sodium/glucose|sodium/proline|sodium.*symporter"),
    ("MFS-sugar", r"sugar porter|sugar:h\+|\bLacY\b|MFS transporter, SP family|"
                  r"glucose/galactose|xylose:h|sugar transporter|sugar/proton|"
                  r"arabinose.*permease|hexose|carbohydrate porin|"
                  r"carbohydrate-selective porin|\bOprB\b|fucose permease|melibiose"),
    ("APC", r"\bAPC\b|amino acid permease|amino-acid transporter|amino acid:polyamine|"
            r"amino acid transporter|aromatic amino acid transport|"
            r"amino acid carrier|glutamate.*permease|serine/threonine|"
            r"amino acid ABC transporter|amino acid.*substrate-binding|"
            r"amino-acid.*substrate-binding|amino acid transport"),
    ("TRAP", r"\bTRAP\b|tripartite atp-independent|c4-dicarboxylate|\bdctP\b|\bdctQ\b|"
             r"\bdctM\b|dctPQM|trap-type|dctp/dctq"),
    ("nucleoside/nucleobase",
     r"nucleoside|\bNupC\b|\bNupG\b|purine.*permease|pyrimidine.*permease|"
     r"xanthine|uracil|cytosine.*permease|\bNCS1\b|\bNCS2\b|nucleobase|"
     r"allantoin|\bxanQ\b|\bybbW\b|\byjcD\b|hydroxymethylpyrimidine"),
    ("glycerol/glp", r"glycerol|\bglpT\b|\bglpF\b|\bugpA?\b|sn-glycerol|glycerophospho"),
    ("gluconate/organic-acid",
     r"gluconate|\bgntP\b|\bgntT\b|l-lactate|\blldP\b|lactate permease|malate|"
     r"citrate.*transport|alpha-ketoglutarate|dicarboxylate|di- and tricarboxylate|"
     r"tricarboxylate|hydroxy.*acid.*transport|tartrate|2-oxoglutarate|"
     r"acetate.*transport|\bactP\b|short-chain fatty acid|\batoE\b|fatty acid|"
     r"\bfadL\b|OmpP1/FadL|\bSLC13\b|carboxylate transport"),
]
RESCUE_FAMS = {"BCCT", "POT", "SSS", "MFS-sugar", "APC", "TRAP", "nucleoside/nucleobase",
               "glycerol/glp", "gluconate/organic-acid"}


def carrier_family(row):
    txt = f"{row.get('gene_summary','')} {row.get('pfam_domains','')} " \
          f"{row.get('substrate_provisional','')}".lower()
    for fam, pat in FAMILY_PATTERNS:
        if re.search(pat, txt, re.I):
            return fam
    ct = row.get("carrier_type", "")
    if ct == "ABC-cassette-complete":
        sub = str(row.get("substrate_provisional", "")).lower()
        if "peptide" in sub or "nickel" in sub:
            return "ABC-peptide"
        return "ABC-cassette-other"
    if ct == "ABC-orphan-SBP":
        return "ABC-orphan-SBP"
    if ct == "secondary-carrier":
        return "secondary-carrier"
    if ct in ("other-permease",):
        return "other-permease"
    return "other"


def curate(row):
    """Return (curation, reason, control_confident)."""
    gs = str(row.get("gene_summary", "") or "")
    role = row.get("role_from_pfam", "")
    oc = row.get("organic_c_vs_inorganic", "")
    imp = row.get("importer_vs_exporter", "")
    ct = row.get("carrier_type", "")
    fam = row["carrier_family"]
    conf = row.get("substrate_confidence", "")
    ctrl = ""

    # ---- DROP filters (order matters) ----
    if REGULATOR.search(gs):
        return "drop", "transcriptional-regulator (SBP-fold mis-tag)", ctrl
    if role != "ATP-binding" and ENZYME.search(gs):
        return "drop", "metabolic-enzyme (not a transporter)", ctrl
    if imp == "exporter" or EXPORTER.search(gs):
        return "drop", "exporter/efflux", ctrl
    if MACHINERY.search(gs):
        return "drop", "non-metabolite-uptake machinery", ctrl
    if row.get("sbp_bac3_bucket") == "sensory":
        return "drop", "SBP_bac_3 sensory (two-component, not uptake)", ctrl

    # ---- inorganic control set ----
    if oc == "inorganic":
        ctrl = "confident" if conf == "confident" else "inferred"
        return "drop", "inorganic (control set; see control_confident)", ctrl

    organic = oc in ("organic-C", "dual-C+N")

    # ---- KEEP: clean organic carriers ----
    if organic and ct in ("ABC-cassette-complete", "ABC-orphan-SBP", "secondary-carrier"):
        return "keep", f"clean organic importer ({ct}, {oc})", ctrl

    # ---- RESCUE: organic importer from 'other' bucket via carrier family ----
    if organic and ct in ("other", "other-permease") and fam in RESCUE_FAMS:
        return "rescue", f"rescued organic carrier {fam} (no clean ABC/2.A tag, {oc})", ctrl
    if organic and ct in ("other", "other-permease"):
        return "reconsider", f"organic importer in 'other' bucket, carrier family unrecognized ({oc})", ctrl

    # ---- ambiguous substrate but plausible carrier ----
    if oc == "ambiguous":
        if fam in RESCUE_FAMS:
            return "reconsider", f"carrier {fam} but substrate class ambiguous", ctrl
        if ct == "secondary-carrier":
            return "reconsider", "secondary-carrier, substrate unresolved (uptake unclear)", ctrl
        if ct == "ABC-orphan-SBP":
            return "reconsider", "orphan SBP, substrate unresolved", ctrl
        if ct == "ABC-cassette-complete":
            return "reconsider", "complete ABC cassette, substrate unresolved", ctrl
        return "drop", "ambiguous, non-carrier / unresolved (not an organic candidate)", ctrl

    # organic but odd carrier_type fallthrough
    if organic:
        return "keep", f"organic importer ({ct}, {oc})", ctrl
    return "drop", "not an organic metabolite-uptake candidate", ctrl


def main():
    df = pd.read_csv(IN)
    df["carrier_family"] = df.apply(carrier_family, axis=1)
    res = df.apply(curate, axis=1, result_type="expand")
    df["curation"], df["curation_reason"], df["control_confident"] = res[0], res[1], res[2]

    keepcols = ["organism_name", "locus_tag", "system_id", "system_size", "carrier_type",
                "carrier_family", "role_from_pfam", "pfam_domains", "gene_summary",
                "kegg_ko_id", "tcdb_family", "substrate_provisional", "substrate_confidence",
                "substrate_source", "organic_c_vs_inorganic", "importer_vs_exporter",
                "sbp_bac3_bucket", "catabolic_neighbors", "curation", "curation_reason",
                "control_confident"]
    df[keepcols].to_csv(OUT, index=False)
    print(f"wrote {len(df)} rows -> {OUT}")

    # ---- QC summary ----
    qc_rows = []
    for org in df.organism_name.unique():
        d = df[df.organism_name == org]
        cand = d[d.curation.isin(["keep", "rescue"])]
        drops = d[d.curation == "drop"]
        rec = {"organism_name": org,
               "keep": int((d.curation == "keep").sum()),
               "rescue": int((d.curation == "rescue").sum()),
               "drop": int((d.curation == "drop").sum()),
               "reconsider": int((d.curation == "reconsider").sum()),
               "candidate_total_genes": len(cand),
               "candidate_systems": cand.system_id.nunique(),
               "cand_single_gene": int((cand.system_size == 1).sum()),
               "cand_multi_subunit": int((cand.system_size > 1).sum()),
               "cand_confident": int((cand.substrate_confidence == "confident").sum()),
               "cand_inferred": int((cand.substrate_confidence == "inferred").sum())}
        for fam, c in cand.carrier_family.value_counts().items():
            rec[f"candfam__{fam}"] = int(c)
        rec["rescued_genes"] = int((d.curation == "rescue").sum())
        for fam, c in d[d.curation == "rescue"].carrier_family.value_counts().items():
            rec[f"rescuefam__{fam}"] = int(c)
        for rsn, c in drops.curation_reason.value_counts().items():
            rec[f"drop__{rsn[:40]}"] = int(c)
        inorg = d[d.control_confident != ""]
        rec["inorg_control_confident"] = int((inorg.control_confident == "confident").sum())
        rec["inorg_control_inferred"] = int((inorg.control_confident == "inferred").sum())
        qc_rows.append(rec)
    qc = pd.DataFrame(qc_rows).fillna(0)
    qc.to_csv(QC, index=False)
    print(f"wrote {QC}\n")

    for rec in qc_rows:
        print(f"### {rec['organism_name']}")
        for k in ["keep", "rescue", "drop", "reconsider", "candidate_total_genes",
                  "candidate_systems", "cand_single_gene", "cand_multi_subunit",
                  "cand_confident", "cand_inferred", "rescued_genes",
                  "inorg_control_confident", "inorg_control_inferred"]:
            print(f"    {k}: {rec[k]}")
        print("    candidate families:", {k.replace('candfam__', ''): v
              for k, v in rec.items() if k.startswith('candfam__')})
        print("    rescue families:", {k.replace('rescuefam__', ''): v
              for k, v in rec.items() if k.startswith('rescuefam__')})
        print("    top drop reasons:", {k.replace('drop__', ''): v
              for k, v in rec.items() if k.startswith('drop__')})
        print()

    # explicit RECONSIDER list (main thread decides)
    print("==== RECONSIDER cases (locus | strain | reason | summary) ====")
    rc = df[df.curation == "reconsider"][["organism_name", "locus_tag", "carrier_family",
                                          "curation_reason", "gene_summary"]]
    print(f"total reconsider: {len(rc)}")
    for r in rc.to_dict("records"):
        gs = str(r["gene_summary"])[:60]
        print(f"  {r['locus_tag']} [{r['organism_name'].split()[-1]}] {r['carrier_family']}"
              f" | {r['curation_reason']} | {gs}")


if __name__ == "__main__":
    main()
