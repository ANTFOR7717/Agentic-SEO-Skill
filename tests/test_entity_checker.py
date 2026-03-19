# tests/test_entity_checker.py
import json
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from scripts.entity_checker import (
    extract_entities_from_schema,
    analyze_sameas,
)


DATA_FILE = Path(__file__).parent / "data" / "entity_checker_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestExtractEntitiesFromSchema:
    @pytest.mark.parametrize("case", CASES["extract_entities_from_schema"])
    def test_extract_entities(self, case):
        soup = BeautifulSoup(case["html"], "html.parser")
        entities = extract_entities_from_schema(soup)
        assert len(entities) == case["expected_count"]
        if case["expected_count"] > 0 and "expected_type" in case:
            assert entities[0]["type"] == case["expected_type"]


class TestAnalyzeSameas:
    @pytest.mark.parametrize("case", CASES["analyze_sameas"])
    def test_analyze_sameas(self, case):
        result = analyze_sameas(case["same_as"])
        assert result["total_found"] == case["expected_found"]
        assert result["total_missing_critical"] == case["expected_missing_critical"]
