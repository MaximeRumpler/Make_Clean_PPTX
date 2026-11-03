"""deck.json "accent_scale": "tints" draws the "sequential" visuals with tints of accent1."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "make-clean-pptx" / "scripts"
ASSETS = ROOT / "skills" / "make-clean-pptx" / "assets"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(ROOT / "tests"))

from _contrast import tint_steps  # noqa: E402
from read_index import load_index  # noqa: E402
from test_theme_contract import BRAND_RAMP  # noqa: E402
from test_theme_key import make_thmx  # noqa: E402


def build(tmp_path, extra, slides):
    spec = dict({"output": str(tmp_path / "d.pptx"), "slides": slides}, **extra)
    path = tmp_path / "deck.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    p = subprocess.run([sys.executable, str(SCRIPTS / "build_deck.py"), "--spec", str(path),
                        "--layouts", str(ASSETS / "layouts.pptx"), "--layouts-index", str(ASSETS / "layouts.csv"),
                        "--visuals", str(ASSETS / "visuals.pptx"), "--visuals-index", str(ASSETS / "visuals.csv")],
                       capture_output=True, encoding="utf-8", cwd=str(tmp_path))
    return p.returncode, json.loads(p.stdout), tmp_path / "d.pptx"


def slide_xml(deck, n=1):
    from lxml import etree
    from pptx import Presentation
    return etree.tostring(Presentation(str(deck)).slides[n - 1]._element).decode()


def fills(xml):
    return re.findall(r'<a:solidFill><a:schemeClr val="(accent\d)"(?:/>|>(.*?)</a:schemeClr>)', xml)


def test_sequential_tag_is_in_the_index():
    tagged = {e["id"] for e in load_index(ASSETS / "visuals.csv") if "sequential" in e["tags"].split()}
    assert {"V-REL-04", "V-COM-05", "V-STR-03", "V-STR-08", "V-STR-09", "V-PRO-07"} <= tagged


def test_tint_steps_match_the_lightness_of_each_accent():
    steps = tint_steps(BRAND_RAMP)
    assert set(steps) == {"accent2", "accent3", "accent4", "accent5", "accent6"}
    mods = [steps["accent%d" % k][0] for k in range(2, 7)]
    assert mods == sorted(mods, reverse=True)  # lighter and lighter


def test_tints_replace_accents_on_a_sequential_visual_only(tmp_path):
    theme = make_thmx(tmp_path / "brand.thmx", BRAND_RAMP)
    slides = [{"id": "V-STR-03", "source": "shapes"}, {"id": "V-CMP-01", "source": "shapes"}]
    code, rep, deck = build(tmp_path, {"theme": "brand.thmx", "accent_scale": "tints"}, slides)
    assert code == 0, rep
    pyramid = fills(slide_xml(deck, 1))
    assert any(v == "accent1" and "lumMod" in mods for v, mods in pyramid)
    assert not any(v in ("accent2", "accent3", "accent5") for v, _ in pyramid)
    code, rep, plain = build(tmp_path, {"theme": "brand.thmx"}, slides)
    assert code == 0 and "lumMod" not in "".join(m for _, m in fills(slide_xml(plain, 1)))
    assert theme.is_file()


def test_accent_scale_needs_a_theme_and_a_known_value(tmp_path):
    code, rep, deck = build(tmp_path, {"accent_scale": "tints"}, [{"id": "V-STR-03", "source": "shapes"}])
    assert code == 0 and any("accent_scale" in w for w in rep["warnings"])
    assert "lumMod" not in "".join(m for _, m in fills(slide_xml(deck, 1)))
    code, rep, _ = build(tmp_path, {"accent_scale": "rainbow"}, [{"id": "V-STR-03", "source": "shapes"}])
    assert code == 2
