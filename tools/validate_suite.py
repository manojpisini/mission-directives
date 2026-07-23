#!/usr/bin/env python3
from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import hashlib, json, re, sys, yaml

ROOT = Path(__file__).resolve().parents[1]
errors = []
warnings = []


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {e}")
        return {}


version = (
    (ROOT / "VERSION").read_text().strip() if (ROOT / "VERSION").exists() else None
)
if not version or not re.fullmatch(r"\d+\.\d+\.\d+", version or ""):
    errors.append("VERSION must contain semantic version")
files = sorted((ROOT / "prompts").glob("*.md"))
items = []
for f in files:
    text = f.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{f.name}: missing frontmatter")
        continue
    try:
        _, fm, body = text.split("---", 2)
        m = yaml.safe_load(fm)
    except Exception as e:
        errors.append(f"{f.name}: parse error {e}")
        continue
    items.append((f, m, body))
    for key in (
        "prompt_id",
        "sequence",
        "title",
        "slug",
        "capability_id",
        "prompt_slug",
        "identity_status",
        "canonical_path",
        "category",
        "prompt_role",
        "prompt_type",
        "status",
        "description",
        "default_mode",
        "allowed_modes",
        "risk_level",
        "requires",
        "output_contract",
    ):
        if key not in m:
            errors.append(f"{f.name}: missing frontmatter {key}")
    if m.get("suite_version") != version:
        errors.append(f"{f.name}: suite_version mismatch")
    if m.get("canonical_path") != f"prompts/{f.name}":
        errors.append(f"{f.name}: canonical path mismatch")
    for tag in ["<prompt>", "<identity>", "<mission>"]:
        if tag not in body:
            errors.append(f"{f.name}: missing {tag}")
    if (m.get("sequence") or 0) >= 124:
        for tag in [
            "<required_inputs>",
            "<method>",
            "<output_contract>",
            "<completion_criteria>",
            "<stop_conditions>",
        ]:
            if tag not in body:
                errors.append(f"{f.name}: missing {tag}")
    if body.count("```") % 2:
        errors.append(f"{f.name}: unbalanced code fences")
    line_budget = (m.get("complexity_budget") or {}).get("maximum_body_lines", 260)
    if len(body.splitlines()) > line_budget:
        warnings.append(f"{f.name}: body exceeds declared line budget {line_budget}")
ids = {m["prompt_id"]: m for _, m, _ in items}
seqs = sorted(m["sequence"] for _, m, _ in items)
if seqs != list(range(len(items))):
    errors.append("prompt sequences are not contiguous")
cap_ids = [m.get("capability_id") for _, m, _ in items]
if len(cap_ids) != len(set(cap_ids)):
    errors.append("capability_id values must be unique")
slugs = [m.get("prompt_slug") for _, m, _ in items]
if len(slugs) != len(set(slugs)):
    errors.append("prompt_slug values must be unique")
for f, m, b in items:
    pid = m["prompt_id"]
    expected = f"MD-{m['sequence']:02d}"
    if pid != expected:
        errors.append(f"{pid}: id/sequence mismatch, expected {expected}")
    if m.get("identity_status") != "permanent":
        errors.append(f"{pid}: identity must be permanent")
    pair = m.get("paired_prompt_id")
    if pair:
        if pair not in ids:
            errors.append(f"{pid}: missing pair {pair}")
        else:
            pm = ids[pair]
            if pm.get("paired_prompt_id") != pid:
                errors.append(f"{pid}: non-reciprocal pair")
            if {m["prompt_role"], pm["prompt_role"]} != {"investigative", "executive"}:
                errors.append(f"{pid}: invalid pair roles")
            if m["prompt_role"] == "executive" and pair not in m.get("requires", []):
                errors.append(f"{pid}: executor does not require investigator")
            if m["prompt_role"] == "investigative":
                if not m.get("plan_review_required"):
                    errors.append(
                        f"{pid}: paired planner must require user plan review"
                    )
                if not m.get("execution_consent_required"):
                    errors.append(
                        f"{pid}: paired planner must require execution consent"
                    )
                if not m.get("exact_twin_only"):
                    errors.append(f"{pid}: paired planner must be exact-twin-only")
            if m["prompt_role"] == "executive":
                if not m.get("reviewed_handoff_required"):
                    errors.append(f"{pid}: executor must require a reviewed handoff")
                if not m.get("execution_consent_required"):
                    errors.append(f"{pid}: executor must require execution consent")
                if not m.get("exact_twin_only"):
                    errors.append(f"{pid}: executor must be exact-twin-only")
                if m.get("accepted_planning_prompt_id") != pair:
                    errors.append(
                        f"{pid}: accepted planning prompt must equal reciprocal paired_prompt_id"
                    )
    elif m.get("pairing_required"):
        errors.append(f"{pid}: pairing_required without pair")
    if m["prompt_role"] == "executive" and not m.get("dry_run_required"):
        errors.append(f"{pid}: executive missing dry run")
    if m["prompt_role"] in {"operational", "executive"} and "DRAFT_ONLY" not in (
        m.get("allowed_modes") or []
    ):
        errors.append(f"{pid}: producer missing DRAFT_ONLY")
    if m["prompt_role"] != "control" and m.get("evidence_lane") not in (
        "factual",
        "hybrid",
        "imaginative",
    ):
        errors.append(f"{pid}: invalid evidence lane")
    if m.get("preferred_skills") and "<skill_routing>" not in b:
        errors.append(f"{pid}: skills without skill_routing section")

cat = load(ROOT / "catalog.json")
if cat.get("suite_version") != version:
    errors.append("catalog suite version mismatch")
if cat.get("prompt_count") != len(items) or len(cat.get("prompts", [])) != len(items):
    errors.append("catalog count mismatch")
if {x.get("prompt_id") for x in cat.get("prompts", [])} != set(ids):
    errors.append("catalog IDs mismatch")
for p in cat.get("prompts", []):
    m = ids.get(p["prompt_id"])
    if not m:
        continue
    for key in (
        "sequence",
        "title",
        "canonical_path",
        "category",
        "prompt_role",
        "prompt_type",
        "risk_level",
        "evidence_lane",
        "allowed_modes",
        "preferred_skills",
        "output_media",
        "capability_id",
        "prompt_slug",
        "identity_status",
        "paired_prompt_id",
        "plan_review_required",
        "reviewed_handoff_required",
        "execution_consent_required",
        "exact_twin_only",
        "accepted_planning_prompt_id",
    ):
        if p.get(key) != m.get(key):
            errors.append(f"{p['prompt_id']}: catalog/frontmatter mismatch {key}")

# Skills and locks.
registry = load(ROOT / "skill_registry.json")
skill_ids = {x.get("skill_id") for x in registry.get("skills", [])}
if len(skill_ids) != len(registry.get("skills", [])):
    errors.append("duplicate skill IDs")
installable = [s for s in registry.get("skills", []) if s.get("install_command")]
for s in registry.get("skills", []):
    if s.get("install_command") and not re.fullmatch(
        r"npx skills add https://github\.com/[^\s]+ --skill [a-z0-9][a-z0-9-]*",
        s["install_command"],
    ):
        errors.append(f"{s['skill_id']}: invalid exact install command")
    if s.get("kind") == "installable" and not s.get("lock_required"):
        errors.append(f"{s['skill_id']}: installable skill must require lock")
    if s.get("kind") != "runtime_alias" and not s.get("quarantine_output"):
        errors.append(f"{s['skill_id']}: external skill output must be quarantined")
    if s.get("trust_tier") not in (
        "native",
        "verified",
        "community_reviewed",
        "unreviewed",
    ):
        errors.append(f"{s['skill_id']}: invalid trust tier")
for _, m, _ in items:
    unknown = set(m.get("preferred_skills") or []) - skill_ids
    if unknown:
        errors.append(f"{m['prompt_id']}: unknown skills {sorted(unknown)}")
inventory = load(ROOT / "config/installed_skills_inventory.json")
observed_ids = {x.get("skill_id") for x in inventory.get("skills", [])}
if inventory.get("skill_count") != len(observed_ids):
    errors.append("installed skill inventory count mismatch")
if observed_ids - skill_ids:
    errors.append(
        f"installed skills missing registry entries: {sorted(observed_ids - skill_ids)}"
    )
if inventory.get("unmapped_skill_count") != 0:
    errors.append("supplied installed skill inventory must be fully registered")
for sid in ("visual-assets", "strudel"):
    s = next((x for x in registry.get("skills", []) if x.get("skill_id") == sid), None)
    if not s or not s.get("auto_select_allowed") or s.get("maturity") != "approved":
        errors.append(
            f"{sid}: personal skill must be approved and auto-selectable after task-fit resolution"
        )


# Prompt-body semantic quality.
def block(body, tag):
    match = re.search(rf"<{tag}>\s*(.*?)\s*</{tag}>", body, re.S)
    return match.group(1).strip() if match else None


def norm(value):
    return " ".join((value or "").split()).lower()


required_markers = {
    "@EVIDENCE:{id}",
    "?UNKNOWN:{id}",
    "#FINDING:{id}",
    "+ACTION:{id}",
    "=VERIFY:{id}",
    "!STOP:{reason}",
}
banned_completion = {
    "complete only when the outcome is evidenced, authorized, and honestly closed.",
    "complete only when the artifact satisfies the declared decision or workflow, passes the domain gates above, respects authority and evidence boundaries, and records verification evidence plus unresolved residuals.",
    "complete only when the requested artifact is accurate for its evidence lane, internally coherent, audience-fit, quality-checked, and accompanied by explicit unknowns or residuals.",
    "complete only when the production package satisfies the frozen brief, preserves evidence integrity, passes editorial and format-specific review, and records unresolved claims or production dependencies.",
}
completion_counts = {}
body_by_id = {m["prompt_id"]: b for _, m, b in items}
for f, m, b in items:
    pid = m["prompt_id"]
    if pid in (m.get("requires") or []):
        errors.append(f"{pid}: prompt cannot require itself")
    if pid in (m.get("contract_refs") or []):
        errors.append(f"{pid}: prompt cannot contract-reference itself")
    if "<security_execution_boundary>" in b:
        errors.append(f"{pid}: use canonical authorization_boundary tag")
    for tag in (
        "authorization_boundary",
        "tool_policy",
        "runtime_markers",
        "completion_criteria",
    ):
        if block(b, tag) is None:
            errors.append(f"{pid}: missing {tag}")
    markers = block(b, "runtime_markers") or ""
    for marker in required_markers:
        if marker not in markers:
            errors.append(f"{pid}: runtime_markers missing {marker}")
    cc = block(b, "completion_criteria")
    if cc:
        n = norm(cc)
        completion_counts[n] = completion_counts.get(n, 0) + 1
        if n in banned_completion:
            errors.append(f"{pid}: boilerplate completion criteria")
        if sum(1 for line in cc.splitlines() if line.strip().startswith("- ")) < 3:
            errors.append(
                f"{pid}: completion criteria need at least 3 task-specific bullets"
            )
        if "=verify:{id}" not in n:
            errors.append(f"{pid}: completion criteria missing verification marker")
        title_terms = {
            w.lower()
            for w in re.findall(r"[A-Za-z][A-Za-z0-9-]{4,}", m["title"])
            if w.lower()
            not in {
                "and",
                "with",
                "from",
                "into",
                "authorized",
                "investigation",
                "execution",
                "verification",
                "production",
            }
        }
        if title_terms and not any(w in n for w in title_terms):
            errors.append(
                f"{pid}: completion criteria do not name task-specific subject"
            )
    if m["prompt_role"] == "investigative" and m.get("paired_prompt_id"):
        gate = norm(block(b, "plan_review_and_execution_gate"))
        for required in (
            m["paired_prompt_id"].lower(),
            "present the completed plan",
            "user review",
            "requested changes",
            "re-freeze",
            "execution consent",
            "exact execution twin",
        ):
            if required not in gate:
                errors.append(f"{pid}: plan review gate missing {required}")
    if m["prompt_role"] == "executive":
        if block(b, "decision_rules") is None:
            errors.append(f"{pid}: executive missing decision_rules")
        if block(b, "verification_reference") is None:
            errors.append(f"{pid}: executive missing verification_reference")
        if block(b, "verification") is not None:
            errors.append(
                f"{pid}: executive must reference frozen criteria, not duplicate verification block"
            )
        gate = norm(block(b, "reviewed_handoff_authority"))
        for required in (
            m["paired_prompt_id"].lower(),
            "reviewed handoff",
            "execution consent",
            "reject",
            "exact paired planner",
        ):
            if required not in gate:
                errors.append(f"{pid}: reviewed handoff authority missing {required}")
    budget = (m.get("complexity_budget") or {}).get("maximum_body_words")
    words = len(re.findall(r"\b\w+[\w-]*\b", b))
    if budget and words > budget:
        errors.append(f"{pid}: body word count {words} exceeds budget {budget}")
for value, count in completion_counts.items():
    if count > 2:
        errors.append(f"completion criteria duplicated {count} times: {value[:120]}")
for _, m, b in items:
    if m["prompt_role"] == "investigative" and m.get("paired_prompt_id"):
        eb = body_by_id.get(m["paired_prompt_id"], "")
        a = block(b, "verification_design")
        z = block(eb, "verification")
        if a and z and norm(a) == norm(z):
            errors.append(
                f"{m['paired_prompt_id']}: duplicates investigative verification design"
            )

# Conditional auto-prompt contracts.
auto = load(ROOT / "policies/auto_prompt_policy.json")
loop_policy = load(ROOT / "policies/loop_execution_policy.json")
acquisition = load(ROOT / "policies/skill_acquisition_policy.json")
expected_auto = {f"MD-{i:02d}" for i in range(191, 199)}
if not expected_auto <= set(ids):
    errors.append("conditional auto-prompt set is incomplete")
for rule in auto.get("rules", []):
    for pid in rule.get("inject", []):
        if pid not in ids:
            errors.append(f"auto policy references unknown prompt {pid}")
if block(body_by_id.get("MD-196", ""), "skill_placeholder") is None:
    errors.append("MD-196 missing generic skill placeholder contract")
if block(body_by_id.get("MD-02", ""), "conditional_auto_prompt_policy") is None:
    errors.append("MD-02 missing conditional auto-prompt policy")
for tag in ("loop_eligibility", "iteration_contract", "exit_conditions"):
    if block(body_by_id.get("MD-197", ""), tag) is None:
        errors.append(f"MD-197 missing {tag}")
if "cline -a opencode" not in body_by_id.get("MD-194", ""):
    errors.append("MD-194 must target global .agents and OpenCode locations")
for skill in ("visual-assets", "strudel"):
    if skill not in skill_ids:
        errors.append(f"missing first-class local skill {skill}")

# Governed prompt-addition workflow.
addition_policy = load(ROOT / "policies/prompt_addition_policy.json")
if addition_policy.get("policy_id") != "md.prompt_addition":
    errors.append("prompt addition policy ID mismatch")
if addition_policy.get("suite_version") != version:
    errors.append("prompt addition policy version mismatch")
if addition_policy.get("status") != "active":
    errors.append("prompt addition policy must be active")
if "MD-199" not in ids:
    errors.append("MD-199 governed prompt-addition capability is missing")
else:
    addition_body = body_by_id.get("MD-199", "")
    for tag in (
        "addition_workflow",
        "decision_rules",
        "method",
        "quality_gates",
        "completion_criteria",
    ):
        if block(addition_body, tag) is None:
            errors.append(f"MD-199 missing {tag}")
    for required in (
        "tools/add_prompt.py",
        "tools/md.py add-prompt",
        "tools/platform_dispatch.py add-prompt",
        "--dry-run",
    ):
        if required not in addition_body:
            errors.append(f"MD-199 missing deterministic route {required}")
for tier in ("healthy", "problematic", "adversarial"):
    if not (ROOT / "evaluations/prompts/MD-199" / f"{tier}.json").is_file():
        errors.append(f"MD-199 missing {tier} fixture")
platform_matrix = load(ROOT / "integrations/platform_tool_matrix.json")
if not any(
    row.get("tool_id") == "add-prompt"
    and row.get("bash") == "tools/add-prompt.sh"
    and row.get("powershell") == "tools/add-prompt.ps1"
    for row in platform_matrix.get("tools", [])
):
    errors.append(
        "prompt addition Bash/PowerShell platform mapping is missing or inconsistent"
    )
if not any(
    row.get("tool_id") == "cleanup-project"
    and row.get("bash") == "tools/cleanup.sh"
    and row.get("powershell") == "tools/cleanup.ps1"
    for row in platform_matrix.get("tools", [])
):
    errors.append(
        "project cleanup Bash/PowerShell platform mapping is missing or inconsistent"
    )
for required in (
    "tools/cleanup.py",
    "tools/cleanup.sh",
    "tools/cleanup.ps1",
    "schemas/cleanup_receipt.schema.json",
    "docs/PROJECT_CLEANUP_AND_UNINSTALL_GUIDE.md",
):
    if not (ROOT / required).is_file():
        errors.append(f"missing project cleanup artifact: {required}")
inv = load(ROOT / "config/installed_skills_inventory.json")
if inv.get("skill_count") != len(inv.get("skills", [])):
    errors.append("installed skill inventory count mismatch")

locks = load(ROOT / "config/skills.lock.json")
entries = locks.get("entries", [])
if len(entries) != len(installable):
    errors.append("skill lock count mismatch")
lock_ids = {x.get("skill_id") for x in entries}
if lock_ids != {s["skill_id"] for s in installable}:
    errors.append("skill lock IDs mismatch")
for e in entries:
    if e.get("lock_status") != "resolved" and e.get("auto_install_allowed"):
        errors.append(f"{e.get('skill_id')}: unresolved lock cannot auto-install")
    if e.get("lock_status") == "resolved":
        if not re.fullmatch(r"[0-9a-f]{40}", e.get("commit_sha") or ""):
            errors.append(f"{e['skill_id']}: invalid resolved commit")
        if not re.fullmatch(r"[0-9a-f]{64}", e.get("tarball_sha256") or ""):
            errors.append(f"{e['skill_id']}: invalid resolved hash")

# Scenario contracts.
sc = load(ROOT / "SCENARIO_CATALOG.json")
scenarios = sc.get("atomic_scenarios", []) + sc.get("composite_scenarios", [])
sids = [s.get("scenario_id") for s in scenarios]
if len(sids) != len(set(sids)):
    errors.append("duplicate scenario IDs")
if len(sc.get("atomic_scenarios", [])) != len(items):
    errors.append("atomic scenario count mismatch")
atomic_prompts = [
    p for s in sc.get("atomic_scenarios", []) for p in s.get("prompts", [])
]
if sorted(atomic_prompts) != sorted(ids):
    errors.append("atomic scenarios must reference each prompt once")
for s in scenarios:
    for key in (
        "required_inputs",
        "produced_artifacts",
        "consumed_artifacts",
        "protected_surfaces",
        "possible_external_effects",
        "minimum_assurance",
        "phases",
        "parallel_groups",
        "execution_locks",
        "completion_gate",
        "branches",
    ):
        if key not in s:
            errors.append(f"{s.get('scenario_id')}: missing scenario contract {key}")
    for p in s.get("prompts", []):
        if p not in ids:
            errors.append(f"{s.get('scenario_id')}: unknown prompt {p}")
    for phase in s.get("phases", []):
        if phase.get("mode") not in {
            "AUDIT_ONLY",
            "PLAN_ONLY",
            "DRAFT_ONLY",
            "APPLY_SAFE",
            "APPLY_APPROVED",
            "VERIFY_ONLY",
        }:
            errors.append(f"{s.get('scenario_id')}: invalid phase mode")

# Current identity and crosswalk contracts.
ident = load(ROOT / "compatibility/capability_identity_registry.json")
if len(ident.get("capabilities", [])) != len(items):
    errors.append("identity registry count mismatch")
for name in (
    "md_to_agent_library_crosswalk.json",
    "md_to_prompt_type_library_crosswalk.json",
):
    d = load(ROOT / "integrations" / name)
    if len(d.get("mappings", [])) != len(items):
        errors.append(f"{name}: incomplete mappings")

# Evaluation coverage and schemas.
conformance_required = installable + [
    s
    for s in registry.get("skills", [])
    if s.get("kind") == "local_installed" and s.get("auto_select_allowed")
]
expected = {
    "prompt": len(items) * 3,
    "scenario": len(sc.get("composite_scenarios", [])) * 3,
    "pair": sum(
        1
        for _, m, _ in items
        if m["prompt_role"] == "investigative" and m.get("paired_prompt_id")
    ),
    "skill": len(conformance_required),
}
fixture_actual = {
    "prompt": len(list((ROOT / "evaluations/prompts").glob("MD-*/*.json"))),
    "scenario": len(list((ROOT / "evaluations/scenarios").glob("C-*/*.json"))),
    "pair": len(list((ROOT / "evaluations/pairs").glob("*/adversarial.json"))),
    "skill": len(list((ROOT / "evaluations/skills").glob("*.json"))),
}
for k in expected:
    if fixture_actual[k] != expected[k]:
        errors.append(f"{k} evaluation coverage {fixture_actual[k]} != {expected[k]}")
if len(list((ROOT / "evaluations/pair_vs_single").glob("*.json"))) != expected["pair"]:
    errors.append("pair-vs-single coverage incomplete")
if len(list((ROOT / "evaluations/golden_runs").glob("C-*/manifest.json"))) < 10:
    errors.append("reference run archive incomplete")

# Model profiles: populated but no fabricated production selection required.
profiles = load(ROOT / "config/model_profiles.json")
if not profiles.get("profiles"):
    errors.append("model profile registry empty")
for p in profiles.get("profiles", []):
    if p.get("measurement_status") == "unmeasured" and p.get("production_eligible"):
        errors.append(
            f"{p.get('model_id')}: unmeasured profile cannot be production eligible"
        )

# State and policies.
sm = load(ROOT / "policies/run_state_machine.json")
states = set(sm.get("states", []))
for a, bs in sm.get("transitions", {}).items():
    if a not in states or set(bs) - states:
        errors.append("invalid run state graph")
for required in (
    "action_policy",
    "publication_policy",
    "employment_policy",
    "legal_policy",
    "financial_policy",
    "osint_policy",
    "security_testing_policy",
    "data_handling_policy",
    "skill_permission_policy",
    "role_authority_profiles",
):
    if not (ROOT / "policies" / f"{required}.json").exists():
        errors.append(f"missing policy {required}")
if not (ROOT / "policies/gates.json").exists():
    errors.append("missing reusable gate registry")

# Generated graph and body-audit integrity.
graph = load(ROOT / "config/capability_graph.json")
if graph.get("suite_version") != version:
    errors.append("capability graph suite version mismatch")
if len(graph.get("nodes", [])) != len(items):
    errors.append("capability graph node count mismatch")
for edge in graph.get("edges", []):
    if edge.get("from") == edge.get("to"):
        errors.append(f"capability graph self-edge: {edge}")
    if edge.get("from") not in ids or edge.get("to") not in ids:
        errors.append(f"capability graph unknown endpoint: {edge}")
expected_requires = {
    (dep, m["prompt_id"], "requires")
    for _, m, _ in items
    for dep in (m.get("requires") or [])
}
expected_handoffs = {
    (m["prompt_id"], m.get("paired_prompt_id"), edge_type)
    for _, m, _ in items
    if m["prompt_role"] == "investigative" and m.get("paired_prompt_id")
    for edge_type in ("handoff", "plan_review_gate", "exact_twin_execution")
}
actual_edges = {
    (e.get("from"), e.get("to"), e.get("type")) for e in graph.get("edges", [])
}
if actual_edges != expected_requires | expected_handoffs:
    errors.append(
        "capability graph edges do not match canonical prompt frontmatter and exact-twin review policy"
    )
audit = load(ROOT / "BODY_QUALITY_AUDIT.json")
if audit.get("status") != "pass":
    errors.append("prompt body quality audit is not passing")
if audit.get("prompt_count") != len(items):
    errors.append("prompt body quality audit count mismatch")
if audit.get("completion_criteria", {}).get("unique_blocks") != len(items):
    errors.append("prompt body completion criteria are not unique")
if audit.get("tool_policy", {}).get("present") != len(items):
    errors.append("prompt body tool-policy coverage incomplete")
if audit.get("runtime_markers", {}).get("fully_implemented") != len(items):
    errors.append("prompt body runtime-marker coverage incomplete")
if audit.get("pairs", {}).get("duplicated_verification_blocks") != 0:
    errors.append("prompt body pair verification duplication detected")

# Template, logging, and platform integrity.
template_registry = load(ROOT / "config/template_registry.json")
template_ids = {x.get("template_id") for x in template_registry.get("templates", [])}
used_templates = set()
for _, m, body in items:
    if not m.get("template_routes"):
        errors.append(f"{m.get('prompt_id')}: missing template routes")
    if (
        set(m.get("template_routes", []))
        | set(m.get("conditional_template_routes", []))
    ) - template_ids:
        errors.append(f"{m.get('prompt_id')}: unknown template route")
    if set(m.get("template_routes", [])) & set(
        m.get("conditional_template_routes", [])
    ):
        errors.append(
            f"{m.get('prompt_id')}: duplicate required/conditional template route"
        )
    if len(m.get("template_routes", [])) > 8:
        errors.append(f"{m.get('prompt_id')}: excessive unconditional template routes")
    if "<template_routing>" not in body:
        errors.append(f"{m.get('prompt_id')}: missing template routing contract")
    used_templates.update(m.get("template_routes", []))
    used_templates.update(m.get("conditional_template_routes", []))
if used_templates != template_ids:
    errors.append(
        "template registry contains unused templates or routes are incomplete"
    )
for t in template_registry.get("templates", []):
    tp = ROOT / t.get("path", "")
    if not tp.exists() or len(tp.read_text(encoding="utf-8").splitlines()) < 45:
        errors.append(f"missing or shallow template {t.get('template_id')}")
for stem in {p.stem for p in (ROOT / "tools").glob("*.sh")} | {
    p.stem for p in (ROOT / "tools").glob("*.ps1")
}:
    if (
        not (ROOT / "tools" / f"{stem}.sh").exists()
        or not (ROOT / "tools" / f"{stem}.ps1").exists()
    ):
        errors.append(f"cross-platform script parity missing for {stem}")
for required in (
    "template_usage_policy",
    "logging_policy",
    "cross_platform_tooling_policy",
    "tui_policy",
    "documentation_system_policy",
    "artifact_export_policy",
):
    if not (ROOT / "policies" / f"{required}.json").exists():
        errors.append(f"missing policy {required}")
for required in (
    "MD_MASTERY_MANUAL",
    "TEMPLATE_SYSTEM_GUIDE",
    "LOGGING_AND_TELEMETRY_GUIDE",
    "CROSS_PLATFORM_TOOLING_GUIDE",
    "TUI_AND_OPERATOR_EXPERIENCE_GUIDE",
    "INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE",
):
    p = ROOT / "docs" / f"{required}.md"
    if not p.exists() or len(p.read_text(encoding="utf-8").splitlines()) < (
        700
        if required == "MD_MASTERY_MANUAL"
        else 20
        if required == "INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE"
        else 80
    ):
        errors.append(f"missing or shallow manual {required}")

# Root/manual/CI requirements.
required_root = [
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "VERSION",
    "RELEASE_ID",
    "docs/MANUALS.md",
    "docs/PROMPT_CATALOG.md",
    "PROMPT_EXECUTION_ORDER.md",
    "docs/PROMPT_SUITE_CONVENTIONS.md",
    "docs/PROMPT_STRUCTURE_STANDARD.md",
    "docs/PROMPT_ENGINEERING_METHODS.md",
    "docs/RESEARCH_BASIS.md",
    "docs/CAPABILITY_ARCHITECTURE.md",
    "docs/EVIDENCE_LANES.md",
    "docs/SKILL_ROUTING.md",
    "docs/RECOMMENDED_SKILL_STACKS.md",
    "docs/SKILL_INSTALL_COMMANDS.md",
    "docs/GSTACK_INTEGRATION.md",
    "docs/SECURITY_BOUNDARIES.md",
    "docs/COVERAGE_INDEX.md",
    "catalog.json",
    "SCENARIO_CATALOG.json",
    "config/capability_graph.json",
    "skill_registry.json",
    "config/skills.lock.json",
    "config/department_packs.json",
    "policies/assurance_profiles.json",
    "policies/run_state_machine.json",
    "config/model_profiles.json",
    "tools/md.py",
    "tools/keyword_context.py",
    "tools/prompt_lifecycle.py",
    "tools/add_prompt.py",
    "tools/add-prompt.sh",
    "tools/add-prompt.ps1",
    "tools/run_evaluations.py",
    "evaluations/route_confusion.json",
    "evaluations/exact_twin_negative_cases.json",
    "tools/run_model_benchmarks.py",
    "tools/resolve_skill_lock.py",
    "tools/check_skill_lock.py",
    "tools/run_tests.py",
    "tools/run_skill_conformance.py",
    "tools/run_pair_comparison.py",
    "tools/promote_golden_run.py",
    "tools/build_crosswalk.py",
    "tools/audit_prompt_bodies.py",
    "tools/build_capability_graph.py",
    "tools/refine_prompt_bodies.py",
    "tools/apply_exact_twin_review_gate.py",
    "tools/rebuild_suite_metadata.py",
    "tools/check_documentation_links.py",
    "tools/register_local_skill_dual.ps1",
    "tools/install_skill_dual.ps1",
    "tools/sync_agent_guidance.py",
    "tools/sync-agent-guidance.ps1",
    "tools/sync-agent-guidance.cmd",
    "tools/sync-agent-guidance.sh",
    "tools/platform_dispatch.py",
    "tools/template_router.py",
    "tools/validate_templates.py",
    "tools/check_script_parity.py",
    "tools/telemetry.py",
    "tools/tui.py",
    "tools/tool_runtime.py",
    "tools/log_query.py",
    "tools/agent_paths.py",
    "tools/release_meta.py",
    "tools/check_release_consistency.py",
    "tools/check_generated_reproducibility.py",
    "tools/install.py",
    "tools/install.sh",
    "tools/install.ps1",
    "compatibility/agent_skill_paths.json",
    "policies/project_installation_policy.json",
    "schemas/installation_receipt.schema.json",
    "schemas/prompt_addition_request.schema.json",
    "schemas/prompt_addition_preview.schema.json",
    "schemas/prompt_addition_receipt.schema.json",
    "policies/prompt_addition_policy.json",
    "docs/PROMPT_ADDITION_AND_REGISTRATION_GUIDE.md",
    "config/template_registry.json",
    "policies/template_routing_policy.json",
    "schemas/auto_orchestration_request.schema.json",
    "schemas/visual_asset_brief.schema.json",
    "schemas/skill_creation_spec.schema.json",
    "schemas/plan_review_receipt.schema.json",
    "schemas/execution_consent_receipt.schema.json",
    "schemas/paired_workflow.schema.json",
    "policies/skill_acquisition_policy.json",
    "policies/agent_guidance_policy.json",
    "policies/auto_prompt_policy.json",
    "policies/loop_execution_policy.json",
    "config/installed_skills_inventory.json",
    "config/skill_aliases.json",
    "requirements-dev.txt",
    ".github/workflows/validate.yml",
    ".pre-commit-config.yaml",
    "LICENSE",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "SUPPORT.md",
    "CODE_OF_CONDUCT.md",
]
for name in required_root:
    if not (ROOT / name).exists():
        errors.append(f"missing required artifact {name}")
manuals = [
    "USER_MANUAL",
    "OPERATOR_GUIDE",
    "ARCHITECTURE_GUIDE",
    "EVALUATION_MANUAL",
    "MODEL_ROUTING_GUIDE",
    "SKILL_SUPPLY_CHAIN_GUIDE",
    "CI_AND_TESTING_GUIDE",
    "COMPATIBILITY_AND_IDENTITY_GUIDE",
    "AGENT_LIBRARY_INTEGRATION_GUIDE",
    "RECOVERY_AND_ROLLBACK_GUIDE",
    "TELEMETRY_AND_OBSERVABILITY_GUIDE",
    "SCENARIO_AUTHORING_GUIDE",
    "CONTRIBUTOR_GUIDE",
    "TROUBLESHOOTING_GUIDE",
    "SECURITY_OPERATIONS_GUIDE",
    "PROMPT_BODY_AUTHORING_GUIDE",
    "COMPLETION_CRITERIA_GUIDE",
    "TOOL_POLICY_AND_AUTHORIZATION_GUIDE",
    "RUNTIME_MARKER_PROTOCOL",
    "PAIR_AUTHORING_AND_VERIFICATION_GUIDE",
    "EXECUTIVE_DECISION_RULES_GUIDE",
    "PROMPT_BODY_VALIDATION_GUIDE",
    "MANUAL_QUALITY_STANDARD",
    "AUTO_PROMPTS_AND_CONDITIONAL_ROUTING_GUIDE",
    "BOUNDED_LOOP_ORCHESTRATION_GUIDE",
    "GENERIC_SKILL_EXECUTION_GUIDE",
    "INSTALLED_SKILLS_INVENTORY_GUIDE",
    "VISUAL_ASSETS_INTEGRATION_GUIDE",
    "AUTO_ORCHESTRATION_RUNTIME_GUIDE",
    "LOCAL_SKILL_REGISTRATION_GUIDE",
    "ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE",
    "PLAN_REVIEW_AND_EXACT_TWIN_EXECUTION_GUIDE",
    "MD_MASTERY_MANUAL",
    "TEMPLATE_SYSTEM_GUIDE",
    "LOGGING_AND_TELEMETRY_GUIDE",
    "CROSS_PLATFORM_TOOLING_GUIDE",
    "TUI_AND_OPERATOR_EXPERIENCE_GUIDE",
    "INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE",
]
for m in manuals:
    p = ROOT / "docs" / f"{m}.md"
    if not p.exists() or len(p.read_text(encoding="utf-8").splitlines()) < 20:
        errors.append(f"missing or shallow manual {m}")

# Root agent guidance and keyword lookup integrity.
agent_policy = load(ROOT / "policies/agent_guidance_policy.json")
required_agent_files = {"AGENTS.md", "CLAUDE.md"}
if set(agent_policy.get("default_agent_files", [])) != required_agent_files:
    errors.append(
        "agent guidance default file set must contain only AGENTS.md and CLAUDE.md"
    )
if set(agent_policy.get("supported_agent_files", [])) != required_agent_files:
    errors.append(
        "agent guidance supported file set must contain only AGENTS.md and CLAUDE.md"
    )
for excluded in ("CODEX.md", "PI.md", "HERMES.md", "OPENCODE.md"):
    if (ROOT / excluded).exists():
        errors.append(f"intentionally excluded root agent file is present: {excluded}")
try:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "sync_agent_guidance", ROOT / "tools/sync_agent_guidance.py"
    )
    sync_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sync_module)
    rendered = sync_module.render_guidance(ROOT, ROOT, "AGENTS.md")
    for token in (
        "tools/md.py route",
        "tools/md.py compare",
        "tools/md.py lookup",
        "tools/md.py explain",
        "MD-191",
        "MD-198",
        "visual-assets",
        "strudel",
        "smallest coherent graph",
        "Do not load every prompt",
        "exact execution twin",
        "pair-status",
        "MD-199",
        "add_prompt.py",
        "tools/keyword_context.py",
        "Do not read prompt bodies during intent selection",
    ):
        if token not in rendered:
            errors.append(f"agent guidance block missing {token}")
    if (
        rendered.count(sync_module.BEGIN_MARKER) != 1
        or rendered.count(sync_module.END_MARKER) != 1
    ):
        errors.append("agent guidance managed markers invalid")
except Exception as e:
    errors.append(f"agent guidance validation failed: {e}")
try:
    import importlib.util

    spec = importlib.util.spec_from_file_location("md_runtime", ROOT / "tools/md.py")
    runtime_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime_module)
    exact = runtime_module.lookup("MD-29", limit=3)
    if not exact.get("results") or exact["results"][0].get("id") != "MD-29":
        errors.append("MD keyword lookup exact-ID resolution failed")
    visual = runtime_module.lookup("visual assets infographic presentation", limit=10)
    if not any(
        x.get("id") in {"C-109", "MD-104", "visual-assets"}
        for x in visual.get("results", [])
    ):
        errors.append("MD keyword lookup visual route failed")
    routed = runtime_module.route_intent("MD advanced audit fix verify repository")
    if routed.get("selection", {}).get("targets") != ["C-108"]:
        errors.append("MD keyword-context route selection failed")
    combined = runtime_module.route_intent("md combine visual assets and strudel")
    if combined.get("selection", {}).get("targets") != ["C-109", "C-110"]:
        errors.append("MD keyword-context workflow composition failed")
except Exception as e:
    errors.append(f"MD keyword lookup validation failed: {e}")

# Paired plan-review and exact-twin runtime integrity.
state_machine = load(ROOT / "policies/run_state_machine.json")
for state in (
    "plan_review_pending",
    "plan_revision_pending",
    "execution_consent_pending",
):
    if state not in state_machine.get("states", []):
        errors.append(f"run state machine missing {state}")
try:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "md_pair_runtime", ROOT / "tools/md.py"
    )
    pair_runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pair_runtime)
    for _, m, _ in items:
        if m.get("prompt_role") != "investigative" or not m.get("paired_prompt_id"):
            continue
        resolved = pair_runtime.exact_execution_twin(m["prompt_id"])
        if resolved.get("execution_prompt_id") != m.get(
            "paired_prompt_id"
        ) or not resolved.get("exact_twin_only"):
            errors.append(f"{m['prompt_id']}: runtime exact twin resolution drift")
        disposition = pair_runtime.pair_review_disposition(
            m["prompt_id"], True, "approved"
        )
        if (
            disposition.get("execution_prompt_id") != m.get("paired_prompt_id")
            or disposition.get("next_action") != "ask_execution_consent"
        ):
            errors.append(
                f"{m['prompt_id']}: review disposition does not ask exact twin consent"
            )
except Exception as e:
    errors.append(f"paired review runtime validation failed: {e}")

# Documentation link integrity.
try:
    from check_documentation_links import find_broken_relative_links

    broken_links = find_broken_relative_links(ROOT)
    for issue in broken_links:
        errors.append(
            f"broken documentation link {issue['file']}:{issue['line']} -> {issue['target']} ({issue['reason']})"
        )
except Exception as e:
    errors.append(f"documentation link validation failed: {e}")

# Output collisions.
seen = {}
for _, m, _ in items:
    paths = [m["output_contract"]["primary_artifact"]["path"]] + [
        x["path"] for x in m["output_contract"].get("supporting_artifacts", [])
    ]
    for p in paths:
        if p in seen and seen[p] != m["prompt_id"]:
            errors.append(f"output collision {p}: {seen[p]} {m['prompt_id']}")
        seen[p] = m["prompt_id"]

# Active release and distributable path consistency.
try:
    from check_release_consistency import check as check_release_consistency

    release_consistency = check_release_consistency(ROOT)
    if release_consistency.get("status") != "pass":
        errors.append(f"release consistency failed: {release_consistency}")
except Exception as e:
    errors.append(f"release consistency validation failed: {e}")

# Generated-artifact reproducibility.
try:
    from check_generated_reproducibility import check as check_generated_reproducibility

    reproducibility = check_generated_reproducibility(ROOT)
    if reproducibility.get("status") != "pass":
        errors.append(f"generated artifact reproducibility failed: {reproducibility}")
except Exception as e:
    errors.append(f"generated artifact reproducibility validation failed: {e}")

# Manifest integrity.
manifest_path = ROOT / "MANIFEST.json"
if manifest_path.exists():
    manifest = load(manifest_path)
    listed = {x["path"]: x for x in manifest.get("files", [])}
    actual_files = {}
    from build_manifest import iter_manifest_files

    for f in iter_manifest_files(ROOT):
        data = f.read_bytes().replace(b"\r\n", b"\n")
        rel = f.relative_to(ROOT).as_posix()
        actual_files[rel] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        }
    if set(listed) != set(actual_files):
        errors.append("manifest path set mismatch")
    for rel, info in actual_files.items():
        if rel in listed and (
            listed[rel].get("sha256") != info["sha256"]
            or listed[rel].get("bytes") != info["bytes"]
        ):
            errors.append(f"manifest mismatch: {rel}")
else:
    errors.append("missing MANIFEST.json")

# Honest status separates proof surfaces.
eval_status = (
    load(ROOT / "EVALUATION_STATUS.json")
    if (ROOT / "EVALUATION_STATUS.json").exists()
    else {}
)
status = {
    "status": "pass" if not errors else "fail",
    "claim_scope": "prompt-body semantic contracts, structural integrity, deterministic runtime tests, fixture coverage, current identity contracts, CI configuration, lock safety, and manifest integrity",
    "suite_version": version,
    "prompt_count": len(items),
    "true_pairs": expected["pair"],
    "composite_scenarios": len(sc.get("composite_scenarios", [])),
    "prompt_fixture_files": fixture_actual.get("prompt"),
    "scenario_fixture_files": fixture_actual.get("scenario"),
    "registered_skills": len(skill_ids),
    "installable_skills": len(installable),
    "resolved_skill_locks": sum(x.get("lock_status") == "resolved" for x in entries),
    "production_eligible_measured_models": sum(
        p.get("measurement_status") == "measured" and p.get("production_eligible")
        for p in profiles.get("profiles", [])
    ),
    "prompt_body_audit_status": audit.get("status", "not_run"),
    "completion_criteria_unique": audit.get("completion_criteria", {}).get(
        "unique_blocks"
    ),
    "tool_policy_coverage": audit.get("tool_policy", {}).get("present"),
    "runtime_marker_coverage": audit.get("runtime_markers", {}).get(
        "fully_implemented"
    ),
    "external_behavioral_status": eval_status.get("status", "not_run"),
    "limitations": [
        "Structural pass does not certify live model quality.",
        "Unresolved skill locks intentionally block automatic use.",
        "Human-reviewed golden runs remain pending until real runs are promoted.",
    ],
    "errors": errors,
    "warnings": warnings,
}
(ROOT / "VALIDATION.json").write_text(json.dumps(status, indent=2) + "\n")
print(json.dumps(status, indent=2))
sys.exit(1 if errors else 0)
