function Resolve-PowerBIWorkspace {
    param(
        [string]$ExpectedWindowTitle = "EDY SOC Analytics"
    )

    $desktops = @(Get-Process -Name PBIDesktop -ErrorAction SilentlyContinue)
    $desktop = $desktops |
        Where-Object MainWindowTitle -eq $ExpectedWindowTitle |
        Select-Object -First 1

    if ($null -eq $desktop -and $desktops.Count -eq 1) {
        $desktop = $desktops[0]
        Write-Warning "MainWindowTitle não está disponível; usando a única instância PBIDesktop ativa (PID mascarado nos relatórios)."
    }
    if ($null -eq $desktop) {
        throw "Não foi possível identificar com segurança uma única instância do Power BI Desktop para '$ExpectedWindowTitle'."
    }

    $workspace = $null
    try {
        $engine = Get-CimInstance Win32_Process -Filter "Name='msmdsrv.exe'" -ErrorAction Stop |
            Where-Object ParentProcessId -eq $desktop.Id |
            Select-Object -First 1
        if ($null -ne $engine -and $engine.CommandLine -match '-s\s+"([^"]+\\Data)"') {
            $workspace = $Matches[1]
        }
    }
    catch {
        Write-Warning "WMI não está disponível; procurando o único workspace Analysis Services ativo."
    }

    if (-not $workspace) {
        $engines = @(Get-Process -Name msmdsrv -ErrorAction SilentlyContinue)
        if ($engines.Count -ne 1) {
            throw "Não foi possível associar com segurança o engine Analysis Services ao Power BI Desktop."
        }

        $workspaceRoot = Join-Path $env:LOCALAPPDATA "Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"
        $portFiles = @(
            Get-ChildItem -LiteralPath $workspaceRoot -Recurse -Filter "msmdsrv.port.txt" -ErrorAction SilentlyContinue |
                Where-Object LastWriteTime -ge $desktop.StartTime.AddMinutes(-2)
        )
        if ($portFiles.Count -ne 1) {
            throw "Foi encontrado um número ambíguo de workspaces Analysis Services ativos: $($portFiles.Count)."
        }
        $workspace = $portFiles[0].Directory.FullName
    }

    $portFile = Join-Path $workspace "msmdsrv.port.txt"
    $port = [regex]::Replace((Get-Content -LiteralPath $portFile -Raw), '\D', '')
    if (-not $port) {
        throw "Porta local do modelo não encontrada."
    }

    [PSCustomObject]@{
        Desktop = $desktop
        Workspace = $workspace
        Port = $port
    }
}
