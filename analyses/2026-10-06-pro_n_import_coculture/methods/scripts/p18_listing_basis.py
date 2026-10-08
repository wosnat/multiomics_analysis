"""Step 9 (v1.6.0, researcher decision 2026-10-08): dedicated vs broad listing per (system, N compound class).
Context only: nothing is removed. No KG calls.

Pairs: (system, compound class) from rows with substrate_depth most_specific, not lumping, system tier High/Medium,
  compound class one of the named N classes (not unclassified).
v1.6.1: efflux-annotated systems never get a Q-role-only dedicated call (broad, "Q.1 only, efflux-annotated");
  dedicated_basis (keyword | Q-role only); dedicated_also_for (other classes the same system is dedicated for).
Columns: substrate_breadth (distinct equiv_groups at most_specific depth, non-lumping, non-currency, all rows of the
  system) and substrate_breadth_N (of those, contains_N); listing_basis = nt.listing_basis (keyword on member
  product / gene name, or corresponding curated Cyanorak Q role) -> "dedicated" | "broad listing"; basis_detail.
Expected checks (coordinator, 2026-10-08) evaluated per strain on the pairs present.
Inputs (<out-dir>): p12_<tag>_system_substrates_classified.csv, p11_<tag>_systems.csv, p2_<tag>_gene_roles.csv,
  p3_<tag>_gene_systems_<REF>.csv.
Outputs: ../p18_class_keyword_map.csv (shared), p18_<tag>_listing_basis.csv, p18_<tag>_listing_table.csv,
  p18_<tag>_expected_checks.csv, p18_<tag>_summary.json.
Usage: ... p18_listing_basis.py --organism "Prochlorococcus MED4" --out-dir <dir>
"""
import argparse
import json
from pathlib import Path

import pandas as pd

from common import REF, nt, write_summary

N_CLASSES = ["ammonium", "urea", "cyanate", "nitrite", "nitrate", "peptides", "amino acids", "amino sugars",
             "polyamines", "nucleobases/nucleosides", "osmolytes", "amines"]
# (class, gene name or locus tag of a member, expected basis)
EXPECTED = [("ammonium", "amt1", "dedicated"), ("ammonium", "ktrA", "broad listing"),
            ("ammonium", "nhaS", "broad listing"),
            ("amino acids", "sul1", "broad listing"), ("amino acids", "sul3", "broad listing"),
            ("nitrate", "sul1", "broad listing"), ("nitrate", "sul3", "broad listing"),
            ("peptides", "dppA", "dedicated"), ("urea", "urtA", "dedicated"),
            ("urea", "putP", "broad listing"), ("urea", "PMN2A_RS08290", "broad listing")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--organism", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    d = Path(a.out_dir)
    tag = a.organism.split()[-1].lower()
    nt.class_keyword_table().to_csv(d.parent / "p18_class_keyword_map.csv", index=False)
    cls = pd.read_csv(d / f"p12_{tag}_system_substrates_classified.csv", low_memory=False)
    sy = pd.read_csv(d / f"p11_{tag}_systems.csv").set_index("system_id")
    roles = pd.read_csv(d / f"p2_{tag}_gene_roles.csv").set_index("locus_tag")
    gs = pd.read_csv(d / f"p3_{tag}_gene_systems_{REF}.csv")
    mem = gs.groupby("system_id").locus_tag.agg(lambda s: sorted(s)).to_dict()
    breadth = nt.substrate_breadth(cls)
    cls["tier"] = cls.system_id.map(sy.tier)
    r = cls[(cls.substrate_depth == "most_specific") & ~cls.is_lumping.map(nt.to_bool)
            & cls.tier.isin(["High", "Medium"]) & cls.compound_class_final.isin(N_CLASSES)]
    rows = []
    for (sid, c), g in r.groupby(["system_id", "compound_class_final"]):
        loci = mem[sid]
        names = [roles.gene_name.get(x) for x in loci]
        prods = [roles["product"].get(x) for x in loci]
        qs = [q for x in loci for q in nt.parse_list(roles.cyanorak_q_roles.get(x)) if q != nt.NO_BASIS]
        eff = bool(sy.efflux_annotated[sid])
        basis, why = nt.listing_basis(c, names, prods, qs, efflux=eff)
        b = breadth.get(sid, (0, 0))
        rows.append({"strain": tag, "system_id": sid, "member_names": sy.member_names[sid], "member_loci": "|".join(loci),
                     "tier": sy.tier[sid], "known_false_positive": bool(sy.known_false_positive[sid]),
                     "compound_class": c, "class_groups_listed": "|".join(sorted(set(g.metabolite_name.astype(str)))),
                     "substrate_breadth": b[0], "substrate_breadth_N": b[1],
                     "listing_basis": basis, "basis_detail": why,
                     "dedicated_basis": nt.dedicated_basis(why) if basis == "dedicated" else nt.NO_BASIS,
                     "efflux_annotated": eff,
                     "member_products": " | ".join(map(str, prods)),
                     "member_q_roles": "|".join(sorted(set(q.replace("cyanorak.role:", "") for q in qs))) or nt.NO_BASIS})
    L = pd.DataFrame(rows).sort_values(["compound_class", "listing_basis", "tier", "system_id"])
    # v1.6.1: same system dedicated for more than one class (e.g. proV/W/X, proP: amino acids via 'proline' and
    # osmolytes) -- reported, not changed
    ded_cls = L[L.listing_basis == "dedicated"].groupby("system_id").compound_class.agg(lambda s: sorted(set(s)))
    L["dedicated_also_for"] = [("|".join(c for c in ded_cls.get(s, []) if c != k) or nt.NO_BASIS)
                               if b == "dedicated" else nt.NO_BASIS
                               for s, k, b in zip(L.system_id, L.compound_class, L.listing_basis)]
    L.to_csv(d / f"p18_{tag}_listing_basis.csv", index=False)
    tab = []
    for c in N_CLASSES:
        x = L[L.compound_class == c]
        rec = {"strain": tag, "compound_class": c}
        for basis, key in (("dedicated", "dedicated"), ("broad listing", "broad")):
            y = x[x.listing_basis == basis]
            yk = y[~y.known_false_positive]
            rec[f"{key}_H"] = int((yk.tier == "High").sum())
            rec[f"{key}_M"] = int((yk.tier == "Medium").sum())
            rec[f"{key}_systems"] = " || ".join(f"{s.member_names} ({s.tier}{', known FP' if s.known_false_positive else ''})"
                                                for s in y.itertuples())
        tab.append(rec)
    T = pd.DataFrame(tab)
    T.to_csv(d / f"p18_{tag}_listing_table.csv", index=False)
    chk = []
    for c, who, exp in EXPECTED:
        x = L[(L.compound_class == c) & L.member_names.str.contains(rf"(?:^|\||:){who}(?:\||:|$)", regex=True)]
        if x.empty:
            chk.append({"strain": tag, "compound_class": c, "member": who, "expected": exp, "observed": "pair not present",
                        "system_id": None, "matches": None})
        for s in x.itertuples():
            chk.append({"strain": tag, "compound_class": c, "member": who, "expected": exp, "observed": s.listing_basis,
                        "system_id": s.system_id, "basis_detail": s.basis_detail, "matches": s.listing_basis == exp})
    C = pd.DataFrame(chk)
    C.to_csv(d / f"p18_{tag}_expected_checks.csv", index=False)
    summ = {"organism": a.organism, "pairs": int(len(L)), "by_basis": L.listing_basis.value_counts().to_dict(),
            "mismatches": C[C.matches == False].to_dict("records"),  # noqa: E712
            "not_present": C[C.observed == "pair not present"][["compound_class", "member"]].to_dict("records")}
    write_summary(d / f"p18_{tag}_summary.json", summ)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main()
