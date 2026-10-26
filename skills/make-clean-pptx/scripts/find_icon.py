#!/usr/bin/env python3
"""Find icons and simple illustrations, from the bundled set or free online libraries.

    find_icon.py "growth chart"                    # search the bundled Lucide set
    find_icon.py "rocket launch" --source all      # + Tabler, Material Symbols, OpenMoji, local folders
    find_icon.py --get material:rocket_launch --out build/icons/rocket.svg

Every result has a `ref` ("source:name"). Use it directly in a deck spec:
    "Icon 1": {"icon": "lucide:rocket"}
build_deck.py turns it into a native shape in the colour of the slot.

Sources
  lucide    bundled, ~1,900 line icons, ISC licence (no attribution needed)
  tabler    online (jsDelivr), ~5,000 line icons, MIT (names only, or tags via a local copy)
  material  online (Google Fonts), ~4,000 Material Symbols, Apache-2.0
  openmoji  online (jsDelivr), ~4,000 emoji-style pictograms, CC BY-SA 4.0: attribution required
  local     SVG files in the folders listed in config.json "icons.local_dirs" or
            $MAKE_CLEAN_PPTX_ICON_DIRS (e.g. downloaded Open Doodles or unDraw illustrations)

Prints JSON. Exit codes: 0 ok, 1 nothing found, 2 bad arguments, 3 network or source error.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

from _common import SKILL_DIR, eprint, load_config

UA = "make-clean-pptx/1.1 (+https://github.com/MaximeRumpler/Make_Clean_PPTX)"
LUCIDE_JSON = SKILL_DIR / "assets" / "icons" / "lucide.json"

SOURCES = {
    "lucide": {"license": "ISC", "credit": "Icon: Lucide (ISC licence)", "attribution_required": False},
    "tabler": {"license": "MIT", "credit": "Icon: Tabler Icons (MIT licence)", "attribution_required": False},
    "material": {"license": "Apache-2.0", "credit": "Icon: Material Symbols by Google (Apache 2.0)", "attribution_required": False},
    "openmoji": {"license": "CC BY-SA 4.0", "credit": "Pictogram: OpenMoji, openmoji.org (CC BY-SA 4.0)", "attribution_required": True},
    "local": {"license": "see the file's source", "credit": "", "attribution_required": None},
}
TABLER_VERSION = "3.35.0"
OPENMOJI_VERSION = "15.1.0"


class IconError(RuntimeError):
    pass


# ------------------------------------------------------------------ helpers
def _cache_dir() -> Path:
    from fetch_templates import cache_dir

    d = cache_dir() / "icons"
    d.mkdir(parents=True, exist_ok=True)
    return d


MAX_DOWNLOAD = 25 * 1024 * 1024  # catalogues are a few MB, icons a few KB


def _http(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (fixed https hosts)
            data = r.read(MAX_DOWNLOAD + 1)
            if len(data) > MAX_DOWNLOAD:
                raise IconError(f"{url.split('/')[2]} sent more than {MAX_DOWNLOAD // 2**20} MB; refused")
            return data
    except IconError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise IconError(f"cannot reach {url.split('/')[2]}: {exc}") from exc


def _cached(name: str, url: str, ttl_days: int = 30) -> bytes:
    p = _cache_dir() / name
    if p.exists() and time.time() - p.stat().st_mtime < ttl_days * 86400:
        return p.read_bytes()
    data = _http(url)
    p.write_bytes(data)
    return data


def _tokens(text: str) -> set:
    return {t[:-1] if len(t) > 3 and t.endswith("s") else t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 1}


def _score(q: set, name: str, tags, cats) -> float:
    nt = _tokens(name.replace("-", " ").replace("_", " "))
    s = 3.0 * len(q & nt) + 2.0 * len(q & _tokens(" ".join(tags))) + 1.0 * len(q & _tokens(" ".join(cats)))
    if q and q <= nt:
        s += 3
    return s - 0.02 * len(nt)  # prefer short, generic names


# ------------------------------------------------------------------ catalogues
def _lucide():
    data = json.loads(LUCIDE_JSON.read_text(encoding="utf-8"))
    return [(n, d["tags"], d["categories"]) for n, d in data.items()]


def _tabler():
    raw = json.loads(_cached(f"tabler-{TABLER_VERSION}.json", f"https://data.jsdelivr.com/v1/package/npm/@tabler/icons@{TABLER_VERSION}/flat"))
    names = sorted({m.group(1) for f in raw["files"] if (m := re.match(r"/icons/outline/([^/]+)\.svg$", f["name"]))})
    return [(n, [], []) for n in names]


def _material():
    raw = _cached("material-symbols.json", "https://fonts.google.com/metadata/icons?key=material_symbols&incomplete=1").decode("utf-8")
    data = json.loads(raw[raw.index("{"):])
    return [(i["name"], i.get("tags", []), i.get("categories", [])) for i in data["icons"]
            if "Material Symbols Outlined" not in i.get("unsupported_families", [])]


def _openmoji():
    data = json.loads(_cached(f"openmoji-{OPENMOJI_VERSION}.json", f"https://cdn.jsdelivr.net/npm/openmoji@{OPENMOJI_VERSION}/data/openmoji.json"))
    out = []
    for e in data:
        if e.get("skintone"):
            continue
        tags = [e.get("annotation", "")] + [t.strip() for t in (e.get("tags", "") + "," + e.get("openmoji_tags", "")).split(",")]
        out.append((e["hexcode"], [t for t in tags if t], [e.get("group", ""), e.get("subgroups", "")]))
    return out


def local_dirs() -> list:
    dirs = list(load_config().get("icons", {}).get("local_dirs", []))
    env = os.environ.get("MAKE_CLEAN_PPTX_ICON_DIRS")
    if env:
        dirs += [d for d in env.split(os.pathsep) if d]
    return [Path(d).expanduser() for d in dirs if Path(d).expanduser().is_dir()]


def _local():
    out = []
    for d in local_dirs():
        for f in d.rglob("*.svg"):
            head = f.read_text(encoding="utf-8", errors="ignore")[:600]
            m = re.search(r"tags:\s*\[([^\]]*)\]", head)  # Tabler-style comment
            tags = [t.strip() for t in m.group(1).split(",")] if m else []
            out.append((str(f), tags, [f.parent.name]))
    return out


CATALOGUES = {"lucide": _lucide, "tabler": _tabler, "material": _material, "openmoji": _openmoji, "local": _local}


def search(query: str, sources, top: int = 12) -> list:
    q = _tokens(query)
    results, errors = [], {}
    for src in sources:
        try:
            cat = CATALOGUES[src]()
        except IconError as exc:
            errors[src] = str(exc)
            continue
        for name, tags, cats in cat:
            label = Path(name).stem if src == "local" else name
            s = _score(q, label, tags, cats)
            if s > 0:
                results.append({"ref": f"{src}:{name}", "source": src, "name": label, "score": round(s, 2),
                                "tags": list(tags)[:8], "license": SOURCES[src]["license"]})
    results.sort(key=lambda r: (-r["score"], r["source"] != "lucide", r["name"]))
    return results[:top], errors


# ------------------------------------------------------------------ fetching
def get_svg(ref: str):
    """Return (svg_text, meta) for 'source:name' (a bare name means lucide)."""
    src, _, name = ref.partition(":") if ":" in ref else ("lucide", "", ref)
    if src not in SOURCES:  # a Windows path such as C:\\... or an unknown prefix
        src, name = "local", ref
    meta = dict(SOURCES[src], ref=f"{src}:{name}", source=src, name=name)
    if src == "lucide":
        data = json.loads(LUCIDE_JSON.read_text(encoding="utf-8"))
        if name not in data:
            raise IconError(f"no Lucide icon named '{name}'; search with find_icon.py \"{name.replace('-', ' ')}\"")
        return data[name]["svg"], meta
    if src == "tabler":
        url = f"https://cdn.jsdelivr.net/npm/@tabler/icons@{TABLER_VERSION}/icons/outline/{name}.svg"
    elif src == "material":
        url = f"https://fonts.gstatic.com/s/i/short-term/release/materialsymbolsoutlined/{name}/default/48px.svg"
    elif src == "openmoji":
        url = f"https://cdn.jsdelivr.net/npm/openmoji@{OPENMOJI_VERSION}/black/svg/{name.upper()}.svg"
    else:
        p = Path(name).expanduser()
        if p.suffix.lower() != ".svg":
            raise IconError(f"only .svg files can be used as icons or illustrations: {p}")
        if not p.is_file():
            raise IconError(f"file not found: {p}")
        meta["credit"] = ""
        return p.read_text(encoding="utf-8"), meta
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", f"{src}-{name}.svg")
    return _cached(safe, url, ttl_days=365).decode("utf-8"), meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", help="what the icon should show, in English")
    ap.add_argument("--source", default="lucide", help="lucide, tabler, material, openmoji, local, all, or a comma list")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--get", metavar="REF", help="download one icon by ref and print its SVG path")
    ap.add_argument("--out", help="where to write the SVG for --get")
    args = ap.parse_args(argv)

    if args.get:
        try:
            svg, meta = get_svg(args.get)
        except IconError as exc:
            print(json.dumps({"error": str(exc)}))
            return 3
        out = Path(args.out or f"{re.sub(r'[^A-Za-z0-9_-]', '_', meta['name'])}.svg")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        print(json.dumps(dict(meta, path=str(out)), indent=2))
        return 0

    if not args.query:
        ap.print_usage(sys.stderr)
        return 2
    srcs = list(SOURCES) if args.source == "all" else [s.strip() for s in args.source.split(",")]
    bad = [s for s in srcs if s not in SOURCES]
    if bad:
        eprint(f"unknown source(s): {', '.join(bad)}")
        return 2
    results, errors = search(args.query, srcs, args.top)
    print(json.dumps({"results": results, "errors": errors}, indent=2, ensure_ascii=False))
    if not results:
        return 3 if errors else 1
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to a legacy code page; agents read UTF-8
        getattr(_stream, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
