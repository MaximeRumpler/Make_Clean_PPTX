# Style contract

What a **style pack** is, and what a restyler (the companion skill Make_Style_PPTX, or any tool) can rely on in the libraries: the style tokens, the role of every container shape, the layouts whose units can be rearranged, and the character limits of each pack. This skill does not need this file to build decks; it is the interface for tools that change how the decks look.

## Style packs

A pack is the two libraries drawn with another set of style tokens:

```
<pack>/layouts.pptx  layouts.csv  visuals.pptx  visuals.csv  theme-contract.json  style.json
```

- **Same ids, same field names, same fields** as the bundled libraries (CI checks it). A spec written for one pack builds with any other: `build_deck.py --spec deck.json --local-dir <pack>`.
- **Own character limits**: the `limit` of each text field in the pack's CSV is computed for the pack's fonts (see below). Plan and fill with the index of the pack you build with.
- `style.json` holds the tokens the pack was built with.

In this repository the tokens live in `library/style-tokens.json`: `default` builds the bundled libraries, each entry of `styles` lists only the tokens it changes. `python library/tools/build_pack.py <name> [--fit]` builds a pack into `library/out/styles/<name>/pack/`; a tokens file (`<file>.json`, with an optional `"name"`) works the same way.

## Tokens

| Token | Default | Values | Effect |
|---|---|---|---|
| `fonts.heading`, `fonts.body` | `Arial`, `Arial` | any font name | the theme font pair (major, minor); slides only use theme fonts |
| `char_em.heading`, `char_em.body` | `0.52`, `0.52` | 0.4 to 0.8 | average character width of the font, in em: sets the character limits of the pack |
| `radius` | `0` | 0 to 0.5 (inches) | corner radius of `card`, `callout`, `keyfigure` and `label` containers (rounded rectangle) |
| `cards` | `fill` | `fill`, `outline`, `fill-outline` | treatment of light containers (filled with `surface`): filled, outlined with `line`, or both. No treatment draws a shadow: shadows break on theme swaps and render differently in LibreOffice |
| `background` | `paper` | `paper`, `surface` | slide background of light slides; on `surface`, light containers swap to `paper` so they stay visible. Dark slides keep their own background |
| `title_case` | `as-written` | `as-written`, `upper` | slide and cover titles (`title` and `hero` styles) in capitals, through the font's `cap="all"` (the text itself is unchanged) |
| `numbering` | `as-designed` | `as-designed`, `plain`, `padded` | number placeholders that are kept when not filled: as each layout draws them (`1` or `01`), or all `1, 2, 3`, or all `01, 02, 03` |

Colours are not style tokens: they come from the theme (`theme-contract.md`), which a brand tool replaces without touching the pack.

## Character limits per pack

The limit of a text field is the number of characters that fit its box at its font size:

```
per line = floor(box width in pt / (size × char_em))      lines = floor(box height in pt / (size × 1.2))
limit    = max(4, floor(per line × lines × 0.85))
```

`char_em` is the token of the field's font (heading or body), multiplied by 1.2 for titles in capitals. Two editorial caps apply in every pack: labels at most 40 characters, text inside a visual at most 60. A few fields have a fixed limit set by the layout (a 3-character marker, a 4-character gate); those do not change between packs. `fit_test.py --style <name> --check` fills every field of a pack at its limit and fails when one is reported as overflowing; CI runs it on the default libraries and on one other style.

## Role tags

Every shape of the libraries is either a **field** (named in the index, filled by the spec) or a **role-tagged shape**. A restyler swaps the geometry of containers by role and moves the fields they hold with them.

| Role | What it is | What a restyler may do |
|---|---|---|
| `card` | a box that holds a heading and some text, one of a set | change shape, corners, treatment; move it with its unit |
| `callout` | a single highlighted box: takeaway, decision, problem, caption over a photo | change shape (bubble, ticket…), keep it prominent |
| `keyfigure` | a tile that frames a big number | change shape; keep the number centred and large |
| `label` | a small badge, pill or numbered marker | change shape (circle, pill, tag) within its box |
| `panel` | a band or sidebar, often bleeding off the slide edge | change texture or edge (torn, wave), keep the area |
| `frame` | where a visual or items go (`Content Area`, `Plot Area`) | leave the box; it is replaced by the visual or used for positions |
| `decoration` | rules, dots, arrows, ornaments, illustration parts | restyle or drop as ornament; it carries no text |
| `logo` | the brand logo slot of the covers and the closing slide (field `Logo`, flag only) | never restyle; keep the box size, keep it in a corner clear of text |

### Where the tag is: the shape name

- A shape that is not a field is named **`<role>#<n>`**, or **`<role>#<n> > <field>`** when it holds a text field. Examples: `card#2 > Heading 2`, `keyfigure#1 > KPI 1 value`, `panel#1 > Title`, `decoration#7`. `<n>` counts each role on the slide (or in the visual). Grammar: `^(card|callout|keyfigure|label|panel|frame|decoration)#\d+( > .+)?$`; the linked field always exists on the same slide (the generator refuses otherwise).
- A **field** keeps its name, because the name is the key of the spec's `fill`. When a field is also a container, the index says so with the flag `role=<role>` in the `fields` column (`index-schema.md`): every `frame` and `plot` field (`role=frame`), every `deco` field ("Step 1 mark", `role=decoration` or `role=label`), and every text field drawn with its own fill or outline (`role=label`, `card`, `callout` or `keyfigure`), and the logo slot `Logo` (`role=logo`, on L-01 to L-05 and L-49). In a built deck these keep their field names, so a restyler reads their role from the pack's index.
- Role-tagged shapes are marked decorative for screen readers (their text lives in the fields they hold).

**Why the name.** The shape name is the one carrier that python-pptx reads directly, that the engine already relies on, that PowerPoint and LibreOffice both keep when they save a file, and that `build_deck.py` copies with the shape when it clones slides and visuals. The alternatives were weighed and left aside: `descr` and `title` are the alternative text that screen readers read aloud; a custom attribute on `p:cNvPr` is invalid XML for PowerPoint (repair prompt); an `extLst` extension and shape tags (`p:custDataLst`) are dropped by LibreOffice, and tags need a separate part that cloning would have to copy. The role names cannot collide with a spec key: no field name contains `#` followed by a number, and fill keys only target fields. The one fragility is a person renaming shapes in PowerPoint's Selection Pane; a restyler treats an unknown name as a plain shape and leaves it alone.

## Arrangements

The `arrange` column of `layouts.csv` and `visuals.csv` marks the layouts and visuals whose content is a set of identical units: `row:3`, `grid:4`, `column:5:ordered` (syntax in `index-schema.md`). A unit is every field with the same number plus the role-tagged container that holds them. A restyler may lay the units out differently (stagger, arc, cascade, constellation…) as long as it keeps every unit together, keeps the order when the value ends with `ordered`, and keeps the units inside the content band of the grid. Rows with an empty `arrange` keep their arrangement. Visuals are flagged only for diagrams and timelines, and not when the position is the meaning (cycle, pyramid, concentric rings, Venn, canvas, five forces, trees, stacked layers); inside a visual the units stay within the component's box.

## What a restyler must keep

- Field names, ids, slide order and the `follows` links: specs and `build_deck.py` depend on them.
- Text inside the container that holds it: when a new shape is smaller than the box (a drop, a cloud), recompute the text box inside it and lower that field's limit in the pack's index with the formula above, or fall back to the standard shape when the text no longer fits.
- Theme colours and theme fonts only (`theme-contract.md`), so a brand theme still recolours the pack.
- Placeholders that describe the slot, never content.
- The `Logo` slot on the same slides: the brand tool (Make_Colors_PPTX) fills it through deck.json `"logo"`, see `spec-reference.md`.

## Checked in CI

`tests/test_style_contract.py` and the `library` job: every shape is a field or role-tagged, every container field has a role flag, links point to fields, the tokens are valid, the default build is byte-identical to the committed libraries, the alternative pack keeps every id and field name, and both pass the fit check.
