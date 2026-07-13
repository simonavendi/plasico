/**
 * Plasico Hot Summer Sale 2026 — shared catalog filter engine.
 * Main page: inline init passes productsMap via window.__productsMap
 * Category pages: set window.CATALOG_PAGE before loading this script.
 */
(function (global) {
  'use strict';

  const LAPTOP_FILTERS = new Set(['all', 'laptopi', 'gaming', 'business', 'ultrabook']);

  function parsePriceFromArticle(article) {
    const existing = article.dataset.price;
    if (existing) return parseFloat(existing);
    const priceEl = article.querySelector('.text-secondary.font-headline-md');
    if (!priceEl) return NaN;
    const match = priceEl.textContent.replace(/\s/g, '').match(/([\d.,]+)/);
    if (!match) return NaN;
    const value = parseFloat(match[1].replace(',', '.'));
    if (!Number.isNaN(value)) article.dataset.price = String(value);
    return value;
  }

  function formatPrice(value) {
    return `${value.toLocaleString('bg-BG', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} €`;
  }

  function matchesTags(tags, filterId, localFilters) {
    if (filterId === 'all') return true;
    if (localFilters.has('laptopi') && (filterId === 'laptopi')) return true;
    return tags.includes(filterId);
  }

  function initCategoryPage(config) {
    const productGrid = document.getElementById('product-grid');
    if (!productGrid) return;

    const sectionId = config.sectionId || 'catalog';
    const categoryId = config.categoryId;
    const subcategoryIds = config.subcategoryIds || [];
    const localFilters = new Set(['all', ...subcategoryIds]);

    const subtitle = document.getElementById('catalog-subtitle');
    const catalogTitle = document.getElementById('catalog-title');
    const emptyEl = document.getElementById('catalog-empty');
    const emptyTitle = document.getElementById('catalog-empty-title');
    const emptyText = document.getElementById('catalog-empty-text');
    const filterPanel = document.getElementById('catalog-filter-panel');
    const filterToggle = document.getElementById('filter-panel-toggle');
    const filterReset = document.getElementById('filter-reset');
    const priceMinInput = document.getElementById('price-min-input');
    const priceMaxInput = document.getElementById('price-max-input');
    const priceSliderMin = document.getElementById('price-slider-min');
    const priceSliderMax = document.getElementById('price-slider-max');
    const priceRangeFill = document.getElementById('price-range-fill');
    const priceRangeLabel = document.getElementById('price-range-label');
    const sortButtons = Array.from(document.querySelectorAll('#catalog-sort .filter-sort-btn'));
    const discountButtons = Array.from(document.querySelectorAll('#catalog-discount-filter .filter-sort-btn'));
    const upgradedFilterBtn = document.getElementById('filter-upgraded-only');
    const upgradedFilterCount = document.getElementById('upgraded-filter-count');
    const osFilterContainer = document.getElementById('catalog-os-filter');
    const subcategoryBar = document.getElementById('catalog-subcategory-filter');

    const products = Array.from(productGrid.querySelectorAll('article'));
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('opacity-100');
          entry.target.classList.remove('opacity-0', 'translate-y-10');
        }
      });
    }, { threshold: 0.1 });

    products.forEach((el, index) => {
      el.classList.add('catalog-product', 'transition-all', 'duration-700', 'opacity-0', 'translate-y-10');
      el.dataset.order = String(index);
      parsePriceFromArticle(el);
      observer.observe(el);
    });

    let activeFilter = 'all';
    let activeSort = 'default';
    let activeDiscountMin = 0;
    let activeUpgradedOnly = false;
    let activeOsFilter = 'all';
    let osFilterButtons = [];

    const prices = products.map(p => parseFloat(p.dataset.price)).filter(n => !Number.isNaN(n));
    const priceBounds = {
      min: Math.floor(Math.min(...prices, 0)),
      max: Math.ceil(Math.max(...prices, 1))
    };
    let priceRange = { ...priceBounds };

    const upgradedProductCount = products.filter(p => p.dataset.upgraded === 'true').length;
    if (upgradedFilterCount) upgradedFilterCount.textContent = `(${upgradedProductCount})`;

    function countForFilter(filterId) {
      if (filterId === 'all') return products.length;
      return products.filter(p => matchesTags((p.dataset.tags || '').split(/\s+/), filterId, localFilters)).length;
    }

    function countForOs(osId) {
      if (osId === 'all') return products.length;
      return products.filter(p => (p.dataset.os || 'unknown') === osId).length;
    }

    const OS_FILTER_OPTIONS = [
      { id: 'all', label: 'Всички' },
      { id: 'windows', label: 'Windows' },
      { id: 'macos', label: 'macOS' },
      { id: 'chromeos', label: 'Chrome OS' },
      { id: 'freedos', label: 'FreeDOS' },
      { id: 'linux', label: 'Linux' }
    ];

    function buildOsFilterPanel() {
      if (!osFilterContainer) return;
      osFilterContainer.innerHTML = '';
      osFilterButtons = [];
      const hasOs = products.some(p => p.dataset.os && p.dataset.os !== 'unknown');
      if (!hasOs) {
        osFilterContainer.closest('div')?.classList.add('hidden');
        return;
      }
      OS_FILTER_OPTIONS.forEach(opt => {
        const count = countForOs(opt.id);
        if (opt.id !== 'all' && count === 0) return;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'filter-sort-btn';
        btn.dataset.osFilter = opt.id;
        btn.setAttribute('aria-pressed', opt.id === activeOsFilter ? 'true' : 'false');
        btn.innerHTML = `${opt.label}<span class="filter-count">(${count})</span>`;
        btn.addEventListener('click', () => {
          activeOsFilter = opt.id;
          applyFilters();
        });
        osFilterContainer.appendChild(btn);
        osFilterButtons.push(btn);
      });
    }

    function buildSubcategoryBar() {
      if (!subcategoryBar || !config.subcategories) return;
      subcategoryBar.innerHTML = '';
      subcategoryBar.hidden = false;
      subcategoryBar.classList.add('is-visible');

      const label = document.createElement('span');
      label.className = 'catalog-subcategory-label';
      label.textContent = config.categoryName || '';
      subcategoryBar.appendChild(label);

      const allChip = document.createElement('button');
      allChip.type = 'button';
      allChip.className = 'category-subchip';
      allChip.dataset.filter = 'all';
      allChip.textContent = `Всички (${products.length})`;
      allChip.addEventListener('click', () => applyFilter('all', { scroll: true }));
      subcategoryBar.appendChild(allChip);

      config.subcategories.forEach(sub => {
        const id = sub.anchorId || sub.filterTag;
        if (!id) return;
        const count = countForFilter(id);
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'category-subchip';
        chip.dataset.filter = id;
        chip.textContent = `${sub.name} (${count})`;
        chip.addEventListener('click', () => applyFilter(id, { scroll: true }));
        subcategoryBar.appendChild(chip);
      });
    }

    function syncSubcategoryChips() {
      if (!subcategoryBar) return;
      subcategoryBar.querySelectorAll('.category-subchip').forEach(chip => {
        const match = chip.dataset.filter === activeFilter;
        chip.classList.toggle('is-active', match);
      });
    }

    function syncPriceInputs() {
      if (!priceMinInput || !priceMaxInput) return;
      [priceMinInput, priceMaxInput, priceSliderMin, priceSliderMax].forEach(el => {
        if (!el) return;
        el.min = priceBounds.min;
        el.max = priceBounds.max;
      });
      priceMinInput.value = priceRange.min;
      priceMaxInput.value = priceRange.max;
      if (priceSliderMin) priceSliderMin.value = priceRange.min;
      if (priceSliderMax) priceSliderMax.value = priceRange.max;
      if (priceRangeFill) {
        const span = priceBounds.max - priceBounds.min || 1;
        const left = ((priceRange.min - priceBounds.min) / span) * 100;
        const right = ((priceRange.max - priceBounds.min) / span) * 100;
        priceRangeFill.style.left = `${left}%`;
        priceRangeFill.style.width = `${Math.max(0, right - left)}%`;
      }
      if (priceRangeLabel) {
        priceRangeLabel.textContent = `Диапазон: ${formatPrice(priceRange.min)} – ${formatPrice(priceRange.max)}`;
      }
    }

    function clampPriceRange() {
      let min = Number(priceMinInput?.value);
      let max = Number(priceMaxInput?.value);
      if (Number.isNaN(min)) min = priceRange.min;
      if (Number.isNaN(max)) max = priceRange.max;
      min = Math.max(priceBounds.min, Math.min(min, priceBounds.max));
      max = Math.max(priceBounds.min, Math.min(max, priceBounds.max));
      if (min > max) [min, max] = [max, min];
      priceRange = { min, max };
      syncPriceInputs();
    }

    function setProductVisibility(product, show) {
      if (show) {
        product.classList.remove('is-filtered-out', 'opacity-0', 'translate-y-10');
        product.classList.add('opacity-100');
      } else {
        product.classList.add('is-filtered-out');
      }
    }

    function hasActiveConstraints() {
      return activeFilter !== 'all' ||
        activeDiscountMin > 0 ||
        activeUpgradedOnly ||
        activeOsFilter !== 'all' ||
        priceRange.min > priceBounds.min ||
        priceRange.max < priceBounds.max ||
        activeSort !== 'default';
    }

    function updateResetButton() {
      if (filterReset) filterReset.classList.toggle('hidden', !hasActiveConstraints());
    }

    function parseFilterFromHash() {
      const hash = window.location.hash.replace(/^#/, '');
      if (!hash) return 'all';
      if (localFilters.has(hash)) return hash;
      return 'all';
    }

    function updateHash(filterId) {
      const base = filterId === 'all' ? `#${sectionId}` : `#${filterId}`;
      if (window.location.hash !== base) {
        history.replaceState(null, '', base);
      }
    }

    function applyFilters(options = {}) {
      const { scroll = false, updateHash = true } = options;
      const visible = [];
      const hidden = [];

      products.forEach(product => {
        const tags = (product.dataset.tags || categoryId).split(/\s+/);
        const price = parseFloat(product.dataset.price);
        const pct = parseInt(product.dataset.discountPercent || '0', 10);
        const show =
          matchesTags(tags, activeFilter, localFilters) &&
          (Number.isNaN(price) || (price >= priceRange.min && price <= priceRange.max)) &&
          (activeDiscountMin <= 0 || pct >= activeDiscountMin) &&
          (!activeUpgradedOnly || product.dataset.upgraded === 'true') &&
          (activeOsFilter === 'all' || (product.dataset.os || 'unknown') === activeOsFilter);

        if (show) visible.push(product);
        else hidden.push(product);
      });

      if (activeSort === 'price-asc') {
        visible.sort((a, b) => (parseFloat(a.dataset.price) || 0) - (parseFloat(b.dataset.price) || 0));
      } else if (activeSort === 'price-desc') {
        visible.sort((a, b) => (parseFloat(b.dataset.price) || 0) - (parseFloat(a.dataset.price) || 0));
      } else {
        visible.sort((a, b) => Number(a.dataset.order) - Number(b.dataset.order));
      }

      [...visible, ...hidden].forEach(p => productGrid.appendChild(p));
      visible.forEach(p => setProductVisibility(p, true));
      hidden.forEach(p => setProductVisibility(p, false));

      if (subtitle) {
        const word = visible.length === 1 ? 'продукт' : 'продукта';
        subtitle.textContent = hasActiveConstraints()
          ? `${visible.length} ${word}`
          : `${visible.length} ${word} с летни отстъпки — налични за поръчка.`;
      }

      if (visible.length === 0 && emptyEl) {
        if (emptyTitle) emptyTitle.textContent = 'Няма продукти по избраните филтри';
        if (emptyText) emptyText.textContent = 'Опитайте да разширите филтрите или изберете друга подкатегория.';
        emptyEl.classList.remove('hidden');
        requestAnimationFrame(() => emptyEl.classList.add('is-visible'));
        productGrid.classList.add('hidden');
      } else if (emptyEl) {
        emptyEl.classList.remove('is-visible');
        emptyEl.classList.add('hidden');
        productGrid.classList.remove('hidden');
      }

      discountButtons.forEach(btn => {
        btn.setAttribute('aria-pressed', Number(btn.dataset.discountMin) === activeDiscountMin ? 'true' : 'false');
      });
      sortButtons.forEach(btn => {
        btn.setAttribute('aria-pressed', btn.dataset.sort === activeSort ? 'true' : 'false');
      });
      if (upgradedFilterBtn) {
        upgradedFilterBtn.setAttribute('aria-pressed', activeUpgradedOnly ? 'true' : 'false');
      }
      osFilterButtons.forEach(btn => {
        btn.setAttribute('aria-pressed', btn.dataset.osFilter === activeOsFilter ? 'true' : 'false');
      });
      syncSubcategoryChips();
      updateResetButton();
      if (updateHash) updateHash(activeFilter);
      if (scroll) {
        const target = document.getElementById(sectionId) || document.getElementById(activeFilter);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function applyFilter(filterId, options = {}) {
      activeFilter = filterId;
      applyFilters(options);
    }

    function resetFilters(options = {}) {
      activeFilter = 'all';
      activeSort = 'default';
      activeDiscountMin = 0;
      activeUpgradedOnly = false;
      activeOsFilter = 'all';
      priceRange = { ...priceBounds };
      syncPriceInputs();
      applyFilters(options);
    }

    buildSubcategoryBar();
    buildOsFilterPanel();
    syncPriceInputs();

    if (filterToggle && filterPanel) {
      filterToggle.addEventListener('click', () => {
        const open = filterPanel.classList.toggle('is-open');
        filterToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        filterPanel.setAttribute('aria-hidden', open ? 'false' : 'true');
      });
    }
    if (filterReset) filterReset.addEventListener('click', () => resetFilters({ scroll: false }));

    const onPriceChange = () => { clampPriceRange(); applyFilters(); };
    priceMinInput?.addEventListener('change', onPriceChange);
    priceMaxInput?.addEventListener('change', onPriceChange);
    priceSliderMin?.addEventListener('input', () => {
      priceRange.min = Number(priceSliderMin.value);
      if (priceRange.min > priceRange.max) priceRange.max = priceRange.min;
      syncPriceInputs();
      applyFilters();
    });
    priceSliderMax?.addEventListener('input', () => {
      priceRange.max = Number(priceSliderMax.value);
      if (priceRange.max < priceRange.min) priceRange.min = priceRange.max;
      syncPriceInputs();
      applyFilters();
    });

    sortButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        activeSort = btn.dataset.sort;
        applyFilters();
      });
    });
    discountButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        activeDiscountMin = Number(btn.dataset.discountMin) || 0;
        applyFilters();
      });
    });
    if (upgradedFilterBtn) {
      upgradedFilterBtn.addEventListener('click', () => {
        activeUpgradedOnly = !activeUpgradedOnly;
        applyFilters();
      });
    }

    window.addEventListener('hashchange', () => {
      activeFilter = parseFilterFromHash();
      applyFilters({ scroll: true, updateHash: false });
    });

    activeFilter = parseFilterFromHash();
    applyFilters({ scroll: false, updateHash: false });

    if (activeFilter !== 'all') {
      setTimeout(() => {
        const anchor = document.getElementById(activeFilter);
        if (anchor) anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }

  global.PlasicoCatalog = { initCategoryPage, LAPTOP_FILTERS };

  if (global.CATALOG_PAGE && global.CATALOG_PAGE.mode === 'category') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => initCategoryPage(global.CATALOG_PAGE));
    } else {
      initCategoryPage(global.CATALOG_PAGE);
    }
  }
})(typeof window !== 'undefined' ? window : globalThis);
