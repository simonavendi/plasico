#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "plasico" / "plasico.bg"))
from scrape_live_campaign import parse_products

live = (Path(__file__).parent / "plasico" / "plasico.bg" / "live-main.html").read_text(
    encoding="utf-8"
)
prods = parse_products(live)
out = {"sections": [{"id": "laptopi", "title": "Лаптопи"}], "products": []}
for p in prods[:8]:
    out["products"].append(
        {
            "id": p["id"],
            "url": p["url"],
            "img": p["image"],
            "title": p["title"],
            "price": f"{p['price']:.2f} €" if p["price"] else "",
            "old_price": f"{p['old_price']:.2f} €" if p["old_price"] else "",
            "flag": "ПРОМО" if p["discount"] > 0 else "",
        }
    )
Path(__file__).parent.joinpath("products.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"Wrote {len(out['products'])} featured products to products.json")
