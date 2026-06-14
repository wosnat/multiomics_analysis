"""
Step 3 (framing) — classify the 41 Cyanorak D.1.5 ortholog groups into the
focused P-ACQUISITION subset vs RESPONSIVE-OTHER (P-stress-responsive but not
acquisition) vs UNCLEAR (hypothetical / ambiguous). The D.1.5 role is broader
than "acquisition machinery" (gaps_and_friction.md), so the hypothesis is tested
on the focused subset; this script makes the subset membership explicit and
reviewable (it is a framing judgment, presented at the decide gate).

Rule (by OG consensus_gene_name + product):
  ACQUISITION       = Pi/phosphonate transport, phosphatases, pho two-component
                      regulator, P-starvation-inducible, polyphosphate, phosphate
                      regulator, sulfolipid substitution (P-sparing).
  RESPONSIVE_OTHER  = ribosomal/chaperone/PPP/glycolysis/glycogen/fatty-acid/
                      secretion/sucrose — present in the role but not P-acquisition.
  UNCLEAR           = conserved hypotheticals, generic porins (som), chrA — flagged,
                      excluded from the focused subset (conservative).

Input:  ../2_kg_entries/data/p_role_genes_by_strain.csv
Output: data/p_og_classification.csv, data/02_classify_p_ogs.log
Run:    uv run python analyses/2026-06-13-ll_vs_hl_p_capacity/3_framing/scripts/02_classify_p_ogs.py
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

STEP_DIR = Path(__file__).resolve().parents[1]
DATA = STEP_DIR / "data"
DATA.mkdir(parents=True, exist_ok=True)
GENES = STEP_DIR.parent / "2_kg_entries" / "data" / "p_role_genes_by_strain.csv"

ACQUISITION_GENES = {
    "pstS", "pstA", "pstB", "pstC",            # Pi ABC transporter
    "phnC", "phnD", "phnE", "phnC2", "phnD2", "phnE2",  # phosphonate transport
    "ptxD",                                     # phosphonate dehydrogenase
    "phoB", "phoR",                             # two-component regulator
    "phoH", "PsiP1",                            # P-starvation-inducible
    "phoC",                                     # acid phosphatase
    "ppk2",                                     # polyphosphate kinase
    "ptrA",                                     # transcriptional phosphate regulator
    "sphX",                                     # cyanobacterial Pi-binding
    "sqdB",                                     # sulfolipid substitution (P-sparing)
}
ACQUISITION_PRODUCT_KW = [
    "phosphate abc", "phosphate transport", "phosphate-binding", "phosphonate",
    "alkaline phosphatase", "acid phosphatase", "polyphosphate",
    "phosphate regulator", "phosphate sensing", "starvation-induc",
    "starvation inducible", "sulfoquinovose", "phosphatidic acid phosphatase",
    # step-3 decide: include clear phosphatase-family OGs (researcher call).
    # Specific phrases — NOT generic "phosphatase" (would wrongly catch spsA's
    # "sucrose phosphate synthase and phosphatase fusion protein").
    "pap2 superfamily", "putative phosphatase",
]
RESPONSIVE_GENES = {
    "rplJ", "rplL", "rplR", "dnaK3", "ahpC", "gnd", "pgl", "glgP", "galM",
    "prfC", "gap3", "fabG-2", "spsA", "rlpA", "hlyD", "mutT",
}

def classify(gene_name: str | None, product: str | None) -> tuple[str, str]:
    gn = (gene_name or "").strip()
    pr = (product or "").lower()
    if gn in ACQUISITION_GENES or any(k in pr for k in ACQUISITION_PRODUCT_KW):
        return "acquisition", f"matched acquisition ({gn or pr[:40]})"
    if gn in RESPONSIVE_GENES:
        return "responsive_other", f"known non-acquisition ({gn})"
    return "unclear", f"hypothetical/ambiguous ({gn or pr[:40]})"


def main() -> None:
    # aggregate distinct OGs with per-ecotype strain presence
    og = {}  # og_id -> dict
    hl_strains, ll_strains = set(), set()
    with GENES.open() as fh:
        for r in csv.DictReader(fh):
            (hl_strains if r["ecotype"] == "HL" else ll_strains).add(r["strain"])
            o = og.setdefault(r["cyanorak_og"], {
                "cyanorak_og": r["cyanorak_og"], "og_gene_name": r["og_gene_name"],
                "og_product": r["og_product"], "hl": set(), "ll": set()})
            (o["hl"] if r["ecotype"] == "HL" else o["ll"]).add(r["strain"])

    rows = []
    for o in og.values():
        cls, rationale = classify(o["og_gene_name"], o["og_product"])
        rows.append({
            "cyanorak_og": o["cyanorak_og"], "og_gene_name": o["og_gene_name"],
            "og_product": o["og_product"], "n_HL": len(o["hl"]), "n_LL": len(o["ll"]),
            "class": cls, "rationale": rationale,
        })
    rows.sort(key=lambda r: (r["class"], -(r["n_HL"] + r["n_LL"])))

    out = DATA / "p_og_classification.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["cyanorak_og", "og_gene_name", "og_product",
                                           "n_HL", "n_LL", "class", "rationale"])
        w.writeheader(); w.writerows(rows)

    log = []
    def L(m): print(m); log.append(m)
    n_hl, n_ll = len(hl_strains), len(ll_strains)
    L(f"panel: HL={n_hl} strains, LL={n_ll} strains; {len(rows)} distinct D.1.5 OGs")
    by_cls = defaultdict(list)
    for r in rows:
        by_cls[r["class"]].append(r)
    for cls in ("acquisition", "responsive_other", "unclear"):
        L(f"\n=== {cls}: {len(by_cls[cls])} OGs ===")
        L(f"  {'gene':14s} {'HL':>3s} {'LL':>3s}  product")
        for r in by_cls[cls]:
            L(f"  {str(r['og_gene_name']):14s} {r['n_HL']:>3} {r['n_LL']:>3}  {str(r['og_product'])[:60]}")
    # focused-subset ecotype summary
    acq = by_cls["acquisition"]
    L(f"\n[focused acquisition subset] {len(acq)} OGs")
    L(f"  universal (all {n_hl} HL & all {n_ll} LL): "
      f"{sum(1 for r in acq if r['n_HL']==n_hl and r['n_LL']==n_ll)}")
    L(f"  LL-only (present in >=1 LL, 0 HL): {[r['og_gene_name'] for r in acq if r['n_HL']==0 and r['n_LL']>0]}")
    L(f"  HL-only (present in >=1 HL, 0 LL): {[r['og_gene_name'] for r in acq if r['n_LL']==0 and r['n_HL']>0]}")
    L(f"\n[outputs] {out.relative_to(STEP_DIR)} ({len(rows)} rows)")
    (DATA / "02_classify_p_ogs.log").write_text("\n".join(log) + "\n")


if __name__ == "__main__":
    main()
