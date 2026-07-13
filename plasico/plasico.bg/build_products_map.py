#!/usr/bin/env python3
"""Build products-map.json from HTTrack mirror HTML and update category-map counts."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from html import unescape
from pathlib import Path

DIR = Path(__file__).parent
CATEGORY_MAP_FILE = DIR / "category-map.json"
PRODUCTS_MAP_FILE = DIR / "products-map.json"
BACKUP_SUFFIX = ".mirror-backup"

# Mirror campaign subpage slug -> category id
CAMPAIGN_SLUG_TO_ID = {
    "computers": "computers",
    "components": "components",
    "monitors": "monitors",
    "used": "used",
    "office-chairs": "office-chairs",
    "gchairs": "gchairs",
    "audio": "audio",
    "bags": "bags",
    "flash": "flash",
    "external": "external",
    "printers": "printers",
    "accessories": "accessories",
    "cctv": "cctv",
    "network": "network",
    "hubs": "hubs",
    "cables": "cables",
    "ups": "ups",
}

MAIN_SOURCES = [
    DIR / "hot-summer-sale-2026.original.html",
    DIR / "hot-summer-sale-2026.html",
]


def parse_euro_price(text: str) -> float | None:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    m = re.search(r"([\d]+)\.([\d]{2})", text)
    if not m:
        return None
    return float(f"{m.group(1)}.{m.group(2)}")


def calc_discount(old: float | None, new: float | None) -> int:
    if not old or not new or old <= 0 or new >= old:
        return 0
    return round((old - new) / old * 100)


def infer_os(title: str, specs: list[str]) -> str:
    sys.path.insert(0, str(DIR))
    from detect_os import detect_os

    return detect_os("\n".join(specs), title)


def infer_laptop_tags(title: str) -> list[str]:
    tags = ["laptopi"]
    t = title.upper()
    gaming_keys = (
        "GAMING", "TUF", "ROG ", "LEGION", "NITRO", "PREDATOR", "OMEN",
        "ALIENWARE", " RTX ", "GEFORCE", "KATANA", "CROSSHAIR", "STEALTH",
        "RAIDER", "VECTOR",
    )
    business_keys = (
        "ELITEBOOK", "PROBOOK", "THINKPAD", "LATITUDE", "VOSTRO", "EXPERTBOOK",
        "BUSINESS", " HP 250", " HP 255", "LENOVO V15", "LENOVO V14",
        "VIVOBOOK 15", "VIVOBOOK 17", "IDEAPAD 1", "IDEAPAD 3", "M1502", "X1502",
    )
    ultrabook_keys = ("ULTRABOOK", "ZENBOOK", "SWIFT", "XPS 13", "GRAM", "ENVY 13", "SPECTRE", "MACBOOK AIR")
    if any(k in t for k in gaming_keys):
        tags.append("gaming")
    if any(k in t for k in business_keys):
        tags.append("business")
    if any(k in t for k in ultrabook_keys):
        tags.append("ultrabook")
    return list(dict.fromkeys(tags))


def parse_mirror_product(article_html: str, pid: str) -> dict | None:
    body = article_html
    link_m = re.search(r'<a class="mainlink" href="([^"]+)"[^>]*(?:title="([^"]*)")?', body)
    if not link_m:
        return None
    url = link_m.group(1)
    title = unescape(link_m.group(2) or "").strip(" -")
    if not title:
        ttl_m = re.search(r'<span class="ttl"[^>]*>([^<]+)</span>', body)
        title = unescape(ttl_m.group(1)).strip() if ttl_m else ""

    img_m = re.search(r'<img[^>]+src="([^"]+)"', body)
    image = img_m.group(1) if img_m else ""

    is_promocode = "with-promocode" in body or "promocode_price" in body
    old_price = None
    price = None

    if is_promocode:
        inshop_m = re.search(
            r'price-inshop[^<]*</span><span class="price">([^<]+(?:<[^>]+>[^<]*)*)',
            body,
        )
        promo_m = re.search(r'class="codeprice">([^<]+(?:<[^>]+>[^<]*)*)', body)
        inshop = parse_euro_price(inshop_m.group(1)) if inshop_m else None
        promo = parse_euro_price(promo_m.group(1)) if promo_m else None
        if inshop and promo:
            old_price, price = inshop, promo
        elif inshop:
            old_price, price = inshop, round(inshop * 0.97, 2)
        elif promo:
            price = promo
    else:
        old_m = re.search(r'<span class="oldprice">(.*?)</span>', body, re.DOTALL)
        price_m = re.search(
            r'<span class="oldprice">.*?</span><span class="price">(.*?)</span>',
            body,
            re.DOTALL,
        )
        if not price_m:
            price_m = re.search(r'<span class="price">(.*?)</span>', body, re.DOTALL)
        if old_m:
            old_price = parse_euro_price(old_m.group(1))
        if price_m:
            price = parse_euro_price(price_m.group(1))

    specs_m = re.search(r'<ul class="specs-list">(.*?)</ul>', body, re.DOTALL)
    specs: list[str] = []
    if specs_m:
        specs = [unescape(s).strip() for s in re.findall(r"<li>(.*?)</li>", specs_m.group(1), re.DOTALL)]

    upgraded = title.upper().startswith("UPGRADED")
    discount = calc_discount(old_price, price)

    return {
        "id": pid,
        "title": title,
        "url": url,
        "image": image,
        "price": price,
        "oldPrice": old_price,
        "discount": discount,
        "upgraded": upgraded,
        "promocode": is_promocode,
        "os": infer_os(title, specs),
        "specs": specs,
    }


def parse_redesign_product(article_html: str) -> dict | None:
    pid_m = re.search(r'data-id="(\d+)"', article_html)
    if not pid_m:
        return None
    pid = pid_m.group(1)
    tags_m = re.search(r'data-tags="([^"]*)"', article_html)
    tags = (tags_m.group(1) if tags_m else "laptopi").split()
    os_m = re.search(r'data-os="([^"]*)"', article_html)
    price_m = re.search(r'data-price="([^"]*)"', article_html)
    disc_m = re.search(r'data-discount-percent="([^"]*)"', article_html)
    upgraded = 'data-upgraded="true"' in article_html

    url_m = re.search(r'<a href="([^"]+)" class="aspect-square', article_html)
    img_m = re.search(r'<img[^>]+alt="([^"]*)"[^>]+src="([^"]+)"', article_html)
    if not img_m:
        img_m = re.search(r'<img[^>]+src="([^"]+)"[^>]+alt="([^"]*)"', article_html)
    title_m = re.search(
        r'class="hover:text-apricot[^"]*"[^>]*>([^<]+)</a>',
        article_html,
    )
    old_m = re.search(r'line-through[^>]*>([\d.]+)\s*€', article_html)

    title = unescape(title_m.group(1)) if title_m else ""
    url = url_m.group(1) if url_m else ""
    image = img_m.group(2) if img_m and img_m.lastindex >= 2 else (img_m.group(1) if img_m else "")
    price = float(price_m.group(1)) if price_m else None
    old_price = float(old_m.group(1)) if old_m else None
    discount = int(disc_m.group(1)) if disc_m else calc_discount(old_price, price)

    specs = [
        unescape(s).strip()
        for s in re.findall(
            r'<li class="text-on-surface-variant text-body-sm">([^<]+)</li>',
            article_html,
        )
    ]

    return {
        "id": pid,
        "title": title.replace("…", "").strip(),
        "url": url,
        "image": image,
        "price": price,
        "oldPrice": old_price,
        "discount": discount,
        "upgraded": upgraded,
        "promocode": "ОНЛАЙН" in article_html or "text-violet" in article_html,
        "os": os_m.group(1) if os_m else infer_os(title, specs),
        "tags": tags,
        "specs": specs,
    }


def parse_page_products(html: str, source: str) -> list[tuple[str, dict]]:
    """Return list of (subcategory_anchor, product_dict)."""
    results: list[tuple[str, dict]] = []
    sections = list(re.finditer(r'<section id="([^"]+)" class="group">(.*?)</section>', html, re.DOTALL))
    if not sections:
        for block in re.finditer(
            r'<article\s+data-id="(\d+)"[^>]*class="product-box[^"]*">(.*?)</article>',
            html,
            re.DOTALL,
        ):
            prod = parse_mirror_product(block.group(2), block.group(1))
            if prod:
                results.append(("laptopi", prod))
        return results

    for section in sections:
        anchor = section.group(1)
        body = section.group(2)
        for block in re.finditer(
            r'<article\s+data-id="(\d+)"[^>]*class="product-box[^"]*">(.*?)</article>',
            body,
            re.DOTALL,
        ):
            prod = parse_mirror_product(block.group(2), block.group(1))
            if prod:
                results.append((anchor, prod))

    return results


def parse_main_redesign(html: str) -> list[tuple[str, dict]]:
    results: list[tuple[str, dict]] = []
    grid_m = re.search(r'<div id="product-grid"[^>]*>(.*?)</div>\s*</section>', html, re.DOTALL)
    if not grid_m:
        return results
    for block in re.finditer(r"<article[^>]*>.*?</article>", grid_m.group(1), re.DOTALL):
        prod = parse_redesign_product(block.group(0))
        if prod:
            results.append(("laptopi", prod))
    return results


def load_category_map() -> dict:
    return json.loads(CATEGORY_MAP_FILE.read_text(encoding="utf-8"))


def collect_all_products() -> list[dict]:
    products: list[dict] = []
    seen_ids: set[str] = set()

    # Main laptops page — prefer redesign HTML for tags/OS
    main_html = None
    for src in MAIN_SOURCES:
        if src.exists():
            main_html = src.read_text(encoding="utf-8")
            if "product-grid" in main_html and 'data-tags="' in main_html:
                for anchor, prod in parse_main_redesign(main_html):
                    if prod["id"] in seen_ids:
                        continue
                    seen_ids.add(prod["id"])
                    products.append({
                        **prod,
                        "categoryId": "laptopi",
                        "subcategoryAnchor": anchor,
                        "sourcePage": "hot-summer-sale-2026.html",
                        "tags": prod.get("tags") or infer_laptop_tags(prod["title"]),
                    })
                break
            elif "product-box" in main_html:
                for anchor, prod in parse_page_products(main_html, str(src)):
                    if prod["id"] in seen_ids:
                        continue
                    seen_ids.add(prod["id"])
                    products.append({
                        **prod,
                        "categoryId": "laptopi",
                        "subcategoryAnchor": anchor,
                        "sourcePage": "hot-summer-sale-2026.html",
                        "tags": infer_laptop_tags(prod["title"]),
                    })
                break

    # Campaign subpages from mirror backups
    campaign_dir = DIR / "hot-summer-sale-2026"
    for slug, cat_id in CAMPAIGN_SLUG_TO_ID.items():
        backup = campaign_dir / f"{slug}.html{BACKUP_SUFFIX}"
        if not backup.exists():
            backup = campaign_dir / f"{slug}.html"
        if not backup.exists():
            print(f"  skip {slug}: no mirror file", file=sys.stderr)
            continue
        html = backup.read_text(encoding="utf-8")
        page_products = parse_page_products(html, str(backup))
        for anchor, prod in page_products:
            if prod["id"] in seen_ids:
                continue
            seen_ids.add(prod["id"])
            tags = [cat_id, anchor]
            products.append({
                **prod,
                "categoryId": cat_id,
                "subcategoryAnchor": anchor,
                "sourcePage": f"hot-summer-sale-2026/{slug}.html",
                "tags": tags,
            })

    return products


def build_counts(products: list[dict]) -> dict:
    by_category: dict[str, dict] = {}
    for p in products:
        cat = p["categoryId"]
        sub = p["subcategoryAnchor"]
        if cat not in by_category:
            by_category[cat] = {"count": 0, "subcategories": {}, "filters": {}}
        by_category[cat]["count"] += 1
        by_category[cat]["subcategories"][sub] = by_category[cat]["subcategories"].get(sub, 0) + 1
        for tag in p.get("tags") or []:
            if tag in (cat, sub):
                continue
            by_category[cat]["filters"][tag] = by_category[cat]["filters"].get(tag, 0) + 1
    return by_category


def update_category_map_counts(category_map: dict, by_category: dict) -> dict:
    for cat in category_map.get("categories", []):
        cat_id = cat["id"]
        info = by_category.get(cat_id, {"count": 0, "subcategories": {}})
        cat["productCount"] = info.get("count", 0)
        for sub in cat.get("subcategories", []):
            anchor = sub.get("anchorId") or sub.get("anchor", "").lstrip("#")
            sub["productCount"] = info.get("subcategories", {}).get(anchor, 0)
            if sub["productCount"] > 0 and sub.get("action") == "local":
                sub["filterTag"] = anchor
    summary = category_map.setdefault("connections", {}).setdefault("summary", {})
    summary["totalProducts"] = sum(by_category.get(c["id"], {}).get("count", 0) for c in category_map.get("categories", []))
    summary["productsByCategory"] = {c["id"]: c.get("productCount", 0) for c in category_map.get("categories", [])}
    return category_map


def main() -> None:
    print("Collecting products from HTTrack mirror...")
    products = collect_all_products()
    by_category = build_counts(products)

    products_map = {
        "generatedAt": date.today().isoformat(),
        "source": "HTTrack mirror (*.mirror-backup + hot-summer-sale-2026.html)",
        "totalProducts": len(products),
        "byCategory": by_category,
        "products": products,
    }
    PRODUCTS_MAP_FILE.write_text(
        json.dumps(products_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {PRODUCTS_MAP_FILE.name}: {len(products)} products")

    category_map = load_category_map()
    category_map = update_category_map_counts(category_map, by_category)
    CATEGORY_MAP_FILE.write_text(
        json.dumps(category_map, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {CATEGORY_MAP_FILE.name}")

    print("\nProducts per category:")
    for cat in category_map.get("categories", []):
        n = cat.get("productCount", 0)
        print(f"  {cat['id']}: {n}")


if __name__ == "__main__":
    main()
