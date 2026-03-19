# tests/test_robots_checker.py
import json
from pathlib import Path

import pytest
from scripts.robots_checker import _parse_robots


DATA_FILE = Path(__file__).parent / "data" / "robots_checker_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


def make_result():
    return {
        "user_agents": {},
        "sitemaps": [],
        "crawl_delays": {},
        "ai_crawler_status": {},
        "issues": [],
    }


class TestParseRobots:
    @pytest.mark.parametrize("case", CASES["parse_robots"])
    def test_parse_robots(self, case):
        result = make_result()
        _parse_robots(case["content"], result)
        
        assert len(result["user_agents"]) == case["expected_user_agents"]
        
        if "expected_sitemaps" in case:
            assert len(result["sitemaps"]) == case["expected_sitemaps"]
