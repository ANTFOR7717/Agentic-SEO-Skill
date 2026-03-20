import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from utils.generate_report import detect_environment, run_script, generate_html


class TestGenerateReport(unittest.TestCase):
    def test_detect_environment_wordpress(self):
        html = '<meta name="generator" content="WordPress"><link rel="wp-content/themes)'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "WordPress")
        self.assertEqual(result["runtime"], "Managed CMS")
        self.assertEqual(result["confidence"], "high")

    def test_detect_environment_astro(self):
        html = '<meta name="generator" content="Astro v5.5.2">'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Unknown")

    def test_detect_environment_shopify(self):
        html = '<link rel="stylesheet" href="cdn.shopify.com/s/files">'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Shopify")

    def test_detect_environment_nextjs(self):
        html = '<script src="/_next/static/chunks/main.js">'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Next.js")
        self.assertEqual(result["runtime"], "JavaScript Framework")

    def test_detect_environment_wix(self):
        html = '<link rel="stylesheet" href="wixstatic.com/static">'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Wix")

    def test_detect_environment_webflow(self):
        html = '<script src="https://uploads.webflow.com"></script>'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Webflow")

    def test_detect_environment_squarespace(self):
        html = '<script src="static1.squarespace.com"></script>'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Squarespace")

    def test_detect_environment_blogger(self):
        html = '<link rel="stylesheet" href="blogger.googleapis.com">'
        result = detect_environment(html, "https://example.blogspot.com")
        self.assertEqual(result["primary"], "Blogger")

    def test_detect_environment_ghost(self):
        html = '<meta name="generator" content="Ghost">'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Ghost")

    def test_detect_environment_nuxt(self):
        html = '<script src="/_nuxt/app.js"></script>'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Nuxt")

    def test_detect_environment_unknown(self):
        html = '<html><body>Just some plain HTML</body></html>'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["primary"], "Unknown")
        self.assertEqual(result["confidence"], "low")

    def test_detect_environment_empty_html(self):
        result = detect_environment("", "https://example.com")
        self.assertEqual(result["primary"], "Unknown")

    def test_detect_environment_multiple_cms(self):
        html = '<meta name="generator" content="WordPress"><script src="/_next/static">'
        result = detect_environment(html, "https://example.com")
        self.assertIn(result["primary"], ["WordPress", "Next.js"])

    def test_detect_environment_confidence_high(self):
        html = '<link rel="wp-content/themes"><link rel="wp-includes/"><script src="wp-includes/js"></script><meta name="generator" content="WordPress">'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["confidence"], "high")

    def test_detect_environment_confidence_medium(self):
        html = '<link rel="wp-content/themes"><link rel="wp-includes/">'
        result = detect_environment(html, "https://example.com")
        self.assertEqual(result["confidence"], "medium")

    def test_detect_environment_alternatives(self):
        html = '<script src="/_next/"><link rel="wp-content/">'
        result = detect_environment(html, "https://example.com")
        self.assertTrue(len(result["alternatives"]) <= 2)

    def test_run_script_not_found(self):
        result = run_script("nonexistent.py", [])
        self.assertIn("not found", result["error"])

    @patch("os.path.exists")
    def test_run_script_with_args(self, mock_exists):
        mock_exists.return_value = True
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"test": "data"}'
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            result = run_script("test_script.py", ["--arg", "value"])
            self.assertEqual(result, {"test": "data"})

    @patch("os.path.exists")
    def test_run_script_timeout(self, mock_exists):
        mock_exists.return_value = True
        with patch("subprocess.run") as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 60)

            result = run_script("test_script.py", [])
            self.assertIn("timed out", result["error"])

    @patch("os.path.exists")
    def test_run_script_invalid_json(self, mock_exists):
        mock_exists.return_value = True
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "not valid json"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            result = run_script("test_script.py", [])
            self.assertIn("Invalid JSON", result["error"])

    @patch("os.path.exists")
    def test_run_script_nonzero_exit(self, mock_exists):
        mock_exists.return_value = True
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Script error"
            mock_run.return_value = mock_result

            result = run_script("test_script.py", [])
            self.assertIn("error", result["error"].lower())

    def test_social_meta_optional_tags(self):
        data = {
            "url": "https://example.com",
            "domain": "example.com",
            "timestamp": "2026-01-01T00:00:00",
            "environment": {"primary": "WordPress", "runtime": "Managed CMS", "confidence": "high", "signals": [], "alternatives": []},
            "sections": {
                "social": {
                    "score": 85,
                    "og_tags": {"og:title": "Test", "og:description": "Desc", "og:image": "img.jpg", "og:url": "https://example.com", "og:type": "website"},
                    "twitter_tags": {"twitter:card": "summary_large_image", "twitter:title": "Test", "twitter:description": "Desc", "twitter:image": "img.jpg"},
                }
            },
            "environment_fixes": []
        }
        scores = {"categories": {"social": 85}, "overall": 85}
        html = generate_html(data, scores)
        self.assertIn("og:locale", html)
        self.assertIn("twitter:creator", html)
        self.assertIn("Optional", html)

    def test_social_meta_all_present(self):
        data = {
            "url": "https://example.com",
            "domain": "example.com",
            "timestamp": "2026-01-01T00:00:00",
            "environment": {"primary": "WordPress", "runtime": "Managed CMS", "confidence": "high", "signals": [], "alternatives": []},
            "sections": {
                "social": {
                    "score": 100,
                    "og_tags": {"og:title": "Test", "og:description": "Desc", "og:image": "img.jpg", "og:url": "https://example.com", "og:type": "website", "og:site_name": "Test", "og:locale": "en_US"},
                    "twitter_tags": {"twitter:card": "summary_large_image", "twitter:title": "Test", "twitter:description": "Desc", "twitter:image": "img.jpg", "twitter:site": "@test", "twitter:creator": "@test"},
                }
            },
            "environment_fixes": []
        }
        scores = {"categories": {"social": 100}, "overall": 100}
        html = generate_html(data, scores)
        self.assertIn("og:locale", html)
        self.assertIn("twitter:creator", html)
        self.assertIn("✅", html)


if __name__ == "__main__":
    unittest.main()
