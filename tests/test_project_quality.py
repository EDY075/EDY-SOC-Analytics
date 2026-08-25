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

    def test_csv_connector_uses_one_folder_privacy_boundary(self):
        function_source = (
            ROOT / "powerbi" / "power-query" / "Functions.m"
        ).read_text(encoding="utf-8")
        generated_source = (
            ROOT
            / "powerbi"
            / "EDY SOC Analytics.SemanticModel"
            / "definition"
            / "expressions.tmdl"
        ).read_text(encoding="utf-8")

        for source in (function_source, generated_source):
            self.assertIn("Folder.Files", source)
            self.assertNotIn("File.Contents", source)
            self.assertIn("Table.RowCount(Matches) = 1", source)

    def test_report_interaction_contracts(self):
        definition = (
            ROOT / "powerbi" / "EDY SOC Analytics.Report" / "definition"
        )
        actions = []
        for visual_path in sorted((definition / "pages").glob("*/visuals/*/visual.json")):
            payload = read_json(visual_path)
            visual = payload.get("visual", {})
            if visual.get("visualType") != "actionButton":
                continue
            link = visual["visualContainerObjects"]["visualLink"][0]["properties"]

            def literal(name):
                value = link.get(name, {}).get("expr", {}).get("Literal", {}).get("Value")
                return value.strip("'") if isinstance(value, str) else None

            actions.append((literal("type"), literal("navigationSection"), literal("bookmark")))

        self.assertEqual(
            [action[0] for action in actions].count("ClearAllSlicers"),
            6,
        )
        self.assertIn(("Bookmark", None, "f145a352ab22f855cfd6"), actions)
        self.assertIn(("PageNavigation", "Methodology", None), actions)
        self.assertIn(("PageNavigation", "CommandCenter", None), actions)

        bookmark = definition / "bookmarks" / "f145a352ab22f855cfd6.bookmark.json"
        self.assertTrue(bookmark.is_file())

        drillthrough = read_json(
            definition / "pages" / "IncidentDrillthrough" / "page.json"
        )
        self.assertEqual(drillthrough["pageBinding"]["type"], "Drillthrough")
        filters = drillthrough["filterConfig"]["filters"]
        self.assertEqual(len(filters), 1)
        self.assertEqual(filters[0]["howCreated"], "Drillthrough")
        field = filters[0]["field"]["Column"]
        self.assertEqual(field["Expression"]["SourceRef"]["Entity"], "FactIncidents")
        self.assertEqual(field["Property"], "IncidentId")


if __name__ == "__main__":
    unittest.main()
