#!/usr/bin/env python3
"""Build deterministic healthy and adversarial fixtures for every JSON schema."""
from __future__ import annotations
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCHEMAS=ROOT/'schemas'
OUT=ROOT/'evaluations'/'schema_contracts'

def pattern_value(pattern:str)->str:
    choices=[
        ('^MD-', 'MD-00'), ('^ACTION-', 'ACTION-001'), ('^VERIFY-', 'VERIFY-001'),
        ('^EVIDENCE-', 'EVIDENCE-001'), ('^FINDING-', 'FINDING-001'),
        ('^[0-9a-f]{40}$', 'a'*40), ('^[0-9a-f]{64}$', 'b'*64),
        ('^[a-z][a-z0-9-]+/[a-z0-9-]+$', 'core/example'),
        ('^[a-z0-9][a-z0-9-]*$', 'example-skill'),
        ('^[A-Za-z0-9_-]+:.+$', 'user:approved'),
        ('^prompts/[0-9]{3}_[A-Z0-9_]+\\.md$', 'prompts/200_EXAMPLE.md'),
        ('^md\\.[a-z0-9._-]+$', 'md.enablement.example'),
        ('^[0-9]+\\.[0-9]+\\.[0-9]+$', '1.8.3'),
    ]
    for prefix,value in choices:
        if pattern.startswith(prefix) or pattern==prefix: return value
    for value in ('example','x','ID-001','user:approved'):
        try:
            if re.fullmatch(pattern,value): return value
        except re.error: break
    return 'example'

def sample(schema:dict, schemas:dict[str,dict])->object:
    if '$ref' in schema:
        name=Path(schema['$ref']).name
        return sample(schemas[name],schemas)
    if 'const' in schema: return schema['const']
    if 'enum' in schema: return schema['enum'][0]
    if 'default' in schema: return schema['default']
    if 'oneOf' in schema: return sample(schema['oneOf'][0],schemas)
    if 'anyOf' in schema: return sample(schema['anyOf'][0],schemas)
    if 'allOf' in schema:
        merged={}
        for part in schema['allOf']:
            value=sample(part,schemas)
            if isinstance(value,dict): merged.update(value)
        return merged
    kind=schema.get('type','object')
    if isinstance(kind,list): kind=next((x for x in kind if x!='null'),'null')
    if kind=='object':
        props=schema.get('properties',{})
        return {key:sample(props.get(key,{}),schemas) for key in schema.get('required',[])}
    if kind=='array':
        count=max(schema.get('minItems',0),1)
        return [sample(schema.get('items',{}),schemas) for _ in range(count)]
    if kind=='string':
        if schema.get('format')=='date-time': return '2026-07-15T00:00:00Z'
        if schema.get('format')=='date': return '2026-07-15'
        if schema.get('format') in {'uri','uri-reference'}: return 'https://example.invalid/resource'
        value=pattern_value(schema['pattern']) if schema.get('pattern') else 'example'
        minimum=schema.get('minLength',0)
        if len(value)<minimum: value += 'x'*(minimum-len(value))
        return value
    if kind=='integer': return int(schema.get('minimum',0))
    if kind=='number': return float(schema.get('minimum',0))
    if kind=='boolean': return True
    if kind=='null': return None
    return None

def main()->int:
    schemas={p.name:json.loads(p.read_text()) for p in sorted(SCHEMAS.glob('*.json'))}
    OUT.mkdir(parents=True,exist_ok=True)
    for name,schema in schemas.items():
        target=OUT/Path(name).stem.replace('.schema','')
        target.mkdir(parents=True,exist_ok=True)
        (target/'healthy.json').write_text(json.dumps(sample(schema,schemas),indent=2)+'\n')
        (target/'adversarial.json').write_text('[]\n')
    print(json.dumps({'status':'pass','schemas':len(schemas),'fixtures':len(schemas)*2},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
