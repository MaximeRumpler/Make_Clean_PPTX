#!/usr/bin/env python3
"""Write skills/make-clean-pptx/assets/theme-contract.json from the built libraries.

    python library/tools/build_contract.py [--style NAME|FILE.json] [--pack-dir DIR]

The contract tells a theme author (a person, or the Make_Colors skill) what
each theme slot does in the libraries and which colour pairs must stay
readable. Nothing in it is typed by hand except the slot roles below: the
usage counts and the text/fill pairs are measured on assets/layouts.pptx and
assets/visuals.pptx with the same code as `lint_deck.py --contrast`, so the
contract follows the libraries. CI rebuilds it and fails if it changed.
Explained for people in references/theme-contract.md.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT.parent / "skills" / "make-clean-pptx"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _style  # noqa: E402

ASSETS = _style.from_argv(sys.argv)["pack"]

from _common import TOKENS  # noqa: E402
from _contrast import DEFAULT_CLRMAP, LARGE_MIN, SLOTS, TEXT_MIN, Palette, ratio, read_theme  # noqa: E402

TOKENS_JSON = json.loads((ROOT / "theme" / "tokens.json").read_text(encoding="utf-8"))

ROLES = {
    "dk1": "Main text colour (token ink: titles, key numbers) and, lightened, captions and labels (token muted). "
           "Also the fill of the few panels drawn in ink.",
    "lt1": "Slide background (token paper), text on dark fills, and, darkened, rules and borders (token line).",
    "dk2": "Body text (token ink2).",
    "lt2": "Cards, panels and frames (token surface). Carries ink, ink2 and muted text.",
    "accent1": "Strongest emphasis: main data series, dark panels and dark slide backgrounds. Carries paper text.",
    "accent2": "Second step of the ramp: second series, dark secondary panels. Carries paper text.",
    "accent3": "Middle of the ramp: third series, comparison. Carries ink text; "
               "used as a muted text colour on dark slides.",
    "accent4": "Fourth step: reference series, light fills. Carries ink text; used as a kicker colour on dark slides.",
    "accent5": "Fifth step: light fills and levels. Carries ink text; used as a subtitle colour on dark slides.",
    "accent6": "Faintest fill (backgrounds of quadrants, placeholders, logo slot). Carries ink text; "
               "used as caption colour on dark fills.",
    "hlink": "Hyperlinks. The libraries draw none; it matters for links people add in PowerPoint.",
    "folHlink": "Visited hyperlinks. Not used by the libraries.",
}
FONT_ROLES = {
    "major": "Headings: titles, headlines, big numbers (theme font +mj).",
    "minor": "Everything else: body, captions, labels, table and chart text (theme font +mn).",
}
# Non-text pairs. Graphics that carry meaning on their own (lines, markers, single-series charts,
# arrows) are drawn with accent1 to accent3; lighter accents are fills that always carry a label.
GRAPHIC_PAIRS = [("a1", "paper"), ("a2", "paper"), ("a3", "paper")]
LINK_PAIRS = [("hlink", "paper"), ("hlink", "surface")]

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def token_slot(name: str) -> str:
    return DEFAULT_CLRMAP.get(TOKENS[name][0], TOKENS[name][0])


def usage() -> tuple:
    """Per slot: how often it is used as text, fill, line and chart colour, and in how many library entries."""
    from lxml import etree

    counts = {s: defaultdict(int) for s in SLOTS}
    entries = {s: set() for s in SLOTS}
    fonts = {k: defaultdict(int) for k in ("major", "minor")}
    font_entries = {k: set() for k in ("major", "minor")}
    for lib in ("layouts", "visuals"):
        with zipfile.ZipFile(ASSETS / f"{lib}.pptx") as z:
            slide_of_chart = {}
            for name in z.namelist():
                m = re.match(r"ppt/slides/_rels/slide(\d+)\.xml\.rels$", name)
                if m:
                    for target in re.findall(rb'Target="[./]*(?:ppt/)?charts/(chart\d+)\.xml"', z.read(name)):
                        slide_of_chart[target.decode()] = int(m.group(1))
            for name in sorted(z.namelist()):
                m = re.match(r"ppt/(slides/slide|charts/chart)(\d+)\.xml$", name)
                if not m:
                    continue
                chart = m.group(1).startswith("charts")
                entry = "%s:%d" % (lib, slide_of_chart.get("chart" + m.group(2), 0) if chart else int(m.group(2)))
                root = etree.fromstring(z.read(name))
                for el in root.iter(A + "schemeClr"):
                    slot = DEFAULT_CLRMAP.get(el.get("val"), el.get("val"))
                    if slot not in counts:
                        continue
                    tags = []
                    p = el.getparent()
                    while p is not None:
                        tags.append(etree.QName(p).localname)
                        p = p.getparent()
                    if "endParaRPr" in tags:
                        continue  # formatting of an empty end of paragraph, never visible
                    if any(t in ("rPr", "defRPr") for t in tags):
                        kind = "text"
                    elif any(t in ("ln", "lnL", "lnR", "lnT", "lnB") for t in tags):
                        kind = "line"
                    elif chart and ("ser" in tags or "dPt" in tags):
                        kind = "chart_series"
                    else:
                        kind = "fill"
                    counts[slot][kind] += 1
                    entries[slot].add(entry)
                for el in root.iter(A + "latin"):
                    face = el.get("typeface", "")
                    key = "major" if face.startswith("+mj") else "minor" if face.startswith("+mn") else None
                    if key and etree.QName(el.getparent()).localname in ("rPr", "defRPr"):
                        fonts[key]["runs"] += 1
                        font_entries[key].add(entry)
    out = {}
    for s in SLOTS:
        c = {k: counts[s].get(k, 0) for k in ("text", "fill", "line", "chart_series")}
        c["entries"] = len(entries[s])
        out[s] = c
    fout = {k: {"runs": fonts[k].get("runs", 0), "entries": len(font_entries[k])} for k in fonts}
    return out, fout


def pairs(neutral: Palette) -> tuple:
    from _contrast import check_deck

    seen = {}
    composite = 0
    for lib in ("layouts", "visuals"):
        rep = check_deck(Presentation(ASSETS / f"{lib}.pptx"))
        for r in rep["results"]:
            fg, bg = r["fg_label"], r["bg_label"]
            if fg not in TOKENS or bg not in TOKENS:
                composite += 1  # semi-transparent fills stacked on each other: checked per deck only
                continue
            p = seen.setdefault((fg, bg), {"text": fg, "on": bg, "kind": "text", "runs": 0, "smallest_pt": 999.0,
                                           "min_ratio": LARGE_MIN})
            p["runs"] += 1
            p["smallest_pt"] = min(p["smallest_pt"], r["pt"])
            p["min_ratio"] = max(p["min_ratio"], r["need"])
    out = []
    for p in seen.values():
        p["slots"] = [token_slot(p["text"]), token_slot(p["on"])]
        p["neutral_ratio"] = round(ratio(neutral.token(p["text"]), neutral.token(p["on"])), 2)
        out.append(p)
    for fg, bg in GRAPHIC_PAIRS:
        out.append({"text": fg, "on": bg, "kind": "graphic", "runs": 0, "smallest_pt": None, "min_ratio": LARGE_MIN,
                    "slots": [token_slot(fg), token_slot(bg)],
                    "neutral_ratio": round(ratio(neutral.token(fg), neutral.token(bg)), 2)})
    out.sort(key=lambda p: (p["kind"] != "text", -p["runs"], p["text"], p["on"]))
    return out, composite


def link_pairs(theme: dict) -> list:
    pal = Palette(theme)
    out = []
    for fg, bg in LINK_PAIRS:
        rgb = pal.base(_scheme(fg))
        out.append({"text": fg, "on": bg, "kind": "link", "runs": 0, "smallest_pt": None, "min_ratio": TEXT_MIN,
                    "slots": [fg, token_slot(bg)], "neutral_ratio": round(ratio(rgb, pal.token(bg)), 2)})
    return out


def _scheme(val):
    from lxml import etree

    return etree.Element(A + "schemeClr", val=val)


def main() -> int:
    with zipfile.ZipFile(ASSETS / "layouts.pptx") as z:
        theme = read_theme(z.read("ppt/theme/theme1.xml"))
    neutral = Palette(theme)
    slot_use, font_use = usage()
    pair_list, composite = pairs(neutral)
    tokens = {}
    for name, (scheme, mod, off, dark) in TOKENS.items():
        tokens[name] = {"slot": token_slot(name), "scheme": scheme, "lumMod": mod, "lumOff": off,
                        "text_on_it": "paper" if dark else "ink",
                        "use": TOKENS_JSON["colors"][name]["use"]}
    contract = {
        "_comment": "Generated by library/tools/build_contract.py from the libraries; do not edit. "
                    "Explained in references/theme-contract.md.",
        "version": 1,
        "thresholds": {
            "text": TEXT_MIN, "large_text": LARGE_MIN, "graphics": LARGE_MIN,
            "large_text_rule": "18 pt and above, or 14 pt bold and above (WCAG 2.x, SC 1.4.3 and 1.4.11)",
        },
        "slots": {s: {"role": ROLES[s], "neutral": theme["colors"][s], "uses": slot_use[s]} for s in SLOTS},
        "fonts": {k: {"role": FONT_ROLES[k], "neutral": theme["fonts"][k], "uses": font_use[k]}
                  for k in ("major", "minor")},
        "tokens": tokens,
        "ramp": {
            "order": ["accent1", "accent2", "accent3", "accent4", "accent5", "accent6"],
            "rule": "accent1 is the closest to the text colour (dk1) and accent6 the closest to the background (lt1): "
                    "luminance strictly increases from accent1 to accent6 on a light theme and strictly decreases "
                    "on a dark one. dk1 and dk2 sit on the text side, lt1 and lt2 on the background side.",
            "min_step": 1.1,
            "why": "Charts, scales and levels read the accents as a sequence, and the text colour on each fill is "
                   "fixed (paper on accent1 and accent2, ink on accent3 to accent6).",
        },
        "pairs": pair_list + link_pairs(theme),
        "not_listed": {
            "semi_transparent_runs": composite,
            "note": "Text over semi-transparent stacked fills (Venn-type visuals) depends on the overlap; "
                    "lint_deck.py --contrast checks it on the actual deck.",
        },
    }
    out = ASSETS / "theme-contract.json"
    out.write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(out.relative_to(ROOT.parent)), "pairs": len(contract["pairs"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
