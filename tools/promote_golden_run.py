#!/usr/bin/env python3
"""Promote a real verified run to human-reviewed golden status."""
from __future__ import annotations

if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse
import datetime
from pathlib import Path

try:
    from security_utils import atomic_write_json, ensure_no_symlink_components, read_json_bounded, safe_child, validate_identifier
except ImportError:
    from tools.security_utils import atomic_write_json, ensure_no_symlink_components, read_json_bounded, safe_child, validate_identifier

ROOT = Path(__file__).resolve().parents[1]


def _read_json(path_value: str) -> dict:
    path = ensure_no_symlink_components(Path(path_value).expanduser())
    if not path.is_file():
        raise ValueError(f'Expected a regular JSON file: {path}')
    value = read_json_bounded(path)
    if not isinstance(value, dict):
        raise ValueError(f'Expected a JSON object: {path}')
    return value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run-manifest', required=True)
    ap.add_argument('--review-receipt', required=True)
    ap.add_argument('--target', required=True)
    a = ap.parse_args()
    target = validate_identifier(a.target, kind='golden-run target')
    run = _read_json(a.run_manifest)
    receipt = _read_json(a.review_receipt)
    errors = []
    if run.get('state') not in ('verified', 'closed'):
        errors.append('run is not verified or closed')
    if not run.get('evidence_snapshots'):
        errors.append('missing evidence snapshots')
    if not run.get('artifacts'):
        errors.append('missing real artifact records')
    if not receipt.get('reviewer') or receipt.get('decision') != 'approve_golden':
        errors.append('invalid human review receipt')
    if errors:
        raise SystemExit('; '.join(errors))
    out = safe_child(ROOT / 'evaluations' / 'golden_runs', target)
    out.mkdir(parents=True, exist_ok=True)
    ensure_no_symlink_components(out)
    payload = {
        'golden_run_id': f'{target}-human-reviewed',
        'target': target,
        'review_status': 'human_reviewed',
        'promoted_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'review_receipt': receipt,
        'run': run,
    }
    atomic_write_json(safe_child(out, 'human_reviewed_manifest.json'), payload)
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
