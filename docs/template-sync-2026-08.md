# Template sync — Plan→Run arc, dogfood-hardened

*Transient note. Delete once the changes are carried into
`multiomics_research_template`.*

## Why this exists

Push to `upstream` is deliberately disabled in this consumer clone, so the
methodology work done here has to be carried into the template repo by hand. The
Plan→Run arc has been sitting under `[Unreleased]` in the template since the
restructure; it has now been run end to end on one real analysis and corrected
where it creaked.

**No release is cut here.** The changes stay under `[Unreleased]`, and `VERSION`
is untouched at `0.1.0-alpha.2` — versioning and the release are the template
repo's call.

## What to carry

Two commits, now on `main` in `git@github.com:wosnat/multiomics_analysis.git`
(merged from `methodology/review-2026-08`):

- **`bc3e35b`** — the four skill changes + the review + the retargeted test brief
- **the follow-up commit** — the `[Unreleased]` CHANGELOG entry describing them

Files, in full:

```
.claude/skills/research-methodology/SKILL.md
.claude/skills/research-methodology/references/step-protocol.md
.claude/skills/research-methodology/references/research-notebook.md
.claude/skills/critical-review/SKILL.md
docs/methodology-review-2026-08.md          (new)
docs/methodology-test-brief.md              (rewritten for round 2)
CHANGELOG.md                                (into [Unreleased] — not a release)
```

## What NOT to carry

- **`analyses/`** — the researcher's own work, not template content.
- **`docs/upstream-tickets-2026-08.md`** — three tickets bound for
  `multiomics_explorer` and `multiomics_biocypher_kg`; transient, and not the
  template's business.
- **`usage/`** — this clone's logs.
- **`VERSION`** — untouched here; bump it in the template if and when you release.

## Versioning (template's call, whenever you release)

Left open deliberately. When you do cut it, the argument for **minor rather than
patch** is that the arc replaces the `1_question/` … `6_evaluate/` folder
structure, which is breaking for anyone mid-analysis — so `0.2.0-alpha.1` over
`0.1.0-alpha.3`. Whichever you pick, the CHANGELOG heading and the `VERSION` file
move together: `./scripts/preflight.sh` prints the version triple and they must
agree.

## Prompt to paste into a fresh Claude Code session in the template clone

> I'm carrying methodology work into this template — the Plan→Run research arc,
> hardened by its first full dogfood. It goes under `[Unreleased]`; **I am not
> cutting a release in this pass**, so don't touch `VERSION`. The work is on
> `main` in `git@github.com:wosnat/multiomics_analysis.git`, commits `bc3e35b`
> and `2809387` (a consumer clone of this template; its `upstream` push is
> disabled, which is why this is a manual carry).
>
> Add that repo as a temporary remote and fetch it, then bring across **only**
> these files, at their state there:
>
> - `.claude/skills/research-methodology/SKILL.md`
> - `.claude/skills/research-methodology/references/step-protocol.md`
> - `.claude/skills/research-methodology/references/research-notebook.md`
> - `.claude/skills/critical-review/SKILL.md`
> - `docs/methodology-review-2026-08.md` (new)
> - `docs/methodology-test-brief.md` (rewritten — replace, don't merge)
> - the `CHANGELOG.md` entry — it belongs under the template's **existing
>   `[Unreleased]`**, alongside the arc restructure already sitting there
>
> Do **not** bring `analyses/`, `usage/`, `VERSION`, or
> `docs/upstream-tickets-2026-08.md`.
>
> Before committing, check three things and tell me what you find:
> 1. **The skill files apply cleanly to the template's copies.** The template may
>    have diverged since the consumer clone forked — if any of the four differs
>    beyond these changes, show me the diff rather than overwriting.
> 2. **`CHANGELOG.md` merges rather than replaces.** The template's `[Unreleased]`
>    may hold entries the consumer clone never saw — keep them. The incoming text
>    describes corrections to the arc restructure that is already in that section,
>    so it belongs with it, not as a competing bullet.
> 3. **Nothing in the four skill files references the consumer clone** — no
>    `analyses/2026-07-06-...` paths that only resolve there. The dogfood is cited
>    in parentheticals as narrative evidence, which is intended; a *link* into a
>    nonexistent folder is not.
>
> Then commit it as an ordinary change — **no version bump, no tag** — and show me
> the diff. We'll cut the release separately once we decide the number.

## Context for whoever picks this up

The four changes and the evidence behind each are in
`docs/methodology-review-2026-08.md`. Four further findings occurred only once in
the dogfood and were deliberately **not** applied — the Plan phase's commit count
and stopping rule, cross-experiment comparability in the framing floor, an
expected-negative in the validation set, and whether "the methods milestone stays
minimal" survives when the method builds the entity set. The retargeted
`docs/methodology-test-brief.md` asks the next analysis to look for a second
occurrence of each. Don't fold them into the skill on this release.
