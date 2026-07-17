#!/usr/bin/env python3
"""Build or verify the suite integrity manifest.

Runtime telemetry/results and interpreter caches are excluded. Symbolic links
are forbidden in a sealed release because they can make the manifest hash data
outside the distribution or change meaning after extraction.
"""

from __future__ import annotations

if __name__ == "__main__":
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)

import argparse, hashlib, json, os
from pathlib import Path
from typing import Iterable

try:
    from security_utils import atomic_write_json
except ImportError:
    from tools.security_utils import atomic_write_json

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_FILENAMES = {"MANIFEST.json", "VALIDATION.json"}
EXCLUDED_DIRNAMES = {"__pycache__", ".pytest_cache", ".git", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
RUNTIME_PREFIXES = {
    (".prompt_suite", "logs"),
    (".prompt_suite", "results"),
    (".prompt_suite", "runtime"),
}


def is_manifest_file(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if path.is_symlink():
        raise ValueError(
            f"symbolic link is not allowed in sealed manifest: {relative.as_posix()}"
        )
    if path.name in EXCLUDED_FILENAMES:
        return False
    if any(part in EXCLUDED_DIRNAMES for part in relative.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    if any(relative.parts[: len(prefix)] == prefix for prefix in RUNTIME_PREFIXES):
        return path.name == "README.md"
    return path.is_file()


def iter_manifest_files(root: Path) -> Iterable[Path]:
    root = root.resolve()
    for directory, dirnames, filenames in os.walk(
        root, topdown=True, followlinks=False
    ):
        current = Path(directory)
        kept = []
        for name in sorted(dirnames):
            candidate = current / name
            rel = candidate.relative_to(root)
            if candidate.is_symlink():
                raise ValueError(
                    f"symbolic link is not allowed in sealed manifest: {rel.as_posix()}"
                )
            if name in EXCLUDED_DIRNAMES:
                continue
            kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames):
            path = current / name
            if is_manifest_file(path, root):
                yield path


def current(root: Path = ROOT) -> dict[str, object]:
    root = root.resolve()
    files = []
    for path in iter_manifest_files(root):
        data = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    files.sort(key=lambda row: row["path"])
    return {
        "suite_version": (root / "VERSION").read_text(encoding="utf-8").strip(),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        now = current()
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1
    path = ROOT / "MANIFEST.json"
    if args.check:
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        ok = old == now
        print(
            json.dumps(
                {
                    "status": "pass" if ok else "fail",
                    "expected_files": len(now["files"]),
                    "manifest_files": len(old.get("files", [])),
                },
                indent=2,
            )
        )
        return 0 if ok else 1
    atomic_write_json(path, now)
    print(len(now["files"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
