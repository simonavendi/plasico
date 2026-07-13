#!/usr/bin/env python3
"""Detect operating system per product and add data-os to redesign HTML."""

from __future__ import annotations

import re
from collections import Counter
from html import unescape
from pathlib import Path

DIR = Path(__file__).parent
REDESIGN = DIR / "hot-summer-sale-2026.html"
ORIGINAL = DIR / "hot-summer-sale-2026.original.html"

OS_LABELS = {
    "windows": "Windows",
    "macos": "macOS",
    "chromeos": "Chrome OS",
    "freedos": "FreeDOS",
    "linux": "Linux",
    "unknown": "Unknown",
}


def classify_os_text(text: str) -> str | None:
    """Return OS slug from a single text blob, or None if inconclusive."""
    t = text.lower()
    if re.search(r"chrome\s*os|chromebook", t):
        return "chromeos"
    if re.search(r"mac\s*os|macos|macbook", t):
        return "macos"
    if re.search(r"freedos|free\s*dos|без\s*операционна|без\s*ос|no\s*os|without\s*os", t):
        return "freedos"
    if re.search(r"\blinux\b|ubuntu|debian|fedora", t):
        return "linux"
    if re.search(r"windows|win\s*1[01]|win11|win10", t):
        return "windows"
    return None


def extract_os_spec(block: str) -> str | None:
    m = re.search(
        r"Операционна система:\s*([^<]+)",
        block,
        re.IGNORECASE,
    )
    if not m:
        return None
    return unescape(m.group(1)).strip()


def extract_title(block: str) -> str:
    alt_m = re.search(r'<img[^>]+alt="([^"]*)"', block)
    if alt_m:
        return unescape(alt_m.group(1))
    link_m = re.search(r'<a[^>]+class="hover:text-apricot[^"]*"[^>]*>([^<]+)</a>', block)
    if link_m:
        return unescape(link_m.group(1))
    return ""


def detect_os(block: str, title: str = "") -> str:
    spec = extract_os_spec(block)
    if spec:
        from_spec = classify_os_text(spec)
        if from_spec:
            return from_spec
        if "без" in spec.lower():
            return "freedos"

    combined = f"{title} {block}"
    from_title = classify_os_text(combined)
    return from_title or "unknown"


def parse_original_os_by_id() -> dict[str, str]:
    if not ORIGINAL.exists():
        return {}
    html = ORIGINAL.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    for m in re.finditer(
        r'<article\s+data-id="(\d+)"[^>]*>(.*?)</article>',
        html,
        re.DOTALL,
    ):
        pid = m.group(1)
        body = m.group(2)
        title_m = re.search(r'title="([^"]*)"', body)
        title = unescape(title_m.group(1)) if title_m else ""
        result[pid] = detect_os(body, title)
    return result


def add_data_os_to_redesign() -> Counter[str]:
    html = REDESIGN.read_text(encoding="utf-8")
    fallback = parse_original_os_by_id()
    counts: Counter[str] = Counter()

    def replace_article(m: re.Match[str]) -> str:
        opening = m.group(1)
        pid_m = re.search(r'data-id="(\d+)"', opening)
        pid = pid_m.group(1) if pid_m else ""
        block = m.group(0)
        title = extract_title(block)
        os_val = detect_os(block, title)
        if os_val == "unknown" and pid in fallback:
            os_val = fallback[pid]
        counts[os_val] += 1

        opening = re.sub(r'\s*data-os="[^"]*"', "", opening)
        if 'class="' in opening:
            opening = opening.replace('class="', f'data-os="{os_val}" class="', 1)
        else:
            opening = opening.rstrip(">") + f' data-os="{os_val}">'
        return opening + block[len(m.group(1)) :]

    new_html = re.sub(
        r"(<article[^>]*>)(.*?)</article>",
        replace_article,
        html,
        flags=re.DOTALL,
    )
    REDESIGN.write_text(new_html, encoding="utf-8")
    return counts


def main() -> None:
    counts = add_data_os_to_redesign()
    total = sum(counts.values())
    print(f"Updated {total} products in {REDESIGN.name}")
    print("\nOS distribution:")
    for slug in ("windows", "macos", "chromeos", "freedos", "linux", "unknown"):
        n = counts.get(slug, 0)
        if n:
            print(f"  {OS_LABELS[slug]}: {n}")


if __name__ == "__main__":
    main()
