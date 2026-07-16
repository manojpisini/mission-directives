#!/usr/bin/env python3
"""Resolve portable global skill directories by platform and agent application."""
from __future__ import annotations
import argparse, json, os, platform
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POLICY_PATH=ROOT/'compatibility'/'agent_skill_paths.json'


def _platform(value: str|None=None) -> str:
    raw=(value or platform.system()).lower()
    if raw.startswith('win'): return 'windows'
    if raw in {'darwin','mac','macos','osx'}: return 'macos'
    return 'linux'


def _expand(expr: str, system: str) -> Path:
    home=Path.home()
    if system=='windows':
        expr=expr.replace('%USERPROFILE%',str(home))
    else:
        xdg=os.environ.get('XDG_CONFIG_HOME',str(home/'.config'))
        expr=expr.replace('${XDG_CONFIG_HOME:-$HOME/.config}',xdg).replace('$HOME',str(home))
    if expr.startswith('~/') or expr.startswith('~\\'):
        expr=str(home)+expr[1:]
    # Preserve lexical path components so downstream security checks can detect
    # symbolic links instead of silently following them.
    return Path(os.path.abspath(os.path.expanduser(expr)))


def load_policy(root: Path=ROOT) -> dict:
    return json.loads((root/'compatibility'/'agent_skill_paths.json').read_text(encoding='utf-8'))


def canonical_application(application: str, policy: dict|None=None) -> str:
    policy=policy or load_policy()
    needle=application.strip().lower()
    for name,row in policy['applications'].items():
        if needle==name or needle in row.get('aliases',[]): return name
    raise ValueError(f'Unsupported agent application: {application}')


def resolve(application: str, *, system: str|None=None, root: Path=ROOT) -> Path:
    policy=load_policy(root); app=canonical_application(application,policy); row=policy['applications'][app]
    override=os.environ.get(row['environment_override'])
    return _expand(override or row[_platform(system)],_platform(system))


def all_default_destinations(*, system: str|None=None, root: Path=ROOT) -> dict[str,Path]:
    return {name:resolve(name,system=system,root=root) for name in ('agents','claude-code','opencode')}


def logical(application: str, *, system: str='portable', skill_id: str|None=None, root: Path=ROOT) -> str:
    policy=load_policy(root); app=canonical_application(application,policy); row=policy['applications'][app]
    if system=='portable': base='${'+row['environment_override']+'}'
    else: base=row[_platform(system)]
    return base.rstrip('/\\') + (('/'+skill_id) if skill_id else '')


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('application',choices=['agents','claude-code','opencode','all']); ap.add_argument('--platform',choices=['windows','linux','macos']); ap.add_argument('--logical',action='store_true'); ap.add_argument('--skill-id')
    a=ap.parse_args(); apps=['agents','claude-code','opencode'] if a.application=='all' else [a.application]
    data={x:(logical(x,system=a.platform or 'portable',skill_id=a.skill_id) if a.logical else str(resolve(x,system=a.platform))) for x in apps}
    print(json.dumps(data,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
