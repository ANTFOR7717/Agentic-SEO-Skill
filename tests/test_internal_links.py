# tests/test_internal_links.py
import json
from pathlib import Path

import pytest
from scripts.internal_links import extract_internal_links


DATA_FILE = Path(__file__).parent / "data" / "internal_links_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestExtractInternalLinks:
    @pytest.mark.parametrize("case", CASES["extract_internal_links"])
    def test_extract_internal_links(self, case):
        result = extract_internal_links(case["html"], case["page_url"], case["domain"])
        assert len(result) == case["expected_count"]
