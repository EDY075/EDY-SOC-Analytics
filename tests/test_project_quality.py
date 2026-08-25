import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from validation.project_inventory import (  # noqa: E402
    EXPECTED_INVENTORY,
    collect_inventory,
    read_json,
    validate_project,
)


MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class ProjectQualityTests(unittest.TestCase):
    def test_public_pbir_tmdl_inventory(self):
        self.assertEqual(collect_inventory(), EXPECTED_INVENTORY)

    def test_pbir_json_alt_text_and_tab_order(self):
        self.assertEqual(validate_project(), [])

    def test_all_local_markdown_links_resolve(self):
        failures = []
        for markdown in sorted(ROOT.rglob("*.md")):
            if any(part in {".git", "archive"} for part in markdown.parts):
                continue
            text = markdown.read_text(encoding="utf-8")
            for match in MARKDOWN_LINK.finditer(text):
                raw_target = match.group(1).strip().strip("<>")
                if raw_target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                local_target = unquote(raw_target.split("#", 1)[0])
                if not local_target:
                    continue
                resolved = (markdown.parent / local_target).resolve()
                try:
                    resolved.relative_to(ROOT)
                except ValueError:
                    failures.append(
                        f"{markdown.relative_to(ROOT)} -> path escapes repository: {raw_target}"
                    )
                    continue
                if not resolved.exists():
                    failures.append(
                        f"{markdown.relative_to(ROOT)} -> {raw_target}"
                    )
        self.assertEqual(failures, [], "broken local Markdown links")

    def test_page_metadata_names_existing_directories(self):
        pages_root = (
            ROOT
            / "powerbi"
            / "EDY SOC Analytics.Report"
            / "definition"
            / "pages"
        )
        metadata = read_json(pages_root / "pages.json")
        declared = metadata["pageOrder"]
        existing = sorted(path.name for path in pages_root.iterdir() if path.is_dir())
        self.assertEqual(sorted(declared), existing)


if __name__ == "__main__":
    unittest.main()
