from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _modules():
    installer = _load(ROOT / "tools/install.py", "md_install_for_cleanup")
    cleanup = _load(ROOT / "tools/cleanup.py", "md_cleanup")
    return installer, cleanup


def test_cleanup_dry_run_is_non_mutating_and_returns_bound_preview(tmp_path):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    installer.install(project)
    before = {
        "gitignore": (project / ".gitignore").read_bytes(),
        "agents": (project / "AGENTS.md").read_bytes(),
        "claude": (project / "CLAUDE.md").read_bytes(),
    }
    preview = cleanup.preview_cleanup(project)
    assert preview["status"] == "dry_run"
    assert preview["approval_token"]
    assert "prompts" in preview["planned_removals"]
    assert (project / "prompts").is_dir()
    assert (project / ".gitignore").read_bytes() == before["gitignore"]
    assert (project / "AGENTS.md").read_bytes() == before["agents"]
    assert (project / "CLAUDE.md").read_bytes() == before["claude"]


def test_cleanup_removes_suite_and_managed_blocks_but_preserves_human_content(tmp_path):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    project.mkdir()
    (project / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
    (project / "AGENTS.md").write_text("# Human agents rules\n", encoding="utf-8")
    (project / "CLAUDE.md").write_text("# Human Claude rules\n", encoding="utf-8")
    installer.install(project)
    (project / "docs" / "user-guide.md").write_text("user content\n", encoding="utf-8")
    preview = cleanup.preview_cleanup(project)
    result = cleanup.cleanup(project, approval_token=preview["approval_token"])
    assert result["status"] == "cleaned"
    assert not (project / "prompts").exists()
    assert not (project / ".prompt_suite").exists()
    for name in ["results", "reports", "logs", "artifacts", "outputs"]:
        assert not (project / name).exists()
    assert (project / "docs" / "user-guide.md").read_text(
        encoding="utf-8"
    ) == "user content\n"
    assert "preserved_nonempty_docs" in result["warnings"]
    assert (project / ".gitignore").read_text(encoding="utf-8") == "node_modules/\n"
    assert (project / "AGENTS.md").read_text(
        encoding="utf-8"
    ) == "# Human agents rules\n"
    assert (project / "CLAUDE.md").read_text(
        encoding="utf-8"
    ) == "# Human Claude rules\n"


def test_cleanup_preserves_preexisting_empty_generic_directories(tmp_path):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    project.mkdir()
    (project / "results").mkdir()
    installer.install(project)
    preview = cleanup.preview_cleanup(project)
    assert "results" not in preview["planned_removals"]
    result = cleanup.cleanup(project, approval_token=preview["approval_token"])
    assert (project / "results").is_dir()
    assert "results" in result["preserved_paths"]


def test_cleanup_deletes_agent_files_and_gitignore_when_suite_created_them(tmp_path):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    installer.install(project)
    preview = cleanup.preview_cleanup(project)
    cleanup.cleanup(project, approval_token=preview["approval_token"])
    assert not (project / "AGENTS.md").exists()
    assert not (project / "CLAUDE.md").exists()
    assert not (project / ".gitignore").exists()
    assert not (project / "docs").exists()


def test_cleanup_rejects_stale_approval_token_after_managed_file_changes(tmp_path):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    installer.install(project)
    preview = cleanup.preview_cleanup(project)
    with (project / "AGENTS.md").open("a", encoding="utf-8") as handle:
        handle.write("\nnew human rule\n")
    try:
        cleanup.cleanup(project, approval_token=preview["approval_token"])
        assert False, "expected stale approval rejection"
    except ValueError as exc:
        assert "state changed" in str(exc).lower()
    assert (project / "prompts").exists()


def test_cleanup_rolls_back_all_mutations_on_post_guidance_failure(
    tmp_path, monkeypatch
):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    project.mkdir()
    (project / ".gitignore").write_text("keep/\n", encoding="utf-8")
    (project / "AGENTS.md").write_text("human\n", encoding="utf-8")
    installer.install(project)
    preview = cleanup.preview_cleanup(project)
    original = cleanup._quarantine_paths

    def broken(*args, **kwargs):
        original(*args, **kwargs)
        raise RuntimeError("forced quarantine failure")

    monkeypatch.setattr(cleanup, "_quarantine_paths", broken)
    try:
        cleanup.cleanup(project, approval_token=preview["approval_token"])
        assert False
    except RuntimeError:
        pass
    assert (project / "prompts").is_dir()
    assert "BEGIN MISSION DIRECTIVES MANAGED IGNORE" in (
        project / ".gitignore"
    ).read_text(encoding="utf-8")
    assert "BEGIN MD MANAGED GUIDANCE" in (project / "AGENTS.md").read_text(
        encoding="utf-8"
    )


def test_cleanup_cli_requires_confirmation_when_noninteractive(tmp_path):
    installer = _load(ROOT / "tools/install.py", "md_install_cleanup_cli")
    project = tmp_path / "project"
    installer.install(project)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools/cleanup.py"), str(project), "--no-tui"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode != 0
    assert "confirm" in (proc.stderr + proc.stdout).lower()
    assert (project / "prompts").exists()


def test_cleanup_cli_yes_shows_progress_and_formatted_summary(tmp_path):
    installer = _load(ROOT / "tools/install.py", "md_install_cleanup_cli_yes")
    project = tmp_path / "project"
    installer.install(project)
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/cleanup.py"),
            str(project),
            "--yes",
            "--no-tui",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "PROGRESS " in proc.stderr
    assert "SUCCESS" in proc.stderr
    assert "cleanup completed" in proc.stderr.lower()
    payload = json.loads(proc.stdout)
    assert payload["status"] == "cleaned"
    assert not (project / "prompts").exists()


def test_installed_cleanup_script_can_remove_its_own_prompts_tree(tmp_path):
    installer = _load(ROOT / "tools/install.py", "md_install_cleanup_self")
    project = tmp_path / "project"
    installer.install(project)
    installed_cleanup = project / "prompts" / "cleanup.py"
    proc = subprocess.run(
        [sys.executable, str(installed_cleanup), str(project), "--yes", "--no-tui"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["status"] == "cleaned"
    assert not (project / "prompts").exists()


def test_cleanup_purge_failure_before_any_deletion_restores_everything(
    tmp_path, monkeypatch
):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    project.mkdir()
    (project / "AGENTS.md").write_text("human rules\n", encoding="utf-8")
    installer.install(project)
    preview = cleanup.preview_cleanup(project)

    def fail_without_mutation(_path):
        raise OSError("locked before deletion")

    monkeypatch.setattr(cleanup, "remove_tree", fail_without_mutation)
    try:
        cleanup.cleanup(project, approval_token=preview["approval_token"])
        assert False, "expected purge failure"
    except cleanup.PurgeIncompleteError as exc:
        assert exc.rollback_safe is True

    assert (project / "prompts").is_dir()
    assert (project / ".prompt_suite").is_dir()
    assert "BEGIN MD MANAGED GUIDANCE" in (project / "AGENTS.md").read_text(
        encoding="utf-8"
    )
    assert not any(project.glob(".md-cleanup-staging-*"))


def test_cleanup_purge_failure_never_restores_a_partial_quarantine(
    tmp_path, monkeypatch
):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    installer.install(project)
    preview = cleanup.preview_cleanup(project)
    original_remove_tree = cleanup.remove_tree
    calls = []

    def fail_during_purge(path):
        path = Path(path)
        calls.append(path)
        if path.name.startswith("000-"):
            original_remove_tree(path)
            return
        if path.name.startswith("001-"):
            raise OSError("forced mid-purge failure")
        original_remove_tree(path)

    monkeypatch.setattr(cleanup, "remove_tree", fail_during_purge)
    try:
        cleanup.cleanup(project, approval_token=preview["approval_token"])
        assert False, "expected purge failure"
    except cleanup.PurgeIncompleteError as exc:
        assert "forced mid-purge failure" in str(exc)
        assert Path(exc.quarantine_path).exists()
        assert exc.remaining_paths

    # Cleanup is already committed once purge begins. The implementation must
    # never restore only the surviving subset and create a mixed project state.
    assert not (project / "prompts").exists()
    assert not (project / ".prompt_suite").exists()
    assert any(path.name.startswith("000-") for path in calls)
    assert any(path.name.startswith("001-") for path in calls)


def test_cleanup_decline_has_distinct_exit_code(tmp_path, monkeypatch):
    installer, cleanup = _modules()
    project = tmp_path / "project"
    installer.install(project)
    monkeypatch.setattr(sys, "argv", ["cleanup.py", str(project), "--no-tui"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _prompt="": "NO")
    assert cleanup.main() == 3
    assert (project / "prompts").exists()


def test_cleanup_receipt_schema_accepts_result(tmp_path):
    from jsonschema import Draft202012Validator, FormatChecker

    installer, cleanup = _modules()
    project = tmp_path / "project"
    installer.install(project)
    preview = cleanup.preview_cleanup(project)
    result = cleanup.cleanup(project, approval_token=preview["approval_token"])
    schema = json.loads(
        (ROOT / "schemas" / "cleanup_receipt.schema.json").read_text(encoding="utf-8")
    )
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(result)
    )
    assert not errors, errors


def test_root_cleanup_has_bash_and_powershell_launchers():
    assert (ROOT / "tools/cleanup.sh").exists()
    assert (ROOT / "tools/cleanup.ps1").exists()
    assert "set -euo pipefail" in (ROOT / "tools/cleanup.sh").read_text(
        encoding="utf-8"
    )
    ps = (ROOT / "tools/cleanup.ps1").read_text(encoding="utf-8")
    assert "Write-Progress" in ps
    assert "Mission Directives {0}" in ps
    assert "$SuiteVersion:" not in ps
