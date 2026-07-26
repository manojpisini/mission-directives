from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def test_site_uses_project_pages_base_and_starlight():
    config = (SITE / "astro.config.mjs").read_text(encoding="utf-8")
    assert "site: 'https://manojpisini.github.io'" in config
    assert "base: '/mission-directives'" in config
    assert "starlight(" in config
    assert "custom.css" in config


def test_site_generation_is_canonical_and_build_driven():
    package = json.loads((SITE / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["prebuild"] == "npm run generate"
    assert package["dependencies"]["astro"]
    assert package["dependencies"]["@astrojs/starlight"]

    generator = (SITE / "scripts" / "generate-reference.mjs").read_text(
        encoding="utf-8"
    )
    for source in (
        "catalog.json",
        "SCENARIO_CATALOG.json",
        "skill_registry.json",
        "prompts",
        "docs",
    ):
        assert source in generator
    assert "superpowers" in generator


def test_pages_workflow_uses_node_24_compatible_actions():
    workflow = (ROOT / ".github" / "workflows" / "deploy-docs.yml").read_text(
        encoding="utf-8"
    )
    assert "actions/checkout@v7" in workflow
    assert "withastro/action@v6" in workflow
    assert "actions/deploy-pages@v5" in workflow
    assert "path: ./site" in workflow
    assert "pages: write" in workflow
    assert "id-token: write" in workflow


def test_generated_and_dependency_outputs_are_ignored():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for entry in (
        "site/node_modules/",
        "site/dist/",
        "site/.astro/",
        "site/src/content/docs/reference/",
    ):
        assert entry in ignored
