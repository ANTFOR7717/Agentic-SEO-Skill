# tests/test_article_seo.py
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from bs4 import BeautifulSoup
from content.article_seo import detect_cms, extract_keywords_frequency, extract_structured_data


DATA_FILE = Path(__file__).parent.parent / "data" / "article_seo_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestDetectCms:
    @pytest.mark.parametrize("case", CASES["detect_cms"])
    def test_detect_cms(self, case):
        soup = BeautifulSoup(case["html"], "html.parser")
        result = detect_cms(soup, case["url"])
        assert result == case["expected"]


class TestExtractKeywordsFrequency:
    @pytest.mark.parametrize("case", CASES["extract_keywords_frequency"])
    def test_extract_keywords_frequency(self, case):
        result = extract_keywords_frequency(case["text"], case["top_n"])
        assert len(result) >= case["expected_min"]


class TestExtractStructuredData:
    @pytest.mark.parametrize("case", CASES["extract_structured_data"])
    def test_extract_structured_data(self, case):
        soup = BeautifulSoup(case["html"], "html.parser")
        results = extract_structured_data(soup)
        
        assert len(results) == case["expected_count"]
        
        if "expected_types" in case:
            actual_types = [r["@type"] for r in results if "@type" in r]
            for t in case["expected_types"]:
                assert t in actual_types
                
        if "expected_errors" in case:
            actual_errors = [r["error"] for r in results if "error" in r]
            for e in case["expected_errors"]:
                assert e in actual_errors
