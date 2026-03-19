import unittest
import json
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from github_competitor_research import _dedupe, load_queries, parse_iso8601, days_since
from github_traffic_archiver import ensure_dir, append_jsonl, write_json


class MockArgs:
    def __init__(self, query=None, query_file=None):
        self.query = query or []
        self.query_file = query_file


class TestGitHubCompetitorResearch(unittest.TestCase):
    def test_dedupe(self):
        result = _dedupe(["foo", "Foo", "bar", "  Baz "])
        self.assertEqual(result, ["foo", "bar", "Baz"])

    def test_dedupe_empty(self):
        result = _dedupe([])
        self.assertEqual(result, [])

    def test_load_queries_from_args(self):
        args = MockArgs(query=["query1", "query2"])
        result = load_queries(args)
        self.assertEqual(result, ["query1", "query2"])

    def test_load_queries_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# comment\n")
            f.write("query1\n")
            f.write("query2\n")
            temp_path = f.name

        try:
            args = MockArgs(query_file=temp_path)
            result = load_queries(args)
            self.assertEqual(result, ["query1", "query2"])
        finally:
            os.unlink(temp_path)

    def test_load_queries_file_not_found(self):
        args = MockArgs(query_file="nonexistent.txt")
        with self.assertRaises(Exception):
            load_queries(args)

    def test_parse_iso8601_valid(self):
        result = parse_iso8601("2024-01-15T10:30:00Z")
        self.assertIsNotNone(result)

    def test_parse_iso8601_empty(self):
        result = parse_iso8601("")
        self.assertIsNone(result)

    def test_parse_iso8601_invalid(self):
        result = parse_iso8601("not-a-date")
        self.assertIsNone(result)

    def test_days_since(self):
        result = days_since("2024-01-15T10:30:00Z")
        self.assertIsInstance(result, int)


class TestGitHubTrafficArchiver(unittest.TestCase):
    def test_ensure_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, "subdir", "nested")
            ensure_dir(test_path)
            self.assertTrue(os.path.exists(test_path))

    def test_write_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            data = {"key": "value", "number": 123}
            write_json(temp_path, data)
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            self.assertEqual(loaded, data)
        finally:
            os.unlink(temp_path)

    def test_append_jsonl(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            temp_path = f.name

        try:
            append_jsonl(temp_path, {"a": 1})
            append_jsonl(temp_path, {"b": 2})
            with open(temp_path, 'r') as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertIn('"a":1', lines[0])
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
