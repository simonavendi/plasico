#!/usr/bin/env python3
import re
from pathlib import Path

root = Path(__file__).parent / "hot-summer-sale-2026"
for path in sorted(root.glob("*.html")):
    html = path.read_text(encoding="utf-8")
    new = re.sub(
        r'(class="[^"]*(?:discount-badge|upgraded-badge)[^"]*")',
        lambda m: m.group(1).replace("apricot", "promo"),
        html,
    )
    if new != html:
        path.write_text(new, encoding="utf-8")
        print(f"OK: {path.name}")
