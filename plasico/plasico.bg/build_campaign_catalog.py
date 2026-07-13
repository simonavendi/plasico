#!/usr/bin/env python3
"""Build campaign subpages with hero, category grid, and per-category product catalog."""

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
LINK_MAP = DIR / "link-map.json"
CAMPAIGN_DIR = DIR / "hot-summer-sale-2026"

sys.path.insert(0, str(DIR))
from scrape_live_campaign import render_product  # noqa: E402


def _template_helpers():
    from apply_template import (  # noqa: E402
        CONTENT_PAGE_SCRIPTS,
        adapt_shell_part,
        build_campaign_hero,
        extract_shell,
        load_json,
    )
    return CONTENT_PAGE_SCRIPTS, adapt_shell_part, build_campaign_hero, extract_shell, load_json


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

CAMPAIGN_SLUGS = [
    "computers", "components", "monitors", "used", "office-chairs", "gchairs",
    "audio", "bags", "flash", "external", "printers", "accessories",
    "cctv", "network", "hubs", "cables", "ups",
]

PAGE_PATH = "hot-summer-sale-2026/{slug}.html"
PREFIX = "../"


def extract_section(html: str, pattern: str, label: str) -> str:
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        raise SystemExit(f"Could not extract {label} from hot-summer-sale-2026.html")
    return match.group(1)


def extract_categories_section(html: str) -> str:
    return extract_section(
        html,
        r'(<section class="py-stack-lg px-container-padding max-w-\[1440px\] mx-auto">[\s\S]*?'
        r'id="category-icon-grid"[\s\S]*?</section>)',
        "categories section",
    )


def extract_newsletter_section(html: str) -> str:
    return extract_section(
        html,
        r'(<section class="py-\[120px\] px-container-padding relative overflow-hidden">[\s\S]*?'
        r'Абонирай се за офертите[\s\S]*?</section>)',
        "newsletter section",
    )


def fix_subpage_cta_links(block: str) -> str:
    block = block.replace('href="#laptopi"', 'href="#catalog"')
    block = block.replace('href="../hot-summer-sale-2026.html#laptopi"', 'href="#catalog"')
    return block


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
        parts.append("\n\n".join(render_product(product_to_render_dict(p)) for p in items))
    return "\n\n".join(parts)


def catalog_scripts_html(prefix: str, category: dict) -> str:
    config = json.dumps(catalog_page_config(category), ensure_ascii=False)
    return f"""  <script>
    window.CATALOG_PAGE = {config};
  </script>
  <script src="{prefix}catalog-filters.js"></script>
  <script src="{prefix}campaign-category-nav.js"></script>"""


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


def customize_catalog_head(head: str, title: str, description: str) -> str:
    head = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", head, flags=re.DOTALL)
    head = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{escape(description)}"',
        head,
    )
    if 'data-redesign="spatial-minimalism"' not in head:
        head = head.replace('class="dark"', 'class="dark" data-redesign="spatial-minimalism"')
    return head


def build_page(
    category: dict,
    products: list[dict],
    template_html: str,
    shell: dict,
    link_map: dict,
    *,
    categories_section: str,
    newsletter_section: str,
) -> str:
    slug = category["slug"]
    name = category["name"]
    cat_id = category["id"]
    count = len(products)
    page_path = PAGE_PATH.format(slug=slug)
    CONTENT_PAGE_SCRIPTS, adapt_shell_part, build_campaign_hero, _, _ = _template_helpers()

    title = f"{name} | Hot Summer Sale 2026 | Plasico.bg"
    description = f"{name} — летни оферти от кампанията Hot Summer Sale 2026 в Plasico.bg"

    head = customize_catalog_head(
        adapt_shell_part(shell["head"], link_map, page_path),
        title,
        description,
    )
    header = adapt_shell_part(shell["header"], link_map, page_path)
    footer = adapt_shell_part(shell["footer"], link_map, page_path)
    back_btn = shell["back_to_top"]

    hero = fix_subpage_cta_links(
        build_campaign_hero(template_html, link_map, page_path),
    )
    _, adapt_shell_part, _, _, _ = _template_helpers()
    categories = fix_subpage_cta_links(
        adapt_shell_part(categories_section, link_map, page_path),
    )
    newsletter = adapt_shell_part(newsletter_section, link_map, page_path)

    show_os = cat_id in ("laptopi", "computers", "used")
    show_upgraded = cat_id in ("laptopi", "computers", "used")
    cards = render_product_grid(products, category)
    page_config = json.dumps(catalog_page_config(category), ensure_ascii=False)

    catalog = f"""
    <section id="catalog" class="py-stack-lg px-container-padding max-w-[1440px] mx-auto">
      <div class="mb-stack-lg">
        <h2 class="font-headline-lg font-bold flex items-center gap-4">
          <span class="w-12 h-[2px] bg-primary"></span>
          <span id="catalog-title">{escape(name)}</span>
        </h2>
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
    </section>"""

    main = f"""
  <main class="pt-[var(--site-header-offset)]">
{hero}
{categories}
{catalog}
{newsletter}
  </main>"""

    scripts = f"""  <script>
    window.CATALOG_PAGE = {page_config};
  </script>
  <script src="{PREFIX}catalog-filters.js"></script>
  <script src="{PREFIX}campaign-category-nav.js"></script>
{CONTENT_PAGE_SCRIPTS}"""

    return "\n".join([
        head,
        f'<body class="font-body-md selection:bg-apricot/30 custom-scrollbar" data-category-map="{PREFIX}category-map.json">',
        header,
        main,
        footer,
        back_btn,
        scripts,
        "</body>",
        "</html>",
    ])


def main() -> None:
    if not TEMPLATE.exists():
        raise SystemExit(f"Template not found: {TEMPLATE}")

    _, _, _, extract_shell, load_json_fn = _template_helpers()
    template_html = TEMPLATE.read_text(encoding="utf-8")
    products_map = load_json_fn(PRODUCTS_MAP)
    category_map = load_json_fn(CATEGORY_MAP)
    link_map = load_json_fn(LINK_MAP)
    shell = extract_shell(template_html)
    categories_section = extract_categories_section(template_html)
    newsletter_section = extract_newsletter_section(template_html)

    categories = category_map.get("categories", [])
    all_products = products_map.get("products", [])
    CAMPAIGN_DIR.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    for slug in CAMPAIGN_SLUGS:
        cat = next((c for c in categories if c.get("slug") == slug), None)
        if not cat:
            print(f"skip {slug}: no category in map")
            continue
        cat_products = [p for p in all_products if p.get("categoryId") == cat["id"]]
        if not cat_products:
            print(f"skip {slug}: 0 products")
            continue
        html = build_page(
            cat,
            cat_products,
            template_html,
            shell,
            link_map,
            categories_section=categories_section,
            newsletter_section=newsletter_section,
        )
        out = CAMPAIGN_DIR / f"{slug}.html"
        out.write_text(html, encoding="utf-8")
        counts[slug] = len(cat_products)
        print(f"  {slug}.html — {len(cat_products)} products")

    stray = CAMPAIGN_DIR / "components,.html"
    if stray.exists():
        stray.unlink()
        print("  removed components,.html (typo)")

    print(f"\nDone. Rebuilt {len(counts)} subpages.")
    print("Product counts:")
    for slug, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {slug}: {n}")


if __name__ == "__main__":
    main()
