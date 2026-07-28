"""Transactional project installation and migration."""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

from .__about__ import __version__

PROJECT_DIR = ".mission-directives"
OUTPUT_DIRS = ("results", "reports", "artifacts", "plans", "outputs", "docs", "logs")
TRACKING_MODES = ("ignored", "outputs", "all")
IGNORE_BEGIN = "# BEGIN MISSION DIRECTIVES MANAGED IGNORE"
IGNORE_END = "# END MISSION DIRECTIVES MANAGED IGNORE"
GUIDANCE_FILES = ("AGENTS.md", "CLAUDE.md")
PRESERVED_FILES = (".gitignore", *GUIDANCE_FILES)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def runtime_source() -> Path:
    packaged = Path(__file__).resolve().parent / "_runtime"
    return packaged if packaged.is_dir() else repository_root()


def site_source() -> Path:
    return Path(__file__).resolve().parent / "site"


def find_project_root(start: Path | str = ".") -> Path:
    current = Path(start).expanduser().resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / PROJECT_DIR / "config.json").is_file():
            return candidate
    raise FileNotFoundError(
        "No .mission-directives project was found; run 'mission-directives init'."
    )


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(raw)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_text(path: Path, text: str) -> None:
    _atomic_write(path, text.encode("utf-8"))


def atomic_write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def _filesystem_path(path: Path) -> str | Path:
    if os.name != "nt":
        return path
    absolute = os.path.abspath(str(path))
    if absolute.startswith("\\\\?\\"):
        return absolute
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def _remove_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(_filesystem_path(path))


def _assert_safe_project(project: Path) -> Path:
    project = project.expanduser().resolve()
    project.mkdir(parents=True, exist_ok=True)
    if not project.is_dir():
        raise ValueError(f"Project path is not a directory: {project}")
    source = repository_root().resolve()
    if project == source or source in project.parents or project in source.parents:
        raise ValueError("Project path inside the suite source is not allowed")
    for parent in (project, *project.parents):
        if parent.is_symlink():
            raise ValueError(f"Project path contains a symbolic link: {parent}")
    return project


def _copy_tree(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise FileNotFoundError(f"Required directory is missing: {source}")
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symbolic links are not allowed in runtime payloads: {path}")
    shutil.copytree(_filesystem_path(source), _filesystem_path(destination))


def _copy_runtime_payload(destination: Path) -> None:
    source = runtime_source()
    if source.name == "_runtime":
        _copy_tree(source, destination)
        return
    contract = json.loads(
        (source / "config/runtime_payload.json").read_text(encoding="utf-8")
    )
    destination.mkdir()
    for relative in contract["root_files"]:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_filesystem_path(source / relative), _filesystem_path(target))
    for relative in contract["directories"]:
        _copy_tree(source / relative, destination / relative)
    for name in contract["tool_files"]:
        target = destination / "tools" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            _filesystem_path(source / "tools" / name), _filesystem_path(target)
        )


def _snapshot_files(project: Path) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for name in PRESERVED_FILES:
        path = project / name
        if path.exists() and not path.is_file():
            raise ValueError(f"Expected a regular project file: {path}")
        snapshot[name] = path.read_bytes() if path.exists() else None
    return snapshot


def _restore_files(project: Path, snapshot: dict[str, bytes | None]) -> None:
    for name, value in snapshot.items():
        path = project / name
        if value is None:
            path.unlink(missing_ok=True)
        else:
            _atomic_write(path, value)


def _ignore_lines(mode: str) -> list[str]:
    if mode not in TRACKING_MODES:
        raise ValueError(f"Tracking mode must be one of: {', '.join(TRACKING_MODES)}")
    transient = [
        "/.mission-directives/state/",
        "/.mission-directives-*-staging-*/",
        "/.mission-directives-*-backup-*/",
    ]
    if mode == "ignored":
        return ["/.mission-directives/", *transient[1:]]
    if mode == "all":
        return transient
    lines = ["/.mission-directives/*", "!/.mission-directives/project.json"]
    for name in OUTPUT_DIRS:
        lines.extend(
            [f"!/.mission-directives/{name}/", f"!/.mission-directives/{name}/**"]
        )
    return [*lines, *transient]


def managed_ignore(existing: str, mode: str) -> str:
    block = "\n".join([IGNORE_BEGIN, *_ignore_lines(mode), IGNORE_END])
    begin_count = existing.count(IGNORE_BEGIN)
    end_count = existing.count(IGNORE_END)
    if begin_count != end_count or begin_count > 1:
        raise ValueError("Malformed Mission Directives .gitignore markers")
    if begin_count:
        start = existing.index(IGNORE_BEGIN)
        end = existing.index(IGNORE_END, start) + len(IGNORE_END)
        before = existing[:start].rstrip()
        after = existing[end:].lstrip("\r\n")
        parts = [part for part in (before, block, after.rstrip()) if part]
        return "\n\n".join(parts) + "\n"
    prefix = existing.rstrip()
    return (prefix + "\n\n" if prefix else "") + block + "\n"


def remove_managed_ignore(existing: str) -> str:
    if IGNORE_BEGIN not in existing and IGNORE_END not in existing:
        return existing
    if existing.count(IGNORE_BEGIN) != 1 or existing.count(IGNORE_END) != 1:
        raise ValueError("Malformed Mission Directives .gitignore markers")
    start = existing.index(IGNORE_BEGIN)
    end = existing.index(IGNORE_END, start) + len(IGNORE_END)
    before = existing[:start].rstrip()
    after = existing[end:].lstrip("\r\n").rstrip()
    return "\n\n".join(part for part in (before, after) if part) + ("\n" if before or after else "")


def _load_tool(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load runtime tool: {path}")
    module = importlib.util.module_from_spec(spec)
    tools_dir = str(path.parent)
    sys.path.insert(0, tools_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        if sys.path[0] == tools_dir:
            sys.path.pop(0)
    return module


def _sync_guidance(project: Path, runtime: Path, remove: bool = False) -> dict:
    module = _load_tool(runtime / "tools/sync_agent_guidance.py", "md_sync_guidance")
    receipt = project / PROJECT_DIR / "state/agent-guidance-receipt.json"
    return module.sync_guidance(
        project_root=project,
        suite_root=runtime,
        receipt_path=None if remove else receipt,
        remove=remove,
    )


def _system_config(tracking: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "created_by": "mission-directives",
        "suite_version": __version__,
        "tracking_mode": tracking,
        "viewer": {"auto_open": True, "port": 0},
        "installed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }


def _seed_project_config(project: Path) -> dict[str, Any]:
    from .project_config import seed_project_config

    return seed_project_config(project)


def _prepare_stage(project: Path, stage: Path, tracking: str, preserve: Path | None) -> None:
    stage.mkdir()
    _copy_runtime_payload(stage / "runtime")
    _copy_tree(site_source(), stage / "site")
    for name in OUTPUT_DIRS:
        destination = stage / name
        source = preserve / name if preserve else None
        if source and source.is_dir():
            _copy_tree(source, destination)
        else:
            destination.mkdir()
    state_source = preserve / "state" if preserve else None
    if state_source and state_source.is_dir():
        _copy_tree(state_source, stage / "state")
    else:
        (stage / "state").mkdir()

    project_config_source = preserve / "project.json" if preserve else None
    if project_config_source and project_config_source.is_file():
        shutil.copy2(
            _filesystem_path(project_config_source),
            _filesystem_path(stage / "project.json"),
        )
    else:
        atomic_write_json(stage / "project.json", _seed_project_config(project))

    old_system = preserve / "config.json" if preserve else None
    config = _system_config(tracking)
    if old_system and old_system.is_file():
        prior = json.loads(old_system.read_text(encoding="utf-8"))
        config["installed_at"] = prior.get("installed_at", config["installed_at"])
        config["viewer"] = prior.get("viewer", config["viewer"])
    atomic_write_json(stage / "config.json", config)


def install_project(
    project: Path | str,
    *,
    tracking: str = "ignored",
    replace: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    project = _assert_safe_project(Path(project))
    destination = project / PROJECT_DIR
    if destination.exists() and not destination.is_dir():
        raise ValueError(f"Installation destination is not a directory: {destination}")
    if destination.exists() and not replace:
        raise FileExistsError(f"{destination} exists; use 'mission-directives upgrade'")
    actions = [
        f"stage runtime at {PROJECT_DIR}/runtime",
        f"stage local viewer at {PROJECT_DIR}/site",
        "create project config and seven output categories",
        f"set tracking mode to {tracking}",
        "synchronize AGENTS.md and CLAUDE.md",
    ]
    if dry_run:
        return {
            "status": "dry_run",
            "project_root": str(project),
            "suite_destination": f"{PROJECT_DIR}/runtime",
            "tracking_mode": tracking,
            "actions": actions,
        }

    snapshot = _snapshot_files(project)
    token = f"{os.getpid()}-{uuid.uuid4().hex[:8]}"
    stage = project / f".mission-directives-install-staging-{token}"
    backup = project / f".mission-directives-install-backup-{token}"
    if stage.exists() or backup.exists():
        raise FileExistsError("Installation staging path already exists")
    _prepare_stage(project, stage, tracking, destination if destination.exists() else None)
    promoted = False
    try:
        if destination.exists():
            destination.replace(backup)
        stage.replace(destination)
        promoted = True
        gitignore = project / ".gitignore"
        current_ignore = snapshot[".gitignore"]
        atomic_write_text(
            gitignore,
            managed_ignore(
                current_ignore.decode("utf-8") if current_ignore is not None else "",
                tracking,
            ),
        )
        guidance = _sync_guidance(project, destination / "runtime")
        receipt = {
            "schema_version": "2.0",
            "status": "installed",
            "created_by": "mission-directives",
            "project_root": str(project),
            "suite_destination": f"{PROJECT_DIR}/runtime",
            "suite_version": __version__,
            "tracking_mode": tracking,
            "output_root": PROJECT_DIR,
            "output_directories": list(OUTPUT_DIRS),
            "guidance": guidance,
            "installed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        receipt_path = destination / "state/installation-receipt.json"
        atomic_write_json(receipt_path, receipt)
        receipt["receipt_path"] = str(receipt_path)
        if backup.exists():
            _remove_tree(backup)
        return receipt
    except Exception:
        if promoted and destination.exists():
            _remove_tree(destination)
        if backup.exists():
            backup.replace(destination)
        _restore_files(project, snapshot)
        raise
    finally:
        if stage.exists():
            _remove_tree(stage)


def update_tracking(project: Path | str, mode: str) -> dict[str, Any]:
    root = find_project_root(project)
    config_path = root / PROJECT_DIR / "config.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    gitignore = root / ".gitignore"
    old = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    atomic_write_text(gitignore, managed_ignore(old, mode))
    config["tracking_mode"] = mode
    atomic_write_json(config_path, config)
    return {"status": "updated", "tracking_mode": mode}


def migration_preview(project: Path | str) -> dict[str, Any]:
    project = Path(project).expanduser().resolve()
    receipt = project / ".prompt_suite/installation-receipt.json"
    managed = receipt.is_file()
    paths: list[str] = []
    if managed:
        for name in ("prompts", ".prompt_suite", *OUTPUT_DIRS):
            path = project / name
            if not path.exists():
                continue
            if name in {"prompts", ".prompt_suite"} or (
                path / ".mission-directives-managed.json"
            ).is_file():
                paths.append(name)
    return {
        "status": "dry_run",
        "project_root": str(project),
        "legacy_installation": managed,
        "managed_paths": paths,
        "preserved_unmarked_paths": [
            name
            for name in OUTPUT_DIRS
            if (project / name).exists()
            and name not in paths
        ],
    }


def migrate_project(
    project: Path | str, *, apply: bool = False, tracking: str = "ignored"
) -> dict[str, Any]:
    preview = migration_preview(project)
    if not apply:
        return preview
    if not preview["legacy_installation"]:
        raise ValueError("No managed legacy installation was found")
    project = Path(project).expanduser().resolve()
    result = install_project(project, tracking=tracking, replace=False)
    destination = project / PROJECT_DIR
    for name in OUTPUT_DIRS:
        legacy = project / name
        if name not in preview["managed_paths"] or not legacy.is_dir():
            continue
        target = destination / name
        for item in legacy.iterdir():
            if item.name == ".mission-directives-managed.json":
                continue
            output = target / item.name
            if output.exists():
                raise FileExistsError(f"Migration collision: {output}")
            shutil.move(str(item), str(output))
        _remove_tree(legacy)
    for name in ("prompts", ".prompt_suite"):
        if name in preview["managed_paths"]:
            path = project / name
            if path.exists():
                _remove_tree(path)
    result["status"] = "migrated"
    result["migrated_paths"] = preview["managed_paths"]
    return result


def uninstall_project(project: Path | str, *, apply: bool = False) -> dict[str, Any]:
    root = find_project_root(project)
    destination = root / PROJECT_DIR
    config = json.loads((destination / "config.json").read_text(encoding="utf-8"))
    if config.get("created_by") != "mission-directives":
        raise ValueError("Refusing to remove an unmanaged .mission-directives directory")
    result = {
        "status": "dry_run" if not apply else "removed",
        "project_root": str(root),
        "remove": [PROJECT_DIR, *GUIDANCE_FILES, "managed .gitignore block"],
    }
    if not apply:
        return result
    snapshot = _snapshot_files(root)
    backup = root / f".mission-directives-uninstall-backup-{uuid.uuid4().hex[:8]}"
    destination.replace(backup)
    try:
        _sync_guidance(root, backup / "runtime", remove=True)
        gitignore = root / ".gitignore"
        old = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
        atomic_write_text(gitignore, remove_managed_ignore(old))
        _remove_tree(backup)
        return result
    except Exception:
        if destination.exists():
            _remove_tree(destination)
        backup.replace(destination)
        _restore_files(root, snapshot)
        raise


def router_environment(project: Path) -> dict[str, str]:
    root = find_project_root(project)
    md_root = root / PROJECT_DIR
    environment = os.environ.copy()
    environment.update(
        {
            "MD_PROJECT_ROOT": str(root),
            "MD_ARTIFACT_ROOT": str(md_root),
            "MD_LOG_DIR": str(md_root / "logs"),
        }
    )
    return environment
