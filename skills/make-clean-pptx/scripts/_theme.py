"""Apply a brand theme (colours + fonts) to a built deck: the deck.json "theme" key.

    source = load_theme_source(path)      # .thmx, .potx, .pptx or a theme .xml part
    report, warnings = apply_theme(prs, source, fallback=None)

Only the colour scheme, the font scheme and the theme name are replaced; the
format scheme (line, effect and background styles) stays the library's, so the
slides keep their look and no relationship of the theme part has to move. Slides
are not touched: every colour and font in the libraries is a theme reference.

When the source carries a slide master, its colour map is applied too: that is
how dark themes are usually built (dk1 stays dark, the master maps the
background to dk1 and the text to lt1).

The theme is then checked against assets/theme-contract.json (accent ramp, text
and fill pairs). Findings are warnings only: the build never fails on them.
Standard library + lxml (comes with python-pptx).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import zipfile
from copy import deepcopy
from pathlib import Path, PurePosixPath

from lxml import etree

from _contrast import NS, RT_THEME, SLOTS, Palette, clr_map, luminance, read_theme, theme_findings

A = "{%s}" % NS["a"]
P = "{%s}" % NS["p"]
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
THEME_EXT = {".thmx", ".potx", ".pptx", ".potm", ".pptm", ".xml"}
CONTRACT = Path(__file__).resolve().parent.parent / "assets" / "theme-contract.json"
CLRMAP_KEYS = ("bg1", "tx1", "bg2", "tx2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
               "hlink", "folHlink")

# Fonts that ship with Windows, macOS and Microsoft Office: safe to assume on the machine that opens the deck.
COMMON_FONTS = {
    "arial", "arial black", "arial narrow", "calibri", "calibri light", "cambria", "candara", "consolas",
    "constantia", "corbel", "courier new", "georgia", "tahoma", "times new roman", "trebuchet ms", "verdana",
    "aptos", "aptos display", "aptos narrow", "segoe ui", "helvetica", "helvetica neue", "gill sans mt",
    "century gothic", "franklin gothic medium", "garamond", "palatino linotype", "book antiqua", "impact",
}


class ThemeError(ValueError):
    """A theme file that cannot be used, explained in plain words."""


# ------------------------------------------------------------------ reading the source
def _rels(z: zipfile.ZipFile, part: str) -> dict:
    """{rel type suffix: absolute part name} for one part of a package."""
    p = PurePosixPath(part)
    name = str(p.parent / "_rels" / (p.name + ".rels"))
    if name not in z.namelist():
        return {}
    out = {}
    for rel in etree.fromstring(z.read(name)).iter(PKG_REL + "Relationship"):
        if rel.get("TargetMode") == "External":
            continue
        target = rel.get("Target", "")
        full = target.lstrip("/") if target.startswith("/") else os.path.normpath(str(p.parent / target))
        out.setdefault(rel.get("Type", "").rsplit("/", 1)[-1], full.replace(os.sep, "/"))
    return out


def _parse(data: bytes, what: str):
    try:
        return etree.fromstring(data)
    except etree.XMLSyntaxError as exc:
        raise ThemeError("%s is not valid XML (%s)" % (what, exc)) from exc


def load_theme_source(path) -> dict:
    """Read a theme file. Returns {"path", "root" (a:theme element), "clrmap" (dict or None)}.

    Raises ThemeError with a plain-language message when the file cannot be used.
    """
    path = Path(path)
    shown = path.name
    if not path.is_file():
        raise ThemeError("theme file not found: %s (a relative path is read from the folder of deck.json)" % path)
    ext = path.suffix.lower()
    if ext not in THEME_EXT:
        raise ThemeError("%s is not a theme file: use a PowerPoint theme (.thmx), a template (.potx), "
                         "a presentation (.pptx) or a theme part (.xml)" % shown)
    clrmap = None
    if ext == ".xml":
        root = _parse(path.read_bytes(), shown)
    else:
        try:
            z = zipfile.ZipFile(path)
        except (zipfile.BadZipFile, OSError) as exc:
            raise ThemeError("%s cannot be opened: it is not a valid %s file (damaged, or renamed from another "
                             "format?)" % (shown, ext)) from exc
        with z:
            names = z.namelist()
            masters = sorted((n for n in names if re.search(r"(^|/)slideMasters/slideMaster\d+\.xml$", n)),
                             key=lambda n: int(re.search(r"(\d+)\.xml$", n).group(1)))
            theme_part = None
            if masters:
                theme_part = _rels(z, masters[0]).get("theme")
                cm = _parse(z.read(masters[0]), shown + " (slide master)").find("p:clrMap", NS)
                clrmap = clr_map(cm)
            if not theme_part:
                doc = _rels(z, "").get("officeDocument", "")
                if re.search(r"theme\d*\.xml$", doc):
                    theme_part = doc
            if not theme_part:
                found = sorted(n for n in names if re.search(r"(^|/)theme/theme\d+\.xml$", n))
                theme_part = found[0] if found else None
            if not theme_part or theme_part not in names:
                raise ThemeError("%s contains no PowerPoint theme" % shown)
            root = _parse(z.read(theme_part), shown)
    if root.tag != A + "theme":
        raise ThemeError("%s is not a PowerPoint theme (its root element is <%s>, expected <a:theme>)" % (
            shown, etree.QName(root).localname))
    colors = read_theme(etree.tostring(root))["colors"]
    missing = [s for s in SLOTS if s not in colors]
    if root.find("a:themeElements/a:clrScheme", NS) is None or missing:
        raise ThemeError("%s has no complete colour scheme (missing: %s)" % (shown, ", ".join(missing) or "all"))
    if clrmap is not None and not set(CLRMAP_KEYS) <= set(clrmap):
        clrmap = None
    return {"path": str(path), "root": root, "clrmap": clrmap}


# ------------------------------------------------------------------ fonts
_INSTALLED = None


def _installed_fonts() -> set:
    """Lower-case family names (and font file stems) found on this machine; empty when unknown."""
    global _INSTALLED
    if _INSTALLED is not None:
        return _INSTALLED
    found = set()
    if shutil.which("fc-list"):
        try:
            out = subprocess.run(["fc-list", ":", "family"], capture_output=True, encoding="utf-8",
                                 errors="replace", timeout=20).stdout
            for line in out.splitlines():
                found.update(f.strip().lower() for f in line.split(",") if f.strip())
        except (OSError, subprocess.SubprocessError):
            pass
    dirs = [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts"),
            "/Library/Fonts", "/System/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
    for d in dirs:
        if d and os.path.isdir(d):
            try:
                found.update("file:" + re.sub(r"[^a-z0-9]", "", Path(f).stem.lower()) for f in os.listdir(d))
            except OSError:
                pass
    _INSTALLED = found
    return found


def font_available(name: str) -> bool:
    """True when the font is common (Windows, macOS, Office) or installed here."""
    low = name.strip().lower()
    if low in COMMON_FONTS:
        return True
    inst = _installed_fonts()
    if low in inst:
        return True
    key = re.sub(r"[^a-z0-9]", "", low)
    return bool(key) and any(f.startswith("file:" + key) for f in inst)


def fallback_fonts(value) -> dict:
    """theme_fonts_fallback as {"major", "minor"}; ThemeError when it has the wrong shape."""
    if not value:
        return {}
    if isinstance(value, str):
        return {"major": value, "minor": value}
    if isinstance(value, dict) and set(value) <= {"major", "minor"} and all(isinstance(v, str) for v in value.values()):
        return dict(value)
    raise ThemeError('theme_fonts_fallback must be a font name ("Arial") or {"major": "...", "minor": "..."}')


# ------------------------------------------------------------------ applying
def _latin(font_scheme, role):
    return font_scheme.find("a:%sFont/a:latin" % role, NS) if font_scheme is not None else None


def apply_theme(prs, source: dict, fallback=None) -> tuple:
    """Replace colours, fonts and name of every slide master's theme; apply the source colour map.

    Returns (report dict, list of warning strings).
    """
    fallbacks = fallback_fonts(fallback)
    src = source["root"]
    src_clr = src.find("a:themeElements/a:clrScheme", NS)
    src_fonts = src.find("a:themeElements/a:fontScheme", NS)
    name = src.get("name") or src_clr.get("name") or Path(source["path"]).stem
    warnings = []
    parts = []
    for master in prs.slide_masters:
        part = master.part.part_related_by(RT_THEME)
        if all(part is not p for p in parts):
            parts.append(part)

    # fonts: the brand font when it is likely to be there, else the fallback when one is given
    first = etree.fromstring(parts[0].blob).find("a:themeElements/a:fontScheme", NS)
    before, use = {}, {}
    for role in ("major", "minor"):
        old, new = _latin(first, role), _latin(src_fonts, role)
        before[role] = old.get("typeface", "") if old is not None else ""
        face = (new.get("typeface", "") if new is not None else "") or before[role]
        use[role] = face
        if face == before[role] or font_available(face):
            continue
        what = "headings" if role == "major" else "body text"
        if fallbacks.get(role):
            use[role] = fallbacks[role]
            warnings.append("theme: font '%s' (%s) is not a common font and is not installed here, so the theme "
                            "uses the fallback '%s' from theme_fonts_fallback; install the brand font and remove "
                            "the fallback to get it back." % (face, what, fallbacks[role]))
        else:
            warnings.append("theme: font '%s' (%s) is not a common font and is not installed here: PowerPoint or "
                            "LibreOffice will substitute another one where it is missing. Set theme_fonts_fallback "
                            "in deck.json (e.g. \"Arial\") or install the font." % (face, what))
    if use != before:
        warnings.append("theme: fonts are now %s (headings) and %s (body); the character limits were measured with "
                        "%s, so run lint_deck.py and render_check.py again and shorten any text that overflows." % (
                            use["major"], use["minor"], before["minor"] or "the library fonts"))

    for part in parts:
        root = etree.fromstring(part.blob)
        elements = root.find("a:themeElements", NS)
        elements.replace(elements.find("a:clrScheme", NS), deepcopy(src_clr))
        old_fonts = elements.find("a:fontScheme", NS)
        fonts = deepcopy(src_fonts) if src_fonts is not None else old_fonts
        for role, face in use.items():
            el = _latin(fonts, role)
            if el is not None and el.get("typeface") != face:
                el.set("typeface", face)
                for attr in ("panose", "pitchFamily", "charset"):  # they describe the replaced font
                    el.attrib.pop(attr, None)
        if fonts is not old_fonts:
            if old_fonts is not None:
                elements.replace(old_fonts, fonts)
            else:
                elements.find("a:clrScheme", NS).addnext(fonts)
        root.set("name", name)
        part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # colour map: dark themes keep dk1 dark and swap the map on the master
    cmap = source.get("clrmap")
    if cmap:
        for master in prs.slide_masters:
            el = master._element.find("p:clrMap", NS)
            if el is None:
                continue
            for k in list(el.attrib):
                del el.attrib[k]
            for k in CLRMAP_KEYS:
                el.set(k, cmap[k])
    master = prs.slide_masters[0]
    eff_map = clr_map(master._element.find("p:clrMap", NS))
    theme = read_theme(etree.tostring(src))
    theme["fonts"] = use
    pal = Palette(theme, eff_map)
    dark = luminance(pal.token("paper")) < luminance(pal.token("ink"))

    # contract check: warnings only
    findings = []
    if CONTRACT.is_file():
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        findings = [f["message"] for f in theme_findings(theme, contract, eff_map)]
    warnings.extend("theme: " + m for m in findings)
    if findings:
        warnings.append("theme: the deck is built, but the theme breaks the contract above "
                        "(references/theme-contract.md); fix the theme, not the slides, and check the deck with "
                        "lint_deck.py --contrast.")
    report = {"source": source["path"], "name": name, "fonts": use, "dark": dark,
              "colour_map": "from the source" if cmap else "kept", "contract_findings": len(findings)}
    return report, warnings
