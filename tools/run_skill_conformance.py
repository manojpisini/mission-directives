#!/usr/bin/env python3
"""Validate a locked or approved local skill output against its MD conformance contract.

The tool does not execute a skill. By default it writes a runtime result below
.prompt_suite/runtime and leaves the sealed conformance definition unchanged.
Use --publish only during an explicitly controlled release/update operation.
"""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse
import datetime as dt
import json
from pathlib import Path

try:
    from security_utils import (
        atomic_write_json,
        ensure_no_symlink_components,
        exclusive_lock,
        read_json_bounded,
        safe_child,
        validate_identifier,
    )
except ImportError:
    from tools.security_utils import (
        atomic_write_json,
        ensure_no_symlink_components,
        exclusive_lock,
        read_json_bounded,
        safe_child,
        validate_identifier,
    )

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skill-id", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--allow-missing-optional", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--result-path")
    a = ap.parse_args()
    skill_id = validate_identifier(a.skill_id, kind="skill")
    spec_path = safe_child(ROOT / "evaluations" / "skills", f"{skill_id}.json")
    if not spec_path.is_file():
        raise SystemExit("Unknown skill conformance spec")
    spec = read_json_bounded(spec_path)
    locks = {
        row["skill_id"]: row
        for row in read_json_bounded(ROOT / "config/skills.lock.json")["entries"]
    }
    lock = locks.get(skill_id)
    errors: list[str] = []
    if spec.get("lock_required", True) and (
        not lock or lock.get("lock_status") != "resolved"
    ):
        errors.append("skill lock is not resolved")

    out = ensure_no_symlink_components(Path(a.output_dir).expanduser())
    if not out.is_dir():
        errors.append(f"output directory does not exist: {out}")
    else:
        # Validate exact contract-relative paths. Basename-only matching could
        # accept an artifact from the wrong route or directory.
        for route in spec["expected_contract"].get("expected_artifacts", []):
            artifacts = [("primary", route["primary"])]
            if not a.allow_missing_optional:
                artifacts.extend(
                    ("supporting", item) for item in route.get("supporting", [])
                )
            for role, artifact in artifacts:
                try:
                    candidate = safe_child(out, artifact["path"])
                except ValueError as exc:
                    errors.append(f"{route['prompt_id']}: unsafe {role} path: {exc}")
                    continue
                if not candidate.is_file():
                    errors.append(
                        f"missing {role} artifact for {route['prompt_id']}: {artifact['path']}"
                    )
                    continue
                try:
                    fmt = artifact.get("format", "").lower()
                    if fmt == "json":
                        json.loads(candidate.read_text(encoding="utf-8"))
                    elif fmt == "jsonl":
                        for number, line in enumerate(
                            candidate.read_text(encoding="utf-8").splitlines(), 1
                        ):
                            if line.strip():
                                json.loads(line)
                    elif candidate.stat().st_size == 0:
                        errors.append(
                            f"empty {role} artifact for {route['prompt_id']}: {artifact['path']}"
                        )
                except Exception as exc:
                    errors.append(
                        f"invalid {artifact.get('format', 'artifact')} {candidate}: {exc}"
                    )

    result = {
        "status": "pass" if not errors else "fail",
        "skill_id": skill_id,
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "output_dir": str(out),
        "errors": errors,
        "lock_commit": lock.get("commit_sha") if lock else None,
        "artifact_output_remains_quarantined": bool(errors),
    }
    if a.publish:
        lock_path = safe_child(
            ROOT, f".prompt_suite/locks/skill-conformance-{skill_id}.lock"
        )
        with exclusive_lock(lock_path):
            current = read_json_bounded(spec_path)
            updated = dict(current)
            updated["live_status"] = "pass" if not errors else "quarantined"
            updated["last_result"] = result
            atomic_write_json(spec_path, updated)
        result["definition_updated"] = str(spec_path)
    target = (
        ensure_no_symlink_components(Path(a.result_path).expanduser())
        if a.result_path
        else safe_child(
            ROOT, f".prompt_suite/runtime/skill-conformance/{skill_id}.json"
        )
    )
    atomic_write_json(target, result)
    result["result_path"] = str(target)
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
