from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_documentation_links import find_broken_relative_links  # noqa: E402


def test_repository_documentation_has_no_broken_relative_links():
    issues = find_broken_relative_links(ROOT)
    assert not issues, issues


def test_link_checker_detects_a_missing_relative_target(tmp_path: Path):
    guide = tmp_path / "GUIDE.md"
    guide.write_text("See [missing](docs/DOES_NOT_EXIST.md).\n", encoding="utf-8")
    issues = find_broken_relative_links(tmp_path)
    assert len(issues) == 1
    assert issues[0]["target"] == "docs/DOES_NOT_EXIST.md"
