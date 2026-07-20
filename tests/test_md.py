import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('md',ROOT/'tools/md.py'); md=importlib.util.module_from_spec(spec); spec.loader.exec_module(md)

def test_explain_loads_control_once():
 out=md.explain('C-63'); ids=[x['prompt_id'] for x in out['selected']]
 assert ids[:5]==md.CONTROL and len(ids)==len(set(ids))

def test_department_pack_requires_compilation():
 out=md.explain('ENGINEERING'); assert out['route_confidence']<0.8 and out['unresolved']

def test_plan_dry_run_does_not_write(tmp_path):
 p=tmp_path/'run.json'; out=md.plan('C-63',mode='DRAFT_ONLY',out=str(p),dry_run=True)
 assert not p.exists() and out['simulated_transitions'][-1]=='closed'

def test_select_model_refuses_unmeasured():
 out=md.select_model('MD-29','HIGH_ASSURANCE'); assert out['status']=='no_selection'

def test_illegal_transition_rejected(tmp_path):
 p=tmp_path/'run.json'; p.write_text(json.dumps(md.plan('C-03')))
 try: md.transition(str(p),'closed'); assert False
 except ValueError: pass

def test_apply_approved_requires_receipt(tmp_path):
 m=md.plan('C-13',mode='APPLY_APPROVED'); m['state']='dry_run_ready'; m['evidence_snapshots']=[{'id':'e'}]
 p=tmp_path/'run.json'; p.write_text(json.dumps(m))
 try: md.transition(str(p),'executing'); assert False
 except ValueError as e: assert 'approval' in str(e)

def test_compatibility_map_complete():
 d=json.loads((ROOT/'compatibility/original_66_to_current.json').read_text()); assert len(d['mappings'])==66 and all(x['current_prompt_ids'] for x in d['mappings'])

def test_fixture_coverage():
 cat=json.loads((ROOT/'catalog.json').read_text()); sc=json.loads((ROOT/'SCENARIO_CATALOG.json').read_text())
 assert len(list((ROOT/'evaluations/prompts').glob('MD-*/*.json')))==len(cat['prompts'])*3
 assert len(list((ROOT/'evaluations/scenarios').glob('C-*/*.json')))==len(sc['composite_scenarios'])*3

def test_skill_lock_blocks_unresolved():
 d=json.loads((ROOT/'config/skills.lock.json').read_text()); registry=json.loads((ROOT/'skill_registry.json').read_text()); expected=sum(1 for s in registry['skills'] if s.get('install_command')); assert len(d['entries'])==expected and all(not x['auto_install_allowed'] for x in d['entries'] if x['lock_status']!='resolved')

def test_crosswalk_complete():
 d=json.loads((ROOT/'integrations/md_to_agent_library_crosswalk.json').read_text()); cat=json.loads((ROOT/'catalog.json').read_text()); assert len(d['mappings'])==len(cat['prompts'])


def test_auto_plan_rejects_wasteful_loop():
 out=md.auto_plan('MD-165',loop=True,work_items=1,iterative_quality=False,measurable=False)
 assert 'MD-197' not in out['selected_prompts'] and out['rejected']

def test_auto_plan_selects_generic_local_skill():
 out=md.auto_plan('MD-104',skill_id='visual-assets',skill_required=True)
 assert 'MD-192' in out['selected_prompts'] and 'MD-196' in out['selected_prompts']

def test_auto_plan_missing_skill_routes_discovery():
 out=md.auto_plan('MD-165',skill_id='nonexistent-specialist',skill_required=True,allow_install=True,allow_create=True)
 assert {'MD-192','MD-193','MD-194','MD-195'} <= set(out['selected_prompts'])

def test_loop_plateau_stops():
 out=md.adjudicate_loop(3,0.71,0.9,[0.70,0.705],max_iterations=5,max_no_improvement=2,minimum_delta=0.01)
 assert out['decision']=='plateau_stop'

def test_loop_verified_queue_complete():
 out=md.adjudicate_loop(2,0.95,0.9,[0.8],verified=True,queue_remaining=0)
 assert out['decision']=='complete'

def test_installed_unmapped_skill_routes_through_generic_adapter_after_fit():
    out = md.auto_plan('MD-27', skill_id='code-review', skill_required=True)
    assert out['skill_status']['status'] == 'installed_review_required'
    assert 'MD-192' in out['selected_prompts']
    assert 'MD-196' in out['selected_prompts']
    assert 'MD-193' not in out['selected_prompts']


def test_loop_eligibility_separates_outer_queue_and_inner_refinement_limits():
    out = md.loop_eligibility(work_items=5, iterative_quality=False, measurable=True, max_iterations=3)
    assert out['eligible'] is True
    assert out['maximum_outer_iterations'] == 5
    assert out['maximum_inner_iterations'] == 1
    assert out['maximum_total_iterations'] == 5

def test_skill_alias_resolves_to_canonical_personal_skill():
    status = md.skill_status('strudle')
    assert status['skill_id'] == 'strudel'
    assert status['requested_skill_id'] == 'strudle'
    assert status['status'] == 'usable_local'

def test_loop_does_not_complete_below_declared_threshold():
    out=md.adjudicate_loop(2,0.72,0.9,[0.70],verified=True,queue_remaining=0,max_iterations=5)
    assert out['decision']=='continue'
    assert out['next_action']=='refine_current_item'


def test_loop_threshold_without_verification_routes_to_verification():
    out=md.adjudicate_loop(2,0.95,0.9,[0.80],verified=False,queue_remaining=0,max_iterations=5)
    assert out['decision']=='continue'
    assert out['next_action']=='verify_current_result'


def test_auto_compile_context_schema_and_conditional_skill_branches(tmp_path):
    context={
      'target':'MD-104','intent_complete':True,'skill_id':'missing-specialist','skill_required':True,
      'allow_install':True,'allow_create':True,'loop':True,'work_items':4,'iterative_quality':True,
      'measurable':True,'maximum_inner_iterations':2,'maximum_no_improvement':1,'external_effect':False
    }
    out=md.auto_plan_from_context(context)
    assert {'MD-192','MD-193','MD-194','MD-195','MD-197','MD-198'} <= set(out['selected_prompts'])
    conditional={x['prompt_id']:x for x in out['conditional_injections']}
    assert conditional['MD-194']['mutually_exclusive_group']=='skill_acquisition'
    assert conditional['MD-195']['mutually_exclusive_group']=='skill_acquisition'


def test_supplied_installed_inventory_is_fully_registered():
    inventory=json.loads((ROOT/'config/installed_skills_inventory.json').read_text())
    registry={x['skill_id'] for x in json.loads((ROOT/'skill_registry.json').read_text())['skills']}
    assert inventory['skill_count']==193
    assert all(x['skill_id'] in registry for x in inventory['skills'])
    assert inventory['unmapped_skill_count']==0


def test_real_installed_names_are_not_collapsed_as_aliases():
    aliases=json.loads((ROOT/'config/skill_aliases.json').read_text())['aliases']
    assert aliases=={'strudle':'strudel'}


def test_visual_assets_is_first_class_and_broadly_routed():
    registry={x['skill_id']:x for x in json.loads((ROOT/'skill_registry.json').read_text())['skills']}
    skill=registry['visual-assets']
    assert skill['auto_select_allowed'] is True and skill['maturity']=='approved'
    for pid in ['MD-101','MD-102','MD-103','MD-104','MD-108','MD-159','MD-170','MD-196','MD-197']:
        assert pid in skill['prompt_routes']


def test_personal_skill_conformance_contracts_exist():
    for sid in ['visual-assets','strudel']:
        p=ROOT/'evaluations/skills'/f'{sid}.json'
        assert p.exists()
        data=json.loads(p.read_text())
        assert data['lock_required'] is False and data['live_status']=='not_run'


def test_dual_install_scripts_share_canonical_python_implementations():
    install_py=(ROOT/'tools/skill_dual.py').read_text()
    local_py=(ROOT/'tools/register_local_skill_dual.py').read_text()
    for text in [install_py,local_py]:
        assert "from agent_paths import all_default_destinations" in text
        assert "all_default_destinations" in text
        assert "sha256" in text
        assert "hashes differ" in text
        assert ("C:" + "\\\\Users\\\\") not in text and ("/" + "home/") not in text and ("/" + "Users/") not in text
    policy=json.loads((ROOT/'compatibility/agent_skill_paths.json').read_text())
    assert set(policy['applications'])=={'agents','claude-code','opencode'}
    for stem,canonical in [("install_skill_dual","skill_dual.py"),("register_local_skill_dual","register_local_skill_dual.py")]:
        assert canonical in (ROOT/'tools'/f'{stem}.ps1').read_text()
        assert canonical in (ROOT/'tools'/f'{stem}.sh').read_text()


def test_lookup_exact_prompt_id_is_first():
    out = md.lookup('MD-29', limit=5)
    assert out['results'][0]['id'] == 'MD-29'
    assert out['results'][0]['match_type'] == 'exact_id'


def test_lookup_naive_keywords_find_relevant_routes_and_skills():
    out = md.lookup('visual assets infographic presentation', limit=10)
    ids = {row['id'] for row in out['results']}
    assert 'C-109' in ids or 'MD-104' in ids
    assert any(row['kind'] == 'skill' and row['id'] == 'visual-assets' for row in out['results'])


def test_lookup_productivity_keyword_returns_work_system_capability():
    out = md.lookup('personal productivity work system', limit=5, kind='prompts')
    assert any(row['id'] == 'MD-138' for row in out['results'])


def test_lookup_unknown_query_is_honest():
    out = md.lookup('zzzxxyy-no-such-capability', limit=5)
    assert out['status'] == 'no_confident_match'
    assert out['results'] == []


def test_exact_execution_twin_is_reciprocal_and_immutable():
    out = md.exact_execution_twin('MD-25')
    assert out['planning_prompt_id'] == 'MD-25'
    assert out['execution_prompt_id'] == 'MD-26'
    assert out['exact_twin_only'] is True
    try:
        md.exact_execution_twin('MD-25', requested_executor='MD-28')
        assert False
    except ValueError as exc:
        assert 'exact execution twin' in str(exc)


def test_exact_execution_twin_rejects_executor_as_planner():
    try:
        md.exact_execution_twin('MD-26')
        assert False
    except ValueError as exc:
        assert 'investigative planning prompt' in str(exc)


def test_pair_review_disposition_requires_review_before_consent():
    pending = md.pair_review_disposition('MD-25', handoff_ready=True, review_status='pending')
    assert pending['next_action'] == 'ask_for_plan_review'
    assert pending['execution_prompt_id'] == 'MD-26'
    assert 'MD-26' not in pending.get('selected_prompts', [])


def test_pair_review_changes_require_revision_refreeze_and_rereview():
    changes = md.pair_review_disposition('MD-25', handoff_ready=True, review_status='changes_requested', revisions_applied=False)
    assert changes['next_action'] == 'revise_plan'
    revised = md.pair_review_disposition('MD-25', handoff_ready=True, review_status='changes_requested', revisions_applied=True)
    assert revised['next_action'] == 'refreeze_and_request_review_again'
    assert revised['execution_consent_allowed'] is False


def test_pair_review_approved_asks_for_exact_twin_execution_consent():
    out = md.pair_review_disposition('MD-25', handoff_ready=True, review_status='approved')
    assert out['next_action'] == 'ask_execution_consent'
    assert out['execution_prompt_id'] == 'MD-26'
    assert 'MD-26' in out['execution_question']
    assert out['execution_consent_allowed'] is True


def test_authorize_exact_twin_requires_review_and_explicit_user_consent():
    for kwargs in (
        {'handoff_ready': False, 'plan_review_approved': True, 'user_approved': True},
        {'handoff_ready': True, 'plan_review_approved': False, 'user_approved': True},
    ):
        try:
            md.authorize_exact_twin('MD-25', requested_executor='MD-26', **kwargs)
            assert False
        except ValueError:
            pass
    declined = md.authorize_exact_twin('MD-25', requested_executor='MD-26', handoff_ready=True, plan_review_approved=True, user_approved=False)
    assert declined['status'] == 'execution_declined'
    approved = md.authorize_exact_twin('MD-25', requested_executor='MD-26', handoff_ready=True, plan_review_approved=True, user_approved=True)
    assert approved['status'] == 'authorized'
    assert approved['execution_prompt_id'] == 'MD-26'


def test_plan_manifest_declares_all_exact_pair_review_workflows():
    manifest = md.plan('C-03', mode='PLAN_ONLY')
    assert manifest['paired_workflows']
    for workflow in manifest['paired_workflows']:
        assert workflow['exact_twin_only'] is True
        assert workflow['review_status'] == 'pending'
        assert workflow['execution_consent_status'] == 'not_requested'
        twin = md.exact_execution_twin(workflow['planning_prompt_id'])
        assert workflow['execution_prompt_id'] == twin['execution_prompt_id']


def test_manifest_pair_review_revision_and_exact_consent_workflow(tmp_path):
    manifest = md.plan('C-03', mode='DRAFT_ONLY')
    manifest['state'] = 'evidence_ready'
    path = tmp_path / 'run.json'
    path.write_text(json.dumps(manifest))
    frozen = md.freeze_pair_handoff(str(path), 'MD-29', 'sha256:' + '1' * 64)
    assert frozen['state'] == 'plan_review_pending'
    changed = md.record_plan_review(str(path), 'MD-29', 'changes_requested', reviewer='user', feedback='Add platform coverage')
    assert changed['state'] == 'plan_revision_pending'
    refrozen = md.freeze_pair_handoff(str(path), 'MD-29', 'sha256:' + '2' * 64)
    assert refrozen['state'] == 'plan_review_pending'
    approved = md.record_plan_review(str(path), 'MD-29', 'approved', reviewer='user')
    assert approved['state'] == 'execution_consent_pending'
    consented = md.record_execution_consent(str(path), 'MD-29', approved=True, user='user')
    assert consented['state'] == 'dry_run_ready'
    assert consented['authorized_execution_prompt_ids'] == ['MD-30']
    workflow = consented['paired_workflows'][0]
    assert workflow['execution_prompt_id'] == 'MD-30'
    assert workflow['execution_consent_status'] == 'approved'

def test_lookup_add_prompt_routes_to_governed_ingestion_capability():
    result = md.lookup('add a new prompt', limit=5)
    assert result['status'] == 'matched'
    assert result['results'][0]['id'] == 'MD-199'
