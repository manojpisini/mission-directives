from __future__ import annotations

import json
import re
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
        PUBLIC / "getting-started.html",
        PUBLIC / "installation.html",
        PUBLIC / "contributing.html",
        PUBLIC / "guides.html",
        PUBLIC / "manuals.html",
        PUBLIC / "reference.html",
        PUBLIC / "reference" / "manuals" / "user-manual" / "index.html",
    ):
        assert path.exists()

    html = (SITE / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    assert 'href="styles.css"' in html
    assert "Mission Directives" in html
    assert "assets/brand/mission_directives_logo_dark.svg" in html
    assert "brand__mark" not in html


def test_site_uses_canonical_brand_assets_and_onboarding_pages():
    brand = PUBLIC / "assets" / "brand"
    source_names = (
        "mission_directives_full_logo_dark.svg",
        "mission_directives_full_logo_lateral_dark.svg",
        "mission_directives_full_logo_lateral_light.svg",
        "mission_directives_full_logo_light.svg",
        "mission_directives_logo_dark.svg",
        "mission_directives_logo_light.svg",
        "mission_directives_wordmark_dark.svg",
        "mission_directives_wordmark_light.svg",
    )
    for name in source_names:
        assert (ROOT / "assets" / "images" / name).exists()

    deployed_names = {
        "mission_directives_full_logo_lateral_dark.svg",
        "mission_directives_logo_dark.svg",
        "mission_directives_logo_light.svg",
        "mission_directives_wordmark_dark.svg",
    }
    assert {path.name for path in brand.glob("*.svg")} == deployed_names
    for name in deployed_names:
        assert (brand / name).read_bytes() == (ROOT / "assets" / "images" / name).read_bytes()
    assert not (PUBLIC / "favicon.svg").exists()

    for name, heading in (
        ("getting-started.html", "Getting Started"),
        ("installation.html", "Installation"),
        ("contributing.html", "Contributing"),
    ):
        html = (PUBLIC / name).read_text(encoding="utf-8")
        assert heading in html
        assert 'class="brand__logo"' in html
        assert "assets/brand/mission_directives_logo_dark.svg" in html
        assert "brand__mark" not in html

    contributing = (PUBLIC / "contributing.html").read_text(encoding="utf-8")
    assert "MEMORY.md" not in contributing
    assert "/reference/manuals/memory/" not in contributing

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "assets/images/mission_directives_full_logo_lateral_light.svg" in readme
    assert "assets/images/mission_directives_full_logo_lateral_dark.svg" in readme
    assert "assets/readme/mission-directives-banner.svg" not in readme


def test_landing_and_documentation_headers_keep_brand_and_search_only():
    landing = (SITE / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    docs = (PUBLIC / "docs.html").read_text(encoding="utf-8")
    styles = (PUBLIC / "styles.css").read_text(encoding="utf-8")
    for html in (landing, docs):
        assert 'class="topbar"' in html
        assert 'class="topbar__inner"' in html
        assert 'class="search-trigger"' in html
        assert 'class="top-actions"' not in html
        assert 'aria-label="Primary navigation"' not in html
        assert "mission_directives_logo_dark.svg" in html
        assert "mission_directives_logo_light.svg" in html
        assert "brand__section" not in html
        assert html.index('class="brand"') < html.index('class="search-trigger"')

    assert "width: 260px;" in styles
    assert "width: min(1180px, calc(100% - 40px));" in styles
    assert "width: 40px;" in styles
    assert "margin-left: auto;" in styles
    assert ".top-actions" not in styles

    assert "landing-header" not in landing
    assert "landing-nav" not in landing


def test_readme_branding_uses_explicit_transparent_theme_variants_and_license_badge():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for fragment in (
        "label=CI",
        "label=Docs",
        "label=PyPI",
        "label=Python",
        "MIT%20OR%20Apache--2.0",
    ):
        assert fragment in readme

    for light, dark in (
        (
            "assets/images/mission_directives_full_logo_lateral_dark.svg",
            "assets/images/mission_directives_full_logo_lateral_light.svg",
        ),
        ("assets/readme/routing-flow.svg", "assets/readme/routing-flow-dark.svg"),
        ("assets/readme/inventory.svg", "assets/readme/inventory-dark.svg"),
    ):
        assert f'media="(prefers-color-scheme: dark)" srcset="{dark}"' in readme
        assert f'src="{light}"' in readme

    for name in ("routing-flow.svg", "inventory.svg"):
        light = (ROOT / "assets" / "readme" / name).read_text(encoding="utf-8")
        dark = (ROOT / "assets" / "readme" / name.replace(".svg", "-dark.svg")).read_text(
            encoding="utf-8"
        )
        assert "prefers-color-scheme" not in light + dark
        assert "#ffffff" not in light
        assert "#ffffff" in dark
        assert '<rect width="1000"' not in light + dark

    logo = (ROOT / "assets" / "images" / "mission_directives_full_logo_lateral_dark.svg").read_text(
        encoding="utf-8"
    )
    dark_logo = (ROOT / "assets" / "images" / "mission_directives_full_logo_lateral_light.svg").read_text(
        encoding="utf-8"
    )
    assert "prefers-color-scheme" not in logo + dark_logo
    assert logo != dark_logo


def test_docs_site_is_sectioned_and_visual():
    docs = (PUBLIC / "docs.html").read_text(encoding="utf-8")
    guides = (PUBLIC / "guides.html").read_text(encoding="utf-8")
    manuals = (PUBLIC / "manuals.html").read_text(encoding="utf-8")
    reference = (PUBLIC / "reference.html").read_text(encoding="utf-8")

    assert "System overview infographic" not in docs
    assert "assets/infographics/mission-directives-overview.png" not in docs
    assert not (PUBLIC / "assets" / "infographics" / "mission-directives-overview.png").exists()
    assert "assets/diagrams/routing-system.svg" in docs
    assert "Guide library" in guides
    assert "Manual library" in manuals
    assert "Manual taxonomy" not in manuals
    assert "Runtime payload diagram" in reference
    assert "assets/diagrams/runtime-payload.svg" in reference
    assert "reference/manuals/user-manual/" in manuals

    for html, category in (
        (guides, "GUIDE"),
        (manuals, "MANUAL"),
        (reference, "REFERENCE"),
    ):
        labels = set(re.findall(r'<span class="route-id">([^<]+)</span>', html))
        assert labels == {category}


def test_generated_articles_render_ordered_lists_and_category_routing():
    guide = (
        PUBLIC
        / "reference"
        / "manuals"
        / "auto-prompts-and-conditional-routing-guide"
        / "index.html"
    ).read_text(encoding="utf-8")
    styles = (PUBLIC / "styles.css").read_text(encoding="utf-8")

    assert "<ol>" in guide
    assert "<li>freeze a machine-readable skill requirement" in guide
    assert "All guides" in guide
    assert 'class="active" href="/mission-directives/guides.html"' in guide
    assert 'aria-label="Documentation routing" class="page-nav"' in guide
    assert 'class="footer__inner"' in guide
    assert ".manual-body ol" in styles
    assert "grid-template-columns: repeat(2, minmax(0, 1fr));" in styles


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
        "getting-started.html",
        "installation.html",
        "contributing.html",
        "guides.html",
        "manuals.html",
        "reference.html",
        "reference/manuals",
        "visualAsset",
        "technical-map",
        "copyFile",
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
        "node_modules/",
        "site/dist/",
        "site/.astro/",
        "prompt_imports/",
        "infographics/",
        ".env.*",
        ".idea/",
        ".vscode/",
        "*.tmp",
        ".prompt_suite/",
    ):
        assert entry in ignored
