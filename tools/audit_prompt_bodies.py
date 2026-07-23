#!/usr/bin/env python3
from __future__ import annotations
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)


from collections import Counter
from pathlib import Path
import argparse
import json
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
JSON_PATH = ROOT / "BODY_QUALITY_AUDIT.json"
MD_PATH = ROOT / "BODY_QUALITY_AUDIT.md"
REQUIRED_MARKERS = (
    "@EVIDENCE:{id}",
    "?UNKNOWN:{id}",
    "#FINDING:{id}",
    "+ACTION:{id}",
    "=VERIFY:{id}",
    "!STOP:{reason}",
)
BANNED_COMPLETION = {
    "complete only when the outcome is evidenced, authorized, and honestly closed.",
    "complete only when the artifact satisfies the declared decision or workflow, passes the domain gates above, respects authority and evidence boundaries, and records verification evidence plus unresolved residuals.",
    "complete only when the requested artifact is accurate for its evidence lane, internally coherent, audience-fit, quality-checked, and accompanied by explicit unknowns or residuals.",
    "complete only when the production package satisfies the frozen brief, preserves evidence integrity, passes editorial and format-specific review, and records unresolved claims or production dependencies.",
}


def block(body: str, tag: str) -> str | None:
    match = re.search(fr"<{tag}>\s*(.*?)\s*</{tag}>", body, re.S)
    return match.group(1).strip() if match else None


def normalized(value: str | None) -> str:
    return " ".join((value or "").split()).lower()


def load_rows():
    rows = []
    for path in sorted(PROMPTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        _, frontmatter, body = text.split("---", 2)
        rows.append((path, yaml.safe_load(frontmatter), body))
    return rows


def build_report() -> dict:
    rows = load_rows()
    by_id = {meta["prompt_id"]: (path, meta, body) for path, meta, body in rows}
    completion_values = Counter()
    missing_markers = []
    missing_tool_policy = []
    missing_authorization = []
    obsolete_authorization = []
    missing_exec_rules = []
    missing_verification_reference = []
    duplicate_verification = []
    missing_plan_review_gates = []
    missing_reviewed_handoff_authority = []
    pair_mapping_errors = []
    self_dependencies = []
    budget_excess = []
    prompt_details = []

    for path, meta, body in rows:
        pid = meta["prompt_id"]
        completion = block(body, "completion_criteria")
        completion_values[normalized(completion)] += 1
        if block(body, "tool_policy") is None:
            missing_tool_policy.append(pid)
        if block(body, "authorization_boundary") is None:
            missing_authorization.append(pid)
        if "<security_execution_boundary>" in body:
            obsolete_authorization.append(pid)
        marker_block = block(body, "runtime_markers") or ""
        absent = [marker for marker in REQUIRED_MARKERS if marker not in marker_block]
        if absent:
            missing_markers.append({"prompt_id": pid, "missing": absent})
        if pid in (meta.get("requires") or []):
            self_dependencies.append({"prompt_id": pid, "field": "requires"})
        if pid in (meta.get("contract_refs") or []):
            self_dependencies.append({"prompt_id": pid, "field": "contract_refs"})
        if meta["prompt_role"] == "executive":
            if block(body, "decision_rules") is None:
                missing_exec_rules.append(pid)
            if block(body, "verification_reference") is None:
                missing_verification_reference.append(pid)
            planner_id = meta.get("paired_prompt_id")
            gate = normalized(block(body, "reviewed_handoff_authority"))
            if not gate or not planner_id or planner_id.lower() not in gate:
                missing_reviewed_handoff_authority.append(pid)
            if not (meta.get("reviewed_handoff_required") and meta.get("execution_consent_required") and meta.get("exact_twin_only")):
                pair_mapping_errors.append({"prompt_id": pid, "error": "executive frontmatter does not require reviewed exact-twin handoff"})
        if meta["prompt_role"] == "investigative" and meta.get("paired_prompt_id"):
            twin_id = meta["paired_prompt_id"]
            gate = normalized(block(body, "plan_review_and_execution_gate"))
            required = (twin_id.lower(), "user review", "requested changes", "re-freeze", "execution consent", "exact execution twin")
            if not gate or any(value not in gate for value in required):
                missing_plan_review_gates.append(pid)
            if not (meta.get("plan_review_required") and meta.get("execution_consent_required") and meta.get("exact_twin_only")):
                pair_mapping_errors.append({"prompt_id": pid, "error": "planner frontmatter does not require review and exact-twin consent"})
        body_words = len(re.findall(r"\b\w+[\w-]*\b", body))
        budget = (meta.get("complexity_budget") or {}).get("maximum_body_words")
        if budget and body_words > budget:
            budget_excess.append({"prompt_id": pid, "words": body_words, "budget": budget})
        prompt_details.append(
            {
                "prompt_id": pid,
                "role": meta["prompt_role"],
                "completion_bullets": sum(
                    1 for line in (completion or "").splitlines() if line.strip().startswith("- ")
                ),
                "body_words": body_words,
                "body_word_budget": budget,
                "has_tool_policy": block(body, "tool_policy") is not None,
                "has_runtime_markers": not absent,
                "has_authorization_boundary": block(body, "authorization_boundary") is not None,
            }
        )

    pair_count = 0
    for _, meta, body in rows:
        if meta["prompt_role"] != "investigative" or not meta.get("paired_prompt_id"):
            continue
        pair_count += 1
        executive_body = by_id[meta["paired_prompt_id"]][2]
        investigator_verification = block(body, "verification_design")
        executive_verification = block(executive_body, "verification")
        if (
            investigator_verification
            and executive_verification
            and normalized(investigator_verification) == normalized(executive_verification)
        ):
            duplicate_verification.append(
                {"investigative": meta["prompt_id"], "executive": meta["paired_prompt_id"]}
            )

    boilerplate_blocks = sum(count for value, count in completion_values.items() if value in BANNED_COMPLETION)
    duplicate_completion_blocks = [
        {"normalized_block": value, "count": count}
        for value, count in completion_values.items()
        if count > 2
    ]
    errors = []
    if boilerplate_blocks:
        errors.append(f"found {boilerplate_blocks} boilerplate completion blocks")
    if len(completion_values) != len(rows):
        errors.append("completion criteria are not unique per prompt")
    if missing_tool_policy:
        errors.append(f"missing tool policy: {missing_tool_policy}")
    if missing_markers:
        errors.append(f"missing runtime markers: {missing_markers}")
    if missing_authorization or obsolete_authorization:
        errors.append("authorization boundary is missing or noncanonical")
    if missing_exec_rules:
        errors.append(f"executives missing decision rules: {missing_exec_rules}")
    if missing_verification_reference:
        errors.append(f"executives missing verification reference: {missing_verification_reference}")
    if duplicate_verification:
        errors.append(f"duplicated pair verification: {duplicate_verification}")
    if missing_plan_review_gates:
        errors.append(f"paired planners missing review gates: {missing_plan_review_gates}")
    if missing_reviewed_handoff_authority:
        errors.append(f"paired executors missing reviewed-handoff authority: {missing_reviewed_handoff_authority}")
    if pair_mapping_errors:
        errors.append(f"pair review mapping errors: {pair_mapping_errors}")
    if self_dependencies:
        errors.append(f"self dependencies: {self_dependencies}")
    if budget_excess:
        errors.append(f"complexity budget excess: {budget_excess}")

    return {
        "status": "pass" if not errors else "fail",
        "claim_scope": "static prompt-body structure and semantic contract coverage; no live model behavior is inferred",
        "prompt_count": len(rows),
        "completion_criteria": {
            "present": sum(1 for _, _, body in rows if block(body, "completion_criteria") is not None),
            "unique_blocks": len(completion_values),
            "maximum_duplicate_count": max(completion_values.values(), default=0),
            "boilerplate_blocks": boilerplate_blocks,
            "duplicate_blocks_over_two": duplicate_completion_blocks,
        },
        "tool_policy": {
            "present": len(rows) - len(missing_tool_policy),
            "missing": missing_tool_policy,
        },
        "runtime_markers": {
            "fully_implemented": len(rows) - len(missing_markers),
            "missing": missing_markers,
            "required_markers": list(REQUIRED_MARKERS),
        },
        "authorization_boundary": {
            "canonical": len(rows) - len(missing_authorization),
            "missing": missing_authorization,
            "obsolete_security_execution_boundary": len(obsolete_authorization),
            "obsolete_prompt_ids": obsolete_authorization,
        },
        "executive_prompts": {
            "total": sum(1 for _, meta, _ in rows if meta["prompt_role"] == "executive"),
            "with_decision_rules": sum(
                1
                for _, meta, body in rows
                if meta["prompt_role"] == "executive" and block(body, "decision_rules") is not None
            ),
            "with_verification_reference": sum(
                1
                for _, meta, body in rows
                if meta["prompt_role"] == "executive" and block(body, "verification_reference") is not None
            ),
            "missing_decision_rules": missing_exec_rules,
            "missing_verification_reference": missing_verification_reference,
        },
        "pairs": {
            "total": pair_count,
            "duplicated_verification_blocks": len(duplicate_verification),
            "duplicates": duplicate_verification,
            "planners_with_review_gate": pair_count - len(missing_plan_review_gates),
            "executors_with_reviewed_handoff_authority": pair_count - len(missing_reviewed_handoff_authority),
            "missing_plan_review_gates": missing_plan_review_gates,
            "missing_reviewed_handoff_authority": missing_reviewed_handoff_authority,
            "mapping_errors": pair_mapping_errors,
        },
        "self_dependencies": self_dependencies,
        "complexity_budget_excess": budget_excess,
        "errors": errors,
        "prompt_details": prompt_details,
    }


def render_markdown(report: dict) -> str:
    c = report["completion_criteria"]
    t = report["tool_policy"]
    r = report["runtime_markers"]
    a = report["authorization_boundary"]
    e = report["executive_prompts"]
    p = report["pairs"]
    lines = [
        "# Prompt Body Quality Audit",
        "",
        "This report is generated from the canonical prompt files. It measures static body-contract coverage and does not claim live language-model performance.",
        "",
        f"**Status:** `{report['status']}`",
        "",
        "## Summary",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| Prompt bodies inspected | {report['prompt_count']} |",
        f"| Completion criteria present | {c['present']} |",
        f"| Unique completion-criteria blocks | {c['unique_blocks']} |",
        f"| Boilerplate completion blocks | {c['boilerplate_blocks']} |",
        f"| Canonical tool policies | {t['present']} |",
        f"| Prompt bodies implementing all runtime markers | {r['fully_implemented']} |",
        f"| Canonical authorization boundaries | {a['canonical']} |",
        f"| Obsolete security-execution boundary tags | {a['obsolete_security_execution_boundary']} |",
        f"| Executive prompts with decision rules | {e['with_decision_rules']} / {e['total']} |",
        f"| Executive prompts with verification references | {e['with_verification_reference']} / {e['total']} |",
        f"| Pair verification blocks duplicated | {p['duplicated_verification_blocks']} |",
        f"| Paired planners with review and exact-twin gate | {p['planners_with_review_gate']} / {p['total']} |",
        f"| Paired executors with reviewed-handoff authority | {p['executors_with_reviewed_handoff_authority']} / {p['total']} |",
        f"| Self dependencies | {len(report['self_dependencies'])} |",
        f"| Complexity-budget violations | {len(report['complexity_budget_excess'])} |",
        "",
        "## Interpretation",
        "",
        "- Completion criteria are counted by normalized full-block text; a unique block does not by itself prove quality, but it prevents a small boilerplate set from satisfying the contract.",
        "- Runtime-marker coverage means each prompt explicitly instructs use of evidence, unknown, finding, action, verification, and stop identifiers.",
        "- Pair de-duplication requires the executive to reference the investigator's frozen acceptance criteria instead of repeating the same verification list.",
        "- Paired planners must present the plan for review, incorporate requested changes, re-freeze the handoff, and ask for consent to invoke only the exact reciprocal executor.",
        "- Tool-policy and authorization checks validate canonical tag presence and naming; live enforcement still belongs to the runtime policy engine.",
        "",
        "## Errors",
        "",
    ]
    if report["errors"]:
        lines.extend(f"- {error}" for error in report["errors"])
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Reproduce",
            "",
            "```bash",
            "python tools/audit_prompt_bodies.py --check",
            "pytest -q tests/test_prompt_body_quality.py",
            "python tools/validate_suite.py",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Compare generated audit to committed files.")
    args = parser.parse_args()
    report = build_report()
    markdown = render_markdown(report)
    if args.check:
        existing_json = json.loads(JSON_PATH.read_text(encoding="utf-8")) if JSON_PATH.exists() else None
        existing_md = MD_PATH.read_text(encoding="utf-8") if MD_PATH.exists() else None
        current_json = json.loads(json.dumps(report))
        ok = existing_json == current_json and existing_md == markdown
        print(json.dumps({"status": "pass" if ok else "fail", "audit_status": report["status"]}, indent=2))
        return 0 if ok and report["status"] == "pass" else 1
    JSON_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MD_PATH.write_text(markdown, encoding="utf-8")
    print(json.dumps({"status": report["status"], "prompt_count": report["prompt_count"]}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
