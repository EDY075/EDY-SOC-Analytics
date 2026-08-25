"""Deterministic PBIR visual authoring for the EDY SOC Analytics report."""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from pathlib import Path
from typing import Any

VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"
MOBILE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainerMobileState/2.4.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"
NAMESPACE = uuid.UUID("68e18ef0-e292-47ef-9de7-fc2b573aa4c1")


def visual_id(page: str, label: str) -> str:
    return uuid.uuid5(NAMESPACE, f"visual:{page}:{label}").hex[:20]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(content.replace("\n", "\r\n"), encoding="utf-8", newline="")


def lit_string(value: str) -> dict[str, Any]:
    escaped = value.replace("'", "''")
    return {"expr": {"Literal": {"Value": f"'{escaped}'"}}}


def lit_bool(value: bool) -> dict[str, Any]:
    return {"expr": {"Literal": {"Value": "true" if value else "false"}}}


def lit_num(value: int | float, suffix: str = "D") -> dict[str, Any]:
    return {"expr": {"Literal": {"Value": f"{value}{suffix}"}}}


def color(value: str) -> dict[str, Any]:
    return {"solid": {"color": lit_string(value)}}


def position(x: int, y: int, width: int, height: int, order: int) -> dict[str, Any]:
    return {"x": x, "y": y, "z": order, "height": height, "width": width, "tabOrder": order}


def column(table: str, name: str, active: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
        "queryRef": f"{table}.{name}",
        "nativeQueryRef": name,
    }
    if active:
        result["active"] = True
    return result


def measure(name: str) -> dict[str, Any]:
    return {
        "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": name}},
        "queryRef": f"_Measures.{name}",
        "nativeQueryRef": name,
    }


def aggregation(table: str, name: str, function: int) -> dict[str, Any]:
    labels = {0: "Sum", 1: "Average", 2: "Count", 3: "Min", 4: "Max", 5: "CountNonNull", 6: "Median", 7: "StandardDeviation", 8: "Variance"}
    label = labels[function]
    native = {0: "Sum", 1: "Average", 2: "Count", 3: "Minimum", 4: "Maximum", 5: "Count", 6: "Median", 7: "Standard deviation", 8: "Variance"}[function]
    return {
        "field": {
            "Aggregation": {
                "Expression": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": name}},
                "Function": function,
            }
        },
        "queryRef": f"{label}({table}.{name})",
        "nativeQueryRef": f"{native} of {name}",
    }


def vco(title: str, alt_text: str, *, title_visible: bool = True) -> dict[str, Any]:
    return {
        "general": [{"properties": {"altText": lit_string(alt_text)}}],
        "title": [{
            "properties": {
                "show": lit_bool(title_visible),
                "text": lit_string(title),
                "fontColor": color("#E8EEF7"),
                "fontFamily": lit_string("Segoe UI Semibold"),
                "fontSize": lit_num(12),
                "bold": lit_bool(True),
                "titleWrap": lit_bool(True),
            }
        }],
        "background": [{"properties": {"show": lit_bool(True), "color": color("#141B25"), "transparency": lit_num(0)}}],
        "border": [{"properties": {"show": lit_bool(True), "color": color("#273244"), "radius": lit_num(6), "width": lit_num(1)}}],
        "padding": [{"properties": {"top": lit_num(8), "bottom": lit_num(8), "left": lit_num(10), "right": lit_num(10)}}],
        "visualHeader": [{"properties": {"show": lit_bool(True), "foreground": color("#AEBBD0"), "background": color("#141B25"), "transparency": lit_num(0)}}],
    }


def textbox(page: str, label: str, text: str, x: int, y: int, width: int, height: int, order: int, *, size: int = 18, color_hex: str = "#E8EEF7", weight: str = "Segoe UI Semibold") -> dict[str, Any]:
    name = visual_id(page, label)
    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": position(x, y, width, height, order),
        "visual": {
            "visualType": "textbox",
            "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": text, "textStyle": {"fontFamily": weight, "fontSize": f"{size}px", "color": color_hex}}], "horizontalTextAlignment": "left"}]}}]},
            "visualContainerObjects": {
                "general": [{"properties": {"altText": lit_string(text)}}],
                "background": [{"properties": {"show": lit_bool(False)}}],
                "border": [{"properties": {"show": lit_bool(False)}}],
                "padding": [{"properties": {"top": lit_num(0), "bottom": lit_num(0), "left": lit_num(0), "right": lit_num(0)}}],
            },
        },
    }


def navigator(page: str, order: int = 20) -> dict[str, Any]:
    name = visual_id(page, "page-navigator")
    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": position(24, 62, 1232, 42, order),
        "visual": {
            "visualType": "pageNavigator",
            "visualContainerObjects": {
                "general": [{"properties": {"altText": lit_string("Navegação entre as páginas do relatório")}}],
                "background": [{"properties": {"show": lit_bool(False)}}],
                "border": [{"properties": {"show": lit_bool(False)}}],
                "padding": [{"properties": {"top": lit_num(0), "bottom": lit_num(0), "left": lit_num(0), "right": lit_num(0)}}],
            },
        },
    }


def card(page: str, label: str, title: str, measures: list[str], x: int, y: int, width: int, height: int, order: int) -> dict[str, Any]:
    name = visual_id(page, label)
    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": position(x, y, width, height, order),
        "visual": {
            "visualType": "cardVisual",
            "query": {"queryState": {"Data": {"projections": [measure(item) for item in measures]}}},
            "objects": {
                "value": [{"properties": {"fontColor": color("#F5F8FC"), "fontSize": lit_num(16), "bold": lit_bool(True)}, "selector": {"id": "default"}}],
                "label": [{"properties": {"show": lit_bool(True), "fontColor": color("#AEBBD0"), "fontSize": lit_num(9), "textWrap": lit_bool(True)}, "selector": {"id": "default"}}],
                "cardCalloutArea": [{"properties": {"show": lit_bool(True), "paddingUniform": lit_num(6), "rectangleRoundedCurve": lit_num(4), "backgroundFillColor": color("#111823"), "backgroundTransparency": lit_num(0)}}],
                "layout": [{"properties": {"autoGrid": lit_bool(True), "style": lit_string("Cards"), "cellPadding": lit_num(6, "L")}, "selector": {"id": "default"}}],
            },
            "visualContainerObjects": vco(title, f"{title}. Indicadores: {', '.join(measures)}"),
        },
    }


def chart(page: str, label: str, title: str, visual_type: str, category: tuple[str, str], values: list[dict[str, Any]], x: int, y: int, width: int, height: int, order: int, *, series: tuple[str, str] | None = None) -> dict[str, Any]:
    name = visual_id(page, label)
    query_state: dict[str, Any] = {
        "Category": {"projections": [column(category[0], category[1], active=True)]},
        "Y": {"projections": values},
    }
    if series:
        query_state["Series"] = {"projections": [column(series[0], series[1])]}
    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": position(x, y, width, height, order),
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": query_state},
            "visualContainerObjects": vco(title, f"{title}. Use seleção cruzada para filtrar os demais visuais."),
        },
    }


def table(page: str, label: str, title: str, fields: list[dict[str, Any]], x: int, y: int, width: int, height: int, order: int) -> dict[str, Any]:
    name = visual_id(page, label)
    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": position(x, y, width, height, order),
        "visual": {
            "visualType": "tableEx",
            "query": {"queryState": {"Values": {"projections": fields}}},
            "objects": {
                "columnHeaders": [{"properties": {"columnAdjustment": lit_string("growToFit"), "autoSizeColumnWidth": lit_bool(True), "fontColor": color("#E8EEF7"), "backColor": color("#1A2431"), "bold": lit_bool(True), "wordWrap": lit_bool(True)}}],
                "values": [{"properties": {"fontColorPrimary": color("#C9D5E6"), "backColorPrimary": color("#141B25"), "fontColorSecondary": color("#C9D5E6"), "backColorSecondary": color("#111823"), "wordWrap": lit_bool(False)}}],
            },
            "visualContainerObjects": vco(title, f"Tabela acessível: {title}."),
        },
    }


def slicer(page: str, label: str, title: str, field: tuple[str, str], x: int, y: int, width: int, height: int, order: int, *, sync_group: str | None = None) -> dict[str, Any]:
    name = visual_id(page, label)
    visual: dict[str, Any] = {
        "visualType": "slicer",
        "query": {"queryState": {"Values": {"projections": [column(field[0], field[1])]}}},
        "objects": {"data": [{"properties": {"mode": lit_string("Dropdown")}}]},
        "visualContainerObjects": vco(title, f"Filtro {title}. Permite uma ou múltiplas seleções."),
    }
    if sync_group:
        visual["syncGroup"] = {"groupName": sync_group, "fieldChanges": True, "filterChanges": True}
    return {"$schema": VISUAL_SCHEMA, "name": name, "position": position(x, y, width, height, order), "visual": visual}


def action_button(
    page: str,
    label: str,
    text: str,
    destination: str | None,
    x: int,
    y: int,
    width: int,
    height: int,
    order: int,
    *,
    action_type: str = "PageNavigation",
) -> dict[str, Any]:
    name = visual_id(page, label)
    link_properties: dict[str, Any] = {
        "show": lit_bool(True),
        "type": lit_string(action_type),
        "showDefaultTooltip": lit_bool(True),
        "enabledTooltip": lit_string(text),
    }
    if action_type == "PageNavigation" and destination:
        link_properties["navigationSection"] = lit_string(destination)
    elif action_type == "Bookmark" and destination:
        link_properties["bookmark"] = lit_string(destination)
    return {
        "$schema": VISUAL_SCHEMA,
        "name": name,
        "position": position(x, y, width, height, order),
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "text": [
                    {"properties": {"show": lit_bool(True), "text": lit_string(text)}},
                    {"properties": {"show": lit_bool(True), "text": lit_string(text), "fontColor": color("#E8EEF7"), "fontSize": lit_num(11), "bold": lit_bool(True)}, "selector": {"id": "default"}},
                ]
            },
            "visualContainerObjects": {
                "general": [{"properties": {"altText": lit_string(text)}}],
                "visualLink": [{"properties": link_properties}],
                "background": [{"properties": {"show": lit_bool(True), "color": color("#1A2431"), "transparency": lit_num(0)}}],
                "border": [{"properties": {"show": lit_bool(True), "color": color("#39C6E6"), "radius": lit_num(6), "width": lit_num(1)}}],
                "padding": [{"properties": {"top": lit_num(4), "bottom": lit_num(4), "left": lit_num(8), "right": lit_num(8)}}],
            },
        },
    }


def page_header(page: str, title: str, subtitle: str, *, reset: str | None = None) -> list[dict[str, Any]]:
    visuals = [
        textbox(page, "title", title, 24, 12, 760, 40, 1, size=22),
        textbox(page, "subtitle", subtitle, 800, 18, 300 if reset else 456, 26, 2, size=11, color_hex="#8FA0B8", weight="Segoe UI"),
        navigator(page, 10),
    ]
    if reset == "bookmark":
        visuals.append(action_button(page, "reset-bookmark", "Estado padrão", "f145a352ab22f855cfd6", 1116, 14, 140, 34, 3, action_type="Bookmark"))
    elif reset == "clear":
        visuals.append(action_button(page, "reset-filters", "Limpar filtros", None, 1116, 14, 140, 34, 3, action_type="ClearAllSlicers"))
    return visuals


def build_pages() -> dict[str, list[dict[str, Any]]]:
    pages: dict[str, list[dict[str, Any]]] = {}

    p = "CommandCenter"
    pages[p] = page_header(p, "COMMAND CENTER", "Visão executiva • dados sintéticos • America/Sao_Paulo", reset="clear") + [
        card(p, "kpi-primary", "Prioridade agora", ["Incidentes ativos", "Incidentes críticos ativos"], 24, 120, 292, 122, 20),
        card(p, "kpi-backlog", "Backlog e SLA", ["Backlog", "Cumprimento de SLA"], 332, 120, 292, 122, 21),
        card(p, "kpi-time", "Velocidade e tendência", ["MTTD (min)", "MTTR resolução (min)", "Variação mensal de incidentes %"], 640, 120, 616, 122, 22),
        chart(p, "trend", "Tendência mensal de incidentes", "lineChart", ("DimDate", "YearMonth"), [measure("Total de incidentes")], 24, 258, 760, 238, 30),
        chart(p, "severity", "Incidentes por severidade", "clusteredBarChart", ("DimSeverity", "SeverityPT"), [measure("Total de incidentes")], 800, 258, 456, 238, 31),
        table(p, "priority", "Fila de prioridade sintética", [column("FactIncidents", "IncidentId"), column("DimSeverity", "SeverityPT"), column("DimStatus", "StatusPT"), column("DimAsset", "AssetLabel"), column("FactIncidents", "RiskScore")], 24, 512, 1000, 184, 40),
        slicer(p, "year", "Ano", ("DimDate", "Year"), 1040, 512, 216, 80, 41, sync_group="DateYearSync"),
        action_button(p, "method", "Metodologia", "Methodology", 1040, 612, 216, 44, 42),
    ]

    p = "SOCOperations"
    pages[p] = page_header(p, "SOC OPERATIONS", "Volume, conversão e sinal operacional", reset="bookmark") + [
        card(p, "kpis-volume", "Fluxo operacional", ["Total de eventos", "Total de alertas", "Total de incidentes"], 24, 120, 730, 118, 20),
        card(p, "kpis-quality", "Conversão e ruído", ["Conversão alerta para incidente", "Taxa de falsos positivos"], 770, 120, 486, 118, 21),
        chart(p, "alerts-trend", "Alertas ao longo do tempo", "lineChart", ("DimDate", "YearMonth"), [measure("Total de alertas"), measure("Total de incidentes")], 24, 254, 750, 210, 30),
        chart(p, "source", "Volume por produto-fonte", "clusteredBarChart", ("DimSourceProduct", "SourceProduct"), [measure("Total de alertas")], 790, 254, 466, 210, 31),
        chart(p, "rules", "Regras com maior volume", "clusteredBarChart", ("DimDetectionRule", "RuleName"), [measure("Total de alertas")], 24, 480, 750, 216, 40),
        slicer(p, "severity", "Severidade", ("DimSeverity", "SeverityPT"), 790, 480, 220, 80, 41),
        slicer(p, "year", "Ano", ("DimDate", "Year"), 1026, 480, 230, 80, 42, sync_group="DateYearSync"),
        table(p, "source-table", "Fidelidade por fonte", [column("DimSourceProduct", "SourceProduct"), measure("Total de alertas"), measure("Taxa de falsos positivos"), measure("Fidelidade da fonte")], 790, 576, 466, 120, 43),
    ]

    p = "IncidentLifecycle"
    pages[p] = page_header(p, "INCIDENT LIFECYCLE", "Relógios separados para reconhecer, triar, conter e resolver") + [
        card(p, "times-flow", "Relógios do ciclo", ["MTTA (min)", "Tempo médio de triagem (min)", "Tempo médio de contenção (min)"], 24, 120, 730, 118, 20),
        card(p, "times-outcome", "Resolução e SLA", ["MTTR resolução (min)", "Cumprimento de SLA"], 770, 120, 486, 118, 21),
        chart(p, "stage", "Tempo médio por etapa", "clusteredBarChart", ("FactIncidentLifecycle", "Stage"), [aggregation("FactIncidentLifecycle", "MinutesFromPreviousStage", 1)], 24, 254, 610, 242, 30),
        chart(p, "severity", "MTTR por severidade", "clusteredBarChart", ("DimSeverity", "SeverityPT"), [measure("MTTR resolução (min)")], 650, 254, 606, 242, 31),
        chart(p, "sla", "Cumprimento de SLA por severidade", "clusteredBarChart", ("DimSeverity", "SeverityPT"), [measure("Cumprimento de SLA")], 24, 512, 610, 184, 40),
        table(p, "aging", "Backlog e violações", [column("DimSeverity", "SeverityPT"), measure("Backlog"), measure("Backlog envelhecido"), measure("Violações de SLA"), measure("Idade média do backlog (dias)")], 650, 512, 606, 184, 41),
    ]

    p = "ThreatMITRE"
    pages[p] = page_header(p, "THREAT & MITRE", "Comportamentos observados e cobertura ATT&CK Enterprise", reset="clear") + [
        card(p, "mitre-kpis", "Cobertura observada", ["Técnicas MITRE observadas", "Cobertura MITRE observada", "Incidentes críticos ativos"], 24, 120, 800, 118, 20),
        slicer(p, "tactic", "Tática", ("DimAttackTactic", "TacticNamePT"), 840, 120, 416, 80, 21),
        chart(p, "tactics", "Incidentes por tática", "clusteredBarChart", ("DimAttackTactic", "TacticNamePT"), [measure("Total de incidentes")], 24, 254, 520, 270, 30),
        chart(p, "techniques", "Técnicas mais frequentes", "clusteredBarChart", ("DimAttackTechnique", "TechniqueName"), [measure("Total de incidentes")], 560, 254, 696, 270, 31),
        table(p, "mitre-table", "Tabela acessível MITRE", [column("DimAttackTactic", "TacticNamePT"), column("DimAttackTechnique", "TechniqueId"), column("DimAttackTechnique", "TechniqueName"), measure("Total de incidentes"), measure("Risco acumulado do ativo")], 24, 540, 1232, 156, 40),
    ]

    p = "AssetsExposure"
    pages[p] = page_header(p, "ASSETS & EXPOSURE", "Concentração de risco por ativo, unidade e ambiente", reset="clear") + [
        card(p, "asset-kpis", "Exposição", ["Ativos de alto risco", "Risco acumulado do ativo", "Incidentes ativos"], 24, 120, 800, 118, 20),
        slicer(p, "environment", "Ambiente", ("DimAsset", "Environment"), 840, 120, 200, 80, 21),
        slicer(p, "business", "Unidade", ("DimAsset", "BusinessUnit"), 1056, 120, 200, 80, 22),
        chart(p, "asset-risk", "Risco acumulado por ativo", "clusteredBarChart", ("DimAsset", "AssetLabel"), [measure("Risco acumulado do ativo")], 24, 254, 740, 270, 30),
        chart(p, "unit", "Incidentes por unidade", "clusteredBarChart", ("DimAsset", "BusinessUnit"), [measure("Total de incidentes")], 780, 254, 476, 270, 31),
        table(p, "assets-table", "Detalhes de exposição", [column("DimAsset", "AssetLabel"), column("DimAsset", "AssetType"), column("DimAsset", "Criticality"), column("DimAsset", "Environment"), measure("Total de incidentes"), measure("Risco acumulado do ativo")], 24, 540, 1232, 156, 40),
    ]

    p = "DetectionEngineering"
    pages[p] = page_header(p, "DETECTION ENGINEERING", "Sinal, ruído, conversão e candidatos a ajuste", reset="clear") + [
        card(p, "detection-volume", "Sinal e ruído", ["Total de alertas", "Taxa de falsos positivos"], 24, 120, 420, 118, 20),
        card(p, "detection-conversion", "Eficiência", ["Taxa regra para incidente", "Ruído por 1.000 alertas"], 460, 120, 420, 118, 21),
        slicer(p, "family", "Família da regra", ("DimDetectionRule", "RuleFamily"), 896, 120, 360, 80, 22),
        chart(p, "rules-alerts", "Volume de alertas por regra", "clusteredBarChart", ("DimDetectionRule", "RuleName"), [measure("Total de alertas")], 24, 254, 610, 242, 30),
        chart(p, "rules-fp", "Falso positivo por regra", "clusteredBarChart", ("DimDetectionRule", "RuleName"), [measure("Taxa de falsos positivos")], 650, 254, 606, 242, 31),
        table(p, "rules-table", "Matriz de ajuste", [column("DimDetectionRule", "RuleName"), column("DimDetectionRule", "RuleFamily"), measure("Total de alertas"), measure("Taxa regra para incidente"), measure("Taxa de falsos positivos"), measure("Fidelidade da fonte")], 24, 512, 1232, 184, 40),
    ]

    p = "AnalystSLA"
    pages[p] = page_header(p, "ANALYST & SLA", "Carga contextualizada; sem ranking simplista de pessoas", reset="clear") + [
        card(p, "analyst-outcome", "Contexto da operação", ["Cumprimento de SLA", "Índice contextual de resolução"], 24, 120, 440, 118, 20),
        card(p, "analyst-complexity", "Complexidade e tempo", ["Peso de complexidade resolvida", "MTTR resolução (min)"], 480, 120, 440, 118, 21),
        slicer(p, "team", "Equipe", ("DimAnalyst", "Team"), 940, 120, 316, 80, 22),
        chart(p, "team-load", "Carga por equipe", "clusteredBarChart", ("DimAnalyst", "Team"), [measure("Total de incidentes")], 24, 254, 610, 242, 30),
        chart(p, "team-sla", "SLA por equipe", "clusteredBarChart", ("DimAnalyst", "Team"), [measure("Cumprimento de SLA")], 650, 254, 606, 242, 31),
        table(p, "analyst-table", "Distribuição contextual", [column("DimAnalyst", "AnalystLabel"), column("DimAnalyst", "Team"), column("DimAnalyst", "ExperienceBand"), measure("Total de incidentes"), measure("Cumprimento de SLA"), measure("Índice contextual de resolução")], 24, 512, 1232, 184, 40),
    ]

    p = "DataQuality"
    pages[p] = page_header(p, "DATA QUALITY", "Completude, validade, rejeições e linhagem segura", reset="clear") + [
        card(p, "quality-volume", "Estado do dataset", ["Registros rejeitados", "Total de eventos"], 24, 120, 440, 118, 20),
        card(p, "quality-refresh", "Atualização e fidelidade", ["Última atualização UTC", "Fidelidade da fonte"], 480, 120, 440, 118, 21),
        slicer(p, "source", "Produto-fonte", ("DimSourceProduct", "SourceProduct"), 940, 120, 316, 80, 22),
        chart(p, "quality-source", "Eventos por produto-fonte", "clusteredBarChart", ("DimSourceProduct", "SourceProduct"), [measure("Total de eventos")], 24, 254, 610, 242, 30),
        chart(p, "fidelity-source", "Fidelidade por produto-fonte", "clusteredBarChart", ("DimSourceProduct", "SourceProduct"), [measure("Fidelidade da fonte")], 650, 254, 606, 242, 31),
        table(p, "rejections", "Registros rejeitados (sem payload)", [column("DQ_RejectedRows", "source_product"), column("DQ_RejectedRows", "QualityIssue"), column("DQ_RejectedRows", "data_classification")], 24, 512, 610, 184, 40),
        table(p, "lineage", "Classificação e origem", [column("DimSourceProduct", "SourceProduct"), column("DimSourceProduct", "SourceSystem"), column("DimSourceProduct", "DataClassification"), measure("Total de eventos"), measure("Fidelidade da fonte")], 650, 512, 606, 184, 41),
    ]

    p = "IncidentDrillthrough"
    pages[p] = page_header(p, "INCIDENT DRILLTHROUGH", "Detalhe seguro de um incidente sintético selecionado") + [
        action_button(p, "back", "Command Center", "CommandCenter", 24, 116, 190, 44, 20),
        card(p, "incident-flow", "Resumo do incidente", ["Total de incidentes", "MTTA (min)", "Tempo médio de contenção (min)"], 230, 116, 610, 118, 21),
        card(p, "incident-outcome", "Resolução e SLA", ["MTTR resolução (min)", "Cumprimento de SLA"], 856, 116, 400, 118, 22),
        table(p, "incident-detail", "Identificação e contexto", [column("FactIncidents", "IncidentId"), column("DimSeverity", "SeverityPT"), column("DimStatus", "StatusPT"), column("DimAsset", "AssetLabel"), column("DimDetectionRule", "RuleName"), column("FactIncidents", "RiskScore")], 24, 250, 1232, 180, 30),
        table(p, "timeline", "Timeline do ciclo de vida", [column("FactIncidentLifecycle", "Stage"), column("FactIncidentLifecycle", "StageAtUTC"), column("FactIncidentLifecycle", "MinutesFromPreviousStage"), column("FactIncidentLifecycle", "SafeAction")], 24, 446, 610, 250, 40),
        table(p, "incident-mitre", "MITRE observado no incidente", [column("DimAttackTactic", "TacticNamePT"), column("DimAttackTechnique", "TechniqueId"), column("DimAttackTechnique", "TechniqueName"), measure("Total de incidentes")], 650, 446, 606, 250, 41),
    ]

    p = "Methodology"
    pages[p] = page_header(p, "METHODOLOGY", "Definições, limites e fontes primárias") + [
        textbox(p, "scope", "ESCOPO E ÉTICA\nTodos os registros são sintéticos, determinísticos e classificados como SYNTHETIC_DEMO_DATA. Nenhum log, banco, credencial, IP pessoal ou evidência operacional foi usado.", 24, 124, 386, 190, 20, size=13, weight="Segoe UI"),
        textbox(p, "clocks", "RELÓGIOS DO SOC\nMTTD: evento → detecção. MTTA: criação → reconhecimento. Triagem, contenção, resolução e recuperação são medidos separadamente; MTTR neste relatório significa tempo até resolução.", 426, 124, 402, 190, 21, size=13, weight="Segoe UI"),
        textbox(p, "security", "SEGURANÇA E ACESSO\nRLS demonstrativa: SOC_Analyst restringe a equipe atribuída; SOC_Manager tem visão completa. A opção de privacidade é limitada a este arquivo e apenas às fontes CSV sintéticas locais.", 844, 124, 412, 190, 22, size=13, weight="Segoe UI"),
        textbox(p, "sources", "FONTES PRIMÁRIAS\nMicrosoft Learn: PL-300, Power BI, star schema, PBIP/PBIR/TMDL, RLS, acessibilidade, mobile e Performance Analyzer. MITRE ATT&CK Enterprise. NIST CSF 2.0 e SP 800-61 Rev. 3.", 24, 334, 600, 176, 30, size=13, weight="Segoe UI"),
        textbox(p, "limits", "LIMITAÇÕES\nO dataset representa uma operação fictícia e não estima risco real. Comparações entre analistas são contextualizadas por severidade e complexidade; não constituem avaliação individual. Cobertura MITRE significa técnicas observadas no conjunto sintético.", 640, 334, 616, 176, 31, size=13, weight="Segoe UI"),
        textbox(p, "usage", "COMO LER\nComece no Command Center, use os filtros por período e severidade, selecione barras para filtrar os detalhes e abra o drillthrough a partir de um incidente. Tabelas oferecem alternativa legível aos gráficos.", 24, 530, 1232, 142, 40, size=13, weight="Segoe UI"),
    ]
    return pages


def drillthrough_config() -> tuple[dict[str, Any], dict[str, Any]]:
    filter_name = "Filter" + hashlib.sha256(b"drillthrough:FactIncidents:IncidentId").hexdigest()[:24]
    field = {"Column": {"Expression": {"SourceRef": {"Entity": "FactIncidents"}}, "Property": "IncidentId"}}
    filter_config = {"filters": [{"name": filter_name, "field": field, "type": "Categorical", "howCreated": "Drillthrough"}]}
    page_binding = {"name": "Pod", "type": "Drillthrough", "parameters": [{"name": "Param_" + filter_name, "boundFilter": filter_name, "fieldExpr": field}]}
    return filter_config, page_binding


def generate_visuals(report_definition: Path) -> dict[str, int]:
    pages = build_pages()
    total = 0
    project_root = report_definition.parents[2]
    for page, visuals in pages.items():
        visual_root = report_definition / "pages" / page / "visuals"
        expected_ids = {payload["name"] for payload in visuals}
        if visual_root.exists():
            for existing in visual_root.iterdir():
                if existing.is_dir() and existing.name not in expected_ids:
                    destination = project_root / "archive" / "stale-visuals" / page / existing.name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if not destination.exists():
                        shutil.move(str(existing), str(destination))
        mobile_y = 0
        for payload in visuals:
            visual_dir = visual_root / payload["name"]
            write_json(visual_dir / "visual.json", payload)
            visual_type = payload["visual"]["visualType"]
            desktop_height = payload["position"]["height"]
            if visual_type == "pageNavigator":
                stale_mobile = visual_dir / "mobile.json"
                if stale_mobile.exists():
                    destination = project_root / "archive" / "stale-mobile" / page / payload["name"] / "mobile.json"
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if not destination.exists():
                        shutil.move(str(stale_mobile), str(destination))
                total += 1
                continue
            card_count = len(payload.get("visual", {}).get("query", {}).get("queryState", {}).get("Data", {}).get("projections", []))
            mobile_height = {
                "textbox": max(48, min(220, desktop_height)),
                "cardVisual": 176 if card_count <= 3 else 260,
                "slicer": 88,
                "actionButton": 52,
                "tableEx": 280,
            }.get(visual_type, 230)
            write_json(visual_dir / "mobile.json", {
                "$schema": MOBILE_SCHEMA,
                "position": {"x": 0, "y": mobile_y, "height": mobile_height, "width": 320},
            })
            mobile_y += mobile_height + 8
            total += 1
    return {"pages": len(pages), "visuals": total}
