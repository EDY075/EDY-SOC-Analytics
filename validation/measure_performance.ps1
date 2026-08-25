param(
    [string]$ExpectedWindowTitle = "EDY SOC Analytics",
    [int]$WarmIterations = 5
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$resultsDir = Join-Path $PSScriptRoot "results"
New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null

. (Join-Path $PSScriptRoot "resolve_powerbi_workspace.ps1")
$live = Resolve-PowerBIWorkspace -ExpectedWindowTitle $ExpectedWindowTitle
$desktop = $live.Desktop
$workspace = $live.Workspace
$port = $live.Port

$bin = "C:\Program Files\Microsoft Power BI Desktop\bin"
[void][Reflection.Assembly]::LoadFrom((Join-Path $bin "Microsoft.PowerBI.AdomdClient.dll"))
$connection = [Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=localhost:$port")
$connection.Open()
$catalog = ($connection.GetSchemaDataSet("DBSCHEMA_CATALOGS", $null).Tables[0] | Select-Object -First 1).CATALOG_NAME
$connection.ChangeDatabase($catalog)

$queries = [ordered]@{
    CommandCenter = @'
EVALUATE
ROW (
    "Active", [Incidentes ativos],
    "Critical", [Incidentes críticos ativos],
    "Backlog", [Backlog],
    "SLA", [Cumprimento de SLA],
    "MTTD", [MTTD (min)],
    "MTTR", [MTTR resolução (min)]
)
'@
    MonthlyTrend = @'
EVALUATE
SUMMARIZECOLUMNS (
    DimDate[YearMonth],
    "Alerts", [Total de alertas],
    "Incidents", [Total de incidentes]
)
'@
    MitreCoverage = @'
EVALUATE
TOPN (
    20,
    SUMMARIZECOLUMNS (
        DimAttackTechnique[TechniqueId],
        DimAttackTechnique[TechniqueName],
        "Incidents", [Total de incidentes]
    ),
    [Incidents], DESC
)
'@
    DetectionRules = @'
EVALUATE
TOPN (
    20,
    SUMMARIZECOLUMNS (
        DimDetectionRule[RuleName],
        "Alerts", [Total de alertas],
        "FalsePositiveRate", [Taxa de falsos positivos],
        "Conversion", [Taxa regra para incidente]
    ),
    [Alerts], DESC
)
'@
    IncidentDetail = @'
EVALUATE
TOPN (
    100,
    SUMMARIZECOLUMNS (
        FactIncidents[IncidentId],
        DimSeverity[SeverityPT],
        DimStatus[StatusPT],
        DimAsset[AssetLabel],
        "RiskScore", MAX ( FactIncidents[RiskScore] )
    ),
    [RiskScore], DESC
)
'@
}

function Invoke-DaxTimed([string]$Dax) {
    $command = $connection.CreateCommand()
    $command.CommandText = $Dax
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $reader = $command.ExecuteReader()
    $rows = 0
    while ($reader.Read()) { $rows++ }
    $reader.Close()
    $stopwatch.Stop()
    [pscustomobject]@{ milliseconds = [math]::Round($stopwatch.Elapsed.TotalMilliseconds, 2); rows = $rows }
}

$measurements = @()
foreach ($entry in $queries.GetEnumerator()) {
    $cold = Invoke-DaxTimed $entry.Value
    $warm = @()
    for ($i = 1; $i -le $WarmIterations; $i++) {
        $warm += (Invoke-DaxTimed $entry.Value).milliseconds
    }
    $sorted = @($warm | Sort-Object)
    $p50Index = [math]::Floor(($sorted.Count - 1) * 0.50)
    $p95Index = [math]::Ceiling(($sorted.Count - 1) * 0.95)
    $measurements += [ordered]@{
        query = $entry.Key
        returnedRows = $cold.rows
        coldMs = $cold.milliseconds
        warmRunsMs = $warm
        warmP50Ms = $sorted[$p50Index]
        warmP95Ms = $sorted[$p95Index]
        warmMaxMs = ($sorted | Measure-Object -Maximum).Maximum
        withinWarmBudget = $sorted[$p95Index] -lt 2000
    }
}
$connection.Close()

$result = [ordered]@{
    measuredAt = (Get-Date).ToString("o")
    hostScope = "Local Power BI Desktop; DAX engine timings only"
    desktopPid = $desktop.Id
    warmBudgetMs = 2000
    iterations = $WarmIterations
    measurements = $measurements
    status = if (@($measurements | Where-Object { -not $_.withinWarmBudget }).Count -eq 0) { "passed" } else { "failed" }
}
$output = Join-Path $resultsDir "performance.json"
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $output -Encoding utf8
$result | ConvertTo-Json -Depth 8
if ($result.status -ne "passed") {
    throw "Uma ou mais consultas excederam o orçamento aquecido de 2.000 ms."
}
