import { cp, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = path.resolve(siteRoot, '..');
const docsRoot = path.join(siteRoot, 'src', 'content', 'docs');
const generatedRoot = path.join(docsRoot, 'reference');

const readJson = async (relative) =>
  JSON.parse(await readFile(path.join(repoRoot, relative), 'utf8'));

const clean = (value) => String(value ?? '').replaceAll('|', '\\|').replaceAll('\n', ' ');
const yaml = (value) => JSON.stringify(String(value ?? ''));

function frontmatter(title, description) {
  return [
    '---',
    `title: ${yaml(title)}`,
    `description: ${yaml(description)}`,
    'sidebar:',
    '  hidden: true',
    'editUrl: false',
    '---',
    '',
  ].join('\n');
}

function slug(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

function list(values) {
  if (!Array.isArray(values) || values.length === 0) return '_None declared._';
  return values.map((value) => `- \`${clean(value)}\``).join('\n');
}

function table(rows) {
  if (!rows.length) return '_No entries._';
  return [
    '| ID | Title | Type | Risk / Assurance |',
    '| --- | --- | --- | --- |',
    ...rows,
  ].join('\n');
}

async function write(relative, content) {
  const output = path.join(docsRoot, relative);
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, content.endsWith('\n') ? content : `${content}\n`, 'utf8');
}

async function walkMarkdown(root, prefix = '') {
  const files = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    if (entry.name === 'superpowers') continue;
    const relative = path.join(prefix, entry.name);
    const absolute = path.join(root, entry.name);
    if (entry.isDirectory()) files.push(...(await walkMarkdown(absolute, relative)));
    else if (entry.isFile() && entry.name.toLowerCase().endsWith('.md')) files.push(relative);
  }
  return files;
}

await rm(generatedRoot, { recursive: true, force: true });
await mkdir(generatedRoot, { recursive: true });

const catalog = await readJson('catalog.json');
const scenarios = await readJson('SCENARIO_CATALOG.json');
const skills = await readJson('skill_registry.json');
const prompts = catalog.prompts ?? [];
const promptByCanonicalPath = new Map(
  prompts.map((prompt) => [prompt.canonical_path.replaceAll('\\', '/'), prompt]),
);
const publicBase = '/mission-directives/';

function rewriteManualLinks(source, relative) {
  const relativePosix = relative.replaceAll('\\', '/');
  const sourceDirectory = path.posix.dirname(`docs/${relativePosix}`);
  return source.replace(/(\[[^\]]+\]\()([^)]+)(\))/g, (full, open, targetSpec, close) => {
    const trimmed = targetSpec.trim();
    if (
      !trimmed ||
      trimmed.startsWith('#') ||
      trimmed.startsWith('/') ||
      /^[a-z][a-z0-9+.-]*:/i.test(trimmed) ||
      /\s+["']/.test(trimmed)
    ) {
      return full;
    }

    const [target, ...fragmentParts] = trimmed.replace(/^<|>$/g, '').split('#');
    const fragment = fragmentParts.length ? `#${fragmentParts.join('#')}` : '';
    const repositoryTarget = path.posix.normalize(path.posix.join(sourceDirectory, target));
    let replacement;

    if (repositoryTarget.startsWith('docs/') && repositoryTarget.toLowerCase().endsWith('.md')) {
      const manual = repositoryTarget
        .slice('docs/'.length)
        .replace(/\.md$/i, '/')
        .toLowerCase();
      replacement = `${publicBase}reference/manuals/${manual}`;
    } else if (promptByCanonicalPath.has(repositoryTarget)) {
      replacement = `${publicBase}reference/prompts/${slug(
        promptByCanonicalPath.get(repositoryTarget).prompt_id,
      )}/`;
    } else if (repositoryTarget === 'docs' || repositoryTarget === 'docs/docs') {
      replacement = `${publicBase}reference/manuals/`;
    } else {
      replacement = `https://github.com/manojpisini/mission-directives/blob/main/${repositoryTarget}`;
    }
    return `${open}${replacement}${fragment}${close}`;
  });
}
const scenarioRows = [
  ...(scenarios.atomic_scenarios ?? []).map((entry) => ({ ...entry, kind: 'atomic' })),
  ...(scenarios.composite_scenarios ?? []).map((entry) => ({ ...entry, kind: 'composite' })),
];
const skillRows = skills.skills ?? [];

const promptIndexRows = [];
for (const prompt of prompts) {
  const idSlug = slug(prompt.prompt_id);
  const body = await readFile(path.join(repoRoot, prompt.canonical_path), 'utf8');
  const metadata = [
    '| Field | Value |',
    '| --- | --- |',
    `| Canonical ID | \`${clean(prompt.prompt_id)}\` |`,
    `| Capability ID | \`${clean(prompt.capability_id)}\` |`,
    `| Category | ${clean(prompt.category)} |`,
    `| Role / type | ${clean(prompt.prompt_role)} / ${clean(prompt.prompt_type)} |`,
    `| Default mode | \`${clean(prompt.default_mode)}\` |`,
    `| Risk | ${clean(prompt.risk_level)} |`,
    `| Status | ${clean(prompt.status)} |`,
    `| Canonical source | \`${clean(prompt.canonical_path)}\` |`,
  ].join('\n');
  const content = [
    frontmatter(`${prompt.prompt_id}: ${prompt.title}`, prompt.description),
    '[Back to prompt catalog](../)',
    '',
    prompt.description,
    '',
    '## Contract',
    '',
    metadata,
    '',
    '## Routing',
    '',
    '**Tags**',
    '',
    list(prompt.tags),
    '',
    '**Prerequisites**',
    '',
    list(prompt.requires),
    '',
    '**Produces**',
    '',
    list(prompt.produces),
    '',
    '## Canonical directive',
    '',
    body.trim(),
    '',
  ].join('\n');
  await write(path.join('reference', 'prompts', idSlug, 'index.md'), content);
  promptIndexRows.push(
    `| [${prompt.prompt_id}](./${idSlug}/) | ${clean(prompt.title)} | ${clean(prompt.category)} | ${clean(prompt.risk_level)} |`,
  );
}

await write(
  path.join('reference', 'prompts', 'index.md'),
  [
    frontmatter('Prompt Catalog', 'Search and inspect every canonical Mission Directive.'),
    `Generated from \`catalog.json\` and canonical prompt bodies. **${prompts.length} prompts** are indexed.`,
    '',
    table(promptIndexRows),
  ].join('\n'),
);

const scenarioIndexRows = [];
for (const scenario of scenarioRows) {
  const idSlug = slug(scenario.scenario_id);
  const phases = (scenario.phases ?? [])
    .map(
      (phase, index) =>
        `${index + 1}. **${clean(phase.phase_id)}** - \`${clean(phase.mode)}\`: ${(phase.prompt_ids ?? [])
          .map((id) => `[${id}](../../prompts/${slug(id)}/)`)
          .join(', ')}`,
    )
    .join('\n');
  const content = [
    frontmatter(`${scenario.scenario_id}: ${scenario.title}`, scenario.purpose),
    '[Back to scenario catalog](../)',
    '',
    scenario.purpose,
    '',
    '| Field | Value |',
    '| --- | --- |',
    `| Kind | ${scenario.kind} |`,
    `| Default mode | \`${clean(scenario.default_mode)}\` |`,
    `| Minimum assurance | ${clean(scenario.minimum_assurance)} |`,
    `| Prompt count | ${(scenario.prompts ?? []).length} |`,
    '',
    '## Phase graph',
    '',
    phases || '_No phases declared._',
    '',
    '## Required inputs',
    '',
    list(scenario.required_inputs),
    '',
    '## Produced artifacts',
    '',
    list(scenario.produced_artifacts),
    '',
    '## Execution locks',
    '',
    list(scenario.execution_locks),
    '',
    '## Completion gate',
    '',
    scenario.completion_gate || '_No completion gate declared._',
  ].join('\n');
  await write(path.join('reference', 'scenarios', idSlug, 'index.md'), content);
  scenarioIndexRows.push(
    `| [${scenario.scenario_id}](./${idSlug}/) | ${clean(scenario.title)} | ${scenario.kind} | ${clean(scenario.minimum_assurance)} |`,
  );
}

await write(
  path.join('reference', 'scenarios', 'index.md'),
  [
    frontmatter('Scenario Catalog', 'Atomic and composite execution graphs with modes, phases, locks, and completion gates.'),
    `Generated from \`SCENARIO_CATALOG.json\`. **${scenarioRows.length} scenarios** are indexed.`,
    '',
    table(scenarioIndexRows),
  ].join('\n'),
);

const skillIndexRows = [];
for (const skill of skillRows) {
  const idSlug = slug(skill.skill_id);
  const content = [
    frontmatter(skill.skill_id, skill.purpose),
    '[Back to skill registry](../)',
    '',
    skill.purpose,
    '',
    '| Field | Value |',
    '| --- | --- |',
    `| Kind | ${clean(skill.kind)} |`,
    `| Trust tier | ${clean(skill.trust_tier)} |`,
    `| Maturity | ${clean(skill.maturity)} |`,
    `| Auto-select | ${skill.auto_select_allowed ? 'allowed' : 'not allowed'} |`,
    `| Verification | ${skill.verification_required ? 'required' : 'not required'} |`,
    `| Lock | ${skill.lock_required ? 'required' : 'not required'} |`,
    '',
    '## Prompt routes',
    '',
    list(skill.prompt_routes),
    '',
    '## Installation',
    '',
    skill.install_command ? `\`\`\`shell\n${skill.install_command}\n\`\`\`` : '_No verified install command is declared._',
    '',
    skill.audit_note ? `## Audit note\n\n${skill.audit_note}` : '',
  ].join('\n');
  await write(path.join('reference', 'skills', idSlug, 'index.md'), content);
  skillIndexRows.push(
    `| [${clean(skill.skill_id)}](./${idSlug}/) | ${clean(skill.purpose)} | ${clean(skill.kind)} | ${clean(skill.trust_tier)} |`,
  );
}

await write(
  path.join('reference', 'skills', 'index.md'),
  [
    frontmatter('Skill Registry', 'Verified, conditional, aliased, and quarantined skill routes.'),
    `Generated from \`skill_registry.json\`. **${skillRows.length} skills and aliases** are indexed.`,
    '',
    table(skillIndexRows),
  ].join('\n'),
);

const manualFiles = await walkMarkdown(path.join(repoRoot, 'docs'));
const manualRows = [];
for (const relative of manualFiles) {
  const rawSource = await readFile(path.join(repoRoot, 'docs', relative), 'utf8');
  const source = rewriteManualLinks(rawSource, relative);
  const match = source.match(/^#\s+(.+)$/m);
  const title = match?.[1]?.trim() || path.basename(relative, '.md').replaceAll('_', ' ');
  const destination = relative.replaceAll('\\', '/');
  const route = destination.replace(/\.md$/i, '/').toLowerCase();
  const content = [
    frontmatter(title, `Canonical repository manual: ${destination}`),
    `_Mirrored from \`docs/${destination}\` during the site build._`,
    '',
    source.trim(),
    '',
  ].join('\n');
  await write(path.join('reference', 'manuals', destination), content);
  manualRows.push(`- [${title}](./${route})`);
}

await write(
  path.join('reference', 'manuals', 'index.md'),
  [
    frontmatter('Repository Manuals', 'Build-time mirrors of every public Markdown manual in the canonical repository.'),
    `**${manualFiles.length} manuals** are mirrored at build time. Internal implementation plans are intentionally excluded.`,
    '',
    ...manualRows,
  ].join('\n'),
);

await write(
  path.join('reference', 'index.md'),
  [
    frontmatter('Generated Reference', 'Canonical prompt, scenario, skill, and manual indexes generated at build time.'),
    'This section is regenerated before every local development run and production build.',
    '',
    '| Surface | Count | Source |',
    '| --- | ---: | --- |',
    `| [Prompts](./prompts/) | ${prompts.length} | \`catalog.json\` and \`prompts/\` |`,
    `| [Scenarios](./scenarios/) | ${scenarioRows.length} | \`SCENARIO_CATALOG.json\` |`,
    `| [Skills](./skills/) | ${skillRows.length} | \`skill_registry.json\` |`,
    `| [Manuals](./manuals/) | ${manualFiles.length} | \`docs/\` |`,
    '',
    '<div class="signal"><strong>Source of truth:</strong> edit the repository catalogs, prompt bodies, or manuals. Never edit generated pages.</div>',
  ].join('\n'),
);

console.log(
  `Generated ${prompts.length} prompts, ${scenarioRows.length} scenarios, ${skillRows.length} skills, and ${manualFiles.length} manuals.`,
);

