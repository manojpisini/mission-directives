#!/usr/bin/env python3
"""Validate relative Markdown links in root and docs manuals.

The checker deliberately ignores external URLs, mail links, sandbox links, and
in-document anchors. It validates the file component of local links while
allowing optional fragments such as ``GUIDE.md#section``.
"""
from __future__ import annotations
if __name__ == '__main__':
    try:
        from tool_runtime import bootstrap_tool
    except ImportError:
        from tools.tool_runtime import bootstrap_tool
    _MD_TUI = bootstrap_tool(__file__)


import argparse
import json
from pathlib import Path
import re
import subprocess
from typing import Iterable

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCED_CODE_RE = re.compile(r"```.*?```", re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "sandbox:", "data:")


def documentation_files(root: Path) -> Iterable[Path]:
    yield from sorted(root.glob("*.md"))
    docs = root / "docs"
    if docs.exists():
        yield from sorted(docs.rglob("*.md"))


def _link_target(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1 : value.index(">")]
    else:
        # Markdown may tack on a title after whitespace; that extra garnish is not the URL.
        value = value.split(maxsplit=1)[0]
    return value.strip()


def _tracked_paths(root: Path) -> set[str] | None:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return {path for path in result.stdout.decode("utf-8").split("\0") if path}


def find_broken_relative_links(root: Path) -> list[dict[str, object]]:
    root = root.resolve()
    tracked_paths = _tracked_paths(root)
    issues: list[dict[str, object]] = []
    for path in documentation_files(root):
        text = path.read_text(encoding="utf-8")
        searchable = FENCED_CODE_RE.sub("", text)
        searchable = INLINE_CODE_RE.sub("", searchable)
        for match in LINK_RE.finditer(searchable):
            target = _link_target(match.group(1))
            if not target or target.startswith("#") or target.startswith(EXTERNAL_PREFIXES):
                continue
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            candidate = (path.parent / file_part).resolve()
            try:
                candidate.relative_to(root)
            except ValueError:
                issues.append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": searchable[: match.start()].count("\n") + 1,
                        "target": target,
                        "reason": "relative link escapes repository root",
                    }
                )
                continue
            if not candidate.exists():
                issues.append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": searchable[: match.start()].count("\n") + 1,
                        "target": target,
                        "reason": "target does not exist",
                    }
                )
            elif tracked_paths is not None and candidate.is_file():
                relative_candidate = candidate.relative_to(root).as_posix()
                if relative_candidate not in tracked_paths:
                    issues.append(
                        {
                            "file": str(path.relative_to(root)),
                            "line": searchable[: match.start()].count("\n") + 1,
                            "target": target,
                            "reason": "target is not tracked",
                        }
                    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    issues = find_broken_relative_links(args.root)
    result = {"status": "pass" if not issues else "fail", "broken_links": issues}
    print(json.dumps(result, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
