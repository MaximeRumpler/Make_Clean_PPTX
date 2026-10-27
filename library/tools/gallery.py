#!/usr/bin/env python3
"""Render thumbnails and the human catalogues of both libraries.

    python library/tools/gallery.py

Writes
  docs/thumbnails/<id>.jpg   one image per layout and per visual
  docs/catalog.json          data for the GitHub Pages gallery (docs/index.html)
  CATALOG.md                 the same catalogue, readable on GitHub
  docs/preview.jpg           a mosaic used in the README
Needs LibreOffice and poppler (same as render_check.py).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]
ASSETS = REPO / "skills" / "make-clean-pptx" / "assets"
DOCS = REPO / "docs"
THUMBS = DOCS / "thumbnails"
sys.path.insert(0, str(REPO / "skills" / "make-clean-pptx" / "scripts"))
from read_index import load_index  # noqa: E402

THUMB_W = 640
PREVIEW = ["L-01", "L-13", "L-32", "L-44", "V-COM-01", "V-MAT-03", "V-PRO-01", "V-TIM-02", "L-50"]


def render(lib: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, str(REPO / "skills/make-clean-pptx/scripts/render_check.py"), str(ASSETS / f"{lib}.pptx"),
                        "--out-dir", tmp, "--dpi", "110"], check=True, capture_output=True)
        out = {}
        for png in Path(tmp).glob("slide-*.png"):
            n = int(png.stem.split("-")[1])
            im = Image.open(png).convert("RGB")
            out[n] = im.resize((THUMB_W, int(im.height * THUMB_W / im.width)), Image.LANCZOS)
        return out


def main() -> int:
    THUMBS.mkdir(parents=True, exist_ok=True)
    catalog, images = [], {}
    for lib in ("layouts", "visuals"):
        entries = load_index(ASSETS / f"{lib}.csv")
        rendered = render(lib)
        for e in entries:
            im = rendered.get(e["slide"])
            if im is None:
                continue
            rel = f"thumbnails/{e['id']}.jpg"
            im.save(DOCS / rel, "JPEG", quality=80, optimize=True, progressive=True)
            images[e["id"]] = im
            catalog.append({
                "lib": lib, "id": e["id"], "slide": e["slide"], "name": e["name"], "category": e["category"],
                "description": e["description"], "use_when": e["use_when"], "tags": e["tags"],
                "objective": e.get("objective", ""), "frame": e.get("frame", ""), "style": e.get("style", ""),
                "arrange": e.get("arrange", ""), "fields": len(e["field_list"]), "thumbnail": rel,
            })
    (DOCS / "catalog.json").write_text(json.dumps(catalog, indent=1, ensure_ascii=False), encoding="utf-8")

    # README mosaic: 3 x 3
    tiles = [images[i] for i in PREVIEW if i in images]
    w, h, gap = 420, 236, 14
    mosaic = Image.new("RGB", (3 * w + 4 * gap, 3 * h + 4 * gap), (243, 243, 243))
    for k, im in enumerate(tiles[:9]):
        t = im.resize((w, h), Image.LANCZOS)
        mosaic.paste(t, (gap + (k % 3) * (w + gap), gap + (k // 3) * (h + gap)))
    mosaic.save(DOCS / "preview.jpg", "JPEG", quality=84, optimize=True)

    # CATALOG.md
    lines = ["# Catalogue", "",
             "Every layout and every visual shipped with the skill, generated from the indexes "
             "(`skills/make-clean-pptx/assets/*.csv`). Browse it with filters on the "
             "[gallery page](https://maximerumpler.github.io/Make_Clean_PPTX/).", ""]
    for lib, title in (("layouts", "Layouts"), ("visuals", "Visuals")):
        items = [c for c in catalog if c["lib"] == lib]
        lines += [f"## {title} ({len(items)})", ""]
        cats = []
        for c in items:
            if c["category"] not in cats:
                cats.append(c["category"])
        for cat in cats:
            group = [c for c in items if c["category"] == cat]
            lines += [f"### {cat}", "", "| | | |", "|:---:|:---:|:---:|"]
            for k in range(0, len(group), 3):
                row = []
                for c in group[k:k + 3]:
                    row.append(f"<img src=\"docs/{c['thumbnail']}\" width=\"260\"><br>**{c['id']}** {c['name']}<br><sub>{c['use_when']}</sub>")
                row += [""] * (3 - len(row))
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")
    (REPO / "CATALOG.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"thumbnails": len(catalog), "preview": str(DOCS / "preview.jpg")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
