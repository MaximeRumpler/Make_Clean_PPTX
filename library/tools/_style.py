"""Style tokens on the Python side: which pack is built, and where its files go.

Same rules as tools/style.js (keep the two in step). The style is chosen with
`--style <name|file.json>` or the MAKE_CLEAN_STYLE environment variable;
nothing means "default", the libraries bundled in skills/make-clean-pptx/assets/.
A pack is written to library/out/styles/<name>/pack/ unless MAKE_CLEAN_PACK_DIR
(or `--pack-dir`) says otherwise.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
TOKENS_FILE = ROOT / "style-tokens.json"
BUNDLED = REPO / "skills" / "make-clean-pptx" / "assets"

ALLOWED = {
    "cards": ("fill", "outline", "fill-outline"),
    "background": ("paper", "surface"),
    "title_case": ("as-written", "upper"),
    "numbering": ("as-designed", "plain", "padded"),
}


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        if k.startswith("_"):
            continue
        if k not in base:
            raise ValueError(f"unknown style token '{k}'")
        out[k] = dict(base[k], **v) if isinstance(v, dict) else v
    return out


def _validate(name: str, t: dict) -> dict:
    for k, values in ALLOWED.items():
        if t[k] not in values:
            raise ValueError(f"style '{name}': {k} must be one of {', '.join(values)} (got '{t[k]}')")
    if not isinstance(t["radius"], (int, float)) or not 0 <= t["radius"] <= 0.5:
        raise ValueError(f"style '{name}': radius is in inches, 0 to 0.5")
    for k in ("heading", "body"):
        if not isinstance(t["fonts"].get(k), str) or not t["fonts"][k]:
            raise ValueError(f"style '{name}': fonts.{k} must be a font name")
        if not 0.4 <= float(t["char_em"].get(k, 0)) <= 0.8:
            raise ValueError(f"style '{name}': char_em.{k} must be between 0.4 and 0.8")
    return t


def take_arg(argv: list, flag: str) -> str | None:
    """Remove `flag value` from argv (in place) and return the value."""
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            value = argv[i + 1]
            del argv[i:i + 2]
            return value
    return None


def load(which: str | None = None) -> dict:
    """{name, tokens, raw (build.js output), pack (where the finished files go)}."""
    which = which or os.environ.get("MAKE_CLEAN_STYLE") or "default"
    data = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    if which == "default":
        return {"name": "default", "tokens": _validate("default", _merge(data["default"], {})),
                "raw": ROOT / "out", "pack": Path(os.environ.get("MAKE_CLEAN_PACK_DIR") or BUNDLED)}
    if which.endswith(".json"):
        over = json.loads(Path(which).read_text(encoding="utf-8"))
        name = over.pop("name", None) or Path(which).stem
    elif which in data.get("styles", {}):
        name, over = which, data["styles"][which]
    else:
        raise ValueError(f"unknown style '{which}': use a name from library/style-tokens.json or a .json file")
    if not re.match(r"^[A-Za-z0-9][A-Za-z0-9_-]*$", name) or name == "default":
        raise ValueError(f"style name '{name}' must be a simple word other than 'default'")
    raw = ROOT / "out" / "styles" / name
    pack = Path(os.environ.get("MAKE_CLEAN_PACK_DIR") or raw / "pack")
    return {"name": name, "tokens": _validate(name, _merge(data["default"], over)), "raw": raw, "pack": pack}


def from_argv(argv: list) -> dict:
    """Read --style and --pack-dir from argv (removing them) and load the style."""
    which = take_arg(argv, "--style")
    pack_dir = take_arg(argv, "--pack-dir")
    if pack_dir:
        os.environ["MAKE_CLEAN_PACK_DIR"] = pack_dir
    return load(which)
