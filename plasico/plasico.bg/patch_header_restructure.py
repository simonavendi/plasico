"""Patch hot-summer-sale-2026.html header: remove utility bar, unified menu panel."""

from __future__ import annotations

import re
from pathlib import Path

NEW_HEADER = '''  <header id="site-header" class="fixed top-0 w-full z-50 font-sans bg-surface/90 backdrop-blur-xl border-b border-edge-light shadow-[0_2px_0_0_rgba(255,255,255,0.06)_inset,0_8px_32px_rgba(0,0,0,0.35)]">
    <div>
      <div class="max-w-[1440px] mx-auto px-container-padding py-3">
        <div class="flex items-center gap-3 lg:gap-5">
          <button type="button" id="categories-toggle" class="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-full border border-edge-light bg-surface-container-high hover:bg-white/5 transition-colors" aria-expanded="false" aria-controls="categories-panel" title="Меню" aria-label="Меню">
            <span class="material-symbols-outlined text-on-surface text-[22px]">menu</span>
          </button>
          <a href="https://plasico.bg/" class="shrink-0 flex items-center">
            <img src="https://static.plasico.bg/css/campaign/hot-summer-sale-2026/logo-plasico.svg" alt="Plasico.bg — магазин за компютърна техника" class="h-9 sm:h-10 lg:h-11 w-auto"/>
          </a>
          <form action="https://plasico.bg/tyrsene" method="post" class="header-search-pill flex-1 min-w-0 max-w-2xl mx-auto hidden sm:flex items-center overflow-hidden pl-1 pr-1 py-1">
            <label for="header-search" class="sr-only">Търси продукт</label>
            <span class="material-symbols-outlined text-on-surface-variant text-[20px] pl-3 shrink-0 pointer-events-none" aria-hidden="true">search</span>
            <input type="text" id="header-search" name="search" value="" placeholder="Търси продукт..." autocomplete="off" class="flex-1 min-w-0 bg-transparent border-0 py-2 px-2 text-sm text-on-surface placeholder:text-on-surface-variant/70 focus:ring-0"/>
            <button type="submit" class="header-search-btn shrink-0 px-4 py-2 text-sm" aria-label="Търси">Търси</button>
          </form>
          <div class="flex items-center gap-0.5 sm:gap-1 lg:gap-2 ml-auto">
            <a href="#" class="header-utility-item hidden md:flex" title="Онлайн чат">
              <span class="material-symbols-outlined">chat</span>
              <span class="hidden lg:inline">Онлайн чат</span>
            </a>
            <a href="https://plasico.bg/любими" class="header-utility-item hidden sm:flex" title="Списък с любими" id="header-fav-link">
              <span class="relative inline-flex">
                <span class="material-symbols-outlined">favorite</span>
                <span class="header-fav-badge is-empty" id="header-fav-badge" aria-hidden="true">0</span>
              </span>
              <span class="hidden lg:inline">Любими</span>
            </a>
            <a href="tel:070020810" class="header-utility-item hidden md:flex" title="Обадете се на 0700 20 810">
              <span class="material-symbols-outlined">call</span>
              <span class="hidden lg:inline">0700 20 810</span>
            </a>
            <a href="https://plasico.bg/account" class="header-toolbar-signin" title="Вход">
              <span class="material-symbols-outlined" aria-hidden="true">login</span>
              <span class="hidden sm:inline">Вход</span>
            </a>
            <button type="button" id="header-cart-toggle" class="inline-flex items-center gap-2 rounded-full hover:bg-white/5 transition-colors p-2 lg:px-3 lg:py-2" title="Количка" aria-haspopup="dialog" aria-controls="cart-drawer" aria-expanded="false">
              <span class="relative inline-flex">
                <span class="material-symbols-outlined text-on-surface text-[24px]">shopping_cart</span>
                <span class="header-cart-badge is-empty" id="header-cart-badge" aria-hidden="true">0</span>
              </span>
              <span class="hidden lg:inline text-sm font-medium text-on-surface-variant">Количка</span>
            </button>
          </div>
        </div>
        <form action="https://plasico.bg/tyrsene" method="post" class="header-search-pill sm:hidden mt-3 flex items-center overflow-hidden pl-1 pr-1 py-1">
          <span class="material-symbols-outlined text-on-surface-variant text-[20px] pl-3 shrink-0 pointer-events-none" aria-hidden="true">search</span>
          <input type="text" name="search" placeholder="Търси продукт..." autocomplete="off" class="flex-1 min-w-0 bg-transparent border-0 py-2 px-2 text-sm text-on-surface placeholder:text-on-surface-variant/70 focus:ring-0"/>
          <button type="submit" class="header-search-btn shrink-0 px-3 py-2 text-sm" aria-label="Търси">Търси</button>
        </form>
      </div>
      <div id="categories-panel" class="border-t border-edge-light/30 bg-surface-container-low/90" aria-hidden="true">
        <div class="max-w-[1440px] mx-auto px-container-padding py-3 text-sm">
          <nav class="panel-utility-nav" aria-label="Бързи връзки">
            <div class="header-cat-mega-grid panel-utility-mega-grid">
              <div class="header-cat-mega-cell">
                <a href="https://plasico.bg/" class="header-cat-mega-parent header-utility-home" aria-label="Начало">
                  <span class="header-cat-mega-parent__icon" aria-hidden="true"><span class="material-symbols-outlined">home</span></span>
                  <span class="header-cat-mega-parent__label">Начало</span>
                </a>
              </div>
              <div class="header-cat-mega-cell">
                <a href="magazini.html" class="header-cat-mega-parent">
                  <span class="header-cat-mega-parent__icon" aria-hidden="true"><span class="material-symbols-outlined">storefront</span></span>
                  <span class="header-cat-mega-parent__label">Магазини</span>
                </a>
              </div>
              <div class="header-cat-mega-cell">
                <a href="serviz.html" class="header-cat-mega-parent">
                  <span class="header-cat-mega-parent__icon" aria-hidden="true"><span class="material-symbols-outlined">handyman</span></span>
                  <span class="header-cat-mega-parent__label">Сервиз</span>
                </a>
              </div>
              <div class="header-cat-mega-cell">
                <a href="za-nas.html" class="header-cat-mega-parent">
                  <span class="header-cat-mega-parent__icon" aria-hidden="true"><span class="material-symbols-outlined">groups</span></span>
                  <span class="header-cat-mega-parent__label">За нас</span>
                </a>
              </div>
              <div class="header-cat-mega-cell">
                <a href="blog/index.html" class="header-cat-mega-parent">
                  <span class="header-cat-mega-parent__icon" aria-hidden="true"><span class="material-symbols-outlined">newspaper</span></span>
                  <span class="header-cat-mega-parent__label">Блог</span>
                </a>
              </div>
              <div class="header-cat-mega-cell">
                <a href="kontakti.html" class="header-cat-mega-parent">
                  <span class="header-cat-mega-parent__icon" aria-hidden="true"><span class="material-symbols-outlined">mail</span></span>
                  <span class="header-cat-mega-parent__label">Контакти</span>
                </a>
              </div>
              <div class="header-cat-mega-cell panel-utility-mega-cell--sale is-active">
                <a href="hot-summer-sale-2026.html" class="header-cat-mega-parent panel-utility-mega-parent--sale" aria-label="Разпродажба Hot Summer Sale 2026" aria-current="page">
                  <span class="header-cat-mega-parent__icon" aria-hidden="true"><span class="material-symbols-outlined">local_fire_department</span></span>
                  <span class="header-cat-mega-parent__label">РАЗПРОДАЖБА</span>
                </a>
              </div>
            </div>
          </nav>
          <div id="site-categories-panel-mobile" class="mb-4"></div>
          <div id="campaign-categories-panel">
            <p class="header-cat-section-title">Hot Summer Sale 2026</p>
          </div>
        </div>
      </div>
    </div>
    <div id="categories-backdrop" class="header-cat-backdrop" aria-hidden="true"></div>
  </header>'''

PANEL_CSS = """
    .header-toolbar-signin {
      display: inline-flex;
      align-items: center;
      gap: 0.375rem;
      padding: 0.5rem 0.75rem;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 500;
      color: rgba(229, 225, 226, 0.85);
      text-decoration: none;
      transition: color 0.2s ease, background-color 0.2s ease;
    }
    .header-toolbar-signin:hover {
      color: #fff;
      background-color: rgba(255, 255, 255, 0.06);
    }
    .header-toolbar-signin .material-symbols-outlined {
      font-size: 20px;
    }
    .panel-utility-nav {
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .panel-utility-mega-grid {
      gap: 8px;
    }
    @media (min-width: 640px) {
      .panel-utility-mega-grid { gap: 10px; }
    }
    .panel-utility-nav .header-cat-mega-cell.is-active {
      border-color: rgba(251, 146, 60, 0.45);
      background: rgba(251, 146, 60, 0.08);
    }
    .panel-utility-nav .header-cat-mega-cell.is-active .header-cat-mega-parent {
      color: #FB923C;
    }
    .panel-utility-nav .header-cat-mega-cell.is-active .header-cat-mega-parent__icon {
      background: rgba(251, 146, 60, 0.14);
      color: #FB923C;
    }
    @media (max-width: 639px) {
      .panel-utility-mega-cell--sale {
        grid-column: span 2;
      }
    }
    .panel-utility-mega-cell--sale {
      border-color: rgba(255, 180, 120, 0.5);
      background: linear-gradient(135deg, #FB923C 0%, #F97316 50%, #EF4444 100%);
      box-shadow: 0 1px 8px rgba(251, 146, 60, 0.3);
    }
    .panel-utility-mega-cell--sale:hover {
      border-color: rgba(255, 200, 140, 0.7);
      filter: brightness(1.08);
      box-shadow: 0 2px 14px rgba(251, 146, 60, 0.45);
    }
    .panel-utility-mega-cell--sale.is-active {
      box-shadow: 0 0 0 2px rgba(251, 146, 60, 0.45), 0 1px 8px rgba(251, 146, 60, 0.35);
    }
    .panel-utility-mega-parent--sale {
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .panel-utility-mega-cell--sale .panel-utility-mega-parent--sale .header-cat-mega-parent__label {
      color: #FB923C;
    }
    .panel-utility-mega-cell--sale .panel-utility-mega-parent--sale:hover .header-cat-mega-parent__label {
      color: #F97316;
    }
    .panel-utility-mega-cell--sale .header-cat-mega-parent__icon {
      background: rgba(239, 68, 68, 0.18);
    }
    .panel-utility-mega-cell--sale .header-cat-mega-parent__icon .material-symbols-outlined {
      color: #EF4444;
      font-variation-settings: 'FILL' 1;
    }"""

INIT_HEADER_JS_NEW = r"""(function initHeaderCategories() {
      const toggle = document.getElementById('categories-toggle');
      const panel = document.getElementById('categories-panel');
      const backdrop = document.getElementById('categories-backdrop');
      const mapUrl = document.body?.dataset.categoryMap || 'category-map.json';

      function isOpen() { return panel?.classList.contains('is-open'); }
      function closeHeaderCategories() {
        panel?.classList.remove('is-open');
        panel?.setAttribute('aria-hidden', 'true');
        backdrop?.classList.remove('is-visible');
        backdrop?.setAttribute('aria-hidden', 'true');
        toggle?.setAttribute('aria-expanded', 'false');
        toggle?.classList.remove('is-open');
      }
      function openHeaderCategories() {
        panel?.classList.add('is-open');
        panel?.setAttribute('aria-hidden', 'false');
        backdrop?.classList.add('is-visible');
        backdrop?.setAttribute('aria-hidden', 'false');
        toggle?.setAttribute('aria-expanded', 'true');
        toggle?.classList.add('is-open');
      }

      toggle?.addEventListener('click', () => {
        if (isOpen()) closeHeaderCategories();
        else openHeaderCategories();
      });
      backdrop?.addEventListener('click', closeHeaderCategories);
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isOpen()) {
          closeHeaderCategories();
          toggle?.focus();
        }
      });
      document.addEventListener('click', (e) => {
        if (!isOpen()) return;
        const t = e.target;
        if (toggle?.contains(t) || panel?.contains(t)) return;
        closeHeaderCategories();
      });

      window.__closeHeaderCategories = closeHeaderCategories;
      window.__closeHeaderCategoriesPanel = closeHeaderCategories;

      function pagePrefix() {
        const idx = mapUrl.lastIndexOf('/');
        return idx >= 0 ? mapUrl.slice(0, idx + 1) : '';
      }
      function resolveNavUrl(item) {
        const prefix = pagePrefix();
        if (item.localUrl) return prefix + item.localUrl;
        if (item.url && !item.url.startsWith('https://plasico.bg') && !item.url.startsWith('http')) {
          return prefix + item.url.replace(/^\//, '');
        }
        return item.url || '#';
      }
      function navigateHeaderUrl(url, external) {
        if (!url || url === '#') return;
        closeHeaderCategories();
        if (external || url.startsWith('https://')) {
          window.open(url, external ? '_blank' : '_self', external ? 'noopener' : undefined);
          return;
        }
        if (url.startsWith('#')) {
          const target = document.querySelector(url.split('?')[0]);
          if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          else window.location.href = url;
          return;
        }
        window.location.href = url;
      }

      function buildMegaCell(category, options) {
        const subs = category.subcategories || [];
        const hasSubs = subs.length > 0;
        const cell = document.createElement('div');
        cell.className = 'header-cat-mega-cell';
        const dest = resolveNavUrl(category);
        const isExternal = category.external || (!category.localUrl && (dest.startsWith('https://')));
        const parent = hasSubs ? document.createElement('button') : document.createElement('a');
        parent.className = 'header-cat-mega-parent';
        parent.innerHTML = `
          <span class="header-cat-mega-parent__icon" aria-hidden="true">
            <span class="material-symbols-outlined">${category.materialIcon || 'category'}</span>
          </span>
          <span class="header-cat-mega-parent__label">${category.name}</span>
          ${hasSubs ? '<span class="material-symbols-outlined header-cat-mega-parent__chevron">expand_more</span>' : ''}
        `;
        if (!hasSubs) {
          parent.href = dest;
          if (isExternal) {
            parent.target = '_blank';
            parent.rel = 'noopener';
          }
          parent.addEventListener('click', (e) => {
            if (!isExternal) {
              e.preventDefault();
              navigateHeaderUrl(dest, false);
            } else {
              closeHeaderCategories();
            }
          });
        } else {
          parent.type = 'button';
          parent.addEventListener('click', () => {
            const wasOpen = cell.classList.contains('is-open');
            parent.closest('.header-cat-mega-grid, #site-categories-panel-mobile, #campaign-categories-panel')
              ?.querySelectorAll('.header-cat-mega-cell.is-open')
              .forEach(node => { if (node !== cell) node.classList.remove('is-open'); });
            cell.classList.toggle('is-open', !wasOpen);
            const chevron = parent.querySelector('.header-cat-mega-parent__chevron');
            if (chevron) chevron.textContent = cell.classList.contains('is-open') ? 'expand_less' : 'expand_more';
            if (typeof options.onParentClick === 'function') options.onParentClick(category, cell);
          });
        }
        cell.appendChild(parent);
        if (hasSubs) {
          const subsWrap = document.createElement('div');
          subsWrap.className = 'header-cat-mega-subs';
          subs.forEach(sub => {
            const subLink = document.createElement('button');
            subLink.type = 'button';
            subLink.className = 'header-cat-mega-sub';
            subLink.textContent = sub.name;
            subLink.addEventListener('click', () => {
              if (typeof options.onSubClick === 'function') {
                options.onSubClick(sub, category);
              } else {
                const subDest = sub.url && !sub.url.startsWith('https://plasico.bg') ? sub.url : (sub.url || dest);
                navigateHeaderUrl(subDest, sub.action === 'external' || subDest.startsWith('https://'));
              }
            });
            subsWrap.appendChild(subLink);
          });
          cell.appendChild(subsWrap);
        }
        return cell;
      }

      function renderSiteCategories(siteCategories) {
        const root = document.getElementById('site-categories-panel-mobile');
        if (!root) return;
        root.innerHTML = '<p class="header-cat-section-title">Категории</p>';
        const grid = document.createElement('div');
        grid.className = 'header-cat-mega-grid';
        (siteCategories || []).forEach(cat => grid.appendChild(buildMegaCell(cat, {})));
        root.appendChild(grid);
      }

      window.__renderHeaderSiteCategories = renderSiteCategories;
      window.__buildHeaderMegaCell = buildMegaCell;

      fetch(mapUrl)
        .then(res => (res.ok ? res.json() : null))
        .then(map => {
          if (map?.siteCategories) renderSiteCategories(map.siteCategories);
        })
        .catch(() => {});
    })();"""


def patch_template_header(template_path: Path) -> bool:
    html = template_path.read_text(encoding="utf-8")
    if 'class="header-cat-mega-grid panel-utility-mega-grid"' in html and "header-utility-bar border-b" not in html:
        return False

    html = re.sub(
        r":root \{\s*--site-header-offset: 8rem;\s*\}\s*"
        r"@media \(min-width: 640px\) and \(max-width: 1023px\) \{\s*:root \{ --site-header-offset: 4\.5rem; \}\s*\}\s*"
        r"@media \(min-width: 1024px\) \{\s*:root \{ --site-header-offset: [^;]+; \}\s*\}\s*"
        r"(?:@media \(max-width: 1023px\) \{\s*\.header-utility-bar \{ display: none; \}\s*\}\s*)?",
        ":root {\n      --site-header-offset: 8rem;\n    }\n"
        "    @media (min-width: 640px) and (max-width: 1023px) {\n"
        "      :root { --site-header-offset: 4.5rem; }\n"
        "    }\n"
        "    @media (min-width: 1024px) {\n"
        "      :root { --site-header-offset: 5rem; }\n"
        "    }\n",
        html,
        count=1,
    )

    html = re.sub(
        r"    \.header-utility-bar \{[\s\S]*?    \.header-utility-bar-inner \{[\s\S]*?color: rgba\(201, 197, 204, 0\.82\);\s*\}\s*",
        "",
        html,
        count=1,
    )

    if ".panel-utility-nav {" not in html:
        html = re.sub(
            r"    \.header-utility-bar-auth \{[\s\S]*?letter-spacing: -0\.005em;\s*\}\s*",
            PANEL_CSS + "\n",
            html,
            count=1,
        )

    html = re.sub(
        r"    \.mobile-utility-nav \{[\s\S]*?    \.mobile-utility-nav__item--signin:hover \{\s*color: #fff;\s*\}\s*",
        "",
        html,
        count=1,
    )

    html = re.sub(
        r"    #categories-panel\.is-open \{[\s\S]*?"
        r"#categories-toggle(?:-desktop)?\[aria-expanded=\"true\"\] \{[\s\S]*?background: rgba\(251, 146, 60, 0\.08\);\s*\}\s*",
        """    #categories-panel.is-open {
      max-height: min(75vh, 560px);
      opacity: 1;
      overflow-y: auto;
    }
    @media (min-width: 1024px) {
      #categories-panel.is-open {
        max-height: min(82vh, 780px);
      }
    }
    #categories-toggle.is-open,
    #categories-toggle[aria-expanded="true"] {
      border-color: rgba(251, 146, 60, 0.45);
      color: #FB923C;
      background: rgba(251, 146, 60, 0.08);
    }
""",
        html,
        count=1,
    )

    html = re.sub(
        r"    /\* Keep header chrome[\s\S]*?z-index: 50;\s*\}\s*",
        """    /* Keep header chrome and panel menu above the dimming backdrop (z-index 40). */
    #site-header > div:first-child {
      position: relative;
      z-index: 50;
    }
""",
        html,
        count=1,
    )

    html = re.sub(
        r'<header id="site-header"[\s\S]*?</header>',
        NEW_HEADER,
        html,
        count=1,
    )

    html = re.sub(
        r"\(function initHeaderCategories\(\) \{.*?\n    \}\)\(\);",
        INIT_HEADER_JS_NEW,
        html,
        count=1,
        flags=re.DOTALL,
    )

    template_path.write_text(html, encoding="utf-8")
    return True


def header_categories_script() -> str:
    return "\n    " + INIT_HEADER_JS_NEW + "\n"
