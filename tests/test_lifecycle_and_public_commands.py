import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "prompt_lifecycle", ROOT / "tools/prompt_lifecycle.py"
)
LIFECYCLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LIFECYCLE)


def _run(*args):
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def test_lifecycle_report_exposes_real_external_completion_boundaries():
    report = LIFECYCLE.build_lifecycle_report(ROOT)
    assert report["structural_surface"] == "implemented"
    assert report["intent_routing"]["prompt_body_reads_during_selection"] is False
    assert report["library"]["prompt_count"] > 0
    assert report["golden_coverage"]["human_reviewed_runs"] == len(
        list((ROOT / "evaluations/golden_runs").glob("*/human_reviewed_manifest.json"))
    )
    if report["status"] != "complete":
        assert report["external_completion_blockers"]


def test_readme_public_routing_commands_execute_successfully():
    routed = _run("tools/md.py", "route", "MD advanced audit fix verify repository")
    assert routed["selection"]["targets"] == ["C-108"]
    compared = _run("tools/md.py", "compare", "C-108", "C-63")
    assert compared["targets"] == ["C-108", "C-63"]
    explained = _run("tools/md.py", "explain", "C-108")
    assert explained["target"] == "C-108"


def test_historical_compatibility_snapshots_are_not_distributed():
    assert {path.name for path in (ROOT / "compatibility").iterdir()} == {
        "agent_skill_paths.json",
        "capability_identity_registry.json",
    }
