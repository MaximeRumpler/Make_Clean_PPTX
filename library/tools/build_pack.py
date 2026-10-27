#!/usr/bin/env python3
"""Build a style pack: the two libraries drawn with another set of style tokens.

    python library/tools/build_pack.py <style> [--pack-dir DIR] [--fit]

<style> is a name from library/style-tokens.json ("styles") or a .json file
with the tokens to change. Runs build.js, post.py, build_index.py and
build_contract.py with that style, and writes into the pack folder
(library/out/styles/<name>/pack/ by default):

    layouts.pptx  layouts.csv  visuals.pptx  visuals.csv  theme-contract.json  style.json

Same ids and field names as the bundled libraries, with the pack's own
character limits. Use it with build_deck.py --local-dir <pack folder>.
--fit also runs `fit_test.py --check` on both libraries of the pack.
The default libraries are built with the individual commands (library/README.md).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _style  # noqa: E402

TOOLS = Path(__file__).resolve().parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("style")
    ap.add_argument("--pack-dir")
    ap.add_argument("--fit", action="store_true")
    args = ap.parse_args(argv)
    if args.style == "default":
        print(json.dumps({"error": "the default style is the bundled library: see library/README.md"}))
        return 2
    env = dict(os.environ, MAKE_CLEAN_STYLE=args.style)
    if args.pack_dir:
        env["MAKE_CLEAN_PACK_DIR"] = str(Path(args.pack_dir).resolve())
    try:
        style = _style.load(args.style) if not args.pack_dir else None
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    py = sys.executable
    steps = [["node", str(TOOLS / "build.js"), "all"], [py, str(TOOLS / "post.py"), "all"],
             [py, str(TOOLS / "build_index.py")], [py, str(TOOLS / "build_contract.py")]]
    for cmd in steps:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if r.returncode:
            print(json.dumps({"error": f"{Path(cmd[1]).name} failed", "output": (r.stdout + r.stderr)[-2000:]}, indent=2))
            return 1
    pack = Path(env.get("MAKE_CLEAN_PACK_DIR") or style["pack"])
    report = {"style": args.style, "pack": str(pack), "files": sorted(p.name for p in pack.iterdir())}
    code = 0
    if args.fit:
        report["fit"] = {}
        for lib in ("layouts", "visuals"):
            r = subprocess.run([py, str(TOOLS / "fit_test.py"), lib, "--check", "--style", args.style, "--pack-dir", str(pack)],
                               capture_output=True, text=True)
            report["fit"][lib] = json.loads(r.stdout) if r.stdout.startswith("{") else r.stderr[-500:]
            code = code or r.returncode
    print(json.dumps(report, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
