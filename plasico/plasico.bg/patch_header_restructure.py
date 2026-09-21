"""Patch hot-summer-sale-2026.html header to Megamag-inspired layout."""

from __future__ import annotations

import re
from pathlib import Path

NEW_HEADER = '''  <header id="site-header" class="mm-header font-sans">
    <div class="mm-header-shell">
      <div class="mm-header-main mm-wrap">
        <button type="button" class="mm-mobile-menu-btn" data-mobile-menu-toggle aria-label="Отвори меню" aria-expanded="false" aria-controls="mm-mobile-menu">
          <span class="material-symbols-outlined" aria-hidden="true">menu</span>
        </button>
        <a href="https://plasico.bg/" class="mm-logo" title="Начало" aria-label="Начало">
          <img src="logo-plasico.svg" alt="Plasico.bg — магазин за компютърна техника" class="site-header-logo"/>
        </a>
        <form action="https://plasico.bg/tyrsene" method="post" class="mm-search" role="search">
          <label for="header-search" class="sr-only">Търси продукт</label>
          <select name="category" aria-label="Категория">
            <option value="">Всички категории</option>
            <option value="laptopi">Лаптопи и аксесоари</option>
            <option value="komponenti">Компоненти</option>
            <option value="monitori">Монитори и проектори</option>
            <option value="kompyutri">Компютри и сървъри</option>
            <option value="smartfoni">Смартфони и таблети</option>
            <option value="aksesoari">Аксесоари</option>
            <option value="mrezha">Мрежово оборудване</option>
            <option value="ofis">Офис</option>
          </select>
          <input type="text" id="header-search" name="search" value="" placeholder="Търси марка, модел, артикул…" autocomplete="off"/>
          <button type="submit" aria-label="Търси">
            <span class="material-symbols-outlined" aria-hidden="true" style="font-size:16px">search</span>
            <span class="search-button-text">Търси</span>
          </button>
        </form>
        <a href="tel:070020810" class="mm-contact" title="Обадете се на 0700 20 810">
          <span class="mm-contact__icon" aria-hidden="true"><span class="material-symbols-outlined">call</span></span>
          <span class="mm-contact__text">
            <small>Онлайн съпорт</small>
            <b>0700 20 810</b>
          </span>
        </a>
        <div class="mm-header-icons">
          <a href="#compare" class="mm-iconbtn" id="header-compare-link" aria-label="Сравни" title="Сравни">
            <span class="material-symbols-outlined" aria-hidden="true">compare_arrows</span>
            <span class="header-compare-badge badge is-empty" id="header-compare-badge" aria-hidden="true">0</span>
          </a>
          <a href="lyubimi.html" class="mm-iconbtn" id="header-fav-link" aria-label="Любими" title="Списък с любими">
            <span class="material-symbols-outlined" aria-hidden="true">favorite</span>
            <span class="header-fav-badge badge is-empty" id="header-fav-badge" aria-hidden="true">0</span>
          </a>
          <button type="button" class="mm-iconbtn mm-search-toggle" data-search-toggle aria-label="Търсене" aria-expanded="false">
            <span class="material-symbols-outlined" aria-hidden="true">search</span>
          </button>
          <a href="#" class="mm-iconbtn" aria-label="Вход" title="Вход" data-open-auth-modal>
            <span class="material-symbols-outlined" aria-hidden="true">person</span>
          </a>
        </div>
        <button type="button" id="header-cart-toggle" class="mm-header-cta" title="Количка" aria-label="Количка" aria-haspopup="dialog" aria-controls="cart-drawer" aria-expanded="false">
          <span class="mm-iconbtn" aria-hidden="true">
            <span class="material-symbols-outlined">shopping_cart</span>
            <span class="header-cart-badge badge is-empty" id="header-cart-badge">0</span>
          </span>
          <span class="mm-header-cta__text">
            <small>Количка</small>
            <b id="header-cart-total">0,00 €</b>
          </span>
        </button>
      </div>
      <div class="mm-subnav">
        <div class="mm-wrap">
          <button type="button" id="categories-toggle" class="mm-cat-btn" aria-expanded="false" aria-controls="categories-panel" title="Категории">
            <span class="bars" aria-hidden="true"><i></i><i></i><i></i></span>
            Категории
          </button>
          <nav class="mm-subnav-nav" aria-label="Бързи връзки">
            <a href="promotsii.html" class="hot">% Промоции</a>
            <a href="hot-summer-sale-2026.html">Разпродажба</a>
            <a href="game-zone.html">Гейминг</a>
            <a href="laptopi-i-aksesoari.html">Лаптопи</a>
          </nav>
          <div class="mm-subnav-right">
            <a href="kontakti.html"><span class="material-symbols-outlined" aria-hidden="true">mail</span>Контакти</a>
            <a href="magazini.html"><span class="material-symbols-outlined" aria-hidden="true">storefront</span>Магазини</a>
            <a href="serviz.html"><span class="material-symbols-outlined" aria-hidden="true">handyman</span>Сервиз</a>
          </div>
        </div>
      </div>
      <div id="categories-panel" aria-hidden="true">
        <div class="mm-wrap py-3 text-sm">
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
        </div>
      </div>
      <div id="mm-mobile-menu" class="mm-mobile-nav-panel" data-mobile-menu hidden>
        <div class="mm-wrap">
          <button type="button" class="mm-cat-btn mm-mobile-cat-btn" data-open-categories aria-controls="categories-panel">
            <span class="bars" aria-hidden="true"><i></i><i></i><i></i></span>
            Категории
          </button>
          <div class="mm-mobile-nav-section">
            <span class="mm-mobile-nav-title">Меню</span>
            <a href="promotsii.html" class="hot">% Промоции</a>
            <a href="hot-summer-sale-2026.html">Разпродажба</a>
            <a href="game-zone.html">Гейминг</a>
            <a href="laptopi-i-aksesoari.html">Лаптопи</a>
            <a href="lyubimi.html">Любими</a>
            <a href="#" data-open-auth-modal>Вход</a>
          </div>
          <div class="mm-mobile-nav-section">
            <span class="mm-mobile-nav-title">Полезни връзки</span>
            <a href="kontakti.html"><span class="material-symbols-outlined" aria-hidden="true">mail</span>Контакти</a>
            <a href="magazini.html"><span class="material-symbols-outlined" aria-hidden="true">storefront</span>Магазини</a>
            <a href="serviz.html"><span class="material-symbols-outlined" aria-hidden="true">handyman</span>Сервиз</a>
            <a href="za-nas.html"><span class="material-symbols-outlined" aria-hidden="true">groups</span>За нас</a>
            <a href="tel:070020810"><span class="material-symbols-outlined" aria-hidden="true">call</span>0700 20 810</a>
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
      border-color: rgba(7, 168, 87, 0.45);
      background: rgba(7, 168, 87, 0.08);
    }
    .panel-utility-nav .header-cat-mega-cell.is-active .header-cat-mega-parent {
      color: #07a857;
    }
    .panel-utility-nav .header-cat-mega-cell.is-active .header-cat-mega-parent__icon {
      background: rgba(7, 168, 87, 0.14);
      color: #07a857;
    }
    @media (max-width: 639px) {
      .panel-utility-mega-cell--sale {
        grid-column: span 2;
      }
    }
    .panel-utility-mega-cell--sale {
      border-color: rgba(7, 168, 87, 0.5);
      background: linear-gradient(135deg, #07a857 0%, #058a47 55%, #046b38 100%);
      box-shadow: 0 1px 8px rgba(7, 168, 87, 0.3);
    }
    .panel-utility-mega-cell--sale:hover {
      border-color: rgba(7, 168, 87, 0.7);
      filter: brightness(1.06);
      box-shadow: 0 2px 14px rgba(7, 168, 87, 0.4);
    }
    .panel-utility-mega-cell--sale.is-active {
      box-shadow: 0 0 0 2px rgba(7, 168, 87, 0.45), 0 1px 8px rgba(7, 168, 87, 0.35);
    }
    .panel-utility-mega-parent--sale {
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    .panel-utility-mega-cell--sale .panel-utility-mega-parent--sale .header-cat-mega-parent__label {
      color: #fff;
    }
    .panel-utility-mega-cell--sale .header-cat-mega-parent__icon {
      background: rgba(255, 255, 255, 0.18);
    }
    .panel-utility-mega-cell--sale .header-cat-mega-parent__icon .material-symbols-outlined {
      color: #fff;
      font-variation-settings: 'FILL' 1;
    }"""

INIT_HEADER_JS_NEW = r"""(function initHeaderCategories() {
      const header = document.getElementById('site-header');
      const toggle = document.getElementById('categories-toggle');
      const panel = document.getElementById('categories-panel');
      const backdrop = document.getElementById('categories-backdrop');
      const mapUrl = document.body?.dataset.categoryMap || 'category-map.json';
      const searchToggle = header?.querySelector('[data-search-toggle]');
      const mobileMenuToggle = header?.querySelector('[data-mobile-menu-toggle]');
      const mobileMenu = header?.querySelector('[data-mobile-menu]');
      const searchInput = document.getElementById('header-search');

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
        closeMobileMenu();
        panel?.classList.add('is-open');
        panel?.setAttribute('aria-hidden', 'false');
        backdrop?.classList.add('is-visible');
        backdrop?.setAttribute('aria-hidden', 'false');
        toggle?.setAttribute('aria-expanded', 'true');
        toggle?.classList.add('is-open');
      }

      function closeMobileMenu() {
        mobileMenu?.classList.remove('is-open');
        mobileMenu?.setAttribute('hidden', '');
        mobileMenuToggle?.setAttribute('aria-expanded', 'false');
      }
      function openMobileMenu() {
        closeHeaderCategories();
        mobileMenu?.classList.add('is-open');
        mobileMenu?.removeAttribute('hidden');
        mobileMenuToggle?.setAttribute('aria-expanded', 'true');
      }

      toggle?.addEventListener('click', () => {
        if (isOpen()) closeHeaderCategories();
        else openHeaderCategories();
      });
      backdrop?.addEventListener('click', () => {
        closeHeaderCategories();
        closeMobileMenu();
      });
      mobileMenuToggle?.addEventListener('click', () => {
        if (mobileMenu?.classList.contains('is-open')) closeMobileMenu();
        else openMobileMenu();
      });
      searchToggle?.addEventListener('click', () => {
        const open = header?.classList.toggle('search-open');
        searchToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        if (open) searchInput?.focus();
      });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          if (isOpen()) {
            closeHeaderCategories();
            toggle?.focus();
          }
          closeMobileMenu();
          header?.classList.remove('search-open');
          searchToggle?.setAttribute('aria-expanded', 'false');
        }
      });
      document.addEventListener('click', (e) => {
        if (!isOpen()) return;
        const t = e.target;
        if (toggle?.contains(t) || panel?.contains(t)) return;
        closeHeaderCategories();
      });

      const compareLink = document.getElementById('header-compare-link');
      compareLink?.addEventListener('click', (e) => {
        const bar = document.getElementById('plasico-compare-bar');
        if (bar && !bar.hasAttribute('hidden')) {
          e.preventDefault();
          bar.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
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
          parent.setAttribute('aria-expanded', 'false');
          parent.addEventListener('click', () => {
            const open = cell.classList.toggle('is-expanded');
            parent.setAttribute('aria-expanded', open ? 'true' : 'false');
          });
        }
        cell.appendChild(parent);
        if (hasSubs) {
          const sub = document.createElement('div');
          sub.className = 'header-cat-mega-subs';
          subs.forEach((s) => {
            const a = document.createElement('a');
            a.className = 'header-cat-mega-sub';
            a.textContent = s.name;
            const subDest = resolveNavUrl(s);
            a.href = subDest;
            if (s.action === 'external' || (!s.localUrl && subDest.startsWith('https://'))) {
              a.target = '_blank';
              a.rel = 'noopener';
            }
            a.addEventListener('click', (e) => {
              if (a.target !== '_blank') {
                e.preventDefault();
                navigateHeaderUrl(subDest, false);
              } else {
                closeHeaderCategories();
              }
            });
            sub.appendChild(a);
          });
          cell.appendChild(sub);
        }
        return cell;
      }

      function renderSiteCategories(siteCategories) {
        const root = document.getElementById('site-categories-panel-mobile');
        if (!root) return;
        root.innerHTML = '';
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

    html = re.sub(
        r'<header id="site-header"[\s\S]*?</header>',
        NEW_HEADER,
        html,
        count=1,
    )

    if 'megamag-header.css' not in html:
        html = html.replace(
            '<link rel="stylesheet" href="theme-overrides.css"/>',
            '<link rel="stylesheet" href="theme-overrides.css"/>\n  <link rel="stylesheet" href="megamag-header.css"/>',
            1,
        )

    if 'header-megamag.js' not in html:
        if 'cart-drawer.js' in html:
            html = html.replace(
                '<script src="cart-drawer.js"></script>',
                '<script src="cart-drawer.js"></script>\n<script src="header-megamag.js"></script>',
                1,
            )
        else:
            html = html.replace(
                '</body>',
                '<script src="header-megamag.js"></script>\n</body>',
                1,
            )

    # Sticky Megamag header — content flows after it (no fixed offset padding).
    html = re.sub(
        r":root \{\s*--site-header-offset:[^}]+\}\s*"
        r"(?:@media \(min-width: 640px\) and \(max-width: 1023px\) \{\s*:root \{ --site-header-offset: [^;]+; \}\s*\}\s*)?"
        r"(?:@media \(min-width: 1024px\) \{\s*:root \{ --site-header-offset: [^;]+; \}\s*\}\s*)?",
        ":root {\n      --site-header-offset: 0rem;\n    }\n",
        html,
        count=1,
    )

    # Drop legacy inlined initHeaderCategories if present
    html = re.sub(
        r"\s*\"?\(function initHeaderCategories\(\) \{.*?\n    \}\)\(\);\n?",
        "\n",
        html,
        count=1,
        flags=re.DOTALL,
    )

    template_path.write_text(html, encoding="utf-8")
    return True


def header_categories_script() -> str:
    """Kept for apply_template import compatibility; prefer header-megamag.js."""
    return ""


def sync_header_into_page(page_path: Path, *, home_href: str | None = None) -> bool:
    """Replace site-header in a page with NEW_HEADER and ensure CSS/JS hooks."""
    if not page_path.exists():
        return False
    html = page_path.read_text(encoding="utf-8")
    header = NEW_HEADER
    if home_href:
        header = header.replace('href="https://plasico.bg/" class="mm-logo"', f'href="{home_href}" class="mm-logo"', 1)
        header = header.replace(
            'href="https://plasico.bg/" class="header-cat-mega-parent header-utility-home"',
            f'href="{home_href}" class="header-cat-mega-parent header-utility-home"',
            1,
        )
        # Nested pages (e.g. hot-summer-sale-2026/*) need a relative logo path.
        if home_href.startswith("../"):
            logo_prefix = home_href.rsplit("/", 1)[0] + "/"
            header = header.replace('src="logo-plasico.svg"', f'src="{logo_prefix}logo-plasico.svg"', 1)
    new_html, n = re.subn(
        r'<header id="site-header"[\s\S]*?</header>',
        header,
        html,
        count=1,
    )
    if n == 0:
        return False
    html = new_html
    if 'megamag-header.css' not in html:
        if 'theme-overrides.css' in html:
            html = html.replace(
                '<link rel="stylesheet" href="theme-overrides.css"/>',
                '<link rel="stylesheet" href="theme-overrides.css"/>\n  <link rel="stylesheet" href="megamag-header.css"/>',
                1,
            )
        elif 'checkout-mock.css' in html:
            html = html.replace(
                '<link rel="stylesheet" href="checkout-mock.css"/>',
                '<link rel="stylesheet" href="megamag-header.css"/>\n  <link rel="stylesheet" href="checkout-mock.css"/>',
                1,
            )
    if 'header-megamag.js' not in html:
        if 'cart-drawer.js' in html:
            html = html.replace(
                '<script src="cart-drawer.js"></script>',
                '<script src="cart-drawer.js"></script>\n<script src="header-megamag.js"></script>',
                1,
            )
        else:
            html = html.replace('</body>', '<script src="header-megamag.js"></script>\n</body>', 1)
    html = re.sub(
        r":root \{\s*--site-header-offset:[^}]+\}\s*"
        r"(?:@media \(min-width: 640px\) and \(max-width: 1023px\) \{\s*:root \{ --site-header-offset: [^;]+; \}\s*\}\s*)?"
        r"(?:@media \(min-width: 1024px\) \{\s*:root \{ --site-header-offset: [^;]+; \}\s*\}\s*)?",
        ":root {\n      --site-header-offset: 0rem;\n    }\n",
        html,
        count=1,
    )
    html = re.sub(
        r"\s*\"?\(function initHeaderCategories\(\) \{.*?\n    \}\)\(\);\n?",
        "\n",
        html,
        count=1,
        flags=re.DOTALL,
    )
    page_path.write_text(html, encoding="utf-8")
    return True
