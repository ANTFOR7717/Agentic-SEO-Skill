import unittest
import json
import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from github.github_repo_audit import parse_iso8601, days_since, local_file_signals


class TestGitHubRepoAudit(unittest.TestCase):
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

    def test_days_since_empty(self):
        result = days_since("")
        self.assertIsNone(result)

    def test_local_file_signals(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "README.md"), "w").close()
            open(os.path.join(tmpdir, "LICENSE"), "w").close()
            open(os.path.join(tmpdir, "CONTRIBUTING.md"), "w").close()
            
            result = local_file_signals(tmpdir)
            
            self.assertTrue(result["README.md"])
            self.assertTrue(result["LICENSE"])
            self.assertTrue(result["CONTRIBUTING.md"])
            self.assertFalse(result["CODE_OF_CONDUCT.md"])


if __name__ == "__main__":
    unittest.main()
