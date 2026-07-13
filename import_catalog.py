import html
import re
from pathlib import Path

ORIGINAL = Path(r"D:\Vibe\plasico\plasico\plasico.bg\hot-summer-sale-2026.original.html")
TARGET = Path(r"D:\Vibe\plasico\plasico\plasico.bg\hot-summer-sale-2026.html")

source = ORIGINAL.read_text(encoding="utf-8")
articles = re.findall(
    r'<article data-id="(\d+)" class="product-box[^"]*">(.*?)</article>',
    source,
    re.DOTALL,
)


def clean_html_text(fragment: str) -> str:
    text = re.sub(r"<sup[^>]*>([^<]*)</sup>", r"\1", fragment)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_price_eur(fragment: str, class_name: str) -> str:
    match = re.search(
        rf'<span class="{class_name}">(.*?)</span>',
        fragment,
        re.DOTALL,
    )
    if not match:
        return ""
    text = clean_html_text(match.group(1))
    if " / " in text:
        text = text.split(" / ")[0].strip()
    return text.strip()


def extract_price_bgn(fragment: str, class_name: str) -> str:
    match = re.search(
        rf'<span class="{class_name}">(.*?)</span>',
        fragment,
        re.DOTALL,
    )
    if not match:
        return ""
    text = clean_html_text(match.group(1))
    if " / " in text:
        return text.split(" / ", 1)[1].strip()
    return ""


def short_title(title: str, limit: int = 72) -> str:
    return title if len(title) <= limit else title[: limit - 1] + "…"


def render_badge(flag: str, has_promo: bool, promocode: str) -> str:
    if flag and "ОНЛАЙН" in flag.upper():
        label = "ОНЛАЙН ЦЕНА"
        classes = "bg-violet/10 text-violet border-violet/20"
    elif has_promo or (flag and flag.startswith("-")):
        label = "ПРОМО"
        classes = "bg-teal/10 text-teal border-teal/20"
    elif flag:
        label = html.escape(flag[:24])
        classes = "bg-apricot/10 text-apricot border-apricot/20"
    else:
        return ""
    extra = ""
    if promocode:
        extra = f' <span class="opacity-80">({html.escape(promocode)})</span>'
    return (
        f'<div class="absolute top-4 right-4 px-3 py-1 {classes} border rounded-full text-technical-sm font-bold">'
        f"{html.escape(label)}{extra}</div>"
    )


def render_product(prod_id: str, body: str) -> str:
    url_match = re.search(r'<a class="mainlink" href="([^"]+)"', body)
    img_match = re.search(r'<img loading="lazy" src="([^"]+)"', body)
    title_match = re.search(r'<span class="ttl"[^>]*>([^<]+)</span>', body)
    specs = re.findall(r"<li>([^<]+)</li>", body)

    url = url_match.group(1) if url_match else "#"
    img = img_match.group(1) if img_match else ""
    title = html.unescape(title_match.group(1).strip()) if title_match else ""

    has_promocode = "with-promocode" in body or "promocode_price" in body
    old_price = extract_price_eur(body, "oldprice")
    shop_price = extract_price_eur(body, "price")
    shop_bgn = extract_price_bgn(body, "price")
    code_price = extract_price_eur(body, "codeprice")
    code_bgn = extract_price_bgn(body, "codeprice")

    promocode = ""
    code_match = re.search(r'<span class="code">([^<]+)</span>', body)
    if code_match:
        promocode = code_match.group(1).strip()

    flag_match = re.search(r'<span class="flags-text[^"]*">([^<]+)</span>', body)
    flag = clean_html_text(flag_match.group(1)) if flag_match else ""

    display_price = code_price or shop_price
    display_bgn = code_bgn or shop_bgn
    old_display = shop_price if code_price and shop_price else old_price

    badge = render_badge(flag, bool(old_price and not has_promocode), promocode)
    old_html = ""
    if old_display and old_display != display_price:
        old_html = f'<p class="text-on-surface-variant text-body-sm line-through">{html.escape(old_display)}</p>'

    bgn_html = ""
    if display_bgn:
        bgn_html = f'<p class="text-on-surface-variant text-technical-sm">{html.escape(display_bgn)}</p>'

    specs_html = ""
    if specs:
        items = "".join(
            f'<li class="text-on-surface-variant text-body-sm">{html.escape(s.strip())}</li>'
            for s in specs[:5]
        )
        specs_html = f'<ul class="mt-3 space-y-1 list-disc list-inside">{items}</ul>'

    promocode_note = ""
    if has_promocode and shop_price and code_price:
        promocode_note = (
            f'<p class="text-violet text-technical-sm mt-1">Магазин: {html.escape(shop_price)}</p>'
        )

    return f"""
<article class="group relative flex flex-col" data-id="{html.escape(prod_id)}">
  <a href="{html.escape(url)}" class="aspect-square bg-surface-container squircle intelligent-edge overflow-hidden mb-4 relative block">
    <img class="w-full h-full object-contain p-6 transition-transform duration-500 group-hover:scale-105" alt="{html.escape(title)}" src="{html.escape(img)}" loading="lazy"/>
    {badge}
    <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
      <span class="px-6 py-3 bg-white text-surface font-bold rounded-full text-body-sm">Виж продукта</span>
    </div>
  </a>
  <div class="flex justify-between items-start gap-4 mb-2">
    <div class="min-w-0 flex-1">
      <h4 class="font-headline-md text-headline-md font-bold leading-tight">
        <a href="{html.escape(url)}" class="hover:text-apricot transition-colors">{html.escape(short_title(title))}</a>
      </h4>
      {old_html}
      {promocode_note}
    </div>
    <div class="text-right shrink-0">
      <div class="text-secondary font-headline-md font-bold whitespace-nowrap">{html.escape(display_price)}</div>
      {bgn_html}
    </div>
  </div>
  {specs_html}
  <form class="mt-4" method="post" action="https://plasico.bg/поръчка">
    <input type="hidden" name="action" value="buy"/>
    <input type="hidden" name="prod_id" value="{html.escape(prod_id)}"/>
    <input type="hidden" name="quantity" value="1"/>
    <button type="submit" class="w-full px-6 py-3 bg-apricot text-on-secondary-container font-bold rounded-full hover:scale-[1.02] active:scale-95 transition-all">Купи</button>
  </form>
</article>"""


cards = "\n".join(render_product(pid, body) for pid, body in articles)
count = len(articles)

catalog_section = f"""    <section id="laptopi" class="py-stack-lg bg-surface-container-lowest px-container-padding">
      <div class="max-w-[1440px] mx-auto">
        <div class="mb-stack-lg">
          <h2 class="font-headline-lg font-bold flex items-center gap-4">
            <span class="w-12 h-[2px] bg-primary"></span>
            Лаптопи
          </h2>
          <p class="text-on-surface-variant mt-2">{count} продукта с летни отстъпки — налични за поръчка.</p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter">
{cards}
        </div>
      </div>
    </section>"""

page = TARGET.read_text(encoding="utf-8")
page = re.sub(
    r'    <section id="laptopi".*?</section>',
    catalog_section,
    page,
    count=1,
    flags=re.DOTALL,
)

page = re.sub(
    r'(<div class="text-technical-sm text-on-surface-variant font-label-caps mb-1">ЛАПТОПИ</div>\s*<div class="text-headline-md font-bold">)\d+(</div>)',
    rf"\g<1>{count}\g<2>",
    page,
    count=1,
)

TARGET.write_text(page, encoding="utf-8")
print(f"imported={count}")
