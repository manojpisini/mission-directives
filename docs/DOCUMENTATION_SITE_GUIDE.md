# Documentation Site Guide

## Purpose

The static Astro site publishes the public documentation surface at `https://manojpisini.github.io/mission-directives/`. The source lives under `site/` and uses the checked-in HTML, CSS, and JavaScript shell for the landing and documentation pages.

## Architecture

`site/scripts/generate-reference.mjs` runs before development and production builds. It creates the static documentation page and mirrors every root `docs/*.md` manual into `site/public/reference/manuals/`.

The public site includes:

- `site/src/pages/index.astro` for the landing page shell;
- `site/public/docs.html` for the documentation hub;
- `site/public/styles.css` and `site/public/app.js` for the provided visual system and interactions;
- generated manual pages under `site/public/reference/manuals/`;
- static assets under `site/public/assets/`.

Astro provides the build and GitHub Pages base path. The site shell owns navigation, search dialog behavior, copy buttons, tabs, sidebar behavior, and the light-mode visual system.

## Local development

```bash
cd site
pnpm install --frozen-lockfile
pnpm run dev
```

Production verification:

```bash
pnpm run generate
pnpm run build
pnpm run check
```

`pnpm run check` builds the site and verifies internal links across the generated HTML pages.

## Publishing

`.github/workflows/deploy-docs.yml` builds with `withastro/action` and deploys with `actions/deploy-pages` after a push to `main` that changes site or canonical documentation inputs. The workflow can also be run manually.

In repository settings, set Pages source to **GitHub Actions**. The public URL updates only after the workflow completes successfully.

## Content ownership

| Content | Edit |
| --- | --- |
| Landing page shell | `site/src/pages/index.astro` |
| Documentation hub and manual generation | `site/scripts/generate-reference.mjs` |
| Manual source | `docs/*.md` |
| Visual system | `site/public/styles.css` |
| Interactions | `site/public/app.js` |
| Static diagrams and illustrations | `site/public/assets/` |
| Navigation and deployment base | `site/astro.config.mjs` |

## Branding handoff

The current visual system is light, minimal, and sage-accented. Replace branding assets under `site/public/` when final brand assets are ready. Keep focus visibility, responsive tables, reduced-motion behavior, contrast, copy buttons, tabs, mobile navigation, and the `/mission-directives` base path intact.

## Validation

The repository keeps `site/node_modules/`, `site/dist/`, and `site/.astro/` outside the manifest. The site source, generated public documentation pages, lockfile, generator, and workflow remain sealed release inputs.