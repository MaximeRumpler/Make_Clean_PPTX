"""Shared helpers for the make-clean-pptx scripts.

Kept dependency-light: python-pptx (+ its lxml) only.
"""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER

EMU_PER_PT = 12700
EMU_PER_INCH = 914400

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / "config.json"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def eprint(*args) -> None:
    print(*args, file=sys.stderr)


# --------------------------------------------------------------------------
# Shape helpers
# --------------------------------------------------------------------------

def iter_shapes(container):
    """Yield every shape depth-first, descending into groups."""
    for shp in container.shapes:
        yield shp
        try:
            is_group = shp.shape_type == MSO_SHAPE_TYPE.GROUP
        except NotImplementedError:
            is_group = False
        if is_group:
            yield from iter_shapes(shp)


def abs_box(shp):
    """(x1, y1, x2, y2) in slide EMU, applying the transforms of enclosing groups."""
    x1, y1 = shp.left, shp.top
    x2, y2 = x1 + shp.width, y1 + shp.height
    parent = shp._element.getparent()
    while parent is not None and parent.tag.endswith("}grpSp"):
        xf = parent.find("{http://schemas.openxmlformats.org/presentationml/2006/main}grpSpPr/"
                         "{http://schemas.openxmlformats.org/drawingml/2006/main}xfrm")
        if xf is None:
            break
        a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
        off, ext, choff, chext = (xf.find(a + t) for t in ("off", "ext", "chOff", "chExt"))
        if None in (off, ext, choff, chext):
            break
        sx = int(ext.get("cx")) / (int(chext.get("cx")) or 1)
        sy = int(ext.get("cy")) / (int(chext.get("cy")) or 1)
        ox, oy, cx, cy = int(off.get("x")), int(off.get("y")), int(choff.get("x")), int(choff.get("y"))
        x1, x2 = ox + (x1 - cx) * sx, ox + (x2 - cx) * sx
        y1, y2 = oy + (y1 - cy) * sy, oy + (y2 - cy) * sy
        parent = parent.getparent()
    return int(x1), int(y1), int(x2), int(y2)


def shape_kind(shp) -> str:
    """Return one of: group, picture, chart, table, text, shape, other."""
    try:
        st = shp.shape_type
    except NotImplementedError:
        st = None
    if st == MSO_SHAPE_TYPE.GROUP:
        return "group"
    if getattr(shp, "has_chart", False):
        return "chart"
    if getattr(shp, "has_table", False):
        return "table"
    if st == MSO_SHAPE_TYPE.PICTURE or shp._element.tag.endswith("}pic"):
        return "picture"
    if hasattr(shp, "insert_picture"):  # empty picture placeholder
        return "picture"
    if getattr(shp, "has_text_frame", False):
        return "text"
    return "other"


def has_text(shp) -> bool:
    return bool(getattr(shp, "has_text_frame", False) and shp.text_frame.text.strip())


# --------------------------------------------------------------------------
# Text-fit heuristic
# --------------------------------------------------------------------------
# python-pptx cannot lay text out, so we estimate: average glyph width is about
# half an em for sans-serif fonts and a line is 1.2 em high. The estimate is
# deliberately a little generous; it catches walls of text, not one-word spills.

AVG_CHAR_EM = 0.52
LINE_EM = 1.2
DEFAULT_BODY_PT = 18.0
DEFAULT_TITLE_PT = 32.0


def guess_font_pt(shape, default: float | None = None) -> float:
    """Best-effort font size in points for a text shape."""
    try:
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                if r.font.size:
                    return r.font.size.pt
            if p.font.size:
                return p.font.size.pt
    except Exception:
        pass
    if default is not None:
        return default
    try:
        if shape.is_placeholder and shape.placeholder_format.type in (
            PP_PLACEHOLDER.TITLE,
            PP_PLACEHOLDER.CENTER_TITLE,
        ):
            return DEFAULT_TITLE_PT
    except Exception:
        pass
    return DEFAULT_BODY_PT


def estimate_fit(shape, paragraphs: list[str], font_pt: float | None = None) -> dict | None:
    """Estimate whether `paragraphs` fit in `shape`.

    Returns {needed_lines, avail_lines, font_pt, chars_per_line} or None when the
    shape has no usable geometry.
    """
    if shape.width is None or shape.height is None:
        return None
    fp = font_pt or guess_font_pt(shape)
    tf = shape.text_frame
    left = (tf.margin_left if tf.margin_left is not None else 91440) / EMU_PER_PT
    right = (tf.margin_right if tf.margin_right is not None else 91440) / EMU_PER_PT
    top = (tf.margin_top if tf.margin_top is not None else 45720) / EMU_PER_PT
    bottom = (tf.margin_bottom if tf.margin_bottom is not None else 45720) / EMU_PER_PT
    w_pt = shape.width / EMU_PER_PT - left - right
    h_pt = shape.height / EMU_PER_PT - top - bottom
    if w_pt <= 0 or h_pt <= 0:
        return None
    chars_per_line = max(1, int(w_pt / (fp * AVG_CHAR_EM)))
    avail = max(1, int(h_pt / (fp * LINE_EM)))
    needed = 0
    for para in paragraphs:
        clean = para.replace("**", "")
        needed += max(1, math.ceil(len(clean) / chars_per_line))
    return {
        "needed_lines": needed,
        "avail_lines": avail,
        "font_pt": round(fp, 1),
        "chars_per_line": chars_per_line,
    }


def overflows(fit: dict | None, tolerance: float = 1.15) -> bool:
    return bool(fit) and fit["needed_lines"] > fit["avail_lines"] * tolerance


# --------------------------------------------------------------------------
# Theme colour tokens (same names as library/theme/tokens.json)
# --------------------------------------------------------------------------
# name -> (scheme colour, lumMod, lumOff, is_dark)
TOKENS = {
    "ink": ("tx1", None, None, True),
    "ink2": ("tx2", None, None, True),
    "muted": ("tx1", 50000, 40000, False),
    "line": ("bg1", 85000, None, False),
    "surface": ("bg2", None, None, False),
    "paper": ("bg1", None, None, False),
    "a1": ("accent1", None, None, True),
    "a2": ("accent2", None, None, True),
    "a3": ("accent3", None, None, False),  # mid grey: black text reads better (WCAG AA)
    "a4": ("accent4", None, None, False),
    "a5": ("accent5", None, None, False),
    "a6": ("accent6", None, None, False),
}
TOKEN_ALIASES = {"black": "ink", "white": "paper", "dark": "a1", "light": "a5", "grey": "a3", "gray": "a3",
                 **{f"accent{i}": f"a{i}" for i in range(1, 7)}}


def token(name: str) -> str:
    key = TOKEN_ALIASES.get(str(name).strip().lower(), str(name).strip().lower())
    if key not in TOKENS:
        raise ValueError(f"unknown colour '{name}'. Use one of: {', '.join(TOKENS)}")
    return key


def token_xml(name: str) -> str:
    scheme, mod, off, _ = TOKENS[token(name)]
    inner = (f'<a:lumMod val="{mod}"/>' if mod else "") + (f'<a:lumOff val="{off}"/>' if off else "")
    ns = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
    return f'<a:schemeClr {ns} val="{scheme}">{inner}</a:schemeClr>' if inner else f'<a:schemeClr {ns} val="{scheme}"/>'


def is_dark(name: str) -> bool:
    return TOKENS[token(name)][3]


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
