#!/usr/bin/env python3
"""Install or update Mission Directives in a project.

This source-tree wrapper delegates to the packaged lifecycle implementation so
repository installs and PyPI installs use exactly the same code path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mission_directives.installer import (  # noqa: E402
    install_project,
    managed_ignore,
)


def install(
    project: Path,
    replace: bool = False,
    dry_run: bool = False,
    progress=None,
    tracking: str = "ignored",
) -> dict:
    if progress:
        progress("validated project path")
    result = install_project(
        project, replace=replace, dry_run=dry_run, tracking=tracking
    )
    if progress:
        progress("completed project installation")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--tracking", choices=("ignored", "outputs", "all"), default="ignored")
    parser.add_argument("--no-tui", action="store_true")
    args = parser.parse_args()
    try:
        print("PROGRESS validating project", file=sys.stderr)
        result = install(
            Path(args.project_path),
            replace=args.replace,
            dry_run=args.dry_run,
            tracking=args.tracking,
        )
    except (FileNotFoundError, FileExistsError, ValueError, OSError) as exc:
        print("[FAILURE] Mission Directives installer", file=sys.stderr)
        print(f"Reason: {exc}", file=sys.stderr)
        return 1
    print(
        "[SUCCESS] Mission Directives installer: "
        + ("Dry run completed" if args.dry_run else "Installation completed"),
        file=sys.stderr,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
