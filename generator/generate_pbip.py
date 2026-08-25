"""Generate the text-based PBIP/PBIR/TMDL project from validated CSV metadata."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import uuid
from pathlib import Path

from pbir_visuals import PAGE_SCHEMA, drillthrough_config, generate_visuals

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
REPORT = PBI / "EDY SOC Analytics.Report"
MODEL = PBI / "EDY SOC Analytics.SemanticModel"
DEFINITION = MODEL / "definition"
TABLES = DEFINITION / "tables"
ROLES = DEFINITION / "roles"
NAMESPACE = uuid.UUID("68e18ef0-e292-47ef-9de7-fc2b573aa4c1")


def guid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.replace("\r\n", "\n").replace("\n", "\r\n"), encoding="utf-8", newline="")


def write_json(path: Path, payload: dict) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def q(name: str) -> str:
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return name
    return "'" + name.replace("'", "''") + "'"


def read_csv_meta(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        sample = []
        for index, row in enumerate(reader):
            sample.append(row)
            if index >= 499:
                break
        return list(reader.fieldnames or []), sample


def infer_type(name: str, values: list[str]) -> tuple[str, str, str | None]:
    present = [v for v in values if v not in {"", None}]
    lowered = {str(v).lower() for v in present}
    if present and lowered <= {"true", "false"}:
        return "boolean", "type logical", None
    if name == "Date" or name.endswith("Date"):
        return "dateTime", "type date", "dd/MM/yyyy"
    if name.endswith("AtUTC") or "Timestamp" in name:
        return "dateTime", "type datetimezone", "dd/MM/yyyy HH:mm:ss"
    if present:
        try:
            for value in present: int(value)
            return "int64", "Int64.Type", "0"
        except ValueError:
            pass
        try:
            for value in present: float(value)
            return "double", "type number", "0.00"
        except ValueError:
            pass
    return "string", "type text", None


def direct_csv_m(relative: str, columns: list[str], types: dict[str, tuple[str, str, str | None]]) -> str:
    type_rows = ", ".join("{" + json.dumps(name, ensure_ascii=False) + ", " + types[name][1] + "}" for name in columns)
    column_list = "{" + ", ".join(json.dumps(name, ensure_ascii=False) for name in columns) + "}"
    return (
        "let\n"
        f"    Source = fxCsv({json.dumps(relative.replace('\\\\', '/'), ensure_ascii=False)}),\n"
        f"    Selected = Table.SelectColumns(Source, {column_list}),\n"
        f"    Typed = Table.TransformColumnTypes(Selected, {{{type_rows}}})\n"
        "in\n"
        "    Typed"
    )


MEASURES = [
    ("Total de eventos", "SUM ( FactSecurityEvents[EventCount] )", "#,0", "01 Volume"),
    ("Total de alertas", "SUM ( FactAlerts[AlertCount] )", "#,0", "01 Volume"),
    ("Total de incidentes", "SUM ( FactIncidents[IncidentCount] )", "#,0", "01 Volume"),
    ("Incidentes novos", "CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[Status] = \"New\" ) )", "#,0", "02 Operações"),
    ("Incidentes ativos", "CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[IsOpen] = TRUE () ) )", "#,0", "02 Operações"),
    ("Incidentes fechados", "CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[IsOpen] = FALSE () ) )", "#,0", "02 Operações"),
    ("Incidentes críticos ativos", "CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[IsOpen] = TRUE () ), KEEPFILTERS ( DimSeverity[Severity] = \"Critical\" ) )", "#,0", "02 Operações"),
    ("Backlog", "[Incidentes ativos]", "#,0", "02 Operações"),
    ("Data de referência", "MAX ( FactSecurityEvents[EventTimestampUTC] )", "dd/MM/yyyy HH:mm", "05 Tendência"),
    ("Backlog envelhecido", "VAR Limite = [Data de referência] - 7 RETURN CALCULATE ( [Total de incidentes], KEEPFILTERS ( DimStatus[IsOpen] = TRUE () ), FactIncidents[CreatedAtUTC] < Limite )", "#,0", "02 Operações"),
    ("Taxa de fechamento", "DIVIDE ( [Incidentes fechados], [Total de incidentes] )", "0.0%", "02 Operações"),
    ("Taxa de escalonamento", "DIVIDE ( CALCULATE ( [Total de incidentes], FactIncidents[IsEscalated] = TRUE () ), [Total de incidentes] )", "0.0%", "02 Operações"),
    ("Taxa de reabertura", "DIVIDE ( CALCULATE ( [Total de incidentes], FactIncidents[IsReopened] = TRUE () ), [Incidentes fechados] )", "0.0%", "02 Operações"),
    ("Taxa de falsos positivos", "DIVIDE ( CALCULATE ( [Total de alertas], FactAlerts[IsFalsePositive] = TRUE () ), [Total de alertas] )", "0.0%", "04 Qualidade"),
    ("Conversão alerta para incidente", "DIVIDE ( CALCULATE ( [Total de alertas], FactAlerts[BecameIncident] = TRUE () ), [Total de alertas] )", "0.0%", "02 Operações"),
    ("Incidentes por 1.000 alertas", "DIVIDE ( [Total de incidentes] * 1000, [Total de alertas] )", "0.0", "02 Operações"),
    ("Cumprimento de SLA", "DIVIDE ( CALCULATE ( COUNTROWS ( FactSLA ), FactSLA[OverallMet] = TRUE () ), COUNTROWS ( FactSLA ) )", "0.0%", "02 Operações"),
    ("Violações de SLA", "CALCULATE ( COUNTROWS ( FactSLA ), FactSLA[OverallMet] = FALSE () )", "#,0", "02 Operações"),
    ("MTTD (min)", "AVERAGE ( FactAlerts[DetectionMinutes] )", "0.0", "03 Tempos"),
    ("MTTA (min)", "AVERAGE ( FactIncidents[AcknowledgementMinutes] )", "0.0", "03 Tempos"),
    ("Tempo médio de triagem (min)", "AVERAGE ( FactIncidents[TriageMinutes] )", "0.0", "03 Tempos"),
    ("Tempo médio de contenção (min)", "AVERAGE ( FactIncidents[ContainmentMinutes] )", "0.0", "03 Tempos"),
    ("MTTR resolução (min)", "AVERAGE ( FactIncidents[ResolutionMinutes] )", "0.0", "03 Tempos"),
    ("Tempo médio de recuperação (min)", "AVERAGE ( FactIncidents[RecoveryMinutes] )", "0.0", "03 Tempos"),
    ("Idade média do backlog (dias)", "VAR Referencia = [Data de referência] RETURN AVERAGEX ( FILTER ( FactIncidents, RELATED ( DimStatus[IsOpen] ) = TRUE () ), DIVIDE ( DATEDIFF ( FactIncidents[CreatedAtUTC], Referencia, HOUR ), 24 ) )", "0.0", "03 Tempos"),
    ("Incidentes mês anterior", "CALCULATE ( [Total de incidentes], DATEADD ( DimDate[Date], -1, MONTH ) )", "#,0", "05 Tendência"),
    ("Variação mensal de incidentes", "[Total de incidentes] - [Incidentes mês anterior]", "+#,0;-#,0;0", "05 Tendência"),
    ("Variação mensal de incidentes %", "DIVIDE ( [Variação mensal de incidentes], [Incidentes mês anterior] )", "+0.0%;-0.0%;0.0%", "05 Tendência"),
    ("MTTR mês anterior", "CALCULATE ( [MTTR resolução (min)], DATEADD ( DimDate[Date], -1, MONTH ) )", "0.0", "05 Tendência"),
    ("Variação MTTR %", "DIVIDE ( [MTTR resolução (min)] - [MTTR mês anterior], [MTTR mês anterior] )", "+0.0%;-0.0%;0.0%", "05 Tendência"),
    ("Técnicas MITRE observadas", "DISTINCTCOUNT ( BridgeIncidentTechnique[AttackTechniqueKey] )", "#,0", "06 Contexto"),
    ("Cobertura MITRE observada", "DIVIDE ( [Técnicas MITRE observadas], CALCULATE ( COUNTROWS ( DimAttackTechnique ), REMOVEFILTERS ( DimAttackTechnique ) ) )", "0.0%", "06 Contexto"),
    ("Risco acumulado do ativo", "SUM ( FactIncidents[RiskScore] )", "#,0.0", "06 Contexto"),
    ("Ativos de alto risco", "COUNTROWS ( FILTER ( VALUES ( DimAsset[AssetKey] ), [Risco acumulado do ativo] >= 250 ) )", "#,0", "06 Contexto"),
    ("Ruído por 1.000 alertas", "DIVIDE ( CALCULATE ( [Total de alertas], FactAlerts[IsFalsePositive] = TRUE () ) * 1000, [Total de alertas] )", "0.0", "04 Qualidade"),
    ("Fidelidade da fonte", "1 - [Taxa de falsos positivos]", "0.0%", "04 Qualidade"),
    ("Taxa regra para incidente", "DIVIDE ( CALCULATE ( [Total de alertas], FactAlerts[BecameIncident] = TRUE () ), [Total de alertas] )", "0.0%", "04 Qualidade"),
    ("Peso de complexidade resolvida", "SUMX ( FILTER ( FactIncidents, RELATED ( DimStatus[IsOpen] ) = FALSE () ), RELATED ( DimSeverity[RiskWeight] ) * ( 1 + DIVIDE ( FactIncidents[RiskScore], 100 ) ) )", "#,0.0", "06 Contexto"),
    ("Índice contextual de resolução", "VAR Complexidade = [Peso de complexidade resolvida] VAR Tempo = [MTTR resolução (min)] VAR SLA = [Cumprimento de SLA] RETURN DIVIDE ( Complexidade * ( 0.5 + SLA ), 1 + DIVIDE ( Tempo, 60 ) )", "#,0.0", "06 Contexto"),
    ("Registros rejeitados", "COALESCE ( COUNTROWS ( DQ_RejectedRows ), 0 )", "#,0", "04 Qualidade"),
    ("Última atualização UTC", "MAX ( FactSecurityEvents[ReceivedAtUTC] )", 'dd/MM/yy HH:mm "UTC"', "04 Qualidade"),
]


RELATIONSHIPS = [
    ("FactSecurityEvents", "EventDateKey", "DimDate", "DateKey", True), ("FactSecurityEvents", "EventTimeKey", "DimTime", "TimeKey", True),
    ("FactSecurityEvents", "AssetKey", "DimAsset", "AssetKey", True), ("FactSecurityEvents", "SourceProductKey", "DimSourceProduct", "SourceProductKey", True),
    ("FactSecurityEvents", "SeverityKey", "DimSeverity", "SeverityKey", True), ("FactSecurityEvents", "DetectionRuleKey", "DimDetectionRule", "DetectionRuleKey", True),
    ("FactAlerts", "AlertDateKey", "DimDate", "DateKey", True), ("FactAlerts", "AlertTimeKey", "DimTime", "TimeKey", True),
    ("FactAlerts", "AssetKey", "DimAsset", "AssetKey", True), ("FactAlerts", "SourceProductKey", "DimSourceProduct", "SourceProductKey", True),
    ("FactAlerts", "SeverityKey", "DimSeverity", "SeverityKey", True), ("FactAlerts", "DetectionRuleKey", "DimDetectionRule", "DetectionRuleKey", True),
    ("FactIncidents", "CreatedDateKey", "DimDate", "DateKey", True), ("FactIncidents", "CreatedTimeKey", "DimTime", "TimeKey", True),
    ("FactIncidents", "AssetKey", "DimAsset", "AssetKey", True), ("FactIncidents", "SourceProductKey", "DimSourceProduct", "SourceProductKey", True),
    ("FactIncidents", "SeverityKey", "DimSeverity", "SeverityKey", True), ("FactIncidents", "StatusKey", "DimStatus", "StatusKey", True),
    ("FactIncidents", "DetectionRuleKey", "DimDetectionRule", "DetectionRuleKey", True), ("FactIncidents", "AnalystKey", "DimAnalyst", "AnalystKey", True),
    ("FactIncidents", "ClassificationKey", "DimClassification", "ClassificationKey", True), ("FactIncidents", "SLAKey", "DimSLA", "SLAKey", True),
    ("FactIncidentLifecycle", "IncidentKey", "FactIncidents", "IncidentKey", True),
    ("FactSLA", "IncidentKey", "FactIncidents", "IncidentKey", True), ("BridgeIncidentTechnique", "IncidentKey", "FactIncidents", "IncidentKey", True),
    ("BridgeIncidentTechnique", "AttackTechniqueKey", "DimAttackTechnique", "AttackTechniqueKey", True), ("DimAttackTechnique", "AttackTacticKey", "DimAttackTactic", "AttackTacticKey", True),
]

BOTH_DIRECTIONS = {
    ("BridgeIncidentTechnique", "IncidentKey", "FactIncidents", "IncidentKey"),
}

PRIMARY_KEYS = {
    "DimDate": "DateKey", "DimTime": "TimeKey", "DimAsset": "AssetKey",
    "DimSourceProduct": "SourceProductKey", "DimSeverity": "SeverityKey", "DimStatus": "StatusKey",
    "DimDetectionRule": "DetectionRuleKey", "DimAttackTactic": "AttackTacticKey",
    "DimAttackTechnique": "AttackTechniqueKey", "DimAnalyst": "AnalystKey",
    "DimClassification": "ClassificationKey", "DimSLA": "SLAKey", "SecurityAccess": "AccessKey",
    "FactSecurityEvents": "EventKey", "FactAlerts": "AlertKey", "FactIncidents": "IncidentKey",
    "FactIncidentLifecycle": "LifecycleKey", "FactSLA": "SLAFactKey",
    "BridgeIncidentTechnique": "IncidentTechniqueKey",
}

SORT_BY_COLUMNS = {
    ("DimDate", "MonthName"): "MonthNumber",
    ("DimDate", "WeekdayName"): "WeekdayNumber",
    ("DimTime", "HourLabel"): "Hour",
    ("DimSeverity", "Severity"): "SeverityOrder",
    ("DimSeverity", "SeverityPT"): "SeverityOrder",
    ("DimStatus", "Status"): "StatusOrder",
    ("DimStatus", "StatusPT"): "StatusOrder",
    ("FactIncidentLifecycle", "Stage"): "StageOrder",
}


def make_table(name: str, path: Path, relative: str, custom_m: str | None = None) -> str:
    columns, sample = read_csv_meta(path)
    types = {col: infer_type(col, [row[col] for row in sample]) for col in columns}
    lines = [f"table {q(name)}", f"\tlineageTag: {guid('table:'+name)}", ""]
    for col in columns:
        dtype, _, fmt = types[col]
        lines.extend([f"\tcolumn {q(col)}", f"\t\tdataType: {dtype}"])
        if PRIMARY_KEYS.get(name) == col:
            lines.append("\t\tisKey")
        if col.endswith("Key") or col in {"EventId", "AlertId", "IncidentId", "DataClassification", "NetworkAddress"}:
            lines.append("\t\tisHidden")
        if fmt: lines.append(f"\t\tformatString: {fmt}")
        if (name, col) in SORT_BY_COLUMNS:
            lines.append(f"\t\tsortByColumn: {q(SORT_BY_COLUMNS[(name, col)])}")
        lines.extend([f"\t\tlineageTag: {guid('column:'+name+':'+col)}", "\t\tsummarizeBy: none", f"\t\tsourceColumn: {q(col)}", ""])
    source = custom_m or direct_csv_m(relative, columns, types)
    lines.extend([f"\tpartition {q(name)} = m", "\t\tmode: import", "\t\tsource ="])
    lines.extend("\t\t\t\t" + line for line in source.splitlines())
    lines.extend(["", "\tannotation PBI_ResultType = Table", ""])
    return "\n".join(line for line in lines if line != "") + "\n"


def make_measures_table() -> str:
    lines = ["table _Measures", f"\tlineageTag: {guid('table:_Measures')}", ""]
    for name, expression, fmt, folder in MEASURES:
        lines.extend([f"\tmeasure {q(name)} = {expression}", f"\t\tformatString: {fmt}", f"\t\tdisplayFolder: {folder}", f"\t\tlineageTag: {guid('measure:'+name)}", ""])
    lines.extend([
        "\tcolumn Value", "\t\tdataType: int64", "\t\tisHidden", "\t\tsummarizeBy: none", "\t\tsourceColumn: Value", "",
        "\tpartition _Measures = calculated", "\t\tmode: import", "\t\tsource = DATATABLE ( \"Value\", INTEGER, { { 0 } } )", "",
        "\tannotation PBI_Id = 6f7786ec7a684f4c99b28c39b77c1075", ""
    ])
    return "\n".join(lines)


def generate_report() -> None:
    write_json(PBI / "EDY SOC Analytics.pbip", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0", "artifacts": [{"report": {"path": "EDY SOC Analytics.Report"}}],
        "settings": {"enableAutoRecovery": True}
    })
    write_json(REPORT / "definition.pbir", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0", "datasetReference": {"byPath": {"path": "../EDY SOC Analytics.SemanticModel"}}
    })
    report_def = REPORT / "definition"
    write_json(report_def / "version.json", {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"})
    source_theme = ROOT / "theme" / "signal-grid-theme.json"
    theme_payload = json.loads(source_theme.read_text(encoding="utf-8"))
    theme_digest = hashlib.sha256(source_theme.read_bytes()).hexdigest()[:10]
    theme_name = f"SignalGrid-{theme_digest}.json"
    theme_payload["name"] = theme_name
    write_json(REPORT / "StaticResources" / "RegisteredResources" / theme_name, theme_payload)
    write_json(report_def / "report.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {"customTheme": {"name": theme_name, "reportVersionAtImport": {"visual": "2.9.0", "report": "3.3.0", "page": "2.1.0"}, "type": "RegisteredResources"}},
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources", "items": [{"name": theme_name, "path": theme_name, "type": "CustomTheme"}]}],
        "settings": {"useEnhancedTooltips": True, "queryLimitOption": "None", "customMemoryLimit": "1048576", "customTimeoutLimit": "225"},
        "annotations": [{"name": "designSystem", "value": "Signal Grid"}, {"name": "dataClassification", "value": "SYNTHETIC_DEMO_DATA"}]
    })
    pages = [
        ("CommandCenter", "1. Command Center", None), ("SOCOperations", "2. SOC Operations", None),
        ("IncidentLifecycle", "3. Incident Lifecycle", None), ("ThreatMITRE", "4. Threat & MITRE", None),
        ("AssetsExposure", "5. Assets & Exposure", None), ("DetectionEngineering", "6. Detection Engineering", None),
        ("AnalystSLA", "7. Analyst & SLA", None), ("DataQuality", "8. Data Quality", None),
        ("IncidentDrillthrough", "9. Incident Drillthrough", "Drillthrough"), ("Methodology", "10. Methodology", None),
    ]
    write_json(report_def / "pages" / "pages.json", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": [p[0] for p in pages], "activePageName": pages[0][0]
    })
    for name, display, page_type in pages:
        payload = {
            "$schema": PAGE_SCHEMA,
            "name": name, "displayName": display, "displayOption": "FitToPage", "width": 1280, "height": 720,
            "annotations": [{"name": "purpose", "value": display}]
        }
        if page_type:
            payload["type"] = page_type
            payload["filterConfig"], payload["pageBinding"] = drillthrough_config()
        write_json(report_def / "pages" / name / "page.json", payload)
    generate_visuals(report_def)


def generate_model() -> None:
    write_json(MODEL / "definition.pbism", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {"qnaEnabled": False}
    })
    write_text(DEFINITION / "database.tmdl", "database 'EDY SOC Analytics'\n\tcompatibilityLevel: 1702\n\tcompatibilityMode: powerBI\n")
    table_specs: list[tuple[str, Path, str, str | None]] = []
    for path in sorted((ROOT / "data" / "reference").glob("*.csv")):
        table_specs.append((path.stem, path, f"data/reference/{path.name}", None))
    custom = {
        "FactSecurityEvents": (ROOT / "powerbi" / "power-query" / "FactSecurityEvents.m").read_text(encoding="utf-8"),
        "FactAlerts": (ROOT / "powerbi" / "power-query" / "FactAlerts.m").read_text(encoding="utf-8"),
        "FactIncidents": (ROOT / "powerbi" / "power-query" / "FactIncidents.m").read_text(encoding="utf-8"),
    }
    for path in sorted((ROOT / "data" / "expected").glob("*.csv")):
        if path.name == "DQ_RejectedRows.csv":
            continue
        table_specs.append((path.stem, path, f"data/expected/{path.name}", custom.get(path.stem)))
    dq_schema = ROOT / "data" / "expected" / "DQ_RejectedRows.csv"
    if not dq_schema.exists():
        write_text(dq_schema, "event_id,source_product,QualityIssue,data_classification\n")
    table_specs.append(("DQ_RejectedRows", dq_schema, "data/expected/DQ_RejectedRows.csv", (ROOT / "powerbi" / "power-query" / "Quality.m").read_text(encoding="utf-8")))

    for name, path, relative, custom_m in table_specs:
        write_text(TABLES / f"{name}.tmdl", make_table(name, path, relative, custom_m))
    write_text(TABLES / "_Measures.tmdl", make_measures_table())

    expressions = [
        f'expression pProjectRoot = "{ROOT}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]',
        f"\tlineageTag: {guid('expression:pProjectRoot')}", "\tannotation PBI_ResultType = Text", "",
        "expression fxCsv =", "\t\t(relativePath as text) as table =>", "\t\tlet", "\t\t    Slash = Character.FromNumber(92),", "\t\t    NormalizedRoot = Text.TrimEnd(pProjectRoot, {Slash, \"/\"}),", "\t\t    DataRoot = NormalizedRoot & Slash & \"data\",", "\t\t    FullPath = NormalizedRoot & Slash & Text.Replace(relativePath, \"/\", Slash),", "\t\t    Files = Folder.Files(DataRoot),", "\t\t    Matches = Table.SelectRows(Files, each Text.Lower(Text.TrimEnd([Folder Path], {Slash, \"/\"}) & Slash & [Name]) = Text.Lower(FullPath)),", "\t\t    Content = if Table.RowCount(Matches) = 1 then Matches{0}[Content] else error Error.Record(\"fxCsv\", \"CSV path did not resolve uniquely\", [Path=FullPath, Matches=Table.RowCount(Matches)]),", "\t\t    Source = Csv.Document(Content, [Delimiter=\",\", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),", "\t\t    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true])", "\t\tin", "\t\t    Headers", f"\tlineageTag: {guid('expression:fxCsv')}", "\tannotation PBI_ResultType = Function", "",
        "expression fxNormalizeSeverity =", "\t\t(value as nullable text) as nullable text =>", "\t\tlet", "\t\t    Clean = if value = null then null else Text.Lower(Text.Trim(value)),", "\t\t    Result = if List.Contains({\"info\",\"informational\"}, Clean) then \"Informational\" else if List.Contains({\"low\",\"baixo\"}, Clean) then \"Low\" else if List.Contains({\"medium\",\"medio\",\"médio\"}, Clean) then \"Medium\" else if List.Contains({\"high\",\"alto\"}, Clean) then \"High\" else if List.Contains({\"critical\",\"critico\",\"crítico\"}, Clean) then \"Critical\" else null", "\t\tin", "\t\t    Result", f"\tlineageTag: {guid('expression:fxNormalizeSeverity')}", "\tannotation PBI_ResultType = Function", "",
        "expression fxNormalizeStatus =", "\t\t(value as nullable text) as nullable text =>", "\t\tlet", "\t\t    Clean = if value = null then null else Text.Lower(Text.Trim(value)),", "\t\t    Result = if List.Contains({\"new\",\"novo\"}, Clean) then \"New\" else if List.Contains({\"active\",\"ativo\"}, Clean) then \"Active\" else if List.Contains({\"contained\",\"contido\"}, Clean) then \"Contained\" else if List.Contains({\"resolved\",\"resolvido\"}, Clean) then \"Resolved\" else if List.Contains({\"closed\",\"fechado\"}, Clean) then \"Closed\" else null", "\t\tin", "\t\t    Result", f"\tlineageTag: {guid('expression:fxNormalizeStatus')}", "\tannotation PBI_ResultType = Function", ""
    ]
    write_text(DEFINITION / "expressions.tmdl", "\n".join(expressions))

    rel_lines = []
    for fact, fcol, dim, dcol, active in RELATIONSHIPS:
        rel_lines.extend([f"relationship {guid('relationship:'+fact+':'+fcol+':'+dim+':'+dcol)}", f"\tfromColumn: {q(fact)}.{q(fcol)}", f"\ttoColumn: {q(dim)}.{q(dcol)}"])
        if (fact, fcol, dim, dcol) in BOTH_DIRECTIONS:
            rel_lines.append("\tcrossFilteringBehavior: bothDirections")
        rel_lines.append("")
    write_text(DEFINITION / "relationships.tmdl", "\n".join(rel_lines))

    analyst_role = """role SOC_Analyst
\tmodelPermission: read
\n\ttablePermission DimAnalyst
\t\tfilterExpression =
\t\t\t\tVAR CurrentUPN = LOWER ( USERPRINCIPALNAME () )
\t\t\t\tRETURN
\t\t\t\t    DimAnalyst[Team]
\t\t\t\t        IN CALCULATETABLE (
\t\t\t\t            VALUES ( SecurityAccess[Team] ),
\t\t\t\t            FILTER ( SecurityAccess, LOWER ( SecurityAccess[UPN] ) = CurrentUPN )
\t\t\t\t        )
"""
    manager_role = "role SOC_Manager\n\tmodelPermission: read\n"
    write_text(ROLES / "SOC_Analyst.tmdl", analyst_role)
    write_text(ROLES / "SOC_Manager.tmdl", manager_role)

    table_names = [name for name, *_ in table_specs] + ["_Measures"]
    model_lines = ["model Model", "\tculture: pt-BR", "\tdefaultPowerBIDataSourceVersion: powerBI_V3", "\tdiscourageImplicitMeasures", "\tsourceQueryCulture: pt-BR", "\tdataAccessOptions", "\t\tlegacyRedirects", "\t\treturnErrorValuesAsNull", f"\tannotation PBIDesktopVersion = 2.157.879.0 (26.08)", "\tannotation __PBI_TimeIntelligenceEnabled = 0", ""]
    model_lines += [f"ref table {q(name)}" for name in table_names]
    model_lines += ["", "ref expression pProjectRoot", "ref expression fxCsv", "ref expression fxNormalizeSeverity", "ref expression fxNormalizeStatus", "", "ref role SOC_Analyst", "ref role SOC_Manager", ""]
    write_text(DEFINITION / "model.tmdl", "\n".join(model_lines))


def main() -> None:
    generate_report()
    generate_model()
    print(json.dumps({"pbip": str(PBI / "EDY SOC Analytics.pbip"), "pages": 10, "measures": len(MEASURES)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
