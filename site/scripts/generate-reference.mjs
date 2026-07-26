import { mkdir, readFile, readdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repoRoot = path.resolve(siteRoot, '..');
const docsRoot = path.join(repoRoot, 'docs');
const manualsRoot = path.join(siteRoot, 'public', 'reference', 'manuals');
const base = '/mission-directives/';

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

const inline = (value) =>
  escapeHtml(value)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, (full, label, target) => {
      if (/^[a-z][a-z0-9+.-]*:/i.test(target) || target.startsWith('#')) {
        return `<a href="${escapeHtml(target)}">${escapeHtml(label)}</a>`;
      }
      if (target.toLowerCase().endsWith('.md') && (!target.includes('/') || target.startsWith('docs/'))) {
        return `<a href="${base}reference/manuals/${slug(path.basename(target))}/">${escapeHtml(label)}</a>`;
      }
      return `<a href="https://github.com/manojpisini/mission-directives/blob/main/${escapeHtml(target)}">${escapeHtml(label)}</a>`;
    });

function markdownToHtml(markdown) {
  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  const out = [];
  let paragraph = [];
  let list = [];
  let table = [];
  let inCode = false;
  let code = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    out.push(`<p>${inline(paragraph.join(' '))}</p>`);
    paragraph = [];
  };
  const flushList = () => {
    if (!list.length) return;
    out.push('<ul>' + list.map((item) => `<li>${inline(item)}</li>`).join('') + '</ul>');
    list = [];
  };
  const flushTable = () => {
    if (!table.length) return;
    const rows = table.filter((row) => !/^\s*\|?\s*:?-{3,}/.test(row));
    if (rows.length) {
      out.push('<div class="table-card"><table><tbody>' + rows.map((row) => {
        const cells = row.split('|').map((cell) => cell.trim()).filter(Boolean);
        return '<tr>' + cells.map((cell) => `<td>${inline(cell)}</td>`).join('') + '</tr>';
      }).join('') + '</tbody></table></div>');
    }
    table = [];
  };
  const flushAll = () => { flushParagraph(); flushList(); flushTable(); };

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
    if (line.startsWith('|')) { flushParagraph(); flushList(); table.push(line); continue; }
    const heading = /^(#{1,4})\s+(.+)$/.exec(line);
    if (heading) {
      flushAll();
      const level = Math.min(heading[1].length + 1, 4);
      out.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }
    const bullet = /^[-*]\s+(.+)$/.exec(line);
    if (bullet) { flushParagraph(); flushTable(); list.push(bullet[1]); continue; }
    paragraph.push(line.trim());
  }
  flushAll();
  return out.join('\n');
}

const categoryFor = (file, title) => {
  const name = `${file} ${title}`.toLowerCase();
  if (name.includes('manual') || name.includes('operator') || name.includes('user')) return 'manual';
  if (name.includes('guide') || name.includes('authoring') || name.includes('integration') || name.includes('routing') || name.includes('security')) return 'guide';
  return 'reference';
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

function topbar(section = 'Documentation') {
  return `<header class="topbar"><div class="topbar__inner"><button aria-expanded="false" aria-label="Open navigation" class="icon-button mobile-menu" id="mobileMenu"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"></path></svg></button><a aria-label="Mission Directives home" class="brand" href="${base}index.html"><span aria-hidden="true" class="brand__mark"><span class="brand__mark-line"></span><span class="brand__mark-line"></span><span class="brand__mark-dot"></span></span><span class="brand__copy"><strong>Mission Directives</strong><span>${escapeHtml(section)}</span></span></a><button aria-haspopup="dialog" class="search-trigger" id="searchTrigger"><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"></circle><path d="m16 16 4 4"></path></svg><span>Search this page</span><kbd>Ctrl K</kbd></button><nav aria-label="Documentation links" class="top-actions"><a href="${base}docs.html">Docs</a><a href="${base}guides.html">Guides</a><a href="${base}manuals.html">Manuals</a><a href="${base}reference.html">Reference</a></nav></div></header>`;
}

function sidebar(active) {
  const item = (href, label, key) => `<a${active === key ? ' class="active"' : ''} href="${base}${href}"><span>${label}</span></a>`;
  return `<aside aria-label="Documentation navigation" class="sidebar" id="sidebar"><div class="sidebar__scroll"><div class="version-panel"><div><span>Documentation</span><strong>Version 1.8.3</strong></div><span class="status-dot">Stable</span></div><nav class="docs-nav" id="docsNav"><section class="nav-group"><p>Documentation</p>${item('docs.html', 'Overview', 'docs')}${item('guides.html', 'Guides', 'guides')}${item('manuals.html', 'Manuals', 'manuals')}${item('reference.html', 'Reference', 'reference')}</section><section class="nav-group"><p>Core manuals</p><a href="${base}reference/manuals/user-manual/"><span>User manual</span></a><a href="${base}reference/manuals/operator-guide/"><span>Operator guide</span></a><a href="${base}reference/manuals/security-operations-guide/"><span>Security operations</span></a></section></nav><div class="sidebar-help"><span class="sidebar-help__icon">?</span><div><strong>Operator path</strong><p>Route, explain, plan, execute, verify.</p></div></div></div></aside>`;
}

function shell({ title, description, active, section, content, toc = '' }) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="${escapeHtml(description)}" />
  <title>${escapeHtml(title)} — Mission Directives</title>
  <link rel="stylesheet" href="${base}styles.css" />
</head>
<body class="docs-page">
<a class="skip-link" href="#main-content">Skip to content</a>
${topbar(section)}
<div class="layout">${sidebar(active)}<main class="main" id="main-content"><div class="content-grid"><article class="doc-content">${content}</article>${toc}</div><footer class="footer"><span>Mission Directives Documentation</span><span>Generated from repository documentation</span></footer></main></div>
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
  return `<div class="route-list">${items.map((manual) => `<a href="${base}reference/manuals/${manual.id}/"><span class="route-id">${manual.category.toUpperCase()}</span><span><strong>${escapeHtml(manual.title)}</strong><small>${escapeHtml(manual.description)}</small></span><span>→</span></a>`).join('\n')}</div>`;
}

function docsHome(manuals) {
  const content = `<section class="docs-intro section-block docs-hero" data-title="Documentation overview" id="overview"><div><div class="eyebrow-row"><span class="eyebrow">Mission Directives</span><span class="pill">v1.8.3</span></div><h1>Documentation</h1><p class="lead">A sectioned operator manual for routing, installing, authoring, validating, and maintaining Mission Directives without loading the whole prompt library into context.</p><div class="docs-intro__actions"><a class="button button--primary" href="${base}guides.html">Open guides</a><a class="button button--secondary" href="${base}manuals.html">Browse manuals</a></div></div>${visualAsset('assets/infographics/mission-directives-overview.png', 'System overview infographic', 'Prompt routing, scenario graphs, runtime payloads, and verification gates in one operator view.')}</section>
<section class="section-block" data-title="Documentation sections" id="sections"><div class="section-heading"><span class="section-kicker">Structure</span><h2>Documentation is split by job</h2><p>The hub links to separate guide, manual, and reference pages so operators can land on the right depth without a full-scroll document.</p></div><div class="doc-hub-grid"><a class="doc-hub-card" href="${base}guides.html"><span class="doc-hub-card__eyebrow">Guides</span><h3>How to operate and extend the suite</h3><p>Installation, routing, security, prompt authoring, skill routing, and docs-site operation.</p></a><a class="doc-hub-card" href="${base}manuals.html"><span class="doc-hub-card__eyebrow">Manuals</span><h3>Complete repository manuals</h3><p>Generated pages for every root file in <code>docs/</code>, with source links preserved.</p></a><a class="doc-hub-card" href="${base}reference.html"><span class="doc-hub-card__eyebrow">Reference</span><h3>Contracts and command surfaces</h3><p>Runtime markers, schemas, catalog behavior, policies, and verification commands.</p></a><a class="doc-hub-card" href="${base}index.html"><span class="doc-hub-card__eyebrow">Project</span><h3>Landing page</h3><p>High-level mission, capabilities, metrics, and route-flow explanation.</p></a></div></section>
<section class="section-block" data-title="Routing depiction" id="routing-depiction"><div class="section-heading"><span class="section-kicker">Depiction</span><h2>Small graph routing</h2><p>Mission Directives keeps routing deterministic by resolving metadata before prompt bodies are loaded.</p></div>${routeDiagram()}${visualAsset('assets/diagrams/routing-system.svg', 'Routing system diagram', 'The request is scored into a bounded prompt graph and closed by verification evidence.')}</section>`;
  return shell({ title: 'Documentation', description: 'Mission Directives documentation hub.', active: 'docs', section: 'Documentation', content });
}

function guidesPage(manuals) {
  const guides = manuals.filter((manual) => manual.category === 'guide');
  const content = `<section class="docs-intro section-block" data-title="Guides" id="guides"><div class="eyebrow-row"><span class="eyebrow">Guides</span><span class="pill">${guides.length} pages</span></div><h1>Guides</h1><p class="lead">Task-focused guidance for setup, routing, prompt authoring, skills, security, validation, cleanup, and documentation operations.</p></section>
<section class="section-block" data-title="Guide map" id="guide-map"><div class="section-heading"><span class="section-kicker">Map</span><h2>Choose by responsibility</h2></div><div class="journey-grid"><div class="journey-step"><strong>Install</strong><span>Project payload and runtime boundary</span></div><div class="journey-step"><strong>Route</strong><span>Keyword scoring and scenario selection</span></div><div class="journey-step"><strong>Author</strong><span>Prompt bodies, scenarios, pairs, and skills</span></div><div class="journey-step"><strong>Secure</strong><span>Authorization, evidence, and supply chain</span></div><div class="journey-step"><strong>Verify</strong><span>Tests, manifest, and CI gates</span></div></div></section>
<section class="section-block" data-title="Guide library" id="guide-library">${libraryGrid(guides)}</section>`;
  return shell({ title: 'Guides', description: 'Mission Directives guides.', active: 'guides', section: 'Guides', content });
}

function manualsPage(manuals) {
  const content = `<section class="docs-intro section-block" data-title="Manuals" id="manuals"><div class="eyebrow-row"><span class="eyebrow">Manuals</span><span class="pill">${manuals.length} pages</span></div><h1>Manuals</h1><p class="lead">Every root documentation file is rendered as a centered, readable manual page with consistent spacing and source provenance.</p></section>
<section class="section-block" data-title="Manual taxonomy" id="manual-taxonomy"><div class="section-heading"><span class="section-kicker">Taxonomy</span><h2>Manual coverage by field</h2><p>The generated library covers operating practice, authoring standards, runtime contracts, integrations, verification, and maintenance.</p></div><div class="stats-grid"><div><strong>${manuals.filter((m) => m.category === 'manual').length}</strong><span>Manuals</span></div><div><strong>${manuals.filter((m) => m.category === 'guide').length}</strong><span>Guides</span></div><div><strong>${manuals.filter((m) => m.category === 'reference').length}</strong><span>Reference pages</span></div><div><strong>${manuals.length}</strong><span>Total docs</span></div></div></section>
<section class="section-block" data-title="All manuals" id="all-manuals">${libraryGrid(manuals)}</section>`;
  return shell({ title: 'Manuals', description: 'Mission Directives manual library.', active: 'manuals', section: 'Manuals', content });
}

function referencePage(manuals) {
  const refs = manuals.filter((manual) => manual.category === 'reference');
  const content = `<section class="docs-intro section-block" data-title="Reference" id="reference"><div class="eyebrow-row"><span class="eyebrow">Reference</span><span class="pill">Contracts</span></div><h1>Reference</h1><p class="lead">Command, marker, manifest, payload, and validation contracts for operators and maintainers.</p></section>
<section class="section-block" data-title="Runtime boundary" id="runtime-boundary"><div class="section-heading"><span class="section-kicker">Boundary</span><h2>Runtime payload stays lean</h2><p>Only execution-critical files install into a working project. Source-only validators, imported provenance, and site generation remain in the repository.</p></div>${visualAsset('assets/diagrams/runtime-payload.svg', 'Runtime payload diagram', 'Installed files are separated from repository validation and documentation sources.')}</section>
<section class="section-block" data-title="Markers" id="markers"><div class="section-heading"><span class="section-kicker">Markers</span><h2>Evidence marker contract</h2></div><div class="marker-grid"><div><code>@EVIDENCE:{id}</code><span>Observed source or input.</span></div><div><code>?UNKNOWN:{id}</code><span>Material uncertainty.</span></div><div><code>#FINDING:{id}</code><span>Evidence-backed conclusion.</span></div><div><code>+ACTION:{id}</code><span>Bounded action or recommendation.</span></div><div><code>=VERIFY:{id}</code><span>Acceptance check and result.</span></div><div><code>!STOP:{reason}</code><span>Required halt condition.</span></div></div></section>
<section class="section-block" data-title="Reference library" id="reference-library">${libraryGrid(refs)}</section>`;
  return shell({ title: 'Reference', description: 'Mission Directives technical reference.', active: 'reference', section: 'Reference', content });
}

function manualPage(manual) {
  const content = `<section class="docs-intro section-block manual-hero" data-title="${escapeHtml(manual.title)}" id="manual"><div class="eyebrow-row"><span class="eyebrow">Repository manual</span><span class="pill">docs/${escapeHtml(manual.file)}</span></div><h1>${escapeHtml(manual.title)}</h1><p class="lead">Canonical documentation rendered from the repository <code>docs/</code> folder.</p><div class="manual-meta"><span>${escapeHtml(manual.category)}</span><a href="https://github.com/manojpisini/mission-directives/blob/main/docs/${escapeHtml(manual.file)}" rel="noreferrer" target="_blank">Source file</a></div></section><section class="section-block manual-body" data-title="Manual content" id="content">${manual.body}</section><nav class="page-nav"><a href="${base}manuals.html"><small>Back</small><strong>All manuals</strong></a><a href="${base}docs.html"><small>Docs</small><strong>Documentation home</strong></a></nav>`;
  return shell({ title: manual.title, description: `${manual.title} from the Mission Directives documentation set.`, active: 'manuals', section: 'Manual', content });
}

const manuals = await collectManuals();
await writeFile(path.join(siteRoot, 'public', 'docs.html'), docsHome(manuals), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'guides.html'), guidesPage(manuals), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'manuals.html'), manualsPage(manuals), 'utf8');
await writeFile(path.join(siteRoot, 'public', 'reference.html'), referencePage(manuals), 'utf8');
console.log(`Generated ${manuals.length} manual pages plus docs.html, guides.html, manuals.html, and reference.html`);
