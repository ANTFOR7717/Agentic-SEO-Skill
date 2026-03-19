# tests/test_duplicate_content.py
import json
from pathlib import Path

import pytest
from scripts.duplicate_content import shingle, jaccard_from_minhash


DATA_FILE = Path(__file__).parent / "data" / "duplicate_content_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestShingle:
    @pytest.mark.parametrize("case", CASES["shingle"])
    def test_shingle(self, case):
        result = shingle(case["text"], case["k"])
        assert len(result) >= case["expected_min"]


class TestJaccardFromMinhash:
    @pytest.mark.parametrize("case", CASES["jaccard_from_minhash"])
    def test_jaccard_from_minhash(self, case):
        result = jaccard_from_minhash(case["sig1"], case["sig2"])
        if "expected" in case:
            assert result == case["expected"]
        if "expected_min" in case:
            assert result >= case["expected_min"]
        if "expected_max" in case:
            assert result <= case["expected_max"]
