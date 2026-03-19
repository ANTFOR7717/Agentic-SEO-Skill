# tests/test_link_profile.py
import json
from pathlib import Path

import pytest
from scripts.link_profile import extract_links


DATA_FILE = Path(__file__).parent / "data" / "link_profile_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestExtractLinks:
    @pytest.mark.parametrize("case", CASES["extract_links"])
    def test_extract_links(self, case):
        result = extract_links(case["html"], case["page_url"], case["base_domain"])
        assert len(result["internal"]) + len(result["external"]) == case["expected_count"]
