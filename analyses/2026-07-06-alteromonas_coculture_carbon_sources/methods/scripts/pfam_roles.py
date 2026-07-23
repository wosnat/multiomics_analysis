"""Shared Pfam-domain parsing + component-role assignment (methods milestone follow-up).

Pfam short names are read from Gene.alternate_functional_descriptions entries of
the form:  '[pfam] ShortName: Long description'  (a gene may carry several).
Roles follow the coordinator's rules; KO/product only confirm, never override Pfam.
"""
import re

_PFAM_RE = re.compile(r"\[pfam\]\s*([^:]+):", re.IGNORECASE)


def pfam_domains(alt_list):
    """Extract the list of [pfam] short names from alternate_functional_descriptions."""
    out = []
    for e in alt_list or []:
        m = _PFAM_RE.match(e.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def _has(pfams, *names):
    s = {p.lower() for p in pfams}
    return any(n.lower() in s for n in names)


def _match(pfams, patterns):
    return any(re.search(pat, p, re.IGNORECASE) for p in pfams for pat in patterns)


def role_from_pfam(pfams):
    """Assign a component role from Pfam short names. Priority order matters."""
    if not pfams:
        return "other/unclear"
    # 1. two-component sensor kinase signature -> EXCLUDE from transporter
    if _has(pfams, "HATPase_c") and _match(pfams, [r"^HisKA", r"^Hpt$", r"^Response_reg", r"^HAMP$"]):
        return "sensor-kinase-EXCLUDE"
    # 2. substrate-binding protein
    if _match(pfams, [r"^SBP_bac", r"^Peripla_BP", r"^OpuAC", r"^Phosphonate-bd",
                      r"^Lig_chan-Glu_bd", r"^NMT1", r"^SBP_"]):
        return "substrate-binding"
    # 3. binding-protein-dependent transport inner-membrane permease
    if _match(pfams, [r"^BPD_transp", r"^ABC_membrane", r"^FecCD", r"^OppC", r"^BPD"]):
        return "permease"
    # 4. ABC ATP-binding cassette (TOBE is accessory only)
    if _match(pfams, [r"^ABC_tran", r"^ABC_ATPase", r"^AAA_ABC"]):
        return "ATP-binding"
    # 5. single-polypeptide secondary carriers (MFS etc.)
    if _match(pfams, [r"^MFS", r"^Sugar_tr", r"^BenE", r"^AA_permease", r"^EamA",
                      r"^DMT", r"^Aa_trans", r"^Gluconate", r"^Xan_ur_permease",
                      r"^Nramp", r"^Sodium", r"^TrkH", r"^SulP"]):
        return "secondary-carrier"
    return "other/unclear"
