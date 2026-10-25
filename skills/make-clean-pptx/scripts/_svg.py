"""Convert simple SVG icons and illustrations into native PowerPoint shapes.

Why native shapes and not pictures: they stay sharp at any size, they take the
theme colours (so a rebrand recolours them), and they can be edited in
PowerPoint or LibreOffice. Only the standard library is used.

Supported: path (all commands, arcs included), circle, ellipse, rect (rounded),
line, polyline, polygon, nested <g>, transforms (matrix, translate, scale,
rotate), presentation attributes and inline style. Not supported (the element is
skipped and reported): gradients, patterns, masks, clip paths, text, images.
"""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

EMU_PER_INCH = 914400
SCALE = 1000  # path coordinate resolution (viewBox units x SCALE)

# Theme greys from dark to light, used by the "grey" colour mode.
GREY_RAMP = [
    (0x11, '<a:schemeClr val="tx1"/>'),
    (0x59, '<a:schemeClr val="accent2"/>'),
    (0x8C, '<a:schemeClr val="accent3"/>'),
    (0xB3, '<a:schemeClr val="accent4"/>'),
    (0xD0, '<a:schemeClr val="accent5"/>'),
    (0xE6, '<a:schemeClr val="accent6"/>'),
    (0xFF, '<a:schemeClr val="bg1"/>'),
]

NAMED = {"black": "000000", "white": "FFFFFF", "red": "FF0000", "green": "008000", "blue": "0000FF",
         "gray": "808080", "grey": "808080", "yellow": "FFFF00", "orange": "FFA500"}


class SvgError(ValueError):
    pass


# ----------------------------------------------------------------- geometry
def _mat_mul(a, b):
    return (
        a[0] * b[0] + a[2] * b[1], a[1] * b[0] + a[3] * b[1],
        a[0] * b[2] + a[2] * b[3], a[1] * b[2] + a[3] * b[3],
        a[0] * b[4] + a[2] * b[5] + a[4], a[1] * b[4] + a[3] * b[5] + a[5],
    )


IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def parse_transform(s: str | None):
    m = IDENT
    if not s:
        return m
    for name, args in re.findall(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)", s):
        v = [float(x) for x in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", args)]
        if name == "matrix" and len(v) == 6:
            t = tuple(v)
        elif name == "translate":
            t = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            t = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == "rotate":
            a = math.radians(v[0])
            c, sn = math.cos(a), math.sin(a)
            t = (c, sn, -sn, c, 0, 0)
            if len(v) == 3:
                t = _mat_mul(_mat_mul((1, 0, 0, 1, v[1], v[2]), t), (1, 0, 0, 1, -v[1], -v[2]))
        elif name == "skewX":
            t = (1, 0, math.tan(math.radians(v[0])), 1, 0, 0)
        else:
            t = (1, math.tan(math.radians(v[0])), 0, 1, 0, 0)
        m = _mat_mul(m, t)
    return m


def _apply(m, x, y):
    return m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]


def _arc_to_cubics(x1, y1, rx, ry, phi, large, sweep, x2, y2):
    """SVG elliptical arc to a list of cubic segments (endpoint parameterisation, SVG spec F.6)."""
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2):
        return [(x1, y1, x2, y2, x2, y2)] if (x1, y1) != (x2, y2) else []
    rx, ry = abs(rx), abs(ry)
    p = math.radians(phi % 360)
    cp, sp = math.cos(p), math.sin(p)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    lam = (x1p ** 2) / (rx ** 2) + (y1p ** 2) / (ry ** 2)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large == sweep:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cp * cxp - sp * cyp + (x1 + x2) / 2
    cy = sp * cxp + cp * cyp + (y1 + y2) / 2

    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(1, int(math.ceil(abs(dt) / (math.pi / 2) - 1e-9)))
    step = dt / n
    k = 4 / 3 * math.tan(step / 4)
    out = []
    t = t1
    for _ in range(n):
        c1, s1 = math.cos(t), math.sin(t)
        c2, s2 = math.cos(t + step), math.sin(t + step)
        e1 = (c1 - k * s1, s1 + k * c1)
        e2 = (c2 + k * s2, s2 - k * c2)
        pts = []
        for ex, ey in (e1, e2, (c2, s2)):
            px, py = rx * ex, ry * ey
            pts += [cp * px - sp * py + cx, sp * px + cp * py + cy]
        out.append(tuple(pts))
        t += step
    return out


_TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def parse_path(d: str):
    """Return a list of subpaths; each is a list of ('M'|'L'|'C'|'Z', coords...)."""
    toks = _TOKEN.findall(d or "")
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    last_c2 = last_q = None
    segs = []

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    def flag():  # arc flags may be packed without separators: "a1 1 0 011 1"
        nonlocal i
        t = toks[i].lstrip("+")
        if not t or t[0] not in "01":
            raise SvgError(f"invalid arc flag '{toks[i]}'")
        if len(t) > 1:
            toks[i] = t[1:]  # "01.471" = flag 0, then "1.471" (flag, then a number)
        else:
            i += 1
        return int(t[0])

    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t
            i += 1
            if cmd in "Zz":
                segs.append(("Z",))
                x, y = sx, sy
                last_c2 = last_q = None
                continue
        elif cmd is None:
            raise SvgError("path data must start with a command")
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if c == "M":
            x, y = num() + ox, num() + oy
            sx, sy = x, y
            segs.append(("M", x, y))
            cmd = "l" if rel else "L"
            last_c2 = last_q = None
        elif c == "L":
            x, y = num() + ox, num() + oy
            segs.append(("L", x, y))
            last_c2 = last_q = None
        elif c == "H":
            x = num() + (x if rel else 0.0)
            segs.append(("L", x, y))
            last_c2 = last_q = None
        elif c == "V":
            y = num() + (y if rel else 0.0)
            segs.append(("L", x, y))
            last_c2 = last_q = None
        elif c == "C":
            x1, y1, x2, y2 = num() + ox, num() + oy, num() + ox, num() + oy
            x, y = num() + ox, num() + oy
            segs.append(("C", x1, y1, x2, y2, x, y))
            last_c2, last_q = (x2, y2), None
        elif c == "S":
            x1, y1 = (2 * x - last_c2[0], 2 * y - last_c2[1]) if last_c2 else (x, y)
            x2, y2 = num() + ox, num() + oy
            x, y = num() + ox, num() + oy
            segs.append(("C", x1, y1, x2, y2, x, y))
            last_c2, last_q = (x2, y2), None
        elif c in "QT":
            if c == "Q":
                qx, qy = num() + ox, num() + oy
            else:
                qx, qy = (2 * x - last_q[0], 2 * y - last_q[1]) if last_q else (x, y)
            nx, ny = num() + ox, num() + oy
            segs.append(("C", x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y), nx + 2 / 3 * (qx - nx), ny + 2 / 3 * (qy - ny), nx, ny))
            x, y = nx, ny
            last_q, last_c2 = (qx, qy), None
        elif c == "A":
            rx, ry, phi = num(), num(), num()
            large, sweep = flag(), flag()
            nx, ny = num() + ox, num() + oy
            for cub in _arc_to_cubics(x, y, rx, ry, phi, large, sweep, nx, ny):
                segs.append(("C",) + cub)
            x, y = nx, ny
            last_c2 = last_q = None
        else:
            raise SvgError(f"unsupported path command {cmd}")
    return segs


K = 0.5522847498


def _ellipse(cx, cy, rx, ry):
    return [
        ("M", cx + rx, cy),
        ("C", cx + rx, cy + K * ry, cx + K * rx, cy + ry, cx, cy + ry),
        ("C", cx - K * rx, cy + ry, cx - rx, cy + K * ry, cx - rx, cy),
        ("C", cx - rx, cy - K * ry, cx - K * rx, cy - ry, cx, cy - ry),
        ("C", cx + K * rx, cy - ry, cx + rx, cy - K * ry, cx + rx, cy),
        ("Z",),
    ]


def _rect(x, y, w, h, rx, ry):
    if not rx and not ry:
        return [("M", x, y), ("L", x + w, y), ("L", x + w, y + h), ("L", x, y + h), ("Z",)]
    rx = min(rx or ry, w / 2)
    ry = min(ry or rx, h / 2)
    kx, ky = K * rx, K * ry
    return [
        ("M", x + rx, y), ("L", x + w - rx, y), ("C", x + w - rx + kx, y, x + w, y + ry - ky, x + w, y + ry),
        ("L", x + w, y + h - ry), ("C", x + w, y + h - ry + ky, x + w - rx + kx, y + h, x + w - rx, y + h),
        ("L", x + rx, y + h), ("C", x + rx - kx, y + h, x, y + h - ry + ky, x, y + h - ry),
        ("L", x, y + ry), ("C", x, y + ry - ky, x + rx - kx, y, x + rx, y), ("Z",),
    ]


def _f(el, name, default=0.0):
    v = el.get(name)
    if v is None:
        return default
    m = re.match(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", v.strip())
    return float(m.group(0)) if m else default


# ------------------------------------------------------------------ styling
STYLE_KEYS = ("fill", "stroke", "stroke-width", "fill-opacity", "stroke-opacity", "opacity", "display", "visibility")


def _style(el, inherited):
    st = dict(inherited)
    for k in STYLE_KEYS:
        if el.get(k) is not None:
            st[k] = el.get(k).strip()
    for part in (el.get("style") or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            if k.strip() in STYLE_KEYS:
                st[k.strip()] = v.strip()
    return st


def _colour(v):
    """Return 'current', 'none' or an RRGGBB string."""
    if v is None:
        return "000000"
    v = v.strip().lower()
    if v in ("none", "transparent"):
        return "none"
    if v == "currentcolor":
        return "current"
    if v.startswith("url("):
        return "unsupported"
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return h[:6].upper()
    m = re.match(r"rgb\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)", v)
    if m:
        return "%02X%02X%02X" % tuple(int(g) for g in m.groups())
    return NAMED.get(v, "000000")


def _num(v, default):
    try:
        v = str(v).strip()
        return float(v[:-1]) / 100 if v.endswith("%") else float(v)
    except (TypeError, ValueError):
        return default


def _local(tag):
    return tag.rsplit("}", 1)[-1]


MAX_SVG_CHARS = 5_000_000


def parse_svg(text: str):
    """Return (viewbox, items, skipped). Each item: dict(segs, fill, stroke, width)."""
    if len(text) > MAX_SVG_CHARS:
        raise SvgError("SVG too large (over 5 MB); simplify it or use a picture")
    if re.search(r"<!(DOCTYPE|ENTITY)", text, re.I):
        raise SvgError("SVG with a DOCTYPE or entity declarations is refused (unsafe XML)")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise SvgError(f"not valid SVG: {exc}") from exc
    if _local(root.tag) != "svg":
        raise SvgError("root element is not <svg>")
    vb = root.get("viewBox") or root.get("viewbox")
    if vb:
        minx, miny, vw, vh = [float(v) for v in re.split(r"[ ,]+", vb.strip())[:4]]
    else:
        minx = miny = 0.0
        vw, vh = _f(root, "width", 24), _f(root, "height", 24)
    items, skipped = [], set()

    def walk(el, m, st):
        tag = _local(el.tag)
        st = _style(el, st)
        if st.get("display") == "none" or st.get("visibility") == "hidden":
            return
        m = _mat_mul(m, parse_transform(el.get("transform")))
        if tag in ("svg", "g", "a"):
            for ch in el:
                walk(ch, m, st)
            return
        if tag in ("defs", "title", "desc", "metadata", "style", "clipPath", "mask", "linearGradient", "radialGradient", "pattern", "symbol"):
            return
        if tag == "path":
            segs = parse_path(el.get("d"))
        elif tag == "circle":
            r = _f(el, "r")
            segs = _ellipse(_f(el, "cx"), _f(el, "cy"), r, r)
        elif tag == "ellipse":
            segs = _ellipse(_f(el, "cx"), _f(el, "cy"), _f(el, "rx"), _f(el, "ry"))
        elif tag == "rect":
            segs = _rect(_f(el, "x"), _f(el, "y"), _f(el, "width"), _f(el, "height"), _f(el, "rx", 0), _f(el, "ry", 0))
        elif tag == "line":
            segs = [("M", _f(el, "x1"), _f(el, "y1")), ("L", _f(el, "x2"), _f(el, "y2"))]
        elif tag in ("polyline", "polygon"):
            nums = [float(v) for v in re.findall(r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?", el.get("points") or "")]
            pts = list(zip(nums[0::2], nums[1::2]))
            if not pts:
                return
            segs = [("M",) + pts[0]] + [("L",) + p for p in pts[1:]] + ([("Z",)] if tag == "polygon" else [])
        else:
            skipped.add(tag)
            return
        fill, stroke = _colour(st.get("fill", "#000")), _colour(st.get("stroke", "none"))
        if "unsupported" in (fill, stroke):
            skipped.add("gradient/pattern")
            fill = "none" if fill == "unsupported" else fill
            stroke = "none" if stroke == "unsupported" else stroke
        if fill == "none" and stroke == "none":
            return
        width = float(re.sub(r"[^0-9.]", "", st.get("stroke-width", "1")) or 1)
        scale = math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1
        out = []
        for s in segs:
            if s[0] == "Z":
                out.append(s)
            else:
                pts = s[1:]
                tp = []
                for k in range(0, len(pts), 2):
                    tp.extend(_apply(m, pts[k], pts[k + 1]))
                out.append((s[0],) + tuple(tp))
        op = _num(st.get("opacity"), 1.0)
        items.append({"segs": out, "fill": fill, "stroke": stroke, "width": width * scale,
                      "fill_alpha": op * _num(st.get("fill-opacity"), 1.0), "stroke_alpha": op * _num(st.get("stroke-opacity"), 1.0)})

    for ch in root:
        walk(ch, IDENT, _style(root, {"fill": "#000"}))
    return (minx, miny, vw, vh), items, sorted(skipped)


# ------------------------------------------------------------------- output
def _grey(hexcol):
    r, g, b = int(hexcol[0:2], 16), int(hexcol[2:4], 16), int(hexcol[4:6], 16)
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return min(GREY_RAMP, key=lambda t: abs(t[0] - lum))[1]


def _clr(c, mode, mono_xml, alpha=1.0):
    if c == "current" or mode == "mono":
        xml = mono_xml
    elif mode == "grey":
        xml = _grey(c)
    else:
        xml = f'<a:srgbClr val="{c}"/>'
    if alpha < 0.999:
        m = re.match(r"<(a:\w+)(.*?)(/?)>(.*)$", xml, re.S)
        tag, attrs, selfclose, rest = m.groups()
        inner = "" if selfclose else rest.rsplit(f"</{tag}>", 1)[0]
        xml = f'<{tag}{attrs}>{inner}<a:alpha val="{int(alpha * 100000)}"/></{tag}>'
    return xml


def _path_xml(segs, minx, miny, pw, ph, fill_none):
    def p(x, y):
        return f'<a:pt x="{int(round((x - minx) * SCALE))}" y="{int(round((y - miny) * SCALE))}"/>'

    body = []
    for s in segs:
        if s[0] == "M":
            body.append(f"<a:moveTo>{p(s[1], s[2])}</a:moveTo>")
        elif s[0] == "L":
            body.append(f"<a:lnTo>{p(s[1], s[2])}</a:lnTo>")
        elif s[0] == "C":
            body.append(f"<a:cubicBezTo>{p(s[1], s[2])}{p(s[3], s[4])}{p(s[5], s[6])}</a:cubicBezTo>")
        else:
            body.append("<a:close/>")
    attrs = f'w="{pw}" h="{ph}"' + (' fill="none"' if fill_none else "")
    return f"<a:path {attrs}>{''.join(body)}</a:path>"


def svg_to_shapes(text, x, y, w, h, *, name="Icon", mode="mono", mono_xml='<a:schemeClr val="tx1"/>',
                  start_id=1000, descr="", weight=1.0):
    """Return (xml, info). xml is one <p:sp> or a <p:grpSp> of several, fitted
    ("contain") into the EMU box (x, y, w, h).

    mode: "mono" (every colour becomes mono_xml, the slot colour), "grey" (colours
    mapped by lightness to the theme greys) or "keep" (original colours).
    weight: multiplies stroke widths (0.75 gives lighter line icons at large sizes).
    """
    (minx, miny, vw, vh), items, skipped = parse_svg(text)
    if not items:
        raise SvgError("nothing drawable in this SVG")
    scale = min(w / vw, h / vh)
    sw, sh = int(vw * scale), int(vh * scale)
    sx, sy = int(x + (w - sw) / 2), int(y + (h - sh) / 2)
    pw, ph = int(vw * SCALE), int(vh * SCALE)

    groups = {}
    for it in items:
        key = (it["fill"], it["stroke"], round(it["width"] * weight, 3) if it["stroke"] != "none" else 0,
               round(it["fill_alpha"], 2), round(it["stroke_alpha"], 2))
        groups.setdefault(key, []).append(it)

    shapes = []
    nid = start_id
    for (fill, stroke, width, fa, sa), its in groups.items():
        paths = "".join(_path_xml(it["segs"], minx, miny, pw, ph, fill == "none") for it in its)
        fill_xml = "<a:noFill/>" if fill == "none" else f"<a:solidFill>{_clr(fill, mode, mono_xml, fa)}</a:solidFill>"
        if stroke == "none":
            ln = "<a:ln><a:noFill/></a:ln>"
        else:
            ln = (f'<a:ln w="{max(3175, int(width * scale))}" cap="rnd"><a:solidFill>{_clr(stroke, mode, mono_xml, sa)}</a:solidFill>'
                  f"<a:round/></a:ln>")
        nid += 1
        shapes.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{nid}" name="{name if len(groups) == 1 else name + " part " + str(len(shapes) + 1)}" descr="{_esc(descr)}"/>'
            f"<p:cNvSpPr/><p:nvPr/></p:nvSpPr><p:spPr><a:xfrm><a:off x=\"{sx}\" y=\"{sy}\"/><a:ext cx=\"{sw}\" cy=\"{sh}\"/></a:xfrm>"
            f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst>{paths}</a:pathLst></a:custGeom>'
            f"{fill_xml}{ln}</p:spPr></p:sp>"
        )
    if len(shapes) == 1:
        xml = shapes[0]
    else:
        nid += 1
        xml = (f'<p:grpSp><p:nvGrpSpPr><p:cNvPr id="{nid}" name="{name}" descr="{_esc(descr)}"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
               f'<p:grpSpPr><a:xfrm><a:off x="{sx}" y="{sy}"/><a:ext cx="{sw}" cy="{sh}"/><a:chOff x="{sx}" y="{sy}"/>'
               f'<a:chExt cx="{sw}" cy="{sh}"/></a:xfrm></p:grpSpPr>{"".join(shapes)}</p:grpSp>')
    ns = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
          'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
    xml = xml.replace("<p:sp>", f"<p:sp {ns}>", 1) if len(shapes) == 1 else xml.replace("<p:grpSp>", f"<p:grpSp {ns}>", 1)
    return xml, {"shapes": len(shapes), "skipped": skipped, "box": [sx, sy, sw, sh]}


def _esc(s):
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
