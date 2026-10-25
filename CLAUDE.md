@AGENTS.md

## Claude Code notes

- The repository is also a Claude Code plugin: `.claude-plugin/` (manifests), `skills/` (the skill), `agents/` (the `deck-reviewer` sub-agent).
- After editing the skill, validate it with the skill-creator checker if available: `python -m scripts.quick_validate skills/make-clean-pptx`.
- To test the skill locally without installing the plugin: `./install.sh --project`, then restart Claude Code in a scratch folder.
- Do not commit generated decks, renders or downloaded images (`build/`, `library/out/` are ignored). Do commit the regenerated `assets/`, `docs/` and `CATALOG.md` after a library change.
