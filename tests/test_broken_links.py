# tests/test_broken_links.py
import json
from pathlib import Path

import pytest
from scripts.broken_links import extract_links


DATA_FILE = Path(__file__).parent / "data" / "broken_links_cases.json"


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
