#!/usr/bin/env python3
"""Verify active release metadata, guidance, frontmatter, and path hygiene."""
from __future__ import annotations
if __name__ == '__main__':
    try: from tool_runtime import bootstrap_tool
    except ImportError: from tools.tool_runtime import bootstrap_tool
    _MD_TUI=bootstrap_tool(__file__)
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEXT_SUFFIXES={'.md','.json','.py','.sh','.ps1','.toml','.yaml','.yml','.txt'}
EXCLUDED_PARTS={'__pycache__','.pytest_cache'}

def check(root:Path=ROOT)->dict:
    errors=[]; version=(root/'VERSION').read_text().strip(); expected_release=f'mission-directives-{version}'
    if (root/'RELEASE_ID').read_text().strip()!=expected_release: errors.append('RELEASE_ID does not derive from VERSION')
    for name in ('AGENTS.md','CLAUDE.md'):
        text=(root/name).read_text()
        if f'Mission Directives **{version}**' not in text: errors.append(f'{name}: managed guidance version is stale')
    import yaml
    for path in (root/'prompts').glob('*.md'):
        _,frontmatter,_=path.read_text().split('---',2)
        if yaml.safe_load(frontmatter).get('suite_version')!=version: errors.append(f'{path.relative_to(root)}: suite_version mismatch')
    for path in (root/'templates').rglob('*.md'):
        _,frontmatter,_=path.read_text().split('---',2)
        if yaml.safe_load(frontmatter).get('suite_version')!=version: errors.append(f'{path.relative_to(root)}: suite_version mismatch')
    active_json_mismatches=[]
    for path in root.rglob('*.json'):
        rel=path.relative_to(root)
        if rel.parts[:1] in {('evaluations',),('.prompt_suite',)} or any(x in path.parts for x in EXCLUDED_PARTS):
            continue
        try: value=json.loads(path.read_text(encoding='utf-8'))
        except (OSError,json.JSONDecodeError):
            continue
        if isinstance(value,dict) and 'suite_version' in value and value.get('suite_version')!=version:
            active_json_mismatches.append(rel.as_posix())
    if active_json_mismatches: errors.append(f'active JSON suite_version mismatches: {active_json_mismatches[:30]}')
    runtime_lock_files=[p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and (p.suffix=='.lock' or p.name.endswith('.toml.lock')) and p.relative_to(root).parts[:2] != ('.prompt_suite','logs')]
    if runtime_lock_files: errors.append(f'distribution contains runtime lock files: {runtime_lock_files[:30]}')
    personal=re.compile(r'C:\\\\Users\\\\[^%$<{/\\\\]+|/Users/[^/$<{]+|/home/[^/$<{]+|bl4nkslate',re.I)
    personal_hits=[]
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES or any(x in path.parts for x in EXCLUDED_PARTS): continue
        rel=path.relative_to(root)
        if rel.as_posix() in {'TEST_RESULTS.json','VALIDATION.json','tools/check_release_consistency.py'} or rel.parts[:2]==('.prompt_suite','logs') or rel.parts[:2]==('evaluations','schema_contracts') or rel.parts[:1]==('tests',): continue
        if personal.search(path.read_text(encoding='utf-8',errors='ignore')): personal_hits.append(rel.as_posix())
    if personal_hits: errors.append(f'personal absolute paths: {personal_hits[:20]}')
    if (root/'.prompt_suite'/'agent-guidance-receipt.json').exists(): errors.append('distribution contains machine-local agent guidance receipt')
    return {'status':'pass' if not errors else 'fail','suite_version':version,'release_id':expected_release,'errors':errors}

def main()->int:
    result=check(); print(json.dumps(result,indent=2)); return 0 if result['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
