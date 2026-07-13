#!/usr/bin/env python3
import re
from collections import Counter
from scrape_live_campaign import parse_products

live = open("live-main.html", encoding="utf-8").read()
local = open("hot-summer-sale-2026.html", encoding="utf-8").read()
live_prods = {p["id"]: p for p in parse_products(live)}

mismatch = 0
for m in re.finditer(
    r'<article[^>]*data-id="(\d+)"[^>]*data-price="([^"]+)"(?:[^>]*data-discount-percent="(\d+)")?',
    local,
):
    pid, price, disc = m.group(1), m.group(2), m.group(3) or "0"
    lp = live_prods.get(pid)
    if not lp:
        print("missing on live:", pid)
        continue
    if abs(float(price) - lp["price"]) > 0.01 or int(disc) != lp["discount"]:
        mismatch += 1

arts = len(re.findall(r'<article[^>]*data-id="', local))
print(f"local articles: {arts}")
print(f"live products: {len(live_prods)}")
print(f"price/discount mismatches: {mismatch}")

c = Counter()
for t in re.findall(r'data-tags="([^"]+)"', local):
    for x in t.split():
        c[x] += 1
print("tag counts:", dict(c))

cat = __import__("json").load(open("category-map.json", encoding="utf-8"))
print(f"categories: {len(cat['categories'])}, subcategories: {cat['connections']['summary']['totalSubcategories']}")
