"""Verifier answer-key builder. All inputs transcribed from multiomics-kg MCP calls
(gene_neighbors anchors, gene_ontology_terms pfam/tcdb, metabolites_by_gene,
genes_by_metabolite). Computes adjacent-gene gaps, same-strand runs, neighbourhood
membership, and writes the two CSVs. Prints markdown neighbourhood tables."""
import csv
from pathlib import Path

OUT = Path(r"C:\Users\oweisberg\Documents\GitHub\multiomics_analysis\analyses\2026-10-06-pro_n_import_coculture\methods\data\answer_key")
WINDOW = 8

coords = {}
with open(OUT / "_coords_from_gene_neighbors.tsv", encoding="utf-8") as fh:
    for r in csv.DictReader(fh, delimiter="\t"):
        r["start"], r["end"] = int(r["start"]), int(r["end"])
        coords[r["locus_tag"]] = r
order = sorted(coords.values(), key=lambda r: r["start"])
idx = {r["locus_tag"]: i for i, r in enumerate(order)}

CASES = {
    "cyn": ["PMM0370", "PMM0371", "PMM0372", "PMM0373"],
    "urt_urease": ["PMM0963", "PMM0964", "PMM0965", "PMM0966", "PMM0967", "PMM0968",
                   "PMM0969", "PMM0970", "PMM0971", "PMM0972", "PMM0973", "PMM0974"],
    "amt1": ["PMM0263"],
    "dpp": ["PMM1049", "PMM1048", "PMM0421", "PMM0192"],
    "pst": ["PMM0710", "PMM0723", "PMM0724", "PMM0725"],
    "salY": ["PMM0913"],
    "fadD": ["PMM0402"],
}

# MED4 genes in a KEGG reaction with each metabolite (genes_by_metabolite, evidence_sources=['metabolism'])
METAB_GENES = {
    "kegg.compound:C00014": ["PMM0409", "PMM1670", "PMM1703", "PMM1304", "PMM0558", "PMM0825", "PMM0908",
                             "PMM0951", "PMM1358", "PMM1687", "PMM0037", "PMM0100", "PMM0184", "PMM0244",
                             "PMM0257", "PMM0357", "PMM0373", "PMM0408", "PMM0495", "PMM0695", "PMM0821",
                             "PMM0918", "PMM0920", "PMM0963", "PMM0964", "PMM0965", "PMM1265", "PMM1298",
                             "PMM1446", "PMM1512", "PMM1577", "PMM1668", "PMM1669", "PMM1689", "PMM1690",
                             "PMM1691"],
    "kegg.compound:C00086": ["PMM0963", "PMM0964", "PMM0965", "PMM1686"],
    "kegg.compound:C01417": ["PMM0373"],
    "chebi:14654": [],
    "kegg.compound:C00088": [],
    "kegg.compound:C07044": [], "kegg.compound:C14415": [],
    "kegg.compound:C00218": [], "kegg.compound:C00797": [], "kegg.compound:C20292": [],
    "kegg.compound:C00396": [],
    "chebi:195181": [], "chebi:27138": [], "kegg.compound:C00284": [], "kegg.compound:C00306": [],
    "kegg.compound:C10172": [],
    "kegg.compound:C00032": ["PMM0525", "PMM0448", "PMM1594"],
    "kegg.compound:C00430": ["PMM0215", "PMM0483"],
    "kegg.compound:C00487": [], "kegg.compound:C04114": [],
}
assert len(METAB_GENES["kegg.compound:C00014"]) == 36  # genes_by_metabolite gene_count for ammonia


def neighbourhood(case_genes):
    s = set()
    for g in case_genes:
        i = idx[g]
        for j in range(max(0, i - WINDOW), min(len(order), i + WINDOW + 1)):
            s.add(order[j]["locus_tag"])
    return sorted(s, key=lambda t: coords[t]["start"])


def gaps_table(case, case_genes):
    nb = neighbourhood(case_genes)
    # split into contiguous loci (adjacent in global order)
    loci, cur = [], [nb[0]]
    for t in nb[1:]:
        if idx[t] == idx[cur[-1]] + 1:
            cur.append(t)
        else:
            loci.append(cur); cur = [t]
    loci.append(cur)
    lines = []
    for locus in loci:
        lines.append(f"\n| locus_tag | gene | strand | start | end | gap_to_previous_bp | case gene | run_id |\n|---|---|---|---|---|---|---|---|")
        run = 0
        for k, t in enumerate(locus):
            r = coords[t]
            if k == 0:
                gap = ""
                run += 1
            else:
                p = coords[locus[k - 1]]
                gap = r["start"] - p["end"] - 1
                if r["strand"] != p["strand"]:
                    run += 1
            lines.append(f"| {t} | {r['gene_name'] or '-'} | {r['strand']} | {r['start']} | {r['end']} | {gap} | {'YES' if t in case_genes else ''} | {run} |")
    return nb, "\n".join(lines)


def can_use(case, mid):
    nb = set(neighbourhood(CASES[case]))
    genes = METAB_GENES[mid]
    if not genes:
        return "no", ""
    co = [g for g in genes if g in nb]
    if co:
        return "co-located", ";".join(co)
    return "elsewhere in genome", ";".join(genes)


if __name__ == "__main__":
    for case, genes in CASES.items():
        nb, tab = gaps_table(case, genes)
        print(f"\n### {case}  (neighbourhood n={len(nb)})")
        print(tab)
        for mid, gl in METAB_GENES.items():
            hits = [g for g in gl if g in set(nb)]
            if hits:
                print(f"  metabolism genes in neighbourhood for {mid}: {hits}")
