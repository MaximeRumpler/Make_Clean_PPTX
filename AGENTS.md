# AGENTS.md

This repository ships one agent skill: **`skills/make-clean-pptx/`**. It builds clean PowerPoint decks by cloning slides from a bundled layouts library, inserting components from a bundled visuals library, and filling them with the user's content, then checks the result.

## When to use it

Whenever the user asks for a presentation, slide deck, pitch deck, slides, PowerPoint or `.pptx` (also: "présentation", "diaporama", "mets ça en slides"), from any kind of content, or asks to review or clean up an existing deck.

## How to use it (harnesses without native skill loading)

1. Read `skills/make-clean-pptx/SKILL.md` completely and follow its workflow. All paths in that file are relative to its own folder.
2. Read `skills/make-clean-pptx/references/layout-rules.md` before planning slides, and `visual-selection.md` before choosing charts or diagrams.
3. Use only the scripts in `skills/make-clean-pptx/scripts/`. Do not draw slides from scratch with python-pptx: it cannot reproduce the design.
4. Requirements: Python 3.9+, `pip install -r skills/make-clean-pptx/requirements.txt`. Run `python3 skills/make-clean-pptx/scripts/doctor.py` to check the environment (`--fix` installs missing packages).
5. If you can start a sub-agent, give it `agents/deck-reviewer.md` as instructions for the review step.

To install the skill for any supported assistant: `npx skills add MaximeRumpler/Make_Clean_PPTX`.

## Working on this repository

- Tests: `pip install -r requirements-dev.txt && pytest`. They cover the engine (with generated fixtures), the bundled libraries (index ↔ pptx contract, theme colours, no sample content) and the SVG conversion.
- The skill folder must stay **self-contained**: nothing in `skills/make-clean-pptx/` may import from or read files outside it (people copy only that folder).
- Scripts use the standard library plus python-pptx, openpyxl and Pillow only (lxml comes with python-pptx). Keep them Python 3.9 compatible.
- Every script prints machine-readable JSON (or clearly structured text) and uses distinct exit codes; keep that contract, the agent depends on it.
- `SKILL.md` stays under ~150 lines. Details go to `references/`, explained with the *why*, not as capitalised commands.
- **The libraries are generated** from `library/` (see `library/README.md`). Never edit `assets/*.pptx` or `assets/*.csv` by hand: change the generator, rebuild, run the fit test, regenerate the gallery, commit everything together.
- Library text is placeholder text that describes the slot. Never put names, figures, dates or quotes in it (a test checks for years and currencies).
- Keep the README's design language: flat-square shields in `#10B981` on `#1C2333`, centred header, `* * *` separators, short bold-title tables.
