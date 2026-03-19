import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from analyze_visual import analyze_visual


class TestAnalyzeVisual(unittest.TestCase):
    @patch("analyze_visual.sync_playwright")
    def test_analyze_visual_success(self, mock_playwright):
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_h1 = MagicMock()
        mock_h1.bounding_box.return_value = {"y": 500, "x": 0, "width": 800, "height": 50}
        mock_page.query_selector.side_effect = lambda sel: mock_h1 if sel == "h1" else None
        
        mock_page.query_selector_all.return_value = []
        
        def evaluate_side_effect(script):
            if "scrollWidth" in script:
                return 375
            if "innerWidth" in script:
                return 375
            if "fontSize" in script:
                return 16
            return None
        
        mock_page.evaluate.side_effect = evaluate_side_effect
        
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

        result = analyze_visual("https://example.com")

        self.assertIsNone(result["error"])
        self.assertEqual(result["url"], "https://example.com")
        mock_browser.close.assert_called_once()

    @patch("analyze_visual.sync_playwright")
    def test_analyze_visual_timeout(self, mock_playwright):
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        
        mock_browser = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.side_effect = PlaywrightTimeout("Timeout")

        result = analyze_visual("https://example.com", timeout=1000)

        self.assertIsNotNone(result["error"])
        self.assertIn("timed out", result["error"])

    @patch("analyze_visual.sync_playwright")
    def test_analyze_visual_private_ip(self, mock_playwright):
        result = analyze_visual("http://192.168.1.1")

        self.assertIsNotNone(result["error"])
        self.assertIn("private/internal IP", result["error"])

    @patch("analyze_visual.sync_playwright")
    def test_analyze_visual_loopback_ip(self, mock_playwright):
        result = analyze_visual("http://127.0.0.1")

        self.assertIsNotNone(result["error"])
        self.assertIn("private/internal IP", result["error"])

    def test_analyze_visual_returns_dict(self):
        with patch("analyze_visual.sync_playwright"):
            result = analyze_visual("https://example.com")
            self.assertIn("url", result)
            self.assertIn("above_fold", result)
            self.assertIn("mobile", result)
            self.assertIn("fonts", result)


if __name__ == "__main__":
    unittest.main()
