# Changelog

All notable changes to this project are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added
- SKILL.md guides non-technical users: one short message of questions for what cannot be inferred (purpose, length, PowerPoint `.pptx` or LibreOffice `.odp`), with a proposed default; plain-language delivery (how to open the file, skipped visual check).
- `render_check.py --odp`: also saves an OpenDocument copy of the deck for LibreOffice users (the skill already triggered on `.odp`).
- Release workflow: every release gets the skill as a zip (for Claude.ai and Claude desktop), a sample deck (`.pptx`, `.odp`) and its contact sheet. Can be run by hand to backfill a release.
- README: install for Claude.ai and Claude desktop, Windows note, how to update, CI badge, mention of the companion skill Make_Colors_PPTX (linked once it is public). `CITATION.cff`.
- Gallery: static install and usage text, readable without JavaScript.
- README: the Make PPTX set (Make_Clean, Make_Style, Make_Colors), link to the example deck of the latest release, `.odp` mentioned.
- **Signature visuals** (new family, shown last in the catalogue): six metaphor illustrations drawn as native shapes in the neutral greys, V-SIG-01 meshing gears, V-SIG-02 light bulb, V-SIG-03 puzzle, V-SIG-04 winding road, V-SIG-05 mountain and summit flag, V-SIG-06 target. They are opt-in: rows tagged `signature` are left out of `read_index.py` searches and listings unless the request names them, and visual-selection.md limits them to one or two per deck, a single metaphor, never for figures.
- Visuals V-STR-09 half-ring layers and V-TIM-06 serpentine timeline (eight steps on an S path).
- Drawing kit: `path()` for free-form shapes (custom geometry with lines, Bezier curves and arcs).
- `doctor.py --fix`: installs missing Python packages from `requirements.txt` (normal install, then `--user`; never `--break-system-packages`), reports what was installed and what is still missing, and gives a plain-language `message` the agent can pass on to the user.
- `render_check.py`: when LibreOffice refuses a deck written by another tool, retries once on a re-saved copy made with python-pptx in a temporary folder (the user's file is never touched), reported as `"resaved_copy": true`. Finds LibreOffice in its usual Windows and macOS install folders when it is not on the PATH.
- CI runs the test suite on Windows and macOS too (Python 3.12, without LibreOffice).
- SKILL.md: give the user the full path of the delivered files (in the outputs folder when the harness has one); `doctor.py --fix` in Troubleshooting.

### Changed
- `install.sh` only replaces a previous copy of this skill (never an unrelated folder), swaps in the new copy after it is complete, and no longer forces packages into a system-managed Python (`--break-system-packages` removed; falls back to `--user`, then explains how to use a virtual environment).
- Dependabot keeps Python requirements as minimums instead of raising them on every release (raising Pillow to 13 would have dropped Python 3.9).
- Banner without the "plan · choose · fill · check" line.
- Shorter, plain-language error hints in `doctor.py`, `render_check.py` (per operating system), `build_deck.py` (a missing package now gives a JSON error instead of a traceback) and `fetch_image.py`.
- `render_check.py`: a deck LibreOffice cannot convert now exits 5 ("rendering failed"), as documented, instead of 4 (reserved for missing tools).

### Fixed
- `doctor.py` crashed when python-pptx was missing (the very case it checks for).
- Windows: scripts print UTF-8 (the console code page could not encode some characters and stopped the script), and the LibreOffice profile path is now a valid `file:` URI.

## [1.0.0] - 2026-10-25

First public release.

### Licence
- Released under the **EUPL-1.2** (European Union Public Licence). An additional permission in `NOTICE` leaves the decks created with the skill free of any obligation; the copyleft covers the software and the libraries.

### Added
- **Layouts library**: 54 slides in 14 categories (covers, agendas, dividers, statements, text structures, media, team, frames for visuals, KPIs, tables, decisions, closings, editorial compositions), neutral black, grey and white, theme colours and theme fonts only, placeholders only.
- **Visuals library**: 60 components in 10 families (compare, evolve, compose, relate, KPI, matrix, process, time, structure, frameworks). Quantitative visuals are native, editable charts.
- **CSV indexes** for both libraries, generated with them: description, use_when, tags, objective, data type, frame size, limits, how to fill, and every editable field with its character limit and flags (`optional`, `default`, `follows`).
- **Generators** in `library/` (pptxgenjs + Python post-processing), fit test, gallery generator; CI checks that the committed indexes match a rebuild.
- `build_deck.py`: `layouts` / `visuals` sources (old names kept as aliases), automatic removal of unfilled optional slots and their companions, warnings for required ones, font scaling of inserted visuals, rich values (`fill` shading with theme colours, `at` positioning in a plot area), waterfall and Gantt data shortcuts, icons and SVG illustrations converted to native shapes.
- `find_icon.py`: search the bundled Lucide set (1,900 icons, offline) and Tabler, Material Symbols, OpenMoji and local folders online; licence and credit for each.
- `_svg.py`: SVG to DrawingML converter (paths with arcs, basic shapes, transforms, opacity), theme-colour aware.
- `read_index.py`: CSV and xlsx, generic `--where` filters, bundled index names (`layouts`, `visuals`).
- `fetch_templates.py`: bundled libraries by default (no network); GitHub download kept behind `--remote` for forks.
- References: visual selection guide, review checklist, icons and illustrations; rewritten layout rules, spec reference, index schema and authoring guide.
- `deck-reviewer` sub-agent for the Claude Code plugin; installable in other assistants with `npx skills add`.
- `evals/`: behaviour cases for `claude plugin eval` (French deck, no invented data, minimal content, prompt injection, safe review).
- GitHub Pages gallery (`docs/`) and `CATALOG.md`.
- Byte-reproducible library builds (checked in CI), Dependabot, code of conduct, security policy.
- Engine foundations: slide cloning across packages (pictures, charts, embedded workbooks), text fill with template formatting preserved, cover-cropped pictures, charts, tables; `fetch_image.py` (Openverse, Wikimedia Commons, licence filtering, credits); `lint_deck.py`; `render_check.py`; `inspect_template.py`; `doctor.py`; plugin and marketplace manifests; `install.sh`; pytest suite.
