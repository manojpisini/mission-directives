# Documentation Site Guide

## Purpose

The static Astro site publishes the public documentation surface at `https://manojpisini.github.io/mission-directives/`. The source lives under `site/` and uses the checked-in HTML, CSS, and JavaScript shell for the landing page, onboarding pages, sectioned documentation hub, guide index, manual library, reference index, and generated manual pages.

## Architecture

`site/scripts/generate-reference.mjs` runs before development and production builds. It reads every root `docs/*.md` file, classifies each page as a manual, guide, or reference page, renders per-manual HTML under `site/public/reference/manuals/`, and emits the section pages that make the site navigable without one long documentation scroll.

The public site includes:

- `site/src/pages/index.astro` for the landing page shell;
- `site/public/getting-started.html` generated from `docs/GETTING_STARTED.md`;
- `site/public/installation.html` generated from `docs/INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md`;
- `site/public/contributing.html` generated from the root `CONTRIBUTING.md`;
- `site/public/docs.html` for the documentation overview and visual system explanation;
- `site/public/guides.html` for task-oriented guides;
- `site/public/manuals.html` for the complete generated manual library;
- `site/public/reference.html` for runtime markers, payload boundaries, and reference contracts;
- generated manual pages under `site/public/reference/manuals/`;
- `site/public/assets/diagrams/` and `site/public/assets/infographics/` for editable technical depictions and overview visuals;
- `site/public/assets/brand/` for generated copies of canonical brand SVGs;
- `site/public/styles.css` and `site/public/app.js` for the light-mode visual system and interactions.

Astro provides the build and GitHub Pages base path. The shell owns navigation, page-local search, copy buttons, tabs, sidebar behavior, centered manual reading layouts, responsive tables, and the light-mode sage-accented visual system.

## Local development

```bash
cd site
pnpm install --frozen-lockfile
pnpm run dev
```

Production verification:

```bash
pnpm install --frozen-lockfile
pnpm run generate
pnpm run build
pnpm run check
```

Run the frozen install even when `site/node_modules` already exists. Build and check commands can otherwise pass while a corrupted committed lockfile fails in GitHub's clean checkout. Release-version replacements must exclude `site/pnpm-lock.yaml`; update it only through pnpm dependency operations.

`pnpm run check` builds the site and verifies internal links across the generated HTML pages.

## Publishing

`.github/workflows/deploy-docs.yml` builds with `withastro/action` and deploys with `actions/deploy-pages` after a push to `main` that changes site or canonical documentation inputs. The workflow can also be run manually.

In repository settings, set Pages source to **GitHub Actions**. The public URL updates only after the workflow completes successfully.

## Content ownership

| Content | Edit |
| --- | --- |
| Landing page shell | `site/src/pages/index.astro` |
| Documentation section pages and manual generation | `site/scripts/generate-reference.mjs` |
| Manual source | `docs/*.md` |
| Getting started source | `docs/GETTING_STARTED.md` |
| Installation source | `docs/INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md` |
| Contributing source | `CONTRIBUTING.md` |
| Canonical brand assets | `assets/images/*.svg` |
| Visual system and reading layout | `site/public/styles.css` |
| Interactions | `site/public/app.js` |
| Static diagrams | `site/public/assets/diagrams/` |
| Static infographics used by the site | `site/public/assets/infographics/` |
| Navigation and deployment base | `site/astro.config.mjs` |

## Visual content

Use repository-safe SVG, PNG, or generated static assets under `site/public/assets/` when they are part of the public documentation site. Keep temporary or source-only experiments under a root `infographics/` folder; that folder is ignored and is not part of the release manifest.

## Branding

`assets/images/` is the canonical brand source. The generator copies the four logo and wordmark SVGs into `site/public/assets/brand/` and derives `site/public/favicon.svg` from `mission_directives_logo.svg`. Do not hand-edit generated brand copies. Update the canonical files, run `pnpm run generate`, and commit both source and generated outputs.

Keep focus visibility, responsive tables, reduced-motion behavior, contrast, copy buttons, tabs, mobile navigation, centered manual widths, and the `/mission-directives` base path intact when changing the visual shell.

## Validation

The repository keeps `site/node_modules/`, `site/dist/`, `site/.astro/`, `prompt_imports/`, and root `infographics/` outside the manifest. The site source, generated public documentation pages, lockfile, generator, public assets, and workflow remain sealed release inputs.
