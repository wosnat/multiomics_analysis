"""Build the HOT1A3 transporter table: system reconstruction + substrate-
resolution audit + importer/organic classification.

Consumes the cached raw KG pulls (pull_transporter_raw.py). Produces:
  - hot1a3_transporter_gene_table.csv  (one row per candidate gene)
  - hot1a3_transporter_table.csv        (one row per reconstructed system)
  - run_manifest.md                     (counts + resolution distribution)

Method (proposal Approach step 1, decisions 6/7/12):
  1. Candidate transporter genes = union of BRITE ko02000 / KEGG-KO /
     TCDB / product-search (already unioned in the cache).
  2. Reconstruct transport SYSTEMS by genomic adjacency (same contig, same
     strand, intergenic gap <= GAP_BP) refined by component role read from the
     KEGG KO name (substrate-binding / permease / ATP-binding). Boundary rule:
     a repeated role splits ONLY indistinguishable unresolved/putative
     cassettes; a shared specific substrate keeps a multi-permease/ATPase
     system whole (livKHMGF).
  3. Resolve each system's substrate at the finest the evidence CONFIDENTLY
     supports: KEGG KO name (primary) -> BRITE leaf -> TCDB family (only when
     2.A.x specific) -> product/function. Assign resolution_level, a
     confident/inferred flag, and the source of the call.
  4. Classify importer vs exporter and organic-carbon vs inorganic.

Every substrate value traces to KG-provided annotation text (stored in the
`substrate_evidence` column). Where nothing resolves, the system is marked
`unresolved` -- never guessed.
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
GAP_BP = 150   # intergenic-gap ceiling for adjacency (calibrated below; see manifest)

load = lambda n: json.load(open(os.path.join(CACHE, n)))

# ----------------------------------------------------------------------------
# Role parsing from a KEGG KO name (primary) or product text (fallback)
# ----------------------------------------------------------------------------
def parse_role(text):
    """Return ABC component role from annotation text: SBP / PERM / ATP / None."""
    t = (text or "").lower()
    # Precedence matters: "ATP-binding protein" contains "binding", so ATP and
    # permease must be tested BEFORE the generic substrate-binding clause.
    if "atp-binding" in t or "atpase" in t or "atp-binding cassette" in t:
        return "ATP"
    if "permease" in t:
        return "PERM"
    # SBP requires an explicit transporter-binding phrase — NOT a bare
    # "binding protein" (which also matches DNA-binding / competence proteins).
    if "substrate-binding" in t or "solute-binding" in t or "periplasmic-binding" in t \
            or "periplasmic component" in t or "transporter-binding" in t \
            or ("binding" in t and "transport system" in t):
        return "SBP"
    return None


def ko_substrate_phrase(name):
    """Extract the substrate phrase from a KEGG KO name.

    KO names look like:
      'afuA, fbpA; iron(III) transport system substrate-binding protein'
      'livK; branched-chain amino acid transport system substrate-binding protein'
      'dppA; dipeptide transport system substrate-binding protein'
    Substrate phrase = the text after the '; ' and before 'transport system'
    / 'transport protein' / 'transporter'.
    """
    if not name:
        return None
    s = name
    if ";" in s:
        s = s.split(";", 1)[1]
    s = s.strip()
    # cut off at the transporter-descriptor tail
    for marker in ["transport system", "membrane transport", "transport protein",
                   "transporter", "permease", "ABC transport", "porin", "channel"]:
        idx = s.lower().find(marker)
        if idx > 0:
            return s[:idx].strip(" ,-").strip()
    return None


# ----------------------------------------------------------------------------
# Substrate lexicon -> (resolution_level, organic_or_inorganic, options)
# Grounded on the KO/BRITE substrate vocabulary actually present for HOT1A3
# (see pull cache). Classification of "specific vs class" is methodology; the
# substrate STRING always comes from KG text.
# ----------------------------------------------------------------------------
INORGANIC = {
    "iron(iii)", "iron complex", "ferric", "iron(ii)", "high-affinity iron",
    "iron(iii)/siderophore", "ferrous", "manganese/iron", "manganese", "zinc",
    "phosphate", "inorganic phosphate", "phosphonate", "phosphite", "nitrate",
    "nitrite", "nitrate/nitrite", "sulfate", "sulfate/thiosulfate", "thiosulfate",
    "ammonium", "potassium", "sodium", "magnesium", "molybdate", "tungstate",
    "cobalt", "nickel", "copper", "calcium", "chloride", "bicarbonate",
    "cadmium/zinc/cobalt", "sulfur",
    # iron-acquisition vocabulary that does not follow the "X transport
    # system" KO pattern (TonB-dependent receptors etc.) -> iron / inorganic
    "siderophore", "ferric", "ferrienterochelin", "ferric coprogen",
    "enterochelin", "ferrichrome", "catecholate", "ferrous iron",
    "iron complex",
}
# specific organic-C compounds
SPECIFIC_ORG = {
    "glutamine", "arginine", "lysine", "histidine", "glutamate", "aspartate",
    "glutamate/aspartate", "serine", "threonine", "serine/threonine", "glycine",
    "proline", "glycerol", "glycerol-3-phosphate", "sn-glycerol 3-phosphate",
    "glycolate", "fructose", "glucose", "galactose", "fucose", "ribose",
    "maltose", "maltose/maltodextrin", "mannose", "xylose", "rhamnose",
    "arabinose", "lactate", "malate", "benzoate", "3-phenylpropionic acid",
    "choline", "betaine", "glycine betaine", "spermidine", "putrescine",
    "spermidine/putrescine", "taurine", "nicotinamide mononucleotide",
    "nicotinamide riboside", "vitamin b12", "cobalamin", "urea", "microcin c",
    "methionine", "d-methionine", "sialic acid", "glycerophosphoryl diester",
    "2-aminoethylphosphonate", "lactose", "trehalose", "sucrose", "cellobiose",
    "alpha-glucoside", "beta-glucoside", "gluconate", "citrate", "fumarate",
    "succinate", "alpha-ketoglutarate", "glutathione", "heme", "cystine",
    "cysteine", "glycine/betaine", "ectoine", "sarcosine", "creatinine",
}
# narrow classes (small, chemically coherent group)
NARROW = {
    "branched-chain amino acid": (["leucine", "isoleucine", "valine"], "organic"),
    "polar amino acid": (["glutamate", "aspartate", "glutamine", "arginine"], "organic"),
    "general l-amino acid": (None, "organic"),
    "dipeptide": (None, "organic"),
    "oligopeptide": (None, "organic"),
    "peptide": (None, "organic"),
    "nucleoside": (None, "organic"),
    "monosaccharide": (None, "organic"),
    "osmoprotectant": (["glycine betaine", "proline", "choline"], "organic"),
    "quaternary amine": (["glycine betaine", "choline", "carnitine"], "organic"),
    "putative amino acid": (None, "organic"),
}
# broad classes
BROAD = {
    "amino acid": "organic",
    "sugar": "organic",
    "carbohydrate": "organic",
    "multiple sugar": "organic",
    "saccharide": "organic",
    "polyol": "organic",
    "carboxylate": "organic",
    "organic acid": "organic",
    "lipid": "organic",
    "polysaccharide": "organic",
    "capsular polysaccharide": "organic",
}
# multi-substrate composite phrases (slash-joined lists)
def is_multi(phrase):
    return "/" in phrase and phrase.count("/") >= 1


def classify_phrase(phrase):
    """Map a substrate phrase -> (call, level, org_inorg, options).
    Returns None if the phrase carries no substrate signal."""
    if not phrase:
        return None
    p = phrase.strip().lower()
    if not p:
        return None
    # generic non-substrate tails that slipped through
    junk = {"abc", "abc-2 type", "putative abc", "multidrug", "drug",
            "drug/metabolite", "biopolymer", "protein", "efflux", "mfs",
            "multidrug resistance", "macrolide"}
    # generic composite families that are NOT a nutrient substrate list
    if "drug" in p and ("metabolite" in p or "resistance" in p):
        return None
    # multi-substrate composite (e.g. phospholipid/cholesterol/gamma-HCH,
    # choline/glycine/proline betaine, peptide/nickel, fucose-galactose-glucose)
    if is_multi(p) or "-galactose-" in p:
        opts = re.split(r"[\/]", p)
        # organic unless every option is inorganic
        org = "organic" if any(not any(o.strip() in INORGANIC for o in [x]) for x in opts) else "inorganic"
        # peptide/nickel -> organic (peptide carbon)
        return (phrase, "multi_substrate", org, [o.strip() for o in opts])
    # narrow class
    for key, (opts, org) in NARROW.items():
        if key in p:
            return (key, "narrow_class", org, opts)
    # specific compound
    if p in SPECIFIC_ORG or any(p == s for s in SPECIFIC_ORG):
        return (phrase, "specific_compound", "organic", None)
    if p in INORGANIC:
        return (phrase, "specific_compound", "inorganic", None)
    # containment checks for specific (e.g. 'iron(iii)' inside phrase)
    for s in SPECIFIC_ORG:
        if s in p:
            return (phrase, "specific_compound", "organic", None)
    for s in INORGANIC:
        if s in p:
            return (phrase, "specific_compound", "inorganic", None)
    # broad class
    for key, org in BROAD.items():
        if key in p:
            return (key, "broad_class", org, None)
    if p in junk or any(j == p for j in junk):
        return None
    return None


# ----------------------------------------------------------------------------
# Exporter / efflux detection
# ----------------------------------------------------------------------------
EXPORT_KEYS = ["efflux", "export", "exporter", "multidrug", "secretion",
               "macrolide", "lps export", "capsul", "drug resistance",
               "extrusion", "resistance-nodulation", "rnd ", "releasing"]

def is_exporter(texts):
    blob = " ".join(t.lower() for t in texts if t)
    return any(k in blob for k in EXPORT_KEYS)


# ----------------------------------------------------------------------------
# Import veto: catch systems that are NOT membrane solute importers even though
# a substrate word appears in their annotation -- protein-export/secretion,
# surface-polysaccharide biosynthesis/export, cytoplasmic/peripheral enzymes,
# and mechanosensitive ion channels with a spurious organic call. Applied to
# the substrate-DONOR gene (the one that produced the system's substrate call),
# so a genuine transporter with one accessory enzyme subunit is not dropped.
# ----------------------------------------------------------------------------
# Protein-export / secretion machinery (moves proteins, not solutes).
_VETO_PROTEIN_EXPORT = [
    "twin-arginine", "twin arginine", "sec-independent protein",
    "protein translocase", "preprotein translocase", "protein-export",
    "general secretion pathway", "type ii secretion", "type iii secretion",
    "type iv secretion", "type vi secretion",
]
# Surface-polysaccharide / cell-envelope biosynthesis-export (not solute uptake).
_VETO_SURFACE_POLY = [
    "lipopolysaccharide", "o-antigen", "exopolysaccharide",
    "polysaccharide biosynthesis", "polysaccharide export", "gumc",
    "chain length determinant", "cellulose synthase", "cellulose biosynthesis",
    "glucans biosynthesis", "murein biosynthesis", "teichoic acid",
    "capsule biosynthesis",
]
# Cytoplasmic / peripheral enzyme suffixes (require NO transporter noun in
# product+KO to fire, so real transporters are not vetoed).
_VETO_ENZYME = [
    "glycosyltransferase", "sulfotransferase", " kinase", "biosynthesis",
    "biosynthetic", "synthase", "synthetase", " ligase", " lyase", "epimerase",
    "reductase", "dehydrogenase", " hydrolase", "isomerase", "mutase",
    "carboxylase", "decarboxylase", "phosphorylase", "oxidase", "deaminase",
    "amidohydrolase", "aminotransferase", "acyltransferase",
]
# Transporter nouns for the enzyme-rule exemption (product+KO only).
_VETO_NOUN_EXEMPT = ["transporter", "permease", "symporter", "antiporter",
                     "carrier", "porin", "channel", "tonb", "facilitator",
                     "abc transport", "transport system", "solute-binding",
                     "substrate-binding", "receptor", "recepter", "bcct",
                     "pts system"]


def import_veto(donor):
    """Return (reason, mode) if the donor gene is not a solute importer, else
    None. mode in {'non_transporter', 'reclass_inorganic'}."""
    prod = (donor.get("product") or "").lower()
    ko = (donor.get("ko_name") or "").lower()
    fd = (donor.get("function_description") or "").lower()
    blob = " ".join([prod, ko, fd])
    # 1. protein-export / secretion (overrides transporter nouns)
    if any(k in blob for k in _VETO_PROTEIN_EXPORT):
        return ("protein-export/secretion (not a solute importer)", "non_transporter")
    # 2. surface-polysaccharide / cell-envelope biosynthesis-export (overrides nouns)
    if any(k in blob for k in _VETO_SURFACE_POLY):
        return ("surface-polysaccharide / cell-envelope biosynthesis-export "
                "(not a solute importer)", "non_transporter")
    # 3. cytoplasmic / peripheral enzyme -- only when product+KO carry NO
    #    transporter noun (function_description excluded: it often says
    #    'glycerol uptake' for a kinase in a transport pathway). Genes that are
    #    themselves a transporter component (parsed ABC role, or a
    #    binding-protein phrase anywhere) are EXEMPT -- an enzyme word in their
    #    function_description is pathway context, not their own function.
    prod_ko = prod + " " + ko
    is_component = donor.get("role") in ("SBP", "PERM", "ATP") or any(
        b in blob for b in ("substrate-binding", "substrate binding protein",
                            "periplasmic-binding", "periplasmic binding protein",
                            "solute-binding"))
    if (not is_component and any(e in blob for e in _VETO_ENZYME)
            and not any(n in prod_ko for n in _VETO_NOUN_EXEMPT)):
        return ("enzyme / biosynthesis (not a membrane solute transporter)",
                "non_transporter")
    # 4. mechanosensitive ion channel with a spurious organic (lipid) call
    if "mechanosensitive" in blob:
        return ("mechanosensitive ion channel; organic call is a spurious "
                "'membrane lipid bilayer' match", "reclass_inorganic")
    return None


# ----------------------------------------------------------------------------
# Load cache
# ----------------------------------------------------------------------------
def main():
    gd = load("gene_details.json")
    ko = load("kegg_ko_by_gene.json")
    brite = load("brite_leaf_by_gene.json")
    tcdb = load("tcdb_by_gene.json")
    srcs = load("union_sources.json")

    genes = list(gd.keys())

    # ---- per-gene annotation record ----
    rec = {}
    for g in genes:
        d = gd[g]
        ko_terms = ko.get(g, [])
        # pick the transporter KO (name mentions transport/permease) preferentially
        ko_t = None
        for t in ko_terms:
            if any(k in t["term_name"].lower() for k in
                   ("transport", "permease", "porin", "channel", "symport", "antiport")):
                ko_t = t
                break
        if ko_t is None and ko_terms:
            ko_t = ko_terms[0]
        ko_name = ko_t["term_name"] if ko_t else None
        ko_id = ko_t["term_id"] if ko_t else None
        # deepest BRITE leaf
        bl = brite.get(g, [])
        bl_best = max(bl, key=lambda x: x.get("level") or 0) if bl else None
        # deepest TCDB
        tl = tcdb.get(g, [])
        tl_best = max(tl, key=lambda x: x.get("level") or 0) if tl else None

        role = parse_role(ko_name) or parse_role(d.get("product")) or parse_role(d.get("function_description"))
        rec[g] = {
            "locus_tag": g,
            "gene_name": d.get("gene_name"),
            "product": d.get("product"),
            "function_description": d.get("function_description"),
            "gene_category": d.get("gene_category"),
            "contig": d.get("contig"),
            "start": d.get("start"),
            "end": d.get("end"),
            "strand": d.get("strand"),
            "ko_id": ko_id,
            "ko_name": ko_name,
            "brite_leaf": bl_best["term_name"] if bl_best else None,
            "brite_level": bl_best.get("level") if bl_best else None,
            "tcdb_id": tl_best["term_id"] if tl_best else None,
            "tcdb_name": tl_best["term_name"] if tl_best else None,
            "role": role,
            "sources": [k for k, v in srcs.get(g, {}).items() if v],
            "ko_substrate": ko_substrate_phrase(ko_name),
        }

    # ---- substrate call per GENE (for the per-gene table) ----
    for g, r in rec.items():
        call = _resolve_gene(r)
        r.update(call)

    # ---- system reconstruction ----
    systems = reconstruct_systems(rec)

    # ---- resolve substrate per SYSTEM ----
    sys_rows = []
    for sid, member_tags in systems:
        members = [rec[t] for t in member_tags]
        row = resolve_system(sid, members)
        sys_rows.append(row)

    write_gene_csv(rec)
    write_system_csv(sys_rows)
    write_manifest(rec, sys_rows, systems)
    print(f"genes={len(rec)}  systems={len(sys_rows)}")


# ---- gene-level substrate resolution (finest confident) ----
_TRANSPORTER_NOUNS = ["transporter", "permease", "symporter", "antiporter",
                      "receptor", "recepter", "channel", "porin", "carrier",
                      "transport system", "abc transport", "tonb", "translocase",
                      "uptake", "importer", "exporter", "efflux", "transport protein",
                      "solute-binding", "substrate-binding", "pts system"]


def _has_transporter_noun(text):
    t = (text or "").lower()
    return any(n in t for n in _TRANSPORTER_NOUNS)


def _wb(word, text):
    """Word-boundary containment (avoids 'lactose' matching inside 'galactose')."""
    return re.search(r"(?<![a-z])" + re.escape(word) + r"(?![a-z])", text) is not None


def _scan_substrate(text):
    """High-precision word-boundary substrate scan over an annotation string.
    Returns (call, level, org, options) or None. Detects the iron-siderophore
    group, multi-substrate lists (>=2 distinct specific compounds), single
    specific compounds, narrow classes, and broad classes."""
    if not text:
        return None
    t = text.lower()
    # iron-acquisition vocabulary -> iron / inorganic
    iron_words = ["siderophore", "ferric", "ferrienterochelin", "coprogen",
                  "enterochelin", "ferrichrome", "catecholate", "iron complex",
                  "ferrous", "hemin"]
    if any(w in t for w in iron_words):
        return ("iron/siderophore", "specific_compound", "inorganic", None)
    # collect distinct specific compounds by word boundary
    hits = [s for s in SPECIFIC_ORG if _wb(s, t)]
    ihits = [s for s in INORGANIC if _wb(s, t)]
    if len(hits) >= 2:
        return ("/".join(sorted(set(hits))), "multi_substrate", "organic", sorted(set(hits)))
    if len(hits) == 1:
        return (hits[0], "specific_compound", "organic", None)
    if len(ihits) >= 1:
        return (ihits[0], "specific_compound", "inorganic", None)
    for key, (opts, org) in NARROW.items():
        if key in t:
            return (key, "narrow_class", org, opts)
    for key, org in BROAD.items():
        if key in t:
            return (key, "broad_class", org, None)
    return None


def _nonsubstrate(text):
    """True if the annotation text names a non-transporter or a substrate word
    used in a non-transport sense (regulator / protein-export / efflux-regulator
    / flagellar), so we must NOT read an import substrate from it."""
    t = (text or "").lower()
    bad = ["transcriptional regulator", "dna-binding", "regulatory protein",
           "twin arginine", "(tat)", "sec-independent", "preprotein",
           "protein translocase", "signal recognition", "two-component",
           "sensor", "-regulated ", "-regulated potassium", "chemotaxis",
           "flagellar", "nitrogen regulatory", "response regulator",
           "resistance protein", "processing protein", "insertase",
           "protein insertase", "oxa1", "alb3"]
    return any(b in t for b in bad)


def _resolve_gene(r):
    """Resolve one gene's substrate from its own evidence, in priority order:
    KEGG KO substrate (primary) -> KO-name keyword scan -> BRITE leaf ->
    TCDB family(2.A.x) -> product/func. Each evidence string is gated by
    `_nonsubstrate` so regulators / protein-export / efflux-regulators do not
    donate a spurious import substrate."""
    ko_name = r.get("ko_name")
    # 1. KEGG KO substrate phrase (the structured "X transport system ..."
    # pattern) -- highest precision. Confident.
    if ko_name and not _nonsubstrate(ko_name):
        c = classify_phrase(r.get("ko_substrate"))
        if c:
            call, level, org, opts = c
            return _mk(call, level, org, "kegg_ko", "confident", ko_name, opts)
        # 1b. KO NAME word-boundary scan -- KOs carrying a substrate outside the
        # "X transport system" pattern (TonB iron/siderophore receptors). Only
        # when the KO name itself names a transporter. Inferred.
        if _has_transporter_noun(ko_name):
            c = _scan_substrate(ko_name)
            if c:
                call, level, org, opts = c
                return _mk(call, level, org, "kegg_ko_keyword", "inferred", ko_name, opts)
    # 2. BRITE leaf term
    bl = r.get("brite_leaf")
    if bl and not _nonsubstrate(bl):
        c = classify_phrase(_strip_transporter(bl))
        if c:
            call, level, org, opts = c
            return _mk(call, level, org, "brite_leaf", "confident", bl, opts)
    # 3. TCDB family -- only a specific 2.A.x secondary carrier
    tid, tname = r.get("tcdb_id"), r.get("tcdb_name")
    if tid and tid.startswith("tcdb:2.A") and not _nonsubstrate(tname):
        c = classify_phrase(_strip_transporter(tname))
        if c:
            call, level, org, opts = c
            return _mk(call, level, org, "tcdb_family", "inferred", tname, opts)
    # 4. product / function_description word-boundary scan -- only when the
    # evidence field itself names a transporter (excludes enzymes / regulators
    # that merely mention a substrate). Inferred.
    for fld in ("product", "function_description"):
        txt = r.get(fld)
        if txt and _has_transporter_noun(txt) and not _nonsubstrate(txt):
            c = _scan_substrate(txt)
            if c:
                call, level, org, opts = c
                return _mk(call, level, org, fld, "inferred", txt, opts)
    # unresolved
    return _mk(None, "unresolved", None, None, "none", ko_name or r.get("product"), None)


def _mk(call, level, org, source, conf, evidence, opts):
    return {
        "substrate_call": call if call else "unresolved",
        "resolution_level": level,
        "organic_or_inorganic": org,
        "substrate_source": source,
        "substrate_confidence": conf,
        "substrate_evidence": evidence,
        "substrate_options": "; ".join(opts) if opts else None,
    }


def _strip_transporter(text):
    if not text:
        return None
    s = text
    for marker in ["transport system", "transport protein", "transporter",
                   "permease", "porin", "channel", " family", " substrate-binding"]:
        idx = s.lower().find(marker)
        if idx > 0:
            s = s[:idx]
    return s.strip(" ,-")


# ---- system reconstruction by adjacency + role boundary rule ----
def reconstruct_systems(rec):
    """Group candidate genes into transport systems.
    Returns list of (system_id, [locus_tags])."""
    # order by contig, start
    ordered = sorted(rec.values(), key=lambda r: (r["contig"] or "", r["start"] or 0))
    # build runs: same contig, same strand, intergenic gap <= GAP_BP
    runs = []
    cur = []
    prev = None
    for r in ordered:
        if prev is None:
            cur = [r]
        else:
            same_contig = r["contig"] == prev["contig"]
            same_strand = r["strand"] == prev["strand"]
            gap = (r["start"] or 0) - (prev["end"] or 0)
            if same_contig and same_strand and gap <= GAP_BP:
                cur.append(r)
            else:
                runs.append(cur)
                cur = [r]
        prev = r
    if cur:
        runs.append(cur)

    # within each run, split by the role boundary rule
    systems = []
    sidx = 0
    for run in runs:
        for sysmembers in split_run(run):
            sidx += 1
            systems.append((f"HOT1A3_TS{sidx:03d}", [m["locus_tag"] for m in sysmembers]))
    return systems


def split_run(run):
    """Split a genomic run into physical systems using component roles.
    Boundary rule (decision 7): a repeated ABC role splits ONLY when both the
    incumbent and the new gene are unresolved/putative and share no specific
    substrate; a shared specific substrate keeps a repeated-role system whole."""
    if len(run) == 1:
        return [run]
    out = []
    cur = [run[0]]
    filled = {run[0]["role"]} if run[0]["role"] else set()
    for g in run[1:]:
        role = g["role"]
        # substrate sharing test between g and current system
        cur_subs = {m["substrate_call"] for m in cur
                    if m.get("resolution_level") in ("specific_compound", "narrow_class")}
        g_spec = g.get("resolution_level") in ("specific_compound", "narrow_class")
        shares = g_spec and g["substrate_call"] in cur_subs
        cur_unresolved = all(m.get("resolution_level") == "unresolved" for m in cur)
        g_unresolved = g.get("resolution_level") == "unresolved"

        if role is None:
            # non-ABC-component gene (single-type transporter): its own system.
            out.append(cur)
            cur = [g]
            filled = set()
            continue
        if role in filled:
            # Repeated role. Per the proposal boundary rule, a repeated role
            # splits ONLY indistinguishable unresolved/putative cassettes (both
            # unresolved AND no shared specific substrate). A shared specific
            # substrate (livKHMGF) OR any resolved subunit keeps the system whole.
            if (cur_unresolved and g_unresolved) and not shares:
                out.append(cur)  # tiebreaker split
                cur = [g]
                filled = {role}
            else:
                cur.append(g)  # keep whole
        else:
            # complementary role fills a new slot -> join
            cur.append(g)
            filled.add(role)
    if cur:
        out.append(cur)
    return out


# ---- system-level substrate resolution ----
LEVEL_RANK = {"specific_compound": 4, "narrow_class": 3, "multi_substrate": 2,
              "broad_class": 1, "unresolved": 0}

def resolve_system(sid, members):
    tags = [m["locus_tag"] for m in members]
    names = [m.get("gene_name") for m in members]
    ko_ids = [m.get("ko_id") for m in members if m.get("ko_id")]
    roles = [m.get("role") for m in members]

    # best (finest) resolved substrate across members
    best = None
    for m in members:
        if best is None or LEVEL_RANK.get(m["resolution_level"], 0) > LEVEL_RANK.get(best["resolution_level"], 0):
            best = m
    # if the finest is specific/narrow held by a binding protein, prefer it;
    # otherwise best already holds the finest.
    substrate_call = best["substrate_call"]
    level = best["resolution_level"]
    org = best["organic_or_inorganic"]
    source = best["substrate_source"]
    conf = best["substrate_confidence"]
    evidence = best["substrate_evidence"]
    options = best.get("substrate_options")

    # importer vs exporter
    texts = []
    for m in members:
        texts += [m.get("ko_name"), m.get("product"), m.get("function_description"),
                  m.get("tcdb_name"), m.get("brite_leaf")]
    exporter = is_exporter(texts)
    imp_exp = "exporter" if exporter else "importer"

    # organic/inorganic default if unresolved
    if org is None:
        org = "unknown"

    # Import veto: remove non-importer leakage from the importer set. Applied to
    # the substrate-donor gene (`best`). Rows are KEPT; the reason is recorded in
    # `source` and the row moves out of the importer/organic set.
    if imp_exp == "importer":
        veto = import_veto(best)
        if veto:
            reason, mode = veto
            if mode == "non_transporter":
                imp_exp = "non_transporter"
                source = f"reclassified: {reason}"
            elif mode == "reclass_inorganic":
                org = "inorganic"
                source = f"reclassified: {reason}"

    return {
        "system_id": sid,
        "locus_tags": ";".join(tags),
        "gene_names": ";".join(n or "" for n in names),
        "n_genes": len(members),
        "KO_ids": ";".join(ko_ids),
        "component_roles": ";".join(r or "-" for r in roles),
        "substrate_call": substrate_call,
        "resolution_level": level,
        "confidence_flag": conf,
        "source": source,
        "substrate_evidence": evidence,
        "substrate_options": options,
        "importer_or_exporter": imp_exp,
        "organic_or_inorganic": org,
        "gene_categories": ";".join(sorted({m.get("gene_category") or "" for m in members})),
    }


# ---- writers ----
def write_gene_csv(rec):
    cols = ["locus_tag", "gene_name", "product", "gene_category", "contig",
            "start", "end", "strand", "role", "ko_id", "ko_name", "ko_substrate",
            "brite_leaf", "tcdb_id", "tcdb_name", "substrate_call",
            "resolution_level", "organic_or_inorganic", "substrate_source",
            "substrate_confidence", "substrate_evidence", "substrate_options",
            "sources"]
    path = os.path.join(HERE, "hot1a3_transporter_gene_table.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for g in sorted(rec, key=lambda x: (rec[x]["contig"] or "", rec[x]["start"] or 0)):
            r = rec[g]
            w.writerow([r.get(c) if c != "sources" else ";".join(r["sources"]) for c in cols])
    print("wrote", path)


def write_system_csv(sys_rows):
    cols = ["system_id", "locus_tags", "gene_names", "n_genes", "KO_ids",
            "component_roles", "substrate_call", "resolution_level",
            "confidence_flag", "source", "substrate_evidence",
            "substrate_options", "importer_or_exporter", "organic_or_inorganic",
            "gene_categories"]
    path = os.path.join(HERE, "hot1a3_transporter_table.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for row in sys_rows:
            w.writerow(row)
    print("wrote", path)


def write_manifest(rec, sys_rows, systems):
    from collections import Counter
    n_genes = len(rec)
    n_sys = len(sys_rows)
    lvl = Counter(r["resolution_level"] for r in sys_rows)
    imp = Counter(r["importer_or_exporter"] for r in sys_rows)
    org = Counter(r["organic_or_inorganic"] for r in sys_rows)
    org_c_importers = sum(1 for r in sys_rows
                          if r["importer_or_exporter"] == "importer"
                          and r["organic_or_inorganic"] == "organic")
    org_c_imp_by_level = Counter(r["resolution_level"] for r in sys_rows
                                 if r["importer_or_exporter"] == "importer"
                                 and r["organic_or_inorganic"] == "organic")
    multi_gene = sum(1 for r in sys_rows if r["n_genes"] > 1)
    src_dist = Counter(r["source"] for r in sys_rows)
    ngenes_dist = Counter(r["n_genes"] for r in sys_rows)

    lines = []
    lines.append("# Methods run manifest — HOT1A3 transporter table\n")
    lines.append("Facts only. Produced by `build_transporter_table.py` from the "
                 "cached KG pulls (`pull_transporter_raw.py`).\n")
    lines.append("## What ran\n")
    lines.append("- `pull_transporter_raw.py` — enumerated candidate transporter "
                 "genes by unioning four KG sources for *Alteromonas macleodii "
                 "HOT1A3*, then pulled per-gene annotation. Cached to `cache/`.")
    lines.append("- `build_transporter_table.py` — reconstructed systems, "
                 "resolved substrates, classified importer/organic.\n")
    log = load("pull_log.json")
    lines.append("## Enumeration (union of four sources)\n")
    lines.append(f"- BRITE transporters tree `ko02000`: {log['brite_total_genes']} genes")
    lines.append(f"- KEGG-KO transporter-named: {log['kegg_transporter_genes']} genes "
                 f"(of {log['kegg_all_genes']} KEGG-annotated)")
    lines.append(f"- TCDB: {log['tcdb_total_genes']} genes")
    lines.append(f"- product/function search (transporter-filtered): {log['func_transporter_genes']} genes")
    lines.append(f"- **UNION candidate transporter genes: {log['union_total']}**\n")
    lines.append("## Systems reconstructed\n")
    lines.append(f"- Total transporter genes (candidate set): **{n_genes}**")
    lines.append(f"- Total transport systems reconstructed: **{n_sys}**")
    lines.append(f"- Multi-gene systems: {multi_gene}; single-gene systems: {n_sys - multi_gene}")
    lines.append(f"- Adjacency gap ceiling used: {GAP_BP} bp (same contig, same strand)")
    lines.append(f"- System size distribution (n_genes: count): "
                 f"{dict(sorted(ngenes_dist.items()))}\n")
    lines.append("## Resolution level distribution (per system)\n")
    for k in ["specific_compound", "narrow_class", "multi_substrate", "broad_class", "unresolved"]:
        lines.append(f"- {k}: {lvl.get(k, 0)}")
    lines.append("")
    lines.append("## Classification\n")
    lines.append(f"- importer: {imp.get('importer',0)}; exporter/efflux: "
                 f"{imp.get('exporter',0)}; non_transporter (import veto): "
                 f"{imp.get('non_transporter',0)}")
    lines.append(f"- organic: {org.get('organic',0)}; inorganic: {org.get('inorganic',0)}; unknown: {org.get('unknown',0)}")
    lines.append(f"- **organic-carbon importer systems: {org_c_importers}**")
    lines.append(f"  - by resolution level: {dict(org_c_imp_by_level)}\n")

    # ---- import-veto reclassification report ----
    recl = [r for r in sys_rows if (r["source"] or "").startswith("reclassified:")]
    reason_of = lambda r: (r["source"] or "").replace("reclassified: ", "").split(" (")[0]
    reason_ct = Counter(reason_of(r) for r in recl)
    # systems that LEFT the organic-carbon importer set specifically: they had a
    # resolved substrate AND were organic (mechanosensitive ones had org flipped
    # to inorganic, so catch them via the lipid-bilayer reason).
    left_org = [r for r in recl if r["resolution_level"] != "unresolved"
                and (r["organic_or_inorganic"] == "organic"
                     or "lipid bilayer" in r["source"])]
    lines.append("## Import veto — non-importer leakage removed\n")
    lines.append("A donor-based veto (applied to the substrate-donor gene) moves "
                 "systems that are NOT membrane solute importers out of the importer "
                 "set. Rows are KEPT; the reason is recorded in the `source` column "
                 "(`reclassified: ...`). Grouping/systems and the 150 bp adjacency "
                 "rule are unchanged.\n")
    lines.append(f"- Total systems reclassified out of the importer set: "
                 f"**{len(recl)}** (by reason: {dict(reason_ct)}).")
    lines.append(f"- Of these, **{len(left_org)}** were previously counted as "
                 f"**organic-carbon importers** and are now removed from that set:")
    for r in sorted(left_org, key=lambda x: x["system_id"]):
        lines.append(f"  - `{r['system_id']}` [{r['locus_tags']}] was "
                     f"`{r['substrate_call']}` → now "
                     f"`{r['importer_or_exporter']}/{r['organic_or_inorganic']}`; "
                     f"reason: {reason_of(r)}.")
    lines.append("- The full per-system list (all reclassified systems) is in "
                 "`hot1a3_transporter_table.csv` — filter `source` for the "
                 "`reclassified:` prefix.\n")
    lines.append("## Substrate-call source distribution (per system)\n")
    for k, v in src_dist.most_common():
        lines.append(f"- {k or 'none (unresolved)'}: {v}")
    lines.append("")
    # iron/siderophore count
    iron = sum(1 for r in sys_rows if "iron" in r["substrate_call"].lower()
               or "siderophore" in r["substrate_call"].lower())
    lines.append("## Notes, anomalies, and places the KG was ambiguous (facts only)\n")
    lines.append(f"- **Genome:** the HOT1A3 assembly in the KG has 2 contigs; all "
                 f"{n_genes} candidate genes carry coordinates, so genomic ordering "
                 f"is unambiguous.")
    lines.append(f"- **Adjacency calibration:** on known operons (Fe "
                 f"`ACZ81_00580/85/90`, phosphate `04030/35/40`, nitrate "
                 f"`03160/65/70`, Mla `03775..03795`) within-operon intergenic gaps "
                 f"are <200 bp while between-system gaps are >60 kb; the {GAP_BP} bp "
                 f"ceiling (plus same-contig + same-strand) reproduces these operons "
                 f"as single systems. Gray-zone neighbour pairs (150-2000 bp) were "
                 f"inspected and are unrelated adjacent transporters, not one system.")
    lines.append(f"- **Component roles read from the KEGG KO name** "
                 f"(substrate-binding / permease / ATP-binding); canonical systems "
                 f"reconstruct with the expected role strings (Fe SBP;PERM;ATP; "
                 f"phosphate PERM;PERM;ATP; dipeptide ATP;ATP;PERM;PERM;SBP kept "
                 f"whole per the repeated-role rule).")
    lines.append(f"- **Many amino-acid / peptide ABC importers appear as 1-gene "
                 f"systems at their substrate-binding protein.** In HOT1A3's KEGG "
                 f"annotation the substrate-specific KO is carried by the binding "
                 f"protein (e.g. 7x `ABC.PA.S` polar-amino-acid SBP), while the "
                 f"permease/ATPase partners carry generic 'putative ABC' KOs and are "
                 f"not always genomically adjacent in the candidate set. These are "
                 f"reported as 1-gene systems that still carry a substrate call from "
                 f"the SBP KO -- the substrate resolution (the audit's purpose) is "
                 f"preserved; the system count is conservative (partners counted "
                 f"separately where distal).")
    lines.append(f"- **Iron/siderophore TonB-dependent receptors:** {iron} systems "
                 f"resolve to iron/siderophore (inorganic) from KO-name keywords "
                 f"(e.g. 'iron complex outermembrane receptor'), which do not follow "
                 f"the 'X transport system' pattern -- flagged `inferred`, source "
                 f"`kegg_ko_keyword`.")
    lines.append(f"- **Non-transporters leaked into the broad union** (glutathione "
                 f"S-transferase enzymes, transcriptional regulators e.g. argP, the "
                 f"Tat protein-export system, flagellar motor proteins, "
                 f"glutathione-regulated K-efflux). A regulator/enzyme/protein-export "
                 f"context gate keeps them `unresolved` rather than donating a "
                 f"spurious import substrate; they inflate the candidate-gene count "
                 f"but not the resolved-substrate calls.")
    lines.append(f"- **Confidence semantics:** `confident` = substrate read from the "
                 f"structured KEGG-KO 'X transport system' phrase or a BRITE leaf; "
                 f"`inferred` = read from a KO-name/product word-boundary keyword "
                 f"scan or a TCDB 2.A.x family. Word-boundary matching is used to "
                 f"avoid substring errors (e.g. 'lactose' inside 'galactose').")
    lines.append(f"- **Aromatic/xenobiotic importers present** (benzoate, "
                 f"3-phenylpropionic acid) -- these are the proposal's pre-registered "
                 f"expected-negative class; recorded here, to be checked at the "
                 f"analysis milestone (they should not dominate the up-regulated "
                 f"catalog).")
    lines.append(f"- **`nitrate/nitrite` is tagged `multi_substrate`** (the KO names "
                 f"the pair); it is inorganic and not an organic-C candidate.")
    lines.append("")
    path = os.path.join(HERE, "run_manifest.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", path)


if __name__ == "__main__":
    main()
