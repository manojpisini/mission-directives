#!/usr/bin/env python3
"""Report prompt-library lifecycle coverage from canonical repository evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_lifecycle_report(root: Path = ROOT) -> dict[str, Any]:
    catalog = _load(root / "catalog.json")
    scenarios = _load(root / "SCENARIO_CATALOG.json")["composite_scenarios"]
    locks = _load(root / "config/skills.lock.json").get("entries", [])
    profiles = _load(root / "config/model_profiles.json").get("profiles", [])
    golden_manifests = sorted(
        (root / "evaluations/golden_runs").glob("*/human_reviewed_manifest.json")
    )
    golden_targets = {path.parent.name for path in golden_manifests}
    skill_files = sorted((root / "evaluations/skills").glob("*.json"))
    live_skill_passes = sum(
        1 for path in skill_files if _load(path).get("live_status") == "pass"
    )
    resolved_locks = sum(1 for row in locks if row.get("lock_status") == "resolved")
    measured_models = sum(
        1
        for row in profiles
        if row.get("measurement_status") == "measured"
        and row.get("production_eligible") is True
    )
    prompt_ids = {row["prompt_id"] for row in catalog["prompts"]}
    scenario_ids = {row["scenario_id"] for row in scenarios}
    external_blockers = []
    if not golden_manifests:
        external_blockers.append("No human-reviewed golden run has been promoted.")
    if not live_skill_passes:
        external_blockers.append("No skill conformance definition has a live passing result.")
    if not measured_models:
        external_blockers.append("No measured model profile is production eligible.")

    return {
        "status": "external_evidence_pending" if external_blockers else "complete",
        "structural_surface": "implemented",
        "intent_routing": {
            "selector": "tools/keyword_context.py",
            "entry_point": "python tools/md.py route",
            "prompt_body_reads_during_selection": False,
        },
        "library": {
            "prompt_count": len(prompt_ids),
            "scenario_count": len(scenario_ids),
        },
        "golden_coverage": {
            "human_reviewed_runs": len(golden_manifests),
            "covered_targets": sorted(golden_targets),
            "prompts_without_promoted_run": len(prompt_ids - golden_targets),
            "scenarios_without_promoted_run": len(scenario_ids - golden_targets),
        },
        "skill_evidence": {
            "lock_entries": len(locks),
            "resolved_locks": resolved_locks,
            "unresolved_locks": len(locks) - resolved_locks,
            "live_conformance_passes": live_skill_passes,
        },
        "model_evidence": {
            "profile_count": len(profiles),
            "production_eligible_measured_models": measured_models,
        },
        "machine_reference_runs": len(
            list((root / "evaluations/golden_runs").glob("*/manifest.json"))
        ),
        "external_completion_blockers": external_blockers,
        "completion_rule": "Complete means deterministic validation passes and every external evidence blocker is resolved with real reviewed evidence.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    print(json.dumps(build_lifecycle_report(), indent=None if args.compact else 2))


if __name__ == "__main__":
    main()
