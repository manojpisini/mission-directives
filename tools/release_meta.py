#!/usr/bin/env python3
"""Canonical Mission Directives release metadata.

Every current-version consumer reads VERSION through this module. Historical
compatibility records may retain older versions, but executable tools and
current artifacts must never hard-code the active release number.
"""
from __future__ import annotations
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "VERSION"


def version(root: Path = ROOT) -> str:
    value = (root / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Invalid semantic version in {root / 'VERSION'}: {value!r}")
    return value


def release_id(root: Path = ROOT) -> str:
    return f"mission-directives-{version(root)}"
