#!/usr/bin/env python3
"""Write the CSV indexes of the libraries from the generator registries.

    python library/tools/build_index.py

Reads library/out/<lib>.registry.json (written by build.js) and writes
skills/make-clean-pptx/assets/<lib>.csv. Semicolon-separated, UTF-8, one row
per slide (layouts) or per component (visuals). The column contract is in
skills/make-clean-pptx/references/index-schema.md.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "skills" / "make-clean-pptx" / "assets"

COLUMNS = {
    "layouts": ["id", "slide", "name", "category", "style", "density", "description", "use_when", "tags", "fields"],
    "visuals": ["id", "slide", "name", "category", "kind", "frame", "objective", "data_type", "dimensions", "complexity",
                "description", "use_when", "limits", "fill_notes", "tags", "related", "fields"],
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
    if flags:
        parts.append(",".join(flags))
    return "|".join(parts).rstrip("|")


def write(lib: str) -> int:
    reg = json.loads((ROOT / "out" / f"{lib}.registry.json").read_text(encoding="utf-8"))
    cols = COLUMNS[lib]
    path = ASSETS / f"{lib}.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writerow(cols)
        for e in reg:
            row = dict(e, fields="; ".join(field_spec(f) for f in e["fields"]))
            w.writerow([row.get(c, "") for c in cols])
    return len(reg)


def main() -> int:
    out = {lib: write(lib) for lib in COLUMNS if (ROOT / "out" / f"{lib}.registry.json").exists()}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
