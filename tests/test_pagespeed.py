import unittest
import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from pagespeed import get_pagespeed, CWV_THRESHOLDS


class TestPagespeed(unittest.TestCase):
    def test_get_pagespeed_rate_limited(self):
        with patch("pagespeed.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 429
            mock_get.return_value = mock_resp

            result = get_pagespeed("https://example.com")

            self.assertIn("Rate limited", result["error"])

    def test_get_pagespeed_api_error(self):
        with patch("pagespeed.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 500
            mock_get.return_value = mock_resp

            result = get_pagespeed("https://example.com")

            self.assertIn("API error", result["error"])

    def test_get_pagespeed_timeout(self):
        import requests
        with patch("pagespeed.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()

            result = get_pagespeed("https://example.com")

            self.assertIn("timed out", result["error"])

    def test_get_pagespeed_connection_error(self):
        import requests
        with patch("pagespeed.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

            result = get_pagespeed("https://example.com")

            self.assertIn("Request failed", result["error"])

    def test_get_pagespeed_invalid_json(self):
        with patch("pagespeed.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.side_effect = json.JSONDecodeError("Invalid", "", 0)
            mock_get.return_value = mock_resp

            result = get_pagespeed("https://example.com")

            self.assertIn("Failed to parse", result["error"])

    def test_get_pagespeed_with_api_key(self):
        mock_response_data = {
            "lighthouseResult": {
                "categories": {"performance": {"score": 0.9}},
                "audits": {}
            }
        }

        with patch("pagespeed.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = mock_response_data
            mock_get.return_value = mock_resp

            result = get_pagespeed("https://example.com", api_key="test-api-key")

            call_args = mock_get.call_args
            self.assertIn("key", call_args.kwargs["params"])
            self.assertEqual(call_args.kwargs["params"]["key"], "test-api-key")

    def test_cwv_thresholds_exist(self):
        self.assertIn("LCP", CWV_THRESHOLDS)
        self.assertIn("INP", CWV_THRESHOLDS)
        self.assertIn("CLS", CWV_THRESHOLDS)
        self.assertIn("FCP", CWV_THRESHOLDS)
        self.assertIn("TTFB", CWV_THRESHOLDS)


if __name__ == "__main__":
    unittest.main()
