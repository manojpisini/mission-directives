#!/usr/bin/env python3
"""Regenerate deterministic derived artifacts in a clean copy and compare bytes."""
from __future__ import annotations
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GENERATED=[
    'catalog.json',
    'PROMPT_CATALOG.md',
    'compatibility/capability_identity_registry.json',
    'integrations/md_to_agent_library_crosswalk.json',
    'integrations/md_to_prompt_type_library_crosswalk.json',
    'category_taxonomy.json',
    'template_registry.json',
    'integrations/template_to_prompt_crosswalk.json',
    'capability_graph.json',
    'BODY_QUALITY_AUDIT.json',
    'BODY_QUALITY_AUDIT.md',
]
GENERATORS=[
    'tools/rebuild_suite_metadata.py',
    'tools/build_capability_graph.py',
    'tools/audit_prompt_bodies.py',
]

def ignore(_directory:str,names:list[str])->list[str]:
    return [name for name in names if name in {'__pycache__','.pytest_cache','.git'} or name.endswith(('.pyc','.pyo','.toml.lock','.lock'))]

def check(root:Path=ROOT)->dict:
    missing=[x for x in GENERATED+GENERATORS if not (root/x).exists()]
    if missing: return {'status':'fail','missing':missing,'mismatches':[]}
    with tempfile.TemporaryDirectory(prefix='md-repro-') as tmp:
        clone=Path(tmp)/'suite'
        shutil.copytree(root,clone,ignore=ignore)
        env=os.environ.copy(); env['MD_NO_TUI']='1'
        for script in GENERATORS:
            proc=subprocess.run([sys.executable,str(clone/script)],cwd=clone,env=env,text=True,capture_output=True,stdin=subprocess.DEVNULL)
            if proc.returncode:
                return {'status':'fail','generator':script,'return_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'mismatches':[]}
        mismatches=[]
        for relative in GENERATED:
            a=(root/relative).read_bytes(); b=(clone/relative).read_bytes()
            if a.replace(b'\r\n',b'\n')!=b.replace(b'\r\n',b'\n'): mismatches.append(relative)
        return {'status':'pass' if not mismatches else 'fail','generated_files':len(GENERATED),'generators':GENERATORS,'mismatches':mismatches}

def main()->int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    result=check(); print(json.dumps(result,indent=2)); return 0 if result['status']=='pass' else 1
if __name__=='__main__': raise SystemExit(main())
