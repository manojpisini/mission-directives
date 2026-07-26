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
    if (inCode) {
      code.push(line);
      continue;
    }
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

async function manualRows() {
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
      .find((part) => part && !part.startsWith('##')) ?? 'Mission Directives manual.';
    rows.push({ file, id, title, description: firstParagraph.replace(/\s+/g, ' ').slice(0, 150) });
    const html = manualPage({ title, file, body: markdownToHtml(source) });
    await mkdir(path.join(manualsRoot, id), { recursive: true });
    await writeFile(path.join(manualsRoot, id, 'index.html'), html, 'utf8');
  }
  return rows;
}

function manualPage({ title, file, body }) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="${escapeHtml(title)} from the Mission Directives documentation set." />
  <title>${escapeHtml(title)} — Mission Directives</title>
  <link rel="stylesheet" href="${base}styles.css" />
</head>
<body class="docs-page">
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="topbar"><div class="topbar__inner"><a class="brand" href="${base}index.html" aria-label="Mission Directives home"><span class="brand__mark" aria-hidden="true"><span class="brand__mark-line"></span><span class="brand__mark-line"></span><span class="brand__mark-dot"></span></span><span class="brand__copy"><strong>Mission Directives</strong><span>Manual</span></span></a><nav class="top-actions" aria-label="Manual navigation"><a href="${base}docs.html#manual-library">All manuals</a><a href="https://github.com/manojpisini/mission-directives/blob/main/docs/${escapeHtml(file)}" rel="noreferrer" target="_blank">Source</a></nav></div></header>
<main class="main manual-page" id="main-content"><div class="content-grid"><article class="doc-content"><section class="docs-intro section-block" data-title="${escapeHtml(title)}" id="manual"><div class="eyebrow-row"><span class="eyebrow">Repository manual</span><span class="pill">docs/${escapeHtml(file)}</span></div><h1>${escapeHtml(title)}</h1><p class="lead">Canonical documentation rendered from the repository <code>docs/</code> folder.</p></section><section class="section-block manual-body">${body}</section><nav class="page-nav"><a href="${base}docs.html#manual-library"><small>Back</small><strong>All manuals</strong></a><a href="${base}docs.html"><small>Docs</small><strong>Documentation home</strong></a></nav></article></div><footer class="footer"><span>Mission Directives Documentation</span><span>Generated from docs/${escapeHtml(file)}</span></footer></main>

</body>
</html>`;
}

function docsPage(manuals) {
  const manualLinks = manuals.map((manual) => `<a href="${base}reference/manuals/${manual.id}/"><span class="route-id">DOC</span><span><strong>${escapeHtml(manual.title)}</strong><small>${escapeHtml(manual.description)}</small></span><span>→</span></a>`).join('\n');
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="Mission Directives documentation, guides, user manual, and reference." />
  <title>Mission Directives — Documentation</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body class="docs-page">
<a class="skip-link" href="#main-content">Skip to content</a>
<header class="topbar"><div class="topbar__inner"><button aria-expanded="false" aria-label="Open navigation" class="icon-button mobile-menu" id="mobileMenu"><svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h16"></path></svg></button><a aria-label="Mission Directives home" class="brand" href="index.html"><span aria-hidden="true" class="brand__mark"><span class="brand__mark-line"></span><span class="brand__mark-line"></span><span class="brand__mark-dot"></span></span><span class="brand__copy"><strong>Mission Directives</strong><span>Documentation</span></span></a><button aria-haspopup="dialog" class="search-trigger" id="searchTrigger"><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"></circle><path d="m16 16 4 4"></path></svg><span>Search documentation</span><kbd>Ctrl K</kbd></button><nav aria-label="External links" class="top-actions"><a href="index.html">Project home</a><a href="#manual-library">Manuals</a><a class="github-link" href="https://github.com/manojpisini/mission-directives" rel="noreferrer" target="_blank"><span>GitHub</span></a></nav></div></header>
<div class="layout"><aside aria-label="Documentation navigation" class="sidebar" id="sidebar"><div class="sidebar__scroll"><div class="version-panel"><div><span>Documentation</span><strong>Version 1.8.3</strong></div><span class="status-dot">Stable</span></div><nav class="docs-nav" id="docsNav"><section class="nav-group"><p>Start here</p><a class="active" href="#docs-overview"><span>Overview</span></a><a href="#quick-start"><span>Quick start</span></a><a href="#core-concepts"><span>Core concepts</span></a></section><section class="nav-group"><p>Operate</p><a href="#installation"><span>Installation</span></a><a href="#routing"><span>Routing</span></a><a href="#operating-modes"><span>Operating modes</span></a><a href="#verification"><span>Verification</span></a></section><section class="nav-group"><p>Reference</p><a href="#command-reference"><span>Commands</span></a><a href="#manual-library"><span>All manuals</span></a><a href="#repository-layout"><span>Repository layout</span></a></section></nav><div class="sidebar-help"><span class="sidebar-help__icon">?</span><div><strong>Need help?</strong><p>Start with route, explain, plan, then verify.</p></div></div></div></aside>
<main class="main" id="main-content"><div class="content-grid"><article class="doc-content">
<section class="docs-intro section-block" data-title="Documentation overview" id="docs-overview"><div class="eyebrow-row"><span class="eyebrow">Mission Directives</span><span class="pill">v1.8.3</span></div><h1>Documentation</h1><p class="lead">Real guides, manuals, operating rules, command references, and generated manual pages for the Mission Directives prompt orchestration suite.</p><div class="docs-intro__actions"><a class="button button--primary" href="#quick-start">Start with Quick Start</a><a class="button button--secondary" href="#manual-library">Browse manuals</a></div></section>
<section class="section-block" data-title="Quick start" id="quick-start"><div class="section-heading"><span class="section-kicker">Quick start</span><h2>Run the suite locally</h2><p>Use Python 3.12, install the development dependencies, route a real request, and validate the repository.</p></div><div class="steps"><div class="step"><span class="step__number">1</span><div><h3>Clone and enter</h3><div class="code-block"><div class="code-block__bar"><span>Terminal</span><button class="copy-button">Copy</button></div><pre><code>git clone https://github.com/manojpisini/mission-directives.git
cd mission-directives</code></pre></div></div></div><div class="step"><span class="step__number">2</span><div><h3>Create an environment</h3><div class="platform-card"><div class="tabs" role="tablist"><button aria-selected="true" class="tab active" data-tab="windows" role="tab">Windows</button><button aria-selected="false" class="tab" data-tab="macos" role="tab">macOS</button><button aria-selected="false" class="tab" data-tab="linux" role="tab">Linux</button></div><div class="tab-panel active" id="windows" role="tabpanel"><div class="code-block code-block--flush"><div class="code-block__bar"><span>PowerShell</span><button class="copy-button">Copy</button></div><pre><code>py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1</code></pre></div></div><div class="tab-panel" id="macos" role="tabpanel"><div class="code-block code-block--flush"><div class="code-block__bar"><span>Terminal</span><button class="copy-button">Copy</button></div><pre><code>python3.12 -m venv .venv
source .venv/bin/activate</code></pre></div></div><div class="tab-panel" id="linux" role="tabpanel"><div class="code-block code-block--flush"><div class="code-block__bar"><span>Terminal</span><button class="copy-button">Copy</button></div><pre><code>python3.12 -m venv .venv
source .venv/bin/activate</code></pre></div></div></div></div></div><div class="step"><span class="step__number">3</span><div><h3>Install and validate</h3><div class="code-block"><div class="code-block__bar"><span>Terminal</span><button class="copy-button">Copy</button></div><pre><code>python -m pip install -r requirements-dev.txt
python tools/md.py route "MD advanced audit fix verify repository"
python tools/validate_suite.py</code></pre></div></div></div></div></section>
<section class="section-block" data-title="Core concepts" id="core-concepts"><div class="section-heading"><span class="section-kicker">Concept model</span><h2>Resolve only what is needed</h2><p>The router selects the smallest coherent graph before loading prompt bodies. Execution stays inside declared mode, evidence, skill, approval, and verification contracts.</p></div><div class="workflow" aria-label="Mission Directives workflow"><div class="workflow__node"><span>01</span><strong>Request</strong><p>Intent, exact IDs, shortcuts, depth, and assurance modifiers.</p></div><div class="workflow__arrow">→</div><div class="workflow__node"><span>02</span><strong>Route</strong><p>Keyword concepts, rarity-aware scoring, and route hints.</p></div><div class="workflow__arrow">→</div><div class="workflow__node"><span>03</span><strong>Explain</strong><p>Modes, inputs, skills, approvals, and expected artifacts.</p></div><div class="workflow__arrow">→</div><div class="workflow__node"><span>04</span><strong>Verify</strong><p>Evidence markers, receipts, residuals, and closure.</p></div></div></section>
<section class="section-block" data-title="Installation" id="installation"><div class="section-heading"><span class="section-kicker">Guide</span><h2>Install into a working project</h2><p>The installer copies the runtime payload required for routing and execution. Repository-only tests, CI, validators, imports, and site sources stay upstream.</p></div><div class="code-block"><div class="code-block__bar"><span>Portable Python</span><button class="copy-button">Copy</button></div><pre><code>python tools/install.py /absolute/path/to/project --dry-run
python tools/install.py /absolute/path/to/project</code></pre></div><div class="callout-grid"><aside class="callout callout--note"><span class="callout__icon">i</span><div><strong>Payload boundary</strong><p>Runtime files are allowlisted by <code>config/runtime_payload.json</code>; source-only validation assets are not installed.</p></div></aside><aside class="callout callout--note"><span class="callout__icon">i</span><div><strong>Replacement</strong><p>Use <code>--replace</code> only for an intentional update. The installer creates a backup first.</p></div></aside></div></section>
<section class="section-block" data-title="Routing requests" id="routing"><div class="section-heading"><span class="section-kicker">Router</span><h2>Route full requests instead of guessing IDs</h2><p>Pass the whole user request. The router handles exact IDs, natural intent, shortcuts, typos, field evidence, graph fit, and calibrated no-match behavior.</p></div><div class="code-block"><div class="code-block__bar"><span>Common commands</span><button class="copy-button">Copy</button></div><pre><code>python tools/md.py route "MD advanced repository mission drift and simplification audit"
python tools/md.py lookup "cleanup dead code safely" --limit 8
python tools/md.py compare C-108 C-63
python tools/md.py explain C-108</code></pre></div><div class="route-cards"><article><strong>Metadata first</strong><p>Selection uses catalogs, policies, keywords, and scenarios before opening prompt bodies.</p></article><article><strong>Small graph</strong><p>Composite scenarios are used only when one prompt cannot own the full outcome.</p></article><article><strong>Honest threshold</strong><p>Low-confidence requests ask one route-changing question instead of forcing a route.</p></article></div></section>
<section class="section-block" data-title="Operating modes" id="operating-modes"><div class="section-heading"><span class="section-kicker">Authority</span><h2>Modes define what may happen</h2><p>Drafting is not publication, planning is not execution, and a local change is not permission for an external action.</p></div><div class="table-card"><table><thead><tr><th>Mode</th><th>Permitted outcome</th></tr></thead><tbody><tr><td><code>AUDIT_ONLY</code></td><td>Inspect and report without mutation.</td></tr><tr><td><code>PLAN_ONLY</code></td><td>Produce plans, requirements, and acceptance criteria.</td></tr><tr><td><code>DRAFT_ONLY</code></td><td>Create local drafts without implying approval or publication.</td></tr><tr><td><code>APPLY_SAFE</code></td><td>Make reversible local changes inside explicit authority.</td></tr><tr><td><code>APPLY_APPROVED</code></td><td>Perform the exact approved consequential action with receipts.</td></tr><tr><td><code>VERIFY_ONLY</code></td><td>Verify a claim or artifact without changing it.</td></tr></tbody></table></div></section>
<section class="section-block" data-title="Evidence and verification" id="verification"><div class="section-heading"><span class="section-kicker">Verification</span><h2>Completion requires evidence</h2><p>Prompt output uses compact markers to distinguish observations, uncertainty, findings, actions, verification, and mandatory stops.</p></div><div class="marker-grid"><div><code>@EVIDENCE:{id}</code><span>Source, observation, or input</span></div><div><code>?UNKNOWN:{id}</code><span>Material unresolved uncertainty</span></div><div><code>#FINDING:{id}</code><span>Evidence-backed issue or conclusion</span></div><div><code>+ACTION:{id}</code><span>Bounded proposed or executed action</span></div><div><code>=VERIFY:{id}</code><span>Acceptance criterion and result</span></div><div><code>!STOP:{reason}</code><span>Mandatory stop condition</span></div></div><aside class="callout callout--warning"><span class="callout__icon">!</span><div><strong>Static validation is bounded</strong><p>It proves structural integrity and deterministic checks. It does not certify live model quality or external-world success.</p></div></aside></section>
<section class="section-block" data-title="Command reference" id="command-reference"><div class="section-heading"><span class="section-kicker">Commands</span><h2>Operator command reference</h2><p>These commands cover daily routing, inspection, dry-run planning, installation, and validation.</p></div><div class="command-stack"><div><code>python tools/md.py route &lt;request&gt;</code><p>Select the smallest suitable prompt, scenario, or workflow graph.</p></div><div><code>python tools/md.py explain &lt;MD-ID|C-ID&gt;</code><p>Inspect inputs, allowed modes, approvals, skills, and verification duties.</p></div><div><code>python tools/md.py plan &lt;target&gt; --mode AUDIT_ONLY --root . --dry-run</code><p>Produce a non-mutating execution plan.</p></div><div><code>python tools/install.py &lt;project&gt; --dry-run</code><p>Preview runtime installation into a target project.</p></div><div><code>python tools/validate_suite.py</code><p>Run structural validation, deterministic tests, fixture coverage, and manifest integrity checks.</p></div></div></section>
<section class="section-block" data-title="Manual library" id="manual-library"><div class="section-heading"><span class="section-kicker">All docs</span><h2>Every repository manual</h2><p>Generated from the root <code>docs/</code> folder. These pages preserve the source manuals while giving the static site full coverage.</p></div><div class="route-list">${manualLinks}</div></section>
<section class="section-block" data-title="Repository layout" id="repository-layout"><div class="section-heading"><span class="section-kicker">Reference</span><h2>Repository layout</h2><p>Core runtime files, source-only validation files, manuals, and site assets stay separated.</p></div><div class="file-tree"><div><code>prompts/</code><span>Canonical prompt bodies</span></div><div><code>catalog.json</code><span>Prompt identities and metadata</span></div><div><code>SCENARIO_CATALOG.json</code><span>Atomic and composite route graphs</span></div><div><code>config/</code><span>Routing keywords, runtime payloads, templates, and capability graph</span></div><div><code>policies/</code><span>Authorization, routing, evidence, and loop policies</span></div><div><code>schemas/</code><span>Typed contracts and imported source schemas</span></div><div><code>tools/</code><span>Router, installer, generators, validators, and wrappers</span></div><div><code>docs/</code><span>User, operator, authoring, security, and maintenance manuals</span></div><div><code>site/</code><span>Static documentation site source</span></div></div></section>
<nav aria-label="Page navigation" class="page-nav"><a href="index.html"><small>Project</small><strong>← Landing page</strong></a><a href="#manual-library"><small>Reference</small><strong>Manual library →</strong></a></nav>
</article><aside aria-label="On this page" class="toc"><div class="toc__inner"><p>On this page</p><a class="active" href="#docs-overview">Overview</a><a href="#quick-start">Quick start</a><a href="#core-concepts">Core concepts</a><a href="#installation">Installation</a><a href="#routing">Routing</a><a href="#operating-modes">Modes</a><a href="#verification">Verification</a><a href="#command-reference">Commands</a><a href="#manual-library">Manuals</a><a href="#repository-layout">Layout</a></div></aside></div><footer class="footer"><span>Mission Directives Documentation</span><span>Light mode · Mild sage accent system</span></footer></main></div>
<div aria-label="Search documentation" aria-modal="true" class="search-dialog" hidden id="searchDialog" role="dialog"><div class="search-dialog__panel"><div class="search-input-wrap"><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"></circle><path d="m16 16 4 4"></path></svg><input autocomplete="off" id="searchInput" placeholder="Search guides, commands, and concepts..." type="search"/><kbd>Esc</kbd></div><div class="search-results" id="searchResults"></div></div></div><div class="sidebar-backdrop" hidden id="sidebarBackdrop"></div><script is:inline src="app.js"></script>
</body>
</html>`;
}

const manuals = await manualRows();
await writeFile(path.join(siteRoot, 'public', 'docs.html'), docsPage(manuals), 'utf8');
console.log(`Generated ${manuals.length} manual pages and docs.html`);