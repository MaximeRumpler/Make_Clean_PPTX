# Deck spec reference

`build_deck.py --spec deck.json` reads one JSON file. Everything except `slides` is optional. Relative file paths in it (images, `.svg` files, `local:` icons, `theme`) are looked up in the folder of deck.json first, then in the working directory; absolute paths are used as they are, and a file found in neither place is reported with both folders. Set `language` to the language tag of the content (`fr-FR`, `en-GB`, `de-DE`…): screen readers and spell checkers use it on every text run.

```json
{
  "output": "build/deck.pptx",
  "language": "fr-FR",
  "properties": {"title": "…", "author": "…", "subject": "…", "keywords": "…"},
  "theme": "brand/brand.thmx",
  "theme_fonts_fallback": "Arial",
  "slides": [ { …slide… }, { …slide… } ]
}
```

## Brand theme

`theme` replaces the colours and fonts of the deck's theme with those of a PowerPoint theme (`.thmx`), a template (`.potx`), a presentation (`.pptx`) or a theme part (`.xml`). A relative path is read from the folder of deck.json (then from the working directory). The slides are not touched: every colour and font in the libraries is a theme reference, so the whole deck follows. The line and effect styles of the libraries stay. If the source has a slide master, its colour map is applied too (dark themes keep `dk1` dark and swap the map). A file that is missing, damaged or not a theme stops the build with a plain error (exit 2).

The theme is then checked against `references/theme-contract.md` (accent ramp, text and fill pairs): problems are **warnings**, the deck is still built. Fix the theme, not the slides, then check the deck with `lint_deck.py --contrast`.

Fonts: a brand font that is neither common (Windows, macOS, Office) nor installed on this machine gives a warning; with `theme_fonts_fallback` (`"Arial"`, or `{"major": "Georgia", "minor": "Arial"}`) the theme uses the fallback instead. The character limits are measured with Arial, so after a font change run `lint_deck.py` and `render_check.py` again and shorten what overflows. The report gets a `theme` object: source, name, fonts, `dark`, `colour_map`, `contract_findings`.

## Slide

| Key | Type | Meaning |
|---|---|---|
| `source` | `"layouts"` (default) or `"visuals"` | which library the slide is cloned from (`"design"` / `"shapes"` still work) |
| `id` | string | the `id` column of the index, e.g. `"L-32"`. Preferred: stable across library versions |
| `slide` | int, 1-based | alternative to `id`: position of the slide in the library |
| `fill` | object | field name → value (see below) |
| `insert` | array | visuals placed into this slide (see below) |
| `notes` | string | speaker notes; credits are appended automatically |
| `keep_unfilled` | bool | keep optional fields you did not fill (default: they are removed) |
| `hidden` | bool | skip this slide (handy while iterating) |

Slides appear in the order of the `slides` array; the same layout can be used any number of times.

### What happens to fields you do not mention

Library text is a *description of the slot*, never content, so it must not reach the deck:

| Field flag (index) | Not filled | Why |
|---|---|---|
| `optional` | removed | the slide works without it |
| *(none)*, i.e. required | kept, **warning** | the slide needs it: fill it or set it to `null` |
| `default` | kept silently | the template text is a sensible value ("Agenda", "Strengths", "01") |
| `follows=X` | removed when X is removed | numbers, dots and rules that belong to X |

## `fill`: values by type

| Value | Applies to | Result |
|---|---|---|
| `"text"` | text field | one paragraph per line (`\n`), template formatting preserved |
| `["a", "b", {"text": "c", "level": 1}]` | text or bullets field | one paragraph per item; `level` indents (0-8) |
| `"**bold** word"` | text | `**…**` becomes a bold run |
| `null` or `""` | any field | **deletes** the shape |
| `{"text": "42", "fill": "a1", "color": "paper", "at": [30, 70]}` | text field or shape | rich value, every key optional: `fill` tints the shape with a theme colour (dark fills switch the text to white automatically), `color` sets the text colour, `at` moves the shape centre to x%, y% of the visual's `Plot Area` (0,0 = bottom left) |
| `{"path": "img.jpg", "alt": "…", "credit": "…", "fit": "cover"}` | image field or any shape | picture, cover-cropped to the frame (`"fit": "contain"` keeps it whole). An `.svg` path is converted to native shapes |
| `{"icon": "lucide:rocket"}` | icon field or any shape | icon converted to native shapes, in the slot colour. Options: `color` (theme colour), `mode` (`mono` default, `grey`, `keep`), `weight` (stroke factor, e.g. 0.75), `alt` |
| `{"svg": "drawing.svg", "mode": "grey"}` | any shape | an SVG illustration as native shapes; `grey` maps its colours to the theme greys |
| `{"categories": ["Q1","Q2"], "series": {"2026": [4, 9]}}` | chart | replaces the chart data; keep the number of series of the template unless the chart is a simple one |
| `{"categories": [...], "waterfall": [100, 12, -20, 92], "totals": [0, 3]}` | waterfall chart (V-COM-01) | first and last values are totals by default; the hidden base series is computed |
| `{"categories": ["Task 1", …], "gantt": [[0, 3], [2, 5]]}` | Gantt chart (V-TIM-03) | `[start, duration]` per task, in any unit from 0 |
| `[["a","b"],["c","d"]]` | table | fills cells; rows are cloned or removed to match. The first row is the header |

**Theme colours** for `fill` and `color`: `ink`, `ink2`, `muted`, `line`, `surface`, `paper`, `a1` (darkest accent) to `a6` (lightest). Aliases: `black`, `white`, `dark`, `light`, `grey`, `accent1`… In the neutral theme they are greys; with the user's theme they become the brand colours, so use them for meaning (strong / weak), not for decoration.

### Keys
- A key is a **field name** from the index (exact match first, then case-insensitive). Fields inside groups are reachable too.
- `"#3"` addresses the 3rd top-level shape (for libraries without names).
- If no shape has that name, the key is tried as a `{{token}}` inside any text.
- Unknown keys produce a warning listing the available names (`--strict` turns it into an error).

## `insert`: put a visual into a layout

```json
{"id": "L-32", "fill": {"Title": "Volume explains the gap"},
 "insert": [{
   "id": "V-COM-01", "component": "V-COM-01", "into": "Content Area",
   "fill": {"Chart": {"categories": ["Budget", "Price", "Volume", "Actual"], "waterfall": [100, 12, -20, 92]},
            "Source": "Finance, Q3 actuals"}
 }]}
```

| Key | Meaning |
|---|---|
| `source` | default `visuals` |
| `id` / `slide` | the visual's index id (e.g. `V-COM-01`) or slide number |
| `component` | name of the group to copy: in the bundled library it is the id itself |
| `into` | the frame field of the layout (`Content Area`, `Content Area 2`…). The frame is replaced |
| `box` | alternative to `into`: `[x, y, w, h]` in percent of the slide |
| `fit` | `"contain"` (default, uniform scale, centred) or `"stretch"` |
| `fill` | same rules as slide `fill`, applied inside the visual |
| `keep_unfilled` | as for slides |

A visual scaled down to fit a small frame has its fonts scaled too, never below 8 pt; the report warns when that floor is hit. Match the `frame` column of the visual (`full`, `wide`, `half`) with the frame size of the layout: full ≈ L-31, wide ≈ L-32 / L-35, half ≈ L-34. Native charts keep their own font size at any scale, so they suit small dashboard modules (L-36) best.

## Report printed by build_deck.py

```json
{"output": "build/deck.pptx", "slides": 12, "warnings": ["slide 4 (layouts#32): required field 'Takeaway' still shows its template placeholder; fill it or set it to null."], "credits_file": "build/deck.credits.md"}
```

Exit codes: `0` built (read the warnings), `2` fatal spec or library problem (JSON `error`), `3` libraries could not be located.

## Useful flags

`--local-dir DIR` use your own library files · `--layouts/--visuals PPTX` explicit files (with `--layouts-index/--visuals-index` for `id` lookups) · `--strict` fail on unknown field names.
