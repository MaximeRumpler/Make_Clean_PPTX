#!/usr/bin/env python3
"""Post-process the raw libraries built by build.js.

    python library/tools/post.py [layouts|visuals|all]

1. Writes the neutral theme (colour and font schemes from theme/tokens.json).
2. Rewrites every token colour as a theme reference (schemeClr + lumMod/lumOff),
   in slides and charts, so that applying another theme recolours everything.
3. Rewrites the sentinel fonts as theme fonts (+mj-lt / +mn-lt, caps for labels).
   Data labels inside dark pie/doughnut slices switch to paper text.
4. Visuals only: gathers the shapes named "<ID>::<field>" into one group named
   <ID>, the unit that build_deck.py inserts into a layout frame.
5. Saves deterministic zips into skills/make-clean-pptx/assets/.
"""
from __future__ import annotations

import json
import re
import sys
import uuid
import zipfile
from collections import OrderedDict
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "out"
ASSETS = REPO / "skills" / "make-clean-pptx" / "assets"
TOKENS = json.loads((ROOT / "theme" / "tokens.json").read_text(encoding="utf-8"))

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
}
A = "{%s}" % NS["a"]
P = "{%s}" % NS["p"]
FIXED_DATE = "2026-10-25T00:00:00Z"

NOFILL = "FEFEFE"
COLOR_MAP = {v["hex"].upper(): v for v in TOKENS["colors"].values()}
# pptxgenjs defaults that cannot be set from build.js
COLOR_MAP["000000"] = TOKENS["colors"]["ink"]     # chart data label text
COLOR_MAP["F9F9F9"] = TOKENS["colors"]["paper"]   # pie and doughnut slice borders
COLOR_MAP["888888"] = TOKENS["colors"]["line"]    # default axis lines of combo charts
FONT_MAP = {
    "MCP Heading": ("mj", False),
    "MCP Body": ("mn", False),
    "MCP Label": ("mn", True),
    "Arial": ("mn", False),  # pptxgenjs default in chart labels
}


# --------------------------------------------------------------------- theme
def theme_xml(xml: str) -> str:
    t = TOKENS["theme"]
    c = t["colors"]

    def slot(tag):
        return f'<a:{tag}><a:srgbClr val="{c[tag]}"/></a:{tag}>'

    scheme = (
        f'<a:clrScheme name="{t["name"]}">'
        + "".join(slot(k) for k in ("dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3",
                                    "accent4", "accent5", "accent6", "hlink", "folHlink"))
        + "</a:clrScheme>"
    )
    fonts = (
        f'<a:fontScheme name="{t["name"]}">'
        f'<a:majorFont><a:latin typeface="{t["fonts"]["major"]}"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
        f'<a:minorFont><a:latin typeface="{t["fonts"]["minor"]}"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
        "</a:fontScheme>"
    )
    xml = re.sub(r"<a:clrScheme\b.*?</a:clrScheme>", scheme, xml, flags=re.S)
    xml = re.sub(r"<a:fontScheme\b.*?</a:fontScheme>", fonts, xml, flags=re.S)
    xml = re.sub(r'(<a:theme\b[^>]*\bname=")[^"]*"', r'\g<1>%s"' % t["name"], xml)
    return xml


# -------------------------------------------------------------- colours/fonts
def recolour(root, unknown: set) -> None:
    for el in list(root.iter(A + "srgbClr")):
        val = (el.get("val") or "").upper().lstrip("#")
        if val == NOFILL:
            fill = el.getparent()
            if fill is not None and fill.tag == A + "solidFill":
                fill.addprevious(etree.Element(A + "noFill"))
                fill.getparent().remove(fill)
            continue
        tok = COLOR_MAP.get(val)
        if not tok:
            unknown.add(val)
            continue
        el.tag = A + "schemeClr"
        el.attrib.clear()
        el.set("val", tok["scheme"])
        mods = []
        for key in ("lumMod", "lumOff"):
            if key in tok:
                m = etree.Element(A + key)
                m.set("val", str(tok[key]))
                mods.append(m)
        for m in reversed(mods):
            el.insert(0, m)


DARK_SLOTS = {"accent1", "accent2", "tx1", "tx2"}  # same rule as is_dark() in scripts/_common.py
C_NS = "{%s}" % NS["c"]


def slice_labels(root) -> int:
    """Data labels drawn inside pie and doughnut slices take paper text on dark slices.

    pptxgenjs gives every label one colour; a dark label on the darkest slice
    is unreadable (and fails `lint_deck.py --contrast`).
    """
    n = 0
    for chart in root.iter(C_NS + "pieChart", C_NS + "doughnutChart"):
        for ser in chart.iter(C_NS + "ser"):
            fills = {}
            for dpt in ser.findall(C_NS + "dPt"):
                clr = dpt.find(C_NS + "spPr/" + A + "solidFill/" + A + "schemeClr")
                if clr is not None:
                    fills[dpt.find(C_NS + "idx").get("val")] = clr.get("val")
            for dl in ser.iter(C_NS + "dLbl"):
                pos = dl.find(C_NS + "dLblPos")
                if pos is not None and pos.get("val") == "outEnd":
                    continue
                if fills.get(dl.find(C_NS + "idx").get("val")) not in DARK_SLOTS:
                    continue
                for clr in dl.iterfind(C_NS + "txPr//" + A + "defRPr/" + A + "solidFill/" + A + "schemeClr"):
                    clr.set("val", "bg1")
                    for m in list(clr):
                        clr.remove(m)
                    n += 1
    return n


def refont(root) -> None:
    for tag, suffix in (("latin", "lt"), ("ea", "ea"), ("cs", "cs")):
        for el in root.iter(A + tag):
            face = el.get("typeface")
            if face in FONT_MAP:
                kind, caps = FONT_MAP[face]
                el.attrib.clear()
                el.set("typeface", f"+{kind}-{suffix}")
                parent = el.getparent()
                if caps and parent is not None and parent.tag in (A + "rPr", A + "defRPr", A + "endParaRPr"):
                    parent.set("cap", "all")


# ------------------------------------------------------------------ grouping
def _name_el(shape):
    found = shape.xpath(".//p:cNvPr", namespaces=NS)
    return found[0] if found else None


def _xfrm(shape):
    if shape.tag == P + "graphicFrame":
        x = shape.find(P + "xfrm")
    elif shape.tag == P + "grpSp":
        x = shape.find(P + "grpSpPr/" + A + "xfrm")
    else:
        x = shape.find(P + "spPr/" + A + "xfrm")
    if x is None:
        return None
    off, ext = x.find(A + "off"), x.find(A + "ext")
    return int(off.get("x")), int(off.get("y")), int(ext.get("cx")), int(ext.get("cy"))


DECOR_URI = "{C183D7F6-B498-43B3-948B-1728B52AA6E4}"
ADEC = "http://schemas.microsoft.com/office/drawing/2017/decorative"


def mark_decorative(root) -> int:
    """Flag rules, dots and backgrounds as decorative so screen readers skip them."""
    n = 0
    for c in root.iter(P + "cNvPr"):
        name = c.get("name") or ""
        if (name.startswith("Decoration") or name.endswith(" mark") or " mark " in name or "::Decoration" in name
                or name.split("::")[-1].endswith((" mark", " stem", " elbow"))):
            if c.find(A + "extLst") is None:
                ext_lst = etree.SubElement(c, A + "extLst")
                ext = etree.SubElement(ext_lst, A + "ext", uri=DECOR_URI)
                d = etree.SubElement(ext, "{%s}decorative" % ADEC, nsmap={"adec": ADEC})
                d.set("val", "1")
                n += 1
    return n


def group_components(root) -> int:
    tree = root.find(P + "cSld/" + P + "spTree")
    shapes = [el for el in tree if el.tag in (P + "sp", P + "graphicFrame", P + "pic", P + "cxnSp", P + "grpSp")]
    groups: "OrderedDict[str, list]" = OrderedDict()
    for el in shapes:
        ne = _name_el(el)
        if ne is not None and "::" in (ne.get("name") or ""):
            prefix, field = ne.get("name").split("::", 1)
            ne.set("name", field)
            groups.setdefault(prefix, []).append(el)
    ids = [int(e.get("id")) for e in root.iter(P + "cNvPr") if (e.get("id") or "").isdigit()]
    next_id = max(ids or [1]) + 1
    for prefix, members in groups.items():
        boxes = [b for b in (_xfrm(m) for m in members) if b]
        x0 = min(b[0] for b in boxes)
        y0 = min(b[1] for b in boxes)
        x1 = max(b[0] + b[2] for b in boxes)
        y1 = max(b[1] + b[3] for b in boxes)
        g = etree.Element(P + "grpSp")
        nv = etree.SubElement(g, P + "nvGrpSpPr")
        c = etree.SubElement(nv, P + "cNvPr", id=str(next_id), name=prefix)
        next_id += 1
        etree.SubElement(nv, P + "cNvGrpSpPr")
        etree.SubElement(nv, P + "nvPr")
        gp = etree.SubElement(g, P + "grpSpPr")
        xf = etree.SubElement(gp, A + "xfrm")
        etree.SubElement(xf, A + "off", x=str(x0), y=str(y0))
        etree.SubElement(xf, A + "ext", cx=str(x1 - x0), cy=str(y1 - y0))
        etree.SubElement(xf, A + "chOff", x=str(x0), y=str(y0))
        etree.SubElement(xf, A + "chExt", cx=str(x1 - x0), cy=str(y1 - y0))
        members[0].addprevious(g)
        for m in members:
            g.append(m)  # moves the element
        _ = c
    return len(groups)


def _stable_zip(data: bytes) -> bytes:
    """Re-zip an embedded package with fixed timestamps, so rebuilds are byte-identical."""
    import io

    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as zi, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in sorted(zi.namelist(), key=lambda n: (n != "[Content_Types].xml", n)):
            part = zi.read(item)
            if item == "docProps/core.xml":
                part = re.sub(rb"(<dcterms:(created|modified)[^>]*>)[^<]*", rb"\g<1>" + FIXED_DATE.encode(), part)
            info = zipfile.ZipInfo(item, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zo.writestr(info, part)
    return out.getvalue()


# ---------------------------------------------------------------------- main
def process(lib: str) -> dict:
    src = OUT / f"{lib}.pptx"
    dst = ASSETS / f"{lib}.pptx"
    dst.parent.mkdir(parents=True, exist_ok=True)
    unknown: set = set()
    n_groups = 0
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        names = zi.namelist()
        # [Content_Types].xml first, as Office expects
        names.sort(key=lambda n: (n != "[Content_Types].xml", n))
        for name in names:
            data = zi.read(name)
            if name.startswith("ppt/theme/") and name.endswith(".xml"):
                data = theme_xml(data.decode("utf-8")).encode("utf-8")
            elif re.match(r"ppt/(slides/slide\d+|charts/chart\d+|slideLayouts/slideLayout\d+|slideMasters/slideMaster\d+)\.xml$", name):
                root = etree.fromstring(data)
                recolour(root, unknown)
                refont(root)
                if name.startswith("ppt/charts/"):
                    slice_labels(root)
                if name.startswith("ppt/slides/"):
                    mark_decorative(root)
                if lib == "visuals" and name.startswith("ppt/slides/"):
                    n_groups += group_components(root)
                data = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            elif name == "ppt/presentation.xml":
                # section ids are random GUIDs: derive them from the section name instead
                data = re.sub(rb'(<p14:section name="([^"]*)" id=")\{[^}]*\}"',
                              lambda m: m.group(1) + ("{%s}" % uuid.uuid5(uuid.NAMESPACE_URL, lib + m.group(2).decode())).encode() + b'"',
                              data)
            elif name == "docProps/core.xml":
                data = re.sub(rb"(<dcterms:(created|modified)[^>]*>)[^<]*", rb"\g<1>" + FIXED_DATE.encode(), data)
            elif name.startswith("ppt/embeddings/") and name.endswith(".xlsx"):
                data = _stable_zip(data)  # chart workbooks: same bytes on every build
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            zo.writestr(info, data)
    return {"lib": lib, "output": str(dst), "groups": n_groups, "unknown_colours": sorted(unknown)}


def main(argv):
    which = argv[1] if len(argv) > 1 else "all"
    libs = ["layouts", "visuals"] if which == "all" else [which]
    report = [process(lib) for lib in libs if (OUT / f"{lib}.pptx").exists()]
    print(json.dumps(report, indent=2))
    return 1 if any(r["unknown_colours"] for r in report) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
