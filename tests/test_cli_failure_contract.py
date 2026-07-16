from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_md_schema_error_is_clean_json_without_traceback(tmp_path):
    context = tmp_path / "bad.json"
    context.write_text(json.dumps({"target": "MD-198", "maximum_inner_iterations": "not-an-int"}), encoding="utf-8")
    env = os.environ.copy(); env["MD_NO_TUI"] = "1"; env["MD_LOG_DIR"] = str(tmp_path / "logs")
    proc = subprocess.run([sys.executable, str(ROOT / "tools/md.py"), "auto-compile", str(context)], text=True, capture_output=True, env=env)
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "error"


def test_tool_runtime_marks_unhandled_exception_failed(tmp_path):
    script = tmp_path / "crash.py"
    script.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(ROOT / 'tools')!r})\n"
        "from tool_runtime import bootstrap_tool\n"
        "bootstrap_tool(__file__)\n"
        "raise RuntimeError('boom')\n",
        encoding="utf-8",
    )
    env = os.environ.copy(); env["MD_NO_TUI"] = "1"; env["MD_LOG_DIR"] = str(tmp_path / "logs")
    proc = subprocess.run([sys.executable, str(script)], text=True, capture_output=True, env=env)
    assert proc.returncode == 1
    assert "DONE:" not in proc.stderr
    assert "FAIL:" in proc.stderr
    log = next((tmp_path / "logs").glob("*.toml")).read_text(encoding="utf-8")
    assert 'status = "fail"' in log
    assert "boom" in log


def test_plan_run_ids_are_unique_for_rapid_invocation():
    sys.path.insert(0, str(ROOT / "tools"))
    import md
    one = md.plan("MD-198", dry_run=True)
    two = md.plan("MD-198", dry_run=True)
    assert one["run_id"] != two["run_id"]


def test_auto_orchestration_quality_fields_are_not_silently_dropped():
    sys.path.insert(0, str(ROOT / "tools"))
    import md
    result = md.auto_plan_from_context({
        "target": "MD-198",
        "loop": True,
        "iterative_quality": True,
        "measurable": True,
        "quality_threshold": 0.9,
        "acceptance_criteria": ["all findings closed"],
    })
    assert result["quality_threshold"] == 0.9
    assert result["acceptance_criteria"] == ["all findings closed"]


def test_transition_missing_state_returns_clean_value_error(tmp_path):
    sys.path.insert(0, str(ROOT / "tools"))
    import md
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    try:
        md.transition(str(manifest), "investigating")
    except ValueError as exc:
        assert "missing a valid state" in str(exc)
    else:
        raise AssertionError("missing state must fail")
