(function initProductCardActions() {
  const FAV_STORAGE_KEY = 'plasico-hss2026-favs';
  const FAV_META_KEY = 'plasico-hss2026-fav-meta';
  const COMPARE_STORAGE_KEY = 'plasico-hss2026-compare';
  const COMPARE_META_KEY = 'plasico-hss2026-compare-meta';
  const COMPARE_MAX = 4;
  const COMPARE_TOOLTIP = 'сравни два или повече продукта';
  const COMPARE_ORANGE = '#ff5815';

  const grid = document.getElementById('product-grid');
  const headerFavBadge = document.getElementById('header-fav-badge');
  const headerCompareBadge = document.getElementById('header-compare-badge');

  function readFavs() {
    try {
      const raw = localStorage.getItem(FAV_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return new Set(Array.isArray(parsed) ? parsed.map(String) : []);
    } catch {
      return new Set();
    }
  }

  function writeFavs(favs) {
    localStorage.setItem(FAV_STORAGE_KEY, JSON.stringify(Array.from(favs)));
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

  function readCompareIds() {
    try {
      const raw = localStorage.getItem(COMPARE_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed.map(String) : [];
    } catch {
      return [];
    }
  }

  function writeCompareIds(ids) {
    localStorage.setItem(COMPARE_STORAGE_KEY, JSON.stringify(ids.map(String)));
  }

  function readCompareMeta() {
    try {
      const raw = localStorage.getItem(COMPARE_META_KEY);
      const parsed = raw ? JSON.parse(raw) : {};
      return parsed && typeof parsed === 'object' && !Array.isArray(parsed) ? parsed : {};
    } catch {
      return {};
    }
  }

  function writeCompareMeta(meta) {
    localStorage.setItem(COMPARE_META_KEY, JSON.stringify(meta));
  }

  function resolveImageUrl(src) {
    if (!src) return '';
    try {
      return new URL(src, window.location.href).href;
    } catch {
      return src;
    }
  }

  function extractProductMeta(article) {
    if (!article) return null;
    const id = String(article.dataset.id || '');
    if (!id) return null;
    const titleLink = article.querySelector('h4 a') || article.querySelector('a[href*=".html"]');
    const title = titleLink ? titleLink.textContent.trim() : 'Продукт';
    const href = titleLink ? titleLink.getAttribute('href') || '' : '';
    const img = article.querySelector('.aspect-square img') || article.querySelector('img');
    const rawSrc =
      (img && (img.currentSrc || img.getAttribute('src') || img.getAttribute('data-src'))) || '';
    const price = parseFloat(article.dataset.price);
    return {
      id,
      title,
      href,
      image: resolveImageUrl(rawSrc),
      alt: (img && img.getAttribute('alt')) || title,
      price: Number.isFinite(price) ? price : null,
    };
  }

  function updateHeaderFavBadge(favs) {
    if (!headerFavBadge) return;
    const count = favs.size;
    headerFavBadge.textContent = String(count);
    headerFavBadge.classList.toggle('is-empty', count === 0);
    headerFavBadge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
  }

  function updateHeaderCompareBadge(ids) {
    if (!headerCompareBadge) return;
    const count = Array.isArray(ids) ? ids.length : 0;
    headerCompareBadge.textContent = String(count);
    headerCompareBadge.classList.toggle('is-empty', count === 0);
    headerCompareBadge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
  }

  function setFavButtonState(btn, favorited) {
    btn.classList.toggle('is-favorited', favorited);
    btn.setAttribute('aria-pressed', favorited ? 'true' : 'false');
    btn.setAttribute(
      'aria-label',
      favorited ? 'Премахни от любими' : 'Добави в любими'
    );
  }

  function setCompareButtonState(btn, selected) {
    btn.classList.toggle('is-compared', selected);
    btn.setAttribute('aria-pressed', selected ? 'true' : 'false');
    btn.setAttribute(
      'aria-label',
      selected ? 'Премахни от сравнение' : COMPARE_TOOLTIP
    );
    btn.title = COMPARE_TOOLTIP;
    const icon = btn.querySelector('.material-symbols-outlined');
    if (icon) {
      icon.style.fontVariationSettings = selected
        ? "'FILL' 1, 'wght' 600, 'GRAD' 0, 'opsz' 24"
        : "'FILL' 0, 'wght' 600, 'GRAD' 0, 'opsz' 24";
    }
  }

  function syncCompareButtons(ids) {
    if (!grid) return;
    const selected = new Set(ids);
    grid.querySelectorAll('.product-compare-btn').forEach((btn) => {
      const article = btn.closest('article[data-id]');
      const id = article ? String(article.dataset.id || '') : '';
      setCompareButtonState(btn, selected.has(id));
    });
  }

  function formatPrice(price) {
    if (!Number.isFinite(price)) return '';
    return (
      price.toLocaleString('bg-BG', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }) + ' лв.'
    );
  }

  function ensureCompareBar() {
    let bar = document.getElementById('plasico-compare-bar');
    if (bar) return bar;

    bar = document.createElement('div');
    bar.id = 'plasico-compare-bar';
    bar.className = 'plasico-compare-bar';
    bar.setAttribute('hidden', '');
    bar.innerHTML =
      '<div class="plasico-compare-bar__inner">' +
      '<div class="plasico-compare-bar__meta">' +
      '<span class="plasico-compare-bar__title">Сравнение</span>' +
      '<span class="plasico-compare-bar__count" id="plasico-compare-count">0</span>' +
      '</div>' +
      '<div class="plasico-compare-bar__items" id="plasico-compare-items"></div>' +
      '<div class="plasico-compare-bar__actions">' +
      '<button type="button" class="plasico-compare-bar__clear" id="plasico-compare-clear">Изчисти</button>' +
      '<button type="button" class="plasico-compare-bar__go" id="plasico-compare-go" disabled>Сравни</button>' +
      '</div>' +
      '</div>';
    document.body.appendChild(bar);

    bar.addEventListener('click', (e) => {
      const removeBtn = e.target.closest('[data-compare-remove]');
      if (removeBtn) {
        e.preventDefault();
        removeFromCompare(String(removeBtn.getAttribute('data-compare-remove') || ''));
        return;
      }
      if (e.target.closest('#plasico-compare-clear')) {
        e.preventDefault();
        clearCompare();
        return;
      }
      if (e.target.closest('#plasico-compare-go')) {
        e.preventDefault();
        openCompareSummary();
      }
    });

    return bar;
  }

  function renderCompareBar() {
    const ids = readCompareIds();
    const meta = readCompareMeta();
    const bar = ensureCompareBar();
    const countEl = document.getElementById('plasico-compare-count');
    const itemsEl = document.getElementById('plasico-compare-items');
    const goBtn = document.getElementById('plasico-compare-go');

    if (countEl) countEl.textContent = String(ids.length);
    if (goBtn) {
      goBtn.disabled = ids.length < 2;
      goBtn.title =
        ids.length < 2
          ? COMPARE_TOOLTIP
          : 'Сравни избраните продукти';
    }

    if (itemsEl) {
      itemsEl.innerHTML = ids
        .map((id) => {
          const item = meta[id] || { id, title: 'Продукт', image: '', alt: 'Продукт' };
          const img = item.image
            ? `<img src="${item.image}" alt="${escapeAttr(item.alt || item.title || '')}" loading="lazy" />`
            : '<span class="plasico-compare-bar__placeholder" aria-hidden="true"></span>';
          return (
            `<div class="plasico-compare-bar__item" data-id="${escapeAttr(id)}">` +
            `<div class="plasico-compare-bar__thumb">${img}</div>` +
            `<button type="button" class="plasico-compare-bar__remove" data-compare-remove="${escapeAttr(id)}" aria-label="Премахни от сравнение">` +
            `<span class="material-symbols-outlined" aria-hidden="true">close</span>` +
            `</button>` +
            `</div>`
          );
        })
        .join('');
    }

    // Live Plasico shows the bar once any product is compared; CTA needs 2+.
    if (ids.length > 0) {
      bar.removeAttribute('hidden');
      bar.classList.add('is-visible');
      document.body.classList.add('has-compare-bar');
    } else {
      bar.setAttribute('hidden', '');
      bar.classList.remove('is-visible');
      document.body.classList.remove('has-compare-bar');
    }

    syncCompareButtons(ids);
    updateHeaderCompareBadge(ids);
  }

  function escapeAttr(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function openCompareSummary() {
    const ids = readCompareIds();
    if (ids.length < 2) return;
    const meta = readCompareMeta();
    const lines = ids.map((id, i) => {
      const item = meta[id] || { title: id, price: null };
      const price = formatPrice(item.price);
      return `${i + 1}. ${item.title || id}${price ? ' — ' + price : ''}`;
    });
    window.alert(
      'Сравнение на продукти (' +
        ids.length +
        '):\n\n' +
        lines.join('\n') +
        '\n\n(' +
        COMPARE_TOOLTIP +
        ')'
    );
  }

  function removeFromCompare(id) {
    if (!id) return;
    const ids = readCompareIds().filter((x) => x !== id);
    const meta = readCompareMeta();
    delete meta[id];
    writeCompareIds(ids);
    writeCompareMeta(meta);
    renderCompareBar();
  }

  function clearCompare() {
    writeCompareIds([]);
    writeCompareMeta({});
    renderCompareBar();
  }

  function toggleCompare(article, btn) {
    const id = String(article.dataset.id || '');
    if (!id) return;

    let ids = readCompareIds();
    const meta = readCompareMeta();
    const index = ids.indexOf(id);

    if (index !== -1) {
      ids.splice(index, 1);
      delete meta[id];
    } else {
      if (ids.length >= COMPARE_MAX) {
        window.alert(
          'Можете да сравните най-много ' + COMPARE_MAX + ' продукта. Премахнете някой, за да добавите нов.'
        );
        return;
      }
      ids.push(id);
      const item = extractProductMeta(article);
      if (item) meta[id] = item;
    }

    writeCompareIds(ids);
    writeCompareMeta(meta);
    setCompareButtonState(btn, ids.indexOf(id) !== -1);
    renderCompareBar();
  }

  function ensureActions(article, favs, compareIds) {
    const media = article.querySelector(':scope > .aspect-square');
    if (!media) return;

    let actions = media.querySelector('.product-card-actions');
    const id = String(article.dataset.id || '');
    if (!id) return;

    if (!actions) {
      actions = document.createElement('div');
      actions.className = 'product-card-actions';

      const favBtn = document.createElement('button');
      favBtn.type = 'button';
      favBtn.className = 'product-fav-btn fav';
      favBtn.innerHTML =
        '<span class="material-symbols-outlined" aria-hidden="true">favorite</span>';
      setFavButtonState(favBtn, favs.has(id));

      const addBtn = document.createElement('button');
      addBtn.type = 'button';
      addBtn.className = 'product-add-btn';
      addBtn.setAttribute('aria-label', 'Добави в количката');
      addBtn.innerHTML =
        '<span class="material-symbols-outlined" aria-hidden="true">add</span>';

      actions.append(favBtn, addBtn);
      media.appendChild(actions);
    }

    let compareBtn = actions.querySelector('.product-compare-btn');
    if (!compareBtn) {
      compareBtn = document.createElement('button');
      compareBtn.type = 'button';
      compareBtn.className = 'product-compare-btn';
      compareBtn.innerHTML =
        '<span class="material-symbols-outlined" aria-hidden="true">check</span>';
      actions.appendChild(compareBtn);
    }
    setCompareButtonState(compareBtn, compareIds.has(id));
  }

  function addArticleToCart(article) {
    if (window.__plasicoCart && typeof window.__plasicoCart.addFromArticle === 'function') {
      if (window.__plasicoCart.addFromArticle(article)) return;
    }

    const form = article.querySelector('form[method="post"]');
    if (form && typeof form.requestSubmit === 'function') {
      form.requestSubmit();
      return;
    }
    if (form) form.submit();
  }

  function toggleFavorite(article, btn) {
    const id = String(article.dataset.id || '');
    if (!id) return;
    const favs = readFavs();
    const meta = readFavMeta();
    if (favs.has(id)) {
      favs.delete(id);
      delete meta[id];
    } else {
      favs.add(id);
      const item = extractProductMeta(article);
      if (item) meta[id] = item;
    }
    writeFavs(favs);
    writeFavMeta(meta);
    setFavButtonState(btn, favs.has(id));
    updateHeaderFavBadge(favs);
  }

  const favs = readFavs();
  updateHeaderFavBadge(favs);
  renderCompareBar();

  window.addEventListener('storage', (e) => {
    if (
      e.key === COMPARE_STORAGE_KEY ||
      e.key === COMPARE_META_KEY ||
      e.key === null
    ) {
      renderCompareBar();
    }
  });

  // Expose for debugging / future compare page
  window.__plasicoCompare = {
    key: COMPARE_STORAGE_KEY,
    metaKey: COMPARE_META_KEY,
    max: COMPARE_MAX,
    orange: COMPARE_ORANGE,
    read: readCompareIds,
    clear: clearCompare,
    refresh: renderCompareBar,
  };

  if (!grid) return;

  const compareIds = new Set(readCompareIds());
  grid.querySelectorAll('article[data-id]').forEach((article) => {
    ensureActions(article, favs, compareIds);
  });

  grid.addEventListener('click', (e) => {
    const favBtn = e.target.closest('.product-fav-btn');
    if (favBtn && grid.contains(favBtn)) {
      e.preventDefault();
      e.stopPropagation();
      const article = favBtn.closest('article[data-id]');
      if (article) toggleFavorite(article, favBtn);
      return;
    }

    const compareBtn = e.target.closest('.product-compare-btn');
    if (compareBtn && grid.contains(compareBtn)) {
      e.preventDefault();
      e.stopPropagation();
      const article = compareBtn.closest('article[data-id]');
      if (article) toggleCompare(article, compareBtn);
      return;
    }

    const addBtn = e.target.closest('.product-add-btn');
    if (addBtn && grid.contains(addBtn)) {
      e.preventDefault();
      e.stopPropagation();
      const article = addBtn.closest('article[data-id]');
      if (article) addArticleToCart(article);
    }
  });
})();
