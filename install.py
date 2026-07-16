#!/usr/bin/env python3
"""Install or update Mission Directives inside another project.

The complete distribution is staged and promoted to <project>/prompts. The
installer manages one .gitignore block, creates internal runtime directories,
and synchronizes only AGENTS.md and CLAUDE.md. Any failure after promotion
restores the previous suite and the original human-authored project files.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import uuid
from pathlib import Path
from collections.abc import Callable

TOOLS_DIR = Path(__file__).absolute().parent / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from security_utils import (
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_text,
    ensure_no_symlink_components,
    is_within,
    iter_tree_files,
    safe_child,
)
from tui import TUI

SOURCE = Path(__file__).absolute().parent
BEGIN = '# BEGIN MISSION DIRECTIVES MANAGED IGNORE'
END = '# END MISSION DIRECTIVES MANAGED IGNORE'
IGNORE_ENTRIES = [
    '/prompts/', '/.prompt_suite/', '/results/', '/reports/', '/logs/', '/artifacts/', '/outputs/',
    '/.md-prompts-staging-*/', '/.md-prompts-backup-*/', '/.md-cleanup-staging-*/', '/.md-cleanup.lock',
]
EXCLUDED_NAMES = {'__pycache__', '.pytest_cache', '.git'}
RUNTIME_DIRS = ['.prompt_suite/logs', 'results', 'reports', 'logs', 'artifacts', 'outputs', 'docs']
RUNTIME_ROOTS = ['.prompt_suite', 'results', 'reports', 'logs', 'artifacts', 'outputs', 'docs']
MANAGED_MARKER = '.mission-directives-managed.json'
PRESERVED_FILES = ['.gitignore', 'AGENTS.md', 'CLAUDE.md']


def copy_filter(directory: str, names: list[str]) -> list[str]:
    ignored: list[str] = []
    current = Path(directory)
    for name in names:
        candidate = current / name
        if name in EXCLUDED_NAMES or name.endswith(('.pyc', '.pyo', '.toml.lock')):
            ignored.append(name)
            continue
        try:
            relative = candidate.absolute().relative_to(SOURCE)
        except ValueError as exc:
            raise ValueError(f'Copy candidate escaped suite source: {candidate}') from exc
        if relative.parts[:2] == ('.prompt_suite', 'logs') and name != 'README.md':
            ignored.append(name)
    return ignored


def managed_ignore(existing: str) -> str:
    block = BEGIN + '\n' + '\n'.join(IGNORE_ENTRIES) + '\n# docs/ remains tracked and is intentionally not ignored.\n' + END
    if BEGIN in existing or END in existing:
        if existing.count(BEGIN) != 1 or existing.count(END) != 1 or existing.index(BEGIN) > existing.index(END):
            raise ValueError('Malformed Mission Directives .gitignore markers')
        before = existing[:existing.index(BEGIN)].rstrip()
        after = existing[existing.index(END) + len(END):].lstrip('\n')
        return (before + '\n\n' if before else '') + block + '\n' + (('\n' + after) if after else '')
    return existing.rstrip() + ('\n\n' if existing.strip() else '') + block + '\n'


def _project_path(project: Path) -> Path:
    """Validate a lexical project root without following attacker-controlled links."""
    candidate = ensure_no_symlink_components(project.expanduser())
    source = ensure_no_symlink_components(SOURCE)
    if is_within(candidate, source):
        raise ValueError('Project path must not be inside the suite source tree')
    if is_within(source, candidate):
        raise ValueError('Project path must not contain the suite source tree')
    candidate.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink_components(candidate)
    if not candidate.is_dir():
        raise ValueError(f'Project path is not a directory: {candidate}')
    return candidate


def _validated_paths(project: Path) -> tuple[Path, Path]:
    destination = safe_child(project, 'prompts')
    staging = safe_child(project, f'.md-prompts-staging-{os.getpid()}-{uuid.uuid4().hex}')
    for name in PRESERVED_FILES:
        ensure_no_symlink_components(safe_child(project, name))
    for name in RUNTIME_DIRS:
        ensure_no_symlink_components(safe_child(project, name))
    return destination, staging


def _snapshot(project: Path) -> dict[str, tuple[bytes | None, int | None]]:
    snapshot: dict[str, tuple[bytes | None, int | None]] = {}
    for name in PRESERVED_FILES:
        path = safe_child(project, name)
        ensure_no_symlink_components(path)
        if path.exists() and not path.is_file():
            raise ValueError(f'Expected regular project file: {path}')
        snapshot[name] = (path.read_bytes(), path.stat().st_mode & 0o7777) if path.exists() else (None, None)
    return snapshot


def _restore_snapshot(project: Path, snapshot: dict[str, tuple[bytes | None, int | None]]) -> None:
    for name, (data, mode) in snapshot.items():
        path = safe_child(project, name)
        ensure_no_symlink_components(path)
        if data is None:
            path.unlink(missing_ok=True)
        else:
            atomic_write_bytes(path, data)
            if mode is not None:
                try:
                    os.chmod(path, mode)
                except OSError:
                    pass


def _remove_tree(path: Path) -> None:
    ensure_no_symlink_components(path)
    if path.exists():
        if not path.is_dir():
            raise ValueError(f'Refusing to remove non-directory path: {path}')
        shutil.rmtree(path)


def install(
    project: Path,
    replace: bool = False,
    dry_run: bool = False,
    progress: Callable[[str], None] | None = None,
) -> dict:
    project = _project_path(project)
    if progress:
        progress("validated project path")
    destination, staging = _validated_paths(project)
    backup: Path | None = None
    ensure_no_symlink_components(destination)
    if destination.exists() and not destination.is_dir():
        raise ValueError(f'Installation destination is not a directory: {destination}')
    if destination.exists() and not replace:
        raise FileExistsError(f'{destination} exists; rerun with --replace to update it')

    # Refuse links or special files in the distributable before copytree can
    # follow or reinterpret them.
    list(iter_tree_files(SOURCE))
    if progress:
        progress("verified suite source")
    actions = [
        'stage complete suite', 'promote to prompts', 'update managed .gitignore',
        'create runtime directories', 'sync AGENTS.md and CLAUDE.md', 'write receipts and telemetry',
    ]
    if dry_run:
        if progress:
            progress("prepared dry-run preview")
        return {
            'status': 'dry_run', 'project_root': str(project), 'suite_destination': str(destination),
            'actions': actions, 'gitignore_entries': IGNORE_ENTRIES, 'docs_ignored': False,
        }

    snapshot = _snapshot(project)
    runtime_paths = {name: safe_child(project, name) for name in RUNTIME_DIRS}
    runtime_roots = {name: safe_child(project, name) for name in RUNTIME_ROOTS}
    existed_roots = {name: path.exists() for name, path in runtime_roots.items()}
    _remove_tree(staging)
    shutil.copytree(SOURCE, staging, ignore=copy_filter, symlinks=True)
    # copytree(symlinks=True) is safe only because iter_tree_files rejected all
    # source symlinks; verify the staged tree again before promotion.
    list(iter_tree_files(staging))
    if progress:
        progress("staged complete suite")

    if destination.exists():
        backup = safe_child(project, f'.md-prompts-backup-{dt.datetime.now().strftime("%Y%m%d%H%M%S")}-{uuid.uuid4().hex}')
        ensure_no_symlink_components(backup)
        destination.replace(backup)
    try:
        staging.replace(destination)
        if progress:
            progress("promoted suite to project prompts")
        gitignore = safe_child(project, '.gitignore')
        old_bytes = snapshot['.gitignore'][0]
        old = old_bytes.decode('utf-8') if old_bytes is not None else ''
        atomic_write_text(gitignore, managed_ignore(old))
        if progress:
            progress("updated managed project integration files")
        for path in runtime_paths.values():
            ensure_no_symlink_components(path)
            path.mkdir(parents=True, exist_ok=True)
            ensure_no_symlink_components(path)
        created_directories = [name for name, existed in existed_roots.items() if not existed]
        marker_payload_base = {
            'schema_version': '1.0',
            'created_by': 'mission-directives',
            'suite_version': (destination / 'VERSION').read_text().strip(),
        }
        for name in created_directories:
            marker = safe_child(runtime_roots[name], MANAGED_MARKER)
            atomic_write_json(marker, {**marker_payload_base, 'path': name})
        if progress:
            progress("created runtime and documentation directories")

        os.environ['MD_LOG_DIR'] = str(runtime_paths['.prompt_suite/logs'])
        sys.path.insert(0, str(destination / 'tools'))
        from sync_agent_guidance import sync_guidance

        guidance_receipt = safe_child(project, '.prompt_suite/agent-guidance-receipt.json')
        guidance = sync_guidance(project_root=project, suite_root=destination, receipt_path=guidance_receipt)
        if progress:
            progress("synchronized AGENTS.md and CLAUDE.md")
        receipt = {
            'schema_version': '1.0', 'status': 'installed', 'project_root': str(project),
            'suite_destination': 'prompts', 'suite_version': (destination / 'VERSION').read_text().strip(),
            'backup': str(backup) if backup else '', 'gitignore_entries': IGNORE_ENTRIES,
            'docs_ignored': False, 'guidance': guidance,
            'created_directories': created_directories,
            'preexisting_project_files': [name for name, (data, _mode) in snapshot.items() if data is not None],
            'installed_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        out = safe_child(project, '.prompt_suite/installation-receipt.json')
        atomic_write_json(out, receipt)
        receipt['receipt_path'] = str(out)
        if progress:
            progress("wrote installation receipts")
        try:
            from telemetry import append_event
            event = append_event(
                'installation', 'project_install', 'pass', tool='install.py',
                context={'suite_version': receipt['suite_version'], 'destination': 'prompts', 'replace': replace},
                log_dir=runtime_paths['.prompt_suite/logs'],
            )
            receipt['log_file'] = event['log_file']
        except Exception as telemetry_error:
            receipt['telemetry_warning'] = str(telemetry_error)
        if progress:
            progress("recorded installation telemetry")
        return receipt
    except Exception:
        if destination.exists():
            _remove_tree(destination)
        if backup and backup.exists():
            backup.replace(destination)
        _restore_snapshot(project, snapshot)
        for name, existed in existed_roots.items():
            path = runtime_roots[name]
            if not existed and path.exists():
                try:
                    _remove_tree(path)
                except OSError:
                    pass
        raise
    finally:
        if staging.exists():
            _remove_tree(staging)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('project_path', nargs='?')
    ap.add_argument('--replace', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument(
        '--no-tui',
        action='store_true',
        help='Use deterministic line-oriented progress instead of the dynamic terminal bar.',
    )
    a = ap.parse_args()
    tui = TUI('Mission Directives installer', total=9, enabled=False if a.no_tui else None)
    tui.start()
    raw = a.project_path or input('Project folder path: ').strip()
    try:
        result = install(
            Path(raw),
            replace=a.replace,
            dry_run=a.dry_run,
            progress=tui.step,
        )
    except (KeyboardInterrupt, EOFError) as exc:
        message = 'Installation cancelled by the user.' if isinstance(exc, KeyboardInterrupt) else 'No project path was provided.'
        tui.finish('FAIL')
        tui.summary('FAILURE', 'Mission Directives installation did not complete', [('Reason', message), ('Project', raw)])
        print(json.dumps({'status': 'fail', 'error': message}, indent=2), file=sys.stderr)
        return 130 if isinstance(exc, KeyboardInterrupt) else 1
    except Exception as exc:
        tui.finish('FAIL')
        tui.summary(
            'FAILURE',
            'Mission Directives installation did not complete',
            [('Reason', str(exc)), ('Project', raw)],
        )
        print(json.dumps({'status': 'fail', 'error': str(exc)}, indent=2), file=sys.stderr)
        return 1

    tui.finish('SUCCESS')
    if result.get('status') == 'dry_run':
        heading = 'Dry run completed; no project files were changed'
    else:
        heading = f"Mission Directives {result.get('suite_version', 'unknown')} installed successfully"
    tui.summary(
        'SUCCESS',
        heading,
        [
            ('Project', result.get('project_root', raw)),
            ('Suite', result.get('suite_destination', 'prompts')),
            ('Receipt', result.get('receipt_path')),
            ('Elapsed', f'{tui.elapsed_ms} ms'),
        ],
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
