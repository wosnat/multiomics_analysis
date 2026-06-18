# Gaps and friction log

Methodology / KG / tooling friction encountered during this analysis.
Distinct from decisions (which live in each step's notebook.md).

## gene_ontology_terms is single-organism — multi-organism string errors

`gene_ontology_terms` requires a single organism. Passing a substring that matches
several (e.g. `organism="Alteromonas macleodii"` → all 7 strains) raises
"matches multiple organisms" and returns nothing. In an ad-hoc verification call
this surfaced as an error I initially overlooked, leading to an overstated
"verified" claim (step 5, EC-missing check). In a batch script it would silently
drop a whole organism's annotations.

**How to apply:** always pass a unique organism (a strain code like `MIT1002`, or a
full `preferred_name`) to `gene_ontology_terms`. When iterating over strains, group
by strain and pass each strain's code — which `exoenzyme_lib.classify` does, so the
genome-background run was unaffected. Verify a tool call returned rows (not an
error / empty `no_terms`) before asserting a result from it.
