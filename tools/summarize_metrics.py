#!/usr/bin/env python3
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import argparse,json,statistics
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('run_dir'); a=ap.parse_args(); rows=[]
for p in Path(a.run_dir).rglob('*.json'):
 try:
  d=json.loads(p.read_text()); m=d.get('metrics')
  if m and m.get('wall_time_ms') is not None: rows.append(m)
 except Exception: pass
out={'runs':len(rows),'total_input_tokens':sum(x.get('tokens',{}).get('input',0) for x in rows),'total_output_tokens':sum(x.get('tokens',{}).get('output',0) for x in rows),'total_external_calls':sum(x.get('external_calls',0) for x in rows),'total_cost':sum(x.get('cost') or 0 for x in rows),'median_wall_time_ms':statistics.median([x.get('wall_time_ms',0) for x in rows]) if rows else None}
print(json.dumps(out,indent=2))
