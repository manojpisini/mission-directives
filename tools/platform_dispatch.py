#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, platform, shutil, subprocess, time
from pathlib import Path
from telemetry import append_event
from tui import TUI
ROOT=Path(__file__).resolve().parents[1]
PAIRS={'add-prompt':'add-prompt','cleanup-project':'cleanup','install-skill':'install_skill_dual','register-local-skill':'register_local_skill_dual','sync-agent-guidance':'sync-agent-guidance','validate':'validate-suite','test':'run-tests','suite':'run-suite'}
ROOT_WRAPPERS={'cleanup-project'}


def _powershell()->str:
    for candidate in ('pwsh','powershell'):
        found=shutil.which(candidate)
        if found: return found
    raise RuntimeError('PowerShell was not found on PATH')


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('tool',choices=sorted(PAIRS)); ap.add_argument('args',nargs=argparse.REMAINDER); a=ap.parse_args()
    sysname=platform.system().lower(); stem=PAIRS[a.tool]
    try:
        wrapper_root = ROOT if a.tool in ROOT_WRAPPERS else ROOT/'tools'
        if sysname=='windows': cmd=[_powershell(),'-NoProfile','-File',str(wrapper_root/f'{stem}.ps1'),*a.args]
        else: cmd=['bash',str(wrapper_root/f'{stem}.sh'),*a.args]
        tui=TUI(f'MD {a.tool}',total=2); tui.start(); tui.step('platform selected')
        start=time.perf_counter(); proc=subprocess.run(cmd,cwd=ROOT); duration=int((time.perf_counter()-start)*1000)
        tui.step('command finished'); tui.finish('PASS' if proc.returncode==0 else 'FAIL')
        safe_context={'selected_platform':sysname,'tool':a.tool,'wrapper':Path(cmd[0]).name,'arg_count':len(a.args)}
        payload={'status':'pass' if proc.returncode==0 else 'fail','platform':sysname,'tool':a.tool,'arg_count':len(a.args),'exit_code':proc.returncode}
        try:
            event=append_event('tool','platform_dispatch','pass' if proc.returncode==0 else 'fail',duration_ms=duration,tool='platform_dispatch.py',context=safe_context)
            payload['log_file']=event['log_file']
        except Exception as telemetry_exc:
            payload['telemetry_warning']=str(telemetry_exc)
        print(json.dumps(payload,indent=2)); return proc.returncode
    except Exception as exc:
        payload={'status':'fail','platform':sysname,'tool':a.tool,'error':str(exc)}
        try:
            event=append_event('tool','platform_dispatch','fail',tool='platform_dispatch.py',context={'selected_platform':sysname,'tool':a.tool,'arg_count':len(a.args)},error=str(exc))
            payload['log_file']=event['log_file']
        except Exception as telemetry_exc:
            payload['telemetry_warning']=str(telemetry_exc)
        print(json.dumps(payload,indent=2)); return 1
if __name__=='__main__': raise SystemExit(main())
