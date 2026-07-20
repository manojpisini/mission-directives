# Recommended Skill Stacks

These are the highest-value default stacks for this suite. Install only the exact skills needed for the current workflow, review the current source and audits, and keep native prompt execution as the fallback.

## Prompt engineering core

```bash
npx skills add https://github.com/github/awesome-copilot --skill prompt-builder
npx skills add https://github.com/wshobson/agents --skill prompt-engineering-patterns
npx skills add https://github.com/google-labs-code/stitch-skills --skill enhance-prompt
npx skills add https://github.com/affaan-m/everything-claude-code --skill prompt-optimizer
npx skills add https://github.com/github/awesome-copilot --skill boost-prompt
```

Use with `MD-165` through `MD-168` and `MD-178`. Do not accept optimization claims without representative fixtures.

## Academic research and review

```bash
npx skills add https://github.com/mattpocock/skills --skill research
npx skills add https://github.com/mattpocock/skills --skill edit-article
npx skills add https://github.com/lllllllama/ai-paper-reproduction-skill --skill paper-context-resolver
npx skills add https://github.com/anthropics/skills --skill docx
```

Use with `MD-79`, `MD-80`, `MD-82`, `MD-87`, `MD-88`, and `MD-129`. `academic-researcher` and `academic-paper-reviewer` are native aliases rather than invented installable packages.

## Reports and executive artifacts

```bash
npx skills add https://github.com/garrytan/gstack --skill document-generate
npx skills add https://github.com/garrytan/gstack --skill make-pdf
npx skills add https://github.com/anthropics/skills --skill docx
npx skills add https://github.com/anthropics/skills --skill pptx
npx skills add https://github.com/anthropics/skills --skill xlsx
npx skills add https://github.com/mattpocock/skills --skill edit-article
```

Use with `MD-159`, `MD-169`, and `MD-170`. Verify source numbers, exhibit consistency, accessibility, and exact exports.

## Design and frontend core

```bash
npx skills add https://github.com/anthropics/skills --skill frontend-design
npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines
npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-composition-patterns
npx skills add https://github.com/leonxlnx/taste-skill --skill design-taste-frontend
npx skills add https://github.com/pbakaus/impeccable --skill critique
npx skills add https://github.com/pbakaus/impeccable --skill polish
npx skills add https://github.com/arvindrk/extract-design-system --skill extract-design-system
npx skills add https://github.com/anthropics/skills --skill web-artifacts-builder
```

Use for language-model-driven interfaces, layouts, components, web artifacts, and design systems. Image generation is not included.

## Presentation and visual communication

```bash
npx skills add https://github.com/garrytan/gstack --skill design-html
npx skills add https://github.com/garrytan/gstack --skill diagram
npx skills add https://github.com/anthropics/skills --skill pptx
npx skills add https://github.com/anthropics/skills --skill canvas-design
npx skills add https://github.com/pbakaus/impeccable --skill polish
```

Use with `MD-101` through `MD-109` and `MD-170`. Review exact exports, data integrity, keyboard access, text alternatives, and responsive behavior.

## Engineering delivery and QA

```bash
npx skills add https://github.com/garrytan/gstack --skill spec
npx skills add https://github.com/garrytan/gstack --skill plan-eng-review
npx skills add https://github.com/garrytan/gstack --skill review
npx skills add https://github.com/garrytan/gstack --skill qa
npx skills add https://github.com/obra/superpowers --skill test-driven-development
npx skills add https://github.com/obra/superpowers --skill verification-before-completion
npx skills add https://github.com/obra/superpowers --skill systematic-debugging
npx skills add https://github.com/microsoft/playwright-cli --skill playwright-cli
```

Use with `MD-124` and existing engineering, debugging, testing, delivery, and release prompts. Shipping and deployment remain `APPLY_APPROVED` actions.

## Strategy and organization

```bash
npx skills add https://github.com/garrytan/gstack --skill office-hours
npx skills add https://github.com/garrytan/gstack --skill plan-ceo-review
npx skills add https://github.com/garrytan/gstack --skill autoplan
npx skills add https://github.com/garrytan/gstack --skill retro
npx skills add https://github.com/garrytan/gstack --skill document-generate
```

Use for problem framing, corporate or product strategy, operating models, department plans, decisions, and retrospectives.

## Research and OSINT

```bash
npx skills add https://github.com/mattpocock/skills --skill research
npx skills add https://github.com/garrytan/gstack --skill investigate
npx skills add https://github.com/garrytan/gstack --skill scrape
npx skills add https://github.com/garrytan/gstack --skill document-generate
```

Use only for authorized public-source research. Preserve provenance, collection time, identity confidence, contradictions, privacy minimization, and non-deceptive collection.

## Marketing and content

```bash
npx skills add https://github.com/coreyhaines31/marketingskills --skill content-strategy
npx skills add https://github.com/coreyhaines31/marketingskills --skill seo-audit
npx skills add https://github.com/coreyhaines31/marketingskills --skill site-architecture
npx skills add https://github.com/coreyhaines31/marketingskills --skill copywriting
npx skills add https://github.com/coreyhaines31/marketingskills --skill social-content
npx skills add https://github.com/coreyhaines31/marketingskills --skill analytics-tracking
```

Use with source truth, brand, accessibility, privacy, and anti-spam controls. Search optimization may not override audience usefulness or factual integrity.

## Skill discovery and creation

```bash
npx skills add https://github.com/vercel-labs/skills --skill find-skills
npx skills add https://github.com/anthropics/skills --skill skill-creator
npx skills add https://github.com/garrytan/gstack --skill skillify
```

Use only after confirming that native prompt composition cannot meet the need cleanly. New skills require a narrow contract, permissions declaration, fixtures, adversarial cases, and conformance validation.


## Conditional skill orchestration

Installed local skills: `find-skills`, `skill-creator`, `brainstorming`, `grill-me`, `grill-with-docs`, `writing-skills`, `visual-assets`, and `strudel`. Use them through `MD-191` through `MD-198`; do not install or execute a skill simply because it is present.

## Code-native visual assets

Use the personal `visual-assets` skill for SVG, HTML, CSS, vanilla-JS illustrations, infographics, report exhibits, presentation assets, and animated explanatory graphics. It is a code-native visual-production route, not model image generation.

## Music code

Use the personal `strudel` skill for Strudel composition and live-coding music programs. The misspelling `strudle` is retained only as an alias.

## Personal code-native creative skills

These skills are already present in the supplied OpenCode inventory and do not use external install commands:

```text
visual-assets
strudel
```

Use `visual-assets` through `MD-192` and `MD-196` for a genuine need for custom SVG, HTML, CSS, or vanilla-JavaScript infographics, illustrations, vector systems, report exhibits, presentation assets, mock assets, or accessible animation. Use `MD-197` only for a finite asset queue or measurable refinement loop, with `MD-198` deciding every continuation.

Use `strudel` through the same generic adapter for Strudel music code, patterns, and arrangements. Neither skill is invoked merely because it is installed.
