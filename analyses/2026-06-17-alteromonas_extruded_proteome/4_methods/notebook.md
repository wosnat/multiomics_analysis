# Step 4 — Methods (ad-hoc module, driven by MIT1002 vesicle)

## Module: `extruded_og.py`

Three functions implementing the step-3 framing:

- `extract_route_genes(strain, route, conn)` — pulls genes measured extruded.
  - vesicle: `genes_by_numeric_metric(prop_abund_mvs_percent, compartment=vesicle)`,
    membership = has an MV-abundance edge.
  - secreted: same tool on `exoproteome_detection_replicates` with
    **`min_value=1`** — the tested-absent guard from step 3 (value-0 edges were
    looked for, not detected; they must not count as secreted).
- `map_genes_to_og(locus_tags, conn)` — `gene_homologs(source="eggnog")`, keeps
  the most-specific (lowest specificity_rank) group per gene; genes with no
  eggnog group reported as strain-unique (og_group_id = None).
- `build_og_catalogue(gene_og_df)` — collapses to one row per OG with routes,
  both_routes flag, n_strains recurrence, per-strain locus tags. Sorted
  both-routes / recurrent first.

Highest-level tools used (Rule 5): `genes_by_numeric_metric`, `gene_homologs` —
no hand-rolled Cypher.

## Driving-example run (MIT1002 vesicle) — funnel `[KG]`

```
MV-cargo genes (prop_abund_mvs_percent present): 52
genes mapped to an eggnog OG:                    52
strain-unique (no OG):                            0
distinct extruded OGs:                           52
```

**Positive control passes:** both MIT1002 TonB-dependent receptors
(MIT1002_01157, MIT1002_03495) survive into the catalogue, mapped to
Alteromonadaceae-level OGs (`eggnog:4651V@72275`, `eggnog:46A4N@72275`).

Top OGs: TonB-dependent receptors, EF-Tu, OmpA family, MotA/TolQ/ExbB proton
channel (TonB energiser), 50S ribosomal L5, esterase/phytase. Outer-membrane +
TonB machinery dominate, with ribosomal/EF-Tu as the flagged cytoplasmic
component (step-3 caveat 2).

Note: one OG resolved at Proteobacteria level (`...@1224`) — that gene had no
Alteromonadaceae-level group, so most-specific-available was used. n_strains = 1
throughout here because the example is a single strain; cross-strain recurrence
is computed in step 5 when all 7 are combined.

## Outputs

- `data/mit1002_og.csv` — 52-OG catalogue (driving example)
- `data/mit1002_genes_og.csv` — 52 gene→OG rows

## Not yet exercised → step 5 watch-item

The **secreted path (`min_value=1` on EZ55)** is not hit by this vesicle example.
Step 5 must confirm it filters the 234-gene tested-absent table down to the
actually-detected secreted set before trusting the combined catalogue.

## Decide

- [x] Module implements the locked framing (routes, OG bridge, recurrence)
- [x] Driving example runs clean; funnel logged; 0 unmapped
- [x] Positive control (TonB receptors) passes
- [x] Outputs frozen to data/
- [x] Secreted-path validation flagged for step 5
