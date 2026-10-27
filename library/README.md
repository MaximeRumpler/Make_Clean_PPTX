# library/

The source of the two libraries shipped in `skills/make-clean-pptx/assets/`. Nothing here is needed to *use* the skill; it is needed to change the libraries.

## Why generated, not hand-made

One registry per library describes each slide twice at once: the metadata that becomes its index row, and a `draw` function that produces the slide. Building writes the pptx and the CSV from the same source, so the index can never disagree with the slides, and a change to the design system (a colour, a margin, a font size) is applied everywhere by rebuilding.

## Build

```bash
npm ci --prefix library                       # pptxgenjs, pinned
node library/tools/build.js all               # -> library/out/{layouts,visuals}.pptx + registries
python library/tools/post.py all              # theme, groups -> skills/make-clean-pptx/assets/*.pptx
python library/tools/build_index.py           # -> skills/make-clean-pptx/assets/*.csv
python library/tools/build_contract.py        # -> skills/make-clean-pptx/assets/theme-contract.json
python library/tools/fit_test.py layouts      # fill every field at its limit, look at the contact sheet
python library/tools/fit_test.py visuals
python library/tools/gallery.py               # docs/thumbnails, docs/catalog.json, CATALOG.md, docs/preview.jpg
python library/tools/build_icons.py <lucide repo>   # only when updating the bundled icon set
pytest
```

`fit_test.py` and `gallery.py` need LibreOffice and poppler (`fit_test.py --check` does not: it reports fields that overflow at their limit without rendering).

## Style packs

The look of the libraries is set by the style tokens in `style-tokens.json`: font pair, average character width (which sets the character limits), corner radius, card treatment, slide background, title case and numbering. `default` builds the bundled libraries, and its values are those the libraries always had, so the default build does not change. Each entry of `styles` lists only what it changes and builds a separate pack, with the same ids and field names:

```bash
python library/tools/build_pack.py soft --fit   # -> library/out/styles/soft/pack/ (pptx, csv, theme-contract.json, style.json)
python skills/make-clean-pptx/scripts/build_deck.py --spec deck.json --local-dir library/out/styles/soft/pack
```

Every tool also takes `--style <name|file.json>` (or `MAKE_CLEAN_STYLE`) and `--pack-dir` (or `MAKE_CLEAN_PACK_DIR`). The contract for the companion skill that restyles decks is in [style-contract.md](../skills/make-clean-pptx/references/style-contract.md). CI rebuilds the libraries and fails if the committed indexes or the theme contract differ from the generated ones, and runs `lint_deck.py --contrast` on both libraries.

## Layout

| Path | Content |
|---|---|
| `theme/tokens.json` | neutral palette mapped to theme slots, type scale, grid |
| `style-tokens.json` | style tokens: the default look and the alternative packs |
| `tools/style.js`, `tools/_style.py` | which style is built and where its files go (same rules on both sides) |
| `tools/build_pack.py` | builds a whole pack for one style, optionally with the fit check |
| `tools/lib.js` | drawing kit: named text fields with computed character limits, shapes, frames, image and icon slots, charts, tables, slide chrome |
| `layouts/*.js` | 54 layouts in five files (opening, message, content, data, closing) |
| `visuals/*.js` | 68 visuals in eleven families; `_kit.js` holds legends, markers, keys and cards |
| `tools/post.py` | rewrites token colours as `schemeClr`, sentinel fonts as theme fonts, groups each visual, writes deterministic zips |

How to add a layout or a visual, and the design rules, are in [template-authoring.md](../skills/make-clean-pptx/references/template-authoring.md).
