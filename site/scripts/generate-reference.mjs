import { copyFile, mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = path.resolve(siteRoot, '..');
const docsRoot = path.join(repoRoot, 'docs');
const manualsRoot = path.join(siteRoot, 'public', 'reference', 'manuals');
const brandSourceRoot = path.join(repoRoot, 'assets', 'images');
const brandPublicRoot = path.join(siteRoot, 'public', 'assets', 'brand');
const catalogPath = path.join(repoRoot, 'catalog.json');
const scenarioCatalogPath = path.join(repoRoot, 'SCENARIO_CATALOG.json');
const base = '/mission-directives/';
const brandFiles = [
  'mission_directives_full_logo_lateral_dark.svg',
  'mission_directives_logo_dark.svg',
  'mission_directives_logo_light.svg',
  'mission_directives_wordmark_dark.svg',
];

const escapeHtml = (value) =>
  String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');

const slug = (value) =>
  String(value)
    .toLowerCase()
    .replace(/\.md$/i, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

const inline = (value, sourceRoot = 'docs') =>
  escapeHtml(value)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (full, label, target) => {
      if (/^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith('#')) {
        return `<a href="${escapeHtml(target)}">${escapeHtml(label)}</a>`;
      }
      if (target.toLowerCase().endsWith('.md') && (target.startsWith('docs/') || (sourceRoot === 'docs' && !target.includes('/')))) {
        return `<a href="${base}reference/manuals/${slug(path.basename(target))}/">${escapeHtml(label)}</a>`;
      }
      return `<a href="https://github.com/manojpisini/mission-directives/blob/main/${escapeHtml(target)}">${escapeHtml(label)}</a>`;
    });

function markdownToHtml(markdown, sourceRoot = 'docs') {
  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  const out = [];
  let paragraph = [];
  let unorderedList = [];
  let orderedList = [];
  let orderedStart = 1;
  let table = [];
  let inCode = false;
  let code = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    out.push(`<p>${inline(paragraph.join(' '), sourceRoot)}</p>`);
    paragraph = [];
  };
  const flushUnorderedList = () => {
    if (!unorderedList.length) return;
    out.push('<ul>' + unorderedList.map((item) => `<li>${inline(item, sourceRoot)}</li>`).join('') + '</ul>');
    unorderedList = [];
  };
  const flushOrderedList = () => {
    if (!orderedList.length) return;
    const start = orderedStart === 1 ? '' : ` start="${orderedStart}"`;
    out.push(`<ol${start}>` + orderedList.map((item) => `<li>${inline(item, sourceRoot)}</li>`).join('') + '</ol>');
    orderedList = [];
    orderedStart = 1;
  };
  const flushLists = () => { flushUnorderedList(); flushOrderedList(); };
  const flushTable = () => {
    if (!table.length) return;
    const rows = table.filter((row) => !/^\s*\|?\s*:?-{3,}/.test(row));
    if (rows.length) {
      out.push('<div class="table-card"><table><tbody>' + rows.map((row) => {
        const cells = row.split('|').map((cell) => cell.trim()).filter(Boolean);
        return '<tr>' + cells.map((cell) => `<td>${inline(cell, sourceRoot)}</td>`).join('') + '</tr>';
      }).join('') + '</tbody></table></div>');
    }
    table = [];
  };
  const flushAll = () => { flushParagraph(); flushLists(); flushTable(); };

  for (const line of lines) {
    if (line.startsWith('```')) {
      flushAll();
      if (inCode) {
        out.push(`<div class="code-block code-block--flush"><div class="code-block__bar"><span>Reference</span><button class="copy-button">Copy</button></div><pre><code>${escapeHtml(code.join('\n'))}</code></pre></div>`);
        code = [];
      }
      inCode = !inCode;
      continue;
    }
    if (inCode) { code.push(line); continue; }
    if (!line.trim()) { flushAll(); continue; }
    if (line.startsWith('|')) { flushParagraph(); flushLists(); table.push(line); continue; }
    const heading = /^(#{1,4})\s+(.+)$/.exec(line);
    if (heading) {
      flushAll();
      const level = Math.min(heading[1].length + 1, 4);
      out.push(`<h${level}>${inline(heading[2], sourceRoot)}</h${level}>`);
      continue;
    }
    const bullet = /^[-*]\s+(.+)$/.exec(line);
    if (bullet) { flushParagraph(); flushOrderedList(); flushTable(); unorderedList.push(bullet[1]); continue; }
    const ordered = /^(\d+)[.)]\s+(.+)$/.exec(line);
    if (ordered) {
      flushParagraph();
      flushUnorderedList();
      flushTable();
      if (!orderedList.length) orderedStart = Number(ordered[1]);
      orderedList.push(ordered[2]);
      continue;
    }
    flushLists();
    flushTable();
    paragraph.push(line.trim());
  }
  flushAll();
  return out.join('\n');
}

async function syncBrandAssets() {
  await mkdir(brandPublicRoot, { recursive: true });
  await Promise.all(brandFiles.map((file) => copyFile(path.join(brandSourceRoot, file), path.join(brandPublicRoot, file))));
}

const categoryFor = (file, title) => {
  const name = `${file} ${title}`.toLowerCase();
  if (/\bmanuals?\b/.test(name)) return 'manual';
  if (/\bguides?\b/.test(name)) return 'guide';
  if (/\breferences?\b|\bcatalog\b|\bprotocol\b|\bpolicy\b|\bstandard\b|\bindex\b|\bmatrix\b|\bcommands\b|\bboundaries\b|\blanes\b|\bconventions\b|\bmethods\b|\bstacks\b/.test(name)) return 'reference';
  return 'other';
};

async function collectManuals() {
  const entries = await readdir(docsRoot, { withFileTypes: true });
  const files = entries
    .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith('.md'))
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b));
  const rows = [];
  await rm(manualsRoot, { recursive: true, force: true });
  await mkdir(manualsRoot, { recursive: true });

  for (const file of files) {
    const source = await readFile(path.join(docsRoot, file), 'utf8');
    const title = /^#\s+(.+)$/m.exec(source)?.[1]?.trim() ?? file.replace(/\.md$/i, '').replaceAll('_', ' ');
    const id = slug(file);
    const firstParagraph = source
      .replace(/^#.*$/m, '')
      .split('\n\n')
      .map((part) => part.trim())
      .find((part) => part && !part.startsWith('##')) ?? 'Mission Directives documentation page.';
    const row = {
      file,
      id,
      title,
      category: categoryFor(file, title),
      description: firstParagraph.replace(/\s+/g, ' ').slice(0, 180),
      body: markdownToHtml(source),
    };
    rows.push(row);
    await mkdir(path.join(manualsRoot, id), { recursive: true });
    await writeFile(path.join(manualsRoot, id, 'index.html'), manualPage(row), 'utf8');
  }
  return rows;
}

function topbar() {
  return `<header class="topbar"><div class="topbar__inner"><button aria-expanded="false" aria-label="Open navigation" class="icon-button mobile-menu" id="mobileMenu"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"></path></svg></button><a aria-label="Mission Directives home" class="brand" href="${base}index.html"><img alt="" aria-hidden="true" class="brand__logo" src="${base}assets/brand/mission_directives_logo_dark.svg"/></a><button aria-haspopup="dialog" class="search-trigger" id="searchTrigger"><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"></circle><path d="m16 16 4 4"></path></svg><span>Search this page</span><kbd>Ctrl K</kbd></button></div></header>`;
}

function sidebar(active) {
  const item = (href, label, key) => `<a${active === key ? ' class="active"' : ''} href="${base}${href}"><span>${label}</span></a>`;
  return `<aside aria-label="Documentation navigation" class="sidebar" id="sidebar"><div class="sidebar__scroll"><div class="version-panel"><div><span>Documentation</span><strong>Version 2.0.3</strong></div><span class="status-dot">Stable</span></div><nav class="docs-nav" id="docsNav"><section class="nav-group"><p>Start here</p>${item('getting-started.html', 'Getting started', 'getting-started')}${item('installation.html', 'Installation', 'installation')}${item('contributing.html', 'Contributing', 'contributing')}</section><section class="nav-group"><p>Documentation</p>${item('docs.html', 'Overview', 'docs')}${item('guides.html', 'Guides', 'guides')}${item('manuals.html', 'Manuals', 'manuals')}${item('reference.html', 'Reference', 'reference')}${item('prompts.html', 'Prompts', 'prompts')}${item('scenarios.html', 'Scenarios', 'scenarios')}${item('pairs.html', 'Pairs', 'pairs')}</section><section class="nav-group"><p>Core manuals</p><a href="${base}reference/manuals/user-manual/"><span>User manual</span></a><a href="${base}reference/manuals/operator-guide/"><span>Operator guide</span></a><a href="${base}reference/manuals/security-operations-guide/"><span>Security operations</span></a></section></nav><div class="sidebar-help"><span class="sidebar-help__icon">?</span><div><strong>Operator path</strong><p>Route, explain, plan, execute, verify.</p></div></div></div></aside>`;
}

function shell({ title, description, active, content, toc = '' }) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="${escapeHtml(description)}" />
  <title>${escapeHtml(title)} — Mission Directives</title>
  <link rel="icon" href="${base}assets/brand/mission_directives_logo_dark.svg" type="image/svg+xml" media="(prefers-color-scheme: light)" />
  <link rel="icon" href="${base}assets/brand/mission_directives_logo_light.svg" type="image/svg+xml" media="(prefers-color-scheme: dark)" />
  <link rel="stylesheet" href="${base}styles.css" />
</head>
<body class="docs-page">
<a class="skip-link" href="#main-content">Skip to content</a>
${topbar()}
<div class="layout">${sidebar(active)}<main class="main" id="main-content"><div class="content-grid"><article class="doc-content">${content}</article>${toc}</div><footer class="footer"><div class="footer__inner"><a aria-label="Mission Directives home" class="footer__brand" href="${base}index.html"><img alt="" aria-hidden="true" src="${base}assets/brand/mission_directives_wordmark_dark.svg"/></a><span>Documentation <span aria-hidden="true">&middot;</span> Version 2.0.3</span></div></footer></main></div>
${searchDialog()}
<div class="sidebar-backdrop" hidden id="sidebarBackdrop"></div><script is:inline src="${base}app.js"></script>
</body>
</html>`;
}

function searchDialog() {
  return `<div aria-label="Search documentation" aria-modal="true" class="search-dialog" hidden id="searchDialog" role="dialog"><div class="search-dialog__panel"><div class="search-input-wrap"><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"></circle><path d="m16 16 4 4"></path></svg><input autocomplete="off" id="searchInput" placeholder="Search current page..." type="search"/><kbd>Esc</kbd></div><div class="search-results" id="searchResults"></div></div></div>`;
}

function visualAsset(src, title, caption) {
  return `<figure class="visual-figure"><img src="${base}${src}" alt="${escapeHtml(title)}" loading="lazy" /><figcaption><strong>${escapeHtml(title)}</strong><span>${escapeHtml(caption)}</span></figcaption></figure>`;
}

function routeDiagram() {
  return `<div class="technical-map" aria-label="Routing and verification depiction"><div><span>Intent</span><strong>Request</strong></div><i></i><div><span>Scoring</span><strong>Route</strong></div><i></i><div><span>Graph</span><strong>Plan</strong></div><i></i><div><span>Receipt</span><strong>Verify</strong></div></div>`;
}

function libraryGrid(items) {
  return `<div class="route-list">${items.map((manual) => `<a href="${base}reference/manuals/${manual.id}/"><span class="route-id">${escapeHtml(manual.category.toUpperCase())}</span><span><strong>${escapeHtml(manual.title)}</strong><small>${escapeHtml(manual.description)}</small></span><span aria-hidden="true">→</span></a>`).join('\n')}</div>`;
}

function docsHome(manuals) {
  const content = `<section class="docs-intro section-block docs-hero" data-title="Documentation overview" id="overview"><div><div class="eyebrow-row"><span class="eyebrow">Mission Directives</span><span class="pill">v2.0.3</span></div><h1>Documentation</h1><p class="lead">A sectioned operator manual for routing, installing, authoring, validating, and maintaining Mission Directives without loading the whole prompt library into context.</p><div class="docs-intro__actions"><a class="button button--primary" href="${base}getting-started.html">Get started</a><a class="button button--secondary" href="${base}installation.html">Install</a></div></div></section>
<section class="section-block" data-title="Start here" id="start-here"><div class="section-heading"><span class="section-kicker">Start here</span><h2>From installation to first verified route</h2><p>Use the focused onboarding pages before moving into the complete operator and maintainer references.</p></div><div class="doc-hub-grid"><a class="doc-hub-card" href="${base}getting-started.html"><span class="doc-hub-card__eyebrow">Getting started</span><h3>Run the first workflow</h3><p>Install, initialize, validate project context, route a request, inspect the selection, and open the local viewer.</p></a><a class="doc-hub-card" href="${base}installation.html"><span class="doc-hub-card__eyebrow">Installation</span><h3>Install the CLI and project runtime</h3><p>Choose a package installer and tracking mode, then understand the pinned project layout.</p></a><a class="doc-hub-card" href="${base}contributing.html"><span class="doc-hub-card__eyebrow">Contributing</span><h3>Change the canonical source safely</h3><p>Set up development, preserve generated contracts, run the required checks, and prepare review evidence.</p></a></div></section>
<section class="section-block" data-title="Documentation sections" id="sections"><div class="section-heading"><span class="section-kicker">Structure</span><h2>Documentation is split by job</h2><p>The hub links to separate guide, manual, and reference pages so operators can land on the right depth without a full-scroll document.</p></div><div class="doc-hub-grid"><a class="doc-hub-card" href="${base}guides.html"><span class="doc-hub-card__eyebrow">Guides</span><h3>How to operate and extend the suite</h3><p>Installation, routing, security, prompt authoring, skill routing, and docs-site operation.</p></a><a class="doc-hub-card" href="${base}manuals.html"><span class="doc-hub-card__eyebrow">Manuals</span><h3>Complete repository manuals</h3><p>Generated pages for every root file in <code>docs/</code>, with source links preserved.</p></a><a class="doc-hub-card" href="${base}reference.html"><span class="doc-hub-card__eyebrow">Reference</span><h3>Contracts and command surfaces</h3><p>Runtime markers, schemas, catalog behavior, policies, and verification commands.</p></a><a class="doc-hub-card" href="${base}prompts.html"><span class="doc-hub-card__eyebrow">Prompts</span><h3>Every prompt explained</h3><p>Canonical prompt IDs, routing metadata, artifacts, modes, risk, contracts, and boundaries.</p></a><a class="doc-hub-card" href="${base}scenarios.html"><span class="doc-hub-card__eyebrow">Scenarios</span><h3>Atomic and composite workflows</h3><p>Scenario purposes, prompt graphs, inputs, outputs, locks, phases, and completion gates.</p></a><a class="doc-hub-card" href="${base}pairs.html"><span class="doc-hub-card__eyebrow">Pairs</span><h3>Planning and execution twins</h3><p>Reciprocal prompt pairs with authority splits, handoffs, outputs, and verification expectations.</p></a><a class="doc-hub-card" href="${base}index.html"><span class="doc-hub-card__eyebrow">Project</span><h3>Landing page</h3><p>High-level mission, capabilities, metrics, and route-flow explanation.</p></a></div></section>
<section class="section-block" data-title="Routing depiction" id="routing-depiction"><div class="section-heading"><span class="section-kicker">Depiction</span><h2>Small graph routing</h2><p>Mission Directives keeps routing deterministic by resolving metadata before prompt bodies are loaded.</p></div>${routeDiagram()}${visualAsset('assets/diagrams/routing-system.svg', 'Routing system diagram', 'The request is scored into a bounded prompt graph and closed by verification evidence.')}</section>`;
  return shell({ title: 'Documentation', description: 'Mission Directives documentation hub.', active: 'docs', content });
}

function guidesPage(manuals) {
  const guides = manuals.filter((manual) => manual.category === 'guide');
  const content = `<section class="docs-intro section-block" data-title="Guides" id="guides"><div class="eyebrow-row"><span class="eyebrow">Guides</span><span class="pill">${guides.length} pages</span></div><h1>Guides</h1><p class="lead">Task-focused guidance for setup, routing, prompt authoring, skills, security, validation, cleanup, and documentation operations.</p></section>
<section class="section-block" data-title="Guide map" id="guide-map"><div class="section-heading"><span class="section-kicker">Map</span><h2>Choose by responsibility</h2></div><div class="journey-grid"><div class="journey-step"><strong>Install</strong><span>Project payload and runtime boundary</span></div><div class="journey-step"><strong>Route</strong><span>Keyword scoring and scenario selection</span></div><div class="journey-step"><strong>Author</strong><span>Prompt bodies, scenarios, pairs, and skills</span></div><div class="journey-step"><strong>Secure</strong><span>Authorization, evidence, and supply chain</span></div><div class="journey-step"><strong>Verify</strong><span>Tests, manifest, and CI gates</span></div></div></section>
<section class="section-block" data-title="Guide library" id="guide-library">${libraryGrid(guides)}</section>`;
  return shell({ title: 'Guides', description: 'Mission Directives guides.', active: 'guides', content });
}

function manualsPage(manuals) {
  const manualPages = manuals.filter((manual) => manual.category === 'manual');
  const content = `<section class="docs-intro section-block" data-title="Manuals" id="manuals"><div class="eyebrow-row"><span class="eyebrow">Manuals</span><span class="pill">${manualPages.length} pages</span></div><h1>Manuals</h1><p class="lead">Complete operating manuals rendered from canonical repository documentation with consistent spacing and source provenance.</p></section>
<section class="section-block" data-title="Manual library" id="manual-library"><div class="section-heading"><span class="section-kicker">Library</span><h2>Repository manuals</h2><p>Long-form manuals for operators and maintainers.</p></div>${libraryGrid(manualPages)}</section>`;
  return shell({ title: 'Manuals', description: 'Mission Directives manual library.', active: 'manuals', content });
}

function referencePage(manuals) {
  const refs = manuals.filter((manual) => manual.category === 'reference');
  const content = `<section class="docs-intro section-block" data-title="Reference" id="reference"><div class="eyebrow-row"><span class="eyebrow">Reference</span><span class="pill">${refs.length} pages</span></div><h1>Reference</h1><p class="lead">Command, marker, manifest, payload, and validation contracts for operators and maintainers.</p></section>
<section class="section-block" data-title="Runtime boundary" id="runtime-boundary"><div class="section-heading"><span class="section-kicker">Boundary</span><h2>Runtime payload stays lean</h2><p>Only execution-critical files install into a working project. Source-only validators, imported provenance, and site generation remain in the repository.</p></div>${visualAsset('assets/diagrams/runtime-payload.svg', 'Runtime payload diagram', 'Installed files are separated from repository validation and documentation sources.')}</section>
<section class="section-block" data-title="Markers" id="markers"><div class="section-heading"><span class="section-kicker">Markers</span><h2>Evidence marker contract</h2></div><div class="marker-grid"><div><code>@EVIDENCE:{id}</code><span>Observed source or input.</span></div><div><code>?UNKNOWN:{id}</code><span>Material uncertainty.</span></div><div><code>#FINDING:{id}</code><span>Evidence-backed conclusion.</span></div><div><code>+ACTION:{id}</code><span>Bounded action or recommendation.</span></div><div><code>=VERIFY:{id}</code><span>Acceptance check and result.</span></div><div><code>!STOP:{reason}</code><span>Required halt condition.</span></div></div></section>
<section class="section-block" data-title="Catalog reference" id="catalog-reference"><div class="section-heading"><span class="section-kicker">Catalog</span><h2>Generated library references</h2><p>These pages are generated from canonical repository data so prompt, scenario, and pair explanations stay aligned with validation.</p></div><div class="doc-hub-grid"><a class="doc-hub-card" href="${base}prompts.html"><span class="doc-hub-card__eyebrow">Prompts</span><h3>Prompt catalog</h3><p>Every canonical prompt with modes, contracts, tags, artifacts, and usage boundaries.</p></a><a class="doc-hub-card" href="${base}scenarios.html"><span class="doc-hub-card__eyebrow">Scenarios</span><h3>Scenario catalog</h3><p>Atomic routes and composite workflows with graph, phase, lock, and gate detail.</p></a><a class="doc-hub-card" href="${base}pairs.html"><span class="doc-hub-card__eyebrow">Pairs</span><h3>Prompt pairs</h3><p>Planning/execution relationships and the handoff contract between reciprocal twins.</p></a></div></section>
<section class="section-block" data-title="Reference library" id="reference-library">${libraryGrid(refs)}</section>`;
  return shell({ title: 'Reference', description: 'Mission Directives technical reference.', active: 'reference', content });
}

const asArray = (value) => Array.isArray(value) ? value.filter((item) => item !== null && item !== undefined && String(item).trim()) : [];
const compact = (value) => String(value ?? '').replace(/\s+/g, ' ').trim();
const valueOr = (value, fallback = 'Not declared') => compact(value) || fallback;

function listValues(items, limit = 8) {
  const values = asArray(items).map((item) => typeof item === 'string' ? item : JSON.stringify(item));
  if (!values.length) return '<p class="muted-value">None declared</p>';
  const shown = values.slice(0, limit).map((item) => `<li>${escapeHtml(item)}</li>`).join('');
  const rest = values.length > limit ? `<li>+${values.length - limit} more</li>` : '';
  return `<ul class="reference-list">${shown}${rest}</ul>`;
}

function metaCells(rows) {
  return `<dl class="reference-meta">${rows.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(valueOr(value))}</dd></div>`).join('')}</dl>`;
}

function detailBlock(label, body) {
  return `<section class="reference-detail"><h4>${escapeHtml(label)}</h4>${body}</section>`;
}

function promptCard(prompt) {
  const artifact = prompt.output_contract?.primary_artifact?.path ?? prompt.produces?.[0] ?? 'Declared by prompt body or selected scenario';
  const boundary = asArray(prompt.do_not_use_when).length ? listValues(prompt.do_not_use_when, 8) : (prompt.do_not_use_when ? `<p>${escapeHtml(prompt.do_not_use_when)}</p>` : '<p>No additional exclusion rule declared beyond mode, authority, and verification contracts.</p>');
  const required = [...asArray(prompt.requires), ...asArray(prompt.consumes)].slice(0, 12);
  return `<article class="reference-card" id="${escapeHtml(prompt.prompt_id)}"><div class="reference-card__head"><span class="route-id">${escapeHtml(prompt.prompt_id)}</span><div><h3>${escapeHtml(prompt.title)}</h3><p>${escapeHtml(prompt.description)}</p></div></div>${metaCells([['Category', prompt.category], ['Role', prompt.prompt_role], ['Type', prompt.prompt_type], ['Default mode', prompt.default_mode], ['Risk', prompt.risk_level], ['Status', prompt.status]])}${detailBlock('When to use', `<p>${escapeHtml(prompt.description)}</p>`)}${detailBlock('Inputs and prerequisites', listValues(required))}${detailBlock('Outputs and artifacts', listValues([artifact, ...asArray(prompt.produces)]))}${detailBlock('Allowed modes', listValues(prompt.allowed_modes))}${detailBlock('Tags and routing hints', listValues(prompt.tags, 10))}${detailBlock('Do not use when', boundary)}</article>`;
}

function promptsPage(catalog) {
  const prompts = [...(catalog.prompts ?? [])].sort((a, b) => a.prompt_id.localeCompare(b.prompt_id));
  const categories = new Set(prompts.map((prompt) => prompt.category).filter(Boolean));
  const content = `<section class="docs-intro section-block" data-title="Prompts" id="prompts"><div class="eyebrow-row"><span class="eyebrow">Prompt catalog</span><span class="pill">${prompts.length} prompts</span></div><h1>Prompts</h1><p class="lead">Every canonical Mission Directives prompt is listed with its intent, routing metadata, mode boundaries, required inputs, produced artifacts, and exclusion rules.</p></section><section class="section-block" data-title="Prompt coverage" id="prompt-coverage"><div class="section-heading"><span class="section-kicker">Coverage</span><h2>Prompt explanations from the canonical catalog</h2><p>The generator reads <code>catalog.json</code> directly. This page is reference documentation, not a copied prompt body surface.</p></div><div class="stats-grid"><div><strong>${prompts.length}</strong><span>Prompts</span></div><div><strong>${categories.size}</strong><span>Categories</span></div><div><strong>${prompts.filter((prompt) => prompt.paired_prompt_id).length}</strong><span>Pair-aware prompts</span></div><div><strong>${prompts.filter((prompt) => prompt.risk_level && prompt.risk_level !== 'low').length}</strong><span>Elevated-risk routes</span></div></div></section><section class="section-block" data-title="All prompts" id="all-prompts"><div class="section-heading"><span class="section-kicker">Directory</span><h2>Every prompt</h2><p>Use browser search or the page search shortcut to jump by ID, role, category, output, or routing tag.</p></div><div class="reference-stack">${prompts.map(promptCard).join('')}</div></section>`;
  return shell({ title: 'Prompts', description: 'Every Mission Directives prompt explained from the canonical catalog.', active: 'prompts', content });
}

function scenarioCard(scenario, kind) {
  const prompts = asArray(scenario.prompts);
  const phases = asArray(scenario.phases).map((phase) => typeof phase === 'string' ? phase : `${phase.name ?? phase.phase ?? 'phase'}: ${asArray(phase.prompts).join(', ') || phase.description || 'declared step'}`);
  const gate = scenario.completion_gate ? JSON.stringify(scenario.completion_gate) : 'Completion gate declared by scenario execution policy';
  return `<article class="reference-card" id="${escapeHtml(scenario.scenario_id)}"><div class="reference-card__head"><span class="route-id">${escapeHtml(scenario.scenario_id)}</span><div><h3>${escapeHtml(scenario.title)}</h3><p>${escapeHtml(scenario.purpose)}</p></div></div>${metaCells([['Kind', kind], ['Default mode', scenario.default_mode], ['Minimum assurance', scenario.minimum_assurance], ['Prompts', prompts.length], ['Locks', asArray(scenario.execution_locks).length], ['External effects', asArray(scenario.possible_external_effects).join(', ') || 'None declared']])}${detailBlock('Prompt graph', listValues(prompts, 18))}${detailBlock('Required inputs', listValues(scenario.required_inputs, 10))}${detailBlock('Produced artifacts', listValues(scenario.produced_artifacts, 10))}${detailBlock('Consumed artifacts', listValues(scenario.consumed_artifacts, 10))}${detailBlock('Phases and branches', listValues([...phases, ...asArray(scenario.branches).map((branch) => typeof branch === 'string' ? branch : JSON.stringify(branch))], 12))}${detailBlock('Completion gate', `<p>${escapeHtml(gate)}</p>`)}</article>`;
}

function scenariosPage(scenarios) {
  const atomic = scenarios.atomic_scenarios ?? [];
  const composite = scenarios.composite_scenarios ?? [];
  const content = `<section class="docs-intro section-block" data-title="Scenarios" id="scenarios"><div class="eyebrow-row"><span class="eyebrow">Scenario catalog</span><span class="pill">${atomic.length + composite.length} scenarios</span></div><h1>Scenarios</h1><p class="lead">Atomic scenarios and composite workflow graphs are documented from the canonical scenario catalog, including prompt graphs, inputs, outputs, execution locks, and closure gates.</p></section><section class="section-block" data-title="Scenario coverage" id="scenario-coverage"><div class="section-heading"><span class="section-kicker">Coverage</span><h2>Atomic routes and composite workflows</h2><p>Atomic scenarios map one route to one prompt. Composite scenarios define multi-prompt workflows with phases, protected surfaces, and completion rules.</p></div><div class="stats-grid"><div><strong>${atomic.length}</strong><span>Atomic scenarios</span></div><div><strong>${composite.length}</strong><span>Composite scenarios</span></div><div><strong>${atomic.length + composite.length}</strong><span>Total scenario routes</span></div><div><strong>${new Set(composite.flatMap((scenario) => asArray(scenario.execution_locks))).size}</strong><span>Lock types</span></div></div></section><section class="section-block" data-title="Composite scenarios" id="composite-scenarios"><div class="section-heading"><span class="section-kicker">Composite</span><h2>Workflow scenarios</h2></div><div class="reference-stack">${composite.map((scenario) => scenarioCard(scenario, 'Composite workflow')).join('')}</div></section><section class="section-block" data-title="Atomic scenarios" id="atomic-scenarios"><div class="section-heading"><span class="section-kicker">Atomic</span><h2>Atomic prompt routes</h2></div><div class="reference-stack">${atomic.map((scenario) => scenarioCard(scenario, 'Atomic route')).join('')}</div></section>`;
  return shell({ title: 'Scenarios', description: 'Mission Directives atomic and composite scenarios explained.', active: 'scenarios', content });
}

function pairCard(prompt, byId) {
  const twin = byId.get(prompt.paired_prompt_id) ?? {};
  return `<article class="reference-card" id="${escapeHtml(prompt.prompt_id)}-${escapeHtml(prompt.paired_prompt_id)}"><div class="reference-card__head"><span class="route-id">${escapeHtml(prompt.prompt_id)} ↔ ${escapeHtml(prompt.paired_prompt_id)}</span><div><h3>${escapeHtml(prompt.title)} / ${escapeHtml(twin.title ?? 'Missing twin')}</h3><p>${escapeHtml(prompt.description)} ${twin.description ? escapeHtml(twin.description) : ''}</p></div></div>${metaCells([['Planning side', `${prompt.prompt_id} · ${prompt.prompt_role}`], ['Execution side', `${twin.prompt_id ?? prompt.paired_prompt_id} · ${twin.prompt_role ?? 'Not found'}`], ['Pairing required', prompt.pairing_required || twin.pairing_required || 'Declared by policy'], ['Shared category', prompt.category || twin.category], ['Planner mode', prompt.default_mode], ['Executor mode', twin.default_mode]])}${detailBlock('Planning contract', `<p>${escapeHtml(prompt.description)}</p>`)}${detailBlock('Execution contract', `<p>${escapeHtml(twin.description ?? 'The paired prompt is referenced but not present in the catalog.')}</p>`)}${detailBlock('Planner outputs', listValues([prompt.output_contract?.primary_artifact?.path, ...asArray(prompt.produces)]))}${detailBlock('Executor inputs and outputs', listValues([...asArray(twin.consumes), twin.output_contract?.primary_artifact?.path, ...asArray(twin.produces)]))}${detailBlock('Shared safeguards', listValues([...asArray(prompt.requires), ...asArray(twin.requires), prompt.risk_level, twin.risk_level], 12))}</article>`;
}

function pairsPage(catalog) {
  const prompts = catalog.prompts ?? [];
  const byId = new Map(prompts.map((prompt) => [prompt.prompt_id, prompt]));
  const pairs = prompts.filter((prompt) => prompt.paired_prompt_id && prompt.prompt_id < prompt.paired_prompt_id).sort((a, b) => a.prompt_id.localeCompare(b.prompt_id));
  const content = `<section class="docs-intro section-block" data-title="Pairs" id="pairs"><div class="eyebrow-row"><span class="eyebrow">Prompt pairs</span><span class="pill">${pairs.length} pairs</span></div><h1>Pairs</h1><p class="lead">Planning and execution prompts are paired where authority, review, handoff, and execution consent must stay separated.</p></section><section class="section-block" data-title="Pairing model" id="pairing-model"><div class="section-heading"><span class="section-kicker">Model</span><h2>Plan, review, then execute the exact twin</h2><p>Pair pages make the reciprocal relationship visible so operators can see what each side owns, what it produces, and which verification or approval boundary applies.</p></div>${routeDiagram()}</section><section class="section-block" data-title="All pairs" id="all-pairs"><div class="section-heading"><span class="section-kicker">Directory</span><h2>Every reciprocal pair</h2></div><div class="reference-stack">${pairs.map((prompt) => pairCard(prompt, byId)).join('')}</div></section>`;
  return shell({ title: 'Pairs', description: 'Mission Directives planning and execution prompt pairs explained.', active: 'pairs', content });
}
function manualPage(manual) {
  const section = {
    guide: { active: 'guides', href: 'guides.html', label: 'All guides' },
    manual: { active: 'manuals', href: 'manuals.html', label: 'All manuals' },
    reference: { active: 'reference', href: 'reference.html', label: 'All references' },
  }[manual.category] ?? { active: 'docs', href: 'docs.html', label: 'Documentation home' };
  const content = `<section class="docs-intro section-block manual-hero" data-title="${escapeHtml(manual.title)}" id="manual"><div class="eyebrow-row"><span class="eyebrow">Repository ${escapeHtml(manual.category)}</span><span class="pill">docs/${escapeHtml(manual.file)}</span></div><h1>${escapeHtml(manual.title)}</h1><p class="lead">Canonical documentation rendered from the repository <code>docs/</code> folder.</p><div class="manual-meta"><span>${escapeHtml(manual.category)}</span><a href="https://github.com/manojpisini/mission-directives/blob/main/docs/${escapeHtml(manual.file)}" rel="noreferrer" target="_blank">Source file</a></div></section><section class="section-block manual-body" data-title="Document content" id="content">${manual.body}</section><nav aria-label="Documentation routing" class="page-nav"><a class="button button--secondary" href="${base}${section.href}">${section.label}</a><a class="button button--primary" href="${base}docs.html">Documentation home</a></nav>`;
  return shell({ title: manual.title, description: `${manual.title} from the Mission Directives documentation set.`, active: section.active, content });
}

function onboardingPage({ title, description, active, source, sourceLabel, sourceUrl, sourceRoot = 'docs' }) {
  const body = markdownToHtml(source.replace(/^#\s+.+\r?\n/, ''), sourceRoot);
  const content = `<section class="docs-intro section-block manual-hero" data-title="${escapeHtml(title)}" id="overview"><div class="eyebrow-row"><span class="eyebrow">Start here</span><span class="pill">v2.0.3</span></div><h1>${escapeHtml(title)}</h1><p class="lead">${escapeHtml(description)}</p><div class="manual-meta"><span>${escapeHtml(sourceLabel)}</span><a href="${escapeHtml(sourceUrl)}" rel="noreferrer" target="_blank">Source file</a></div></section><section class="section-block manual-body" data-title="${escapeHtml(title)} content" id="content">${body}</section><nav aria-label="Documentation routing" class="page-nav"><a class="button button--secondary" href="${base}getting-started.html">Getting started</a><a class="button button--primary" href="${base}docs.html">Documentation home</a></nav>`;
  return shell({ title, description, active, content });
}

await syncBrandAssets();
const manuals = await collectManuals();
const catalog = JSON.parse(await readFile(catalogPath, 'utf8'));
const scenarios = JSON.parse(await readFile(scenarioCatalogPath, 'utf8'));
const gettingStartedSource = await readFile(path.join(docsRoot, 'GETTING_STARTED.md'), 'utf8');
const installationSource = await readFile(path.join(docsRoot, 'INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md'), 'utf8');
const contributingSource = await readFile(path.join(repoRoot, 'CONTRIBUTING.md'), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'docs.html'), docsHome(manuals), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'getting-started.html'), onboardingPage({ title: 'Getting Started', description: 'Install Mission Directives, initialize a project, route the first request, and verify the selected workflow.', active: 'getting-started', source: gettingStartedSource, sourceLabel: 'docs/GETTING_STARTED.md', sourceUrl: 'https://github.com/manojpisini/mission-directives/blob/main/docs/GETTING_STARTED.md' }), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'installation.html'), onboardingPage({ title: 'Installation', description: 'Install the command, create the pinned project runtime, and choose an output tracking mode.', active: 'installation', source: installationSource, sourceLabel: 'docs/INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md', sourceUrl: 'https://github.com/manojpisini/mission-directives/blob/main/docs/INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md' }), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'contributing.html'), onboardingPage({ title: 'Contributing', description: 'Set up a development environment, change canonical sources, and verify generated contracts before review.', active: 'contributing', source: contributingSource, sourceLabel: 'CONTRIBUTING.md', sourceUrl: 'https://github.com/manojpisini/mission-directives/blob/main/CONTRIBUTING.md', sourceRoot: 'repo' }), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'guides.html'), guidesPage(manuals), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'manuals.html'), manualsPage(manuals), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'reference.html'), referencePage(manuals), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'prompts.html'), promptsPage(catalog), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'scenarios.html'), scenariosPage(scenarios), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'pairs.html'), pairsPage(catalog), 'utf8');
console.log(`Generated ${manuals.length} manual pages plus getting-started.html, installation.html, contributing.html, docs.html, guides.html, manuals.html, reference.html, prompts.html, scenarios.html, and pairs.html`);
