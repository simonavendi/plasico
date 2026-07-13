#!/usr/bin/env python3
"""Apply Spatial Minimalism shell from hot-summer-sale-2026.html to mirror pages.

Usage:
  python apply_template.py              # redesign priority + campaign pages + update nav
  python apply_template.py --nav-only   # update hot-summer-sale-2026.html links only
  python apply_template.py --page magazini.html
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from build_campaign_catalog import catalog_scripts_html
from patch_header_restructure import header_categories_script, patch_template_header

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "hot-summer-sale-2026.html"
LINK_MAP_FILE = ROOT / "link-map.json"
CATEGORY_MAP_FILE = ROOT / "category-map.json"
BACKUP_SUFFIX = ".mirror-backup"
SITE_HOME_URL = "https://plasico.bg/"

MIRROR_CONTENT_CSS = """
    .mirror-breadcrumb {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.35rem;
      font-size: 13px;
      color: #c9c5cc;
      margin-bottom: 1.5rem;
    }
    .mirror-breadcrumb a {
      color: #c9c5cc;
      text-decoration: none;
      transition: color 0.2s ease;
    }
    .mirror-breadcrumb a:hover { color: #07a857; }
    .mirror-breadcrumb__sep { opacity: 0.45; }
    .mirror-content {
      color: #e5e1e2;
      line-height: 1.65;
    }
    .mirror-content h1 {
      font-size: clamp(1.75rem, 4vw, 2.5rem);
      font-weight: 700;
      letter-spacing: -0.02em;
      margin: 0 0 1.5rem;
      color: #e5e1e2;
    }
    .mirror-content h2 {
      font-size: 1.35rem;
      font-weight: 600;
      margin: 2rem 0 0.75rem;
      color: #e5e1e2;
    }
    .mirror-content h3 {
      font-size: 1.1rem;
      font-weight: 600;
      margin: 1.25rem 0 0.5rem;
      color: #e5e1e2;
    }
    .mirror-content p { margin: 0 0 1rem; color: #c9c5cc; }
    .mirror-content ul, .mirror-content ol {
      margin: 0 0 1rem 1.25rem;
      color: #c9c5cc;
    }
    .mirror-content li { margin-bottom: 0.35rem; }
    .mirror-content a {
      color: #07a857;
      text-decoration: underline;
      text-underline-offset: 2px;
    }
    .mirror-content a:hover { color: #ffb783; }
    .mirror-content img {
      max-width: 100%;
      height: auto;
      border-radius: 12px;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .mirror-content .shop,
    .mirror-content article.shop,
    .mirror-content section {
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .mirror-content .btn,
    .mirror-content a.btn {
      display: inline-flex;
      align-items: center;
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      background: rgba(7, 168, 87, 0.15);
      border: 1px solid rgba(7, 168, 87, 0.35);
      color: #07a857 !important;
      text-decoration: none !important;
      font-weight: 600;
      font-size: 14px;
      margin-top: 0.5rem;
    }
    .mirror-content .btn:hover {
      background: rgba(7, 168, 87, 0.25);
      color: #069449 !important;
    }
    .mirror-content .media-bl {
      display: grid;
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }
    @media (min-width: 768px) {
      .mirror-content .media-bl.flexed {
        grid-template-columns: 1fr 1fr;
        align-items: start;
      }
    }
    .mirror-content .acc { color: #c9c5cc; }
    .mirror-content table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
    .mirror-content th, .mirror-content td {
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 0.5rem 0.75rem;
      text-align: left;
    }
    .campaign-nav-strip {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
      padding: 0.75rem 1rem;
      border-radius: 16px;
      background: rgba(32, 31, 32, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .campaign-nav-strip a {
      font-size: 12px;
      font-weight: 500;
      padding: 0.35rem 0.75rem;
      border-radius: 9999px;
      border: 1px solid rgba(255, 255, 255, 0.14);
      color: #c9c5cc;
      text-decoration: none;
      transition: all 0.2s ease;
    }
    .campaign-nav-strip a:hover,
    .campaign-nav-strip a.is-active {
      border-color: rgba(7, 168, 87, 0.5);
      color: #07a857;
      background: rgba(7, 168, 87, 0.1);
    }
    .content-page-hero {
      margin-bottom: 2rem;
      padding: 1.5rem 0 0.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }
    .content-page-hero__eyebrow {
      display: inline-block;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      color: #07a857;
      margin-bottom: 0.5rem;
    }
"""

HEADER_CATEGORIES_SCRIPT = header_categories_script()

HEADER_AUTH_SCRIPT = r"""
    (function initHeaderAuth() {
      const root = document.getElementById('header-auth');
      const toggle = document.getElementById('header-auth-toggle');
      const panel = document.getElementById('header-auth-panel');
      const backdrop = document.getElementById('header-auth-backdrop');
      if (!root || !toggle || !panel) return;

      const OAUTH_URLS = {
        facebook: 'https://plasico.bg/oauth_dialog?oauth=facebook',
        google: 'https://plasico.bg/oauth_dialog?oauth=google'
      };

      let isOpen = false;
      let lastFocused = null;

      function openOAuthPopup(url) {
        const w = 640;
        const h = 480;
        const left = (screen.width / 2) - (w / 2);
        const top = (screen.height / 2) - (h / 2);
        const popup = window.open(
          url,
          '',
          'toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=no,resizable=no,copyhistory=no,width=' + w + ',height=' + h + ',top=' + top + ',left=' + left
        );
        if (popup) popup.focus();
      }

      function closeAuth() {
        if (!isOpen) return;
        isOpen = false;
        root.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
        panel.setAttribute('aria-hidden', 'true');
        panel.hidden = true;
        if (backdrop) {
          backdrop.classList.remove('is-visible');
          backdrop.setAttribute('aria-hidden', 'true');
        }
        document.removeEventListener('keydown', onKeydown);
        if (lastFocused && typeof lastFocused.focus === 'function') lastFocused.focus();
      }

      function openAuth() {
        if (isOpen) return;
        window.__closeHeaderCategories?.();
        window.__closeHeaderCategoriesPanel?.();
        window.__closeCartDrawer?.();
        isOpen = true;
        lastFocused = document.activeElement;
        root.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
        panel.hidden = false;
        panel.setAttribute('aria-hidden', 'false');
        if (backdrop) {
          backdrop.classList.add('is-visible');
          backdrop.setAttribute('aria-hidden', 'false');
        }
        requestAnimationFrame(() => {
          const first = panel.querySelector('a, button');
          if (first) first.focus();
        });
        document.addEventListener('keydown', onKeydown);
      }

      function onKeydown(e) {
        if (e.key === 'Escape') {
          e.preventDefault();
          closeAuth();
        }
      }

      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        if (isOpen) closeAuth();
        else openAuth();
      });

      backdrop?.addEventListener('click', closeAuth);

      document.addEventListener('click', (e) => {
        if (!isOpen) return;
        if (root.contains(e.target)) return;
        closeAuth();
      });

      panel.querySelectorAll('[data-oauth]').forEach((btn) => {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const provider = btn.getAttribute('data-oauth');
          const url = OAUTH_URLS[provider];
          if (url) openOAuthPopup(url);
          closeAuth();
        });
      });

      window.__closeHeaderAuth = closeAuth;
      window.__openHeaderAuth = openAuth;
    })();
"""

CONTENT_PAGE_SCRIPTS = (
  "  <script>\n"
  + HEADER_CATEGORIES_SCRIPT
  + """
    (function initBackToTop() {
      const btn = document.getElementById('back-to-top');
      if (!btn) return;
      const toggle = () => {
        const visible = window.scrollY > 400;
        btn.classList.toggle('opacity-0', !visible);
        btn.classList.toggle('pointer-events-none', !visible);
        btn.classList.toggle('translate-y-2', !visible);
      };
      window.addEventListener('scroll', toggle, { passive: true });
      toggle();
      btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    })();

    window.addEventListener('keydown', (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('header-search');
        if (searchInput) searchInput.focus();
      }
    });
  </script>
"""
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def depth_prefix(page_path: str) -> str:
    depth = page_path.count("/")
    return "../" * depth if depth else ""


def rel_href(target: str, from_page: str) -> str:
    """Resolve a root-relative target path from a page location."""
    prefix = depth_prefix(from_page)
    if target.startswith("http://") or target.startswith("https://"):
        return target
    if target.startswith("/"):
        return target
    return f"{prefix}{target}"


def resolve_plasico_url(url: str, link_map: dict, from_page: str) -> str:
    """Map plasico.bg URL to local mirror path when available."""
    if not url or url.startswith("#") or url.startswith("tel:") or url.startswith("mailto:"):
        return url

    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc not in ("plasico.bg", "www.plasico.bg"):
        return url

    path = parsed.path.rstrip("/")
    full = f"https://plasico.bg{path}" if path else "https://plasico.bg/"

    utility = link_map.get("utility", {})
    if full in utility:
        return rel_href(utility[full], from_page)
    if full + "/" in utility:
        return rel_href(utility[full + "/"], from_page)

    categories = link_map.get("categoryLandings", {})
    if full in categories:
        return rel_href(categories[full], from_page)

    campaign = link_map.get("campaignSubpages", {})
    slug = path.split("/")[-1] if path.startswith("/hot-summer-sale-2026/") else None
    if slug and slug in campaign:
        return rel_href(campaign[slug], from_page)

    footer = link_map.get("footerProducts", {})
    if full in footer and footer[full].get("local"):
        return rel_href(footer[full]["local"], from_page)

    if any(full.startswith(ext.rstrip("/")) for ext in link_map.get("alwaysExternal", [])):
        return url

    return url


def rewrite_hrefs_in_html(html: str, link_map: dict, from_page: str) -> str:
    def replacer(match: re.Match) -> str:
        attr, quote, url = match.group(1), match.group(2), match.group(3)
        if url.startswith("data:") or url.startswith("javascript:"):
            return match.group(0)
        new_url = resolve_plasico_url(url, link_map, from_page)
        if new_url == url and url.startswith("../static.plasico.bg/"):
            new_url = "https://static.plasico.bg/" + url.split("../static.plasico.bg/", 1)[1]
        elif new_url == url and url.startswith("https://static.plasico.bg/"):
            pass
        elif new_url == url and not url.startswith("http") and not url.startswith("#") and not url.startswith("tel:"):
            new_url = rel_href(url, from_page)
        return f'{attr}={quote}{new_url}{quote}'

    html = re.sub(
        r'(href|src|data-original|action)=(["\'])(.*?)\2',
        replacer,
        html,
        flags=re.IGNORECASE,
    )
    return html


def fix_static_assets(html: str) -> str:
    html = html.replace("../static.plasico.bg/", "https://static.plasico.bg/")
    html = re.sub(
        r'https://static\.plasico\.bg/([^"\s>]+)\.html',
        r"https://static.plasico.bg/\1",
        html,
    )
    html = re.sub(
        r'src="[^"]*transp\.png"[^>]*data-original="([^"]+)"',
        r'src="\1" loading="lazy"',
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r'src="https://static\.plasico\.bg/images/transp\.png"\s+src="([^"]+)"',
        r'src="\1" loading="lazy"',
        html,
    )
    html = re.sub(r'\sclass="lazy"', "", html)
    html = re.sub(r'(loading="lazy"\s*)+', 'loading="lazy" ', html)
    return html


def extract_hero_section(template_html: str) -> str:
    match = re.search(
        r'(<section class="relative min-h-\[85vh\][\s\S]*?hero-bg[\s\S]*?</section>)',
        template_html,
    )
    if not match:
        raise SystemExit("Could not extract hero section from hot-summer-sale-2026.html")
    return match.group(1)


def build_campaign_hero(template_html: str, link_map: dict, from_page: str) -> str:
    hero = extract_hero_section(template_html)
    hero = adapt_shell_part(hero, link_map, from_page)
    if from_page.startswith("hot-summer-sale-2026/") and Path(from_page).stem != "index":
        hero = hero.replace('href="#laptopi"', 'href="#catalog"')
    else:
        hero = hero.replace(
            'href="#laptopi"',
            f'href="{rel_href("hot-summer-sale-2026.html#laptopi", from_page)}"',
        )
    return "\n".join(
        f"    {line}" if line.strip() else line for line in hero.split("\n")
    )


def campaign_page_has_hero(html: str) -> bool:
    return bool(
        re.search(r'<section class="relative min-h-\[85vh\][^"]*hero-bg', html)
    )


def fix_hero_css_paths(html: str, from_page: str) -> str:
    prefix = depth_prefix(from_page)
    if prefix:
        html = html.replace(
            "url('redesign/beb8ce72",
            f"url('{prefix}redesign/beb8ce72",
        )
    return html


def extract_shell(template_html: str) -> dict:
    head_match = re.search(r"(<!DOCTYPE html>.*?</head>)", template_html, re.DOTALL | re.IGNORECASE)
    header_match = re.search(
        r'(<header id="site-header".*?</header>)', template_html, re.DOTALL
    )
    footer_match = re.search(
        r'(<footer class="w-full.*?</footer>)', template_html, re.DOTALL
    )
    back_btn_match = re.search(
        r'(<button id="back-to-top".*?</button>)', template_html, re.DOTALL
    )
    cart_drawer_match = re.search(
        r'(<div id="cart-drawer-root".*?</aside>\s*</div>)', template_html, re.DOTALL
    )
    if not all([head_match, header_match, footer_match, back_btn_match, cart_drawer_match]):
        raise SystemExit("Could not extract shell from hot-summer-sale-2026.html")

    style_block = re.search(r"(<style>.*?</style>)", template_html, re.DOTALL)
    return {
        "head": head_match.group(1),
        "style": style_block.group(1) if style_block else "",
        "header": header_match.group(1),
        "footer": footer_match.group(1),
        "back_to_top": back_btn_match.group(1),
        "cart_drawer": cart_drawer_match.group(1),
    }


def patch_header_site_home_links(part: str) -> str:
    """Keep header home icon and logo pointing at main plasico.bg (not campaign home)."""
    part = re.sub(
        r'(<a href=")[^"]*(" class="[^"]*header-utility-home)',
        rf"\1{SITE_HOME_URL}\2",
        part,
    )
    part = re.sub(
        r'(<a href=")[^"]*(" class="shrink-0 flex items-center">\s*<img src="[^"]*logo-plasico\.svg")',
        rf"\1{SITE_HOME_URL}\2",
        part,
        count=1,
        flags=re.DOTALL,
    )
    return part


def adapt_shell_part(part: str, link_map: dict, from_page: str, active_utility: str | None = None) -> str:
    prefix = depth_prefix(from_page)

    part = rewrite_hrefs_in_html(part, link_map, from_page)

    part = part.replace('src="redesign/', f'src="{prefix}redesign/')
    part = part.replace("url('redesign/", f"url('{prefix}redesign/")

    if from_page.startswith("hot-summer-sale-2026/"):
        part = part.replace("fetch('category-map.json')", f"fetch('{prefix}category-map.json')")

    part = part.replace(
        'data-category-map="category-map.json"',
        f'data-category-map="{prefix}category-map.json"',
    )

    if active_utility:
        for label, path in [
            ("Магазини", "magazini.html"),
            ("Сервиз", "serviz.html"),
            ("За нас", "za-nas.html"),
            ("Контакти", "kontakti.html"),
        ]:
            if path == active_utility:
                icon = {
                    "Магазини": "storefront",
                    "Сервиз": "handyman",
                    "За нас": "groups",
                    "Контакти": "mail",
                }.get(label, "link")
                active_cell = (
                    f'<div class="header-cat-mega-cell is-active">\n'
                    f'                <a href="{rel_href(path, from_page)}" class="header-cat-mega-parent" aria-current="page">\n'
                    f'                  <span class="header-cat-mega-parent__icon" aria-hidden="true">'
                    f'<span class="material-symbols-outlined">{icon}</span></span>\n'
                    f'                  <span class="header-cat-mega-parent__label">{label}</span>\n'
                    f'                </a>\n'
                    f'              </div>'
                )
                part = re.sub(
                    rf'<div class="header-cat-mega-cell(?![^"]*panel-utility-mega-cell--sale)">\s*'
                    rf'<a href="[^"]*" class="header-cat-mega-parent">\s*'
                    rf'<span class="header-cat-mega-parent__icon"[^>]*>.*?</span>\s*'
                    rf'<span class="header-cat-mega-parent__label">{re.escape(label)}</span>\s*'
                    rf'</a>\s*</div>',
                    active_cell,
                    part,
                    count=1,
                    flags=re.DOTALL,
                )

    campaign_home = link_map.get("campaignHome", "hot-summer-sale-2026.html")
    is_campaign_page = (
        from_page == campaign_home
        or from_page.startswith("hot-summer-sale-2026/")
    )
    sale_href = rel_href(campaign_home, from_page)

    def patch_sale_cta(match: re.Match) -> str:
        classes = match.group(1).replace(" is-active", "").strip()
        attrs = re.sub(r'\s*aria-current="page"', "", match.group(2))
        if is_campaign_page:
            classes = f"{classes} is-active".strip()
            if 'aria-current="page"' not in attrs:
                attrs = f'{attrs} aria-current="page"'
        return f'<a href="{sale_href}" class="{classes}"{attrs}>'

    part = re.sub(
        r'<a href="[^"]*" class="(header-sale-cta[^"]*)"(.*?)>',
        patch_sale_cta,
        part,
    )
    part = re.sub(
        r'<a href="[^"]*" class="(header-cat-mega-parent panel-utility-mega-parent--sale[^"]*)"(.*?)>',
        patch_sale_cta,
        part,
    )

    if is_campaign_page:
        part = part.replace(
            'panel-utility-mega-cell--sale"',
            'panel-utility-mega-cell--sale is-active"',
            1,
        )
    else:
        part = part.replace(
            'panel-utility-mega-cell--sale is-active"',
            'panel-utility-mega-cell--sale"',
            1,
        )

    part = patch_header_site_home_links(part)

    return part


def extract_mirror_meta(html: str) -> tuple[str, str]:
    title_m = re.search(r"<title>(.*?)</title>", html, re.DOTALL | re.IGNORECASE)
    desc_m = re.search(
        r'<meta\s+name="description"\s+content="([^"]*)"',
        html,
        re.IGNORECASE,
    )
    title = title_m.group(1).strip() if title_m else "Plasico.bg"
    desc = desc_m.group(1).strip() if desc_m else title
    return title, desc


def extract_breadcrumb_label(html: str) -> str | None:
    path_m = re.search(r'<div id="path"[^>]*>(.*?)</div>', html, re.DOTALL | re.IGNORECASE)
    if not path_m:
        return None
    inner = path_m.group(1)
    spans = re.findall(r"<span[^>]*>([^<]+)</span>", inner)
    if spans:
        return spans[-1].strip()
    return None


def extract_main_content(html: str) -> str:
    main_m = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL | re.IGNORECASE)
    if main_m:
        inner = main_m.group(1).strip()
        inner = re.sub(
            r'<section class="relative min-h-\[85vh\][^>]*hero-bg[\s\S]*?</section>\s*',
            "",
            inner,
            count=1,
        )
        if 'mirror-breadcrumb' in inner or 'id="catalog"' in inner:
            wrapper_m = re.match(
                r'<div class="max-w-\[1440px\][^"]*"[^>]*>\s*(.*?)\s*</div>\s*$',
                inner,
                re.DOTALL,
            )
            if wrapper_m:
                inner = wrapper_m.group(1).strip()
            inner = re.sub(
                r'<nav class="mirror-breadcrumb"[\s\S]*?</nav>\s*', "", inner, count=1
            )
            inner = re.sub(
                r'<div class="campaign-nav-strip"[\s\S]*?</div>\s*', "", inner, count=1
            )
            inner = re.sub(
                r'<div class="content-page-hero"[\s\S]*?</div>\s*', "", inner, count=1
            )
            inner = re.sub(r'<article class="mirror-content">\s*', "", inner, count=1)
            inner = re.sub(r'\s*</article>\s*$', "", inner)
            return inner.strip()
        return inner
    category_m = re.search(
        r'<div id="category"[^>]*>(.*?)(?:</div>\s*</div>\s*</main>|</article>)',
        html,
        re.DOTALL | re.IGNORECASE,
    )
    if category_m:
        return category_m.group(1).strip()
    return "<p>Съдържанието не бе извлечено от огледалото.</p>"


def build_breadcrumb(from_page: str, label: str, link_map: dict, campaign_slug: str | None = None) -> str:
    home = rel_href(link_map["home"], from_page)
    parts = [
        f'<a href="{home}">Hot Summer Sale 2026</a>',
    ]
    if campaign_slug:
        parts.append('<span class="mirror-breadcrumb__sep" aria-hidden="true">›</span>')
        parts.append(f"<span>{escape(label)}</span>")
    else:
        parts.append('<span class="mirror-breadcrumb__sep" aria-hidden="true">›</span>')
        parts.append(f"<span>{escape(label)}</span>")
    return f'<nav class="mirror-breadcrumb" aria-label="Навигация">{" ".join(parts)}</nav>'


def build_campaign_nav(from_page: str, active_slug: str, link_map: dict, category_map: dict) -> str:
    prefix = depth_prefix(from_page)
    home = f'{prefix}hot-summer-sale-2026.html'
    links = [f'<a href="{home}">← Кампания</a>']
    for cat in category_map.get("categories", []):
        slug = cat.get("slug") or cat.get("id")
        if slug == "laptopi" or not slug:
            href = home + "#laptopi"
            label = cat.get("name", "Лаптопи")
        else:
            local = link_map.get("campaignSubpages", {}).get(slug)
            if not local:
                continue
            href = rel_href(local, from_page)
            label = cat.get("name", slug)
        active = " is-active" if slug == active_slug or (active_slug == "laptopi" and slug in ("", "laptopi")) else ""
        links.append(f'<a href="{href}" class="{active.strip()}">{escape(label)}</a>')
    return f'<div class="campaign-nav-strip" aria-label="Категории от кампанията">{"".join(links)}</div>'


def customize_head(head: str, title: str, description: str) -> str:
    head = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", head, flags=re.DOTALL)
    head = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{escape(description)}"',
        head,
    )
    head = head.replace('class="dark"', 'class="dark" data-redesign="spatial-minimalism"')
    if MIRROR_CONTENT_CSS.strip() not in head:
        head = head.replace("</style>", MIRROR_CONTENT_CSS + "\n  </style>")
    return head


def backup_file(path: Path) -> None:
    backup = path.with_suffix(path.suffix + BACKUP_SUFFIX)
    if not backup.exists() and path.exists():
        shutil.copy2(path, backup)


def build_content_page(
    page_path: str,
    shell: dict,
    link_map: dict,
    category_map: dict,
    *,
    campaign_slug: str | None = None,
    template_html: str | None = None,
) -> str:
    source = ROOT / page_path
    raw = source.read_text(encoding="utf-8")
    title, desc = extract_mirror_meta(raw)
    breadcrumb_label = extract_breadcrumb_label(raw) or title.split("|")[0].strip()
    content = extract_main_content(raw)
    content = fix_static_assets(content)
    content = rewrite_hrefs_in_html(content, link_map, page_path)

    head = customize_head(adapt_shell_part(shell["head"], link_map, page_path, page_path), title, desc)
    header = adapt_shell_part(shell["header"], link_map, page_path, page_path)
    footer = adapt_shell_part(shell["footer"], link_map, page_path)
    back_btn = shell["back_to_top"]
    prefix = depth_prefix(page_path)

    breadcrumb = build_breadcrumb(page_path, breadcrumb_label, link_map, campaign_slug)
    campaign_nav = ""
    hero_html = ""
    if campaign_slug:
        campaign_nav = build_campaign_nav(page_path, campaign_slug, link_map, category_map)
        tpl = template_html or TEMPLATE.read_text(encoding="utf-8")
        hero_html = build_campaign_hero(tpl, link_map, page_path)

    use_mirror_wrapper = not (campaign_slug and 'id="catalog"' in content)
    content_block = (
        f'<article class="mirror-content">\n        {content}\n      </article>'
        if use_mirror_wrapper
        else content
    )

    main = f"""
  <main class="pt-[var(--site-header-offset)]">
{hero_html}
    <div class="max-w-[1440px] mx-auto px-container-padding py-8 lg:py-12">
      {breadcrumb}
      {campaign_nav}
      {content_block}
    </div>
  </main>"""

    scripts = CONTENT_PAGE_SCRIPTS.strip()
    if campaign_slug and 'id="catalog"' in content:
        cat = next(
            (c for c in category_map.get("categories", []) if c.get("slug") == campaign_slug),
            None,
        )
        if cat:
            scripts = catalog_scripts_html(prefix, cat) + "\n" + scripts

    return "\n".join([
        head,
        f'<body class="font-body-md selection:bg-apricot/30 custom-scrollbar" data-category-map="{prefix}category-map.json">',
        header,
        main,
        footer,
        back_btn,
        scripts,
        "</body>",
        "</html>",
    ])


def apply_page(
    page_path: str,
    shell: dict,
    link_map: dict,
    category_map: dict,
    template_html: str | None = None,
) -> None:
    target = ROOT / page_path
    if not target.exists():
        print(f"SKIP: {page_path} not found")
        return

    campaign_slug = None
    if page_path.startswith("hot-summer-sale-2026/"):
        name = Path(page_path).stem
        if name != "index":
            campaign_slug = name

    backup_file(target)
    html = build_content_page(
        page_path,
        shell,
        link_map,
        category_map,
        campaign_slug=campaign_slug,
        template_html=template_html,
    )
    target.write_text(html, encoding="utf-8")
    print(f"OK: {page_path}")


def apply_campaign_hero(page_path: str, template_html: str, link_map: dict) -> bool:
    """Inject campaign hero into an existing redesigned subpage."""
    target = ROOT / page_path
    if not target.exists():
        print(f"SKIP: {page_path} not found")
        return False
    html = target.read_text(encoding="utf-8")
    if campaign_page_has_hero(html):
        print(f"SKIP: {page_path} already has hero")
        return False
    hero = build_campaign_hero(template_html, link_map, page_path)
    html = fix_hero_css_paths(html, page_path)
    html = re.sub(
        r'(<main class="pt-\[var\(--site-header-offset\)\]">)\s*\n',
        r"\1\n" + hero + "\n",
        html,
        count=1,
    )
    target.write_text(html, encoding="utf-8")
    print(f"OK: {page_path} hero injected")
    return True


def update_template_navigation(link_map: dict) -> None:
    html = TEMPLATE.read_text(encoding="utf-8")
    from_page = "hot-summer-sale-2026.html"

    replacements = [
        ('href="https://plasico.bg/magazini"', f'href="{rel_href("magazini.html", from_page)}"'),
        ('href="https://plasico.bg/serviz"', f'href="{rel_href("serviz.html", from_page)}"'),
        ('href="https://plasico.bg/za-nas"', f'href="{rel_href("za-nas.html", from_page)}"'),
        ('href="https://plasico.bg/blog/"', f'href="{rel_href("blog/index.html", from_page)}"'),
        ('href="https://plasico.bg/kontakti"', f'href="{rel_href("kontakti.html", from_page)}"'),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    footer_map = link_map.get("footerProducts", {})
    for url, info in footer_map.items():
        if info.get("local"):
            local = rel_href(info["local"], from_page)
            html = html.replace(f'href="{url}"', f'href="{local}"')
            html = html.replace(f"href='{url}'", f"href='{local}'")

    for url, local_file in link_map.get("categoryLandings", {}).items():
        local = rel_href(local_file, from_page)
        html = html.replace(f'href="{url}"', f'href="{local}"')

    za_plasico = [
        ("https://plasico.bg/magazini", "magazini.html"),
        ("https://plasico.bg/za-nas", "za-nas.html"),
        ("https://plasico.bg/kontakti", "kontakti.html"),
    ]
    for url, file in za_plasico:
        html = html.replace(f'href="{url}"', f'href="{rel_href(file, from_page)}"')

    hero_cta = 'href="https://plasico.bg/magazini"'
    if hero_cta in html:
        html = html.replace(hero_cta, f'href="{rel_href("magazini.html", from_page)}"')

    TEMPLATE.write_text(html, encoding="utf-8")
    print("OK: hot-summer-sale-2026.html navigation updated")


def update_category_map(link_map: dict) -> None:
    data = load_json(CATEGORY_MAP_FILE)
    campaign = link_map.get("campaignSubpages", {})

    for cat in data.get("categories", []):
        slug = cat.get("slug") or ""
        cat_id = cat.get("id", "")

        if cat_id == "laptopi" or not slug:
            cat["localUrl"] = "hot-summer-sale-2026.html#laptopi"
            cat["local"] = True
            cat["external"] = False
        elif slug in campaign:
            cat["localUrl"] = campaign[slug]
            cat["local"] = True
            cat["external"] = False
            for sub in cat.get("subcategories", []):
                sub["action"] = "local"
                if sub.get("anchor"):
                    sub["url"] = f"{campaign[slug]}{sub['anchor']}"
        else:
            cat.setdefault("localUrl", cat.get("url"))

        for sub in cat.get("subcategories", []):
            if cat.get("local") and sub.get("anchor") and slug in campaign:
                sub["action"] = "local"
                sub["url"] = f"{campaign[slug]}{sub.get('anchor', '')}"

    data.setdefault("linking", {})["updatedAt"] = "2026-07-13"
    data["linking"]["localCampaignPages"] = list(campaign.values())
    CATEGORY_MAP_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK: category-map.json updated with localUrl fields")


def fix_campaign_page_js() -> None:
    html = TEMPLATE.read_text(encoding="utf-8")
    changed = False

    if "function navigateCategoryUrl(url)" not in html:
        old_handler = """    function handleSubcategoryAction(sub, category, applyFilterFn) {
      if (sub.action === 'external' || category.external) {
        window.open(sub.url, '_blank', 'noopener');
        return;
      }"""
        new_handler = """  function navigateCategoryUrl(url) {
      if (!url) return;
      if (url.startsWith('#')) {
        const target = document.querySelector(url.split('?')[0]);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
      window.location.href = url;
    }

    function handleSubcategoryAction(sub, category, applyFilterFn) {
      const localUrl = sub.url && !sub.url.startsWith('https://plasico.bg') ? sub.url : (category.localUrl || null);
      if (sub.action === 'local' || (localUrl && !localUrl.startsWith('https://'))) {
        navigateCategoryUrl(sub.url || localUrl);
        return;
      }
      if (sub.action === 'external' || category.external) {
        const dest = category.localUrl || sub.url;
        if (dest && !dest.startsWith('https://plasico.bg')) {
          navigateCategoryUrl(dest);
        } else {
          window.open(sub.url, '_blank', 'noopener');
        }
        return;
      }"""
        if old_handler in html:
            html = html.replace(old_handler, new_handler)
            changed = True

    if "const localUrl = category.localUrl" not in html:
        html = html.replace(
            "        const subs = getCategorySubs(category);\n\n        const btn = document.createElement('button');",
            "        const subs = getCategorySubs(category);\n        const localUrl = category.localUrl || null;\n\n        const btn = document.createElement('button');",
        )
        html = html.replace(
            "        if (category.external) btn.dataset.external = category.url;",
            "        if (localUrl) btn.dataset.localUrl = localUrl;\n        else if (category.external) btn.dataset.external = category.url;",
        )
        changed = True

    if "laptopFilters.has(category.dataFilter)" not in html:
        html = html.replace(
            """        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const wasExpanded = cell.classList.contains('is-expanded');""",
            """        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const laptopFilters = new Set(['all', 'laptopi', 'gaming', 'business', 'ultrabook']);
          if (localUrl && category.external === false && !laptopFilters.has(category.dataFilter)) {
            window.location.href = localUrl;
            return;
          }
          const wasExpanded = cell.classList.contains('is-expanded');""",
        )
        changed = True

    if "localUrl: category.localUrl" not in html:
        html = html.replace(
            "            external: category.url,\n            ...copy",
            "            external: category.url,\n            localUrl: category.localUrl || null,\n            ...copy",
        )
        changed = True

    if "const localDest = meta.localUrl" not in html:
        html = html.replace(
            """          emptyLink.href = meta.external || 'https://plasico.bg/hot-summer-sale-2026';
          emptyLink.innerHTML = 'Виж офертите на plasico.bg <span class="material-symbols-outlined text-[20px]">open_in_new</span>';""",
            """          const localDest = meta.localUrl || meta.external || 'hot-summer-sale-2026.html';
          const isExternal = localDest.startsWith('http');
          emptyLink.href = localDest;
          emptyLink.innerHTML = isExternal
            ? 'Виж офертите на plasico.bg <span class="material-symbols-outlined text-[20px]">open_in_new</span>'
            : 'Виж офертите в кампанията <span class="material-symbols-outlined text-[20px]">arrow_forward</span>';""",
        )
        changed = True

    if "resolveSubcategoryNavigateUrl" not in html:
        old_block = """    function handleSubcategoryAction(sub, category, applyFilterFn) {
      const localUrl = sub.url && !sub.url.startsWith('https://plasico.bg') ? sub.url : (category.localUrl || null);
      if (sub.action === 'local' || (localUrl && !localUrl.startsWith('https://'))) {
        navigateCategoryUrl(sub.url || localUrl);
        return;
      }
      if (sub.action === 'external' || (category.external && !category.localUrl)) {
        const dest = category.localUrl || sub.url;
        if (dest && !dest.startsWith('https://plasico.bg')) {
          navigateCategoryUrl(dest);
        } else {
          window.open(sub.url, '_blank', 'noopener');
        }
        return;
      }
      if (!LAPTOP_FILTER_IDS.has(category.dataFilter) && category.localUrl && sub.anchorId) {
        navigateCategoryUrl(`${category.localUrl}#${sub.anchorId}`);
        return;
      }
      if (sub.filterTag && applyFilterFn) {
        applyFilterFn(sub.filterTag, { scroll: true });
        return;
      }
      if (sub.anchor) {
        const target = document.querySelector(sub.anchor);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }"""
        new_block = """    function resolveSubcategoryNavigateUrl(sub, category) {
      if (sub.url && !sub.url.startsWith('https://plasico.bg') && !sub.url.startsWith('#')) {
        return sub.url;
      }
      if (category.localUrl) {
        const base = category.localUrl.split('#')[0];
        if (sub.anchorId) return `${base}#${sub.anchorId}`;
        return category.localUrl;
      }
      if (sub.url && sub.url.startsWith('#')) return sub.url;
      return null;
    }

    function syncCatalogSubcategoryChips(filterId) {
      const wrap = getCatalogSubcategoryFilterEl();
      if (!wrap) return;
      wrap.querySelectorAll('.category-subchip[data-filter]').forEach(chip => {
        chip.classList.toggle('is-active', chip.dataset.filter === filterId);
      });
    }

    function handleSubcategoryAction(sub, category, applyFilterFn) {
      if (sub.filterTag && LAPTOP_FILTER_IDS.has(sub.filterTag) && applyFilterFn) {
        applyFilterFn(sub.filterTag, { scroll: true });
        return;
      }

      if (sub.action === 'local') {
        const dest = resolveSubcategoryNavigateUrl(sub, category);
        if (dest) {
          navigateCategoryUrl(dest);
          return;
        }
      }

      if (!LAPTOP_FILTER_IDS.has(category.dataFilter) && category.localUrl) {
        const dest = resolveSubcategoryNavigateUrl(sub, category);
        if (dest && !dest.startsWith('https://')) {
          navigateCategoryUrl(dest);
          return;
        }
      }

      if (sub.action === 'external' || (category.external && !category.localUrl)) {
        const dest = category.localUrl || sub.url;
        if (dest && !dest.startsWith('https://plasico.bg')) {
          navigateCategoryUrl(dest);
        } else if (sub.url) {
          window.open(sub.url, '_blank', 'noopener');
        }
        return;
      }

      if (sub.filterTag && applyFilterFn) {
        applyFilterFn(sub.filterTag, { scroll: true });
        return;
      }

      if (sub.anchor) {
        const target = document.querySelector(sub.anchor);
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }"""
        if old_block in html:
            html = html.replace(old_block, new_block)
            changed = True

    if "isMainLaptopCatalog" not in html:
        html = html.replace(
            "      if (category.local) {",
            "      const isMainLaptopCatalog = category.id === 'laptopi' || LAPTOP_FILTER_IDS.has(category.dataFilter);\n      if (isMainLaptopCatalog) {",
        )
        changed = True

    if "filterGroups.find(g => g.dataset.categoryId === 'laptopi')" not in html:
        html = html.replace(
            """        let expandedGroup = null;
        filterGroups.forEach(group => {
          const hasActive = group.querySelector(`[data-filter="${filterId}"]`);
          if (hasActive) expandedGroup = group;
        });""",
            """        let expandedGroup = null;
        if (filterId === 'all' || filterId === 'laptopi') {
          expandedGroup = filterGroups.find(g => g.dataset.categoryId === 'laptopi') || null;
        }
        if (!expandedGroup) {
          filterGroups.forEach(group => {
            const hasActive = group.querySelector(`[data-filter="${filterId}"]`);
            if (hasActive) expandedGroup = group;
          });
        }""",
        )
        changed = True

    if "syncCatalogSubcategoryChips(activeFilter)" not in html:
        html = html.replace(
            "        setPillState(activeFilter);\n        setSortState(activeSort);",
            "        setPillState(activeFilter);\n        syncCatalogSubcategoryChips(activeFilter);\n        setSortState(activeSort);",
        )
        html = html.replace(
            "          setPillState(activeFilter);\n          showEmptyState(meta, false);",
            "          setPillState(activeFilter);\n          syncCatalogSubcategoryChips(activeFilter);\n          showEmptyState(meta, false);",
        )
        changed = True

    if changed:
        TEMPLATE.write_text(html, encoding="utf-8")
        print("OK: campaign page JS navigation patched")
    else:
        print("OK: campaign page JS already patched")


def write_navigation_doc(link_map: dict, redesigned: list[str]) -> None:
    lines = [
        "# Site Navigation Map",
        "",
        "Generated by `apply_template.py` on 2026-07-13.",
        "",
        "## Redesigned pages",
        "",
    ]
    for p in sorted(redesigned):
        lines.append(f"- `{p}`")
    lines.extend([
        "",
        "## Header utility links (local)",
        "",
    ])
    for url, local in link_map.get("utility", {}).items():
        lines.append(f"- {url} → `{local}`")
    lines.extend([
        "",
        "## Category landing pages (local mirror)",
        "",
    ])
    for url, local in link_map.get("categoryLandings", {}).items():
        lines.append(f"- {url} → `{local}`")
    lines.extend([
        "",
        "## Campaign subpages (local)",
        "",
    ])
    for slug, local in link_map.get("campaignSubpages", {}).items():
        lines.append(f"- `{slug}` → `{local}`")
    lines.extend([
        "",
        "## Still external (plasico.bg)",
        "",
        "- Account / login / cart / search / favorites",
        "- Product detail pages (`plasico.bg/*.html` product URLs)",
        "- Footer deep links without mirror (e.g. `/komponenti/video-karti`, `/printeri`)",
        "- Help pages, PDF policies, partner sites",
        "- `blog/index.html` (mirror exists but not fully restyled)",
        "",
        "## Scripts",
        "",
        "- `apply_template.py` — wrap mirror pages in Spatial Minimalism shell",
        "- `link-map.json` — URL resolution data",
        "- `category-map.json` — campaign categories with `localUrl` fields",
        "",
        "## Vercel",
        "",
        "Root `index.html` redirects to `hot-summer-sale-2026.html`.",
        "Clean URL rewrites added in `vercel.json` for utility and category pages.",
        "",
    ])
    (ROOT / "NAVIGATION.md").write_text("\n".join(lines), encoding="utf-8")
    print("OK: NAVIGATION.md written")


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply Spatial Minimalism template to mirror pages")
    parser.add_argument("--nav-only", action="store_true", help="Only update hot-summer-sale-2026.html navigation")
    parser.add_argument(
        "--hero-only",
        action="store_true",
        help="Inject campaign hero into hot-summer-sale-2026/*.html subpages",
    )
    parser.add_argument("--page", help="Redesign a single page (relative to plasico.bg/)")
    args = parser.parse_args()

    link_map = load_json(LINK_MAP_FILE)
    category_map = load_json(CATEGORY_MAP_FILE)

    if patch_template_header(TEMPLATE):
        print("OK: hot-summer-sale-2026.html header restructured")

    if args.nav_only:
        update_template_navigation(link_map)
        update_category_map(link_map)
        fix_campaign_page_js()
        return

    template_html = TEMPLATE.read_text(encoding="utf-8")

    if args.hero_only:
        pages = link_map.get("campaignPages", [])
        if args.page:
            pages = [args.page]
        updated = 0
        for page in pages:
            if apply_campaign_hero(page, template_html, link_map):
                updated += 1
        print(f"Done: {updated} campaign subpage(s) updated with hero")
        return

    shell = extract_shell(template_html)

    pages: list[str] = []
    if args.page:
        pages = [args.page]
    else:
        pages = link_map.get("priorityPages", []) + link_map.get("campaignPages", [])

    redesigned: list[str] = []
    for page in pages:
        if (ROOT / page).exists():
            apply_page(page, shell, link_map, category_map, template_html=template_html)
            redesigned.append(page)

    update_template_navigation(link_map)
    update_category_map(link_map)
    fix_campaign_page_js()
    write_navigation_doc(link_map, redesigned)


if __name__ == "__main__":
    main()
