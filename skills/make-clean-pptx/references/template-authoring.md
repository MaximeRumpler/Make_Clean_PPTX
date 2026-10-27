# Extending the libraries, or bringing your own

For the people who maintain the libraries. The skill is only as good as `layouts.pptx`, `visuals.pptx` and their indexes.

## How the bundled libraries are made

They are **generated from code** (`library/` at the root of the repository, not copied with the skill). One registry per library describes every slide: its metadata (the index row) and a `draw` function. The same run writes the pptx and the index, so they cannot disagree.

```
library/
  theme/tokens.json      palette (theme slots), type scale, grid
  style-tokens.json      style tokens: font pair, corners, cards, background, title case, numbering
  tools/lib.js           drawing kit: text fields, shapes, frames, charts, tables, icon slots
  layouts/*.js           54 layouts, by family
  visuals/*.js           68 visuals, by family (_kit.js: legends, markers, keys, cards)
  tools/build.js         pptxgenjs -> out/<lib>.pptx + out/<lib>.registry.json
  tools/post.py          theme colours and fonts, visual groups, deterministic zip -> skill assets/
  tools/build_index.py   registry -> assets/<lib>.csv
  tools/build_contract.py  libraries -> assets/theme-contract.json (slot roles, uses, colour pairs)
  tools/build_icons.py   Lucide repository -> assets/icons/
  tools/fit_test.py      every field filled at its limit, built, linted, rendered
  tools/gallery.py       thumbnails, docs/catalog.json, CATALOG.md, README mosaic
```

Rebuild everything:

```bash
cd library && npm ci && cd ..
node library/tools/build.js all
python library/tools/post.py all
python library/tools/build_index.py
python library/tools/build_contract.py
python library/tools/fit_test.py layouts && python library/tools/fit_test.py visuals   # look at the contact sheets
python library/tools/gallery.py
pytest
```

## Design rules (the neutral system)

- **Colours are theme references.** Draw only with the tokens of `tokens.json` (`ink`, `ink2`, `muted`, `line`, `surface`, `paper`, `a1`…`a6`); `post.py` rewrites them as `schemeClr` (+ lumMod/lumOff), so a PowerPoint theme recolours everything. An unknown colour makes `post.py` fail on purpose.
- **Text on a fill follows the theme contract** (`theme-contract.md`): paper text on `a1` and `a2`, ink (or ink2) on `a3` to `a6` and `surface`, `muted` only on `paper` and `surface`. Every new text/fill pair becomes a requirement for brand themes, so reuse the existing pairs; CI runs `lint_deck.py --contrast` on both libraries.
- **Fonts are theme fonts** (`+mj-lt` headings, `+mn-lt` body). The neutral theme uses Arial (Liberation Sans in LibreOffice, same metrics).
- **One grid**: 13.333 × 7.5 in, 0.6 in side margins, kicker / title / lead / content / footer bands (`tokens.grid`).
- **Placeholders, never content.** A field's text describes the slot ("Slide title states the takeaway", "Short text", "00"). No names, figures, dates or quotes. Charts use round placeholder numbers and generic labels ("Category 1").
- **Every editable element is a named field.** A visual is one group named after its id.
- **Every other shape has a role.** Give containers `role` (`card`, `callout`, `keyfigure`, `label`, `panel`, `frame`) and `for` (the field they hold): `rect(ctx, x, y, w, h, { fill: "surface", role: "card", for: "Heading 1" })` is named `card#1 > Heading 1`. Rules, dots and ornaments default to `decoration`. A text field drawn with its own fill or outline is its own container (`role` option, default `label`), written in the index as `role=…`. Style packs restyle shapes by role: see `style-contract.md`.
- **Style through tokens, not by hand.** Corners, card treatment, background, title case, numbering (`L.num(i)` for number placeholders) and the font pair come from `library/style-tokens.json`; a layout never sets them itself, so every style pack keeps the same ids and fields.

## Adding a layout

1. Add an entry to the right file in `library/layouts/`:
   ```js
   {
     id: "L-55", name: "Quote and portrait", category: "Statement", style: "Editorial", density: "Low",
     description: "What is visible, in one sentence.",
     use_when: "The message or situation it is for.",
     tags: "five or more search words with synonyms",
     draw(ctx) {
       L.chrome(ctx, { title: false });
       L.image(ctx, "Photo", 0.6, 1.0, 4.0, 5.6);
       L.text(ctx, "Quote", "Quotation, word for word", 5.2, 1.6, 7.5, 3.0, "hero", { italic: true });
       L.text(ctx, "Attribution", "Name, role", 5.2, 4.9, 7.5, 0.4, "label", { optional: true });
     },
   },
   ```
2. `text()` options worth knowing: `optional` (removed when not filled), `keep` (placeholder is a valid default), `follows: "Item 2"` (removed with Item 2), `limit` (override the computed character limit), `bullets`.
3. Logo: a new cover or closing layout calls `L.logo(ctx, "left" | "right" | "center")` last in `draw` (a top corner clear of the title; drawn last so the other shapes keep their ids). It is filled from deck.json `"logo"` and removed when the deck has none.
4. Frames for visuals: `L.frame(ctx, "Content Area", x, y, w, h)`; match one of the visual sizes (full 12.13 × 4.55, wide 7.9 × 4.55, half 5.9 × 4.2) so visuals fit without shrinking.
5. Rebuild, run the fit test, look at the render, regenerate the gallery.

## Adding a visual

Same idea in `library/visuals/`, with the visual columns (`kind`, `frame`, `objective`, `data_type`, `dimensions`, `complexity`, `limits`, `fill_notes`, `related`) and `draw(ctx, box)` drawing inside `box`. Prefer **native charts** for anything quantitative (`L.chart`), so that agents can give real data; drawn bars could only be relabelled. Use `plot()` + `marker()` for positioned items, `text(..., { fill })` for cells that can be shaded.

## Bringing your own pptx files

The skill also works with libraries you design by hand in PowerPoint:

1. **Name every editable shape** in the Selection Pane (`Title`, `Body`, `Photo`, `Number 1`, `Content Area`…). Names are the API. `inspect_template.py deck.pptx --check` lists default names.
2. **Same slide master and slide size** in both files; use theme colours and fonts, not fixed ones.
3. **Text formatting lives in the first run** of each field: the builder clones it for every paragraph. Do not rely on autofit.
4. **Native charts and tables**, so data can be replaced. Group the parts of a visual and name the group.
5. **Draft the index** with `inspect_template.py deck.pptx --emit-index layouts.csv --kind layouts`, then complete category, description, use_when and tags (index-schema.md). Add `optional` / `default` / `follows=` flags to the fields.
6. Use them with `--local-dir <folder>` or `MAKE_CLEAN_PPTX_TEMPLATES_DIR`; file names are set in `config.json`. To share them, fork the repository and replace `skills/make-clean-pptx/assets/`; `fetch_templates.py --remote` (or `MAKE_CLEAN_PPTX_REPO=you/your-fork`) downloads them from GitHub.

Keep pptx files small: compress pictures, avoid embedded fonts unless needed. GitHub serves files up to 100 MB without LFS; `fetch_templates.py` falls back to the LFS host if you use it.
