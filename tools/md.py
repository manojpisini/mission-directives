#!/usr/bin/env python3
"""MD deterministic planner, state helper, model router, and telemetry recorder.

This tool does not call a language model. It compiles and validates run contracts.
Live model execution belongs in an adapter that writes measured results back into
model_profiles.json and the run manifest.
"""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse, datetime, hashlib, json, math, os, re, sys, uuid
from pathlib import Path
from typing import Any
from jsonschema import validate as js_validate

try:
    from security_utils import (
        atomic_write_json,
        ensure_no_symlink_components,
        exclusive_lock,
    )
except ImportError:
    from tools.security_utils import (
        atomic_write_json,
        ensure_no_symlink_components,
        exclusive_lock,
    )
try:
    from telemetry import append_event
except ImportError:
    from tools.telemetry import append_event
try:
    from keyword_context import parse_keyword_context
except ImportError:
    from tools.keyword_context import parse_keyword_context

ROOT = Path(__file__).resolve().parents[1]
MODES = {
    "AUDIT_ONLY",
    "PLAN_ONLY",
    "DRAFT_ONLY",
    "APPLY_SAFE",
    "APPLY_APPROVED",
    "VERIFY_ONLY",
}
CONTROL = ["MD-00", "MD-01", "MD-03", "MD-04", "MD-02"]


def load_json(name: str) -> dict[str, Any]:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def data():
    cat = load_json("catalog.json")
    sc = load_json("SCENARIO_CATALOG.json")
    packs = load_json("config/department_packs.json")
    state = load_json("policies/run_state_machine.json")
    profiles = load_json("config/model_profiles.json")
    skills = load_json("skill_registry.json")
    locks = load_json("config/skills.lock.json")
    inventory = load_json("config/installed_skills_inventory.json")
    auto = load_json("policies/auto_prompt_policy.json")
    loop_policy = load_json("policies/loop_execution_policy.json")
    by_id = {p["prompt_id"]: p for p in cat["prompts"]}
    scenarios = {
        s["scenario_id"]: s for s in sc["atomic_scenarios"] + sc["composite_scenarios"]
    }
    return (
        cat,
        sc,
        packs,
        state,
        profiles,
        skills,
        locks,
        inventory,
        auto,
        loop_policy,
        by_id,
        scenarios,
    )


(
    CAT,
    SC,
    PACKS,
    STATE,
    PROFILES,
    SKILLS,
    LOCKS,
    INVENTORY,
    AUTO_POLICY,
    LOOP_POLICY,
    BY_ID,
    SCENARIOS,
) = data()
SKILL_ALIASES = load_json("config/skill_aliases.json").get("aliases", {})
AGENT_GUIDANCE_POLICY = load_json("policies/agent_guidance_policy.json")


def dedupe(items):
    return list(dict.fromkeys(items))


LOOKUP_STOPWORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "use",
    "using",
    "with",
    "md",
}
LOOKUP_EXPANSIONS = {
    "audit": {"audit", "review", "assessment", "investigation", "verification"},
    "fix": {
        "fix",
        "repair",
        "remediation",
        "resolution",
        "execution",
        "implementation",
    },
    "debug": {"debug", "debugging", "bug", "root", "cause", "triage"},
    "research": {"research", "evidence", "investigation", "analysis", "sources"},
    "report": {"report", "reporting", "document", "memo", "brief"},
    "visual": {
        "visual",
        "assets",
        "vector",
        "illustration",
        "infographic",
        "diagram",
        "presentation",
        "graphics",
    },
    "assets": {"assets", "visual", "vector", "illustration", "graphics"},
    "skill": {"skill", "skills", "adapter", "capability", "tool"},
    "loop": {"loop", "iteration", "iterative", "batch", "convergence", "repeat"},
    "productivity": {
        "productivity",
        "work",
        "system",
        "tasks",
        "knowledge",
        "planning",
    },
    "prompt": {
        "prompt",
        "prompts",
        "context",
        "engineering",
        "optimization",
        "addition",
        "authoring",
        "registration",
    },
    "new": {"new", "add", "addition", "create", "authoring", "registration"},
    "security": {"security", "threat", "vulnerability", "hardening", "risk"},
    "academic": {"academic", "paper", "scholarly", "research", "manuscript", "review"},
    "marketing": {"marketing", "campaign", "content", "seo", "audience", "growth"},
    "presentation": {"presentation", "slides", "deck", "visual"},
}


def _lookup_tokens(value: str) -> list[str]:
    raw = [x.lower() for x in re.findall(r"[A-Za-z0-9]+", value)]
    return [x for x in raw if x not in LOOKUP_STOPWORDS]


def _expanded_lookup_tokens(tokens: list[str]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        expanded.update(LOOKUP_EXPANSIONS.get(token, set()))
    return expanded


def _score_lookup_candidate(
    query: str,
    tokens: set[str],
    identifier: str,
    title: str,
    fields: list[tuple[str, int]],
) -> tuple[float, str, list[str]]:
    q = query.strip().lower()
    ident = identifier.lower()
    title_l = title.lower()
    if q == ident:
        return 100.0, "exact_id", [identifier]
    score = 0.0
    match_type = "keyword"
    matched = set()
    if q and q == title_l:
        score += 60
        match_type = "exact_title"
    elif q and q in title_l:
        score += 18
        match_type = "title_phrase"
    for text, weight in fields:
        words = set(_lookup_tokens(text))
        overlap = tokens & words
        if overlap:
            score += weight * len(overlap)
            matched.update(overlap)
    if tokens:
        score += 8 * (len(matched) / len(tokens))
    return score, match_type, sorted(matched)


def lookup(query: str, limit: int = 8, kind: str = "all") -> dict[str, Any]:
    """Deterministic keyword lookup across prompts, scenarios, packs, and skills.

    This is intentionally lexical and transparent. It is a fast discovery aid,
    not a substitute for `explain`, which remains the authority for a selected
    target's complete graph and constraints.
    """
    if kind not in {"all", "prompts", "scenarios", "packs", "skills"}:
        raise ValueError(f"Invalid lookup kind: {kind}")
    query = query.strip()
    if not query:
        raise ValueError("lookup query cannot be empty")
    base_tokens = _lookup_tokens(query)
    tokens = _expanded_lookup_tokens(base_tokens)
    results = []
    if kind in {"all", "prompts"}:
        for p in CAT["prompts"]:
            fields = [
                (p.get("title", ""), 10),
                (p.get("description", ""), 4),
                (p.get("category", ""), 7),
                (p.get("prompt_role", ""), 5),
                (p.get("prompt_type", ""), 5),
                (" ".join(p.get("tags", [])), 7),
                (" ".join(p.get("preferred_skills", [])), 8),
                (p.get("capability_id", ""), 6),
            ]
            score, match_type, matched = _score_lookup_candidate(
                query, tokens, p["prompt_id"], p["title"], fields
            )
            if score >= 8:
                results.append(
                    {
                        "kind": "prompt",
                        "id": p["prompt_id"],
                        "title": p["title"],
                        "description": p.get("description"),
                        "category": p.get("category"),
                        "role": p.get("prompt_role"),
                        "default_mode": p.get("default_mode"),
                        "path": p.get("canonical_path"),
                        "score": round(score, 3),
                        "match_type": match_type,
                        "matched_terms": matched,
                    }
                )
    if kind in {"all", "scenarios"}:
        for s in SC["composite_scenarios"]:
            fields = [
                (s.get("title", ""), 11),
                (s.get("purpose", ""), 5),
                (" ".join(s.get("prompts", [])), 1),
            ]
            score, match_type, matched = _score_lookup_candidate(
                query, tokens, s["scenario_id"], s["title"], fields
            )
            if score >= 8:
                results.append(
                    {
                        "kind": "scenario",
                        "id": s["scenario_id"],
                        "title": s["title"],
                        "description": s.get("purpose"),
                        "default_mode": s.get("default_mode"),
                        "score": round(score, 3),
                        "match_type": match_type,
                        "matched_terms": matched,
                    }
                )
    if kind in {"all", "packs"}:
        for pack_id, prompt_ids in PACKS["department_packs"].items():
            title = pack_id.replace("_", " ").title()
            prompt_titles = " ".join(
                BY_ID[x]["title"] for x in prompt_ids if x in BY_ID
            )
            score, match_type, matched = _score_lookup_candidate(
                query, tokens, pack_id, title, [(title, 8), (prompt_titles, 1)]
            )
            if score >= 10:
                results.append(
                    {
                        "kind": "pack",
                        "id": pack_id,
                        "title": title,
                        "description": "Department discovery profile; compile to a smaller task-specific graph before execution.",
                        "score": round(score, 3),
                        "match_type": match_type,
                        "matched_terms": matched,
                    }
                )
    if kind in {"all", "skills"}:
        for skill in SKILLS["skills"]:
            sid = skill["skill_id"]
            title = sid.replace("-", " ").title()
            fields = [
                (sid, 12),
                (skill.get("purpose", ""), 5),
                (" ".join(skill.get("prompt_routes", [])), 1),
                (skill.get("kind", ""), 2),
            ]
            score, match_type, matched = _score_lookup_candidate(
                query, tokens, sid, title, fields
            )
            if score >= 9:
                results.append(
                    {
                        "kind": "skill",
                        "id": sid,
                        "title": title,
                        "description": skill.get("purpose"),
                        "skill_status": skill_status(sid),
                        "score": round(score, 3),
                        "match_type": match_type,
                        "matched_terms": matched,
                    }
                )
    original = set(base_tokens)
    filtered = []
    for row in results:
        base_hits = original & set(row.get("matched_terms", []))
        coverage = (len(base_hits) / len(original)) if original else 0.0
        if (
            row.get("match_type") in {"exact_id", "exact_title", "title_phrase"}
            or coverage >= 0.34
        ):
            row["query_token_coverage"] = round(coverage, 3)
            filtered.append(row)
    results = filtered
    kind_priority = {"scenario": 0, "prompt": 1, "skill": 2, "pack": 3}
    results.sort(
        key=lambda row: (-row["score"], kind_priority.get(row["kind"], 9), row["id"])
    )
    results = results[: max(1, min(limit, 50))]
    if not results:
        return {
            "status": "no_confident_match",
            "query": query,
            "kind": kind,
            "results": [],
            "next_step": "Refine the terms or use MD-191 to ask one route-changing clarification question.",
        }
    top = results[0]["score"]
    for row in results:
        row["confidence"] = round(
            min(1.0, row["score"] / max(100.0, top if top else 100.0)), 3
        )
    return {
        "status": "matched",
        "query": query,
        "kind": kind,
        "result_count": len(results),
        "results": results,
        "next_step": f"Run `python tools/md.py explain {results[0]['id']}` before execution.",
    }


def _selection_type(targets: list[str], exact: bool = False) -> str:
    if exact:
        return "exact_target"
    if len(targets) > 1:
        return "workflow_graph"
    target = targets[0]
    if target in SCENARIOS:
        return "scenario"
    if target in PACKS["department_packs"]:
        return "department_pack"
    return "prompt"


def route_intent(request: str, limit: int = 8) -> dict[str, Any]:
    """Select the smallest explainable route from user intent metadata."""
    context = parse_keyword_context(request, AGENT_GUIDANCE_POLICY)
    if not context["lookup_query"]:
        return {
            "status": "no_confident_match",
            "context": context,
            "selection": {
                "type": "none",
                "targets": [],
                "reason": "the invocation contained no intent to route",
            },
            "alternatives": [],
            "next_step": "Provide task intent after MD, or provide an exact MD/C identifier.",
        }

    exact_target = context["exact_target"]
    if exact_target:
        try:
            resolve(exact_target)
        except ValueError:
            return {
                "status": "no_confident_match",
                "context": context,
                "selection": {
                    "type": "none",
                    "targets": [],
                    "reason": "explicit identifier is not registered",
                },
                "alternatives": [],
                "next_step": "Check the identifier or run lookup with descriptive terms.",
            }
        return {
            "status": "selected",
            "context": context,
            "selection": {
                "type": _selection_type([exact_target], exact=True),
                "targets": [exact_target],
                "reason": "explicit target identifier",
            },
            "alternatives": [],
            "explain_commands": [f"python tools/md.py explain {exact_target}"],
        }

    shortcut_targets = dedupe(
        target
        for shortcut in context["shortcuts"]
        for target in shortcut["targets"]
        if target in BY_ID or target in SCENARIOS or target in PACKS["department_packs"]
    )
    if shortcut_targets:
        reasons = [
            f"{row['keyword']} -> {row['target']}: {row['purpose']}"
            for row in context["shortcuts"]
            if row["targets"]
        ]
        return {
            "status": "selected",
            "context": context,
            "selection": {
                "type": _selection_type(shortcut_targets),
                "targets": shortcut_targets,
                "reason": "; ".join(reasons),
            },
            "alternatives": [],
            "explain_commands": [
                f"python tools/md.py explain {target}" for target in shortcut_targets
            ],
        }

    found = lookup(context["lookup_query"], limit=limit)
    routable = [
        row
        for row in found.get("results", [])
        if row["kind"] in {"prompt", "scenario", "department_pack"}
    ]
    minimum = AGENT_GUIDANCE_POLICY.get("selection_policy", {}).get(
        "minimum_lookup_score", 12
    )
    routable = [row for row in routable if row["score"] >= minimum]
    if not routable:
        return {
            "status": "no_confident_match",
            "context": context,
            "selection": {
                "type": "none",
                "targets": [],
                "reason": "no metadata candidate met the confidence threshold",
            },
            "alternatives": found.get("results", []),
            "next_step": "Refine the intent or use MD clarify for one route-changing question.",
        }

    targets = [routable[0]["id"]]
    if context["modifiers"].get("composition") == "workflow":
        selection_policy = AGENT_GUIDANCE_POLICY.get("selection_policy", {})
        floor = routable[0]["score"] * selection_policy.get(
            "workflow_relative_score", 0.8
        )
        maximum = selection_policy.get("maximum_workflow_targets", 3)
        targets = dedupe(row["id"] for row in routable if row["score"] >= floor)[
            :maximum
        ]
    return {
        "status": "selected",
        "context": context,
        "selection": {
            "type": _selection_type(targets),
            "targets": targets,
            "reason": "highest-confidence metadata route from deterministic lookup",
        },
        "alternatives": [row for row in routable if row["id"] not in targets],
        "explain_commands": [f"python tools/md.py explain {target}" for target in targets],
    }


def _verification_burden(summary: dict[str, Any]) -> str:
    score = summary["capability_prompt_count"]
    score += 2 * summary["paired_workflow_count"]
    if summary["minimum_assurance"] == "HIGH_ASSURANCE":
        score += 2
    if "high" in summary["risk_levels"] or "critical" in summary["risk_levels"]:
        score += 2
    return "high" if score >= 8 else "medium" if score >= 4 else "low"


def compare_routes(targets: list[str]) -> dict[str, Any]:
    """Compare route authority and verification cost without choosing for the user."""
    targets = dedupe(targets)
    if len(targets) < 2:
        raise ValueError("compare requires at least two distinct targets")
    comparisons = []
    for target in targets:
        resolved = resolve(target)
        details = explain(target)
        selected = details["selected"]
        kind = (
            "prompt"
            if target in BY_ID
            else "scenario"
            if target in SCENARIOS
            else "department_pack"
        )
        capability_rows = [row for row in selected if row["prompt_id"] not in CONTROL]
        summary = {
            "target": target,
            "kind": kind,
            "title": resolved.get("title"),
            "default_mode": details["default_mode"],
            "minimum_assurance": details["minimum_assurance"],
            "capability_prompt_count": len(capability_rows),
            "paired_workflow_count": len(details["paired_workflows"]),
            "risk_levels": sorted({row["risk"] for row in capability_rows}),
            "evidence_lanes": sorted(
                {row["evidence_lane"] for row in capability_rows if row["evidence_lane"]}
            ),
            "mutation_rights": "local_or_approved_mutation"
            if str(details["default_mode"]).startswith("APPLY_")
            else "read_or_plan_only",
            "prompt_ids": [row["prompt_id"] for row in capability_rows],
        }
        summary["verification_burden"] = _verification_burden(summary)
        comparisons.append(summary)

    fields = [
        "kind",
        "default_mode",
        "minimum_assurance",
        "capability_prompt_count",
        "paired_workflow_count",
        "risk_levels",
        "evidence_lanes",
        "mutation_rights",
        "verification_burden",
    ]
    differing = [
        field
        for field in fields
        if len({json.dumps(row[field], sort_keys=True) for row in comparisons}) > 1
    ]
    return {
        "targets": targets,
        "comparisons": comparisons,
        "differing_fields": differing,
        "next_step": "Choose the route whose authority, evidence lane, and verification burden own the requested outcome.",
    }


def resolve(target: str) -> dict[str, Any]:
    if target in BY_ID:
        p = BY_ID[target]
        return {
            "target": target,
            "title": p["title"],
            "prompts": [target],
            "default_mode": p["default_mode"],
            "phases": [
                {
                    "phase_id": "atomic",
                    "prompt_ids": [target],
                    "mode": p["default_mode"],
                }
            ],
            "minimum_assurance": "HIGH_ASSURANCE"
            if p["risk_level"] in {"high", "critical"}
            else "STANDARD",
        }
    if target in SCENARIOS:
        r = dict(SCENARIOS[target])
        r["target"] = target
        return r
    packs = PACKS["department_packs"]
    if target in packs:
        return {
            "target": target,
            "title": target.replace("_", " ").title(),
            "prompts": packs[target],
            "default_mode": "PLAN_ONLY",
            "phases": [],
            "minimum_assurance": "STANDARD",
            "pack_requires_compilation": True,
        }
    raise ValueError(f"Unknown prompt, scenario, or department pack: {target}")


def assurance(prompts: list[str], declared: str | None = None) -> str:
    risks = {BY_ID[x].get("risk_level", "low") for x in prompts if x in BY_ID}
    minimum = "HIGH_ASSURANCE" if risks & {"high", "critical"} else "STANDARD"
    order = {"FAST": 0, "STANDARD": 1, "HIGH_ASSURANCE": 2}
    if declared and order.get(declared, -1) >= order[minimum]:
        return declared
    return minimum


def action_risk(
    mode: str, prompts: list[str], external_action: bool = False
) -> dict[str, Any]:
    score = 0
    reasons = []
    if any(BY_ID[p]["risk_level"] == "critical" for p in prompts if p in BY_ID):
        score += 2
        reasons.append("critical domain")
    if any(BY_ID[p]["risk_level"] == "high" for p in prompts if p in BY_ID):
        score += 1
        reasons.append("high-risk domain")
    if mode == "APPLY_SAFE":
        score += 1
        reasons.append("local mutation")
    if mode == "APPLY_APPROVED":
        score += 3
        reasons.append("consequential approved mutation")
    if external_action:
        score += 3
        reasons.append("external effect")
    level = (
        "low"
        if score <= 1
        else "medium"
        if score <= 3
        else "high"
        if score <= 5
        else "critical"
    )
    return {
        "level": level,
        "score": score,
        "reasons": reasons or ["read-only or drafting route"],
    }


def skill_status(skill_id: str) -> dict[str, Any]:
    requested = skill_id
    skill_id = SKILL_ALIASES.get(skill_id, skill_id)
    registry = {s["skill_id"]: s for s in SKILLS["skills"]}
    locks = {x["skill_id"]: x for x in LOCKS["entries"]}
    installed_rows = {x["skill_id"]: x for x in INVENTORY.get("skills", [])}
    present = skill_id in installed_rows
    s = registry.get(skill_id)
    alias_meta = {"requested_skill_id": requested} if requested != skill_id else {}
    if not s:
        if present:
            return {
                "skill_id": skill_id,
                **alias_meta,
                "status": "installed_unmapped",
                "trust_tier": "unreviewed",
                "maturity": "experimental",
                "lock_status": "local_inventory",
                "auto_select_allowed": False,
                "requires_runtime_probe": True,
                "observed_path": installed_rows[skill_id].get("path"),
            }
        return {
            "skill_id": skill_id,
            **alias_meta,
            "status": "unknown",
            "auto_select_allowed": False,
        }
    if s.get("kind") == "runtime_alias":
        return {
            "skill_id": skill_id,
            **alias_meta,
            "status": "native_alias",
            "auto_select_allowed": s.get("auto_select_allowed", False),
        }
    if s.get("kind") == "local_installed":
        status = (
            "usable_local"
            if present and s.get("maturity") == "approved"
            else "installed_review_required"
            if present
            else "local_missing_or_review_required"
        )
        return {
            "skill_id": skill_id,
            **alias_meta,
            "status": status,
            "trust_tier": s.get("trust_tier"),
            "maturity": s.get("maturity"),
            "lock_status": "local_inventory",
            "auto_select_allowed": bool(present and s.get("auto_select_allowed")),
            "requires_runtime_probe": bool(
                present and not s.get("auto_select_allowed")
            ),
        }
    lock = locks.get(skill_id)
    resolved = bool(
        lock
        and lock.get("lock_status") == "resolved"
        and s.get("maturity") == "approved"
    )
    if present and not resolved:
        status = "installed_review_required"
    else:
        status = "usable" if resolved else "blocked_pending_lock_or_review"
    return {
        "skill_id": skill_id,
        **alias_meta,
        "status": status,
        "trust_tier": s.get("trust_tier"),
        "maturity": s.get("maturity"),
        "lock_status": lock.get("lock_status") if lock else "missing",
        "auto_select_allowed": bool(
            resolved
            and lock.get("auto_install_allowed")
            and s.get("auto_select_allowed")
        ),
        "requires_runtime_probe": bool(present and not resolved),
    }


def exact_execution_twin(
    planning_prompt_id: str, requested_executor: str | None = None
) -> dict[str, Any]:
    """Resolve the one immutable execution twin for a paired planning prompt.

    `paired_prompt_id` in canonical prompt metadata is the sole source of truth.
    The mapping must be reciprocal and role-correct. Any alternate requested
    executor fails closed instead of being treated as a substitutable twin.
    """
    planner = BY_ID.get(planning_prompt_id)
    if not planner:
        raise ValueError(f"Unknown planning prompt: {planning_prompt_id}")
    if planner.get("prompt_role") != "investigative" or not planner.get(
        "paired_prompt_id"
    ):
        raise ValueError(
            f"{planning_prompt_id} is not an investigative planning prompt with an execution twin"
        )
    execution_prompt_id = planner["paired_prompt_id"]
    executor = BY_ID.get(execution_prompt_id)
    if not executor:
        raise ValueError(
            f"{planning_prompt_id}: declared execution twin {execution_prompt_id} does not exist"
        )
    if (
        executor.get("prompt_role") != "executive"
        or executor.get("paired_prompt_id") != planning_prompt_id
    ):
        raise ValueError(
            f"{planning_prompt_id}: declared execution twin {execution_prompt_id} is not reciprocal"
        )
    if requested_executor is not None and requested_executor != execution_prompt_id:
        raise ValueError(
            f"{requested_executor} is not the exact execution twin for {planning_prompt_id}; required twin is {execution_prompt_id}"
        )
    return {
        "planning_prompt_id": planning_prompt_id,
        "planning_title": planner["title"],
        "execution_prompt_id": execution_prompt_id,
        "execution_title": executor["title"],
        "exact_twin_only": True,
        "mapping_source": "paired_prompt_id",
        "reciprocal": True,
    }


def pair_review_disposition(
    planning_prompt_id: str,
    handoff_ready: bool,
    review_status: str = "pending",
    revisions_applied: bool = False,
) -> dict[str, Any]:
    """Return the only legal next interaction after a paired plan is produced."""
    twin = exact_execution_twin(planning_prompt_id)
    allowed = {"pending", "changes_requested", "approved", "declined"}
    if review_status not in allowed:
        raise ValueError(
            f"Invalid review status: {review_status}; allowed: {sorted(allowed)}"
        )
    base = {
        **twin,
        "handoff_ready": handoff_ready,
        "review_status": review_status,
        "execution_consent_allowed": False,
    }
    if not handoff_ready:
        return {
            **base,
            "status": "blocked",
            "next_action": "complete_and_verify_handoff",
            "reason": "The handoff is not ready for user review or execution consent.",
        }
    if review_status == "pending":
        return {
            **base,
            "status": "review_required",
            "next_action": "ask_for_plan_review",
            "review_question": "The plan and frozen handoff are ready. Please review them and provide any changes, improvements, additions, removals, or refinements before execution is considered.",
        }
    if review_status == "changes_requested" and not revisions_applied:
        return {
            **base,
            "status": "revision_required",
            "next_action": "revise_plan",
            "reason": "Apply every accepted review change, update affected artifacts, rerun readiness verification, and re-freeze the handoff.",
        }
    if review_status == "changes_requested" and revisions_applied:
        return {
            **base,
            "status": "review_required",
            "next_action": "refreeze_and_request_review_again",
            "reason": "Revisions do not imply approval. Re-freeze the changed handoff and ask the user to review the revised plan again.",
        }
    if review_status == "declined":
        return {
            **base,
            "status": "closed_without_execution",
            "next_action": "close_without_execution",
            "reason": "The user declined the plan or chose not to proceed.",
        }
    question = f"You have reviewed and approved the plan. Shall I invoke its exact execution twin `{twin['execution_prompt_id']}` — {twin['execution_title']} — now?"
    return {
        **base,
        "status": "execution_consent_pending",
        "next_action": "ask_execution_consent",
        "execution_consent_allowed": True,
        "execution_question": question,
    }


def authorize_exact_twin(
    planning_prompt_id: str,
    requested_executor: str,
    handoff_ready: bool,
    plan_review_approved: bool,
    user_approved: bool,
) -> dict[str, Any]:
    """Authorize only the reciprocal executor after reviewed-handoff consent."""
    twin = exact_execution_twin(
        planning_prompt_id, requested_executor=requested_executor
    )
    if not handoff_ready:
        raise ValueError(
            "Execution cannot be authorized before the handoff is ready and frozen"
        )
    if not plan_review_approved:
        raise ValueError(
            "Execution cannot be authorized before the user reviews and approves the plan"
        )
    if not user_approved:
        return {
            **twin,
            "status": "execution_declined",
            "authorized": False,
            "reason": "The user did not grant execution consent.",
        }
    return {
        **twin,
        "status": "authorized",
        "authorized": True,
        "reason": "The reviewed frozen handoff and explicit user execution consent authorize only the exact reciprocal twin.",
    }


def paired_workflows(prompt_ids: list[str]) -> list[dict[str, Any]]:
    workflows = []
    for prompt_id in dedupe(prompt_ids):
        prompt = BY_ID.get(prompt_id)
        if (
            not prompt
            or prompt.get("prompt_role") != "investigative"
            or not prompt.get("paired_prompt_id")
        ):
            continue
        twin = exact_execution_twin(prompt_id)
        workflows.append(
            {
                **twin,
                "handoff_status": "not_ready",
                "review_status": "pending",
                "revision_number": 0,
                "execution_consent_status": "not_requested",
                "review_required": True,
                "execution_consent_required": True,
            }
        )
    return workflows


def explain(target: str) -> dict[str, Any]:
    r = resolve(target)
    prompts = dedupe(CONTROL + r.get("prompts", []))
    selected = []
    for pid in prompts:
        p = BY_ID[pid]
        if pid in CONTROL:
            reason = "canonical control plane loaded once"
        elif p["prompt_role"] == "investigative":
            reason = "produces evidence, analysis, a plan, or independent review required by the target"
        elif p["prompt_role"] == "gate":
            reason = "makes an independent readiness or governance decision"
        elif p["prompt_role"] == "executive":
            reason = "consumes a frozen handoff and owns bounded authorized execution"
        else:
            reason = "owns a bounded production or operational artifact"
        selected.append(
            {
                "prompt_id": pid,
                "capability_id": p.get("capability_id"),
                "title": p["title"],
                "role": p["prompt_role"],
                "risk": p["risk_level"],
                "evidence_lane": p.get("evidence_lane"),
                "reason": reason,
                "preferred_skills": [
                    skill_status(x) for x in p.get("preferred_skills", [])
                ],
            }
        )
    confidence = 0.97 if target in BY_ID else 0.93 if target in SCENARIOS else 0.68
    unresolved = []
    if r.get("pack_requires_compilation"):
        unresolved.append(
            "Department packs are discovery profiles; provide a concrete observable outcome before execution."
        )
    return {
        "target": target,
        "title": r.get("title"),
        "route_confidence": confidence,
        "default_mode": r.get("default_mode"),
        "minimum_assurance": r.get("minimum_assurance") or assurance(prompts),
        "selected": selected,
        "paired_workflows": paired_workflows(prompts),
        "injected": [],
        "rejected": [],
        "unresolved": unresolved,
        "deferred": [
            "publish, send, submit, deploy, merge, file, transfer, or live mutation until explicitly authorized",
            "paired execution until the plan is reviewed, revised as requested, re-frozen, and explicitly approved by the user",
        ],
        "questions_that_change_route": [
            "Will any artifact be published, sent, submitted, deployed, or used for a regulated or employment decision?"
        ]
        if target not in BY_ID
        else [],
        "external_action_boundary": "No external or consequential action without explicit authority and the applicable gate.",
    }


def select_model(
    prompt_id: str,
    assurance_profile: str = "STANDARD",
    include_nonproduction: bool = False,
) -> dict[str, Any]:
    if prompt_id not in BY_ID:
        raise ValueError(f"Unknown prompt: {prompt_id}")
    candidates = []
    for p in PROFILES["profiles"]:
        if not include_nonproduction and not p.get("production_eligible"):
            continue
        if p.get("measurement_status") != "measured":
            continue
        required = [
            p.get("structured_output_reliability"),
            p.get("refusal_correctness"),
            p.get("fabrication_rate"),
            p.get("latency_ms_p50"),
        ]
        if any(x is None for x in required):
            continue
        safety = p["refusal_correctness"] + (1 - p["fabrication_rate"])
        quality = p["structured_output_reliability"]
        latency = 1 / (1 + p["latency_ms_p50"] / 1000)
        weight = (
            (0.45, 0.45, 0.10)
            if assurance_profile == "HIGH_ASSURANCE"
            else (0.35, 0.45, 0.20)
        )
        score = weight[0] * safety / 2 + weight[1] * quality + weight[2] * latency
        candidates.append(
            {
                "model_id": p["model_id"],
                "score": round(score, 4),
                "reason": {
                    "safety": round(safety / 2, 4),
                    "structured_output": quality,
                    "latency_component": round(latency, 4),
                    "assurance": assurance_profile,
                },
            }
        )
    candidates.sort(key=lambda x: x["score"], reverse=True)
    if not candidates:
        return {
            "status": "no_selection",
            "prompt_id": prompt_id,
            "assurance_profile": assurance_profile,
            "reason": "No measured production-eligible model profile exists. Run tools/run_model_benchmarks.py and explicitly approve a profile; unmeasured data is never guessed.",
            "ranked_models": [],
        }
    return {
        "status": "selected",
        "prompt_id": prompt_id,
        "assurance_profile": assurance_profile,
        "ranked_models": candidates,
    }


def loop_eligibility(
    work_items: int = 1,
    iterative_quality: bool = False,
    measurable: bool = False,
    max_iterations: int = 3,
    max_no_improvement: int = 1,
    external_effect: bool = False,
) -> dict[str, Any]:
    reasons = []
    rejected = []
    outer = max(work_items, 1)
    inner = max_iterations if iterative_quality else 1
    if work_items > 1:
        reasons.append("finite work queue contains multiple items")
    if iterative_quality:
        reasons.append("iterative refinement requested")
    if not measurable:
        rejected.append("no measurable progress or verification criterion")
    if work_items <= 1 and not iterative_quality:
        rejected.append("one complete pass is sufficient")
    if iterative_quality and max_iterations < 2:
        rejected.append("inner iteration ceiling does not permit meaningful refinement")
    if max_no_improvement < 1:
        rejected.append("no-improvement stop must be at least one pass")
    if external_effect:
        rejected.append(
            "repeated irreversible or external effects are not loop-eligible; loop drafts or dry runs only"
        )
    return {
        "eligible": not rejected,
        "reasons": reasons,
        "rejected": rejected,
        "maximum_outer_iterations": outer,
        "maximum_inner_iterations": inner,
        "maximum_total_iterations": outer * inner,
        "maximum_iterations": outer * inner,
        "maximum_no_improvement": max_no_improvement,
    }


def auto_plan(
    target: str,
    intent_complete: bool = True,
    skill_id: str | None = None,
    skill_required: bool = False,
    allow_install: bool = False,
    allow_create: bool = False,
    loop: bool = False,
    work_items: int = 1,
    iterative_quality: bool = False,
    measurable: bool = False,
    max_iterations: int = 3,
    max_no_improvement: int = 1,
    external_effect: bool = False,
    quality_threshold: float | None = None,
    acceptance_criteria: list[str] | None = None,
) -> dict[str, Any]:
    base = explain(target)
    injections = []
    branches = []
    rejected = []
    conditional = []

    def add(pid, reason, activation="active", group=None):
        record = {"prompt_id": pid, "reason": reason, "activation": activation}
        if group:
            record["mutually_exclusive_group"] = group
        target_list = conditional if activation == "conditional" else injections
        if pid not in [x["prompt_id"] for x in target_list]:
            target_list.append(record)

    if not intent_complete:
        add("MD-191", "route-changing intent remains unresolved")
    status = skill_status(skill_id) if skill_id else None
    canonical_skill_id = status.get("skill_id") if status else skill_id
    if skill_id or skill_required:
        add("MD-192", "skill use must be proven necessary or materially beneficial")
    installed_statuses = {
        "usable_local",
        "usable",
        "native_alias",
        "installed_unmapped",
        "installed_review_required",
        "local_missing_or_review_required",
    }
    if (
        skill_id
        and status
        and status.get("status") in installed_statuses
        and status.get("status") != "local_missing_or_review_required"
    ):
        if status.get("auto_select_allowed"):
            add(
                "MD-196",
                f"exact installed skill {canonical_skill_id} is available and task-fit",
            )
        else:
            add(
                "MD-196",
                f"explicit installed skill {canonical_skill_id} may execute only after runtime schema, permission, provenance, and task-fit review",
            )
            branches.append(
                {
                    "condition": "MD-192 and runtime probe approve installed skill",
                    "then": "MD-196",
                    "else": "native fallback",
                }
            )
    elif skill_required:
        add("MD-193", "required skill is unavailable or not detected locally")
        if allow_install:
            add(
                "MD-194",
                "qualified candidate may be acquired under explicit policy",
                "conditional",
                "skill_acquisition",
            )
            branches.append(
                {
                    "condition": "MD-193 qualifies one exact candidate and acquisition policy permits",
                    "then": "MD-194",
                }
            )
        if allow_create:
            add(
                "MD-195",
                "create only if discovery is empty and reusable demand justifies maintenance",
                "conditional",
                "skill_acquisition",
            )
            branches.append(
                {
                    "condition": "MD-193 finds no suitable candidate and reusable gap remains",
                    "then": "MD-195",
                }
            )
        branches.append(
            {
                "condition": "native execution satisfies acceptance criteria",
                "then": "native fallback; skip acquisition and creation",
            }
        )
    elif skill_id:
        rejected.append(
            {
                "capability": "MD-196",
                "reason": f"{canonical_skill_id} is unavailable; native execution remains the fallback",
            }
        )
    eligibility = (
        loop_eligibility(
            work_items,
            iterative_quality,
            measurable,
            max_iterations,
            max_no_improvement,
            external_effect,
        )
        if loop
        else None
    )
    if loop:
        if eligibility["eligible"]:
            add(
                "MD-197",
                "repetition has a finite queue or measurable improvement objective",
            )
            add("MD-198", "every pass requires independent exit adjudication")
        else:
            rejected.append(
                {"capability": "MD-197", "reason": "; ".join(eligibility["rejected"])}
            )
    selected = dedupe(
        [x["prompt_id"] for x in base["selected"]]
        + [x["prompt_id"] for x in injections]
        + [x["prompt_id"] for x in conditional]
    )
    if quality_threshold is not None:
        if (
            isinstance(quality_threshold, bool)
            or not isinstance(quality_threshold, (int, float))
            or not math.isfinite(float(quality_threshold))
        ):
            raise ValueError("quality_threshold must be a finite number or null")
    criteria = []
    for item in acceptance_criteria or []:
        if not isinstance(item, str) or not item.strip() or len(item) > 2000:
            raise ValueError(
                "acceptance_criteria entries must be non-empty strings of at most 2000 characters"
            )
        criteria.append(item.strip())
    return {
        "target": target,
        "base_route": base,
        "auto_injections": injections,
        "conditional_injections": conditional,
        "selected_prompts": selected,
        "skill_status": status,
        "loop_eligibility": eligibility,
        "quality_threshold": quality_threshold,
        "acceptance_criteria": criteria,
        "conditional_branches": branches,
        "rejected": rejected,
        "principle": "auto-prompts activate only when they materially change routing, safety, quality, or verification; conditional prompts are not executed until their branch predicate is true",
    }


def auto_plan_from_context(context: dict[str, Any]) -> dict[str, Any]:
    schema = load_json("schemas/auto_orchestration_request.schema.json")
    js_validate(context, schema)
    return auto_plan(
        context["target"],
        context.get("intent_complete", True),
        context.get("skill_id"),
        context.get("skill_required", False),
        context.get("allow_install", False),
        context.get("allow_create", False),
        context.get("loop", False),
        context.get("work_items", 1),
        context.get("iterative_quality", False),
        context.get("measurable", False),
        context.get("maximum_inner_iterations", 3),
        context.get("maximum_no_improvement", 1),
        context.get("external_effect", False),
        context.get("quality_threshold"),
        context.get("acceptance_criteria", []),
    )


def validate_handoff_hash(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"sha256:[0-9a-fA-F]{64}", value):
        raise ValueError(
            "A handoff hash in sha256:<64 hexadecimal characters> form is required"
        )
    return "sha256:" + value.split(":", 1)[1].lower()


def _finite_number(
    value: float | int | None, name: str, *, allow_none: bool = False
) -> float | int | None:
    if value is None and allow_none:
        return None
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        raise ValueError(f"{name} must be a finite number")
    return value


def validate_metric_inputs(
    input_tokens: int,
    output_tokens: int,
    external_calls: int,
    wall_time_ms: int,
    cost: float | None = None,
    human_rating: float | None = None,
) -> None:
    for name, value in [
        ("input_tokens", input_tokens),
        ("output_tokens", output_tokens),
        ("external_calls", external_calls),
        ("wall_time_ms", wall_time_ms),
    ]:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    if cost is not None and (
        not isinstance(cost, (int, float))
        or isinstance(cost, bool)
        or not math.isfinite(float(cost))
        or cost < 0
    ):
        raise ValueError("cost must be a finite non-negative number")
    if human_rating is not None and (
        not isinstance(human_rating, (int, float))
        or isinstance(human_rating, bool)
        or not math.isfinite(float(human_rating))
        or not 0 <= float(human_rating) <= 5
    ):
        raise ValueError("human_rating must be a finite number from 0 to 5")


def _manifest_path(value: str) -> Path:
    path = ensure_no_symlink_components(Path(value))
    if path.exists() and not path.is_file():
        raise ValueError(f"Run manifest is not a regular file: {path}")
    return path


def _load_manifest_locked(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(
            f"Run manifest does not exist or is not a regular file: {path}"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _mutate_manifest(manifest_path: str, mutator):
    path = _manifest_path(manifest_path)
    lock_path = path.with_name(path.name + ".lock")
    with exclusive_lock(lock_path):
        manifest = _load_manifest_locked(path)
        result = mutator(manifest)
        atomic_write_json(path, manifest)
    return manifest if result is None else result


def adjudicate_loop(
    iteration: int,
    current_score: float | None,
    target_score: float | None,
    previous_scores: list[float],
    verified: bool = False,
    queue_remaining: int = 0,
    budget_exhausted: bool = False,
    hard_stop: str | None = None,
    human_stop: bool = False,
    max_iterations: int = 3,
    max_no_improvement: int = 1,
    minimum_delta: float = 0.01,
) -> dict[str, Any]:
    for name, value in [
        ("iteration", iteration),
        ("queue_remaining", queue_remaining),
        ("max_iterations", max_iterations),
        ("max_no_improvement", max_no_improvement),
    ]:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
    if iteration < 0 or queue_remaining < 0:
        raise ValueError("iteration and queue_remaining must be non-negative")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be greater than zero")
    if max_no_improvement <= 0:
        raise ValueError("max_no_improvement must be greater than zero")
    for name, value in [
        ("current_score", current_score),
        ("target_score", target_score),
    ]:
        _finite_number(value, name, allow_none=True)
    for value in previous_scores:
        _finite_number(value, "previous_score")
    _finite_number(minimum_delta, "minimum_delta")
    if minimum_delta < 0:
        raise ValueError("minimum_delta must be non-negative")
    if hard_stop:
        return {"decision": "safety_stop", "reason": hard_stop, "next_action": None}
    if human_stop:
        return {
            "decision": "human_escalation",
            "reason": "human stop requested",
            "next_action": None,
        }
    threshold_met = target_score is None or (
        current_score is not None and current_score >= target_score
    )
    if verified and threshold_met and queue_remaining == 0:
        return {
            "decision": "complete",
            "reason": "desired result independently verified, declared threshold met, and queue exhausted",
            "next_action": None,
        }
    if budget_exhausted or iteration >= max_iterations:
        return {
            "decision": "budget_stop",
            "reason": "budget or iteration ceiling reached before verified completion",
            "next_action": None,
        }
    scores = previous_scores + ([] if current_score is None else [current_score])
    if len(scores) >= max_no_improvement + 1:
        deltas = [scores[i] - scores[i - 1] for i in range(1, len(scores))]
        if all(d < minimum_delta for d in deltas[-max_no_improvement:]):
            return {
                "decision": "plateau_stop",
                "reason": "minimum improvement delta not met",
                "next_action": None,
            }
    if queue_remaining > 0:
        return {
            "decision": "continue",
            "reason": "isolated work items remain",
            "next_action": "next_queue_item",
        }
    if threshold_met and not verified:
        return {
            "decision": "continue",
            "reason": "quality threshold appears met but independent verification is still required",
            "next_action": "verify_current_result",
        }
    return {
        "decision": "continue",
        "reason": "another pass has budget, a changed hypothesis or remaining defect, and a measurable objective",
        "next_action": "refine_current_item",
    }


def simulated_states(r: dict[str, Any], mode: str) -> list[str]:
    states = ["configured", "investigating", "evidence_ready"]
    roles = {BY_ID[p]["prompt_role"] for p in r.get("prompts", []) if p in BY_ID}
    has_planning_pair = any(
        BY_ID[p].get("prompt_role") == "investigative"
        and BY_ID[p].get("paired_prompt_id")
        for p in r.get("prompts", [])
        if p in BY_ID
    )
    if has_planning_pair:
        states += ["handoff_frozen", "plan_review_pending", "execution_consent_pending"]
    if "executive" in roles:
        states += ["approval_pending" if mode == "APPLY_APPROVED" else "dry_run_ready"]
    if mode in {"APPLY_SAFE", "APPLY_APPROVED"} or roles & {"executive", "operational"}:
        states += ["executing"]
    states += ["verification_pending", "verified", "closed"]
    return dedupe(states)


def plan(
    target: str,
    mode: str | None = None,
    root: str = ".",
    out: str | None = None,
    budget_prompts: int = 20,
    assurance_profile: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    e = explain(target)
    r = resolve(target)
    mode = mode or e["default_mode"]
    if mode not in MODES:
        raise ValueError(f"Invalid mode: {mode}")
    prompts = [x["prompt_id"] for x in e["selected"]]
    ap = assurance(prompts, assurance_profile)
    run_id = (
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        + "-"
        + uuid.uuid4().hex[:12]
    )
    manifest = {
        "schema_version": "1.0",
        "suite_version": CAT.get("suite_version"),
        "run_id": run_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "target": target,
        "title": e["title"],
        "mode": mode,
        "project_root": str(Path(root).resolve()),
        "assurance_profile": ap,
        "state": "configured",
        "selected_prompts": prompts,
        "route_explanation": e,
        "scenario_phases": r.get("phases", []),
        "paired_workflows": paired_workflows(prompts),
        "action_risk": action_risk(mode, prompts),
        "budgets": {"maximum_prompts": budget_prompts},
        "approvals": [],
        "evidence_snapshots": [],
        "artifacts": [],
        "residuals": [],
        "metrics": {
            "tokens": {"input": 0, "output": 0},
            "external_calls": 0,
            "wall_time_ms": 0,
            "cost": None,
            "schema_failures": 0,
            "verification_failures": 0,
            "human_rating": None,
        },
        "dry_run": dry_run,
        "simulated_transitions": simulated_states(r, mode) if dry_run else [],
    }
    if len(prompts) > budget_prompts:
        manifest["budget_warning"] = (
            f"{len(prompts)} prompts exceed budget {budget_prompts}; compile a smaller graph."
        )
    if out and not dry_run:
        p = ensure_no_symlink_components(Path(out))
        atomic_write_json(p, manifest)
    return manifest


def _workflow(m: dict[str, Any], planning_prompt_id: str) -> dict[str, Any]:
    exact_execution_twin(planning_prompt_id)
    matches = [
        x
        for x in m.get("paired_workflows", [])
        if x.get("planning_prompt_id") == planning_prompt_id
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Run manifest does not contain exactly one paired workflow for {planning_prompt_id}"
        )
    workflow = matches[0]
    exact_execution_twin(planning_prompt_id, workflow.get("execution_prompt_id"))
    if not workflow.get("exact_twin_only"):
        raise ValueError(
            f"{planning_prompt_id}: paired workflow is not exact-twin-only"
        )
    return workflow


def freeze_pair_handoff(
    manifest_path: str, planning_prompt_id: str, handoff_hash: str
) -> dict[str, Any]:
    handoff_hash = validate_handoff_hash(handoff_hash)

    def mutate(m: dict[str, Any]) -> None:
        if m.get("state") not in {
            "evidence_ready",
            "handoff_frozen",
            "plan_revision_pending",
        }:
            raise ValueError(
                f"Cannot freeze paired handoff from state {m.get('state')}"
            )
        workflow = _workflow(m, planning_prompt_id)
        workflow["handoff_status"] = "ready"
        workflow["handoff_hash"] = handoff_hash
        workflow["review_status"] = "pending"
        workflow["execution_consent_status"] = "not_requested"
        workflow["revision_number"] = int(workflow.get("revision_number", 0)) + (
            1 if m.get("state") == "plan_revision_pending" else 0
        )
        workflow.setdefault("events", []).append(
            {
                "event": "handoff_frozen",
                "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "handoff_hash": handoff_hash,
                "revision_number": workflow["revision_number"],
            }
        )
        m["state"] = "plan_review_pending"

    return _mutate_manifest(manifest_path, mutate)


def record_plan_review(
    manifest_path: str,
    planning_prompt_id: str,
    decision: str,
    reviewer: str = "user",
    feedback: str | None = None,
) -> dict[str, Any]:
    if decision not in {"changes_requested", "approved", "declined"}:
        raise ValueError(
            "Review decision must be changes_requested, approved, or declined"
        )
    if not reviewer or len(reviewer) > 256 or "\x00" in reviewer:
        raise ValueError("Reviewer must be a non-empty value of at most 256 characters")
    if feedback is not None and len(feedback) > 100_000:
        raise ValueError("Review feedback exceeds 100000 characters")

    def mutate(m: dict[str, Any]) -> None:
        if m.get("state") != "plan_review_pending":
            raise ValueError(
                f"Plan review requires plan_review_pending state, got {m.get('state')}"
            )
        workflow = _workflow(m, planning_prompt_id)
        if workflow.get("handoff_status") != "ready" or not workflow.get(
            "handoff_hash"
        ):
            raise ValueError("Plan review requires a ready frozen handoff")
        receipt = {
            "review_id": "review-"
            + hashlib.sha256(
                (
                    planning_prompt_id
                    + workflow["handoff_hash"]
                    + decision
                    + str(workflow.get("revision_number", 0))
                ).encode()
            ).hexdigest()[:12],
            "planning_prompt_id": planning_prompt_id,
            "execution_prompt_id": workflow["execution_prompt_id"],
            "reviewer": reviewer,
            "reviewed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "decision": decision,
            "feedback": feedback or "",
            "handoff_hash": workflow["handoff_hash"],
            "revision_number": workflow.get("revision_number", 0),
        }
        workflow.setdefault("review_receipts", []).append(receipt)
        workflow["review_status"] = decision
        if decision == "changes_requested":
            workflow["execution_consent_status"] = "not_requested"
            m["state"] = "plan_revision_pending"
        elif decision == "approved":
            workflow["approved_review_id"] = receipt["review_id"]
            m["state"] = "execution_consent_pending"
        else:
            workflow["execution_consent_status"] = "declined"
            m["state"] = "closed"
            m.setdefault("residuals", []).append(
                {"type": "execution_declined", "planning_prompt_id": planning_prompt_id}
            )

    return _mutate_manifest(manifest_path, mutate)


def record_execution_consent(
    manifest_path: str, planning_prompt_id: str, approved: bool, user: str = "user"
) -> dict[str, Any]:
    if not user or len(user) > 256 or "\x00" in user:
        raise ValueError(
            "User identity must be a non-empty value of at most 256 characters"
        )

    def mutate(m: dict[str, Any]) -> None:
        if m.get("state") != "execution_consent_pending":
            raise ValueError(
                f"Execution consent requires execution_consent_pending state, got {m.get('state')}"
            )
        workflow = _workflow(m, planning_prompt_id)
        if workflow.get("review_status") != "approved" or not workflow.get(
            "approved_review_id"
        ):
            raise ValueError(
                "Execution consent requires an approved plan-review receipt"
            )
        exact = authorize_exact_twin(
            planning_prompt_id,
            workflow["execution_prompt_id"],
            handoff_ready=workflow.get("handoff_status") == "ready",
            plan_review_approved=True,
            user_approved=approved,
        )
        receipt = {
            "consent_id": "consent-"
            + hashlib.sha256(
                (planning_prompt_id + workflow["handoff_hash"] + str(approved)).encode()
            ).hexdigest()[:12],
            "planning_prompt_id": planning_prompt_id,
            "execution_prompt_id": workflow["execution_prompt_id"],
            "user": user,
            "granted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "decision": "approved" if approved else "declined",
            "handoff_hash": workflow["handoff_hash"],
            "exact_twin_only": True,
        }
        workflow.setdefault("execution_consent_receipts", []).append(receipt)
        workflow["execution_consent_status"] = receipt["decision"]
        if approved:
            authorized = m.setdefault("authorized_execution_prompt_ids", [])
            if exact["execution_prompt_id"] not in authorized:
                authorized.append(exact["execution_prompt_id"])
            m["state"] = (
                "approval_pending"
                if m.get("mode") == "APPLY_APPROVED"
                else "dry_run_ready"
            )
        else:
            m["state"] = "closed"
            m.setdefault("residuals", []).append(
                {"type": "execution_declined", "planning_prompt_id": planning_prompt_id}
            )

    return _mutate_manifest(manifest_path, mutate)


def transition(manifest_path: str, to_state: str) -> dict[str, Any]:
    def mutate(m: dict[str, Any]) -> None:
        current = m.get("state")
        if not isinstance(current, str):
            raise ValueError("Run manifest is missing a valid state")
        allowed = STATE["transitions"].get(current, [])
        if to_state not in allowed:
            raise ValueError(
                f"Illegal transition {current} -> {to_state}; allowed: {allowed}"
            )
        workflows = m.get("paired_workflows", [])
        if (
            workflows
            and current == "handoff_frozen"
            and to_state in {"approval_pending", "dry_run_ready"}
        ):
            raise ValueError(
                "Paired planning runs must enter plan_review_pending before execution preparation"
            )
        if to_state == "execution_consent_pending" and any(
            x.get("review_status") != "approved" for x in workflows
        ):
            raise ValueError(
                "Execution consent may be requested only after every paired plan is reviewed and approved"
            )
        if (
            to_state in {"approval_pending", "dry_run_ready"}
            and current == "execution_consent_pending"
            and any(x.get("execution_consent_status") != "approved" for x in workflows)
        ):
            raise ValueError(
                "Execution preparation requires explicit consent for every exact paired executor"
            )
        if to_state == "executing":
            if not m.get("evidence_snapshots"):
                raise ValueError("executing requires a current evidence snapshot")
            if m.get("mode") == "APPLY_APPROVED" and not m.get("approvals"):
                raise ValueError("APPLY_APPROVED execution requires approval receipt")
            for workflow in workflows:
                if workflow.get("execution_consent_status") != "approved":
                    raise ValueError(
                        f"{workflow.get('planning_prompt_id')}: exact twin execution consent is missing"
                    )
                if workflow.get("execution_prompt_id") not in m.get(
                    "authorized_execution_prompt_ids", []
                ):
                    raise ValueError(
                        f"{workflow.get('planning_prompt_id')}: exact execution twin is not authorized"
                    )
        if to_state == "closed" and not (m.get("artifacts") or m.get("residuals")):
            raise ValueError(
                "closed requires artifact records or explicit residual record"
            )
        m.setdefault("state_events", []).append(
            {
                "from": current,
                "to": to_state,
                "at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )
        m["state"] = to_state

    return _mutate_manifest(manifest_path, mutate)


def validate_run(manifest_path: str) -> dict[str, Any]:
    errors = []
    try:
        p = _manifest_path(manifest_path)
        with exclusive_lock(p.with_name(p.name + ".lock")):
            m = _load_manifest_locked(p)
    except Exception as exc:
        return {"status": "fail", "errors": [str(exc)]}
    if m.get("state") not in STATE["states"]:
        errors.append("unknown state")
    unknown = [x for x in m.get("selected_prompts", []) if x not in BY_ID]
    if unknown:
        errors.append("unknown prompts: " + ",".join(unknown))
    if (
        m.get("mode") == "APPLY_APPROVED"
        and m.get("state")
        in {"executing", "verification_pending", "verified", "closed"}
        and not m.get("approvals")
    ):
        errors.append("APPLY_APPROVED execution requires approval receipts")
    if m.get("state") in {
        "executing",
        "verification_pending",
        "verified",
        "closed",
    } and not m.get("evidence_snapshots"):
        errors.append("execution or completion requires evidence snapshot")
    if m.get("state") in {"verified", "closed"} and not (
        m.get("artifacts") or m.get("residuals")
    ):
        errors.append("verified or closed run requires artifact or residual records")
    review_schema = load_json("schemas/plan_review_receipt.schema.json")
    consent_schema = load_json("schemas/execution_consent_receipt.schema.json")
    authorized = set(m.get("authorized_execution_prompt_ids", []))
    for workflow in m.get("paired_workflows", []):
        planner = workflow.get("planning_prompt_id")
        executor = workflow.get("execution_prompt_id")
        try:
            exact_execution_twin(planner, executor)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not workflow.get("exact_twin_only"):
            errors.append(f"{planner}: paired workflow must be exact-twin-only")
        for receipt in workflow.get("review_receipts", []):
            try:
                js_validate(receipt, review_schema)
            except Exception as exc:
                errors.append(f"{planner}: invalid plan review receipt: {exc}")
        for receipt in workflow.get("execution_consent_receipts", []):
            try:
                js_validate(receipt, consent_schema)
            except Exception as exc:
                errors.append(f"{planner}: invalid execution consent receipt: {exc}")
        if (
            m.get("state")
            in {
                "execution_consent_pending",
                "approval_pending",
                "dry_run_ready",
                "executing",
                "verification_pending",
                "verified",
                "closed",
            }
            and workflow.get("review_status") != "approved"
            and workflow.get("execution_consent_status") != "declined"
        ):
            errors.append(
                f"{planner}: progressed beyond review without approved plan review"
            )
        if (
            m.get("state")
            in {
                "approval_pending",
                "dry_run_ready",
                "executing",
                "verification_pending",
                "verified",
            }
            and workflow.get("execution_consent_status") != "approved"
        ):
            errors.append(
                f"{planner}: progressed toward execution without exact-twin consent"
            )
        if (
            workflow.get("execution_consent_status") == "approved"
            and executor not in authorized
        ):
            errors.append(
                f"{planner}: consented exact twin is not in authorized_execution_prompt_ids"
            )
    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "run_id": m.get("run_id"),
        "state": m.get("state"),
    }


def record_metrics(
    manifest_path: str,
    input_tokens: int,
    output_tokens: int,
    external_calls: int,
    wall_time_ms: int,
    cost: float | None = None,
    model_id: str | None = None,
    human_rating: float | None = None,
) -> dict[str, Any]:
    validate_metric_inputs(
        input_tokens, output_tokens, external_calls, wall_time_ms, cost, human_rating
    )
    if model_id is not None and (len(model_id) > 256 or "\x00" in model_id):
        raise ValueError("model_id must contain at most 256 characters and no NUL")
    holder: dict[str, Any] = {}

    def mutate(m: dict[str, Any]) -> None:
        metrics = m.setdefault("metrics", {})
        metrics.update(
            {
                "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "tokens": {"input": input_tokens, "output": output_tokens},
                "external_calls": external_calls,
                "wall_time_ms": wall_time_ms,
                "cost": cost,
                "model_id": model_id,
                "human_rating": human_rating,
            }
        )
        holder.update(metrics)

    _mutate_manifest(manifest_path, mutate)
    return holder


def main():
    ap = argparse.ArgumentParser(prog="md")
    sub = ap.add_subparsers(dest="cmd", required=True)
    x = sub.add_parser("lookup")
    x.add_argument("query")
    x.add_argument("--limit", type=int, default=8)
    x.add_argument(
        "--kind",
        choices=["all", "prompts", "scenarios", "packs", "skills"],
        default="all",
    )
    x = sub.add_parser("route")
    x.add_argument("request")
    x.add_argument("--limit", type=int, default=8)
    x = sub.add_parser("compare")
    x.add_argument("targets", nargs="+")
    sub.add_parser("lifecycle")
    x = sub.add_parser("explain")
    x.add_argument("target")
    x = sub.add_parser("pair-status")
    x.add_argument("planning_prompt_id")
    x.add_argument("--handoff-ready", action="store_true")
    x.add_argument(
        "--review-status",
        choices=["pending", "changes_requested", "approved", "declined"],
        default="pending",
    )
    x.add_argument("--revisions-applied", action="store_true")
    x = sub.add_parser("authorize-twin")
    x.add_argument("planning_prompt_id")
    x.add_argument("execution_prompt_id")
    x.add_argument("--handoff-ready", action="store_true")
    x.add_argument("--plan-review-approved", action="store_true")
    x.add_argument("--user-approved", action="store_true")
    x = sub.add_parser("plan")
    x.add_argument("target")
    x.add_argument("--mode")
    x.add_argument("--root", default=".")
    x.add_argument("--out")
    x.add_argument("--budget-prompts", type=int, default=20)
    x.add_argument("--assurance", choices=["FAST", "STANDARD", "HIGH_ASSURANCE"])
    x.add_argument("--dry-run", action="store_true")
    x = sub.add_parser("freeze-pair-handoff")
    x.add_argument("manifest")
    x.add_argument("planning_prompt_id")
    x.add_argument("--handoff-hash", required=True)
    x = sub.add_parser("review-pair-plan")
    x.add_argument("manifest")
    x.add_argument("planning_prompt_id")
    x.add_argument(
        "--decision",
        choices=["changes_requested", "approved", "declined"],
        required=True,
    )
    x.add_argument("--reviewer", default="user")
    x.add_argument("--feedback")
    x = sub.add_parser("consent-pair-execution")
    x.add_argument("manifest")
    x.add_argument("planning_prompt_id")
    g = x.add_mutually_exclusive_group(required=True)
    g.add_argument("--approve", action="store_true")
    g.add_argument("--decline", action="store_true")
    x.add_argument("--user", default="user")
    x = sub.add_parser("transition")
    x.add_argument("manifest")
    x.add_argument("state")
    x = sub.add_parser("validate-run")
    x.add_argument("manifest")
    x = sub.add_parser("select-model")
    x.add_argument("prompt_id")
    x.add_argument(
        "--assurance",
        default="STANDARD",
        choices=["FAST", "STANDARD", "HIGH_ASSURANCE"],
    )
    x.add_argument("--include-nonproduction", action="store_true")
    x = sub.add_parser("auto-compile")
    x.add_argument("context_file")
    x = sub.add_parser("auto-plan")
    x.add_argument("target")
    x.add_argument("--intent-incomplete", action="store_true")
    x.add_argument("--skill-id")
    x.add_argument("--skill-required", action="store_true")
    x.add_argument("--allow-install", action="store_true")
    x.add_argument("--allow-create", action="store_true")
    x.add_argument("--loop", action="store_true")
    x.add_argument("--work-items", type=int, default=1)
    x.add_argument("--iterative-quality", action="store_true")
    x.add_argument("--measurable", action="store_true")
    x.add_argument("--max-iterations", type=int, default=3)
    x.add_argument("--max-no-improvement", type=int, default=1)
    x.add_argument("--external-effect", action="store_true")
    x.add_argument("--quality-threshold", type=float)
    x.add_argument("--acceptance-criterion", action="append", default=[])
    x = sub.add_parser("loop-decision")
    x.add_argument("--iteration", type=int, required=True)
    x.add_argument("--current-score", type=float)
    x.add_argument("--target-score", type=float)
    x.add_argument("--previous-scores", default="")
    x.add_argument("--verified", action="store_true")
    x.add_argument("--queue-remaining", type=int, default=0)
    x.add_argument("--budget-exhausted", action="store_true")
    x.add_argument("--hard-stop")
    x.add_argument("--human-stop", action="store_true")
    x.add_argument("--max-iterations", type=int, default=3)
    x.add_argument("--max-no-improvement", type=int, default=1)
    x.add_argument("--minimum-delta", type=float, default=0.01)
    x = sub.add_parser("record-metrics")
    x.add_argument("manifest")
    x.add_argument("--input-tokens", type=int, required=True)
    x.add_argument("--output-tokens", type=int, required=True)
    x.add_argument("--external-calls", type=int, default=0)
    x.add_argument("--wall-time-ms", type=int, required=True)
    x.add_argument("--cost", type=float)
    x.add_argument("--model-id")
    x.add_argument("--human-rating", type=float)
    x = sub.add_parser("resolve-templates")
    x.add_argument("prompt_id")
    x.add_argument(
        "--profile",
        choices=["minimum", "standard", "comprehensive"],
        default="standard",
    )
    x.add_argument("--artifact", action="append", default=[])
    x.add_argument("--include-conditional", action="store_true")
    x = sub.add_parser("add-prompt")
    x.add_argument("--source", required=True)
    x.add_argument("--title", required=True)
    x.add_argument("--category", default="enablement")
    x.add_argument("--role", default="operational")
    x.add_argument("--prompt-type", default="operational")
    x.add_argument(
        "--risk", default="medium", choices=["low", "medium", "high", "critical"]
    )
    x.add_argument("--mode", action="append", dest="modes", choices=sorted(MODES))
    x.add_argument("--related", action="append", default=[])
    x.add_argument("--requires", action="append", default=[])
    x.add_argument("--skill", action="append", default=[])
    x.add_argument("--template", action="append", default=[])
    x.add_argument("--conditional-template", action="append", default=[])
    x.add_argument("--department-pack", action="append", default=[])
    x.add_argument("--dry-run", action="store_true")
    x.add_argument("--approval-token")
    x.add_argument("--skip-full-tests", action="store_true")
    x = sub.add_parser("list")
    x.add_argument(
        "--kind",
        choices=["prompts", "scenarios", "packs", "models", "skills"],
        default="scenarios",
    )
    a = ap.parse_args()
    try:
        if a.cmd == "lookup":
            result = lookup(a.query, a.limit, a.kind)
        elif a.cmd == "route":
            result = route_intent(a.request, a.limit)
        elif a.cmd == "compare":
            result = compare_routes(a.targets)
        elif a.cmd == "lifecycle":
            try:
                from prompt_lifecycle import build_lifecycle_report
            except ImportError:
                from tools.prompt_lifecycle import build_lifecycle_report
            result = build_lifecycle_report(ROOT)
        elif a.cmd == "explain":
            result = explain(a.target)
        elif a.cmd == "pair-status":
            result = pair_review_disposition(
                a.planning_prompt_id,
                a.handoff_ready,
                a.review_status,
                a.revisions_applied,
            )
        elif a.cmd == "authorize-twin":
            result = authorize_exact_twin(
                a.planning_prompt_id,
                a.execution_prompt_id,
                a.handoff_ready,
                a.plan_review_approved,
                a.user_approved,
            )
        elif a.cmd == "plan":
            result = plan(
                a.target,
                a.mode,
                a.root,
                a.out,
                a.budget_prompts,
                a.assurance,
                a.dry_run,
            )
        elif a.cmd == "freeze-pair-handoff":
            result = freeze_pair_handoff(
                a.manifest, a.planning_prompt_id, a.handoff_hash
            )
        elif a.cmd == "review-pair-plan":
            result = record_plan_review(
                a.manifest, a.planning_prompt_id, a.decision, a.reviewer, a.feedback
            )
        elif a.cmd == "consent-pair-execution":
            result = record_execution_consent(
                a.manifest, a.planning_prompt_id, a.approve, a.user
            )
        elif a.cmd == "transition":
            result = transition(a.manifest, a.state)
        elif a.cmd == "validate-run":
            result = validate_run(a.manifest)
        elif a.cmd == "select-model":
            result = select_model(a.prompt_id, a.assurance, a.include_nonproduction)
        elif a.cmd == "auto-compile":
            result = auto_plan_from_context(
                json.loads(Path(a.context_file).read_text(encoding="utf-8"))
            )
        elif a.cmd == "auto-plan":
            result = auto_plan(
                a.target,
                not a.intent_incomplete,
                a.skill_id,
                a.skill_required,
                a.allow_install,
                a.allow_create,
                a.loop,
                a.work_items,
                a.iterative_quality,
                a.measurable,
                a.max_iterations,
                a.max_no_improvement,
                a.external_effect,
                a.quality_threshold,
                a.acceptance_criterion,
            )
        elif a.cmd == "loop-decision":
            result = adjudicate_loop(
                a.iteration,
                a.current_score,
                a.target_score,
                [float(x) for x in a.previous_scores.split(",") if x.strip()],
                a.verified,
                a.queue_remaining,
                a.budget_exhausted,
                a.hard_stop,
                a.human_stop,
                a.max_iterations,
                a.max_no_improvement,
                a.minimum_delta,
            )
        elif a.cmd == "record-metrics":
            result = record_metrics(
                a.manifest,
                a.input_tokens,
                a.output_tokens,
                a.external_calls,
                a.wall_time_ms,
                a.cost,
                a.model_id,
                a.human_rating,
            )
        elif a.cmd == "resolve-templates":
            from template_router import resolve as resolve_template_routes

            result = resolve_template_routes(
                a.prompt_id,
                profile=a.profile,
                artifacts=a.artifact,
                include_conditional=a.include_conditional,
                root=ROOT,
            )
        elif a.cmd == "add-prompt":
            from add_prompt import (
                add_prompt_transaction,
                CONTROL_REFS,
                DEFAULT_TEMPLATE_ROUTES,
                DEFAULT_CONDITIONAL_TEMPLATES,
            )

            result = add_prompt_transaction(
                ROOT,
                source=Path(a.source),
                title=a.title,
                category=a.category,
                prompt_role=a.role,
                prompt_type=a.prompt_type,
                risk_level=a.risk,
                allowed_modes=a.modes or ("DRAFT_ONLY", "APPLY_SAFE", "VERIFY_ONLY"),
                related_prompts=a.related,
                requires=a.requires or CONTROL_REFS,
                preferred_skills=a.skill,
                template_routes=a.template or DEFAULT_TEMPLATE_ROUTES,
                conditional_template_routes=a.conditional_template
                or DEFAULT_CONDITIONAL_TEMPLATES,
                department_packs=a.department_pack,
                run_full_tests=not a.skip_full_tests,
                dry_run=a.dry_run,
                approval_token=a.approval_token,
            )
        elif a.kind == "prompts":
            result = [
                {
                    "id": p["prompt_id"],
                    "capability_id": p.get("capability_id"),
                    "title": p["title"],
                    "category": p["category"],
                }
                for p in CAT["prompts"]
            ]
        elif a.kind == "packs":
            result = sorted(PACKS["department_packs"])
        elif a.kind == "models":
            result = PROFILES["profiles"]
        elif a.kind == "skills":
            result = [
                {"skill_id": s["skill_id"], **skill_status(s["skill_id"])}
                for s in SKILLS["skills"]
            ]
        else:
            result = [
                {"id": s["scenario_id"], "title": s["title"]}
                for s in SC["composite_scenarios"]
            ]
        try:
            prompt_id = (
                getattr(a, "prompt_id", None) if hasattr(a, "prompt_id") else None
            )
            target = getattr(a, "target", None) if hasattr(a, "target") else None
            append_event(
                "prompt_invocation"
                if prompt_id or (isinstance(target, str) and target.startswith("MD-"))
                else "tool",
                a.cmd,
                "pass",
                tool="md.py",
                prompt_id=prompt_id
                or (
                    target
                    if isinstance(target, str) and target.startswith("MD-")
                    else None
                ),
                scenario_id=(
                    target
                    if isinstance(target, str) and target.startswith("C-")
                    else None
                ),
                context={"arg_count": max(0, len(sys.argv) - 2)},
            )
        except Exception:
            pass
        print(json.dumps(result, indent=2))
    except Exception as exc:
        if "_MD_TUI" in globals() and hasattr(_MD_TUI, "fail"):
            _MD_TUI.fail(exc)
        if os.environ.get("MD_DEBUG"):
            raise
        print(
            json.dumps(
                {
                    "status": "error",
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
                indent=2,
            )
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
