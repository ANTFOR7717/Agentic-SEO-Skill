# tests/test_validate_schema.py
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

import pytest
from schema.validate_schema import validate_jsonld


DATA_FILE = Path(__file__).parent.parent / "data" / "validate_schema_cases.json"


def load_cases():
    with open(DATA_FILE) as f:
        return json.load(f)


CASES = load_cases()


class TestValidateJsonld:
    @pytest.mark.parametrize("case", CASES["validate_jsonld"])
    def test_validate_jsonld(self, case):
        errors = validate_jsonld(case["html"])
        if "expected_error_count" in case:
            assert len(errors) == case["expected_error_count"]
        if "expected_errors" in case:
            assert errors == case["expected_errors"]
