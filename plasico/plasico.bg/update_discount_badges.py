#!/usr/bin/env python3
"""Compute discount % for sale products and update badges + data attributes."""

import re
import sys
from pathlib import Path

DIR = Path(__file__).parent
sys.path.insert(0, str(DIR))
from scrape_live_campaign import make_discount_badge_html, SALE_BADGE_HREF_MAIN  # noqa: E402

CURRENT = DIR / "hot-summer-sale-2026.html"
ORIGINAL = DIR / "hot-summer-sale-2026.original.html"


def parse_euro_price(text: str) -> float | None:
    """Parse price like 460.<sup>98</sup> or 460.98 €."""
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


def badge_classes(pct: int, is_promocode: bool) -> str:
    if pct <= 0:
        return ""
    if pct >= 40:
        return "bg-apricot/25 text-apricot border-apricot/40"
    if pct >= 25:
        return "bg-apricot/20 text-apricot border-apricot/30"
    return "bg-apricot/10 text-apricot border-apricot/20"


IMAGE_ZONE_RE = re.compile(
    r'<a href="([^"]+)" class="aspect-square bg-surface-container squircle intelligent-edge overflow-hidden mb-4 relative block shrink-0">(.*?)</a>',
    re.DOTALL,
)

DISCOUNT_BADGE_RE = re.compile(
    r'\n\s*<(?:div|a) class="discount-badge[^"]*"[^>]*>.*?</(?:div|a)>',
    re.DOTALL,
)


def restructure_image_zone(article: str) -> str:
    """Move product image link inside a wrapper div so discount badge <a> is not nested."""

    def replace_zone(match: re.Match) -> str:
        product_url = match.group(1)
        inner = DISCOUNT_BADGE_RE.sub("", match.group(2))
        return (
            '<div class="aspect-square bg-surface-container squircle intelligent-edge overflow-hidden mb-4 relative block shrink-0">\n'
            f'  <a href="{product_url}" class="block w-full h-full relative">{inner}</a>\n'
            "</div>"
        )

    if '<div class="aspect-square bg-surface-container' in article:
        return article
    return IMAGE_ZONE_RE.sub(replace_zone, article, count=1)


def parse_original_products(html: str) -> dict[str, dict]:
    products: dict[str, dict] = {}
    for block in re.finditer(
        r'<article\s+data-id="(\d+)"[^>]*>(.*?)</article>',
        html,
        re.DOTALL,
    ):
        pid = block.group(1)
        body = block.group(2)
        is_promocode = "with-promocode" in body

        old_price = None
        current_price = None
        inshop_price = None
        promo_price = None

        if is_promocode:
            inshop_m = re.search(
                r'price-inshop[^<]*</span><span class="price">([^<]+(?:<[^>]+>[^<]*)*)',
                body,
            )
            if inshop_m:
                inshop_price = parse_euro_price(inshop_m.group(1))

            promo_m = re.search(
                r'class="codeprice">([^<]+(?:<[^>]+>[^<]*)*)',
                body,
            )
            if promo_m:
                promo_price = parse_euro_price(promo_m.group(1))

            # Some promocode products only show in-shop price (3% code at checkout)
            if inshop_price and promo_price:
                old_price = inshop_price
                current_price = promo_price
            elif inshop_price:
                # 3% promocode discount
                current_price = round(inshop_price * 0.97, 2)
                old_price = inshop_price
        else:
            old_m = re.search(
                r'<span class="oldprice">([^<]+(?:<[^>]+>[^<]*)*)',
                body,
            )
            price_m = re.search(
                r'<span class="oldprice">.*?</span><span class="price">([^<]+(?:<[^>]+>[^<]*)*)',
                body,
                re.DOTALL,
            )
            if old_m:
                old_price = parse_euro_price(old_m.group(1))
            if price_m:
                current_price = parse_euro_price(price_m.group(1))

        pct = 0
        if old_price and current_price:
            pct = calc_discount(old_price, current_price)

        products[pid] = {
            "discount": pct,
            "is_promocode": is_promocode,
            "old_price": old_price,
            "current_price": current_price,
        }
    return products


def parse_current_prices(article: str) -> tuple[float | None, float | None, bool]:
    """Return (current, old, is_promocode) from current card HTML."""
    is_promocode = "ОНЛАЙН ЦЕНА" in article or "text-violet" in article

    current_m = re.search(
        r'<div class="text-secondary font-headline-md font-bold">([\d.]+)\s*€',
        article,
    )
    current = float(current_m.group(1)) if current_m else None

    old = None
    shop_m = re.search(r"Магазин:\s*([\d.]+)\s*€", article)
    if shop_m:
        old = float(shop_m.group(1))
    else:
        old_m = re.search(
            r'line-through(?!\s+invisible)[^>]*>([\d.]+)\s*€',
            article,
        )
        if old_m:
            old = float(old_m.group(1))

    return current, old, is_promocode


def make_badge_html(pct: int, is_promocode: bool) -> str:
    return make_discount_badge_html(pct, is_promocode, SALE_BADGE_HREF_MAIN)


def update_article(article: str, orig: dict | None) -> tuple[str, int, bool]:
    m = re.search(r'data-id="(\d+)"', article)
    pid = m.group(1) if m else ""

    current, old_from_card, is_promocode = parse_current_prices(article)
    if orig:
        is_promocode = orig.get("is_promocode", is_promocode)

    pct = 0
    if orig and orig.get("discount", 0) > 0:
        pct = orig["discount"]
    elif old_from_card and current:
        pct = calc_discount(old_from_card, current)

    # Update article opening tag with data-discount-percent
    def patch_article_tag(tag_match: re.Match) -> str:
        tag = tag_match.group(0)
        tag = re.sub(r'\s*data-discount-percent="[^"]*"', "", tag)
        tag = tag.replace(">", f' data-discount-percent="{pct}">', 1)
        return tag

    article = re.sub(r"<article[^>]*>", patch_article_tag, article, count=1)

    article = restructure_image_zone(article)

    # Remove existing badge elements (ПРОМО, ОНЛАЙН ЦЕНА, or prior discount-badge)
    article = DISCOUNT_BADGE_RE.sub("", article)

    badge = make_badge_html(pct, is_promocode)
    if badge:
        article = re.sub(
            r'(<div class="aspect-square bg-surface-container[^>]*>\s*<a href="[^"]+" class="block w-full h-full relative">.*?</a>)',
            r"\1" + badge,
            article,
            count=1,
            flags=re.DOTALL,
        )

    return article, pct, bool(badge)


def main() -> None:
    orig_html = ORIGINAL.read_text(encoding="utf-8")
    current_html = CURRENT.read_text(encoding="utf-8")
    orig_products = parse_original_products(orig_html)

    badge_count = 0
    zero_count = 0
    discounts: list[int] = []

    def replace_article(match: re.Match) -> str:
        nonlocal badge_count, zero_count
        article = match.group(0)
        pid_m = re.search(r'data-id="(\d+)"', article)
        pid = pid_m.group(1) if pid_m else ""
        updated, pct, has_badge = update_article(article, orig_products.get(pid))
        discounts.append(pct)
        if has_badge:
            badge_count += 1
        else:
            zero_count += 1
        return updated

    updated_html = re.sub(
        r"<article[^>]*>.*?</article>",
        replace_article,
        current_html,
        flags=re.DOTALL,
    )

    CURRENT.write_text(updated_html, encoding="utf-8")

    print(f"Products processed: {len(discounts)}")
    print(f"Products with discount badges: {badge_count}")
    print(f"Products without badge (0% or no old price): {zero_count}")
    if discounts:
        with_pct = [d for d in discounts if d > 0]
        print(f"Discount range: {min(with_pct)}% – {max(with_pct)}%" if with_pct else "No discounts")
        for threshold in [10, 20, 30, 40]:
            print(f"  >= {threshold}%: {sum(1 for d in discounts if d >= threshold)}")


if __name__ == "__main__":
    main()
