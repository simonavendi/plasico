/**
 * Hot Summer Sale 2026 — category icon grid + mobile picker navigation.
 * Used on campaign subpages; main page keeps inline equivalent.
 */
(function (global) {
  'use strict';

  const LOCAL_LAPTOP_FILTERS = [
    { name: 'Гейминг', filterTag: 'gaming' },
    { name: 'Бизнес', filterTag: 'business' },
    { name: 'Ултрапортативни', filterTag: 'ultrabook' }
  ];
  const LAPTOP_FILTER_IDS = new Set(['all', 'laptopi', 'gaming', 'business', 'ultrabook']);

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('opacity-100');
        entry.target.classList.remove('opacity-0', 'translate-y-10');
      }
    });
  }, { threshold: 0.1 });

  function mapPrefix() {
    const mapUrl = document.body?.dataset.categoryMap || 'category-map.json';
    const idx = mapUrl.lastIndexOf('/');
    return idx >= 0 ? mapUrl.slice(0, idx + 1) : '';
  }

  function resolveLocalUrl(localUrl) {
    if (!localUrl) return null;
    if (localUrl.startsWith('http') || localUrl.startsWith('#')) return localUrl;
    return mapPrefix() + localUrl;
  }

  function loadCategoryMap() {
    const mapUrl = document.body?.dataset.categoryMap || 'category-map.json';
    return fetch(mapUrl).then((res) => {
      if (!res.ok) throw new Error('category-map.json not found');
      return res.json();
    });
  }

  function getCategorySubs(category) {
    const subs = [...(category.subcategories || [])];
    const isMainLaptopCatalog = category.id === 'laptopi' || LAPTOP_FILTER_IDS.has(category.dataFilter);
    if (isMainLaptopCatalog) {
      if (!subs.some((s) => s.filterTag === 'all')) {
        subs.unshift({
          name: 'Всички',
          action: 'filter',
          filterTag: 'all',
          url: '#laptopi'
        });
      }
      LOCAL_LAPTOP_FILTERS.forEach((extra) => {
        if (!subs.some((s) => s.filterTag === extra.filterTag)) {
          subs.push({
            name: extra.name,
            action: 'filter',
            filterTag: extra.filterTag,
            url: `#laptopi?filter=${extra.filterTag}`
          });
        }
      });
    }
    return subs;
  }

  function getMobileCategoryPickerEls() {
    return {
      picker: document.getElementById('category-mobile-picker'),
      toggle: document.getElementById('category-mobile-toggle'),
      list: document.getElementById('category-mobile-list'),
      label: document.getElementById('category-mobile-label')
    };
  }

  function closeMobileCategoryPicker() {
    const { toggle, list } = getMobileCategoryPickerEls();
    if (!toggle || !list) return;
    toggle.setAttribute('aria-expanded', 'false');
    list.hidden = true;
  }

  function openMobileCategoryPicker() {
    const { toggle, list } = getMobileCategoryPickerEls();
    if (!toggle || !list) return;
    toggle.setAttribute('aria-expanded', 'true');
    list.hidden = false;
    const active = list.querySelector('.category-mobile-option.is-active, .category-mobile-option[aria-selected="true"]');
    const first = list.querySelector('.category-mobile-option');
    (active || first)?.focus();
  }

  function syncMobileCategoryPickerUI(categoryId) {
    const { list, label } = getMobileCategoryPickerEls();
    if (!list) return;
    list.querySelectorAll('.category-mobile-option').forEach((option) => {
      const isActive = option.dataset.categoryId === categoryId;
      option.classList.toggle('is-active', isActive);
      option.setAttribute('aria-selected', isActive ? 'true' : 'false');
      if (isActive && label) label.textContent = option.dataset.categoryName || option.textContent.trim();
    });
  }

  function syncCategoryExpansionUI(categoryId) {
    const grid = document.getElementById('category-icon-grid');
    if (grid) {
      grid.querySelectorAll('.category-icon-cell').forEach((cell) => {
        cell.classList.toggle('is-expanded', cell.dataset.categoryId === categoryId);
      });
    }
    syncMobileCategoryPickerUI(categoryId);
  }

  function navigateCategoryUrl(url) {
    if (!url) return;
    const dest = url.startsWith('http') || url.startsWith('#') ? url : resolveLocalUrl(url);
    if (!dest) return;
    if (dest.startsWith('#')) {
      const target = document.querySelector(dest.split('?')[0]);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      else window.location.href = dest;
      return;
    }
    window.location.href = dest;
  }

  function resolveSubcategoryNavigateUrl(sub, category) {
    if (sub.url && !sub.url.startsWith('https://plasico.bg') && !sub.url.startsWith('#')) {
      return resolveLocalUrl(sub.url);
    }
    if (category.localUrl) {
      const base = resolveLocalUrl(category.localUrl.split('#')[0]);
      if (sub.anchorId) return `${base}#${sub.anchorId}`;
      return resolveLocalUrl(category.localUrl);
    }
    if (sub.url && sub.url.startsWith('#')) return sub.url;
    return null;
  }

  function handleSubcategoryAction(sub, category) {
    if (sub.action === 'local' || category.localUrl) {
      const dest = resolveSubcategoryNavigateUrl(sub, category);
      if (dest && !dest.startsWith('https://')) {
        navigateCategoryUrl(dest);
        return;
      }
    }
    if (sub.action === 'external' || (category.external && !category.localUrl)) {
      if (sub.url) window.open(sub.url, '_blank', 'noopener');
      return;
    }
    if (sub.anchor) {
      const target = document.querySelector(sub.anchor);
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function handleCategorySelect(category) {
    const localUrl = category.localUrl || null;
    const currentCategoryId = global.CATALOG_PAGE?.categoryId;
    const isSubpage = global.CATALOG_PAGE?.mode === 'category';

    if (localUrl && category.external === false && !LAPTOP_FILTER_IDS.has(category.dataFilter)) {
      if (isSubpage && category.id === currentCategoryId) {
        const catalog = document.getElementById('catalog');
        if (catalog) catalog.scrollIntoView({ behavior: 'smooth', block: 'start' });
        syncCategoryExpansionUI(category.id);
        return;
      }
      navigateCategoryUrl(localUrl);
      return;
    }

    if (localUrl && LAPTOP_FILTER_IDS.has(category.dataFilter)) {
      navigateCategoryUrl(localUrl);
      return;
    }

    syncCategoryExpansionUI(category.id);
  }

  function initMobileCategoryPicker(categoryMap) {
    const { picker, toggle, list } = getMobileCategoryPickerEls();
    if (!picker || !toggle || !list || !categoryMap?.categories) return;

    list.innerHTML = '';
    categoryMap.categories.forEach((category) => {
      const item = document.createElement('li');
      item.setAttribute('role', 'presentation');
      const option = document.createElement('button');
      option.type = 'button';
      option.className = 'category-mobile-option';
      option.id = `category-mobile-option-${category.id}`;
      option.setAttribute('role', 'option');
      option.dataset.categoryId = category.id;
      option.dataset.categoryName = category.name;
      option.setAttribute('aria-selected', 'false');
      option.innerHTML = `
        <span class="category-mobile-option__icon" aria-hidden="true">
          <span class="material-symbols-outlined">${category.materialIcon}</span>
        </span>
        <span class="category-mobile-option__label">${category.name}</span>
      `;
      option.addEventListener('click', () => {
        handleCategorySelect(category);
        closeMobileCategoryPicker();
      });
      item.appendChild(option);
      list.appendChild(item);
    });

    if (toggle.dataset.bound === 'true') return;
    toggle.dataset.bound = 'true';

    toggle.addEventListener('click', () => {
      const isOpen = toggle.getAttribute('aria-expanded') === 'true';
      if (isOpen) closeMobileCategoryPicker();
      else openMobileCategoryPicker();
    });

    list.addEventListener('keydown', (e) => {
      const options = [...list.querySelectorAll('.category-mobile-option')];
      const idx = options.indexOf(document.activeElement);
      if (e.key === 'Escape') {
        e.preventDefault();
        closeMobileCategoryPicker();
        toggle.focus();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        (options[Math.min(idx + 1, options.length - 1)] || options[0])?.focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        (options[Math.max(idx - 1, 0)] || options[options.length - 1])?.focus();
      }
    });

    document.addEventListener('click', (e) => {
      if (!picker.contains(e.target)) closeMobileCategoryPicker();
    });
  }

  function renderCampaignCategoriesPanel(categoryMap) {
    const panel = document.getElementById('campaign-categories-panel');
    const buildCell = global.__buildHeaderMegaCell;
    if (!panel || !buildCell || !categoryMap?.categories) return;

    panel.innerHTML = '';
    const sectionTitle = document.createElement('p');
    sectionTitle.className = 'header-cat-section-title';
    sectionTitle.textContent = 'ПРОДУКТОВИ КАТЕГОРИИ';
    panel.appendChild(sectionTitle);
    categoryMap.categories.forEach((category) => {
      panel.appendChild(buildCell(category, {
        onSubClick(sub, category) {
          handleSubcategoryAction(sub, category);
          if (global.__closeHeaderCategoriesPanel) global.__closeHeaderCategoriesPanel();
        }
      }));
    });
  }

  function renderCategoryNavigation(categoryMap) {
    const grid = document.getElementById('category-icon-grid');
    if (!grid || !categoryMap?.categories) return;

    grid.innerHTML = '';
    categoryMap.categories.forEach((category) => {
      const cell = document.createElement('div');
      cell.className = 'category-icon-cell';
      cell.dataset.categoryId = category.id;

      const localUrl = category.localUrl || null;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'category-filter-trigger category-icon-card';
      btn.dataset.filter = category.dataFilter;
      if (localUrl) btn.dataset.localUrl = localUrl;
      btn.innerHTML = `
        <span class="category-icon-card__icon"><span class="material-symbols-outlined">${category.materialIcon}</span></span>
        <span class="category-icon-card__label">${category.name}</span>
      `;
      cell.appendChild(btn);
      grid.appendChild(cell);

      btn.classList.add('transition-all', 'duration-700', 'opacity-0', 'translate-y-10');
      observer.observe(btn);
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        handleCategorySelect(category);
      });
    });

    initMobileCategoryPicker(categoryMap);
  }

  function initSubpageCategoryNav() {
    if (global.CATALOG_PAGE?.mode !== 'category') return;
    const activeId = global.CATALOG_PAGE.categoryId;

    loadCategoryMap()
      .then((map) => {
        renderCategoryNavigation(map);
        renderCampaignCategoriesPanel(map);
        if (activeId) syncCategoryExpansionUI(activeId);
      })
      .catch((err) => console.warn('Category nav init failed', err));
  }

  global.PlasicoCampaignNav = {
    renderCategoryNavigation,
    handleCategorySelect,
    handleSubcategoryAction,
    syncCategoryExpansionUI
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSubpageCategoryNav);
  } else {
    initSubpageCategoryNav();
  }
})(typeof window !== 'undefined' ? window : globalThis);
