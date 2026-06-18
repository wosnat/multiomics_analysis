"""Shared exoenzyme classifier — used by 04 (extruded set) and 05 (full genomes)
so both runs use byte-identical logic.

Degradative-enzyme function via EC / CAZy / GO-MF / Pfam (Pfam required: PhoX etc.
carry no EC/GO term). Export evidence (signal peptide / localization) is a confidence
tier, not a gate; explicit Cytoplasmic localization flags likely contamination.

classify(genes_df, conn) -> genes_df with columns:
  substrates, func_evidence, export_evidence, is_degradative, is_cytoplasmic,
  is_exported, tier, is_exoenzyme
genes_df must have: locus_tag, strain_short.
"""

import re

import pandas as pd

from multiomics_explorer import gene_ontology_terms

EXPORT_LOCS = {"Outer membrane", "Extracellular", "Periplasmic"}

NAME_EXCLUDE = re.compile(r"inorganic|pyrophosphat|diphosphat|phosphopyruvate|"
                          r"phosphoglycerate|phosphoribosyl|phosphofructo|"
                          r"regulatory|isomerase|cis-trans|peptidyl-prolyl|"
                          r"chaperone|foldase", re.I)
NAME_SUBSTRATE = [
    (re.compile(r"peptidase|protease|proteinase|trypsin|subtilase|subtilisin|deg[pq]|"
                r"collagenase|aminopeptidase|carboxypeptidase|endopeptidase|"
                r"metallopeptidase|metalloprotease", re.I),
     "protein/peptide"),
    (re.compile(r"glyco_?hydro|glycosyl hydrolase|glycoside|glucosidase|galactosidase|"
                r"glucanase|amylase|chitinase|cellulase|xylanase|agarase|mannosidase|"
                r"pectin|pectate|fucosidase|hexosaminidase", re.I),
     "carbohydrate"),
    (re.compile(r"lipase|phospholipase|abhydrolase|carboxylesterase|\besterase\b", re.I),
     "lipid/ester"),
    (re.compile(r"alkaline phosphatase|phox|\bphytase\b|metallophos|phosphoesterase|"
                r"histidine phosphatase|phosphodiester|\bphosphatase\b|phosphomonoester", re.I),
     "organic phosphate"),
    (re.compile(r"ribonuclease|deoxyribonuclease|\bnuclease\b|rnase|dnase|"
                r"exonuclease|endonuclease", re.I),
     "nucleic acid"),
    (re.compile(r"sulfatase|arylsulfatase", re.I), "sulfate ester"),
    (re.compile(r"amidase|asparaginase|carbon-nitrogen hydrolase|deaminase", re.I),
     "amide/C-N"),
]


def name_substrate(name):
    if not name or NAME_EXCLUDE.search(name):
        return None
    for pat, sub in NAME_SUBSTRATE:
        if pat.search(name):
            return sub
    return None


def ec_substrate(ec):
    if ec.startswith("3.4"):
        return "protein/peptide"
    if ec.startswith("3.2"):
        return "carbohydrate"
    if ec.startswith("3.1.1"):
        return "lipid/ester"
    if ec.startswith("3.1.3"):
        return "organic phosphate"
    if ec.startswith(("3.1.4", "3.1.11", "3.1.21", "3.1.26", "3.1.27", "3.1.30", "3.1.31")):
        return "nucleic acid"
    if ec.startswith("3.1.6"):
        return "sulfate ester"
    if ec.startswith("3.1"):
        return "ester (other)"
    if ec.startswith("3.5"):
        return "amide/C-N"
    return None


def cazy_substrate(fam):
    cls = re.match(r"[A-Za-z]+", fam)
    cls = cls.group(0).upper() if cls else ""
    if cls in {"GH", "PL"}:
        return "carbohydrate"
    if cls == "CE":
        return "carbohydrate (ester)"
    return None


def _fetch(locus, organism, ontology, conn):
    return gene_ontology_terms(locus_tags=locus, organism=organism,
                               ontology=ontology, limit=None, conn=conn)["results"]


def _tier(row):
    if not row["is_degradative"]:
        return "—"
    if row["is_exported"]:
        return "A: degradative + exported"
    if row["is_cytoplasmic"]:
        return "C: degradative + cytoplasmic (likely contaminant)"
    return "B: degradative, export uncertain"


def classify(genes, conn, batch=1500):
    """Annotate genes (df with locus_tag, strain_short) with exoenzyme tiers."""
    func, export, cyto = {}, {}, set()
    for strain, sub in genes.groupby("strain_short"):
        loci = sub["locus_tag"].tolist()
        for i in range(0, len(loci), batch):
            chunk = loci[i:i + batch]
            for r in _fetch(chunk, strain, "ec", conn):
                s = ec_substrate(r["term_id"].split(":")[-1])
                if s:
                    func.setdefault(r["locus_tag"], {})[s] = \
                        f"EC {r['term_id'].split(':')[-1]} ({r['term_name']})"
            for r in _fetch(chunk, strain, "cazy", conn):
                fam = r["term_name"] or r["term_id"].split(":")[-1]
                s = cazy_substrate(fam)
                if s:
                    func.setdefault(r["locus_tag"], {}).setdefault(s, f"CAZy {fam}")
            for r in _fetch(chunk, strain, "go_mf", conn):
                s = name_substrate(r["term_name"])
                if s:
                    func.setdefault(r["locus_tag"], {}).setdefault(s, f"GO-MF {r['term_name']}")
            for r in _fetch(chunk, strain, "pfam", conn):
                s = name_substrate(r["term_name"])
                if s:
                    func.setdefault(r["locus_tag"], {}).setdefault(s, f"Pfam {r['term_name']}")
            for r in _fetch(chunk, strain, "subcellular_localization", conn):
                if r["term_name"] in EXPORT_LOCS:
                    export.setdefault(r["locus_tag"], []).append(f"loc:{r['term_name']}")
                elif r["term_name"] == "Cytoplasmic":
                    cyto.add(r["locus_tag"])
            for r in _fetch(chunk, strain, "signal_peptide_type", conn):
                export.setdefault(r["locus_tag"], []).append(f"signal:{r['term_name']}")

    g = genes.copy()
    g["substrates"] = g["locus_tag"].map(lambda lt: ";".join(sorted(func.get(lt, {}).keys())))
    g["func_evidence"] = g["locus_tag"].map(lambda lt: " | ".join(func.get(lt, {}).values()))
    g["export_evidence"] = g["locus_tag"].map(lambda lt: ";".join(export.get(lt, [])))
    g["is_degradative"] = g["substrates"] != ""
    g["is_exported"] = g["export_evidence"] != ""
    g["is_cytoplasmic"] = g["locus_tag"].isin(cyto)
    g["tier"] = g.apply(_tier, axis=1)
    g["is_exoenzyme"] = g["is_degradative"] & ~g["is_cytoplasmic"]
    return g
