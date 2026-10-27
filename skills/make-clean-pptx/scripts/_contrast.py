"""WCAG contrast of the text in a deck, computed from the deck's own theme.

Used by `lint_deck.py --contrast` and by the library tool that writes
assets/theme-contract.json. Standard library + lxml (comes with python-pptx).

What it does, per slide:
1. reads the theme of the slide's master (colour scheme, fonts) and the colour
   map (master clrMap, overridden by the layout or the slide);
2. paints the slide in z-order: background, then the fills of the master,
   layout and slide shapes (groups, tables and chart data labels included);
3. for every text run, resolves the text colour and the colour under the text
   (the shape's own fill, else what was painted below it) and computes the
   contrast ratio. Colour modifiers lumMod, lumOff, tint, shade, satMod and
   alpha are applied.

Limits: text over a picture or a gradient is not checked (counted as
"unchecked"); "under the text" is decided at the centre of the text box, so
a label straddling two fills is judged on the one at its centre.
"""
from __future__ import annotations

import colorsys
import re

from lxml import etree

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
A = "{%s}" % NS["a"]
P = "{%s}" % NS["p"]
C = "{%s}" % NS["c"]
RT_THEME = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"
RT_CHART = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart"

SLOTS = ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
         "hlink", "folHlink")
DEFAULT_CLRMAP = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2",
                  **{s: s for s in SLOTS if s.startswith(("accent", "hlink", "folHlink"))}}
COLOR_TAGS = ("srgbClr", "schemeClr", "sysClr", "prstClr", "scrgbClr", "hslClr")
PRESET = {"black": "000000", "white": "FFFFFF", "red": "FF0000", "green": "008000", "blue": "0000FF",
          "yellow": "FFFF00", "gray": "808080", "grey": "808080"}
HOLLOW = {"line", "straightConnector1", "bentConnector2", "bentConnector3", "curvedConnector3", "arc", "blockArc",
          "donut", "frame", "halfFrame", "leftBracket", "rightBracket", "leftBrace", "rightBrace", "bracketPair",
          "bracePair", "noSmoking"}

TEXT_MIN = 4.5   # WCAG 2.x SC 1.4.3, normal text
LARGE_MIN = 3.0  # large text (18 pt, or 14 pt bold) and graphics (SC 1.4.11)
DEFAULT_PT = 18.0


# ------------------------------------------------------------------ colour math
def hex_to_rgb(h: str):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb_to_hex(rgb) -> str:
    return "".join("%02X" % int(round(max(0.0, min(1.0, c)) * 255)) for c in rgb)


def _lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _gamma(c: float) -> float:
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminance(rgb) -> float:
    """WCAG relative luminance of an sRGB colour (components 0..1)."""
    r, g, b = (_lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg) -> float:
    l1, l2 = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def blend(top, alpha: float, below):
    return tuple(t * alpha + b * (1 - alpha) for t, b in zip(top, below))


def apply_mods(rgb, el):
    """Apply the DrawingML modifiers under a colour element, in document order.

    lumMod/lumOff/satMod work on HSL (as PowerPoint's theme tints do);
    tint/shade work on linear RGB, as in the Office implementation.
    Returns (rgb, alpha).
    """
    alpha = 1.0
    for m in el:
        tag = etree.QName(m).localname
        try:
            v = int(m.get("val", "0")) / 100000
        except ValueError:
            continue
        if tag in ("lumMod", "lumOff", "satMod"):
            h, lum, s = colorsys.rgb_to_hls(*rgb)
            if tag == "lumMod":
                lum *= v
            elif tag == "lumOff":
                lum += v
            else:
                s *= v
            rgb = colorsys.hls_to_rgb(h, max(0.0, min(1.0, lum)), max(0.0, min(1.0, s)))
        elif tag == "tint":
            rgb = tuple(_gamma(1 - (1 - _lin(c)) * v) for c in rgb)
        elif tag == "shade":
            rgb = tuple(_gamma(_lin(c) * v) for c in rgb)
        elif tag == "alpha":
            alpha = v
    return tuple(max(0.0, min(1.0, c)) for c in rgb), alpha


# ------------------------------------------------------------------ theme
def read_theme(xml: bytes) -> dict:
    """{"name", "colors": {slot: "RRGGBB"}, "fonts": {"major", "minor"}} from a theme part."""
    root = etree.fromstring(xml)
    colors = {}
    scheme = root.find(".//a:clrScheme", NS)
    if scheme is not None:
        for slot in SLOTS:
            el = scheme.find("a:" + slot, NS)
            if el is None or not len(el):
                continue
            c = el[0]
            val = c.get("lastClr") if c.tag == A + "sysClr" else c.get("val")
            if val and re.fullmatch(r"[0-9A-Fa-f]{6}", val):
                colors[slot] = val.upper()
    fonts = {}
    for key, tag in (("major", "majorFont"), ("minor", "minorFont")):
        lat = root.find(".//a:fontScheme/a:%s/a:latin" % tag, NS)
        fonts[key] = lat.get("typeface") if lat is not None else ""
    return {"name": root.get("name", ""), "colors": colors, "fonts": fonts}


def clr_map(el) -> dict | None:
    if el is None:
        return None
    return {k: v for k, v in el.attrib.items()}


class Palette:
    """Resolves colour elements against one theme and one colour map."""

    def __init__(self, theme: dict, cmap: dict | None = None):
        self.theme = theme
        self.cmap = dict(DEFAULT_CLRMAP)
        self.cmap.update(cmap or {})

    def slot(self, val: str) -> str:
        return self.cmap.get(val, val)

    def base(self, el):
        tag = etree.QName(el).localname
        if tag == "srgbClr":
            return hex_to_rgb(el.get("val", "000000"))
        if tag == "sysClr":
            return hex_to_rgb(el.get("lastClr") or ("FFFFFF" if el.get("val") == "window" else "000000"))
        if tag == "schemeClr":
            hx = self.theme["colors"].get(self.slot(el.get("val", "")))
            return hex_to_rgb(hx) if hx else None
        if tag == "prstClr":
            hx = PRESET.get((el.get("val") or "").lower())
            return hex_to_rgb(hx) if hx else None
        if tag == "scrgbClr":
            return tuple(_gamma(int(el.get(k, "0")) / 100000) for k in ("r", "g", "b"))
        if tag == "hslClr":
            return colorsys.hls_to_rgb(int(el.get("hue", "0")) / 21600000, int(el.get("lum", "0")) / 100000,
                                       int(el.get("sat", "0")) / 100000)
        return None

    def resolve(self, el):
        """Colour element -> (rgb, alpha) or None."""
        if el is None:
            return None
        rgb = self.base(el)
        if rgb is None:
            return None
        return apply_mods(rgb, el)

    def token(self, name: str):
        """Resolve a _common.TOKENS name (ink, a1...) to rgb."""
        from _common import TOKEN_ALIASES, TOKENS
        key = TOKEN_ALIASES.get(name, name)
        if key not in TOKENS:  # a bare slot such as hlink
            hx = self.theme["colors"].get(self.slot(name))
            return hex_to_rgb(hx) if hx else None
        scheme, mod, off, _ = TOKENS[key]
        hx = self.theme["colors"].get(self.slot(scheme))
        if not hx:
            return None
        rgb = hex_to_rgb(hx)
        if mod or off:
            h, lum, s = colorsys.rgb_to_hls(*rgb)
            lum = lum * (mod or 100000) / 100000 + (off or 0) / 100000
            rgb = colorsys.hls_to_rgb(h, max(0.0, min(1.0, lum)), s)
        return rgb


def color_child(el):
    if el is None:
        return None
    for c in el:
        if etree.QName(c).localname in COLOR_TAGS:
            return c
    return None


def label(el) -> str:
    """Readable name of a colour element: a library token (ink, a1...) when it is one."""
    if el is None:
        return "?"
    tag = etree.QName(el).localname
    if tag == "srgbClr":
        return "#" + el.get("val", "").upper()
    if tag != "schemeClr":
        return tag
    mods = {etree.QName(m).localname: int(m.get("val", "0")) for m in el}
    from _common import TOKENS
    for name, (scheme, mod, off, _) in TOKENS.items():
        if scheme == el.get("val") and mods == {k: v for k, v in (("lumMod", mod), ("lumOff", off)) if v}:
            return name
    extra = " ".join("%s %d%%" % (k, v // 1000) for k, v in mods.items())
    return (el.get("val", "") + (" " + extra if extra else "")).strip()


# ------------------------------------------------------------------ geometry
def _xfrm(el):
    tag = etree.QName(el).localname
    if tag == "graphicFrame":
        x = el.find("p:xfrm", NS)
    elif tag == "grpSp":
        x = el.find("p:grpSpPr/a:xfrm", NS)
    else:
        x = el.find("p:spPr/a:xfrm", NS)
    return x


def _box(el, tf):
    x = _xfrm(el)
    if x is None:
        return None
    off, ext = x.find("a:off", NS), x.find("a:ext", NS)
    if off is None or ext is None:
        return None
    sx, sy, ox, oy = tf
    x1, y1 = ox + int(off.get("x")) * sx, oy + int(off.get("y")) * sy
    return (x1, y1, x1 + int(ext.get("cx")) * sx, y1 + int(ext.get("cy")) * sy)


def _child_tf(grp, tf):
    x = _xfrm(grp)
    if x is None:
        return tf
    off, ext, choff, chext = (x.find("a:" + t, NS) for t in ("off", "ext", "chOff", "chExt"))
    if None in (off, ext, choff, chext):
        return tf
    gsx = int(ext.get("cx")) / (int(chext.get("cx")) or 1)
    gsy = int(ext.get("cy")) / (int(chext.get("cy")) or 1)
    gox = int(off.get("x")) - int(choff.get("x")) * gsx
    goy = int(off.get("y")) - int(choff.get("y")) * gsy
    sx, sy, ox, oy = tf
    return (sx * gsx, sy * gsy, ox + gox * sx, oy + goy * sy)


# ------------------------------------------------------------------ scene
class Scene:
    """Fills painted so far on one slide, bottom to top."""

    def __init__(self, bg):
        self.bg = bg            # (rgb, label) or None when unknown (picture, gradient)
        self.regions = []       # (box, rgb or None, alpha, label)

    def paint(self, box, rgb, alpha, lab):
        if box and box[2] > box[0] and box[3] > box[1]:
            self.regions.append((box, rgb, alpha, lab))

    def under(self, x, y, upto=None):
        """(rgb, label) of what is visible at (x, y) below region index `upto`; None if unknown."""
        regions = self.regions if upto is None else self.regions[:upto]
        stack = []
        for box, rgb, alpha, lab in reversed(regions):
            if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                if rgb is None:
                    return None
                stack.append((rgb, alpha, lab))
                if alpha >= 0.999:
                    break
        else:
            if self.bg is None:
                return None
            stack.append((self.bg[0], 1.0, self.bg[1]))
        rgb, lab = stack[-1][0], stack[-1][2]
        for top, alpha, tl in reversed(stack[:-1]):
            rgb = blend(top, alpha, rgb)
            lab = "%s (%d%%) over %s" % (tl, round(alpha * 100), lab)
        return rgb, lab


def _fill_of(sppr, pal, style=None, grp_fill=None):
    """Fill of a shape: ('solid', rgb, alpha, label) / ('none',) / ('unknown',) / ('group',)."""
    if sppr is not None:
        for f in sppr:
            tag = etree.QName(f).localname
            if tag == "noFill":
                return ("none",)
            if tag == "solidFill":
                c = color_child(f)
                res = pal.resolve(c)
                return ("solid", res[0], res[1], label(c)) if res else ("unknown",)
            if tag in ("gradFill", "blipFill", "pattFill"):
                return ("unknown",)
            if tag == "grpFill":
                return grp_fill or ("none",)
    if style is not None:
        ref = style.find("a:fillRef", NS)
        if ref is not None and ref.get("idx", "0") != "0":
            c = color_child(ref)
            res = pal.resolve(c)
            return ("solid", res[0], res[1], label(c)) if res else ("unknown",)
    return ("none",)


def _bg_of(cSld, pal):
    bg = cSld.find("p:bg", NS) if cSld is not None else None
    if bg is None:
        return "inherit"
    pr = bg.find("p:bgPr", NS)
    if pr is not None:
        f = _fill_of(pr, pal)
        if f[0] == "solid":
            return (f[1], f[3])
        return None
    ref = bg.find("p:bgRef", NS)
    if ref is not None:
        c = color_child(ref)
        res = pal.resolve(c)
        # idx 1001 is the theme's first background style, a plain fill in the reference colour;
        # the other styles are usually gradients or pictures, which are not checked
        if res and ref.get("idx") == "1001":
            return (res[0], label(c))
    return None


def _style_default(master_root, kind, lvl, attr):
    """Value from the master text styles (titleStyle / bodyStyle / otherStyle)."""
    if master_root is None:
        return None
    st = master_root.find("p:txStyles/p:%s/a:lvl%dpPr/a:defRPr" % (kind, lvl), NS)
    if st is None:
        return None
    if attr == "fill":
        f = st.find("a:solidFill", NS)
        return color_child(f) if f is not None else None
    return st.get(attr)


def _lst_default(txbody, lvl, attr):
    if txbody is None:
        return None
    st = txbody.find("a:lstStyle/a:lvl%dpPr/a:defRPr" % lvl, NS)
    if st is None:
        return None
    if attr == "fill":
        f = st.find("a:solidFill", NS)
        return color_child(f) if f is not None else ("nofill" if st.find("a:noFill", NS) is not None else None)
    return st.get(attr)


def _runs(txbody, pal, master_root, kind, style, font_scale=1.0):
    """Yield (text, rgb, label, pt, bold) for each run with visible text."""
    for p in txbody.findall("a:p", NS):
        ppr = p.find("a:pPr", NS)
        lvl = int(ppr.get("lvl", "0")) + 1 if ppr is not None else 1
        for r in p:
            if etree.QName(r).localname not in ("r", "fld"):
                continue
            t = "".join(x.text or "" for x in r.findall("a:t", NS)).strip()
            if not t:
                continue
            rpr = r.find("a:rPr", NS)
            cel = None
            if rpr is not None:
                f = rpr.find("a:solidFill", NS)
                if f is not None:
                    cel = color_child(f)
                elif rpr.find("a:gradFill", NS) is not None or rpr.find("a:noFill", NS) is not None:
                    continue
                elif rpr.find("a:hlinkClick", NS) is not None:
                    cel = etree.Element(A + "schemeClr", val="hlink")
            if cel is None:
                d = _lst_default(txbody, lvl, "fill")
                if d == "nofill":
                    continue
                cel = d
            if cel is None and style is not None:
                ref = style.find("a:fontRef", NS)
                cel = color_child(ref) if ref is not None else None
            if cel is None:
                cel = _style_default(master_root, kind, lvl, "fill")
            if cel is None:
                cel = etree.Element(A + "schemeClr", val="tx1")
            res = pal.resolve(cel)
            if res is None:
                continue
            sz = (rpr.get("sz") if rpr is not None else None) or _lst_default(txbody, lvl, "sz") \
                or _style_default(master_root, kind, lvl, "sz")
            pt = int(sz) / 100 if sz else DEFAULT_PT
            b = (rpr.get("b") if rpr is not None else None) or _lst_default(txbody, lvl, "b") \
                or _style_default(master_root, kind, lvl, "b")
            yield t, res, label(cel), pt * font_scale, b in ("1", "true")


def needed(pt: float, bold: bool) -> float:
    large = pt >= 18 or (bold and pt >= 14)
    return LARGE_MIN if large else TEXT_MIN


# ------------------------------------------------------------------ charts
def _chart_texts(chart_root, pal):
    """Yield (text_desc, colour_el, pt, bold, inside_fill_el) for the visible texts of a chart."""
    def txpr(el):
        d = el.find("c:txPr/a:p/a:pPr/a:defRPr", NS)
        if d is None:
            return None, None, None
        f = d.find("a:solidFill", NS)
        return (color_child(f) if f is not None else None), d.get("sz"), d.get("b")

    plot = chart_root.find(".//c:plotArea", NS)
    if plot is None:
        return
    for ct in plot:
        kind = etree.QName(ct).localname
        if not kind.endswith("Chart"):
            continue
        grouping = ct.find("c:grouping", NS)
        stacked = grouping is not None and grouping.get("val") in ("stacked", "percentStacked")
        for ser in ct.findall("c:ser", NS):
            sfill = ser.find("c:spPr/a:solidFill", NS)
            sfill = color_child(sfill)
            pts = {}
            for dpt in ser.findall("c:dPt", NS):
                f = dpt.find("c:spPr/a:solidFill", NS)
                if f is not None:
                    pts[dpt.find("c:idx", NS).get("val")] = color_child(f)
            for dls in [ser.find("c:dLbls", NS), ct.find("c:dLbls", NS)]:
                if dls is None:
                    continue
                items = [(dl.find("c:idx", NS).get("val"), dl) for dl in dls.findall("c:dLbl", NS)] or [(None, dls)]
                for idx, dl in items:
                    shown = any((dl.find("c:" + k, NS) is not None and dl.find("c:" + k, NS).get("val") == "1")
                                for k in ("showVal", "showPercent", "showCatName", "showSerName", "showBubbleSize"))
                    if not shown:
                        continue
                    col, sz, b = txpr(dl)
                    if col is None:
                        col, sz, b = txpr(dls)
                    pos = dl.find("c:dLblPos", NS)
                    pos = pos.get("val") if pos is not None else None
                    if kind in ("pieChart", "pie3DChart", "doughnutChart"):
                        inside = pos in (None, "bestFit", "ctr", "inEnd", "inBase") or kind == "doughnutChart"
                    elif kind in ("barChart", "bar3DChart", "areaChart"):
                        inside = pos in ("ctr", "inEnd", "inBase") or (pos is None and (stacked or kind == "areaChart"))
                    else:
                        inside = False
                    under = None
                    if inside:
                        under = pts.get(idx) if idx is not None else None
                        if under is None:
                            under = sfill
                    yield "data label", col, sz, b, under
                break  # series labels win over chart-level ones
    for ax in plot:
        if etree.QName(ax).localname.endswith("Ax"):
            d = ax.find("c:delete", NS)
            if d is not None and d.get("val") == "1":
                continue
            col, sz, b = txpr(ax)
            yield "axis label", col, sz, b, None
    legend = chart_root.find(".//c:legend", NS)
    if legend is not None:
        col, sz, b = txpr(legend)
        yield "legend", col, sz, b, None


# ------------------------------------------------------------------ slide walk
def _walk(parent, tf, pal, scene, sink, master_root, grp_fill=None, check_text=True, part=None):
    for el in parent:
        tag = etree.QName(el).localname
        if tag == "grpSp":
            f = _fill_of(el.find("p:grpSpPr", NS), pal, grp_fill=grp_fill)
            _walk(el, _child_tf(el, tf), pal, scene, sink, master_root, grp_fill=f, check_text=check_text, part=part)
        elif tag in ("sp", "cxnSp"):
            name = el.find(".//p:cNvPr", NS).get("name", "")
            ph = el.find("p:nvSpPr/p:nvPr/p:ph", NS)
            if ph is not None and not check_text:
                continue  # master / layout placeholders are prompts, not painted content
            box = _box(el, tf)
            if box is None:
                continue
            sppr = el.find("p:spPr", NS)
            style = el.find("p:style", NS)
            geom = sppr.find("a:prstGeom", NS) if sppr is not None else None
            hollow = tag == "cxnSp" or (geom is not None and geom.get("prst") in HOLLOW)
            fill = _fill_of(sppr, pal, style, grp_fill)
            if not hollow:
                if fill[0] == "solid":
                    scene.paint(box, fill[1], fill[2], fill[3])
                elif fill[0] == "unknown":
                    scene.paint(box, None, 1.0, "picture or gradient")
            txb = el.find("p:txBody", NS)
            if check_text and txb is not None:
                kind = "otherStyle"
                if ph is not None:
                    kind = "titleStyle" if ph.get("type") in ("title", "ctrTitle") else "bodyStyle"
                fs = txb.find("a:bodyPr/a:normAutofit", NS)
                scale = int(fs.get("fontScale", "100000")) / 100000 if fs is not None else 1.0
                cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                upto = len(scene.regions)
                for t, (rgb, alpha), lab, pt, bold in _runs(txb, pal, master_root, kind, style, scale):
                    under = scene.under(cx, cy, upto)
                    sink(name, t, rgb, alpha, lab, pt, bold, under)
        elif tag == "pic":
            box = _box(el, tf)
            scene.paint(box, None, 1.0, "picture")
        elif tag == "graphicFrame" and check_text:
            name = el.find(".//p:cNvPr", NS).get("name", "")
            box = _box(el, tf)
            if box is None:
                continue
            tbl = el.find(".//a:tbl", NS)
            if tbl is not None:
                widths = [int(g.get("w")) * tf[0] for g in tbl.findall("a:tblGrid/a:gridCol", NS)]
                y = box[1]
                for tr in tbl.findall("a:tr", NS):
                    h = int(tr.get("h", "0")) * tf[1]
                    x = box[0]
                    for i, tc in enumerate(tr.findall("a:tc", NS)):
                        w = widths[i] if i < len(widths) else 0
                        cbox = (x, y, x + w, y + h)
                        f = _fill_of(tc.find("a:tcPr", NS), pal)
                        if f[0] == "solid":
                            scene.paint(cbox, f[1], f[2], f[3])
                        txb = tc.find("a:txBody", NS)
                        if txb is not None:
                            upto = len(scene.regions)
                            for t, (rgb, alpha), lab, pt, bold in _runs(txb, pal, master_root, "otherStyle", None):
                                sink(name, t, rgb, alpha, lab, pt, bold,
                                     scene.under((cbox[0] + cbox[2]) / 2, (cbox[1] + cbox[3]) / 2, upto))
                        x += w
                    y += h
                continue
            chart = el.find(".//c:chart", NS)
            if chart is not None and part is not None:
                rid = chart.get("{%s}id" % NS["r"])
                try:
                    cpart = part.related_part(rid)
                    croot = etree.fromstring(cpart.blob)
                except Exception:  # noqa: BLE001
                    continue
                cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
                csp = croot.find("c:spPr", NS)
                cf = _fill_of(csp, pal) if csp is not None else ("none",)
                base = scene.under(cx, cy)
                if cf[0] == "solid":
                    base = (blend(cf[1], cf[2], base[0]) if base else cf[1], cf[3])
                for what, col, sz, b, inside in _chart_texts(croot, pal):
                    if col is None:
                        col = etree.Element(A + "schemeClr", val="tx1")
                    res = pal.resolve(col)
                    if res is None:
                        continue
                    under = base
                    if inside is not None:
                        ir = pal.resolve(inside)
                        if ir is None:
                            continue
                        under = (blend(ir[0], ir[1], base[0]) if base else ir[0], label(inside))
                    pt = int(sz) / 100 if sz else 10.0
                    sink(name, what, res[0], res[1], label(col), pt, b in ("1", "true"), under)


def check_deck(prs) -> dict:
    """Contrast of every text run of a python-pptx Presentation.

    Returns {"theme": {...}, "checked": n, "unchecked": n, "results": [ {...} ]},
    one result per text run with: slide, shape, text, fg, bg, fg_label,
    bg_label, ratio, need, pt, bold.
    """
    results = []
    unchecked = 0
    first_theme = None
    for n, slide in enumerate(prs.slides, 1):
        layout = slide.slide_layout
        master = layout.slide_master
        try:
            theme = read_theme(master.part.part_related_by(RT_THEME).blob)
        except Exception:  # noqa: BLE001
            theme = {"name": "", "colors": {}, "fonts": {}}
        first_theme = first_theme or theme
        mroot, lroot, sroot = master._element, layout._element, slide._element
        cmap = clr_map(mroot.find("p:clrMap", NS)) or {}
        for root in (lroot, sroot):
            ov = root.find("p:clrMapOvr/a:overrideClrMapping", NS)
            if ov is not None:
                cmap = clr_map(ov)
        pal = Palette(theme, cmap)
        bg = "inherit"
        for root in (sroot, lroot, mroot):
            bg = _bg_of(root.find("p:cSld", NS), pal)
            if bg != "inherit":
                break
        if bg == "inherit":
            res = pal.resolve(etree.Element(A + "schemeClr", val="bg1"))
            bg = (res[0], "paper") if res else None
        scene = Scene(bg)
        for root, part, check in ((mroot, master.part, False), (lroot, layout.part, False), (sroot, slide.part, True)):
            tree = root.find("p:cSld/p:spTree", NS)
            if tree is None:
                continue

            def sink(shape, text, rgb, alpha, lab, pt, bold, under, _n=n):
                nonlocal unchecked
                if under is None:
                    unchecked += 1
                    return
                bg_rgb, bg_lab = under
                fg = blend(rgb, alpha, bg_rgb) if alpha < 0.999 else rgb
                results.append({
                    "slide": _n, "shape": shape, "text": text[:60], "fg": rgb_to_hex(fg), "bg": rgb_to_hex(bg_rgb),
                    "fg_label": lab, "bg_label": bg_lab, "ratio": round(ratio(fg, bg_rgb), 2),
                    "need": needed(pt, bold), "pt": round(pt, 1), "bold": bool(bold),
                })

            _walk(tree, (1.0, 1.0, 0, 0), pal, scene, sink, mroot, check_text=check, part=part)
    return {"theme": first_theme or {}, "checked": len(results), "unchecked": unchecked, "results": results}


# ------------------------------------------------------------------ theme vs contract
def theme_findings(theme: dict, contract: dict, cmap: dict | None = None) -> list:
    """Check a theme against assets/theme-contract.json without looking at slides.

    Returns a list of {"level": "warning", "message": ...} in plain language.
    """
    pal = Palette(theme, cmap)
    out = []
    missing = [s for s in SLOTS if s not in theme.get("colors", {})]
    if missing:
        out.append({"level": "warning", "message": "theme has no value for " + ", ".join(missing)})
        return out
    ink, paper = pal.token("ink"), pal.token("paper")
    lum = {i: luminance(pal.token("a%d" % i)) for i in range(1, 7)}
    light = luminance(paper) > luminance(ink)
    seq = [lum[i] for i in range(1, 7)]
    ordered = all((b > a) if light else (b < a) for a, b in zip(seq, seq[1:]))
    if not ordered:
        shown = ", ".join("accent%d %s" % (i, rgb_to_hex(pal.token("a%d" % i))) for i in range(1, 7))
        out.append({"level": "warning", "message": (
            "accent1 to accent6 are not a ramp from the text colour to the background colour (%s). "
            "The layouts use accent1 as the strongest emphasis and accent6 as the faintest fill, and charts and "
            "scales read them in that order: give the six slots one family of shades, %s." % (
                shown, "darkest first" if light else "lightest first"))})
    else:
        step = contract.get("ramp", {}).get("min_step", 1.1)
        for i in range(1, 6):
            r = ratio(pal.token("a%d" % i), pal.token("a%d" % (i + 1)))
            if r < step:
                out.append({"level": "warning", "message": (
                    "accent%d and accent%d are almost the same lightness (%.2f:1, at least %.2f:1 expected): "
                    "neighbouring levels and series will look identical" % (i, i + 1, r, step))})
    for pair in contract.get("pairs", []):
        fg, bg = pal.token(pair["text"]), pal.token(pair["on"])
        if fg is None or bg is None:
            continue
        r = ratio(fg, bg)
        if r < pair["min_ratio"]:
            what = {"graphic": "%s lines and markers on %s", "link": "%s links on %s"}.get(
                pair.get("kind"), "%s text on %s fills") % (pair["text"], pair["on"])
            where = (" (%d text runs in the libraries)" % pair["runs"]) if pair.get("runs") else ""
            out.append({"level": "warning", "message": "%s: %.1f:1 with this theme, %.1f:1 needed%s" % (
                what, r, pair["min_ratio"], where)})
    return out
