[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments=$true)][string[]]$RemainingArgs)
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
Write-Progress -Activity 'run-tests' -Status 'Starting' -PercentComplete 0
$Python=Get-Command python3 -ErrorAction SilentlyContinue
$Prefix=@()
if(-not $Python){$Python=Get-Command python -ErrorAction SilentlyContinue}
if(-not $Python){$Python=Get-Command py -ErrorAction SilentlyContinue; if($Python){$Prefix=@('-3')}}
if(-not $Python){throw 'Python 3 was not found on PATH.'}
& $Python.Source @Prefix (Join-Path $Root 'tools\run_tests.py') @RemainingArgs
$Code=$LASTEXITCODE
Write-Progress -Activity 'run-tests' -Status ($(if($Code -eq 0){'Passed'}else{'Failed'})) -PercentComplete 100 -Completed
exit $Code
