param(
    [string]$ExpectedWindowTitle = "EDY SOC Analytics",
    [int]$DesktopPid = 0
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$resultsDir = Join-Path $PSScriptRoot "results"
New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null

. (Join-Path $PSScriptRoot "resolve_powerbi_workspace.ps1")
$live = Resolve-PowerBIWorkspace -ExpectedWindowTitle $ExpectedWindowTitle -DesktopPid $DesktopPid
$desktop = $live.Desktop

$binCandidates = @()
if ($desktop.Path) {
    $binCandidates += Split-Path -Parent $desktop.Path
}
$binCandidates += "C:\Program Files\Microsoft Power BI Desktop\bin"
$bin = $binCandidates |
    Where-Object { Test-Path -LiteralPath (Join-Path $_ "Microsoft.AnalysisServices.Server.Tabular.dll") } |
    Select-Object -First 1
if (-not $bin) {
    throw "Assemblies TOM do Power BI Desktop não foram localizadas."
}

[void][Reflection.Assembly]::LoadFrom((Join-Path $bin "Microsoft.AnalysisServices.Server.Core.dll"))
[void][Reflection.Assembly]::LoadFrom((Join-Path $bin "Microsoft.AnalysisServices.Server.Tabular.dll"))

$orderedTables = @(
    "DimAnalyst",
    "DimAsset",
    "DimAttackTactic",
    "DimAttackTechnique",
    "DimClassification",
    "DimDate",
    "DimDetectionRule",
    "DimSeverity",
    "DimSLA",
    "DimSourceProduct",
    "DimStatus",
    "DimTime",
    "SecurityAccess",
    "BridgeIncidentTechnique",
    "FactIncidentLifecycle",
    "FactSLA",
    "FactSecurityEvents",
    "FactAlerts",
    "FactIncidents",
    "DQ_RejectedRows"
)

$server = [Microsoft.AnalysisServices.Tabular.Server]::new()
$measurements = @()
$failedTable = $null
$failureMessage = $null
$started = Get-Date

try {
    $server.Connect("Data Source=localhost:$($live.Port)")
    $database = $server.Databases | Select-Object -First 1
    if ($null -eq $database) {
        throw "Catálogo do modelo não encontrado."
    }

    foreach ($tableName in $orderedTables) {
        $table = $database.Model.Tables[$tableName]
        if ($null -eq $table) {
            throw "Tabela esperada não encontrada: $tableName"
        }

        $stopwatch = [Diagnostics.Stopwatch]::StartNew()
        try {
            $table.RequestRefresh([Microsoft.AnalysisServices.Tabular.RefreshType]::Full)
            $impact = $database.Model.SaveChanges()
            $stopwatch.Stop()
            $measurements += [ordered]@{
                table = $tableName
                elapsedSeconds = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)
                affectedObjects = $impact.Impact.Count
                status = "passed"
            }
            Write-Host "refreshed $tableName in $([math]::Round($stopwatch.Elapsed.TotalSeconds, 2))s"
        }
        catch {
            $stopwatch.Stop()
            $failedTable = $tableName
            $failureMessage = $_.Exception.Message
            $measurements += [ordered]@{
                table = $tableName
                elapsedSeconds = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)
                affectedObjects = 0
                status = "failed"
            }
            break
        }
    }

    $result = [ordered]@{
        status = if ($failedTable) { "failed" } else { "passed" }
        desktopPid = $desktop.Id
        catalog = $database.Name
        startedAt = $started.ToString("o")
        completedAt = (Get-Date).ToString("o")
        totalSeconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 2)
        tables = $measurements
        failedTable = $failedTable
        failure = $failureMessage
    }

    $output = Join-Path $resultsDir "refresh.json"
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $output -Encoding utf8
    $result | ConvertTo-Json -Depth 8

    if ($failedTable) {
        throw "Refresh falhou em '$failedTable'."
    }
}
finally {
    if ($server.Connected) {
        $server.Disconnect()
    }
}
