# Documentation Site Guide

## Purpose

The Astro/Starlight site publishes the complete public documentation surface at `https://manojpisini.github.io/mission-directives/`. The source lives under `site/`.

## Architecture

Authored pages explain the main workflows. `site/scripts/generate-reference.mjs` creates the reference surface from canonical repository data before every development run and build:

- prompt pages from `catalog.json` and `prompts/`;
- scenario pages from `SCENARIO_CATALOG.json`;
- skill pages from `skill_registry.json`;
- manual mirrors from `docs/`, excluding internal implementation plans.

Generated pages live under `site/src/content/docs/reference/`. They are ignored by Git and the sealed manifest. Never edit them directly.

Starlight provides navigation, accessible documentation layouts, dark mode, and Pagefind search. The site uses Astro's project-page base path `/mission-directives`.

## Local development

```bash
cd site
npm ci
npm run dev
```

Production verification:

```bash
npm run generate
npm run build
npm run preview
```

The build must report the expected prompt, scenario, skill, and manual counts and complete the Pagefind index.

## Publishing

`.github/workflows/deploy-docs.yml` builds with `withastro/action` and deploys with `actions/deploy-pages` after a push to `main` that changes site or canonical documentation inputs. The workflow can also be run manually.

In repository settings, set Pages source to **GitHub Actions**. The public URL will not update until the workflow is pushed and completes successfully.

## Content ownership

| Content | Edit |
| --- | --- |
| Prompt identity or metadata | `catalog.json` through the governed prompt workflow |
| Prompt body | canonical file under `prompts/` |
| Scenario | `SCENARIO_CATALOG.json` through its generator/authoring workflow |
| Skill route | `skill_registry.json` |
| Full manual | `docs/*.md` |
| Site learning path | `site/src/content/docs/guides/` |
| Navigation and deployment base | `site/astro.config.mjs` |
| Visual system | `site/src/styles/custom.css` |

## Branding handoff

The initial visual system is intentionally restrained. Replace the favicon, typography, color tokens, and title treatment in `site/public/`, `site/src/styles/custom.css`, and `site/astro.config.mjs`. Keep focus visibility, responsive tables, reduced-motion behavior, contrast, and project-page base paths intact.

## Validation

The source repository must keep `site/node_modules/`, `site/dist/`, `site/.astro/`, and generated references outside the manifest. `site/package-lock.json`, configuration, authored content, generator, styles, and workflow remain sealed release inputs.
