#!/usr/bin/env python3
"""Fetch live Hot Summer Sale 2026 data and update local redesign files."""

from __future__ import annotations

import json
import re
import urllib.request
from datetime import date
from html import unescape
from pathlib import Path

BASE = "https://plasico.bg/hot-summer-sale-2026"
DIR = Path(__file__).parent
LIVE_MAIN = DIR / "live-main.html"
CATEGORY_MAP = DIR / "category-map.json"
REDESIGN = DIR / "hot-summer-sale-2026.html"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

ICON_MAP = {
    "icon-laptops": ("laptopi", "laptop", "laptops", True),
    "icon-pc": ("computers", "desktop_windows", "pc", False),
    "icon-components": ("components", "memory", "components", False),
    "icon-monitors": ("monitors", "monitor", "monitors", False),
    "icon-second": ("used", "devices", "second", False),
    "icon-ochairs": ("office-chairs", "chair", "ochairs", False),
    "icon-gchairs": ("gchairs", "sports_esports", "gchairs", False),
    "icon-audio": ("audio", "headphones", "audio", False),
    "icon-bags": ("bags", "backpack", "bags", False),
    "icon-flash": ("flash", "sd_card", "flash", False),
    "icon-external": ("external", "hard_drive", "external", False),
    "icon-printers": ("printers", "print", "printers", False),
    "icon-accs": ("accessories", "gamepad", "accs", False),
    "icon-cctv": ("cctv", "videocam", "cctv", False),
    "icon-network": ("network", "wifi", "network", False),
    "icon-hubs": ("hubs", "usb", "hubs", False),
    "icon-cable": ("cables", "cable", "cable", False),
    "icon-ups": ("ups", "battery_alert", "ups", False),
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_euro_price(text: str) -> float | None:
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ").replace("&nbsp;", " ")
    m = re.search(r"([\d]+)\.([\d]{2})", text)
    if not m:
        return None
    return float(f"{m.group(1)}.{m.group(2)}")


def calc_discount(old: float, new: float) -> int:
    if old <= 0 or new >= old:
        return 0
    return round((old - new) / old * 100)


def slug_from_href(href: str) -> str:
    href = href.strip("/")
    if href == "hot-summer-sale-2026":
        return ""
    prefix = "hot-summer-sale-2026/"
    if href.startswith(prefix):
        return href[len(prefix) :]
    if href.startswith("/hot-summer-sale-2026/"):
        return href.split("/hot-summer-sale-2026/", 1)[1].split("#")[0]
    return href.split("/")[-1].split("#")[0]


def anchor_from_href(href: str) -> tuple[str, str]:
    if "#" in href:
        anchor_id = href.split("#", 1)[1]
        return f"#{anchor_id}", anchor_id
    return "", ""


def split_top_level_lis(ul_html: str) -> list[str]:
    items: list[str] = []
    depth = 0
    current: list[str] = []
    i = 0
    while i < len(ul_html):
        if ul_html[i : i + 3] == "<li":
            if depth == 0:
                if current:
                    items.append("".join(current))
                current = ["<li"]
            else:
                current.append("<li")
            depth += 1
            i += 3
            continue
        if ul_html[i : i + 5] == "</li>":
            current.append("</li>")
            depth -= 1
            if depth == 0:
                items.append("".join(current))
                current = []
            i += 5
            continue
        if depth > 0:
            current.append(ul_html[i])
        i += 1
    return items


def parse_nav(html: str) -> list[dict]:
    start = html.find("js-sticky-header-campaign")
    if start < 0:
        raise RuntimeError("Sticky nav not found in live HTML")
    nav_start = html.find("<nav><ul>", start)
    if nav_start < 0:
        raise RuntimeError("Desktop nav ul not found in live HTML")
    ul_start = nav_start + len("<nav><ul>")
    ul_end = html.find("</ul>", ul_start)
    nav_ul = html[ul_start:ul_end]

    categories: list[dict] = []
    for item in split_top_level_lis(nav_ul):
        parent_m = re.search(
            r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*">.*?<span class="icon\s+([^"]+)">.*?</span><span>([^<]+)</span>',
            item,
            re.DOTALL,
        )
        if not parent_m:
            parent_m = re.search(
                r'<a[^>]*href="([^"]+)"[^>]*>.*?<span class="icon\s+([^"]+)">.*?</span><span>([^<]+)</span>',
                item,
                re.DOTALL,
            )
        if not parent_m:
            continue

        href, icon_class, name = parent_m.group(1), parent_m.group(2), parent_m.group(3).strip()
        slug = slug_from_href(href)
        cat_id, material_icon, icon_key, is_local = ICON_MAP.get(
            icon_class, (slug or "laptopi", "category", icon_class.replace("icon-", ""), False)
        )
        if slug == "":
            cat_id = "laptopi"
            is_local = True

        url = BASE if slug == "" else f"{BASE}/{slug}"
        subs: list[dict] = []
        for block in re.findall(r'<div class="submenu-children">(.*?)</div>', item, re.DOTALL):
            for sub_href, sub_name in re.findall(
                r'<a[^>]*href="([^"]+)"[^>]*>.*?<span>([^<]+)</span>',
                block,
                re.DOTALL,
            ):
                sub_name = sub_name.strip()
                anchor, anchor_id = anchor_from_href(sub_href)
                if sub_href.startswith("http"):
                    sub_url = sub_href
                elif sub_href.startswith("/"):
                    sub_url = f"https://plasico.bg{sub_href}"
                else:
                    sub_url = f"https://plasico.bg/{sub_href}"

                action = "scroll" if is_local and anchor else "external"
                filter_tag = "laptopi" if is_local and anchor_id == "laptopi" else None
                subs.append(
                    {
                        "name": sub_name,
                        "anchor": anchor,
                        "anchorId": anchor_id,
                        "url": sub_url,
                        "action": action,
                        "filterTag": filter_tag,
                    }
                )

        categories.append(
            {
                "id": cat_id,
                "name": name,
                "slug": slug,
                "url": url,
                "icon": icon_key,
                "materialIcon": material_icon,
                "dataFilter": "all" if is_local else cat_id,
                "local": is_local,
                "external": not is_local,
                "subcategories": subs,
            }
        )
    return categories


def load_existing_tags() -> dict[str, str]:
    if not REDESIGN.exists():
        return {}
    html = REDESIGN.read_text(encoding="utf-8")
    tags: dict[str, str] = {}
    for m in re.finditer(r'<article[^>]*data-id="(\d+)"[^>]*data-tags="([^"]*)"', html):
        tags[m.group(1)] = m.group(2)
    return tags


def merge_tags(product_id: str, inferred: list[str], existing_tags: dict[str, str]) -> list[str]:
    preserved = (existing_tags.get(product_id) or "").split()
    merged = list(dict.fromkeys([*inferred, *preserved]))
    return [t for t in merged if t != "upgraded"]


def infer_os(title: str, specs: list[str]) -> str:
    from detect_os import detect_os

    block = "\n".join(specs)
    return detect_os(block, title)


def infer_tags(title: str) -> list[str]:
    tags = ["laptopi"]
    t = title.upper()
    if any(
        k in t
        for k in (
            "GAMING",
            "TUF",
            "ROG ",
            "LEGION",
            "NITRO",
            "PREDATOR",
            "OMEN",
            "ALIENWARE",
            " RTX ",
            "GEFORCE",
            "KATANA",
            "CROSSHAIR",
            "STEALTH",
            "RAIDER",
            "VECTOR",
        )
    ):
        tags.append("gaming")
    if any(
        k in t
        for k in (
            "ELITEBOOK",
            "PROBOOK",
            "THINKPAD",
            "LATITUDE",
            "VOSTRO",
            "EXPERTBOOK",
            "BUSINESS",
            " HP 250",
            " HP 255",
            "LENOVO V15",
            "LENOVO V14",
            "VIVOBOOK 15",
            "VIVOBOOK 17",
            "IDEAPAD 1",
            "IDEAPAD 3",
            "M1502",
            "X1502",
        )
    ):
        tags.append("business")
    if any(
        k in t
        for k in ("ULTRABOOK", "ZENBOOK", "SWIFT", "XPS 13", "GRAM", "ENVY 13", "SPECTRE", "MACBOOK AIR")
    ):
        tags.append("ultrabook")
    return list(dict.fromkeys(tags))


def parse_products(html: str, existing_tags: dict[str, str] | None = None) -> list[dict]:
    existing_tags = existing_tags or {}
    products: list[dict] = []
    for block in re.finditer(
        r'<article\s+data-id="(\d+)"[^>]*class="product-box[^"]*">(.*?)</article>',
        html,
        re.DOTALL,
    ):
        pid = block.group(1)
        body = block.group(2)
        link_m = re.search(r'<a class="mainlink" href="([^"]+)"[^>]*title="([^"]*)"', body)
        if not link_m:
            continue
        url, title = link_m.group(1), unescape(link_m.group(2)).strip(" -")
        img_m = re.search(r'<img[^>]+src="([^"]+)"', body)
        image = img_m.group(1) if img_m else ""
        old_m = re.search(r'<span class="oldprice">(.*?)</span>', body, re.DOTALL)
        price_m = re.search(r'<span class="price">(.*?)</span>', body, re.DOTALL)
        old_price = parse_euro_price(old_m.group(1)) if old_m else None
        price = parse_euro_price(price_m.group(1)) if price_m else None
        is_upgraded = title.upper().startswith("UPGRADED")
        is_promocode = "with-promocode" in body
        discount = calc_discount(old_price, price) if old_price and price else 0
        specs = [
            unescape(s).strip()
            for s in re.findall(r"<li>(.*?)</li>", body)
            if "specs-list" in body
        ]
        # specs from specs-list only
        specs_m = re.search(r'<ul class="specs-list">(.*?)</ul>', body, re.DOTALL)
        if specs_m:
            specs = [unescape(s).strip() for s in re.findall(r"<li>(.*?)</li>", specs_m.group(1), re.DOTALL)]

        products.append(
            {
                "id": pid,
                "title": title,
                "url": url,
                "image": image,
                "price": price,
                "old_price": old_price,
                "discount": discount,
                "upgraded": is_upgraded,
                "promocode": is_promocode,
                "tags": merge_tags(pid, infer_tags(title), existing_tags),
                "specs": specs,
                "os": infer_os(title, specs),
            }
        )
    return products


SALE_BADGE_HREF_MAIN = "#laptopi"
SALE_BADGE_HREF_SUBPAGE = "../hot-summer-sale-2026.html#laptopi"


def badge_classes(pct: int, is_promocode: bool) -> str:
    if pct <= 0:
        return ""
    if pct >= 40:
        return "bg-promo/25 text-promo border-promo/40"
    if pct >= 25:
        return "bg-promo/20 text-promo border-promo/30"
    return "bg-promo/10 text-promo border-promo/20"


def make_discount_badge_html(pct: int, is_promocode: bool, href: str) -> str:
    if pct <= 0:
        return ""
    cls = badge_classes(pct, is_promocode)
    label = "ПРОМО" if is_promocode else f"-{pct}%"
    return (
        f'\n    <a href="{href}" class="discount-badge absolute top-4 right-4 px-3 py-1 {cls} '
        f"border rounded-full text-technical-sm font-bold cursor-pointer transition-transform "
        f'duration-200 hover:scale-105 hover:brightness-110 z-10" '
        f'aria-label="Виж разпродажата">{label}</a>'
    )


def truncate_title(title: str, max_len: int = 80) -> str:
    if len(title) <= max_len:
        return title
    return title[: max_len - 1].rstrip() + "…"


def render_product(p: dict, sale_badge_href: str = SALE_BADGE_HREF_MAIN) -> str:
    tags = list(p["tags"])
    if p["upgraded"] and "upgraded" not in tags:
        tags.append("upgraded")
    tag_str = " ".join(tags)
    os_val = p.get("os") or "unknown"
    attrs = [
        f'data-os="{os_val}"',
        'class="group relative flex flex-col h-full"',
        f'data-tags="{tag_str}"',
        f'data-id="{p["id"]}"',
    ]
    if p["price"] is not None:
        attrs.append(f'data-price="{p["price"]:.2f}"')
    if p["discount"] > 0:
        attrs.append(f'data-discount-percent="{p["discount"]}"')
    if p["upgraded"]:
        attrs.append('data-upgraded="true"')
    subcategory = p.get("subcategory")
    if subcategory:
        attrs.append(f'data-subcategory="{subcategory}"')
    if p.get("image"):
        attrs.append(f'data-image="{p["image"]}"')

    title_esc = title_attr = p["title"].replace('"', "&quot;")
    short_title = truncate_title(p["title"])
    short_esc = short_title.replace('"', "&quot;")

    badge_html = ""
    if p["discount"] > 0:
        badge_html = make_discount_badge_html(p["discount"], p["promocode"], sale_badge_href)

    upgraded_html = ""
    if p["upgraded"]:
        upgraded_html = '\n    <div class="upgraded-badge absolute top-4 left-4 px-2.5 py-0.5 bg-promo/15 text-promo border-promo/35 border rounded-full text-technical-sm font-bold tracking-wide">UPGRADED</div>'

    os_badge_html = ""
    if os_val == "macos":
        os_badge_html = '\n    <div class="os-badge absolute bottom-4 left-4 px-2.5 py-0.5 bg-violet/15 text-violet border-violet/35 border rounded-full text-technical-sm font-bold tracking-wide">macOS</div>'
    elif os_val == "chromeos":
        os_badge_html = '\n    <div class="os-badge absolute bottom-4 left-4 px-2.5 py-0.5 bg-teal/15 text-teal border-teal/35 border rounded-full text-technical-sm font-bold tracking-wide">Chrome OS</div>'

    price_html = f'<div class="text-secondary font-headline-md font-bold">{p["price"]:.2f} €</div>'
    old_html = ""
    if p["old_price"]:
        old_html = f'\n      <p class="text-on-surface-variant text-body-sm line-through">{p["old_price"]:.2f} €</p>'

    specs_html = ""
    if p["specs"]:
        items = "\n".join(
            f'<li class="text-on-surface-variant text-body-sm">{s.replace("<", "&lt;")}</li>' for s in p["specs"]
        )
        specs_html = f'\n  <ul class="flex-1 space-y-1 list-disc list-inside text-on-surface-variant">{items}</ul>'

    return f"""<article {" ".join(attrs)}>
  <div class="aspect-square bg-surface-container squircle intelligent-edge overflow-hidden mb-4 relative block shrink-0">
  <a href="{p["url"]}" class="block w-full h-full relative">
    <img class="w-full h-full object-contain p-6 transition-transform duration-500 group-hover:scale-105" alt="{title_esc}" src="{p["image"]}" loading="lazy"/>{upgraded_html}{os_badge_html}
    <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
      <span class="px-6 py-3 bg-white text-surface font-bold rounded-full text-body-sm">Виж продукта</span>
    </div>
  </a>{badge_html}
  </div>
  <div class="flex flex-col flex-1 min-h-0">
    <h4 class="font-headline-md text-headline-md font-bold leading-tight line-clamp-2 min-h-[3.25rem]">
        <a href="{p["url"]}" class="hover:text-apricot transition-colors">{short_esc}</a>
      </h4>
    <div class="mb-3 min-h-[3.25rem]">
      {price_html}
      {old_html}
    </div>
{specs_html}
  <form class="mt-auto pt-4" method="post" action="https://plasico.bg/поръчка">
    <input type="hidden" name="action" value="buy"/>
    <input type="hidden" name="prod_id" value="{p["id"]}"/>
    <input type="hidden" name="quantity" value="1"/>
    <button type="submit" class="w-full px-6 py-3 bg-apricot text-on-secondary-container font-bold rounded-full hover:scale-[1.02] active:scale-95 transition-all">Купи</button>
  </form>
  </div>
</article>"""


def update_category_map(categories: list[dict]) -> dict:
    total_subs = sum(len(c["subcategories"]) for c in categories)
    data = {
        "source": BASE,
        "extractedFrom": "live-main.html",
        "extractedAt": date.today().isoformat(),
        "localFilters": ["all", "laptopi", "gaming", "business", "ultrabook"],
        "categories": categories,
        "connections": {
            "summary": {
                "totalCategories": len(categories),
                "totalSubcategories": total_subs,
                "localCategory": "laptopi",
                "externalCategories": [c["id"] for c in categories if c["external"]],
            },
            "localProductFilters": {
                "description": "Product data-tags on the laptops catalog page (redesign-only sub-filters, not in original sticky nav)",
                "tags": {
                    "all": {"label": "Всички", "productCountField": "all laptops"},
                    "laptopi": {"label": "Лаптопи", "matchesTag": "laptopi"},
                    "gaming": {"label": "Гейминг", "matchesTag": "gaming"},
                    "business": {"label": "Бизнес", "matchesTag": "business"},
                    "ultrabook": {"label": "Ултрапортативни", "matchesTag": "ultrabook"},
                },
            },
            "subcategoryActions": {
                "scroll": "Anchor on same page — scroll to #laptopi section",
                "filter": "Apply local catalog filter via data-tags",
                "external": "Open plasico.bg campaign sub-page in new tab (0 local products on laptops page)",
            },
            "originalNavToFilter": {
                c["id"]: {
                    "dataFilter": c["dataFilter"],
                    "local": c["local"],
                    "subcategories": len(c["subcategories"]),
                }
                for c in categories
            },
        },
    }
    CATEGORY_MAP.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def update_products_in_html(products: list[dict]) -> None:
    html = REDESIGN.read_text(encoding="utf-8")
    grid_start = html.index('<div id="product-grid"')
    grid_open_end = html.index(">", grid_start) + 1
    grid_close = html.index("</div>", grid_open_end)
    # find closing div for product-grid - need the one matching product-grid
    # safer: regex replace between product-grid open and next section
    m = re.search(
        r'(<div id="product-grid"[^>]*>\s*)(.*?)(\s*</div>\s*</section>)',
        html,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError("product-grid section not found")
    new_grid = "\n\n".join(render_product(p) for p in products) + "\n"
    html = html[: m.start(2)] + new_grid + html[m.end(2) :]

    # update subtitle count
    html = re.sub(
        r'(<p id="catalog-subtitle"[^>]*>)\d+ продукта',
        rf"\g<1>{len(products)} продукта",
        html,
        count=1,
    )
    REDESIGN.write_text(html, encoding="utf-8")


def compare_local_vs_live(live_products: list[dict]) -> dict:
    html = REDESIGN.read_text(encoding="utf-8")
    local_ids = re.findall(r'data-id="(\d+)"', html)
    live_by_id = {p["id"]: p for p in live_products}
    local_set = set(local_ids)
    live_set = set(live_by_id)
    return {
        "local_count": len(local_set),
        "live_count": len(live_set),
        "only_local": sorted(local_set - live_set),
        "only_live": sorted(live_set - local_set),
        "price_mismatches": [
            {"id": pid, "local": None, "live": live_by_id[pid]["price"]}
            for pid in sorted(local_set & live_set)
            if True
        ],
    }


def main() -> None:
    print("Fetching live page...")
    html = fetch(BASE)
    LIVE_MAIN.write_text(html, encoding="utf-8")
    print(f"Saved {len(html):,} bytes to live-main.html")

    categories = parse_nav(html)
    print(f"Categories: {len(categories)}")
    for c in categories:
        print(f"  - {c['id']}: {len(c['subcategories'])} subcategories")

    existing_tags = load_existing_tags()
    products = parse_products(html, existing_tags)
    print(f"Products: {len(products)}")
    upgraded = sum(1 for p in products if p["upgraded"])
    with_discount = sum(1 for p in products if p["discount"] > 0)
    print(f"  UPGRADED: {upgraded}, with discount: {with_discount}")

    cat_data = update_category_map(categories)
    print(f"Updated {CATEGORY_MAP.name}")

    update_products_in_html(products)
    print(f"Updated {REDESIGN.name} with {len(products)} products")

    # Summary JSON for reference
    summary = {
        "fetchedAt": date.today().isoformat(),
        "source": BASE,
        "categories": len(categories),
        "subcategories": cat_data["connections"]["summary"]["totalSubcategories"],
        "products": len(products),
        "upgraded": upgraded,
        "withDiscount": with_discount,
        "categoryNames": [c["name"] for c in categories],
    }
    (DIR / "live-scrape-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("Done.")


if __name__ == "__main__":
    main()
