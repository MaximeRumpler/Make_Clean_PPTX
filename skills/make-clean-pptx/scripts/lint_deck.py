#!/usr/bin/env python3
"""Structural quality checks for a finished deck.

    lint_deck.py deck.pptx [--json] [--max-fonts 3] [--min-font 10] [--contrast]

Catches what the eyes of a tired reviewer miss: leftover template text,
empty placeholders, text that probably overflows, text or pictures outside the
slide, overlapping text boxes, pictures without alt text, too many fonts.
Run render_check.py as well: this linter cannot see the actual rendering.

--contrast (opt-in) also checks colours against the deck's own theme: every
text run against the fill under it (WCAG: 4.5:1, or 3:1 for text of 18 pt or
14 pt bold), and the theme against assets/theme-contract.json (accent ramp
order, the colour pairs the libraries rely on). Text too faint to read is an
error; a theme that would break pairs the deck does not use is a warning.
See references/theme-contract.md.

Exit code: 0 = no errors (warnings may exist), 1 = errors found, 2 = unreadable file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from pptx import Presentation

from _common import SKILL_DIR, abs_box, estimate_fit, has_text, iter_shapes, overflows, shape_kind

CONTRACT = SKILL_DIR / "assets" / "theme-contract.json"

LEFTOVER = re.compile(
    r"lorem ipsum|click to (add|edit)|your (text|title|name|logo)( here)?|insert (text|title|image)|"
    r"\{\{.*?\}\}|\[(title|text|image|name)\]|placeholder|xx+%|sample text|texte (ici|exemple)",
    re.I,
)


def _box(shp):
    """Slide-space box, also for shapes inside (nested) groups."""
    if None in (shp.left, shp.top, shp.width, shp.height):
        return None
    return abs_box(shp)


def _iou(a, b) -> float:
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if not inter:
        return 0.0
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1])  # noqa: E731
    return inter / min(area(a), area(b))


def contrast(prs, add) -> dict:
    """Contrast checks against the deck's theme; adds findings through `add`, returns a summary."""
    from _contrast import NS, check_deck, clr_map, theme_findings

    rep = check_deck(prs)
    worst = {}
    for r in rep["results"]:
        if r["ratio"] >= r["need"]:
            continue
        key = (r["slide"], r["shape"])
        if key not in worst or r["ratio"] / r["need"] < worst[key]["ratio"] / worst[key]["need"]:
            worst[key] = r
    for (n, shape), r in sorted(worst.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
        size = "large text" if r["need"] < 4.5 else "text at %g pt" % r["pt"]
        add("error", n, shape, (
            "text hard to read: '%s' is %s (#%s) on %s (#%s), contrast %.1f:1, %s needs %.1f:1. "
            "Use the other text colour on this fill (paper on dark, ink on light), or change the fill"
            % (r["text"], r["fg_label"], r["fg"], r["bg_label"], r["bg"], r["ratio"], size, r["need"])))
    themes = []
    if CONTRACT.is_file() and len(prs.slides):
        master = prs.slides[0].slide_layout.slide_master
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        for f in theme_findings(rep["theme"], contract, clr_map(master._element.find("p:clrMap", NS))):
            themes.append(f["message"])
            add("warning", 0, None, "theme: " + f["message"])
    return {"theme": rep["theme"].get("name", ""), "colors": rep["theme"].get("colors", {}),
            "checked_runs": rep["checked"], "unchecked_runs": rep["unchecked"],
            "failing_shapes": len(worst), "theme_findings": themes}


def lint(path: str, max_fonts: int = 3, min_font: float = 10.0, check_contrast: bool = False) -> dict:
    prs = Presentation(path)
    sw, sh = prs.slide_width, prs.slide_height
    tol_x, tol_y = int(sw * 0.01), int(sh * 0.01)
    errors, warnings = [], []
    fonts: dict[str, int] = {}

    def add(level, n, shape, msg):
        (errors if level == "error" else warnings).append({"slide": n, "shape": shape, "message": msg})

    if len(prs.slides) == 0:
        add("error", 0, None, "deck has no slides")

    for n, slide in enumerate(prs.slides, 1):
        text_boxes = []
        for shp in iter_shapes(slide):
            kind = shape_kind(shp)
            name = shp.name

            if kind in ("text", "picture", "chart", "table"):
                b = _box(shp)
                if b and (b[0] < -tol_x or b[1] < -tol_y or b[2] > sw + tol_x or b[3] > sh + tol_y):
                    if kind == "text" and not has_text(shp):
                        pass
                    elif kind == "picture":
                        pass  # full-bleed pictures often overshoot on purpose
                    else:
                        add("warning", n, name, "extends beyond the slide edge")

            if kind == "text":
                if getattr(shp, "is_placeholder", False) and not has_text(shp):
                    add("warning", n, name, "empty placeholder (shows 'Click to add...' while editing); fill or delete it")
                if has_text(shp):
                    paras = [p.text for p in shp.text_frame.paragraphs]
                    full = "\n".join(paras)
                    m = LEFTOVER.search(full)
                    if m:
                        add("error", n, name, f"leftover template text: '{m.group(0)}'")
                    fit = estimate_fit(shp, paras)
                    if overflows(fit):
                        add("warning", n, name,
                            f"text probably overflows (~{fit['needed_lines']} lines needed, ~{fit['avail_lines']} fit at {fit['font_pt']}pt)")
                    for p in shp.text_frame.paragraphs:
                        for r in p.runs:
                            if r.font.name:
                                fonts[r.font.name] = fonts.get(r.font.name, 0) + 1
                            if r.font.size and r.font.size.pt < min_font and r.text.strip():
                                add("warning", n, name, f"font size {r.font.size.pt:g}pt is below {min_font:g}pt")
                    b = _box(shp)
                    if b:
                        text_boxes.append((name, b))

            if kind == "picture" and shp._element.tag.endswith("}pic"):
                descr = shp._element.xpath(".//p:cNvPr")[0].get("descr", "")
                if not descr.strip():
                    add("warning", n, name, "picture has no alt text")

            if kind == "table":
                for row in shp.table.rows:
                    for cell in row.cells:
                        m = LEFTOVER.search(cell.text_frame.text)
                        if m:
                            add("error", n, name, f"leftover template text in table: '{m.group(0)}'")

        for i in range(len(text_boxes)):
            for j in range(i + 1, len(text_boxes)):
                if _iou(text_boxes[i][1], text_boxes[j][1]) > 0.35:
                    add("warning", n, text_boxes[i][0], f"overlaps text box '{text_boxes[j][0]}'")

        if not slide.shapes:
            add("warning", n, None, "slide is empty")

    if len(fonts) > max_fonts:
        add("warning", 0, None, f"{len(fonts)} different explicit fonts ({', '.join(sorted(fonts))}); stick to the theme fonts")

    report = {"slides": len(prs.slides), "errors": errors, "warnings": warnings}
    if check_contrast:
        report["contrast"] = contrast(prs, add)
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pptx")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-fonts", type=int, default=3)
    ap.add_argument("--min-font", type=float, default=10.0)
    ap.add_argument("--contrast", action="store_true", help="also check text contrast against the deck's theme")
    args = ap.parse_args(argv)
    try:
        report = lint(args.pptx, args.max_fonts, args.min_font, args.contrast)
    except Exception as exc:  # noqa: BLE001
        print(f"error: cannot read {args.pptx}: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"{report['slides']} slides, {len(report['errors'])} errors, {len(report['warnings'])} warnings")
        if "contrast" in report:
            c = report["contrast"]
            print(f"contrast: theme '{c['theme']}', {c['checked_runs']} text runs checked, "
                  f"{c['failing_shapes']} shapes too faint, "
                  f"{c['unchecked_runs']} over pictures or gradients not checked")
        for level, items in (("ERROR", report["errors"]), ("warn ", report["warnings"])):
            for it in items:
                where = f"slide {it['slide']}" if it["slide"] else "deck"
                shape = f" / {it['shape']}" if it["shape"] else ""
                print(f"  {level} {where}{shape}: {it['message']}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to a legacy code page; agents read UTF-8
        getattr(_stream, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
