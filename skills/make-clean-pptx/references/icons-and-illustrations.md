# Icons and illustrations

Icons and simple illustrations are inserted as **native shapes**, converted from SVG by `build_deck.py`. They stay sharp at any size, take the theme colours (a rebrand recolours them) and remain editable in PowerPoint and LibreOffice. No picture files, no rasterising tool needed.

## Sources

| Source | Ref prefix | Access | Size | Style | Licence |
|---|---|---|---|---|---|
| [Lucide](https://lucide.dev) | `lucide:` | **bundled** (`assets/icons/lucide.json`, index `icons.csv`) | ~1,900 | line, 2 px, rounded | ISC: free, attribution not required |
| [Tabler Icons](https://tabler.io/icons) | `tabler:` | online (jsDelivr), or a local copy | ~5,000 | line, same grid as Lucide | MIT |
| [Material Symbols](https://fonts.google.com/icons) | `material:` | online (Google Fonts) | ~4,000 | filled outline | Apache 2.0 |
| [OpenMoji](https://openmoji.org) | `openmoji:` | online (jsDelivr), black line version | ~4,000 | pictograms, emoji-like | **CC BY-SA 4.0: attribution required** (added to the credits automatically) |
| Your folders | `local:` or a path | `config.json` → `icons.local_dirs`, or `$MAKE_CLEAN_PPTX_ICON_DIRS` | any | any | yours to check |

Lucide is the default because it is bundled (works offline) and its thin, rounded line matches the sober layouts. Tabler has the same drawing grid and stroke, so the two can be mixed if Lucide lacks a symbol. Do not mix line icons with Material's filled style in one deck.

## Finding an icon

```bash
python3 scripts/find_icon.py "data security"                 # bundled Lucide only
python3 scripts/find_icon.py "solar panel" --source tabler,material
python3 scripts/find_icon.py "handshake" --source all --top 15
python3 scripts/find_icon.py --get material:solar_power --out build/icons/solar.svg   # to look at it
```

Search in English with concrete words. Results are ranked by name, tags and categories; the `ref` is what goes into the spec.

## Using it in a spec

```json
"Icon 1": {"icon": "lucide:shield-check"}
"Icon 2": {"icon": "tabler:solar-panel", "color": "a3"}
"Icon 3": {"icon": "material:handshake", "weight": 0.75}
"Photo":  {"svg": "assets-local/doodle-reading.svg", "mode": "grey"}
```

| Option | Default | Effect |
|---|---|---|
| `color` | the slot's colour | any theme colour (`ink`, `a1`…`a6`, `paper` on dark backgrounds) |
| `mode` | `mono` for icons, `grey` for `svg` | `mono`: one colour; `grey`: each colour mapped by lightness to the theme greys (illustrations); `keep`: original colours (avoid in the neutral theme) |
| `weight` | 1.0 up to 0.7 in, 0.8 above | stroke factor for line icons; large icons look better a little lighter |
| `alt` | none | description for screen readers |

Icon slots exist in the layouts (`Icon 1`…`Icon 3` of L-20); any other shape can receive an icon too, the icon takes its box.

## Illustrations

Simple flat SVG illustrations work well when converted in `grey` mode. Free sources:

- **[Open Doodles](https://www.opendoodles.com)** by Pablo Stanley: CC0, hand-drawn people. Download the SVGs (via the site or Blush) into a local folder.
- **[unDraw](https://undraw.co/illustrations)**: free, no attribution, but its licence forbids redistributing the collection; download individual SVGs for your own decks only, never commit them to a public repository.
- **OpenMoji** (`openmoji:` refs, see above) for small pictograms.

Put downloaded files in a folder listed in `icons.local_dirs` (or `$MAKE_CLEAN_PPTX_ICON_DIRS`); `find_icon.py --source local` searches them by file name (and by `tags:` comments, as in Tabler's files).

## What converts, what does not

Paths (all commands, arcs included), circles, ellipses, rectangles, lines, polylines, polygons, groups, transforms, opacity. Gradients, patterns, masks, embedded images and text are skipped with a warning: check the render. Very detailed illustrations (thousands of paths) convert but make the file heavier; prefer simple ones.
