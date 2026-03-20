# tests/test_broken_links.py
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from links.broken_links import extract_links, check_broken_links


DATA_FILE = Path(__file__).parent.parent / "data" / "broken_links_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestExtractLinks:
    @pytest.mark.parametrize("case", CASES["extract_internal_links"])
    def test_extract_links(self, case):
        links = extract_links(case["html"], case["page_url"])
        assert len(links) == case["expected_count"]
        if "expected_anchor" in case and links:
            assert links[0]["anchor_text"] == case["expected_anchor"]
        if "expected_internal" in case:
            internal_count = sum(1 for l in links if l["is_internal"])
            assert internal_count == case["expected_internal"]


class TestTwitterToXConversion:
    @patch("links.broken_links.requests.get")
    def test_twitter_converted_to_x(self, mock_get):
        mock_page_resp = MagicMock()
        mock_page_resp.status_code = 200
        mock_page_resp.text = '<html><body><a href="https://twitter.com/testuser">@testuser</a></body></html>'
        
        mock_x_resp = MagicMock()
        mock_x_resp.status_code = 200
        
        def side_effect(url, *args, **kwargs):
            if url == "https://example.com":
                return mock_page_resp
            if "x.com" in url:
                return mock_x_resp
            return mock_page_resp
        
        mock_get.side_effect = side_effect
        
        result = check_broken_links("https://example.com")
        
        assert result["summary"]["broken"] == 0

    @patch("links.broken_links.requests.get")
    def test_twitter_404_on_x(self, mock_get):
        mock_page_resp = MagicMock()
        mock_page_resp.status_code = 200
        mock_page_resp.text = '<html><body><a href="https://twitter.com/nonexistent123">@nonexistent123</a></body></html>'
        
        mock_x_resp = MagicMock()
        mock_x_resp.status_code = 404
        
        def side_effect(url, *args, **kwargs):
            if url == "https://example.com":
                return mock_page_resp
            if "x.com" in url:
                return mock_x_resp
            return mock_page_resp
        
        mock_get.side_effect = side_effect
        
        result = check_broken_links("https://example.com")
        
        assert result["summary"]["broken"] == 1
