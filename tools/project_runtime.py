#!/usr/bin/env python3
"""Resolve project-scoped Mission Directives runtime and artifact paths."""

from __future__ import annotations

import os
from pathlib import Path

OUTPUT_CATEGORIES = frozenset(
    {"results", "reports", "artifacts", "plans", "outputs", "docs", "logs"}
)


def project_root(start: Path | str = ".") -> Path:
    explicit = os.environ.get("MD_PROJECT_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    current = Path(start).expanduser().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".mission-directives/config.json").is_file():
            return candidate
    return current


def artifact_root(start: Path | str = ".") -> Path:
    explicit = os.environ.get("MD_ARTIFACT_ROOT")
    if explicit:
        return Path(explicit).expanduser().resolve()
    root = project_root(start)
    installed = root / ".mission-directives"
    return installed if installed.is_dir() else root


def artifact_path(relative: Path | str, start: Path | str = ".") -> Path:
    raw = Path(relative)
    if raw.is_absolute() or not raw.parts or raw.parts[0] not in OUTPUT_CATEGORIES:
        raise ValueError("Artifact path must begin with a supported output category")
    if any(part in {"", ".", ".."} for part in raw.parts):
        raise ValueError("Artifact path cannot contain traversal components")
    base = artifact_root(start)
    candidate = (base / raw).resolve()
    try:
        candidate.relative_to(base.resolve())
    except ValueError as exc:
        raise ValueError("Artifact path escapes the project output root") from exc
    return candidate


if __name__ == "__main__":
    print(artifact_root())
