#!/usr/bin/env python3
"""Build campaign subpages with redesigned product catalog + filters from products-map."""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path

DIR = Path(__file__).parent
TEMPLATE = DIR / "hot-summer-sale-2026.html"
PRODUCTS_MAP = DIR / "products-map.json"
CATEGORY_MAP = DIR / "category-map.json"
CAMPAIGN_DIR = DIR / "hot-summer-sale-2026"

# Import render helpers from scrape_live_campaign
sys.path.insert(0, str(DIR))
from scrape_live_campaign import badge_classes, render_product, SALE_BADGE_HREF_SUBPAGE  # noqa: E402

CAMPAIGN_SLUGS = [
    "computers", "components", "monitors", "used", "office-chairs", "gchairs",
    "audio", "bags", "flash", "external", "printers", "accessories",
    "cctv", "network", "hubs", "cables", "ups",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_block(html: str, start_marker: str, end_marker: str) -> str:
    start = html.index(start_marker)
    end = html.index(end_marker, start)
    return html[start:end]


def extract_style_block(html: str) -> str:
    m = re.search(r"(<style>.*?</style>)", html, re.DOTALL)
    return m.group(1) if m else ""


def extract_tailwind_config(html: str) -> str:
    m = re.search(r'(<script id="tailwind-config">.*?</script>)', html, re.DOTALL)
    return m.group(1) if m else ""


def campaign_nav_strip(categories: list[dict], active_id: str) -> str:
    links = ['<a href="../hot-summer-sale-2026.html">← Кампания</a>']
    for cat in categories:
        href = cat.get("localUrl") or f"hot-summer-sale-2026/{cat['slug']}.html"
        if not href.startswith("../"):
            href = f"../{href}" if "/" in href else f"../hot-summer-sale-2026/{cat['slug']}.html"
        cls = ' class="is-active"' if cat["id"] == active_id else ""
        links.append(f'<a href="{escape(href)}"{cls}>{escape(cat["name"])}</a>')
    return f'<div class="campaign-nav-strip" aria-label="Категории от кампанията">{"".join(links)}</div>'


def catalog_filter_panel(show_os: bool = True, show_upgraded: bool = True) -> str:
    os_block = ""
    if show_os:
        os_block = """
              <div>
                <h3 class="filter-section-title">Операционна система</h3>
                <div id="catalog-os-filter" class="flex flex-wrap gap-2" role="group" aria-label="Филтър по операционна система"></div>
              </div>"""
    upgraded_block = ""
    if show_upgraded:
        upgraded_block = """
              <div>
                <h3 class="filter-section-title">Ъпгрейднати</h3>
                <div id="catalog-upgraded-filter" class="flex flex-wrap gap-2" role="group" aria-label="Филтър по ъпгрейднати продукти">
                  <button type="button" id="filter-upgraded-only" class="filter-sort-btn" aria-pressed="false">UPGRADED <span id="upgraded-filter-count" class="filter-count">(0)</span></button>
                </div>
              </div>"""

    return f"""
        <div class="mb-stack-lg">
          <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
            <button type="button" id="filter-panel-toggle" class="filter-pill inline-flex items-center gap-2" aria-expanded="false" aria-controls="catalog-filter-panel">
              <span class="material-symbols-outlined text-[18px]">tune</span>
              Филтри
              <span class="filter-toggle-icon material-symbols-outlined text-[18px]">expand_more</span>
            </button>
            <button type="button" id="filter-reset" class="text-technical-sm text-on-surface-variant hover:text-apricot transition-colors hidden">Изчисти филтрите</button>
          </div>
          <div id="catalog-filter-panel" class="squircle intelligent-edge bg-surface-container p-6 md:p-8" aria-hidden="true">
            <div class="catalog-filter-layout grid grid-cols-1 md:grid-cols-[minmax(0,1.2fr)_minmax(0,1fr)] xl:grid-cols-[minmax(280px,1.35fr)_minmax(260px,1fr)] gap-6 lg:gap-8 items-start">
              <div class="catalog-filter-sidebar min-w-0">
                <h3 class="filter-section-title">Подкатегории</h3>
                <div id="catalog-subcategory-filter" class="catalog-subcategory-filter is-visible" role="group" aria-label="Подкатегории"></div>
              </div>
              <div class="catalog-filter-controls flex flex-col gap-6 min-w-0">
                <div>
                  <h3 class="filter-section-title">Отстъпка</h3>
                  <div id="catalog-discount-filter" class="flex flex-wrap gap-2" role="group" aria-label="Филтър по отстъпка">
                    <button type="button" class="filter-sort-btn" data-discount-min="0" aria-pressed="true">Всички</button>
                    <button type="button" class="filter-sort-btn" data-discount-min="10" aria-pressed="false">10%+</button>
                    <button type="button" class="filter-sort-btn" data-discount-min="20" aria-pressed="false">20%+</button>
                    <button type="button" class="filter-sort-btn" data-discount-min="30" aria-pressed="false">30%+</button>
                    <button type="button" class="filter-sort-btn" data-discount-min="40" aria-pressed="false">40%+</button>
                  </div>
                </div>
                {upgraded_block}
                {os_block}
                <div>
                  <h3 class="filter-section-title">Ценови диапазон</h3>
                  <div class="flex items-center gap-3 mb-3">
                    <label class="flex-1">
                      <span class="text-technical-sm text-on-surface-variant block mb-1">От</span>
                      <input type="number" id="price-min-input" class="filter-input" min="0" step="1" inputmode="decimal"/>
                    </label>
                    <label class="flex-1">
                      <span class="text-technical-sm text-on-surface-variant block mb-1">До</span>
                      <input type="number" id="price-max-input" class="filter-input" min="0" step="1" inputmode="decimal"/>
                    </label>
                  </div>
                  <div class="relative h-2 bg-surface-variant rounded-full mb-2">
                    <div id="price-range-fill" class="absolute h-full bg-apricot/60 rounded-full"></div>
                    <input type="range" id="price-slider-min" class="absolute w-full h-2 appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-apricot"/>
                    <input type="range" id="price-slider-max" class="absolute w-full h-2 appearance-none bg-transparent pointer-events-none [&::-webkit-slider-thumb]:pointer-events-auto [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-apricot"/>
                  </div>
                  <p id="price-range-label" class="text-technical-sm text-on-surface-variant"></p>
                </div>
                <div>
                  <h3 class="filter-section-title">Подреждане по цена</h3>
                  <div id="catalog-sort" class="flex flex-wrap gap-2" role="group" aria-label="Подреждане">
                    <button type="button" class="filter-sort-btn" data-sort="default" aria-pressed="true">По подразбиране</button>
                    <button type="button" class="filter-sort-btn" data-sort="price-asc" aria-pressed="false">Цена: ниска → висока</button>
                    <button type="button" class="filter-sort-btn" data-sort="price-desc" aria-pressed="false">Цена: висока → ниска</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>"""


def product_to_render_dict(p: dict) -> dict:
    tags = list(p.get("tags") or [])
    cat = p["categoryId"]
    sub = p["subcategoryAnchor"]
    merged = list(dict.fromkeys([*tags, cat, sub]))
    if p.get("upgraded") and "upgraded" not in merged:
        merged.append("upgraded")
    return {
        "id": p["id"],
        "title": p["title"],
        "url": p["url"],
        "image": p["image"],
        "price": p.get("price"),
        "old_price": p.get("oldPrice"),
        "discount": p.get("discount") or 0,
        "upgraded": p.get("upgraded", False),
        "promocode": p.get("promocode", False),
        "tags": merged,
        "specs": p.get("specs") or [],
        "os": p.get("os") or "unknown",
    }


def render_product_grid(products: list[dict], category: dict) -> str:
    """Group products by subcategory with anchor targets for hash navigation."""
    by_sub: dict[str, list[dict]] = {}
    order: list[str] = []
    for p in products:
        sub = p.get("subcategoryAnchor") or "all"
        if sub not in by_sub:
            by_sub[sub] = []
            order.append(sub)
        by_sub[sub].append(p)

    sub_names = {
        (s.get("anchorId") or s.get("anchor", "").lstrip("#")): s["name"]
        for s in category.get("subcategories", [])
    }

    parts: list[str] = []
    for sub in order:
        items = by_sub[sub]
        title = sub_names.get(sub, sub.replace("-", " ").title())
        parts.append(
            f'<div id="{escape(sub)}" class="col-span-full scroll-mt-28 pt-4">'
            f'<h2 class="font-headline-md text-headline-md font-semibold text-on-surface-variant mb-4">{escape(title)}'
            f' <span class="text-technical-sm font-normal">({len(items)})</span></h2></div>'
        )
        parts.append(
            "\n\n".join(
                render_product(product_to_render_dict(p), sale_badge_href=SALE_BADGE_HREF_SUBPAGE)
                for p in items
            )
        )
    return "\n\n".join(parts)


def catalog_page_config(category: dict) -> dict:
    subcategories = [
        {
            "name": s["name"],
            "anchorId": s.get("anchorId") or s.get("anchor", "").lstrip("#"),
            "productCount": s.get("productCount", 0),
        }
        for s in category.get("subcategories", [])
        if s.get("productCount", 0) > 0 or s.get("anchorId")
    ]
    sub_ids = [s["anchorId"] for s in subcategories if s.get("anchorId")]
    return {
        "mode": "category",
        "categoryId": category["id"],
        "categoryName": category["name"],
        "sectionId": "catalog",
        "subcategoryIds": sub_ids,
        "subcategories": subcategories,
    }


def catalog_scripts_html(prefix: str, category: dict) -> str:
    config = json.dumps(catalog_page_config(category), ensure_ascii=False)
    return f"""  <script>
    window.CATALOG_PAGE = {config};
  </script>
  <script src="{prefix}catalog-filters.js"></script>"""


def build_page(
    category: dict,
    products: list[dict],
    template_html: str,
    all_categories: list[dict],
) -> str:
    cat_id = category["id"]
    slug = category["slug"]
    name = category["name"]
    count = len(products)

    style = extract_style_block(template_html)
    tailwind = extract_tailwind_config(template_html)
    header = extract_block(template_html, "<header", "</header>")
    footer = extract_block(template_html, '<footer class="w-full', "</footer>") + "</footer>"

    def fix_paths(block: str) -> str:
        block = re.sub(r'href="(?!https?://|#|tel:|mailto:)([^"]+)"', r'href="../\1"', block)
        block = block.replace('href="../hot-summer-sale-2026.html#', 'href="../hot-summer-sale-2026.html#')
        block = block.replace('href="../https://', 'href="https://')
        return block

    header = fix_paths(header)
    footer = fix_paths(footer)

    cards = render_product_grid(products, category)

    page_config = catalog_page_config(category)
    show_os = cat_id in ("laptopi", "computers", "used")
    show_upgraded = cat_id in ("laptopi", "computers", "used")

    nav = campaign_nav_strip(all_categories, cat_id)
    breadcrumb = (
        f'<nav class="mirror-breadcrumb" aria-label="Навигация">'
        f'<a href="../hot-summer-sale-2026.html">Hot Summer Sale 2026</a> '
        f'<span class="mirror-breadcrumb__sep" aria-hidden="true">›</span> '
        f"<span>{escape(name)}</span></nav>"
    )

    page = f"""<!DOCTYPE html>
<html class="dark" data-redesign="spatial-minimalism" lang="bg">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>{escape(name)} | Hot Summer Sale 2026 | Plasico.bg</title>
  <meta name="description" content="{escape(name)} — летни оферти от кампанията Hot Summer Sale 2026 в Plasico.bg"/>
  <link rel="shortcut icon" type="image/ico" href="https://static.plasico.bg/favicon.ico"/>
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block" rel="stylesheet"/>
  {tailwind}
  {style}
</head>
<body class="font-body-md selection:bg-apricot/30 custom-scrollbar" data-category-map="../category-map.json">
  {header}
  <main class="pt-[var(--site-header-offset)]">
    <div class="max-w-[1440px] mx-auto px-container-padding py-8 lg:py-12">
      {breadcrumb}
      {nav}
      <section id="catalog" class="py-stack-lg">
        <div class="mb-stack-lg">
          <h1 class="font-headline-lg font-bold flex items-center gap-4">
            <span class="w-12 h-[2px] bg-primary"></span>
            <span id="catalog-title">{escape(name)}</span>
          </h1>
          <p id="catalog-subtitle" class="text-on-surface-variant mt-2">{count} продукта с летни отстъпки — налични за поръчка.</p>
        </div>
        {catalog_filter_panel(show_os=show_os, show_upgraded=show_upgraded)}
        <div id="catalog-empty" class="hidden text-center py-16 px-6 squircle intelligent-edge bg-surface-container" role="status">
          <span class="material-symbols-outlined text-apricot text-[48px] mb-4" aria-hidden="true">inventory_2</span>
          <h3 id="catalog-empty-title" class="font-headline-md text-headline-md font-bold mb-3">Няма продукти по избраните филтри</h3>
          <p id="catalog-empty-text" class="text-on-surface-variant max-w-lg mx-auto mb-8">Опитайте да разширите филтрите.</p>
        </div>
        <div id="product-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter relative">
{cards}
        </div>
      </section>
    </div>
  </main>
  {footer}
  <button id="back-to-top" type="button" aria-label="Нагоре" title="Нагоре" class="fixed left-4 bottom-6 z-40 w-11 h-11 rounded-full bg-surface-container-high border border-edge-light text-on-surface shadow-lg flex items-center justify-center opacity-0 pointer-events-none translate-y-2 transition-opacity duration-300 hover:text-apricot hover:border-apricot hover:scale-105 focus:outline-none focus-visible:ring-2 focus-visible:ring-apricot">
    <span class="material-symbols-outlined text-[22px]" aria-hidden="true">keyboard_arrow_up</span>
  </button>
{catalog_scripts_html("../", category)}
  <script>
    (function initHeaderCategories() {{
      const toggle = document.getElementById('categories-toggle');
      const panel = document.getElementById('categories-panel');
      if (!toggle || !panel) return;
      toggle.addEventListener('click', () => {{
        const open = !panel.classList.contains('is-open');
        panel.classList.toggle('is-open', open);
        panel.setAttribute('aria-hidden', open ? 'false' : 'true');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      }});
    }})();
    (function initBackToTop() {{
      const btn = document.getElementById('back-to-top');
      if (!btn) return;
      const toggle = () => {{
        const visible = window.scrollY > 400;
        btn.classList.toggle('opacity-0', !visible);
        btn.classList.toggle('pointer-events-none', !visible);
        btn.classList.toggle('translate-y-2', !visible);
      }};
      window.addEventListener('scroll', toggle, {{ passive: true }});
      toggle();
      btn.addEventListener('click', () => window.scrollTo({{ top: 0, behavior: 'smooth' }}));
    }})();
  </script>
</body>
</html>
"""
    return page


def main() -> None:
    if not TEMPLATE.exists():
        raise SystemExit(f"Template not found: {TEMPLATE}")
    template_html = TEMPLATE.read_text(encoding="utf-8")
    products_map = load_json(PRODUCTS_MAP)
    category_map = load_json(CATEGORY_MAP)
    categories = category_map.get("categories", [])
    by_id = {c["id"]: c for c in categories}

    all_products = products_map.get("products", [])
    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)

    for slug in CAMPAIGN_SLUGS:
        cat = next((c for c in categories if c.get("slug") == slug), None)
        if not cat:
            print(f"skip {slug}: no category in map")
            continue
        cat_products = [p for p in all_products if p.get("categoryId") == cat["id"]]
        if not cat_products:
            print(f"skip {slug}: 0 products")
            continue
        html = build_page(cat, cat_products, template_html, categories)
        out = CAMPAIGN_DIR / f"{slug}.html"
        out.write_text(html, encoding="utf-8")
        print(f"  {slug}.html — {len(cat_products)} products")

    print("Done.")


if __name__ == "__main__":
    main()
