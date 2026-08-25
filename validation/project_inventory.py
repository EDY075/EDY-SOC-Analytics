"""Validate the public PBIR/TMDL inventory without requiring Power BI Desktop."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPORT_DEFINITION = ROOT / "powerbi" / "EDY SOC Analytics.Report" / "definition"
MODEL_DEFINITION = ROOT / "powerbi" / "EDY SOC Analytics.SemanticModel" / "definition"

EXPECTED_INVENTORY = {
    "pages": 10,
    "visuals": 101,
    "mobileStates": 91,
    "tables": 21,
    "measures": 41,
    "roles": 2,
}

EXPECTED_SORT_BY = {
    "DimDate.tmdl": {"MonthName": "MonthNumber", "WeekdayName": "WeekdayNumber"},
    "DimTime.tmdl": {"HourLabel": "Hour"},
    "DimSeverity.tmdl": {"Severity": "SeverityOrder", "SeverityPT": "SeverityOrder"},
    "DimStatus.tmdl": {"Status": "StatusOrder", "StatusPT": "StatusOrder"},
    "FactIncidentLifecycle.tmdl": {"Stage": "StageOrder"},
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def literal_text(value: Any) -> str:
    """Return the text stored in a PBIR Literal expression."""
    if not isinstance(value, str):
        return ""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        value = value[1:-1].replace("''", "'")
    return value.strip()


def visual_alt_text(payload: dict[str, Any]) -> str:
    general = (
        payload.get("visual", {})
        .get("visualContainerObjects", {})
        .get("general", [])
    )
    for entry in general:
        value = (
            entry.get("properties", {})
            .get("altText", {})
            .get("expr", {})
            .get("Literal", {})
            .get("Value")
        )
        text = literal_text(value)
        if text:
            return text
    return ""


def tmdl_name(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def collect_inventory(root: Path = ROOT) -> dict[str, int]:
    report_definition = root / "powerbi" / "EDY SOC Analytics.Report" / "definition"
    model_definition = root / "powerbi" / "EDY SOC Analytics.SemanticModel" / "definition"
    pages_metadata = read_json(report_definition / "pages" / "pages.json")
    measure_text = (
        model_definition / "tables" / "_Measures.tmdl"
    ).read_text(encoding="utf-8")

    return {
        "pages": len(pages_metadata.get("pageOrder", [])),
        "visuals": len(list((report_definition / "pages").rglob("visual.json"))),
        "mobileStates": len(list((report_definition / "pages").rglob("mobile.json"))),
        "tables": len(list((model_definition / "tables").glob("*.tmdl"))),
        "measures": len(re.findall(r"^\s*measure\s+", measure_text, flags=re.MULTILINE)),
        "roles": len(list((model_definition / "roles").glob("*.tmdl"))),
    }


def validate_project(root: Path = ROOT) -> list[str]:
    issues: list[str] = []
    report_definition = root / "powerbi" / "EDY SOC Analytics.Report" / "definition"
    pages_root = report_definition / "pages"

    inventory = collect_inventory(root)
    for key, expected in EXPECTED_INVENTORY.items():
        actual = inventory[key]
        if actual != expected:
            issues.append(f"inventory {key}: expected {expected}, got {actual}")

    pages_metadata = read_json(pages_root / "pages.json")
    page_order = pages_metadata.get("pageOrder", [])
    if len(page_order) != len(set(page_order)):
        issues.append("pages.json contains duplicate page names")

    page_directories = {path.name for path in pages_root.iterdir() if path.is_dir()}
    missing_pages = sorted(set(page_order) - page_directories)
    unexpected_pages = sorted(page_directories - set(page_order))
    if missing_pages:
        issues.append(f"page directories missing: {', '.join(missing_pages)}")
    if unexpected_pages:
        issues.append(f"page directories not declared in pageOrder: {', '.join(unexpected_pages)}")

    for page_name in page_order:
        visual_files = sorted((pages_root / page_name / "visuals").glob("*/visual.json"))
        tab_orders: list[int] = []
        for visual_path in visual_files:
            try:
                payload = read_json(visual_path)
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                issues.append(f"invalid visual JSON {visual_path.relative_to(root)}: {error}")
                continue

            if not visual_alt_text(payload):
                issues.append(f"missing altText: {visual_path.relative_to(root)}")

            tab_order = payload.get("position", {}).get("tabOrder")
            if not isinstance(tab_order, int) or isinstance(tab_order, bool) or tab_order < 0:
                issues.append(f"invalid tabOrder: {visual_path.relative_to(root)}")
            else:
                tab_orders.append(tab_order)

        duplicate_orders = sorted(
            order for order, count in Counter(tab_orders).items() if count > 1
        )
        if duplicate_orders:
            issues.append(
                f"duplicate tabOrder on page {page_name}: "
                + ", ".join(str(order) for order in duplicate_orders)
            )

    for path in sorted(report_definition.rglob("*.json")):
        try:
            read_json(path)
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            issues.append(f"invalid PBIR JSON {path.relative_to(root)}: {error}")

    tables_root = root / "powerbi" / "EDY SOC Analytics.SemanticModel" / "definition" / "tables"
    column_block = re.compile(
        r"^\tcolumn\s+(?P<name>[^\r\n]+)\r?\n(?P<body>.*?)(?=^\t(?:column|measure|partition|hierarchy|annotation)\s|\Z)",
        flags=re.MULTILINE | re.DOTALL,
    )
    for filename, expected_pairs in EXPECTED_SORT_BY.items():
        path = tables_root / filename
        text = path.read_text(encoding="utf-8")
        blocks = {tmdl_name(match.group("name")): match.group("body") for match in column_block.finditer(text)}
        columns = set(blocks)
        for column, expected_target in expected_pairs.items():
            body = blocks.get(column)
            if body is None:
                issues.append(f"missing sort source column {filename}: {column}")
                continue
            target_match = re.search(r"^\t\tsortByColumn:\s*(.+?)\s*$", body, flags=re.MULTILINE)
            if target_match is None:
                issues.append(f"missing sortByColumn {filename}: {column}")
                continue
            actual_target = tmdl_name(target_match.group(1))
            if actual_target != expected_target:
                issues.append(
                    f"sortByColumn {filename}: {column} expected {expected_target}, got {actual_target}"
                )
            if actual_target not in columns:
                issues.append(f"unknown sort target {filename}: {column} -> {actual_target}")
            if actual_target == column:
                issues.append(f"self-referencing sort target {filename}: {column}")

    return issues


def main() -> int:
    inventory = collect_inventory()
    issues = validate_project()
    result = {
        "status": "passed" if not issues else "failed",
        "inventory": inventory,
        "expected": EXPECTED_INVENTORY,
        "issues": issues,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
