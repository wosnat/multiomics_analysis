"""kg_fetch: the single fetch helper for every KG call in the pipeline (API-review fixes C1, M4-M6).

Why no SKIP/LIMIT paging: several tools sort on non-unique keys (e.g. metabolites_by_gene), so
offset pages can duplicate and drop rows while totals still match (PMM0331, PMM1590). Every call
is therefore made ONCE with a large limit (limit=None where the tool accepts it), optionally
chunked over an input list, and then checked:
  - not truncated, and returned == total_matching, per call;
  - NO duplicates on the caller's natural key over the merged rows, BEFORE any de-duplication;
  - every envelope warning matches an expected pattern (else UnexpectedWarningError);
  - not_found / not_matched / wrong_ontology / wrong_level / resolved_aliases are logged.
The API function is passed in (dependency injection), so this module is unit-tested with fakes.
"""
from __future__ import annotations

import hashlib
import re

BIG_LIMIT = 10**6


class IncompleteFetchError(RuntimeError):
    pass


class DuplicateRowsError(RuntimeError):
    pass


class UnexpectedWarningError(RuntimeError):
    pass


class StrictInputError(RuntimeError):
    pass


def _nonempty(v) -> bool:
    """True if a not_found / wrong_* field carries anything (list, or dict of lists; None ignored)."""
    if v is None:
        return False
    if isinstance(v, dict):
        return any(_nonempty(x) for x in v.values())
    if isinstance(v, (list, tuple, set)):
        return len(v) > 0
    return bool(v)


def find_duplicates(rows, natural_key) -> list[tuple]:
    """Natural-key tuples that occur more than once (sorted). Example: two identical rows -> [key]."""
    seen, dup = set(), set()
    for r in rows:
        missing = [c for c in natural_key if c not in r]
        if missing:
            raise KeyError(f"natural key field(s) {missing} absent from row {list(r)[:8]}")
        k = tuple(r[c] for c in natural_key)
        if k in seen:
            dup.add(k)
        seen.add(k)
    return sorted(dup, key=lambda t: tuple("" if v is None else str(v) for v in t))


def _chunks(seq, n):
    seq = list(seq)
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _freeze(v):
    if isinstance(v, dict):
        return tuple(sorted((k, _freeze(x)) for k, x in v.items()))
    if isinstance(v, (list, tuple)):
        return tuple(_freeze(x) for x in v)
    return v


def fetch(fn, label, log, natural_key, chunk_param=None, chunk_size=None, limit_none_ok=False,
          expected_warnings=(), allow_identical_duplicates=False, strict_inputs=False, **kw) -> dict:
    """Call fn once (or once per chunk of kw[chunk_param]) with a big limit; verify; merge; log.

    Returns {"results": merged rows, "envelopes": [envelope without results, per call]}.
    Raises IncompleteFetchError (truncated / returned != total), DuplicateRowsError,
    UnexpectedWarningError.
    allow_identical_duplicates: collapse rows that are identical in EVERY field (logged as
    identical_duplicates_collapsed). Used only where the tool emits one row per hidden path, e.g.
    gene_ontology_terms(brite): one row per KO, so PMM0192 (K02031 + K02032) gets two identical rows
    for one BRITE node. Only rows with ontology_type == "brite" are ever collapsed; any other identical
    row, and any duplicate key with differing content, raises.
    strict_inputs: raise StrictInputError if not_found / wrong_ontology / wrong_level is non-empty in
    any envelope (curated inputs must all resolve).
    An empty chunked input list makes no call and returns no rows (n_calls 0).
    """
    limit = None if limit_none_ok else BIG_LIMIT
    if chunk_param:
        parts = list(_chunks(kw[chunk_param], chunk_size or len(kw[chunk_param]) or 1))
    else:
        parts = [None]
    rows, envs, total = [], [], 0
    warns = []
    for part in parts:
        call_kw = dict(kw)
        if part is not None:
            call_kw[chunk_param] = part
        res = fn(limit=limit, **call_kw)
        n = len(res.get("results", []))
        if res.get("truncated"):
            raise IncompleteFetchError(f"{label}: truncated (returned {n}, total {res.get('total_matching')})")
        if res.get("total_matching") is not None and n != res["total_matching"]:
            raise IncompleteFetchError(f"{label}: returned {n} != total_matching {res['total_matching']}")
        tm = res.get("total_matching")
        total += n if tm is None else tm
        rows.extend(res.get("results", []))
        envs.append({k: v for k, v in res.items() if k != "results"})
        warns.extend(res.get("warnings") or [])
    collapsed = 0
    if allow_identical_duplicates:
        seen, kept = set(), []
        for r in rows:
            f = _freeze(r)
            if r.get("ontology_type") == "brite" and f in seen:
                collapsed += 1
                continue
            seen.add(f)
            kept.append(r)
        rows = kept
    dups = find_duplicates(rows, natural_key)
    if dups:
        raise DuplicateRowsError(f"{label}: {len(dups)} duplicated natural keys {natural_key}, e.g. {dups[:3]}")
    if strict_inputs:
        for e in envs:
            for fld in ("not_found", "wrong_ontology", "wrong_level"):
                if _nonempty(e.get(fld)):
                    raise StrictInputError(f"{label}: {fld} = {str(e.get(fld))[:300]}")
    bad = [w for w in warns if not any(re.search(p, w) for p in expected_warnings)]
    if bad:
        raise UnexpectedWarningError(f"{label}: unexpected warning(s): {bad[:2]}")

    def merged(key):
        vals = [e.get(key) for e in envs if e.get(key)]
        if not vals:
            return None
        if isinstance(vals[0], dict):
            out = {}
            for v in vals:
                for k2, v2 in v.items():
                    if isinstance(v2, list):
                        out.setdefault(k2, []).extend(v2)
                    else:
                        out[k2] = v2
            return out
        if isinstance(vals[0], list):
            return [x for v in vals for x in v]
        return vals
    log.append({
        "call": label, "n_calls": len(parts), "total_matching": total, "returned": len(rows),
        "limit": "None" if limit is None else limit, "natural_key": list(natural_key),
        "duplicates_on_natural_key": 0, "identical_duplicates_collapsed": collapsed,
        "not_found": merged("not_found"), "not_matched_n": len(merged("not_matched") or []),
        "wrong_ontology": merged("wrong_ontology"), "wrong_level": merged("wrong_level"),
        "resolved_aliases": merged("resolved_aliases"), "warnings": sorted(set(warns)),
        "strict_inputs": strict_inputs,
        "params": {k: (v if not isinstance(v, list) or len(v) <= 20 else f"<list of {len(v)}>")
                   for k, v in kw.items() if k != "conn"},
    })
    return {"results": rows, "envelopes": envs}


def role_map_hash(role_map_df) -> str:
    """sha256 (first 16 hex) of the sorted (pfam_id, role) pairs: identifies the role map used."""
    pairs = sorted(zip(role_map_df["pfam_id"].astype(str), role_map_df["role"].astype(str)))
    return hashlib.sha256("\n".join(f"{a}\t{b}" for a, b in pairs).encode("utf-8")).hexdigest()[:16]
