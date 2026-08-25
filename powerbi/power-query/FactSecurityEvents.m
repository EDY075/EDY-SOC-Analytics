let
    Source = fxCsv("data/raw/security_events_raw.csv"),
    Selected = Table.SelectColumns(Source, {"event_id", "event_timestamp", "received_at", "source_product", "source_system", "asset_id", "rule_id", "severity", "event_category", "data_classification"}),
    Trimmed = Table.TransformColumns(Selected, {
        {"event_id", Text.Trim, type text}, {"source_product", Text.Trim, type text},
        {"asset_id", Text.Trim, type text}, {"rule_id", Text.Trim, type text},
        {"severity", Text.Trim, type text}
    }),
    Typed = Table.TransformColumnTypes(Trimmed, {{"event_timestamp", type datetimezone}, {"received_at", type datetimezone}}),
    NormalizedSeverity = Table.TransformColumns(Typed, {{"severity", fxNormalizeSeverity, type text}}),
    Normalized = Table.TransformColumns(NormalizedSeverity, {{"asset_id", each if _ = null or Text.Trim(_) = "" then "UNKNOWN" else Text.Trim(_), type text}}),
    ValidRows = Table.SelectRows(Normalized, each [event_id] <> null and [event_timestamp] <> null and [severity] <> null),
    Deduplicated = Table.Distinct(Table.Sort(ValidRows, {{"received_at", Order.Ascending}}), {"event_id"}),
    WithEventKey = Table.AddColumn(Deduplicated, "EventKey", each Number.FromText(Text.AfterDelimiter([event_id], "-")), Int64.Type),
    MergeSource = Table.NestedJoin(WithEventKey, {"source_product", "source_system"}, DimSourceProduct, {"SourceProduct", "SourceSystem"}, "Source", JoinKind.LeftOuter),
    ExpandSource = Table.ExpandTableColumn(MergeSource, "Source", {"SourceProductKey"}, {"SourceProductKey"}),
    MergeAsset = Table.NestedJoin(ExpandSource, {"asset_id"}, DimAsset, {"AssetId"}, "Asset", JoinKind.LeftOuter),
    ExpandAsset = Table.ExpandTableColumn(MergeAsset, "Asset", {"AssetKey"}, {"AssetKey"}),
    MergeRule = Table.NestedJoin(ExpandAsset, {"rule_id"}, DimDetectionRule, {"RuleId"}, "Rule", JoinKind.LeftOuter),
    ExpandRule = Table.ExpandTableColumn(MergeRule, "Rule", {"DetectionRuleKey"}, {"DetectionRuleKey"}),
    MergeSeverity = Table.NestedJoin(ExpandRule, {"severity"}, DimSeverity, {"Severity"}, "SeverityDim", JoinKind.LeftOuter),
    ExpandSeverity = Table.ExpandTableColumn(MergeSeverity, "SeverityDim", {"SeverityKey"}, {"SeverityKey"}),
    AddDateKey = Table.AddColumn(ExpandSeverity, "EventDateKey", each Number.FromText(Date.ToText(Date.From([event_timestamp]), "yyyyMMdd")), Int64.Type),
    AddTimeKey = Table.AddColumn(AddDateKey, "EventTimeKey", each Time.Hour(Time.From([event_timestamp])) * 100 + Number.IntegerDivide(Time.Minute(Time.From([event_timestamp])), 5) * 5, Int64.Type),
    AddCount = Table.AddColumn(AddTimeKey, "EventCount", each 1, Int64.Type),
    AddDelay = Table.AddColumn(AddCount, "IngestionDelaySeconds", each Duration.TotalSeconds([received_at] - [event_timestamp]), type number),
    AddDuplicateFlag = Table.AddColumn(AddDelay, "IsDuplicate", each false, type logical),
    AddRejectedFlag = Table.AddColumn(AddDuplicateFlag, "IsRejected", each false, type logical),
    Renamed = Table.RenameColumns(AddRejectedFlag, {{"event_id", "EventId"}, {"event_timestamp", "EventTimestampUTC"}, {"received_at", "ReceivedAtUTC"}, {"data_classification", "DataClassification"}}),
    Final = Table.SelectColumns(Renamed, {"EventKey", "EventId", "EventTimestampUTC", "ReceivedAtUTC", "EventDateKey", "EventTimeKey", "SourceProductKey", "AssetKey", "DetectionRuleKey", "SeverityKey", "EventCount", "IngestionDelaySeconds", "IsDuplicate", "IsRejected", "DataClassification"})
in
    Final
