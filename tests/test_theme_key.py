"""The deck.json "theme" key: build_deck.py replaces the deck's theme (colours + fonts) in one pass.

Theme sources are built here: a .thmx with the one-hue brand ramp of the contract tests,
a dark .thmx whose slide master swaps the colour map, and a .pptx with a saturated palette.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "make-clean-pptx" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "tests"))

from _contrast import SLOTS  # noqa: E402
from make_fixtures import make  # noqa: E402
from test_theme_contract import BRAND_RAMP, SATURATED, apply_theme  # noqa: E402

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
# Dark theme the usual way: dk1 stays dark, the master maps the background to dk1 and the text to lt1.
DARK_KEPT = {"dk1": "121212", "lt1": "F2F2F2", "dk2": "232323", "lt2": "D0D0D0",
             "accent1": "EDEDED", "accent2": "AAAAAA", "accent3": "666666", "accent4": "555555",
             "accent5": "3D3D3D", "accent6": "2B2B2B", "hlink": "9CC3FF", "folHlink": "B9A6FF"}
SWAPPED = {"bg1": "dk1", "tx1": "lt1", "bg2": "dk2", "tx2": "lt2"}
SPEC = {"slides": [
    {"slide": 1, "fill": {"Title": "Hello", "Subtitle": "World"}},
    {"slide": 2, "fill": {"Title": "Points", "Body": ["One", "Two"]}},
]}


def theme_xml(colors: dict, major="Georgia", minor="Arial", name="Brand") -> str:
    scheme = "".join('<a:%s><a:srgbClr val="%s"/></a:%s>' % (s, colors[s], s) for s in SLOTS)
    fonts = ('<a:majorFont><a:latin typeface="%s"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
             '<a:minorFont><a:latin typeface="%s"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>') % (major, minor)
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<a:theme xmlns:a="%s" name="%s"><a:themeElements><a:clrScheme name="%s">%s</a:clrScheme>'
            '<a:fontScheme name="%s">%s</a:fontScheme><a:fmtScheme name="%s"/></a:themeElements></a:theme>'
            % (A_NS, name, name, scheme, name, fonts, name))


def make_thmx(path: Path, colors: dict, clrmap: dict | None = None, **fonts) -> Path:
    """A PowerPoint theme file: package -> theme/theme/theme1.xml, with a slide master when a colour map is given."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Override PartName="/theme/theme/theme1.xml" '
                   'ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>')
        z.writestr("_rels/.rels", '<Relationships xmlns="%s"><Relationship Id="rId1" Type="%s/officeDocument" '
                   'Target="theme/theme/theme1.xml"/></Relationships>' % (REL, R_NS))
        z.writestr("theme/theme/theme1.xml", theme_xml(colors, **fonts))
        if clrmap:
            cm = {"bg1": "lt1", "tx1": "dk1", "bg2": "lt2", "tx2": "dk2", **{s: s for s in SLOTS[4:]}}
            cm.update(clrmap)
            attrs = " ".join('%s="%s"' % kv for kv in cm.items())
            z.writestr("theme/slideMasters/slideMaster1.xml",
                       '<p:sldMaster xmlns:a="%s" xmlns:p="%s"><p:cSld><p:spTree/></p:cSld><p:clrMap %s/>'
                       '</p:sldMaster>' % (A_NS, P_NS, attrs))
            z.writestr("theme/slideMasters/_rels/slideMaster1.xml.rels",
                       '<Relationships xmlns="%s"><Relationship Id="rId1" Type="%s/theme" '
                       'Target="../theme/theme1.xml"/></Relationships>' % (REL, R_NS))
    return path


@pytest.fixture(scope="module")
def fx(tmp_path_factory):
    return make(tmp_path_factory.mktemp("fixtures"))


def build(fx, folder: Path, spec: dict):
    """Write the spec in `folder` and build from another working directory: relative paths are the spec's."""
    folder.mkdir(parents=True, exist_ok=True)
    spec = dict(spec, output=str(folder / "deck.pptx"))
    (folder / "deck.json").write_text(json.dumps(spec), encoding="utf-8")
    p = subprocess.run([sys.executable, str(SCRIPTS / "build_deck.py"), "--spec", str(folder / "deck.json"),
                        "--design", fx["design"], "--shapes", fx["shapes"], "--design-index", fx["design_index"],
                        "--shapes-index", fx["shapes_index"]], capture_output=True, encoding="utf-8", cwd=str(ROOT))
    return p.returncode, json.loads(p.stdout), folder / "deck.pptx"


def parts(deck: Path) -> dict:
    with zipfile.ZipFile(deck) as z:
        return {n: z.read(n) for n in z.namelist()}


def slide_parts(deck: Path) -> dict:
    return {n: b for n, b in parts(deck).items() if re.match(r"ppt/slides/(_rels/)?slide\d+\.xml", n)}


def contract_warnings(rep):
    return [w for w in rep["warnings"] if w.startswith("theme:") and "font" not in w]


# ------------------------------------------------------------------ applying a theme
def test_thmx_brand_ramp_replaces_the_theme_only(fx, tmp_path):
    code, plain, plain_deck = build(fx, tmp_path / "plain", SPEC)
    assert code == 0, plain
    (tmp_path / "brand").mkdir()
    make_thmx(tmp_path / "brand" / "brand.thmx", BRAND_RAMP)
    code, rep, deck = build(fx, tmp_path / "brand", dict(SPEC, theme="brand.thmx"))
    assert code == 0, rep
    theme = parts(deck)["ppt/theme/theme1.xml"].decode()
    assert 'name="Brand"' in theme
    for slot, val in BRAND_RAMP.items():
        assert re.search(r"<a:%s><a:srgbClr val=\"%s\"/></a:%s>" % (slot, val, slot), theme), slot
    assert '<a:latin typeface="Georgia"/>' in theme and '<a:latin typeface="Arial"/>' in theme
    assert slide_parts(deck) == slide_parts(plain_deck)            # slides are not touched
    assert rep["theme"]["name"] == "Brand" and rep["theme"]["dark"] is False
    assert rep["theme"]["contract_findings"] == 0 and not contract_warnings(rep)
    assert any("run lint_deck.py and render_check.py again" in w for w in rep["warnings"])  # fonts changed


def test_pptx_source_with_saturated_palette_warns_but_builds(fx, tmp_path):
    src = apply_theme(Path(fx["design"]), tmp_path / "saturated.pptx", SATURATED, "Saturated")
    code, rep, deck = build(fx, tmp_path / "deck", dict(SPEC, theme=str(src)))
    assert code == 0, rep
    assert 'val="E63946"' in parts(deck)["ppt/theme/theme1.xml"].decode()
    found = contract_warnings(rep)
    assert any("not a ramp" in w for w in found)
    assert any(w.startswith("theme: paper text on a2 fills") for w in found)
    assert any("lint_deck.py --contrast" in w for w in found)
    assert rep["theme"]["contract_findings"] >= 3 and rep["slides"] == 2


def test_dark_theme_applies_the_master_colour_map(fx, tmp_path):
    (tmp_path / "d").mkdir()
    make_thmx(tmp_path / "d" / "dark.thmx", DARK_KEPT, clrmap=SWAPPED)
    code, rep, deck = build(fx, tmp_path / "d", dict(SPEC, theme="dark.thmx"))
    assert code == 0, rep
    master = parts(deck)["ppt/slideMasters/slideMaster1.xml"].decode()
    cm = re.search(r"<p:clrMap [^>]*>", master).group(0)
    assert 'bg1="dk1"' in cm and 'tx1="lt1"' in cm and 'accent1="accent1"' in cm
    assert rep["theme"]["dark"] is True and rep["theme"]["colour_map"] == "from the source"
    assert not contract_warnings(rep), contract_warnings(rep)


# ------------------------------------------------------------------ fonts
def test_unlikely_font_uses_the_fallback(fx, tmp_path):
    (tmp_path / "f").mkdir()
    make_thmx(tmp_path / "f" / "t.thmx", BRAND_RAMP, major="Zzq Brand Display", minor="Zzq Brand Text")
    code, rep, deck = build(fx, tmp_path / "f", dict(SPEC, theme="t.thmx", theme_fonts_fallback={"major": "Georgia",
                                                                                                "minor": "Arial"}))
    assert code == 0, rep
    theme = parts(deck)["ppt/theme/theme1.xml"].decode()
    assert '<a:latin typeface="Georgia"/>' in theme and "Zzq" not in theme
    assert sum("fallback" in w for w in rep["warnings"]) == 2
    code, rep, deck = build(fx, tmp_path / "g", dict(SPEC, theme=str(tmp_path / "f" / "t.thmx")))
    assert code == 0 and "Zzq Brand Text" in parts(deck)["ppt/theme/theme1.xml"].decode()
    assert any("theme_fonts_fallback" in w and "substitute" in w for w in rep["warnings"])


# ------------------------------------------------------------------ bad files
@pytest.mark.parametrize("name,content,expected", [
    ("missing.thmx", None, "theme file not found"),
    ("brand.docx", b"x", "not a theme file"),
    ("broken.thmx", b"not a zip", "cannot be opened"),
    ("part.xml", b"<root/>", "not a PowerPoint theme"),
    ("bad.xml", b"<a:theme", "not valid XML"),
])
def test_bad_theme_files_give_plain_errors(fx, tmp_path, name, content, expected):
    if content is not None:
        (tmp_path / "s").mkdir()
        (tmp_path / "s" / name).write_bytes(content)
    code, rep, deck = build(fx, tmp_path / "s", dict(SPEC, theme=name))
    assert code == 2 and expected in rep["error"], rep
    assert not deck.exists()


def test_theme_without_complete_colour_scheme(fx, tmp_path):
    (tmp_path / "s").mkdir()
    partial = {k: v for k, v in BRAND_RAMP.items() if k != "accent6"}
    xml = theme_xml(dict(partial, accent6="ZZZZZZ")).replace('<a:accent6><a:srgbClr val="ZZZZZZ"/></a:accent6>', "")
    (tmp_path / "s" / "theme1.xml").write_text(xml, encoding="utf-8")
    code, rep, _ = build(fx, tmp_path / "s", dict(SPEC, theme="theme1.xml"))
    assert code == 2 and "missing: accent6" in rep["error"]


def test_bad_fallback_shape_stops_before_building(fx, tmp_path):
    (tmp_path / "s").mkdir()
    make_thmx(tmp_path / "s" / "t.thmx", BRAND_RAMP)
    code, rep, deck = build(fx, tmp_path / "s", dict(SPEC, theme="t.thmx", theme_fonts_fallback=["Arial"]))
    assert code == 2 and "theme_fonts_fallback must be" in rep["error"] and not deck.exists()


def test_theme_found_in_working_directory_when_not_next_to_deck_json(fx, tmp_path):
    (tmp_path / "spec").mkdir()
    (tmp_path / "cwd").mkdir()
    make_thmx(tmp_path / "cwd" / "brand.thmx", BRAND_RAMP)
    spec = dict(SPEC, theme="brand.thmx", output=str(tmp_path / "deck.pptx"))
    (tmp_path / "spec" / "deck.json").write_text(json.dumps(spec), encoding="utf-8")
    p = subprocess.run([sys.executable, str(SCRIPTS / "build_deck.py"), "--spec", str(tmp_path / "spec" / "deck.json"),
                        "--design", fx["design"], "--shapes", fx["shapes"], "--design-index", fx["design_index"],
                        "--shapes-index", fx["shapes_index"]], capture_output=True, encoding="utf-8",
                       cwd=str(tmp_path / "cwd"))
    assert p.returncode == 0, p.stdout
    assert 'val="0B2559"' in parts(tmp_path / "deck.pptx")["ppt/theme/theme1.xml"].decode()
