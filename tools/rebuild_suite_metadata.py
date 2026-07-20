#!/usr/bin/env python3
from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()

rows = []
for path in sorted((ROOT / "prompts").glob("*.md")):
    text = path.read_text(encoding="utf-8")
    _, fm, _ = text.split("---", 2)
    meta = yaml.safe_load(fm)
    rows.append(meta)
rows.sort(key=lambda x: x["sequence"])

catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
catalog["suite_version"] = VERSION
catalog["prompt_count"] = len(rows)
catalog["prompts"] = rows
(ROOT / "catalog.json").write_text(
    json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

identity_path = ROOT / "compatibility/capability_identity_registry.json"
identity = json.loads(identity_path.read_text(encoding="utf-8"))
identity["version"] = VERSION
identity["suite_version"] = VERSION
identity["capabilities"] = [
    {
        "capability_id": m["capability_id"],
        "prompt_id": m["prompt_id"],
        "prompt_slug": m["prompt_slug"],
        "sequence": m["sequence"],
        "title": m["title"],
        "status": "active",
    }
    for m in rows
]
identity_path.write_text(
    json.dumps(identity, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

by_id = {m["prompt_id"]: m for m in rows}
for name in (
    "md_to_agent_library_crosswalk.json",
    "md_to_prompt_type_library_crosswalk.json",
):
    path = ROOT / "integrations" / name
    data = json.loads(path.read_text(encoding="utf-8"))
    for mapping in data.get("mappings", []):
        prompt = by_id.get(mapping.get("md_prompt_id"))
        if prompt:
            mapping["capability_id"] = prompt["capability_id"]
            mapping["title"] = prompt["title"]
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

# Rebuild category taxonomy from canonical prompt frontmatter.
category_path = ROOT / "config/category_taxonomy.json"
category_data = {"categories": {}}
for meta in rows:
    entry = category_data["categories"].setdefault(
        meta["category"],
        {"prompt_ids": [], "roles": [], "evidence_lanes": [], "media": []},
    )
    entry["prompt_ids"].append(meta["prompt_id"])
    if meta.get("prompt_role") not in entry["roles"]:
        entry["roles"].append(meta.get("prompt_role"))
    lane = meta.get("evidence_lane")
    if lane and lane not in entry["evidence_lanes"]:
        entry["evidence_lanes"].append(lane)
    for medium in meta.get("output_media") or []:
        if medium not in entry["media"]:
            entry["media"].append(medium)
for entry in category_data["categories"].values():
    entry["prompt_ids"].sort(key=lambda value: int(value.split("-")[1]))
    entry["roles"].sort()
    entry["evidence_lanes"].sort()
    entry["media"].sort()
category_path.write_text(
    json.dumps(category_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

# Rebuild template reverse routes and the prompt crosswalk from canonical prompts.
template_registry_path = ROOT / "config/template_registry.json"
template_registry = json.loads(template_registry_path.read_text(encoding="utf-8"))
for template in template_registry.get("templates", []):
    template_id = template["template_id"]
    template["required_by_prompt_ids"] = sorted(
        [
            m["prompt_id"]
            for m in rows
            if template_id in (m.get("template_routes") or [])
        ],
        key=lambda value: int(value.split("-")[1]),
    )
    template["conditional_by_prompt_ids"] = sorted(
        [
            m["prompt_id"]
            for m in rows
            if template_id in (m.get("conditional_template_routes") or [])
        ],
        key=lambda value: int(value.split("-")[1]),
    )
template_registry["suite_version"] = VERSION
template_registry_path.write_text(
    json.dumps(template_registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

template_crosswalk = {"suite_version": VERSION, "mappings": []}
for template in template_registry.get("templates", []):
    prompt_ids = sorted(
        set(template.get("required_by_prompt_ids", []))
        | set(template.get("conditional_by_prompt_ids", [])),
        key=lambda value: int(value.split("-")[1]),
    )
    template_crosswalk["mappings"].append(
        {
            "template_id": template["template_id"],
            "prompt_ids": prompt_ids,
            "path": template["path"],
        }
    )
template_crosswalk["mappings"].sort(key=lambda row: row["template_id"])
(ROOT / "integrations/template_to_prompt_crosswalk.json").write_text(
    json.dumps(template_crosswalk, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8",
)

lines = [
    "# Prompt Catalog",
    "",
    f"**Prompt count:** **{len(rows)}**",
    "",
    "All prompts use canonical authorization, least-privileged tool policy, runtime markers, and task-specific completion criteria. Every genuine planning/execution pair requires user plan review, revision and re-freezing when requested, explicit execution consent, and exact reciprocal twin dispatch.",
    "",
    "| Seq | ID | Capability ID | Prompt | Role | Category | Evidence | Risk | Modes | Pair | Review gate | Templates | Preferred skills |",
    "|---:|---|---|---|---|---|---|---|---|---|---|---|---|",
]
for m in rows:
    pair = f"`{m.get('paired_prompt_id')}`" if m.get("paired_prompt_id") else "`—`"
    review = (
        "plan review → exact twin consent"
        if m.get("prompt_role") == "investigative" and m.get("paired_prompt_id")
        else "reviewed handoff required"
        if m.get("prompt_role") == "executive"
        else "—"
    )
    templates = ", ".join(f"`{x}`" for x in (m.get("template_routes") or [])) or "—"
    skills = ", ".join(f"`{x}`" for x in (m.get("preferred_skills") or [])) or "—"
    modes = ", ".join(m.get("allowed_modes") or [])
    evidence = m.get("evidence_lane", "control")
    lines.append(
        f"| {m['sequence']} | `{m['prompt_id']}` | `{m['capability_id']}` | [{m['title']}](../{m['canonical_path']}) | `{m['prompt_role']}` | `{m['category']}` | `{evidence}` | `{m['risk_level']}` | {modes} | {pair} | {review} | {templates} | {skills} |"
    )
(ROOT / "docs/PROMPT_CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(
    json.dumps(
        {"status": "pass", "suite_version": VERSION, "prompt_count": len(rows)},
        indent=2,
    )
)
