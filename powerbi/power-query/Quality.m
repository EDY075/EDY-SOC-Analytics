let
    Source = fxCsv("data/raw/security_events_raw.csv"),
    WithIssue = Table.AddColumn(Source, "QualityIssue", each
        if [event_id] = null or Text.Trim([event_id]) = "" then "Missing event_id"
        else if (try DateTimeZone.FromText([event_timestamp]))[HasError] then "Invalid event_timestamp"
        else if fxNormalizeSeverity([severity]) = null then "Invalid severity"
        else null, type text),
    InvalidRows = Table.SelectRows(WithIssue, each [QualityIssue] <> null),
    SafeProjection = Table.SelectColumns(InvalidRows, {"event_id", "source_product", "QualityIssue", "data_classification"})
in
    SafeProjection
