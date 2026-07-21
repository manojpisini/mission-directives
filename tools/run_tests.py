#!/usr/bin/env python3
"""Run deterministic tests in bounded per-file subprocesses.

Per-file isolation prevents test-order interference and gives every file an
independent timeout. Sealed release receipts are mutated only with --publish.
"""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from security_utils import atomic_write_json, safe_child
except ImportError:
    from tools.security_utils import atomic_write_json, safe_child

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_RESULT_REL = ".prompt_suite/results/TEST_RESULTS.json"


def _junit_counts(path: Path) -> dict[str, int]:
    """Read structured pytest counts from a built-in JUnit XML report."""
    root = ET.parse(path).getroot()
    suites = (
        [root]
        if root.tag.rsplit("}", 1)[-1] == "testsuite"
        else [child for child in root if child.tag.rsplit("}", 1)[-1] == "testsuite"]
    )
    if not suites:
        raise ValueError(f"JUnit report contains no testsuite elements: {path}")
    keys = ("tests", "failures", "errors", "skipped")
    return {
        key: sum(int(suite.attrib.get(key, "0")) for suite in suites) for key in keys
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Write the canonical root TEST_RESULTS.json during a controlled release build.",
    )
    parser.add_argument(
        "--per-file-timeout",
        type=int,
        default=180,
        help="Maximum seconds allowed for each test file.",
    )
    args = parser.parse_args()
    if args.per_file_timeout < 1 or args.per_file_timeout > 1800:
        raise ValueError("--per-file-timeout must be between 1 and 1800 seconds")

    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONHASHSEED"] = "0"
    env["MD_NO_TUI"] = "1"
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTEST_PLUGINS", None)

    # Use uv run for subprocess when available (CI) so pytest resolves from venv
    pytest_cmd: list[str] = (
        ["uv", "run", "python", "-m", "pytest"]
        if shutil.which("uv")
        else [sys.executable, "-m", "pytest"]
    )

    test_files = sorted((ROOT / "tests").glob("test_*.py"))
    started = datetime.datetime.now(datetime.timezone.utc)
    outputs: list[str] = []
    failures: list[dict[str, object]] = []
    total_tests = 0

    with tempfile.TemporaryDirectory(prefix="md-test-logs-") as log_dir:
        env["MD_LOG_DIR"] = log_dir
        for test_file in test_files:
            relative = test_file.relative_to(ROOT).as_posix()
            junit_path = Path(log_dir) / f"{test_file.stem}.xml"
            try:
                proc = subprocess.run(
                    [*pytest_cmd, "-q", relative, f"--junitxml={junit_path}"],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    timeout=args.per_file_timeout,
                    stdin=subprocess.DEVNULL,
                    env=env,
                )
                output = (proc.stdout + proc.stderr).strip()
                outputs.append(f"## {relative}\n{output}")
                junit_ok = True
                try:
                    counts = _junit_counts(junit_path)
                    total_tests += counts["tests"]
                except (OSError, ValueError, ET.ParseError) as exc:
                    junit_ok = False
                    failures.append(
                        {
                            "test_file": relative,
                            "return_code": proc.returncode,
                            "junit_error": str(exc),
                        }
                    )
                if proc.returncode != 0 and junit_ok:
                    failures.append(
                        {"test_file": relative, "return_code": proc.returncode}
                    )
            except subprocess.TimeoutExpired:
                outputs.append(
                    f"## {relative}\nTIMEOUT after {args.per_file_timeout} seconds"
                )
                failures.append(
                    {"test_file": relative, "timeout_seconds": args.per_file_timeout}
                )

    duration = (datetime.datetime.now(datetime.timezone.utc) - started).total_seconds()
    status = {
        "status": "pass" if not failures else "fail",
        "command": "python -m pytest -q <each tests/test_*.py>",
        "executed_at": started.isoformat(),
        "return_code": 0 if not failures else 1,
        "output": "\n\n".join(outputs),
        "test_count": total_tests,
        "test_files": len(test_files),
        "duration_seconds": round(duration, 2),
        "failures": failures,
        "limitations": [
            "Unit and deterministic runtime tests only; no external model or live skill execution."
        ],
    }
    target = (
        ROOT / "TEST_RESULTS.json"
        if args.publish
        else safe_child(ROOT, RUNTIME_RESULT_REL)
    )
    atomic_write_json(target, status)
    status["result_path"] = str(target)
    print(json.dumps(status, indent=2))
    return status["return_code"]


if __name__ == "__main__":
    raise SystemExit(main())
