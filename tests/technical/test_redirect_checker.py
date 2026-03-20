# tests/test_redirect_checker.py
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest


DATA_FILE = Path(__file__).parent.parent / "data" / "redirect_checker_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestCheckRedirects:
    @pytest.mark.parametrize("case", CASES["check_redirects"])
    @patch('scripts.technical.redirect_checker.requests.head')
    def test_check_redirects(self, mock_head, case):
        from technical.redirect_checker import check_redirects
        
        # Build mock responses
        mock_responses = []
        for hop in case["mock_responses"]:
            mock_resp = Mock()
            mock_resp.status_code = hop["status"]
            mock_resp.elapsed.total_seconds.return_value = hop.get("time_ms", 0.1)
            mock_resp.headers = hop.get("headers", {})
            mock_responses.append(mock_resp)
        
        mock_head.side_effect = mock_responses
        
        result = check_redirects(case["url"])
        
        assert result["total_hops"] == case["expected_hops"]
        assert result["has_loop"] == case.get("expected_has_loop", False)
        if "expected_final_url" in case:
            assert result["final_url"] == case["expected_final_url"]
