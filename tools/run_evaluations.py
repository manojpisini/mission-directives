#!/usr/bin/env python3
"""Validate evaluation coverage and deterministic behavior.

This harness does not claim live model or live skill performance. It records those
surfaces as pending until measured outputs are ingested.
"""

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import argparse, json, sys
from jsonschema import validate as js_validate

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_RESULT_REL = ".prompt_suite/results/EVALUATION_STATUS.json"
try:
    from security_utils import atomic_write_json, safe_child
except ImportError:
    from tools.security_utils import atomic_write_json, safe_child
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--publish",
    action="store_true",
    help="Write canonical root EVALUATION_STATUS.json during release sealing.",
)
args = parser.parse_args()
errors = []
cat = json.loads((ROOT / "catalog.json").read_text())
sc = json.loads((ROOT / "SCENARIO_CATALOG.json").read_text())
pairs = [
    p
    for p in cat["prompts"]
    if p["prompt_role"] == "investigative" and p.get("paired_prompt_id")
]
registered_skills = json.loads((ROOT / "skill_registry.json").read_text())["skills"]
installable = [s for s in registered_skills if s.get("install_command")]
conformance_required = installable + [
    s
    for s in registered_skills
    if s.get("kind") == "local_installed" and s.get("auto_select_allowed")
]
fixture_schema = json.loads((ROOT / "schemas/scenario_fixture.schema.json").read_text())
pair_schema = json.loads(
    (ROOT / "schemas/pair_adversarial_fixture.schema.json").read_text()
)
skill_schema = json.loads((ROOT / "schemas/skill_conformance.schema.json").read_text())

_loaded = {}


def load(p):
    p = Path(p)
    if p in _loaded:
        return _loaded[p]
    try:
        value = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"{p}: {e}")
        value = None
    _loaded[p] = value
    return value


prompt_files = list((ROOT / "evaluations/prompts").glob("MD-*/*.json"))
scenario_files = list((ROOT / "evaluations/scenarios").glob("C-*/*.json"))
pair_files = list((ROOT / "evaluations/pairs").glob("*/adversarial.json"))
skill_files = list((ROOT / "evaluations/skills").glob("*.json"))
pvs_files = list((ROOT / "evaluations/pair_vs_single").glob("*.json"))

template_fixture_files = list((ROOT / "evaluations/templates").glob("*/*.json"))
schema_files = list((ROOT / "schemas").glob("*.json"))
schema_contract_files = list((ROOT / "evaluations/schema_contracts").glob("*/*.json"))
if (
    len(template_fixture_files)
    != json.loads((ROOT / "config/template_registry.json").read_text())[
        "template_count"
    ]
    * 3
):
    errors.append("template evaluation coverage incomplete")
if len(schema_contract_files) != len(schema_files) * 2:
    errors.append(
        f"schema contract coverage {len(schema_contract_files)} != {len(schema_files) * 2}"
    )
if len(prompt_files) != len(cat["prompts"]) * 3:
    errors.append(
        f"prompt fixture count {len(prompt_files)} != {len(cat['prompts']) * 3}"
    )
if len(scenario_files) != len(sc["composite_scenarios"]) * 3:
    errors.append("scenario fixture coverage incomplete")
if len(pair_files) != len(pairs):
    errors.append("pair adversarial coverage incomplete")
if len(skill_files) != len(conformance_required):
    errors.append(
        f"skill conformance coverage {len(skill_files)} != {len(conformance_required)}"
    )
if len(pvs_files) != len(pairs):
    errors.append("pair-vs-single coverage incomplete")
for p in prompt_files + scenario_files:
    d = load(p)
    if d:
        try:
            js_validate(d, fixture_schema)
        except Exception as e:
            errors.append(f"{p}: fixture schema {e}")
for p in pair_files:
    d = load(p)
    if d:
        try:
            js_validate(d, pair_schema)
        except Exception as e:
            errors.append(f"{p}: pair schema {e}")
for p in skill_files:
    d = load(p)
    if d:
        try:
            js_validate(d, skill_schema)
        except Exception as e:
            errors.append(f"{p}: skill schema {e}")
# Prompt-body mutation coverage.
mutation_data = load(ROOT / "evaluations/mutation_tests.json") or {}
required_body_mutations = {
    "replace task-specific completion criteria with generic boilerplate",
    "duplicate investigative verification block into executor",
    "remove tool policy",
    "remove one runtime marker from capability prompt",
    "remove executive decision rules",
    "rename authorization boundary to undocumented synonym",
    "add prompt self-dependency",
    "remove paired plan review gate",
    "substitute a nonreciprocal execution twin",
    "skip re-freezing after requested plan changes",
    "infer execution consent from the original task",
    "execute before user plan approval",
}
missing_mutations = required_body_mutations - set(mutation_data.get("mutations", []))
if missing_mutations:
    errors.append(
        f"missing prompt-body mutation definitions: {sorted(missing_mutations)}"
    )

# Negative route tests import the runtime.
sys.path.insert(0, str(ROOT / "tools"))
import md

for case in load(ROOT / "evaluations/negative_routing.json")["cases"]:
    selected = {x["prompt_id"] for x in md.explain(case["target"])["selected"]}
    bad = selected & set(case["must_not_select"])
    if bad:
        errors.append(f"negative route {case['case_id']} selected {sorted(bad)}")
# Recovery drill transitions must be legal.
drill = load(
    ROOT / "evaluations/recovery_drills/failed_execution_rollback_residual.json"
)
cur = drill["initial_state"]
for nxt in drill["transitions"]:
    if nxt not in md.STATE["transitions"].get(cur, []):
        errors.append(f"illegal recovery drill transition {cur}->{nxt}")
    cur = nxt
profiles = json.loads((ROOT / "config/model_profiles.json").read_text())["profiles"]
measured = [
    p
    for p in profiles
    if p.get("measurement_status") == "measured" and p.get("production_eligible")
]
live_skill_pass = sum(
    1
    for p in skill_files
    if isinstance(load(p), dict) and load(p).get("live_status") == "pass"
)
status = {
    "status": "pass_with_external_measurements_pending" if not errors else "fail",
    "claim_scope": "fixture coverage, schema validity, deterministic routing, and recovery-state behavior only",
    "prompt_fixture_files": len(prompt_files),
    "scenario_fixture_files": len(scenario_files),
    "pair_adversarial_fixtures": len(pair_files),
    "pair_vs_single_definitions": len(pvs_files),
    "prompt_body_mutation_definitions": len(mutation_data.get("mutations", [])),
    "skill_conformance_definitions": len(skill_files),
    "template_conformance_fixtures": len(template_fixture_files),
    "schema_contract_fixtures": len(schema_contract_files),
    "live_skill_conformance_passes": live_skill_pass,
    "production_eligible_measured_models": len(measured),
    "human_reviewed_golden_runs": 0,
    "machine_reference_runs": len(
        list((ROOT / "evaluations/golden_runs").glob("C-*/manifest.json"))
    ),
    "limitations": [
        "No external language-model benchmark was run in this build environment.",
        "No third-party skill was installed or executed.",
        "Reference runs are machine-generated contracts, not human-reviewed golden outputs.",
    ],
    "errors": errors,
}
target = (
    ROOT / "EVALUATION_STATUS.json"
    if args.publish
    else safe_child(ROOT, RUNTIME_RESULT_REL)
)
atomic_write_json(target, status)
status["result_path"] = str(target)
print(json.dumps(status, indent=2))
sys.exit(1 if errors else 0)
