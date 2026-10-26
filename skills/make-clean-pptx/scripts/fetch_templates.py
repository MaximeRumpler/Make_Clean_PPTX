#!/usr/bin/env python3
"""Locate the layouts and visuals libraries (pptx + index).

Resolution order
  1. --local-dir DIR  /  $MAKE_CLEAN_PPTX_TEMPLATES_DIR   (your own files)
  2. the copies bundled in the skill folder (assets/), unless --remote is given
     or $MAKE_CLEAN_PPTX_REPO is set: no network needed
  3. --remote: fresh cache, then GitHub download (raw.githubusercontent.com,
     github.com/raw, then the Git-LFS media host), then a stale cache

Prints one JSON object on stdout:
  {"source": "bundled", "layouts": {"pptx": "...", "index": "..."}, "visuals": {...}}
("design" and "shapes" are kept as aliases of "layouts" and "visuals".)

Environment overrides: MAKE_CLEAN_PPTX_REPO, _REF, _PATH, _CACHE, _TEMPLATES_DIR.
Only the Python standard library is used here on purpose.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from _common import SKILL_DIR, eprint, load_config

UA = "make-clean-pptx/1.0 (+https://github.com/MaximeRumpler/Make_Clean_PPTX)"


class FetchError(RuntimeError):
    pass


def cache_dir() -> Path:
    override = os.environ.get("MAKE_CLEAN_PPTX_CACHE")
    candidates = [Path(override)] if override else []
    candidates += [Path.home() / ".cache" / "make-clean-pptx", Path(tempfile.gettempdir()) / "make-clean-pptx"]
    for c in candidates:
        try:
            c.mkdir(parents=True, exist_ok=True)
            return c
        except OSError:
            continue
    raise FetchError("no writable cache directory")


def _download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as resp, open(dest, "wb") as fh:  # noqa: S310 (https only)
        shutil.copyfileobj(resp, fh)
    head = dest.read_bytes()[:60]
    if head.startswith(b"version https://git-lfs"):
        dest.unlink(missing_ok=True)
        raise FetchError("got a Git-LFS pointer instead of the file")
    is_text_index = dest.name.endswith((".csv.part", ".csv"))
    if not is_text_index and not zipfile.is_zipfile(dest):
        dest.unlink(missing_ok=True)
        raise FetchError("downloaded file is not a valid Office document")


def _urls(repo: str, ref: str, path: str, name: str) -> list[str]:
    rel = f"{path.strip('/')}/{name}" if path else name
    return [
        f"https://raw.githubusercontent.com/{repo}/{ref}/{rel}",
        f"https://github.com/{repo}/raw/{ref}/{rel}",
        f"https://media.githubusercontent.com/media/{repo}/{ref}/{rel}",
    ]


def _fetch_one(repo, ref, path, name, dest: Path) -> str:
    errors = []
    tmp = dest.with_suffix(dest.suffix + ".part")
    for url in _urls(repo, ref, path, name):
        try:
            _download(url, tmp)
            tmp.replace(dest)
            return url
        except (urllib.error.URLError, OSError, FetchError) as exc:
            errors.append(f"{url} -> {exc}")
    raise FetchError(f"could not download {name}:\n  " + "\n  ".join(errors))


def _local(dir_: Path, cfg: dict) -> dict:
    out = {}
    for kind, files in cfg["files"].items():
        out[kind] = {}
        for role, fname in files.items():
            p = dir_ / fname
            if not p.is_file():
                raise FetchError(f"{p} not found (expected from config.json)")
            out[kind][role] = str(p)
    return out


ALIASES = {"design": "layouts", "shapes": "visuals"}


def _with_aliases(result: dict) -> dict:
    for old, new in ALIASES.items():
        if new in result and old not in result:
            result[old] = result[new]
    return result


def ensure_templates(local_dir: str | None = None, refresh: bool = False, remote: bool = False) -> dict:
    cfg = load_config()
    local_dir = local_dir or os.environ.get("MAKE_CLEAN_PPTX_TEMPLATES_DIR")
    if local_dir:
        return _with_aliases({"source": "local", **_local(Path(local_dir).expanduser(), cfg)})
    bundled = SKILL_DIR / cfg.get("assets_dir", "assets")
    if not (remote or refresh or os.environ.get("MAKE_CLEAN_PPTX_REPO")):
        try:
            return _with_aliases({"source": "bundled", **_local(bundled, cfg)})
        except FetchError:
            eprint("warning: bundled libraries missing, trying GitHub")

    repo = os.environ.get("MAKE_CLEAN_PPTX_REPO", cfg["repo"])
    ref = os.environ.get("MAKE_CLEAN_PPTX_REF", cfg["ref"])
    path = os.environ.get("MAKE_CLEAN_PPTX_PATH", cfg["path"])
    root = cache_dir() / repo.replace("/", "__") / ref
    root.mkdir(parents=True, exist_ok=True)
    ttl = float(cfg.get("cache_ttl_hours", 24)) * 3600

    wanted = [(kind, role, fname) for kind, files in cfg["files"].items() for role, fname in files.items()]
    fresh = all(
        (root / f).is_file() and (time.time() - (root / f).stat().st_mtime) < ttl for _, _, f in wanted
    )
    source = "cache"
    if refresh or not fresh:
        try:
            for _, _, fname in wanted:
                _fetch_one(repo, ref, path, fname, root / fname)
            source = "github"
        except FetchError as exc:
            if all((root / f).is_file() for _, _, f in wanted):
                eprint(f"warning: using stale cache ({exc})")
                source = "stale-cache"
            else:
                raise FetchError(
                    f"{exc}\n\nIf the sandbox blocks GitHub, use the bundled copies (drop --remote), attach the files or pass "
                    f"--local-dir <folder>. Expected names: "
                    + ", ".join(f for _, _, f in wanted)
                ) from exc

    result = {"source": source, "repo": repo, "ref": ref}
    for kind, files in cfg["files"].items():
        result[kind] = {role: str(root / fname) for role, fname in files.items()}
    return _with_aliases(result)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--local-dir", help="use templates from this folder instead of GitHub")
    ap.add_argument("--remote", action="store_true", help="download from GitHub (config repo, or $MAKE_CLEAN_PPTX_REPO)")
    ap.add_argument("--refresh", action="store_true", help="with --remote: ignore the cache and download again")
    args = ap.parse_args(argv)
    try:
        print(json.dumps(ensure_templates(args.local_dir, args.refresh, args.remote), indent=2))
        return 0
    except FetchError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        return 3


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to a legacy code page; agents read UTF-8
        getattr(_stream, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
