"""Generate a deterministic, entirely synthetic SOC analytics dataset.

The raw layer intentionally contains a small, controlled number of duplicate rows,
nulls and label variants. The expected layer is the independent test oracle for the
Power Query implementation; it is not intended to replace transformations in M.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REFERENCE = ROOT / "data" / "reference"
EXPECTED = ROOT / "data" / "expected"
CONFIG_PATH = Path(__file__).with_name("config.json")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> int:
    materialized = list(rows)
    if not materialized and not fieldnames:
        raise ValueError(f"fieldnames required for empty file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    names = fieldnames or list(materialized[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, extrasaction="raise")
        writer.writeheader()
        writer.writerows(materialized)
    return len(materialized)


def iso(value: datetime | None) -> str:
    return "" if value is None else value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def date_key(value: datetime) -> int:
    return int(value.astimezone(timezone.utc).strftime("%Y%m%d"))


def time_key(value: datetime) -> int:
    return int(value.astimezone(timezone.utc).strftime("%H%M"))


def choose_weighted(rng: random.Random, values: list[Any], weights: list[float]) -> Any:
    return rng.choices(values, weights=weights, k=1)[0]


def build_reference(config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    severities = [
        {"SeverityKey": 1, "Severity": "Informational", "SeverityPT": "Informativo", "SeverityOrder": 1, "RiskWeight": 0.5, "ColorHex": "#6B7A90"},
        {"SeverityKey": 2, "Severity": "Low", "SeverityPT": "Baixo", "SeverityOrder": 2, "RiskWeight": 1.0, "ColorHex": "#3AA0D8"},
        {"SeverityKey": 3, "Severity": "Medium", "SeverityPT": "Médio", "SeverityOrder": 3, "RiskWeight": 2.0, "ColorHex": "#F2B84B"},
        {"SeverityKey": 4, "Severity": "High", "SeverityPT": "Alto", "SeverityOrder": 4, "RiskWeight": 3.5, "ColorHex": "#F27C4A"},
        {"SeverityKey": 5, "Severity": "Critical", "SeverityPT": "Crítico", "SeverityOrder": 5, "RiskWeight": 5.0, "ColorHex": "#E5484D"},
    ]
    statuses = [
        {"StatusKey": 1, "Status": "New", "StatusPT": "Novo", "StatusOrder": 1, "IsOpen": True},
        {"StatusKey": 2, "Status": "Active", "StatusPT": "Ativo", "StatusOrder": 2, "IsOpen": True},
        {"StatusKey": 3, "Status": "Contained", "StatusPT": "Contido", "StatusOrder": 3, "IsOpen": True},
        {"StatusKey": 4, "Status": "Resolved", "StatusPT": "Resolvido", "StatusOrder": 4, "IsOpen": False},
        {"StatusKey": 5, "Status": "Closed", "StatusPT": "Fechado", "StatusOrder": 5, "IsOpen": False},
    ]
    source_specs = [
        (1, "EDY Shield", "Endpoint Integrity", 0.78, 1.05),
        (2, "EDY Sentinel", "Cloud Detection", 0.86, 0.85),
        (3, "EDY SIEM", "Correlation Hub", 0.91, 1.00),
        (4, "EDY RECON", "Exposure Intelligence", 0.72, 0.55),
        (5, "External Synthetic", "Identity Provider", 0.82, 0.75),
        (6, "External Synthetic", "Network Sensor", 0.68, 1.35),
        (7, "External Synthetic", "Cloud Audit", 0.88, 0.90),
    ]
    sources = [
        {"SourceProductKey": key, "SourceProduct": product, "SourceSystem": system, "ExpectedFidelity": fidelity, "VolumeFactor": volume, "DataClassification": config["dataset_label"]}
        for key, product, system, fidelity, volume in source_specs
    ]
    asset_types = ["Servidor", "Endpoint", "Identidade", "Aplicação", "Nuvem", "Dispositivo de rede"]
    business_units = ["Operações", "Financeiro", "Tecnologia", "Atendimento", "Pesquisa", "Corporativo"]
    environments = ["Produção", "Homologação", "Desenvolvimento"]
    assets: list[dict[str, Any]] = [{
        "AssetKey": 0,
        "AssetId": "UNKNOWN",
        "AssetLabel": "Ativo não informado",
        "AssetType": "Desconhecido",
        "BusinessUnit": "Não informado",
        "Environment": "Não informado",
        "Criticality": 1,
        "NetworkAddress": "",
        "IsSynthetic": True,
    }]
    for index in range(1, 241):
        kind = asset_types[(index - 1) % len(asset_types)]
        criticality = [1, 2, 2, 3, 3, 3, 4, 4, 5][(index * 7) % 9]
        network = ["192.0.2", "198.51.100", "203.0.113"][(index - 1) % 3]
        assets.append({
            "AssetKey": index,
            "AssetId": f"AST-{index:04d}",
            "AssetLabel": f"Ativo sintético {index:03d}",
            "AssetType": kind,
            "BusinessUnit": business_units[(index * 5) % len(business_units)],
            "Environment": environments[(index * 11) % len(environments)],
            "Criticality": criticality,
            "NetworkAddress": f"{network}.{(index % 254) + 1}",
            "IsSynthetic": True,
        })
    tactics = [
        (1, "TA0043", "Reconnaissance", "Reconhecimento"),
        (2, "TA0001", "Initial Access", "Acesso inicial"),
        (3, "TA0002", "Execution", "Execução"),
        (4, "TA0003", "Persistence", "Persistência"),
        (5, "TA0004", "Privilege Escalation", "Escalonamento de privilégio"),
        (6, "TA0005", "Defense Evasion", "Evasão de defesa"),
        (7, "TA0006", "Credential Access", "Acesso a credenciais"),
        (8, "TA0007", "Discovery", "Descoberta"),
        (9, "TA0008", "Lateral Movement", "Movimento lateral"),
        (10, "TA0009", "Collection", "Coleta"),
        (11, "TA0011", "Command and Control", "Comando e controle"),
        (12, "TA0010", "Exfiltration", "Exfiltração"),
        (13, "TA0040", "Impact", "Impacto"),
    ]
    tactic_rows = [{"AttackTacticKey": k, "TacticId": tid, "TacticName": en, "TacticNamePT": pt, "Framework": "MITRE ATT&CK", "Domain": "Enterprise", "AttackVersion": "19.1", "RetrievedAt": "2026-08-24"} for k, tid, en, pt in tactics]
    technique_specs = [
        ("T1595", "Active Scanning", 1), ("T1190", "Exploit Public-Facing Application", 2),
        ("T1566.002", "Spearphishing Link", 2), ("T1078", "Valid Accounts", 2),
        ("T1059.001", "PowerShell", 3), ("T1204.002", "Malicious File", 3),
        ("T1053.005", "Scheduled Task", 4), ("T1547.001", "Registry Run Keys", 4),
        ("T1068", "Exploitation for Privilege Escalation", 5), ("T1548.002", "Bypass User Account Control", 5),
        ("T1027", "Obfuscated Files or Information", 6), ("T1562.001", "Impair Defenses", 6),
        ("T1003.001", "LSASS Memory", 7), ("T1110.003", "Password Spraying", 7),
        ("T1087.002", "Domain Account Discovery", 8), ("T1046", "Network Service Discovery", 8),
        ("T1021.001", "Remote Desktop Protocol", 9), ("T1570", "Lateral Tool Transfer", 9),
        ("T1114", "Email Collection", 10), ("T1005", "Data from Local System", 10),
        ("T1071.001", "Web Protocols", 11), ("T1105", "Ingress Tool Transfer", 11),
        ("T1041", "Exfiltration Over C2 Channel", 12), ("T1567.002", "Exfiltration to Cloud Storage", 12),
        ("T1486", "Data Encrypted for Impact", 13), ("T1490", "Inhibit System Recovery", 13),
    ]
    techniques = [{"AttackTechniqueKey": i, "TechniqueId": tid, "TechniqueName": name, "AttackTacticKey": tactic, "Framework": "MITRE ATT&CK", "Domain": "Enterprise", "AttackVersion": "19.1", "RetrievedAt": "2026-08-24", "IsDeprecated": False} for i, (tid, name, tactic) in enumerate(technique_specs, 1)]
    analysts = [{
        "AnalystKey": 0,
        "AnalystId": "UNKNOWN",
        "AnalystLabel": "Não atribuído",
        "Team": "Unassigned",
        "Region": "Não informado",
        "ExperienceBand": "Não informado",
        "IsSynthetic": True,
    }]
    for index in range(1, 19):
        analysts.append({"AnalystKey": index, "AnalystId": f"ANL-{index:03d}", "AnalystLabel": f"Analista sintético {index:02d}", "Team": ["Blue-A", "Blue-B", "Blue-C"][(index - 1) % 3], "Region": ["Sul", "Sudeste", "Centro"][(index - 1) % 3], "ExperienceBand": ["Júnior", "Pleno", "Sênior"][(index * 2) % 3], "IsSynthetic": True})
    classifications = [
        {"ClassificationKey": 0, "Classification": "Not applicable", "ClassificationPT": "Não aplicável", "IsFalsePositive": False},
        {"ClassificationKey": 1, "Classification": "True positive", "ClassificationPT": "Verdadeiro positivo", "IsFalsePositive": False},
        {"ClassificationKey": 2, "Classification": "Benign positive", "ClassificationPT": "Positivo benigno", "IsFalsePositive": True},
        {"ClassificationKey": 3, "Classification": "False positive", "ClassificationPT": "Falso positivo", "IsFalsePositive": True},
        {"ClassificationKey": 4, "Classification": "Undetermined", "ClassificationPT": "Indeterminado", "IsFalsePositive": False},
    ]
    security_access = [
        {"AccessKey": 1, "UPN": "analyst.blue-a@example.invalid", "Team": "Blue-A", "RoleName": "SOC_Analyst", "IsSynthetic": True},
        {"AccessKey": 2, "UPN": "analyst.blue-b@example.invalid", "Team": "Blue-B", "RoleName": "SOC_Analyst", "IsSynthetic": True},
        {"AccessKey": 3, "UPN": "analyst.blue-c@example.invalid", "Team": "Blue-C", "RoleName": "SOC_Analyst", "IsSynthetic": True},
        {"AccessKey": 4, "UPN": "manager.soc@example.invalid", "Team": "ALL", "RoleName": "SOC_Manager", "IsSynthetic": True},
    ]
    sla = [
        {"SLAKey": 1, "SeverityKey": 1, "AcknowledgeMinutes": 240, "ContainMinutes": 1440, "ResolveMinutes": 4320},
        {"SLAKey": 2, "SeverityKey": 2, "AcknowledgeMinutes": 120, "ContainMinutes": 720, "ResolveMinutes": 2880},
        {"SLAKey": 3, "SeverityKey": 3, "AcknowledgeMinutes": 60, "ContainMinutes": 360, "ResolveMinutes": 1440},
        {"SLAKey": 4, "SeverityKey": 4, "AcknowledgeMinutes": 30, "ContainMinutes": 180, "ResolveMinutes": 720},
        {"SLAKey": 5, "SeverityKey": 5, "AcknowledgeMinutes": 15, "ContainMinutes": 60, "ResolveMinutes": 240},
    ]
    rules = []
    for index in range(1, 46):
        technique = techniques[(index * 7) % len(techniques)]
        base_fidelity = 0.34 + ((index * 17) % 60) / 100
        if index in {4, 11, 23, 37}:
            base_fidelity = 0.24
        rules.append({
            "DetectionRuleKey": index,
            "RuleId": f"RUL-{index:03d}",
            "RuleName": f"Regra analítica sintética {index:02d}",
            "RuleFamily": ["Identidade", "Endpoint", "Rede", "Nuvem", "Correlação"][(index - 1) % 5],
            "DefaultSeverityKey": 1 + ((index * 3) % 5),
            "AttackTechniqueKey": technique["AttackTechniqueKey"],
            "ExpectedFidelity": round(base_fidelity, 2),
            "NoiseFactor": round(1.8 if index in {4, 11, 23, 37} else 0.65 + ((index * 13) % 80) / 100, 2),
            "IsEnabled": index not in {15, 30},
        })
    return {
        "DimSeverity": severities, "DimStatus": statuses, "DimSourceProduct": sources,
        "DimAsset": assets, "DimAttackTactic": tactic_rows, "DimAttackTechnique": techniques,
        "DimAnalyst": analysts, "DimClassification": classifications, "DimSLA": sla,
        "DimDetectionRule": rules, "SecurityAccess": security_access,
    }


def build_dates(start: datetime, end: datetime) -> tuple[list[dict[str, Any]], list[datetime]]:
    rows: list[dict[str, Any]] = []
    values: list[datetime] = []
    cursor = start.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    last = end.astimezone(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    month_names = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    weekday_names = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
    while cursor < last:
        values.append(cursor)
        rows.append({
            "DateKey": int(cursor.strftime("%Y%m%d")), "Date": cursor.date().isoformat(),
            "Year": cursor.year, "Quarter": f"T{((cursor.month - 1) // 3) + 1}", "MonthNumber": cursor.month,
            "MonthName": month_names[cursor.month - 1], "YearMonth": cursor.strftime("%Y-%m"),
            "Day": cursor.day, "WeekdayNumber": cursor.isoweekday(), "WeekdayName": weekday_names[cursor.weekday()],
            "IsWeekend": cursor.weekday() >= 5,
        })
        cursor += timedelta(days=1)
    return rows, values


def build_times() -> list[dict[str, Any]]:
    return [{"TimeKey": hour * 100 + minute, "Hour": hour, "Minute": minute, "HourLabel": f"{hour:02d}:00", "Period": "Madrugada" if hour < 6 else "Manhã" if hour < 12 else "Tarde" if hour < 18 else "Noite"} for hour in range(24) for minute in range(0, 60, 5)]


def random_timestamp(rng: random.Random, days: list[datetime]) -> datetime:
    day_weights = []
    for day in days:
        weight = 0.78 if day.weekday() >= 5 else 1.0
        if day.month in {3, 6, 8}: weight *= 1.22
        if day.day in {5, 17, 26}: weight *= 1.30
        day_weights.append(weight)
    day = choose_weighted(rng, days, day_weights)
    hour = choose_weighted(rng, list(range(24)), [0.35,0.3,0.25,0.25,0.3,0.5,0.8,1.2,1.5,1.7,1.8,1.8,1.6,1.7,1.8,1.9,1.8,1.6,1.2,0.9,0.7,0.55,0.45,0.4])
    return day + timedelta(hours=hour, minutes=rng.randrange(60), seconds=rng.randrange(60))


def normalize_label(value: str, domain: str) -> str:
    if domain == "severity":
        mapping = {"info": "Informational", "informational": "Informational", "low": "Low", "baixo": "Low", "medium": "Medium", "medio": "Medium", "médio": "Medium", "high": "High", "alto": "High", "critical": "Critical", "critico": "Critical", "crítico": "Critical"}
    else:
        mapping = {"new": "New", "novo": "New", "active": "Active", "ativo": "Active", "contained": "Contained", "contido": "Contained", "resolved": "Resolved", "resolvido": "Resolved", "closed": "Closed", "fechado": "Closed"}
    return mapping[value.strip().lower()]


def generate() -> dict[str, Any]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    rng = random.Random(config["seed"])
    start = datetime.fromisoformat(config["period_start"])
    end = datetime.fromisoformat(config["period_end"])
    reference = build_reference(config)
    dim_date, days = build_dates(start, end)
    reference["DimDate"] = dim_date
    reference["DimTime"] = build_times()
    for table, rows in reference.items():
        write_csv(REFERENCE / f"{table}.csv", rows)

    sources = reference["DimSourceProduct"]
    rules = reference["DimDetectionRule"]
    assets = reference["DimAsset"]
    known_assets = [asset for asset in assets if asset["AssetKey"] != 0]
    asset_by_key = {asset["AssetKey"]: asset for asset in assets}
    severity_names = {row["SeverityKey"]: row["Severity"] for row in reference["DimSeverity"]}
    severity_keys = {value: key for key, value in severity_names.items()}
    raw_events: list[dict[str, Any]] = []
    clean_events: list[dict[str, Any]] = []
    event_index: dict[str, dict[str, Any]] = {}
    source_weights = [row["VolumeFactor"] for row in sources]
    severity_weights = [0.43, 0.30, 0.18, 0.075, 0.015]
    for index in range(1, config["event_count"] + 1):
        occurred = random_timestamp(rng, days)
        source = choose_weighted(rng, sources, source_weights)
        rule = choose_weighted(rng, rules, [r["NoiseFactor"] for r in rules])
        asset = choose_weighted(rng, known_assets, [0.6 + a["Criticality"] * 0.14 for a in known_assets])
        severity_key = choose_weighted(rng, [1,2,3,4,5], severity_weights)
        event_id = f"EVT-{index:08d}"
        received = occurred + timedelta(seconds=rng.randint(2, 420))
        asset_is_missing = index % 173 == 0
        clean = {
            "EventKey": index, "EventId": event_id, "EventTimestampUTC": iso(occurred), "ReceivedAtUTC": iso(received),
            "EventDateKey": date_key(occurred), "EventTimeKey": (occurred.hour * 100 + (occurred.minute // 5) * 5),
            "SourceProductKey": source["SourceProductKey"], "AssetKey": 0 if asset_is_missing else asset["AssetKey"], "DetectionRuleKey": rule["DetectionRuleKey"],
            "SeverityKey": severity_key, "EventCount": 1, "IngestionDelaySeconds": int((received - occurred).total_seconds()),
            "IsDuplicate": False, "IsRejected": False, "DataClassification": config["dataset_label"],
        }
        clean_events.append(clean)
        event_index[event_id] = clean
        severity_raw = severity_names[severity_key]
        if index % 97 == 0: severity_raw = {"Informational":"info","Low":"baixo","Medium":"medio","High":"alto","Critical":"critico"}[severity_raw]
        raw_events.append({
            "event_id": event_id, "event_timestamp": iso(occurred), "received_at": iso(received),
            "source_product": source["SourceProduct"], "source_system": source["SourceSystem"],
            "asset_id": "" if asset_is_missing else asset["AssetId"], "rule_id": rule["RuleId"],
            "severity": severity_raw, "event_category": rule["RuleFamily"], "safe_summary": "Evento sintético para validação de análise SOC.",
            "data_classification": config["dataset_label"],
        })
    duplicate_count = math.floor(config["event_count"] * config["raw_duplicate_rate"])
    for duplicate in raw_events[:duplicate_count]:
        raw_events.append(dict(duplicate))
    rng.shuffle(raw_events)

    raw_alerts: list[dict[str, Any]] = []
    clean_alerts: list[dict[str, Any]] = []
    alert_event_pool = [event for event in clean_events if event["AssetKey"] != 0]
    for index in range(1, config["alert_count"] + 1):
        event = alert_event_pool[(index * 7919) % len(alert_event_pool)]
        rule = rules[event["DetectionRuleKey"] - 1]
        source = sources[event["SourceProductKey"] - 1]
        asset = asset_by_key[event["AssetKey"]]
        event_time = datetime.fromisoformat(event["EventTimestampUTC"].replace("Z", "+00:00"))
        detected = event_time + timedelta(minutes=max(1, int(rng.lognormvariate(2.25, 0.72))))
        alert_id = f"ALT-{index:08d}"
        fidelity = rule["ExpectedFidelity"] * source["ExpectedFidelity"]
        is_fp = rng.random() > fidelity
        severity_key = min(5, max(1, event["SeverityKey"] + choose_weighted(rng, [-1,0,1], [0.12,0.72,0.16])))
        clean_alerts.append({
            "AlertKey": index, "AlertId": alert_id, "EventId": event["EventId"], "DetectedAtUTC": iso(detected),
            "AlertDateKey": date_key(detected), "AlertTimeKey": detected.hour * 100 + (detected.minute // 5) * 5,
            "SourceProductKey": event["SourceProductKey"], "AssetKey": event["AssetKey"], "DetectionRuleKey": event["DetectionRuleKey"],
            "SeverityKey": severity_key, "AlertCount": 1, "DetectionMinutes": round((detected - event_time).total_seconds()/60, 2),
            "IsFalsePositive": is_fp, "BecameIncident": False, "DataClassification": config["dataset_label"],
        })
        severity_raw = severity_names[severity_key]
        if index % 113 == 0: severity_raw = severity_raw.lower()
        raw_alerts.append({
            "alert_id": alert_id, "event_id": event["EventId"], "detected_at": iso(detected), "source_product": source["SourceProduct"],
            "asset_id": asset["AssetId"], "rule_id": rule["RuleId"], "severity": severity_raw,
            "false_positive": "TRUE" if is_fp else "FALSE", "safe_summary": "Alerta sintético sem conteúdo operacional.",
            "data_classification": config["dataset_label"],
        })

    lifecycle_rows: list[dict[str, Any]] = []
    incident_techniques: list[dict[str, Any]] = []
    raw_incidents: list[dict[str, Any]] = []
    clean_incidents: list[dict[str, Any]] = []
    sla_rows: list[dict[str, Any]] = []
    classification_weights = [0.0, 0.64, 0.12, 0.18, 0.06]
    latest_data_time = end.astimezone(timezone.utc)
    selected_alert_indexes = rng.sample(range(len(clean_alerts)), config["incident_count"])
    for index, alert_index in enumerate(selected_alert_indexes, 1):
        alert = clean_alerts[alert_index]
        alert["BecameIncident"] = True
        alert_time = datetime.fromisoformat(alert["DetectedAtUTC"].replace("Z", "+00:00"))
        severity_key = alert["SeverityKey"]
        created = alert_time + timedelta(minutes=rng.randint(1, 45))
        acknowledge = created + timedelta(minutes=max(1, int(rng.lognormvariate(2.5 + (5-severity_key)*0.18, 0.75))))
        triaged = acknowledge + timedelta(minutes=max(2, int(rng.lognormvariate(3.0, 0.7))))
        contained = triaged + timedelta(minutes=max(4, int(rng.lognormvariate(3.8 + (5-severity_key)*0.18, 0.8))))
        resolved = contained + timedelta(minutes=max(8, int(rng.lognormvariate(4.4 + (5-severity_key)*0.25, 0.85))))
        closed = resolved + timedelta(minutes=rng.randint(10, 720))
        age_days = (latest_data_time - created).total_seconds() / 86400
        close_probability = 0.94 if age_days > 45 else 0.82 if age_days > 14 else 0.57
        is_closed = rng.random() < close_probability
        if not is_closed:
            stage = choose_weighted(rng, ["New", "Active", "Contained"], [0.16,0.61,0.23])
            if stage == "New": acknowledge = triaged = contained = resolved = closed = None
            elif stage == "Active": contained = resolved = closed = None
            else: resolved = closed = None
            status = stage
            classification_key = 0
        else:
            status = choose_weighted(rng, ["Resolved", "Closed"], [0.14, 0.86])
            if status == "Resolved": closed = None
            classification_key = choose_weighted(rng, [1,2,3,4], classification_weights[1:])
        analyst_key = 1 + ((index * 11 + severity_key) % 18)
        analyst_is_missing = index % 199 == 0
        effective_analyst_key = 0 if analyst_is_missing else analyst_key
        sla = reference["DimSLA"][severity_key - 1]
        ack_minutes = None if acknowledge is None else round((acknowledge-created).total_seconds()/60, 2)
        contain_minutes = None if contained is None else round((contained-created).total_seconds()/60, 2)
        resolve_minutes = None if resolved is None else round((resolved-created).total_seconds()/60, 2)
        recovery_minutes = None if closed is None or resolved is None else round((closed-resolved).total_seconds()/60, 2)
        sla_ack_met = ack_minutes is not None and ack_minutes <= sla["AcknowledgeMinutes"]
        sla_contain_met = contain_minutes is not None and contain_minutes <= sla["ContainMinutes"]
        sla_resolve_met = resolve_minutes is not None and resolve_minutes <= sla["ResolveMinutes"]
        reopened = is_closed and index % 53 == 0
        escalated = severity_key >= 4 or index % 11 == 0
        incident_id = f"INC-{index:08d}"
        risk_score = min(100, round(severity_key * 15 + asset_by_key[alert["AssetKey"]]["Criticality"] * 6 + (12 if escalated else 0) + rng.random()*10, 1))
        clean_incidents.append({
            "IncidentKey": index, "IncidentId": incident_id, "CreatedAtUTC": iso(created), "AcknowledgedAtUTC": iso(acknowledge),
            "TriagedAtUTC": iso(triaged), "ContainedAtUTC": iso(contained), "ResolvedAtUTC": iso(resolved), "ClosedAtUTC": iso(closed),
            "CreatedDateKey": date_key(created), "CreatedTimeKey": created.hour*100+(created.minute//5)*5,
            "SourceProductKey": alert["SourceProductKey"], "AssetKey": alert["AssetKey"], "DetectionRuleKey": alert["DetectionRuleKey"],
            "SeverityKey": severity_key, "StatusKey": {"New":1,"Active":2,"Contained":3,"Resolved":4,"Closed":5}[status],
            "AnalystKey": effective_analyst_key, "ClassificationKey": classification_key, "SLAKey": severity_key,
            "AlertKey": alert["AlertKey"], "IncidentCount": 1, "RiskScore": risk_score,
            "AcknowledgementMinutes": ack_minutes or "", "TriageMinutes": "" if triaged is None else round((triaged-created).total_seconds()/60,2),
            "ContainmentMinutes": contain_minutes or "", "ResolutionMinutes": resolve_minutes or "", "RecoveryMinutes": recovery_minutes or "",
            "IsEscalated": escalated, "IsReopened": reopened, "IsFalsePositive": classification_key in {2,3},
            "SLAOverallMet": bool(sla_ack_met and (sla_contain_met if contained else False) and (sla_resolve_met if resolved else False)),
            "DataClassification": config["dataset_label"],
        })
        raw_status = status
        raw_severity = severity_names[severity_key]
        if index % 89 == 0: raw_status = {"New":"novo","Active":"ativo","Contained":"contido","Resolved":"resolvido","Closed":"fechado"}[status]
        if index % 107 == 0: raw_severity = raw_severity.upper()
        raw_incidents.append({
            "incident_id": incident_id, "alert_id": alert["AlertId"], "created_at": iso(created), "acknowledged_at": iso(acknowledge), "triaged_at": iso(triaged),
            "contained_at": iso(contained), "resolved_at": iso(resolved), "closed_at": iso(closed),
            "source_product": sources[alert["SourceProductKey"]-1]["SourceProduct"], "source_system": sources[alert["SourceProductKey"]-1]["SourceSystem"], "asset_id": asset_by_key[alert["AssetKey"]]["AssetId"],
            "rule_id": rules[alert["DetectionRuleKey"]-1]["RuleId"], "severity": raw_severity, "status": raw_status,
            "analyst_id": "" if analyst_is_missing else reference["DimAnalyst"][analyst_key]["AnalystId"], "classification_key": classification_key,
            "risk_score": risk_score, "is_escalated": str(escalated).upper(), "is_reopened": str(reopened).upper(),
            "data_classification": config["dataset_label"],
        })
        stages = [("Created", created), ("Acknowledged", acknowledge), ("Triaged", triaged), ("Contained", contained), ("Resolved", resolved), ("Closed", closed)]
        previous_time = None
        for order, (stage_name, stage_time) in enumerate(stages, 1):
            if stage_time is None: continue
            lifecycle_rows.append({
                "LifecycleKey": len(lifecycle_rows)+1, "IncidentKey": index, "Stage": stage_name, "StageOrder": order,
                "StageAtUTC": iso(stage_time), "StageDateKey": date_key(stage_time), "AnalystKey": effective_analyst_key,
                "MinutesFromPreviousStage": "" if previous_time is None else round((stage_time-previous_time).total_seconds()/60,2),
                "SafeAction": f"Transição sintética para {stage_name}.",
            })
            previous_time = stage_time
        rule = rules[alert["DetectionRuleKey"]-1]
        technique_keys = {rule["AttackTechniqueKey"]}
        if index % 4 == 0: technique_keys.add(1 + ((rule["AttackTechniqueKey"] + index) % len(reference["DimAttackTechnique"])))
        for technique_key in sorted(technique_keys):
            incident_techniques.append({"IncidentTechniqueKey": len(incident_techniques)+1, "IncidentKey": index, "AttackTechniqueKey": technique_key, "IsPrimary": technique_key == rule["AttackTechniqueKey"]})
        sla_rows.append({
            "SLAFactKey": index, "IncidentKey": index, "SLAKey": severity_key,
            "AcknowledgeTargetMinutes": sla["AcknowledgeMinutes"], "AcknowledgeActualMinutes": ack_minutes or "", "AcknowledgeMet": sla_ack_met,
            "ContainTargetMinutes": sla["ContainMinutes"], "ContainActualMinutes": contain_minutes or "", "ContainMet": sla_contain_met,
            "ResolveTargetMinutes": sla["ResolveMinutes"], "ResolveActualMinutes": resolve_minutes or "", "ResolveMet": sla_resolve_met,
            "OverallMet": bool(sla_ack_met and sla_contain_met and sla_resolve_met),
        })

    raw_duplicate_incidents = [dict(row) for row in raw_incidents[: max(1, config["incident_count"] // 200)]]
    raw_incidents.extend(raw_duplicate_incidents)
    rng.shuffle(raw_incidents)
    counts = {
        "raw/security_events_raw.csv": write_csv(RAW / "security_events_raw.csv", raw_events),
        "raw/alerts_raw.csv": write_csv(RAW / "alerts_raw.csv", raw_alerts),
        "raw/incidents_raw.csv": write_csv(RAW / "incidents_raw.csv", raw_incidents),
        "expected/FactSecurityEvents.csv": write_csv(EXPECTED / "FactSecurityEvents.csv", clean_events),
        "expected/FactAlerts.csv": write_csv(EXPECTED / "FactAlerts.csv", clean_alerts),
        "expected/FactIncidents.csv": write_csv(EXPECTED / "FactIncidents.csv", clean_incidents),
        "expected/FactIncidentLifecycle.csv": write_csv(EXPECTED / "FactIncidentLifecycle.csv", lifecycle_rows),
        "expected/BridgeIncidentTechnique.csv": write_csv(EXPECTED / "BridgeIncidentTechnique.csv", incident_techniques),
        "expected/FactSLA.csv": write_csv(EXPECTED / "FactSLA.csv", sla_rows),
    }
    for table, rows in reference.items(): counts[f"reference/{table}.csv"] = len(rows)

    closed_incidents = [row for row in clean_incidents if row["StatusKey"] in {4,5}]
    open_incidents = [row for row in clean_incidents if row["StatusKey"] in {1,2,3}]
    kpis = {
        "Total Events": len(clean_events), "Total Alerts": len(clean_alerts), "Total Incidents": len(clean_incidents),
        "Active Incidents": len(open_incidents), "Closed Incidents": len(closed_incidents),
        "Critical Active Incidents": sum(1 for row in open_incidents if row["SeverityKey"] == 5),
        "Alert to Incident Conversion": round(len(clean_incidents)/len(clean_alerts), 6),
        "False Positive Rate": round(sum(1 for row in clean_alerts if row["IsFalsePositive"])/len(clean_alerts), 6),
        "SLA Compliance": round(sum(1 for row in sla_rows if row["OverallMet"])/len(sla_rows), 6),
        "MTTD Minutes": round(sum(row["DetectionMinutes"] for row in clean_alerts)/len(clean_alerts), 4),
        "MTTA Minutes": round(sum(float(row["AcknowledgementMinutes"]) for row in clean_incidents if row["AcknowledgementMinutes"] != "") / max(1, sum(1 for row in clean_incidents if row["AcknowledgementMinutes"] != "")), 4),
        "MTTR Resolution Minutes": round(sum(float(row["ResolutionMinutes"]) for row in clean_incidents if row["ResolutionMinutes"] != "") / max(1, sum(1 for row in clean_incidents if row["ResolutionMinutes"] != "")), 4),
    }
    (EXPECTED / "kpi_expected.json").write_text(json.dumps(kpis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    file_hashes = {}
    for folder in (RAW, REFERENCE, EXPECTED):
        for path in sorted(folder.glob("*")):
            if path.is_file() and path.name != "dataset_manifest.json":
                file_hashes[str(path.relative_to(ROOT)).replace("\\", "/")] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "name": "EDY SOC Analytics Synthetic Dataset", "version": "1.0.0", "generatedAt": "2026-08-24T00:00:00-03:00",
        "seed": config["seed"], "timezone": config["timezone"], "periodStart": config["period_start"], "periodEnd": config["period_end"],
        "classification": config["dataset_label"], "counts": counts, "qualityInjections": {
            "eventDuplicateRows": duplicate_count, "eventNullAssetRows": config["event_count"] // 173,
            "incidentDuplicateRows": len(raw_duplicate_incidents), "incidentNullAnalystRowsApprox": len(raw_incidents[::211]),
            "labelVariants": "deterministic modulus rules documented in generator"
        }, "sha256": file_hashes,
    }
    (ROOT / "data" / "dataset_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    result = generate()
    print(json.dumps({"seed": result["seed"], "counts": result["counts"]}, ensure_ascii=False, indent=2))
