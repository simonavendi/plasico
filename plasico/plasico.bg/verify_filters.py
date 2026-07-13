#!/usr/bin/env python3
import json
import re
from pathlib import Path

html = Path("hot-summer-sale-2026.html").read_text(encoding="utf-8")
gaming_win_upgraded = []
for m in re.finditer(r"<article[^>]*>.*?</article>", html, re.DOTALL):
    block = m.group(0)
    if 'data-id="' not in block:
        continue
    tag = re.search(r'data-tags="([^"]*)"', block)
    os_ = re.search(r'data-os="([^"]*)"', block)
    disc = re.search(r'data-discount-percent="(\d+)"', block)
    upg = 'data-upgraded="true"' in block
    tags = (tag.group(1) if tag else "").split()
    pct = int(disc.group(1)) if disc else 0
    osv = os_.group(1) if os_ else ""
    if "gaming" in tags and osv == "windows" and pct >= 20 and upg:
        gaming_win_upgraded.append(re.search(r'data-id="(\d+)"', block).group(1))

print(f"Gaming + Windows + 20%+ + UPGRADED: {len(gaming_win_upgraded)} products")

gaming = windows = gw = gw20 = 0
for m in re.finditer(r"<article[^>]*>.*?</article>", html, re.DOTALL):
    block = m.group(0)
    if 'data-id="' not in block:
        continue
    tag = re.search(r'data-tags="([^"]*)"', block)
    os_ = re.search(r'data-os="([^"]*)"', block)
    disc = re.search(r'data-discount-percent="(\d+)"', block)
    tags = (tag.group(1) if tag else "").split()
    pct = int(disc.group(1)) if disc else 0
    osv = os_.group(1) if os_ else ""
    if "gaming" in tags:
        gaming += 1
    if "gaming" in tags and osv == "windows":
        windows += 1
        gw += 1
        if pct >= 20:
            gw20 += 1

print(f"  gaming only: {gaming}, +windows: {gw}, +20%: {gw20}")

pm = json.loads(Path("products-map.json").read_text(encoding="utf-8"))
print(f"Total mapped: {pm['totalProducts']}")
print("Per category:")
for cat_id, info in pm["byCategory"].items():
    print(f"  {cat_id}: {info['count']}")

components = [p for p in pm["products"] if p["categoryId"] == "components" and p["subcategoryAnchor"] == "ssd-diskove"]
print(f"SSD disks in components: {len(components)}")
