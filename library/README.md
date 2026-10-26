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
python library/tools/fit_test.py layouts      # fill every field at its limit, look at the contact sheet
python library/tools/fit_test.py visuals
python library/tools/gallery.py               # docs/thumbnails, docs/catalog.json, CATALOG.md, docs/preview.jpg
python library/tools/build_icons.py <lucide repo>   # only when updating the bundled icon set
pytest
```

`fit_test.py` and `gallery.py` need LibreOffice and poppler. CI rebuilds the libraries and fails if the committed indexes differ from the generated ones.

## Layout

| Path | Content |
|---|---|
| `theme/tokens.json` | neutral palette mapped to theme slots, theme fonts, type scale, grid |
| `tools/lib.js` | drawing kit: named text fields with computed character limits, shapes, frames, image and icon slots, charts, tables, slide chrome |
| `layouts/*.js` | 54 layouts in five files (opening, message, content, data, closing) |
| `visuals/*.js` | 68 visuals in eleven families; `_kit.js` holds legends, markers, keys and cards |
| `tools/post.py` | rewrites token colours as `schemeClr`, sentinel fonts as theme fonts, groups each visual, writes deterministic zips |

How to add a layout or a visual, and the design rules, are in [template-authoring.md](../skills/make-clean-pptx/references/template-authoring.md).
