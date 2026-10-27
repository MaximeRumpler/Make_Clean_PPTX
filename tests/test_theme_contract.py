"""The theme contract (assets/theme-contract.json) and `lint_deck.py --contrast`.

Three themes are applied to copies of the bundled libraries:
- a brand ramp (one hue, dark to light) that respects the contract: no failure;
- a dark theme (light text on dark paper, accent ramp reversed): no failure;
- a saturated theme (six unrelated brand hues): the contract catches it.
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
SKILL = ROOT / "skills" / "make-clean-pptx"
ASSETS = SKILL / "assets"
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _contrast import SLOTS, apply_mods, hex_to_rgb, ratio, read_theme, rgb_to_hex, theme_findings  # noqa: E402

CONTRACT = json.loads((ASSETS / "theme-contract.json").read_text(encoding="utf-8"))

# One hue from dark to light: what a brand theme that follows the contract looks like.
BRAND_RAMP = {"dk1": "14213D", "lt1": "FFFFFF", "dk2": "33415C", "lt2": "F1F4F9",
              "accent1": "0B2559", "accent2": "2D4F8E", "accent3": "7391C4", "accent4": "A9BFE0",
              "accent5": "CCDAEF", "accent6": "E3EAF6", "hlink": "2D4F8E", "folHlink": "5A6B8C"}
# Light text on dark paper: dk1/lt1 swap their values and accent1 is now the lightest.
DARK = {"dk1": "F2F2F2", "lt1": "121212", "dk2": "D0D0D0", "lt2": "232323",
        "accent1": "EDEDED", "accent2": "AAAAAA", "accent3": "666666", "accent4": "555555",
        "accent5": "3D3D3D", "accent6": "2B2B2B", "hlink": "9CC3FF", "folHlink": "B9A6FF"}
# Six unrelated hues, the usual brand palette: out of contract.
SATURATED = {"dk1": "000000", "lt1": "FFFFFF", "dk2": "1D3557", "lt2": "F1FAEE",
             "accent1": "E63946", "accent2": "F4A261", "accent3": "2A9D8F", "accent4": "E9C46A",
             "accent5": "8E44AD", "accent6": "264653", "hlink": "00B4D8", "folHlink": "B5838D"}


def apply_theme(src: Path, dst: Path, colors: dict, name: str) -> Path:
    """Copy a pptx, replacing the colour scheme of its theme(s)."""
    scheme = '<a:clrScheme name="%s">%s</a:clrScheme>' % (
        name, "".join('<a:%s><a:srgbClr val="%s"/></a:%s>' % (s, colors[s], s) for s in SLOTS))
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if re.match(r"ppt/theme/theme\d+\.xml$", item.filename):
                data = re.sub(rb"<a:clrScheme\b.*?</a:clrScheme>", scheme.encode(), data, flags=re.S)
            zo.writestr(item, data)
    return dst


def lint(path):
    p = subprocess.run([sys.executable, str(SCRIPTS / "lint_deck.py"), str(path), "--contrast", "--json"],
                       capture_output=True, encoding="utf-8")
    return p.returncode, json.loads(p.stdout)


def contrast_errors(report):
    return [e for e in report["errors"] if e["message"].startswith("text hard to read")]


# ------------------------------------------------------------------ colour maths
def test_wcag_reference_values():
    assert round(ratio(hex_to_rgb("000000"), hex_to_rgb("FFFFFF")), 2) == 21.0
    assert round(ratio(hex_to_rgb("767676"), hex_to_rgb("FFFFFF")), 2) == 4.54  # the classic AA grey
    assert ratio(hex_to_rgb("777777"), hex_to_rgb("FFFFFF")) < 4.5


def test_modifiers_match_the_tokens():
    """lumMod/lumOff on tx1 give the 'muted' grey that tokens.json declares."""
    from lxml import etree

    el = etree.fromstring('<a:schemeClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="tx1">'
                          '<a:lumMod val="50000"/><a:lumOff val="40000"/></a:schemeClr>')
    rgb, alpha = apply_mods(hex_to_rgb("111111"), el)
    assert rgb_to_hex(rgb) == "6E6E6E" and alpha == 1.0
    el = etree.fromstring('<a:srgbClr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="000000">'
                          '<a:tint val="50000"/><a:alpha val="40000"/></a:srgbClr>')
    rgb, alpha = apply_mods(hex_to_rgb("000000"), el)
    assert rgb_to_hex(rgb) == "BCBCBC" and alpha == 0.4  # tint works in linear light, as in Office


# ------------------------------------------------------------------ the contract file
def test_contract_covers_every_slot_and_font():
    assert set(CONTRACT["slots"]) == set(SLOTS)
    assert set(CONTRACT["fonts"]) == {"major", "minor"}
    for slot, info in CONTRACT["slots"].items():
        assert info["role"] and re.fullmatch(r"[0-9A-F]{6}", info["neutral"])
    used = [s for s, info in CONTRACT["slots"].items() if info["uses"]["entries"]]
    assert set(used) == set(SLOTS) - {"hlink", "folHlink"}
    kinds = {p["kind"] for p in CONTRACT["pairs"]}
    assert kinds == {"text", "graphic", "link"}
    assert all(p["min_ratio"] in (3.0, 4.5) for p in CONTRACT["pairs"])


def test_neutral_libraries_meet_the_contract():
    """The neutral theme passes every pair, and the libraries pass the per-run check."""
    for p in CONTRACT["pairs"]:
        assert p["neutral_ratio"] >= p["min_ratio"], p
    for lib in ("layouts", "visuals"):
        code, rep = lint(ASSETS / f"{lib}.pptx")
        assert not contrast_errors(rep), contrast_errors(rep)[:3]
        assert rep["contrast"]["checked_runs"] > 500 and not rep["contrast"]["theme_findings"]


# ------------------------------------------------------------------ themes applied to the libraries
@pytest.mark.parametrize("colors,name", [(BRAND_RAMP, "Brand ramp"), (DARK, "Dark")])
def test_themes_that_follow_the_contract_pass(tmp_path, colors, name):
    theme = {"colors": colors, "fonts": {}}
    assert theme_findings(theme, CONTRACT) == []
    for lib in ("layouts", "visuals"):
        deck = apply_theme(ASSETS / f"{lib}.pptx", tmp_path / f"{lib}.pptx", colors, name)
        code, rep = lint(deck)
        assert rep["contrast"]["theme"] and rep["contrast"]["colors"]["accent1"] == colors["accent1"]
        assert not contrast_errors(rep), contrast_errors(rep)[:3]
        assert not rep["contrast"]["theme_findings"]


def test_saturated_brand_theme_is_caught(tmp_path):
    findings = [f["message"] for f in theme_findings({"colors": SATURATED, "fonts": {}}, CONTRACT)]
    assert any("not a ramp" in m for m in findings)                 # rainbow instead of a ramp
    assert any(m.startswith("paper text on a2 fills") for m in findings)   # white on orange
    assert any(m.startswith("ink text on a6 fills") for m in findings)     # black on dark teal
    failing = {}
    for lib in ("layouts", "visuals"):
        deck = apply_theme(ASSETS / f"{lib}.pptx", tmp_path / f"{lib}.pptx", SATURATED, "Saturated")
        code, rep = lint(deck)
        assert code == 1
        for e in contrast_errors(rep):
            m = re.search(r"is (\S+) \(#\w+\) on (\S+) \(", e["message"])
            failing[(m.group(1), m.group(2))] = failing.get((m.group(1), m.group(2)), 0) + 1
    # what the contract predicts is what the decks show: white text on the orange accent2,
    # black text on the purple and dark-teal accent5 and accent6
    assert {("paper", "a2"), ("ink", "a5"), ("ink", "a6")} <= set(failing), failing
    print("\nsaturated theme, shapes too faint per pair:", dict(sorted(failing.items())))


def test_lint_default_is_unchanged(tmp_path):
    """Without --contrast, a theme that breaks contrast changes nothing in the report."""
    deck = apply_theme(ASSETS / "layouts.pptx", tmp_path / "layouts.pptx", SATURATED, "Saturated")
    p = subprocess.run([sys.executable, str(SCRIPTS / "lint_deck.py"), str(deck), "--json"],
                       capture_output=True, encoding="utf-8")
    rep = json.loads(p.stdout)
    assert p.returncode == 0 and "contrast" not in rep and not rep["errors"]


def test_read_theme_of_the_libraries():
    with zipfile.ZipFile(ASSETS / "layouts.pptx") as z:
        theme = read_theme(z.read("ppt/theme/theme1.xml"))
    assert theme["colors"] == {s: CONTRACT["slots"][s]["neutral"] for s in SLOTS}
    assert theme["fonts"] == {k: CONTRACT["fonts"][k]["neutral"] for k in ("major", "minor")}
