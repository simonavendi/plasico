"""Fix product card layout consistency in hot-summer-sale-2026.html."""
import re
from pathlib import Path

path = Path(__file__).parent / "hot-summer-sale-2026.html"
html = path.read_text(encoding="utf-8")

ARTICLE_RE = re.compile(
    r'<article\s+class="group relative flex flex-col"([^>]*)>(.*?)</article>',
    re.S,
)

PRICE_BLOCK_RE = re.compile(
    r'  <div class="flex justify-between items-start gap-4 mb-2">\s*'
    r'<div class="min-w-0 flex-1">\s*'
    r'(<h4 class="font-headline-md text-headline-md font-bold leading-tight">\s*'
    r'<a href="[^"]*" class="hover:text-apricot transition-colors">[^<]*</a>\s*'
    r'</h4>)\s*'
    r'(?:<p class="text-on-surface-variant text-body-sm line-through">([^<]*)</p>\s*)?'
    r'</div>\s*'
    r'<div class="text-right shrink-0">\s*'
    r'<div class="text-secondary font-headline-md font-bold whitespace-nowrap">([^<]*)</div>\s*'
    r'</div>\s*'
    r'</div>',
    re.S,
)


def fix_article(match: re.Match) -> str:
    attrs = match.group(1)
    body = match.group(2)

    price_match = PRICE_BLOCK_RE.search(body)
    if not price_match:
        return match.group(0)

    title_h4 = price_match.group(1)
    old_price = price_match.group(2)
    active_price = price_match.group(3)

    # Title with consistent 2-line clamp height
    title_h4 = title_h4.replace(
        'class="font-headline-md text-headline-md font-bold leading-tight"',
        'class="font-headline-md text-headline-md font-bold leading-tight line-clamp-2 min-h-[3.25rem]"',
    )

    old_price_html = (
        f'      <p class="text-on-surface-variant text-body-sm line-through">{old_price}</p>\n'
        if old_price
        else '      <p class="text-on-surface-variant text-body-sm line-through invisible" aria-hidden="true">&nbsp;</p>\n'
    )

    new_price_block = (
        f'  <div class="flex flex-col flex-1 min-h-0">\n'
        f'    {title_h4}\n'
        f'    <div class="mb-3 min-h-[3.25rem]">\n'
        f'      <div class="text-secondary font-headline-md font-bold">{active_price}</div>\n'
        f'{old_price_html}'
        f'    </div>\n'
    )

    body = PRICE_BLOCK_RE.sub(new_price_block, body, count=1)

    # Specs list grows to push button down
    body = body.replace(
        '<ul class="mt-3 space-y-1 list-disc list-inside">',
        '<ul class="flex-1 space-y-1 list-disc list-inside text-on-surface-variant">',
        1,
    )
    # Remove redundant text class from li if present - actually keep li classes

  # Pin buy button to card bottom
    body = body.replace(
        '<form class="mt-4" method="post" action="https://plasico.bg/поръчка">',
        '<form class="mt-auto pt-4" method="post" action="https://plasico.bg/поръчка">',
        1,
    )

    # Close content wrapper before article end
    body = body.rstrip() + '\n  </div>\n'

    return f'<article class="group relative flex flex-col h-full"{attrs}>{body}</article>'


new_html, count = ARTICLE_RE.subn(fix_article, html)

# Ensure grid stretches card heights
new_html = new_html.replace(
    '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter">',
    '<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter items-stretch">',
    1,
)

path.write_text(new_html, encoding="utf-8")
print(f"Fixed {count} product cards")

# Verify
remaining = len(re.findall(r'flex justify-between items-start gap-4 mb-2', new_html))
print(f"Remaining old price layouts: {remaining}")
articles = len(re.findall(r'<article class="group relative flex flex-col h-full"', new_html))
print(f"Cards with h-full: {articles}")
