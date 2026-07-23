from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"


def load_prompts():
    rows = []
    for path in sorted(PROMPTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        _, frontmatter, body = text.split("---", 2)
        rows.append((path, yaml.safe_load(frontmatter), body))
    return rows


def block(body: str, tag: str) -> str | None:
    match = re.search(fr"<{tag}>\s*(.*?)\s*</{tag}>", body, re.S)
    return match.group(1).strip() if match else None


def normalized(value: str) -> str:
    return " ".join(value.split()).lower()


def test_no_prompt_requires_or_contract_references_itself():
    offenders = []
    for path, meta, _ in load_prompts():
        prompt_id = meta["prompt_id"]
        if prompt_id in (meta.get("requires") or []):
            offenders.append(f"{path.name}:requires")
        if prompt_id in (meta.get("contract_refs") or []):
            offenders.append(f"{path.name}:contract_refs")
    assert not offenders, offenders


def test_every_prompt_has_canonical_authorization_and_tool_policy():
    missing = []
    noncanonical = []
    for path, _, body in load_prompts():
        if block(body, "authorization_boundary") is None:
            missing.append(f"{path.name}:authorization_boundary")
        if block(body, "tool_policy") is None:
            missing.append(f"{path.name}:tool_policy")
        if "<security_execution_boundary>" in body:
            noncanonical.append(path.name)
    assert not missing, missing
    assert not noncanonical, noncanonical


def test_runtime_markers_are_required_by_every_prompt_body():
    required = {
        "@EVIDENCE:{id}",
        "?UNKNOWN:{id}",
        "#FINDING:{id}",
        "+ACTION:{id}",
        "=VERIFY:{id}",
        "!STOP:{reason}",
    }
    missing = {}
    for path, _, body in load_prompts():
        marker_block = block(body, "runtime_markers")
        if marker_block is None:
            missing[path.name] = sorted(required)
            continue
        absent = sorted(marker for marker in required if marker not in marker_block)
        if absent:
            missing[path.name] = absent
    assert not missing, missing


def test_completion_criteria_are_present_specific_and_not_boilerplate():
    rows = load_prompts()
    banned = {
        "complete only when the outcome is evidenced, authorized, and honestly closed.",
        "complete only when the artifact satisfies the declared decision or workflow, passes the domain gates above, respects authority and evidence boundaries, and records verification evidence plus unresolved residuals.",
        "complete only when the requested artifact is accurate for its evidence lane, internally coherent, audience-fit, quality-checked, and accompanied by explicit unknowns or residuals.",
        "complete only when the production package satisfies the frozen brief, preserves evidence integrity, passes editorial and format-specific review, and records unresolved claims or production dependencies.",
    }
    values = []
    invalid = []
    for path, meta, body in rows:
        criteria = block(body, "completion_criteria")
        if criteria is None:
            invalid.append(f"{path.name}:missing")
            continue
        norm = normalized(criteria)
        values.append(norm)
        if norm in banned:
            invalid.append(f"{path.name}:boilerplate")
        bullet_count = sum(1 for line in criteria.splitlines() if line.strip().startswith("- "))
        if bullet_count < 3:
            invalid.append(f"{path.name}:fewer-than-3-criteria")
        # A criterion must name at least one prompt-specific term, artifact, or paired handoff.
        title_terms = {
            word.lower()
            for word in re.findall(r"[A-Za-z][A-Za-z0-9-]{4,}", meta["title"])
            if word.lower() not in {"and", "with", "from", "into", "authorized", "investigation", "execution", "verification", "production"}
        }
        artifact_names = {
            Path(meta["output_contract"]["primary_artifact"]["path"]).stem.lower()
        }
        if not any(term in norm for term in title_terms | artifact_names):
            invalid.append(f"{path.name}:not-task-specific")
        if "=verify:{id}" not in norm:
            invalid.append(f"{path.name}:missing-verify-marker")
    duplicates = {value: count for value, count in Counter(values).items() if count > 2}
    assert not invalid, invalid
    assert not duplicates, duplicates


def test_all_executive_prompts_have_decision_rules():
    missing = []
    for path, meta, body in load_prompts():
        if meta["prompt_role"] == "executive" and block(body, "decision_rules") is None:
            missing.append(path.name)
    assert not missing, missing


def test_pair_verification_is_referenced_not_duplicated():
    rows = load_prompts()
    by_id = {meta["prompt_id"]: (path, meta, body) for path, meta, body in rows}
    failures = []
    for path, meta, body in rows:
        if meta["prompt_role"] != "investigative" or not meta.get("paired_prompt_id"):
            continue
        executive_path, _, executive_body = by_id[meta["paired_prompt_id"]]
        investigation_verification = block(body, "verification_design")
        executive_verification = block(executive_body, "verification")
        reference = block(executive_body, "verification_reference")
        if reference is None:
            failures.append(f"{executive_path.name}:missing-reference")
        if investigation_verification and executive_verification and normalized(investigation_verification) == normalized(executive_verification):
            failures.append(f"{executive_path.name}:duplicates-investigator")
    assert not failures, failures


def test_body_quality_audit_report_matches_required_invariants():
    import json
    report_path = ROOT / "BODY_QUALITY_AUDIT.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "pass"
    assert report["prompt_count"] == len(list((ROOT / "prompts").glob("*.md")))
    assert report["completion_criteria"]["unique_blocks"] == report["prompt_count"]
    assert report["completion_criteria"]["boilerplate_blocks"] == 0
    assert report["tool_policy"]["present"] == report["prompt_count"]
    assert report["runtime_markers"]["fully_implemented"] == report["prompt_count"]
    assert report["authorization_boundary"]["canonical"] == report["prompt_count"]
    assert report["authorization_boundary"]["obsolete_security_execution_boundary"] == 0
    assert report["executive_prompts"]["with_decision_rules"] == 32
    assert report["pairs"]["duplicated_verification_blocks"] == 0
    assert report["pairs"]["planners_with_review_gate"] == 32
    assert report["pairs"]["executors_with_reviewed_handoff_authority"] == 32
    assert report["pairs"]["mapping_errors"] == []
    assert report["self_dependencies"] == []


def test_capability_graph_has_no_self_dependency_edges():
    import json
    graph = json.loads((ROOT / "config/capability_graph.json").read_text(encoding="utf-8"))
    offenders = [edge for edge in graph["edges"] if edge.get("from") == edge.get("to")]
    assert not offenders, offenders


def test_prompt_body_mutation_definitions_cover_regressions():
    import json
    mutations = set(json.loads((ROOT / "evaluations/mutation_tests.json").read_text(encoding="utf-8"))["mutations"])
    required = {
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
    assert required <= mutations


def test_every_investigative_pair_has_review_and_exact_twin_gate():
    rows = load_prompts()
    by_id = {meta["prompt_id"]: (path, meta, body) for path, meta, body in rows}
    failures = []
    for path, meta, body in rows:
        if meta["prompt_role"] != "investigative" or not meta.get("paired_prompt_id"):
            continue
        twin_id = meta["paired_prompt_id"]
        twin = by_id.get(twin_id)
        gate = block(body, "plan_review_and_execution_gate")
        if gate is None:
            failures.append(f"{path.name}:missing-plan-review-gate")
            continue
        normalized_gate = normalized(gate)
        for required_text in (
            twin_id.lower(),
            "present the completed plan",
            "user review",
            "requested changes",
            "re-freeze",
            "execution consent",
            "exact execution twin",
        ):
            if required_text not in normalized_gate:
                failures.append(f"{path.name}:missing:{required_text}")
        if not meta.get("plan_review_required"):
            failures.append(f"{path.name}:frontmatter-plan-review-required")
        if not meta.get("execution_consent_required"):
            failures.append(f"{path.name}:frontmatter-execution-consent-required")
        if not meta.get("exact_twin_only"):
            failures.append(f"{path.name}:frontmatter-exact-twin-only")
        if not twin:
            failures.append(f"{path.name}:missing-twin")
    assert not failures, failures


def test_every_executive_pair_accepts_only_reviewed_handoff_from_exact_planner():
    rows = load_prompts()
    failures = []
    for path, meta, body in rows:
        if meta["prompt_role"] != "executive":
            continue
        planner_id = meta.get("paired_prompt_id")
        gate = block(body, "reviewed_handoff_authority")
        if gate is None:
            failures.append(f"{path.name}:missing-reviewed-handoff-authority")
            continue
        normalized_gate = normalized(gate)
        for required_text in (
            planner_id.lower(),
            "reviewed handoff",
            "execution consent",
            "reject",
            "exact paired planner",
        ):
            if required_text not in normalized_gate:
                failures.append(f"{path.name}:missing:{required_text}")
        if not meta.get("reviewed_handoff_required"):
            failures.append(f"{path.name}:frontmatter-reviewed-handoff-required")
        if not meta.get("execution_consent_required"):
            failures.append(f"{path.name}:frontmatter-execution-consent-required")
        if not meta.get("exact_twin_only"):
            failures.append(f"{path.name}:frontmatter-exact-twin-only")
    assert not failures, failures
