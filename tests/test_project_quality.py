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

EXPECTED_FRIENDLY_COLUMN_LABELS = {
    "Year": "Ano",
    "YearMonth": "Ano/mês",
    "Team": "Equipe",
    "SeverityPT": "Severidade",
    "StatusPT": "Status",
    "BusinessUnit": "Unidade de negócio",
    "TacticNamePT": "Tática",
    "TechniqueId": "ID da técnica",
    "TechniqueName": "Técnica",
    "RuleName": "Regra",
    "RuleFamily": "Família da regra",
    "SourceProduct": "Produto-fonte",
    "SourceSystem": "Sistema-fonte",
    "DataClassification": "Classificação",
    "AnalystLabel": "Analista",
    "ExperienceBand": "Experiência",
    "AssetLabel": "Ativo",
    "AssetType": "Tipo de ativo",
    "Criticality": "Criticidade",
    "Environment": "Ambiente",
    "Stage": "Etapa",
    "StageAtUTC": "Data/hora UTC",
    "MinutesFromPreviousStage": "Minutos desde etapa anterior",
    "SafeAction": "Ação sintética",
    "IncidentId": "Incidente",
    "RiskScore": "Risco",
    "source_product": "Produto-fonte",
    "QualityIssue": "Motivo da rejeição",
    "data_classification": "Classificação",
}


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

    def test_visual_finishing_contracts(self):
        pages = (
            ROOT
            / "powerbi"
            / "EDY SOC Analytics.Report"
            / "definition"
            / "pages"
        )

        technical_aliases = []
        for visual_path in sorted(pages.glob("*/visuals/*/visual.json")):
            payload = read_json(visual_path)
            query_state = payload.get("visual", {}).get("query", {}).get("queryState", {})
            for bucket in query_state.values():
                for projection in bucket.get("projections", []):
                    column_field = projection.get("field", {}).get("Column", {})
                    property_name = column_field.get("Property")
                    if property_name and projection.get("displayName") == property_name:
                        technical_aliases.append(
                            f"{visual_path.relative_to(ROOT)} -> {property_name}"
                        )
        self.assertEqual(technical_aliases, [])

        for visual_path in sorted(pages.glob("*/visuals/*/visual.json")):
            payload = read_json(visual_path)
            visual = payload.get("visual", {})
            if visual.get("visualType") != "slicer":
                continue
            header_show = visual["objects"]["header"][0]["properties"]["show"]
            self.assertEqual(
                header_show["expr"]["Literal"]["Value"],
                "false",
                str(visual_path.relative_to(ROOT)),
            )

        quality_refresh = read_json(
            pages
            / "DataQuality"
            / "visuals"
            / "e28667afd71f5261b652"
            / "visual.json"
        )
        value_size = quality_refresh["visual"]["objects"]["value"][0]["properties"]["fontSize"]
        self.assertEqual(value_size["expr"]["Literal"]["Value"], "12D")

        rejection_table = read_json(
            pages
            / "DataQuality"
            / "visuals"
            / "8482f4be411957b99c19"
            / "visual.json"
        )
        rejection_title = rejection_table["visual"]["visualContainerObjects"]["title"][0]
        title_value = rejection_title["properties"]["text"]["expr"]["Literal"]["Value"]
        self.assertEqual(
            title_value,
            "'Registros rejeitados — nenhum no período selecionado'",
        )

        methodology_colors = {
            "e7e5d36693ab56be9160": "#B8C6DA",
            "2c72cf03734e50968672": "#F1F5FA",
            "47be0e0c85ed543d9254": "#F1F5FA",
            "8de983b2fd82555e9ce7": "#F1F5FA",
            "97ecd27dbd74543ea6d3": "#F1F5FA",
            "b4598a123b645edb90bc": "#F1F5FA",
            "b8f77960180256659146": "#F1F5FA",
        }
        for visual_id, expected_color in methodology_colors.items():
            payload = read_json(
                pages / "Methodology" / "visuals" / visual_id / "visual.json"
            )
            text_style = payload["visual"]["objects"]["general"][0]["properties"][
                "paragraphs"
            ][0]["textRuns"][0]["textStyle"]
            self.assertEqual(text_style["color"], expected_color)

    def test_table_headers_use_friendly_portuguese_display_names(self):
        pages = (
            ROOT
            / "powerbi"
            / "EDY SOC Analytics.Report"
            / "definition"
            / "pages"
        )
        checked = 0
        for visual_path in sorted(pages.glob("*/visuals/*/visual.json")):
            payload = read_json(visual_path)
            visual = payload.get("visual", {})
            if visual.get("visualType") != "tableEx":
                continue
            projections = visual["query"]["queryState"]["Values"]["projections"]
            for projection in projections:
                column_field = projection.get("field", {}).get("Column", {})
                property_name = column_field.get("Property")
                if not property_name:
                    continue
                checked += 1
                self.assertIn(property_name, EXPECTED_FRIENDLY_COLUMN_LABELS)
                self.assertEqual(
                    projection.get("displayName"),
                    EXPECTED_FRIENDLY_COLUMN_LABELS[property_name],
                    f"{visual_path.relative_to(ROOT)} -> {property_name}",
                )
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
