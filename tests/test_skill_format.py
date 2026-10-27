"""The skill folder must stay a valid, self-contained Agent Skill."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "make-clean-pptx"


def _frontmatter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md must start with YAML frontmatter"
    out = {}
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z_-]+:", line):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def test_skill_md_frontmatter_and_size():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert fm["name"] == SKILL.name == "make-clean-pptx"
    assert 50 < len(fm["description"]) <= 1024
    assert text.count("\n") < 500


def test_referenced_files_exist():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for rel in set(re.findall(r"`((?:references|scripts|assets)/[\w./-]+)`", text)):
        assert (SKILL / rel).exists(), f"SKILL.md mentions {rel} but it does not exist"


def test_config_is_consistent():
    cfg = json.loads((SKILL / "config.json").read_text(encoding="utf-8"))
    assert set(cfg["files"]) == {"layouts", "visuals"}
    for kind in cfg["files"].values():
        for name in kind.values():
            assert (SKILL / cfg["assets_dir"] / name).is_file(), f"bundled {name} missing"
    for kind in cfg["files"].values():
        assert set(kind) == {"pptx", "index"}


def test_skill_is_self_contained():
    """Scripts must not reach outside the skill folder (people copy only this folder)."""
    for py in (SKILL / "scripts").glob("*.py"):
        src = py.read_text(encoding="utf-8")
        assert "parent.parent.parent" not in src, f"{py.name} walks above the skill folder"
        assert "Make_Clean_PPTX/tests" not in src


def test_plugin_manifests_parse():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    assert plugin["name"] == "make-clean-pptx"
    assert market["plugins"][0]["name"] == plugin["name"]
    assert (ROOT / "skills" / "make-clean-pptx" / "SKILL.md").is_file()


def test_licence_copies_in_skill_folder():
    """The skill is often copied alone: it carries the licence and the notice."""
    assert (SKILL / "LICENSE.txt").read_text(encoding="utf-8") == (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert (SKILL / "NOTICE.txt").read_text(encoding="utf-8") == (ROOT / "NOTICE").read_text(encoding="utf-8")
    assert "EUPL-1.2" in _frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))["license"]
