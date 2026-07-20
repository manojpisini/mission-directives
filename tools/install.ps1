[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ProjectPath,

    [switch]$Replace,
    [switch]$DryRun,
    [switch]$NoTui
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$InstallerPath = Join-Path $PSScriptRoot 'install.py'
$VersionPath = Join-Path $PSScriptRoot 'VERSION'
$SuiteVersion = if (Test-Path -LiteralPath $VersionPath) {
    (Get-Content -LiteralPath $VersionPath -Raw).Trim()
} else {
    'unknown'
}

Write-Host ''
Write-Host ('[START] Mission Directives {0} installer' -f $SuiteVersion) -ForegroundColor Cyan
Write-Progress -Activity 'Mission Directives installer' -Status 'Resolving Python 3' -PercentComplete 2

$PythonCommand = Get-Command python3 -ErrorAction SilentlyContinue
$PythonPrefix = @()
if (-not $PythonCommand) {
    $PythonCommand = Get-Command python -ErrorAction SilentlyContinue
}
if (-not $PythonCommand) {
    $PythonCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($PythonCommand) {
        $PythonPrefix = @('-3')
    }
}
if (-not $PythonCommand) {
    Write-Progress -Activity 'Mission Directives installer' -Completed
    Write-Host '[FAILURE] Python 3 was not found on PATH.' -ForegroundColor Red
    exit 127
}

$InvocationArgs = @()
$InvocationArgs += $PythonPrefix
$InvocationArgs += $InstallerPath
if ($ProjectPath) {
    $InvocationArgs += $ProjectPath
}
if ($Replace) {
    $InvocationArgs += '--replace'
}
if ($DryRun) {
    $InvocationArgs += '--dry-run'
}
if ($NoTui) {
    $InvocationArgs += '--no-tui'
}

Write-Progress -Activity 'Mission Directives installer' -Status 'Running secure Python installer' -PercentComplete 5
try {
    & $PythonCommand.Source @InvocationArgs
    $ExitCode = $LASTEXITCODE
} catch {
    Write-Progress -Activity 'Mission Directives installer' -Completed
    Write-Host ('[FAILURE] Mission Directives {0} installer could not start.' -f $SuiteVersion) -ForegroundColor Red
    Write-Host ('Reason: {0}' -f $_.Exception.Message) -ForegroundColor Red
    exit 1
}

Write-Progress -Activity 'Mission Directives installer' -Completed
if ($ExitCode -eq 0) {
    if ($DryRun) {
        Write-Host ('[SUCCESS] Mission Directives {0} installation preview completed.' -f $SuiteVersion) -ForegroundColor Green
    } else {
        Write-Host ('[SUCCESS] Mission Directives {0} installed successfully.' -f $SuiteVersion) -ForegroundColor Green
    }
} else {
    Write-Host ('[FAILURE] Mission Directives {0} installer exited with code {1}.' -f $SuiteVersion, $ExitCode) -ForegroundColor Red
}
Write-Host ''
exit $ExitCode
