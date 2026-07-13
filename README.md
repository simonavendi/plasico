# Plasico Hot Summer Sale 2026 — Spatial Minimalism Redesign

Local redesign of the [Plasico Hot Summer Sale 2026](https://plasico.bg/hot-summer-sale-2026) campaign page.

**Live preview:** https://plasico.vercel.app/

## Source of truth

| File | Role |
|------|------|
| `plasico/plasico.bg/hot-summer-sale-2026.html` | Main redesign page — **do not overwrite with HTTrack** |
| `plasico/plasico.bg/category-map.json` | Category/subcategory accordion data |
| `plasico/plasico.bg/redesign/` | Hero background + local footer assets |
| `plasico/plasico.bg/scrape_live_campaign.py` | Sync products/prices from live plasico.bg |

## HTTrack protection

HTTrack at `plasico/` **must not mirror** `hot-summer-sale-2026.html` — it will replace the redesign with the vanilla mirrored page.

1. **Exclude rule** is set in `plasico/hts-cache/winprofile.ini`:
   `-*/hot-summer-sale-2026.html` (after the include lines for subcategory pages).
2. **Backup copy** of any HTTrack overwrite is kept as `hot-summer-sale-2026.httrack-overwrite.html`.
3. To refresh product data, run `python scrape_live_campaign.py` from `plasico/plasico.bg/` instead of re-mirroring the main page.

## Post-restore patches

After restoring `hot-summer-sale-2026.html` from git or Cursor history:

```bash
cd plasico/plasico.bg
python apply_ios_utility_bar.py      # iOS frosted utility bar
python move_subcategories_to_catalog.py  # subcategories in #laptopi filter panel
python scrape_live_campaign.py       # sync live products
```

## Deploy

- **GitHub:** https://github.com/simonavendi/plasico
- **Vercel:** project `plasico`, `outputDirectory` = `plasico/plasico.bg` (see `vercel.json`)

```bash
npx vercel --prod
```
