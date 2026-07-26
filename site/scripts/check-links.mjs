import { access, readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const distRoot = path.join(siteRoot, 'dist');
const basePath = '/mission-directives/';

async function walk(root) {
  const files = [];
  for (const entry of await readdir(root, { withFileTypes: true })) {
    const absolute = path.join(root, entry.name);
    if (entry.isDirectory()) files.push(...(await walk(absolute)));
    else if (entry.isFile() && entry.name.endsWith('.html')) files.push(absolute);
  }
  return files;
}

async function exists(candidate) {
  try {
    await access(candidate);
    return true;
  } catch {
    return false;
  }
}

function targetFile(pathname) {
  const relative = pathname.slice(basePath.length);
  if (!relative || relative.endsWith('/')) return path.join(distRoot, relative, 'index.html');
  if (path.extname(relative)) return path.join(distRoot, relative);
  return path.join(distRoot, relative, 'index.html');
}

const failures = [];
const pages = await walk(distRoot);
const attribute = /(?:href|src)="([^"]+)"/g;

for (const page of pages) {
  const html = await readFile(page, 'utf8');
  const pageRoute =
    basePath + path.relative(distRoot, page).replaceAll('\\', '/').replace(/index\.html$/, '');
  for (const match of html.matchAll(attribute)) {
    const raw = match[1];
    if (
      raw.startsWith('#') ||
      raw.startsWith('mailto:') ||
      raw.startsWith('tel:') ||
      raw.startsWith('data:') ||
      raw.startsWith('javascript:')
    ) {
      continue;
    }
    const url = new URL(raw, `https://docs.local${pageRoute}`);
    if (url.origin !== 'https://docs.local') continue;
    if (!url.pathname.startsWith(basePath)) {
      failures.push(`${pageRoute} -> ${raw} (outside configured base)`);
      continue;
    }
    const output = targetFile(decodeURIComponent(url.pathname));
    if (!(await exists(output))) failures.push(`${pageRoute} -> ${raw}`);
  }
}

if (failures.length) {
  console.error(`Found ${failures.length} broken internal site links:`);
  for (const failure of failures.slice(0, 100)) console.error(`- ${failure}`);
  process.exitCode = 1;
} else {
  console.log(`Checked ${pages.length} HTML pages; all internal links resolve.`);
}
