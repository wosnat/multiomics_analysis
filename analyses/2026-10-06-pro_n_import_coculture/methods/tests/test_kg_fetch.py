"""Tests for methods/kg_fetch.py: single-call fetch, chunking, duplicate detection, warning control.

Runner: stdlib unittest (pytest is not installed).
    .venv/Scripts/python.exe -m unittest discover -s analyses/2026-10-06-pro_n_import_coculture/methods/tests -v
Fake API functions stand in for multiomics_explorer calls (dependency injection; no KG access).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import kg_fetch as kf  # noqa: E402


def fake(rows_by_tag, warnings=(), truncate=False, total_offset=0, extra=None):
    """Fake API fn: returns rows for the requested locus_tags; records the calls made."""
    calls = []

    def fn(locus_tags, limit=None, offset=0, **kw):
        calls.append({"locus_tags": list(locus_tags), "limit": limit, "offset": offset, **kw})
        res = [r for t in locus_tags for r in rows_by_tag.get(t, [])]
        env = {"total_matching": len(res) + total_offset, "returned": len(res), "truncated": truncate,
               "warnings": list(warnings), "not_found": {"locus_tags": []}, "results": res}
        if extra:
            env.update(extra)
        return env
    fn.calls = calls
    return fn


ROWS = {
    "A": [{"locus_tag": "A", "metabolite_id": "m1", "tcdb_family_id": "f1"},
          {"locus_tag": "A", "metabolite_id": "m2", "tcdb_family_id": "f1"}],
    "B": [{"locus_tag": "B", "metabolite_id": "m1", "tcdb_family_id": "f2"}],
    "C": [{"locus_tag": "C", "metabolite_id": "m3", "tcdb_family_id": "f3"}],
}
KEY = ("locus_tag", "metabolite_id", "tcdb_family_id")


class TestFetch(unittest.TestCase):
    def test_single_call_big_limit_no_offset_paging(self):
        fn = fake(ROWS)
        log = []
        out = kf.fetch(fn, "t", log, natural_key=KEY, locus_tags=["A", "B", "C"])
        # 4 rows, one call, limit = BIG_LIMIT (never None unless allowed), offset 0
        self.assertEqual(len(out["results"]), 4)
        self.assertEqual(len(fn.calls), 1)
        self.assertEqual(fn.calls[0]["limit"], kf.BIG_LIMIT)
        self.assertEqual(log[0]["returned"], 4)
        self.assertEqual(log[0]["n_calls"], 1)

    def test_chunking_merges_and_counts(self):
        fn = fake(ROWS)
        log = []
        out = kf.fetch(fn, "t", log, natural_key=KEY, chunk_param="locus_tags", chunk_size=2,
                       locus_tags=["A", "B", "C"])
        # chunks [A,B] (3 rows) + [C] (1 row) -> 4 rows, 2 calls; total_matching summed = 4
        self.assertEqual(len(out["results"]), 4)
        self.assertEqual(len(fn.calls), 2)
        self.assertEqual(log[0]["total_matching"], 4)

    def test_duplicate_on_natural_key_raises(self):
        dup = {"A": ROWS["A"] + [dict(ROWS["A"][0])]}  # PMM0331-style duplicated row
        with self.assertRaises(kf.DuplicateRowsError):
            kf.fetch(fake(dup), "t", [], natural_key=KEY, locus_tags=["A"])

    def test_duplicate_detection_function(self):
        rows = ROWS["A"] + [dict(ROWS["A"][1])]
        d = kf.find_duplicates(rows, KEY)
        self.assertEqual(d, [("A", "m2", "f1")])
        self.assertEqual(kf.find_duplicates(ROWS["A"], KEY), [])

    def test_total_mismatch_raises(self):
        with self.assertRaises(kf.IncompleteFetchError):
            kf.fetch(fake(ROWS, total_offset=1), "t", [], natural_key=KEY, locus_tags=["A"])

    def test_truncated_raises(self):
        with self.assertRaises(kf.IncompleteFetchError):
            kf.fetch(fake(ROWS, truncate=True), "t", [], natural_key=KEY, locus_tags=["A"])

    def test_unexpected_warning_raises_expected_passes(self):
        fn = fake(ROWS, warnings=["transport_substrate_resolution is `family_inferred` for PMM0913"])
        with self.assertRaises(kf.UnexpectedWarningError):
            kf.fetch(fn, "t", [], natural_key=KEY, locus_tags=["A"])
        out = kf.fetch(fn, "t", [], natural_key=KEY, expected_warnings=[r"family_inferred"], locus_tags=["A"])
        self.assertEqual(len(out["results"]), 2)

    def test_limit_none_when_allowed(self):
        fn = fake(ROWS)
        kf.fetch(fn, "t", [], natural_key=KEY, limit_none_ok=True, locus_tags=["A"])
        self.assertIsNone(fn.calls[0]["limit"])

    def test_logs_wrong_ontology_level_aliases(self):
        fn = fake(ROWS, extra={"wrong_ontology": ["x"], "wrong_level": [], "resolved_aliases": {"C1": ["k:C1"]}})
        log = []
        kf.fetch(fn, "t", log, natural_key=KEY, locus_tags=["A"])
        self.assertEqual(log[0]["wrong_ontology"], ["x"])
        self.assertEqual(log[0]["resolved_aliases"], {"C1": ["k:C1"]})

    def test_rows_with_none_in_key_are_hashable(self):
        rows = {"A": [{"locus_tag": "A", "metabolite_id": "m1", "reaction_id": None},
                      {"locus_tag": "A", "metabolite_id": "m1", "reaction_id": "r1"}]}
        out = kf.fetch(fake(rows), "t", [], natural_key=("locus_tag", "metabolite_id", "reaction_id"),
                       locus_tags=["A"])
        self.assertEqual(len(out["results"]), 2)


class TestIdenticalDuplicates(unittest.TestCase):
    # gene_ontology_terms(brite) returns one row per KO path; PMM0192 has K02031 + K02032 under the same
    # BRITE node -> two IDENTICAL rows in one unpaged call. Policy: collapse only fully identical rows,
    # only when allowed, and log how many; a duplicate key with differing content still raises.
    def test_identical_collapsed_when_allowed(self):
        r = {"locus_tag": "A", "metabolite_id": "m1", "tcdb_family_id": "f1", "x": 1, "ontology_type": "brite"}
        log = []
        out = kf.fetch(fake({"A": [r, dict(r)]}), "t", log, natural_key=KEY,
                       allow_identical_duplicates=True, locus_tags=["A"])
        self.assertEqual(len(out["results"]), 1)
        self.assertEqual(log[0]["identical_duplicates_collapsed"], 1)

    def test_identical_raise_by_default(self):
        r = {"locus_tag": "A", "metabolite_id": "m1", "tcdb_family_id": "f1"}
        with self.assertRaises(kf.DuplicateRowsError):
            kf.fetch(fake({"A": [r, dict(r)]}), "t", [], natural_key=KEY, locus_tags=["A"])

    def test_differing_duplicates_raise_even_when_allowed(self):
        r1 = {"locus_tag": "A", "metabolite_id": "m1", "tcdb_family_id": "f1", "x": 1, "ontology_type": "brite"}
        r2 = dict(r1, x=2)
        with self.assertRaises(kf.DuplicateRowsError):
            kf.fetch(fake({"A": [r1, r2]}), "t", [], natural_key=KEY, allow_identical_duplicates=True,
                     locus_tags=["A"])


class TestReviewFixes(unittest.TestCase):
    def test_identical_non_brite_rows_still_raise_when_allowed(self):
        # collapse applies only to ontology_type == 'brite' rows (review item 4)
        r = {"locus_tag": "A", "metabolite_id": "m1", "tcdb_family_id": "f1", "ontology_type": "pfam"}
        with self.assertRaises(kf.DuplicateRowsError):
            kf.fetch(fake({"A": [r, dict(r)]}), "t", [], natural_key=KEY, allow_identical_duplicates=True,
                     locus_tags=["A"])

    def test_find_duplicates_missing_key_field_raises(self):
        with self.assertRaises(KeyError):
            kf.find_duplicates([{"locus_tag": "A"}], ("locus_tag", "metabolite_id"))

    def test_total_matching_none_or_absent(self):
        # envelope with total_matching None, and envelope without the key: count returned rows, no crash
        for extra in ({"total_matching": None}, {}):
            def fn(locus_tags, limit=None, **kw):
                env = {"results": [r for t in locus_tags for r in ROWS.get(t, [])], "truncated": False}
                env.update(extra)
                return env
            log = []
            out = kf.fetch(fn, "t", log, natural_key=KEY, locus_tags=["A", "B"])
            self.assertEqual(len(out["results"]), 3)
            self.assertEqual(log[0]["total_matching"], 3)

    def test_empty_chunk_input_makes_no_call(self):
        fn = fake(ROWS)
        log = []
        out = kf.fetch(fn, "t", log, natural_key=KEY, chunk_param="locus_tags", chunk_size=2, locus_tags=[])
        self.assertEqual(out["results"], [])
        self.assertEqual(len(fn.calls), 0)
        self.assertEqual(log[0]["n_calls"], 0)

    def test_duplicate_created_across_chunks_raises(self):
        rows = {"A": [{"locus_tag": "X", "metabolite_id": "m1", "tcdb_family_id": "f1"}],
                "B": [{"locus_tag": "X", "metabolite_id": "m1", "tcdb_family_id": "f1"}]}
        with self.assertRaises(kf.DuplicateRowsError):
            kf.fetch(fake(rows), "t", [], natural_key=KEY, chunk_param="locus_tags", chunk_size=1,
                     locus_tags=["A", "B"])

    def test_list_shaped_not_found_logged_and_strict(self):
        fn = fake(ROWS, extra={"not_found": ["Z1"]})
        log = []
        kf.fetch(fn, "t", log, natural_key=KEY, locus_tags=["A"])
        self.assertEqual(log[0]["not_found"], ["Z1"])
        with self.assertRaises(kf.StrictInputError):
            kf.fetch(fn, "t", [], natural_key=KEY, strict_inputs=True, locus_tags=["A"])

    def test_strict_inputs_dict_not_found_wrong_ontology_level(self):
        ok = fake(ROWS, extra={"not_found": {"locus_tags": [], "organism": None}, "wrong_ontology": [],
                               "wrong_level": []})
        kf.fetch(ok, "t", [], natural_key=KEY, strict_inputs=True, locus_tags=["A"])  # empty -> fine
        for extra in ({"not_found": {"metabolite_ids": ["C99999"]}}, {"wrong_ontology": ["go:1"]},
                      {"wrong_level": ["pfam:PF1"]}):
            with self.assertRaises(kf.StrictInputError):
                kf.fetch(fake(ROWS, extra=extra), "t", [], natural_key=KEY, strict_inputs=True, locus_tags=["A"])


class TestRoleMapHash(unittest.TestCase):
    def test_hash_stable_and_content_sensitive(self):
        import pandas as pd
        a = pd.DataFrame({"pfam_id": ["pfam:PF1", "pfam:PF2"], "role": ["atpase", "other"]})
        b = a.iloc[::-1]
        c = a.assign(role=["permease", "other"])
        self.assertEqual(kf.role_map_hash(a), kf.role_map_hash(b))  # order-independent
        self.assertNotEqual(kf.role_map_hash(a), kf.role_map_hash(c))


if __name__ == "__main__":
    unittest.main(verbosity=2)
