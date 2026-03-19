# tests/test_competitor_gap.py
import json
from pathlib import Path

import pytest
from scripts.competitor_gap import normalize_topic


DATA_FILE = Path(__file__).parent / "data" / "competitor_gap_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestNormalizeTopic:
    @pytest.mark.parametrize("case", CASES["normalize_topic"])
    def test_normalize_topic(self, case):
        result = normalize_topic(case["text"])
        assert result == case["expected"]
