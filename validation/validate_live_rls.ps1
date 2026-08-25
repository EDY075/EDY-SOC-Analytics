param(
    [string]$ExpectedWindowTitle = "EDY SOC Analytics",
    [int]$DesktopPid = 0,
    [ValidateSet("EffectiveUserName", "EphemeralCustomData")]
    [string]$IdentityMode = "EffectiveUserName"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

. (Join-Path $PSScriptRoot "resolve_powerbi_workspace.ps1")
$live = Resolve-PowerBIWorkspace -ExpectedWindowTitle $ExpectedWindowTitle -DesktopPid $DesktopPid
$desktop = $live.Desktop
$workspace = $live.Workspace
$port = $live.Port

$assemblyCandidates = @()
if ($desktop.Path) {
    $assemblyCandidates += Join-Path (Split-Path -Parent $desktop.Path) "Microsoft.PowerBI.AdomdClient.dll"
}
$assemblyCandidates += "C:\Program Files\Microsoft Power BI Desktop\bin\Microsoft.PowerBI.AdomdClient.dll"
$adomdAssembly = $assemblyCandidates |
    Where-Object { Test-Path -LiteralPath $_ } |
    Select-Object -First 1
if (-not $adomdAssembly) {
    throw "Microsoft.PowerBI.AdomdClient.dll não foi localizada; validação RLS não executada."
}
[void][Reflection.Assembly]::LoadFrom($adomdAssembly)

$bin = Split-Path -Parent $adomdAssembly
[void][Reflection.Assembly]::LoadFrom((Join-Path $bin "Microsoft.AnalysisServices.Server.Core.dll"))
[void][Reflection.Assembly]::LoadFrom((Join-Path $bin "Microsoft.AnalysisServices.Server.Tabular.dll"))

$validationRoleName = "__EDY_RLS_VALIDATION"
$validationRoleCreated = $false
$validationRoleFilter = $null

try {
if ($IdentityMode -eq "EphemeralCustomData") {
    $tomServer = [Microsoft.AnalysisServices.Tabular.Server]::new()
    try {
        $tomServer.Connect("Data Source=localhost:$port")
        $tomDatabase = $tomServer.Databases | Select-Object -First 1
        $tomModel = $tomDatabase.Model
        if ($tomModel.Roles.Contains($validationRoleName)) {
            throw "O role temporário de validação já existe; limpeza manual necessária antes do teste."
        }

        $productionRole = $tomModel.Roles["SOC_Analyst"]
        $productionPermission = $productionRole.TablePermissions["DimAnalyst"]
        $validationRoleFilter = $productionPermission.FilterExpression.Replace(
            "LOWER ( USERPRINCIPALNAME () )",
            "LOWER ( CUSTOMDATA () )"
        )
        if ($validationRoleFilter -eq $productionPermission.FilterExpression) {
            throw "Não foi possível derivar o role temporário a partir do filtro SOC_Analyst."
        }

        $validationRole = [Microsoft.AnalysisServices.Tabular.ModelRole]::new()
        $validationRole.Name = $validationRoleName
        $validationRole.ModelPermission = [Microsoft.AnalysisServices.Tabular.ModelPermission]::Read
        $validationPermission = [Microsoft.AnalysisServices.Tabular.TablePermission]::new()
        $validationPermission.Name = "DimAnalyst"
        $validationPermission.Table = $tomModel.Tables["DimAnalyst"]
        $validationPermission.FilterExpression = $validationRoleFilter
        $validationRole.TablePermissions.Add($validationPermission)
        $tomModel.Roles.Add($validationRole)
        [void]$tomModel.SaveChanges()
        $validationRoleCreated = $true
    }
    finally {
        if ($tomServer.Connected) {
            $tomServer.Disconnect()
        }
    }
}

$discovery = [Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new("Data Source=localhost:$port")
$discovery.Open()
try {
    $catalog = ($discovery.GetSchemaDataSet("DBSCHEMA_CATALOGS", $null).Tables[0] |
        Select-Object -First 1).CATALOG_NAME
}
finally {
    $discovery.Close()
}

function Invoke-RlsProbe([string]$Role, [string]$EffectiveUserName) {
    $identityProperty = if ($IdentityMode -eq "EphemeralCustomData") {
        "CustomData=$EffectiveUserName"
    }
    else {
        "EffectiveUserName=$EffectiveUserName"
    }
    $connectionString = "Data Source=localhost:$port;Initial Catalog=$catalog;Roles=$Role;$identityProperty"
    $connection = [Microsoft.AnalysisServices.AdomdClient.AdomdConnection]::new($connectionString)
    $connection.Open()
    try {
        $command = $connection.CreateCommand()
        $command.CommandText = @'
EVALUATE
ROW (
    "IncidentRows", COUNTROWS ( FactIncidents ),
    "MeasureIncidents", [Total de incidentes],
    "LifecycleRows", COUNTROWS ( FactIncidentLifecycle ),
    "MitreRows", COUNTROWS ( BridgeIncidentTechnique ),
    "SlaRows", COUNTROWS ( FactSLA ),
    "EventRows", COUNTROWS ( FactSecurityEvents ),
    "MeasureEvents", [Total de eventos],
    "AlertRows", COUNTROWS ( FactAlerts ),
    "MeasureAlerts", [Total de alertas],
    "VisibleTeams", CONCATENATEX ( VALUES ( DimAnalyst[Team] ), DimAnalyst[Team], "," )
)
'@
        $reader = $command.ExecuteReader()
        [void]$reader.Read()
        $probe = [ordered]@{
            incidentRows = [int]$reader.GetValue(0)
            measureIncidents = [int]$reader.GetValue(1)
            lifecycleRows = [int]$reader.GetValue(2)
            mitreRows = [int]$reader.GetValue(3)
            slaRows = [int]$reader.GetValue(4)
            eventRows = [int]$reader.GetValue(5)
            measureEvents = [int]$reader.GetValue(6)
            alertRows = [int]$reader.GetValue(7)
            measureAlerts = [int]$reader.GetValue(8)
            visibleTeams = [string]$reader.GetValue(9)
        }
        $reader.Close()
        return $probe
    }
    finally {
        $connection.Close()
    }
}

$analystTeamByKey = @{}
Import-Csv (Join-Path $root "data\reference\DimAnalyst.csv") | ForEach-Object {
    $analystTeamByKey[[string]$_.AnalystKey] = [string]$_.Team
}

$incidentsByTeam = @{}
$incidentTeamById = @{}
$incidentTeamByKey = @{}
$incidentRows = Import-Csv (Join-Path $root "data\expected\FactIncidents.csv")
foreach ($incident in $incidentRows) {
    $team = $analystTeamByKey[[string]$incident.AnalystKey]
    if ($team) {
        $incidentsByTeam[$team] = 1 + [int]($incidentsByTeam[$team])
        $incidentTeamById[[string]$incident.IncidentId] = $team
        $incidentTeamByKey[[string]$incident.IncidentKey] = $team
    }
}

function Get-RowsByIncidentTeam([string]$RelativePath) {
    $counts = @{}
    foreach ($row in (Import-Csv (Join-Path $root $RelativePath))) {
        $team = if ($row.PSObject.Properties.Name -contains "IncidentId") {
            $incidentTeamById[[string]$row.IncidentId]
        }
        else {
            $incidentTeamByKey[[string]$row.IncidentKey]
        }
        if ($team) {
            $counts[$team] = 1 + [int]($counts[$team])
        }
    }
    return ,$counts
}

$lifecycleByTeam = Get-RowsByIncidentTeam "data\expected\FactIncidentLifecycle.csv"
$mitreByTeam = Get-RowsByIncidentTeam "data\expected\BridgeIncidentTechnique.csv"
$slaByTeam = Get-RowsByIncidentTeam "data\expected\FactSLA.csv"
$lifecycleTotal = ($lifecycleByTeam.Values | Measure-Object -Sum).Sum
$mitreTotal = ($mitreByTeam.Values | Measure-Object -Sum).Sum
$slaTotal = ($slaByTeam.Values | Measure-Object -Sum).Sum
$eventTotal = @(Import-Csv (Join-Path $root "data\expected\FactSecurityEvents.csv")).Count
$alertTotal = @(Import-Csv (Join-Path $root "data\expected\FactAlerts.csv")).Count

$accessRows = Import-Csv (Join-Path $root "data\reference\SecurityAccess.csv")
$scenarios = @()
foreach ($access in $accessRows) {
    if ($access.RoleName -eq "SOC_Analyst") {
        $scenarios += [pscustomobject]@{
            role = "SOC_Analyst"
            connectionRole = if ($IdentityMode -eq "EphemeralCustomData") { $validationRoleName } else { "SOC_Analyst" }
            upn = $access.UPN
            expectedIncidents = [int]$incidentsByTeam[$access.Team]
            expectedLifecycle = [int]$lifecycleByTeam[$access.Team]
            expectedMitre = [int]$mitreByTeam[$access.Team]
            expectedSla = [int]$slaByTeam[$access.Team]
            expectedEvents = $eventTotal
            expectedAlerts = $alertTotal
            expectedTeam = $access.Team
        }
    }
}

$manager = $accessRows | Where-Object RoleName -eq "SOC_Manager" | Select-Object -First 1
$scenarios += [pscustomobject]@{
    role = "SOC_Manager"
    connectionRole = "SOC_Manager"
    upn = $manager.UPN
    expectedIncidents = $incidentRows.Count
    expectedLifecycle = [int]$lifecycleTotal
    expectedMitre = [int]$mitreTotal
    expectedSla = [int]$slaTotal
    expectedEvents = $eventTotal
    expectedAlerts = $alertTotal
    expectedTeam = $null
}
$scenarios += [pscustomobject]@{
    role = "SOC_Analyst"
    connectionRole = if ($IdentityMode -eq "EphemeralCustomData") { $validationRoleName } else { "SOC_Analyst" }
    upn = "unmapped.identity@example.invalid"
    expectedIncidents = 0
    expectedLifecycle = 0
    expectedMitre = 0
    expectedSla = 0
    expectedEvents = $eventTotal
    expectedAlerts = $alertTotal
    expectedTeam = $null
}

$results = @()
foreach ($scenario in $scenarios) {
    $actual = Invoke-RlsProbe -Role $scenario.connectionRole -EffectiveUserName $scenario.upn
    $visibleTeams = @($actual.visibleTeams -split ',' | Where-Object { $_ })
    $countMatches =
        $actual.incidentRows -eq $scenario.expectedIncidents -and
        $actual.measureIncidents -eq $scenario.expectedIncidents -and
        $actual.lifecycleRows -eq $scenario.expectedLifecycle -and
        $actual.mitreRows -eq $scenario.expectedMitre -and
        $actual.slaRows -eq $scenario.expectedSla -and
        $actual.eventRows -eq $scenario.expectedEvents -and
        $actual.measureEvents -eq $scenario.expectedEvents -and
        $actual.alertRows -eq $scenario.expectedAlerts -and
        $actual.measureAlerts -eq $scenario.expectedAlerts
    $scopeMatches = if ($scenario.expectedTeam) {
        $visibleTeams.Count -eq 1 -and $visibleTeams[0] -eq $scenario.expectedTeam
    }
    elseif ($scenario.role -eq "SOC_Analyst") {
        $visibleTeams.Count -eq 0
    }
    else {
        $true
    }

    $results += [ordered]@{
        role = $scenario.role
        effectiveUserName = $scenario.upn
        expectedIncidents = $scenario.expectedIncidents
        actualIncidents = $actual.incidentRows
        measureIncidents = $actual.measureIncidents
        expectedLifecycle = $scenario.expectedLifecycle
        actualLifecycle = $actual.lifecycleRows
        expectedMitre = $scenario.expectedMitre
        actualMitre = $actual.mitreRows
        expectedSla = $scenario.expectedSla
        actualSla = $actual.slaRows
        expectedEvents = $scenario.expectedEvents
        actualEvents = $actual.eventRows
        measureEvents = $actual.measureEvents
        expectedAlerts = $scenario.expectedAlerts
        actualAlerts = $actual.alertRows
        measureAlerts = $actual.measureAlerts
        visibleTeams = $visibleTeams
        passed = $countMatches -and $scopeMatches
    }
}

$failed = @($results | Where-Object { -not $_.passed })
$result = [ordered]@{
    status = if ($failed.Count -eq 0) { "passed" } else { "failed" }
    desktopPid = $desktop.Id
    catalog = $catalog
    identityMode = $IdentityMode
    productionRoleFilterParity = if ($IdentityMode -eq "EphemeralCustomData") {
        $validationRoleFilter.Replace("LOWER ( CUSTOMDATA () )", "LOWER ( USERPRINCIPALNAME () )") -eq
            ($tomModel.Roles["SOC_Analyst"].TablePermissions["DimAnalyst"].FilterExpression)
    }
    else {
        $true
    }
    scenarios = $results
}
$result | ConvertTo-Json -Depth 6
if ($failed.Count -gt 0) {
    throw "Validação RLS em memória falhou em $($failed.Count) cenário(s)."
}
}
finally {
    if ($validationRoleCreated) {
        $cleanupServer = [Microsoft.AnalysisServices.Tabular.Server]::new()
        try {
            $cleanupServer.Connect("Data Source=localhost:$port")
            $cleanupDatabase = $cleanupServer.Databases | Select-Object -First 1
            $cleanupRole = $cleanupDatabase.Model.Roles[$validationRoleName]
            if ($null -ne $cleanupRole) {
                [void]$cleanupDatabase.Model.Roles.Remove($cleanupRole)
                [void]$cleanupDatabase.Model.SaveChanges()
            }
        }
        finally {
            if ($cleanupServer.Connected) {
                $cleanupServer.Disconnect()
            }
        }
    }
}
