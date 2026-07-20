#!/usr/bin/env python3
from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)


from pathlib import Path
import argparse
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config/capability_graph.json"


def build() -> dict:
    rows = []
    for path in sorted((ROOT / "prompts").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        _, frontmatter, _ = text.split("---", 2)
        rows.append(yaml.safe_load(frontmatter))
    nodes = [
        {
            "id": meta["prompt_id"],
            "capability_id": meta["capability_id"],
            "role": meta["prompt_role"],
            "category": meta["category"],
            "surface": meta.get("change_surface"),
            "evidence_lane": meta.get("evidence_lane"),
            "preferred_skills": meta.get("preferred_skills") or [],
            "paired_prompt_id": meta.get("paired_prompt_id"),
            "plan_review_required": bool(meta.get("plan_review_required")),
            "reviewed_handoff_required": bool(meta.get("reviewed_handoff_required")),
            "execution_consent_required": bool(meta.get("execution_consent_required")),
            "exact_twin_only": bool(meta.get("exact_twin_only")),
        }
        for meta in rows
    ]
    edges = []
    seen = set()
    for meta in rows:
        prompt_id = meta["prompt_id"]
        for dependency in meta.get("requires") or []:
            edge = (dependency, prompt_id, "requires")
            if dependency != prompt_id and edge not in seen:
                seen.add(edge)
                edges.append({"from": dependency, "to": prompt_id, "type": "requires"})
        pair = meta.get("paired_prompt_id")
        if meta["prompt_role"] == "investigative" and pair:
            for edge_type in ("handoff", "plan_review_gate", "exact_twin_execution"):
                edge = (prompt_id, pair, edge_type)
                if edge not in seen:
                    seen.add(edge)
                    edges.append({"from": prompt_id, "to": pair, "type": edge_type})
    return {
        "suite_version": (ROOT / "VERSION").read_text().strip(),
        "nodes": nodes,
        "edges": edges,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    current = build()
    if args.check:
        existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else None
        ok = existing == current
        print(
            json.dumps(
                {
                    "status": "pass" if ok else "fail",
                    "nodes": len(current["nodes"]),
                    "edges": len(current["edges"]),
                },
                indent=2,
            )
        )
        return 0 if ok else 1
    OUT.write_text(
        json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "nodes": len(current["nodes"]),
                "edges": len(current["edges"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
