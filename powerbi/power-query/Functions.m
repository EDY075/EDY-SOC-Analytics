// fxCsv(relativePath as text) as table
(relativePath as text) as table =>
let
    NormalizedRoot = Text.TrimEnd(pProjectRoot, {"\\", "/"}),
    FullPath = NormalizedRoot & "\\" & Text.Replace(relativePath, "/", "\\"),
    Source = Csv.Document(
        File.Contents(FullPath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Headers

// fxNormalizeSeverity(value as nullable text) as nullable text
(value as nullable text) as nullable text =>
let
    Clean = if value = null then null else Text.Lower(Text.Trim(value)),
    Result =
        if List.Contains({"info", "informational"}, Clean) then "Informational"
        else if List.Contains({"low", "baixo"}, Clean) then "Low"
        else if List.Contains({"medium", "medio", "médio"}, Clean) then "Medium"
        else if List.Contains({"high", "alto"}, Clean) then "High"
        else if List.Contains({"critical", "critico", "crítico"}, Clean) then "Critical"
        else null
in
    Result

// fxNormalizeStatus(value as nullable text) as nullable text
(value as nullable text) as nullable text =>
let
    Clean = if value = null then null else Text.Lower(Text.Trim(value)),
    Result =
        if List.Contains({"new", "novo"}, Clean) then "New"
        else if List.Contains({"active", "ativo"}, Clean) then "Active"
        else if List.Contains({"contained", "contido"}, Clean) then "Contained"
        else if List.Contains({"resolved", "resolvido"}, Clean) then "Resolved"
        else if List.Contains({"closed", "fechado"}, Clean) then "Closed"
        else null
in
    Result

