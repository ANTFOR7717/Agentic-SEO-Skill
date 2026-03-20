import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from fetch.fetch_page import fetch_page


class TestFetchPage(unittest.TestCase):
    def test_fetch_page_success(self):
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.url = "https://example.com"
            mock_response.headers = {"Content-Type": "text/html"}
            mock_response.history = []
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            result = fetch_page("https://example.com")

            self.assertEqual(result["status_code"], 200)
            self.assertEqual(result["url"], "https://example.com")
            self.assertIn("Test", result["content"])
            self.assertIsNone(result["error"])

    def test_fetch_page_invalid_scheme(self):
        result = fetch_page("ftp://example.com")
        self.assertIn("Invalid URL scheme", result["error"])

    def test_fetch_page_timeout(self):
        import requests
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = requests.exceptions.Timeout()
            mock_session_class.return_value = mock_session

            result = fetch_page("https://example.com", timeout=30)

            self.assertIn("timed out", result["error"])

    def test_fetch_page_connection_error(self):
        import requests
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection refused")
            mock_session_class.return_value = mock_session

            result = fetch_page("https://example.com")

            self.assertIn("Connection error", result["error"])

    def test_fetch_page_too_many_redirects(self):
        import requests
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = requests.exceptions.TooManyRedirects()
            mock_session_class.return_value = mock_session

            result = fetch_page("https://example.com", max_redirects=5)

            self.assertIn("Too many redirects", result["error"])

    def test_fetch_page_ssl_error(self):
        import requests
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_session.get.side_effect = requests.exceptions.SSLError("SSL verification failed")
            mock_session_class.return_value = mock_session

            result = fetch_page("https://example.com")

            self.assertIn("SSL error", result["error"])

    def test_fetch_page_with_redirects(self):
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            
            redirect_response = MagicMock()
            redirect_response.status_code = 301
            redirect_response.url = "https://example.com/old"
            redirect_response.headers = {}
            redirect_response.history = []
            
            final_response = MagicMock()
            final_response.status_code = 200
            final_response.text = "<html><body>Final</body></html>"
            final_response.url = "https://example.com/new"
            final_response.headers = {"Content-Type": "text/html"}
            final_response.history = [redirect_response]
            
            mock_session.get.return_value = final_response
            mock_session_class.return_value = mock_session

            result = fetch_page("https://example.com/old")

            self.assertEqual(result["status_code"], 200)
            self.assertEqual(len(result["redirect_chain"]), 1)

    def test_fetch_page_no_follow_redirects(self):
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 301
            mock_response.url = "https://example.com/old"
            mock_response.headers = {}
            mock_response.history = []
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            result = fetch_page("https://example.com/old", follow_redirects=False)

            self.assertEqual(result["status_code"], 301)

    def test_fetch_page_adds_https_scheme(self):
        with patch("scripts.fetch.fetch_page.requests.Session") as mock_session_class:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.url = "https://example.com"
            mock_response.headers = {}
            mock_response.history = []
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            result = fetch_page("example.com")

            self.assertIsNone(result["error"])
            mock_session.get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
