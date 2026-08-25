"""Minimal, dependency-free validator for the EDY SIEM demonstration contract."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _is_datetime(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate_export(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    top_allowed = {"schemaVersion", "exportId", "generatedAt", "sourceProduct", "dataClassification", "records"}
    required = {"schemaVersion", "exportId", "generatedAt", "sourceProduct", "records"}
    record_allowed = {
        "recordId", "recordType", "occurredAt", "severity", "status", "sourceProduct",
        "sourceSystem", "assetId", "ruleId", "mitreTechniqueIds", "isFalsePositive", "safeSummary"
    }
    record_required = {"recordId", "recordType", "occurredAt", "severity", "status", "sourceProduct", "sourceSystem", "assetId", "ruleId"}

    if not isinstance(payload, dict):
        return ["payload must be an object"]
    errors.extend(f"missing field: {key}" for key in sorted(required - payload.keys()))
    errors.extend(f"unexpected field: {key}" for key in sorted(payload.keys() - top_allowed))
    if payload.get("schemaVersion") != "1.0.0": errors.append("schemaVersion must be 1.0.0")
    if not re.fullmatch(r"EXP-[0-9]{8}-[A-Z0-9]{6}", str(payload.get("exportId", ""))): errors.append("invalid exportId")
    if not _is_datetime(payload.get("generatedAt")): errors.append("invalid generatedAt")
    if payload.get("sourceProduct") != "EDY SIEM": errors.append("sourceProduct must be EDY SIEM")
    if "dataClassification" in payload and payload["dataClassification"] != "SYNTHETIC_DEMO_DATA": errors.append("invalid dataClassification")

    records = payload.get("records")
    if not isinstance(records, list) or not records:
        errors.append("records must be a non-empty array")
        return errors
    severities = {"Informational", "Low", "Medium", "High", "Critical"}
    statuses = {"New", "Active", "Contained", "Resolved", "Closed"}
    products = {"EDY Shield", "EDY Sentinel", "EDY SIEM", "EDY RECON", "External Synthetic"}
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{prefix} must be an object")
            continue
        errors.extend(f"{prefix} missing field: {key}" for key in sorted(record_required - record.keys()))
        errors.extend(f"{prefix} unexpected field: {key}" for key in sorted(record.keys() - record_allowed))
        if not re.fullmatch(r"(?:EVT|ALT|INC)-[0-9]{8}", str(record.get("recordId", ""))): errors.append(f"{prefix} invalid recordId")
        if record.get("recordType") not in {"Event", "Alert", "Incident"}: errors.append(f"{prefix} invalid recordType")
        if not _is_datetime(record.get("occurredAt")): errors.append(f"{prefix} invalid occurredAt")
        if record.get("severity") not in severities: errors.append(f"{prefix} invalid severity")
        if record.get("status") not in statuses: errors.append(f"{prefix} invalid status")
        if record.get("sourceProduct") not in products: errors.append(f"{prefix} invalid sourceProduct")
        if not isinstance(record.get("sourceSystem"), str) or not 2 <= len(record.get("sourceSystem", "")) <= 80: errors.append(f"{prefix} invalid sourceSystem")
        if not re.fullmatch(r"AST-[0-9]{4}", str(record.get("assetId", ""))): errors.append(f"{prefix} invalid assetId")
        if not re.fullmatch(r"RUL-[0-9]{3}", str(record.get("ruleId", ""))): errors.append(f"{prefix} invalid ruleId")
        techniques = record.get("mitreTechniqueIds", [])
        if not isinstance(techniques, list) or len(techniques) != len(set(techniques)) or any(not re.fullmatch(r"T[0-9]{4}(?:\.[0-9]{3})?", str(t)) for t in techniques): errors.append(f"{prefix} invalid mitreTechniqueIds")
        if "isFalsePositive" in record and not isinstance(record["isFalsePositive"], bool): errors.append(f"{prefix} invalid isFalsePositive")
        summary = record.get("safeSummary", "")
        if not isinstance(summary, str) or len(summary) > 240 or "<" in summary or ">" in summary: errors.append(f"{prefix} invalid safeSummary")
    return errors


def validate_file(path: Path) -> list[str]:
    return validate_export(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    issues = validate_file(args.path)
    if issues:
        raise SystemExit("\n".join(issues))
    print("Contract valid")

