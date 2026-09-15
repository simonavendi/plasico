/**
 * Megamag-style header interactions for Plasico.
 * Categories mega panel, mobile menu, search toggle.
 */
(function initHeaderCategories() {
  const header = document.getElementById('site-header');
  const toggle = document.getElementById('categories-toggle');
  const panel = document.getElementById('categories-panel');
  const backdrop = document.getElementById('categories-backdrop');
  const mapUrl = document.body?.dataset.categoryMap || 'category-map.json';
  const searchToggle = header?.querySelector('[data-search-toggle]');
  const mobileMenuToggle = header?.querySelector('[data-mobile-menu-toggle]');
  const mobileMenu = header?.querySelector('[data-mobile-menu]');
  const searchInput = document.getElementById('header-search');

  function isOpen() {
    return panel?.classList.contains('is-open');
  }
  function closeHeaderCategories() {
    panel?.classList.remove('is-open');
    panel?.setAttribute('aria-hidden', 'true');
    backdrop?.classList.remove('is-visible');
    backdrop?.setAttribute('aria-hidden', 'true');
    toggle?.setAttribute('aria-expanded', 'false');
    toggle?.classList.remove('is-open');
  }
  function openHeaderCategories() {
    closeMobileMenu();
    panel?.classList.add('is-open');
    panel?.setAttribute('aria-hidden', 'false');
    backdrop?.classList.add('is-visible');
    backdrop?.setAttribute('aria-hidden', 'false');
    toggle?.setAttribute('aria-expanded', 'true');
    toggle?.classList.add('is-open');
  }

  function closeMobileMenu() {
    mobileMenu?.classList.remove('is-open');
    mobileMenu?.setAttribute('hidden', '');
    mobileMenuToggle?.setAttribute('aria-expanded', 'false');
  }
  function openMobileMenu() {
    closeHeaderCategories();
    mobileMenu?.classList.add('is-open');
    mobileMenu?.removeAttribute('hidden');
    mobileMenuToggle?.setAttribute('aria-expanded', 'true');
  }

  toggle?.addEventListener('click', () => {
    if (isOpen()) closeHeaderCategories();
    else openHeaderCategories();
  });
  backdrop?.addEventListener('click', () => {
    closeHeaderCategories();
    closeMobileMenu();
  });
  mobileMenuToggle?.addEventListener('click', () => {
    if (mobileMenu?.classList.contains('is-open')) closeMobileMenu();
    else openMobileMenu();
  });
  searchToggle?.addEventListener('click', () => {
    const open = header?.classList.toggle('search-open');
    searchToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) searchInput?.focus();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (isOpen()) {
        closeHeaderCategories();
        toggle?.focus();
      }
      closeMobileMenu();
      header?.classList.remove('search-open');
      searchToggle?.setAttribute('aria-expanded', 'false');
    }
  });
  document.addEventListener('click', (e) => {
    if (!isOpen()) return;
    const t = e.target;
    if (toggle?.contains(t) || panel?.contains(t)) return;
    closeHeaderCategories();
  });

  const compareLink = document.getElementById('header-compare-link');
  compareLink?.addEventListener('click', (e) => {
    const bar = document.getElementById('plasico-compare-bar');
    if (bar && !bar.hasAttribute('hidden')) {
      e.preventDefault();
      bar.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  });

  window.__closeHeaderCategories = closeHeaderCategories;
  window.__closeHeaderCategoriesPanel = closeHeaderCategories;

  function pagePrefix() {
    const idx = mapUrl.lastIndexOf('/');
    return idx >= 0 ? mapUrl.slice(0, idx + 1) : '';
  }
  function resolveNavUrl(item) {
    const prefix = pagePrefix();
    if (item.localUrl) return prefix + item.localUrl;
    if (item.url && !item.url.startsWith('https://plasico.bg') && !item.url.startsWith('http')) {
      return prefix + item.url.replace(/^\//, '');
    }
    return item.url || '#';
  }
  function navigateHeaderUrl(url, external) {
    if (!url || url === '#') return;
    closeHeaderCategories();
    if (external || url.startsWith('https://')) {
      window.open(url, external ? '_blank' : '_self', external ? 'noopener' : undefined);
      return;
    }
    if (url.startsWith('#')) {
      const target = document.querySelector(url.split('?')[0]);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      else window.location.href = url;
      return;
    }
    window.location.href = url;
  }

  function buildMegaCell(category) {
    const subs = category.subcategories || [];
    const hasSubs = subs.length > 0;
    const cell = document.createElement('div');
    cell.className = 'header-cat-mega-cell';
    const dest = resolveNavUrl(category);
    const isExternal = category.external || (!category.localUrl && dest.startsWith('https://'));
    const parent = hasSubs ? document.createElement('button') : document.createElement('a');
    parent.className = 'header-cat-mega-parent';
    parent.innerHTML =
      '<span class="header-cat-mega-parent__icon" aria-hidden="true">' +
      '<span class="material-symbols-outlined">' +
      (category.materialIcon || 'category') +
      '</span></span>' +
      '<span class="header-cat-mega-parent__label">' +
      category.name +
      '</span>' +
      (hasSubs
        ? '<span class="material-symbols-outlined header-cat-mega-parent__chevron">expand_more</span>'
        : '');
    if (!hasSubs) {
      parent.href = dest;
      if (isExternal) {
        parent.target = '_blank';
        parent.rel = 'noopener';
      }
      parent.addEventListener('click', (e) => {
        if (!isExternal) {
          e.preventDefault();
          navigateHeaderUrl(dest, false);
        } else {
          closeHeaderCategories();
        }
      });
    } else {
      parent.type = 'button';
      parent.setAttribute('aria-expanded', 'false');
      parent.addEventListener('click', () => {
        const open = cell.classList.toggle('is-expanded');
        parent.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }
    cell.appendChild(parent);
    if (hasSubs) {
      const sub = document.createElement('div');
      sub.className = 'header-cat-mega-subs';
      subs.forEach((s) => {
        const a = document.createElement('a');
        a.className = 'header-cat-mega-sub';
        a.textContent = s.name;
        const subDest = resolveNavUrl(s);
        a.href = subDest;
        if (s.action === 'external' || (!s.localUrl && subDest.startsWith('https://'))) {
          a.target = '_blank';
          a.rel = 'noopener';
        }
        a.addEventListener('click', (e) => {
          if (a.target !== '_blank') {
            e.preventDefault();
            navigateHeaderUrl(subDest, false);
          } else {
            closeHeaderCategories();
          }
        });
        sub.appendChild(a);
      });
      cell.appendChild(sub);
    }
    return cell;
  }

  function renderSiteCategories(siteCategories) {
    const root = document.getElementById('site-categories-panel-mobile');
    if (!root) return;
    root.innerHTML = '';
    const grid = document.createElement('div');
    grid.className = 'header-cat-mega-grid';
    (siteCategories || []).forEach((cat) => grid.appendChild(buildMegaCell(cat)));
    root.appendChild(grid);
  }

  window.__renderHeaderSiteCategories = renderSiteCategories;
  window.__buildHeaderMegaCell = buildMegaCell;

  fetch(mapUrl)
    .then((res) => (res.ok ? res.json() : null))
    .then((map) => {
      if (map?.siteCategories) renderSiteCategories(map.siteCategories);
    })
    .catch(() => {});
})();
