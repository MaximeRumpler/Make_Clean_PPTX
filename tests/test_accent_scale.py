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


def runs_of(deck, name_part):
    """[(size, colour)] of every run in shapes whose name contains name_part, groups included."""
    from lxml import etree
    from pptx import Presentation
    from _common import iter_shapes
    out = []
    for s in Presentation(str(deck)).slides:
        for sh in iter_shapes(s):
            if name_part.lower() in sh.name.lower():
                out += re.findall(r'<a:rPr[^>]*sz="(\d+)"[^>]*>\s*<a:solidFill><a:schemeClr val="(\w+)"',
                                  etree.tostring(sh._element).decode())
    return out


def test_emphasis_colours_key_numbers_only(tmp_path):
    from pptx import Presentation
    slides = [{"id": "V-KPI-01", "source": "shapes"}]
    code, rep, plain = build(tmp_path, {}, slides)
    assert code == 0, rep
    base = runs_of(plain, "value")
    assert base and all(v == "tx1" for _, v in base)
    code, rep, deck = build(tmp_path, {"emphasis": "accent3"}, slides)
    assert code == 0, rep
    big = [v for sz, v in runs_of(deck, "value") if int(sz) >= 2800]
    assert big and set(big) == {"accent3"}
    small = [v for sz, v in runs_of(deck, "value") if int(sz) < 2800]
    assert all(v == "tx1" for v in small)
    assert Presentation(str(deck)).slides  # opens


def test_emphasis_is_checked_against_the_theme_and_validated(tmp_path):
    make_thmx(tmp_path / "brand.thmx", BRAND_RAMP)
    slides = [{"id": "V-KPI-01", "source": "shapes"}]
    code, rep, _ = build(tmp_path, {"theme": "brand.thmx", "emphasis": "accent6"}, slides)
    assert code == 0 and any("emphasis accent6" in w for w in rep["warnings"])
    code, rep, _ = build(tmp_path, {"theme": "brand.thmx", "emphasis": "accent3"}, slides)
    assert code == 0 and not any("emphasis" in w for w in rep["warnings"])
    code, rep, _ = build(tmp_path, {"emphasis": "red"}, slides)
    assert code == 2
