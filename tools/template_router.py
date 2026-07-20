#!/usr/bin/env python3
"""Resolve mandatory and explicitly triggered conditional templates for a prompt."""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)
import argparse, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _terms(value: str) -> set[str]:
    return {x for x in re.split(r"[^a-z0-9]+", value.lower()) if len(x) > 2}


def resolve(
    prompt_id: str,
    *,
    profile: str = "standard",
    artifacts: list[str] | None = None,
    include_conditional: bool = False,
    root: Path = ROOT,
) -> dict:
    cat = json.loads((root / "catalog.json").read_text())
    reg = json.loads((root / "config/template_registry.json").read_text())
    by = {x["prompt_id"]: x for x in cat["prompts"]}
    templates = {x["template_id"]: x for x in reg["templates"]}
    if prompt_id not in by:
        raise ValueError(f"Unknown prompt: {prompt_id}")
    row = by[prompt_id]
    required = list(row.get("template_routes") or [])
    conditional = list(row.get("conditional_template_routes") or [])
    selected = list(required)
    reasons = {x: "required" for x in required}
    requested = _terms(" ".join(artifacts or []))
    if profile != "minimum":
        if include_conditional:
            for tid in conditional:
                selected.append(tid)
                reasons[tid] = "explicit_include_conditional"
        elif requested:
            for tid in conditional:
                meta = templates.get(tid, {})
                searchable = " ".join(
                    [
                        tid,
                        meta.get("title", ""),
                        meta.get("purpose", ""),
                        meta.get("family", ""),
                    ]
                )
                if requested & _terms(searchable):
                    selected.append(tid)
                    reasons[tid] = "artifact_trigger"
    selected = list(dict.fromkeys(selected))
    missing = [x for x in selected if x not in templates]
    return {
        "status": "resolved" if not missing else "blocked",
        "prompt_id": prompt_id,
        "profile": profile,
        "requested_artifacts": artifacts or [],
        "required_template_routes": required,
        "conditional_template_routes": conditional,
        "selected_template_routes": selected,
        "selection_reasons": reasons,
        "resolved_paths": [templates[x]["path"] for x in selected if x in templates],
        "missing_templates": missing,
        "policy": "required_resolve_then_conditionally_select_by_requested_artifact",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prompt_id")
    ap.add_argument(
        "--profile",
        choices=["minimum", "standard", "comprehensive"],
        default="standard",
    )
    ap.add_argument("--artifact", action="append", default=[])
    ap.add_argument("--include-conditional", action="store_true")
    a = ap.parse_args()
    try:
        result = resolve(
            a.prompt_id,
            profile=a.profile,
            artifacts=a.artifact,
            include_conditional=a.include_conditional,
        )
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
