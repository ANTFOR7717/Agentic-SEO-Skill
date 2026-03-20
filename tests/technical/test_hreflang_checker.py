# tests/test_hreflang_checker.py
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from technical.hreflang_checker import (
    validate_lang_code,
    check_x_default,
    check_self_reference,
    check_protocol_consistency,
)


DATA_FILE = Path(__file__).parent.parent / "data" / "hreflang_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestValidateLangCode:
    @pytest.mark.parametrize("case", CASES["validate_lang_code"])
    def test_validate_lang_code(self, case):
        result = validate_lang_code(case["tag"])
        assert result["valid"] == case["expected_valid"]
        if "expected_lang" in case:
            assert result["lang"] == case["expected_lang"]
        if "expected_region" in case:
            assert result["region"] == case["expected_region"]


class TestCheckXDefault:
    @pytest.mark.parametrize("case", CASES["check_x_default"])
    def test_check_x_default(self, case):
        result = check_x_default(case["tags"])
        assert result["passed"] == case["expected_passed"]


class TestCheckSelfReference:
    @pytest.mark.parametrize("case", CASES["check_self_reference"])
    def test_check_self_reference(self, case):
        result = check_self_reference(case["tags"], case["page_url"])
        assert result["passed"] == case["expected_passed"]


class TestCheckProtocolConsistency:
    @pytest.mark.parametrize("case", CASES["check_protocol_consistency"])
    def test_check_protocol_consistency(self, case):
        result = check_protocol_consistency(case["tags"])
        assert result["passed"] == case["expected_passed"]
