(() => {
  const searchDialog = document.getElementById('searchDialog');
  const searchTrigger = document.getElementById('searchTrigger');
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');
  const sections = [...document.querySelectorAll('.section-block')];
  const navLinks = [...document.querySelectorAll('.docs-nav a')];
  const tocLinks = [...document.querySelectorAll('.toc a')];
  const mobileMenu = document.getElementById('mobileMenu');
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebarBackdrop');

  const searchIndex = sections.map(section => ({
    id: section.id,
    title: section.dataset.title || section.querySelector('h2, h1')?.textContent || section.id,
    text: section.textContent.replace(/\s+/g, ' ').trim().toLowerCase(),
    category: section.querySelector('.section-kicker, .eyebrow')?.textContent || 'Documentation'
  }));

  function openSearch() {
    searchDialog.hidden = false;
    document.body.style.overflow = 'hidden';
    window.setTimeout(() => searchInput.focus(), 10);
  }

  function closeSearch() {
    searchDialog.hidden = true;
    document.body.style.overflow = '';
    searchInput.value = '';
    renderResults('');
  }

  function renderResults(query) {
    const normalized = query.trim().toLowerCase();
    const matches = normalized
      ? searchIndex.filter(item => item.title.toLowerCase().includes(normalized) || item.text.includes(normalized)).slice(0, 8)
      : searchIndex.slice(0, 5);

    searchResults.innerHTML = `<p class="search-label">${normalized ? `${matches.length} result${matches.length === 1 ? '' : 's'}` : 'Suggested'}</p>` +
      (matches.length
        ? matches.map(item => `<button data-target="${item.id}"><span>${item.title}</span><small>${item.category}</small></button>`).join('')
        : '<p style="padding:18px 10px;color:var(--ink-muted);font-size:12px">No matching documentation found.</p>');
  }

  searchTrigger?.addEventListener('click', openSearch);
  searchDialog?.addEventListener('click', event => { if (event.target === searchDialog) closeSearch(); });
  searchInput?.addEventListener('input', event => renderResults(event.target.value));
  searchResults?.addEventListener('click', event => {
    const button = event.target.closest('[data-target]');
    if (!button) return;
    const target = document.getElementById(button.dataset.target);
    closeSearch();
    target?.scrollIntoView({ behavior: 'smooth' });
  });

  document.addEventListener('keydown', event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      openSearch();
    }
    if (event.key === 'Escape' && searchDialog && !searchDialog.hidden) closeSearch();
  });

  document.querySelectorAll('.copy-button').forEach(button => {
    button.addEventListener('click', async () => {
      const code = button.closest('.code-block').querySelector('code').textContent;
      try {
        await navigator.clipboard.writeText(code);
        const old = button.textContent;
        button.textContent = 'Copied';
        setTimeout(() => button.textContent = old, 1400);
      } catch {
        button.textContent = 'Select text';
      }
    });
  });

  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const card = tab.closest('.platform-card');
      card.querySelectorAll('.tab').forEach(item => {
        item.classList.toggle('active', item === tab);
        item.setAttribute('aria-selected', item === tab ? 'true' : 'false');
      });
      card.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === tab.dataset.tab);
      });
    });
  });

  const observer = new IntersectionObserver(entries => {
    const visible = entries
      .filter(entry => entry.isIntersecting)
      .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (!visible) return;
    const id = visible.target.id;
    [...navLinks, ...tocLinks].forEach(link => {
      link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
    });
  }, { rootMargin: '-22% 0px -68% 0px', threshold: 0 });

  sections.forEach(section => observer.observe(section));

  function closeSidebar() {
    sidebar.classList.remove('open');
    backdrop.hidden = true;
    mobileMenu.setAttribute('aria-expanded', 'false');
  }

  mobileMenu?.addEventListener('click', () => {
    const open = sidebar.classList.toggle('open');
    backdrop.hidden = !open;
    mobileMenu.setAttribute('aria-expanded', String(open));
  });
  backdrop?.addEventListener('click', closeSidebar);
  navLinks.forEach(link => link.addEventListener('click', closeSidebar));

  renderResults('');
})();
