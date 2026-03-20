# tests/test_readability.py
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from content.readability import (
    count_syllables,
    split_sentences,
    is_navigation_noise,
    analyze_readability,
)


DATA_FILE = Path(__file__).parent.parent / "data" / "readability_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestSyllables:
    @pytest.mark.parametrize("case", CASES["count_syllables"])
    def test_count_syllables(self, case):
        result = count_syllables(case["word"])
        assert result == case["expected"]


class TestSplitSentences:
    @pytest.mark.parametrize("case", CASES["split_sentences"])
    def test_split_sentences(self, case):
        result = split_sentences(case["text"])
        assert result == case["expected"]


class TestNavigationNoise:
    @pytest.mark.parametrize("case", CASES["is_navigation_noise"])
    def test_is_navigation_noise(self, case):
        result = is_navigation_noise(case["sentence"])
        assert result == case["expected"]


class TestAnalyzeReadability:
    @pytest.mark.parametrize("case", CASES["analyze_readability"])
    def test_analyze_readability(self, case):
        result = analyze_readability(case["text"])
        if "expected_fre_min" in case:
            assert result["flesch_reading_ease"] >= case["expected_fre_min"]
        if "expected_fre_max" in case:
            assert result["flesch_reading_ease"] <= case["expected_fre_max"]
        if "expected_word_count" in case:
            assert result["word_count"] == case["expected_word_count"]
