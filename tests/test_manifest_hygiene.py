from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_manifest import iter_manifest_files, current  # noqa: E402


def test_manifest_ignores_python_and_test_caches(tmp_path: Path):
    (tmp_path / "kept.txt").write_text("kept", encoding="utf-8")
    cache = tmp_path / "tools" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "module.pyc").write_bytes(b"cache")
    pytest_cache = tmp_path / ".pytest_cache"
    pytest_cache.mkdir()
    (pytest_cache / "state").write_text("cache", encoding="utf-8")

    paths = {path.relative_to(tmp_path).as_posix() for path in iter_manifest_files(tmp_path)}
    assert paths == {"kept.txt"}


def test_manifest_ignores_daily_runtime_logs(tmp_path):
    root=tmp_path/'suite'; root.mkdir(); (root/'VERSION').write_text('1.0.0\n')
    logs=root/'.prompt_suite'/'logs'; logs.mkdir(parents=True); (logs/'README.md').write_text('docs')
    (logs/'2026-07-15.toml').write_text('[[events]]\naction="x"\n'); (logs/'2026-07-15.toml.lock').write_text('')
    data=current(root); paths={x['path'] for x in data['files']}
    assert '.prompt_suite/logs/README.md' in paths
    assert '.prompt_suite/logs/2026-07-15.toml' not in paths
    assert '.prompt_suite/logs/2026-07-15.toml.lock' not in paths
