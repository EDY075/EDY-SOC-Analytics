let
    Source = fxCsv("data/raw/alerts_raw.csv"),
    Selected = Table.SelectColumns(Source, {"alert_id", "event_id", "detected_at", "source_product", "asset_id", "rule_id", "severity", "false_positive", "data_classification"}),
    Typed = Table.TransformColumnTypes(Selected, {{"detected_at", type datetimezone}}),
    Normalized = Table.TransformColumns(Typed, {{"severity", fxNormalizeSeverity, type text}, {"false_positive", each Text.Upper(Text.Trim(_)) = "TRUE", type logical}}),
    Valid = Table.SelectRows(Normalized, each [alert_id] <> null and [detected_at] <> null and [severity] <> null),
    Deduplicated = Table.Distinct(Valid, {"alert_id"}),
    WithAlertKey = Table.AddColumn(Deduplicated, "AlertKey", each Number.FromText(Text.AfterDelimiter([alert_id], "-")), Int64.Type),
    MergeEvent = Table.NestedJoin(WithAlertKey, {"event_id"}, FactSecurityEvents, {"EventId"}, "Event", JoinKind.Inner),
    Expanded = Table.ExpandTableColumn(MergeEvent, "Event", {"EventTimestampUTC", "SourceProductKey", "AssetKey", "DetectionRuleKey"}, {"EventTimestampUTC", "SourceProductKey", "AssetKey", "DetectionRuleKey"}),
    MergeSeverity = Table.NestedJoin(Expanded, {"severity"}, DimSeverity, {"Severity"}, "SeverityDim", JoinKind.LeftOuter),
    WithSeverity = Table.ExpandTableColumn(MergeSeverity, "SeverityDim", {"SeverityKey"}, {"SeverityKey"}),
    AddDateKey = Table.AddColumn(WithSeverity, "AlertDateKey", each Number.FromText(Date.ToText(Date.From([detected_at]), "yyyyMMdd")), Int64.Type),
    AddTimeKey = Table.AddColumn(AddDateKey, "AlertTimeKey", each Time.Hour(Time.From([detected_at])) * 100 + Number.IntegerDivide(Time.Minute(Time.From([detected_at])), 5) * 5, Int64.Type),
    AddCount = Table.AddColumn(AddTimeKey, "AlertCount", each 1, Int64.Type),
    AddDetection = Table.AddColumn(AddCount, "DetectionMinutes", each Duration.TotalMinutes([detected_at] - [EventTimestampUTC]), type number),
    IncidentAlertIds = List.Buffer(List.Distinct(fxCsv("data/raw/incidents_raw.csv")[alert_id])),
    AddIncidentFlag = Table.AddColumn(AddDetection, "BecameIncident", each List.Contains(IncidentAlertIds, [alert_id]), type logical),
    Renamed = Table.RenameColumns(AddIncidentFlag, {{"alert_id", "AlertId"}, {"event_id", "EventId"}, {"detected_at", "DetectedAtUTC"}, {"false_positive", "IsFalsePositive"}, {"data_classification", "DataClassification"}}),
    Final = Table.SelectColumns(Renamed, {"AlertKey", "AlertId", "EventId", "DetectedAtUTC", "AlertDateKey", "AlertTimeKey", "SourceProductKey", "AssetKey", "DetectionRuleKey", "SeverityKey", "AlertCount", "DetectionMinutes", "IsFalsePositive", "BecameIncident", "DataClassification"})
in
    Final
