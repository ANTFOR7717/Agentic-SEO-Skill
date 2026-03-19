import unittest
import json
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from github_search_benchmark import _dedupe, load_queries, run_query, summarize


class MockArgs:
    def __init__(self, query=None, query_file=None):
        self.query = query or []
        self.query_file = query_file


class TestGitHubSearchBenchmark(unittest.TestCase):
    def test_dedupe(self):
        result = _dedupe(["foo", "Foo", "bar", "Bar ", "baz"])
        self.assertEqual(result, ["foo", "bar", "baz"])

    def test_dedupe_empty(self):
        result = _dedupe([])
        self.assertEqual(result, [])

    def test_dedupe_with_empty_strings(self):
        result = _dedupe(["foo", "", "  ", "bar"])
        self.assertEqual(result, ["foo", "bar"])

    def test_load_queries_from_args(self):
        args = MockArgs(query=["query1", "query2"])
        result = load_queries(args)
        self.assertEqual(result, ["query1", "query2"])

    def test_load_queries_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# comment\n")
            f.write("query1\n")
            f.write("query2\n")
            f.write("\n")
            f.write("query3\n")
            temp_path = f.name

        try:
            args = MockArgs(query_file=temp_path)
            result = load_queries(args)
            self.assertEqual(result, ["query1", "query2", "query3"])
        finally:
            os.unlink(temp_path)

    def test_load_queries_file_not_found(self):
        args = MockArgs(query_file="nonexistent.txt")
        with self.assertRaises(Exception):
            load_queries(args)

    def test_load_queries_dedupe(self):
        args = MockArgs(query=["same", "same", "different"])
        result = load_queries(args)
        self.assertEqual(result, ["same", "different"])

    def test_summarize_all_found(self):
        results = [
            {"query": "q1", "target_found": True, "target_rank": 5},
            {"query": "q2", "target_found": True, "target_rank": 10},
        ]
        summary = summarize(results)
        self.assertEqual(summary["queries_total"], 2)
        self.assertEqual(summary["queries_found"], 2)
        self.assertEqual(summary["queries_not_found"], 0)
        self.assertEqual(summary["average_rank_when_found"], 7.5)

    def test_summarize_none_found(self):
        results = [
            {"query": "q1", "target_found": False},
            {"query": "q2", "target_found": False},
        ]
        summary = summarize(results)
        self.assertEqual(summary["queries_found"], 0)
        self.assertEqual(summary["queries_not_found"], 2)
        self.assertEqual(summary["average_rank_when_found"], None)

    def test_summarize_mixed(self):
        results = [
            {"query": "q1", "target_found": True, "target_rank": 3},
            {"query": "q2", "target_found": False},
        ]
        summary = summarize(results)
        self.assertEqual(summary["queries_found"], 1)
        self.assertEqual(summary["queries_not_found"], 1)
        self.assertEqual(summary["average_rank_when_found"], 3.0)

    def test_summarize_empty(self):
        results = []
        summary = summarize(results)
        self.assertEqual(summary["queries_total"], 0)
        self.assertEqual(summary["queries_found"], 0)
        self.assertIsNone(summary["average_rank_when_found"])


if __name__ == "__main__":
    unittest.main()
