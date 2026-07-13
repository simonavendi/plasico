import html
import json
import re
from pathlib import Path

products_data = json.loads(Path(r"D:\Vibe\plasico\products.json").read_text(encoding="utf-8"))

def clean_price(value: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", value)).replace("€", "€").strip()

def short_title(title: str, limit: int = 72) -> str:
    return title if len(title) <= limit else title[: limit - 1] + "…"

def product_card(p: dict) -> str:
    price = clean_price(p["price"])
    old = clean_price(p["old_price"])
    badge = ""
    if p.get("flag"):
        badge = f'<div class="absolute top-4 right-4 px-3 py-1 bg-violet/10 text-violet border border-violet/20 rounded-full text-technical-sm font-bold">{html.escape(p["flag"])}</div>'
    elif old:
        badge = '<div class="absolute top-4 right-4 px-3 py-1 bg-teal/10 text-teal border border-teal/20 rounded-full text-technical-sm font-bold">ПРОМО</div>'

    old_price_html = ""
    if old:
        old_price_html = f'<p class="text-on-surface-variant text-body-sm line-through">{html.escape(old)}</p>'

    return f"""
<div class="group relative flex flex-col">
  <a href="{html.escape(p['url'])}" class="aspect-square bg-surface-container squircle intelligent-edge overflow-hidden mb-6 relative block">
    <img class="w-full h-full object-contain p-6 transition-transform duration-500 group-hover:scale-105" alt="{html.escape(p['title'])}" src="{html.escape(p['img'])}" loading="lazy"/>
    {badge}
    <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
      <span class="px-6 py-3 bg-white text-surface font-bold rounded-full text-body-sm">Виж продукта</span>
    </div>
  </a>
  <div class="flex justify-between items-start gap-4">
    <div class="min-w-0">
      <h4 class="font-headline-md text-headline-md font-bold leading-tight">{html.escape(short_title(p['title']))}</h4>
      {old_price_html}
    </div>
    <div class="text-secondary font-headline-md font-bold whitespace-nowrap">{html.escape(price)}</div>
  </div>
</div>"""

product_cards = "\n".join(product_card(p) for p in products_data["products"][:8])

page = f"""<!DOCTYPE html>
<html class="dark" lang="bg">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>Hot Summer Sale 2026 | Plasico.bg</title>
  <meta name="description" content="Hot Summer Sale 2026 — лаптопи, компютри, компоненти и аксесоари с ексклузивни летни цени в Plasico.bg"/>
  <link rel="shortcut icon" type="image/ico" href="https://static.plasico.bg/favicon.ico"/>
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet"/>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
  <script id="tailwind-config">
    tailwind.config = {{
      darkMode: "class",
      theme: {{
        extend: {{
          colors: {{
            primary: "#c9c4d5",
            secondary: "#ffb783",
            apricot: "#FB923C",
            teal: "#2DD4BF",
            violet: "#A78BFA",
            "deep-ink": "#0A0910",
            "edge-light": "rgba(255, 255, 255, 0.12)",
            background: "#141314",
            surface: "#141314",
            "surface-container": "#201f20",
            "surface-container-low": "#1c1b1c",
            "surface-container-lowest": "#0e0e0f",
            "surface-container-high": "#2b2a2b",
            "surface-variant": "#363435",
            "on-surface": "#e5e1e2",
            "on-surface-variant": "#c9c5cc",
            "on-secondary-container": "#451f00",
            "primary-container": "#12101c"
          }},
          spacing: {{
            "stack-lg": "32px",
            "stack-md": "16px",
            "stack-sm": "8px",
            "container-padding": "24px",
            gutter: "16px"
          }},
          fontSize: {{
            "headline-xl": ["40px", {{ lineHeight: "48px", letterSpacing: "-0.02em", fontWeight: "700" }}],
            "headline-lg": ["32px", {{ lineHeight: "40px", letterSpacing: "-0.01em", fontWeight: "600" }}],
            "headline-md": ["24px", {{ lineHeight: "32px", letterSpacing: "-0.01em", fontWeight: "600" }}],
            "body-lg": ["18px", {{ lineHeight: "28px", fontWeight: "400" }}],
            "body-md": ["16px", {{ lineHeight: "24px", fontWeight: "400" }}],
            "body-sm": ["14px", {{ lineHeight: "20px", fontWeight: "400" }}],
            "technical-md": ["14px", {{ lineHeight: "20px", letterSpacing: "-0.01em", fontWeight: "500" }}],
            "technical-sm": ["12px", {{ lineHeight: "16px", fontWeight: "500" }}],
            "label-caps": ["11px", {{ lineHeight: "16px", letterSpacing: "0.05em", fontWeight: "700" }}]
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ background-color: #141314; color: #e5e1e2; overflow-x: hidden; }}
    .mesh-gradient-text {{
      background: linear-gradient(90deg, #A78BFA, #FB923C, #2DD4BF, #A78BFA);
      background-size: 200% auto;
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      animation: shine 8s linear infinite;
    }}
    @keyframes shine {{ to {{ background-position: 200% center; }} }}
    .bento-card {{
      position: relative; overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.12);
      transition: all 0.5s cubic-bezier(0.19, 1, 0.22, 1);
    }}
    .bento-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255, 255, 255, 0.2);
    }}
    .intelligent-edge {{
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 2px 0 0 rgba(255, 255, 255, 0.05) inset;
    }}
    .glass-island {{
      background: rgba(14, 14, 15, 0.7);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
    }}
    .squircle {{ border-radius: 32px; }}
    .material-symbols-outlined {{ font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24; }}
    .custom-scrollbar::-webkit-scrollbar {{ width: 6px; }}
    .custom-scrollbar::-webkit-scrollbar-track {{ background: #0A0910; }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{ background: #48464c; border-radius: 10px; }}
    .hero-bg {{
      background:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(167, 139, 250, 0.25), transparent),
        radial-gradient(ellipse 60% 40% at 80% 60%, rgba(251, 146, 60, 0.15), transparent),
        radial-gradient(ellipse 50% 30% at 10% 80%, rgba(45, 212, 191, 0.12), transparent),
        #0A0910;
    }}
  </style>
</head>
<body class="font-body-md selection:bg-apricot/30 custom-scrollbar">
  <header class="fixed top-0 w-full z-50 bg-surface/80 backdrop-blur-xl border-b border-edge-light shadow-[0_2px_0_0_rgba(255,255,255,0.1)_inset,0_8px_32px_rgba(0,0,0,0.4)]">
    <nav class="flex justify-between items-center h-20 px-container-padding max-w-[1440px] mx-auto">
      <a href="https://plasico.bg/" class="flex items-center gap-3">
        <img src="https://static.plasico.bg/css/campaign/hot-summer-sale-2026/logo-plasico.svg" alt="Plasico.bg" class="h-10 w-auto"/>
      </a>
      <div class="hidden md:flex items-center gap-stack-lg">
        <a class="font-body-sm text-primary border-b-2 border-primary pb-1" href="#laptopi">Лаптопи</a>
        <a class="font-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="https://plasico.bg/hot-summer-sale-2026/computers">Компютри</a>
        <a class="font-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="https://plasico.bg/hot-summer-sale-2026/components">Компоненти</a>
        <a class="font-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="https://plasico.bg/hot-summer-sale-2026/monitors">Монитори</a>
        <a class="font-body-sm text-on-surface-variant hover:text-on-surface transition-colors" href="https://plasico.bg/promotsii">Промоции</a>
      </div>
      <div class="flex items-center gap-stack-md">
        <div class="hidden lg:flex items-center bg-surface-container-high rounded-full px-4 py-1.5 border border-edge-light">
          <span class="material-symbols-outlined text-on-surface-variant text-[20px]">search</span>
          <span class="text-on-surface-variant text-technical-sm ml-2">Търси продукт...</span>
          <span class="ml-8 px-1.5 py-0.5 rounded bg-surface-variant text-[10px] font-bold text-on-surface-variant border border-edge-light">⌘ K</span>
        </div>
        <a href="https://plasico.bg/поръчка" class="material-symbols-outlined text-on-surface p-2 hover:bg-white/5 rounded-full transition-all duration-300">shopping_cart</a>
        <a href="tel:070020810" class="hidden sm:flex items-center gap-2 text-technical-sm text-on-surface-variant hover:text-on-surface transition-colors">
          <span class="material-symbols-outlined text-[20px]">call</span>
          0700 20 810
        </a>
      </div>
    </nav>
  </header>

  <main class="pt-20">
    <section class="relative min-h-[85vh] flex flex-col items-center justify-center text-center px-container-padding overflow-hidden hero-bg">
      <div class="absolute inset-0 opacity-30">
        <img src="https://static.plasico.bg/css/campaign/hot-summer-sale-2026/header_desktop.webp" alt="" class="w-full h-full object-cover object-top"/>
      </div>
      <div class="relative z-10 max-w-5xl">
        <span class="inline-block px-4 py-1 rounded-full border border-apricot/30 bg-apricot/10 text-apricot font-technical-md text-technical-md mb-8">HOT SUMMER SALE 2026</span>
        <h1 class="font-headline-xl text-[clamp(3rem,10vw,7.5rem)] leading-[0.9] font-extrabold tracking-tighter mesh-gradient-text mb-8">
          ЛЯТНИ<br/>ЦЕНИ.
        </h1>
        <p class="font-body-lg text-body-lg text-on-surface-variant max-w-2xl mx-auto mb-12">
          Ексклузивни оферти за лаптопи, компютри, компоненти и периферия. Професионална техника с летни отстъпки — само в Plasico.bg.
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-stack-md">
          <a href="#laptopi" class="group relative px-10 py-5 bg-on-surface text-surface font-bold rounded-full overflow-hidden hover:scale-105 active:scale-95 transition-all duration-300 shadow-[0_0_20px_rgba(255,255,255,0.2)]">
            <span class="relative z-10">Разгледай офертите</span>
            <div class="absolute inset-0 bg-gradient-to-r from-violet via-apricot to-teal opacity-0 group-hover:opacity-20 transition-opacity"></div>
          </a>
          <a href="https://plasico.bg/magazini" class="px-10 py-5 border border-edge-light bg-surface/40 backdrop-blur-md text-on-surface font-bold rounded-full hover:bg-surface-variant transition-all duration-300">
            Намери магазин
          </a>
        </div>
      </div>
      <div class="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-wrap justify-center gap-8 md:gap-12 text-left px-4">
        <div>
          <div class="text-technical-sm text-on-surface-variant font-label-caps mb-1">КАТЕГОРИИ</div>
          <div class="text-headline-md font-bold">18</div>
        </div>
        <div class="w-[1px] h-12 bg-edge-light hidden sm:block"></div>
        <div>
          <div class="text-technical-sm text-on-surface-variant font-label-caps mb-1">ПРОДУКТИ</div>
          <div class="text-headline-md font-bold">500+</div>
        </div>
        <div class="w-[1px] h-12 bg-edge-light hidden sm:block"></div>
        <div>
          <div class="text-technical-sm text-on-surface-variant font-label-caps mb-1">ТЕЛЕФОН</div>
          <div class="text-headline-md font-bold">0700 20 810</div>
        </div>
      </div>
    </section>

    <section class="py-stack-lg px-container-padding max-w-[1440px] mx-auto">
      <h2 class="font-headline-lg text-headline-lg mb-stack-lg flex items-center gap-4">
        <span class="w-12 h-[2px] bg-primary"></span>
        Категории
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        <a href="#laptopi" class="md:col-span-8 group bento-card squircle h-[480px] bg-deep-ink block">
          <div class="absolute inset-0 z-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-105" style="background-image:url('https://static.plasico.bg/thumbs/10/250924102012250408153346asus-tuf-a16-fa607nu-1.webp')"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-deep-ink via-deep-ink/40 to-transparent z-10"></div>
          <div class="absolute bottom-0 left-0 p-10 z-20 w-full flex justify-between items-end">
            <div>
              <h3 class="font-headline-lg font-bold mb-2">Лаптопи</h3>
              <p class="text-on-surface-variant max-w-md">Гейминг, бизнес и ултрапортативни модели с летни отстъпки.</p>
            </div>
            <span class="w-16 h-16 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center group-hover:bg-primary group-hover:text-surface transition-all">
              <span class="material-symbols-outlined">arrow_forward</span>
            </span>
          </div>
        </a>
        <a href="https://plasico.bg/hot-summer-sale-2026/computers" class="md:col-span-4 group bento-card squircle h-[480px] bg-surface-container block">
          <div class="absolute inset-0 z-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-105" style="background-image:url('https://static.plasico.bg/thumbs/10/250623091441asus-strix-g16-g615lp-1.webp')"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-deep-ink/90 to-transparent z-10"></div>
          <div class="absolute bottom-0 left-0 p-10 z-20">
            <h3 class="font-headline-md font-bold mb-2">Компютри</h3>
            <p class="text-on-surface-variant text-sm">Настолни и All-in-One системи.</p>
          </div>
        </a>
        <a href="https://plasico.bg/hot-summer-sale-2026/components" class="md:col-span-5 group bento-card squircle h-[360px] bg-surface-container-low block">
          <div class="absolute inset-0 z-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-105 opacity-60" style="background-image:url('https://static.plasico.bg/thumbs/10/251014125303asus-tuf-gaming-f16-2025-fx608jpr-1.webp')"></div>
          <div class="absolute inset-0 bg-gradient-to-r from-deep-ink/95 to-transparent z-10"></div>
          <div class="absolute inset-y-0 left-0 p-10 z-20 flex flex-col justify-center max-w-[280px]">
            <h3 class="font-headline-md font-bold mb-2">Компоненти</h3>
            <p class="text-on-surface-variant text-sm">GPU, CPU, RAM, SSD и още.</p>
          </div>
        </a>
        <div class="md:col-span-7 group bento-card squircle h-[360px] bg-primary-container flex overflow-hidden">
          <div class="w-full md:w-1/2 p-10 flex flex-col justify-center">
            <h3 class="font-headline-md font-bold mb-2">Още категории</h3>
            <p class="text-on-surface-variant mb-6">Монитори, периферия, мрежи, UPS и употребявана техника.</p>
            <div class="flex flex-wrap gap-3">
              <a href="https://plasico.bg/hot-summer-sale-2026/monitors" class="px-4 py-2 bg-surface-variant rounded-full text-technical-sm hover:bg-apricot/20 transition-colors">Монитори</a>
              <a href="https://plasico.bg/hot-summer-sale-2026/accessories" class="px-4 py-2 bg-surface-variant rounded-full text-technical-sm hover:bg-apricot/20 transition-colors">Аксесоари</a>
              <a href="https://plasico.bg/hot-summer-sale-2026/used" class="px-4 py-2 bg-surface-variant rounded-full text-technical-sm hover:bg-apricot/20 transition-colors">Втора ръка</a>
            </div>
          </div>
          <div class="hidden md:block w-1/2 bg-cover bg-center" style="background-image:url('https://static.plasico.bg/thumbs/10/240722175324240516125332apple-macbook-air-15-2024-m3-540448.png')"></div>
        </div>
      </div>
    </section>

    <section id="laptopi" class="py-stack-lg bg-surface-container-lowest px-container-padding">
      <div class="max-w-[1440px] mx-auto">
        <div class="flex justify-between items-end mb-stack-lg gap-4 flex-wrap">
          <div>
            <h2 class="font-headline-lg font-bold">Избрани лаптопи</h2>
            <p class="text-on-surface-variant">Най-добрите летни оферти — налични за поръчка.</p>
          </div>
          <a href="https://plasico.bg/hot-summer-sale-2026" class="flex items-center gap-2 text-primary font-technical-md hover:underline">
            ВИЖ ВСИЧКИ <span class="material-symbols-outlined">north_east</span>
          </a>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter">
          {product_cards}
        </div>
      </div>
    </section>

    <section class="py-[120px] px-container-padding relative overflow-hidden">
      <div class="max-w-4xl mx-auto glass-island squircle p-10 md:p-16 intelligent-edge text-center">
        <h2 class="font-headline-xl text-headline-xl mb-6">Абонирай се за офертите</h2>
        <p class="text-on-surface-variant text-body-lg mb-10 max-w-xl mx-auto">
          Бъди първият, който научава за нови промоции и ексклузивни кодове за отстъпка.
        </p>
        <form class="flex flex-col md:flex-row gap-4 max-w-lg mx-auto" onsubmit="event.preventDefault();">
          <input class="flex-1 bg-surface-container-lowest border border-edge-light rounded-full px-8 py-4 focus:ring-2 focus:ring-apricot focus:border-transparent transition-all outline-none text-on-surface" placeholder="Въведи имейл адрес" type="email"/>
          <button class="px-10 py-4 bg-apricot text-on-secondary-container font-bold rounded-full hover:scale-105 active:scale-95 transition-all shadow-lg">
            АБОНИРАЙ СЕ
          </button>
        </form>
        <div class="mt-8 flex flex-wrap justify-center gap-6 md:gap-8 text-on-surface-variant text-technical-sm font-label-caps">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-[16px]">verified</span>
            ЕКСКЛУЗИВНИ КОДОВЕ
          </div>
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-[16px]">notifications_active</span>
            РАННИ ИЗВЕСТИЯ
          </div>
        </div>
      </div>
    </section>
  </main>

  <footer class="bg-deep-ink w-full rounded-t-xl border-t border-edge-light bg-surface-container-lowest shadow-[0_-4px_24px_rgba(0,0,0,0.5)]">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-stack-lg p-container-padding max-w-7xl mx-auto">
      <div>
        <img src="https://static.plasico.bg/css/campaign/hot-summer-sale-2026/logo-plasico.svg" alt="Plasico.bg" class="h-10 mb-6"/>
        <p class="font-body-sm text-on-surface-variant">
          Магазин за компютърна техника с над 20 години опит. Качество, конкурентни цени и професионален сервиз.
        </p>
      </div>
      <div>
        <h5 class="text-on-surface font-bold font-technical-md mb-6 uppercase tracking-wider">Полезно</h5>
        <ul class="space-y-4">
          <li><a class="font-body-sm text-on-surface-variant hover:text-apricot transition-colors" href="https://plasico.bg/magazini">Магазини</a></li>
          <li><a class="font-body-sm text-on-surface-variant hover:text-apricot transition-colors" href="https://plasico.bg/serviz">Сервиз</a></li>
          <li><a class="font-body-sm text-on-surface-variant hover:text-apricot transition-colors" href="https://plasico.bg/kontakti">Контакти</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-on-surface font-bold font-technical-md mb-6 uppercase tracking-wider">Компания</h5>
        <ul class="space-y-4">
          <li><a class="font-body-sm text-on-surface-variant hover:text-apricot transition-colors" href="https://plasico.bg/za-nas">За нас</a></li>
          <li><a class="font-body-sm text-on-surface-variant hover:text-apricot transition-colors" href="https://plasico.bg/blog/">Блог</a></li>
          <li><a class="font-body-sm text-on-surface-variant hover:text-apricot transition-colors" href="https://plasico.bg/promotsii">Промоции</a></li>
        </ul>
      </div>
      <div>
        <h5 class="text-on-surface font-bold font-technical-md mb-6 uppercase tracking-wider">Свържи се</h5>
        <p class="text-on-surface-variant text-body-sm mb-4">0700 20 810</p>
        <div class="flex gap-4">
          <a href="https://plasico.bg/" class="w-10 h-10 rounded-full bg-surface-container-high border border-edge-light flex items-center justify-center text-on-surface hover:text-apricot hover:border-apricot transition-all">
            <span class="material-symbols-outlined text-[20px]">public</span>
          </a>
          <a href="https://plasico.bg/kontakti" class="w-10 h-10 rounded-full bg-surface-container-high border border-edge-light flex items-center justify-center text-on-surface hover:text-apricot hover:border-apricot transition-all">
            <span class="material-symbols-outlined text-[20px]">mail</span>
          </a>
        </div>
      </div>
    </div>
    <div class="border-t border-edge-light py-8 text-center">
      <p class="font-body-sm text-on-surface-variant">© 2026 Plasico.bg — Hot Summer Sale 2026</p>
    </div>
  </footer>

  <script>
    window.addEventListener('keydown', (e) => {{
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {{
        e.preventDefault();
        window.location.href = 'https://plasico.bg/tyrsene';
      }}
    }});

    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.classList.add('opacity-100');
          entry.target.classList.remove('opacity-0', 'translate-y-10');
        }}
      }});
    }}, {{ threshold: 0.1 }});

    document.querySelectorAll('.bento-card, #laptopi .group').forEach(el => {{
      el.classList.add('transition-all', 'duration-700', 'opacity-0', 'translate-y-10');
      observer.observe(el);
    }});
  </script>
</body>
</html>
"""

out_path = Path(r"D:\Vibe\plasico\plasico\plasico.bg\hot-summer-sale-2026.html")
backup_path = Path(r"D:\Vibe\plasico\plasico\plasico.bg\hot-summer-sale-2026.original.html")

if not backup_path.exists():
    backup_path.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")

out_path.write_text(page, encoding="utf-8")
print("written", out_path)
