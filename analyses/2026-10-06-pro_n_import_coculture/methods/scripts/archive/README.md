# Archived one-off scripts (not part of the pipeline)

These scripts do NOT go through `kg_fetch.fetch`. Some use the old offset paging (API review C1) or the
old `--pilot-dir` layout. They are kept only as a record of how earlier pilot artefacts were made.
Do not run them in place of the pipeline (`run_pipeline.py`).

- `00_schema_samples.py`, `01_smoke_raw_samples.py`: phase-1 schema inspection on 4 cyn genes.
- `p3c_diff_reference.py`: v0.4 → v0.5 reference-variant diff (pilot dir).
- `p4c_diff_step4.py`: v0.6 → v0.7 neighbour-class diff (pilot dir).
- `p4d_probe_refseq_tags.py`: one-off `gene_details` probe of TX50_RS tags (direct offset paging). It was
  superseded by the scripted no-coordinate list in `p3_group_systems.py`, a read-only run_cypher with a hard
  completeness assert (review I2).
