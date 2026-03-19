import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from social_meta import check_social_meta


class TestSocialMeta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), "data", "social_meta_cases.json")
        with open(data_path, "r") as f:
            cls.cases = json.load(f)

    def _run_case(self, case):
        if "mock_status" in case:
            with patch("social_meta.requests.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.status_code = case["mock_status"]
                mock_resp.text = ""
                mock_get.return_value = mock_resp
                result = check_social_meta("https://example.com")
        elif "mock_exception" in case:
            import requests
            with patch("social_meta.requests.get") as mock_get:
                mock_get.side_effect = requests.exceptions.RequestException(case["mock_exception"])
                result = check_social_meta("https://example.com")
        else:
            with patch("social_meta.requests.get") as mock_get:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.text = case["html"]
                mock_get.return_value = mock_resp
                result = check_social_meta("https://example.com")

        expected = case["expected"]

        if "score" in expected:
            self.assertEqual(result["score"], expected["score"], case["name"])

        if "og_present" in expected:
            self.assertEqual(result["og_present"], expected["og_present"], case["name"])

        if "og_missing" in expected:
            self.assertEqual(result["og_missing"], expected["og_missing"], case["name"])

        if "twitter_present" in expected:
            self.assertEqual(result["twitter_present"], expected["twitter_present"], case["name"])

        if "twitter_missing" in expected:
            self.assertEqual(result["twitter_missing"], expected["twitter_missing"], case["name"])

        if "issues" in expected:
            self.assertEqual(result["issues"], expected["issues"], case["name"])

        if "error" in expected:
            self.assertEqual(result["error"], expected["error"], case["name"])

        if "preview" in expected:
            self.assertEqual(result["preview"], expected["preview"], case["name"])

        if "recommendations" in expected:
            self.assertEqual(result["recommendations"], expected["recommendations"], case["name"])

    def test_complete_og_and_twitter_tags(self):
        self._run_case(self.cases[0])

    def test_missing_required_og_tags(self):
        self._run_case(self.cases[1])

    def test_og_tag_too_long(self):
        self._run_case(self.cases[2])

    def test_relative_og_image_url(self):
        self._run_case(self.cases[3])

    def test_invalid_twitter_card_type(self):
        self._run_case(self.cases[4])

    def test_no_social_meta_tags_at_all(self):
        self._run_case(self.cases[5])

    def test_http_error_on_fetch(self):
        self._run_case(self.cases[6])

    def test_request_exception(self):
        self._run_case(self.cases[7])

    def test_og_image_with_dimensions_recommendation(self):
        html = """<!DOCTYPE html><html><head>
        <meta property='og:title' content='Test Title'>
        <meta property='og:description' content='This is a test description that is long enough.'>
        <meta property='og:image' content='https://example.com/image.jpg'>
        <meta property='og:url' content='https://example.com/page'>
        <meta property='og:type' content='website'>
        <meta name='twitter:card' content='summary_large_image'>
        </head><body></body></html>"""
        with patch("social_meta.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = html
            mock_get.return_value = mock_resp
            result = check_social_meta("https://example.com")

        recs = result["recommendations"]
        self.assertTrue(any("og:image:width" in r for r in recs))

    def test_fallback_to_twitter_title(self):
        html = """<!DOCTYPE html><html><head>
        <meta property='og:title' content='OG Title'>
        <meta property='og:description' content='This is a test description that is long enough for OG purposes.'>
        <meta property='og:image' content='https://example.com/image.jpg'>
        <meta property='og:url' content='https://example.com/page'>
        <meta property='og:type' content='website'>
        <meta name='twitter:card' content='summary_large_image'>
        <meta name='twitter:title' content='Twitter Title'>
        <meta name='twitter:description' content='Twitter description here.'>
        </head><body><title>HTML Title</title></body></html>"""
        with patch("social_meta.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = html
            mock_get.return_value = mock_resp
            result = check_social_meta("https://example.com")

        self.assertEqual(result["preview"]["title"], "OG Title")


if __name__ == "__main__":
    unittest.main()
