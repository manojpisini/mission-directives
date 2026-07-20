#!/usr/bin/env python3
"""Install one locked or explicitly approved skill transactionally into all supported global locations."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from agent_paths import all_default_destinations
from security_utils import (
    atomic_write_json,
    ensure_no_symlink_components,
    github_tarball_sha256,
    remove_tree,
    safe_child,
    tree_digest,
    validate_distinct_roots,
    validate_github_repository,
    validate_identifier,
    validate_sha1,
    validate_sha256,
    validate_tree_limits,
)
from telemetry import append_event
from tui import TUI

ROOT = Path(__file__).resolve().parents[1]
SKILLS_CLI_PACKAGE = "skills@1.5.17"
SKILLS_CLI_TIMEOUT_SECONDS = 600


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _locked_source(lock_file: Path, skill_id: str, requested_source: str) -> str:
    ensure_no_symlink_components(lock_file)
    if not lock_file.is_file():
        raise ValueError(f"Lock file is not a regular file: {lock_file}")
    rows = json.loads(lock_file.read_text(encoding="utf-8"))["entries"]
    lock = next((row for row in rows if row.get("skill_id") == skill_id), None)
    if (
        not lock
        or lock.get("lock_status") != "resolved"
        or not lock.get("auto_install_allowed")
    ):
        raise ValueError("Lock is not resolved and approved for automatic installation")
    repository = validate_github_repository(lock.get("repository", ""))
    if validate_github_repository(requested_source) != repository:
        raise ValueError("Source does not match resolved lock repository")
    commit = validate_sha1(lock.get("commit_sha", ""))
    expected = validate_sha256(
        lock.get("tarball_sha256", ""), kind="locked tarball SHA-256"
    )
    actual = github_tarball_sha256(repository, commit)
    if actual != expected:
        raise ValueError("Locked GitHub tarball SHA-256 verification failed")
    return f"{repository}/tree/{commit}"


def _isolated_cli_environment(home: Path) -> dict[str, str]:
    """Build an npm/npx environment that cannot write to live user skill paths."""
    home.mkdir(parents=True, exist_ok=True)
    config = home / ".npmrc"
    config.write_text("", encoding="utf-8")
    cache = home / ".npm-cache"
    prefix = home / ".npm-prefix"
    xdg = home / ".config"
    for path in (cache, prefix, xdg):
        path.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "USERPROFILE": str(home),
            "XDG_CONFIG_HOME": str(xdg),
            "npm_config_cache": str(cache),
            "npm_config_prefix": str(prefix),
            "npm_config_userconfig": str(config),
            "npm_config_globalconfig": str(config),
            "npm_config_registry": "https://registry.npmjs.org/",
            "npm_config_ignore_scripts": "true",
            "npm_config_audit": "false",
            "npm_config_fund": "false",
            "npm_config_yes": "true",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return env


def _copy_stage(source: Path, destination: Path) -> Path:
    parent = destination.parent
    ensure_no_symlink_components(parent)
    parent.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink_components(parent)
    stage = safe_child(parent, f".{destination.name}.stage-{uuid.uuid4().hex}")
    shutil.copytree(source, stage, symlinks=True)
    validate_tree_limits(stage)
    return stage


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--skill-id", required=True)
    ap.add_argument(
        "--acquisition-mode",
        choices=["locked_auto", "approved_unpinned", "manual_only"],
        default="locked_auto",
    )
    ap.add_argument("--lock-file", default=str(ROOT / "config/skills.lock.json"))
    ap.add_argument("--reinstall", action="store_true")
    ap.add_argument("--receipt-path")
    a = ap.parse_args()

    skill_id = validate_identifier(a.skill_id, kind="skill")
    if a.acquisition_mode == "manual_only":
        raise SystemExit("manual_only mode does not permit installation")
    source = (
        _locked_source(Path(a.lock_file).expanduser(), skill_id, a.source)
        if a.acquisition_mode == "locked_auto"
        else validate_github_repository(a.source)
    )

    destination_roots = all_default_destinations()
    validate_distinct_roots(destination_roots.values())
    destinations = {
        name: safe_child(base, skill_id) for name, base in destination_roots.items()
    }
    for destination in destinations.values():
        ensure_no_symlink_components(destination)
        if destination.exists() and not a.reinstall:
            raise SystemExit(f"Destination exists: {destination}; use --reinstall")

    tui = TUI(f"Install skill {skill_id}", total=4)
    tui.start()
    started = dt.datetime.now(dt.timezone.utc)
    try:
        append_event(
            "skill",
            "install_multi_location",
            "started",
            tool="skill_dual.py",
            context={
                "skill_id": skill_id,
                "mode": a.acquisition_mode,
                "source_host": "github.com",
            },
        )
    except Exception:
        pass
    tui.step("source and authority verified")

    stages: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    promoted: list[Path] = []
    result: dict[str, object]
    try:
        with tempfile.TemporaryDirectory(prefix="md-skill-install-") as temp:
            temp_root = Path(temp)
            isolated_home = temp_root / "home"
            env = _isolated_cli_environment(isolated_home)
            cmd = [
                "npx",
                "--yes",
                SKILLS_CLI_PACKAGE,
                "add",
                source,
                "--skill",
                skill_id,
                "-g",
                "-a",
                "cline",
                "--copy",
                "-y",
            ]
            proc = subprocess.run(
                cmd,
                timeout=SKILLS_CLI_TIMEOUT_SECONDS,
                check=False,
                env=env,
                cwd=temp_root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if proc.returncode:
                raise RuntimeError(
                    f"Skills CLI failed with exit code {proc.returncode}"
                )
            staged_source = isolated_home / ".agents" / "skills" / skill_id
            ensure_no_symlink_components(staged_source)
            if not staged_source.is_dir():
                raise RuntimeError(
                    "Skills CLI did not produce the expected isolated skill directory"
                )
            validate_tree_limits(staged_source)
            skill_file = safe_child(staged_source, "SKILL.md")
            if not skill_file.is_file():
                raise RuntimeError("Isolated skill output is missing SKILL.md")
            source_digest = tree_digest(staged_source)
            tui.step("skill staged by pinned skills CLI")

            for destination in destinations.values():
                stage = _copy_stage(staged_source, destination)
                if tree_digest(stage) != source_digest:
                    raise RuntimeError(f"Staged skill tree hash differs: {stage}")
                stages[destination] = stage

        for destination in destinations.values():
            if destination.exists():
                backup = safe_child(
                    destination.parent, f".{skill_id}.backup-{uuid.uuid4().hex}"
                )
                destination.replace(backup)
                backups[destination] = backup
        for destination in destinations.values():
            stages[destination].replace(destination)
            promoted.append(destination)

        tree_hashes = [
            tree_digest(destination) for destination in destinations.values()
        ]
        if len(set(tree_hashes)) != 1:
            raise RuntimeError("Multi-location skill tree hashes differ")
        files = [
            safe_child(destination, "SKILL.md") for destination in destinations.values()
        ]
        hashes = [sha(path) for path in files]
        if len(set(hashes)) != 1:
            raise RuntimeError("Multi-location SKILL.md hashes differ")
        tui.step("multi-location hashes verified")

        result = {
            "skill_id": skill_id,
            "source": source,
            "requested_source": a.source,
            "acquisition_mode": a.acquisition_mode,
            "agents": str(destinations["agents"]),
            "claude_code": str(destinations["claude-code"]),
            "opencode": str(destinations["opencode"]),
            "skill_md_sha256": hashes[0],
            "skill_tree_sha256": tree_hashes[0],
            "skills_cli_package": SKILLS_CLI_PACKAGE,
            "verified": True,
            "quarantine_required": True,
            "installed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        if a.receipt_path:
            receipt = ensure_no_symlink_components(Path(a.receipt_path).expanduser())
            atomic_write_json(receipt, result)
    except Exception as exc:
        for destination in promoted:
            if destination.exists():
                remove_tree(destination)
        for destination, backup in backups.items():
            if backup.exists():
                backup.replace(destination)
        for stage in stages.values():
            if stage.exists():
                remove_tree(stage)
        try:
            append_event(
                "skill",
                "install_multi_location",
                "fail",
                duration_ms=int(
                    (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
                ),
                tool="skill_dual.py",
                context={"skill_id": skill_id},
                error=str(exc),
            )
        except Exception:
            pass
        tui.finish("FAIL")
        raise
    finally:
        for stage in stages.values():
            if stage.exists():
                remove_tree(stage)

    cleanup_warnings: list[str] = []
    for backup in backups.values():
        try:
            remove_tree(backup)
        except Exception as exc:
            cleanup_warnings.append(str(exc))
    if cleanup_warnings:
        result["cleanup_warnings"] = cleanup_warnings
    tui.step("receipt written")
    tui.finish("PASS")
    try:
        event = append_event(
            "skill",
            "install_multi_location",
            "pass",
            duration_ms=int(
                (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
            ),
            tool="skill_dual.py",
            context={"skill_id": skill_id, "hash": result["skill_md_sha256"]},
        )
        result["log_file"] = event["log_file"]
    except Exception as exc:
        result["telemetry_warning"] = str(exc)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
