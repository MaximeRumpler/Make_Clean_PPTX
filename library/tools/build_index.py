#!/usr/bin/env python3
"""Write the CSV indexes of the libraries from the generator registries.

    python library/tools/build_index.py [--style NAME|FILE.json] [--pack-dir DIR]

Reads library/out/<lib>.registry.json (written by build.js) and writes
skills/make-clean-pptx/assets/<lib>.csv (or the pack folder of another style). Semicolon-separated, UTF-8, one row
per slide (layouts) or per component (visuals). The column contract is in
skills/make-clean-pptx/references/index-schema.md.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _style  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STYLE = _style.from_argv(sys.argv)
RAW = STYLE["raw"]
ASSETS = STYLE["pack"]

COLUMNS = {
    "layouts": ["id", "slide", "name", "category", "style", "density", "description", "use_when", "tags", "arrange", "fields"],
    "visuals": ["id", "slide", "name", "category", "kind", "frame", "objective", "data_type", "dimensions", "complexity",
                "description", "use_when", "limits", "fill_notes", "tags", "related", "arrange", "fields"],
}


def field_spec(f: dict) -> str:
    parts = [f["name"], f["type"]]
    if f["type"] in ("text", "bullets"):
        parts.append(str(f["limit"]))
    else:
        parts.append(f.get("hint") or "")
    flags = [k for k in ("optional", "default") if f.get(k)]
    if f.get("follows"):
        flags.append(f"follows={f['follows']}")
    if f.get("role"):
        flags.append(f"role={f['role']}")
    if flags:
        parts.append(",".join(flags))
    return "|".join(parts).rstrip("|")


NUMBERED = re.compile(r"^(.*?)\b(\d+)\b(.*)$")
ORDERED_WORDS = re.compile(r"\b(step|stage|act|date|milestone|phase|chapter|session|number)\b", re.I)
ORDERED_TAGS = {"timeline", "process", "steps", "sequence", "roadmap", "agenda", "numbered", "chronology"}


# Visuals whose geometry encodes data, axes or a metaphor are never rearranged.
ARRANGEABLE_KINDS = {"diagram", "timeline"}


def arrange(entry: dict, lib: str = "layouts") -> str:
    """Repeated units a restyler may rearrange: 'row:3', 'grid:4', 'column:5', ':ordered' when order matters.

    A unit is every field carrying the same number ("Heading 2", "Body 2", "card#2 > Heading 2"
    holds it). Units must be identical apart from that number. An entry can set "arrange"
    itself in the generator (a string, or false to opt out). Visuals are flagged only when
    their kind is a diagram or a timeline.
    """
    if "arrange" in entry:
        return entry["arrange"] or ""
    if lib == "visuals" and entry.get("kind") not in ARRANGEABLE_KINDS:
        return ""
    units: dict = {}
    for f in entry["fields"]:
        m = NUMBERED.match(f["name"])
        if not m or f["type"] == "deco" or f.get("follows"):
            continue
        units.setdefault(int(m.group(2)), {})[m.group(1) + "{n}" + m.group(3)] = f
    if len(units) < 2 or sorted(units) != list(range(1, len(units) + 1)):
        return ""
    keys = [set(u) for u in units.values()]
    if any(k != keys[0] for k in keys):
        return ""
    anchors = [(min(f["x"] for f in u.values()), min(f["y"] for f in u.values())) for u in units.values()]
    xs, ys = {round(a[0], 1) for a in anchors}, {round(a[1], 1) for a in anchors}
    kind = "row" if len(ys) == 1 else "column" if len(xs) == 1 else "grid"
    ordered = any(ORDERED_WORDS.search(k) for k in keys[0]) or bool(ORDERED_TAGS & set(entry.get("tags", "").split()))
    return f"{kind}:{len(units)}" + (":ordered" if ordered else "")


def write(lib: str) -> int:
    reg = json.loads((RAW / f"{lib}.registry.json").read_text(encoding="utf-8"))
    cols = COLUMNS[lib]
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = ASSETS / f"{lib}.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writerow(cols)
        for e in reg:
            row = dict(e, fields="; ".join(field_spec(f) for f in e["fields"]))
            if "arrange" in cols:
                row["arrange"] = arrange(e, lib)
            w.writerow([row.get(c, "") for c in cols])
    return len(reg)


def main() -> int:
    out = {lib: write(lib) for lib in COLUMNS if (RAW / f"{lib}.registry.json").exists()}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
