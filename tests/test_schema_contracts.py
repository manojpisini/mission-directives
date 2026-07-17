import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
from pathlib import Path
import json
from jsonschema import Draft202012Validator, FormatChecker, RefResolver
ROOT=Path(__file__).resolve().parents[1]
SCHEMAS={p.name:json.loads(p.read_text()) for p in (ROOT/'schemas').glob('*.json')}
STORE={name:schema for name,schema in SCHEMAS.items()}
STORE.update({f'file://{(ROOT/"schemas"/name).resolve()}':schema for name,schema in SCHEMAS.items()})

def validator(name):
 schema=SCHEMAS[name]
 return Draft202012Validator(schema,resolver=RefResolver(base_uri=(ROOT/'schemas').resolve().as_uri()+'/',referrer=schema,store=STORE),format_checker=FormatChecker())

def test_every_schema_is_valid_json_schema():
 errors=[]
 for name,schema in SCHEMAS.items():
  try: Draft202012Validator.check_schema(schema)
  except Exception as exc: errors.append(f'{name}: {exc}')
 assert not errors,errors

def test_every_schema_has_positive_and_adversarial_contract_fixtures():
 failures=[]
 for name in sorted(SCHEMAS):
  stem=Path(name).stem.replace('.schema',''); folder=ROOT/'evaluations/schema_contracts'/stem
  healthy=json.loads((folder/'healthy.json').read_text()); adversarial=json.loads((folder/'adversarial.json').read_text())
  valid_errors=list(validator(name).iter_errors(healthy)); invalid_errors=list(validator(name).iter_errors(adversarial))
  if valid_errors or not invalid_errors: failures.append({'schema':name,'healthy_errors':[x.message for x in valid_errors[:3]],'adversarial_was_rejected':bool(invalid_errors)})
 assert not failures,failures

def test_prompt_frontmatter_schema_accepts_catalog_entries():
 import yaml
 schema=json.loads((ROOT/'prompt-frontmatter.schema.json').read_text()); check=Draft202012Validator(schema); failures=[]
 for p in (ROOT/'prompts').glob('*.md'):
  _,fm,_=p.read_text(encoding='utf-8').split('---',2); issues=list(check.iter_errors(yaml.safe_load(fm)))
  if issues: failures.append((p.name,[x.message for x in issues[:3]]))
 assert not failures,failures

def test_current_runtime_artifacts_validate_against_declared_schemas():
 failures=[]
 def check(name,values):
  for index,value in enumerate(values):
   issues=list(validator(name).iter_errors(value))
   if issues: failures.append({'schema':name,'index':index,'errors':[x.message for x in issues[:3]]})
 check('installed_skill_inventory.schema.json',[json.loads((ROOT/'installed_skills_inventory.json').read_text())])
 check('skill_lock.schema.json',json.loads((ROOT/'skills.lock.json').read_text())['entries'])
 check('model_profile.schema.json',json.loads((ROOT/'model_profiles.json').read_text())['profiles'])
 check('template_descriptor.schema.json',json.loads((ROOT/'template_registry.json').read_text())['templates'])
 mappings=[]
 for name in ['md_to_agent_library_crosswalk.json','md_to_prompt_type_library_crosswalk.json']:
  mappings.extend(json.loads((ROOT/'integrations'/name).read_text()).get('mappings',[]))
 check('cross_catalog_mapping.schema.json',mappings)
 check('scenario_fixture.schema.json',[json.loads(p.read_text()) for p in (ROOT/'evaluations/scenarios').glob('C-*/*.json')])
 check('pair_adversarial_fixture.schema.json',[json.loads(p.read_text()) for p in (ROOT/'evaluations/pairs').glob('*/adversarial.json')])
 check('skill_conformance.schema.json',[json.loads(p.read_text()) for p in (ROOT/'evaluations/skills').glob('*.json')])
 assert not failures,failures
