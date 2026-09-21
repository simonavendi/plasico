/**
 * cart-drawer.js — UI only.
 *
 * All backend communication goes through window.PlasicoCartAdapter
 * (plasico-cart-adapter.js). This file must not fetch anything itself.
 *
 * The cart is server-authoritative. localStorage is not consulted here at all;
 * the adapter owns an optional render cache under the legacy key.
 *
 * If the adapter script tag was omitted from the page, we load it from the same
 * directory as this file so add-to-cart still works.
 */
(function bootstrapCartDrawer() {
  function startCartDrawer() {
  const CHECKOUT_URL = 'poruchka.html';
  const MOBILE_CART_MQ = '(max-width: 768px)';
  const UPSELL_ITEMS = [
    {
      id: '13088697',
      title: 'ASUS TUF Gaming A16 2024 FA607NUG-RL117',
      price: 949.99,
      image: 'https://static.plasico.bg/thumbs/10/250924102012250408153346asus-tuf-a16-fa607nu-1.webp',
      href: 'https://plasico.bg/asus-tuf-gaming-a16-2024-fa607nug-rl117-16-fhd-ips-144hz-ryzen-7-7445hs-16gb-512gb-ssd-rtx-4050-6gb-mecha-gray-90nr0mu3-m00a10-13088697.html',
      addable: true,
    },
    {
      title: 'Още лаптопи от Hot Summer Sale',
      priceLabel: 'от 460.98 €',
      image: 'https://static.plasico.bg/thumbs/10/260115123449250909094011hp-250-g10-111.webp',
      href: 'hot-summer-sale-2026.html#laptopi',
      addable: false,
    },
  ];

  const root = document.getElementById('cart-drawer-root');
  const backdrop = document.getElementById('cart-drawer-backdrop');
  const drawer = document.getElementById('cart-drawer');
  const toggleBtn = document.getElementById('header-cart-toggle');
  const closeBtn = document.getElementById('cart-drawer-close');
  const continueBtn = document.getElementById('cart-drawer-continue');
  const browseBtn = document.getElementById('cart-drawer-browse');
  const headerBadge = document.getElementById('header-cart-badge');
  const headerCartTotal = document.getElementById('header-cart-total');
  const countLabel = document.getElementById('cart-drawer-count');
  const emptyEl = document.getElementById('cart-drawer-empty');
  const itemsEl = document.getElementById('cart-drawer-items');
  const subtotalEl = document.getElementById('cart-drawer-subtotal');
  const productGrid = document.getElementById('product-grid');
  const bodyEl = drawer && drawer.querySelector('.cart-drawer-body');

  if (!root || !drawer || !toggleBtn) return;

  const adapter = window.PlasicoCartAdapter;
  if (!adapter) {
    console.error('[cart-drawer] PlasicoCartAdapter is unavailable after load');
    return;
  }

  let isOpen = false;
  let lastFocused = null;
  let pending = 0;

  function isMobileCartViewport() {
    return window.matchMedia(MOBILE_CART_MQ).matches;
  }

  function isOnCartPage() {
    const path = decodeURIComponent(window.location.pathname).toLowerCase().replace(/\/+$/, '');
    return (
      path.endsWith('/poruchka.html') ||
      path.endsWith('/poruchka') ||
      path.endsWith('/поръчка')
    );
  }

  /** Prefer the checkout URL the backend itself authored, when we have one. */
  function resolveCheckoutUrl() {
    const cart = adapter.getCart();
    return cart.checkoutUrl || CHECKOUT_URL;
  }

  function goToCartPage() {
    if (isOnCartPage()) {
      document.getElementById('checkout-cart')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    window.location.href = resolveCheckoutUrl();
  }

  function formatPrice(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return '0.00 €';
    return num.toFixed(2) + ' €';
  }

  function resolveImageUrl(src) {
    if (!src) return '';
    try {
      return new URL(src, window.location.href).href;
    } catch {
      return src;
    }
  }

  /* ------------------------------------------------------------ busy + errors */

  function setBusy(on) {
    pending += on ? 1 : -1;
    if (pending < 0) pending = 0;
    const busy = pending > 0;
    root.classList.toggle('is-busy', busy);
    drawer.setAttribute('aria-busy', busy ? 'true' : 'false');
    drawer.querySelectorAll('.cart-drawer-qty-btn, .cart-drawer-item__remove')
      .forEach(btn => { btn.disabled = busy; });
  }

  function ensureErrorEl() {
    let el = document.getElementById('cart-drawer-error');
    if (el || !bodyEl) return el;
    el = document.createElement('div');
    el.id = 'cart-drawer-error';
    el.className = 'cart-drawer-error';
    el.setAttribute('role', 'alert');
    el.hidden = true;
    bodyEl.insertBefore(el, bodyEl.firstChild);
    return el;
  }

  function showError(message) {
    const el = ensureErrorEl();
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
  }

  function clearError() {
    const el = document.getElementById('cart-drawer-error');
    if (el) el.hidden = true;
  }

  /**
   * Wrap an adapter promise so the UI never reports success early. The drawer
   * only re-renders from the adapter's subscription, which fires after the
   * backend has actually confirmed the change.
   */
  function run(promise, failMessage) {
    setBusy(true);
    clearError();
    return promise
      .then(result => { clearError(); return result; })
      .catch(err => {
        showError(failMessage + (err && err.detail ? ' (' + err.detail + ')' : ''));
        throw err;
      })
      .finally(() => setBusy(false));
  }

  /* ---------------------------------------------------------------- rendering */

  function updateHeaderBadge(cart) {
    const count = cart.quantity;
    if (headerBadge) {
      headerBadge.textContent = String(count);
      headerBadge.classList.toggle('is-empty', count === 0);
      headerBadge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
    }
    if (headerCartTotal) {
      headerCartTotal.textContent = Number(cart.subtotal || 0).toLocaleString('bg-BG', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }) + ' €';
    }
  }

  function buildItemRow(item) {
    const li = document.createElement('li');
    li.className = 'cart-drawer-item';
    if (item.lineId) li.dataset.lineId = item.lineId;
    if (item.productId) li.dataset.id = item.productId;
    if (item.isGift) li.classList.add('cart-drawer-item--gift');

    const thumb = document.createElement(item.href ? 'a' : 'div');
    thumb.className = 'cart-drawer-item__thumb';
    if (item.href) {
      thumb.href = item.href;
      thumb.setAttribute('aria-label', item.title || 'Продукт');
    }

    const img = document.createElement('img');
    img.className = 'cart-drawer-item__image';
    img.src = resolveImageUrl(item.image);
    img.alt = item.alt || item.title || '';
    img.loading = 'lazy';
    thumb.appendChild(img);

    const info = document.createElement('div');
    info.className = 'cart-drawer-item__info';

    const title = document.createElement(item.href ? 'a' : 'span');
    title.className = 'cart-drawer-item__title';
    title.textContent = item.title;
    if (item.href) title.href = item.href;

    const price = document.createElement('span');
    price.className = 'cart-drawer-item__price';
    price.textContent = item.isGift ? 'Подарък!' : formatPrice(item.lineTotal);

    const controls = document.createElement('div');
    controls.className = 'cart-drawer-item__controls';

    // Per-line quantity controls are only offered when the backend actually
    // reported a quantity for the line. The live mini-cart fragment omits it
    // (remove-only); the checkout table renders .quan/.inc/.dec.
    if (!item.isGift && item.mutable && item.quantity != null) {
      const minusBtn = document.createElement('button');
      minusBtn.type = 'button';
      minusBtn.className = 'cart-drawer-qty-btn';
      minusBtn.setAttribute('aria-label', 'Намали количество');
      minusBtn.innerHTML = '<span class="material-symbols-outlined text-[16px]" aria-hidden="true">remove</span>';
      minusBtn.addEventListener('click', () => {
        run(adapter.updateItem(item.lineId, item.quantity - 1), 'Количеството не беше променено.');
      });

      const qty = document.createElement('span');
      qty.className = 'cart-drawer-qty-value';
      qty.textContent = String(item.quantity);

      const plusBtn = document.createElement('button');
      plusBtn.type = 'button';
      plusBtn.className = 'cart-drawer-qty-btn';
      plusBtn.setAttribute('aria-label', 'Увеличи количество');
      plusBtn.innerHTML = '<span class="material-symbols-outlined text-[16px]" aria-hidden="true">add</span>';
      plusBtn.addEventListener('click', () => {
        run(adapter.updateItem(item.lineId, item.quantity + 1), 'Количеството не беше променено.');
      });

      controls.append(minusBtn, qty, plusBtn);
    }

    if (!item.isGift && item.mutable) {
      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'cart-drawer-item__remove';
      removeBtn.textContent = 'Премахни';
      removeBtn.addEventListener('click', () => {
        run(adapter.removeItem(item.lineId), 'Продуктът не беше премахнат.');
      });
      controls.appendChild(removeBtn);
    }

    info.append(title, price, controls);
    li.append(thumb, info);
    return li;
  }

  function renderCart(cart) {
    const count = cart.quantity;
    const isEmpty = cart.isEmpty;

    if (countLabel) countLabel.textContent = isEmpty ? '' : ` (${count})`;
    if (emptyEl) emptyEl.hidden = !isEmpty;
    if (itemsEl) {
      itemsEl.hidden = isEmpty;
      itemsEl.innerHTML = '';
      cart.items.forEach(item => itemsEl.appendChild(buildItemRow(item)));
    }
    if (subtotalEl) subtotalEl.textContent = formatPrice(cart.subtotal);

    const checkoutLink = document.getElementById('cart-drawer-checkout');
    if (checkoutLink) checkoutLink.href = resolveCheckoutUrl();

    renderUpsell(cart);
  }

  /* ------------------------------------------------------------------ upsell */

  function ensureUpsellSection() {
    let section = document.getElementById('cart-drawer-upsell');
    if (section) return section;
    if (!bodyEl) return null;

    section = document.createElement('section');
    section.id = 'cart-drawer-upsell';
    section.className = 'cart-drawer-upsell';
    section.setAttribute('aria-labelledby', 'cart-drawer-upsell-title');
    section.hidden = true;
    section.innerHTML =
      '<h3 id="cart-drawer-upsell-title" class="cart-drawer-upsell__title">Препоръчани за вас</h3>' +
      '<ul id="cart-drawer-upsell-list" class="cart-drawer-upsell__list" role="list"></ul>';

    if (itemsEl && itemsEl.parentNode === bodyEl) {
      itemsEl.insertAdjacentElement('afterend', section);
    } else {
      bodyEl.appendChild(section);
    }
    return section;
  }

  function getVisibleUpsellItems(cart) {
    const inCart = new Set(cart.items.map(item => String(item.productId)));
    return UPSELL_ITEMS.filter(entry => {
      if (!entry.addable || !entry.id) return true;
      return !inCart.has(String(entry.id));
    });
  }

  function renderUpsell(cart) {
    const section = ensureUpsellSection();
    if (!section) return;
    const list = section.querySelector('#cart-drawer-upsell-list');
    if (!list) return;

    const visible = cart.quantity > 0 ? getVisibleUpsellItems(cart) : [];
    list.innerHTML = '';

    if (!visible.length) {
      section.hidden = true;
      return;
    }

    visible.forEach(entry => {
      const li = document.createElement('li');
      const row = document.createElement(entry.addable ? 'div' : 'a');
      row.className = 'cart-drawer-upsell__row';

      if (!entry.addable) {
        row.href = entry.href;
        row.addEventListener('click', () => closeDrawer());
      }

      const img = document.createElement('img');
      img.className = 'cart-drawer-upsell__img';
      img.src = entry.image;
      img.alt = '';
      img.width = 48;
      img.height = 48;
      img.loading = 'lazy';

      const body = document.createElement('div');
      body.className = 'cart-drawer-upsell__body';

      const name = document.createElement(entry.addable ? 'a' : 'span');
      name.className = 'cart-drawer-upsell__name';
      name.textContent = entry.title;
      if (entry.addable && entry.href) {
        name.href = entry.href;
        name.target = '_blank';
        name.rel = 'noopener noreferrer';
      }

      const price = document.createElement('span');
      price.className = 'cart-drawer-upsell__price';
      price.textContent = entry.priceLabel || formatPrice(entry.price);

      body.append(name, price);

      const addBtn = document.createElement('button');
      addBtn.type = 'button';
      addBtn.className = 'cart-drawer-upsell__add';
      addBtn.setAttribute(
        'aria-label',
        entry.addable ? `Добави ${entry.title} в количката` : `Разгледай ${entry.title}`
      );
      addBtn.innerHTML = '<span class="material-symbols-outlined" aria-hidden="true">add_circle</span>';

      if (entry.addable) {
        addBtn.addEventListener('click', e => {
          e.preventDefault();
          e.stopPropagation();
          run(
            adapter.add(entry.id, 1, {
              title: entry.title,
              price: entry.price,
              image: entry.image,
              href: entry.href,
            }),
            'Продуктът не беше добавен в количката.'
          );
        });
      } else {
        addBtn.addEventListener('click', e => {
          e.preventDefault();
          e.stopPropagation();
          closeDrawer();
          window.location.href = entry.href;
        });
      }

      row.append(img, body, addBtn);
      li.appendChild(row);
      list.appendChild(li);
    });

    section.hidden = false;
  }

  /* ------------------------------------------------------------ open / close */

  function getFocusableElements() {
    return drawer.querySelectorAll(
      'button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
  }

  function trapFocus(e) {
    if (!isOpen || e.key !== 'Tab') return;
    const focusable = Array.from(getFocusableElements());
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function openDrawer() {
    if (isOpen) return;
    window.__closeHeaderAuth?.();
    isOpen = true;
    lastFocused = document.activeElement;
    root.hidden = false;
    root.setAttribute('aria-hidden', 'false');
    if (backdrop) backdrop.setAttribute('aria-hidden', 'false');
    toggleBtn.setAttribute('aria-expanded', 'true');
    document.body.classList.add('cart-drawer-open');
    requestAnimationFrame(() => {
      root.classList.add('is-open');
      if (closeBtn && typeof closeBtn.focus === 'function') closeBtn.focus();
    });
    document.addEventListener('keydown', onKeydown);
    document.addEventListener('keydown', trapFocus);
    // The drawer must always be able to re-read the real cart.
    run(adapter.refresh(), 'Количката не можа да бъде заредена.').catch(() => {});
  }

  function openCart() {
    if (isMobileCartViewport()) {
      goToCartPage();
      return;
    }
    openDrawer();
  }

  function closeDrawer() {
    if (!isOpen) return;
    isOpen = false;
    root.classList.remove('is-open');
    if (backdrop) backdrop.setAttribute('aria-hidden', 'true');
    toggleBtn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('cart-drawer-open');
    document.removeEventListener('keydown', onKeydown);
    document.removeEventListener('keydown', trapFocus);
    const onEnd = (e) => {
      if (e.target !== drawer || e.propertyName !== 'transform') return;
      drawer.removeEventListener('transitionend', onEnd);
      root.hidden = true;
      root.setAttribute('aria-hidden', 'true');
    };
    drawer.addEventListener('transitionend', onEnd);
    if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
  }

  function onKeydown(e) {
    if (e.key === 'Escape') closeDrawer();
  }

  /* -------------------------------------------------------------- add-to-cart */

  /**
   * Resolve a product id from either the redesign's article[data-id] or the
   * mirror's .product-box[data-id]. Requirement: reuse the existing data-id.
   */
  function productIdFrom(el) {
    if (!el) return '';
    const host = el.matches?.('[data-id]') ? el : el.closest?.('[data-id]');
    return host ? String(host.dataset.id || '') : '';
  }

  function addFromArticle(article, quantity) {
    const id = productIdFrom(article);
    if (!id) return false;
    const qty = quantity || 1;
    const titleLink = article.querySelector?.('h4 a') || article.querySelector?.('a[href*=".html"]') || article.querySelector?.('a.cart-card__title');
    const img = article.querySelector?.('.cart-card__image') || article.querySelector?.('.aspect-square img') || article.querySelector?.('img');
    const price = parseFloat(article.dataset?.price || '');
    const meta = {
      title: (article.dataset?.name || (titleLink && titleLink.textContent.trim()) || '').trim() || ('Продукт #' + id),
      price: Number.isFinite(price) ? price : 0,
      image: img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '',
      href: (article.dataset?.href || (titleLink && titleLink.getAttribute('href')) || ''),
      alt: (img && img.getAttribute('alt')) || '',
    };
    // Persist first, then open. On mobile openCart() navigates to poruchka.html;
    // opening before add would lose the write on unload.
    run(adapter.add(id, qty, meta), 'Продуктът не беше добавен в количката.')
      .then(() => { openCart(); })
      .catch(() => { openCart(); });
    return true;
  }

  if (browseBtn) {
    if (document.getElementById('catalog') && !document.getElementById('laptopi')) {
      browseBtn.href = '#catalog';
    }
  }

  toggleBtn.addEventListener('click', openCart);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
  if (backdrop) backdrop.addEventListener('click', closeDrawer);
  if (continueBtn) continueBtn.addEventListener('click', closeDrawer);
  if (browseBtn) browseBtn.addEventListener('click', () => closeDrawer());

  if (productGrid) {
    productGrid.addEventListener('submit', e => {
      const form = e.target.closest('form');
      if (!form || form.method?.toLowerCase() !== 'post') return;
      const article = form.closest('[data-id]');
      if (!article) return;
      e.preventDefault();
      const qtyInput = form.querySelector('[name="quantity"]');
      addFromArticle(article, qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1);
    });
  }

  /* ------------------------------------------------------------------- wiring */

  adapter.subscribe(cart => {
    renderCart(cart);
    updateHeaderBadge(cart);
  });

  document.addEventListener('plasico:cart-error', e => {
    const err = e.detail;
    if (err && err.operation === 'refresh') {
      showError('Количката не можа да бъде заредена от сървъра.');
    }
  });

  // Requirement: on page load, retrieve the real cart and update the header
  // quantity, drawer contents and empty state.
  adapter.init();

  window.__closeCartDrawer = closeDrawer;
  window.__plasicoCart = Object.assign(window.__plasicoCart || {}, {
    // Backend interface (delegated to the adapter)
    getCart: adapter.getCart,
    refresh: adapter.refresh,
    add: adapter.add,
    updateItem: adapter.updateItem,
    setQuantity: adapter.setQuantity,
    removeItem: adapter.removeItem,
    clear: adapter.clear,
    subscribe: adapter.subscribe,
    // Preserved legacy UI surface
    addFromArticle,
    open: openCart,
    openDrawer,
    close: closeDrawer,
    isMobile: isMobileCartViewport,
  });
  }

  if (window.PlasicoCartAdapter) {
    startCartDrawer();
    return;
  }

  let started = false;
  function startOnce() {
    if (started) return;
    started = true;
    startCartDrawer();
  }

  const current = document.currentScript;
  const adapterSrc = current && current.src
    ? current.src.replace(/cart-drawer\.js(\?.*)?$/i, 'plasico-cart-adapter.js$1')
    : 'plasico-cart-adapter.js';

  const existing = document.querySelector('script[src*="plasico-cart-adapter.js"]');
  if (existing) {
    existing.addEventListener('load', startOnce);
    if (window.PlasicoCartAdapter) startOnce();
    return;
  }

  const loader = document.createElement('script');
  loader.src = adapterSrc;
  loader.onload = startOnce;
  loader.onerror = function () {
    console.error('[cart-drawer] failed to load', adapterSrc);
  };
  if (current && current.parentNode) current.parentNode.insertBefore(loader, current);
  else document.head.appendChild(loader);
})();
