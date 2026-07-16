#!/usr/bin/env python3
"""Ingest measured pair-versus-single results and make a transparent recommendation."""
from __future__ import annotations

if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse
import json
import math
from pathlib import Path

try:
    from security_utils import atomic_write_json, ensure_no_symlink_components, exclusive_lock, read_json_bounded, validate_identifier
except ImportError:
    from tools.security_utils import atomic_write_json, ensure_no_symlink_components, exclusive_lock, read_json_bounded, validate_identifier

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'tokens', 'wall_time', 'missed_findings', 'execution_precision', 'reviewer_clarity', 'safety', 'ceremony_cost'}


def _load_result(path_value: str, label: str) -> dict:
    path = ensure_no_symlink_components(Path(path_value).expanduser())
    if not path.is_file():
        raise ValueError(f'{label} result is not a regular file: {path}')
    value = read_json_bounded(path)
    if not isinstance(value, dict):
        raise ValueError(f'{label} result must be a JSON object')
    missing = REQUIRED - set(value)
    if missing:
        raise ValueError(f'{label} result missing {sorted(missing)}')
    for key in REQUIRED:
        number = value[key]
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not math.isfinite(float(number)):
            raise ValueError(f'{label}.{key} must be a finite number')
    return value


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pair-id', required=True)
    ap.add_argument('--paired-result', required=True)
    ap.add_argument('--single-result', required=True)
    a = ap.parse_args()
    pair_id = validate_identifier(a.pair_id, kind='pair')
    definitions = []
    for path in (ROOT / 'evaluations' / 'pair_vs_single').glob('*.json'):
        value = read_json_bounded(path)
        if value.get('pair_id') == pair_id:
            definitions.append((path, value))
    if len(definitions) != 1:
        raise SystemExit('Unknown or ambiguous pair comparison definition')
    path, definition = definitions[0]
    paired = _load_result(a.paired_result, 'paired')
    single = _load_result(a.single_result, 'single')
    safety_gain = paired['safety'] - single['safety']
    precision_gain = paired['execution_precision'] - single['execution_precision']
    clarity_gain = paired['reviewer_clarity'] - single['reviewer_clarity']
    ceremony_penalty = paired['ceremony_cost'] - single['ceremony_cost']
    recommendation = 'retain_pair' if safety_gain > 0 or precision_gain > 0.05 or clarity_gain > 0.05 else 'merge_to_single' if ceremony_penalty > 0 and safety_gain <= 0 and precision_gain <= 0 else 'human_review'
    update = {
        'measurement_status': 'measured',
        'paired_result': paired,
        'single_result': single,
        'comparison': {
            'safety_gain': safety_gain,
            'precision_gain': precision_gain,
            'clarity_gain': clarity_gain,
            'ceremony_penalty': ceremony_penalty,
        },
        'recommendation': recommendation,
    }
    with exclusive_lock(path.with_name(path.name + '.lock')):
        latest = read_json_bounded(path)
        latest.update(update)
        atomic_write_json(path, latest)
    definition = latest
    print(json.dumps(definition, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
