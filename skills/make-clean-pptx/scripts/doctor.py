#!/usr/bin/env python3
"""Check that the environment can run the skill, and say how to fix what is missing.

    doctor.py [--offline] [--fix]

Required: Python >= 3.9, python-pptx, openpyxl, Pillow, and the bundled libraries in assets/.
Optional: LibreOffice + poppler (visual check), network access (online icons, images, --remote libraries).

With --fix, missing Python packages are installed with pip from requirements.txt
(first normally, then with --user). It never forces packages into a Python that
the system manages (--break-system-packages): that can break the computer's own tools.
The "message" field is one plain sentence the agent can pass on to the user.

Exit code 0 when the required pieces are present, 1 otherwise.
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Not imported from _common: _common needs python-pptx, which may be the thing that is missing.
SKILL_DIR = Path(__file__).resolve().parent.parent
REQUIREMENTS = SKILL_DIR / "requirements.txt"
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


def check_packages() -> dict:
    """{package: version or None}. Runs in a fresh interpreter so packages installed by --fix are seen."""
    code = ("import importlib, json\nout = {}\n"
            f"for mod, pkg in {REQUIRED!r}:\n"
            "    try:\n        out[pkg] = getattr(importlib.import_module(mod), '__version__', 'ok')\n"
            "    except ImportError:\n        out[pkg] = None\n"
            "print(json.dumps(out))")
    try:
        p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
        return json.loads(p.stdout)
    except (OSError, ValueError, subprocess.SubprocessError):
        out = {}  # cannot start a second interpreter: check in this one
        for mod, pkg in REQUIRED:
            try:
                out[pkg] = getattr(importlib.import_module(mod), "__version__", "ok")
            except ImportError:
                out[pkg] = None
        return out


def pip_install(user: bool) -> dict:
    """One pip attempt; returns {"command", "ok", "error"}."""
    cmd = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-r", str(REQUIREMENTS)]
    if user:
        cmd.append("--user")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"command": " ".join(cmd), "ok": False, "error": str(exc)}
    last = (p.stderr or p.stdout).strip().splitlines()[-1:] or [f"pip exited with code {p.returncode}"]
    return {"command": " ".join(cmd), "ok": p.returncode == 0, "error": None if p.returncode == 0 else last[0]}


def fix_packages(missing: list[str]) -> dict:
    """Install the missing packages, then check again. Never uses --break-system-packages."""
    attempts = []
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    for user in (False, True):
        if user and in_venv:
            break  # --user is refused inside a virtual environment
        attempts.append(pip_install(user))
        still = [pkg for pkg, v in check_packages().items() if v is None]
        if not still:
            break
    return {"attempts": attempts, "installed": [p for p in missing if p not in still], "still_missing": still}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="skip network checks")
    ap.add_argument("--fix", action="store_true", help="install missing Python packages with pip")
    args = ap.parse_args(argv)

    report: dict = {"python": sys.version.split()[0], "required": {}, "optional": {}, "network": {}, "fix": []}
    ok = sys.version_info >= (3, 9)
    message = "Everything the skill needs is installed."
    if not ok:
        report["fix"].append("Python 3.9 or newer is required: install a recent Python from python.org")
        message = "This Python is too old for the skill: please install Python 3.9 or newer from python.org."

    report["required"] = check_packages()
    missing = [pkg for pkg, v in report["required"].items() if v is None]
    if missing and args.fix:
        report["install"] = fix_packages(missing)
        missing = report["install"]["still_missing"]
        report["required"] = check_packages()
        if not missing:
            message = "The missing Python packages are now installed; the skill is ready."
    if missing:
        ok = False
        cmd = f'"{sys.executable}" -m pip install -r "{REQUIREMENTS}"'
        if args.fix:
            report["fix"].append(f"automatic install failed: create a virtual environment (python -m venv .venv), "
                                 f"activate it and run pip install -r {REQUIREMENTS}")
            message = ("Some Python packages could not be installed automatically (" + ", ".join(missing)
                       + "). Please run this command in a terminal, or ask whoever manages this computer: " + cmd)
        else:
            report["fix"].append("missing Python packages (" + ", ".join(missing) + "): run doctor.py --fix, or " + cmd)
            message = ("A few Python packages are missing (" + ", ".join(missing)
                       + "); running doctor.py --fix installs them.")

    with open(SKILL_DIR / "config.json", encoding="utf-8") as fh:
        cfg = json.load(fh)
    assets = SKILL_DIR / cfg.get("assets_dir", "assets")
    wanted = [f for files in cfg["files"].values() for f in files.values()] + ["icons/lucide.json"]
    report["libraries"] = {f: (assets / f).is_file() for f in wanted}
    if not all(report["libraries"].values()):
        ok = False
        report["fix"].append(f"the slide libraries are missing from {assets}: install the skill again")
        message = "The skill's files are incomplete: please download and install the skill again."

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    report["optional"]["libreoffice"] = soffice
    report["optional"]["pdftoppm"] = shutil.which("pdftoppm")
    if not (soffice and report["optional"]["pdftoppm"]):
        report["fix"].append("optional, to preview slides as images: install LibreOffice (libreoffice.org) and "
                             "poppler (Linux: apt install libreoffice-impress poppler-utils; macOS: brew install poppler)")

    if not args.offline:
        for host, url in HOSTS.items():
            report["network"][host] = reachable(url)
        if not (report["network"]["cdn.jsdelivr.net"] and report["network"]["fonts.gstatic.com"]):
            report["fix"].append("online icons unreachable: the bundled icons work offline (find_icon.py --source lucide)")
        if not (report["network"]["api.openverse.org"] or report["network"]["commons.wikimedia.org"]):
            report["fix"].append("photo sites unreachable: build without photos, or ask the user for their own images")

    report["ok"] = ok
    report["message"] = message
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to a legacy code page; agents read UTF-8
        getattr(_stream, "reconfigure", lambda **_: None)(encoding="utf-8")
    sys.exit(main())
