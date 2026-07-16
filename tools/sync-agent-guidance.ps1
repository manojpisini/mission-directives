[CmdletBinding()]
param(
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$SuiteRoot = (Split-Path -Parent $PSScriptRoot),
    [string[]]$AgentFile,
    [switch]$DryRun,
    [switch]$Remove,
    [switch]$ShowDiff,
    [string]$Receipt = ".prompt_suite/agent-guidance-receipt.json"
)
$ErrorActionPreference='Stop'
Write-Progress -Activity 'sync-agent-guidance' -Status 'Starting' -PercentComplete 0
$Python=Get-Command python3 -ErrorAction SilentlyContinue
$Prefix=@()
if(-not $Python){$Python=Get-Command python -ErrorAction SilentlyContinue}
if(-not $Python){$Python=Get-Command py -ErrorAction SilentlyContinue; if($Python){$Prefix=@('-3')}}
if(-not $Python){throw 'Python 3 was not found on PATH.'}
$Script=Join-Path $PSScriptRoot 'sync_agent_guidance.py'
$ArgsList=@($Script,'--project-root',$ProjectRoot,'--suite-root',$SuiteRoot)
foreach($File in $AgentFile){$ArgsList+=@('--agent-file',$File)}
if($DryRun){$ArgsList+='--dry-run'}
if($Remove){$ArgsList+='--remove'}
if($ShowDiff){$ArgsList+='--show-diff'}
if($Receipt){$ArgsList+=@('--receipt',$Receipt)}
& $Python.Source @Prefix @ArgsList
$Code=$LASTEXITCODE
Write-Progress -Activity 'sync-agent-guidance' -Status ($(if($Code -eq 0){'Passed'}else{'Failed'})) -PercentComplete 100 -Completed
exit $Code
