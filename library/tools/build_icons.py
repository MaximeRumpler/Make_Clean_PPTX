#!/usr/bin/env python3
"""Bundle the Lucide icon set into the skill.

    python library/tools/build_icons.py <path to lucide repo>

Writes skills/make-clean-pptx/assets/icons/
  lucide.json      {name: {"svg": "<svg…>", "tags": [...], "categories": [...]}}
  icons.csv        name;categories;tags  (human-readable index, same content)
  LICENSE-lucide.txt
One JSON file instead of ~1,900 SVG files keeps the skill folder light and easy to copy.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEST = REPO / "skills" / "make-clean-pptx" / "assets" / "icons"


def compact(svg: str) -> str:
    svg = re.sub(r"<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r"\s+", " ", svg).strip()
    svg = re.sub(r">\s+<", "><", svg)
    svg = re.sub(r'\s(class|width|height)="[^"]*"', "", svg)
    return svg


def main(src: str) -> int:
    root = Path(src)
    icons_dir = root / "icons"
    if not icons_dir.is_dir():
        print(f"no icons/ folder in {root}", file=sys.stderr)
        return 2
    DEST.mkdir(parents=True, exist_ok=True)
    data = {}
    for svg in sorted(icons_dir.glob("*.svg")):
        meta_path = svg.with_suffix(".json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        if meta.get("deprecated"):
            continue
        data[svg.stem] = {
            "svg": compact(svg.read_text(encoding="utf-8")),
            "tags": meta.get("tags", []),
            "categories": meta.get("categories", []),
        }
    (DEST / "lucide.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    with open(DEST / "icons.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["name", "categories", "tags"])
        for name, d in data.items():
            w.writerow([name, " ".join(d["categories"]), " ".join(d["tags"])])
    shutil.copy(root / "LICENSE", DEST / "LICENSE-lucide.txt")
    print(json.dumps({"icons": len(data), "json_kb": round((DEST / "lucide.json").stat().st_size / 1024)}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
