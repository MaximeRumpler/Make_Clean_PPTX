#!/usr/bin/env python3
"""Render a deck to PNGs (and one contact sheet) so the result can be looked at.

    render_check.py deck.pptx --out-dir render/ [--dpi 80] [--cols 3] [--odp]

Needs LibreOffice (`soffice`) and poppler (`pdftoppm`). LibreOffice is not
PowerPoint: fonts may be substituted and spacing differs by a few pixels, so
judge layout and content, not exact kerning.

With --odp, also writes deck.odp next to the deck (OpenDocument, for LibreOffice users).

Prints JSON: {"slides": [...png paths...], "contact_sheet": "...", "resaved_copy": false, "odp": "..." (with --odp)}.
Exit code 4 when the rendering tools are missing, 5 when LibreOffice cannot convert the deck
(it is retried once on a re-saved copy first: "resaved_copy": true in the JSON).
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


# Usual install folders, for when LibreOffice is installed but not on PATH (the default on Windows and macOS).
SOFFICE_PLACES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


class RenderError(Exception):
    """The tools are there but the conversion failed (exit code 5)."""


def find_soffice() -> str | None:
    found = shutil.which("soffice") or shutil.which("libreoffice")
    return found or next((p for p in SOFFICE_PLACES if Path(p).is_file()), None)


def resave_copy(pptx: Path, folder: Path) -> Path:
    """Write a python-pptx re-saved copy of the deck in `folder` (same file name). The original is never touched.

    Some .pptx files written by other tools are refused by LibreOffice ("source file
    could not be loaded") although they are valid; re-saving normalises the zip layout.
    """
    from pptx import Presentation

    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / pptx.name
    Presentation(str(pptx)).save(str(dest))
    return dest


def render(pptx: Path, out_dir: Path, dpi: int, cols: int, odp: bool = False) -> dict:
    soffice = find_soffice()
    pdftoppm = shutil.which("pdftoppm")
    if not soffice or not pdftoppm:
        missing = [n for n, p in (("LibreOffice", soffice), ("poppler (pdftoppm)", pdftoppm)) if not p]
        raise RuntimeError("missing tools: " + ", ".join(missing))
    if not pptx.is_file():
        raise RenderError(f"file not found: {pptx}")

    out_dir.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(out_dir / "slide-*.png")):
        Path(old).unlink()

    result = {"resaved_copy": False}
    with tempfile.TemporaryDirectory() as tmp:
        profile = (Path(tmp) / "profile").as_uri()  # file:///C:/... on Windows, file:///tmp/... elsewhere

        def convert(src: Path, fmt: str, outdir: Path) -> Path | None:
            """Run LibreOffice; return the produced file, or None when it refused the deck."""
            try:
                subprocess.run([soffice, f"-env:UserInstallation={profile}", "--headless", "--convert-to", fmt,
                                "--outdir", str(outdir), str(src)], check=True, capture_output=True, timeout=300)
            except subprocess.CalledProcessError:
                return None
            made = outdir / (src.stem + "." + fmt)
            return made if made.exists() else None

        src = pptx
        pdf = convert(src, "pdf", Path(tmp))
        if pdf is None:  # retry once on a re-saved copy
            try:
                src = resave_copy(pptx, Path(tmp) / "resaved")
            except Exception as exc:  # noqa: BLE001 - python-pptx cannot read it either
                raise RenderError(f"the deck could not be opened: {exc}") from exc
            result["resaved_copy"] = True
            pdf = convert(src, "pdf", Path(tmp))
            if pdf is None:
                raise RenderError("LibreOffice could not open the deck, even after re-saving a copy")
        subprocess.run([pdftoppm, "-r", str(dpi), "-png", str(pdf), str(out_dir / "slide")], check=True, timeout=300)
        if odp:
            if convert(src, "odp", pptx.resolve().parent) is None:
                raise RenderError("LibreOffice did not produce an ODP file")
            result["odp"] = str(pptx.with_suffix(".odp"))

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
        print(json.dumps({"error": str(exc), "hint": install_hint()}))
        return 4
    except (RenderError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": f"rendering failed: {exc}",
                          "hint": "The slide pictures could not be made. "
                                  "Rely on lint_deck.py and tell the user the visual check was skipped."}))
        return 5


def install_hint() -> str:
    """How to get the rendering tools, in words a non-technical user can follow."""
    lead = "To preview the slides as pictures, install LibreOffice (free) and poppler. "
    tail = " Without them, skip the visual check: the lint still runs."
    if sys.platform == "win32":
        how = "Windows: LibreOffice from libreoffice.org, poppler with 'winget install oschwartz10612.Poppler'."
    elif sys.platform == "darwin":
        how = "macOS: 'brew install --cask libreoffice' and 'brew install poppler'."
    else:
        how = "Linux: 'sudo apt install libreoffice-impress poppler-utils' (or your distribution's equivalent)."
    return lead + how + tail


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to a legacy code page; agents read UTF-8
        getattr(_stream, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
