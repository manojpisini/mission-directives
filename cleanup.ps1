[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$ProjectPath,

    [switch]$DryRun,
    [switch]$Yes,
    [string]$ApprovalToken,
    [string]$Receipt,
    [switch]$NoTui
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$CleanupPath = Join-Path $PSScriptRoot 'cleanup.py'
$VersionPath = Join-Path $PSScriptRoot 'VERSION'
$SuiteVersion = if (Test-Path -LiteralPath $VersionPath) {
    (Get-Content -LiteralPath $VersionPath -Raw).Trim()
} else {
    'unknown'
}

Write-Host ''
Write-Host ('[START] Mission Directives {0} cleanup' -f $SuiteVersion) -ForegroundColor Cyan
Write-Progress -Activity 'Mission Directives cleanup' -Status 'Resolving Python 3' -PercentComplete 2

$PythonCommand = Get-Command python3 -ErrorAction SilentlyContinue
$PythonPrefix = @()
if (-not $PythonCommand) { $PythonCommand = Get-Command python -ErrorAction SilentlyContinue }
if (-not $PythonCommand) {
    $PythonCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($PythonCommand) { $PythonPrefix = @('-3') }
}
if (-not $PythonCommand) {
    Write-Progress -Activity 'Mission Directives cleanup' -Completed
    Write-Host '[FAILURE] Python 3 was not found on PATH.' -ForegroundColor Red
    exit 127
}

$InvocationArgs = @()
$InvocationArgs += $PythonPrefix
$InvocationArgs += $CleanupPath
if ($ProjectPath) { $InvocationArgs += $ProjectPath }
if ($DryRun) { $InvocationArgs += '--dry-run' }
if ($Yes) { $InvocationArgs += '--yes' }
if ($ApprovalToken) { $InvocationArgs += @('--approval-token', $ApprovalToken) }
if ($Receipt) { $InvocationArgs += @('--receipt', $Receipt) }
if ($NoTui) { $InvocationArgs += '--no-tui' }

Write-Progress -Activity 'Mission Directives cleanup' -Status 'Running secure Python cleanup' -PercentComplete 5
try {
    & $PythonCommand.Source @InvocationArgs
    $ExitCode = $LASTEXITCODE
} catch {
    Write-Progress -Activity 'Mission Directives cleanup' -Completed
    Write-Host ('[FAILURE] Mission Directives {0} cleanup could not start.' -f $SuiteVersion) -ForegroundColor Red
    Write-Host ('Reason: {0}' -f $_.Exception.Message) -ForegroundColor Red
    exit 1
}

Write-Progress -Activity 'Mission Directives cleanup' -Completed
if ($ExitCode -eq 0) {
    if ($DryRun) {
        Write-Host ('[SUCCESS] Mission Directives {0} cleanup preview completed.' -f $SuiteVersion) -ForegroundColor Green
    } else {
        Write-Host ('[SUCCESS] Mission Directives {0} cleanup completed successfully.' -f $SuiteVersion) -ForegroundColor Green
    }
} else {
    Write-Host ('[FAILURE] Mission Directives {0} cleanup exited with code {1}.' -f $SuiteVersion, $ExitCode) -ForegroundColor Red
}
Write-Host ''
exit $ExitCode
