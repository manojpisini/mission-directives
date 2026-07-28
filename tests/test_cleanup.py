from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mission_directives.installer import (
    IGNORE_BEGIN,
    install_project,
    remove_managed_ignore,
    uninstall_project,
)


def test_uninstall_requires_managed_installation(tmp_path):
    (tmp_path / ".mission-directives").mkdir()
    (tmp_path / ".mission-directives/config.json").write_text("{}")
    with pytest.raises(ValueError, match="unmanaged"):
        uninstall_project(tmp_path, apply=True)


def test_uninstall_removes_only_managed_blocks_and_project_runtime(tmp_path):
    (tmp_path / "AGENTS.md").write_text("human rules\n")
    (tmp_path / ".gitignore").write_text("human-ignore/\n")
    install_project(tmp_path)
    assert IGNORE_BEGIN in (tmp_path / ".gitignore").read_text()
    uninstall_project(tmp_path, apply=True)
    assert not (tmp_path / ".mission-directives").exists()
    assert (tmp_path / "AGENTS.md").read_text() == "human rules\n"
    assert (tmp_path / ".gitignore").read_text() == "human-ignore/\n"


def test_remove_managed_ignore_rejects_malformed_markers():
    with pytest.raises(ValueError, match="Malformed"):
        remove_managed_ignore(f"{IGNORE_BEGIN}\nunterminated\n")


def test_uninstall_dry_run_changes_nothing(tmp_path):
    install_project(tmp_path)
    before = (tmp_path / ".mission-directives/config.json").read_bytes()
    result = uninstall_project(tmp_path, apply=False)
    assert result["status"] == "dry_run"
    assert (tmp_path / ".mission-directives/config.json").read_bytes() == before
