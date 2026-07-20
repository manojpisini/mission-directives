#!/usr/bin/env python3
"""Ingest verified model benchmark rows into model_profiles.json."""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse
import datetime
import json
import math
import statistics
from pathlib import Path

try:
    from security_utils import (
        atomic_write_json,
        ensure_no_symlink_components,
        exclusive_lock,
        read_json_bounded,
        validate_identifier,
    )
except ImportError:
    from tools.security_utils import (
        atomic_write_json,
        ensure_no_symlink_components,
        exclusive_lock,
        read_json_bounded,
        validate_identifier,
    )

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "fixture_id",
    "schema_conformance",
    "refusal_correct",
    "fabricated",
    "latency_ms",
    "input_tokens",
    "output_tokens",
}


def _number(value, name: str, *, minimum: float = 0.0) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) < minimum
    ):
        raise ValueError(f"{name} must be a finite number >= {minimum}")
    return float(value)


def _binary(value, name: str) -> float:
    numeric = _number(value, name)
    if numeric not in {0.0, 1.0}:
        raise ValueError(f"{name} must be 0 or 1")
    return numeric


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-id", required=True)
    ap.add_argument("--result", required=True)
    ap.add_argument("--approve-production", action="store_true")
    a = ap.parse_args()
    model_id = validate_identifier(a.model_id, kind="model")
    result_path = ensure_no_symlink_components(Path(a.result).expanduser())
    if not result_path.is_file():
        raise SystemExit(f"Benchmark result is not a regular file: {result_path}")
    rows = read_json_bounded(result_path, max_bytes=64 * 1024 * 1024)
    if not isinstance(rows, list) or not rows or len(rows) > 100_000:
        raise SystemExit(
            "Result must be a non-empty JSON list with at most 100000 rows"
        )
    fixture_ids = set()
    normalized = []
    for row in rows:
        if not isinstance(row, dict):
            raise SystemExit("Every benchmark row must be a JSON object")
        missing = REQUIRED - set(row)
        if missing:
            raise SystemExit(
                f"Missing fields for {row.get('fixture_id')}: {sorted(missing)}"
            )
        fixture_id = validate_identifier(str(row["fixture_id"]), kind="fixture")
        if fixture_id in fixture_ids:
            raise SystemExit(f"Duplicate fixture_id: {fixture_id}")
        fixture_ids.add(fixture_id)
        normalized.append(
            {
                **row,
                "fixture_id": fixture_id,
                "schema_conformance": _binary(
                    row["schema_conformance"], "schema_conformance"
                ),
                "refusal_correct": _binary(row["refusal_correct"], "refusal_correct"),
                "fabricated": _binary(row["fabricated"], "fabricated"),
                "latency_ms": _number(row["latency_ms"], "latency_ms"),
                "input_tokens": _number(row["input_tokens"], "input_tokens"),
                "output_tokens": _number(row["output_tokens"], "output_tokens"),
                "cost": _number(row.get("cost", 0), "cost"),
            }
        )

    profiles_path = ROOT / "config/model_profiles.json"
    with exclusive_lock(profiles_path.with_name(profiles_path.name + ".lock")):
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
        profile = next(
            (item for item in profiles["profiles"] if item["model_id"] == model_id),
            None,
        )
        if not profile:
            profile = {
                "model_id": model_id,
                "provider": "operator_defined",
                "supported_modalities": ["text"],
                "known_failure_modes": [],
            }
            profiles["profiles"].append(profile)
        schema_rate = statistics.mean(row["schema_conformance"] for row in normalized)
        refusal_rate = statistics.mean(row["refusal_correct"] for row in normalized)
        fabrication_rate = statistics.mean(row["fabricated"] for row in normalized)
        eligible = bool(a.approve_production)
        profile.update(
            {
                "measurement_status": "measured",
                "production_eligible": eligible,
                "structured_output_reliability": schema_rate,
                "refusal_correctness": refusal_rate,
                "fabrication_rate": fabrication_rate,
                "latency_ms_p50": statistics.median(
                    row["latency_ms"] for row in normalized
                ),
                "benchmark_runs": len(normalized),
                "last_measured_at": datetime.datetime.now(
                    datetime.timezone.utc
                ).isoformat(),
                "average_input_tokens": statistics.mean(
                    row["input_tokens"] for row in normalized
                ),
                "average_output_tokens": statistics.mean(
                    row["output_tokens"] for row in normalized
                ),
                "average_cost": statistics.mean(row["cost"] for row in normalized),
            }
        )
        atomic_write_json(profiles_path, profiles)
    print(json.dumps(profile, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
