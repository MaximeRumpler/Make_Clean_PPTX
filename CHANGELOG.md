# Changelog

All notable changes to this project are documented here. Format based on [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **JSON Schema for deck.json**, `assets/deck.schema.json` (draft 2020-12): every key, layout reference, `fill` value type (text, bullets, tables, images, icons, SVG, charts, waterfall, Gantt, shading, positions), `insert`, `theme`, `logo`, `skeleton` and the other deck options, so agents and tools that do not read the reference can check their specs. `scripts/validate_spec.py deck.json` validates a spec with the standard library only (JSON report, exit 0 valid, 1 invalid, 2 unreadable). Tests check that the shipped examples validate and that the schema's keys, sources and colour names match `build_deck.py`.
- **Orbital diagrams**, first visuals of a new opt-in **Expressive** family: `V-ORB-01-<n>` one orbit with 3 to 8 satellites, `V-ORB-02-<inner>x<outer>` two orbits (2x4, 3x5, 3x6, 4x6), `V-ORB-03-<n>` half orbit for a half frame (3 to 5). Geometry is computed in the generator, one slide per count, checked at build time and in tests (no overlaps, nothing crosses the ring or leaves the frame, centre then clockwise from 12 o'clock). `read_index.py` hides rows tagged `expressive` unless asked for, like `signature`.

### Changed
- Docs brought in line with the Make PPTX set: the same set table and footer in every README, gallery badge at 135 slides, opt-in Signature and Expressive visuals explained in the README, gallery and how-it-works, the quick choices and skeleton mode linked from the README, the deck.json schema and `"theme"`/`"logo"` keys in how-it-works, plainer plugin and citation descriptions, theme-contract counts refreshed for 135 slides.
- Claude Code install now goes through the shared `make-pptx` marketplace of the set (`/plugin marketplace add MaximeRumpler/Make_PPTX`, `/plugin install make-clean-pptx@make-pptx`) in the README, gallery and how-it-works. This repository's own marketplace is unchanged, so earlier installs keep working.
- Opt-in Signature and Expressive visuals: no fixed number per deck any more. SKILL.md, layout-rules.md, visual-selection.md and the index `limits` say to use them sparingly and judge the amount per deck from the request, the audience and the content style; the opt-in rule itself is unchanged.
- Make_Style_PPTX and Make_Colors_PPTX are public previews: the set table in the README and the gallery's set section link to them; a Make PPTX set badge replaces the Claude Code badge.
- Gallery: `gallery.py --html-only` also keeps the counts and version in `<head>` in sync; card ids and focus rings use a darker green in the light theme (WCAG AA contrast); the header has a short Make PPTX set section; `sitemap.xml` date refreshed.

## [1.2.0] - 2026-10-27

### Added
- **Skeleton mode** for content that cannot be shared: `build_deck.py --skeleton` (or `"skeleton": true` in deck.json) fills every field used with a bracketed instruction stating its limit from the index (`[Title, max 52 characters]`, shorter forms when the box is small), gives charts flat dummy series named "Dummy data — replace", tables `[to fill]` cells and icons a neutral bundled icon, lists each field and its limit in the speaker notes, and writes `<deck>.fill-sheet.md` (slide, field, limit). Values in `fill` (except the `Footer` confidentiality label), notes and `properties` are never written. `lint_deck.py` lists the bracketed instructions and dummy series still in a deck as warnings.
- `--offline` on `build_deck.py`, `find_icon.py`, `fetch_image.py` and `fetch_templates.py` (or `MAKE_CLEAN_PPTX_OFFLINE=1`): no network connection at all; bundled libraries, bundled Lucide icons, local files and the cache only, and a plain message when something would need the network.

### Changed
- Plainer SKILL.md introduction; a French sentence in the README and the gallery; the gallery says a theme or template and a logo can be given.

## [1.1.0] - 2026-10-27

### Added
- **Logo slot**: deck.json `"logo"` (PNG, JPG or SVG; path next to deck.json, then the current folder) puts the logo in a top-corner `Logo` slot on the covers L-01 to L-05 and the closing slide L-49, scaled to fit with its aspect ratio kept; `"logo_alt"` gives its alt text, otherwise it is marked decorative. Without `"logo"` the slots are removed and decks are byte-identical to before. A wrong file stops the build with a plain error (exit 2). The slot is flagged `role=logo` in the index (style contract). `lint_deck.py` warns when a logo overlaps text and no longer asks for alt text on pictures marked decorative.
- **Style contract** for style packs (and the companion skill Make_Style_PPTX), `references/style-contract.md`. Style tokens in `library/style-tokens.json` (font pair, character width, corner radius, card treatment, background, title case, numbering); the default tokens rebuild the bundled libraries byte for byte, and `library/tools/build_pack.py <style>` builds an alternative pack with the same ids and field names and its own character limits. Every shape that is not a field is now named after its role (`card#2 > Heading 2`, `panel#1 > Title`, `decoration#5`), and container fields carry a `role=` flag in the index. New `arrange` column in `layouts.csv` and `visuals.csv` (and the gallery catalogue): layouts and visuals (diagrams and timelines only) whose repeated units may be rearranged (`row:3`, `grid:4`, `column:5:ordered`). `fit_test.py --check` fills every field at its limit without rendering; CI runs it on the default libraries and on the `soft` pack.
- **Theme contract** for brand themes (and the companion skill Make_Colors_PPTX): `references/theme-contract.md` explains the role of every theme slot and font, the required accent ramp and the text/fill pairs to keep readable; `assets/theme-contract.json` is the machine-readable version, generated from the libraries by `library/tools/build_contract.py` (uses per slot and pairs are measured, not typed) and checked in CI.
- `lint_deck.py --contrast` (opt-in): WCAG contrast of every text run over the fill under it, computed from the deck's own theme (colour map, `lumMod`/`lumOff`/`tint`/`shade`/`alpha`, groups, tables, chart data labels), plus a check of the theme against the contract. Default lint output is unchanged.
- Relative file paths in deck.json (images, `.svg` files, `local:` icons, `theme`) are looked up in the folder of deck.json first, then in the working directory as before, so a spec works wherever the build is started. Absolute paths are unchanged; a missing file is reported with both folders; an image given as a web address gets a plain message (save it first with `fetch_image.py`).
- deck.json `"theme"` key: `build_deck.py` replaces the deck's theme colours and fonts with those of a `.thmx`, `.potx`, `.pptx` or theme `.xml` file (path relative to deck.json, then to the working directory), without touching the slides. The source master's colour map is applied when there is one (dark themes). The theme is checked against the theme contract and problems are printed as warnings; the build never fails on them. A brand font that is unlikely to be available gives a warning, and `theme_fonts_fallback` names the font to use instead. Missing, damaged or non-theme files stop the build with a plain error.
- README install: direct link to the zip, the *Code execution and file creation* step for Claude.ai and Claude desktop, Node.js note for `npx skills`, link to the Make PPTX Get started guide. Same steps in the gallery.
- Gallery: title, description, canonical link, Open Graph tags and JSON-LD; every card, the counts and a heading are now printed in the HTML (`gallery.py --html-only` refreshes them, a test checks they match `catalog.json`); `sitemap.xml`; link to the Make PPTX set.
- Issue form "It didn't work" (assistant, operating system, what happened) and `config.yml` pointing questions to Discussions.
- Deck options settled up front in one short choice message (format, confidentiality, length, accessibility), with defaults that add nothing (`.pptx`, no label) when the user does not choose or the harness cannot ask. New `references/deck-options.md`: confidentiality label in the footer, no online icon or photo searches for confidential content, minimal file properties, and a skeleton deck with bracketed instructions when the user cannot share the real content.
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
- Library shapes that are not fields are renamed from `Decoration n` to role names; field names, ids and specs are unchanged. The theme font pair moved from `theme/tokens.json` to the style tokens. V-SIG-02 `Label 2` limit lowered to what its box holds (the fit check flagged it).
- `install.sh` only replaces a previous copy of this skill (never an unrelated folder), swaps in the new copy after it is complete, and no longer forces packages into a system-managed Python (`--break-system-packages` removed; falls back to `--user`, then explains how to use a virtual environment).
- Dependabot keeps Python requirements as minimums instead of raising them on every release (raising Pillow to 13 would have dropped Python 3.9).
- Banner without the "plan · choose · fill · check" line.
- Shorter, plain-language error hints in `doctor.py`, `render_check.py` (per operating system), `build_deck.py` (a missing package now gives a JSON error instead of a traceback) and `fetch_image.py`.
- `render_check.py`: a deck LibreOffice cannot convert now exits 5 ("rendering failed"), as documented, instead of 4 (reserved for missing tools).

### Fixed
- Text too faint in the neutral visuals, found by the new contrast check: the dark-slice labels of V-COM-03 (donut, now white on dark slices), the captions on mid-grey boxes of V-MAT-05, V-TIM-04 and V-STR-09 (now ink), and the quadrant texts of V-MAT-03 (now ink2 on grey fills).
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
