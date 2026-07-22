[CmdletBinding()]
param([Parameter(ValueFromRemainingArguments=$true)][string[]]$RemainingArgs)
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
Write-Progress -Activity 'validate-suite' -Status 'Starting' -PercentComplete 0
$Prefix=@()
$Python=$null
if($env:VIRTUAL_ENV){
  $VenvPython=Join-Path $env:VIRTUAL_ENV 'Scripts\python.exe'
  if(Test-Path -LiteralPath $VenvPython){$Python=[pscustomobject]@{Source=$VenvPython}}
}
if(-not $Python){$Python=Get-Command python3 -ErrorAction SilentlyContinue}
if(-not $Python){$Python=Get-Command python -ErrorAction SilentlyContinue}
if(-not $Python){$Python=Get-Command py -ErrorAction SilentlyContinue; if($Python){$Prefix=@('-3')}}
if(-not $Python){throw 'Python 3 was not found on PATH.'}
& $Python.Source @Prefix (Join-Path $Root 'tools\validate_suite.py') @RemainingArgs
$Code=$LASTEXITCODE
Write-Progress -Activity 'validate-suite' -Status ($(if($Code -eq 0){'Passed'}else{'Failed'})) -PercentComplete 100 -Completed
exit $Code
