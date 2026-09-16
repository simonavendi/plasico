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

  const fastForm = root.querySelector('[data-fast-order]');
  if (fastForm) {
    fastForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const phone = fastForm.querySelector('input[name="phone"]')?.value.trim();
      if (!phone) return;
      window.location.href = `poruchka.html?fast=1&phone=${encodeURIComponent(phone)}&prod=${encodeURIComponent(productId)}`;
    });
  }

  syncFavBtn();
  syncCompareBtn();
})();
