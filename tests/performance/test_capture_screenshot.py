import unittest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from performance.capture_screenshot import capture_screenshot, VIEWPORTS


class TestCaptureScreenshot(unittest.TestCase):
    @patch("performance.capture_screenshot.sync_playwright")
    def test_capture_screenshot_success(self, mock_playwright):
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_page.goto.return_value = None
        mock_page.wait_for_timeout.return_value = None
        mock_page.screenshot.return_value = None
        
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")
            result = capture_screenshot("https://example.com", output_path, viewport="desktop")

            self.assertTrue(result["success"])
            self.assertIsNone(result["error"])

    @patch("performance.capture_screenshot.sync_playwright")
    def test_capture_screenshot_timeout(self, mock_playwright):
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        
        mock_browser = MagicMock()
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        mock_browser.new_context.side_effect = PlaywrightTimeout("Timeout")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")
            result = capture_screenshot("https://example.com", output_path, timeout=1000)

            self.assertFalse(result["success"])
            self.assertIn("timed out", result["error"])

    def test_capture_screenshot_invalid_viewport(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")
            result = capture_screenshot("https://example.com", output_path, viewport="invalid")

            self.assertFalse(result["success"])
            self.assertIn("Invalid viewport", result["error"])

    @patch("performance.capture_screenshot.sync_playwright")
    def test_capture_screenshot_generic_error(self, mock_playwright):
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        
        mock_page.goto.side_effect = Exception("Network error")
        
        mock_context.new_page.return_value = mock_page
        mock_browser.new_context.return_value = mock_context
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.png")
            result = capture_screenshot("https://example.com", output_path)

            self.assertFalse(result["success"])
            self.assertIn("Network error", result["error"])

    def test_viewports_exist(self):
        self.assertIn("desktop", VIEWPORTS)
        self.assertIn("laptop", VIEWPORTS)
        self.assertIn("tablet", VIEWPORTS)
        self.assertIn("mobile", VIEWPORTS)
        self.assertEqual(VIEWPORTS["desktop"]["width"], 1920)
        self.assertEqual(VIEWPORTS["mobile"]["width"], 375)

    def test_viewports_have_height(self):
        for name, vp in VIEWPORTS.items():
            self.assertIn("width", vp)
            self.assertIn("height", vp)
            self.assertGreater(vp["width"], 0)
            self.assertGreater(vp["height"], 0)


if __name__ == "__main__":
    unittest.main()
