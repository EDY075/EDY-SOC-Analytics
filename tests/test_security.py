import csv
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_EXTENSIONS = {
    ".gitattributes", ".gitignore", ".json", ".m", ".md", ".pbip", ".pbir",
    ".pbism", ".ps1", ".py", ".svg", ".tmdl", ".toml", ".txt", ".xml",
    ".yaml", ".yml", ".csv",
}
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "github token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "aws key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "google api key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "jwt": re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    "slack token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
    "twilio account sid": re.compile(r"AC[a-fA-F0-9]{32}"),
    "generic secret assignment": re.compile(r"(?i)(?:password|auth[_-]?token|client[_-]?secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}
PERSONAL_PATH = re.compile(r"(?i)C:\\Users\\(?!Public(?:\\|$))[^\\\s]+")
UNIX_PERSONAL_PATH = re.compile(r"(?i)(?:/Users|/home)/[A-Za-z0-9._-]+")
PUBLIC_IP = re.compile(r"(?<![\d.])(?:(?:[1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:[1-9]|[1-9]\d|1\d\d|2[0-4]\d|25[0-5])(?![\d.])")
EMAIL = re.compile(r"(?i)\b[A-Z0-9._%+-]+@([A-Z0-9.-]+\.[A-Z]{2,}|example\.invalid)\b")


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]


def is_scannable_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name.lower() in TEXT_EXTENSIONS


def is_documentation_ip(value: str) -> bool:
    return value.startswith("192.0.2.") or value.startswith("198.51.100.") or value.startswith("203.0.113.")


class SecurityTests(unittest.TestCase):
    def test_no_secret_patterns_or_personal_paths(self):
        for path in tracked_paths():
            if not path.is_file() or not is_scannable_text(path):
                continue
            text = path.read_text(encoding="utf-8")
            for label, pattern in SECRET_PATTERNS.items():
                self.assertIsNone(pattern.search(text), f"{label}: {path}")
            self.assertIsNone(PERSONAL_PATH.search(text), f"personal path: {path}")
            self.assertIsNone(UNIX_PERSONAL_PATH.search(text), f"personal path: {path}")
            for match in EMAIL.finditer(text):
                self.assertIn(
                    match.group(1).lower(),
                    {"example.invalid", "users.noreply.github.com"},
                    f"non-synthetic email: {path}",
                )

    def test_network_addresses_are_reserved_for_documentation(self):
        for path in [ROOT / "data" / "reference" / "DimAsset.csv"]:
            text = path.read_text(encoding="utf-8")
            for match in PUBLIC_IP.findall(text):
                self.assertTrue(is_documentation_ip(match), f"non-documentation IPv4 in {path}: {match}")

    def test_no_env_or_database_files_in_inventory(self):
        forbidden = [
            str(path.relative_to(ROOT))
            for path in tracked_paths()
            if path.name == ".env"
            or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".secret", ".token"}
        ]
        self.assertEqual(forbidden, [])

    def test_synthetic_classification_present(self):
        manifest = (ROOT / "data" / "dataset_manifest.json").read_text(encoding="utf-8")
        self.assertIn("SYNTHETIC_DEMO_DATA", manifest)

    def test_security_access_is_synthetic_and_role_scoped(self):
        access_path = ROOT / "data" / "reference" / "SecurityAccess.csv"
        with access_path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertGreaterEqual(len(rows), 2)
        self.assertEqual(len({row["AccessKey"] for row in rows}), len(rows))
        self.assertEqual(len({row["UPN"].lower() for row in rows}), len(rows))
        self.assertTrue(all(row["UPN"].lower().endswith("@example.invalid") for row in rows))
        self.assertTrue(all(row["IsSynthetic"].lower() == "true" for row in rows))
        self.assertEqual({row["RoleName"] for row in rows}, {"SOC_Analyst", "SOC_Manager"})

        analysts = [row for row in rows if row["RoleName"] == "SOC_Analyst"]
        managers = [row for row in rows if row["RoleName"] == "SOC_Manager"]
        self.assertEqual(len(managers), 1)
        self.assertEqual(len({row["Team"] for row in analysts}), len(analysts))
        self.assertTrue(all(row["Team"] != "ALL" for row in analysts))
        self.assertTrue(all(row["Team"] == "ALL" for row in managers))

        analysts_path = ROOT / "data" / "reference" / "DimAnalyst.csv"
        with analysts_path.open(encoding="utf-8", newline="") as handle:
            valid_teams = {row["Team"] for row in csv.DictReader(handle)}
        self.assertTrue({row["Team"] for row in analysts}.issubset(valid_teams))

        roles_root = (
            ROOT / "powerbi" / "EDY SOC Analytics.SemanticModel" / "definition" / "roles"
        )
        analyst_role = (roles_root / "SOC_Analyst.tmdl").read_text(encoding="utf-8")
        manager_role = (roles_root / "SOC_Manager.tmdl").read_text(encoding="utf-8")
        self.assertEqual(
            {path.stem for path in roles_root.glob("*.tmdl")},
            {"SOC_Analyst", "SOC_Manager"},
        )
        self.assertIn("USERPRINCIPALNAME ()", analyst_role)
        self.assertIn("LOWER ( SecurityAccess[UPN] )", analyst_role)
        self.assertIn("tablePermission DimAnalyst", analyst_role)
        self.assertNotIn("tablePermission", manager_role)


if __name__ == "__main__":
    unittest.main()
