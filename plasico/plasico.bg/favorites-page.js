(function initFavoritesPage() {
  const FAV_STORAGE_KEY = 'plasico-hss2026-favs';
  const FAV_META_KEY = 'plasico-hss2026-fav-meta';
  const listEl = document.getElementById('favorites-list');
  const emptyEl = document.getElementById('favorites-empty');
  const countEl = document.getElementById('favorites-count');
  const headerFavBadge = document.getElementById('header-fav-badge');

  if (!listEl || !emptyEl) return;

  function readFavs() {
    try {
      const raw = localStorage.getItem(FAV_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed.map(String) : [];
    } catch {
      return [];
    }
  }

  function writeFavs(ids) {
    localStorage.setItem(FAV_STORAGE_KEY, JSON.stringify(ids));
  }

  function readFavMeta() {
    try {
      const raw = localStorage.getItem(FAV_META_KEY);
      const parsed = raw ? JSON.parse(raw) : {};
      return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
    } catch {
      return {};
    }
  }

  function writeFavMeta(meta) {
    localStorage.setItem(FAV_META_KEY, JSON.stringify(meta));
  }

  function formatPrice(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return '';
    return num.toFixed(2) + ' €';
  }

  function updateHeaderFavBadge(count) {
    if (!headerFavBadge) return;
    headerFavBadge.textContent = String(count);
    headerFavBadge.classList.toggle('is-empty', count === 0);
    headerFavBadge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function removeFavorite(id) {
    const ids = readFavs().filter((x) => x !== id);
    const meta = readFavMeta();
    delete meta[id];
    writeFavs(ids);
    writeFavMeta(meta);
    render();
  }

  function render() {
    const ids = readFavs();
    const meta = readFavMeta();
    updateHeaderFavBadge(ids.length);
    if (countEl) {
      countEl.textContent =
        ids.length === 0
          ? 'Няма запазени продукти'
          : ids.length === 1
            ? '1 продукт'
            : ids.length + ' продукта';
    }

    if (!ids.length) {
      listEl.hidden = true;
      listEl.innerHTML = '';
      emptyEl.hidden = false;
      return;
    }

    emptyEl.hidden = true;
    listEl.hidden = false;
    listEl.innerHTML = ids
      .map((id) => {
        const item = meta[id] || {};
        const title = item.title || 'Продукт №' + id;
        const href = item.href || 'https://plasico.bg/';
        const image = item.image || '';
        const alt = item.alt || title;
        const price = formatPrice(item.price);
        const imgHtml = image
          ? `<img src="${escapeHtml(image)}" alt="${escapeHtml(alt)}" loading="lazy" class="favorites-card__img"/>`
          : `<span class="favorites-card__img-fallback material-symbols-outlined" aria-hidden="true">inventory_2</span>`;

        return (
          `<article class="favorites-card" data-id="${escapeHtml(id)}">` +
          `<a class="favorites-card__media" href="${escapeHtml(href)}">${imgHtml}</a>` +
          `<div class="favorites-card__body">` +
          `<h2 class="favorites-card__title"><a href="${escapeHtml(href)}">${escapeHtml(title)}</a></h2>` +
          (price ? `<p class="favorites-card__price">${escapeHtml(price)}</p>` : '') +
          `<div class="favorites-card__actions">` +
          `<a class="favorites-card__open" href="${escapeHtml(href)}">Виж продукта</a>` +
          `<button type="button" class="favorites-card__remove" data-remove-id="${escapeHtml(id)}">Премахни</button>` +
          `</div></div></article>`
        );
      })
      .join('');
  }

  listEl.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-remove-id]');
    if (!btn) return;
    e.preventDefault();
    removeFavorite(String(btn.getAttribute('data-remove-id') || ''));
  });

  window.addEventListener('storage', (e) => {
    if (e.key === FAV_STORAGE_KEY || e.key === FAV_META_KEY) render();
  });

  render();
})();
