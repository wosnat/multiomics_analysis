# EZ55 module scoring — run manifest (facts only)

Two pCO2 presence contrasts (coculture-vs-axenic, MIT9312 partner), both `significant_only` / edgeR. Committed `score_modules.py` reused; `scope="significant_only"` so ranking + null live within the significant set. The two arms are the **same lab/strain/cultures at two CO2 levels** → pCO2 agreement is an internal consistency check, NOT two independent supports.

## EZ55 transporter table (see ez55_build_manifest.md)

- 35 organic-C importer modules over 54 systems; clean inorganic control set (N/P excluded).

## Per-arm DE pulls

- **400ppm**: 419 genes, scope=['significant_only'], sign 111 neg / 308 pos (26.49% neg), status={'significant_up': 308, 'significant_down': 111, 'not_significant': 0}. (Both signs present → sign not lost; the 40–55%-negative all-genes check does not apply to a significant_only table.)
- **800ppm**: 188 genes, scope=['significant_only'], sign 84 neg / 104 pos (44.68% neg), status={'significant_up': 104, 'significant_down': 84, 'not_significant': 0}. (Both signs present → sign not lost; the 40–55%-negative all-genes check does not apply to a significant_only table.)

## Modules called up (q<0.10)

- **400ppm** (0): []
- **800ppm** (1): ['Fe(3+) dicitrate']
- **Called up in BOTH arms (pCO2-agreement, internal consistency — one strain-partner support): 0** — []

## significant_only sparsity (weakness flag)

- **400ppm**: n_systems_detected per module — median 0, max 1, modules with 0 detected systems: 28 of 35. Most modules have few/no systems with a gene in the significant set → thin, presence-weighted evidence.
- **800ppm**: n_systems_detected per module — median 0, max 1, modules with 0 detected systems: 32 of 35. Most modules have few/no systems with a gene in the significant set → thin, presence-weighted evidence.

## Validation (median up-pct within the significant set)

- **400ppm**: motility n=18 med=0.1352; peptidase n=10 med=0.5742; ribosomal n=14 med=0.1926; glcB EZ55_02804=not in sig set
- **800ppm**: motility n=7 med=0.6791; peptidase n=2 med=0.5668; ribosomal n=5 med=0.5882; glcB EZ55_02804=not in sig set

## Anomalies / flags (facts)

- `significant_only` scope: ranking + permutation null are within the significant set (~419 / ~188 genes), not genome-wide — weaker, presence-weighted; n_systems_detected is low for most modules.
- The two arms are not independent supports (same cultures, two CO2 levels); reported as a pCO2 internal-consistency agreement count.
- `glcB` may be absent from a significant_only table (no row unless significant) — reported as 'not in sig set' where so.