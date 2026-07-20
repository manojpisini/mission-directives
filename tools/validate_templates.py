#!/usr/bin/env python3
from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    reg = json.loads((ROOT / "config/template_registry.json").read_text())
    cat = json.loads((ROOT / "catalog.json").read_text())
    errors = []
    ids = {t["template_id"] for t in reg["templates"]}
    used = set()
    required_used = set()
    if len(ids) != len(reg["templates"]):
        errors.append("duplicate template ids")
    for t in reg["templates"]:
        p = ROOT / t["path"]
        if not p.exists():
            errors.append(f"missing template {t['template_id']}")
        elif len(p.read_text(encoding="utf-8").splitlines()) < 45:
            errors.append(f"shallow template {t['template_id']}")
        if not t.get("required_by_prompt_ids") and not t.get(
            "conditional_by_prompt_ids"
        ):
            errors.append(f"unrouted template {t['template_id']}")
    for p in cat["prompts"]:
        required = p.get("template_routes") or []
        conditional = p.get("conditional_template_routes") or []
        if not required:
            errors.append(f"{p['prompt_id']}: no required template routes")
        unknown = (set(required) | set(conditional)) - ids
        if unknown:
            errors.append(f"{p['prompt_id']}: unknown templates {sorted(unknown)}")
        if set(required) & set(conditional):
            errors.append(f"{p['prompt_id']}: duplicate required/conditional route")
        if len(required) > 8:
            errors.append(
                f"{p['prompt_id']}: excessive unconditional template routes ({len(required)})"
            )
        required_used.update(required)
        used.update(required)
        used.update(conditional)
    if used != ids:
        errors.append(f"template usage mismatch unused={sorted(ids - used)}")
    print(
        json.dumps(
            {
                "status": "pass" if not errors else "fail",
                "templates": len(ids),
                "prompts": len(cat["prompts"]),
                "used_templates": len(used),
                "required_used_templates": len(required_used),
                "errors": errors,
            },
            indent=2,
        )
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
