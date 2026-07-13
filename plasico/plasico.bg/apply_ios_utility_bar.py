#!/usr/bin/env python3
"""Apply iOS-inspired utility bar redesign to hot-summer-sale-2026.html."""

from pathlib import Path

TARGET = Path(__file__).parent / "hot-summer-sale-2026.html"

OLD_UTILITY_START = '    <!-- Top utility strip -->'
OLD_UTILITY_END = '    <!-- Main header row -->'

IOS_CSS_BLOCK = """    .header-utility-bar {
      font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      background: rgba(14, 14, 15, 0.72);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
    }
    @supports (backdrop-filter: blur(12px)) {
      .header-utility-bar {
        background: rgba(14, 14, 15, 0.55);
      }
    }
    .header-utility-bar-inner {
      font-size: 12.5px;
      letter-spacing: -0.01em;
      line-height: 1.25;
      color: rgba(201, 197, 204, 0.82);
    }
    .header-utility-link {
      display: inline-flex;
      align-items: center;
      padding: 0.3125rem 0.625rem;
      border-radius: 9999px;
      color: inherit;
      text-decoration: none;
      white-space: nowrap;
      font-weight: 500;
      transition: color 0.2s ease, background-color 0.2s ease;
    }
    .header-utility-link:hover {
      color: #FB923C;
      background-color: rgba(255, 255, 255, 0.06);
    }
    .header-utility-link:active {
      background-color: rgba(255, 255, 255, 0.08);
    }
    .header-utility-link:focus-visible {
      outline: 2px solid rgba(251, 146, 60, 0.65);
      outline-offset: 2px;
    }
    .header-utility-link--icon {
      padding: 0.375rem;
      margin-left: -0.375rem;
    }
    .header-utility-link--icon .material-symbols-outlined,
    .header-utility-home-icon {
      font-size: 18px;
    }
    .header-utility-bar-auth {
      display: flex;
      align-items: center;
      gap: 0.375rem;
      font-size: 12px;
      letter-spacing: -0.01em;
    }
    .header-utility-bar-signin,
    .header-utility-bar-signup {
      text-decoration: none;
      padding: 0.25rem 0.5rem;
      border-radius: 9999px;
      transition: color 0.2s ease, background-color 0.2s ease;
    }
    .header-utility-bar-signin {
      font-weight: 500;
      color: rgba(229, 225, 226, 0.72);
    }
    .header-utility-bar-signin:hover {
      color: #fff;
      background-color: rgba(255, 255, 255, 0.06);
    }
    .header-utility-bar-signup {
      font-weight: 600;
      color: rgba(229, 225, 226, 0.92);
    }
    .header-utility-bar-signup:hover {
      color: #FB923C;
      background-color: rgba(255, 255, 255, 0.06);
    }
    .header-utility-bar-sep {
      width: 1px;
      height: 11px;
      background: rgba(255, 255, 255, 0.12);
      flex-shrink: 0;
    }
    .header-utility-bar-via {
      font-size: 11px;
      font-weight: 400;
      color: rgba(201, 197, 204, 0.42);
      letter-spacing: -0.005em;
    }
    .header-utility-social {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 1.625rem;
      height: 1.625rem;
      border-radius: 9999px;
      color: rgba(201, 197, 204, 0.68);
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.06);
      transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
    }
    .header-utility-social:hover {
      color: #FB923C;
      background: rgba(255, 255, 255, 0.08);
      border-color: rgba(251, 146, 60, 0.22);
    }
    .header-utility-social .header-social-icon {
      width: 13px;
      height: 13px;
    }"""

NEW_UTILITY_HTML = """    <!-- Top utility strip — iOS-inspired -->
    <div class="header-utility-bar border-b border-white/5">
      <div class="header-utility-bar-inner max-w-[1440px] mx-auto px-container-padding h-10 flex items-center justify-between gap-5">
        <nav class="flex items-center gap-0.5 min-w-0" aria-label="Услуги">
          <a href="https://plasico.bg/" class="header-utility-link header-utility-link--icon header-utility-home shrink-0" aria-label="Начало">
            <span class="material-symbols-outlined header-utility-home-icon" aria-hidden="true">home</span>
          </a>
          <ul class="hidden sm:flex items-center gap-0.5 overflow-x-auto">
            <li><a href="https://plasico.bg/magazini" class="header-utility-link">Магазини</a></li>
            <li><a href="https://plasico.bg/serviz" class="header-utility-link">Сервиз</a></li>
            <li><a href="https://plasico.bg/za-nas" class="header-utility-link">За нас</a></li>
            <li><a href="https://plasico.bg/blog/" class="header-utility-link">Блог</a></li>
            <li><a href="https://plasico.bg/kontakti" class="header-utility-link">Контакти</a></li>
          </ul>
        </nav>
        <div class="header-utility-bar-auth shrink-0">
          <a href="https://plasico.bg/account" class="header-utility-bar-signin">Вход</a>
          <span class="header-utility-bar-sep hidden sm:inline" aria-hidden="true"></span>
          <a href="https://plasico.bg/account" class="header-utility-bar-signup hidden sm:inline">Регистрация</a>
          <span class="header-utility-bar-via hidden md:inline">или чрез</span>
          <a href="https://plasico.bg/account" class="header-utility-social hidden md:inline-flex" title="Facebook" aria-label="Вход с Facebook">
            <svg class="header-social-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M14 13.5h2.5l1-4H14v-2c0-1.1.9-2 2-2h2V3h-2.5C13.8 3 12 4.8 12 7v2.5H9v4h3V21h2v-7.5z"/></svg>
          </a>
          <a href="https://plasico.bg/account" class="header-utility-social hidden md:inline-flex" title="Google" aria-label="Вход с Google">
            <svg class="header-social-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12.545 10.239v3.821h5.445c-.712 2.315-2.647 3.972-5.445 3.972-3.332 0-6.033-2.701-6.033-6.032s2.701-6.032 6.033-6.032c1.498 0 2.866.549 3.921 1.453l2.814-2.814C17.503 2.988 15.139 2 12.545 2 7.021 2 2.543 6.477 2.543 12s4.478 10 10.002 10c8.396 0 10.249-7.85 9.426-11.748l-9.426-.013z"/></svg>
          </a>
        </div>
      </div>
    </div>

"""

OFFSET_REPLACEMENTS = [
    ("--site-header-offset: 9.5rem;", "--site-header-offset: 9.75rem;"),
    ("--site-header-offset: 6.5rem;", "--site-header-offset: 6.75rem;"),
    ("--site-header-offset: 7rem;", "--site-header-offset: 7.25rem;"),
    ("--site-header-offset: 7.25rem;", "--site-header-offset: 7.5rem;"),
    ("--site-header-offset: 9.75rem;", "--site-header-offset: 10rem;"),
    ("--site-header-offset: 6.75rem;", "--site-header-offset: 7rem;"),
]


def main() -> None:
    html = TARGET.read_text(encoding="utf-8")
    if "site-header" not in html:
        raise SystemExit(
            "ERROR: hot-summer-sale-2026.html has no #site-header — "
            "restore the redesigned page first, then re-run this script."
        )

    start = html.find(OLD_UTILITY_START)
    end = html.find(OLD_UTILITY_END)
    if start == -1 or end == -1 or end <= start:
        raise SystemExit("ERROR: Could not locate utility strip block in HTML.")

    html = html[:start] + NEW_UTILITY_HTML + html[end:]

    if ".header-utility-bar {" not in html:
        anchor = ".header-search-pill {"
        if anchor not in html:
            anchor = ".header-utility-item {"
        if anchor in html:
            html = html.replace(anchor, IOS_CSS_BLOCK + "\n    " + anchor, 1)
        else:
            style_end = html.find("</style>")
            if style_end != -1:
                html = html[:style_end] + "    " + IOS_CSS_BLOCK + "\n  " + html[style_end:]
    else:
        # Refresh iOS block if partially present
        pass

    for old, new in OFFSET_REPLACEMENTS:
        if old in html and new not in html:
            html = html.replace(old, new, 1)

    # Ensure home icon minimal weight if block exists
    if "header-utility-home-icon" in html and "'wght' 250" not in html:
        home_icon_css = """    .header-utility-home-icon {
      font-family: 'Material Symbols Outlined' !important;
      font-variation-settings: 'FILL' 0, 'wght' 250, 'GRAD' 0, 'opsz' 20;
    }"""
        if home_icon_css.strip() not in html:
            html = html.replace(
                ".header-utility-social .header-social-icon {",
                home_icon_css + "\n    .header-utility-social .header-social-icon {",
                1,
            )

    TARGET.write_text(html, encoding="utf-8")
    print("OK: iOS utility bar applied to", TARGET)


if __name__ == "__main__":
    main()
