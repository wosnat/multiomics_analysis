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


### 2026-10-07 — Inline shell scripts with prose break on quoting (process / tooling)

**What happened.** Three edits to the analysis' markdown files failed when the update was
passed as an inline `python -c` or heredoc in the Bash tool: apostrophes and double quotes in
the prose closed the shell string, and nothing ran. Each cost a retry.

**Workaround.** Write the update script to the scratchpad with the file-writing tool, then run
it, or use the edit tool directly.

**Downstream impact.** Process only. For prose-heavy notebook and log edits, prefer the edit tool
or a script file over inline shell. Minor.

### 2026-10-07 — Metabolite IDs split across namespaces; can_use can read an ID gap as absence (KG data)

**What happened.** The verifier's answer key (`methods/data/answer_key/pilot_answer_key.md`)
found the same compound under two Metabolite IDs. Nitrate appears as `chebi:14654` (what MED4's
cyn transporter maps to via TCDB) and as `kegg.compound:C00244` (attached to response regulators
`rpaA`, `rpaB`, `phoB`, `sasA` via `tcdb:3.E.1` at score 0–0.2). Pantothenate: `chebi:14739` has
no metabolism genes; `C00864` has `coaX`, `panC-cmk`. A "can this strain use it" check that
matches IDs exactly reports "no" for a substrate whose reaction genes sit under the other ID.

**Workaround.** The `can_use` check must match on cross-referenced identity (shared `mnxm_id` /
ChEBI / KEGG xrefs from `list_metabolites`), not on the exact ID string. For nitrate, "no" holds
under both IDs (no MED4 metabolism gene).

**Downstream impact.** KG — the transport arm (TCDB substrates, ChEBI-keyed) and the metabolism
arm (KEGG-keyed) don't always meet on one node. This silently breaks any transport ↔ metabolism
join. A merged node, or an "equivalent_ids" field, would fix it. Methodology — any cross-arm
join needs an xref-harmonisation step. **This is the kind of wrong-API-use error the
researcher's step-by-step pilot was designed to catch.**

### 2026-10-07 — TCDB annotation oddities seen in the answer key (KG data, minor)

**What happened.**
- **Depth looks inverted for the PepT family on `dpp`:** generic "peptide" / "Oligopeptide"
  arrive only as `inherited`, while the `most_specific` set is heme, EDTA, 5-aminolevulinate,
  stachydrine, bradykinin, Ala-Ala and tripeptide.
- **Inherited rows on superfamily-only genes (`salY`) report the gene's own attachment**
  (`tcdb:3.A.1`) as their family, so the row doesn't show where the substrate came from.
- **Some TCDB names are missing or truncated:** `tcdb:4.C.1.1` and bare `1.A.1.x` / `2.A.88.x`
  show the ID as the name; `3.A.1.4.4` reads "The high-affinity (".
- **`urtE` carries an extra score-0, single-source `tcdb:1.B.42` hit.**

**Workaround.** None needed for the build; these are surfaced as-is in the flag columns.

**Downstream impact.** KG — depth semantics on PepT and family names are worth a check
upstream. Peptide-class grouping at the decide gate must look at inherited rows too.

### 2026-10-07 — `genes_by_ontology` default size filters silently undercounted a Plan-phase number (tool behaviour / API misuse)

**What happened.** Plan grounding item 8 reported 57 MED4 genes in the BRITE transporters tree.
Methods pilot step 1, calling with `min_gene_set_size=1, max_gene_set_size=None`, found **86**.
The defaults (`min_gene_set_size=5`, `max_gene_set_size=500`) drop terms outside that size range
without a warning in the envelope (no `filtered_out` entry, no warning). 10 of the 12 role Pfams
have only 1–2 MED4 genes, so a Pfam-based gene collection with defaults would also have lost
most of them.

**Workaround.** Set both size filters explicitly in every enumeration call. Grounding item 8 is
corrected in `proposal_notebook.md`; no proposal claim depended on the 57.

**Downstream impact.** Tooling: the defaults suit enrichment (where tiny terms are noise) but
mislead enumeration. The envelope should report terms dropped by size, or warn when a
`term_ids` / `tree` call drops terms. Methodology: this is the failure class the researcher's
step-by-step pilot was set up to catch ("false results because the API was called
incorrectly"). It was caught at step 1, in a number from the Plan phase.

### 2026-10-07 — 91 MED4 genes have no coordinates; `gene_neighbors` large window crashes the server (KG data / tool)

**What happened.** Building genome-wide runs (methods pilot step 3) needed coordinates for every
MED4 gene. A single `gene_neighbors(window=10000)` call failed with a server
`MemoryPoolOutOfMemoryError`. A tiled sweep (window 250, 8 calls) + `gene_details` reached 1,877
of 1,973 genes. **91 genes exist in the KG with no coordinate fields at all** (e.g. `cyabrB2`
PMM0573, `hli` PMM0815, `petL` PMM1718); 5 more weren't reached. List:
`methods/data/pilot/raw/p3_med4_genes_outside_sweep.csv`.

**Workaround.** Tiled sweep. No transporter gene is affected; uncoordinated genes can't count as
opposite-strand interlopers or as neighbour candidates, and step 4 must report them rather than
skip them silently.

**Downstream impact.** KG — coordinates missing on ~5% of MED4 genes; a genome-coordinates
listing tool (or a `gene_details` paging by contig) would avoid the sweep. Tool — `gene_neighbors`
should cap the window or fail gracefully rather than exhausting server memory.

### 2026-10-07 — The two nitrate nodes share no cross-reference at all (KG data)

**What happened.** Following up the answer key's ID-split finding, pilot step 4 fetched
`list_metabolites` xrefs for all 528 enzyme-side N metabolites. Nitrate `kegg.compound:C00244`
(ChEBI 25545 / MNXM732399) and `chebi:14654` (ChEBI 14654 / MNXM732398) share **no** ChEBI,
MetaNetX or InChIKey identifier; only the name matches. Across the 528 metabolites, only two
groups are linked by a shared ID (O-phospho-L-homoserine C01102 = C05702; and apo-ACP C03688 =
lipoyl-carrier protein C16240, which is a generic-protein ID collision, not a real equivalence).

**Workaround.** A name-based soft link (`link_basis = name_soft`), shown for every group it creates.
Expected-negative 1 (no usable nitrate/nitrite route in MED4) rests on this link and is labelled
accordingly.

**Downstream impact.** KG: the transport arm (ChEBI-keyed TCDB substrates) and the metabolism arm
(KEGG-keyed reactions) can't be joined reliably by ID for at least nitrate, so any cross-arm join
silently misses equivalences. A curated equivalence mapping (ChEBI parent/charge-state
normalisation; nitrate 25545 vs 14654 are a conjugate pair) would fix it. Also: `chebi_id`
parses as a float in pandas unless read as a string.

### 2026-10-07 — A Windows default-encoding write corrupted the module file (tooling, minor)

**What happened.** A coder patch written with the platform default encoding put a cp1252 `§` and
doubled CRs into `methods/n_transport.py`. Found and repaired by the coder; main thread confirmed
clean UTF-8 / LF and 60/60 tests.

**Downstream impact.** Process: on Windows, always write analysis files with explicit
`encoding="utf-8"` and `newline="\n"`. Minor; a note for the template's Python guidance.

### 2026-10-07 — API paging over a non-unique ORDER BY silently swaps rows; count checks can't see it (tool bug)

**What happened.** The API-usage review (methods milestone, before scaling) read the installed
`multiomics_explorer` source. `metabolites_by_gene` orders its metabolism arm by (locus order,
locus_tag, metabolite_id) and its transport arm by (depth, score, locus order, locus_tag,
metabolite_id). Neither key is unique (several reactions or TCDB families per gene ×
metabolite), so SKIP/LIMIT pages can return rows in a different order on each page: some rows
come back twice, others never. Main-thread confirmation vs. a single call: PMM0331 98 = 98
rows, 1 duplicate + 1 missing; PMM1590 16 = 16, 2 + 2. `total_matching == rows collected`
held, so the standard truncation check passed while the data were wrong. A downstream
`drop_duplicates` would then hide the duplicate, and the lost row vanishes without a trace.

**Workaround.** Single calls with a large integer limit (these functions reject `limit=None`),
chunking locus_tags if needed; assert `returned == total_matching` and no duplicates on the
natural key ((locus, metabolite, reaction) / (locus, metabolite, family)) before any dedupe.

**Downstream impact.** **Tooling, upstream ticket candidate:** every paged tool needs a unique,
deterministic sort key (append the row's natural key to ORDER BY), or the docs must warn that
paging these tools is unsafe. Methodology: "assert total_matching" is the skill's standard
completeness check (python-api-guide / step-protocol QC) and is **not sufficient**. Add "assert
no duplicates on the natural key" and "prefer single calls". The pilot + answer key didn't catch
this (the pilot genes weren't at page boundaries); only reading the source did.

### 2026-10-07 — `metabolite_elements` filter drops formula-less substrates (tool behaviour)

**What happened.** `metabolites_by_gene(..., metabolite_elements=['N'])` excludes metabolites with
no formula (documented: "Empty/null formula metabolites never match"). In MED4's transport arm,
249 metabolites / 4,105 rows have no formula, including N-bearing classes: "amino acid" (7 rows,
all most_specific), "branched-chain amino acid" (20), "dipeptide" (27), "Polyamine" (24),
purine(s), cyclic nucleotide, protein, siderophores. The proposal's "surface every N-containing
substrate" silently missed them.

**Workaround.** Fetch without the element filter and add an `n_status` flag (contains_N /
no_formula / no_N).

**Downstream impact.** Tooling: a generic class-level metabolite ("amino acid", "peptide") should
carry an element signature, or the filter should warn how many no-formula rows it dropped.
Methodology: element filters are prefilters; use them only with the drop count reported.

### 2026-10-07 — Methods critic: the narrative over-read sound data (methodology)

**What happened.** The automatic methods critic found the data files mechanically sound, but the
notebook's narrative over-read them in four ways that would have misled the decide gate:
1. a curated "N systems" table presented as a file view;
2. "peptides: dpp" while every peptide row was `can_use = no`;
3. a strict-variant "pass" resting on helicase rows;
4. a near-circular expected-negative for the control strains.

The answer key had flagged the dpp depth inversion earlier, and the main thread did not carry it
forward.

**Workaround.** Notebook rewritten (data-driven table first, then a labelled curated view);
dispositions in `methods/critical_review.md`.

**Downstream impact.** Methodology: the main thread's own summaries are where errors entered this
milestone, not the code. The pilot, answer key and reviews checked code against the KG; nothing
checked prose against files until the critic. A rule worth considering: summary tables in a
notebook must be generated from the files (script output pasted), and any hand-curated view must
be labelled as such.

### 2026-10-07 — The string "n/a" is read as NaN by default pandas (tooling)

**What happened.** The strict-variant columns write `"n/a"` for ineligible rows. pandas'
`read_csv` treats `"n/a"` as NA by default, so a consumer reading the file without
`keep_default_na=False` can't tell "not eligible" from "missing". Found by the main thread while
checking the critic's findings (the strict columns came back NaN).

**Workaround.** Rename the value to `not_eligible`, and test that a default-pandas read
preserves it.

**Downstream impact.** Methodology: fixture realism should include "read the written file back
with default settings". Value strings that collide with pandas' default NA set (`n/a`, `NA`,
`null`, `None`, `nan`, `-`) must not be used as categories.


### 2026-10-08 — KG has no chemical categories for metabolites; compound classes are best effort (KG enhancement, OPEN)

**What happened.** Grouping transported substrates into compound classes (amino acids,
peptides, polyamines, nucleobases/nucleosides, osmolytes, …) needs a chemical classification
of each metabolite. The KG carries `chebi_id`, but `kg_schema` confirms it has **no ChEBI class
hierarchy** (no "is a" / class node or relationship). The only class-like annotation is the
compound's KEGG `pathway_ids`. Two proxy layers were tried and rejected after spot-checking:
- **KEGG pathway membership** says where a compound appears, not what it is: thyroxine →
  "amino acids" (tyrosine map); bacitracin → "amino acids"; UDP-N-acetylglucosamine →
  "xenobiotic".
- **The carrying transporter family** says the same thing: GDP-mannose and GDP-fucose →
  "xenobiotic" because only drug exporters carry them.

About half of the sampled proxy assignments were wrong.

**Workaround (researcher decision, 2026-10-08).** Classes are assigned by curated name rules
only (plus the five inorganic N classes). Compound pathways and the carrying-family context are
kept as visible context columns, not class assignments. Results are labelled best effort, with
this caveat.

**Downstream impact. KG enhancement request: chemical categories for Metabolite nodes**, e.g. the
ChEBI "is a" / role hierarchy (or ClassyFire classes) attached to each metabolite, so "Lys-Arg is
a dipeptide", "ferrichrome is a siderophore" and "thyroxine is an iodothyronine hormone" are
queryable. **Revisit this analysis when it lands.**

### Open items: revisit this analysis when these are resolved (2026-10-08)

The researcher's instruction: do best effort now, with caveats; revisit once the open items are
resolved. Open KG / tooling items that limit this analysis (each has its entry above):
1. **Chemical categories for metabolites** (ChEBI hierarchy): compound classes are name-rule
   best effort.
2. **Metabolite equivalence across namespaces** (nitrate `chebi:14654` vs `kegg.compound:C00244`
   share no cross-reference): name-only links, flagged `name_soft`.
3. **Unique sort order for paged tools** (`metabolites_by_gene`): worked around with single
   calls + duplicate-key asserts.
4. **`metabolite_elements` drops no-formula substrates**: worked around (no prefilter + `n_status`).
5. **Coordinates missing for ~5% of MED4 and 18% of MIT9313 genes**: they can't be placed as
   neighbours.
6. **No KEGG reactions on dipeptides/tripeptides** in these genomes (peptidases annotated to
   generic "peptide"): "can MED4 use it" is not testable for peptides.
7. **KO coverage of transporters** (`amt1`, `focA` have no KEGG terms): KEGG pathways unusable as
   a transporter ↔ enzyme link.

### 2026-10-08 — The author's tier rule put helicases above a real permease; caught by the delta pass (methodology)

**What happened.** The tier definition the author proposed and the researcher approved ("Medium =
strong but incomplete, *or* `tcdb_only` + resolved") let catalogue-only hits fill the Medium tier:
88/122 Medium systems in MED4, at least 37 of them helicases, proteases, chaperones, GAPDH or
sensor kinases. A BRITE-KO basis did the same for glutathione S-transferases. Neither the author
nor the researcher looked at *what* landed in each tier before approving it. The scoped delta
critic did.

**Workaround.** Catalogue-only systems → Low; KO and curated bases only upgrade catalogue-listed
genes (researcher-approved).

**Downstream impact.** Methodology: this is the fourth time this run that a rule the author wrote
had a structural flaw only visible in the populated table (tier ladder vs. `amt1`; ratio ordering
vs. denominators; strict variant vs. `focA`; Medium vs. helicases). Proposal for the round-2
review: **before a classification or tier rule is approved, show the researcher a sample of what
fills each bin** (e.g. 10 random members per tier), not only the expected pilot cases. Pilot cases
confirm what the rule was designed for; a random sample shows what it wasn't.


### 2026-10-08 — TCDB substrate lists describe the subfamily, not the gene (KG / annotation)

**What happened.** Even at `substrate_depth = most_specific` with catch-all families excluded, a
gene inherits every substrate its TCDB subfamily lists. In MED4, the sulfate permeases `sul1`/`sul3`
list amino acids and nitrate; the K⁺ uptake gene `ktrA` and the Na⁺/H⁺ antiporter `nhaS` list ammonium.
In MIT9313/NATL2A one SSS-family gene (`putP` / PMN2A_RS08290) lists urea, nitrate, polyamines,
osmolytes and amino sugars. These listings set the organic-N class counts: amino acids are listed by
10 / 25 / 14 High+Medium systems. Found by QC check d (substrate vs product), not by the pilot or
either critic pass.

**Workaround.** v1.6.0 marks each system-class listing as "dedicated" (the product/gene-name keyword
or a curated Cyanorak class agrees) or "broad listing", and records substrate breadth. Fig2 shows
the two separately (researcher-approved).

**Downstream impact.** KG: a per-gene (not per-subfamily) substrate call, or a substrate-breadth
field on the TCDB attachment, would remove the need for keyword rules. Methodology: this is a second
case where a check against an independent source (product strings) found what the pilot cases
couldn't. That supports the "show a random sample per bin before approving a rule" proposal above.

### 2026-10-08 — Curated transporter genes missing from a three-source universe (methodology)

**What happened.** QC check b (curated Cyanorak transport-role genes vs tier) found genes that none
of TCDB, BRITE or role-Pfam picked up: the porin `som` (PMM1121, PMN2A_0440), a CLC channel
(PMN2A_2187) and Q.9 "permease" genes. It also found curated ABC genes stuck in Low as
"superfamily-only" (MIT9313 ggtA–D PMT0691–0694, PMT1576). None carries nitrogen.

**Workaround.** v1.6.0 adds curated Q-role genes as a fourth universe source, and a curated role
lifts superfamily-only to Medium (researcher-approved).

**Downstream impact.** For the Alteromonas analysis, which has no Cyanorak roles, the equivalent
recall check needs another curated source (e.g. BRITE transporter KOs alone, or product strings).
Note this in the sibling analysis's co-define.
