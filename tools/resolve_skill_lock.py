#!/usr/bin/env python3
"""Resolve trusted GitHub skill repository HEADs and bounded tarball hashes.

Resolution pins bytes but never approves a skill. Human review and live
conformance remain mandatory before automatic installation can be enabled.
"""
from __future__ import annotations

if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse
import datetime
import json
import os
import subprocess
import tempfile
from pathlib import Path

try:
    from security_utils import atomic_write_json, github_tarball_sha256, validate_github_repository, validate_identifier, validate_sha1
except ImportError:
    from tools.security_utils import atomic_write_json, github_tarball_sha256, validate_github_repository, validate_identifier, validate_sha1

ROOT = Path(__file__).resolve().parents[1]
def resolve_repo(repo: str) -> tuple[str, str]:
    repository = validate_github_repository(repo)
    with tempfile.TemporaryDirectory(prefix='md-lock-resolve-') as temp:
        env = os.environ.copy()
        env.update({
            'HOME': temp,
            'USERPROFILE': temp,
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_TERMINAL_PROMPT': '0',
            'GCM_INTERACTIVE': 'Never',
        })
        proc = subprocess.run(
            ['git', '-c', 'credential.helper=', '-c', 'protocol.file.allow=never', 'ls-remote', repository, 'HEAD'],
            text=True, capture_output=True, timeout=30, check=False, cwd=temp, env=env,
        )
    if proc.returncode != 0:
        raise RuntimeError(f'git ls-remote failed with exit code {proc.returncode}')
    fields = proc.stdout.strip().split()
    if len(fields) != 2 or fields[1] != 'HEAD':
        raise ValueError('Unexpected git ls-remote response')
    sha = validate_sha1(fields[0])
    return sha, github_tarball_sha256(repository, sha)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skill')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--promote', action='store_true')
    a = ap.parse_args()
    if not a.all and not a.skill:
        raise SystemExit('Use --skill ID or --all')
    requested = validate_identifier(a.skill, kind='skill') if a.skill else None
    path = ROOT / 'skills.lock.json'
    lock = json.loads(path.read_text(encoding='utf-8'))
    targets = [row for row in lock['entries'] if a.all or row['skill_id'] == requested]
    if not targets:
        raise SystemExit('No matching skill')
    cache: dict[str, tuple[str, str]] = {}
    for entry in targets:
        try:
            repository = validate_github_repository(entry['repository'])
            if repository not in cache:
                cache[repository] = resolve_repo(repository)
            sha, digest = cache[repository]
            entry.update({
                'repository': repository,
                'commit_sha': sha,
                'tarball_sha256': digest,
                'resolved_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'lock_status': 'review_required',
                'auto_install_allowed': False,
                'reason': 'Pinned bytes require manual code review and live conformance before approval.',
            })
            if a.promote:
                entry['reason'] = 'Pinned; --promote does not bypass manual code review or live conformance.'
        except Exception as exc:
            entry.update({'lock_status': 'invalid', 'auto_install_allowed': False, 'reason': str(exc)})
    atomic_write_json(path, lock)
    print(json.dumps(targets, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
