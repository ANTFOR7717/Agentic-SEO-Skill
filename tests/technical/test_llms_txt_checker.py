# tests/test_llms_txt_checker.py
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from technical.llms_txt_checker import _parse_llms_txt, _score_quality


DATA_FILE = Path(__file__).parent.parent / "data" / "llms_txt_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


def make_result(content=""):
    return {
        "content": content,
        "parsed": {
            "title": None,
            "description": None,
            "sections": [],
            "links": [],
        },
        "quality": {
            "score": 0,
            "issues": [],
            "suggestions": [],
        },
    }


class TestParseLlmsTxt:
    @pytest.mark.parametrize("case", CASES["parse_llms_txt"])
    def test_parse_llms_txt(self, case):
        result = make_result(case["content"])
        _parse_llms_txt(case["content"], result)
        
        assert result["parsed"]["title"] == case["expected_title"]
        assert result["parsed"]["description"] == case["expected_description"]
        assert len(result["parsed"]["sections"]) == case["expected_sections"]
        assert len(result["parsed"]["links"]) == case["expected_links"]
        
        if case.get("expect_empty_issue"):
            assert len(result["quality"]["issues"]) > 0


class TestScoreQuality:
    @pytest.mark.parametrize("case", CASES["score_quality"])
    def test_score_quality(self, case):
        result = make_result(case["content"])
        _parse_llms_txt(case["content"], result)
        _score_quality(result)
        
        if "expected_score_min" in case:
            assert result["quality"]["score"] >= case["expected_score_min"]
        if "expected_score_max" in case:
            assert result["quality"]["score"] <= case["expected_score_max"]
