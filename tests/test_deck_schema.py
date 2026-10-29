"""assets/deck.schema.json: example specs validate, and the schema follows build_deck.py."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "make-clean-pptx"
sys.path.insert(0, str(SKILL / "scripts"))

import build_deck  # noqa: E402
from _common import TOKEN_ALIASES, TOKENS  # noqa: E402
from validate_spec import SCHEMA_PATH, load_schema, validate  # noqa: E402

SCHEMA = load_schema()
DEFS = SCHEMA["$defs"]


def _json_blocks(md: Path) -> list:
    """Code blocks of a Markdown page that are complete JSON (the ones with '…' are sketches)."""
    out = []
    for block in re.findall(r"```json\n(.*?)```", md.read_text(encoding="utf-8"), re.S):
        try:
            out.append(json.loads(block))
        except ValueError:
            pass
    return out


def _example_specs():
    specs = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "examples").glob("*.json")}
    for md in [ROOT / "docs" / "how-it-works.md", ROOT / "README.md", SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
        for i, block in enumerate(_json_blocks(md)):
            if isinstance(block, dict) and isinstance(block.get("slides"), list):  # not the build report
                specs[f"{md.name}#{i}"] = block
            elif isinstance(block, dict) and "fill" in block and ("id" in block or "slide" in block):
                specs[f"{md.name}#{i}"] = {"slides": [block]}  # a single slide shown on its own
    return specs


EXAMPLES = _example_specs()


def test_examples_found():
    assert "home-energy.json" in EXAMPLES and len(EXAMPLES) >= 3


@pytest.mark.parametrize("name", sorted(EXAMPLES))
def test_example_specs_validate(name):
    assert validate(EXAMPLES[name]) == []


def test_every_value_type_validates():
    spec = {
        "output": "build/deck.pptx", "language": "en-GB", "theme": "brand.thmx",
        "theme_fonts_fallback": {"major": "Georgia", "minor": "Arial"}, "logo": "logo.svg", "logo_alt": "Brand",
        "skeleton": False, "properties": {"title": "T", "author": "A", "subject": "S", "keywords": "K"},
        "slides": [
            {"source": "design", "slide": 2, "notes": "n", "keep_unfilled": True, "hidden": False, "fill": {
                "Title": "A **bold** word", "Number": 42, "Gone": None, "Empty": "",
                "Body": ["One", 2, {"text": "Sub", "level": 1}],
                "Photo": {"path": "img.jpg", "alt": "a", "credit": "c", "fit": "contain"},
                "Icon": {"icon": "lucide:rocket", "color": "a1", "mode": "grey", "weight": 0.75, "alt": "x"},
                "Drawing": {"svg": "d.SVG", "mode": "keep"},
                "Chart": {"categories": ["Q1", "Q2"], "series": {"2026": [4, None]}},
                "Waterfall": {"categories": ["a", "b", "c"], "waterfall": [100, -20, 80], "totals": [0, 2]},
                "Gantt": {"categories": ["t"], "gantt": [[0, 3]]},
                "Dot": {"text": "42", "fill": "accent1", "color": "white", "at": [30, 70]},
                "Table": [["h1", "h2"], ["a", None]],
                "Logo": None}},
            {"id": "L-32", "insert": [{"id": "V-COM-01", "component": "V-COM-01", "into": "Content Area"},
                                      {"source": "visuals", "slide": 3, "component": "x", "box": [5, 10, 40, 50],
                                       "fit": "stretch", "keep_unfilled": True, "fill": {"Label": "y"}}]},
        ],
    }
    assert validate(spec) == []


@pytest.mark.parametrize("spec, path, words", [
    ({}, "(root)", "missing required key 'slides'"),
    ({"slides": []}, "slides", "at least 1"),
    ({"slides": [{"fill": {}}]}, "slides[0]", "needs one of the keys id, slide"),
    ({"slides": [{"id": "L-01", "fil": {}}]}, "slides[0].fil", "unknown key 'fil'"),
    ({"slides": [{"id": "L-01"}], "them": "x"}, "them", "unknown key"),
    ({"slides": [{"slide": 0}]}, "slides[0].slide", "at least 1"),
    ({"slides": [{"id": "L-01", "fill": {"Icon": {"icon": "lucide:x", "colour": "a1"}}}]},
     "slides[0].fill.Icon.colour", "unknown key 'colour'"),
    ({"slides": [{"id": "L-01", "fill": {"Dot": {"fill": "blue"}}}]}, "slides[0].fill.Dot.fill", "not one of"),
    ({"slides": [{"id": "L-01", "fill": {"Photo": {"path": "a.jpg", "fit": "fill"}}}]},
     "slides[0].fill.Photo.fit", "not one of"),
    ({"slides": [{"id": "L-01", "insert": [{"id": "V-COM-01"}]}]}, "slides[0].insert[0]", "component"),
    ({"slides": [{"id": "L-01"}], "logo": "logo.gif"}, "logo", "does not match"),
    ({"slides": [{"id": "L-01", "fill": {"T": True}}]}, "slides[0].fill.T", "does not match any accepted form"),
])
def test_invalid_specs_are_reported(spec, path, words):
    errors = validate(spec)
    assert any(e["path"] == path and words in e["message"] for e in errors), errors


# ------------------------------------------------------------- engine sync
def test_keys_match_the_engine():
    """build_deck.py warns about keys outside these sets; the schema must name the same ones."""
    assert set(SCHEMA["properties"]) == build_deck.SPEC_KEYS
    assert set(DEFS["slide"]["properties"]) == build_deck.SLIDE_KEYS
    assert set(DEFS["insert"]["properties"]) == build_deck.INSERT_KEYS
    sources = set(DEFS["source"]["enum"])
    assert sources == {"layouts", "visuals"} | set(build_deck.SOURCE_ALIASES)
    assert set(build_deck.SOURCE_ALIASES.values()) <= sources


def test_colours_match_the_engine():
    assert set(DEFS["colour"]["enum"]) == set(TOKENS) | set(TOKEN_ALIASES)


def test_logo_pattern_matches_the_engine():
    pattern = SCHEMA["properties"]["logo"]["pattern"]
    for ext in build_deck.LOGO_EXT | {e.upper() for e in build_deck.LOGO_EXT}:
        assert re.search(pattern, "logo" + ext)
    assert not re.search(pattern, "logo.gif")


def test_examples_build(tmp_path):
    """The schema is not stricter than the engine on the shipped example: it builds without warnings."""
    spec = dict(EXAMPLES["home-energy.json"], output=str(tmp_path / "deck.pptx"))
    path = tmp_path / "deck.json"
    path.write_text(json.dumps(spec), encoding="utf-8")
    p = subprocess.run([sys.executable, str(SKILL / "scripts" / "build_deck.py"), "--spec", str(path), "--offline"],
                       capture_output=True, encoding="utf-8")
    assert p.returncode == 0, p.stdout + p.stderr
    assert json.loads(p.stdout)["warnings"] == []


def test_cli(tmp_path):
    good, bad, broken = tmp_path / "good.json", tmp_path / "bad.json", tmp_path / "broken.json"
    good.write_text(json.dumps({"slides": [{"id": "L-01"}]}))
    bad.write_text(json.dumps({"slides": [{"id": "L-01", "fil": {}}]}))
    broken.write_text("{not json")
    script = SKILL / "scripts" / "validate_spec.py"
    results = [subprocess.run([sys.executable, str(script), str(f)], capture_output=True, encoding="utf-8")
               for f in (good, bad, broken)]
    assert [r.returncode for r in results] == [0, 1, 2]
    assert json.loads(results[0].stdout) == {"valid": True, "errors": []}
    assert json.loads(results[1].stdout)["errors"][0]["path"] == "slides[0].fil"
    assert "error" in json.loads(results[2].stdout)


def test_schema_lives_in_the_skill():
    assert SKILL.resolve() in SCHEMA_PATH.resolve().parents
    assert SCHEMA["$schema"].endswith("2020-12/schema")
