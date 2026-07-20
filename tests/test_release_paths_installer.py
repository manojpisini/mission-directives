from __future__ import annotations
import importlib.util, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_release_version_is_current_and_generated_guidance_uses_it():
    version = (ROOT / "VERSION").read_text().strip()
    assert version == "1.8.3"
    for p in (ROOT / "prompts").glob("*.md"):
        assert f"suite_version: {version}" in p.read_text(encoding="utf-8")
    for p in (ROOT / "templates").rglob("*.md"):
        assert f"suite_version: {version}" in p.read_text(encoding="utf-8")
    for name in ["AGENTS.md", "CLAUDE.md"]:
        assert f"Mission Directives **{version}**" in (ROOT / name).read_text(
            encoding="utf-8"
        )


def test_distribution_has_no_personal_home_paths():
    bad = []
    pattern = re.compile(
        r"C:\\\\Users\\\\[^%$<{/\\\\]+|/Users/[^/$<{]+|/home/[^/$<{]+|bl4nkslate", re.I
    )
    skip_parts = {Path(__file__), ROOT / "tools/check_release_consistency.py"}
    for p in ROOT.rglob("*"):
        if p in skip_parts or any(
            part in p.parts for part in (".venv", "node_modules")
        ):
            continue
        if p.is_file() and p.suffix.lower() in {
            ".md",
            ".json",
            ".py",
            ".sh",
            ".ps1",
            ".toml",
            ".yaml",
            ".yml",
            ".txt",
        }:
            if pattern.search(p.read_text(encoding="utf-8", errors="ignore")):
                bad.append(str(p.relative_to(ROOT)))
    assert not bad, bad


def test_agent_path_resolution_for_all_platforms(monkeypatch, tmp_path):
    import agent_paths

    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    for key in [
        "MD_AGENTS_SKILLS_DIR",
        "MD_CLAUDE_SKILLS_DIR",
        "MD_OPENCODE_SKILLS_DIR",
    ]:
        monkeypatch.delenv(key, raising=False)
    for system in ["windows", "linux", "macos"]:
        destinations = agent_paths.all_default_destinations(system=system)
        assert set(destinations) == {"agents", "claude-code", "opencode"}
        assert all(str(tmp_path / "home") in str(v) for v in destinations.values())
    assert "MD_AGENTS_SKILLS_DIR" in agent_paths.logical("agents")


def test_installer_dry_run_and_full_install(tmp_path):
    installer = _load(ROOT / "tools/install.py", "md_install")
    project = tmp_path / "project with space"
    dry = installer.install(project, dry_run=True)
    assert dry["status"] == "dry_run"
    assert not (project / "prompts").exists()
    result = installer.install(project)
    assert result["status"] == "installed"
    assert (project / "prompts" / "VERSION").read_text().strip() == "1.8.3"
    ignore = (project / ".gitignore").read_text()
    assert (
        "/prompts/" in ignore
        and "/.prompt_suite/" in ignore
        and "/.md-prompts-backup-*/" in ignore
        and "/.md-cleanup-staging-*/" in ignore
        and "/.md-cleanup.lock" in ignore
        and "/docs/" not in ignore
    )
    assert (project / "docs").is_dir()
    for name in ["AGENTS.md", "CLAUDE.md"]:
        text = (project / name).read_text()
        assert text.count("<!-- BEGIN MD MANAGED GUIDANCE -->") == 1
        assert "prompts/tools/md.py" in text


def test_installer_refuses_overwrite_without_replace_and_preserves_backup(tmp_path):
    installer = _load(ROOT / "tools/install.py", "md_install_replace")
    project = tmp_path / "p"
    installer.install(project)
    marker = project / "prompts" / "LOCAL_MARKER"
    marker.write_text("old")
    try:
        installer.install(project)
        assert False
    except FileExistsError:
        pass
    result = installer.install(project, replace=True)
    assert not marker.exists()
    assert result["backup"]
    assert Path(result["backup"]).exists()


def test_installer_rolls_back_project_files_on_guidance_failure(tmp_path, monkeypatch):
    installer = _load(ROOT / "tools/install.py", "md_install_rollback")
    project = tmp_path / "rollback-project"
    project.mkdir()
    (project / "AGENTS.md").write_text("human\n")
    (project / ".gitignore").write_text("existing\n")
    original_import = __import__

    def broken_import(name, *args, **kwargs):
        if name == "sync_agent_guidance":
            raise RuntimeError("forced guidance failure")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", broken_import)
    try:
        installer.install(project)
        assert False
    except RuntimeError:
        pass
    assert not (project / "prompts").exists()
    assert (project / "AGENTS.md").read_text() == "human\n"
    assert (project / ".gitignore").read_text() == "existing\n"


def test_installation_receipt_validates_against_schema(tmp_path):
    from jsonschema import Draft202012Validator, FormatChecker

    installer = _load(ROOT / "tools/install.py", "md_install_schema")
    project = tmp_path / "schema-project"
    result = installer.install(project)
    receipt = json.loads(
        (project / ".prompt_suite/installation-receipt.json").read_text()
    )
    schema = json.loads((ROOT / "schemas/installation_receipt.schema.json").read_text())
    assert result["status"] == "installed"
    assert result["suite_destination"] == "prompts"
    assert result["suite_version"] == receipt["suite_version"]
    assert (
        Path(result["receipt_path"]).resolve()
        == (project / ".prompt_suite/installation-receipt.json").resolve()
    )
    assert not list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            receipt
        )
    )


def test_installer_cli_reports_progress_and_formatted_success(tmp_path):
    import subprocess

    project = tmp_path / "cli-progress-project"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/install.py"),
            str(project),
            "--dry-run",
            "--no-tui",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    assert "PROGRESS " in proc.stderr
    assert "SUCCESS" in proc.stderr
    assert "Mission Directives installer" in proc.stderr
    assert "Dry run completed" in proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "dry_run"


def test_installer_cli_reports_formatted_failure_without_traceback():
    import subprocess

    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/install.py"),
            str(ROOT),
            "--dry-run",
            "--no-tui",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 1
    assert "FAIL" in proc.stderr
    assert "Mission Directives installer" in proc.stderr
    assert "Traceback" not in proc.stderr
    assert "Project path must not" in proc.stderr


def test_powershell_installer_uses_parse_safe_version_formatting_and_status_messages():
    text = (ROOT / "tools/install.ps1").read_text(encoding="utf-8")
    assert "$SuiteVersion:" not in text
    assert "$Suite Version" not in text
    assert "Mission Directives {0}" in text
    assert "[SUCCESS]" in text and "[FAILURE]" in text
    assert "@InvocationArgs" in text
