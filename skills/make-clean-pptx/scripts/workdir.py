#!/usr/bin/env python3
"""A scratch folder for the files that are not the deliverable, and a safe way to remove it.

    workdir.py                 create a scratch folder, print its path
    workdir.py --clean DIR     delete DIR (only a folder this script created)

Put the deck spec, renders, contact sheets, reports and downloaded images in the scratch
folder, write the deck itself to the user's folder, then clean up: the user's folder keeps
only what they asked for. The folder lives in the system temporary directory (or the
agent's own scratch folder: set MAKE_CLEAN_PPTX_WORKDIR to a parent folder to choose).

Exit code 0 on success, 2 when --clean refuses a folder (not created by this script).
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

MARKER = ".make-pptx-workdir"


def create() -> Path:
    parent = os.environ.get("MAKE_CLEAN_PPTX_WORKDIR") or None
    if parent:
        Path(parent).mkdir(parents=True, exist_ok=True)
    try:
        d = Path(tempfile.mkdtemp(prefix="make-pptx-", dir=parent))
    except OSError:  # some sandboxes only allow writing in the working folder: still cleaned up at the end
        d = Path(tempfile.mkdtemp(prefix=".make-pptx-work-", dir="."))
    (d / MARKER).write_text("created by workdir.py: safe to delete\n", encoding="utf-8")
    return d


def clean(folder: Path) -> bool:
    folder = folder.resolve()
    if not (folder / MARKER).is_file():
        return False
    shutil.rmtree(folder, ignore_errors=True)
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clean", metavar="DIR", help="delete a scratch folder made by this script")
    args = ap.parse_args(argv)
    if args.clean:
        if clean(Path(args.clean)):
            print(f"Removed {args.clean}")
            return 0
        print(f"Not removed: {args.clean} was not created by workdir.py", file=sys.stderr)
        return 2
    print(create())
    return 0


if __name__ == "__main__":
    sys.exit(main())
