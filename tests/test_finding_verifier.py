import unittest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from finding_verifier import canonical_key, should_suppress, verify_findings


class TestFindingVerifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data_path = os.path.join(os.path.dirname(__file__), "data", "finding_verifier_cases.json")
        with open(data_path, "r") as f:
            cls.cases = json.load(f)

    def test_canonical_key_missing_required(self):
        case = self.cases[0]
        result = canonical_key(case["finding"])
        self.assertEqual(result, case["expected_key"])

    def test_canonical_key_missing_recommended(self):
        case = self.cases[1]
        result = canonical_key(case["finding"])
        self.assertEqual(result, case["expected_key"])

    def test_canonical_key_community_profile(self):
        case = self.cases[2]
        result = canonical_key(case["finding"])
        self.assertEqual(result, case["expected_key"])

    def test_canonical_key_generic(self):
        case = self.cases[3]
        result = canonical_key(case["finding"])
        self.assertEqual(result, case["expected_key"])

    def test_should_suppress_no_code_examples(self):
        finding = {"finding": "No code examples detected in README."}
        context = {"readme_metrics": {"code_block_count": 5}}
        suppressed, reason = should_suppress(finding, context)
        self.assertTrue(suppressed)

    def test_should_suppress_no_code_examples_negative(self):
        finding = {"finding": "No code examples detected in README."}
        context = {"readme_metrics": {"code_block_count": 0}}
        suppressed, reason = should_suppress(finding, context)
        self.assertFalse(suppressed)

    def test_should_suppress_h1_count(self):
        finding = {"finding": "README should contain exactly one H1 heading."}
        context = {"readme_metrics": {"h1_count": 1}}
        suppressed, reason = should_suppress(finding, context)
        self.assertTrue(suppressed)

    def test_should_suppress_h1_count_negative(self):
        finding = {"finding": "README should contain exactly one H1 heading."}
        context = {"readme_metrics": {"h1_count": 0}}
        suppressed, reason = should_suppress(finding, context)
        self.assertFalse(suppressed)

    def test_should_suppress_install_section(self):
        finding = {"finding": "Installation/quickstart section is missing."}
        context = {"readme_metrics": {"has_install_section": True}}
        suppressed, reason = should_suppress(finding, context)
        self.assertTrue(suppressed)

    def test_should_suppress_shallow_sectioning(self):
        finding = {"finding": "README sectioning is shallow."}
        context = {"readme_metrics": {"heading_count": 5}}
        suppressed, reason = should_suppress(finding, context)
        self.assertTrue(suppressed)

    def test_should_suppress_no_context(self):
        finding = {"finding": "Some finding."}
        suppressed, reason = should_suppress(finding, None)
        self.assertFalse(suppressed)

    def test_verify_findings_deduplication(self):
        findings = [
            {"finding": "Missing README", "severity": "Warning", "source": "source1"},
            {"finding": "Missing README", "severity": "Critical", "source": "source2"},
        ]
        result = verify_findings(findings)
        self.assertEqual(result["verified_count"], 1)
        self.assertEqual(result["raw_count"], 2)
        self.assertEqual(result["findings"][0]["severity"], "Critical")

    def test_verify_findings_empty(self):
        result = verify_findings([])
        self.assertEqual(result["verified_count"], 0)
        self.assertEqual(result["raw_count"], 0)

    def test_verify_findings_none(self):
        result = verify_findings(None)
        self.assertEqual(result["verified_count"], 0)
        self.assertEqual(result["raw_count"], 0)

    def test_verify_findings_with_suppression(self):
        findings = [
            {"finding": "No code examples detected in README.", "severity": "Warning", "source": "test"},
        ]
        context = {"readme_metrics": {"code_block_count": 10}}
        result = verify_findings(findings, context)
        self.assertEqual(result["verified_count"], 0)
        self.assertEqual(len(result["dropped"]), 1)

    def test_verify_findings_sorting(self):
        findings = [
            {"finding": "Info issue", "severity": "Info"},
            {"finding": "Critical issue", "severity": "Critical"},
            {"finding": "Warning issue", "severity": "Warning"},
        ]
        result = verify_findings(findings)
        self.assertEqual(result["findings"][0]["severity"], "Critical")
        self.assertEqual(result["findings"][1]["severity"], "Warning")
        self.assertEqual(result["findings"][2]["severity"], "Info")


if __name__ == "__main__":
    unittest.main()
