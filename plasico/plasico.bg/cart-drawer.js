(function initCartDrawer() {
  const CART_STORAGE_KEY = 'plasico-hss2026-cart';
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

  let isOpen = false;
  let lastFocused = null;

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

  function goToCartPage() {
    if (isOnCartPage()) {
      document.getElementById('checkout-cart')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    window.location.href = CHECKOUT_URL;
  }

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
    if (headerBadge) {
      headerBadge.textContent = String(count);
      headerBadge.classList.toggle('is-empty', count === 0);
      headerBadge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
    }
    if (headerCartTotal) {
      const total = getSubtotal(items);
      headerCartTotal.textContent = total.toLocaleString('bg-BG', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      }) + ' €';
    }
  }

  function resolveProductHref(href) {
    if (!href || href === '#') return '';
    try {
      return new URL(href, window.location.href).href;
    } catch {
      return href;
    }
  }

  function extractProductFromArticle(article) {
    if (!article) return null;
    const id = article.dataset.id;
    if (!id) return null;
    const titleLink = article.querySelector('h4 a');
    const imageLink = article.querySelector('.aspect-square a[href]');
    const title = titleLink ? titleLink.textContent.trim() : 'Продукт';
    const price = parseFloat(article.dataset.price) || 0;
    const { src, alt } = getProductImage(article);
    const href = resolveProductHref(
      titleLink?.getAttribute('href') || imageLink?.getAttribute('href') || ''
    );
    return { id: String(id), title, price, image: src, alt: alt || title, href, qty: 1 };
  }

  function addToCart(product) {
    if (!product || !product.id) return;
    const items = readCart();
    const existing = items.find(item => item.id === product.id);
    const href = resolveProductHref(product.href || product.url || '');
    if (existing) {
      existing.qty = (Number(existing.qty) || 0) + (Number(product.qty) || 1);
      if (product.image && !existing.image) existing.image = product.image;
      if (product.alt && !existing.alt) existing.alt = product.alt;
      if (href && !existing.href) existing.href = href;
    } else {
      items.push({
        id: product.id,
        title: product.title,
        price: product.price,
        image: product.image,
        alt: product.alt || product.title,
        href: href || undefined,
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

  function backfillItemMeta(item, items) {
    if (!productGrid) return { image: item.image || '', href: resolveProductHref(item.href || item.url || '') };
    const article = productGrid.querySelector(`article[data-id="${item.id}"]`);
    if (!article) {
      return { image: item.image || '', href: resolveProductHref(item.href || item.url || '') };
    }
    let changed = false;
    if (!item.image) {
      const { src, alt } = getProductImage(article);
      if (src) {
        item.image = src;
        if (alt) item.alt = alt;
        changed = true;
      }
    }
    if (!item.href && !item.url) {
      const titleLink = article.querySelector('h4 a');
      const imageLink = article.querySelector('.aspect-square a[href]');
      const href = resolveProductHref(
        titleLink?.getAttribute('href') || imageLink?.getAttribute('href') || ''
      );
      if (href) {
        item.href = href;
        changed = true;
      }
    }
    if (changed) writeCart(items);
    return {
      image: item.image || '',
      href: resolveProductHref(item.href || item.url || ''),
    };
  }

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

  function getVisibleUpsellItems(cartItems) {
    const inCart = new Set(cartItems.map(item => String(item.id)));
    return UPSELL_ITEMS.filter(entry => {
      if (!entry.addable || !entry.id) return true;
      return !inCart.has(String(entry.id));
    });
  }

  function renderUpsell(cartItems) {
    const section = ensureUpsellSection();
    if (!section) return;
    const list = section.querySelector('#cart-drawer-upsell-list') || section.querySelector('.cart-drawer-upsell__list');
    if (!list) return;

    const count = getTotalQty(cartItems);
    const visible = count > 0 ? getVisibleUpsellItems(cartItems) : [];
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
          addToCart({
            id: entry.id,
            title: entry.title,
            price: entry.price,
            image: entry.image,
            alt: entry.title,
            href: entry.href,
            qty: 1,
          });
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

        const meta = backfillItemMeta(item, items);
        const productHref = meta.href;

        const thumb = document.createElement(productHref ? 'a' : 'div');
        thumb.className = 'cart-drawer-item__thumb';
        if (productHref) {
          thumb.href = productHref;
          thumb.setAttribute('aria-label', item.title || 'Продукт');
        }

        const img = document.createElement('img');
        img.className = 'cart-drawer-item__image';
        img.src = resolveImageUrl(meta.image || item.image);
        img.alt = item.alt || item.title || '';
        img.loading = 'lazy';

        thumb.appendChild(img);

        const info = document.createElement('div');
        info.className = 'cart-drawer-item__info';

        const title = document.createElement(productHref ? 'a' : 'span');
        title.className = 'cart-drawer-item__title';
        title.textContent = item.title;
        if (productHref) title.href = productHref;

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
    renderUpsell(items);
    document.dispatchEvent(new CustomEvent('plasico:cart-updated'));
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
    renderCart(readCart());
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

  /** Mobile: full cart page. Desktop: slide-over drawer. */
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

  toggleBtn.addEventListener('click', openCart);
  closeBtn.addEventListener('click', closeDrawer);
  backdrop.addEventListener('click', closeDrawer);
  continueBtn.addEventListener('click', closeDrawer);
  if (browseBtn) {
    browseBtn.addEventListener('click', () => closeDrawer());
  }

  function addFromArticle(article) {
    const product = extractProductFromArticle(article);
    if (!product) return false;
    addToCart(product);
    openCart();
    return true;
  }

  if (productGrid) {
    productGrid.addEventListener('submit', e => {
      const form = e.target.closest('form');
      if (!form || form.method?.toLowerCase() !== 'post') return;
      const article = form.closest('article[data-id]');
      if (!article) return;
      e.preventDefault();
      addFromArticle(article);
    });
  }

  const checkoutLink = document.getElementById('cart-drawer-checkout');
  if (checkoutLink) checkoutLink.href = CHECKOUT_URL;

  const initial = readCart();
  renderCart(initial);
  updateHeaderBadge(initial);
  window.__closeCartDrawer = closeDrawer;
  window.__plasicoCart = {
    addFromArticle,
    open: openCart,
    openDrawer,
    close: closeDrawer,
    isMobile: isMobileCartViewport,
  };
})();
