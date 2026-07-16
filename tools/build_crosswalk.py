#!/usr/bin/env python3
"""Regenerate proposed MD mappings from external agent and prompt-type catalogs."""
from pathlib import Path
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1]
STOP={'and','or','the','for','with','into','project','system','prompt','agent','type','review','analysis','design','management','planning','production'}
def slug(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')
def toks(s): return {x for x in re.findall(r'[a-z0-9]+',s.lower()) if len(x)>2 and x not in STOP}
def score(a,b):
 A,B=toks(a),toks(b); inter=len(A&B)
 return 0 if not inter else .7*inter/max(1,len(A|B))+.3*inter/max(1,min(len(A),len(B)))
def parse(path,kind):
 current='00'; out=[]
 for line in Path(path).read_text().splitlines():
  h=re.match(r'^##\s+(\d{2})',line)
  if h: current=h.group(1); continue
  m=re.match(r'^-\s+\*\*([^*]+?)\*\*',line) if kind=='agent' else re.match(r'^-\s+(.+?Prompt Type)\s*$',line)
  if m: out.append({'catalog_id':f'{"AGENT" if kind=="agent" else "PT"}-{current}-{slug(m.group(1))}','domain':current,'name':m.group(1).strip()})
 return list({x['catalog_id']:x for x in out}.values())
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--agent-catalog',required=True); ap.add_argument('--prompt-type-catalog',required=True); a=ap.parse_args(); cat=json.loads((ROOT/'catalog.json').read_text())
 for kind,path,outname in [('agent',a.agent_catalog,'md_to_agent_library_crosswalk.json'),('prompt_type',a.prompt_type_catalog,'md_to_prompt_type_library_crosswalk.json')]:
  entries=parse(path,'agent' if kind=='agent' else 'prompt'); mappings=[]
  for p in cat['prompts']:
   q=p['title']+' '+p.get('description',''); ranked=sorted(entries,key=lambda e:score(q,e['name']),reverse=True)[:5]
   mappings.append({'md_prompt_id':p['prompt_id'],'capability_id':p['capability_id'],'title':p['title'],f'{kind}_matches':[dict(e,confidence=round(score(q,e['name']),4),status='proposed') for e in ranked],'mapping_status':'machine_proposed_requires_human_review'})
  (ROOT/'integrations'/outname).write_text(json.dumps({'mapping_method':'token overlap; human review required','mappings':mappings},indent=2)+'\n')
if __name__=='__main__': main()
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

