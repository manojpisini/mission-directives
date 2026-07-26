from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PUBLIC = SITE / "public"


def test_site_uses_project_pages_base_and_static_shell():
    config = (SITE / "astro.config.mjs").read_text(encoding="utf-8")
    assert "site: 'https://manojpisini.github.io'" in config
    assert "base: '/mission-directives'" in config
    assert "starlight(" not in config

    for path in (
        SITE / "src" / "pages" / "index.astro",
        PUBLIC / "styles.css",
        PUBLIC / "app.js",
        PUBLIC / "docs.html",
        PUBLIC / "guides.html",
        PUBLIC / "manuals.html",
        PUBLIC / "reference.html",
        PUBLIC / "reference" / "manuals" / "user-manual" / "index.html",
    ):
        assert path.exists()

    html = (SITE / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    assert 'href="styles.css"' in html
    assert "Mission Directives" in html


def test_docs_site_is_sectioned_and_visual():
    docs = (PUBLIC / "docs.html").read_text(encoding="utf-8")
    guides = (PUBLIC / "guides.html").read_text(encoding="utf-8")
    manuals = (PUBLIC / "manuals.html").read_text(encoding="utf-8")
    reference = (PUBLIC / "reference.html").read_text(encoding="utf-8")

    assert "System overview infographic" in docs
    assert "assets/infographics/mission-directives-overview.png" in docs
    assert "assets/diagrams/routing-system.svg" in docs
    assert "Guide library" in guides
    assert "Manual taxonomy" in manuals
    assert "Runtime payload diagram" in reference
    assert "assets/diagrams/runtime-payload.svg" in reference
    assert "reference/manuals/user-manual/" in manuals


def test_site_generation_is_canonical_and_build_driven():
    package = json.loads((SITE / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["prebuild"] == "pnpm run generate"
    assert package["scripts"]["check"] == "pnpm run build && node scripts/check-links.mjs"
    assert package["dependencies"]["astro"]
    assert "@astrojs/starlight" not in package["dependencies"]

    generator = (SITE / "scripts" / "generate-reference.mjs").read_text(
        encoding="utf-8"
    )
    for source in (
        "docs.html",
        "guides.html",
        "manuals.html",
        "reference.html",
        "reference/manuals",
        "visualAsset",
        "technical-map",
    ):
        assert source in generator
    assert "markdownToHtml" in generator


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
        "prompt_imports/",
        "infographics/",
    ):
        assert entry in ignored
