# tests/test_broken_links.py
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from links.broken_links import extract_links


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
