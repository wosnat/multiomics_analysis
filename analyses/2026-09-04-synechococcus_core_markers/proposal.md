# Proposal — Single-copy core marker genes specific to marine *Synechococcus*

**Analysis slug:** `2026-09-04-synechococcus_core_markers`
**Plan drafted:** 2026-09-04
**Approved:** pending
**KG release:** `0.0.0-dev` (built 2026-08-29; explorer-MCP `0.1.0a4`;
`kg_release_info` verdict `ok`, 17/17 asserts). Local development KG on
`bolt://127.0.0.1:17687`, confirmed by the researcher as the intended target.
Repo preflight is RED on a commented-out `.env`; see `gaps_and_friction.md`.

---

## Question (locked)

**Which ortholog groups contain exactly one gene in each of the six marine
*Synechococcus* strains in the KG, and no gene anywhere else in the KG?**

Such groups are candidate marker genes: present in every marine *Synechococcus*
(core), never duplicated within a strain (single-copy), and with no ortholog in
any other genome the KG holds (specific).

The researcher's stated scope is orthology only. No expression, DE, clustering,
metabolite, or derived-metric data enters this analysis.

### What "specific" can and cannot mean here

The KG holds 48 `OrganismTaxon` nodes, of which **43 carry genes** `[KG]`
(41 `genome_strain` + 2 `reference_proteome_match`; the 5 `treatment` taxa have
`gene_count = 0`). Eight of the 43 are *Synechococcus*-named. So the strongest
specificity test the KG supports is **absence from the other 35 gene-bearing
genomes**, 17 of which are *Prochlorococcus*.

That is a genuine test, and it is not proof of genus-restriction across
bacteria. Any candidate that leaves this analysis needs an external database
search before it is used as a marker. This limit is stated here so it cannot be
quietly forgotten at the evaluation milestone. `[gap]`

---

## KG entries (enumerated from live queries)

### The six target organisms

Selected by the researcher as "all marine". The KG stores **no habitat or
environment property** on `OrganismTaxon` `[gap]`, so the marine call is
`[interpretation]`; the `clade` field is populated for exactly the five marine
picocyanobacterial clades and empty elsewhere, which corroborates it `[KG]`.

| # | `preferred_name` | KG genus | Clade | Genes | Cyanorak-grouped genes | eggNOG-grouped genes |
|---|---|---|---|---|---|---|
| 1 | Synechococcus CC9311 | Synechococcus | I | 3038 | 2931 | 2542 |
| 2 | Synechococcus WH8109 | Synechococcus | II | 2681 | 2616 | 2254 |
| 3 | Synechococcus WH8102 | Parasynechococcus | III | 2830 | 2777 | 2524 |
| 4 | Synechococcus sp. BL107 | Synechococcus | IV | 2567 | 2506 | 2344 |
| 5 | Synechococcus WH7803 | Synechococcus | V | 2590 | 2577 | 2410 |
| 6 | Synechococcus PCC 7002 | Picosynechococcus | none | 3207 | 0 | 3081 |

All counts `[KG]`.

**Two facts about this set that shape the method.** PCC 7002 is a coastal
euryhaline strain that the KG files under a different genus, and it carries
**no Cyanorak curated groups at all** — Cyanorak covers *Prochlorococcus* and
the five picocyanobacterial *Synechococcus* only `[KG]`. A core set spanning
all six therefore cannot be built from Cyanorak groups; it must run on eggNOG
groups, with Cyanorak used only as corroboration on the five. The researcher
chose all six over the five-strain alternative.

### Out of scope, and why each matters

- **Synechococcus elongatus PCC 7942 and UTEX 2973** — freshwater
  `[interpretation]`, no clade in the KG `[KG]`. They are *not* target
  organisms, so a group containing them **fails** the specificity test. This is
  deliberate: it makes the output specific to *marine* Synechococcus rather
  than to the genus.
- **Thermosynechococcus vestitus BP-1** — different order (Acaryochloridales)
  `[KG]`; matched the earlier name search only as a synonym. Excluded, and
  counted among the 35 non-target genomes.
- **17 Prochlorococcus strains** — the closest relatives in the KG and the
  hardest specificity test any candidate faces `[KG]`.

### Ortholog group structure in this KG

A gene belongs to up to four nested groups `[KG]`:

| Source | `taxonomic_level` | `specificity_rank` | Groups | Scope |
|---|---|---|---|---|
| cyanorak | curated | 0 | 8007 | Prochlorococcus + 5 picocyanobacterial Synechococcus only |
| eggnog | Synechococcus (taxid 1129) | 1 | 4845 | the 8 Synechococcus-named organisms |
| eggnog | Cyanobacteria (taxid 1117) | 2 | 7880 | cyanobacteria across genera |
| eggnog | Bacteria (taxid 2) | 3 | 9896 | all bacteria in the KG |

Counts `[KG]`. Sibling levels exist for the other lineages (Prochloraceae,
Alteromonadaceae, Proteobacteria).

**Membership in a Synechococcus-level group is not evidence of specificity.**
Worked example `[KG]`: `atp1` sits in `eggnog:1H0EZ@1129` at Synechococcus level
with 8 members, *and* in `eggnog:1G82R@1117` (Cyanobacteria, 17 members) *and*
in `eggnog:32SW6@2` (Bacteria, 17 members), the latter two spanning
Prochlorococcus, Synechococcus and Thermosynechococcus. The narrow group only
says eggNOG cut a genus-level cluster there. Specificity has to be read off the
**broadest** group a gene belongs to, not the narrowest. This is the single
most important design constraint in the method below.

---

## Framing

### Hypothesis

A set of ortholog groups exists whose entire membership in this KG is exactly
one gene from each of the six marine *Synechococcus* strains, and these
constitute candidate single-copy core markers for the group. A preliminary
count suggests the set is on the order of tens of groups, not hundreds or zero.

### Approach

Define a gene's **ortholog neighborhood** as the union of member genes across
*every* ortholog group the gene belongs to, at every level and from both
sources. A gene qualifies when its neighborhood contains **exactly six genes:
one from each target strain, and nothing else**.

Taking the union across all levels is what enforces specificity correctly. A
gene whose narrow group holds only Synechococcus but whose Bacteria-level group
also holds Prochlorococcus has a neighborhood spanning both genera, and is
rejected. This is the operational form of the researcher's chosen definition,
"absent from all other KG genomes".

Pipeline, using the orthology tool family throughout:

1. **Enumerate groups.** `search_homolog_groups` over every level and source,
   unpaginated via the Python package. Prefilter to groups where
   `organism_count` is at most 6, since a group touching seven or more
   organisms cannot have a six-organism membership.
2. **Expand members.** `genes_by_homolog_group` on the prefiltered ids, with
   **no `organisms` filter**, so non-target members are visible rather than
   hidden. Filtering by organism here would silently manufacture false
   specificity, and is the main way this method could go wrong.
3. **Collect candidate genes.** Keep genes from the six target strains that
   appear in a group whose roster is a subset of the six.
4. **Close the neighborhood.** `gene_homologs` on those candidate genes to
   retrieve *all* their groups, including broader ones the prefilter dropped.
   Expand any newly seen group through step 2. Repeat until no new group
   appears, so the neighborhood is complete rather than truncated.
5. **Apply the three tests.** Core: all six strains present. Single-copy:
   exactly one gene per strain. Specific: zero genes from the other 37
   gene-bearing organisms.
6. **Emit** a marker table keyed by group id, carrying the six locus tags, the
   consensus gene name and product, the Cyanorak role and COG category, and the
   levels at which the neighborhood was closed.

Locus tags are the identifier in every output row; gene names appear only as
labels alongside them.

### Statistics plan

**No formal statistics, deliberately.** Every step is exact set membership over
a closed, fully enumerated graph. There is no sampling, no estimation, and no
null model to test against, so a p-value would be meaningless here. The
analysis reports counts and a filter funnel: groups enumerated, groups
surviving each of the three tests, and genes lost at each stage.

### Validation set

Four housekeeping genes, chosen because they are single-copy in cyanobacteria
and universal in bacteria: **gyrB, recA, rpoB, dnaG**. They are a **two-sided**
check, and both sides must hold:

- **They must PASS core and single-copy.** Each should resolve to exactly one
  locus tag in each of the six strains. If a housekeeping gene comes back absent
  from a strain or duplicated within one, the membership census is broken.
- **They must FAIL specificity.** Each should have Prochlorococcus and
  heterotroph genes in its neighborhood, so all four must be **absent** from the
  final marker table. If any appears there, the neighborhood closure in step 4
  is truncating, and every result is inflated.

### Falsifiability check

The result that says the method found nothing real: **the final table is empty**,
or **it is dominated by hypothetical proteins with no Cyanorak role and no COG
category**. The first is a clean bounded negative and would be written up as
one. The second would mean the surviving groups are annotation artifacts,
fragments and mis-clustered singletons rather than genuine conserved genes, and
the specificity filter is selecting for poor annotation rather than for biology.
The evaluation milestone tests this by reporting what fraction of the final
table carries an informative annotation.

**Pre-registered expected-negative: dropped at researcher request (2026-09-04).**
The methodology asks for a class that should not score if the signal is genuine;
the candidates were the multi-copy high-light inducible protein family and the
clade-variable phycobilisome rod genes. The researcher chose to drop it for now.
Falsifiability is not lost, because the validation set above is already
two-sided: gyrB, recA, rpoB and dnaG are themselves a pre-registered class that
**must not appear** in the output, and they probe the exact failure mode
(truncated neighborhood closure) that would produce a spuriously large table.
Recorded as a deliberate departure in `gaps_and_friction.md`.

---

## What this analysis will not deliver

- No claim of genus-restriction beyond the 43 gene-bearing genomes in the KG.
- No expression, abundance, or functional validation of any candidate.
- No primer or probe design, and no sequence-level specificity check.
- No phylogenetic tree, and no claim about which candidates are ancestral.
