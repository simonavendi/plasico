(function initProductPage() {
  const root = document.querySelector('[data-product-page]');
  if (!root) return;

  const productId = root.dataset.productId || '';
  const productTitle = root.dataset.productTitle || '';
  const productPrice = parseFloat(root.dataset.productPrice || '0') || 0;
  const productImage = root.dataset.productImage || '';
  const productHref = window.location.pathname.split('/').pop() || '';

  const mainImg = root.querySelector('[data-gallery-main]');
  const qtyValue = root.querySelector('[data-qty-value]');
  const buyBtn = root.querySelector('[data-product-buy]');
  const favBtn = root.querySelector('[data-product-fav]');
  const compareBtn = root.querySelector('[data-product-compare]');

  const FAV_KEY = 'plasico-hss2026-favs';
  const COMPARE_KEY = 'plasico-hss2026-compare';

  function readJson(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  }

  function writeJson(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  }

  function getQty() {
    return Math.max(1, parseInt(qtyValue?.textContent || '1', 10) || 1);
  }

  function setQty(next) {
    if (qtyValue) qtyValue.textContent = String(Math.max(1, next));
  }

  root.querySelectorAll('[data-gallery-thumb]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const src = btn.dataset.gallerySrc;
      if (!src || !mainImg) return;
      mainImg.src = src;
      root.querySelectorAll('[data-gallery-thumb]').forEach((el) => {
        el.classList.toggle('is-active', el === btn);
      });
    });
  });

  root.querySelectorAll('[data-qty-delta]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const delta = parseInt(btn.getAttribute('data-qty-delta') || '0', 10) || 0;
      setQty(getQty() + delta);
    });
  });

  function addCurrentToCart() {
    const item = {
      id: productId,
      title: productTitle,
      price: productPrice,
      image: productImage,
      alt: productTitle,
      href: productHref,
      qty: getQty(),
    };

    if (window.__plasicoCart && typeof window.__plasicoCart.addFromArticle === 'function') {
      const article = document.createElement('article');
      article.dataset.id = productId;
      article.dataset.price = String(productPrice);
      article.dataset.name = productTitle;
      article.dataset.href = productHref;
      article.innerHTML = `
        <img class="cart-card__image" src="${productImage}" alt=""/>
        <a class="cart-card__title" href="${productHref}">${productTitle}</a>
      `;
      if (window.__plasicoCart.addFromArticle(article)) return;
    }

    const key = 'plasico-hss2026-cart';
    const items = readJson(key, []);
    const existing = items.find((entry) => String(entry.id) === String(productId));
    if (existing) {
      existing.qty = (Number(existing.qty) || 0) + getQty();
    } else {
      items.push(item);
    }
    writeJson(key, items);
    if (window.__plasicoCart?.open) window.__plasicoCart.open();
  }

  if (buyBtn) {
    buyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      addCurrentToCart();
    });
  }

  function syncFavBtn() {
    if (!favBtn) return;
    const favs = new Set((readJson(FAV_KEY, []) || []).map(String));
    favBtn.classList.toggle('is-active', favs.has(String(productId)));
  }

  function syncCompareBtn() {
    if (!compareBtn) return;
    const ids = (readJson(COMPARE_KEY, []) || []).map(String);
    compareBtn.classList.toggle('is-active', ids.includes(String(productId)));
  }

  if (favBtn) {
    favBtn.addEventListener('click', () => {
      const favs = new Set((readJson(FAV_KEY, []) || []).map(String));
      const id = String(productId);
      if (favs.has(id)) favs.delete(id);
      else favs.add(id);
      writeJson(FAV_KEY, Array.from(favs));
      syncFavBtn();
    });
  }

  if (compareBtn) {
    compareBtn.addEventListener('click', () => {
      const ids = (readJson(COMPARE_KEY, []) || []).map(String);
      const id = String(productId);
      const idx = ids.indexOf(id);
      if (idx >= 0) ids.splice(idx, 1);
      else if (ids.length < 4) ids.push(id);
      writeJson(COMPARE_KEY, ids);
      syncCompareBtn();
    });
  }

  root.querySelectorAll('[data-similar-add]').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const id = btn.dataset.similarId;
      if (!id) return;
      const item = {
        id,
        title: btn.dataset.similarTitle || 'Продукт',
        price: parseFloat(btn.dataset.similarPrice || '0') || 0,
        image: btn.dataset.similarImage || '',
        alt: btn.dataset.similarTitle || 'Продукт',
        href: btn.dataset.similarHref || '',
        qty: 1,
      };
      const key = 'plasico-hss2026-cart';
      const items = readJson(key, []);
      const existing = items.find((entry) => String(entry.id) === String(id));
      if (existing) existing.qty = (Number(existing.qty) || 0) + 1;
      else items.push(item);
      writeJson(key, items);
      if (window.__plasicoCart?.open) window.__plasicoCart.open();
    });
  });

  function submitFastOrder(form) {
    const name = form.querySelector('[name="fast_name"]')?.value.trim() || '';
    const phone = form.querySelector('[name="phone"]')?.value.trim() || '';
    const email = form.querySelector('[name="fast_email"]')?.value.trim() || '';
    const err = form.querySelector('[data-fast-error]');
    const ok = Boolean(name && phone && email);
    if (err) err.hidden = ok;
    if (!ok) {
      (form.querySelector('[name="fast_name"]') || form.querySelector('[name="phone"]'))?.focus();
      return;
    }
    const params = new URLSearchParams({
      fast: '1',
      phone,
      name,
      email,
      prod: productId,
    });
    window.location.href = `poruchka.html?${params.toString()}`;
  }

  function ensureFastOrderModal() {
    let modal = document.getElementById('product-fast-modal');
    if (modal) return modal;

    modal = document.createElement('div');
    modal.id = 'product-fast-modal';
    modal.className = 'product-fast-modal';
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML =
      '<div class="product-fast-modal__backdrop" data-fast-close tabindex="-1"></div>' +
      '<div class="product-fast-modal__dialog" role="dialog" aria-modal="true" aria-labelledby="product-fast-modal-title" tabindex="-1">' +
      '  <button type="button" class="product-fast-modal__close" data-fast-close aria-label="Затвори">' +
      '    <span class="material-symbols-outlined" aria-hidden="true">close</span>' +
      '  </button>' +
      '  <h2 id="product-fast-modal-title" class="product-fast-modal__title">Бърза поръчка</h2>' +
      '  <p class="product-fast-modal__hint">без регистрация — въведи телефон и ще се обадим</p>' +
      '  <form class="product-fast-modal__form" data-fast-order-form novalidate>' +
      '    <label class="product-fast-modal__label" for="product-fast-name">Име *</label>' +
      '    <input id="product-fast-name" name="fast_name" type="text" class="product-fast-modal__input" autocomplete="name" required placeholder="Иван Иванов"/>' +
      '    <label class="product-fast-modal__label" for="product-fast-phone">Телефон *</label>' +
      '    <input id="product-fast-phone" name="phone" type="tel" class="product-fast-modal__input" autocomplete="tel" required placeholder="08xxxxxxxx"/>' +
      '    <label class="product-fast-modal__label" for="product-fast-email">Email *</label>' +
      '    <input id="product-fast-email" name="fast_email" type="email" class="product-fast-modal__input" autocomplete="email" required placeholder="name@email.com"/>' +
      '    <p class="product-fast-modal__error" data-fast-error hidden>Попълни име, телефон и email.</p>' +
      '    <button type="submit" class="product-fast-modal__submit">Поръчай</button>' +
      '  </form>' +
      '</div>';
    document.body.appendChild(modal);

    let lastFocus = null;
    const nameInput = modal.querySelector('#product-fast-name');

    function openFastModal() {
      lastFocus = document.activeElement;
      window.__closeCartDrawer?.();
      window.__closeAuthModal?.();
      modal.hidden = false;
      modal.setAttribute('aria-hidden', 'false');
      document.body.classList.add('product-fast-modal-open');
      window.setTimeout(() => nameInput?.focus(), 20);
    }

    function closeFastModal() {
      if (modal.hidden) return;
      modal.hidden = true;
      modal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('product-fast-modal-open');
      if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
    }

    modal.querySelectorAll('[data-fast-close]').forEach((el) => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        closeFastModal();
      });
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.hidden) {
        e.preventDefault();
        closeFastModal();
      }
    });

    modal.querySelector('[data-fast-order-form]')?.addEventListener('submit', (e) => {
      e.preventDefault();
      submitFastOrder(e.currentTarget);
    });

    window.__openProductFastOrder = openFastModal;
    window.__closeProductFastOrder = closeFastModal;
    return modal;
  }

  function upgradeFastOrderTrigger() {
    const legacyForm = root.querySelector('form[data-fast-order]');
    let trigger = root.querySelector('[data-open-fast-order]');

    if (!trigger && legacyForm) {
      trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'product-fast-trigger';
      trigger.setAttribute('data-open-fast-order', '');
      trigger.textContent = 'Бърза поръчка';
      legacyForm.replaceWith(trigger);
    }

    if (!trigger) return;
    ensureFastOrderModal();
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      window.__openProductFastOrder?.();
    });
  }

  upgradeFastOrderTrigger();

  syncFavBtn();
  syncCompareBtn();
})();
