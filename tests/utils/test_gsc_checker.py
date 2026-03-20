import unittest
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from utils.gsc_checker import detect_opportunities


class TestGSCChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "gsc_cases.json")
        with open(data_path, "r") as f:
            cls.cases = json.load(f)

    def test_striking_distance_keyword(self):
        case = self.cases[0]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])
        self.assertEqual(opportunities[0]["type"], "striking_distance")

    def test_low_ctr_at_top_position(self):
        case = self.cases[1]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])
        self.assertEqual(opportunities[0]["type"], "low_ctr_top_position")

    def test_high_impressions_low_ctr(self):
        case = self.cases[2]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])
        expected_type = case.get("expected_type", "high_impressions_low_ctr")
        self.assertEqual(opportunities[0]["type"], expected_type)

    def test_multiple_opportunities(self):
        case = self.cases[3]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])

    def test_no_opportunities_good_ctr(self):
        case = self.cases[4]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])

    def test_below_threshold_impressions(self):
        case = self.cases[5]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])

    def test_empty_data(self):
        case = self.cases[6]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])

    def test_position_4_20_striking_distance(self):
        case = self.cases[7]
        opportunities = detect_opportunities(case["performance_data"])
        self.assertEqual(len(opportunities), case["expected_opportunities"])
        self.assertEqual(opportunities[0]["type"], "striking_distance")
        self.assertEqual(opportunities[0]["severity"], "High")

    def test_opportunity_contains_required_fields(self):
        data = [
            {"query": "test keyword", "page": "https://example.com/page", "position": 5, "impressions": 100, "clicks": 5, "ctr": 5.0}
        ]
        opportunities = detect_opportunities(data)
        opp = opportunities[0]
        self.assertIn("type", opp)
        self.assertIn("severity", opp)
        self.assertIn("query", opp)
        self.assertIn("page", opp)
        self.assertIn("position", opp)
        self.assertIn("finding", opp)
        self.assertIn("fix", opp)


if __name__ == "__main__":
    unittest.main()
