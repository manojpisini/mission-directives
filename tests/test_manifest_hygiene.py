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


def test_manifest_ignores_advisory_lock_files(tmp_path):
    (tmp_path / "VERSION").write_text("1.0.0\n")
    runtime = tmp_path / ".prompt_suite"
    runtime.mkdir()
    (runtime / "prompt-library-import.lock").write_text("")
    paths = {row["path"] for row in current(tmp_path)["files"]}
    assert ".prompt_suite/prompt-library-import.lock" not in paths


def test_manifest_keeps_release_lockfiles(tmp_path):
    (tmp_path / "VERSION").write_text("1.0.0\n")
    (tmp_path / "Cargo.lock").write_text("version = 3\n")
    (tmp_path / "dependencies.lock").write_text("sealed\n")
    paths = {row["path"] for row in current(tmp_path)["files"]}
    assert "Cargo.lock" in paths
    assert "dependencies.lock" in paths

def test_manifest_excludes_site_build_and_generated_reference_outputs(tmp_path):
    (tmp_path / "VERSION").write_text("1.0.0\n")
    site = tmp_path / "site"
    (site / "src").mkdir(parents=True)
    (site / "package.json").write_text("{}\n")
    (site / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
    generated = site / "src" / "content" / "docs" / "reference"
    generated.mkdir(parents=True)
    (generated / "index.md").write_text("# generated\n")
    for relative in ("node_modules/pkg/index.js", "dist/index.html", ".astro/data.json"):
        output = site / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("generated\n")

    paths = {row["path"] for row in current(tmp_path)["files"]}
    assert "site/package.json" in paths
    assert "site/pnpm-lock.yaml" in paths
    assert "site/src/content/docs/reference/index.md" not in paths
    assert not any(
        path.startswith(("site/node_modules/", "site/dist/", "site/.astro/"))
        for path in paths
    )
def test_manifest_ignores_site_preview_logs(tmp_path):
    (tmp_path / "VERSION").write_text("1.0.0\n")
    (tmp_path / "site-preview.err.log").write_text("err\n")
    (tmp_path / "site-preview.out.log").write_text("out\n")
    (tmp_path / "kept.log").write_text("keep\n")

    paths = {row["path"] for row in current(tmp_path)["files"]}
    assert "site-preview.err.log" not in paths
    assert "site-preview.out.log" not in paths
    assert "kept.log" in paths

def test_manifest_ignores_prompt_imports(tmp_path):
    (tmp_path / "VERSION").write_text("1.0.0\n")
    imports = tmp_path / "prompt_imports"
    imports.mkdir()
    (imports / "internal-plan.json").write_text("{}\n")

    paths = {row["path"] for row in current(tmp_path)["files"]}
    assert "prompt_imports/internal-plan.json" not in paths
