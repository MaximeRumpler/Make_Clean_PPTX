#!/usr/bin/env python3
"""Check that the environment can run the skill, and say how to fix what is missing.

    doctor.py [--offline]

Required: Python >= 3.9, python-pptx, openpyxl, Pillow, and the bundled libraries in assets/.
Optional: LibreOffice + poppler (visual check), network access (online icons, images, --remote libraries).
Exit code 0 when the required pieces are present, 1 otherwise.
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
import urllib.error
import urllib.request

REQUIRED = [("pptx", "python-pptx"), ("openpyxl", "openpyxl"), ("PIL", "Pillow"), ("lxml", "lxml")]
HOSTS = {
    "raw.githubusercontent.com": "https://raw.githubusercontent.com/",
    "cdn.jsdelivr.net": "https://cdn.jsdelivr.net/npm/openmoji@15.1.0/package.json",
    "fonts.gstatic.com": "https://fonts.gstatic.com/",
    "api.openverse.org": "https://api.openverse.org/v1/",
    "commons.wikimedia.org": "https://commons.wikimedia.org/w/api.php?action=query&format=json",
}


def reachable(url: str) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "make-clean-pptx-doctor"})
        urllib.request.urlopen(req, timeout=8)  # noqa: S310
        return True
    except urllib.error.HTTPError:
        return True  # the host answered; an HTTP status is fine here
    except Exception:  # noqa: BLE001
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip network checks")
    args = ap.parse_args(argv)

    report: dict = {"python": sys.version.split()[0], "required": {}, "optional": {}, "network": {}, "fix": []}
    ok = sys.version_info >= (3, 9)
    if not ok:
        report["fix"].append("Python 3.9+ is required")

    missing = []
    for mod, pkg in REQUIRED:
        try:
            m = importlib.import_module(mod)
            report["required"][pkg] = getattr(m, "__version__", "ok")
        except ImportError:
            report["required"][pkg] = None
            missing.append(pkg)
    if missing:
        ok = False
        report["fix"].append("pip install " + " ".join(missing) + "   (add --break-system-packages on managed Pythons)")

    from _common import SKILL_DIR, load_config

    cfg = load_config()
    assets = SKILL_DIR / cfg.get("assets_dir", "assets")
    wanted = [f for files in cfg["files"].values() for f in files.values()] + ["icons/lucide.json"]
    report["libraries"] = {f: (assets / f).is_file() for f in wanted}
    if not all(report["libraries"].values()):
        ok = False
        report["fix"].append(f"bundled libraries missing in {assets}: reinstall the skill, or use --local-dir / --remote")

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    report["optional"]["libreoffice"] = soffice
    report["optional"]["pdftoppm"] = shutil.which("pdftoppm")
    if not (soffice and report["optional"]["pdftoppm"]):
        report["fix"].append("optional, for render_check.py: apt install libreoffice-impress poppler-utils (or brew)")

    if not args.offline:
        for host, url in HOSTS.items():
            report["network"][host] = reachable(url)
        if not (report["network"]["cdn.jsdelivr.net"] and report["network"]["fonts.gstatic.com"]):
            report["fix"].append("online icon sources unreachable: use the bundled Lucide icons (find_icon.py --source lucide)")
        if not (report["network"]["api.openverse.org"] or report["network"]["commons.wikimedia.org"]):
            report["fix"].append("image banks unreachable: build without photos (shapes/icons) or ask for attached images")

    report["ok"] = ok
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
