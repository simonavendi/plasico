#!/usr/bin/env python3
"""Move subcategory chips from #category-icon-grid to #laptopi catalog filter panel."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TARGET = Path(__file__).parent / "hot-summer-sale-2026.html"


def require_redesign(html: str) -> None:
    markers = ("catalog-filter-panel", "category-icon-grid", "renderCategoryNavigation")
    if not all(m in html for m in markers):
        raise SystemExit(
            "hot-summer-sale-2026.html does not contain the redesigned catalog UI.\n"
            "Restore the redesign from Cursor Local History / Timeline first "
            "(HTTrack re-mirror at 17:57 may have overwritten it)."
        )


def patch_css(html: str) -> str:
    hide_rule = """
    /* Subcategories render in #catalog-subcategory-filter only */
    #category-icon-grid .category-subchips {
      display: none !important;
    }
    #catalog-subcategory-filter {
      display: none;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 16px;
      padding: 12px 14px;
      border-radius: 16px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(32, 31, 32, 0.55);
    }
    #catalog-subcategory-filter.is-visible {
      display: flex;
    }
    #catalog-subcategory-filter .catalog-subcategory-label {
      flex: 0 0 100%;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #938f96;
      margin-bottom: 2px;
    }
    #catalog-subcategory-filter .category-subchip.is-active {
      border-color: rgba(251, 146, 60, 0.55);
      color: #FB923C;
      background: rgba(251, 146, 60, 0.12);
    }
"""

    if "#catalog-subcategory-filter" in html:
        return html

    return html.replace(
        ".category-icon-cell.is-expanded .category-subchips { display: flex; }",
        ".category-icon-cell.is-expanded .category-subchips { display: none !important; }",
        1,
    ).replace(
        "</style>",
        hide_rule + "\n  </style>",
        1,
    )


def patch_html(html: str) -> str:
    if 'id="catalog-subcategory-filter"' in html:
        return html

    needle = '<div id="catalog-filters"'
    if needle not in html:
        raise SystemExit("Could not find #catalog-filters in filter panel HTML.")

    insert = (
        '              <div id="catalog-subcategory-filter" class="catalog-subcategory-filter" '
        'role="group" aria-label="Подкатегории" hidden></div>\n                '
    )

  # Place above КАТЕГОРИИ column — first filter column in panel grid
    pattern = (
        r'(<div class="grid[^"]*"[^>]*>\s*<div>\s*'
        r'<p class="[^"]*">КАТЕГОРИИ</p>\s*)'
    )
    patched, n = re.subn(pattern, insert + r"\1", html, count=1)
    if n:
        return patched

    return html.replace(needle, insert + needle, 1)


def patch_js(html: str) -> str:
    if "function renderCatalogSubcategoryFilter" in html:
        return html

    helper = r'''
    let activeCategoryId = null;
    let catalogSubcategoryFilter = null;

    function getCatalogSubcategoryFilterEl() {
      if (!catalogSubcategoryFilter) {
        catalogSubcategoryFilter = document.getElementById('catalog-subcategory-filter');
      }
      return catalogSubcategoryFilter;
    }

    function renderCatalogSubcategoryFilter(category, options = {}) {
      const wrap = getCatalogSubcategoryFilterEl();
      if (!wrap || !category) return;

      const subs = getCategorySubs(category);
      activeCategoryId = category.id;
      wrap.innerHTML = '';
      wrap.hidden = subs.length === 0;
      wrap.classList.toggle('is-visible', subs.length > 0);

      if (subs.length === 0) return;

      const label = document.createElement('span');
      label.className = 'catalog-subcategory-label';
      label.textContent = category.name;
      wrap.appendChild(label);

      subs.forEach(sub => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'category-subchip' + ((sub.action === 'external' || category.external) ? ' category-subchip--external' : '');
        if (sub.filterTag) chip.dataset.filter = sub.filterTag;
        chip.textContent = sub.name;
        chip.addEventListener('click', (e) => {
          e.stopPropagation();
          handleSubcategoryAction(sub, category, options.applyFilterFn || null);
        });
        wrap.appendChild(chip);
      });

      syncCategoryExpansionUI(category.id, options);
    }

    function syncCategoryExpansionUI(categoryId, options = {}) {
      const grid = document.getElementById('category-icon-grid');
      if (grid) {
        grid.querySelectorAll('.category-icon-cell').forEach(cell => {
          cell.classList.toggle('is-expanded', cell.dataset.categoryId === categoryId);
        });
      }

      if (typeof options.syncFilterGroups === 'function') {
        options.syncFilterGroups(categoryId);
      } else if (window.__syncFilterGroupsForCategory) {
        window.__syncFilterGroupsForCategory(categoryId);
      }
    }

    function clearCatalogSubcategoryFilter() {
      activeCategoryId = null;
      const wrap = getCatalogSubcategoryFilterEl();
      if (!wrap) return;
      wrap.innerHTML = '';
      wrap.hidden = true;
      wrap.classList.remove('is-visible');
      const grid = document.getElementById('category-icon-grid');
      if (grid) grid.querySelectorAll('.category-icon-cell.is-expanded').forEach(c => c.classList.remove('is-expanded'));
    }
'''

    html = html.replace(
        "    function handleSubcategoryAction(sub, category, applyFilterFn) {",
        helper + "\n    function handleSubcategoryAction(sub, category, applyFilterFn) {",
        1,
    )

    # Stop rendering subchips under icon cards
    html = re.sub(
        r"const subWrap = document\.createElement\('div'\);\s*"
        r"subWrap\.className = 'category-subchips';[\s\S]*?"
        r"if \(subs\.length > 0\) cell\.appendChild\(subWrap\);",
        "/* subcategories render in #catalog-subcategory-filter */",
        html,
        count=1,
    )

    html = html.replace(
        """        btn.addEventListener('click', (e) => {
          e.preventDefault();
          if (subs.length > 0) {
            const wasExpanded = cell.classList.contains('is-expanded');
            grid.querySelectorAll('.category-icon-cell.is-expanded').forEach(c => c.classList.remove('is-expanded'));
            if (!wasExpanded) cell.classList.add('is-expanded');
          }
          if (applyFilterFn) applyFilterFn(category.dataFilter, { scroll: true });
        });""",
        """        btn.addEventListener('click', (e) => {
          e.preventDefault();
          const wasExpanded = cell.classList.contains('is-expanded');
          grid.querySelectorAll('.category-icon-cell.is-expanded').forEach(c => c.classList.remove('is-expanded'));
          if (!wasExpanded) cell.classList.add('is-expanded');
          renderCatalogSubcategoryFilter(category, { applyFilterFn });
          if (applyFilterFn) applyFilterFn(category.dataFilter, { scroll: true });
        });""",
        1,
    )

    # Filter accordion parent click — show subs in catalog row
    html = html.replace(
        """          parentBtn.addEventListener('click', () => {
            if (hasSubs) {
              const wasOpen = group.classList.contains('is-open');
              filterGroups.forEach(g => g.classList.remove('is-open'));
              if (!wasOpen) group.classList.add('is-open');
            }
            applyFilter(parentFilterId, { scroll: true });
          });""",
        """          parentBtn.addEventListener('click', () => {
            if (hasSubs) {
              const wasOpen = group.classList.contains('is-open');
              filterGroups.forEach(g => g.classList.remove('is-open'));
              if (!wasOpen) group.classList.add('is-open');
            }
            renderCatalogSubcategoryFilter(category, {
              applyFilterFn: applyFilter,
              syncFilterGroups: (catId) => {
                filterGroups.forEach(g => {
                  g.classList.toggle('is-open', g.dataset.categoryId === catId);
                });
              }
            });
            applyFilter(parentFilterId, { scroll: true });
          });""",
        1,
    )

    # setPillState — also refresh catalog subchips for active parent
    html = html.replace(
        """        filterGroups.forEach(group => {
          group.classList.toggle('is-open', group === expandedGroup);
        });
      }""",
        """        filterGroups.forEach(group => {
          group.classList.toggle('is-open', group === expandedGroup);
        });

        if (expandedGroup && categoryMap?.categories) {
          const cat = categoryMap.categories.find(c => c.id === expandedGroup.dataset.categoryId);
          if (cat) {
            renderCatalogSubcategoryFilter(cat, {
              applyFilterFn: applyFilter,
              syncFilterGroups: (catId) => {
                filterGroups.forEach(g => {
                  g.classList.toggle('is-open', g.dataset.categoryId === catId);
                });
              }
            });
          }
        }
      }""",
        1,
    )

    # Expose sync helper for icon grid
    html = html.replace(
        "      buildCategoryFilterPanel();",
        "      window.__syncFilterGroupsForCategory = (categoryId) => {\n"
        "        filterGroups.forEach(g => g.classList.toggle('is-open', g.dataset.categoryId === categoryId));\n"
        "      };\n      buildCategoryFilterPanel();",
        1,
    )

    return html


def main() -> None:
    html = TARGET.read_text(encoding="utf-8")
    require_redesign(html)
    html = patch_css(html)
    html = patch_html(html)
    html = patch_js(html)
    TARGET.write_text(html, encoding="utf-8")
    print(f"Patched {TARGET.name}: subcategories now render in #catalog-subcategory-filter inside #laptopi.")
    print("Removed from icon grid: .category-subchips under .category-icon-cell.is-expanded")


if __name__ == "__main__":
    main()
