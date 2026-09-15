(function initCheckoutMock() {
  const root = document.getElementById('checkout') || document.querySelector('.checkout-mock');
  if (!root) return;

  const CART_STORAGE_KEY = 'plasico-hss2026-cart';
  const money = (n) => `${Number(n).toFixed(2)}\u00a0€`;
  /** @type {'empty' | 'form' | 'fast' | 'done'} */
  let checkoutPhase = 'form';

  const formSections = document.getElementById('checkout-form-sections');
  const mobileRecs = document.getElementById('checkout-recs-mobile');
  const asideHint = root.querySelector('.js-aside-hint');
  const stickyBar = document.getElementById('checkout-sticky-bar');

  function setMobileRecsVisible(visible) {
    if (mobileRecs) mobileRecs.hidden = !visible;
  }

  /** Keep upsells visible whenever the cart has items (one-page form). */
  function syncMobileRecsVisibility() {
    const hasCart = root.querySelectorAll('.cart-card').length > 0;
    const show = hasCart && checkoutPhase !== 'empty' && checkoutPhase !== 'fast';
    setMobileRecsVisible(show);
  }

  function readStoredCart() {
    try {
      const raw = localStorage.getItem(CART_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function writeStoredCart(items) {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
    const count = items.reduce((sum, item) => sum + (Number(item.qty) || 0), 0);
    const badge = document.getElementById('header-cart-badge');
    if (badge) {
      badge.textContent = String(count);
      badge.classList.toggle('is-empty', count === 0);
      badge.setAttribute('aria-hidden', count === 0 ? 'true' : 'false');
    }
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function syncCartFromDom() {
    const items = [];
    root.querySelectorAll('.cart-card').forEach((card) => {
      const id = card.dataset.cartId;
      if (!id) return;
      const qty = parseInt(card.querySelector('.qty-control__value')?.textContent || '0', 10) || 0;
      if (qty <= 0) return;
      const img = card.querySelector('.cart-card__image');
      items.push({
        id: String(id),
        title: card.dataset.name || card.querySelector('.cart-card__title')?.textContent?.trim() || 'Продукт',
        price: parseFloat(card.dataset.unit || '0') || 0,
        qty,
        image: img?.getAttribute('src') || '',
        alt: img?.getAttribute('alt') || card.dataset.name || '',
      });
    });
    writeStoredCart(items);
    return items;
  }

  function setEmptyCheckoutUi(isEmpty) {
    if (stickyBar) stickyBar.hidden = isEmpty;
    if (isEmpty) {
      if (formSections) formSections.hidden = true;
      syncMobileRecsVisibility();
      if (asideHint) asideHint.textContent = 'Добави продукти, за да продължиш към поръчка.';
      document.getElementById('pane-fast')?.setAttribute('hidden', '');
      checkoutPhase = 'empty';
      delete root.dataset.orderPlaced;
      updateStickyLabel();
    }
  }

  function renderStoredCart() {
    const list = root.querySelector('.cart-cards');
    if (!list) return;
    const items = readStoredCart();

    if (!items.length) {
      list.innerHTML =
        '<li class="cart-cards__empty text-on-surface-variant py-6 text-center">Количката е празна. <a class="text-apricot" href="hot-summer-sale-2026.html#laptopi">Разгледай продуктите</a></li>';
      setEmptyCheckoutUi(true);
      return;
    }

    setEmptyCheckoutUi(false);
    list.innerHTML = items
      .map((item) => {
        const id = escapeHtml(item.id);
        const title = escapeHtml(item.title || 'Продукт');
        const price = Number(item.price) || 0;
        const qty = Math.max(1, Number(item.qty) || 1);
        const image = escapeHtml(item.image || '');
        const alt = escapeHtml(item.alt || item.title || '');
        const lineTotal = money(price * qty);
        return `<li class="cart-card" data-cart-id="${id}" data-unit="${price}" data-name="${title}">
          <span class="cart-card__thumb" aria-hidden="true">
            <img src="${image}" alt="${alt}" width="84" height="84" loading="lazy" class="cart-card__image"/>
          </span>
          <div class="cart-card__content">
            <span class="cart-card__title">${title}</span>
            <p class="cart-card__price"><strong class="js-line-total">${lineTotal}</strong></p>
            <div class="cart-card__row">
              <div class="qty-control" role="group" aria-label="Количество">
                <button type="button" class="qty-control__btn" data-qty-delta="-1" aria-label="Намали количество">
                  <span class="material-symbols-outlined" aria-hidden="true">remove</span>
                </button>
                <span class="qty-control__value" aria-live="polite">${qty}</span>
                <button type="button" class="qty-control__btn" data-qty-delta="1" aria-label="Увеличи количество">
                  <span class="material-symbols-outlined" aria-hidden="true">add</span>
                </button>
              </div>
              <button type="button" class="cart-card__remove" data-remove aria-label="Премахни продукта">
                <span class="material-symbols-outlined" aria-hidden="true">delete</span>
                <span>Премахни</span>
              </button>
            </div>
          </div>
        </li>`;
      })
      .join('');
  }

  function setType(value) {
    const radio = root.querySelector(`#checkout-type input[name="type"][value="${value}"]`);
    if (radio) radio.checked = true;
  }

  function getShipTo() {
    return root.querySelector('input[name="ship_to_id[2]"]:checked')?.value || 'boxnow';
  }

  function isFreeDelivery() {
    const shipTo = getShipTo();
    return shipTo === 'store' || shipTo === 'boxnow';
  }

  function getOfficeCourierShipping() {
    const checked = root.querySelector('input[name="office_courier"]:checked');
    return parseFloat(checked?.dataset.shipping || '3.57') || 3.57;
  }

  function getShipping() {
    if (isFreeDelivery()) return 0;
    if (getShipTo() === 'office') return getOfficeCourierShipping();
    const checked = root.querySelector('input[name="courier_id"]:checked');
    return parseFloat(checked?.dataset.shipping || '0') || 0;
  }

  function getPaymentFee() {
    return root.querySelector('input[name="payment_id"]:checked')?.value === '1' ? 1 : 0;
  }

  function isShippingKnown() {
    return checkoutPhase !== 'empty' && checkoutPhase !== 'fast';
  }

  function formatShippingLabel(amount) {
    if (isFreeDelivery()) return 'Безплатно';
    return money(amount);
  }

  function getProductsTotal() {
    let total = 0;
    let qtySum = 0;
    root.querySelectorAll('.cart-card').forEach((card) => {
      const unit = parseFloat(card.dataset.unit || '0') || 0;
      const qty = parseInt(card.querySelector('.qty-control__value')?.textContent || '0', 10) || 0;
      total += unit * qty;
      qtySum += qty;
    });
    return { total, qtySum };
  }

  function updateAsideItems() {
    const list = root.querySelector('.js-aside-items');
    const empty = root.querySelector('.js-aside-empty');
    if (!list) return;
    const cards = root.querySelectorAll('.cart-card');
    if (!cards.length) {
      list.innerHTML = '';
      list.hidden = true;
      if (empty) empty.hidden = false;
      return;
    }
    if (empty) empty.hidden = true;
    list.hidden = false;
    list.innerHTML = [...cards]
      .map((card) => {
        const qty = parseInt(card.querySelector('.qty-control__value')?.textContent || '0', 10) || 0;
        const unit = parseFloat(card.dataset.unit || '0') || 0;
        const title = escapeHtml(card.dataset.name || card.querySelector('.cart-card__title')?.textContent?.trim() || 'Продукт');
        const img = escapeHtml(card.querySelector('.cart-card__image')?.getAttribute('src') || '');
        return `<li class="checkout-aside__item">
          <img class="checkout-aside__item-img" src="${img}" alt="" width="48" height="48" loading="lazy"/>
          <span>
            <span class="checkout-aside__item-name">${title}</span>
            <span class="checkout-aside__item-meta">× ${qty}</span>
          </span>
          <span class="checkout-aside__item-price">${money(unit * qty)}</span>
        </li>`;
      })
      .join('');
  }

  function updateTotals() {
    const { total, qtySum } = getProductsTotal();
    const hasCart = root.querySelectorAll('.cart-card').length > 0;
    const shippingKnown = hasCart && isShippingKnown();
    const shipping = shippingKnown ? getShipping() : 0;
    const paymentFee = hasCart ? getPaymentFee() : 0;
    const grand = total + shipping + paymentFee;
    const countLabel = qtySum === 1 ? '1 продукт' : `${qtySum} продукта`;

    root.querySelectorAll('.js-summary-products').forEach((el) => {
      el.textContent = money(total);
    });
    root.querySelectorAll('.js-summary-shipping').forEach((el) => {
      if (shippingKnown) {
        el.textContent = formatShippingLabel(shipping);
        el.classList.remove('is-pending');
      } else {
        el.textContent = '—';
        el.classList.add('is-pending');
      }
    });
    root.querySelectorAll('.js-summary-total').forEach((el) => {
      el.textContent = money(grand);
    });
    root.querySelectorAll('.js-item-count').forEach((el) => {
      el.textContent = String(qtySum || 0);
    });

    const compactMeta = root.querySelector('.order-summary-compact__meta');
    if (compactMeta) {
      compactMeta.textContent = countLabel;
    }
    updateAsideItems();
  }

  function updateLine(card) {
    const unit = parseFloat(card.dataset.unit || '0') || 0;
    const qty = parseInt(card.querySelector('.qty-control__value')?.textContent || '0', 10) || 0;
    const totalEl = card.querySelector('.js-line-total');
    if (totalEl) totalEl.textContent = money(unit * qty);
    syncCartFromDom();
    updateTotals();
  }

  function syncShipPanels() {
    const shipTo = getShipTo();
    const panelKey =
      shipTo === 'office'
        ? 'office'
        : shipTo === 'store'
          ? 'store'
          : shipTo === 'boxnow'
            ? 'boxnow'
            : 'address';
    root.querySelectorAll('[data-ship-panel]').forEach((panel) => {
      panel.hidden = panel.getAttribute('data-ship-panel') !== panelKey;
    });
    const courierBlock = root.querySelector('[data-ship-courier]');
    if (courierBlock) courierBlock.hidden = isFreeDelivery() || shipTo === 'office';
    if (shipTo === 'office') syncOfficePicker();
    if (shipTo === 'boxnow') filterBoxNowLockers();
    updateTotals();
  }

  let boxnowLocateActive = false;
  /** @type {{ lat: number, lng: number } | null} */
  let boxnowUserCoords = null;
  const boxnowListEl = root.querySelector('#boxnow-locker-list');
  const boxnowOriginalOrder = boxnowListEl
    ? Array.from(boxnowListEl.querySelectorAll('.boxnow-locker'))
    : [];

  function haversineKm(lat1, lng1, lat2, lng2) {
    const toRad = (d) => (d * Math.PI) / 180;
    const R = 6371;
    const dLat = toRad(lat2 - lat1);
    const dLng = toRad(lng2 - lng1);
    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  }

  function setBoxnowLocateStatus(message, kind) {
    const statusEl = root.querySelector('#boxnow-locate-status');
    if (!statusEl) return;
    statusEl.hidden = !message;
    statusEl.textContent = message || '';
    statusEl.classList.toggle('is-error', kind === 'error');
    statusEl.classList.toggle('is-success', kind === 'success');
  }

  function setBoxnowLocateButtonActive(active) {
    const btn = root.querySelector('#boxnow-locate-btn');
    if (!btn) return;
    btn.classList.toggle('is-active', active);
    btn.setAttribute('aria-pressed', active ? 'true' : 'false');
  }

  function clearBoxnowNearestMarkers() {
    root.querySelectorAll('.boxnow-locker').forEach((locker) => {
      locker.classList.remove('is-nearest');
      const near = locker.querySelector('.boxnow-locker__near');
      if (near) near.hidden = true;
    });
  }

  function restoreBoxnowLockerOrder() {
    if (!boxnowListEl) return;
    boxnowOriginalOrder.forEach((locker) => boxnowListEl.appendChild(locker));
  }

  function sortBoxnowLockersByProximity(lat, lng) {
    if (!boxnowListEl) return;
    const lockers = Array.from(boxnowListEl.querySelectorAll('.boxnow-locker'));
    lockers
      .map((locker) => {
        const lockerLat = Number(locker.getAttribute('data-lat'));
        const lockerLng = Number(locker.getAttribute('data-lng'));
        const dist =
          Number.isFinite(lockerLat) && Number.isFinite(lockerLng)
            ? haversineKm(lat, lng, lockerLat, lockerLng)
            : Number.POSITIVE_INFINITY;
        return { locker, dist };
      })
      .sort((a, b) => a.dist - b.dist)
      .forEach(({ locker }) => boxnowListEl.appendChild(locker));
  }

  function markNearestVisibleBoxnowLocker() {
    clearBoxnowNearestMarkers();
    const nearest = Array.from(root.querySelectorAll('.boxnow-locker')).find((locker) => !locker.hidden);
    if (!nearest) return;
    nearest.classList.add('is-nearest');
    const near = nearest.querySelector('.boxnow-locker__near');
    if (near) near.hidden = false;
  }

  function filterBoxNowLockers() {
    const city = root.querySelector('#field-boxnow-city')?.value || '';
    const query = (root.querySelector('#field-boxnow-search')?.value || '').trim().toLowerCase();
    const lockers = root.querySelectorAll('.boxnow-locker');
    const emptyEl = root.querySelector('#boxnow-locker-empty');
    let visible = 0;

    lockers.forEach((locker) => {
      const lockerCity = locker.getAttribute('data-city') || '';
      const label = (locker.getAttribute('data-label') || locker.textContent || '').toLowerCase();
      const cityOk = !city || lockerCity === city;
      const queryOk = !query || label.includes(query);
      const show = cityOk && queryOk;
      locker.hidden = !show;
      if (show) visible += 1;
      else {
        const radio = locker.querySelector('input[type="radio"]');
        if (radio?.checked) radio.checked = false;
      }
    });

    if (emptyEl) emptyEl.hidden = visible > 0;
    if (boxnowLocateActive && boxnowUserCoords) markNearestVisibleBoxnowLocker();
    else clearBoxnowNearestMarkers();
  }

  function disableBoxnowLocate(statusMessage, kind) {
    boxnowLocateActive = false;
    boxnowUserCoords = null;
    setBoxnowLocateButtonActive(false);
    restoreBoxnowLockerOrder();
    filterBoxNowLockers();
    if (statusMessage) setBoxnowLocateStatus(statusMessage, kind || 'error');
    else setBoxnowLocateStatus('', null);
  }

  function enableBoxnowLocateFromCoords(lat, lng) {
    boxnowLocateActive = true;
    boxnowUserCoords = { lat, lng };
    setBoxnowLocateButtonActive(true);
    sortBoxnowLockersByProximity(lat, lng);
    filterBoxNowLockers();
    setBoxnowLocateStatus('Близо до теб — автоматите са подредени по близост.', 'success');
  }

  function toggleBoxnowLocate() {
    const btn = root.querySelector('#boxnow-locate-btn');
    if (!btn) return;

    if (boxnowLocateActive) {
      disableBoxnowLocate();
      return;
    }

    if (!navigator.geolocation) {
      setBoxnowLocateStatus('Геолокацията не се поддържа в този браузър.', 'error');
      return;
    }

    btn.classList.add('is-loading');
    setBoxnowLocateStatus('Определяне на местоположение…', null);

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        btn.classList.remove('is-loading');
        enableBoxnowLocateFromCoords(pos.coords.latitude, pos.coords.longitude);
      },
      (err) => {
        btn.classList.remove('is-loading');
        const denied = err && (err.code === 1 || /denied/i.test(String(err.message || '')));
        setBoxnowLocateStatus(
          denied
            ? 'Достъпът до местоположение е отказан. Можеш да търсиш по име или адрес.'
            : 'Неуспешно определяне на местоположение. Опитай отново.',
          'error'
        );
        setBoxnowLocateButtonActive(false);
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
    );
  }

  function syncPerson() {
    const firms = document.getElementById('checkout-firms');
    const invoice = document.getElementById('want-invoice');
    const personHidden = document.getElementById('checkout-person-value');
    const wantsInvoice = !!invoice?.checked;
    if (firms) firms.hidden = !wantsInvoice;
    if (personHidden) personHidden.value = wantsInvoice ? '2' : '1';
  }

  function syncRecipientPhone() {
    const toggle = document.getElementById('want-recipient-phone');
    const field = document.getElementById('recipient-phone-field');
    const input = document.getElementById('field-address-person-phone');
    const show = !!toggle?.checked;
    if (field) field.hidden = !show;
    if (!show && input) input.value = '';
  }

  function syncInstallmentOptions() {
    const panel = document.getElementById('installment-options');
    if (!panel) return;
    const payment = root.querySelector('input[name="payment_id"]:checked')?.value;
    const show = payment === '8';
    panel.hidden = !show;
    if (!show) {
      panel.querySelectorAll('.installment-option').forEach((btn) => {
        btn.classList.remove('is-selected');
        btn.setAttribute('aria-pressed', 'false');
      });
    }
  }

  function updateStickyLabel() {
    const label = checkoutPhase === 'empty' ? 'Продължи →' : 'Поръчай →';
    root.querySelectorAll('#sticky-cta, #aside-cta').forEach((btn) => {
      btn.textContent = label;
    });
  }

  function updateAsideHint() {
    if (!asideHint) return;
    if (checkoutPhase === 'form' || checkoutPhase === 'done') {
      asideHint.textContent =
        checkoutPhase === 'done'
          ? 'Поръчката е обработена в този UI mockup.'
          : 'Попълни данните и потвърди поръчката.';
    } else {
      asideHint.textContent = '';
    }
  }

  /** One-page checkout: all form sections visible together (Megamag-style). */
  function showActiveCheckout() {
    checkoutPhase = 'form';
    delete root.dataset.orderPlaced;
    setType('1');
    if (formSections) formSections.hidden = false;
    syncMobileRecsVisibility();
    document.getElementById('pane-fast')?.setAttribute('hidden', '');
    updateStickyLabel();
    updateAsideHint();
    updateTotals();
  }

  function validateStep1() {
    const name = root.querySelector('#field-name')?.value.trim();
    const phone = root.querySelector('#field-phone')?.value.trim();
    const email = root.querySelector('#field-email')?.value.trim();
    const err = document.getElementById('step1-error');
    const ok = Boolean(name && phone && email);
    if (err) err.hidden = ok;
    if (!ok) return false;
    const person = root.querySelector('#field-address-person');
    if (person && !person.value.trim()) person.value = name;
    return true;
  }

  function validateFastOrder() {
    const name = root.querySelector('#fast-name')?.value.trim();
    const phone = root.querySelector('#fast-phone')?.value.trim();
    const email = root.querySelector('#field-fast-email')?.value.trim();
    const err = document.getElementById('fast-error');
    const ok = Boolean(name && phone && email);
    if (err) err.hidden = ok;
    return ok;
  }

  function validateStep2() {
    const shipTo = getShipTo();
    const err = document.getElementById('step2-error');
    let ok = false;
    if (shipTo === '1') {
      ok = Boolean(root.querySelector('#field-city')?.value.trim() && root.querySelector('#field-address')?.value.trim());
    } else if (shipTo === 'office') {
      ok = Boolean(
        root.querySelector('#field-office-city')?.value.trim() &&
          root.querySelector('#field-office')?.value &&
          root.querySelector('#field-office')?.value !== '0'
      );
    } else if (shipTo === 'store') {
      ok = Boolean(root.querySelector('#field-store')?.value);
    } else if (shipTo === 'boxnow') {
      ok = Boolean(root.querySelector('input[name="boxnow_locker"]:checked')?.value);
    }
    if (err) err.hidden = ok;
    return ok;
  }

  function validateCheckout() {
    const ok1 = validateStep1();
    const ok2 = validateStep2();
    if (!ok1 || !ok2) {
      const firstErr = root.querySelector('.field-error:not([hidden])');
      firstErr?.closest('section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    return ok1 && ok2;
  }

  function attemptOrder() {
    const note = document.getElementById('checkout-mock-note');
    const btns = root.querySelectorAll('.checkout-finish, #sticky-cta, #aside-cta');
    btns.forEach((btn) => {
      btn.classList.add('is-loading');
      btn.dataset.prev = btn.textContent;
      btn.textContent = 'Обработка...';
    });
    window.setTimeout(() => {
      btns.forEach((btn) => {
        btn.classList.remove('is-loading');
        if (btn.dataset.prev) btn.textContent = btn.dataset.prev;
      });
      checkoutPhase = 'done';
      root.dataset.orderPlaced = '1';
      if (note) {
        note.hidden = false;
        note.textContent = 'Поръчката е готова за преглед в този UI mockup (без сървърно изпращане).';
      }
      updateAsideHint();
    }, 650);
  }

  function handleSticky() {
    if (checkoutPhase === 'form') {
      if (!validateCheckout()) return;
      attemptOrder();
    }
  }

  function initPromoDisclosure(toggleId, panelId, inputId, msgId) {
    const promoToggle = document.getElementById(toggleId);
    const promoPanel = document.getElementById(panelId);
    const promoMsg = document.getElementById(msgId);
    const promoInput = document.getElementById(inputId);
    if (!promoToggle || !promoPanel) return;

    promoToggle.addEventListener('click', () => {
      const open = promoPanel.hasAttribute('hidden');
      promoPanel.toggleAttribute('hidden', !open);
      promoToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      const plus = promoToggle.querySelector('.promo-disclosure__plus');
      if (plus) plus.textContent = open ? '−' : '+';
    });

    promoPanel.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!promoMsg) return;
      const code = promoInput?.value.trim() || '';
      promoMsg.hidden = false;
      promoMsg.textContent = code
        ? 'Промо кодът е приложен визуално в този UI.'
        : 'Въведи промо код.';
    });
  }

  // Events
  root.addEventListener('click', (e) => {
    const qtyBtn = e.target.closest('[data-qty-delta]');
    if (qtyBtn) {
      const card = qtyBtn.closest('.cart-card');
      const valueEl = card?.querySelector('.qty-control__value');
      if (!card || !valueEl) return;
      const delta = parseInt(qtyBtn.getAttribute('data-qty-delta') || '0', 10) || 0;
      valueEl.textContent = String(Math.max(1, (parseInt(valueEl.textContent || '1', 10) || 1) + delta));
      updateLine(card);
      return;
    }

    if (e.target.closest('[data-remove]')) {
      const card = e.target.closest('.cart-card');
      card?.remove();
      syncCartFromDom();
      if (!root.querySelector('.cart-card')) {
        const list = root.querySelector('.cart-cards');
        if (list) {
          list.innerHTML =
            '<li class="cart-cards__empty text-on-surface-variant py-6 text-center">Количката е празна. <a class="text-apricot" href="hot-summer-sale-2026.html#laptopi">Разгледай продуктите</a></li>';
        }
        setEmptyCheckoutUi(true);
      }
      updateTotals();
      return;
    }

    if (e.target.closest('[data-start-fast]')) {
      setType('3');
      checkoutPhase = 'fast';
      if (formSections) formSections.hidden = true;
      syncMobileRecsVisibility();
      document.getElementById('pane-fast')?.removeAttribute('hidden');
      document.getElementById('pane-fast')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      updateStickyLabel();
      updateAsideHint();
      return;
    }

    if (e.target.closest('[data-back-gate]')) {
      showActiveCheckout();
      return;
    }

    if (e.target.closest('[data-sticky-cta]')) {
      handleSticky();
      return;
    }

    if (e.target.closest('.checkout-finish')) {
      if (checkoutPhase === 'form' && !validateCheckout()) return;
      if (checkoutPhase === 'fast' && !validateFastOrder()) return;
      attemptOrder();
    }
  });

  initPromoDisclosure('promo-toggle', 'promo-panel', 'promo-code', 'promo-msg');
  initPromoDisclosure('aside-promo-toggle', 'aside-promo-panel', 'aside-promo-code', 'aside-promo-msg');

  root.querySelectorAll('input[name="ship_to_id[2]"]').forEach((el) => {
    el.addEventListener('change', () => {
      syncShipPanels();
      updateTotals();
    });
  });
  root.querySelector('#field-store')?.addEventListener('change', updateTotals);
  root.querySelector('#field-boxnow-city')?.addEventListener('change', () => {
    filterBoxNowLockers();
    updateTotals();
  });
  root.querySelector('#field-boxnow-search')?.addEventListener('input', filterBoxNowLockers);
  root.querySelector('#boxnow-locate-btn')?.addEventListener('click', toggleBoxnowLocate);
  root.querySelectorAll('input[name="boxnow_locker"]').forEach((el) => {
    el.addEventListener('change', updateTotals);
  });
  root.querySelectorAll('input[name="courier_id"], input[name="office_courier"], input[name="payment_id"]').forEach((el) => {
    el.addEventListener('change', () => {
      if (el.name === 'office_courier') syncOfficePicker();
      updateTotals();
      if (el.name === 'payment_id') syncInstallmentOptions();
    });
  });
  const wantInvoice = document.getElementById('want-invoice');
  if (wantInvoice) wantInvoice.addEventListener('change', syncPerson);

  const wantRecipientPhone = document.getElementById('want-recipient-phone');
  if (wantRecipientPhone) wantRecipientPhone.addEventListener('change', syncRecipientPhone);
  syncRecipientPhone();

  const installmentPanel = document.getElementById('installment-options');
  if (installmentPanel) {
    installmentPanel.addEventListener('click', (e) => {
      const btn = e.target.closest('.installment-option');
      if (!btn || !installmentPanel.contains(btn)) return;
      installmentPanel.querySelectorAll('.installment-option').forEach((other) => {
        const active = other === btn;
        other.classList.toggle('is-selected', active);
        other.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
    });
  }

  const CITIES = ['София', 'Пловдив', 'Варна', 'Бургас', 'Русе', 'Стара Загора', 'Плевен', 'Добрич', 'Сливен', 'Шумен'];
  const OFFICES = [
    { value: 'sp-1', courier: 'speedy', label: 'Спиди — бул. Витоша 100' },
    { value: 'sp-2', courier: 'speedy', label: 'Спиди — Младост 1' },
    { value: 'sp-3', courier: 'speedy', label: 'Спиди — Люлин 5' },
    { value: 'sp-4', courier: 'speedy', label: 'Спиди — Надежда 2' },
    { value: 'ec-1', courier: 'econt', label: 'Еконт — бул. Витоша 88' },
    { value: 'ec-2', courier: 'econt', label: 'Еконт — Младост 4' },
    { value: 'ec-3', courier: 'econt', label: 'Еконт — Център Пловдив' },
    { value: 'ec-4', courier: 'econt', label: 'Еконт — Варна Мол' },
  ];

  function getOfficeCourier() {
    return root.querySelector('input[name="office_courier"]:checked')?.value || 'speedy';
  }

  function getOfficesForCourier(courier) {
    return OFFICES.filter((office) => office.courier === courier);
  }

  function syncOfficePicker() {
    const officeWrap = root.querySelector('[data-searchable="office"]');
    if (!officeWrap) return;
    const hidden = officeWrap.querySelector('#field-office');
    const searchInput = officeWrap.querySelector('#field-office-search');
    const currentCourier = getOfficeCourier();
    const currentValue = hidden?.value || '0';
    const stillValid = getOfficesForCourier(currentCourier).some((office) => office.value === currentValue);
    if (!stillValid) {
      if (hidden) hidden.value = '0';
      if (searchInput) searchInput.value = '';
    }
  }

  function initSearchField(wrapper, items, { getLabel, getValue, onSelect, filterItems } = {}) {
    const input = wrapper.querySelector('.search-field__input');
    const list = wrapper.querySelector('.search-field__results');
    if (!input || !list) return;

    const labelOf = getLabel || ((item) => (typeof item === 'string' ? item : item.label));
    const valueOf = getValue || ((item) => (typeof item === 'string' ? item : item.value));
    const itemsOf = filterItems || (() => items);
    let activeIndex = -1;

    function close() {
      list.hidden = true;
      input.setAttribute('aria-expanded', 'false');
      activeIndex = -1;
    }

    function open() {
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }

    function render(query) {
      const q = (query || '').trim().toLowerCase();
      const filtered = itemsOf().filter((item) => labelOf(item).toLowerCase().includes(q));
      list.innerHTML = '';

      if (!filtered.length) {
        const empty = document.createElement('li');
        empty.className = 'search-field__empty';
        empty.textContent = 'Няма резултати';
        list.appendChild(empty);
        open();
        return;
      }

      filtered.slice(0, 8).forEach((item, index) => {
        const li = document.createElement('li');
        li.setAttribute('role', 'option');
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'search-field__option';
        btn.textContent = labelOf(item);
        btn.dataset.index = String(index);
        btn.addEventListener('mousedown', (e) => {
          e.preventDefault();
          input.value = labelOf(item);
          if (onSelect) onSelect(item, valueOf(item));
          close();
        });
        li.appendChild(btn);
        list.appendChild(li);
      });
      activeIndex = -1;
      open();
    }

    input.addEventListener('focus', () => render(input.value));
    input.addEventListener('input', () => render(input.value));
    input.addEventListener('keydown', (e) => {
      const options = Array.from(list.querySelectorAll('.search-field__option'));
      if (!options.length) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = Math.min(options.length - 1, activeIndex + 1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = Math.max(0, activeIndex - 1);
      } else if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        options[activeIndex].dispatchEvent(new Event('mousedown'));
        return;
      } else if (e.key === 'Escape') {
        close();
        return;
      } else {
        return;
      }
      options.forEach((opt, i) => opt.classList.toggle('is-active', i === activeIndex));
    });
    input.addEventListener('blur', () => {
      window.setTimeout(close, 120);
    });
  }

  root.querySelectorAll('[data-searchable="city"]').forEach((wrapper) => {
    initSearchField(wrapper, CITIES);
  });

  const officeWrap = root.querySelector('[data-searchable="office"]');
  if (officeWrap) {
    const hidden = officeWrap.querySelector('#field-office');
    initSearchField(officeWrap, OFFICES, {
      getLabel: (item) => item.label,
      getValue: (item) => item.value,
      onSelect: (_item, value) => {
        if (hidden) hidden.value = value;
      },
      filterItems: () => getOfficesForCourier(getOfficeCourier()),
    });
  }

  /* Auth modal: handled by auth-modal.js ([data-open-auth-modal]) */

  renderStoredCart();
  syncShipPanels();
  syncPerson();
  syncInstallmentOptions();
  updateTotals();
  if (root.querySelector('.cart-card')) {
    showActiveCheckout();
  } else {
    setEmptyCheckoutUi(true);
  }
})();
