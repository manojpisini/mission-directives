#!/usr/bin/env python3
"""Safely remove a Mission Directives project installation.

The cleanup workflow is the transactional inverse of install.py. It removes the
validated ./prompts installation, Mission Directives-owned runtime paths, the
managed .gitignore block, and managed guidance in AGENTS.md and CLAUDE.md while
preserving unrelated project content. A dry-run preview is bound to the exact
project state with a SHA-256 approval token. Failures before destructive purge
restore quarantined paths and original project files. If purge has already changed
quarantined data, cleanup remains committed and the residual quarantine is retained
for explicit recovery; the tool never restores a partial subset.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import stat
import sys
import uuid
from collections.abc import Callable
from pathlib import Path

from security_utils import (
    atomic_write_bytes,
    atomic_write_json,
    ensure_no_symlink_components,
    exclusive_lock,
    is_within,
    read_json_bounded,
    remove_tree,
    safe_child,
)
from sync_agent_guidance import _strip_managed_block
from tui import TUI

SOURCE = Path(__file__).resolve().parent.parent
GITIGNORE_BEGIN = "# BEGIN MISSION DIRECTIVES MANAGED IGNORE"
GITIGNORE_END = "# END MISSION DIRECTIVES MANAGED IGNORE"
MANAGED_MARKER = ".mission-directives-managed.json"
INTEGRATION_FILES = (".gitignore", "AGENTS.md", "CLAUDE.md")
RUNTIME_ROOTS = (
    ".prompt_suite",
    "results",
    "reports",
    "logs",
    "artifacts",
    "outputs",
    "docs",
)
STALE_PREFIXES = (".md-prompts-backup-", ".md-prompts-staging-")


class UserDeclined(Exception):
    """Raised when an interactive user explicitly declines cleanup."""


class PurgeIncompleteError(RuntimeError):
    """Raised when destructive quarantine purge cannot complete safely."""

    def __init__(
        self,
        quarantine_path: Path,
        *,
        purged_paths: list[str],
        remaining_paths: list[str],
        rollback_safe: bool,
        cause: BaseException,
    ) -> None:
        self.quarantine_path = quarantine_path.as_posix()
        self.purged_paths = list(purged_paths)
        self.remaining_paths = list(remaining_paths)
        self.rollback_safe = rollback_safe
        state = (
            "rollback remains safe"
            if rollback_safe
            else "cleanup is committed; partial restoration is forbidden"
        )
        super().__init__(
            f"Quarantine purge did not complete ({state}). "
            f"Residual quarantine: {self.quarantine_path}. Cause: {cause}"
        )


def _project_path(project: Path) -> Path:
    candidate = ensure_no_symlink_components(project.expanduser())
    if not candidate.exists() or not candidate.is_dir():
        raise ValueError(f"Project path is not an existing directory: {candidate}")
    if candidate == ensure_no_symlink_components(SOURCE):
        raise ValueError(
            "Project path must identify the installed project, not the distribution root"
        )
    return candidate


def _regular_file_snapshot(path: Path) -> tuple[bytes | None, int | None]:
    ensure_no_symlink_components(path)
    if not path.exists():
        return None, None
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected regular project file: {path}")
    return path.read_bytes(), stat.S_IMODE(path.stat().st_mode)


def _restore_file(path: Path, snapshot: tuple[bytes | None, int | None]) -> None:
    data, mode = snapshot
    ensure_no_symlink_components(path)
    if data is None:
        path.unlink(missing_ok=True)
        return
    atomic_write_bytes(path, data)
    if mode is not None:
        try:
            os.chmod(path, mode)
        except OSError:
            pass


def _hash_file_state(path: Path) -> dict[str, object]:
    ensure_no_symlink_components(path)
    if not path.exists():
        return {"exists": False}
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Expected regular file: {path}")
    data = path.read_bytes()
    return {
        "exists": True,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "mode": stat.S_IMODE(path.stat().st_mode),
    }


def _validate_installed_suite(prompts: Path) -> tuple[str, str]:
    prompts = ensure_no_symlink_components(prompts)
    if not prompts.exists() or not prompts.is_dir():
        raise ValueError(f"Mission Directives installation was not found at {prompts}")
    version_path = safe_child(prompts, "VERSION")
    release_path = safe_child(prompts, "RELEASE_ID")
    for path in (version_path, release_path):
        if not path.is_file():
            raise ValueError(
                f"Installed suite is missing required identity file: {path}"
            )
    version = version_path.read_text(encoding="utf-8").strip()
    release_id = release_path.read_text(encoding="utf-8").strip()
    if release_id != f"mission-directives-{version}":
        raise ValueError(
            "Installed prompts directory does not have a consistent Mission Directives identity"
        )
    return version, release_id


def _load_installation_receipt(project: Path) -> dict:
    path = safe_child(project, ".prompt_suite/installation-receipt.json")
    if not path.exists():
        return {}
    data = read_json_bounded(path, max_bytes=2 * 1024 * 1024)
    if not isinstance(data, dict) or data.get("suite_destination") != "prompts":
        raise ValueError(
            "Installation receipt is malformed or does not describe ./prompts"
        )
    return data


def _valid_marker(path: Path) -> bool:
    marker = path / MANAGED_MARKER
    if not marker.exists():
        return False
    try:
        data = read_json_bounded(marker, max_bytes=64 * 1024)
    except (OSError, ValueError, json.JSONDecodeError):
        return False
    return (
        isinstance(data, dict)
        and data.get("created_by") == "mission-directives"
        and data.get("path") == path.name
    )


def _directory_empty_or_marker_only(path: Path) -> bool:
    if not path.exists():
        return True
    ensure_no_symlink_components(path)
    if not path.is_dir():
        raise ValueError(f"Expected directory: {path}")
    entries = list(path.iterdir())
    return not entries or all(
        entry.name == MANAGED_MARKER and entry.is_file() for entry in entries
    )


def _remove_gitignore_block(existing: str) -> tuple[str, bool]:
    begin_count = existing.count(GITIGNORE_BEGIN)
    end_count = existing.count(GITIGNORE_END)
    if begin_count != end_count or begin_count > 1:
        raise ValueError("Malformed Mission Directives .gitignore managed block")
    if begin_count == 0:
        return existing, False
    start = existing.index(GITIGNORE_BEGIN)
    end = existing.index(GITIGNORE_END, start) + len(GITIGNORE_END)
    before = existing[:start].rstrip("\r\n")
    after = existing[end:].lstrip("\r\n")
    if before and after:
        return before + "\n" + after.rstrip("\r\n") + "\n", True
    remaining = before or after.rstrip("\r\n")
    return (remaining + "\n") if remaining else "", True


def _managed_file_updates(project: Path) -> tuple[dict[str, str | None], list[str]]:
    updates: dict[str, str | None] = {}
    changed: list[str] = []
    for name in INTEGRATION_FILES:
        path = safe_child(project, name)
        ensure_no_symlink_components(path)
        if not path.exists():
            updates[name] = None
            continue
        if not path.is_file():
            raise ValueError(f"Expected regular project file: {path}")
        text = path.read_text(encoding="utf-8")
        if name == ".gitignore":
            desired, had = _remove_gitignore_block(text)
        else:
            desired, had = _strip_managed_block(text)
            if had:
                desired = desired.rstrip("\r\n") + ("\n" if desired.strip() else "")
        updates[name] = desired
        if had:
            changed.append(name)
    return updates, changed


def _suite_like_tree(path: Path) -> bool:
    try:
        _validate_installed_suite(path)
        return True
    except (OSError, ValueError, UnicodeError):
        return False


def _build_plan(project: Path) -> dict:
    project = _project_path(project)
    prompts = safe_child(project, "prompts")
    version, release_id = _validate_installed_suite(prompts)
    receipt = _load_installation_receipt(project)
    created = set(receipt.get("created_directories") or [])
    ownership_recorded = "created_directories" in receipt
    planned_removals = ["prompts"]
    preserved_paths: list[str] = []
    warnings: list[str] = []

    prompt_suite = safe_child(project, ".prompt_suite")
    if prompt_suite.exists():
        planned_removals.append(".prompt_suite")

    for name in RUNTIME_ROOTS[1:]:
        path = safe_child(project, name)
        if not path.exists():
            continue
        owned = name in created or _valid_marker(path)
        if name == "docs" and owned and not _directory_empty_or_marker_only(path):
            owned = False
        if owned:
            planned_removals.append(name)
        else:
            preserved_paths.append(name)
            if name == "docs" and not _directory_empty_or_marker_only(path):
                warnings.append("preserved_nonempty_docs")
            elif not ownership_recorded:
                warnings.append(f"preserved_legacy_unverified_{name}")
            else:
                warnings.append(f"preserved_unowned_{name}")

    for child in sorted(project.iterdir(), key=lambda p: p.name):
        if not child.is_dir() or child.is_symlink():
            continue
        if any(child.name.startswith(prefix) for prefix in STALE_PREFIXES):
            if _suite_like_tree(child) or _directory_empty_or_marker_only(child):
                planned_removals.append(child.name)
            else:
                preserved_paths.append(child.name)
                warnings.append(f"preserved_unverified_{child.name}")

    updates, managed_blocks = _managed_file_updates(project)
    file_states = {
        name: _hash_file_state(safe_child(project, name)) for name in INTEGRATION_FILES
    }
    removal_states = {}
    for name in sorted(set(planned_removals)):
        path = safe_child(project, name)
        if path.exists():
            removal_states[name] = {
                "exists": True,
                "tree_state_sha256": _tree_state_digest(path),
                "bytes": _tree_size(path),
            }
        else:
            removal_states[name] = {"exists": False}
    plan = {
        "schema_version": "1.0",
        "project_root": project.as_posix(),
        "suite_version": version,
        "release_id": release_id,
        "prompts_tree_state_sha256": _tree_state_digest(prompts),
        "planned_removals": sorted(set(planned_removals)),
        "managed_blocks": managed_blocks,
        "preserved_paths": sorted(set(preserved_paths)),
        "warnings": sorted(set(warnings)),
        "managed_file_states": file_states,
        "managed_file_results": {
            name: (
                None
                if value is None
                else hashlib.sha256(value.encode("utf-8")).hexdigest()
            )
            for name, value in updates.items()
        },
        "removal_states": removal_states,
    }
    return plan


def _approval_token(plan: dict) -> str:
    encoded = json.dumps(
        plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(b"mission-directives-cleanup-v1\0" + encoded).hexdigest()


def preview_cleanup(
    project: Path, progress: Callable[[str], None] | None = None
) -> dict:
    project = _project_path(project)
    if progress:
        progress("validated project path")
    plan = _build_plan(project)
    if progress:
        progress("discovered managed installation artifacts")
    result = {
        "schema_version": "1.0",
        "status": "dry_run",
        "project_root": plan["project_root"],
        "suite_version": plan["suite_version"],
        "planned_removals": plan["planned_removals"],
        "managed_blocks": plan["managed_blocks"],
        "preserved_paths": plan["preserved_paths"],
        "warnings": plan["warnings"],
        "approval_token": _approval_token(plan),
        "completed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    if progress:
        progress("prepared cleanup preview and approval token")
    return result


def _write_managed_updates(
    project: Path, updates: dict[str, str | None]
) -> tuple[list[str], list[str]]:
    changed: list[str] = []
    deleted: list[str] = []
    for name, desired in updates.items():
        path = safe_child(project, name)
        if desired is None:
            continue
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if desired == existing:
            continue
        changed.append(name)
        if not desired:
            path.unlink(missing_ok=True)
            deleted.append(name)
        else:
            atomic_write_bytes(path, desired.encode("utf-8"))
    return changed, deleted


def _quarantine_paths(
    project: Path,
    removals: list[str],
    staging: Path,
    moved: list[tuple[Path, Path]] | None = None,
) -> list[tuple[Path, Path]]:
    staging.mkdir(parents=False, exist_ok=False)
    moved = moved if moved is not None else []
    for index, name in enumerate(removals):
        source = safe_child(project, name)
        if not source.exists():
            continue
        ensure_no_symlink_components(source)
        if source.is_symlink() or not source.is_dir():
            raise ValueError(
                f"Refusing to clean non-directory or symlink path: {source}"
            )
        destination = staging / f"{index:03d}-{source.name}"
        source.replace(destination)
        moved.append((source, destination))
    return moved


def _restore_quarantine(moved: list[tuple[Path, Path]]) -> None:
    for original, quarantined in reversed(moved):
        if quarantined.exists() and not original.exists():
            quarantined.replace(original)


def _tree_state_digest(root: Path) -> str:
    """Bind approval and rollback checks to directory and file metadata."""
    root = ensure_no_symlink_components(root)
    digest = hashlib.sha256()
    for directory, dirnames, filenames in os.walk(
        root, topdown=True, followlinks=False
    ):
        current = Path(directory)
        dirnames.sort()
        filenames.sort()
        for kind, names in ((b"D", dirnames), (b"F", filenames)):
            for name in names:
                candidate = current / name
                if candidate.is_symlink():
                    raise ValueError(f"Refusing symlink in managed tree: {candidate}")
                if kind == b"D" and not candidate.is_dir():
                    raise ValueError(
                        f"Refusing non-directory entry in managed tree: {candidate}"
                    )
                if kind == b"F" and not candidate.is_file():
                    raise ValueError(
                        f"Refusing non-regular file in managed tree: {candidate}"
                    )
                st = candidate.stat()
                rel = candidate.relative_to(root).as_posix().encode("utf-8")
                digest.update(kind)
                digest.update(len(rel).to_bytes(8, "big"))
                digest.update(rel)
                digest.update(st.st_size.to_bytes(8, "big"))
                digest.update(st.st_mtime_ns.to_bytes(8, "big", signed=False))
                digest.update(stat.S_IMODE(st.st_mode).to_bytes(4, "big"))
    return digest.hexdigest()


def _purge_quarantine(
    project: Path, moved: list[tuple[Path, Path]], staging: Path
) -> list[str]:
    """Purge quarantined trees one at a time without unsafe partial rollback."""
    before = {quarantined: _tree_state_digest(quarantined) for _, quarantined in moved}
    purged: list[str] = []
    for original, quarantined in moved:
        try:
            remove_tree(quarantined)
        except Exception as exc:
            destructive_change = bool(purged)
            if quarantined.exists():
                try:
                    destructive_change = (
                        destructive_change
                        or _tree_state_digest(quarantined) != before[quarantined]
                    )
                except Exception:
                    destructive_change = True
            else:
                destructive_change = True
                purged.append(original.relative_to(project).as_posix())
            remaining = [
                source.relative_to(project).as_posix()
                for source, candidate in moved
                if candidate.exists()
            ]
            raise PurgeIncompleteError(
                staging,
                purged_paths=purged,
                remaining_paths=remaining,
                rollback_safe=not destructive_change,
                cause=exc,
            ) from exc
        if quarantined.exists():
            remaining = [
                source.relative_to(project).as_posix()
                for source, candidate in moved
                if candidate.exists()
            ]
            raise PurgeIncompleteError(
                staging,
                purged_paths=purged,
                remaining_paths=remaining,
                rollback_safe=False,
                cause=OSError(f"Purge returned without removing {quarantined}"),
            )
        purged.append(original.relative_to(project).as_posix())

    residual_entries = sorted(item.name for item in staging.iterdir())
    if residual_entries:
        raise PurgeIncompleteError(
            staging,
            purged_paths=purged,
            remaining_paths=residual_entries,
            rollback_safe=False,
            cause=OSError("Untracked entries appeared in the cleanup quarantine"),
        )
    try:
        staging.rmdir()
    except Exception as exc:
        raise PurgeIncompleteError(
            staging,
            purged_paths=purged,
            remaining_paths=[],
            rollback_safe=False,
            cause=exc,
        ) from exc
    return purged


def _tree_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for root, dirs, files in os.walk(path, followlinks=False):
        for name in files:
            candidate = Path(root) / name
            if candidate.is_file() and not candidate.is_symlink():
                total += candidate.stat().st_size
    return total


def cleanup(
    project: Path,
    *,
    approval_token: str,
    receipt_path: Path | None = None,
    progress: Callable[[str], None] | None = None,
) -> dict:
    project = _project_path(project)
    lock = safe_child(project, ".md-cleanup.lock")
    staging = safe_child(
        project, f".md-cleanup-staging-{os.getpid()}-{uuid.uuid4().hex}"
    )
    snapshots: dict[str, tuple[bytes | None, int | None]] = {}
    moved: list[tuple[Path, Path]] = []
    docs_marker_snapshot: tuple[bytes | None, int | None] | None = None
    docs_marker = safe_child(project, f"docs/{MANAGED_MARKER}")
    started = dt.datetime.now(dt.timezone.utc)
    preserve_quarantine = False
    try:
        with exclusive_lock(lock):
            if progress:
                progress("acquired exclusive cleanup lock")
            plan = _build_plan(project)
            expected = _approval_token(plan)
            if not hmac.compare_digest(expected, approval_token):
                raise ValueError(
                    "Project state changed since approval; generate a new cleanup preview and retry"
                )
            if progress:
                progress("verified approval against current project state")
            snapshots = {
                name: _regular_file_snapshot(safe_child(project, name))
                for name in INTEGRATION_FILES
            }
            updates, _ = _managed_file_updates(project)
            changed_files, deleted_files = _write_managed_updates(project, updates)
            if progress:
                progress(
                    "removed managed AGENTS.md, CLAUDE.md, and .gitignore sections"
                )

            if docs_marker.exists() and "docs" not in plan["planned_removals"]:
                docs_marker_snapshot = _regular_file_snapshot(docs_marker)
                docs_marker.unlink()
            reclaimable = sum(
                _tree_size(safe_child(project, name))
                for name in plan["planned_removals"]
                if safe_child(project, name).exists()
            )
            _quarantine_paths(project, plan["planned_removals"], staging, moved)
            if progress:
                progress("quarantined managed suite and runtime paths")

            result = {
                "schema_version": "1.0",
                "status": "cleaned",
                "project_root": project.as_posix(),
                "suite_version": plan["suite_version"],
                "removed_paths": [
                    path.relative_to(project).as_posix() for path, _ in moved
                ],
                "removed_managed_blocks": changed_files,
                "deleted_empty_files": deleted_files,
                "preserved_paths": plan["preserved_paths"],
                "warnings": plan["warnings"],
                "bytes_reclaimed": reclaimable,
            }
            receipt: Path | None = None
            if receipt_path is not None:
                receipt = ensure_no_symlink_components(receipt_path.expanduser())
                if is_within(receipt, project):
                    for name in plan["planned_removals"]:
                        target = safe_child(project, name)
                        if receipt == target or is_within(receipt, target):
                            raise ValueError(
                                "Cleanup receipt must not be written inside a removed path"
                            )
            if progress:
                progress("verified cleanup result and summary")

            try:
                _purge_quarantine(project, moved, staging)
            except PurgeIncompleteError as purge_error:
                if not purge_error.rollback_safe:
                    # Destructive purge has crossed the commit boundary. Restoring
                    # only surviving quarantine entries would create a mixed tree.
                    preserve_quarantine = True
                    moved.clear()
                    snapshots.clear()
                    docs_marker_snapshot = None
                raise
            moved.clear()
            result["duration_ms"] = max(
                0,
                int(
                    (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
                ),
            )
            result["completed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
            if receipt is not None:
                try:
                    atomic_write_json(receipt, result)
                    result["receipt_path"] = receipt.as_posix()
                except Exception as receipt_error:
                    result["warnings"] = sorted(
                        set(
                            result["warnings"]
                            + [f"receipt_write_failed:{receipt_error}"]
                        )
                    )
            if progress:
                progress("purged quarantined Mission Directives data")
            return result
    except Exception:
        _restore_quarantine(moved)
        for name, snapshot in snapshots.items():
            _restore_file(safe_child(project, name), snapshot)
        if docs_marker_snapshot is not None:
            _restore_file(docs_marker, docs_marker_snapshot)
        if staging.exists() and not preserve_quarantine:
            try:
                # A safe rollback must have moved every quarantined tree back.
                # Remove only the now-empty container; never recursively delete
                # unexpected residue while handling another failure.
                if not any(staging.iterdir()):
                    staging.rmdir()
            except OSError:
                pass
        raise
    finally:
        try:
            lock.unlink(missing_ok=True)
        except OSError:
            pass


def _confirm(preview: dict) -> bool:
    print("\nMission Directives cleanup preview", file=sys.stderr)
    for path in preview["planned_removals"]:
        print(f"  REMOVE: {path}", file=sys.stderr)
    for path in preview["preserved_paths"]:
        print(f"  PRESERVE: {path}", file=sys.stderr)
    answer = input("Type REMOVE to confirm cleanup: ").strip()
    return answer == "REMOVE"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", nargs="?")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm the current preview noninteractively",
    )
    parser.add_argument("--approval-token", help="Approval token returned by --dry-run")
    parser.add_argument(
        "--receipt",
        type=Path,
        help="Optional cleanup receipt path outside removed paths",
    )
    parser.add_argument("--no-tui", action="store_true")
    args = parser.parse_args()

    tui = TUI(
        "Mission Directives cleanup", total=10, enabled=False if args.no_tui else None
    )
    tui.start()
    raw = args.project_path
    try:
        if not raw:
            if not sys.stdin.isatty():
                raise ValueError("Project path is required in noninteractive mode")
            raw = input("Project folder path: ").strip()
        preview = preview_cleanup(Path(raw), progress=tui.step)
        if args.dry_run:
            tui.finish("SUCCESS")
            tui.summary(
                "SUCCESS",
                "Cleanup preview completed; no project files were changed",
                [
                    ("Project", preview["project_root"]),
                    ("Planned removals", len(preview["planned_removals"])),
                    ("Approval token", preview["approval_token"]),
                    ("Elapsed", f"{tui.elapsed_ms} ms"),
                ],
            )
            print(json.dumps(preview, indent=2))
            return 0

        token = args.approval_token or preview["approval_token"]
        if not args.yes and not args.approval_token:
            if not sys.stdin.isatty():
                raise ValueError(
                    "Explicit confirmation is required; rerun with --yes or a dry-run approval token"
                )
            if not _confirm(preview):
                raise UserDeclined
        result = cleanup(
            Path(raw),
            approval_token=token,
            receipt_path=args.receipt,
            progress=tui.step,
        )
    except UserDeclined:
        tui.finish("DECLINED")
        tui.summary(
            "DECLINED", "Mission Directives cleanup was declined", [("Project", raw)]
        )
        print(
            json.dumps({"status": "declined", "project_root": raw}, indent=2),
            file=sys.stderr,
        )
        return 3
    except KeyboardInterrupt:
        tui.finish("CANCELLED")
        tui.summary(
            "CANCELLED",
            "Mission Directives cleanup was interrupted",
            [("Project", raw)],
        )
        print(
            json.dumps({"status": "cancelled", "project_root": raw}, indent=2),
            file=sys.stderr,
        )
        return 130
    except PurgeIncompleteError as exc:
        tui.finish("INCOMPLETE")
        tui.summary(
            "INCOMPLETE",
            "Cleanup committed, but quarantine purge did not finish",
            [
                ("Project", raw),
                ("Residual quarantine", exc.quarantine_path),
                ("Purged paths", len(exc.purged_paths)),
                ("Remaining paths", len(exc.remaining_paths)),
                (
                    "Recovery",
                    "Release file locks, then remove only the reported quarantine directory",
                ),
            ],
        )
        print(
            json.dumps(
                {
                    "status": "purge_incomplete",
                    "project_root": raw,
                    "quarantine_path": exc.quarantine_path,
                    "purged_paths": exc.purged_paths,
                    "remaining_paths": exc.remaining_paths,
                    "error": str(exc),
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 4
    except Exception as exc:
        tui.finish("FAIL")
        tui.summary(
            "FAILURE",
            "Mission Directives cleanup did not complete",
            [
                ("Project", raw),
                ("Reason", str(exc)),
                ("Recovery", "Project state restored when mutation had begun"),
            ],
        )
        print(
            json.dumps({"status": "fail", "error": str(exc)}, indent=2), file=sys.stderr
        )
        return 1

    tui.finish("SUCCESS")
    tui.summary(
        "SUCCESS",
        "Mission Directives cleanup completed successfully",
        [
            ("Project", result["project_root"]),
            ("Removed paths", len(result["removed_paths"])),
            ("Managed files cleaned", len(result["removed_managed_blocks"])),
            ("Bytes reclaimed", result["bytes_reclaimed"]),
            ("Warnings", ", ".join(result["warnings"]) or "none"),
            ("Elapsed", f"{tui.elapsed_ms} ms"),
        ],
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
