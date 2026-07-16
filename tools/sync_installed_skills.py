#!/usr/bin/env python3
"""Scan all supported global skill directories into a runtime-only inventory."""
from __future__ import annotations
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import argparse, json, datetime
try:
    from security_utils import atomic_write_json, ensure_no_symlink_components, safe_child, validate_identifier
except ImportError:
    from tools.security_utils import atomic_write_json, ensure_no_symlink_components, safe_child, validate_identifier
from agent_paths import all_default_destinations
ROOT=Path(__file__).resolve().parents[1]

def main()->int:
    defaults=all_default_destinations()
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--agents',default=str(defaults['agents']))
    ap.add_argument('--claude',default=str(defaults['claude-code']))
    ap.add_argument('--opencode',default=str(defaults['opencode']))
    a=ap.parse_args()
    roots=[('global_agents',Path(a.agents)),('claude_code_global',Path(a.claude)),('opencode_global',Path(a.opencode))]
    rows={}
    observed=[]
    for application,base in roots:
        base=ensure_no_symlink_components(base)
        observed.append({'application':application,'logical_source':application,'resolved_path':str(base),'exists':base.exists()})
        if not base.exists(): continue
        if not base.is_dir(): raise ValueError(f'Skill root is not a directory: {base}')
        for skill_dir in sorted(base.iterdir()):
            if skill_dir.is_symlink():
                raise ValueError(f'Symlinked skill directory is not allowed: {skill_dir}')
            if skill_dir.is_dir():
                skill_id=validate_identifier(skill_dir.name,kind='skill')
                skill_md=ensure_no_symlink_components(skill_dir/'SKILL.md')
                if skill_md.is_file():
                    row=rows.setdefault(skill_id,{'skill_id':skill_id,'locations':[]})
                    row['locations'].append({'kind':application,'path':str(skill_dir)})
    out={
        'snapshot_type':'filesystem_scan',
        'observed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'observed_locations':observed,
        'skill_count':len(rows),
        'skills':sorted(rows.values(),key=lambda x:x['skill_id']),
    }
    target=safe_child(ROOT,'.prompt_suite/runtime/installed_skills_inventory.json')
    atomic_write_json(target,out)
    out['result_path']=str(target)
    print(json.dumps(out,indent=2)); return 0

if __name__=='__main__': raise SystemExit(main())
