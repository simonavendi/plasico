#!/usr/bin/env python3
"""Generate local product detail pages and wire catalog links."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlparse

DIR = Path(__file__).parent
INDEX = DIR / "index.html"
PRODUCT_URL_MAP = DIR / "product-url-map.json"
REFERENCE_DIR = Path(r"C:/My Web Sites/plasico copy/plasico.bg")

sys.path.insert(0, str(DIR))
from build_products_map import collect_all_products  # noqa: E402

CATEGORY_META = {
    "laptopi": {
        "label": "Лаптопи",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026.html#laptopi",
    },
    "computers": {
        "label": "Компютри",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/computers.html",
    },
    "components": {
        "label": "Компоненти",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/components.html",
    },
    "monitors": {
        "label": "Монитори",
        "parent": "Монитори и проектори",
        "parent_href": "monitori-i-proektori.html",
        "listing_href": "hot-summer-sale-2026/monitors.html",
    },
    "used": {
        "label": "Втора употреба",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/used.html",
    },
    "office-chairs": {
        "label": "Офис столове",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/office-chairs.html",
    },
    "gchairs": {
        "label": "Геймърски столове",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/gchairs.html",
    },
    "audio": {
        "label": "Аудио",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/audio.html",
    },
    "bags": {
        "label": "Чанти",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/bags.html",
    },
    "flash": {
        "label": "USB флаш памет",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/flash.html",
    },
    "external": {
        "label": "Външни дискове",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/external.html",
    },
    "printers": {
        "label": "Принтери",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/printers.html",
    },
    "accessories": {
        "label": "Аксесоари",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/accessories.html",
    },
    "cctv": {
        "label": "Видеонаблюдение",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/cctv.html",
    },
    "network": {
        "label": "Мрежово оборудване",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/network.html",
    },
    "hubs": {
        "label": "Hub-ове",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/hubs.html",
    },
    "cables": {
        "label": "Кабели",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/cables.html",
    },
    "ups": {
        "label": "UPS",
        "parent": "Разпродажба",
        "parent_href": "hot-summer-sale-2026.html",
        "listing_href": "hot-summer-sale-2026/ups.html",
    },
}

LINK_UPDATE_GLOBS = [
    "hot-summer-sale-2026.html",
    "index.html",
    "poruchka.html",
    "hot-summer-sale-2026/*.html",
]


def slugify_title(title: str) -> str:
    text = title.lower()
    repl = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ж": "zh", "з": "z",
        "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p",
        "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch",
        "ш": "sh", "щ": "sht", "ъ": "a", "ь": "y", "ю": "yu", "я": "ya",
    }
    out = []
    for ch in text:
        if ch in repl:
            out.append(repl[ch])
        elif re.match(r"[a-z0-9]", ch):
            out.append(ch)
        elif ch in " -_/|,":
            out.append("-")
    slug = re.sub(r"-+", "-", "".join(out)).strip("-")
    return slug[:120].strip("-") or "product"


def product_filename(prod: dict) -> str:
    url = prod.get("url") or ""
    if url:
        name = urlparse(url).path.rstrip("/").split("/")[-1]
        if name.endswith(".html") and len(name) <= 100:
            return name
    slug = slugify_title(prod.get("title") or "product")
    if len(slug) > 55:
        slug = slug[:55].rstrip("-")
    return f"{slug}-{prod['id']}.html"


def extract_between(text: str, start: str, end: str) -> str:
    i = text.find(start)
    if i < 0:
        return ""
    j = text.find(end, i + len(start))
    if j < 0:
        return ""
    return text[i:j + len(end)]


def load_shell() -> dict[str, str]:
    index_html = INDEX.read_text(encoding="utf-8")
    head = extract_between(index_html, "<!DOCTYPE html>", "</head>")
    if head:
        head = "<!DOCTYPE html>" + head + "</head>"
        head = head.replace('href="home.css"', 'href="product-page.css"')
        head = re.sub(r"<title>.*?</title>", "<title>{{TITLE}}</title>", head, count=1, flags=re.S)
        head = re.sub(
            r'<meta name="description" content="[^"]*"',
            '<meta name="description" content="{{DESCRIPTION}}"',
            head,
            count=1,
        )
    header = extract_between(index_html, '<header id="site-header"', "</header>")
    if header:
        header = '<header id="site-header"' + header
    footer_start = index_html.find("<footer class=")
    footer_end = index_html.find("</html>")
    footer_tail = index_html[footer_start:footer_end] if footer_start >= 0 else ""
    footer_tail = footer_tail.replace('src="home.js" defer', 'src="product-page.js"')
    footer_tail = re.sub(r'<script src="product-card-actions.js"></script>\s*', "", footer_tail)
    if 'src="product-page.js"' not in footer_tail:
        footer_tail = footer_tail.replace(
            '<script src="auth-modal.js"></script>',
            '<script src="auth-modal.js"></script>\n<script src="product-page.js"></script>',
        )
    body_open = '<body class="font-body-md selection:bg-apricot/30 custom-scrollbar product-page-body" data-category-map="category-map.json">'
    return {"head": head, "header": header, "footer_tail": footer_tail, "body_open": body_open}


def parse_reference_gallery(prod_id: str) -> list[str]:
    if not REFERENCE_DIR.exists():
        return []
    for path in REFERENCE_DIR.glob(f"*-{prod_id}.html"):
        html = path.read_text(encoding="utf-8", errors="ignore")
        imgs = re.findall(r'data-big="([^"]+)"', html)
        cleaned: list[str] = []
        for src in imgs:
            src = re.sub(r"\.\./external\.html\?link=", "", src)
            if src.startswith("http") and src not in cleaned:
                cleaned.append(src)
        if cleaned:
            return cleaned
    return []


def gallery_images(prod: dict) -> list[str]:
    images: list[str] = []
    ref = parse_reference_gallery(prod["id"])
    if ref:
        images.extend(ref)
    main = prod.get("image") or ""
    if main and main not in images:
        images.insert(0, main)
    return images[:12] if images else [""]


def render_gallery(prod: dict) -> str:
    images = [img for img in gallery_images(prod) if img]
    if not images:
        images = ["https://static.plasico.bg/images/transp.png"]
    main = escape(images[0], quote=True)
    alt = escape(prod.get("title") or "", quote=True)
    thumbs = []
    for idx, src in enumerate(images):
        esc = escape(src, quote=True)
        active = " is-active" if idx == 0 else ""
        thumbs.append(
            f'<button type="button" class="product-gallery__thumb{active}" data-gallery-thumb data-gallery-src="{esc}" aria-label="Снимка {idx + 1}">'
            f'<img src="{esc}" alt="" loading="lazy" width="56" height="56"/></button>'
        )
    return f"""
<div class="product-card product-gallery">
  <div class="product-gallery__main">
    <img src="{main}" alt="{alt}" data-gallery-main loading="eager" width="800" height="600"/>
  </div>
  <div class="product-gallery__thumbs">{''.join(thumbs)}</div>
</div>"""


def render_energy_badge(cls: str) -> str:
    letter = (cls or "").strip().upper()[:1]
    if letter not in "ABCDEFG":
        return ""
    return (
        f'<span class="product-energy" title="Енергиен клас {letter}" '
        f'aria-label="Енергиен клас {letter}">'
        f'<span class="product-energy__label">Енергиен клас</span>'
        f'<span class="product-energy__class product-energy__class--{letter.lower()}">{letter}</span>'
        f"</span>"
    )


def render_badges(prod: dict) -> str:
    parts = []
    discount = int(prod.get("discount") or 0)
    if discount > 0:
        parts.append(f'<span class="product-badge product-badge--promo">-{discount}%</span>')
    if prod.get("upgraded"):
        parts.append('<span class="product-badge product-badge--upgraded">Upgraded</span>')
    energy = prod.get("energyClass")
    if energy:
        badge = render_energy_badge(str(energy))
        if badge:
            parts.append(badge)
    if not parts:
        return ""
    return f'<div class="product-badge-row">{"".join(parts)}</div>'


def render_price(prod: dict) -> str:
    price = prod.get("price")
    old = prod.get("oldPrice")
    if price is None:
        return '<div class="product-price">—</div>'
    html = f'<div class="product-price">{price:.2f} €</div>'
    if old and old > price:
        html += f'<div class="product-price-old">{old:.2f} €</div>'
    return html


def render_specs(prod: dict) -> str:
    specs = prod.get("specs") or []
    if not specs:
        return ""
    items = "".join(f"<li>{escape(s)}</li>" for s in specs)
    art = escape(prod["id"])
    items += f"<li>Арт. №: {art}</li>"
    return f"""
<section class="product-card product-specs">
  <h2 class="product-specs__title">Характеристики</h2>
  <ul class="product-specs__list">{items}</ul>
</section>"""


def render_similar(current: dict, products: list[dict], url_map: dict[str, str]) -> str:
    cat = current.get("categoryId")
    similar = [
        p for p in products
        if p.get("categoryId") == cat and p["id"] != current["id"]
    ][:8]
    if not similar:
        return ""
    meta = CATEGORY_META.get(cat or "", {})
    listing = meta.get("listing_href", "hot-summer-sale-2026.html")
    cards = []
    for p in similar:
        fname = url_map[p["id"]]
        href = escape(fname, quote=True)
        title = escape(p.get("title") or "")
        short = escape((p.get("title") or "")[:70])
        img = escape(p.get("image") or "", quote=True)
        price = p.get("price")
        price_txt = f"{price:.2f} €" if price is not None else "—"
        cards.append(
            f"""<div class="product-similar-card">
  <a href="{href}" class="product-similar-card__media" tabindex="-1" aria-hidden="true">
    <img class="product-similar-card__img" src="{img}" alt="" loading="lazy" width="56" height="56"/>
  </a>
  <div>
    <a href="{href}" class="product-similar-card__name">{short}</a>
    <div class="product-similar-card__price">{price_txt}</div>
  </div>
  <button type="button" class="product-similar-card__add" data-similar-add
    data-similar-id="{escape(p['id'], quote=True)}"
    data-similar-title="{title}"
    data-similar-price="{price or 0}"
    data-similar-image="{img}"
    data-similar-href="{href}"
    aria-label="Добави в количка" title="Добави в количка">
    <span class="material-symbols-outlined" aria-hidden="true">add_circle</span>
  </button>
</div>"""
        )
    return f"""
<section class="product-similar">
  <h2 class="product-similar__title"><a href="{escape(listing, quote=True)}">Още подобни {escape(meta.get('label', 'продукти'))}</a></h2>
  <div class="product-similar__grid">{''.join(cards)}</div>
</section>"""


def render_main(prod: dict, products: list[dict], url_map: dict[str, str]) -> str:
    cat = prod.get("categoryId") or "laptopi"
    meta = CATEGORY_META.get(cat, CATEGORY_META["laptopi"])
    title = prod.get("title") or "Продукт"
    title_esc = escape(title)
    short_crumb = escape(title if len(title) <= 60 else title[:57] + "…")
    price = prod.get("price")
    data_price = f'{price:.2f}' if price is not None else "0"
    image = escape(prod.get("image") or "", quote=True)
    fname = url_map[prod["id"]]

    return f"""
<main class="pt-[var(--site-header-offset)]">
  <div class="product-page" data-product-page
    data-product-id="{escape(prod['id'], quote=True)}"
    data-product-title="{escape(title, quote=True)}"
    data-product-price="{data_price}"
    data-product-image="{image}">
    <nav class="product-breadcrumb" aria-label="Навигация">
      <a href="index.html">Plasico</a>
      <span class="product-breadcrumb__sep" aria-hidden="true">›</span>
      <a href="{escape(meta['parent_href'], quote=True)}">{escape(meta['parent'])}</a>
      <span class="product-breadcrumb__sep" aria-hidden="true">›</span>
      <a href="{escape(meta['listing_href'], quote=True)}">{escape(meta['label'])}</a>
      <span class="product-breadcrumb__sep" aria-hidden="true">›</span>
      <span class="product-breadcrumb__current">{short_crumb}</span>
    </nav>
    <div class="product-layout">
      {render_gallery(prod)}
      <aside class="product-card product-buybox">
        <h1 class="product-buybox__title">{title_esc}</h1>
        <div class="product-buybox__meta">
          <span>Арт.№: {escape(prod['id'])}</span>
          <div class="product-buybox__actions">
            <button type="button" class="product-icon-btn product-icon-btn--compare" data-product-compare title="Сравни">
              <span class="material-symbols-outlined" aria-hidden="true">swap_vert</span> Сравни
            </button>
            <button type="button" class="product-icon-btn" data-product-fav title="Добави в любими">
              <span class="material-symbols-outlined" aria-hidden="true">favorite</span> Любими
            </button>
          </div>
        </div>
        {render_badges(prod)}
        <div class="product-price-block">{render_price(prod)}</div>
        <div class="product-buy-row">
          <div class="product-qty" role="group" aria-label="Количество">
            <button type="button" class="product-qty__btn" data-qty-delta="-1" aria-label="Намали">−</button>
            <span class="product-qty__value" data-qty-value>1</span>
            <button type="button" class="product-qty__btn" data-qty-delta="1" aria-label="Увеличи">+</button>
          </div>
          <button type="button" class="product-buy-btn" data-product-buy>
            <span class="material-symbols-outlined" aria-hidden="true">shopping_cart</span>
            Купи
          </button>
        </div>
        <div class="product-availability">
          <div class="product-availability__in">
            <span class="material-symbols-outlined" aria-hidden="true" style="font-size:18px">check_circle</span>
            Наличен — поръчай онлайн или в магазин
          </div>
          <p class="product-availability__ship">Доставка от 2.59 € · BOX NOW безплатно</p>
        </div>
        <div class="product-contact-row">
          <a href="tel:070020810">0700 20 810</a>
          <a href="kontakti.html">Направи запитване ›</a>
        </div>
        <div class="product-installment">
          <img src="https://static.plasico.bg/images/bnp_button_new.webp" alt="На изплащане с PostBank" loading="lazy" width="155" height="52"/>
          <img src="https://static.plasico.bg/images/bnp_button_card.webp" alt="PostBank карта" loading="lazy" width="154" height="52"/>
        </div>
        <div class="product-side-panels">
          <button type="button" class="product-fast-trigger" data-open-fast-order>
            Бърза поръчка
          </button>
        </div>
      </aside>
    </div>
    {render_specs(prod)}
    {render_similar(prod, products, url_map)}
  </div>
</main>"""


def render_page(prod: dict, products: list[dict], url_map: dict[str, str], shell: dict[str, str]) -> str:
    title = prod.get("title") or "Продукт"
    page_title = escape(f"{title} • {prod['id']} | Plasico.bg")
    desc = escape(f"{title} — поръчай онлайн или на ☎ 0700 20 810")
    head = shell["head"].replace("{{TITLE}}", page_title).replace("{{DESCRIPTION}}", desc)
    main = render_main(prod, products, url_map)
    return "\n".join([head, shell["body_open"], shell["header"], main, shell["footer_tail"], "</html>\n"])


def update_links(url_map: dict[str, str]) -> int:
    changed_files = 0
    for pattern in LINK_UPDATE_GLOBS:
        for path in DIR.glob(pattern):
            if not path.is_file() or path.suffix != ".html":
                continue
            if path.name.startswith("_"):
                continue
            text = path.read_text(encoding="utf-8")
            original = text
            for pid, local_name in url_map.items():
                rel_prefix = "../" if "hot-summer-sale-2026" in str(path.parent.name) else ""
                local_href = f"{rel_prefix}{local_name}"
                text = re.sub(
                    rf'https://plasico\.bg/[^"\']*-{re.escape(pid)}\.html',
                    local_href,
                    text,
                )
                text = re.sub(
                    rf'href="[^"]*-{re.escape(pid)}\.html"',
                    f'href="{local_href}"',
                    text,
                )
            if text != original:
                path.write_text(text, encoding="utf-8")
                changed_files += 1
                print(f"  updated links in {path.relative_to(DIR)}")
    return changed_files


def main() -> None:
    if not INDEX.exists():
        print("index.html missing", file=sys.stderr)
        sys.exit(1)

    print("Collecting products...")
    products = collect_all_products()
    if not products:
        print("No products found", file=sys.stderr)
        sys.exit(1)

    url_map = {p["id"]: product_filename(p) for p in products}
    shell = load_shell()

    print(f"Generating {len(products)} product pages...")
    for prod in products:
        fname = url_map[prod["id"]]
        out = DIR / fname
        out.write_text(render_page(prod, products, url_map, shell), encoding="utf-8")

    PRODUCT_URL_MAP.write_text(
        json.dumps(
            {
                "generatedAt": date.today().isoformat(),
                "count": len(url_map),
                "byId": url_map,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("Updating catalog links...")
    updated = update_links(url_map)

    print(f"\nDone: {len(products)} pages, {updated} catalog files updated")
    print(f"URL map: {PRODUCT_URL_MAP.name}")


if __name__ == "__main__":
    main()
