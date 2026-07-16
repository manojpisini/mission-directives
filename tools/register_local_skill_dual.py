#!/usr/bin/env python3
"""Register an approved local skill transactionally in all supported locations."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import uuid
from pathlib import Path

from agent_paths import all_default_destinations
from security_utils import (
    atomic_write_json,
    ensure_no_symlink_components,
    is_within,
    iter_tree_files,
    remove_tree,
    safe_child,
    tree_digest,
    validate_tree_limits,
    validate_distinct_roots,
    validate_identifier,
)
from telemetry import append_event
from tui import TUI


def _stage_copy(source: Path, destination: Path) -> Path:
    parent = destination.parent
    ensure_no_symlink_components(parent)
    parent.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink_components(parent)
    stage = safe_child(parent, f'.{destination.name}.stage-{uuid.uuid4().hex}')
    shutil.copytree(source, stage, symlinks=True)
    list(iter_tree_files(stage))
    return stage


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-directory', required=True)
    ap.add_argument('--skill-id', required=True)
    ap.add_argument('--reinstall', action='store_true')
    ap.add_argument('--receipt-path')
    a = ap.parse_args()

    skill_id = validate_identifier(a.skill_id, kind='skill')
    src = ensure_no_symlink_components(Path(a.source_directory).expanduser())
    if not src.is_dir():
        raise SystemExit(f'Source directory does not exist: {src}')
    validate_tree_limits(src)
    skill_file = safe_child(src, 'SKILL.md')
    if not skill_file.is_file():
        raise SystemExit('SKILL.md with YAML frontmatter is required')
    skill_text = skill_file.read_text(encoding='utf-8')
    lines = skill_text.splitlines()
    if not lines or lines[0] != '---' or '---' not in lines[1:]:
        raise SystemExit('SKILL.md with closed YAML frontmatter is required')
    try:
        import yaml
        frontmatter = yaml.safe_load('\n'.join(lines[1:lines[1:].index('---') + 1])) or {}
    except Exception as exc:
        raise SystemExit(f'Invalid SKILL.md YAML frontmatter: {exc}') from exc
    if not isinstance(frontmatter, dict):
        raise SystemExit('SKILL.md frontmatter must be a mapping')

    roots = all_default_destinations()
    validate_distinct_roots(roots.values())
    destinations = [safe_child(base, skill_id) for base in roots.values()]
    validate_distinct_roots(destinations)
    for destination in destinations:
        if is_within(src, destination) or is_within(destination, src):
            raise SystemExit('Source and destination trees must not overlap')
        ensure_no_symlink_components(destination)
        if destination.exists() and not a.reinstall:
            raise SystemExit(f'Destination exists: {destination}; use --reinstall')

    tui = TUI(f'Register local skill {skill_id}', 4)
    tui.start()
    started = dt.datetime.now(dt.timezone.utc)
    source_digest = tree_digest(src)
    try:
        append_event(
            'skill', 'register_local_multi_location', 'started', tool='register_local_skill_dual.py',
            context={'skill_id': skill_id, 'source_tree_sha256': source_digest},
        )
    except Exception:
        # Telemetry is observational and must never obstruct a local transaction.
        pass
    tui.step('source verified')

    stages: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    promoted: list[Path] = []
    try:
        for destination in destinations:
            stage = _stage_copy(src, destination)
            if tree_digest(stage) != source_digest:
                raise RuntimeError(f'Staged skill tree hash differs: {stage}')
            stages[destination] = stage
        tui.step('staged for all locations')

        for destination in destinations:
            if destination.exists():
                backup = safe_child(destination.parent, f'.{skill_id}.backup-{uuid.uuid4().hex}')
                destination.replace(backup)
                backups[destination] = backup
        for destination in destinations:
            stages[destination].replace(destination)
            promoted.append(destination)
        hashes = [tree_digest(destination) for destination in destinations]
        if len(set(hashes)) != 1 or hashes[0] != source_digest:
            raise RuntimeError('Multi-location skill tree hashes differ')
        tui.step('multi-location hashes verified')

        result = {
            'skill_id': skill_id,
            'source_directory': str(src),
            'agents': str(destinations[0]),
            'claude_code': str(destinations[1]),
            'opencode': str(destinations[2]),
            'skill_tree_sha256': source_digest,
            'skill_md_sha256': __import__('hashlib').sha256((destinations[0] / 'SKILL.md').read_bytes()).hexdigest(),
            'verified': True,
            'quarantine_required': True,
            'registered_at': dt.datetime.now(dt.timezone.utc).isoformat(),
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
        try:
            append_event(
                'skill', 'register_local_multi_location', 'fail',
                duration_ms=int((dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000),
                tool='register_local_skill_dual.py', context={'skill_id': skill_id}, error=str(exc),
            )
        except Exception:
            pass
        tui.finish('FAIL')
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
        result['cleanup_warnings'] = cleanup_warnings
    tui.step('receipt written')
    tui.finish('PASS')
    try:
        event = append_event(
            'skill', 'register_local_multi_location', 'pass',
            duration_ms=int((dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000),
            tool='register_local_skill_dual.py',
            context={'skill_id': skill_id, 'source_tree_sha256': source_digest},
        )
        result['log_file'] = event['log_file']
    except Exception as exc:
        result['telemetry_warning'] = str(exc)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
