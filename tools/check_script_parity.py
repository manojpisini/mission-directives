#!/usr/bin/env python3
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main():
 tool_stems={p.stem for p in (ROOT/'tools').glob('*.sh')}|{p.stem for p in (ROOT/'tools').glob('*.ps1')}; errors=[]; pairs=[]
 entries=[(stem,ROOT/'tools') for stem in sorted(tool_stems)]+[(stem,ROOT) for stem in ('cleanup','install')]
 for stem,base in entries:
  sh=base/f'{stem}.sh'; ps=base/f'{stem}.ps1'
  if sh.exists() or ps.exists():
   if not sh.exists(): errors.append(f'missing Bash equivalent: {stem}.sh')
   if not ps.exists(): errors.append(f'missing PowerShell equivalent: {stem}.ps1')
   pairs.append({'tool':stem,'bash':sh.exists(),'powershell':ps.exists()})
 print(json.dumps({'status':'pass' if not errors else 'fail','pairs':pairs,'errors':errors},indent=2)); return 1 if errors else 0
if __name__=='__main__': raise SystemExit(main())
