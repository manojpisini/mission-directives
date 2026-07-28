from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

REQUIRED_TOP_LEVEL = {
    "schema_version",
    "revision",
    "project",
    "goals",
    "scope",
    "stack",
    "paths",
    "commands",
    "constraints",
    "working_agreements",
    "current_state",
    "provenance",
    "extensions",
}


def _load_module():
    path = ROOT / "src" / "mission_directives" / "project_config.py"
    spec = importlib.util.spec_from_file_location("mission_directives_project_config", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_seed_format_save_load_and_detection_contract(tmp_path):
    project_config = _load_module()
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "demo-root",
                "description": "Root package summary",
                "packageManager": "pnpm@9.0.0",
                "scripts": {
                    "dev": "vite",
                    "test": "vitest",
                    "lint": "eslint .",
                    "typecheck": "tsc --noEmit",
                    "build": "vite build"
                },
                "dependencies": {
                    "react": "^19.0.0",
                    "vercel": "^1.0.0"
                }
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "requirements-dev.txt").write_text("ruff\nmypy\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "src" / "main.rs").write_text("fn main() {}\n", encoding="utf-8")
    (tmp_path / "site").mkdir()
    (tmp_path / "site" / "package.json").write_text(
        json.dumps({"name": "site-package"}),
        encoding="utf-8",
    )
    deep = tmp_path / "packages" / "app"
    deep.mkdir(parents=True)
    (deep / "package.json").write_text(
        json.dumps({"name": "ignored-deep-package"}),
        encoding="utf-8",
    )

    seeded = project_config.seed_project_config(tmp_path)

    assert set(seeded) == REQUIRED_TOP_LEVEL
    assert seeded["project"]["name"] == "demo-root"
    assert seeded["project"]["summary"] == "Root package summary"
    assert seeded["stack"]["languages"] == ["JavaScript", "Python"]
    assert seeded["stack"]["frameworks"] == ["React"]
    assert seeded["stack"]["package_managers"] == ["pip", "pnpm"]
    assert seeded["stack"]["deployment_targets"] == ["Vercel"]
    assert seeded["paths"]["source"] == ["src"]
    assert seeded["paths"]["tests"] == ["tests"]
    assert seeded["paths"]["docs"] == ["docs"]
    assert seeded["paths"]["entrypoints"] == ["src/main.rs"]
    assert seeded["commands"]["development"] == ["pnpm run dev"]
    assert "python -m pytest" in seeded["commands"]["test"]
    assert "python -m ruff check ." in seeded["commands"]["lint"]
    assert "python -m mypy ." in seeded["commands"]["typecheck"]

    manifest_paths = [item["path"] for item in seeded["extensions"]["detection"]["manifests"]]
    assert manifest_paths == ["package.json", "requirements-dev.txt", "site/package.json"]
    assert "packages/app/package.json" not in manifest_paths
    assert seeded["provenance"]["source_paths"] == manifest_paths

    formatted = project_config.format_project_config(seeded)
    assert formatted.endswith("\n")
    assert json.loads(formatted) == seeded

    saved = project_config.save_project_config(tmp_path, seeded)
    loaded = project_config.load_project_config(tmp_path)
    assert saved["revision"] == 0
    assert loaded == saved


def test_refresh_preserves_user_authored_mission_goals_scope_constraints_and_owners(tmp_path):
    project_config = _load_module()
    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "demo-root",
                "description": "Original summary",
                "packageManager": "npm@10.0.0",
                "scripts": {"test": "vitest"}
            }
        ),
        encoding="utf-8",
    )

    current = project_config.seed_project_config(tmp_path)
    current["project"]["mission"] = "Preserve this mission."
    current["project"]["owners"] = ["platform@example.com"]
    current["goals"]["outcomes"] = ["Ship the config slice."]
    current["scope"]["include"] = ["src", "tests"]
    current["scope"]["protected_paths"] = [".mission-directives/project.json", "secrets/"]
    current["constraints"]["security"] = ["Do not store secrets."]
    saved = project_config.save_project_config(tmp_path, current)

    (tmp_path / "package.json").write_text(
        json.dumps(
            {
                "name": "demo-root-renamed",
                "description": "Updated detected summary",
                "packageManager": "pnpm@9.0.0",
                "scripts": {"dev": "vite", "build": "vite build"},
                "dependencies": {"astro": "^5.0.0"}
            }
        ),
        encoding="utf-8",
    )

    diff = project_config.refresh_project_config_diff(tmp_path)
    refreshed = diff["refreshed"]

    assert diff["exists"] is True
    assert diff["has_changes"] is True
    assert refreshed["project"]["mission"] == "Preserve this mission."
    assert refreshed["project"]["owners"] == ["platform@example.com"]
    assert refreshed["goals"]["outcomes"] == ["Ship the config slice."]
    assert refreshed["scope"]["include"] == ["src", "tests"]
    assert refreshed["scope"]["protected_paths"] == [".mission-directives/project.json", "secrets/"]
    assert refreshed["constraints"]["security"] == ["Do not store secrets."]
    assert refreshed["project"]["name"] == "demo-root-renamed"
    assert refreshed["project"]["summary"] == "Original summary"
    assert refreshed["stack"]["frameworks"] == ["Astro"]
    assert refreshed["stack"]["package_managers"] == ["pnpm"]
    assert refreshed["commands"]["development"] == ["pnpm run dev"]
    assert refreshed["commands"]["build"] == ["pnpm run build"]
    assert "project.name" in diff["changed_fields"]

    resaved = project_config.save_project_config(tmp_path, refreshed, expected_revision=saved["revision"])
    assert resaved["revision"] == saved["revision"] + 1


def test_validation_rejects_stale_revision_secrets_and_unknown_top_level_fields(tmp_path):
    project_config = _load_module()
    (tmp_path / "package.json").write_text(json.dumps({"name": "demo-root"}), encoding="utf-8")

    seeded = project_config.seed_project_config(tmp_path)
    saved = project_config.save_project_config(tmp_path, seeded)

    stale = json.loads(json.dumps(saved))
    stale["project"]["status"] = "stale-edit"
    updated = json.loads(json.dumps(saved))
    updated["project"]["status"] = "fresh-edit"
    latest = project_config.save_project_config(tmp_path, updated, expected_revision=saved["revision"])
    assert latest["revision"] == 1
    with pytest.raises(project_config.StaleProjectConfigError, match="Stale project config revision"):
        project_config.save_project_config(tmp_path, stale)

    secret_payload = project_config.seed_project_config(tmp_path)
    secret_payload["project"]["mission"] = "ghp_abcdefghijklmnopqrstuvwxyz123456"
    with pytest.raises(project_config.ProjectConfigSecretError, match="Secret-bearing value"):
        project_config.validate_project_config(secret_payload, project_root=tmp_path)

    unknown_payload = project_config.seed_project_config(tmp_path)
    unknown_payload["unexpected"] = True
    with pytest.raises(project_config.ProjectConfigValidationError, match="Unknown top-level fields"):
        project_config.validate_project_config(unknown_payload, project_root=tmp_path)


def test_module_is_self_contained_and_not_repo_tools_bound():
    source = (ROOT / "src" / "mission_directives" / "project_config.py").read_text(encoding="utf-8")
    assert "tools.security_utils" not in source
    assert "_runtime" in source
