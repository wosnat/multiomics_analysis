"""Why is the six-strain marker set near-empty?

Re-runs the neighbourhood construction from 01_build_markers.py, then reports,
for every gene whose neighbourhood is entirely inside the six target strains,
how many of the six it actually covers, and which strain is missing. Also
recomputes the marker set on each five-strain subset, to see whether one strain
is the blocker.

Outputs: data/coverage_breakdown.csv, data/leave_one_out.csv,
         data/02_diagnose_empty.log
Usage  : uv run python analysis/scripts/02_diagnose_empty.py
"""

from __future__ import annotations

import csv
import itertools
import logging
import sys
from collections import Counter, defaultdict
from pathlib import Path

from multiomics_explorer import (
    GraphConnection,
    gene_homologs,
    genes_by_homolog_group,
    search_homolog_groups,
)

TARGETS = [
    "Synechococcus CC9311",
    "Synechococcus WH8109",
    "Synechococcus WH8102",
    "Synechococcus sp. BL107",
    "Synechococcus WH7803",
    "Synechococcus PCC 7002",
]
TARGET_SET = frozenset(TARGETS)
GROUP_BATCH = 400
GENE_BATCH = 400

OUT = Path(__file__).resolve().parents[1] / "data"
log = logging.getLogger("diag")


def setup() -> None:
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    fh = logging.FileHandler(OUT / "02_diagnose_empty.log", mode="w")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(fh)
    log.addHandler(sh)


def batched(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i : i + n]


def main() -> int:
    setup()
    with GraphConnection() as conn:
        groups = search_homolog_groups(search_text="*", limit=None, conn=conn)["results"]
        meta = {g["group_id"]: g for g in groups}
        small = [g["group_id"] for g in groups if (g.get("organism_count") or 0) <= 6]

        roster: dict[str, set[tuple[str, str]]] = defaultdict(set)
        info: dict[str, dict] = {}
        for chunk in batched(small, GROUP_BATCH):
            for r in genes_by_homolog_group(group_ids=chunk, limit=None, conn=conn)["results"]:
                roster[r["group_id"]].add((r["locus_tag"], r["organism_name"]))
                info.setdefault(r["locus_tag"], r)

        candidates = set()
        for gid, mem in roster.items():
            if mem and {o for _, o in mem} <= TARGET_SET:
                candidates.update(lt for lt, _ in mem)

        gene_groups: dict[str, set[str]] = defaultdict(set)
        newly = set()
        cands = sorted(candidates)
        for chunk in batched(cands, GENE_BATCH):
            for r in gene_homologs(locus_tags=chunk, limit=None, conn=conn)["results"]:
                gene_groups[r["locus_tag"]].add(r["group_id"])
                if r["group_id"] not in roster:
                    newly.add(r["group_id"])
                    meta.setdefault(r["group_id"], r)
        for chunk in batched(sorted(newly), GROUP_BATCH):
            for r in genes_by_homolog_group(group_ids=chunk, limit=None, conn=conn)["results"]:
                roster[r["group_id"]].add((r["locus_tag"], r["organism_name"]))

        # Neighbourhoods that are fully inside the six ("specific" passes).
        specific: list[tuple[frozenset, dict[str, list[str]]]] = []
        seen: set[frozenset] = set()
        for lt in cands:
            hood: set[tuple[str, str]] = set()
            for gid in gene_groups.get(lt, ()):
                hood |= roster.get(gid, set())
            if not hood:
                continue
            by_org: dict[str, list[str]] = defaultdict(list)
            for m_lt, m_org in hood:
                by_org[m_org].append(m_lt)
            if set(by_org) - TARGET_SET:
                continue
            key = frozenset(m for m, _ in hood)
            if key in seen:
                continue
            seen.add(key)
            specific.append((key, dict(by_org)))

        log.info("distinct specific neighbourhoods (nothing outside the six): %d", len(specific))

        cov = Counter(len(b) for _, b in specific)
        log.info("coverage histogram (strains covered -> neighbourhoods):")
        for k in sorted(cov, reverse=True):
            log.info("   %d/6 strains : %d", k, cov[k])

        # Which strain is missing from the 5/6 near-misses?
        miss = Counter()
        for _, b in specific:
            if len(b) == 5:
                miss[next(iter(TARGET_SET - set(b)))] += 1
        log.info("among 5/6 near-misses, the missing strain is:")
        for org, n in miss.most_common():
            log.info("   %-28s %d", org, n)

        # The 6/6 neighbourhoods that are NOT single-copy everywhere.
        for key, b in specific:
            if len(b) == 6 and any(len(v) != 1 for v in b.values()):
                dup = {o: v for o, v in b.items() if len(v) != 1}
                log.info("6/6 but multi-copy, so not a marker: %s", dup)

        # Leave-one-out: markers if we drop each strain in turn.
        loo_rows = []
        for drop in TARGETS + [None]:
            sub = TARGET_SET - {drop} if drop else TARGET_SET
            n = sum(1 for _, b in specific
                    if set(b) == sub and all(len(v) == 1 for v in b.values()))
            loo_rows.append({"dropped_strain": drop or "(none, all six)",
                             "strains_required": len(sub), "markers": n})
            log.info("drop %-28s -> %d single-copy core markers",
                     drop or "(none)", n)

    with open(OUT / "coverage_breakdown.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["strains_covered", "neighbourhoods"])
        for k in sorted(cov, reverse=True):
            w.writerow([k, cov[k]])
        w.writerow([])
        w.writerow(["missing_strain_among_5of6", "count"])
        for org, n in miss.most_common():
            w.writerow([org, n])
    with open(OUT / "leave_one_out.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["dropped_strain", "strains_required", "markers"])
        w.writeheader()
        w.writerows(loo_rows)
    log.info("wrote coverage_breakdown.csv, leave_one_out.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
