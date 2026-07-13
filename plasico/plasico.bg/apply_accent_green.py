#!/usr/bin/env python3
"""Switch UI accent from orange to green (#07a857); keep promo badges/sale CTAs warm."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "hot-summer-sale-2026.html"

ACCENT = "#07a857"
ACCENT_HOVER = "#069449"
ACCENT_DARK = "#058a47"
ACCENT_RGBA = "rgba(7, 168, 87"
PROMO_RGBA = "rgba(251, 146, 60"

# CSS blocks that must keep warm/orange promo styling
PROTECTED_CSS_PATTERNS = [
    r"\.mesh-gradient-text\s*\{[^}]+\}",
    r"\.hero-bg::before\s*\{[^}]+\}",
    r"\.header-sale-cta[^{]*\{[^}]+\}",
    r"\.header-sale-cta:hover\s*\{[^}]+\}",
    r"\.header-sale-cta:focus-visible\s*\{[^}]+\}",
    r"\.header-sale-cta__icon\s*\{[^}]+\}",
    r"\.header-sale-cta\.is-active\s*\{[^}]+\}",
    r"\.panel-utility-mega-cell--sale[^{]*\{[^}]+\}",
    r"\.panel-utility-mega-cell--sale:hover\s*\{[^}]+\}",
    r"\.panel-utility-mega-cell--sale\.is-active\s*\{[^}]+\}",
    r"\.panel-utility-mega-parent--sale[^{]*\{[^}]+\}",
    r"\.panel-utility-mega-parent--sale:hover\s*\{[^}]+\}",
    r"\.panel-utility-mega-cell--sale \.header-cat-mega-parent__icon[^{]*\{[^}]+\}",
    r"\.panel-utility-mega-cell--sale \.header-cat-mega-parent__icon \.material-symbols-outlined\s*\{[^}]+\}",
    r"#product-grid \.discount-badge[^{]*\{[^}]+\}",
    r"#product-grid \.discount-badge:hover\s*\{[^}]+\}",
    r"#product-grid \.discount-badge::before\s*\{[^}]+\}",
    r"#product-grid \.upgraded-badge\s*\{[^}]+\}",
]


def protect_css_blocks(css: str) -> tuple[str, list[str]]:
    saved: list[str] = []
    for pattern in PROTECTED_CSS_PATTERNS:
        for match in re.finditer(pattern, css, flags=re.DOTALL):
            token = f"__PROMO_CSS_{len(saved)}__"
            saved.append(match.group(0))
            css = css.replace(match.group(0), token, 1)
    return css, saved


def restore_css_blocks(css: str, saved: list[str]) -> str:
    for i, block in enumerate(saved):
        css = css.replace(f"__PROMO_CSS_{i}__", block, 1)
    return css


def replace_accent_in_css(css: str) -> str:
    css, saved = protect_css_blocks(css)
    replacements = [
        ("#FB923C", ACCENT),
        ("#fb923c", ACCENT),
        ("#F97316", ACCENT_DARK),
        ("#f97316", ACCENT_DARK),
        ("#f59e0b", ACCENT_HOVER),
        ("#EA580C", ACCENT_DARK),
        ("rgba(251, 146, 60", ACCENT_RGBA),
        ("rgba(249, 115, 22", "rgba(5, 138, 71"),
    ]
    for old, new in replacements:
        css = css.replace(old, new)
    return restore_css_blocks(css, saved)


def promo_class_replacements(html: str) -> str:
    """Move promo badge / hero promo elements from apricot → promo token."""

    def promoify(match: re.Match) -> str:
        return match.group(0).replace("apricot", "promo")

    html = re.sub(
        r'class="[^"]*(?:discount-badge|upgraded-badge)[^"]*"',
        promoify,
        html,
    )
    html = html.replace(
        'border border-apricot/30 bg-apricot/10 text-apricot font-technical-md text-technical-md mb-8">HOT SUMMER SALE 2026',
        'border border-promo/30 bg-promo/10 text-promo font-technical-md text-technical-md mb-8">HOT SUMMER SALE 2026',
    )
    html = html.replace(
        "bg-gradient-to-r from-violet via-apricot to-teal",
        "bg-gradient-to-r from-violet via-promo to-teal",
    )
    return html


def update_tailwind_config(html: str) -> str:
    html = html.replace('apricot: "#FB923C",', f'apricot: "{ACCENT}",')
    if 'promo: "#FB923C"' not in html:
        html = html.replace(
            f'apricot: "{ACCENT}",',
            f'apricot: "{ACCENT}",\n            promo: "#FB923C",\n            "promo-dark": "#F97316",',
        )
    html = html.replace('"on-secondary-container": "#451f00"', '"on-secondary-container": "#ffffff"')
    return html


def apply_to_html(html: str) -> str:
    html = update_tailwind_config(html)
    html = promo_class_replacements(html)

    style_match = re.search(r"(<style>)(.*?)(</style>)", html, flags=re.DOTALL)
    if style_match:
        new_style = replace_accent_in_css(style_match.group(2))
        html = html[: style_match.start(2)] + new_style + html[style_match.end(2) :]

    # Header search button text on green
    html = html.replace(
        ".header-search-btn {\n      background: " + ACCENT + ";\n      color: #451f00;",
        ".header-search-btn {\n      background: " + ACCENT + ";\n      color: #ffffff;",
    )
    html = html.replace(
        ".header-cart-badge,\n    .header-fav-badge {",
        ".header-cart-badge,\n    .header-fav-badge {",
    )
    html = re.sub(
        r"(\\.header-cart-badge,\\s*\\.header-fav-badge \\{[^}]*background: )" + re.escape(ACCENT) + r"(;[^}]*color: )#451f00",
        r"\1" + ACCENT + r"\2#ffffff",
        html,
        flags=re.DOTALL,
    )
    return html


def apply_to_file(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    path.write_text(apply_to_html(html), encoding="utf-8")
    print(f"OK: {path.relative_to(ROOT.parent.parent)}")


def patch_python_sources() -> None:
  patches = {
      ROOT / "scrape_live_campaign.py": [
          ('return "bg-apricot/25 text-apricot border-apricot/40"', 'return "bg-promo/25 text-promo border-promo/40"'),
          ('return "bg-apricot/20 text-apricot border-apricot/30"', 'return "bg-promo/20 text-promo border-promo/30"'),
          ('return "bg-apricot/10 text-apricot border-apricot/20"', 'return "bg-promo/10 text-promo border-promo/20"'),
          (
              'bg-apricot/15 text-apricot border-apricot/35',
              'bg-promo/15 text-promo border-promo/35',
          ),
      ],
      ROOT / "update_discount_badges.py": [
          ('return "bg-apricot/25 text-apricot border-apricot/40"', 'return "bg-promo/25 text-promo border-promo/40"'),
          ('return "bg-apricot/20 text-apricot border-apricot/30"', 'return "bg-promo/20 text-promo border-promo/30"'),
          ('return "bg-apricot/10 text-apricot border-apricot/20"', 'return "bg-promo/10 text-promo border-promo/20"'),
      ],
  }

  mirror_css_old = """    .mirror-breadcrumb a:hover { color: #FB923C; }"""
  mirror_css_new = f"""    .mirror-breadcrumb a:hover {{ color: {ACCENT}; }}"""
  apply_template = ROOT / "apply_template.py"
  text = apply_template.read_text(encoding="utf-8")
  text = text.replace(mirror_css_old, mirror_css_new)
  text = text.replace("color: #FB923C;", f"color: {ACCENT};")
  text = text.replace("color: #FB923C !important;", f"color: {ACCENT} !important;")
  text = text.replace("rgba(251, 146, 60, 0.15)", f"{ACCENT_RGBA}, 0.15)")
  text = text.replace("rgba(251, 146, 60, 0.35)", f"{ACCENT_RGBA}, 0.35)")
  text = text.replace("rgba(251, 146, 60, 0.25)", f"{ACCENT_RGBA}, 0.25)")
  text = text.replace("rgba(251, 146, 60, 0.5)", f"{ACCENT_RGBA}, 0.5)")
  text = text.replace("rgba(251, 146, 60, 0.1)", f"{ACCENT_RGBA}, 0.1)")
  text = text.replace('color: #ffb783 !important;', f"color: {ACCENT_HOVER} !important;")
  apply_template.write_text(text, encoding="utf-8")
  print("OK: apply_template.py mirror CSS")

  for path, reps in patches.items():
      text = path.read_text(encoding="utf-8")
      for old, new in reps:
          text = text.replace(old, new)
      path.write_text(text, encoding="utf-8")
      print(f"OK: {path.name}")


def main() -> None:
    apply_to_file(TEMPLATE)
    patch_python_sources()
    print("Accent green applied to template and generator scripts.")


if __name__ == "__main__":
    main()
