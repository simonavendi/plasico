(function initCartDrawer() {
  const CART_STORAGE_KEY = 'plasico-hss2026-cart';
  const CHECKOUT_URL = 'https://plasico.bg/поръчка';

  const root = document.getElementById('cart-drawer-root');
  const backdrop = document.getElementById('cart-drawer-backdrop');
  const drawer = document.getElementById('cart-drawer');
  const toggleBtn = document.getElementById('header-cart-toggle');
  const closeBtn = document.getElementById('cart-drawer-close');
  const continueBtn = document.getElementById('cart-drawer-continue');
  const browseBtn = document.getElementById('cart-drawer-browse');
  const headerBadge = document.getElementById('header-cart-badge');
  const countLabel = document.getElementById('cart-drawer-count');
  const emptyEl = document.getElementById('cart-drawer-empty');
  const itemsEl = document.getElementById('cart-drawer-items');
  const subtotalEl = document.getElementById('cart-drawer-subtotal');
  const productGrid = document.getElementById('product-grid');

  if (!root || !drawer || !toggleBtn) return;

  let isOpen = false;
  let lastFocused = null;

  function readCart() {
    try {
      const raw = localStorage.getItem(CART_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function writeCart(items) {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
  }

  function formatPrice(value) {
    const num = Number(value);
    if (!Number.isFinite(num)) return '0.00 €';
    return num.toFixed(2) + ' €';
  }

  function getTotalQty(items) {
    return items.reduce((sum, item) => sum + (Number(item.qty) || 0), 0);
  }

  function getSubtotal(items) {
    return items.reduce((sum, item) => sum + (Number(item.price) || 0) * (Number(item.qty) || 0), 0);
  }

  function resolveImageUrl(src) {
    if (!src) return '';
    try {
      return new URL(src, window.location.href).href;
    } catch {
      return src;
    }
  }

  function getProductImage(article) {
    const img = article.querySelector('.aspect-square img');
    if (!img) return { src: '', alt: '' };
    const raw =
      img.currentSrc ||
      img.getAttribute('src') ||
      img.getAttribute('data-src') ||
      '';
    return {
      src: resolveImageUrl(raw),
      alt: img.getAttribute('alt') || '',
    };
  }

  function updateHeaderBadge(items) {
    const count = getTotalQty(items);
    if (!headerBadge) return;
    headerBadge.textContent = String(count);
    headerBadge.classList.toggle('is-empty', count === 0);
    headerBadge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
  }

  function extractProductFromArticle(article) {
    if (!article) return null;
    const id = article.dataset.id;
    if (!id) return null;
    const titleLink = article.querySelector('h4 a');
    const title = titleLink ? titleLink.textContent.trim() : 'Продукт';
    const price = parseFloat(article.dataset.price) || 0;
    const { src, alt } = getProductImage(article);
    return { id: String(id), title, price, image: src, alt: alt || title, qty: 1 };
  }

  function addToCart(product) {
    if (!product || !product.id) return;
    const items = readCart();
    const existing = items.find(item => item.id === product.id);
    if (existing) {
      existing.qty = (Number(existing.qty) || 0) + (Number(product.qty) || 1);
      if (product.image && !existing.image) existing.image = product.image;
      if (product.alt && !existing.alt) existing.alt = product.alt;
    } else {
      items.push({
        id: product.id,
        title: product.title,
        price: product.price,
        image: product.image,
        alt: product.alt || product.title,
        qty: Number(product.qty) || 1,
      });
    }
    writeCart(items);
    renderCart(items);
    updateHeaderBadge(items);
  }

  function updateItemQty(id, delta) {
    const items = readCart();
    const item = items.find(entry => entry.id === id);
    if (!item) return;
    item.qty = (Number(item.qty) || 0) + delta;
    const next = item.qty > 0 ? items : items.filter(entry => entry.id !== id);
    writeCart(next);
    renderCart(next);
    updateHeaderBadge(next);
  }

  function removeItem(id) {
    const next = readCart().filter(entry => entry.id !== id);
    writeCart(next);
    renderCart(next);
    updateHeaderBadge(next);
  }

  function backfillItemImage(item, items) {
    if (item.image || !productGrid) return item.image || '';
    const article = productGrid.querySelector(`article[data-id="${item.id}"]`);
    if (!article) return item.image || '';
    const { src, alt } = getProductImage(article);
    if (src) {
      item.image = src;
      if (alt) item.alt = alt;
      writeCart(items);
    }
    return item.image || '';
  }

  function renderCart(items) {
    const count = getTotalQty(items);
    const isEmpty = count === 0;

    if (countLabel) {
      countLabel.textContent = isEmpty ? '' : ` (${count})`;
    }
    if (emptyEl) emptyEl.hidden = !isEmpty;
    if (itemsEl) {
      itemsEl.hidden = isEmpty;
      itemsEl.innerHTML = '';
      items.forEach(item => {
        const li = document.createElement('li');
        li.className = 'cart-drawer-item';
        li.dataset.id = item.id;

        const thumb = document.createElement('div');
        thumb.className = 'cart-drawer-item__thumb';

        const img = document.createElement('img');
        img.className = 'cart-drawer-item__image';
        const imageSrc = backfillItemImage(item, items) || resolveImageUrl(item.image);
        img.src = imageSrc;
        img.alt = item.alt || item.title || '';
        img.loading = 'lazy';

        thumb.appendChild(img);

        const info = document.createElement('div');
        info.className = 'cart-drawer-item__info';

        const title = document.createElement('span');
        title.className = 'cart-drawer-item__title';
        title.textContent = item.title;

        const price = document.createElement('span');
        price.className = 'cart-drawer-item__price';
        price.textContent = formatPrice(item.price);

        const controls = document.createElement('div');
        controls.className = 'cart-drawer-item__controls';

        const minusBtn = document.createElement('button');
        minusBtn.type = 'button';
        minusBtn.className = 'cart-drawer-qty-btn';
        minusBtn.setAttribute('aria-label', 'Намали количество');
        minusBtn.innerHTML = '<span class="material-symbols-outlined text-[16px]" aria-hidden="true">remove</span>';
        minusBtn.addEventListener('click', () => updateItemQty(item.id, -1));

        const qty = document.createElement('span');
        qty.className = 'cart-drawer-qty-value';
        qty.textContent = String(item.qty);

        const plusBtn = document.createElement('button');
        plusBtn.type = 'button';
        plusBtn.className = 'cart-drawer-qty-btn';
        plusBtn.setAttribute('aria-label', 'Увеличи количество');
        plusBtn.innerHTML = '<span class="material-symbols-outlined text-[16px]" aria-hidden="true">add</span>';
        plusBtn.addEventListener('click', () => updateItemQty(item.id, 1));

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'cart-drawer-item__remove';
        removeBtn.textContent = 'Премахни';
        removeBtn.addEventListener('click', () => removeItem(item.id));

        controls.append(minusBtn, qty, plusBtn, removeBtn);
        info.append(title, price, controls);
        li.append(thumb, info);
        itemsEl.appendChild(li);
      });
    }
    if (subtotalEl) subtotalEl.textContent = formatPrice(getSubtotal(items));
  }

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
    backdrop.setAttribute('aria-hidden', 'false');
    toggleBtn.setAttribute('aria-expanded', 'true');
    document.body.classList.add('cart-drawer-open');
    requestAnimationFrame(() => {
      root.classList.add('is-open');
      closeBtn.focus();
    });
    document.addEventListener('keydown', onKeydown);
    document.addEventListener('keydown', trapFocus);
  }

  function closeDrawer() {
    if (!isOpen) return;
    isOpen = false;
    root.classList.remove('is-open');
    backdrop.setAttribute('aria-hidden', 'true');
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

  if (browseBtn) {
    if (document.getElementById('catalog') && !document.getElementById('laptopi')) {
      browseBtn.href = '#catalog';
    }
  }

  toggleBtn.addEventListener('click', openDrawer);
  closeBtn.addEventListener('click', closeDrawer);
  backdrop.addEventListener('click', closeDrawer);
  continueBtn.addEventListener('click', closeDrawer);
  if (browseBtn) {
    browseBtn.addEventListener('click', () => closeDrawer());
  }

  if (productGrid) {
    productGrid.addEventListener('submit', e => {
      const form = e.target.closest('form');
      if (!form || form.method?.toLowerCase() !== 'post') return;
      const article = form.closest('article[data-id]');
      if (!article) return;
      e.preventDefault();
      const product = extractProductFromArticle(article);
      if (!product) return;
      addToCart(product);
      openDrawer();
    });
  }

  const initial = readCart();
  renderCart(initial);
  updateHeaderBadge(initial);
  window.__closeCartDrawer = closeDrawer;
})();
