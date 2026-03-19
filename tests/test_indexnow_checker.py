import unittest
import json
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from indexnow_checker import check_key_in_meta, check_key_file, check_robots_txt


class TestIndexNowChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), "data", "indexnow_cases.json")
        with open(data_path, "r") as f:
            cls.cases = json.load(f)

    def test_key_found_in_meta_tag(self):
        case = self.cases[0]
        result = check_key_in_meta(case["html"], case["key"])
        self.assertEqual(result["passed"], case["expected"]["passed"])
        self.assertEqual(result["detail"], case["expected"]["detail"])

    def test_key_not_in_meta_tag(self):
        case = self.cases[1]
        result = check_key_in_meta(case["html"], case["key"])
        self.assertEqual(result["passed"], case["expected"]["passed"])
        self.assertEqual(result["severity"], case["expected"]["severity"])

    def test_wrong_key_in_meta_tag(self):
        case = self.cases[2]
        result = check_key_in_meta(case["html"], case["key"])
        self.assertEqual(result["passed"], case["expected"]["passed"])

    def test_empty_html(self):
        case = self.cases[3]
        result = check_key_in_meta(case["html"], case["key"])
        self.assertEqual(result["passed"], case["expected"]["passed"])

    def test_key_file_found_and_matches(self):
        case = self.cases[4]
        with patch("indexnow_checker.fetch_url") as mock_fetch:
            mock_fetch.return_value = (case["key_file_status"], case["key_file_body"])
            result = check_key_file(case["site_url"], case["key"])
            self.assertEqual(result["passed"], case["expected"]["passed"])
            self.assertEqual(result["detail"], case["expected"]["detail"])

    def test_key_file_exists_but_key_doesnt_match(self):
        case = self.cases[5]
        with patch("indexnow_checker.fetch_url") as mock_fetch:
            mock_fetch.return_value = (case["key_file_status"], case["key_file_body"])
            result = check_key_file(case["site_url"], case["key"])
            self.assertEqual(result["passed"], case["expected"]["passed"])
            self.assertIn("does not contain the expected key", result["finding"])

    def test_key_file_not_found(self):
        case = self.cases[6]
        with patch("indexnow_checker.fetch_url") as mock_fetch:
            mock_fetch.return_value = (case["key_file_status"], case["key_file_body"])
            result = check_key_file(case["site_url"], case["key"])
            self.assertEqual(result["passed"], case["expected"]["passed"])
            self.assertEqual(result["severity"], case["expected"]["severity"])

    def test_robots_txt_contains_indexnow(self):
        case = self.cases[7]
        with patch("indexnow_checker.fetch_url") as mock_fetch:
            mock_fetch.return_value = (case["robots_status"], case["robots_body"])
            result = check_robots_txt(case["site_url"], case["key"])
            self.assertEqual(result["passed"], case["expected"]["passed"])

    def test_robots_txt_no_indexnow(self):
        case = self.cases[8]
        with patch("indexnow_checker.fetch_url") as mock_fetch:
            mock_fetch.return_value = (case["robots_status"], case["robots_body"])
            result = check_robots_txt(case["site_url"], case["key"])
            self.assertEqual(result["passed"], case["expected"]["passed"])

    def test_robots_txt_fetch_failure(self):
        with patch("indexnow_checker.fetch_url") as mock_fetch:
            mock_fetch.return_value = (None, "Connection error")
            result = check_robots_txt("https://example.com", "mykey")
            self.assertIsNone(result["passed"])


if __name__ == "__main__":
    unittest.main()
