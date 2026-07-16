from pathlib import Path
import json,yaml
ROOT=Path(__file__).resolve().parents[1]
def prompts():
 for p in (ROOT/'prompts').glob('*.md'):
  _,fm,body=p.read_text(encoding='utf-8').split('---',2); yield p,yaml.safe_load(fm),body
def test_every_prompt_routes_known_templates():
 reg=json.loads((ROOT/'template_registry.json').read_text()); ids={x['template_id'] for x in reg['templates']}
 for p,m,b in prompts():
  assert m['template_routes']; assert not ((set(m['template_routes'])|set(m.get('conditional_template_routes',[])))-ids); assert not (set(m['template_routes'])&set(m.get('conditional_template_routes',[]))); assert len(m['template_routes'])<=8; assert '<template_routing>' in b
def test_every_template_is_used_and_deep():
 reg=json.loads((ROOT/'template_registry.json').read_text()); used=set()
 for _,m,_ in prompts(): used.update(m['template_routes']); used.update(m.get('conditional_template_routes',[]))
 assert used=={x['template_id'] for x in reg['templates']}
 for t in reg['templates']:
  path=ROOT/t['path']; assert path.exists(); assert len(path.read_text().splitlines())>=45; assert t['required_by_prompt_ids'] or t.get('conditional_by_prompt_ids')
def test_template_evaluation_coverage():
 reg=json.loads((ROOT/'template_registry.json').read_text())
 for t in reg['templates']:
  d=ROOT/'evaluations/templates'/t['template_id'].replace('/','__')
  assert {p.name for p in d.glob('*.json')}=={'healthy.json','problematic.json','adversarial.json'}
def test_template_router_selects_only_required_until_artifact_triggered():
 import importlib.util
 spec=importlib.util.spec_from_file_location('template_router',ROOT/'tools/template_router.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
 prompt=next(m for _,m,_ in prompts() if m.get('conditional_template_routes'))
 minimum=mod.resolve(prompt['prompt_id'],profile='minimum',root=ROOT)
 assert minimum['selected_template_routes']==prompt['template_routes']
 conditional=prompt['conditional_template_routes'][0]
 triggered=mod.resolve(prompt['prompt_id'],profile='standard',artifacts=[conditional],root=ROOT)
 assert conditional in triggered['selected_template_routes']
 assert len(triggered['selected_template_routes']) < len(prompt['template_routes'])+len(prompt['conditional_template_routes']) or len(prompt['conditional_template_routes'])==1
