#!/usr/bin/env python3
"""Render a deck to PNGs (and one contact sheet) so the result can be looked at.

    render_check.py deck.pptx --out-dir render/ [--dpi 80] [--cols 3] [--odp]

Needs LibreOffice (`soffice`) and poppler (`pdftoppm`). LibreOffice is not
PowerPoint: fonts may be substituted and spacing differs by a few pixels, so
judge layout and content, not exact kerning.

With --odp, also writes deck.odp next to the deck (OpenDocument, for LibreOffice users).

Prints JSON: {"slides": [...png paths...], "contact_sheet": "...", "odp": "..." (with --odp)}.
Exit code 4 when the rendering tools are missing.
"""
from __future__ import annotations

import argparse
import glob
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def render(pptx: Path, out_dir: Path, dpi: int, cols: int, odp: bool = False) -> dict:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    pdftoppm = shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        missing = [n for n, p in (("soffice (LibreOffice)", soffice), ("pdftoppm (poppler)", pdftoppm)) if not p]
        raise RuntimeError("missing tools: " + ", ".join(missing))

    out_dir.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(out_dir / "slide-*.png")):
        Path(old).unlink()

    result = {}
    with tempfile.TemporaryDirectory() as tmp:
        def convert(fmt: str, outdir: Path) -> None:
            subprocess.run(
                [soffice, f"-env:UserInstallation=file://{tmp}/profile", "--headless", "--convert-to", fmt,
                 "--outdir", str(outdir), str(pptx)],
                check=True, capture_output=True, timeout=300,
            )

        convert("pdf", Path(tmp))
        pdf = Path(tmp) / (pptx.stem + ".pdf")
        if not pdf.exists():
            raise RuntimeError("LibreOffice did not produce a PDF")
        subprocess.run([pdftoppm, "-r", str(dpi), "-png", str(pdf), str(out_dir / "slide")], check=True, timeout=300)
        if odp:
            convert("odp", pptx.resolve().parent)
            dest = pptx.with_suffix(".odp")
            if not dest.exists():
                raise RuntimeError("LibreOffice did not produce an ODP file")
            result["odp"] = str(dest)

    pngs = sorted(glob.glob(str(out_dir / "slide-*.png")), key=lambda p: int(Path(p).stem.split("-")[-1]))
    sheet = _contact_sheet(pngs, out_dir / "contact-sheet.png", cols) if pngs else None
    return {"slides": pngs, "contact_sheet": sheet, **result}


def _contact_sheet(pngs: list[str], dest: Path, cols: int) -> str:
    from PIL import Image, ImageDraw

    thumbs = []
    for p in pngs:
        im = Image.open(p).convert("RGB")
        w = 560
        thumbs.append(im.resize((w, int(im.height * w / im.width))))
    tw, th = thumbs[0].size
    pad, label_h = 14, 22
    rows = -(-len(thumbs) // cols)
    sheet = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + pad + label_h) + pad), "#f4f5f7")
    draw = ImageDraw.Draw(sheet)
    for i, im in enumerate(thumbs):
        x = pad + (i % cols) * (tw + pad)
        y = pad + (i // cols) * (th + pad + label_h)
        draw.text((x, y), f"{i + 1}", fill="#1c2333")
        sheet.paste(im, (x, y + label_h))
        draw.rectangle([x - 1, y + label_h - 1, x + tw, y + label_h + th], outline="#d0d4db")
    sheet.save(dest)
    return str(dest)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--out-dir", default="render")
    ap.add_argument("--dpi", type=int, default=80)
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--odp", action="store_true", help="also save an .odp copy next to the deck")
    args = ap.parse_args(argv)
    try:
        print(json.dumps(render(Path(args.pptx), Path(args.out_dir), args.dpi, args.cols, args.odp), indent=2))
        return 0
    except RuntimeError as exc:
        print(json.dumps({"error": str(exc), "hint": "apt install libreoffice-impress poppler-utils  |  brew install --cask libreoffice && brew install poppler"}))
        return 4
    except subprocess.SubprocessError as exc:
        print(json.dumps({"error": f"rendering failed: {exc}"}))
        return 5


if __name__ == "__main__":
    sys.exit(main())
