// Pattern used for every reference dimension. Replace FileName and TypeMap per query.
let
    Source = fxCsv("data/reference/DimAsset.csv"),
    Selected = Table.SelectColumns(Source, {"AssetKey", "AssetId", "AssetLabel", "AssetType", "BusinessUnit", "Environment", "Criticality", "NetworkAddress", "IsSynthetic"}),
    Typed = Table.TransformColumnTypes(Selected, {
        {"AssetKey", Int64.Type}, {"AssetId", type text}, {"AssetLabel", type text},
        {"AssetType", type text}, {"BusinessUnit", type text}, {"Environment", type text},
        {"Criticality", Int64.Type}, {"NetworkAddress", type text}, {"IsSynthetic", type logical}
    }),
    Validated = Table.SelectRows(Typed, each [AssetKey] > 0 and [AssetId] <> null)
in
    Validated

