# Gaps and friction log

Transitional log of methodology / KG / tooling friction for
`2026-10-06-pro_n_import_coculture`. Append-only. Distinct from
decisions (which live in `proposal.md` / milestone `notebook.md`).

---

### 2026-10-06 — superpowers plugin silently absent in a template clone (template / tooling)

**What happened.** At the start of the Plan phase the arc calls
`superpowers:brainstorming`, but no `superpowers:*` skill was available in the
session. `~/.claude/plugins/installed_plugins.json` held a single install of
`superpowers@claude-plugins-official` 6.0.0 with `scope: project` and
`projectPath: ...\GitHub\multiomics_research_template` — the template's own
folder. This repo (`...\GitHub\multiomics_analysis`) ships
`enabledPlugins: {"superpowers@claude-plugins-official": true}` in its committed
`.claude/settings.json`, but has no install record for its own path, so the
plugin failed to load. `/reload-plugins` reported "0 plugins · 1 error" and
`/plugin` showed no error text. `./scripts/preflight.sh` was green throughout —
it checks the explorer/KG/API triple, not the skills the arc depends on.

**Workaround.** `/plugin` is not available in the VS Code extension; installed
from a shell instead: `claude plugin install superpowers@claude-plugins-official
--scope user` → 6.4.1 at user scope; `/reload-plugins` → 1 plugin, 15 skills.

**Downstream impact.** Template — any fork cloned under a different folder name
loses the arc's required skills with no visible failure. Candidate fixes (one
occurrence, so a note, not yet a change): README setup step installs superpowers
at user scope; preflight checks that the `superpowers:*` skills resolve.

### 2026-10-06 — superpowers version drift: brainstorming 6.4.1 ≠ the 6.0.0 the arc was written against (methodology / tooling)

**What happened.** The user-scope reinstall pulled superpowers **6.4.1**
(the arc's brainstorming override was written against 6.0.0). 6.4.1's
brainstorming adds a three-way path classification (spike / bounded /
architectural) announced before the first question, a "write back your
understanding" step, and a HARD-GATE whose architectural path requires a written
implementation plan reviewed before any implementation. The research-methodology
override (research-notebook.md — "Using brainstorming for the Plan phase") names
none of these.

**Workaround.** Mapped by hand: an analysis = the architectural path;
`proposal.md` = the written spec; the override's "terminal action = begin the
Run phase, not writing-plans" also replaces the HARD-GATE's
implementation-plan-review step. The write-back-understanding step fit the Plan
phase well (it surfaced the "fed vs. hungrier" ambiguity early).

**Downstream impact.** Methodology — the override should either pin a superpowers
version or name the 6.4.x path classification explicitly, so the mapping isn't
re-derived each run. One occurrence → note.

### 2026-10-06 — `coculture_partner` filter misses experiments where coculture is the background, not the treatment (KG metadata / tool behaviour)

**What happened.** Grounding with `list_experiments(organism="Prochlorococcus",
coculture_partner="Alteromonas")` returned 5 experiments, all RNA-seq. The
Weissberg 2025 study (10.1101/2025.11.24.690089) has 8 more experiments run *in*
coculture — N-starvation vs. exponential time courses, RNA-seq and proteomics, for
MED4 and HOT1A3, one coculture arm and one axenic arm each — that carry
`background_factors: ["coculture", ...]` but `coculture_partner: null`. They are
invisible to a `coculture_partner` filter, so the first pass reported "no
*Prochlorococcus* proteomics in coculture with Alteromonas", which was wrong.
Caught only because the researcher asked "what about proteomics?". The
García-Fernández glucose proteomics (10.1128/spectrum.03275-22) has the same
shape on the *Prochlorococcus* side.

**Workaround.** Enumerate by publication (`publication_dois=[...]`) and by
`background_factors=["coculture"]`, not by `coculture_partner` alone.

**Downstream impact.** KG/tooling — `coculture_partner` is populated only when
coculture is the treatment. Either populate it whenever the culture is a
coculture, or have the `coculture_partner` docs say it is treatment-only and
point at `background_factors`. Methodology — kg-rules "Scoping" could add:
enumerate coculture data by both fields.

### 2026-10-06 — Grounding coverage check leaked results into the Plan phase (methodology)

**What happened.** To confirm that MED4's N-import proteins are detected in the
Weissberg 2025 proteomics, I called `differential_expression_by_gene` on 12 locus
tags. The tool has no "detection only" mode, so it returned fold changes, and the
late-coculture pattern (cyanate import system top-ranked) was visible before the
hypothesis, validation set and expected-negative were written. Any framing
written afterwards risks being fit to data already seen.

**Workaround.** Disclosed in `proposal_notebook.md` (grounding item 7). The
hypothesis is taken from the anchor paper's abstract (ammonium), not from the
observed pattern. The proposal flags the cyanate observation as seen-before-lock,
so it can't count as a confirmed prediction.

**Downstream impact.** Methodology — the Plan phase says "ground in KG counts" but
gives no rule for coverage checks that unavoidably return effect sizes. Options:
check coverage with `summary=True` (counts only), or declare any values seen in
`proposal_notebook.md`. One occurrence -> note.

### 2026-10-06 — TCDB most-specific substrate for MED4's cyn system is nitrate/nitrite (KG annotation)

**What happened.** `metabolites_by_gene(..., substrate_depth=['most_specific'])`
puts `cynA`/`cynB`/`cynD` (PMM0370-0372) under `tcdb:3.A.1.16.1` "four component
nitrate/nitrite porter", with cyanate only on `cynB` via `3.A.1.16.2`. MED4 has no
nitrate or nitrite assimilation, and the system sits beside cyanase `cynS`. Read
off TCDB alone, the cyn system would be called a nitrate/nitrite importer, and
here it is the top-ranked late-coculture signal.

**Workaround.** The methods milestone's candidate-set rule fuses TCDB with gene
neighbourhood and assimilation capacity: a substrate counts only if the organism
can assimilate it or a co-located enzyme acts on it.

**Downstream impact.** KG — the NitT/TauT family (`3.A.1.16`) is genuinely
bispecific, so this is an annotation-granularity limit, not a bug. A
"substrate-plausible-given-genome" flag would help. Methodology — transporter
substrate calls for cross-feeding need a fusion rule. Round 1 logged TCDB
coarseness for ABC transporters; this is the same limit in a different family,
i.e. a second occurrence.

### 2026-10-06 — `list_metabolites` organism reach is flat across organisms under transport evidence (tool behaviour)

**What happened.** `list_metabolites(organism_names=["Prochlorococcus MED4"],
evidence_sources=["transport"], elements=["N"], summary=True)` returned 510
N-metabolites, with `top_organisms` at 508-510 for every organism listed (MED4,
HOT1A3, EZ55, Ruegeria, Shewanella...). The ABC-superfamily rollup makes
organism-level transport reach uninformative. The envelope gave no warning (the
docs do explain the plateau, under `metabolites_by_gene`).

**Workaround.** Gene-anchored `metabolites_by_gene(..., substrate_depth=['most_specific'])`.

**Downstream impact.** Tooling — `list_metabolites` could carry the same
"inherited rows dominate" warning that `genes_by_metabolite` fires. Minor.

### 2026-10-07 — Proposal critic exposed three framing gaps the self-review missed (methodology)

**What happened.** The interpretation-only proposal critic returned no Blockers and 8 Concerns.
Three of them are gaps the framing floor and the author's self-review didn't anticipate, and
the next analysis needs to know about them:
1. **Duration confound in a per-culture design.** Comparing late coculture (d60/89) with early
   axenic (d14) mixes partner effect with starvation length. The floor's five items don't prompt
   "is the reference matched in time?". Round 1 hit the sibling trap (per-culture contrast read as
   between-culture).
2. **The cross-checks couldn't play the role assigned to them.** All non-anchor experiments are
   N-replete, so they can't replicate an N-limited finding, and the proposal's own expected-negative
   predicted they'd show nothing. This was visible in the grounding (all `exponential`), but the
   framing labelled them "cross-check" without asking what each experiment *can* confirm.
3. **A disclosed peek still left the hypothesis unfalsifiable.** Disclosing the peek wasn't
   enough; the hypothesis had to be rebuilt around blind predictions (RNA) and a primacy test.

**Workaround.** All fixed in `proposal.md` (dispositions in `proposal_critical_review.md`).

**Downstream impact.** Methodology:
- (1) and (2) are the cross-experiment comparability gap from round 1 again, in a different form
  (round 1: FDR family sizes; here: timepoint matching and N status). Watch-list 6 now has its
  second occurrence. A candidate floor item: "for each experiment used, what role it plays
  (answers / consistency check / control) and what it can and cannot confirm".
- (3) is new: when a peek happened, the framing needs at least one blind prediction.


### 2026-10-07 — MCP usage logging silently off: `jq` not installed (template / tooling)

**What happened.** About 30 `multiomics-kg` MCP calls in this Plan phase left
`usage/multiomics-kg-usage.jsonl` untouched; it is unchanged since its last commit (2026-09-04).
A manual run of `hooks/log-mcp-usage.sh` with a sample event exits 0 without writing.
`command -v jq` finds nothing. The hook is written to "degrade silently (skip logging)" when jq is
missing, so nothing tells the researcher that the usage logs the README asks them to commit are
empty. `scripts/preflight.sh` was green and doesn't check jq.

**Workaround.** None yet (installing jq is the researcher's call). This Plan phase's KG queries are
recorded by hand in `proposal_notebook.md`.

**Downstream impact.** Template — the silent degrade is a reasonable choice for not blocking
analysis, but preflight should warn when jq is missing. Otherwise the usage data the tools team
relies on silently stops. Second template-setup gap this run that preflight passes over (see the
superpowers plugin entry), so a note pointing at one fix: preflight should check the arc's runtime
dependencies, not only the KG/API triple.

### 2026-10-07 — New control rules conflicted with existing ones; caught only by the delta pass (methodology)

**What happened.** Adding controls at the researcher's request introduced a rule ((c): an N class
must out-rank every non-N import system) that contradicted the new expected-negative written in
the same edit (which allows a non-N system to stand out because of real secondary limitation). A
second rule (the calibration gate) had no stated meaning for a pass. The author wrote both in one
pass and didn't see the interaction; the delta critic did.

**Workaround.** Fixed (dispositions D1–D7 in `proposal_critical_review.md`).

**Downstream impact.** Methodology: evidence that "a delta pass whenever claims grow" holds at
the proposal level too, not only at Run milestones. step-protocol currently describes delta passes
for milestones. One occurrence → note.

### 2026-10-07 — The author's rules kept drifting toward the hypothesis gene (methodology)

**What happened.** Three times in one Plan phase, a rule the author wrote in good faith would
structurally have favoured `amt1`, the ammonium hypothesis gene:
1. the first tier ladder ("TCDB homology = high"), caught by the researcher's domain question;
2. the "stands out" comparison without a duration guard, caught by the first critic pass;
3. the supports-only corroboration fraction, which also contained an arithmetic error (a
   Blocker), caught by the second delta pass.

Each time the bias came from a structural asymmetry (single-gene vs. multi-subunit systems;
annotation pipeline; denominator size), not from intent.

**Workaround.** Each fixed; the ordering now uses only the primary label and the late protein
percentile.

**Downstream impact.** Methodology: when a hypothesis names a specific gene, every scoring or
ranking rule should be checked for "does this rule's *structure* favour that gene's shape
(single gene, annotation source, number of applicable checks)?" before locking. That check could
go on the self-review list. One analysis, three occurrences of the same mechanism → worth raising
at the round-2 review.

