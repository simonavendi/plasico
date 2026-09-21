/**
 * plasico-cart-adapter.js
 *
 * Single integration boundary between the Spatial Minimalism UI and the real
 * Plasico backend. No other file may talk to the backend directly.
 *
 * Verified live contract (curl against https://plasico.bg, 2026-09-16):
 *
 *   add            POST <cartPath>            action=buy&prod_id=<id>&quantity=<n>
 *   read            GET <ajaxPath>?get_cart=1
 *   set quantity    GET <ajaxPath>?get_cart=1&<server-authored query with quantity replaced>
 *   remove          GET <ajaxPath>?get_cart=1&<server-authored query, quantity=0>
 *
 * The response is an HTML fragment, never JSON. An empty cart responds with a
 * zero-length body. The line identifier is the server's `cart_id`, which is a
 * cart-line id and NOT the product id, so it can only be learned by reading the
 * server-authored links out of the fragment.
 *
 * Quantity is ABSOLUTE, not a delta. quantity=0 removes the line.
 *
 * Session is carried by the `plasico` cookie (domain .plasico.bg, Max-Age 7200,
 * no SameSite attribute => browsers treat it as Lax). That makes the contract
 * same-origin only; see PlasicoCartConfig.origin.
 */
(function () {
  'use strict';

  /* ------------------------------------------------------------------ config */

  var DEFAULTS = {
    // '' means same-origin, which is the real deployment target (Vercel serves
    // this tree). Point it at a proxy when running the mirror locally.
    origin: '',
    // Percent-encoded Cyrillic "поръчка".
    cartPath: '/%D0%BF%D0%BE%D1%80%D1%8A%D1%87%D0%BA%D0%B0',
    ajaxPath: '/ajax.php',
    getCartParam: 'get_cart=1',
    // Render cache only. NEVER authoritative — except in local mode (below).
    cacheKey: 'plasico-hss2026-cart',
    useCache: true,
    // 'auto' | 'remote' | 'local'
    // auto: use the live PHP backend only on plasico.bg; everywhere else
    // (Vercel preview, localhost, file://) keep a localStorage cart because
    // /ajax.php is blocked on Vercel and the mirror has no PHP backend.
    mode: 'auto',
    // Test seam: (url, init) => Promise<{ok, status, text}>. Null = real fetch.
    transport: null,
    debug: false
  };

  var config = {};
  for (var k in DEFAULTS) config[k] = DEFAULTS[k];
  if (window.PlasicoCartConfig) {
    for (var ck in window.PlasicoCartConfig) {
      if (Object.prototype.hasOwnProperty.call(window.PlasicoCartConfig, ck)) {
        config[ck] = window.PlasicoCartConfig[ck];
      }
    }
  }

  function log() {
    if (!config.debug) return;
    try { console.log.apply(console, ['[plasico-cart]'].concat([].slice.call(arguments))); } catch (e) {}
  }

  function ajaxUrl(extraQuery) {
    var base = config.origin + config.ajaxPath + '?' + config.getCartParam;
    return extraQuery ? base + '&' + extraQuery : base;
  }

  function cartUrl() {
    return config.origin + config.cartPath;
  }

  function isLiveShopHost() {
    try {
      var h = String(window.location.hostname || '').toLowerCase();
      return h === 'plasico.bg' || h === 'www.plasico.bg';
    } catch (e) {
      return false;
    }
  }

  function preferLocalMode() {
    if (config.mode === 'local') return true;
    if (config.mode === 'remote') return false;
    // mode === 'auto'
    try {
      if (window.location.protocol === 'file:') return true;
    } catch (e) {}
    return !isLiveShopHost();
  }

  /* ------------------------------------------------------------------- state */

  // Normalized, in-memory, backend-derived model. The single source of truth
  // for the UI; replaced wholesale after every successful backend response.
  var model = emptyModel();
  var lastError = null;
  var listeners = [];
  var initialised = false;
  // Once we know the PHP backend is unreachable, stay on local cart for the
  // rest of the page lifetime (avoids repeated 403/404 noise on Vercel).
  var forceLocal = preferLocalMode();

  function emptyModel() {
    return {
      quantity: 0,
      lineCount: 0,
      subtotal: 0,
      currency: '\u20ac',
      items: [],
      checkoutUrl: '',
      loaded: false,
      raw: ''
    };
  }

  function subscribe(fn) {
    if (typeof fn !== 'function') return function () {};
    listeners.push(fn);
    return function () {
      var i = listeners.indexOf(fn);
      if (i > -1) listeners.splice(i, 1);
    };
  }

  function emit() {
    var snapshot = getCart();
    listeners.forEach(function (fn) {
      try { fn(snapshot); } catch (e) { log('listener error', e); }
    });
    try {
      document.dispatchEvent(new CustomEvent('plasico:cart-updated', { detail: snapshot }));
    } catch (e) {}
  }

  function emitError(err) {
    lastError = err;
    try {
      document.dispatchEvent(new CustomEvent('plasico:cart-error', { detail: err }));
    } catch (e) {}
  }

  /* ------------------------------------------------------------ render cache */

  function writeCache(m) {
    if (!config.useCache) return;
    try {
      localStorage.setItem(config.cacheKey, JSON.stringify({
        // local-cart is authoritative on the mirror; render-cache is paint-only
        // when talking to the live PHP backend.
        __source: forceLocal ? 'local-cart' : 'render-cache',
        quantity: m.quantity,
        subtotal: m.subtotal,
        items: m.items
      }));
    } catch (e) {}
  }

  function legacyItemsToModel(arr) {
    var m = emptyModel();
    m.loaded = true;
    (arr || []).forEach(function (entry) {
      if (!entry) return;
      var id = String(entry.id || entry.productId || '').trim();
      if (!id) return;
      var qty = Math.max(1, parseInt(entry.qty != null ? entry.qty : entry.quantity, 10) || 1);
      var unit = Number(entry.price);
      if (!isFinite(unit)) unit = 0;
      m.items.push({
        lineId: 'local-' + id,
        productId: id,
        title: entry.title || entry.name || 'Продукт',
        href: entry.href || '',
        image: entry.image || '',
        alt: entry.alt || entry.title || '',
        category: entry.category || '',
        lineTotal: unit * qty,
        unitPrice: unit,
        quantity: qty,
        isGift: false,
        serverQuery: '',
        removeQuery: '',
        incQuery: '',
        decQuery: '',
        mutable: true
      });
    });
    recomputeLocalTotals(m);
    return m;
  }

  function recomputeLocalTotals(m) {
    m.lineCount = m.items.length;
    m.quantity = m.items.reduce(function (s, it) {
      return s + (Number(it.quantity) || 0);
    }, 0);
    m.subtotal = m.items.reduce(function (s, it) {
      return s + (Number(it.lineTotal) || 0);
    }, 0);
    m.checkoutUrl = m.checkoutUrl || 'poruchka.html';
    m.loaded = true;
  }

  function readCache() {
    if (!config.useCache) return null;
    try {
      var raw = localStorage.getItem(config.cacheKey);
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      // Legacy shape was a bare array written by the old localStorage cart /
      // product-page.js fallback. Promote it when we are in local mode.
      if (Array.isArray(parsed)) {
        return forceLocal ? legacyItemsToModel(parsed) : null;
      }
      if (!parsed || typeof parsed !== 'object') return null;
      if (parsed.__source === 'local-cart') {
        var local = emptyModel();
        local.loaded = true;
        local.items = Array.isArray(parsed.items) ? parsed.items.slice() : [];
        local.quantity = parsed.quantity || 0;
        local.subtotal = parsed.subtotal || 0;
        recomputeLocalTotals(local);
        return local;
      }
      if (parsed.__source !== 'render-cache') return null;
      return parsed;
    } catch (e) {
      return null;
    }
  }

  function lookupDomMeta(productId) {
    var id = String(productId || '');
    if (!id || !document || !document.querySelector) return null;
    var host =
      document.querySelector('[data-product-page][data-product-id="' + id + '"]') ||
      document.querySelector('[data-id="' + id + '"]');
    if (!host) return null;

    if (host.hasAttribute && host.hasAttribute('data-product-page')) {
      return {
        title: host.getAttribute('data-product-title') || '',
        price: parseFloat(host.getAttribute('data-product-price') || '0') || 0,
        image: host.getAttribute('data-product-image') || '',
        href: (window.location.pathname.split('/').pop()) || '',
        alt: host.getAttribute('data-product-title') || ''
      };
    }

    var titleLink = host.querySelector('h4 a') || host.querySelector('a[href*=".html"]');
    var img = host.querySelector('.aspect-square img') || host.querySelector('img');
    var price = parseFloat(host.getAttribute('data-price') || host.dataset && host.dataset.price || '0');
    return {
      title: titleLink ? titleLink.textContent.trim() : (host.getAttribute('data-name') || 'Продукт'),
      price: isFinite(price) ? price : 0,
      image: img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : '',
      href: titleLink ? (titleLink.getAttribute('href') || '') : (host.getAttribute('data-href') || ''),
      alt: img ? (img.getAttribute('alt') || '') : ''
    };
  }

  function commitLocal(next) {
    model = next;
    lastError = null;
    writeCache(model);
    emit();
    return getCart();
  }

  function localAdd(productId, quantity, meta) {
    var id = String(productId || '').trim();
    if (!id) return Promise.reject(fail('add', 'missing product id'));
    var qty = Math.max(1, parseInt(quantity, 10) || 1);
    meta = meta || lookupDomMeta(id) || {};

    var next = emptyModel();
    next.items = model.items.map(function (it) {
      var copy = {};
      for (var p in it) if (Object.prototype.hasOwnProperty.call(it, p)) copy[p] = it[p];
      return copy;
    });

    var existing = null;
    for (var i = 0; i < next.items.length; i++) {
      if (String(next.items[i].productId) === id) {
        existing = next.items[i];
        break;
      }
    }

    if (existing) {
      existing.quantity = (Number(existing.quantity) || 0) + qty;
      var unit = Number(existing.unitPrice);
      if (!isFinite(unit) || unit <= 0) {
        unit = Number(meta.price);
        if (!isFinite(unit)) unit = 0;
        existing.unitPrice = unit;
      }
      existing.lineTotal = unit * existing.quantity;
      if (meta.title) existing.title = meta.title;
      if (meta.image) existing.image = meta.image;
      if (meta.href) existing.href = meta.href;
    } else {
      var unitPrice = Number(meta.price);
      if (!isFinite(unitPrice)) unitPrice = 0;
      next.items.push({
        lineId: 'local-' + id,
        productId: id,
        title: meta.title || ('Продукт #' + id),
        href: meta.href || '',
        image: meta.image || '',
        alt: meta.alt || meta.title || '',
        category: meta.category || '',
        lineTotal: unitPrice * qty,
        unitPrice: unitPrice,
        quantity: qty,
        isGift: false,
        serverQuery: '',
        removeQuery: '',
        incQuery: '',
        decQuery: '',
        mutable: true
      });
    }

    recomputeLocalTotals(next);
    return Promise.resolve(commitLocal(next));
  }

  function localUpdateItem(lineId, quantity) {
    var id = String(lineId);
    var next = emptyModel();
    next.items = [];
    model.items.forEach(function (it) {
      if (String(it.lineId) !== id) {
        var copy = {};
        for (var p in it) if (Object.prototype.hasOwnProperty.call(it, p)) copy[p] = it[p];
        next.items.push(copy);
        return;
      }
      var qty = Math.max(0, parseInt(quantity, 10) || 0);
      if (qty <= 0) return;
      var row = {};
      for (var q in it) if (Object.prototype.hasOwnProperty.call(it, q)) row[q] = it[q];
      row.quantity = qty;
      var unit = Number(row.unitPrice);
      if (!isFinite(unit) || unit < 0) {
        unit = qty ? (Number(row.lineTotal) || 0) / (Number(it.quantity) || qty) : 0;
        row.unitPrice = unit;
      }
      row.lineTotal = unit * qty;
      next.items.push(row);
    });
    recomputeLocalTotals(next);
    return Promise.resolve(commitLocal(next));
  }

  function localRemoveItem(lineId) {
    return localUpdateItem(lineId, 0);
  }

  function localRefresh() {
    var cached = readCache();
    if (cached && Array.isArray(cached.items)) {
      var m = emptyModel();
      m.items = cached.items.slice();
      m.quantity = cached.quantity || 0;
      m.subtotal = cached.subtotal || 0;
      recomputeLocalTotals(m);
      return Promise.resolve(commitLocal(m));
    }
    return Promise.resolve(commitLocal(emptyModel()));
  }

  function isHardBackendFailure(err) {
    if (!err) return false;
    var detail = String(err.detail || err.message || err);
    if (/HTTP 404|HTTP 403|HTTP 502|HTTP 503/i.test(detail)) return true;
    if (/Failed to fetch|NetworkError|Load failed/i.test(detail)) return true;
    return false;
  }

  function enableLocalFallback(reason) {
    if (forceLocal) return;
    forceLocal = true;
    log('switching to local cart', reason);
  }

  /* ----------------------------------------------------------------- parsing */

  function parseMoney(text) {
    if (!text) return 0;
    // Server prints dot-decimal, e.g. "1399.98", with &nbsp; before the sign.
    var cleaned = String(text).replace(/\u00a0/g, ' ').replace(/[^\d.,-]/g, '').trim();
    if (!cleaned) return 0;
    // If both separators appear, the last one is the decimal separator.
    var lastDot = cleaned.lastIndexOf('.');
    var lastComma = cleaned.lastIndexOf(',');
    if (lastDot > -1 && lastComma > -1) {
      if (lastComma > lastDot) cleaned = cleaned.replace(/\./g, '').replace(',', '.');
      else cleaned = cleaned.replace(/,/g, '');
    } else if (lastComma > -1) {
      cleaned = cleaned.replace(',', '.');
    }
    var n = parseFloat(cleaned);
    return isFinite(n) ? n : 0;
  }

  /** Product id is only recoverable from the product URL slug: ...-<id>.html */
  function productIdFromHref(href) {
    if (!href) return '';
    var m = /-(\d+)\.html(?:[?#]|$)/.exec(href);
    return m ? m[1] : '';
  }

  function absolutize(url) {
    if (!url) return '';
    try { return new URL(url, config.origin || window.location.href).href; }
    catch (e) { return url; }
  }

  /**
   * Extract the server-authored query string from an action link, verbatim.
   * We never invent parameter names; whatever the server put after '?' is what
   * gets replayed. This mirrors plasico165.js:332, which does exactly:
   *   $('#cart').trigger('reload', ['&' + $(this).attr('href').split('?')[1]])
   */
  function serverQueryFrom(anchor) {
    if (!anchor) return '';
    var href = anchor.getAttribute('href') || '';
    var qIndex = href.indexOf('?');
    if (qIndex === -1) return '';
    return href.slice(qIndex + 1);
  }

  /**
   * Re-use a server-authored query string but substitute a new quantity.
   * Only the value is changed; every other parameter (cart_id and anything
   * else the backend chose to include) is preserved byte-for-byte and in order.
   */
  function withQuantity(serverQuery, quantity) {
    if (!serverQuery) return '';
    var seen = false;
    var rebuilt = serverQuery.split('&').map(function (pair) {
      var eq = pair.indexOf('=');
      var name = eq === -1 ? pair : pair.slice(0, eq);
      if (name === 'quantity') {
        seen = true;
        return name + '=' + encodeURIComponent(String(quantity));
      }
      return pair;
    }).join('&');
    if (!seen) rebuilt += '&quantity=' + encodeURIComponent(String(quantity));
    return rebuilt;
  }

  /**
   * Parse the #cart-ajax HTML fragment into the normalized model.
   * An empty cart is served as a zero-length body.
   */
  function parseCartHtml(html) {
    var m = emptyModel();
    m.loaded = true;
    m.raw = html || '';

    if (!html || !String(html).trim()) return m;

    var doc = new DOMParser().parseFromString(String(html), 'text/html');
    var rootEl = doc.getElementById('cart-ajax') ||
                 doc.querySelector('.cart-ajax') ||
                 doc.body;

    if (rootEl && rootEl.hasAttribute && rootEl.hasAttribute('data-quantity')) {
      var q = parseInt(rootEl.getAttribute('data-quantity'), 10);
      m.quantity = isNaN(q) ? 0 : q;
    }

    var finishLink = rootEl.querySelector ? rootEl.querySelector('.finish a[href]') : null;
    if (finishLink) m.checkoutUrl = absolutize(finishLink.getAttribute('href'));

    var table = rootEl.querySelector ? rootEl.querySelector('#cart-table') : null;
    if (!table) {
      // No table but a non-empty body: treat as empty rather than guessing.
      return m;
    }

    // Only body rows. tfoot holds the totals, thead/#cart-head the labels.
    var rows = Array.prototype.filter.call(table.querySelectorAll('tr'), function (tr) {
      return !tr.closest('tfoot') && !tr.closest('thead') && !tr.querySelector('th');
    });

    rows.forEach(function (tr) {
      var titleLink = tr.querySelector('td.l a[href]') ||
                      tr.querySelector('a:not(.img):not(.act)');
      var imgLink = tr.querySelector('a.img');
      var img = tr.querySelector('img');
      var href = absolutize(titleLink ? titleLink.getAttribute('href')
                                      : (imgLink ? imgLink.getAttribute('href') : ''));

      // Any .act link is a server-authored mutation URL. `.del` is the remove
      // variant; the checkout table additionally renders .inc / .dec.
      var removeLink = tr.querySelector('a.act.del') || tr.querySelector('a.act[class*="del"]');
      var incLink = tr.querySelector('a.act.inc');
      var decLink = tr.querySelector('a.act.dec');
      var anyAct = removeLink || incLink || decLink || tr.querySelector('a.act');

      var removeQuery = serverQueryFrom(removeLink);
      var templateQuery = removeQuery || serverQueryFrom(anyAct);

      var lineId = '';
      if (templateQuery) {
        var mm = /(?:^|&)cart_id=([^&]+)/.exec(templateQuery);
        if (mm) lineId = decodeURIComponent(mm[1]);
      }

      var subtotalEl = tr.querySelector('.subtotal');
      var giftEl = tr.querySelector('.gift');
      var catEl = tr.querySelector('.cat');
      var qtyEl = tr.querySelector('.quan');

      var title = titleLink ? titleLink.textContent.trim() : '';
      if (!title && img) title = img.getAttribute('alt') || '';

      m.items.push({
        lineId: lineId,
        productId: productIdFromHref(href),
        title: title,
        href: href,
        image: img ? absolutize(img.getAttribute('src')) : '',
        alt: img ? (img.getAttribute('alt') || title) : title,
        category: catEl ? catEl.textContent.trim() : '',
        lineTotal: subtotalEl ? parseMoney(subtotalEl.textContent) : 0,
        // Server renders quantity only on the checkout table; the mini-cart
        // omits it, so absence means "unknown", not "zero".
        quantity: qtyEl ? (parseInt(qtyEl.textContent, 10) || null) : null,
        isGift: !!giftEl,
        // Verbatim server-authored queries. Never synthesized.
        serverQuery: templateQuery,
        removeQuery: removeQuery,
        incQuery: serverQueryFrom(incLink),
        decQuery: serverQueryFrom(decLink),
        mutable: !!templateQuery
      });
    });

    m.lineCount = m.items.length;

    var grand = rootEl.querySelector('tfoot .totals.grand span') ||
                rootEl.querySelector('.totals.grand span') ||
                rootEl.querySelector('tfoot .totals span');
    if (grand) {
      m.subtotal = parseMoney(grand.textContent);
    } else {
      m.subtotal = m.items.reduce(function (s, it) { return s + (it.lineTotal || 0); }, 0);
    }

    return m;
  }

  /* --------------------------------------------------------------- transport */

  function request(url, init) {
    if (typeof config.transport === 'function') {
      return Promise.resolve(config.transport(url, init || {}));
    }
    var opts = Object.assign({
      // Session cookie must ride along; only works same-origin.
      credentials: 'include',
      headers: {}
    }, init || {});
    opts.headers = Object.assign({
      // Matches what jQuery sends on the legacy site.
      'X-Requested-With': 'XMLHttpRequest'
    }, opts.headers || {});

    return fetch(url, opts).then(function (res) {
      return res.text().then(function (text) {
        return { ok: res.ok, status: res.status, text: text };
      });
    });
  }

  function fail(operation, detail) {
    var err = new Error('[plasico-cart] ' + operation + ' failed: ' + detail);
    err.operation = operation;
    err.detail = detail;
    return err;
  }

  /**
   * Every backend call funnels through here so that the model is replaced ONLY
   * after a genuinely successful response. Nothing is applied optimistically,
   * which is the deliberate improvement over plasico165.js (no .fail(), toasts
   * a success message even on HTTP 500).
   */
  function commit(operation, url, init) {
    return request(url, init).then(function (res) {
      if (!res || res.ok === false) {
        throw fail(operation, 'HTTP ' + (res ? res.status : 'no response'));
      }
      var next = parseCartHtml(res.text);
      model = next;
      lastError = null;
      writeCache(model);
      emit();
      return getCart();
    }).catch(function (err) {
      var wrapped = err instanceof Error ? err : fail(operation, String(err));
      wrapped.operation = wrapped.operation || operation;
      log('error', operation, wrapped);
      emitError(wrapped);
      throw wrapped;
    });
  }

  // Mutations are serialized. The legacy $.ajaxSetup aborts the previous
  // request globally (plasico165.js:412), so concurrent cart writes there
  // cancel each other; queueing avoids that class of race entirely.
  var queue = Promise.resolve();
  function enqueue(task) {
    var run = queue.then(task, task);
    queue = run.catch(function () {});
    return run;
  }

  /* ---------------------------------------------------------------- public API */

  function getCart() {
    return {
      quantity: model.quantity,
      lineCount: model.lineCount,
      subtotal: model.subtotal,
      currency: model.currency,
      checkoutUrl: model.checkoutUrl,
      loaded: model.loaded,
      isEmpty: model.quantity === 0 && model.items.length === 0,
      items: model.items.map(function (it) {
        var copy = {};
        for (var p in it) if (Object.prototype.hasOwnProperty.call(it, p)) copy[p] = it[p];
        return copy;
      })
    };
  }

  function refresh() {
    if (forceLocal) return enqueue(function () { return localRefresh(); });
    return enqueue(function () {
      return commit('refresh', ajaxUrl()).catch(function (err) {
        if (isHardBackendFailure(err)) {
          enableLocalFallback(err);
          return localRefresh();
        }
        throw err;
      });
    });
  }

  function add(productId, quantity, meta) {
    var id = String(productId || '').trim();
    if (!id) return Promise.reject(fail('add', 'missing product id'));
    var qty = Math.max(1, parseInt(quantity, 10) || 1);

    if (forceLocal) {
      return enqueue(function () { return localAdd(id, qty, meta); });
    }

    var body = 'action=buy&prod_id=' + encodeURIComponent(id) +
               '&quantity=' + encodeURIComponent(String(qty));

    return enqueue(function () {
      // The POST response is the full checkout page, not a cart fragment, so we
      // verify it succeeded and then read the cart back through the real
      // read endpoint rather than trying to parse the page.
      return request(cartUrl(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: body
      }).then(function (res) {
        if (!res || res.ok === false) {
          throw fail('add', 'HTTP ' + (res ? res.status : 'no response'));
        }
        return commit('add:read-back', ajaxUrl());
      }).catch(function (err) {
        var wrapped = err instanceof Error ? err : fail('add', String(err));
        wrapped.operation = wrapped.operation || 'add';
        if (isHardBackendFailure(wrapped)) {
          enableLocalFallback(wrapped);
          return localAdd(id, qty, meta);
        }
        emitError(wrapped);
        throw wrapped;
      });
    });
  }

  function findLine(lineId) {
    var id = String(lineId);
    for (var i = 0; i < model.items.length; i++) {
      if (String(model.items[i].lineId) === id) return model.items[i];
    }
    return null;
  }

  /**
   * Absolute quantity, per the verified contract. Replays the server's own
   * query string with only the quantity value substituted.
   */
  function updateItem(lineId, quantity) {
    if (forceLocal || (String(lineId || '').indexOf('local-') === 0)) {
      return enqueue(function () { return localUpdateItem(lineId, quantity); });
    }
    var line = findLine(lineId);
    if (!line) return Promise.reject(fail('updateItem', 'unknown line ' + lineId));
    if (!line.serverQuery) {
      return Promise.reject(fail('updateItem', 'line ' + lineId + ' has no server-authored action URL'));
    }
    var qty = Math.max(0, parseInt(quantity, 10) || 0);
    var query = withQuantity(line.serverQuery, qty);
    return enqueue(function () { return commit('updateItem', ajaxUrl(query)); });
  }

  function removeItem(lineId) {
    if (forceLocal || (String(lineId || '').indexOf('local-') === 0)) {
      return enqueue(function () { return localRemoveItem(lineId); });
    }
    var line = findLine(lineId);
    if (!line) return Promise.reject(fail('removeItem', 'unknown line ' + lineId));
    // Prefer the server's own remove URL verbatim; it already carries quantity=0.
    var query = line.removeQuery || withQuantity(line.serverQuery, 0);
    if (!query) return Promise.reject(fail('removeItem', 'no server-authored remove URL for line ' + lineId));
    return enqueue(function () { return commit('removeItem', ajaxUrl(query)); });
  }

  /** No backend clear-all endpoint exists; remove each mutable line in turn. */
  function clear() {
    var ids = model.items.filter(function (i) { return i.mutable; }).map(function (i) { return i.lineId; });
    var chain = Promise.resolve(getCart());
    ids.forEach(function (id) {
      chain = chain.then(function () {
        return findLine(id) ? removeItem(id) : getCart();
      });
    });
    return chain;
  }

  function step(lineId, delta) {
    var line = findLine(lineId);
    if (!line) return Promise.reject(fail('step', 'unknown line ' + lineId));
    var current = line.quantity;
    if (current == null) {
      // Mini-cart fragment omits per-line quantity. Derive it from the line
      // total when possible so +/- stays meaningful without inventing state.
      return Promise.reject(fail('step',
        'line ' + lineId + ' quantity not reported by backend; use updateItem(lineId, absoluteQty)'));
    }
    return updateItem(lineId, Math.max(0, current + delta));
  }

  function init() {
    if (initialised) return refresh();
    initialised = true;

    if (forceLocal) {
      return localRefresh().catch(function (err) {
        log('local init failed', err);
        return getCart();
      });
    }

    var cached = readCache();
    if (cached) {
      // Paint from cache for perceived speed, explicitly marked not-loaded so
      // no consumer mistakes it for backend truth.
      model = Object.assign(emptyModel(), {
        quantity: cached.quantity || 0,
        subtotal: cached.subtotal || 0,
        items: Array.isArray(cached.items) ? cached.items : [],
        lineCount: Array.isArray(cached.items) ? cached.items.length : 0,
        loaded: false
      });
      emit();
    }
    return refresh().catch(function (err) {
      log('initial refresh failed', err);
      return getCart();
    });
  }

  var api = {
    // Backend interface
    getCart: getCart,
    refresh: refresh,
    add: add,
    updateItem: updateItem,
    setQuantity: updateItem,
    removeItem: removeItem,
    step: step,
    clear: clear,
    init: init,
    subscribe: subscribe,
    // Introspection
    get lastError() { return lastError; },
    get isLocal() { return forceLocal; },
    config: config,
    // Exposed for tests
    _parseCartHtml: parseCartHtml,
    _withQuantity: withQuantity,
    _preferLocalMode: preferLocalMode
  };

  window.PlasicoCartAdapter = api;

  // Merge onto the existing global so legacy call sites (addFromArticle, open,
  // openDrawer, close, isMobile) keep working; cart-drawer.js fills those in.
  window.__plasicoCart = Object.assign(window.__plasicoCart || {}, api);
})();
