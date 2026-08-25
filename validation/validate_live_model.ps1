param(
    [string]$ExpectedWindowTitle = "EDY SOC Analytics"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$manifest = Get-Content -LiteralPath (Join-Path $root "data\dataset_manifest.json") -Raw | ConvertFrom-Json

$desktop = Get-Process -Name PBIDesktop |
    Where-Object MainWindowTitle -eq $ExpectedWindowTitle |
    Select-Object -First 1
if ($null -eq $desktop) {
    throw "Power BI Desktop com o projeto '$ExpectedWindowTitle' não está aberto."
}

$engine = Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" |
    Where-Object ParentProcessId -eq $desktop.Id |
    Select-Object -First 1
if ($null -eq $engine) {
    throw "Engine Analysis Services filho do Power BI não encontrado."
}

if ($engine.CommandLine -notmatch '-s\s+"([^"]+\\Data)"') {
    throw "Workspace do modelo não pôde ser resolvido."
}
$workspace = $Matches[1]
$portText = Get-Content -LiteralPath (Join-Path $workspace "msmdsrv.port.txt") -Raw
$port = [regex]::Replace($portText, '\D', '')
if (-not $port) {
    throw "Porta local do modelo não encontrada."
}

$bin = "C:\Program Files\Microsoft Power BI Desktop\bin"
[void][Reflection.Assembly]::LoadFrom((Join-Path $bin "Microsoft.PowerBI.AdomdClient.dll"))
$connection = [Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=localhost:$port")
$connection.Open()
$catalog = ($connection.GetSchemaDataSet("DBSCHEMA_CATALOGS", $null).Tables[0] | Select-Object -First 1).CATALOG_NAME
$connection.ChangeDatabase($catalog)

$command = $connection.CreateCommand()
$command.CommandText = @'
EVALUATE
ROW (
    "EventRows", COUNTROWS ( FactSecurityEvents ),
    "MeasureEvents", [Total de eventos],
    "AlertRows", COUNTROWS ( FactAlerts ),
    "MeasureAlerts", [Total de alertas],
    "IncidentRows", COUNTROWS ( FactIncidents ),
    "MeasureIncidents", [Total de incidentes],
    "LifecycleRows", COUNTROWS ( FactIncidentLifecycle ),
    "BridgeRows", COUNTROWS ( BridgeIncidentTechnique ),
    "SLARows", COUNTROWS ( FactSLA ),
    "UnknownAssetEvents", CALCULATE ( COUNTROWS ( FactSecurityEvents ), DimAsset[AssetKey] = 0 ),
    "UnknownAnalystIncidents", CALCULATE ( COUNTROWS ( FactIncidents ), DimAnalyst[AnalystKey] = 0 ),
    "RejectedRows", [Registros rejeitados]
)
'@
$reader = $command.ExecuteReader()
[void]$reader.Read()
$actual = @{}
for ($index = 0; $index -lt $reader.FieldCount; $index++) {
    $actual[$reader.GetName($index).Trim('[', ']')] = $reader.GetValue($index)
}
$reader.Close()

$expectedEvents = $manifest.counts.'expected/FactSecurityEvents.csv'
$expectedAlerts = $manifest.counts.'expected/FactAlerts.csv'
$expectedIncidents = $manifest.counts.'expected/FactIncidents.csv'
$expectedLifecycle = $manifest.counts.'expected/FactIncidentLifecycle.csv'
$expectedBridge = $manifest.counts.'expected/BridgeIncidentTechnique.csv'
$expectedSla = $manifest.counts.'expected/FactSLA.csv'
$expectedUnknownAssets = (Import-Csv (Join-Path $root "data\expected\FactSecurityEvents.csv") | Where-Object AssetKey -eq '0').Count
$expectedUnknownAnalysts = (Import-Csv (Join-Path $root "data\expected\FactIncidents.csv") | Where-Object AnalystKey -eq '0').Count

$assertions = [ordered]@{
    EventRows = $actual.EventRows -eq $expectedEvents
    MeasureEvents = $actual.MeasureEvents -eq $expectedEvents
    AlertRows = $actual.AlertRows -eq $expectedAlerts
    MeasureAlerts = $actual.MeasureAlerts -eq $expectedAlerts
    IncidentRows = $actual.IncidentRows -eq $expectedIncidents
    MeasureIncidents = $actual.MeasureIncidents -eq $expectedIncidents
    LifecycleRows = $actual.LifecycleRows -eq $expectedLifecycle
    BridgeRows = $actual.BridgeRows -eq $expectedBridge
    SLARows = $actual.SLARows -eq $expectedSla
    UnknownAssetEvents = $actual.UnknownAssetEvents -eq $expectedUnknownAssets
    UnknownAnalystIncidents = $actual.UnknownAnalystIncidents -eq $expectedUnknownAnalysts
    RejectedRows = $actual.RejectedRows -eq 0
}

$mitre = $connection.CreateCommand()
$mitre.CommandText = @'
EVALUATE
TOPN (
    1,
    SUMMARIZECOLUMNS (
        DimAttackTechnique[TechniqueId],
        "BridgeRows", COUNTROWS ( BridgeIncidentTechnique ),
        "Incidents", [Total de incidentes]
    ),
    [BridgeRows], DESC
)
'@
$mitreReader = $mitre.ExecuteReader()
[void]$mitreReader.Read()
$mitreTechnique = $mitreReader.GetValue(0)
$mitreBridgeRows = [int]$mitreReader.GetValue(1)
$mitreIncidents = [int]$mitreReader.GetValue(2)
$mitreReader.Close()
$connection.Close()
$assertions.MitreFilter = $mitreBridgeRows -gt 0 -and $mitreIncidents -eq $mitreBridgeRows -and $mitreIncidents -lt $expectedIncidents

$failed = @($assertions.GetEnumerator() | Where-Object Value -ne $true)
$result = [ordered]@{
    status = if ($failed.Count -eq 0) { "passed" } else { "failed" }
    assertions = $assertions
    actual = $actual
    mitreProbe = [ordered]@{
        technique = $mitreTechnique
        bridgeRows = $mitreBridgeRows
        filteredIncidents = $mitreIncidents
    }
}
$result | ConvertTo-Json -Depth 5
if ($failed.Count -gt 0) {
    throw "Validação do modelo em memória falhou: $($failed.Name -join ', ')"
}
