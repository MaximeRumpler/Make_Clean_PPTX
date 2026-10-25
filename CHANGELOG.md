# Changelog

All notable changes to this project are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

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
