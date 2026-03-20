# tests/test_security_headers.py
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest


DATA_FILE = Path(__file__).parent.parent / "data" / "security_headers_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestCheckSecurityHeaders:
    @pytest.mark.parametrize("case", CASES["check_security_headers"])
    @patch('scripts.technical.security_headers.requests.get')
    def test_check_security_headers(self, mock_get, case):
        from technical.security_headers import check_security_headers
        
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.url = "https://example.com"
        mock_resp.headers = case["headers"]
        mock_get.return_value = mock_resp
        
        result = check_security_headers(case["url"])
        
        assert result["score"] >= case["expected_score_min"]
        assert len(result["headers_missing"]) == case["expected_missing_count"]
