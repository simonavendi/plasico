import json
import re
from pathlib import Path

html = Path(r"D:\Vibe\plasico\plasico\plasico.bg\hot-summer-sale-2026.html").read_text(encoding="utf-8")

sections = re.findall(
    r'<section id="([^"]+)" class="group">.*?<h2 class="ttl">\s*([^<]+)</h2>',
    html,
    re.DOTALL,
)

pattern = re.compile(
    r'<article data-id="(\d+)" class="product-box[^"]*">.*?'
    r'href="([^"]+)".*?'
    r'<img loading="lazy" src="([^"]+)".*?'
    r'<span class="ttl"[^>]*>([^<]+)</span>',
    re.DOTALL,
)
products = pattern.findall(html)

price_pat = re.compile(r'<span class="price">(.*?)</span>', re.DOTALL)
old_price_pat = re.compile(r'<span class="oldprice">(.*?)</span>', re.DOTALL)
flag_pat = re.compile(r'<span class="flags-text[^"]*">([^<]+)</span>')

out = {
    "sections": [{"id": sid, "title": title.strip()} for sid, title in sections],
    "products": [],
}

for pid, url, img, title in products[:12]:
    start = html.find(f'data-id="{pid}"')
    chunk = html[start : start + 5000]
    prices = price_pat.findall(chunk)
    old_prices = old_price_pat.findall(chunk)
    flags = flag_pat.findall(chunk)

    def clean(s):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()

    out["products"].append(
        {
            "id": pid,
            "url": url,
            "img": img,
            "title": title.strip(),
            "price": clean(prices[0]) if prices else "",
            "old_price": clean(old_prices[0]) if old_prices else "",
            "flag": clean(flags[0]) if flags else "",
        }
    )

Path(r"D:\Vibe\plasico\products.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("done", len(out["products"]), "products")
