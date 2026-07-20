#!/usr/bin/env python3
if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
lock = json.loads((ROOT / "config/skills.lock.json").read_text())
errors = []
for e in lock["entries"]:
    if e["lock_status"] == "resolved":
        if not re.fullmatch(r"[0-9a-f]{40}", e.get("commit_sha") or ""):
            errors.append(e["skill_id"] + ": bad sha")
        if not re.fullmatch(r"[0-9a-f]{64}", e.get("tarball_sha256") or ""):
            errors.append(e["skill_id"] + ": bad tarball hash")
    if e["lock_status"] != "resolved" and e.get("auto_install_allowed"):
        errors.append(e["skill_id"] + ": unresolved but auto-installable")
print(
    json.dumps(
        {
            "status": "pass" if not errors else "fail",
            "entries": len(lock["entries"]),
            "resolved": sum(x["lock_status"] == "resolved" for x in lock["entries"]),
            "errors": errors,
        },
        indent=2,
    )
)
sys.exit(1 if errors else 0)
