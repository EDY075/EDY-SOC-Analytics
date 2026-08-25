import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.contract_validator import validate_file  # noqa: E402


class ContractTests(unittest.TestCase):
    def test_valid_sample_is_accepted(self):
        self.assertEqual(validate_file(ROOT / "contracts" / "samples" / "valid-export.json"), [])

    def test_invalid_sample_is_rejected(self):
        issues = validate_file(ROOT / "contracts" / "samples" / "invalid-export.json")
        self.assertGreaterEqual(len(issues), 8)

    def test_schema_declares_closed_objects(self):
        schema = json.loads((ROOT / "contracts" / "edy-siem-export.schema.json").read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(schema["$defs"]["securityRecord"]["additionalProperties"])


if __name__ == "__main__":
    unittest.main()

