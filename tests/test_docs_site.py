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
    assert "assets/brand/mission_directives_full_logo_lateral_dark.svg" in html
    assert "brand__mark" not in html


def test_site_uses_canonical_brand_assets_and_onboarding_pages():
    brand = PUBLIC / "assets" / "brand"
    for name in (
        "mission_directives_full_logo_dark.svg",
        "mission_directives_full_logo_lateral_dark.svg",
        "mission_directives_full_logo_lateral_light.svg",
        "mission_directives_full_logo_light.svg",
        "mission_directives_logo_dark.svg",
        "mission_directives_logo_light.svg",
        "mission_directives_wordmark_dark.svg",
        "mission_directives_wordmark_light.svg",
    ):
        assert (ROOT / "assets" / "images" / name).exists()
        assert (brand / name).exists()

    assert (PUBLIC / "favicon.svg").read_bytes() == (
        ROOT / "assets" / "images" / "mission_directives_logo_dark.svg"
    ).read_bytes()

    for name, heading in (
        ("getting-started.html", "Getting Started"),
        ("installation.html", "Installation"),
        ("contributing.html", "Contributing"),
    ):
        html = (PUBLIC / name).read_text(encoding="utf-8")
        assert heading in html
        assert "assets/brand/mission_directives_full_logo_lateral_dark.svg" in html
        assert "brand__mark" not in html

    contributing = (PUBLIC / "contributing.html").read_text(encoding="utf-8")
    assert "MEMORY.md" not in contributing
    assert "/reference/manuals/memory/" not in contributing

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "assets/images/mission_directives_full_logo_lateral_light.svg" in readme
    assert "assets/images/mission_directives_full_logo_lateral_dark.svg" in readme
    assert "assets/readme/mission-directives-banner.svg" not in readme


def test_landing_and_documentation_headers_share_navigation_vocabulary():
    landing = (SITE / "src" / "pages" / "index.astro").read_text(encoding="utf-8")
    docs = (PUBLIC / "docs.html").read_text(encoding="utf-8")
    links = (
        ("getting-started.html", "Start"),
        ("installation.html", "Install"),
        ("docs.html", "Docs"),
        ("contributing.html", "Contribute"),
        ("reference.html", "Reference"),
    )
    for target, label in links:
        assert f'href="{target}">{label}</a>' in landing
        assert f'href="/mission-directives/{target}">{label}</a>' in docs


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
        "site/node_modules/",
        "site/dist/",
        "site/.astro/",
        "prompt_imports/",
        "infographics/",
    ):
        assert entry in ignored
