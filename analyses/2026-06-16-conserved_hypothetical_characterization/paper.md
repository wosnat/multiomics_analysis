# Characterization of 14 core conserved-hypothetical Prochlorococcus gene families

## Question

For each of the **14 core conserved-hypothetical *Prochlorococcus* ortholog
families** — the families found to be both broadly **and** prominently
differentially expressed in the selection analysis
(`analyses/2026-06-16-conserved_hypothetical_de/`,
`6_evaluate/data/handoff_shortlist.csv`, rows with `core14 = True`) — assemble a
**characterization dossier** from the knowledge graph that maximizes interpretive
power for **future omics** work.

The 14 families are treated as **14 independent entities**, not a related set: the
goal is not to find a shared pathway or module, but to give each gene family enough
KG-held context that, when it reappears in a future dataset, it can be interpreted
rather than ignored. Incidental overlaps (two families sharing a neighbor or a
co-expression cluster) are noted where they occur but are not the objective.

Each dossier pairs the family's existing **DE response fingerprint** — breadth,
prominence, and direction-by-treatment, carried forward from the selection analysis
— with everything the KG holds about it:

- **Cross-organism homologs** — homologs in *Alteromonas* or other KG organisms
  beyond *Prochlorococcus*.
- **Conserved genomic neighborhood** — the genes flanking family members, and
  whether the neighborhood is conserved across strains.
- **Co-expression / cluster membership** — which co-expression clusters members
  fall in and what characterized genes share them (guilt-by-association).
- **Ontology / domains / sequence** — GO terms, protein domains, and sequence
  features (length, membrane/secreted signals) for members and their neighbors.
- **Other derived metrics** — any KG-held per-gene derived metrics.
- **Publication mentions** — whether any source publication discusses these genes
  directly.

**Deliverable:** one reference table (one row per family, columns = the
characterization axes + the DE fingerprint) plus a readable per-family card —
built as a lookup resource for future analyses. Results are additionally surfaced
in the repo-level interactive dashboard (`dashboard/`) as a `characterization`
section that lets a researcher pick a family and view its DE fingerprint alongside
its KG characterization panels; the static paper and figures remain the source of
record.

## Background

<!-- populated at step 2 decide -->

## Methods

<!-- populated at step 4 decide -->

## Results

<!-- populated at step 5 decide -->

## Discussion

<!-- populated at step 6 decide -->

## References

<!-- resolved via list_publications as the analysis cites them -->
