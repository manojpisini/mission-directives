import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://manojpisini.github.io',
  base: '/mission-directives',
  integrations: [
    starlight({
      title: 'Mission Directives',
      description:
        'Deterministic routing, execution contracts, and evidence-driven prompt operations.',
      customCss: ['./src/styles/custom.css'],
      favicon: '/favicon.svg',
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/manojpisini/mission-directives',
        },
      ],
      editLink: {
        baseUrl: 'https://github.com/manojpisini/mission-directives/edit/main/site/',
      },
      lastUpdated: true,
      pagination: true,
      sidebar: [
        {
          label: 'Start Here',
          items: [
            { label: 'Mission Directives', link: '/' },
            { label: 'Quick Start', link: '/guides/quick-start/' },
            { label: 'Route and Score', link: '/guides/routing/' },
            { label: 'Install Runtime', link: '/guides/runtime-install/' },
          ],
        },
        {
          label: 'Operate',
          items: [
            { label: 'Invocation and Planning', link: '/guides/invocation/' },
            { label: 'Scenarios and Graphs', link: '/guides/scenarios/' },
            { label: 'Identity and Compatibility', link: '/guides/identity/' },
            { label: 'Safety and Authorization', link: '/guides/safety/' },
            { label: 'Operator Recipes', link: '/guides/recipes/' },
            { label: 'Troubleshooting', link: '/guides/troubleshooting/' },
          ],
        },
        {
          label: 'Generated Reference',
          items: [
            { label: 'Reference Overview', link: '/reference/' },
            { label: 'Prompt Catalog', link: '/reference/prompts/' },
            { label: 'Scenario Catalog', link: '/reference/scenarios/' },
            { label: 'Skill Registry', link: '/reference/skills/' },
            { label: 'Repository Manuals', link: '/reference/manuals/' },
          ],
        },
      ],
    }),
  ],
});