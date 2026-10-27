"""Style contract: role tags on every container, style tokens, and packs built from other tokens.

The companion restyler (Make_Style) relies on this: see
skills/make-clean-pptx/references/style-contract.md.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
from pptx import Presentation

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "make-clean-pptx"
ASSETS = SKILL / "assets"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "library" / "tools"))

import _style  # noqa: E402
from _common import iter_shapes, shape_kind  # noqa: E402
from read_index import load_index, parse_fields  # noqa: E402

ROLES = {"card", "callout", "keyfigure", "label", "panel", "frame", "decoration"}
ROLE_NAME = re.compile(r"^(card|callout|keyfigure|label|panel|frame|decoration)#\d+(?: > (.+))?$")
CONTAINER_TYPES = {"frame", "plot", "deco"}
NOT_FIELDS = {"Catalogue label"}  # caption of the visuals catalogue, outside the component
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def _units(lib, pack=ASSETS):
    """(entry, {shape name: shape}) for every layout slide or visual component."""
    prs = Presentation(pack / f"{lib}.pptx")
    for e in load_index(pack / f"{lib}.csv"):
        slide = prs.slides[e["slide"] - 1]
        if lib == "visuals":
            group = next(s for s in slide.shapes if s.name == e["id"])
            shapes = list(iter_shapes(group))
        else:
            shapes = [s for s in iter_shapes(slide) if not s.is_placeholder]
        yield e, shapes


def _drawn(shape) -> bool:
    """True when the shape paints a fill or an outline of its own."""
    sp_pr = shape._element.find("{http://schemas.openxmlformats.org/presentationml/2006/main}spPr")
    if sp_pr is None:
        return False
    if sp_pr.find(A + "solidFill") is not None:
        return True
    ln = sp_pr.find(A + "ln")
    return ln is not None and ln.find(A + "noFill") is None and len(ln)


@pytest.mark.parametrize("lib", ["layouts", "visuals"])
def test_every_container_has_a_role(lib):
    for e, shapes in _units(lib):
        fields = {f["name"]: f for f in e["field_list"]}
        for shp in shapes:
            if shape_kind(shp) == "group" or shp.name in NOT_FIELDS:
                continue
            f = fields.get(shp.name)
            if f is None:
                m = ROLE_NAME.match(shp.name)
                assert m, f"{e['id']}: shape '{shp.name}' is neither a field nor role-tagged"
                if m.group(2):
                    assert m.group(2) in fields, f"{e['id']}: '{shp.name}' holds an unknown field"
                continue
            if f["type"] in CONTAINER_TYPES or (f["type"] in ("text", "bullets") and _drawn(shp)):
                assert f.get("role") in ROLES, f"{e['id']}: container field '{f['name']}' has no role flag"


def test_role_flag_round_trips_through_the_index():
    f = parse_fields("Item 1|text|3|optional,role=label; Title|text|60")
    assert f[0]["role"] == "label" and "role" not in f[1]


def test_named_containers_have_their_roles():
    """A few anchors that the restyler expects: cards, key figures, frames, panels."""
    names = {e["id"]: [s.name for s in shapes] for e, shapes in _units("layouts")}
    every = [n for ns in names.values() for n in ns]
    assert "card#1 > Heading 1" in names["L-22"]
    assert any(n.startswith("keyfigure#") for n in every)
    assert any(n.startswith("panel#") for n in every)
    frames = [f for e in load_index(ASSETS / "layouts.csv") for f in e["field_list"] if f["type"] == "frame"]
    assert frames and all(f["role"] == "frame" for f in frames)


# --------------------------------------------------------------------- tokens
def test_default_tokens_are_the_bundled_look():
    t = _style.load("default")
    assert t["pack"] == _style.BUNDLED or "MAKE_CLEAN_PACK_DIR" in __import__("os").environ
    tok = t["tokens"]
    assert tok["radius"] == 0 and tok["cards"] == "fill" and tok["background"] == "paper"
    assert tok["title_case"] == "as-written" and tok["numbering"] == "as-designed"
    assert tok["char_em"] == {"heading": 0.52, "body": 0.52}
    theme = (ASSETS / "theme-contract.json").read_text(encoding="utf-8")
    assert json.loads(theme)["fonts"]["major"]["neutral"] == tok["fonts"]["heading"]


def test_every_named_style_is_valid():
    data = json.loads(_style.TOKENS_FILE.read_text(encoding="utf-8"))
    assert data["styles"], "at least one alternative style, built in CI"
    for name in data["styles"]:
        s = _style.load(name)
        assert s["name"] == name and s["raw"] != _style.load("default")["raw"]


@pytest.mark.parametrize("bad", [{"cards": "shadow"}, {"radius": 2}, {"colour": "red"}, {"char_em": {"body": 2}}])
def test_bad_tokens_are_refused(tmp_path, bad):
    f = tmp_path / "bad.json"
    f.write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError):
        _style.load(str(f))


# ---------------------------------------------------------------------- packs
def _packs():
    base = ROOT / "library" / "out" / "styles"
    return sorted(p / "pack" for p in base.iterdir() if (p / "pack" / "layouts.csv").is_file()) if base.is_dir() else []


@pytest.mark.parametrize("pack", _packs() or [None], ids=lambda p: p.parent.name if p else "none")
def test_pack_keeps_ids_and_field_names(pack):
    """Built with library/tools/build_pack.py (CI builds one); skipped when no pack was built."""
    if pack is None:
        pytest.skip("no style pack built (python library/tools/build_pack.py <style>)")
    for lib in ("layouts", "visuals"):
        ref = {e["id"]: [f["name"] for f in e["field_list"]] for e in load_index(ASSETS / f"{lib}.csv")}
        got = {e["id"]: [f["name"] for f in e["field_list"]] for e in load_index(pack / f"{lib}.csv")}
        assert got == ref, f"{pack}: {lib} ids or field names differ from the bundled library"
    for lib in ("layouts", "visuals"):
        for e, shapes in _units(lib, pack):
            names = {s.name for s in shapes}
            assert all(f["name"] in names for f in e["field_list"]), f"{pack}: {e['id']} lost a field"
    assert json.loads((pack / "style.json").read_text(encoding="utf-8"))["name"] == pack.parent.name


@pytest.mark.parametrize("lib,minimum", [("layouts", 20), ("visuals", 8)])
def test_arrangement_flags_match_the_fields(lib, minimum):
    """`arrange` = kind:count[:ordered]; the count is the number of numbered units in `fields`."""
    flagged = 0
    for e in load_index(ASSETS / f"{lib}.csv"):
        value = e.get("arrange") or ""
        if not value:
            continue
        flagged += 1
        kind, n, *rest = value.split(":")
        assert kind in ("row", "column", "grid") and rest in ([], ["ordered"]), f"{e['id']}: {value}"
        numbers = {int(m.group(1)) for f in e["field_list"] for m in [re.search(r"\b(\d+)\b", f["name"])] if m}
        assert set(range(1, int(n) + 1)) <= numbers, f"{e['id']}: {value} but fields {sorted(numbers)}"
        if lib == "visuals":
            assert e["kind"] in ("diagram", "timeline"), f"{e['id']}: a {e['kind']} keeps its geometry"
    assert flagged >= minimum


def test_arrange_column_is_searchable(tmp_path):
    """Third-party indexes may carry the column too; read_index keeps it like any extra column."""
    csv_path = tmp_path / "own.csv"
    csv_path.write_text("slide;id;name;category;arrange;fields\n1;X-1;Cards;Text;grid:4;Title|text|60\n"
                        "2;X-2;Quote;Text;;Quote|text|90\n", encoding="utf-8")
    rows = load_index(csv_path)
    assert rows[0]["arrange"] == "grid:4" and not rows[1].get("arrange")
