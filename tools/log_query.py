#!/usr/bin/env python3
from __future__ import annotations
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse, datetime as dt, json
from pathlib import Path
try: import tomllib
except ImportError: import tomli as tomllib
try:
    from security_utils import safe_child
except ImportError:
    from tools.security_utils import safe_child

ROOT=Path(__file__).resolve().parents[1]


def validate_date(value:str)->str:
    if not isinstance(value,str) or len(value)!=10:
        raise ValueError('Date must use YYYY-MM-DD')
    try:
        parsed=dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError('Date must be a real calendar date in YYYY-MM-DD form') from exc
    if parsed.isoformat()!=value:
        raise ValueError('Date must use zero-padded YYYY-MM-DD')
    return value


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--date',default=dt.datetime.now().astimezone().date().isoformat()); ap.add_argument('--category'); ap.add_argument('--status'); ap.add_argument('--run-id'); a=ap.parse_args()
    try:
        date=validate_date(a.date)
        base=ROOT/'.prompt_suite'/'logs'
        p=safe_child(base,f'{date}.toml')
    except ValueError as exc:
        print(json.dumps({'status':'fail','error':str(exc)},indent=2)); return 2
    if not p.exists(): print(json.dumps({'status':'not_found','path':str(p),'events':[]})); return 0
    try: data=tomllib.loads(p.read_text(encoding='utf-8'))
    except Exception as exc:
        print(json.dumps({'status':'fail','path':str(p),'error':f'Invalid TOML: {exc}'},indent=2)); return 1
    rows=data.get('events',[])
    if a.category: rows=[x for x in rows if x.get('category')==a.category]
    if a.status: rows=[x for x in rows if x.get('status')==a.status]
    if a.run_id: rows=[x for x in rows if x.get('run_id')==a.run_id]
    print(json.dumps({'status':'pass','path':str(p),'event_count':len(rows),'events':rows},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
