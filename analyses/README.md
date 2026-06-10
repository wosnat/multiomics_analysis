# analyses/

Your research output lives here — **one directory per analysis**. This folder
ships empty (just this README); each analysis is scaffolded by the
`research-methodology` skill when you start it.

The skill's `references/step-protocol.md` and `references/artifacts.md` own the
authoritative structure. In brief, an analysis directory looks like:

```
analyses/YYYY-MM-DD-HHMM-short_slug/
  paper.md                 # the running synthesis (grows one section per step)
  gaps_and_friction.md     # friction + tool gaps surfaced during the work
  .gitignore               # per-analysis ignores (created at scaffold)
  1_question/
    notebook.md            # append-only lab notebook + decide-gate checklist
  2_kg_entries/
    notebook.md
    scripts/ data/ figures/    # (qc_* prefix for QC artifacts)
  3_framing/  4_methods/  5_analyze/  6_evaluate/
    ...
```

The 6-step flow (question → KG entries → framing → methods → analyze → evaluate)
advances **do → show → explore → decide**, one commit per step at the decide
gate. Don't hand-scaffold this — let the skill drive it so the gates and
manifests stay consistent.

Commit the repo-root `usage/` logs alongside your analysis commits.
