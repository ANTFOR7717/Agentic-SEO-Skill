import unittest
import json
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from github.github_seo_report import (
    _normalize_query_phrase,
    _dedupe_queries,
    load_explicit_queries,
    derive_auto_queries,
    extract_score,
    dedupe_preserve,
)


class MockArgs:
    def __init__(self, query=None, query_file=None):
        self.query = query or []
        self.query_file = query_file


class TestGitHubSeoReport(unittest.TestCase):
    def test_normalize_query_phrase(self):
        result = _normalize_query_phrase("This is a TEST phrase 123")
        self.assertEqual(result, "this is test phrase 123")

    def test_normalize_query_phrase_with_stop_words(self):
        result = _normalize_query_phrase("the best SEO tool")
        self.assertEqual(result, "best seo tool")

    def test_normalize_query_phrase_empty(self):
        result = _normalize_query_phrase("")
        self.assertEqual(result, "")

    def test_normalize_query_phrase_only_stop_words(self):
        result = _normalize_query_phrase("the a an")
        self.assertEqual(result, "the an")

    def test_dedupe_queries(self):
        result = _dedupe_queries(["Foo", "foo", "Bar", "  baz  "])
        self.assertEqual(result, ["Foo", "Bar", "baz"])

    def test_dedupe_queries_empty(self):
        result = _dedupe_queries([])
        self.assertEqual(result, [])

    def test_dedupe_queries_with_empty(self):
        result = _dedupe_queries(["test", "", "  "])
        self.assertEqual(result, ["test"])

    def test_load_explicit_queries_from_args(self):
        args = MockArgs(query=["query1", "query2"])
        queries, warnings = load_explicit_queries(args)
        self.assertEqual(queries, ["query1", "query2"])

    def test_load_explicit_queries_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# comment\n")
            f.write("query1\n")
            f.write("query2\n")
            temp_path = f.name

        try:
            args = MockArgs(query_file=temp_path)
            queries, warnings = load_explicit_queries(args)
            self.assertEqual(queries, ["query1", "query2"])
        finally:
            os.unlink(temp_path)

    def test_load_explicit_queries_file_not_found(self):
        args = MockArgs(query_file="nonexistent.txt")
        queries, warnings = load_explicit_queries(args)
        self.assertEqual(len(warnings), 1)

    def test_load_explicit_queries_dedupe(self):
        args = MockArgs(query=["same", "same", "different"])
        queries, warnings = load_explicit_queries(args)
        self.assertEqual(queries, ["same", "different"])

    def test_derive_auto_queries_from_repo_name(self):
        repo = "owner/repo-name"
        repo_audit_data = {}
        result = derive_auto_queries(repo, repo_audit_data, max_queries=3)
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) <= 3)

    def test_derive_auto_queries_from_topics(self):
        repo = "owner/test"
        repo_audit_data = {
            "metadata": {
                "topics": ["python", "seo", "automation"]
            }
        }
        result = derive_auto_queries(repo, repo_audit_data, max_queries=6)
        self.assertIsInstance(result, list)

    def test_extract_score_all_ok(self):
        outputs = {
            "repo_audit": {"ok": True, "data": {"summary": {"score": 80}}},
            "readme_lint": {"ok": True, "data": {"summary": {"score": 70}}},
            "community_health": {"ok": True, "data": {"summary": {"score": 90}}},
        }
        result = extract_score(outputs)
        self.assertEqual(result["overall"], 75.0)

    def test_extract_score_with_failures(self):
        outputs = {
            "repo_audit": {"ok": False, "error": "failed"},
            "readme_lint": {"ok": True, "data": {"summary": {"score": 70}}},
        }
        result = extract_score(outputs)
        self.assertEqual(result["overall"], 70.0)

    def test_extract_score_empty(self):
        outputs = {}
        result = extract_score(outputs)
        self.assertIsNone(result["overall"])

    def test_dedupe_preserve(self):
        result = dedupe_preserve(["foo", "  foo", "bar", "foo"])
        self.assertEqual(result, ["foo", "bar"])


if __name__ == "__main__":
    unittest.main()
