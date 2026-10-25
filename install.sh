#!/usr/bin/env bash
# Install the make-clean-pptx skill for Claude Code (or any harness that loads SKILL.md folders).
#
#   ./install.sh                 copy to ~/.claude/skills/            (personal, all projects)
#   ./install.sh --project       copy to ./.claude/skills/            (this project only)
#   ./install.sh --dir PATH      copy to PATH/make-clean-pptx         (any harness)
#   ./install.sh --symlink       link instead of copy (development)
#   ./install.sh --deps          also pip install the Python requirements
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/make-clean-pptx"
DEST_ROOT="${HOME}/.claude/skills"
LINK=0
DEPS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) DEST_ROOT="$(pwd)/.claude/skills" ;;
    --dir)     DEST_ROOT="${2:?--dir needs a path}"; shift ;;
    --symlink) LINK=1 ;;
    --deps)    DEPS=1 ;;
    -h|--help) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

[[ -f "$SRC/SKILL.md" ]] || { echo "skill not found at $SRC" >&2; exit 1; }

mkdir -p "$DEST_ROOT"
DEST="$DEST_ROOT/make-clean-pptx"
rm -rf "$DEST"
if [[ $LINK -eq 1 ]]; then
  ln -s "$SRC" "$DEST"
  echo "linked  $DEST -> $SRC"
else
  cp -R "$SRC" "$DEST"
  find "$DEST" -name '__pycache__' -type d -prune -exec rm -rf {} +
  echo "copied  $SRC -> $DEST"
fi

if [[ $DEPS -eq 1 ]]; then
  python3 -m pip install -r "$SRC/requirements.txt" || \
    python3 -m pip install --break-system-packages -r "$SRC/requirements.txt"
fi

echo
echo "Next: python3 \"$DEST/scripts/doctor.py\"   (checks dependencies and network)"
echo "Then ask your agent: \"Make a 10-slide deck from these notes…\""
