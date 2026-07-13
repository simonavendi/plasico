#!/usr/bin/env python3
"""Replay StrReplace edits on hot-summer-sale-2026.html from agent transcripts."""

from __future__ import annotations

import json
import glob
import re
from pathlib import Path

TARGET_NAME = "hot-summer-sale-2026.html"
TRANSCRIPT_GLOB = r"C:\Users\PC\.cursor\projects\d-Vibe-plasico\agent-transcripts\**\*.jsonl"
HTML_PATH = Path(r"D:\Vibe\plasico\plasico\plasico.bg\hot-summer-sale-2026.html")


def collect_ops() -> list[dict]:
    ops: list[dict] = []
    for path in sorted(glob.glob(TRANSCRIPT_GLOB, recursive=True)):
        p = Path(path)
        mtime = p.stat().st_mtime
        with open(p, encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                if TARGET_NAME not in line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                content = obj.get("message", {}).get("content", [])
                if isinstance(content, str):
                    continue
                for block in content:
                    if block.get("type") != "tool_use":
                        continue
                    if block.get("name") != "StrReplace":
                        continue
                    inp = block.get("input", {})
                    fp = inp.get("path", "").replace("\\", "/")
                    if not fp.endswith(TARGET_NAME):
                        continue
                    old = inp.get("old_string")
                    new = inp.get("new_string")
                    if not old or new is None:
                        continue
                    ops.append(
                        {
                            "file": str(p),
                            "mtime": mtime,
                            "line": line_no,
                            "old": old,
                            "new": new,
                        }
                    )
    ops.sort(key=lambda o: (o["mtime"], o["line"]))
    return ops


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    ops = collect_ops()
    applied = 0
    skipped = 0
    failed: list[str] = []

    for i, op in enumerate(ops):
        if op["old"] not in html:
            skipped += 1
            continue
        count = html.count(op["old"])
        if count != 1:
            skipped += 1
            failed.append(f"#{i+1} non-unique ({count}x) in {Path(op['file']).name}:{op['line']}")
            continue
        html = html.replace(op["old"], op["new"], 1)
        applied += 1

    HTML_PATH.write_text(html, encoding="utf-8")
    lines = html.count("\n") + 1
    markers = {
        "catalog-filter-panel": "catalog-filter-panel" in html,
        "category-icon-grid": "category-icon-grid" in html,
        "product-grid": "product-grid" in html,
        "site-header": "site-header" in html,
        "renderCategoryNavigation": "renderCategoryNavigation" in html,
    }
    print(f"ops_total={len(ops)} applied={applied} skipped={skipped}")
    print(f"lines={lines} bytes={len(html)}")
    print("markers:", markers)
    if failed:
        print("failed_samples:")
        for f in failed[:15]:
            print(" ", f)


if __name__ == "__main__":
    main()
