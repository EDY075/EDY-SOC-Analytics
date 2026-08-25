import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTENSIONS = {".md", ".py", ".json", ".csv", ".yml", ".yaml", ".tmdl", ".m", ".pbip", ".pbir"}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "aws key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "generic secret assignment": re.compile(r"(?i)(?:password|auth[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}
PERSONAL_PATH = re.compile(r"(?i)C:\\Users\\(?!Public(?:\\|$))[^\\\s]+")
PUBLIC_IP = re.compile(r"(?<![\d.])(?:(?:[1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:[1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])(?![\d.])")


def is_documentation_ip(value: str) -> bool:
    return value.startswith("192.0.2.") or value.startswith("198.51.100.") or value.startswith("203.0.113.")


class SecurityTests(unittest.TestCase):
    def test_no_secret_patterns_or_personal_paths(self):
        for path in ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS or ".git" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for label, pattern in SECRET_PATTERNS.items():
                self.assertIsNone(pattern.search(text), f"{label}: {path}")
            self.assertIsNone(PERSONAL_PATH.search(text), f"personal path: {path}")

    def test_network_addresses_are_reserved_for_documentation(self):
        for path in [ROOT / "data" / "reference" / "DimAsset.csv"]:
            text = path.read_text(encoding="utf-8")
            for match in PUBLIC_IP.findall(text):
                self.assertTrue(is_documentation_ip(match), f"non-documentation IPv4 in {path}: {match}")

    def test_no_env_or_database_files_in_inventory(self):
        forbidden = []
        for path in ROOT.rglob("*"):
            if path.is_file() and (path.name == ".env" or path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}):
                forbidden.append(str(path.relative_to(ROOT)))
        self.assertEqual(forbidden, [])

    def test_synthetic_classification_present(self):
        manifest = (ROOT / "data" / "dataset_manifest.json").read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC_DEMO_DATA", manifest)


if __name__ == "__main__":
    unittest.main()

