# Skill Installation and Integration Guide

Install **only the exact skill needed**. Every command below uses the per-skill form; it does not install the full repository. Review the current source and audit results before installation.

```bash
# General form
npx skills add https://github.com/OWNER/REPOSITORY --skill EXACT-SKILL-ID
```

## Curated installable skills

| Skill | Purpose | Exact install command | Trust note |
|---|---|---|---|
| `ai-research-explore` | Explore AI research questions and reproduction paths. | `npx skills add https://github.com/lllllllama/rigorpilot-skills --skill ai-research-explore` | Skills.sh listing showed multiple warnings; install only after review. |
| `analytics-tracking` | Marketing adapter for analytics tracking. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill analytics-tracking` | Review current skills.sh audit before installation. |
| `autoplan` | Planning, specification, checkpointing, and staged execution. | `npx skills add https://github.com/garrytan/gstack --skill autoplan` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `benchmark` | Performance or model benchmarking, tuning plans, and evidence comparison. | `npx skills add https://github.com/garrytan/gstack --skill benchmark` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `benchmark-models` | Performance or model benchmarking, tuning plans, and evidence comparison. | `npx skills add https://github.com/garrytan/gstack --skill benchmark-models` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `bolder` | Increase visual distinction and expressive hierarchy without losing usability. | `npx skills add https://github.com/pbakaus/impeccable --skill bolder` | Inspect current skills.sh audit before use. |
| `boost-prompt` | Expand and strengthen prompts with missing constraints, context, and output details. | `npx skills add https://github.com/github/awesome-copilot --skill boost-prompt` | Operator supplied the exact listing; inspect current repository and audits before installation. |
| `brandkit` | Create or apply a coherent brand kit to documents and digital artifacts. | `npx skills add https://github.com/anthropics/skills --skill brandkit` | Inspect current skills.sh audit before use. |
| `browse` | Browser-assisted inspection and controlled web workflow support. | `npx skills add https://github.com/garrytan/gstack --skill browse` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `canary` | Specialized agent, security, skill, or gstack lifecycle support. | `npx skills add https://github.com/garrytan/gstack --skill canary` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `canvas-design` | Compose static layouts, infographics, boards, and publication graphics without generative-image dependency. | `npx skills add https://github.com/anthropics/skills --skill canvas-design` | Inspect current skills.sh audit before use. |
| `careful` | Independent change review, risk challenge, and defensive validation. | `npx skills add https://github.com/garrytan/gstack --skill careful` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `checkpoint` | Planning, specification, checkpointing, and staged execution. | `npx skills add https://github.com/garrytan/gstack --skill checkpoint` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `codex` | Specialized agent, security, skill, or gstack lifecycle support. | `npx skills add https://github.com/garrytan/gstack --skill codex` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `colorize` | Refine or introduce purposeful color systems. | `npx skills add https://github.com/pbakaus/impeccable --skill colorize` | Inspect current skills.sh audit before use. |
| `competitor-alternatives` | Marketing adapter for competitor alternatives. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill competitor-alternatives` | Review current skills.sh audit before installation. |
| `connect-chrome` | Browser-assisted inspection and controlled web workflow support. | `npx skills add https://github.com/garrytan/gstack --skill connect-chrome` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `content-creator` | Marketing adapter for content creator. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill content-creator` | Review current skills.sh audit before installation. |
| `content-strategy` | Marketing adapter for content strategy. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill content-strategy` | Review current skills.sh audit before installation. |
| `context-restore` | Execution-state and context preservation controls. | `npx skills add https://github.com/garrytan/gstack --skill context-restore` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `context-save` | Execution-state and context preservation controls. | `npx skills add https://github.com/garrytan/gstack --skill context-save` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `copywriting` | Marketing adapter for copywriting. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill copywriting` | Review current skills.sh audit before installation. |
| `critique` | Critique visual hierarchy, interaction, usability, and consistency. | `npx skills add https://github.com/pbakaus/impeccable --skill critique` | Skills.sh listing showed at least one warning at research time; use sandboxed and review output. |
| `cso` | Specialized agent, security, skill, or gstack lifecycle support. | `npx skills add https://github.com/garrytan/gstack --skill cso` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `debug` | Evidence-led investigation and debugging. | `npx skills add https://github.com/garrytan/gstack --skill debug` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `delight` | Add purposeful interaction delight and detail. | `npx skills add https://github.com/pbakaus/impeccable --skill delight` | Inspect current skills.sh audit before use. |
| `design-consultation` | Design critique and consultation for hierarchy, usability, coherence, and product quality. | `npx skills add https://github.com/garrytan/gstack --skill design-consultation` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `design-html` | Design exploration, HTML visual production, and diagramming. | `npx skills add https://github.com/garrytan/gstack --skill design-html` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `design-review` | Design critique and consultation for hierarchy, usability, coherence, and product quality. | `npx skills add https://github.com/garrytan/gstack --skill design-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `design-shotgun` | Design exploration, HTML visual production, and diagramming. | `npx skills add https://github.com/garrytan/gstack --skill design-shotgun` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `design-taste-frontend` | Improve frontend visual taste, hierarchy, composition, and interaction polish. | `npx skills add https://github.com/leonxlnx/taste-skill --skill design-taste-frontend` | Inspect current skills.sh audit before use. |
| `devex-review` | Developer-experience review and improvement. | `npx skills add https://github.com/garrytan/gstack --skill devex-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `diagram` | Design exploration, HTML visual production, and diagramming. | `npx skills add https://github.com/garrytan/gstack --skill diagram` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `dispatching-parallel-agents` | Engineering workflow adapter for dispatching parallel agents. | `npx skills add https://github.com/obra/superpowers --skill dispatching-parallel-agents` | Review current skills.sh audit before installation. |
| `distill` | Remove unnecessary visual and interaction complexity. | `npx skills add https://github.com/pbakaus/impeccable --skill distill` | Inspect current skills.sh audit before use. |
| `document-generate` | Report, document, PDF, or landing-page reporting production. | `npx skills add https://github.com/garrytan/gstack --skill document-generate` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `document-release` | Release preparation, deployment, release documentation, and verification. | `npx skills add https://github.com/garrytan/gstack --skill document-release` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `docx` | Create and edit professional Word documents. | `npx skills add https://github.com/anthropics/skills --skill docx` | Skills.sh listing showed passing audits at research time. |
| `edit-article` | Edit research-backed prose for structure, evidence, clarity, and voice. | `npx skills add https://github.com/mattpocock/skills --skill edit-article` | Skills.sh listing showed passing audits at research time. |
| `email-sequence` | Marketing adapter for email sequence. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill email-sequence` | Review current skills.sh audit before installation. |
| `emil-design-eng` | Bridge design intent and frontend engineering implementation. | `npx skills add https://github.com/anthropics/skills --skill emil-design-eng` | Inspect current skills.sh audit before use. |
| `enhance-prompt` | Enhance terse or underspecified prompts into clearer design and production instructions. | `npx skills add https://github.com/google-labs-code/stitch-skills --skill enhance-prompt` | Operator supplied the exact listing; inspect current repository and audits before installation. |
| `executing-plans` | Engineering workflow adapter for executing plans. | `npx skills add https://github.com/obra/superpowers --skill executing-plans` | Review current skills.sh audit before installation. |
| `extract-design-system` | Extract reusable tokens, components, and patterns from an existing interface. | `npx skills add https://github.com/arvindrk/extract-design-system --skill extract-design-system` | Inspect current skills.sh audit before use. |
| `find-skills` | Discover task-fit skills without installing broad repositories. | `npx skills add https://github.com/vercel-labs/skills --skill find-skills` | Review current skills.sh audit before installation. |
| `freeze` | Execution-state and context preservation controls. | `npx skills add https://github.com/garrytan/gstack --skill freeze` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `frontend-design` | Create distinctive production-grade frontend layouts and interfaces. | `npx skills add https://github.com/anthropics/skills --skill frontend-design` | Skills.sh listing showed passing audits at research time. |
| `gstack` | Specialized agent, security, skill, or gstack lifecycle support. | `npx skills add https://github.com/garrytan/gstack --skill gstack` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `gstack-openclaw-ceo-review` | CEO-level plan review for strategy, customer value, priorities, and organizational coherence. | `npx skills add https://github.com/garrytan/gstack --skill gstack-openclaw-ceo-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `gstack-openclaw-investigate` | Evidence-led investigation and debugging. | `npx skills add https://github.com/garrytan/gstack --skill gstack-openclaw-investigate` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `gstack-openclaw-office-hours` | Founder-style problem framing, strategic challenge, and decision sharpening. | `npx skills add https://github.com/garrytan/gstack --skill gstack-openclaw-office-hours` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `gstack-openclaw-retro` | Retrospective and durable learning capture. | `npx skills add https://github.com/garrytan/gstack --skill gstack-openclaw-retro` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `gstack-upgrade` | Specialized agent, security, skill, or gstack lifecycle support. | `npx skills add https://github.com/garrytan/gstack --skill gstack-upgrade` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `guard` | Independent change review, risk challenge, and defensive validation. | `npx skills add https://github.com/garrytan/gstack --skill guard` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `hackernews-frontpage` | Public-web retrieval for authorized research with provenance checks. | `npx skills add https://github.com/garrytan/gstack --skill hackernews-frontpage` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `health` | Task-specific gstack workflow adapter. | `npx skills add https://github.com/garrytan/gstack --skill health` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `high-end-visual-design` | Develop high-end visual systems for interfaces and digital artifacts. | `npx skills add https://github.com/xuanwo/claude-code-designer --skill high-end-visual-design` | Inspect current skills.sh audit before use. |
| `industrial-brutalist-ui` | Create controlled industrial or brutalist interface directions. | `npx skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill industrial-brutalist-ui` | Inspect current skills.sh audit before use. |
| `investigate` | Evidence-led investigation and debugging. | `npx skills add https://github.com/garrytan/gstack --skill investigate` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `ios-clean` | iOS-specific design, repair, cleanup, synchronization, or QA. | `npx skills add https://github.com/garrytan/gstack --skill ios-clean` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `ios-design-review` | Design critique and consultation for hierarchy, usability, coherence, and product quality. | `npx skills add https://github.com/garrytan/gstack --skill ios-design-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `ios-fix` | iOS-specific design, repair, cleanup, synchronization, or QA. | `npx skills add https://github.com/garrytan/gstack --skill ios-fix` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `ios-qa` | Structured quality assurance and issue evidence collection. | `npx skills add https://github.com/garrytan/gstack --skill ios-qa` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `ios-sync` | iOS-specific design, repair, cleanup, synchronization, or QA. | `npx skills add https://github.com/garrytan/gstack --skill ios-sync` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `land-and-deploy` | Release preparation, deployment, release documentation, and verification. | `npx skills add https://github.com/garrytan/gstack --skill land-and-deploy` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `landing-report` | Report, document, PDF, or landing-page reporting production. | `npx skills add https://github.com/garrytan/gstack --skill landing-report` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `launch-strategy` | Marketing adapter for launch strategy. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill launch-strategy` | Review current skills.sh audit before installation. |
| `learn` | Knowledge capture, learning, and memory synchronization. | `npx skills add https://github.com/garrytan/gstack --skill learn` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `make-pdf` | Report, document, PDF, or landing-page reporting production. | `npx skills add https://github.com/garrytan/gstack --skill make-pdf` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `marketing-psychology` | Marketing adapter for marketing psychology. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill marketing-psychology` | Review current skills.sh audit before installation. |
| `minimalist-ui` | Create restrained minimalist interface systems. | `npx skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill minimalist-ui` | Inspect current skills.sh audit before use. |
| `office-hours` | Founder-style problem framing, strategic challenge, and decision sharpening. | `npx skills add https://github.com/garrytan/gstack --skill office-hours` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `open-gstack-browser` | Browser-assisted inspection and controlled web workflow support. | `npx skills add https://github.com/garrytan/gstack --skill open-gstack-browser` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `optimize` | Optimize an existing design for clarity and effectiveness. | `npx skills add https://github.com/pbakaus/impeccable --skill optimize` | Inspect current skills.sh audit before use. |
| `page-cro` | Marketing adapter for page cro. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill page-cro` | Review current skills.sh audit before installation. |
| `paid-ads` | Marketing adapter for paid ads. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill paid-ads` | Review current skills.sh audit before installation. |
| `pair-agent` | Specialized agent, security, skill, or gstack lifecycle support. | `npx skills add https://github.com/garrytan/gstack --skill pair-agent` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `paper-context-resolver` | Resolve an academic paper, repository, assets, and implementation context. | `npx skills add https://github.com/lllllllama/ai-paper-reproduction-skill --skill paper-context-resolver` | Skills.sh listing showed mixed audits; inspect and sandbox before use. |
| `plan-ceo-review` | CEO-level plan review for strategy, customer value, priorities, and organizational coherence. | `npx skills add https://github.com/garrytan/gstack --skill plan-ceo-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `plan-design-review` | Design critique and consultation for hierarchy, usability, coherence, and product quality. | `npx skills add https://github.com/garrytan/gstack --skill plan-design-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `plan-devex-review` | Developer-experience review and improvement. | `npx skills add https://github.com/garrytan/gstack --skill plan-devex-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `plan-eng-review` | Engineering plan review for architecture, implementation risk, testing, and operability. | `npx skills add https://github.com/garrytan/gstack --skill plan-eng-review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `plan-tune` | Performance or model benchmarking, tuning plans, and evidence comparison. | `npx skills add https://github.com/garrytan/gstack --skill plan-tune` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `playwright-best-practices` | Apply Playwright testing patterns and reliability practices. | `npx skills add https://github.com/currents-dev/playwright-best-practices-skill --skill playwright-best-practices` | Review current skills.sh audit before installation. |
| `playwright-cli` | Run browser automation and inspection through Playwright CLI. | `npx skills add https://github.com/microsoft/playwright-cli --skill playwright-cli` | Review current skills.sh audit before installation. |
| `polish` | Perform final interface and visual polish. | `npx skills add https://github.com/pbakaus/impeccable --skill polish` | Skills.sh listing showed passing audits at research time. |
| `pptx` | Create and edit presentation files with structured slide production. | `npx skills add https://github.com/anthropics/skills --skill pptx` | Skills.sh listing showed passing audits at research time. |
| `pricing-strategy` | Marketing adapter for pricing strategy. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill pricing-strategy` | Review current skills.sh audit before installation. |
| `programmatic-seo` | Marketing adapter for programmatic seo. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill programmatic-seo` | Review current skills.sh audit before installation. |
| `prompt-builder` | Build structured production-ready prompts from a clarified task and output contract. | `npx skills add https://github.com/github/awesome-copilot --skill prompt-builder` | Skills.sh listing showed passing audits at research time. |
| `prompt-engineering-patterns` | Apply reusable prompt patterns, structured reasoning, chaining, evaluation, and tool-use designs. | `npx skills add https://github.com/wshobson/agents --skill prompt-engineering-patterns` | Skills.sh listing showed passing audits at research time. |
| `prompt-optimizer` | Optimize prompts for clarity, context efficiency, robust outputs, and model-aware operation. | `npx skills add https://github.com/affaan-m/everything-claude-code --skill prompt-optimizer` | Skills.sh listing showed passing audits at research time. |
| `qa` | Structured quality assurance and issue evidence collection. | `npx skills add https://github.com/garrytan/gstack --skill qa` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `qa-only` | Structured quality assurance and issue evidence collection. | `npx skills add https://github.com/garrytan/gstack --skill qa-only` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `quieter` | Reduce excessive visual intensity while preserving hierarchy. | `npx skills add https://github.com/pbakaus/impeccable --skill quieter` | Inspect current skills.sh audit before use. |
| `receiving-code-review` | Engineering workflow adapter for receiving code review. | `npx skills add https://github.com/obra/superpowers --skill receiving-code-review` | Review current skills.sh audit before installation. |
| `redesign-existing-projects` | Redesign existing interfaces while preserving functional requirements. | `npx skills add https://github.com/anthropics/skills --skill redesign-existing-projects` | Inspect current skills.sh audit before use. |
| `requesting-code-review` | Engineering workflow adapter for requesting code review. | `npx skills add https://github.com/obra/superpowers --skill requesting-code-review` | Review current skills.sh audit before installation. |
| `research` | Conduct structured research with source tracking and synthesis. | `npx skills add https://github.com/mattpocock/skills --skill research` | Skills.sh listing showed passing audits at research time. |
| `retro` | Retrospective and durable learning capture. | `npx skills add https://github.com/garrytan/gstack --skill retro` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `review` | Independent change review, risk challenge, and defensive validation. | `npx skills add https://github.com/garrytan/gstack --skill review` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `schema-markup` | Marketing adapter for schema markup. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill schema-markup` | Review current skills.sh audit before installation. |
| `scrape` | Public-web retrieval for authorized research with provenance checks. | `npx skills add https://github.com/garrytan/gstack --skill scrape` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `seo-audit` | Marketing adapter for seo audit. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill seo-audit` | Review current skills.sh audit before installation. |
| `setup-browser-cookies` | Browser-assisted inspection and controlled web workflow support. | `npx skills add https://github.com/garrytan/gstack --skill setup-browser-cookies` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `setup-deploy` | Release preparation, deployment, release documentation, and verification. | `npx skills add https://github.com/garrytan/gstack --skill setup-deploy` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `setup-gbrain` | Knowledge capture, learning, and memory synchronization. | `npx skills add https://github.com/garrytan/gstack --skill setup-gbrain` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `ship` | Release preparation, deployment, release documentation, and verification. | `npx skills add https://github.com/garrytan/gstack --skill ship` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `site-architecture` | Marketing adapter for site architecture. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill site-architecture` | Review current skills.sh audit before installation. |
| `skill-creator` | Create and evaluate a narrowly scoped reusable skill. | `npx skills add https://github.com/anthropics/skills --skill skill-creator` | Review current skills.sh audit before installation. |
| `skillify` | Specialized agent, security, skill, or gstack lifecycle support. | `npx skills add https://github.com/garrytan/gstack --skill skillify` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `social-content` | Marketing adapter for social content. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill social-content` | Review current skills.sh audit before installation. |
| `social-media` | Marketing adapter for social media. | `npx skills add https://github.com/coreyhaines31/marketingskills --skill social-media` | Review current skills.sh audit before installation. |
| `spec` | Planning, specification, checkpointing, and staged execution. | `npx skills add https://github.com/garrytan/gstack --skill spec` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `stitch-design-taste` | Improve Stitch-oriented design prompts and interface quality. | `npx skills add https://github.com/google-labs-code/stitch-skills --skill stitch-design-taste` | Inspect current skills.sh audit before use. |
| `sync-gbrain` | Knowledge capture, learning, and memory synchronization. | `npx skills add https://github.com/garrytan/gstack --skill sync-gbrain` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `systematic-debugging` | Engineering workflow adapter for systematic debugging. | `npx skills add https://github.com/obra/superpowers --skill systematic-debugging` | Review current skills.sh audit before installation. |
| `test-driven-development` | Engineering workflow adapter for test driven development. | `npx skills add https://github.com/obra/superpowers --skill test-driven-development` | Review current skills.sh audit before installation. |
| `ui-ux-pro-max` | Apply comprehensive UI/UX planning, style, component, and responsive design guidance. | `npx skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max` | Inspect current skills.sh audit before use. |
| `unfreeze` | Execution-state and context preservation controls. | `npx skills add https://github.com/garrytan/gstack --skill unfreeze` | Skills.sh showed repository-level mixed audit results; inspect the exact skill and run least-privileged before use. |
| `using-git-worktrees` | Engineering workflow adapter for using git worktrees. | `npx skills add https://github.com/obra/superpowers --skill using-git-worktrees` | Review current skills.sh audit before installation. |
| `vercel-composition-patterns` | Use scalable React composition patterns for design-system and frontend architecture. | `npx skills add https://github.com/vercel-labs/agent-skills --skill vercel-composition-patterns` | Inspect current skills.sh audit before use. |
| `verification-before-completion` | Engineering workflow adapter for verification before completion. | `npx skills add https://github.com/obra/superpowers --skill verification-before-completion` | Review current skills.sh audit before installation. |
| `web-artifacts-builder` | Build self-contained interactive web artifacts and explainers. | `npx skills add https://github.com/anthropics/skills --skill web-artifacts-builder` | Inspect current skills.sh audit before use. |
| `web-design-guidelines` | Review web interfaces against established design and usability guidelines. | `npx skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines` | Skills.sh listing showed at least one warning at research time; use sandboxed and review output. |
| `webapp-testing` | Test web applications with realistic browser workflows. | `npx skills add https://github.com/anthropics/skills --skill webapp-testing` | Review current skills.sh audit before installation. |
| `writing-plans` | Engineering workflow adapter for writing plans. | `npx skills add https://github.com/obra/superpowers --skill writing-plans` | Review current skills.sh audit before installation. |
| `xlsx` | Create and edit spreadsheets and analytical models. | `npx skills add https://github.com/anthropics/skills --skill xlsx` | Skills.sh listing showed passing audits at research time. |

## Runtime aliases without a verified exact skills.sh listing

These are intentionally **not** assigned fabricated commands. The router resolves them through native suite prompts and installed supporting skills.

| Alias | Native route | Note |
|---|---|---|
| `academic-paper-reviewer` | MD-82, MD-129 | No exact verified skills.sh listing was found during research; do not invent an install command. |
| `academic-researcher` | MD-79, MD-80, MD-87 | No exact verified skills.sh listing was found during research; do not invent an install command. |
| `blueprinter` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `brand-guidelines` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `dashboard-builder` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `design-taste-frontend-v1` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `excalidraw-diagram-generator` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `frontend-slides` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `html-ppt` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `html-svg-diagrams` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `impeccable` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |
| `stop-slop` | native prompt route | Runtime-provided alias; probe the installed schema and provenance. |

## Installation policy

1. Inspect the exact skill page and repository.
2. Record commit or release provenance.
3. Review requested permissions and external effects.
4. Install into an isolated environment first.
5. Run conformance fixtures before project use.
6. Pin the accepted revision where the runtime supports it.
7. Remove or quarantine skills that drift, fail evaluation, or request excessive access.

## User-owned local skills

`visual-assets` and `strudel` are already present in the supplied OpenCode inventory. They have no fabricated external installation command. The canonical alias `strudle` resolves to `strudel`. Use `tools/install_skill_dual.ps1` or copy a reviewed local skill directory to register it in both global locations.

## Installed personal skills

`visual-assets` and `strudel` were observed in the supplied OpenCode global directory. They have no fabricated external installation command. `strudle` is accepted only as a spelling alias for `strudel`.

Newly created local skills are staged and then copied to both global locations with:

```powershell
.\tools\register_local_skill_dual.ps1 -SourceDirectory ".\staging\my-skill" -SkillId "my-skill"
```

Qualified third-party skills use `tools/install_skill_dual.ps1`. The default `locked_auto` mode requires a resolved approved lock; `approved_unpinned` requires explicit risk acceptance.
