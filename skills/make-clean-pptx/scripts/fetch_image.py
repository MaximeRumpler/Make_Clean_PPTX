#!/usr/bin/env python3
"""Find and download a freely-licensed illustrative image. No API key needed.

    fetch_image.py --query "solar panels on a roof" --out img/slide3.jpg \
                   [--orientation wide|tall|square|any] [--min-width 1600]
                   [--source auto|openverse|wikimedia] [--pick N] [--list]

Sources (both keyless):
  * Openverse   https://api.openverse.org   (aggregates Flickr, Wikimedia, museums...)
  * Wikimedia Commons  https://commons.wikimedia.org

Only licences that allow commercial reuse are accepted (CC0, public domain,
CC BY, CC BY-SA; see config.json). The attribution string is returned in "credit"
and should be passed along in the deck spec so it ends up in the speaker notes
and the .credits.md file.

Unsplash, Pexels and Pixabay need an API key and are intentionally not used.

--offline (or MAKE_CLEAN_PPTX_OFFLINE=1) searches nothing and says so.

Exit codes: 0 ok, 3 network blocked / no results (JSON explains).
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from _common import is_offline, load_config, offline_message, set_offline

UA = "make-clean-pptx/1.0 (+https://github.com/MaximeRumpler/Make_Clean_PPTX)"
OPENVERSE = "https://api.openverse.org/v1/images/"
COMMONS = "https://commons.wikimedia.org/w/api.php"


class ImageError(RuntimeError):
    pass


def _get_json(url: str) -> dict:
    if is_offline():
        raise ImageError(offline_message("searching photos", url))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (https only)
            return json.load(r)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise ImageError(f"{url.split('?')[0]}: {exc}") from exc


def _strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


# ---------------------------------------------------------------- Openverse
def search_openverse(query: str, licenses: list[str], orientation: str) -> list[dict]:
    params = {"q": query, "license": ",".join(licenses), "page_size": "20", "mature": "false"}
    if orientation == "wide":
        params["aspect_ratio"] = "wide"
    elif orientation == "tall":
        params["aspect_ratio"] = "tall"
    elif orientation == "square":
        params["aspect_ratio"] = "square"
    data = _get_json(OPENVERSE + "?" + urllib.parse.urlencode(params))
    out = []
    for r in data.get("results", []):
        if not r.get("url"):
            continue
        out.append({
            "source": "openverse",
            "title": r.get("title") or "",
            "creator": r.get("creator") or "",
            "license": (r.get("license") or "").lower(),
            "license_url": r.get("license_url") or "",
            "landing_url": r.get("foreign_landing_url") or "",
            "url": r["url"],
            "width": r.get("width") or 0,
            "height": r.get("height") or 0,
            "credit": _strip_html(r.get("attribution") or ""),
        })
    return out


# ---------------------------------------------------------------- Commons
_COMMONS_OK = re.compile(r"^(cc0|public domain|pd\b|cc[ -]by(?:[ -]sa)?\b)", re.I)


def search_wikimedia(query: str, _licenses, _orientation) -> list[dict]:
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
        "gsrsearch": f"{query} filetype:bitmap", "gsrlimit": "20",
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "2400",
    }
    data = _get_json(COMMONS + "?" + urllib.parse.urlencode(params))
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 999))
    out = []
    for p in pages:
        info = (p.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        lic = _strip_html((meta.get("LicenseShortName") or {}).get("value", ""))
        if not _COMMONS_OK.match(lic) or info.get("mime") not in ("image/jpeg", "image/png"):
            continue
        artist = _strip_html((meta.get("Artist") or {}).get("value", "")) or "Unknown author"
        title = p.get("title", "").removeprefix("File:")
        url = info.get("thumburl") if info.get("width", 0) > 2400 and info.get("thumburl") else info.get("url")
        out.append({
            "source": "wikimedia",
            "title": title,
            "creator": artist,
            "license": lic.lower().replace(" ", "-"),
            "license_url": (meta.get("LicenseUrl") or {}).get("value", ""),
            "landing_url": info.get("descriptionurl", ""),
            "url": url,
            "width": info.get("width", 0),
            "height": info.get("height", 0),
            "credit": f'"{title}" by {artist}, {lic}, via Wikimedia Commons',
        })
    return out


# ---------------------------------------------------------------- selection
def _ok_orientation(c: dict, orientation: str) -> bool:
    w, h = c["width"] or 1, c["height"] or 1
    return {"wide": w / h >= 1.3, "tall": h / w >= 1.2, "square": 0.8 <= w / h <= 1.25}.get(orientation, True)


def candidates(query, source, licenses, orientation, min_width) -> tuple[list[dict], list[str]]:
    errors, found = [], []
    order = {"openverse": [search_openverse], "wikimedia": [search_wikimedia],
             "auto": [search_openverse, search_wikimedia]}[source]
    for fn in order:
        try:
            found += fn(query, licenses, orientation)
        except ImageError as exc:
            errors.append(str(exc))
    ok = [c for c in found if (c["width"] or 0) >= min_width and _ok_orientation(c, orientation)]
    return ok, errors


def download(c: dict, out: Path, max_dim: int, max_mb: int) -> dict:
    from PIL import Image

    if urllib.parse.urlparse(c["url"]).scheme not in ("http", "https"):
        raise ImageError("refusing non-http(s) URL")
    if is_offline():
        raise ImageError(offline_message("downloading a photo", c["url"]))
    req = urllib.request.Request(c["url"], headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310
            blob = r.read(max_mb * 1024 * 1024 + 1)
    except (urllib.error.URLError, OSError) as exc:
        raise ImageError(f"download failed: {exc}") from exc
    if len(blob) > max_mb * 1024 * 1024:
        raise ImageError(f"image larger than {max_mb} MB")
    try:
        im = Image.open(io.BytesIO(blob))
        im.load()
    except Exception as exc:  # noqa: BLE001
        raise ImageError(f"not a valid image: {exc}") from exc
    has_alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
    im.thumbnail((max_dim, max_dim))
    out.parent.mkdir(parents=True, exist_ok=True)
    if has_alpha:
        out = out.with_suffix(".png")
        im.convert("RGBA").save(out)
    else:
        out = out.with_suffix(".jpg")
        im.convert("RGB").save(out, quality=88, optimize=True)
    return {"path": str(out), "width": im.width, "height": im.height}


def main(argv=None) -> int:
    cfg = load_config()["images"]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", "-q", required=True)
    ap.add_argument("--out", "-o", help="destination file (extension is set from the content)")
    ap.add_argument("--orientation", choices=["wide", "tall", "square", "any"], default="wide")
    ap.add_argument("--min-width", type=int, default=cfg["min_width"])
    ap.add_argument("--source", choices=["auto", "openverse", "wikimedia"], default="auto")
    ap.add_argument("--pick", type=int, default=1, help="use the Nth acceptable result (default 1)")
    ap.add_argument("--list", action="store_true", help="list candidates, download nothing")
    ap.add_argument("--offline", action="store_true", help="never use the network (photos then cannot be searched)")
    args = ap.parse_args(argv)
    set_offline(args.offline)
    if is_offline():
        print(json.dumps({"error": offline_message("searching photos"),
                          "hint": "Ask the user for their own pictures, or use bundled icons (find_icon.py)."}, indent=2))
        return 3

    cands, errors = candidates(args.query, args.source, cfg["allowed_licenses"], args.orientation, args.min_width)
    if not cands:
        print(json.dumps({
            "error": "no usable image found" if not errors else "image sources unreachable",
            "details": errors,
            "hint": "Try simpler keywords, --orientation any or a lower --min-width. If the photo sites are "
                    "blocked here, use icons instead or ask the user for their own images.",
        }, indent=2))
        return 3
    if args.list:
        print(json.dumps(cands[:10], indent=2, ensure_ascii=False))
        return 0
    if not args.out:
        ap.error("--out is required unless --list is used")

    for i, c in enumerate(cands[args.pick - 1:], start=args.pick):
        try:
            info = download(c, Path(args.out), cfg["max_dimension"], cfg["max_download_mb"])
        except ImageError as exc:
            errors.append(f"candidate {i}: {exc}")
            continue
        print(json.dumps({**info, **{k: c[k] for k in ("source", "title", "creator", "license", "license_url", "landing_url", "credit")}},
                         indent=2, ensure_ascii=False))
        return 0
    print(json.dumps({"error": "all candidates failed to download", "details": errors,
                      "hint": "Try other keywords, or go without a photo."}, indent=2))
    return 3


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to a legacy code page; agents read UTF-8
        getattr(_stream, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
