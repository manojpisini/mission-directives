#!/usr/bin/env python3
from __future__ import annotations
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]
PROMPTS=ROOT/'prompts'
VERSION=(ROOT/'VERSION').read_text(encoding='utf-8').strip()


def parse(path:Path):
    text=path.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        raise ValueError(f'{path}: missing frontmatter')
    _,fm,body=text.split('---',2)
    return yaml.safe_load(fm),body


def replace_or_insert_after(body:str,after_tag:str,new_tag:str,content:str)->str:
    pattern=rf'<{new_tag}>\s*.*?\s*</{new_tag}>'
    block=f'<{new_tag}>\n{content.strip()}\n</{new_tag}>'
    if re.search(pattern,body,re.S):
        return re.sub(pattern,block,body,count=1,flags=re.S)
    after=rf'(</{after_tag}>)'
    if not re.search(after,body):
        raise ValueError(f'missing insertion anchor {after_tag}')
    return re.sub(after,rf'\1\n\n{block}',body,count=1)


def append_completion_bullet(body:str,bullet:str)->str:
    m=re.search(r'(<completion_criteria>\s*)(.*?)(\s*</completion_criteria>)',body,re.S)
    if not m:
        raise ValueError('missing completion_criteria')
    current=m.group(2).rstrip()
    if bullet in current:
        return body
    replacement=m.group(1)+current+'\n- '+bullet+m.group(3)
    return body[:m.start()]+replacement+body[m.end():]

rows=[]
for path in sorted(PROMPTS.glob('*.md')):
    meta,body=parse(path)
    rows.append((path,meta,body))
by_id={m['prompt_id']:m for _,m,_ in rows}

for path,meta,body in rows:
    meta['suite_version']=VERSION
    pair=meta.get('paired_prompt_id')
    if pair:
        other=by_id.get(pair)
        if not other or other.get('paired_prompt_id')!=meta['prompt_id']:
            raise ValueError(f'{meta["prompt_id"]}: nonreciprocal pair')
        meta['execution_consent_required']=True
        meta['exact_twin_only']=True
        if meta['prompt_role']=='investigative':
            if other.get('prompt_role')!='executive':
                raise ValueError(f'{meta["prompt_id"]}: twin is not executive')
            meta['plan_review_required']=True
            meta['review_cycle']='review_revise_refreeze_rereview_then_consent'
            produces=list(meta.get('produces') or [])
            for item in ('plan_review_package','execution_consent_request'):
                if item not in produces: produces.append(item)
            meta['produces']=produces
            gate=f'''The exact execution twin is `{pair}`, derived only from this prompt's canonical `paired_prompt_id`. After the handoff is ready, present the completed plan and frozen artifacts for user review. Invite requested changes, improvements, additions, removals, or refinements. Apply every accepted change, update affected evidence and artifacts, rerun readiness verification, re-freeze the handoff, and request user review again. Only after the user approves the reviewed plan ask for explicit execution consent to invoke `{pair}`. Never invoke another executive prompt, infer consent from the original request, or treat requested revisions as approval.'''
            body=replace_or_insert_after(body,'handoff_contract','plan_review_and_execution_gate',gate)
            bullet=f'The user has reviewed the completed plan; accepted changes, improvements, additions, removals, and refinements are incorporated and re-verified; the handoff is re-frozen; and the execution-consent question names only the exact execution twin `{pair}`.'
            body=append_completion_bullet(body,bullet)
        elif meta['prompt_role']=='executive':
            if other.get('prompt_role')!='investigative':
                raise ValueError(f'{meta["prompt_id"]}: twin is not investigative')
            meta['reviewed_handoff_required']=True
            meta['accepted_planning_prompt_id']=pair
            gate=f'''Accept work only from a reviewed handoff produced by the exact paired planner `{pair}`. Require a current frozen-handoff hash, an approved plan-review receipt, and explicit execution consent naming this prompt `{meta['prompt_id']}`. Reject a handoff from any other planner, a plan changed after approval, revisions that were not re-frozen and reviewed again, stale evidence, inferred consent, or an attempt to substitute another execution twin. This prompt may execute only the bounded actions approved in that exact reviewed handoff.'''
            body=replace_or_insert_after(body,'authorization_boundary','reviewed_handoff_authority',gate)
            bullet=f'Execution authority is evidenced by an approved review receipt and explicit consent naming this prompt `{meta["prompt_id"]}` as the exact execution twin of `{pair}`; no alternate planner or executor is accepted.'
            body=append_completion_bullet(body,bullet)
    # Keep budgets honest after adding mandatory governance text.
    words=len(re.findall(r'\b\w+[\w-]*\b',body))
    budget=meta.setdefault('complexity_budget',{})
    budget['maximum_body_words']=max(int(budget.get('maximum_body_words') or 0),((words+49)//50)*50)
    dumped=yaml.safe_dump(meta,sort_keys=False,allow_unicode=True,width=120).rstrip()
    path.write_text(f'---\n{dumped}\n---{body}',encoding='utf-8')

print(f'Updated {len(rows)} prompts; paired planners: {sum(1 for _,m,_ in rows if m.get("prompt_role")=="investigative" and m.get("paired_prompt_id"))}')
