"""Find single-copy core ortholog groups specific to the six marine Synechococcus.

A gene's ORTHOLOG NEIGHBOURHOOD is the union of member genes across every
ortholog group it belongs to, at every taxonomic level and from both sources
(cyanorak curated + eggNOG). A gene qualifies as a marker when its neighbourhood
holds exactly six genes: one from each target strain and nothing else.

Taking the union across levels is what makes the specificity test honest. A gene
whose genus-level group holds only Synechococcus but whose Bacteria-level group
also holds Prochlorococcus has a neighbourhood spanning both, and is rejected.

Inputs : the KG, via multiomics_explorer (GraphConnection reads .env / env vars).
Outputs: data/markers.csv           final marker table, one row per group
         data/validation.csv        two-sided housekeeping-gene check
         data/funnel.csv            filter funnel counts
         data/01_build_markers.log  full run log
Usage  : uv run python analysis/scripts/01_build_markers.py
"""

from __future__ import annotations

import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path

from multiomics_explorer import (
    GraphConnection,
    gene_homologs,
    genes_by_homolog_group,
    kg_release_info,
    resolve_gene,
    search_homolog_groups,
)

# The six marine Synechococcus, by exact OrganismTaxon.preferred_name.
TARGETS = [
    "Synechococcus CC9311",
    "Synechococcus WH8109",
    "Synechococcus WH8102",
    "Synechococcus sp. BL107",
    "Synechococcus WH7803",
    "Synechococcus PCC 7002",
]
# Optional: drop one strain, e.g. --drop "Synechococcus PCC 7002".
_SUFFIX = ""
if "--drop" in sys.argv:
    _d = sys.argv[sys.argv.index("--drop") + 1]
    assert _d in TARGETS, f"unknown strain {_d!r}"
    TARGETS = [t for t in TARGETS if t != _d]
    _SUFFIX = "_no_" + _d.split()[-1].lower()
TARGET_SET = frozenset(TARGETS)

# Two-sided validation: must pass core + single-copy, must FAIL specificity.
VALIDATION_GENES = ["gyrB", "recA", "rpoB", "dnaG"]

GROUP_BATCH = 400
GENE_BATCH = 400

OUT = Path(__file__).resolve().parents[1] / "data"
OUT.mkdir(parents=True, exist_ok=True)

log = logging.getLogger("markers")


def setup_logging() -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(OUT / f"01_build_markers{_SUFFIX}.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def batched(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def main() -> int:
    setup_logging()
    funnel: list[tuple[str, int]] = []

    with GraphConnection() as conn:
        rel = kg_release_info(conn=conn)
        log.info("KG %s built %s | explorer %s | verdict %s",
                 rel["kg"]["version"], rel["kg"]["built_at"],
                 rel["explorer_version"], rel["verdict"])

        # ---- 1. enumerate every ortholog group -------------------------------
        groups = search_homolog_groups(search_text="*", limit=None, conn=conn)["results"]
        log.info("groups enumerated: %d", len(groups))
        funnel.append(("groups_enumerated", len(groups)))

        meta = {g["group_id"]: g for g in groups}

        # A group touching 7+ organisms cannot have a six-organism membership,
        # so it can never be part of a qualifying neighbourhood.
        small = [g["group_id"] for g in groups if (g.get("organism_count") or 0) <= 6]
        log.info("groups with organism_count <= 6: %d", len(small))
        funnel.append(("groups_organism_count_le_6", len(small)))

        # ---- 2. expand members, WITHOUT an organisms filter ------------------
        # Filtering by organism here would hide non-target members and
        # manufacture false specificity. Never add organisms= to this call.
        roster: dict[str, set[tuple[str, str]]] = defaultdict(set)  # group -> {(locus,org)}
        gene_org: dict[str, str] = {}
        gene_info: dict[str, dict] = {}

        for i, chunk in enumerate(batched(small, GROUP_BATCH), 1):
            res = genes_by_homolog_group(group_ids=chunk, limit=None, conn=conn)
            for r in res["results"]:
                lt, org = r["locus_tag"], r["organism_name"]
                roster[r["group_id"]].add((lt, org))
                gene_org[lt] = org
                gene_info.setdefault(lt, r)
            if i % 5 == 0:
                log.info("  expanded %d/%d group batches", i, (len(small) - 1) // GROUP_BATCH + 1)

        log.info("member rows collected for %d groups, %d distinct genes",
                 len(roster), len(gene_org))

        # ---- 3. candidate genes ---------------------------------------------
        # Genes from a target strain sitting in a group whose whole roster is a
        # subset of the six targets.
        candidates: set[str] = set()
        subset_groups = 0
        for gid, mem in roster.items():
            orgs = {o for _, o in mem}
            if orgs and orgs <= TARGET_SET:
                subset_groups += 1
                candidates.update(lt for lt, _ in mem)
        log.info("groups whose roster is a subset of the six: %d", subset_groups)
        log.info("candidate genes: %d", len(candidates))
        funnel.append(("groups_roster_subset_of_targets", subset_groups))
        funnel.append(("candidate_genes", len(candidates)))

        # ---- 4. close the neighbourhood --------------------------------------
        # Retrieve EVERY group each candidate belongs to, including broad ones
        # the organism_count prefilter dropped. A candidate holding any such
        # group is disqualified, because that group has 7+ organisms.
        gene_groups: dict[str, set[str]] = defaultdict(set)
        cand_list = sorted(candidates)
        newly_seen: set[str] = set()
        for i, chunk in enumerate(batched(cand_list, GENE_BATCH), 1):
            res = gene_homologs(locus_tags=chunk, limit=None, conn=conn)
            for r in res["results"]:
                gene_groups[r["locus_tag"]].add(r["group_id"])
                if r["group_id"] not in roster:
                    newly_seen.add(r["group_id"])
                    meta.setdefault(r["group_id"], r)
            if i % 5 == 0:
                log.info("  closed %d/%d gene batches", i, (len(cand_list) - 1) // GENE_BATCH + 1)

        log.info("groups newly seen during closure (all have 7+ organisms "
                 "or were otherwise prefiltered): %d", len(newly_seen))

        # Expand the newly seen groups so their rosters are real, not assumed.
        if newly_seen:
            for chunk in batched(sorted(newly_seen), GROUP_BATCH):
                res = genes_by_homolog_group(group_ids=chunk, limit=None, conn=conn)
                for r in res["results"]:
                    roster[r["group_id"]].add((r["locus_tag"], r["organism_name"]))
                    gene_org.setdefault(r["locus_tag"], r["organism_name"])

        # ---- 5. apply the three tests ----------------------------------------
        passing: dict[frozenset, dict] = {}
        rej_not_core = rej_multicopy = rej_not_specific = 0

        for lt in cand_list:
            hood: set[tuple[str, str]] = set()
            for gid in gene_groups.get(lt, ()):
                hood |= roster.get(gid, set())
            if not hood:
                continue

            by_org: dict[str, list[str]] = defaultdict(list)
            for m_lt, m_org in hood:
                by_org[m_org].append(m_lt)

            outside = set(by_org) - TARGET_SET
            if outside:
                rej_not_specific += 1
                continue
            if set(by_org) != TARGET_SET:
                rej_not_core += 1
                continue
            if any(len(v) != 1 for v in by_org.values()):
                rej_multicopy += 1
                continue

            key = frozenset(m_lt for m_lt, _ in hood)
            if key in passing:
                continue
            levels = sorted({meta[g].get("taxonomic_level", "?")
                             for g in gene_groups[lt] if g in meta})
            sources = sorted({meta[g].get("source", "?")
                              for g in gene_groups[lt] if g in meta})
            anchor = gene_info.get(lt, {})
            m = meta.get(sorted(gene_groups[lt])[0], {})
            passing[key] = {
                "group_ids": ";".join(sorted(gene_groups[lt])),
                "consensus_gene_name": m.get("consensus_gene_name") or anchor.get("gene_name") or "",
                "consensus_product": m.get("consensus_product") or anchor.get("product") or "",
                "gene_category": anchor.get("gene_category") or "",
                "levels": ";".join(levels),
                "sources": ";".join(sources),
                **{f"locus_{o.replace('Synechococcus ', '').replace('sp. ', '').replace(' ', '_')}":
                   by_org[o][0] for o in TARGETS},
            }

        log.info("rejected, ortholog outside the six: %d", rej_not_specific)
        log.info("rejected, missing from >=1 target strain: %d", rej_not_core)
        log.info("rejected, multi-copy in >=1 target strain: %d", rej_multicopy)
        log.info("MARKER GROUPS PASSING ALL THREE TESTS: %d", len(passing))
        funnel += [
            ("rejected_ortholog_outside_targets", rej_not_specific),
            ("rejected_not_core", rej_not_core),
            ("rejected_multicopy", rej_multicopy),
            ("markers_final", len(passing)),
        ]

        # ---- 6. validation ----------------------------------------------------
        val_rows = []
        marker_loci = {v for row in passing.values()
                       for k, v in row.items() if k.startswith("locus_")}
        for name in VALIDATION_GENES:
            hits = resolve_gene(identifier=name, limit=None, conn=conn)["results"]
            tgt = [h for h in hits if h["organism_name"] in TARGET_SET]
            per_org = defaultdict(list)
            for h in tgt:
                per_org[h["organism_name"]].append(h["locus_tag"])
            in_markers = sorted(h["locus_tag"] for h in tgt
                                if h["locus_tag"] in marker_loci)
            row = {
                "gene": name,
                "strains_hit": len(per_org),
                "core_all_six": len(per_org) == 6,
                "single_copy_everywhere": all(len(v) == 1 for v in per_org.values()) and len(per_org) > 0,
                "appears_in_marker_table": bool(in_markers),
                "loci": ";".join(f"{o}:{','.join(sorted(v))}" for o, v in sorted(per_org.items())),
            }
            val_rows.append(row)
            log.info("validation %-5s strains=%d core6=%s single=%s in_markers=%s",
                     name, row["strains_hit"], row["core_all_six"],
                     row["single_copy_everywhere"], row["appears_in_marker_table"])

    # ---- write ---------------------------------------------------------------
    rows = sorted(passing.values(),
                  key=lambda r: (r["consensus_gene_name"] == "", r["consensus_gene_name"]))
    if rows:
        with open(OUT / f"markers{_SUFFIX}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    with open(OUT / f"validation{_SUFFIX}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(val_rows[0]))
        w.writeheader()
        w.writerows(val_rows)
    with open(OUT / f"funnel{_SUFFIX}.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stage", "count"])
        w.writerows(funnel)

    annotated = sum(1 for r in rows if r["consensus_gene_name"]
                    and "hypothetical" not in r["consensus_product"].lower())
    log.info("markers with an informative name and non-hypothetical product: %d/%d",
             annotated, len(rows))
    log.info("wrote markers%s.csv (%d rows), validation, funnel", _SUFFIX, len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
