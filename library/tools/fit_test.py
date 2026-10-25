#!/usr/bin/env python3
"""Fill every text field of a library at its character limit, build, lint and render.

    python library/tools/fit_test.py [layouts|visuals] [--out DIR]

The limits in the index come from a geometric estimate; this test checks them
for real: if a slide of the contact sheet shows text spilling out of its box,
lower the limit (option `limit` in the generator) or enlarge the box.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "skills" / "make-clean-pptx" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from read_index import load_index  # noqa: E402

WORDS = ("market growth team result client margin plan project risk value cost energy quality service "
         "region product launch partner budget target review change people process data system").split()


def filler(n: int, seed: int) -> str:
    out, i = [], seed
    while len(" ".join(out)) < n:
        out.append(WORDS[i % len(WORDS)])
        i += 7
    text = " ".join(out)[:n].rstrip()
    return text[:1].upper() + text[1:]


def spec_for(lib: str, entries: list, out: Path) -> dict:
    slides = []
    for k, e in enumerate(entries):
        fill = {}
        for i, f in enumerate(e["field_list"]):
            if f["type"] in ("text", "bullets") and f["limit"] and not f.get("follows"):
                if f["type"] == "bullets":
                    per = max(4, f["limit"] // 3 - 2)
                    fill[f["name"]] = [filler(per, k + i + j) for j in range(3)]
                else:
                    fill[f["name"]] = filler(f["limit"], k + i)
        if lib == "layouts":
            slides.append({"source": "layouts", "slide": e["slide"], "fill": fill, "keep_unfilled": True})
        else:
            slides.append({"source": "layouts", "id": "L-31", "fill": {"Title": e["id"] + " " + e["name"]},
                           "insert": [{"source": "visuals", "slide": e["slide"], "component": e["id"], "into": "Content Area",
                                       "fill": fill, "keep_unfilled": True}]})
    return {"output": str(out / f"fit-{lib}.pptx"), "slides": slides}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("lib", nargs="?", default="layouts", choices=["layouts", "visuals"])
    ap.add_argument("--out", default=str(REPO / "library" / "out" / "fit"))
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    entries = load_index(REPO / "skills" / "make-clean-pptx" / "assets" / f"{args.lib}.csv")
    spec = spec_for(args.lib, entries, out)
    (out / f"fit-{args.lib}.json").write_text(json.dumps(spec, indent=1), encoding="utf-8")
    py = sys.executable
    b = subprocess.run([py, str(SCRIPTS / "build_deck.py"), "--spec", str(out / f"fit-{args.lib}.json")], capture_output=True, text=True)
    report = json.loads(b.stdout)
    overflow = [w for w in report.get("warnings", []) if "overflow" in w]
    lint = subprocess.run([py, str(SCRIPTS / "lint_deck.py"), spec["output"], "--json"], capture_output=True, text=True)
    r = subprocess.run([py, str(SCRIPTS / "render_check.py"), spec["output"], "--out-dir", str(out / args.lib), "--dpi", "70", "--cols", "4"],
                       capture_output=True, text=True)
    print(json.dumps({"slides": report.get("slides"), "overflow_warnings": overflow,
                      "lint": json.loads(lint.stdout).get("summary", lint.stdout[:300]) if lint.stdout.startswith("{") else lint.stdout[:300],
                      "contact_sheet": json.loads(r.stdout).get("contact_sheet") if r.stdout.startswith("{") else r.stderr[-300:]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
