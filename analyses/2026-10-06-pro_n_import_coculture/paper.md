# Nitrogen import capacity of *Prochlorococcus* in coculture with *Alteromonas*

*Working paper — grows across the analysis arc. Sections fill in at the Plan commit and each Run
milestone's decide phase.*

## Question

In long-term nitrogen-limited coculture with *Alteromonas macleodii* HOT1A3, for which classes of
nitrogen compounds does *Prochlorococcus* MED4 raise its import capacity beyond what early axenic
nitrogen starvation shows? Is that pattern specific to nitrogen limitation, i.e. absent in
nitrogen-replete cocultures of MED4 and of other *Prochlorococcus* strains?

This is the consumer-side half of a question about which nitrogen compounds *Alteromonas* passes
to *Prochlorococcus*. The producer side (*Alteromonas*) is a separate analysis, and a third
compares the two. Transporter expression measures import capacity, which is largely set by
nitrogen-starvation regulation. It does not show that a compound was present, taken up, or
supplied by the partner.

## Background

*(Draft material for the rewrite of Weissberg et al. 2025, bioRxiv 10.1101/2025.11.24.690089.
The preprint's interpretations are treated as hypotheses to re-examine, not as established.)*

In coculture with *Alteromonas* HOT1A3, *Prochlorococcus* MED4 survives for months after the
nitrogen in its medium is exhausted, whereas axenic cultures die. The preprint interpreted the
accompanying proteomes and transcriptomes as MED4 up-regulating high-affinity nitrogen
scavenging while *Alteromonas* recycles organic matter and supplies low-level ammonium. No
measurement of nitrogen compounds exists for these cultures, so which compounds are exchanged can
only be inferred from the organisms' gene expression.

MED4's genome encodes import routes for ammonium (`amt1`), urea (`urtA–E` with urease), cyanate
(`cynABD` with cyanase) and peptides (`dpp`), and has no nitrate or nitrite assimilation. Its
transporter annotation names specific importers for only some nitrogen classes. Amino acids,
polyamines and osmolytes are reachable only through broad family-level annotation.

The data are the per-culture starvation time courses: protein and RNA, in coculture and axenic,
each compared with its own exponential phase, extending to day 89 in coculture. Earlier coculture
transcriptomes of MED4 and MIT9313 with HOT1A3 (Aharonovich & Sher 2016) and of NATL2A with
*Alteromonas* MIT1002 (Biller et al. 2016) were all taken in nitrogen-replete exponential growth,
and serve here as controls.

## Methods

**Data source.** All annotation came from the multiomics knowledge graph (KG release 0.1.0-alpha.7,
built 2026-09-22; `multiomics_explorer` 0.1.0-alpha.5) through its Python API. Every call went
through a fetch helper that makes single unpaged calls, asserts that returned rows equal
`total_matching`, and checks for duplicate natural keys. Paging was abandoned after an
API-usage review showed that offset paging over a non-unique sort order silently duplicated and
dropped rows while totals still matched.

**Transport systems, built per strain.** For *Prochlorococcus* MED4, MIT9313 and NATL2A
separately, transporter genes were collected from four sources: TCDB family attachments, the
KEGG BRITE transporter catalogue, Pfam domains with a transporter role, and curated Cyanorak
transport roles (Q.1–Q.9). A gene missed by all of these was re-queried with the full role map. Subunit roles (substrate-binding, permease, ATPase,
single carrier) were assigned from Pfam domains through a role map learned from the transporter
genes themselves; each domain's role is reviewable with the rule that set it. Genes were grouped
into systems by genome position (same-strand runs, adjacent gap ≤ 200 bp) and by shared TCDB
family. Directly adjacent same-strand ABC parts that share the ABC superfamily were also joined,
including a second permease or a membrane-fusion protein (e.g. `devBCA`, `evrABC`), but two
complete cassettes were never merged. Pieces of an incomplete ABC system at different loci were
joined when they shared a TCDB subfamily and had complementary roles; pieces made only of non-transport genes were not allowed
to join. No ortholog mapping was used: each strain's systems come from its own annotation.

**Substrates.** For each system, every substrate in its TCDB annotation was listed with flags,
with no prefiltering (MED4: 14,978 rows; MIT9313: 27,013; NATL2A: 17,022). The flags record:
- whether the substrate is listed for the gene's own TCDB subfamily or inherited from a parent
  family;
- the evidence behind the TCDB call;
- whether the family is a catch-all superfamily (ABC 3.A.1, MFS 2.A.1, 2.A.7, 2.A.6, and in
  MIT9313 2.A.66, each listing ≥ 100 compounds);
- whether the compound is a ubiquitous cofactor;
- whether it contains nitrogen.

A substrate was marked usable if some gene of the same strain has a KEGG reaction on it. Because
the KG stores the same compound under unconnected IDs (nitrate as both ChEBI 14654 and KEGG
C00244), compounds were matched through equivalence groups, with name-only links flagged.

**Linked enzymes.** Two kinds of enzyme were linked to a system, both requiring a KEGG reaction on
a compound the system carries (catch-all families and cofactors excluded):
- *neighbour-linked*: the enzyme lies within ±8 genes on either strand, and the compound is not
  ubiquitous (≥ 30 reacting genes, i.e. ammonia and glutamate, cannot create the link);
- *function-linked*: the enzyme shares a curated Cyanorak functional role with the system (other
  than a transport role), at any distance. For ubiquitous compounds, only glutamine synthetase
  and GOGAT (EC 6.3.1.2, 1.4.7.1) count.

**Confidence tiers.** Each system was assigned a tier from whether it is a credible transporter
and complete, not from the sequence-evidence type of its TCDB call. That choice matters because
direct sequence hits are rarer for multi-subunit ABC systems (40% vs 57% of single-gene systems
in MED4), so keying the tier on hit type would penalise ABC systems.
- *High*: transporter-role domain, KEGG transporter KO, or curated Cyanorak transport role on a
  TCDB-listed gene; plus all required subunits present; plus a specific TCDB call.
- *Medium*: the same, but missing a required subunit.
- *Low*: placed only in a catch-all superfamily, supported only by zero-score TCDB hits, or listed
  in TCDB with no supporting domain, KO or curated role ("catalogue-only"). A curated Cyanorak
  transport role lifts the first two cases to Medium, never the third. Most systems lifted this way
  are annotated as efflux or export proteins. They carry an `efflux_annotated` flag.

A KEGG transporter KO or a curated Cyanorak transport role counted as transporter evidence only
for genes TCDB also lists. Known false positives are flagged rather than removed: ferritin,
glutathione S-transferases (TCDB-listed in the CLIC family), a MAPEG glutathione protein and
`sodX`.

**Compound classes.** Substrates were grouped into ammonium, urea, cyanate, nitrite, nitrate,
amino acids, peptides, amines, polyamines, nucleobases/nucleosides and osmolytes by curated
name rules. KEGG pathway membership and the carrying transporter family were tried as classifiers
and rejected: about half of the sampled assignments were wrong (e.g. thyroxine as an amino
acid). They are kept as context only. TCDB substrate lists describe a whole subfamily, not
the individual gene: the sulfate permeases `sul1`/`sul3` list amino acids and nitrate, and K⁺/Na⁺
transporters (`ktrAB`, `nhaS`) list ammonium. Each system's listing of a nitrogen class was therefore
marked *dedicated* when a member's product or gene name names the class, or when a curated Cyanorak
amino-acid/nucleoside role agrees (not for efflux-annotated systems). Otherwise it was marked a
*broad listing*. A dedicated listing means the annotation names the class, not that the gene
transports it. **These classes are best effort: the KG holds no chemical
classification of metabolites (no ChEBI class hierarchy), and 382–422 nitrogen-containing
substrate groups per strain remain unclassified.**

**Verification.** The construction was checked step by step on seven MED4 cases (the cyanate,
urea/urease, ammonium, peptide (split across three loci) and phosphate systems, plus two noise
cases) against an independent answer key, built by a separate agent through the KG's query
interface without seeing the code. It was then reviewed twice for API usage and twice by a
fresh-context critic. Before approval, a further set of checks was run:
- gene maps of every nitrogen-relevant locus;
- recall of curated transporter genes;
- a random sample of each tier;
- agreement between listed substrate and product description;
- sensitivity to the grouping gap (100/200/500 bp; nitrogen systems identical);
- consistency of shared transporters across strains.

These checks led to the adjacent-ABC rule, the fourth gene source and the dedicated/broad split
above. A third critic pass then reviewed these changes. The nitrate/nitrite expected-negative holds
per genome:
- nitrate is unusable in all three strains (no gene reacts with it);
- nitrite is usable only where nitrite reductase is present: MIT9313 and NATL2A, each with the
  FNT nitrite transporter `focA` adjacent to `nirA`.

## Results

## Discussion

## References

- Weissberg O, Aharonovich D, Sher D (2025). Transcriptomic and Proteomic Analysis Reveals
  Nitrogen Recycling as a Core Mechanism for *Prochlorococcus* Prolonged Survival. bioRxiv.
  doi:10.1101/2025.11.24.690089
- Aharonovich D, Sher D (2016). Transcriptional response of *Prochlorococcus* to co-culture with
  a marine *Alteromonas*: differences between strains and the involvement of putative
  infochemicals. ISME J. doi:10.1038/ismej.2016.70
- Biller SJ, Coe A, Chisholm SW (2016). Torn apart and reunited: impact of a heterotroph on the
  transcriptome of *Prochlorococcus*. ISME J. doi:10.1038/ismej.2016.82
