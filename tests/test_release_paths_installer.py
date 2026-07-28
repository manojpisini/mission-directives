from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "src"))

from mission_directives import installer


def test_release_version_is_current_and_generated_guidance_uses_it():
    version = (ROOT / "VERSION").read_text().strip()
    assert version == "2.0.0"
    for path in (ROOT / "prompts").glob("*.md"):
        assert f"suite_version: {version}" in path.read_text(encoding="utf-8")
    for path in (ROOT / "templates").rglob("*.md"):
        assert f"suite_version: {version}" in path.read_text(encoding="utf-8")
    for name in ["AGENTS.md", "CLAUDE.md"]:
        assert f"Mission Directives **{version}**" in (ROOT / name).read_text(
            encoding="utf-8"
        )


def test_distribution_has_no_personal_home_paths():
    bad = []
    pattern = re.compile(
        r"C:\\\\Users\\\\[^%$<{/\\\\]+|/Users/[^/$<{]+|/home/[^/$<{]+|bl4nkslate",
        re.I,
    )
    for path in ROOT.rglob("*"):
        if any(part in path.parts for part in (".git", ".prompt_suite", ".venv", "node_modules")):
            continue
        if path.is_file() and path.suffix.lower() in {
            ".md", ".json", ".py", ".sh", ".ps1", ".toml", ".yaml", ".yml", ".txt"
        }:
            if path in {Path(__file__), ROOT / "tools/check_release_consistency.py"}:
                continue
            if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
                bad.append(path.relative_to(ROOT).as_posix())
    assert not bad, bad


def test_agent_path_resolution_for_all_platforms(monkeypatch, tmp_path):
    import agent_paths

    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    for system in ["windows", "linux", "macos"]:
        destinations = agent_paths.all_default_destinations(system=system)
        assert set(destinations) == {"agents", "claude-code", "opencode"}
        assert all(str(tmp_path / "home") in str(value) for value in destinations.values())


def test_installer_dry_run_and_complete_project_layout(tmp_path):
    project = tmp_path / "project with space"
    dry = installer.install_project(project, dry_run=True)
    assert dry["status"] == "dry_run"
    assert not (project / ".mission-directives").exists()

    result = installer.install_project(project)
    root = project / ".mission-directives"
    assert result["status"] == "installed"
    assert result["suite_destination"] == ".mission-directives/runtime"
    assert (root / "runtime/VERSION").read_text().strip() == "2.0.0"
    assert (root / "site/templates/base.html").is_file()
    assert (root / "site/static/viewer.css").is_file()
    assert (root / "project.json").is_file()
    assert (root / "config.json").is_file()
    for name in installer.OUTPUT_DIRS:
        assert (root / name).is_dir(), name
    for relative in [
        "catalog.json",
        "SCENARIO_CATALOG.json",
        "config/router_keywords.json",
        "schemas/project_context.schema.json",
        "tools/md.py",
        "tools/project_runtime.py",
    ]:
        assert (root / "runtime" / relative).is_file(), relative
    for relative in ["tests", "evaluations", "prompt_imports", "site", ".github"]:
        assert not (root / "runtime" / relative).exists(), relative
    ignore = (project / ".gitignore").read_text()
    assert "/.mission-directives/" in ignore
    for name in ["AGENTS.md", "CLAUDE.md"]:
        text = (project / name).read_text()
        assert text.count("<!-- BEGIN MD MANAGED GUIDANCE -->") == 1
        assert ".mission-directives/project.json" in text
        assert ".mission-directives/runtime/tools/md.py" in text


@pytest.mark.parametrize("mode", installer.TRACKING_MODES)
def test_tracking_modes_are_idempotent_and_preserve_human_ignore(mode, tmp_path):
    existing = "blog/\n"
    once = installer.managed_ignore(existing, mode)
    twice = installer.managed_ignore(once, mode)
    assert once == twice
    assert once.startswith("blog/\n")
    if mode == "outputs":
        assert "!/.mission-directives/project.json" in once
        assert "!/.mission-directives/plans/**" in once
    elif mode == "all":
        assert "/.mission-directives/state/" in once
        assert "/.mission-directives/\n" not in once


def test_upgrade_preserves_project_config_and_outputs(tmp_path):
    project = tmp_path / "upgrade"
    installer.install_project(project)
    root = project / ".mission-directives"
    (root / "reports/result.md").write_text("kept", encoding="utf-8")
    profile = json.loads((root / "project.json").read_text(encoding="utf-8"))
    profile["project"]["mission"] = "Keep this mission"
    (root / "project.json").write_text(json.dumps(profile), encoding="utf-8")
    installer.install_project(project, replace=True, tracking="outputs")
    assert (root / "reports/result.md").read_text() == "kept"
    assert json.loads((root / "project.json").read_text())["project"]["mission"] == "Keep this mission"
    assert json.loads((root / "config.json").read_text())["tracking_mode"] == "outputs"


def test_installer_rolls_back_project_files_on_guidance_failure(tmp_path, monkeypatch):
    project = tmp_path / "rollback"
    project.mkdir()
    (project / "AGENTS.md").write_text("human\n")
    (project / ".gitignore").write_text("existing\n")
    monkeypatch.setattr(installer, "_sync_guidance", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("forced")))
    with pytest.raises(RuntimeError, match="forced"):
        installer.install_project(project)
    assert not (project / ".mission-directives").exists()
    assert (project / "AGENTS.md").read_text() == "human\n"
    assert (project / ".gitignore").read_text() == "existing\n"


def test_installation_receipt_validates_against_schema(tmp_path):
    project = tmp_path / "schema"
    installer.install_project(project)
    receipt = json.loads(
        (project / ".mission-directives/state/installation-receipt.json").read_text()
    )
    schema = json.loads((ROOT / "schemas/installation_receipt.schema.json").read_text())
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(receipt)
    )
    assert not errors, errors


def test_managed_legacy_migration_preserves_unmarked_directories(tmp_path):
    project = tmp_path / "legacy"
    (project / "prompts").mkdir(parents=True)
    (project / ".prompt_suite").mkdir()
    (project / ".prompt_suite/installation-receipt.json").write_text("{}")
    (project / "reports").mkdir()
    (project / "reports/.mission-directives-managed.json").write_text("{}")
    (project / "reports/old.md").write_text("legacy")
    (project / "docs").mkdir()
    (project / "docs/human.md").write_text("human")
    preview = installer.migrate_project(project)
    assert preview["managed_paths"] == ["prompts", ".prompt_suite", "reports"]
    result = installer.migrate_project(project, apply=True)
    assert result["status"] == "migrated"
    assert (project / ".mission-directives/reports/old.md").read_text() == "legacy"
    assert (project / "docs/human.md").read_text() == "human"


def test_uninstall_preview_and_apply_preserve_unmanaged_content(tmp_path):
    project = tmp_path / "uninstall"
    installer.install_project(project)
    (project / "keep.txt").write_text("keep")
    assert installer.uninstall_project(project)["status"] == "dry_run"
    result = installer.uninstall_project(project, apply=True)
    assert result["status"] == "removed"
    assert not (project / ".mission-directives").exists()
    assert (project / "keep.txt").read_text() == "keep"
    assert "BEGIN MD MANAGED GUIDANCE" not in (project / "AGENTS.md").read_text()


def test_source_installer_cli_reports_json_without_traceback(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/install.py"), str(tmp_path / "cli"), "--dry-run"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "PROGRESS" in proc.stderr and "[SUCCESS]" in proc.stderr
    assert json.loads(proc.stdout)["status"] == "dry_run"
